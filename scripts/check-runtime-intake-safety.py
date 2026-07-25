#!/usr/bin/env python3
"""Check runtime-intake plan/package equality and semantic safety regressions."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-24-runtime-intake-questions.md"
)
SKILLS_DIR = ROOT / "skills"
APPENDIX_MARKER = "## Appendix A: Exact question catalogs"
PLAN_SECTION_RE = re.compile(r"^### A\.\d+ `(?P<skill>[^`]+)`$", re.MULTILINE)
PLAN_ROW_RE = re.compile(r"^- `(?P<id>[a-z][a-z0-9_]*)`; ", re.MULTILINE)
PLAN_ROW_CONTENT_RE = re.compile(
    r"header `(?P<header>[^`]+)`; "
    r"ask when (?P<ask_when>.*?); "
    r"question `(?P<question>[^`]+)`; "
    r"options: (?P<options>.*)\."
)
PLAN_OPTION_RE = re.compile(
    r"`(?P<label>[^`]+)` — (?P<description>.*?)"
    r"(?=; `[^`]+` — |\Z)"
)
REFERENCE_CATALOG_RE = re.compile(
    r"```json\n(?P<payload>.*?)\n```",
    re.DOTALL,
)
EXPECTED_SKILLS = (
    "cis-controls-ngfw-compliance",
    "cmmc-nist-800-171-ngfw-compliance",
    "firewall-best-practices-audit",
    "firewall-config-conversion",
    "firewall-config-diff",
    "hipaa-ngfw-compliance",
    "iso27001-ngfw-compliance",
    "parsing-cisco-configs",
    "parsing-fortinet-configs",
    "parsing-palo-configs",
    "parsing-srx-configs",
    "pci-ngfw-compliance",
    "sd-onprem-proxmox-deploy",
    "soc2-ngfw-compliance",
    "srx-advpn",
    "srx-autovpn-full-tunnel",
    "srx-dynamic-ip-feed",
    "srx-ipsec-hub-spoke",
    "srx-mnha",
    "srx-mpls-in-flow",
    "srx-nat",
    "srx-policy",
)

# Appendix A intentionally uses compact "ask when ..." fragments for these
# rows while their exact serialized catalog sentences include the article.
PLAN_ASK_WHEN_THE_IDS = {
    ("firewall-best-practices-audit", "audit_goal"),
    ("firewall-best-practices-audit", "audit_scope"),
    ("firewall-best-practices-audit", "audit_evidence"),
    ("firewall-best-practices-audit", "audit_context"),
    ("firewall-best-practices-audit", "audit_depth"),
    ("firewall-best-practices-audit", "audit_remed"),
    ("parsing-cisco-configs", "cisco_goal"),
    ("parsing-cisco-configs", "cisco_scope"),
    ("parsing-fortinet-configs", "forti_goal"),
    ("parsing-palo-configs", "palo_goal"),
    ("parsing-srx-configs", "srxp_goal"),
    ("pci-ngfw-compliance", "pci_stage"),
    ("pci-ngfw-compliance", "pci_output"),
    ("sd-onprem-proxmox-deploy", "sd_stage"),
    ("sd-onprem-proxmox-deploy", "sd_release"),
    ("sd-onprem-proxmox-deploy", "sd_size"),
    ("sd-onprem-proxmox-deploy", "sd_transfer"),
    ("srx-autovpn-full-tunnel", "autovpn_task"),
    ("srx-dynamic-ip-feed", "dif_task"),
    ("srx-ipsec-hub-spoke", "hsvpn_task"),
    ("srx-ipsec-hub-spoke", "hsvpn_release"),
    ("srx-mnha", "mnha_task"),
    ("srx-mpls-in-flow", "mpls_task"),
    ("srx-mpls-in-flow", "mpls_release"),
    ("srx-mpls-in-flow", "mpls_family"),
    ("srx-mpls-in-flow", "mpls_vrf"),
    ("srx-mpls-in-flow", "mpls_policy"),
    ("srx-nat", "nat_task"),
    ("srx-nat", "nat_release"),
    ("srx-nat", "nat_family"),
    ("srx-nat", "nat_tuple"),
    ("srx-policy", "policy_task"),
    ("srx-policy", "policy_release"),
    ("srx-policy", "policy_model"),
    ("srx-policy", "policy_flow"),
}

# Final-review regression inventory. Each key is an independently unsafe
# recommended default, and each value is the exact safe first label.
SAFE_FIRST_LABELS = {
    ("cis-controls-ngfw-compliance", "cis_evidence"):
        "Inventory evidence (Recommended)",
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_boundary"):
        "Map boundary first (Recommended)",
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_evidence"):
        "Inventory evidence (Recommended)",
    ("firewall-best-practices-audit", "audit_evidence"):
        "Inventory evidence (Recommended)",
    ("firewall-config-conversion", "convert_release"):
        "Discover first (Recommended)",
    ("firewall-config-conversion", "convert_base"):
        "Inspect target first (Recommended)",
    ("firewall-config-diff", "diff_direction"):
        "Establish baseline first (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_role"):
        "Confirm responsibility (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_scope"):
        "Map ePHI scope (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_evidence"):
        "Inventory evidence (Recommended)",
    ("iso27001-ngfw-compliance", "iso_scope"):
        "Map ISMS scope (Recommended)",
    ("iso27001-ngfw-compliance", "iso_soa"):
        "Inventory SoA first (Recommended)",
    ("iso27001-ngfw-compliance", "iso_basis"):
        "Confirm basis first (Recommended)",
    ("iso27001-ngfw-compliance", "iso_period"):
        "Confirm period first (Recommended)",
    ("parsing-cisco-configs", "cisco_coverage"):
        "Verify first (Recommended)",
    ("parsing-fortinet-configs", "forti_coverage"):
        "Verify first (Recommended)",
    ("parsing-palo-configs", "palo_coverage"):
        "Verify first (Recommended)",
    ("parsing-srx-configs", "srxp_coverage"):
        "Verify first (Recommended)",
    ("pci-ngfw-compliance", "pci_scope"):
        "Map CDE scope (Recommended)",
    ("pci-ngfw-compliance", "pci_segment"):
        "Verify segmentation (Recommended)",
    ("pci-ngfw-compliance", "pci_evidence"):
        "Inventory evidence (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_release"):
        "Discover first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_media"):
        "Verify media first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_proxmox"):
        "Inspect/select values (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_network"):
        "Map network first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_services"):
        "Verify services first (Recommended)",
    ("soc2-ngfw-compliance", "soc2_period"):
        "Confirm period first (Recommended)",
    ("soc2-ngfw-compliance", "soc2_system"):
        "Map system first (Recommended)",
    ("soc2-ngfw-compliance", "soc2_vendor"):
        "Inventory vendors first (Recommended)",
    ("srx-advpn", "advpn_release"):
        "Discover first (Recommended)",
    ("srx-advpn", "advpn_topo"):
        "Map topology first (Recommended)",
    ("srx-advpn", "advpn_auth"):
        "Inventory authentication (Recommended)",
    ("srx-advpn", "advpn_evidence"):
        "Inventory evidence (Recommended)",
    ("srx-autovpn-full-tunnel", "autovpn_release"):
        "Discover first (Recommended)",
    ("srx-autovpn-full-tunnel", "autovpn_lans"):
        "Map LANs first (Recommended)",
    ("srx-autovpn-full-tunnel", "autovpn_nat"):
        "Trace NAT first (Recommended)",
    ("srx-autovpn-full-tunnel", "autovpn_route"):
        "Inspect routes first (Recommended)",
    ("srx-autovpn-full-tunnel", "autovpn_evidence"):
        "Inventory evidence (Recommended)",
    ("srx-dynamic-ip-feed", "dif_release"):
        "Discover first (Recommended)",
    ("srx-dynamic-ip-feed", "dif_source"):
        "Inspect source first (Recommended)",
    ("srx-dynamic-ip-feed", "dif_auth"):
        "Verify endpoint first (Recommended)",
    ("srx-dynamic-ip-feed", "dif_route"):
        "Trace route first (Recommended)",
    ("srx-ipsec-hub-spoke", "hsvpn_release"):
        "Discover first (Recommended)",
    ("srx-ipsec-hub-spoke", "hsvpn_topo"):
        "Map topology first (Recommended)",
    ("srx-ipsec-hub-spoke", "hsvpn_route"):
        "Inspect routes first (Recommended)",
    ("srx-ipsec-hub-spoke", "hsvpn_evidence"):
        "Inventory evidence (Recommended)",
    ("srx-mnha", "mnha_release"):
        "Discover first (Recommended)",
    ("srx-mnha", "mnha_migrate"):
        "Inspect starting state (Recommended)",
    ("srx-mnha", "mnha_topo"):
        "Map topology first (Recommended)",
    ("srx-mpls-in-flow", "mpls_release"):
        "Discover first (Recommended)",
    ("srx-mpls-in-flow", "mpls_role"):
        "Confirm role first (Recommended)",
    ("srx-mpls-in-flow", "mpls_signal"):
        "Inspect signaling first (Recommended)",
    ("srx-mpls-in-flow", "mpls_vrf"):
        "Inventory VRFs first (Recommended)",
    ("srx-nat", "nat_release"):
        "Discover first (Recommended)",
    ("srx-nat", "nat_tuple"):
        "Trace tuple first (Recommended)",
    ("srx-nat", "nat_context"):
        "Inspect context first (Recommended)",
    ("srx-nat", "nat_reach"):
        "Trace reachability first (Recommended)",
    ("srx-nat", "nat_return"):
        "Unknown—trace first (Recommended)",
    ("srx-nat", "nat_evidence"):
        "Inventory evidence (Recommended)",
    ("srx-policy", "policy_release"):
        "Discover first (Recommended)",
    ("srx-policy", "policy_flow"):
        "Map flow first (Recommended)",
    ("srx-policy", "policy_nat"):
        "Trace first (Recommended)",
}

# These final-review findings require exact, single-axis option sets, not only a
# safe first label.
EXACT_OPTION_LABELS = {
    ("firewall-best-practices-audit", "audit_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("sd-onprem-proxmox-deploy", "sd_stage"): (
        "Plan/dry-run (Recommended)",
        "Prepare fresh deployment",
        "Troubleshoot existing",
    ),
    ("sd-onprem-proxmox-deploy", "sd_proxmox"): (
        "Inspect/select values (Recommended)",
        "Use supplied new-VM values",
        "Validate existing VM",
    ),
    ("srx-advpn", "advpn_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("srx-autovpn-full-tunnel", "autovpn_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("srx-dynamic-ip-feed", "dif_source"): (
        "Inspect source first (Recommended)",
        "Use supplied endpoint",
        "Design new endpoint",
    ),
    ("srx-ipsec-hub-spoke", "hsvpn_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("srx-mnha", "mnha_service"): (
        "Firewall/NAT only (Recommended)",
        "Firewall/NAT plus IPsec",
        "Advanced/mixed bundle",
    ),
    ("srx-mpls-in-flow", "mpls_service"): (
        "Base policy only (Recommended)",
        "Base plus app/NAT",
        "Full inspection stack",
    ),
    ("srx-nat", "nat_family"): (
        "Identify family first (Recommended)",
        "NAT44",
        "NAT64",
    ),
    ("srx-nat", "nat_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("srx-policy", "policy_service"): (
        "Base policy only (Recommended)",
        "Base plus app/NAT",
        "Full inspection stack",
    ),
    ("srx-policy", "policy_ip"): (
        "Dual-stack unicast (Recommended)",
        "IPv4-only unicast",
        "Unicast plus special",
    ),
    ("srx-policy", "policy_session"): (
        "Leave existing sessions (Recommended)",
        "Clear targeted sessions",
        "Maintenance-window reset",
    ),
}


def sentence(value: str) -> str:
    """Convert the plan's sentence fragment notation to serialized text."""
    value = value.strip()
    return value[:1].upper() + value[1:] + "."


def parse_plan_row(skill: str, question_id: str, raw_row: str) -> dict[str, object]:
    flat_row = " ".join(raw_row.split())
    match = PLAN_ROW_CONTENT_RE.fullmatch(flat_row)
    if not match:
        raise ValueError(
            f"{PLAN_PATH}: cannot parse Appendix A row {skill}/{question_id}"
        )

    option_matches = list(PLAN_OPTION_RE.finditer(match.group("options")))
    if len(option_matches) not in (2, 3):
        raise ValueError(
            f"{PLAN_PATH}: {skill}/{question_id} has "
            f"{len(option_matches)} parseable options"
        )

    ask_when = match.group("ask_when")
    if (skill, question_id) in PLAN_ASK_WHEN_THE_IDS:
        ask_when = f"the {ask_when}"

    return {
        "id": question_id,
        "ask_when": sentence(ask_when),
        "header": match.group("header"),
        "question": match.group("question"),
        "options": [
            {
                "label": option.group("label"),
                "description": sentence(option.group("description")),
            }
            for option in option_matches
        ],
    }


def parse_plan_catalogs() -> dict[str, list[dict[str, object]]]:
    text = PLAN_PATH.read_text(encoding="utf-8")
    if APPENDIX_MARKER not in text:
        raise ValueError(f"{PLAN_PATH}: missing {APPENDIX_MARKER!r}")
    appendix = text[text.index(APPENDIX_MARKER) :]
    sections = list(PLAN_SECTION_RE.finditer(appendix))
    catalogs: dict[str, list[dict[str, object]]] = {}

    for index, section in enumerate(sections):
        skill = section.group("skill")
        body_end = (
            sections[index + 1].start() if index + 1 < len(sections) else len(appendix)
        )
        body = appendix[section.end() : body_end]
        rows = list(PLAN_ROW_RE.finditer(body))
        catalogs[skill] = []
        for row_index, row in enumerate(rows):
            row_end = (
                rows[row_index + 1].start()
                if row_index + 1 < len(rows)
                else len(body)
            )
            raw_row = body[row.end() : row_end].strip()
            catalogs[skill].append(
                parse_plan_row(skill, row.group("id"), raw_row)
            )

    if tuple(catalogs) != EXPECTED_SKILLS:
        raise ValueError(
            f"{PLAN_PATH}: expected Appendix A skills {EXPECTED_SKILLS!r}, "
            f"found {tuple(catalogs)!r}"
        )
    return catalogs


def parse_reference_catalogs() -> dict[str, list[dict[str, object]]]:
    catalogs: dict[str, list[dict[str, object]]] = {}
    for skill in EXPECTED_SKILLS:
        path = SKILLS_DIR / skill / "references" / "runtime-intake.md"
        text = path.read_text(encoding="utf-8")
        matches = list(REFERENCE_CATALOG_RE.finditer(text))
        if len(matches) != 1:
            raise ValueError(f"{path}: expected exactly one JSON catalog")
        try:
            payload = json.loads(matches[0].group("payload"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON catalog: {exc}") from exc
        questions = payload.get("questions") if isinstance(payload, dict) else None
        if not isinstance(questions, list):
            raise ValueError(f"{path}: questions must be a list")
        catalogs[skill] = questions
    return catalogs


def build_question_index(
    catalogs: dict[str, list[dict[str, object]]],
) -> dict[tuple[str, str], list[dict[str, object]]]:
    index: dict[tuple[str, str], list[dict[str, object]]] = {}
    for skill, questions in catalogs.items():
        for question in questions:
            question_id = question.get("id")
            if isinstance(question_id, str):
                index.setdefault((skill, question_id), []).append(question)
    return index


def equality_error(
    skill: str,
    plan_questions: list[dict[str, object]],
    reference_questions: list[dict[str, object]],
) -> str:
    plan_json = json.dumps(plan_questions, indent=2, ensure_ascii=False).splitlines()
    reference_json = json.dumps(
        reference_questions, indent=2, ensure_ascii=False
    ).splitlines()
    diff = "\n".join(
        difflib.unified_diff(
            plan_json,
            reference_json,
            fromfile=f"plan:{skill}",
            tofile=f"reference:{skill}",
            lineterm="",
        )
    )
    return f"{skill}: Appendix A/reference catalog mismatch\n{diff}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?", choices=EXPECTED_SKILLS)
    args = parser.parse_args()

    try:
        plan_catalogs = parse_plan_catalogs()
        reference_catalogs = parse_reference_catalogs()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors: list[str] = []
    plan_index = build_question_index(plan_catalogs)
    reference_index = build_question_index(reference_catalogs)
    manifest_keys = set(SAFE_FIRST_LABELS) | set(EXACT_OPTION_LABELS)

    for key in sorted(manifest_keys):
        for source, index in (
            ("Appendix A", plan_index),
            ("package references", reference_index),
        ):
            resolved = len(index.get(key, []))
            if resolved != 1:
                errors.append(
                    f"{key[0]}/{key[1]}: safety manifest key resolves "
                    f"{resolved} times in {source}, expected exactly once"
                )

    selected_skills = (args.skill,) if args.skill else EXPECTED_SKILLS
    for skill in selected_skills:
        plan_questions = plan_catalogs[skill]
        reference_questions = reference_catalogs[skill]
        if plan_questions != reference_questions:
            errors.append(equality_error(skill, plan_questions, reference_questions))

    for (skill, question_id), expected_label in SAFE_FIRST_LABELS.items():
        if skill not in selected_skills:
            continue
        matches = reference_index.get((skill, question_id), [])
        if len(matches) != 1:
            continue
        options = matches[0].get("options")
        actual_label = (
            options[0].get("label")
            if isinstance(options, list)
            and options
            and isinstance(options[0], dict)
            else None
        )
        if actual_label != expected_label:
            errors.append(
                f"{skill}/{question_id}: unsafe recommended label "
                f"{actual_label!r}; expected {expected_label!r}"
            )

    for (skill, question_id), expected_labels in EXACT_OPTION_LABELS.items():
        if skill not in selected_skills:
            continue
        matches = reference_index.get((skill, question_id), [])
        if len(matches) != 1:
            continue
        options = matches[0].get("options")
        actual_labels = (
            tuple(
                option.get("label") if isinstance(option, dict) else None
                for option in options
            )
            if isinstance(options, list)
            else ()
        )
        if actual_labels != expected_labels:
            errors.append(
                f"{skill}/{question_id}: overlapping or mixed-axis labels "
                f"{actual_labels!r}; expected {expected_labels!r}"
            )

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    scoped = f" for {args.skill}" if args.skill else ""
    print(
        f"OK: {len(EXPECTED_SKILLS)} plan/reference catalogs{scoped}; "
        f"{len(SAFE_FIRST_LABELS)} safe defaults; "
        f"{len(EXACT_OPTION_LABELS)} exact option tuples"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
