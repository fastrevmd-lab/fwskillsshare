#!/usr/bin/env python3
"""Negative contract tests for the runtime-intake validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR_PATH = SCRIPT_DIR / "check-runtime-intake.py"
SPEC = importlib.util.spec_from_file_location("check_runtime_intake", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import validator from {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

CLAUDE_ADAPTATION = """\
- Claude: select at most three neutral entries, project each to only `question`,
  `header`, and `options`, then add `multiSelect: false`; do not send `id` or
  `ask_when`."""
CODEX_ADAPTATION = """\
- Codex: select at most three neutral entries and project each to only `id`,
  `header`, `question`, and `options`; do not send `ask_when` or `multiSelect`."""
FALLBACK_ADAPTATION = """\
- Fallback: ask the same questions in concise plain text with a free-text
  `Other` path."""
TOOL_ADAPTATION = "\n".join(
    (
        CLAUDE_ADAPTATION,
        CODEX_ADAPTATION,
        FALLBACK_ADAPTATION,
        "- Never request secrets.",
    )
)

VALID_CATALOG = {
    "questions": [
        {
            "id": "audit_scope",
            "ask_when": "The requested audit scope is absent.",
            "header": "Scope",
            "question": "What should the audit cover?",
            "options": [
                {
                    "label": "Full device (Recommended)",
                    "description": "Inspect the complete device configuration.",
                },
                {
                    "label": "Rulebase only",
                    "description": "Inspect only the security rulebase.",
                },
            ],
        }
    ]
}


def render_reference(
    catalog: dict[str, object] | None = None,
    adaptation: str = TOOL_ADAPTATION,
) -> str:
    payload = VALID_CATALOG if catalog is None else catalog
    return render_raw_reference(json.dumps(payload, indent=2), adaptation)


def render_raw_reference(
    raw_catalog: str,
    adaptation: str = TOOL_ADAPTATION,
) -> str:
    return f"""\
# Runtime Intake

## When to ask

Ask only unresolved material questions.

## Tool adaptation

{adaptation}

## Question catalog

```json
{raw_catalog}
```
"""


class RuntimeIntakeValidatorTests(unittest.TestCase):
    def assert_has_error(self, text: str, fragment: str) -> None:
        errors = VALIDATOR.validate_catalog(Path("runtime-intake.md"), text)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}, got {errors!r}",
        )

    def test_accepts_exact_neutral_contract(self) -> None:
        self.assertEqual(
            VALIDATOR.validate_catalog(
                Path("runtime-intake.md"), render_reference()
            ),
            [],
        )

    def test_accepts_initialism_in_question(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["question"] = "Which U.S. standard applies?"
        self.assertEqual(
            VALIDATOR.validate_catalog(
                Path("runtime-intake.md"), render_reference(catalog)
            ),
            [],
        )

    def test_accepts_initialism_in_description(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["options"][0]["description"] = (
            "Use U.S. regulatory requirements."
        )
        self.assertEqual(
            VALIDATOR.validate_catalog(
                Path("runtime-intake.md"), render_reference(catalog)
            ),
            [],
        )

    def test_rejects_question_sentence_ending_in_initialism(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["question"] = (
            "Operations occur in the U.S. Which standard applies?"
        )
        self.assert_has_error(
            render_reference(catalog),
            "must contain exactly one sentence boundary",
        )

    def test_rejects_description_sentence_ending_in_initialism(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["options"][0]["description"] = (
            "Use systems in the U.S. Apply regulatory requirements."
        )
        self.assert_has_error(
            render_reference(catalog),
            "must contain exactly one sentence",
        )

    def test_rejects_extra_top_level_keys(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["version"] = 1
        self.assert_has_error(
            render_reference(catalog), "catalog keys must be exactly"
        )

    def test_rejects_unsupported_question_keys(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["multiSelect"] = False
        self.assert_has_error(
            render_reference(catalog), "question keys must be exactly"
        )

    def test_rejects_extra_option_keys(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["options"][0]["value"] = "full"
        self.assert_has_error(
            render_reference(catalog), "option keys must be exactly"
        )

    def test_rejects_duplicate_top_level_question_members(self) -> None:
        raw_catalog = json.dumps(VALID_CATALOG).replace(
            '{"questions":',
            '{"questions": [], "questions":',
            1,
        )
        self.assert_has_error(
            render_raw_reference(raw_catalog),
            "duplicate JSON object key 'questions'",
        )

    def test_rejects_duplicate_question_members(self) -> None:
        raw_catalog = json.dumps(VALID_CATALOG).replace(
            '"id": "audit_scope"',
            '"id": "discarded", "id": "audit_scope"',
            1,
        )
        self.assert_has_error(
            render_raw_reference(raw_catalog),
            "duplicate JSON object key 'id'",
        )

    def test_rejects_duplicate_option_members(self) -> None:
        raw_catalog = json.dumps(VALID_CATALOG).replace(
            '"label": "Full device (Recommended)"',
            '"label": "Discarded", "label": "Full device (Recommended)"',
            1,
        )
        self.assert_has_error(
            render_raw_reference(raw_catalog),
            "duplicate JSON object key 'label'",
        )

    def test_rejects_surrounding_whitespace_in_text_fields(self) -> None:
        cases = (
            (
                "ask_when",
                " ask when needed ",
                "`ask_when` must be non-empty and stripped",
            ),
            ("header", " Scope ", "`header` must be non-empty and stripped"),
            (
                "question",
                " What should be inspected? ",
                "`question` must be non-empty and stripped",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                catalog = copy.deepcopy(VALID_CATALOG)
                catalog["questions"][0][field] = value
                self.assert_has_error(render_reference(catalog), expected)

        option_cases = (
            (
                "label",
                " Full device (Recommended) ",
                "`label` must be non-empty and stripped",
            ),
            (
                "description",
                " Inspect the complete device configuration. ",
                "`description` must be non-empty and stripped",
            ),
        )
        for field, value, expected in option_cases:
            with self.subTest(field=field):
                catalog = copy.deepcopy(VALID_CATALOG)
                catalog["questions"][0]["options"][0][field] = value
                self.assert_has_error(render_reference(catalog), expected)

    def test_rejects_blank_text_fields(self) -> None:
        cases = (
            ("ask_when", "`ask_when` must be non-empty and stripped"),
            ("header", "`header` must be non-empty and stripped"),
            ("question", "`question` must be non-empty and stripped"),
        )
        for field, expected in cases:
            with self.subTest(field=field):
                catalog = copy.deepcopy(VALID_CATALOG)
                catalog["questions"][0][field] = " "
                self.assert_has_error(render_reference(catalog), expected)

        option_cases = (
            ("label", "`label` must be non-empty and stripped"),
            ("description", "`description` must be non-empty and stripped"),
        )
        for field, expected in option_cases:
            with self.subTest(field=field):
                catalog = copy.deepcopy(VALID_CATALOG)
                catalog["questions"][0]["options"][0][field] = " "
                self.assert_has_error(render_reference(catalog), expected)

    def test_rejects_more_than_one_question_mark(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["question"] = "Which standard??"
        self.assert_has_error(
            render_reference(catalog), "must contain exactly one question mark"
        )

    def test_rejects_multiple_question_sentence_boundaries(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["question"] = (
            "Review scope. Which standard applies?"
        )
        self.assert_has_error(
            render_reference(catalog),
            "must contain exactly one sentence boundary",
        )

    def test_rejects_multi_sentence_descriptions(self) -> None:
        catalog = copy.deepcopy(VALID_CATALOG)
        catalog["questions"][0]["options"][0]["description"] = (
            "Inspect the complete device. Include all policies."
        )
        self.assert_has_error(
            render_reference(catalog), "must contain exactly one sentence"
        )

    def test_rejects_missing_or_stale_claude_projection(self) -> None:
        stale = TOOL_ADAPTATION.replace(
            CLAUDE_ADAPTATION,
            "- Claude: send unchanged neutral entries and add `multiSelect: false`.",
        )
        self.assert_has_error(
            render_reference(adaptation=stale),
            "missing exact Claude projection language",
        )

    def test_rejects_missing_or_stale_codex_projection(self) -> None:
        stale = TOOL_ADAPTATION.replace(
            CODEX_ADAPTATION,
            "- Codex: send unchanged neutral entries and omit `multiSelect`.",
        )
        self.assert_has_error(
            render_reference(adaptation=stale),
            "missing exact Codex projection language",
        )

    def test_rejects_fallback_without_plain_text_and_free_text_other(self) -> None:
        stale = TOOL_ADAPTATION.replace(
            FALLBACK_ADAPTATION,
            "- Fallback: ask the same questions.",
        )
        self.assert_has_error(
            render_reference(adaptation=stale),
            "missing exact fallback and free-text Other language",
        )


if __name__ == "__main__":
    unittest.main()
