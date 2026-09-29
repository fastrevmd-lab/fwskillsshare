#!/usr/bin/env python3
"""Verify skills/CHECKSUMS.sha256 matches the current skills/ tree.

install.sh refuses to install a skill payload that does not match this
manifest byte-for-byte. If this check fails, the manifest has drifted from
skills/ -- regenerate it with scripts/gen-checksums.py and commit the result.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
GEN_SCRIPT = Path(__file__).resolve().parent / "gen-checksums.py"

_SPEC = importlib.util.spec_from_file_location("gen_checksums", GEN_SCRIPT)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot import checksum generator from {GEN_SCRIPT}")
GEN = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(GEN)

MANIFEST_PATH = SKILLS_DIR / GEN.MANIFEST_NAME


def main() -> int:
    if not MANIFEST_PATH.is_file():
        raise SystemExit(
            f"missing {MANIFEST_PATH}; run: python3 scripts/gen-checksums.py"
        )

    expected = GEN.generate(SKILLS_DIR)
    actual = MANIFEST_PATH.read_text(encoding="utf-8")
    if expected != actual:
        raise SystemExit(
            f"{MANIFEST_PATH} is out of date with skills/. "
            "Run: python3 scripts/gen-checksums.py"
        )

    file_count = sum(1 for _ in GEN.iter_manifest_files(SKILLS_DIR))
    print(f"OK: {MANIFEST_PATH} matches {file_count} files under skills/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
