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
        "parsing-fortinet-configs",
        "parsing-palo-configs",
        "parsing-srx-configs",
    },
    "srx": {
        "srx-advpn",
        "srx-autovpn-full-tunnel",
        "srx-dynamic-ip-feed",
        "srx-ipsec-hub-spoke",
        "srx-mnha",
        "srx-mpls-in-flow",
        "srx-nat",
        "srx-policy",
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


def main() -> int:
    inventory = run("--list").stdout
    listed = {
        line.removeprefix("  - ")
        for line in inventory.splitlines()
        if line.startswith("  - ")
    }
    if listed != EXPECTED_ALL:
        raise SystemExit(f"inventory mismatch: {sorted(listed ^ EXPECTED_ALL)}")

    for family, expected in EXPECTED_FAMILIES.items():
        with tempfile.TemporaryDirectory(prefix=f"fwskills-{family}-") as temp:
            destination = Path(temp)
            run("--family", family, "--dir", str(destination), "--yes", "--force")
            actual = installed_names(destination)
            if actual != expected:
                raise SystemExit(f"{family} install mismatch: {sorted(actual ^ expected)}")
            for name in expected:
                if not (destination / name / "SKILL.md").is_file():
                    raise SystemExit(f"{family}: missing installed SKILL.md for {name}")

    unknown = run("--family", "not-a-family", "--dir", "/tmp/unused", "--yes", check=False)
    if unknown.returncode == 0 or "Unknown family" not in unknown.stderr:
        raise SystemExit("unknown installer family was not rejected")

    print("OK: installer lists and installs 22 skills across 4 families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
