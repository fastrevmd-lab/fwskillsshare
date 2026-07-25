#!/usr/bin/env python3
"""Validate portable runtime-intake instructions and question catalogs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG_RE = re.compile(r"```json\n(?P<payload>.*?)\n```", re.DOTALL)
RUNTIME_HEADING_RE = re.compile(r"^## Runtime intake[ \t]*$", re.MULTILINE)
SECTION_HEADING_RE = re.compile(r"^## [^\n]+$", re.MULTILINE)
SENTENCE_BOUNDARY_RE = re.compile(r"[.!?](?=\s|$)")
INITIALISM_END_RE = re.compile(r"(?:\b[A-Za-z]\.){2,}$")
CATALOG_KEYS = frozenset({"questions"})
QUESTION_KEYS = frozenset({"id", "ask_when", "header", "question", "options"})
OPTION_KEYS = frozenset({"label", "description"})
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
INVOCATION_CLAUSE = (
    "For each unresolved material fact whose catalog condition is true, invoke "
    "Claude `AskUserQuestion` or Codex `request_user_input` before continuing "
    "or issuing an open-ended request."
)
ROUNDS_CLAUSE = (
    "Ask at most three single-select catalog questions per round. After each "
    "response, ask another round whenever any unresolved material catalog "
    "condition remains true; continue only when none remain. Do not repeat "
    "answered questions or show the full catalog."
)
FALLBACK_CLAUSE = (
    "Without a native tool, present each selected catalog question with its 2-3 "
    "labeled choices and a free-text `Other` path in concise plain text; do not "
    "substitute a generic checklist."
)
CONNECTED_RUNTIME_CONTRACT = " ".join(
    (INVOCATION_CLAUSE, ROUNDS_CLAUSE, FALLBACK_CLAUSE)
)
REQUIRED_RUNTIME_TEXT = (
    "references/runtime-intake.md",
    "Never request secrets",
    "separate explicit approval",
)
REQUIRED_REFERENCE_HEADINGS = (
    "# Runtime Intake",
    "## When to ask",
    "## Tool adaptation",
    "## Question catalog",
)


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object repeats a member name."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key


def object_with_unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(key)
        result[key] = value
    return result


def is_nonempty_stripped(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def sentence_boundary_count(value: str) -> int:
    count = 0
    for match in SENTENCE_BOUNDARY_RE.finditer(value):
        following = value[match.end() :].lstrip()
        # An initialism visibly continues the same sentence only before a
        # lowercase or numeric token. Uppercase is conservatively a boundary.
        initialism_continues_sentence = bool(following) and (
            following[0].islower() or following[0].isdigit()
        )
        is_internal_initialism = (
            match.group() == "."
            and INITIALISM_END_RE.search(value[: match.end()])
            and initialism_continues_sentence
        )
        if not is_internal_initialism:
            count += 1
    return count


def selected_skill_files(skill_name: str | None) -> list[Path]:
    if skill_name:
        return [SKILLS_DIR / skill_name / "SKILL.md"]
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def extract_runtime_section(path: Path, text: str) -> tuple[str | None, list[str]]:
    matches = list(RUNTIME_HEADING_RE.finditer(text))
    if len(matches) != 1:
        return None, [f"{path}: expected exactly one '## Runtime intake' section"]

    start = matches[0].end()
    next_heading = SECTION_HEADING_RE.search(text, start)
    end = next_heading.start() if next_heading else len(text)
    return text[start:end], []


def validate_skill(path: Path, text: str) -> list[str]:
    runtime_section, errors = extract_runtime_section(path, text)
    if runtime_section is None:
        return errors

    for required in REQUIRED_RUNTIME_TEXT:
        if required not in runtime_section:
            errors.append(f"{path}: runtime intake missing {required!r}")

    normalized_section = normalize_whitespace(runtime_section)
    if CONNECTED_RUNTIME_CONTRACT not in normalized_section:
        errors.append(
            f"{path}: runtime intake missing exact connected catalog contract"
        )
    return errors


def validate_catalog(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_REFERENCE_HEADINGS:
        if heading not in text:
            errors.append(f"{path}: missing {heading!r}")
    required_adaptation = (
        ("Claude projection", CLAUDE_ADAPTATION),
        ("Codex projection", CODEX_ADAPTATION),
        ("fallback and free-text Other", FALLBACK_ADAPTATION),
    )
    for name, required_text in required_adaptation:
        if required_text not in text:
            errors.append(f"{path}: missing exact {name} language")

    matches = list(CATALOG_RE.finditer(text))
    if len(matches) != 1:
        errors.append(f"{path}: expected exactly one JSON catalog")
        return errors

    try:
        payload = json.loads(
            matches[0].group("payload"),
            object_pairs_hook=object_with_unique_keys,
        )
    except DuplicateJSONKeyError as exc:
        errors.append(f"{path}: duplicate JSON object key {exc.key!r}")
        return errors
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON catalog: {exc}")
        return errors

    if not isinstance(payload, dict):
        errors.append(f"{path}: catalog must be a JSON object")
        return errors
    if set(payload) != CATALOG_KEYS:
        errors.append(f"{path}: catalog keys must be exactly {{questions}}")

    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"{path}: questions must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, question in enumerate(questions, start=1):
        prefix = f"{path}: question {index}"
        if not isinstance(question, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if set(question) != QUESTION_KEYS:
            errors.append(
                f"{prefix} question keys must be exactly "
                "{id, ask_when, header, question, options}"
            )

        question_id = question.get("id")
        if not isinstance(question_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]*", question_id
        ):
            errors.append(f"{prefix} has invalid id")
        elif question_id in seen_ids:
            errors.append(f"{prefix} duplicates id {question_id!r}")
        else:
            seen_ids.add(question_id)

        ask_when = question.get("ask_when")
        if not is_nonempty_stripped(ask_when):
            errors.append(f"{prefix} `ask_when` must be non-empty and stripped")

        header = question.get("header")
        if not is_nonempty_stripped(header):
            errors.append(f"{prefix} `header` must be non-empty and stripped")
        elif not 1 <= len(header) <= 12:
            errors.append(f"{prefix} header must contain 1-12 characters")

        prompt = question.get("question")
        if not is_nonempty_stripped(prompt):
            errors.append(f"{prefix} `question` must be non-empty and stripped")
        elif not prompt.endswith("?"):
            errors.append(f"{prefix} must contain exactly one question sentence")
        elif prompt.count("?") != 1:
            errors.append(f"{prefix} must contain exactly one question mark")
        elif sentence_boundary_count(prompt) != 1:
            errors.append(f"{prefix} must contain exactly one sentence boundary")

        options = question.get("options")
        if not isinstance(options, list) or not 2 <= len(options) <= 3:
            errors.append(f"{prefix} must have 2-3 options")
            continue

        labels: set[str] = set()
        for option_index, option in enumerate(options, start=1):
            option_prefix = f"{prefix} option {option_index}"
            if not isinstance(option, dict):
                errors.append(f"{option_prefix} must be an object")
                continue
            if set(option) != OPTION_KEYS:
                errors.append(
                    f"{option_prefix} option keys must be exactly "
                    "{label, description}"
                )
            label = option.get("label")
            description = option.get("description")
            if not is_nonempty_stripped(label):
                errors.append(
                    f"{option_prefix} `label` must be non-empty and stripped"
                )
            elif label in labels:
                errors.append(f"{option_prefix} duplicates label {label!r}")
            else:
                labels.add(label)
                words = label.removesuffix(" (Recommended)").split()
                if not 1 <= len(words) <= 5:
                    errors.append(f"{option_prefix} label must contain 1-5 words")
            if not is_nonempty_stripped(description):
                errors.append(
                    f"{option_prefix} `description` must be non-empty and stripped"
                )
            elif (
                not description.endswith((".", "!", "?"))
                or sentence_boundary_count(description) != 1
            ):
                errors.append(
                    f"{option_prefix} description must contain exactly one sentence"
                )

        first_label = options[0].get("label") if isinstance(options[0], dict) else ""
        if not isinstance(first_label, str) or not first_label.endswith("(Recommended)"):
            errors.append(f"{prefix} first option must end with '(Recommended)'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?")
    args = parser.parse_args()
    errors: list[str] = []
    skill_files = selected_skill_files(args.skill)

    for skill_file in skill_files:
        if not skill_file.exists():
            errors.append(f"{skill_file}: missing skill")
            continue
        skill_text = skill_file.read_text(encoding="utf-8")
        errors.extend(validate_skill(skill_file, skill_text))

        reference = skill_file.parent / "references" / "runtime-intake.md"
        if not reference.exists():
            errors.append(f"{reference}: missing runtime-intake reference")
            continue
        errors.extend(validate_catalog(reference, reference.read_text(encoding="utf-8")))

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    print(f"OK: {len(skill_files)} runtime-intake catalogs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
