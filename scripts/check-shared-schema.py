#!/usr/bin/env python3
"""Verify duplicated parsing intermediate-schema.md files stay in sync."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATHS = sorted(ROOT.glob("skills/parsing-*/references/intermediate-schema.md"))


def main() -> int:
    if len(SCHEMA_PATHS) != 4:
        print(f"Expected 4 parsing schema files, found {len(SCHEMA_PATHS)}", file=sys.stderr)
        for path in SCHEMA_PATHS:
            print(path.relative_to(ROOT), file=sys.stderr)
        return 2

    digests = {}
    for path in SCHEMA_PATHS:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        digests.setdefault(digest, []).append(path)

    if len(digests) == 1:
        digest = next(iter(digests))
        print(f"OK: all {len(SCHEMA_PATHS)} intermediate-schema.md files match ({digest[:12]})")
        return 0

    print("ERROR: intermediate-schema.md copies differ", file=sys.stderr)
    for digest, paths in digests.items():
        print(f"{digest[:12]}:", file=sys.stderr)
        for path in paths:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
    print("\nCanonical edit copy: skills/parsing-srx-configs/references/intermediate-schema.md", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
