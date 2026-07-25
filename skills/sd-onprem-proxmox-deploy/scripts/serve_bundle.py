#!/usr/bin/env python3
"""Serve one SD bundle to one source and log completed response bytes."""

from __future__ import annotations

import argparse
import hashlib
import http.server
import ipaddress
import os
import stat
import sys
import urllib.parse
from pathlib import Path


CHUNK_SIZE = 1024 * 1024


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve exactly one SD .tgz bundle to one source IP.",
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--file", required=True)
    parser.add_argument("--bind", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--allow-source", required=True)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()

    bind_ip = ipaddress.ip_address(args.bind)
    if bind_ip.version != 4 or bind_ip.is_unspecified:
        parser.error("--bind must be one approved IPv4 host address, not a wildcard")
    args.bind = str(bind_ip)
    source_ip = ipaddress.ip_address(args.allow_source)
    if source_ip.version != 4:
        parser.error("--allow-source must be one IPv4 address")
    args.allow_source = str(source_ip)
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    if Path(args.file).name != args.file or not args.file.endswith(".tgz"):
        parser.error("--file must be one basename ending in .tgz")
    digest = args.expected_sha256.lower()
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        parser.error("--expected-sha256 must be 64 hexadecimal characters")
    args.expected_sha256 = digest
    return args


def validate_webroot(args: argparse.Namespace) -> tuple[Path, os.stat_result, str]:
    root = args.root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("--root must be a directory")
    entries = list(root.iterdir())
    target = root / args.file
    if (
        len(entries) != 1
        or entries[0] != target
        or target.is_symlink()
        or not target.is_file()
    ):
        raise ValueError("webroot must contain exactly one regular, non-symlink file")
    target_stat = target.stat()
    digest = file_sha256(target)
    if digest != args.expected_sha256:
        raise ValueError("bundle SHA-256 does not match --expected-sha256")
    return target, target_stat, digest


def event(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def handler_factory(
    target: Path,
    original_stat: os.stat_result,
    allowed_source: str,
) -> type[http.server.BaseHTTPRequestHandler]:
    expected_path = f"/{urllib.parse.quote(target.name)}"

    class BundleHandler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def current_target(self) -> os.stat_result:
            current = target.stat(follow_symlinks=False)
            if (
                not stat.S_ISREG(current.st_mode)
                or current.st_dev != original_stat.st_dev
                or current.st_ino != original_stat.st_ino
                or current.st_size != original_stat.st_size
            ):
                raise OSError("bundle changed after startup validation")
            return current

        def reject(self, status: int, label: str) -> None:
            self.send_response(status)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            event(
                f"{label} source={self.client_address[0]} "
                f"path={urllib.parse.urlsplit(self.path).path} status={status}"
            )

        def authorize(self) -> bool:
            if self.client_address[0] != allowed_source:
                self.reject(403, "DENY")
                return False
            request_path = urllib.parse.urlsplit(self.path).path
            if request_path != expected_path:
                self.reject(404, "NOT_FOUND")
                return False
            return True

        def send_bundle_headers(self, length: int) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/gzip")
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()

        def do_HEAD(self) -> None:
            if not self.authorize():
                return
            try:
                current = self.current_target()
            except OSError:
                self.reject(503, "CHANGED")
                return
            self.send_bundle_headers(current.st_size)
            self.close_connection = True
            event(
                f"HEAD source={self.client_address[0]} "
                f"path={expected_path} bytes={current.st_size}"
            )

        def do_GET(self) -> None:
            if not self.authorize():
                return
            try:
                current = self.current_target()
            except OSError:
                self.reject(503, "CHANGED")
                return
            self.send_bundle_headers(current.st_size)
            sent = 0
            try:
                with target.open("rb") as source:
                    for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
                        self.wfile.write(chunk)
                        sent += len(chunk)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
                event(
                    f"INCOMPLETE source={self.client_address[0]} "
                    f"path={expected_path} bytes={sent} expected={current.st_size}"
                )
                self.close_connection = True
                return
            self.close_connection = True
            event(
                f"COMPLETE source={self.client_address[0]} "
                f"path={expected_path} bytes={sent}"
            )

    return BundleHandler


def main() -> int:
    args = parse_args()
    try:
        target, target_stat, digest = validate_webroot(args)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    handler = handler_factory(target, target_stat, args.allow_source)
    server = http.server.ThreadingHTTPServer((args.bind, args.port), handler)
    actual_port = server.server_address[1]
    event(
        f"READY bind={args.bind} port={actual_port} path=/{target.name} "
        f"bytes={target_stat.st_size} sha256={digest} allow_source={args.allow_source}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
