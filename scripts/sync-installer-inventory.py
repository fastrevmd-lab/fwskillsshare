#!/usr/bin/env python3
"""Sync install.sh skill arrays from the authoritative inventory manifest.

This generator keeps install.sh's embedded skill arrays in sync with
skills/inventory.json. The arrays must be embedded because install.sh works
standalone (curl | bash) before any repo exists on disk, and jq is not
guaranteed on all platforms.

Usage:
    python3 scripts/sync-installer-inventory.py         # regenerate in place
    python3 scripts/sync-installer-inventory.py --check # exit non-zero on drift
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills" / "inventory.json"
INSTALLER = ROOT / "install.sh"

BEGIN_MARKER = "# BEGIN generated-inventory"
END_MARKER = "# END generated-inventory"


def load_inventory() -> dict[str, list[str]]:
    """Load skills grouped by family, preserving manifest order."""
    with MANIFEST.open(encoding="utf-8") as f:
        entries = json.load(f)

    families: dict[str, list[str]] = {}
    for entry in entries:
        family = entry["family"]
        families.setdefault(family, []).append(entry["name"])
    return families


def format_bash_array(var_name: str, skills: list[str]) -> str:
    """Generate a bash array declaration matching install.sh formatting."""
    lines = [f"declare -a {var_name}=("]
    for skill in skills:
        lines.append(f'    "{skill}"')
    lines.append(")")
    return "\n".join(lines)


def generate_arrays(families: dict[str, list[str]]) -> str:
    """Generate all five family array declarations."""
    # Map family names to variable names, preserving the exact order in install.sh
    family_vars = [
        ("parsers", "PARSERS"),
        ("srx", "SRX"),
        ("tooling", "TOOLING"),
        ("compliance", "COMPLIANCE"),
        ("deployment", "DEPLOYMENT"),
    ]

    blocks = []
    for family_key, var_name in family_vars:
        skills = families.get(family_key, [])
        blocks.append(format_bash_array(var_name, skills))

    return "\n\n".join(blocks)


def regenerate_installer(check_only: bool = False) -> int:
    """Regenerate install.sh arrays or check for drift.

    Returns:
        0 if in-sync (or successfully regenerated)
        1 if drift detected (--check mode) or markers not found
    """
    families = load_inventory()
    generated = generate_arrays(families)
    generated_block = f"{BEGIN_MARKER}\n{generated}\n{END_MARKER}"

    content = INSTALLER.read_text(encoding="utf-8")

    # Find marker positions
    begin_pos = content.find(BEGIN_MARKER)
    end_pos = content.find(END_MARKER)

    if begin_pos == -1 or end_pos == -1:
        print(
            f"ERROR: markers not found in {INSTALLER}\n"
            f"Add '{BEGIN_MARKER}' and '{END_MARKER}' around the skill arrays",
            file=sys.stderr,
        )
        return 1

    # Extract current block
    end_of_end_marker = end_pos + len(END_MARKER)
    current_block = content[begin_pos:end_of_end_marker]

    if current_block == generated_block:
        if check_only:
            print(f"OK: {INSTALLER.name} arrays are in sync with {MANIFEST.name}")
        return 0

    if check_only:
        print(f"ERROR: {INSTALLER.name} arrays have drifted from {MANIFEST.name}")
        print("\nExpected:")
        print(generated_block)
        print("\nActual:")
        print(current_block)
        return 1

    # Replace the block
    new_content = content[:begin_pos] + generated_block + content[end_of_end_marker:]
    INSTALLER.write_text(new_content, encoding="utf-8")
    print(f"Regenerated {INSTALLER.name} from {MANIFEST.name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync install.sh skill arrays from skills/inventory.json"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift instead of regenerating; exit 1 if out of sync",
    )
    args = parser.parse_args()

    return regenerate_installer(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
