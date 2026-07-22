#!/usr/bin/env python3
"""Guard audit policy populations, ordering, deny-all, and NAT-flow coverage."""

from __future__ import annotations

from collections import Counter, defaultdict
from ipaddress import ip_network
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
FOLLOWUP_PATH = (
    ROOT
    / "docs"
    / "skill-tests"
    / "2026-07-22-firewall-best-practices-audit-v1.1-follow-up.md"
)

Policy = dict[str, Any]
NatRule = dict[str, Any]
ContextKey = tuple[str, ...]

DENY_ACTIONS = frozenset({"deny", "drop"})


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


def _single_concrete(values: object) -> str | None:
    if (
        isinstance(values, list)
        and len(values) == 1
        and isinstance(values[0], str)
        and values[0]
        and values[0] != "any"
    ):
        return values[0]
    return None


def _container_key(
    item: Policy | NatRule, source_vendor: str
) -> tuple[str, str] | None:
    if source_vendor == "srx":
        logical_system = item.get("_logical_system")
        tenant = item.get("_tenant")
        if logical_system and tenant:
            return None
        if logical_system is not None:
            return (
                ("logical-system", logical_system)
                if isinstance(logical_system, str) and logical_system
                else None
            )
        if tenant is not None:
            return ("tenant", tenant) if isinstance(tenant, str) and tenant else None
        return ("root", "root")
    if source_vendor == "panos":
        vsys = item.get("_vsys")
        return ("vsys", vsys) if isinstance(vsys, str) and vsys else None
    if source_vendor == "fortigate":
        vdom = item.get("_vdom")
        return ("vdom", vdom) if isinstance(vdom, str) and vdom else None
    if source_vendor == "cisco_asa":
        source_zone = _single_concrete(item.get("src_zones"))
        return ("binding-zone", source_zone) if source_zone else None
    return None


def _evaluation_context_key(policy: Policy, source_vendor: str) -> ContextKey | None:
    container = _container_key(policy, source_vendor)
    if container is None:
        return None
    if source_vendor == "srx":
        src_zone = _single_concrete(policy.get("src_zones"))
        dst_zone = _single_concrete(policy.get("dst_zones"))
        if policy.get("src_zones") == ["any"] and policy.get("dst_zones") == ["any"]:
            return (source_vendor, *container, "1-global")
        if src_zone and dst_zone:
            return (source_vendor, *container, "0-zone-pair", src_zone, dst_zone)
        return None
    if source_vendor in {"panos", "fortigate"}:
        return (source_vendor, *container, "merged-rulebase")
    if source_vendor == "cisco_asa":
        return (source_vendor, *container, "inbound-binding")
    return None


def _rule_index(policy: Policy) -> int | None:
    index = policy.get("_rule_index")
    return (
        index
        if isinstance(index, int) and not isinstance(index, bool) and index > 0
        else None
    )


def _unrestricted(values: object) -> bool:
    return values in (None, "", []) or is_any(values)


def _is_catchall_match(policy: Policy) -> bool:
    return bool(
        is_any(policy.get("src_addresses"))
        and is_any(policy.get("dst_addresses"))
        and (is_any(policy.get("applications")) or is_any(policy.get("services")))
        and policy.get("negate_source") is not True
        and policy.get("negate_destination") is not True
        and _unrestricted(policy.get("schedule"))
        and _unrestricted(policy.get("source_users"))
        and _unrestricted(policy.get("url_categories"))
        and _unrestricted(policy.get("app_groups"))
    )


def _is_logged_deny_all(policy: Policy) -> bool:
    return bool(
        policy.get("action") in DENY_ACTIONS
        and _is_catchall_match(policy)
        and (policy.get("log_start") is True or policy.get("log_end") is True)
    )


def _ordered_population(policies: list[Policy]) -> list[Policy] | None:
    indices = [_rule_index(policy) for policy in policies]
    if any(index is None for index in indices) or len(indices) != len(set(indices)):
        return None
    return sorted(policies, key=lambda policy: _rule_index(policy) or 0)


def _has_reachable_logged_tail(policies: list[Policy]) -> bool:
    ordered = _ordered_population(policies)
    if not ordered or not _is_logged_deny_all(ordered[-1]):
        return False
    return not any(_is_catchall_match(policy) for policy in ordered[:-1])


def has_no_explicit_rules(policies: list[Policy]) -> bool:
    """Return whether SEC-EMPTY-POLICYSET should evaluate true."""
    enabled, disabled, _ = partition_policies(policies)
    return not enabled and not disabled


def comparison_populations(
    policies: list[Policy], source_vendor: str
) -> list[list[Policy]]:
    """Return grounded, ordered vendor evaluation populations."""
    enabled, _, _ = partition_policies(policies)
    grouped: dict[ContextKey, list[Policy]] = defaultdict(list)
    for policy in enabled:
        context = _evaluation_context_key(policy, source_vendor)
        if context is None or _rule_index(policy) is None:
            return []
        grouped[context].append(policy)

    populations: list[list[Policy]] = []
    for context in sorted(grouped):
        ordered = _ordered_population(grouped[context])
        if ordered is not None:
            populations.append(ordered)
    return populations


def context_has_explicit_logged_deny_all(
    policies: list[Policy], source_vendor: str, flow_context: Policy
) -> bool:
    """Return whether the applicable explicit context has a reachable logged tail."""
    enabled, _, _ = partition_policies(policies)
    context = _evaluation_context_key(flow_context, source_vendor)
    if context is None:
        return False

    if source_vendor != "srx":
        applicable = [
            policy
            for policy in enabled
            if _evaluation_context_key(policy, source_vendor) == context
        ]
        return _has_reachable_logged_tail(applicable)

    if "0-zone-pair" not in context:
        global_rules = [
            policy
            for policy in enabled
            if _evaluation_context_key(policy, source_vendor) == context
        ]
        return _has_reachable_logged_tail(global_rules)

    zone_rules = [
        policy
        for policy in enabled
        if _evaluation_context_key(policy, source_vendor) == context
    ]
    if _has_reachable_logged_tail(zone_rules):
        return True
    if any(_is_catchall_match(policy) for policy in zone_rules):
        return False

    global_context = (*context[:3], "1-global")
    global_rules = [
        policy
        for policy in enabled
        if _evaluation_context_key(policy, source_vendor) == global_context
    ]
    return _has_reachable_logged_tail(global_rules)


def _values_overlap(left: object, right: object) -> bool:
    if (
        not isinstance(left, list)
        or not isinstance(right, list)
        or not left
        or not right
    ):
        return False
    if "any" in left or "any" in right:
        return True
    if set(left) & set(right):
        return True
    for left_value in left:
        for right_value in right:
            if not isinstance(left_value, str) or not isinstance(right_value, str):
                continue
            try:
                if ip_network(left_value, strict=False).overlaps(
                    ip_network(right_value, strict=False)
                ):
                    return True
            except ValueError:
                continue
    return False


def _nat_context_is_grounded(nat_rule: NatRule, source_vendor: str) -> bool:
    if _container_key(nat_rule, source_vendor) is None:
        return False
    return bool(
        _single_concrete(nat_rule.get("src_zones"))
        and _single_concrete(nat_rule.get("dst_zones"))
    )


def nat_flow_has_enabled_permit(
    nat_rule: NatRule, policies: list[Policy], source_vendor: str
) -> bool:
    """Return whether a grounded enabled permit can carry part of a NAT flow."""
    if not _nat_context_is_grounded(nat_rule, source_vendor):
        return False
    nat_container = _container_key(nat_rule, source_vendor)
    enabled, _, _ = partition_policies(policies)
    return any(
        policy.get("action") == "allow"
        and _container_key(policy, source_vendor) == nat_container
        and _values_overlap(nat_rule.get("src_zones"), policy.get("src_zones"))
        and _values_overlap(nat_rule.get("dst_zones"), policy.get("dst_zones"))
        and _values_overlap(nat_rule.get("src_addresses"), policy.get("src_addresses"))
        and _values_overlap(nat_rule.get("dst_addresses"), policy.get("dst_addresses"))
        for policy in enabled
    )


def behavior_errors() -> list[str]:
    errors: list[str] = []
    trust_context: Policy = {"src_zones": ["trust"], "dst_zones": ["untrust"]}
    dmz_context: Policy = {"src_zones": ["dmz"], "dst_zones": ["untrust"]}
    implicit_default: Policy = {
        "name": "vendor-default-deny",
        "action": "deny",
        "src_zones": ["any"],
        "dst_zones": ["any"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "_rule_index": 999,
        "_implicit": True,
    }

    enabled, disabled, implicit = partition_policies([implicit_default])
    if enabled or disabled or implicit != [implicit_default]:
        errors.append(
            "implicit-only fixture was not partitioned away from explicit rules"
        )
    if not has_no_explicit_rules([implicit_default]):
        errors.append("implicit-only fixture did not satisfy explicit-policy emptiness")
    if context_has_explicit_logged_deny_all([implicit_default], "srx", trust_context):
        errors.append(
            "implicit default incorrectly satisfied the explicit logged deny-all check"
        )

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
        errors.append(
            "active comparison population includes disabled or implicit rules"
        )
    if [policy["name"] for policy in disabled] != ["OLD-WEB"]:
        errors.append("disabled explicit population is incorrect")
    if implicit != [implicit_default]:
        errors.append("implicit population is incorrect when explicit rules exist")
    if has_no_explicit_rules([allow, disabled_allow, implicit_default]):
        errors.append("explicit policy fixture was incorrectly treated as empty")

    explicit_deny: Policy = {
        "name": "DENY-REST",
        "action": "deny",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "_rule_index": 2,
        "_implicit": False,
    }
    if not context_has_explicit_logged_deny_all(
        [explicit_deny, implicit_default], "srx", trust_context
    ):
        errors.append(
            "enabled explicit logged deny-all was not recognized before implicit default"
        )

    trust_late: Policy = {
        "name": "TRUST-LATE",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "action": "allow",
        "_rule_index": 20,
        "_implicit": False,
    }
    trust_early: Policy = {
        "name": "TRUST-EARLY",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "action": "allow",
        "_rule_index": 10,
        "_implicit": False,
    }
    dmz_rule: Policy = {
        "name": "DMZ-RULE",
        "src_zones": ["dmz"],
        "dst_zones": ["untrust"],
        "action": "allow",
        "_rule_index": 1,
        "_implicit": False,
    }
    global_rule: Policy = {
        "name": "GLOBAL-RULE",
        "src_zones": ["any"],
        "dst_zones": ["any"],
        "action": "deny",
        "_rule_index": 1,
        "_implicit": False,
    }
    populations = comparison_populations(
        [trust_late, dmz_rule, global_rule, trust_early], "srx"
    )
    population_names = [
        [policy["name"] for policy in population] for population in populations
    ]
    expected_population_names = [
        ["DMZ-RULE"],
        ["TRUST-EARLY", "TRUST-LATE"],
        ["GLOBAL-RULE"],
    ]
    if population_names != expected_population_names:
        errors.append(
            "SRX comparison populations were not separated by zone-pair/global "
            "phase and ordered by _rule_index"
        )
    comparison_pairs = {
        frozenset((left["name"], right["name"]))
        for population in populations
        for index, left in enumerate(population)
        for right in population[index + 1 :]
    }
    if comparison_pairs != {frozenset(("TRUST-EARLY", "TRUST-LATE"))}:
        errors.append("comparison families can pair rules from unrelated SRX contexts")

    logical_system_a: Policy = {
        **trust_early,
        "name": "LS-A",
        "_logical_system": "tenant-a",
    }
    logical_system_b: Policy = {
        **trust_late,
        "name": "LS-B",
        "_logical_system": "tenant-b",
    }
    logical_system_names = [
        [policy["name"] for policy in population]
        for population in comparison_populations(
            [logical_system_b, logical_system_a], "srx"
        )
    ]
    if logical_system_names != [["LS-A"], ["LS-B"]]:
        errors.append("SRX comparison populations crossed logical-system containers")

    pan_vsys1_late: Policy = {
        **trust_late,
        "name": "PAN-VSYS1-LATE",
        "_vsys": "vsys1",
    }
    pan_vsys1_early: Policy = {
        **trust_early,
        "name": "PAN-VSYS1-EARLY",
        "_vsys": "vsys1",
    }
    pan_vsys2: Policy = {**dmz_rule, "name": "PAN-VSYS2", "_vsys": "vsys2"}
    pan_names = [
        [policy["name"] for policy in population]
        for population in comparison_populations(
            [pan_vsys1_late, pan_vsys2, pan_vsys1_early], "panos"
        )
    ]
    if pan_names != [["PAN-VSYS1-EARLY", "PAN-VSYS1-LATE"], ["PAN-VSYS2"]]:
        errors.append("PAN-OS comparison populations were not partitioned by _vsys")
    if comparison_populations([trust_early], "panos"):
        errors.append("PAN-OS comparison ran without a grounded _vsys")

    forti_root: Policy = {**trust_early, "name": "FORTI-ROOT", "_vdom": "root"}
    forti_customer: Policy = {
        **trust_late,
        "name": "FORTI-CUSTOMER",
        "_vdom": "customer",
    }
    forti_names = [
        [policy["name"] for policy in population]
        for population in comparison_populations(
            [forti_root, forti_customer], "fortigate"
        )
    ]
    if forti_names != [["FORTI-CUSTOMER"], ["FORTI-ROOT"]]:
        errors.append("FortiGate comparison populations were not partitioned by _vdom")
    if comparison_populations([trust_early], "fortigate"):
        errors.append("FortiGate comparison ran without a grounded _vdom")

    asa_inside: Policy = {
        **trust_early,
        "name": "ASA-INSIDE",
        "src_zones": ["inside"],
    }
    asa_outside: Policy = {
        **trust_late,
        "name": "ASA-OUTSIDE",
        "src_zones": ["outside"],
    }
    asa_names = [
        [policy["name"] for policy in population]
        for population in comparison_populations([asa_outside, asa_inside], "cisco_asa")
    ]
    if asa_names != [["ASA-INSIDE"], ["ASA-OUTSIDE"]]:
        errors.append(
            "Cisco ASA comparison populations were not partitioned by binding zone"
        )
    if comparison_populations([{**trust_early, "src_zones": ["any"]}], "cisco_asa"):
        errors.append("Cisco ASA comparison ran without a grounded binding zone")

    trust_deny: Policy = {
        "name": "TRUST-DENY",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "action": "deny",
        "log_start": True,
        "_rule_index": 10,
        "_implicit": False,
    }
    if context_has_explicit_logged_deny_all([trust_deny], "srx", dmz_context):
        errors.append("zone-scoped deny-all satisfied an unrelated SRX context")

    global_drop: Policy = {
        **trust_deny,
        "name": "GLOBAL-DROP",
        "src_zones": ["any"],
        "dst_zones": ["any"],
        "action": "drop",
        "_rule_index": 30,
    }
    if not context_has_explicit_logged_deny_all([global_drop], "srx", dmz_context):
        errors.append(
            "logged global drop alias did not satisfy applicable deny-all context"
        )
    if not context_has_explicit_logged_deny_all(
        [dmz_rule, global_drop], "srx", dmz_context
    ):
        errors.append(
            "reachable SRX global fallback was not applied after specific zone rules"
        )

    global_reset: Policy = {
        **global_drop,
        "name": "GLOBAL-RESET",
        "action": "reset-both",
    }
    if context_has_explicit_logged_deny_all([global_reset], "srx", dmz_context):
        errors.append("reset-both was incorrectly treated as a normalized deny alias")

    catchall_allow: Policy = {
        **trust_early,
        "name": "CATCHALL-ALLOW",
        "src_zones": ["dmz"],
        "dst_zones": ["untrust"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "_rule_index": 10,
    }
    global_deny: Policy = {
        **global_drop,
        "name": "GLOBAL-DENY",
        "action": "deny",
    }
    if context_has_explicit_logged_deny_all(
        [catchall_allow, global_deny], "srx", dmz_context
    ):
        errors.append(
            "unreachable global deny incorrectly satisfied a zone catchall context"
        )

    later_allow: Policy = {
        **trust_early,
        "name": "LATER-ALLOW",
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "_rule_index": 20,
    }
    if context_has_explicit_logged_deny_all(
        [later_allow, trust_deny], "srx", trust_context
    ):
        errors.append("deny-all check ignored _rule_index when selecting explicit tail")

    nat_rule: NatRule = {
        "name": "TRUST-OUT",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "src_addresses": ["10.10.0.0/16"],
        "dst_addresses": ["any"],
    }
    deny_only: Policy = {
        **trust_deny,
        "name": "DENY-ONLY",
    }
    if nat_flow_has_enabled_permit(nat_rule, [deny_only], "srx"):
        errors.append("deny-only policy incorrectly covered an intended NAT flow")

    unrelated_allow: Policy = {
        **later_allow,
        "name": "UNRELATED-ALLOW",
        "dst_zones": ["dmz"],
    }
    if nat_flow_has_enabled_permit(nat_rule, [unrelated_allow], "srx"):
        errors.append("unrelated zone policy incorrectly covered an intended NAT flow")

    address_mismatch: Policy = {
        **later_allow,
        "name": "ADDRESS-MISMATCH",
        "src_addresses": ["10.20.0.0/16"],
    }
    if nat_flow_has_enabled_permit(nat_rule, [address_mismatch], "srx"):
        errors.append(
            "address-mismatched policy incorrectly covered an intended NAT flow"
        )

    matching_allow: Policy = {
        **later_allow,
        "name": "MATCHING-ALLOW",
        "src_addresses": ["10.10.0.0/16"],
    }
    if not nat_flow_has_enabled_permit(nat_rule, [matching_allow], "srx"):
        errors.append("enabled matching permit did not cover an intended NAT flow")

    overlapping_allow: Policy = {
        **matching_allow,
        "name": "OVERLAPPING-ALLOW",
        "src_addresses": ["10.10.10.0/24"],
    }
    if not nat_flow_has_enabled_permit(nat_rule, [overlapping_allow], "srx"):
        errors.append(
            "overlapping literal subnet permit did not cover an intended NAT flow"
        )

    disabled_matching_allow: Policy = {
        **matching_allow,
        "name": "DISABLED-MATCHING-ALLOW",
        "disabled": True,
    }
    if nat_flow_has_enabled_permit(nat_rule, [disabled_matching_allow], "srx"):
        errors.append("disabled permit incorrectly covered an intended NAT flow")

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
            "vendor evaluation population",
            "evidence-gap warning",
            "one of `deny` or `drop`",
            "enabled `allow`",
        ),
        CATALOG_PATH: (
            "explicit_rules",
            "enabled_explicit_rules",
            "disabled_explicit_rules",
            "_implicit: true",
            "effective enforcement",
            "SEC-EMPTY-POLICYSET",
            "SEC-NO-DENY-ALL",
            "vendor evaluation population",
            "evidence-gap warning",
            "`deny` or `drop`",
            "enabled explicit `action: allow`",
        ),
    }
    for path, required_terms in requirements.items():
        text = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: missing audit contract term {term!r}"
                )

    catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
    catalog_entry_requirements = {
        "SEC-EMPTY-POLICYSET": ("explicit_rules",),
        "SEC-NO-DENY-ALL": (
            "enabled_explicit_rules",
            "effective enforcement",
            "`deny` or `drop`",
            "_rule_index",
            "global fallback",
        ),
        "SEC-SHADOW": ("enabled_explicit_rules", "vendor evaluation population"),
        "SEC-REDUNDANT": ("enabled_explicit_rules", "vendor evaluation population"),
        "SEC-OVERLAP": ("enabled_explicit_rules", "vendor evaluation population"),
        "SEC-ZONES-NAT-NO-POLICY": (
            "enabled explicit `action: allow`",
            "zone overlap",
            "address overlap",
        ),
        "SEC-DISABLED": ("disabled_explicit_rules",),
        "OPS-CONSOLIDATE": (
            "enabled_explicit_rules",
            "vendor evaluation population",
        ),
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

    followup_text = FOLLOWUP_PATH.read_text(encoding="utf-8")
    followup_terms = (
        "v1.1.4",
        "behavioral regression",
        "comparison populations",
        "`deny`/`drop`",
        "enabled permit",
    )
    for term in followup_terms:
        if term not in followup_text:
            errors.append(
                f"{FOLLOWUP_PATH.relative_to(ROOT)}: missing exact validation claim {term!r}"
            )

    heavy_section = followup_text.split(
        "## Case 2: policy-heavy synthetic SRX fixture", 1
    )[-1].split("### Negative controls, skipped checks, and residuals", 1)[0]
    finding_rows = re.findall(
        r"^\| ((?:SEC|OPS)-[A-Z0-9-]+) \| (Critical|High|Medium|Low|Info) \|",
        heavy_section,
        re.MULTILINE,
    )
    expected_heavy_ids = {
        "SEC-ANY-ANY",
        "SEC-BROAD-SRC",
        "SEC-SHADOW",
        "SEC-EXPOSED-RISKY",
        "SEC-INBOUND-ANY",
        "SEC-BROAD-DST",
        "SEC-OVERLAP",
        "SEC-ORPHAN-REF",
        "SEC-NO-LOG",
        "SEC-NO-DENY-ALL",
        "SEC-REDUNDANT",
        "SEC-LARGE-PORTRANGE",
        "OPS-UNUSED-OBJ",
        "OPS-DUP-OBJ",
        "SEC-DISABLED",
        "SEC-NO-DESC",
        "OPS-NO-DESC-OBJ",
    }
    actual_heavy_ids = [finding_id for finding_id, _ in finding_rows]
    if len(actual_heavy_ids) != len(set(actual_heavy_ids)):
        errors.append(
            f"{FOLLOWUP_PATH.relative_to(ROOT)}: duplicate policy-heavy finding ID"
        )
    if set(actual_heavy_ids) != expected_heavy_ids:
        errors.append(
            f"{FOLLOWUP_PATH.relative_to(ROOT)}: policy-heavy finding table differs "
            "from the behaviorally grounded expected set"
        )

    tally_match = re.search(
        r"\*\*Tally:\*\* Critical (\d+), High (\d+), Medium (\d+), "
        r"Low (\d+), Info (\d+)",
        heavy_section,
    )
    if tally_match is None:
        errors.append(f"{FOLLOWUP_PATH.relative_to(ROOT)}: missing policy-heavy tally")
    else:
        stated_tally = {
            severity: int(count)
            for severity, count in zip(
                ("Critical", "High", "Medium", "Low", "Info"),
                tally_match.groups(),
                strict=True,
            )
        }
        derived_tally = Counter(severity for _, severity in finding_rows)
        if any(
            derived_tally[severity] != count for severity, count in stated_tally.items()
        ):
            errors.append(
                f"{FOLLOWUP_PATH.relative_to(ROOT)}: policy-heavy tally does not "
                "match its finding rows"
            )
    return errors


def main() -> int:
    errors = behavior_errors() + documentation_errors()
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1

    print(
        "OK: audit policy contract partitions vendor evaluation contexts, orders "
        "explicit rules, validates deny-all applicability, and requires NAT-capable permits"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
