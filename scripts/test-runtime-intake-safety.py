#!/usr/bin/env python3
"""Regression tests for runtime-intake semantic safety validation."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAFETY_PATH = ROOT / "scripts" / "check-runtime-intake-safety.py"
SPEC = importlib.util.spec_from_file_location("runtime_intake_safety", SAFETY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {SAFETY_PATH}")
SAFETY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SAFETY)

CATALOG_RE = re.compile(r"```json\n(?P<payload>.*?)\n```", re.DOTALL)
DESIRED_SEMANTICS = {
    ("cis-controls-ngfw-compliance", "cis_version"): (
        "How should an unspecified governing CIS Controls version be resolved?",
        (
            "Confirm version first (Recommended)",
            "Use supplied CIS v8.1",
            "Use supplied CIS v8",
        ),
    ),
    ("cis-controls-ngfw-compliance", "cis_scope"): (
        "How should an unspecified firewall estate scope be resolved?",
        (
            "Inventory estate first (Recommended)",
            "Use supplied full estate",
            "Use supplied named boundary",
        ),
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_basis"): (
        "How should an unspecified assessment framework be resolved?",
        (
            "Confirm framework first (Recommended)",
            "Use supplied CMMC Level 2",
            "Use supplied NIST revision",
        ),
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_overlay"): (
        "How should an unspecified contractual overlay be handled?",
        (
            "Inventory overlays first (Recommended)",
            "Use supplied overlay",
            "Standard only",
        ),
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_assets"): (
        "How should an unspecified CUI asset scope be resolved?",
        (
            "Inventory assets first (Recommended)",
            "Use supplied CUI boundary",
            "Use supplied enterprise scope",
        ),
    ),
    ("cmmc-nist-800-171-ngfw-compliance", "cmmc_stage"): (
        "How should an unspecified assessment stage be resolved?",
        (
            "Confirm stage first (Recommended)",
            "Use supplied pre-assessment",
            "Use supplied formal assessment",
        ),
    ),
    ("firewall-best-practices-audit", "audit_depth"): (
        "How should an unspecified finding-detail tier be resolved?",
        (
            "Confirm detail first (Recommended)",
            "Use supplied full detail",
            "Use supplied material-only detail",
        ),
    ),
    ("firewall-config-diff", "diff_ignore"): (
        "How should an unspecified difference allowlist be handled?",
        (
            "Stop pending allowlist (Recommended)",
            "Use supplied complete allowlist",
            "Use no exclusions",
        ),
    ),
    ("firewall-config-diff", "diff_output"): (
        "How should an unspecified result-detail tier be resolved?",
        (
            "Confirm detail first (Recommended)",
            "Use supplied full report",
            "Use supplied material summary",
        ),
    ),
    ("firewall-config-diff", "diff_format"): (
        "How should an unspecified result format be resolved?",
        (
            "Confirm format first (Recommended)",
            "Use supplied human-readable",
            "Use supplied machine-readable",
        ),
    ),
    ("hipaa-ngfw-compliance", "hipaa_vendor"): (
        "How should unresolved third-party ePHI path scope be handled?",
        (
            "Inventory paths first (Recommended)",
            "Use supplied all paths",
            "Use supplied named paths",
        ),
    ),
    ("parsing-cisco-configs", "cisco_goal"): (
        "How should unspecified parsing depth be resolved?",
        (
            "Confirm depth first (Recommended)",
            "Use full normalization",
            "Use focused extraction",
        ),
    ),
    ("parsing-fortinet-configs", "forti_goal"): (
        "How should unspecified parsing depth be resolved?",
        (
            "Confirm depth first (Recommended)",
            "Use full normalization",
            "Use focused extraction",
        ),
    ),
    ("parsing-palo-configs", "palo_goal"): (
        "How should unspecified parsing depth be resolved?",
        (
            "Confirm depth first (Recommended)",
            "Use full normalization",
            "Use focused extraction",
        ),
    ),
    ("parsing-srx-configs", "srxp_goal"): (
        "How should unspecified parsing depth be resolved?",
        (
            "Confirm depth first (Recommended)",
            "Use full normalization",
            "Use focused extraction",
        ),
    ),
    ("pci-ngfw-compliance", "pci_version"): (
        "How should an unspecified PCI DSS version be resolved?",
        (
            "Confirm version first (Recommended)",
            "Use supplied PCI DSS 4.0.1",
            "Use supplied other version",
        ),
    ),
    ("pci-ngfw-compliance", "pci_overlay"): (
        "How should an unspecified assessment overlay be handled?",
        (
            "Inventory overlays first (Recommended)",
            "Use supplied overlay",
            "Standard only",
        ),
    ),
    ("sd-onprem-proxmox-deploy", "sd_transfer"): (
        "How should an unspecified bundle transfer method be resolved?",
        (
            "Confirm method first (Recommended)",
            "Use supplied HTTPS",
            "Use supplied SCP",
        ),
    ),
    ("sd-onprem-proxmox-deploy", "sd_size"): (
        "How should unresolved appliance sizing be handled?",
        (
            "Measure requirements first (Recommended)",
            "Use supplied final flavor",
        ),
    ),
    ("srx-advpn", "advpn_route"): (
        "How should an unspecified ADVPN routing model be resolved?",
        (
            "Confirm model first (Recommended)",
            "Use supplied OSPF P2MP",
            "Use supplied other model",
        ),
    ),
    ("srx-autovpn-full-tunnel", "autovpn_traffic"): (
        "How should an unspecified AutoVPN traffic model be resolved?",
        (
            "Confirm model first (Recommended)",
            "Use supplied full backhaul",
            "Use supplied split tunnel",
        ),
    ),
    ("srx-autovpn-full-tunnel", "autovpn_auth"): (
        "How should an unspecified target peer-authentication model be "
        "resolved?",
        (
            "Confirm auth first (Recommended)",
            "Use supplied PKI model",
            "Use supplied unique-PSK model",
        ),
    ),
    ("srx-dynamic-ip-feed", "dif_tls"): (
        "How should an unspecified publisher CA source be resolved?",
        (
            "Verify chain first (Recommended)",
            "Use supplied public CA",
            "Use supplied private CA",
        ),
    ),
    ("sd-onprem-proxmox-deploy", "sd_stage"): (
        "How should an unspecified deployment stage be resolved?",
        (
            "Inspect stage first (Recommended)",
            "Plan supplied fresh deployment",
            "Troubleshoot supplied deployment",
        ),
    ),
    ("sd-onprem-proxmox-deploy", "sd_proxmox"): (
        "How should incomplete Proxmox VM state be resolved?",
        (
            "Inspect state first (Recommended)",
            "Plan supplied new VM",
            "Assess supplied existing VM",
        ),
    ),
    ("srx-mnha", "mnha_service"): (
        "How should unspecified failover-service scope be resolved?",
        (
            "Inventory services first (Recommended)",
            "Use supplied core-only bundle",
            "Use supplied core-plus-IPsec",
        ),
    ),
    ("srx-mpls-in-flow", "mpls_service"): (
        "How should unspecified security-service scope be handled?",
        (
            "Confirm services first (Recommended)",
            "Use supplied base-only bundle",
            "Use supplied enhanced bundle",
        ),
    ),
    ("srx-policy", "policy_service"): (
        "How should unspecified security-service scope be handled?",
        (
            "Confirm services first (Recommended)",
            "Use supplied base-only bundle",
            "Use supplied enhanced bundle",
        ),
    ),
    ("srx-nat", "nat_context"): (
        "How should uncertain traffic classification be handled?",
        (
            "Inspect full context first (Recommended)",
            "Use supplied complete context",
            "Stop pending context",
        ),
    ),
    ("srx-policy", "policy_ip"): (
        "Which address families should policy cover?",
        (
            "Dual-stack (Recommended)",
            "IPv4 only",
            "IPv6 only",
        ),
    ),
    ("srx-dynamic-ip-feed", "dif_auth"): (
        "How should uncertain feed authentication be handled?",
        (
            "Verify endpoint first (Recommended)",
            "Use supplied single auth",
            "Use supplied combined auth",
        ),
    ),
    ("srx-dynamic-ip-feed", "dif_session"): (
        "How should unspecified existing-session behavior be resolved?",
        (
            "Confirm behavior first (Recommended)",
            "Use supplied new-sessions-only",
            "Use supplied targeted clear",
        ),
    ),
    ("srx-dynamic-ip-feed", "dif_poll"): (
        "How should an unspecified polling cadence be resolved?",
        (
            "Confirm cadence first (Recommended)",
            "Use supplied standard interval",
            "Use supplied custom interval",
        ),
    ),
    ("srx-ipsec-hub-spoke", "hsvpn_traffic"): (
        "How should an unspecified hub-spoke traffic model be resolved?",
        (
            "Confirm model first (Recommended)",
            "Use supplied central backhaul",
            "Use supplied split tunnel",
        ),
    ),
    ("srx-mnha", "mnha_route"): (
        "How should unresolved MNHA signaling design be handled?",
        (
            "Design from topology first (Recommended)",
            "Use supplied complete design",
        ),
    ),
    ("srx-mpls-in-flow", "mpls_policy"): (
        "How should an unspecified VRF policy architecture be resolved?",
        (
            "Confirm architecture first (Recommended)",
            "Use supplied policy groups",
            "Use supplied VRF-to-zone",
        ),
    ),
    ("srx-policy", "policy_model"): (
        "How should an unspecified policy architecture be resolved?",
        (
            "Confirm architecture first (Recommended)",
            "Use supplied global policy",
            "Use supplied zone-pair policy",
        ),
    ),
    ("hipaa-ngfw-compliance", "hipaa_role"): (
        "How should an unspecified HIPAA responsibility be handled?",
        (
            "Confirm responsibility (Recommended)",
            "Use supplied single-role scope",
            "Use supplied combined scope",
        ),
    ),
    ("soc2-ngfw-compliance", "soc2_vendor"): (
        "How should uncertain subservice-organization treatment be handled?",
        (
            "Inventory vendors first (Recommended)",
            "Use supplied uniform treatment",
            "Use supplied mixed treatment",
        ),
    ),
    ("parsing-cisco-configs", "cisco_platform"): (
        "How should an ambiguous Cisco platform be resolved?",
        (
            "Confirm platform first (Recommended)",
            "Use supplied Cisco ASA",
            "Use supplied Cisco FTD",
        ),
    ),
    ("parsing-palo-configs", "palo_format"): (
        "How should an ambiguous PAN-OS format be resolved?",
        (
            "Confirm format first (Recommended)",
            "Use supplied PAN-OS XML",
            "Use supplied set format",
        ),
    ),
    ("parsing-palo-configs", "palo_scope"): (
        "How should an unspecified PAN-OS context scope be resolved?",
        (
            "Confirm context first (Recommended)",
            "Use supplied all-context scope",
            "Use supplied named-context scope",
        ),
    ),
    ("parsing-palo-configs", "palo_inheritance"): (
        "How should unspecified PAN-OS inheritance treatment be resolved?",
        (
            "Confirm inheritance first (Recommended)",
            "Use supplied effective resolution",
            "Use supplied local-only treatment",
        ),
    ),
    ("parsing-srx-configs", "srxp_format"): (
        "How should an ambiguous Junos format be resolved?",
        (
            "Confirm format first (Recommended)",
            "Use supplied display set",
            "Use supplied hierarchical",
        ),
    ),
    ("srx-advpn", "advpn_gateway"): (
        "How should unresolved ADVPN gateway support be handled?",
        (
            "Verify support first (Recommended)",
            "Use supplied supported static",
            "Use supplied supported dynamic",
        ),
    ),
    ("srx-mnha", "mnha_objective"): (
        "How should an unspecified resilience objective be resolved?",
        (
            "Confirm objective first (Recommended)",
            "Use supplied continuity priority",
            "Use supplied convergence priority",
        ),
    ),
    ("soc2-ngfw-compliance", "soc2_tsc"): (
        "How should unspecified Trust Services categories be resolved?",
        (
            "Confirm categories first (Recommended)",
            "Use supplied security-only scope",
            "Use supplied expanded scope",
        ),
    ),
    ("firewall-best-practices-audit", "audit_scope"): (
        "How should unspecified audit component coverage be resolved?",
        (
            "Inventory components first (Recommended)",
            "Use supplied full-component scope",
            "Use supplied limited-component scope",
        ),
    ),
    ("firewall-best-practices-audit", "audit_boundary"): (
        "How should an unspecified audit boundary be resolved?",
        (
            "Map boundary first (Recommended)",
            "Use supplied all-context boundary",
            "Use supplied named-context boundary",
        ),
    ),
    ("firewall-config-conversion", "convert_source"): (
        "How should an ambiguous source platform be handled?",
        (
            "Confirm platform first (Recommended)",
            "Use supplied exact platform",
            "Analyze as unknown source",
        ),
    ),
}
FINAL_CORPUS_EXPECTED_QUESTIONS = {
    ("cis-controls-ngfw-compliance", "cis_version"): {
        "ask_when": "The governing CIS Controls version is absent.",
        "question":
            "How should an unspecified governing CIS Controls version be "
            "resolved?",
        "options": [
            {
                "label": "Confirm version first (Recommended)",
                "description":
                    "Confirm the governing version and any organizational "
                    "crosswalk before grading.",
            },
            {
                "label": "Use supplied CIS v8.1",
                "description":
                    "Apply CIS Controls v8.1 as explicitly supplied.",
            },
            {
                "label": "Use supplied CIS v8",
                "description":
                    "Apply CIS Controls v8 as explicitly supplied.",
            },
        ],
    },
    ("srx-autovpn-full-tunnel", "autovpn_auth"): {
        "ask_when":
            "The target peer-authentication model is absent and affects the "
            "design.",
        "question":
            "How should an unspecified target peer-authentication model be "
            "resolved?",
        "options": [
            {
                "label": "Confirm auth first (Recommended)",
                "description":
                    "Confirm target peer authentication and existing "
                    "constraints before design.",
            },
            {
                "label": "Use supplied PKI model",
                "description":
                    "Use the supplied certificate and scalable group-identity "
                    "model.",
            },
            {
                "label": "Use supplied unique-PSK model",
                "description":
                    "Use the supplied requirement for a distinct PSK per "
                    "spoke without requesting secret values.",
            },
        ],
    },
}
TASK_30_SEMANTIC_KEYS = frozenset(
    {
        ("cis-controls-ngfw-compliance", "cis_scope"),
        ("cmmc-nist-800-171-ngfw-compliance", "cmmc_basis"),
        ("cmmc-nist-800-171-ngfw-compliance", "cmmc_overlay"),
        ("cmmc-nist-800-171-ngfw-compliance", "cmmc_assets"),
        ("firewall-config-diff", "diff_ignore"),
        ("hipaa-ngfw-compliance", "hipaa_vendor"),
        ("parsing-cisco-configs", "cisco_goal"),
        ("parsing-fortinet-configs", "forti_goal"),
        ("parsing-palo-configs", "palo_goal"),
        ("parsing-srx-configs", "srxp_goal"),
        ("pci-ngfw-compliance", "pci_version"),
        ("pci-ngfw-compliance", "pci_overlay"),
        ("sd-onprem-proxmox-deploy", "sd_transfer"),
        ("srx-dynamic-ip-feed", "dif_tls"),
    }
)
TASK_31_SEMANTIC_KEYS = frozenset(
    {
        ("cmmc-nist-800-171-ngfw-compliance", "cmmc_stage"),
        ("firewall-best-practices-audit", "audit_depth"),
        ("firewall-config-diff", "diff_output"),
        ("firewall-config-diff", "diff_format"),
        ("sd-onprem-proxmox-deploy", "sd_size"),
        ("srx-advpn", "advpn_route"),
        ("srx-autovpn-full-tunnel", "autovpn_traffic"),
        ("srx-dynamic-ip-feed", "dif_session"),
        ("srx-dynamic-ip-feed", "dif_poll"),
        ("srx-ipsec-hub-spoke", "hsvpn_traffic"),
        ("srx-mnha", "mnha_route"),
        ("srx-mpls-in-flow", "mpls_policy"),
        ("srx-policy", "policy_model"),
    }
)
TASK_32_SEMANTIC_KEYS = frozenset(
    {
        ("parsing-cisco-configs", "cisco_platform"),
        ("parsing-palo-configs", "palo_format"),
        ("parsing-palo-configs", "palo_scope"),
        ("parsing-palo-configs", "palo_inheritance"),
        ("parsing-srx-configs", "srxp_format"),
        ("srx-advpn", "advpn_gateway"),
        ("srx-mnha", "mnha_objective"),
        ("soc2-ngfw-compliance", "soc2_tsc"),
        ("firewall-best-practices-audit", "audit_scope"),
        ("firewall-best-practices-audit", "audit_boundary"),
    }
)
TASK_32_EXPECTED_ASK_WHEN = {
    ("parsing-cisco-configs", "cisco_platform"):
        "ASA versus FTD remains ambiguous after artifact inspection.",
    ("parsing-palo-configs", "palo_format"):
        "XML versus set format remains ambiguous after artifact inspection.",
    ("parsing-palo-configs", "palo_scope"):
        "PAN-OS configuration-context selection is unclear.",
    ("parsing-palo-configs", "palo_inheritance"):
        "Inheritance treatment is unclear.",
    ("parsing-srx-configs", "srxp_format"):
        "Display-set versus hierarchical syntax remains ambiguous after "
        "artifact inspection.",
    ("srx-advpn", "advpn_gateway"):
        "Release-specific gateway support is unresolved.",
    ("srx-mnha", "mnha_objective"):
        "Resilience priority is absent.",
    ("soc2-ngfw-compliance", "soc2_tsc"):
        "Trust Services categories are absent.",
    ("firewall-best-practices-audit", "audit_scope"):
        "Audit component coverage is unclear.",
    ("firewall-best-practices-audit", "audit_boundary"):
        "Audit boundary breadth is unclear.",
}
FINAL_REVIEW_SEMANTIC_KEYS = frozenset(
    {
        ("firewall-config-conversion", "convert_source"),
        ("cis-controls-ngfw-compliance", "cis_version"),
        ("srx-autovpn-full-tunnel", "autovpn_auth"),
    }
)
FINAL_REVIEW_EXPECTED_ASK_WHEN = {
    ("firewall-config-conversion", "convert_source"):
        "The source platform cannot be determined confidently.",
    ("cis-controls-ngfw-compliance", "cis_version"):
        "The governing CIS Controls version is absent.",
    ("srx-autovpn-full-tunnel", "autovpn_auth"):
        "The target peer-authentication model is absent and affects the design.",
}
EXPECTED_FINAL_QUESTION_COUNT = 155
EXPECTED_FINAL_SAFE_LABEL_COUNT = 102
EXPECTED_FINAL_EXACT_TUPLE_COUNT = 58
EXPECTED_FINAL_SEMANTIC_ID_COUNT = 50


class RuntimeIntakeSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_plan_path = SAFETY.PLAN_PATH
        self.original_skills_dir = SAFETY.SKILLS_DIR

    def tearDown(self) -> None:
        SAFETY.PLAN_PATH = self.original_plan_path
        SAFETY.SKILLS_DIR = self.original_skills_dir

    def use_temp_catalogs(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        temp_root = Path(temporary.name)
        plan_path = temp_root / "runtime-intake-plan.md"
        shutil.copyfile(self.original_plan_path, plan_path)
        skills_dir = temp_root / "skills"
        for skill in SAFETY.EXPECTED_SKILLS:
            source = (
                self.original_skills_dir
                / skill
                / "references"
                / "runtime-intake.md"
            )
            target = skills_dir / skill / "references" / "runtime-intake.md"
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
        SAFETY.PLAN_PATH = plan_path
        SAFETY.SKILLS_DIR = skills_dir
        return temp_root

    def run_main(self, skill: str | None = None) -> tuple[int, str]:
        argv = [str(SAFETY_PATH)]
        if skill:
            argv.append(skill)
        original_argv = sys.argv
        stream = io.StringIO()
        try:
            sys.argv = argv
            with contextlib.redirect_stdout(stream):
                result = SAFETY.main()
        finally:
            sys.argv = original_argv
        return result, stream.getvalue()

    def package_question(self, skill: str, question_id: str) -> dict[str, object]:
        catalogs = SAFETY.parse_reference_catalogs()
        matches = [
            question
            for question in catalogs[skill]
            if question.get("id") == question_id
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_review_semantics_are_exact(self) -> None:
        for key, (expected_question, expected_labels) in DESIRED_SEMANTICS.items():
            with self.subTest(skill=key[0], question_id=key[1]):
                question = self.package_question(*key)
                actual_labels = tuple(
                    option["label"] for option in question["options"]
                )
                self.assertEqual(question["question"], expected_question)
                self.assertEqual(actual_labels, expected_labels)

    def test_final_corpus_question_objects_are_exact(self) -> None:
        for key, expected in FINAL_CORPUS_EXPECTED_QUESTIONS.items():
            with self.subTest(skill=key[0], question_id=key[1]):
                question = self.package_question(*key)
                self.assertEqual(
                    {
                        "ask_when": question["ask_when"],
                        "question": question["question"],
                        "options": question["options"],
                    },
                    expected,
                )

    def test_review_semantics_have_exact_manifest_coverage(self) -> None:
        protected_keys = (
            TASK_30_SEMANTIC_KEYS
            | TASK_31_SEMANTIC_KEYS
            | TASK_32_SEMANTIC_KEYS
            | FINAL_REVIEW_SEMANTIC_KEYS
        )
        for key in protected_keys:
            with self.subTest(skill=key[0], question_id=key[1]):
                _expected_question, expected_labels = DESIRED_SEMANTICS[key]
                self.assertEqual(
                    SAFETY.SAFE_FIRST_LABELS.get(key),
                    expected_labels[0],
                )
                self.assertEqual(
                    SAFETY.EXACT_OPTION_LABELS.get(key),
                    expected_labels,
                )

    def test_task_32_ask_when_conditions_are_exact(self) -> None:
        for key, expected_ask_when in TASK_32_EXPECTED_ASK_WHEN.items():
            with self.subTest(skill=key[0], question_id=key[1]):
                question = self.package_question(*key)
                self.assertEqual(question["ask_when"], expected_ask_when)

    def test_final_review_ask_when_conditions_are_exact(self) -> None:
        for key, expected_ask_when in FINAL_REVIEW_EXPECTED_ASK_WHEN.items():
            with self.subTest(skill=key[0], question_id=key[1]):
                question = self.package_question(*key)
                self.assertEqual(question["ask_when"], expected_ask_when)

    def test_final_review_inventory_counts_are_exact(self) -> None:
        catalogs = SAFETY.parse_plan_catalogs()
        self.assertEqual(
            sum(len(questions) for questions in catalogs.values()),
            EXPECTED_FINAL_QUESTION_COUNT,
        )
        self.assertEqual(
            len(SAFETY.SAFE_FIRST_LABELS),
            EXPECTED_FINAL_SAFE_LABEL_COUNT,
        )
        self.assertEqual(
            len(SAFETY.EXACT_OPTION_LABELS),
            EXPECTED_FINAL_EXACT_TUPLE_COUNT,
        )
        self.assertEqual(
            len(DESIRED_SEMANTICS),
            EXPECTED_FINAL_SEMANTIC_ID_COUNT,
        )

    def test_duplicate_appendix_skill_section_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"^### A\.1 `cis-controls-ngfw-compliance`\n.*?"
            r"(?=^### A\.2 )",
            text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match)
        SAFETY.PLAN_PATH.write_text(
            text.rstrip() + "\n\n" + match.group(0).rstrip() + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate Appendix A skill section"):
            SAFETY.parse_plan_catalogs()

    def test_unclosed_four_backtick_fence_hides_appendix_sections(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.1 `cis-controls-ngfw-compliance`",
            "````markdown\n### A.1 `cis-controls-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(
            ValueError,
            "expected exactly 22 Appendix A sections, found 0",
        ):
            SAFETY.parse_plan_catalogs()

    def test_noncanonical_appendix_heading_is_detected(self) -> None:
        cases = (
            "### A.01 `cis-controls-ngfw-compliance` ###",
            "### A.1 `cis-controls-ngfw-compliance` ###",
            "### A.01 cis-controls-ngfw-compliance",
            "### A.1",
        )
        for replacement in cases:
            with self.subTest(heading=replacement):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    replacement,
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError,
                    "noncanonical Appendix A heading",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_trailing_extra_appendix_duplicate_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        duplicate = "### A.1 `cis-controls-ngfw-compliance` extra"
        SAFETY.PLAN_PATH.write_text(
            text.rstrip() + f"\n\n{duplicate}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "duplicate Appendix A skill section",
        ):
            SAFETY.parse_plan_catalogs()

    def test_raw_html_wrapped_appendix_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            SAFETY.APPENDIX_MARKER,
            f"<div>\n{SAFETY.APPENDIX_MARKER}",
            1,
        )
        SAFETY.PLAN_PATH.write_text(
            text.rstrip() + "\n</div>\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "raw HTML block syntax is not allowed",
        ):
            SAFETY.parse_plan_catalogs()

    def test_closing_hash_appendix_duplicate_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        duplicate = "### A.1 `cis-controls-ngfw-compliance` ###"
        SAFETY.PLAN_PATH.write_text(
            text.rstrip() + f"\n\n{duplicate}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "duplicate Appendix A skill section",
        ):
            SAFETY.parse_plan_catalogs()

    def test_fenced_and_commented_appendix_decoys_are_inactive(self) -> None:
        decoys = (
            "````markdown\n"
            "### A.1 `cis-controls-ngfw-compliance`\n"
            "````\n",
            "<!--\n"
            "### A.1 `cis-controls-ngfw-compliance`\n"
            "-->\n",
        )
        for decoy in decoys:
            with self.subTest(opener=decoy.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    decoy + "### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_inline_comment_openers_do_not_hide_appendix_structure(
        self,
    ) -> None:
        containers = ("top-level", "quote", "list")
        probes = {
            "marker": SAFETY.APPENDIX_MARKER,
            "section": "### A.1 `cis-controls-ngfw-compliance`",
            "row": (
                "- `inline_comment_probe`; header `Probe`; ask when a probe is "
                "needed; question `Run the probe?`; options: "
                "`Run probe (Recommended)` — Run the probe; "
                "`Skip probe` — Skip the probe."
            ),
        }

        def wrap(lines: tuple[str, ...], container: str) -> str:
            if container == "quote":
                return "".join(f"> {line}\n" for line in lines)
            if container == "list":
                return (
                    f"- {lines[0]}\n"
                    + "".join(f"  {line}\n" for line in lines[1:])
                )
            return "".join(f"{line}\n" for line in lines)

        for probe, active_line in probes.items():
            for container in containers:
                with self.subTest(probe=probe, container=container):
                    self.use_temp_catalogs()
                    text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                    insertion = wrap(
                        (
                            "A paragraph <!--",
                            active_line,
                            "-->",
                        ),
                        container,
                    )
                    anchor = (
                        SAFETY.APPENDIX_MARKER
                        if probe == "marker"
                        else "### A.1 `cis-controls-ngfw-compliance`"
                    )
                    replacement = (
                        anchor + "\n" + insertion
                        if probe == "row"
                        else insertion + anchor
                    )
                    SAFETY.PLAN_PATH.write_text(
                        text.replace(
                            anchor,
                            replacement,
                            1,
                        ),
                        encoding="utf-8",
                    )
                    with self.assertRaises(ValueError):
                        SAFETY.parse_plan_catalogs()
                    self.tearDown()
                    self.setUp()

    def test_container_nested_appendix_headings_are_rejected(self) -> None:
        prefixes = (
            "- ",
            "1. ",
            "> ",
            "> - ",
            "- > ",
        )
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                duplicate = (
                    f"{prefix}### A.1 `cis-controls-ngfw-compliance`\n\n"
                )
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    duplicate + "### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError,
                    "duplicate Appendix A skill section",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_container_nested_appendix_lookalike_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.1 `cis-controls-ngfw-compliance`",
            "> ### A.01 malformed\n\n"
            "### A.1 `cis-controls-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(
            ValueError,
            "noncanonical Appendix A heading",
        ):
            SAFETY.parse_plan_catalogs()

    def test_container_nested_raw_html_in_appendix_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.1 `cis-controls-ngfw-compliance`",
            "- <div>\n\n### A.1 `cis-controls-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(
            ValueError,
            "raw HTML block syntax is not allowed",
        ):
            SAFETY.parse_plan_catalogs()

    def test_appendix_container_continuation_blocks_are_active(self) -> None:
        cases = (
            (
                "10. item\n"
                "    ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "123456789. item\n"
                "           ### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "-    item\n"
                "     <div>\n",
                "raw HTML block syntax is not allowed",
            ),
            (
                "- outer\n\n"
                "  10. inner\n"
                "      ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_list_indentation_uses_tab_stop_columns(self) -> None:
        cases = (
            (
                "-\titem\n"
                "\t### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "10.\titem\n"
                " \t### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "- \titem\n"
                "  \t<div>\n",
                "raw HTML block syntax is not allowed",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_empty_list_items_open_at_block_boundaries(self) -> None:
        cases = (
            (
                "10.\n"
                "    ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "123456789)\t  \n"
                "           ### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "+ \t \n"
                "  <div>\n",
                "raw HTML block syntax is not allowed",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_empty_list_items_do_not_interrupt_paragraphs(
        self,
    ) -> None:
        accepted = (
            "A paragraph\n10.\n"
            "    ### A.1 `cis-controls-ngfw-compliance`\n",
            "A paragraph\n123456789)\t \n"
            "           <div>\n",
        )
        for insertion in accepted:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_appendix_empty_item_fences_and_comments_are_inactive(
        self,
    ) -> None:
        decoys = (
            "10.\t \r\n"
            "    ````markdown\r\n"
            "    ### A.1 `cis-controls-ngfw-compliance`\r\n"
            "    <div>\r\n"
            "    ````\r\n",
            "10.   \n"
            "    <!--\n"
            "    ### A.01 malformed\n"
            "    - `fake`; header `Fake`; ask when fake; "
            "question `Fake?`; options: `Fake` — fake.\n"
            "    -->\n",
        )
        for decoy in decoys:
            with self.subTest(decoy=decoy.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    decoy + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_appendix_tabbed_non_one_marker_respects_paragraph_state(
        self,
    ) -> None:
        accepted = (
            "A paragraph\n2.\t### A.1 `cis-controls-ngfw-compliance`\n",
            "A paragraph\n2.\t<div>\n",
        )
        for insertion in accepted:
            with self.subTest(outcome="accepted", insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_appendix_non_one_ordered_markers_respect_paragraph_state(
        self,
    ) -> None:
        accepted = (
            "A paragraph\n2. ### A.1 `cis-controls-ngfw-compliance`\n",
            "A paragraph\n2. <div>\n",
            "- A paragraph\n  9) ### A.1 `cis-controls-ngfw-compliance`\n",
            "- A paragraph\n  9) <div>\n",
        )
        for insertion in accepted:
            with self.subTest(outcome="accepted", insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

        rejected = (
            "A paragraph\n\n2. ### A.1 `cis-controls-ngfw-compliance`\n",
            "A paragraph\n1. ### A.1 `cis-controls-ngfw-compliance`\n",
        )
        for insertion in rejected:
            with self.subTest(outcome="rejected", insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError,
                    "duplicate Appendix A skill section",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_thematic_breaks_close_paragraphs(self) -> None:
        cases = (
            (
                "A paragraph\n***\n"
                "2. ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "A paragraph\n_ _ _\n"
                "2. ### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "> A paragraph\n> * * *\n"
                "> 2. ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "- A paragraph\n  ***\n"
                "  2. <div>\n",
                "raw HTML block syntax is not allowed",
            ),
            (
                "---\n<runtime-wrapper>\n",
                "raw HTML block syntax is not allowed",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

        raw_html_rejected = (
            "A paragraph\n\n2. <div>\n",
            "A paragraph\n1. <div>\n",
        )
        for insertion in raw_html_rejected:
            with self.subTest(outcome="raw-html-rejected", insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError,
                    "raw HTML block syntax is not allowed",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_ordered_list_siblings_are_active(self) -> None:
        cases = (
            (
                "1. first\n"
                "2. ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "2) first\n"
                "3) ### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "1. first\n"
                "2) ### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "> 1. first\n"
                "> 2) <div>\n",
                "raw HTML block syntax is not allowed",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

        controls = (
            "- first\n"
            "  2. ### A.1 `cis-controls-ngfw-compliance`\n",
            "1. first\n"
            "2) ````markdown\n"
            "   ### A.1 `cis-controls-ngfw-compliance`\n"
            "   <div>\n"
            "   ````\n",
        )
        for insertion in controls:
            with self.subTest(control=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_appendix_quote_and_nested_container_fences_are_inactive(
        self,
    ) -> None:
        wrappers = (
            (
                "> ````markdown\n"
                "> ### A.1 `cis-controls-ngfw-compliance`\n"
                "> <div>\n"
                "> ````\n"
            ),
            (
                "- > ~~~~markdown\n"
                "  > ### A.01 malformed\n"
                "  > <runtime-wrapper>\n"
                "  > ~~~~\n"
            ),
        )
        for wrapper in wrappers:
            with self.subTest(opener=wrapper.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    wrapper + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_appendix_marker_counts_active_container_equivalents(self) -> None:
        cases = (
            (
                f"- {SAFETY.APPENDIX_MARKER}\n\n{SAFETY.APPENDIX_MARKER}",
                "expected exactly one active Appendix A marker",
            ),
            (
                f"- {SAFETY.APPENDIX_MARKER} ###\n\n{SAFETY.APPENDIX_MARKER}",
                "noncanonical Appendix A marker",
            ),
        )
        for replacement, error in cases:
            with self.subTest(replacement=replacement.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(SAFETY.APPENDIX_MARKER, replacement, 1)
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_marker_rejects_setext_equivalents(self) -> None:
        equivalents = (
            "Appendix A: Exact question catalogs\n---\n",
            "Appendix A: Exact\nquestion catalogs\n---\n",
            "[foo\\]]: /url\n"
            "Appendix A: Exact question catalogs\n"
            "---\n",
            "[\n"
            "foo\n"
            "]: /url\n"
            "Appendix A: Exact question catalogs\n"
            "---\n",
            "[foo]: /url '\n"
            " title\n"
            " line\n"
            " '\n"
            "Appendix A: Exact question catalogs\n"
            "---\n",
            "> Appendix A: Exact question catalogs\n> ---\n",
            "> Appendix A: Exact\n"
            "> question catalogs\n"
            "> ---\n",
            "> [foo\\]]: /url\n"
            "> Appendix A: Exact question catalogs\n"
            "> ---\n",
            "- Appendix A: Exact question catalogs\n  ---\n",
            "10.\n"
            "    Appendix A: Exact question catalogs\n"
            "    ---\n",
        )
        for equivalent in equivalents:
            with self.subTest(equivalent=equivalent):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    SAFETY.APPENDIX_MARKER,
                    equivalent + "\n" + SAFETY.APPENDIX_MARKER,
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError,
                    "expected exactly one active Appendix A marker",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_appendix_marker_setext_uses_complete_heading_text(self) -> None:
        decoys = (
            "Planning context\n"
            "Appendix A: Exact question catalogs\n"
            "---\n",
            "> Planning context\n"
            "> Appendix A: Exact question catalogs\n"
            "> ---\n",
            "````markdown\n"
            "Appendix A: Exact question catalogs\n"
            "---\n"
            "````\n",
            "<!--\n"
            "Appendix A: Exact question catalogs\n"
            "---\n"
            "-->\n",
        )
        for decoy in decoys:
            with self.subTest(decoy=decoy.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    SAFETY.APPENDIX_MARKER,
                    decoy + "\n" + SAFETY.APPENDIX_MARKER,
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_pending_link_reference_interrupts_are_active_in_appendix(
        self,
    ) -> None:
        pending_states = {
            "label": ("[foo",),
            "destination": ("[foo]:",),
            "same-line-title": ('[foo]: /url "',),
            "next-line-title": ("[foo]: /url", '"'),
        }

        def wrap(lines: tuple[str, ...], container: str) -> str:
            if container == "quote":
                return "".join(f"> {line}\n" for line in lines)
            if container == "list":
                return (
                    f"- {lines[0]}\n"
                    + "".join(f"  {line}\n" for line in lines[1:])
                )
            return "".join(f"{line}\n" for line in lines)

        def replace_marker(insertion: str) -> None:
            self.use_temp_catalogs()
            text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
            SAFETY.PLAN_PATH.write_text(
                text.replace(
                    SAFETY.APPENDIX_MARKER,
                    insertion + "\n" + SAFETY.APPENDIX_MARKER,
                    1,
                ),
                encoding="utf-8",
            )

        for state, pending in pending_states.items():
            for breaker in (
                "***",
                "=",
                "==",
                "===  ",
                "-",
                "--",
                "---\t",
            ):
                for container in ("top-level", "quote", "list"):
                    with self.subTest(
                        state=state,
                        breaker=breaker,
                        container=container,
                    ):
                        insertion = wrap(
                            pending
                            + (
                                breaker,
                                "Appendix A: Exact question catalogs",
                                "---",
                            ),
                            container,
                        )
                        replace_marker(insertion)
                        with self.assertRaisesRegex(
                            ValueError,
                            "expected exactly one active Appendix A marker",
                        ):
                            SAFETY.parse_plan_catalogs()
                        self.tearDown()
                        self.setUp()

            for opener in (
                "<script>",
                "<?runtime?>",
                "<!RUNTIME>",
                "<![CDATA[runtime]]>",
                "<div>",
            ):
                for container in ("top-level", "quote", "list"):
                    with self.subTest(
                        state=state,
                        opener=opener,
                        container=container,
                    ):
                        insertion = wrap(pending + (opener,), container)
                        replace_marker(insertion)
                        with self.assertRaisesRegex(
                            ValueError,
                            "raw HTML block syntax is not allowed",
                        ):
                            SAFETY.parse_plan_catalogs()
                        self.tearDown()
                        self.setUp()

            for container in ("top-level", "quote", "list"):
                with self.subTest(
                    state=state,
                    opener="type-7-control",
                    container=container,
                ):
                    insertion = wrap(
                        pending + ("<runtime-wrapper>",),
                        container,
                    )
                    replace_marker(insertion)
                    catalogs = SAFETY.parse_plan_catalogs()
                    self.assertEqual(
                        tuple(catalogs),
                        SAFETY.EXPECTED_SKILLS,
                    )
                    self.tearDown()
                    self.setUp()

    def test_container_comments_do_not_pollute_appendix_rows(self) -> None:
        decoys = (
            "> <!--\n"
            "> - `fake`; header `Fake`; ask when fake; question `Fake?`; "
            "options: `Fake` — fake.\n"
            "> -->\n",
            "- <!--\n"
            "  - `fake`; header `Fake`; ask when fake; question `Fake?`; "
            "options: `Fake` — fake.\n"
            "  -->\n",
            "> - <!--\r\n"
            ">   - `fake`; header `Fake`; ask when fake; question `Fake?`; "
            "options: `Fake` — fake.\r\n"
            ">   -->\r\n",
        )
        for decoy in decoys:
            with self.subTest(decoy=decoy.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                following_row = "- `cis_version`;"
                text = text.replace(
                    following_row,
                    decoy + following_row,
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(
                    catalogs["cis-controls-ngfw-compliance"][0]["id"],
                    "cis_goal",
                )
                self.tearDown()
                self.setUp()

    def test_container_scoped_comments_end_when_the_container_exits(
        self,
    ) -> None:
        cases = (
            (
                "> <!--\n"
                "### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
            (
                "- <!--\n"
                "### A.01 malformed\n",
                "noncanonical Appendix A heading",
            ),
            (
                "> - <!--\r\n"
                "<div>\r\n",
                "raw HTML block syntax is not allowed",
            ),
            (
                "> <!--\n"
                "-->\n"
                "### A.1 `cis-controls-ngfw-compliance`\n",
                "duplicate Appendix A skill section",
            ),
        )
        for insertion, error in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, error):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_top_level_comments_retain_document_scope(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.1 `cis-controls-ngfw-compliance`",
            "<!--\n"
            "### A.01 malformed\n"
            "<div>\n"
            "### A.1 `cis-controls-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(
            ValueError,
            "expected exactly 22 Appendix A sections, found 0",
        ):
            SAFETY.parse_plan_catalogs()

    def test_appendix_type7_html_does_not_interrupt_paragraphs(self) -> None:
        cases = (
            "A paragraph\n<runtime-wrapper>\n",
            "> A paragraph\n> <runtime-wrapper>\n",
            "- A paragraph\n  <runtime-wrapper>\n",
        )
        for insertion in cases:
            with self.subTest(insertion=insertion):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "### A.1 `cis-controls-ngfw-compliance`",
                    insertion + "\n### A.1 `cis-controls-ngfw-compliance`",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(tuple(catalogs), SAFETY.EXPECTED_SKILLS)
                self.tearDown()
                self.setUp()

    def test_inactive_appendix_decoy_rows_do_not_pollute_active_rows(
        self,
    ) -> None:
        decoy_row = (
            "- `decoy`; header `Decoy`; ask when decoy is absent; "
            "question `Which decoy is required?`; options: "
            "`First (Recommended)` — Use the first decoy; "
            "`Second` — Use the second decoy.\n"
        )
        wrappers = (
            f"````markdown\n{decoy_row}````\n",
            f"<!--\n{decoy_row}-->\n",
        )
        for wrapper in wrappers:
            with self.subTest(opener=wrapper.splitlines()[0]):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                text = text.replace(
                    "- `cis_scope`;",
                    wrapper + "- `cis_scope`;",
                    1,
                )
                SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
                catalogs = SAFETY.parse_plan_catalogs()
                self.assertEqual(
                    [question["id"] for question in catalogs[
                        "cis-controls-ngfw-compliance"
                    ]],
                    [
                        "cis_goal",
                        "cis_version",
                        "cis_ig",
                        "cis_scope",
                        "cis_evidence",
                        "cis_output",
                    ],
                )
                self.tearDown()
                self.setUp()

    def test_appendix_number_name_pairing_is_rejected(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.2 `cmmc-nist-800-171-ngfw-compliance`",
            "### A.9 `cmmc-nist-800-171-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "expected Appendix A.2"):
            SAFETY.parse_plan_catalogs()

    def test_appendix_numbering_is_lexically_exact(self) -> None:
        self.use_temp_catalogs()
        text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        text = text.replace(
            "### A.1 `cis-controls-ngfw-compliance`",
            "### A.01 `cis-controls-ngfw-compliance`",
            1,
        )
        SAFETY.PLAN_PATH.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "expected Appendix A.1"):
            SAFETY.parse_plan_catalogs()

    def test_duplicate_package_json_member_is_rejected(self) -> None:
        self.use_temp_catalogs()
        path = (
            SAFETY.SKILLS_DIR
            / "cis-controls-ngfw-compliance"
            / "references"
            / "runtime-intake.md"
        )
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            '"id": "cis_goal",',
            '"id": "cis_goal",\n      "id": "cis_goal",',
            1,
        )
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key 'id'"):
            SAFETY.parse_reference_catalogs()

    def test_inactive_package_catalog_is_rejected_standalone(self) -> None:
        self.use_temp_catalogs()
        path = (
            SAFETY.SKILLS_DIR
            / "cis-controls-ngfw-compliance"
            / "references"
            / "runtime-intake.md"
        )
        text = path.read_text(encoding="utf-8")
        catalog_start = text.index("```json")
        catalog_end = text.index("\n```", catalog_start) + len("\n```")
        catalog = text[catalog_start:catalog_end]
        path.write_text(
            text[:catalog_start]
            + f"````markdown\n{catalog}\n````"
            + text[catalog_end:],
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            ValueError,
            "expected exactly one active top-level JSON catalog",
        ):
            SAFETY.parse_reference_catalogs()

    def test_same_line_doubled_field_whitespace_is_rejected(self) -> None:
        replacements = (
            (
                "What outcome should this CIS assessment produce?",
                "What  outcome should this CIS assessment produce?",
                "question",
            ),
            (
                "Gap assessment (Recommended)",
                "Gap  assessment (Recommended)",
                "label",
            ),
            (
                "tickets, and operating records before grading",
                "tickets, and  operating records before grading",
                "description",
            ),
        )
        for old, new, field_name in replacements:
            with self.subTest(field=field_name):
                self.use_temp_catalogs()
                text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
                self.assertIn(old, text)
                SAFETY.PLAN_PATH.write_text(
                    text.replace(old, new, 1),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ValueError,
                    rf"noncanonical whitespace in {field_name}",
                ):
                    SAFETY.parse_plan_catalogs()
                self.tearDown()
                self.setUp()

    def test_focused_output_reports_only_selected_assertions(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SAFETY_PATH),
                "cis-controls-ngfw-compliance",
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout.strip(),
            "OK: 1 selected plan/reference catalog; parsed all 22 catalogs and "
            "resolved all manifest keys; 3 safe defaults; 2 exact option tuples",
        )

    def test_digest_manifest_covers_every_catalog(self) -> None:
        digest_manifest = getattr(SAFETY, "EXPECTED_CATALOG_SHA256", None)
        self.assertIsInstance(
            digest_manifest,
            dict,
            "canonical catalog digest gate is absent",
        )
        self.assertEqual(tuple(digest_manifest), SAFETY.EXPECTED_SKILLS)

    def test_synchronized_content_mutation_fails_digest_gate(self) -> None:
        self.use_temp_catalogs()
        old = "What outcome should this CIS assessment produce?"
        new = "What different outcome should this CIS assessment produce?"
        plan_text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        self.assertIn(old, plan_text)
        SAFETY.PLAN_PATH.write_text(
            plan_text.replace(old, new, 1),
            encoding="utf-8",
        )
        reference = (
            SAFETY.SKILLS_DIR
            / "cis-controls-ngfw-compliance"
            / "references"
            / "runtime-intake.md"
        )
        reference_text = reference.read_text(encoding="utf-8")
        self.assertIn(old, reference_text)
        reference.write_text(
            reference_text.replace(old, new, 1),
            encoding="utf-8",
        )
        result, output = self.run_main("cis-controls-ngfw-compliance")
        self.assertEqual(result, 1, output)
        self.assertIn("canonical catalog digest mismatch", output)

    def test_synchronized_order_mutation_fails_digest_gate(self) -> None:
        self.use_temp_catalogs()
        plan_text = SAFETY.PLAN_PATH.read_text(encoding="utf-8")
        section_match = re.search(
            r"(?P<head>^### A\.1 `cis-controls-ngfw-compliance`\n\n)"
            r"(?P<body>.*?)(?=^### A\.2 )",
            plan_text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(section_match)
        body = section_match.group("body")
        rows = list(re.finditer(r"^- `[a-z][a-z0-9_]*`; ", body, re.MULTILINE))
        self.assertGreaterEqual(len(rows), 3)
        first = body[rows[0].start() : rows[1].start()]
        second = body[rows[1].start() : rows[2].start()]
        reordered_body = (
            body[: rows[0].start()]
            + second
            + first
            + body[rows[2].start() :]
        )
        SAFETY.PLAN_PATH.write_text(
            plan_text[: section_match.start("body")]
            + reordered_body
            + plan_text[section_match.end("body") :],
            encoding="utf-8",
        )

        reference = (
            SAFETY.SKILLS_DIR
            / "cis-controls-ngfw-compliance"
            / "references"
            / "runtime-intake.md"
        )
        reference_text = reference.read_text(encoding="utf-8")
        catalog_match = CATALOG_RE.search(reference_text)
        self.assertIsNotNone(catalog_match)
        payload = json.loads(catalog_match.group("payload"))
        payload["questions"][0], payload["questions"][1] = (
            payload["questions"][1],
            payload["questions"][0],
        )
        replacement = json.dumps(payload, indent=2, ensure_ascii=False)
        reference.write_text(
            reference_text[: catalog_match.start("payload")]
            + replacement
            + reference_text[catalog_match.end("payload") :],
            encoding="utf-8",
        )
        result, output = self.run_main("cis-controls-ngfw-compliance")
        self.assertEqual(result, 1, output)
        self.assertIn("canonical catalog digest mismatch", output)


if __name__ == "__main__":
    unittest.main()
