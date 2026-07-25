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
    ("firewall-config-diff", "diff_ignore"): (
        "How should an unspecified difference allowlist be handled?",
        (
            "Stop pending allowlist (Recommended)",
            "Use supplied complete allowlist",
            "Use no exclusions",
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

    def test_review_semantics_have_exact_manifest_coverage(self) -> None:
        for key in TASK_30_SEMANTIC_KEYS:
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
            "resolved all manifest keys; 2 safe defaults; 1 exact option tuple",
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
