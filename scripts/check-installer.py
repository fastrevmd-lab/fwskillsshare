#!/usr/bin/env python3
"""Exercise installer inventory and family selection in disposable directories."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"
EXPECTED_FAMILIES = {
    "parsers": {
        "parsing-cisco-configs",
        "parsing-firepower-configs",
        "parsing-fortinet-configs",
        "parsing-palo-configs",
        "parsing-srx-configs",
    },
    "srx": {
        "srx-advpn",
        "srx-autovpn-full-tunnel",
        "srx-chassis-cluster-proxmox",
        "srx-dynamic-ip-feed",
        "srx-ipsec-hub-spoke",
        "srx-initial-setup",
        "srx-license-signature-maintenance",
        "srx-mnha",
        "srx-mpls-in-flow",
        "srx-nat",
        "srx-policy",
        "srx-syslog-logging",
    },
    "tooling": {
        "firewall-best-practices-audit",
        "firewall-config-conversion",
        "firewall-config-diff",
    },
    "compliance": {
        "cis-controls-ngfw-compliance",
        "cmmc-nist-800-171-ngfw-compliance",
        "hipaa-ngfw-compliance",
        "iso27001-ngfw-compliance",
        "pci-ngfw-compliance",
        "soc2-ngfw-compliance",
        "srx-disa-stig-compliance",
    },
    "deployment": {
        "clearpass-proxmox-deploy",
        "sd-onprem-proxmox-deploy",
    },
}
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

    print(
        "OK: installer/package inventories match; installer lists and installs "
        "29 skills with byte-identical required artifacts across 5 families "
        "and explicit selections"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
