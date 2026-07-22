#!/usr/bin/env python3
"""Guard the audit contract that separates explicit and implicit policies."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills" / "firewall-best-practices-audit" / "SKILL.md"
CATALOG_PATH = (
    ROOT
    / "skills"
    / "firewall-best-practices-audit"
    / "references"
    / "check-catalog.md"
)

Policy = dict[str, Any]


def partition_policies(
    policies: list[Policy],
) -> tuple[list[Policy], list[Policy], list[Policy]]:
    """Return enabled explicit, disabled explicit, and implicit policies."""
    explicit = [policy for policy in policies if policy.get("_implicit") is not True]
    enabled = [policy for policy in explicit if not policy.get("disabled", False)]
    disabled = [policy for policy in explicit if policy.get("disabled", False)]
    implicit = [policy for policy in policies if policy.get("_implicit") is True]
    return enabled, disabled, implicit


def is_any(values: object) -> bool:
    return isinstance(values, list) and "any" in values


def has_explicit_logged_deny_all(policies: list[Policy]) -> bool:
    """Return whether the enabled explicit tail is a logged deny-all."""
    enabled, _, _ = partition_policies(policies)
    if not enabled:
        return False
    tail = enabled[-1]
    return bool(
        tail.get("action") == "deny"
        and is_any(tail.get("src_addresses"))
        and is_any(tail.get("dst_addresses"))
        and (
            is_any(tail.get("applications"))
            or is_any(tail.get("services"))
        )
        and (tail.get("log_start") is True or tail.get("log_end") is True)
    )


def has_no_explicit_rules(policies: list[Policy]) -> bool:
    """Return whether SEC-EMPTY-POLICYSET should evaluate true."""
    enabled, disabled, _ = partition_policies(policies)
    return not enabled and not disabled


def behavior_errors() -> list[str]:
    errors: list[str] = []
    implicit_default: Policy = {
        "name": "vendor-default-deny",
        "action": "deny",
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "_implicit": True,
    }

    enabled, disabled, implicit = partition_policies([implicit_default])
    if enabled or disabled or implicit != [implicit_default]:
        errors.append("implicit-only fixture was not partitioned away from explicit rules")
    if not has_no_explicit_rules([implicit_default]):
        errors.append("implicit-only fixture did not satisfy explicit-policy emptiness")
    if has_explicit_logged_deny_all([implicit_default]):
        errors.append("implicit default incorrectly satisfied the explicit logged deny-all check")

    allow: Policy = {
        "name": "ALLOW-WEB",
        "action": "allow",
        "_implicit": False,
    }
    disabled_allow: Policy = {
        "name": "OLD-WEB",
        "action": "allow",
        "disabled": True,
        "_implicit": False,
    }
    enabled, disabled, implicit = partition_policies(
        [allow, disabled_allow, implicit_default]
    )
    if [policy["name"] for policy in enabled] != ["ALLOW-WEB"]:
        errors.append("active comparison population includes disabled or implicit rules")
    if [policy["name"] for policy in disabled] != ["OLD-WEB"]:
        errors.append("disabled explicit population is incorrect")
    if implicit != [implicit_default]:
        errors.append("implicit population is incorrect when explicit rules exist")
    if has_no_explicit_rules([allow, disabled_allow, implicit_default]):
        errors.append("explicit policy fixture was incorrectly treated as empty")

    explicit_deny: Policy = {
        "name": "DENY-REST",
        "action": "deny",
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "_implicit": False,
    }
    if not has_explicit_logged_deny_all([allow, explicit_deny, implicit_default]):
        errors.append("enabled explicit logged deny-all was not recognized before implicit default")

    return errors


def documentation_errors() -> list[str]:
    errors: list[str] = []
    requirements = {
        SKILL_PATH: (
            "explicit_rules",
            "enabled_explicit_rules",
            "disabled_explicit_rules",
            "_implicit: true",
            "SEC-EMPTY-POLICYSET",
            "SEC-NO-DENY-ALL",
        ),
        CATALOG_PATH: (
            "explicit_rules",
            "enabled_explicit_rules",
            "disabled_explicit_rules",
            "_implicit: true",
            "effective enforcement",
            "SEC-EMPTY-POLICYSET",
            "SEC-NO-DENY-ALL",
        ),
    }
    for path, required_terms in requirements.items():
        text = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing audit contract term {term!r}")

    catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
    catalog_entry_requirements = {
        "SEC-EMPTY-POLICYSET": ("explicit_rules",),
        "SEC-NO-DENY-ALL": ("enabled_explicit_rules", "effective enforcement"),
        "SEC-SHADOW": ("enabled_explicit_rules",),
        "SEC-REDUNDANT": ("enabled_explicit_rules",),
        "SEC-OVERLAP": ("enabled_explicit_rules",),
        "SEC-DISABLED": ("disabled_explicit_rules",),
    }
    for check_id, required_terms in catalog_entry_requirements.items():
        match = re.search(rf"^- {check_id} — .*?$", catalog_text, re.MULTILINE)
        if not match:
            errors.append(f"{CATALOG_PATH.relative_to(ROOT)}: missing {check_id} entry")
            continue
        entry = match.group(0)
        for term in required_terms:
            if term not in entry:
                errors.append(
                    f"{CATALOG_PATH.relative_to(ROOT)}: {check_id} entry missing {term!r}"
                )

    for entry in re.findall(r"^- (?:SEC|OPS)-.*?$", catalog_text, re.MULTILINE):
        if "security_policies" in entry:
            check_id = entry.split(" —", 1)[0].removeprefix("- ")
            errors.append(
                f"{CATALOG_PATH.relative_to(ROOT)}: {check_id} uses unpartitioned "
                "security_policies"
            )
    return errors


def main() -> int:
    errors = behavior_errors() + documentation_errors()
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1

    print(
        "OK: audit policy contract excludes implicit rules from explicit-rule "
        "checks and preserves effective-default context"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
