#!/usr/bin/env python3
"""Generate skills/CHECKSUMS.sha256, the SHA-256 manifest install.sh verifies.

Run after any change under skills/ and commit the result.
scripts/check-checksums.py verifies in CI that the manifest matches the tree.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_DIR = ROOT / "skills"
MANIFEST_NAME = "CHECKSUMS.sha256"


def iter_manifest_files(skills_dir: Path):
    for path in sorted(skills_dir.rglob("*")):
        if path.is_file() and path.name != MANIFEST_NAME:
            yield path


def generate(skills_dir: Path) -> str:
    lines = []
    for path in iter_manifest_files(skills_dir):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(skills_dir).as_posix()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=DEFAULT_SKILLS_DIR,
        help="directory to checksum (default: skills/)",
    )
    args = parser.parse_args()

    manifest_path = args.skills_dir / MANIFEST_NAME
    manifest_path.write_text(generate(args.skills_dir), encoding="utf-8")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
