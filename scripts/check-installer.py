#!/usr/bin/env python3
"""Exercise installer inventory and family selection in disposable directories."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"
MANIFEST = ROOT / "skills" / "inventory.json"


def load_expected_families() -> dict[str, set[str]]:
    """Load families from the authoritative inventory manifest."""
    with MANIFEST.open(encoding="utf-8") as f:
        inventory = json.load(f)
    families: dict[str, set[str]] = {}
    for skill in inventory:
        family = skill["family"]
        families.setdefault(family, set()).add(skill["name"])
    return families


EXPECTED_FAMILIES = load_expected_families()
EXPECTED_ALL = set().union(*EXPECTED_FAMILIES.values())


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(INSTALLER), *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def installed_names(directory: Path) -> set[str]:
    return {path.name for path in directory.iterdir() if path.is_dir()}


def assert_installed_artifacts(
    destination: Path,
    skill_names: set[str],
    context: str,
) -> None:
    for name in skill_names:
        required_paths = [
            Path("SKILL.md"),
            Path("references/runtime-intake.md"),
        ]
        source_ui = ROOT / "skills" / name / "agents" / "openai.yaml"
        if source_ui.is_file():
            required_paths.append(Path("agents/openai.yaml"))
        for relative_path in required_paths:
            installed_path = destination / name / relative_path
            if not installed_path.is_file():
                raise SystemExit(
                    f"{context}: missing installed {relative_path} for {name}"
                )
            source_path = ROOT / "skills" / name / relative_path
            if installed_path.read_bytes() != source_path.read_bytes():
                raise SystemExit(
                    f"{context}: content mismatch for installed "
                    f"{relative_path} for {name}"
                )


def main() -> int:
    package_names = {
        path.parent.name
        for path in (ROOT / "skills").glob("*/SKILL.md")
    }
    if EXPECTED_ALL != package_names:
        raise SystemExit(
            "package/installer expected inventory mismatch: "
            f"{sorted(EXPECTED_ALL ^ package_names)}"
        )

    inventory = run("--list").stdout
    listed = {
        line.removeprefix("  - ")
        for line in inventory.splitlines()
        if line.startswith("  - ")
    }
    if listed != EXPECTED_ALL:
        raise SystemExit(f"inventory mismatch: {sorted(listed ^ EXPECTED_ALL)}")
    if listed != package_names:
        raise SystemExit(
            f"installer/package inventory mismatch: {sorted(listed ^ package_names)}"
        )

    for family, expected in EXPECTED_FAMILIES.items():
        with tempfile.TemporaryDirectory(prefix=f"fwskills-{family}-") as temp:
            destination = Path(temp)
            run("--family", family, "--dir", str(destination), "--yes", "--force")
            actual = installed_names(destination)
            if actual != expected:
                raise SystemExit(f"{family} install mismatch: {sorted(actual ^ expected)}")
            assert_installed_artifacts(
                destination,
                expected,
                f"{family} family",
            )

    for name in sorted(EXPECTED_ALL):
        with tempfile.TemporaryDirectory(
            prefix=f"fwskills-explicit-{name}-"
        ) as temp:
            destination = Path(temp)
            run("--skill", name, "--dir", str(destination), "--yes", "--force")
            actual = installed_names(destination)
            if actual != {name}:
                raise SystemExit(
                    f"explicit {name} install mismatch: "
                    f"{sorted(actual ^ {name})}"
                )
            assert_installed_artifacts(
                destination,
                {name},
                f"explicit {name}",
            )

    with tempfile.TemporaryDirectory(prefix="fwskills-unknown-family-") as temp:
        destination = Path(temp)
        unknown = run(
            "--family",
            "not-a-family",
            "--dir",
            str(destination),
            "--yes",
            check=False,
        )
        if unknown.returncode == 0 or "Unknown family" not in unknown.stderr:
            raise SystemExit("unknown installer family was not rejected")
        if any(destination.iterdir()):
            raise SystemExit("unknown installer family wrote to its destination")

    # --all -y --dir <tmp> installs exactly 29 skills
    with tempfile.TemporaryDirectory(prefix="fwskills-all-") as temp:
        destination = Path(temp)
        result = run("--all", "-y", "--dir", str(destination))
        actual = installed_names(destination)
        if len(actual) != len(EXPECTED_ALL):
            raise SystemExit(
                f"--all installed {len(actual)} skills; expected {len(EXPECTED_ALL)}"
            )
        if actual != EXPECTED_ALL:
            raise SystemExit(f"--all install mismatch: {sorted(actual ^ EXPECTED_ALL)}")
        assert_installed_artifacts(
            destination,
            EXPECTED_ALL,
            "--all installation",
        )

    # Invalid --family is rejected
    with tempfile.TemporaryDirectory(prefix="fwskills-invalid-family-") as temp:
        destination = Path(temp)
        invalid_family = run(
            "--family",
            "bogus",
            "-y",
            "--dir",
            str(destination),
            check=False,
        )
        if invalid_family.returncode == 0:
            raise SystemExit("--family bogus was accepted (expected rejection)")
        if "Unknown family" not in invalid_family.stderr:
            raise SystemExit(
                f"--family bogus rejection lacked expected message; "
                f"got: {invalid_family.stderr}"
            )

    # Invalid --skill is rejected.
    #
    # --dir is mandatory here even though nothing should be written: with -y
    # and no --dir the installer targets the caller's real ~/.claude/skills,
    # and if this rejection ever regresses to leaving the selection empty the
    # non-interactive fallback installs all 29 skills there before the
    # assertion below runs. A rejection test must not rely on the behaviour it
    # is testing to stay off the workstation. AGENTS.md: installation tests
    # must target disposable paths.
    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_skill = run(
            "--skill",
            "not-a-real-skill",
            "-y",
            "--dir",
            tmpdir,
            check=False,
        )
        if list(Path(tmpdir).iterdir()):
            raise SystemExit(
                "--skill not-a-real-skill wrote into the target directory"
            )
    if invalid_skill.returncode == 0:
        raise SystemExit("--skill not-a-real-skill was accepted (expected rejection)")
    if "Unknown skill" not in invalid_skill.stderr:
        raise SystemExit(
            f"--skill rejection lacked expected message; "
            f"got: {invalid_skill.stderr}"
        )

    # --uninstall removes what --all installed
    with tempfile.TemporaryDirectory(prefix="fwskills-uninstall-") as temp:
        destination = Path(temp)
        run("--all", "-y", "--dir", str(destination))
        installed = installed_names(destination)
        if len(installed) != len(EXPECTED_ALL):
            raise SystemExit(
                f"pre-uninstall check: installed {len(installed)} skills; "
                f"expected {len(EXPECTED_ALL)}"
            )
        run("--all", "--uninstall", "-y", "--dir", str(destination))
        remaining = installed_names(destination)
        if remaining:
            raise SystemExit(
                f"--uninstall --all left {len(remaining)} skills: {sorted(remaining)}"
            )

    print(
        "OK: installer/package inventories match; installer lists and installs "
        "29 skills with byte-identical required artifacts across 5 families "
        "and explicit selections; rejects invalid families and skills; "
        "uninstalls correctly"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
