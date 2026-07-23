#!/usr/bin/env python3
"""Exercise the SRX STIG skill's conservative routing and status contract."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "skills"
    / "srx-disa-stig-compliance"
    / "fixtures"
    / "behavior-cases.json"
)
PINNED_RELEASE = "Y25M01"
PINNED_SHA256 = "9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f"
EVIDENCE_STATES = {
    "missing",
    "partial_failure",
    "complete_failure",
    "complete_satisfaction",
    "complete_inapplicable",
    "stale",
    "ambiguous",
    "unsupported",
}


def route_profiles(roles: dict[str, bool | None]) -> tuple[list[str], list[str]]:
    profiles = ["NDM", "ALG"]
    gaps: list[str] = []
    for role, profile in (("idps", "IDPS"), ("vpn", "VPN")):
        value = roles.get(role)
        if value is True:
            profiles.append(profile)
        elif value is None:
            gaps.append(f"{profile} scope unresolved")
    return profiles, gaps


def decide_status(case: dict[str, Any]) -> str:
    evidence = case["evidence"]
    if evidence not in EVIDENCE_STATES:
        raise ValueError(f"unsupported evidence state: {evidence}")
    if case["implicit_only"]:
        return "Not Reviewed"
    applicable = case["applicable"]
    if applicable is None:
        return "Not Reviewed"
    if applicable is False:
        if case["n_a_allowed"] and evidence == "complete_inapplicable":
            return "Not Applicable"
        return "Not Reviewed"
    if evidence == "complete_failure":
        return "Open"
    if evidence == "complete_satisfaction":
        return "Not a Finding"
    return "Not Reviewed"


def source_result(release: str, digest: str) -> str:
    if release == PINNED_RELEASE and digest == PINNED_SHA256:
        return "valid"
    return "source_validation_failed"


def load_fixture() -> dict[str, Any]:
    try:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot load {FIXTURE.relative_to(ROOT)}: {exc}") from exc


def main() -> int:
    errors: list[str] = []
    fixture = load_fixture()

    for case in fixture["routing_cases"]:
        profiles, gaps = route_profiles(case["roles"])
        if profiles != case["expected_profiles"] or gaps != case["expected_gaps"]:
            errors.append(
                f"routing {case['name']}: got profiles={profiles}, gaps={gaps}"
            )

    for case in fixture["status_cases"]:
        actual = decide_status(case)
        if actual != case["expected"]:
            errors.append(f"status {case['name']}: expected {case['expected']}, got {actual}")

    for case in fixture["source_cases"]:
        actual = source_result(case["release"], case["sha256"])
        if actual != case["expected"]:
            errors.append(f"source {case['name']}: expected {case['expected']}, got {actual}")

    for case in fixture["compatibility_cases"]:
        actual = case["formal_status"]
        if actual != case["expected_status"]:
            errors.append(
                f"compatibility {case['name']}: expected {case['expected_status']}, got {actual}"
            )

    for case in fixture["mutation_cases"]:
        base = dict(case["base"])
        mutant = {**base, **case["mutant"]}
        base_actual = decide_status(base)
        mutant_actual = decide_status(mutant)
        if base_actual != case["base_expected"]:
            errors.append(
                f"mutation {case['name']} base: expected {case['base_expected']}, got {base_actual}"
            )
        if mutant_actual != case["mutant_expected"]:
            errors.append(
                f"mutation {case['name']} mutant: expected {case['mutant_expected']}, got {mutant_actual}"
            )
        if base_actual == mutant_actual:
            errors.append(f"mutation {case['name']}: changed fact did not change status")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        "OK: SRX STIG behavior fixtures cover routing, conservative statuses, "
        "source drift, compatibility separation, and mutations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
