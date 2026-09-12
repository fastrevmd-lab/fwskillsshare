#!/usr/bin/env python3
"""Validate the skill inventory manifest against actual files and documentation."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills" / "inventory.json"
SKILLS_DIR = ROOT / "skills"
INSTALLER = ROOT / "install.sh"
README = ROOT / "README.md"


def load_manifest() -> list[dict[str, str | bool]]:
    """Load and return the inventory manifest."""
    with MANIFEST.open(encoding="utf-8") as f:
        return json.load(f)


def get_actual_skills() -> set[str]:
    """Return skill names that exist on disk."""
    return {
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }


def get_installer_families() -> dict[str, set[str]]:
    """Extract family arrays from install.sh."""
    installer_text = INSTALLER.read_text(encoding="utf-8")
    families = {}

    # Match bash arrays like: declare -a PARSERS=( "name1" "name2" ... )
    family_pattern = re.compile(
        r'declare -a (\w+)=\(\s*((?:"[^"]+"\s*)+)\)',
        re.MULTILINE | re.DOTALL
    )

    for match in family_pattern.finditer(installer_text):
        family_var = match.group(1).lower()
        skills_text = match.group(2)
        skills = re.findall(r'"([^"]+)"', skills_text)
        families[family_var] = set(skills)

    return families




def get_installer_help_total() -> int | None:
    """Extract the total skill count from install.sh --help output."""
    result = subprocess.run(
        [str(INSTALLER), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    match = re.search(r'Select all (\d+) skills', result.stdout)
    return int(match.group(1)) if match else None


def get_readme_reviewed_count() -> tuple[int | None, int | None, int | None, int | None]:
    """Extract reviewed and total counts from the README badge and body.

    Returns: (badge_reviewed, badge_total, body_reviewed, body_total)
    """
    readme_text = README.read_text(encoding="utf-8")

    # Badge: reviewed-26%2F29
    badge_match = re.search(r'reviewed-(\d+)%2F(\d+)', readme_text)
    badge_reviewed = int(badge_match.group(1)) if badge_match else None
    badge_total = int(badge_match.group(2)) if badge_match else None

    # Body: "26 of the 29 packages"
    body_match = re.search(r'(\d+) of the (\d+) packages', readme_text)
    body_reviewed = int(body_match.group(1)) if body_match else None
    body_total = int(body_match.group(2)) if body_match else None

    return badge_reviewed, badge_total, body_reviewed, body_total


def get_schema_count() -> int:
    """Count intermediate-schema.md files in parsing-* packages."""
    return len(list(ROOT.glob("skills/parsing-*/references/intermediate-schema.md")))


def main() -> int:
    errors: list[str] = []

    # Load manifest
    try:
        manifest = load_manifest()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        errors.append(f"failed to load manifest: {e}")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    # Check for duplicates (must fail with the duplicate named)
    names = [skill["name"] for skill in manifest]
    seen = set()
    duplicates = set()
    for name in names:
        if name in seen:
            duplicates.add(name)
        seen.add(name)

    if duplicates:
        for name in sorted(duplicates):
            errors.append(f"duplicate manifest entry: {name}")

    # Get actual skills on disk
    actual_skills = get_actual_skills()
    manifest_skills = set(names)

    # Check for missing or extra skills
    missing = sorted(manifest_skills - actual_skills)
    extra = sorted(actual_skills - manifest_skills)

    if missing:
        errors.append(f"skills in manifest but not on disk: {', '.join(missing)}")
    if extra:
        errors.append(f"skills on disk but not in manifest: {', '.join(extra)}")

    # Group manifest by family
    manifest_families: dict[str, set[str]] = {}
    for skill in manifest:
        family = skill["family"]
        manifest_families.setdefault(family, set()).add(skill["name"])

    # Check against install.sh families
    installer_families = get_installer_families()

    for family in set(manifest_families.keys()) | set(installer_families.keys()):
        manifest_set = manifest_families.get(family, set())
        installer_set = installer_families.get(family, set())

        if manifest_set != installer_set:
            diff = manifest_set ^ installer_set
            errors.append(
                f"family {family!r} mismatch between manifest and install.sh: {sorted(diff)}"
            )

    # check-installer.py now derives its families from this manifest at runtime,
    # so comparing them would be circular. The install.sh arrays are validated
    # by sync-installer-inventory.py --check (wired into `just lint`), which
    # exits non-zero on drift.

    # Check reviewed count
    reviewed_count = sum(1 for skill in manifest if skill.get("reviewed", False))
    badge_reviewed, badge_total, body_reviewed, body_total = get_readme_reviewed_count()

    if badge_reviewed is not None and reviewed_count != badge_reviewed:
        errors.append(
            f"manifest reviewed count ({reviewed_count}) != README badge ({badge_reviewed})"
        )

    if badge_total is not None and len(manifest) != badge_total:
        errors.append(
            f"manifest total ({len(manifest)}) != README badge total ({badge_total})"
        )

    if body_reviewed is not None and reviewed_count != body_reviewed:
        errors.append(
            f"manifest reviewed count ({reviewed_count}) != README body ({body_reviewed})"
        )

    if body_total is not None and len(manifest) != body_total:
        errors.append(
            f"manifest total ({len(manifest)}) != README body total ({body_total})"
        )

    # Check parser count
    parser_count = sum(1 for skill in manifest if skill["family"] == "parsers")
    parsing_count = sum(1 for skill in manifest if skill["name"].startswith("parsing-"))
    schema_count = get_schema_count()

    if parser_count != parsing_count:
        errors.append(
            f"parsers family count ({parser_count}) != parsing-* skill count ({parsing_count})"
        )

    if parser_count != schema_count:
        errors.append(
            f"parsers family count ({parser_count}) != intermediate-schema.md count ({schema_count})"
        )

    # Check install.sh --help total
    help_total = get_installer_help_total()
    if help_total is not None and len(manifest) != help_total:
        errors.append(
            f"manifest total ({len(manifest)}) != install.sh --help total ({help_total})"
        )

    # Print errors
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(
        f"OK: inventory manifest validated: {len(manifest)} skills, "
        f"{len(manifest_families)} families, {reviewed_count} reviewed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
