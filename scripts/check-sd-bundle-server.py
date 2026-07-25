#!/usr/bin/env python3
"""Exercise the SD bundle-only HTTP server in disposable directories."""

from __future__ import annotations

import hashlib
import socket
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = (
    ROOT
    / "skills"
    / "sd-onprem-proxmox-deploy"
    / "scripts"
    / "serve_bundle.py"
)


def command(root: Path, digest: str) -> list[str]:
    return [
        sys.executable,
        str(SERVER),
        "--root",
        str(root),
        "--file",
        "bundle.tgz",
        "--bind",
        "127.0.0.1",
        "--port",
        "0",
        "--allow-source",
        "127.0.0.1",
        "--expected-sha256",
        digest,
    ]


def read_until(process: subprocess.Popen[str], prefix: str) -> str:
    assert process.stderr is not None
    for _ in range(20):
        line = process.stderr.readline()
        if line.startswith(prefix):
            return line
    raise AssertionError(f"server did not emit {prefix!r}")


def main() -> int:
    payload = b"synthetic encrypted SD bundle\n" * 64
    digest = hashlib.sha256(payload).hexdigest()

    with tempfile.TemporaryDirectory(prefix="sd-bundle-server-") as temp:
        webroot = Path(temp)
        (webroot / "bundle.tgz").write_bytes(payload)
        process = subprocess.Popen(
            command(webroot, digest),
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            ready = read_until(process, "READY ")
            port = int(ready.split("port=", 1)[1].split()[0])
            url = f"http://127.0.0.1:{port}/bundle.tgz"

            with urllib.request.urlopen(url, timeout=5) as response:
                received = response.read()
            if received != payload:
                raise AssertionError("full bundle response did not match source bytes")
            complete = read_until(process, "COMPLETE ")
            if f"bytes={len(payload)}" not in complete:
                raise AssertionError(f"completion log has wrong byte count: {complete}")

            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/kvm-env.ini",
                    timeout=5,
                )
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise
            else:
                raise AssertionError("non-bundle path was served")

            with socket.create_connection(
                ("127.0.0.1", port),
                timeout=5,
                source_address=("127.0.0.2", 0),
            ) as denied:
                denied.sendall(
                    b"GET /bundle.tgz HTTP/1.1\r\n"
                    b"Host: 127.0.0.1\r\n"
                    b"Connection: close\r\n\r\n"
                )
                response = denied.recv(256)
            if b" 403 " not in response:
                raise AssertionError("non-approved source was not denied")
        finally:
            process.terminate()
            process.wait(timeout=5)

    with tempfile.TemporaryDirectory(prefix="sd-bundle-server-extra-") as temp:
        webroot = Path(temp)
        (webroot / "bundle.tgz").write_bytes(payload)
        (webroot / "kvm-env.ini").write_text(
            "synthetic-secret=must-not-be-served\n",
            encoding="utf-8",
        )
        rejected = subprocess.run(
            command(webroot, digest),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if rejected.returncode == 0:
            raise AssertionError("server accepted a webroot containing an extra file")
        if "exactly one regular, non-symlink file" not in rejected.stderr:
            raise AssertionError(f"unexpected rejection: {rejected.stderr}")

    print("OK: bundle server enforces file/source boundary and completion bytes (5 checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
