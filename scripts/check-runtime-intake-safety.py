#!/usr/bin/env python3
"""Check runtime-intake plan/package equality and semantic safety regressions."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
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
PLAN_SECTION_LOOKALIKE_RE = re.compile(
    r"^(?P<heading> {0,3}###[ \t]+A\.[^\r\n]*)\r?$",
    re.MULTILINE,
)
PLAN_SECTION_IDENTITY_RE = re.compile(
    r"^ {0,3}###[ \t]+A\.(?P<number>\d+)[ \t]+"
    r"`(?P<skill>[^`\r\n]+)`"
)
PLAN_SECTION_RE = re.compile(
    r"^### A\.(?P<number>\d+) `(?P<skill>[^`\r\n]+)`\r?$",
    re.MULTILINE,
)
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
STRUCTURAL_VALIDATOR_PATH = ROOT / "scripts" / "check-runtime-intake.py"
STRUCTURAL_SPEC = importlib.util.spec_from_file_location(
    "runtime_intake_structural_for_safety",
    STRUCTURAL_VALIDATOR_PATH,
)
if STRUCTURAL_SPEC is None or STRUCTURAL_SPEC.loader is None:
    raise RuntimeError(f"cannot import validator from {STRUCTURAL_VALIDATOR_PATH}")
STRUCTURAL_VALIDATOR = importlib.util.module_from_spec(STRUCTURAL_SPEC)
STRUCTURAL_SPEC.loader.exec_module(STRUCTURAL_VALIDATOR)
EXPECTED_CATALOG_SHA256 = {
    "cis-controls-ngfw-compliance":
        "36e3bf588d757c5d4e4eb554383891c68f813cbca8dc0768081afdff0432b9ec",
    "cmmc-nist-800-171-ngfw-compliance":
        "9addc8cdcfc970ea5087d95d640d86b8695837f74ca7afba84a321ce20054fe5",
    "firewall-best-practices-audit":
        "03e0a7b24132a62065b1ce119b2b1974bc97ab477e0ee6ede4e039196a25a030",
    "firewall-config-conversion":
        "7e23567bfc9642f7b9ba7ee7eaba81794bec82932eabf287c315b76c16a90051",
    "firewall-config-diff":
        "7b56f4b51693140bde7ef1d86024563d18285293b6f419238fb45fcb94cc47f9",
    "hipaa-ngfw-compliance":
        "8d55b564d3dc9c3838c0184124d2937e7778c99cf461b65aaab0fdecff25d390",
    "iso27001-ngfw-compliance":
        "0fb97b6ad0948a71824d9dcb198ca1e18230d6a7d8de7242a7068866b5c2ceaf",
    "parsing-cisco-configs":
        "84b72ab585131ffbd2d760728f726dd8516af80f4a73cc3d059169460d28d614",
    "parsing-fortinet-configs":
        "ce7b8f2984a1e41ecf6d8d49251c4c720a6903ff2a80a6d173d550917b0ee549",
    "parsing-palo-configs":
        "699189bdffe2698134b31bf9538b9f82a1a683dd122a0fd7f7fb0d4bb7e8f2eb",
    "parsing-srx-configs":
        "40cd3dffb4a81490c7f4c8d92a22b710f902f1adc76dac0a53c593ceabbece61",
    "pci-ngfw-compliance":
        "be8aa6f3d7d9f9cc0b2bd83df41d8fe085bf82ca1f8b26a05b2a973408a1b3ff",
    "sd-onprem-proxmox-deploy":
        "75add48ae585220170c3386bb464a122a12eca59892d5a7c4c405c33b9d0d5d2",
    "soc2-ngfw-compliance":
        "2d7c045877c37220a6447234844512d594e16b41f0b905c9aa725b10291fceea",
    "srx-advpn":
        "f4f36efedd495e6866cd0d4812aa2876e58a7cc2018c3fcbceb904f7d4847837",
    "srx-autovpn-full-tunnel":
        "5fc2245ccf43ca81f36094e397531f09be9a70ee18d4c3ab711df92b36e18ff6",
    "srx-dynamic-ip-feed":
        "0c7719121c78336c965f515f2c7ecb171a83df9c4e127fbdbcd87ec096c6abca",
    "srx-ipsec-hub-spoke":
        "3e4e0a5f725b58c2d287835690a4d554242ceb7bea3d0e9eb52e6ecbf6129156",
    "srx-mnha":
        "fc6211bafd7849792651d77ae7616dab7a025481514eefe288ad35072bf671d9",
    "srx-mpls-in-flow":
        "786dcf2196762dd1c2fb463dca1492ebf264ef671a352f6b8b74aa4c8b03c240",
    "srx-nat":
        "b656fabb08f40dcbb609cc04f549dc7682a7ce527bd5b9858d7f085fef5b1601",
    "srx-policy":
        "bd080b00c35715d741793dc364fcb682f14f70fedcb294f22e802f7f9b1a288e",
}

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
    ("cis-controls-ngfw-compliance", "cis_scope"):
        "Inventory estate first (Recommended)",
    ("cis-controls-ngfw-compliance", "cis_evidence"):
        "Inventory evidence (Recommended)",
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_basis"):
        "Confirm framework first (Recommended)",
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_overlay"):
        "Inventory overlays first (Recommended)",
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_assets"):
        "Inventory assets first (Recommended)",
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
    ("firewall-config-diff", "diff_ignore"):
        "Stop pending allowlist (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_role"):
        "Confirm responsibility (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_scope"):
        "Map ePHI scope (Recommended)",
    ("hipaa-ngfw-compliance", "hipaa_vendor"):
        "Inventory paths first (Recommended)",
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
    ("parsing-cisco-configs", "cisco_goal"):
        "Confirm depth first (Recommended)",
    ("parsing-cisco-configs", "cisco_coverage"):
        "Verify first (Recommended)",
    ("parsing-fortinet-configs", "forti_goal"):
        "Confirm depth first (Recommended)",
    ("parsing-fortinet-configs", "forti_coverage"):
        "Verify first (Recommended)",
    ("parsing-palo-configs", "palo_goal"):
        "Confirm depth first (Recommended)",
    ("parsing-palo-configs", "palo_coverage"):
        "Verify first (Recommended)",
    ("parsing-srx-configs", "srxp_goal"):
        "Confirm depth first (Recommended)",
    ("parsing-srx-configs", "srxp_coverage"):
        "Verify first (Recommended)",
    ("pci-ngfw-compliance", "pci_version"):
        "Confirm version first (Recommended)",
    ("pci-ngfw-compliance", "pci_overlay"):
        "Inventory overlays first (Recommended)",
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
        "Inspect state first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_network"):
        "Map network first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_services"):
        "Verify services first (Recommended)",
    ("sd-onprem-proxmox-deploy", "sd_transfer"):
        "Confirm method first (Recommended)",
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
    ("srx-dynamic-ip-feed", "dif_tls"):
        "Verify chain first (Recommended)",
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
        "Inspect full context first (Recommended)",
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
    ("cis-controls-ngfw-compliance", "cis_scope"): (
        "Inventory estate first (Recommended)",
        "Use supplied full estate",
        "Use supplied named boundary",
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_basis"): (
        "Confirm framework first (Recommended)",
        "Use supplied CMMC Level 2",
        "Use supplied NIST revision",
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_overlay"): (
        "Inventory overlays first (Recommended)",
        "Use supplied overlay",
        "Standard only",
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_assets"): (
        "Inventory assets first (Recommended)",
        "Use supplied CUI boundary",
        "Use supplied enterprise scope",
    ),
    ("firewall-best-practices-audit", "audit_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("firewall-config-diff", "diff_ignore"): (
        "Stop pending allowlist (Recommended)",
        "Use supplied complete allowlist",
        "Use no exclusions",
    ),
    ("hipaa-ngfw-compliance", "hipaa_vendor"): (
        "Inventory paths first (Recommended)",
        "Use supplied all paths",
        "Use supplied named paths",
    ),
    ("parsing-cisco-configs", "cisco_goal"): (
        "Confirm depth first (Recommended)",
        "Use full normalization",
        "Use focused extraction",
    ),
    ("parsing-fortinet-configs", "forti_goal"): (
        "Confirm depth first (Recommended)",
        "Use full normalization",
        "Use focused extraction",
    ),
    ("parsing-palo-configs", "palo_goal"): (
        "Confirm depth first (Recommended)",
        "Use full normalization",
        "Use focused extraction",
    ),
    ("parsing-srx-configs", "srxp_goal"): (
        "Confirm depth first (Recommended)",
        "Use full normalization",
        "Use focused extraction",
    ),
    ("pci-ngfw-compliance", "pci_version"): (
        "Confirm version first (Recommended)",
        "Use supplied PCI DSS 4.0.1",
        "Use supplied other version",
    ),
    ("pci-ngfw-compliance", "pci_overlay"): (
        "Inventory overlays first (Recommended)",
        "Use supplied overlay",
        "Standard only",
    ),
    ("sd-onprem-proxmox-deploy", "sd_stage"): (
        "Inspect stage first (Recommended)",
        "Plan supplied fresh deployment",
        "Troubleshoot supplied deployment",
    ),
    ("sd-onprem-proxmox-deploy", "sd_proxmox"): (
        "Inspect state first (Recommended)",
        "Plan supplied new VM",
        "Assess supplied existing VM",
    ),
    ("sd-onprem-proxmox-deploy", "sd_transfer"): (
        "Confirm method first (Recommended)",
        "Use supplied HTTPS",
        "Use supplied SCP",
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
    ("srx-dynamic-ip-feed", "dif_tls"): (
        "Verify chain first (Recommended)",
        "Use supplied public CA",
        "Use supplied private CA",
    ),
    ("srx-dynamic-ip-feed", "dif_auth"): (
        "Verify endpoint first (Recommended)",
        "Use supplied single auth",
        "Use supplied combined auth",
    ),
    ("srx-ipsec-hub-spoke", "hsvpn_evidence"): (
        "Inventory evidence (Recommended)",
        "Use supplied artifacts",
        "Approved live collection",
    ),
    ("srx-mnha", "mnha_service"): (
        "Inventory services first (Recommended)",
        "Use supplied core-only bundle",
        "Use supplied core-plus-IPsec",
    ),
    ("srx-mpls-in-flow", "mpls_service"): (
        "Confirm services first (Recommended)",
        "Use supplied base-only bundle",
        "Use supplied enhanced bundle",
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
    ("srx-nat", "nat_context"): (
        "Inspect full context first (Recommended)",
        "Use supplied complete context",
        "Stop pending context",
    ),
    ("srx-policy", "policy_service"): (
        "Confirm services first (Recommended)",
        "Use supplied base-only bundle",
        "Use supplied enhanced bundle",
    ),
    ("srx-policy", "policy_ip"): (
        "Dual-stack (Recommended)",
        "IPv4 only",
        "IPv6 only",
    ),
    ("srx-policy", "policy_session"): (
        "Leave existing sessions (Recommended)",
        "Clear targeted sessions",
        "Maintenance-window reset",
    ),
    ("hipaa-ngfw-compliance", "hipaa_role"): (
        "Confirm responsibility (Recommended)",
        "Use supplied single-role scope",
        "Use supplied combined scope",
    ),
    ("soc2-ngfw-compliance", "soc2_vendor"): (
        "Inventory vendors first (Recommended)",
        "Use supplied uniform treatment",
        "Use supplied mixed treatment",
    ),
}


class DuplicateJSONKeyError(ValueError):
    """Raised when a package catalog repeats a JSON member name."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key


def object_with_unique_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(key)
        result[key] = value
    return result


def sentence(value: str) -> str:
    """Convert the plan's sentence fragment notation to serialized text."""
    value = value.strip()
    return value[:1].upper() + value[1:] + "."


def normalize_markdown_row(raw_row: str) -> str:
    """Join Markdown-wrapped lines without collapsing same-line whitespace."""
    return " ".join(line.strip() for line in raw_row.splitlines())


def reject_noncanonical_whitespace(
    skill: str,
    question_id: str,
    field_name: str,
    value: str,
) -> None:
    if "\t" in value or "  " in value:
        raise ValueError(
            f"{PLAN_PATH}: {skill}/{question_id} noncanonical whitespace "
            f"in {field_name}"
        )


def parse_plan_row(skill: str, question_id: str, raw_row: str) -> dict[str, object]:
    flat_row = normalize_markdown_row(raw_row)
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
    for field_name in ("ask_when", "header", "question"):
        reject_noncanonical_whitespace(
            skill,
            question_id,
            field_name,
            match.group(field_name),
        )
    for option in option_matches:
        reject_noncanonical_whitespace(
            skill,
            question_id,
            "label",
            option.group("label"),
        )
        reject_noncanonical_whitespace(
            skill,
            question_id,
            "description",
            option.group("description"),
        )
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
    active_markdown = STRUCTURAL_VALIDATOR.mask_inactive_markdown(text)
    if any(
        pattern.search(active_markdown)
        for pattern in STRUCTURAL_VALIDATOR.RAW_HTML_BLOCK_OPENERS
    ):
        raise ValueError(f"{PLAN_PATH}: raw HTML block syntax is not allowed")
    marker_matches = list(
        re.finditer(
            rf"^{re.escape(APPENDIX_MARKER)}[ \t]*\r?$",
            active_markdown,
            re.MULTILINE,
        )
    )
    if len(marker_matches) != 1:
        raise ValueError(f"{PLAN_PATH}: missing {APPENDIX_MARKER!r}")
    appendix_start = marker_matches[0].start()
    appendix = text[appendix_start:]
    active_appendix = active_markdown[appendix_start:]
    lookalikes = list(PLAN_SECTION_LOOKALIKE_RE.finditer(active_appendix))
    catalogs: dict[str, list[dict[str, object]]] = {}

    seen_skills: set[str] = set()
    for lookalike in lookalikes:
        identity = PLAN_SECTION_IDENTITY_RE.match(lookalike.group("heading"))
        if identity is None:
            continue
        skill = identity.group("skill")
        if skill in seen_skills:
            raise ValueError(
                f"{PLAN_PATH}: duplicate Appendix A skill section {skill!r}"
            )
        seen_skills.add(skill)
    for lookalike in lookalikes:
        if PLAN_SECTION_RE.fullmatch(lookalike.group("heading")) is None:
            raise ValueError(
                f"{PLAN_PATH}: noncanonical Appendix A heading "
                f"{lookalike.group('heading').rstrip()!r}"
            )
    sections = list(PLAN_SECTION_RE.finditer(active_appendix))
    if len(sections) != len(EXPECTED_SKILLS):
        raise ValueError(
            f"{PLAN_PATH}: expected exactly {len(EXPECTED_SKILLS)} Appendix A "
            f"sections, found {len(sections)}"
        )

    for index, section in enumerate(sections):
        skill = section.group("skill")
        section_number = section.group("number")
        expected_number = index + 1
        expected_skill = EXPECTED_SKILLS[index]
        if section_number != str(expected_number) or skill != expected_skill:
            raise ValueError(
                f"{PLAN_PATH}: expected Appendix A.{expected_number} "
                f"`{expected_skill}`, found Appendix A.{section_number} "
                f"`{skill}`"
            )
        body_end = (
            sections[index + 1].start()
            if index + 1 < len(sections)
            else len(active_appendix)
        )
        body = appendix[section.end() : body_end]
        active_body = active_appendix[section.end() : body_end]
        rows = list(PLAN_ROW_RE.finditer(active_body))
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
            payload = json.loads(
                matches[0].group("payload"),
                object_pairs_hook=object_with_unique_keys,
            )
        except DuplicateJSONKeyError as exc:
            raise ValueError(
                f"{path}: duplicate JSON object key {exc.key!r}"
            ) from exc
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


def catalog_sha256(questions: list[dict[str, object]]) -> str:
    canonical = json.dumps(
        questions,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    if count == 1:
        return singular
    return plural_form or f"{singular}s"


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
        actual_digest = catalog_sha256(reference_questions)
        expected_digest = EXPECTED_CATALOG_SHA256[skill]
        if actual_digest != expected_digest:
            errors.append(
                f"{skill}: canonical catalog digest mismatch "
                f"{actual_digest!r}; expected {expected_digest!r}"
            )

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

    selected_count = len(selected_skills)
    safe_count = sum(
        skill in selected_skills for skill, _question_id in SAFE_FIRST_LABELS
    )
    tuple_count = sum(
        skill in selected_skills for skill, _question_id in EXACT_OPTION_LABELS
    )
    print(
        f"OK: {selected_count} selected plan/reference "
        f"{plural(selected_count, 'catalog')}; parsed all "
        f"{len(EXPECTED_SKILLS)} catalogs and resolved all manifest keys; "
        f"{safe_count} {plural(safe_count, 'safe default')}; "
        f"{tuple_count} exact {plural(tuple_count, 'option tuple')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
