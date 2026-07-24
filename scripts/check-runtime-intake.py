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
REQUIRED_SKILL_TEXT = (
    "## Runtime intake",
    "references/runtime-intake.md",
    "AskUserQuestion",
    "request_user_input",
    "at most three",
    "plain text",
    "Never request secrets",
    "separate explicit approval",
)
REQUIRED_REFERENCE_HEADINGS = (
    "# Runtime Intake",
    "## When to ask",
    "## Tool adaptation",
    "## Question catalog",
)


def selected_skill_files(skill_name: str | None) -> list[Path]:
    if skill_name:
        return [SKILLS_DIR / skill_name / "SKILL.md"]
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def validate_catalog(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_REFERENCE_HEADINGS:
        if heading not in text:
            errors.append(f"{path}: missing {heading!r}")

    matches = list(CATALOG_RE.finditer(text))
    if len(matches) != 1:
        errors.append(f"{path}: expected exactly one JSON catalog")
        return errors

    try:
        payload = json.loads(matches[0].group("payload"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON catalog: {exc}")
        return errors

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
        if not isinstance(ask_when, str) or not ask_when.strip():
            errors.append(f"{prefix} has empty ask_when")

        header = question.get("header")
        if not isinstance(header, str) or not 1 <= len(header) <= 12:
            errors.append(f"{prefix} header must contain 1-12 characters")

        prompt = question.get("question")
        if not isinstance(prompt, str) or not prompt.strip().endswith("?"):
            errors.append(f"{prefix} question must be non-empty and end with '?'")

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
            label = option.get("label")
            description = option.get("description")
            if not isinstance(label, str) or not label.strip():
                errors.append(f"{option_prefix} has empty label")
            elif label in labels:
                errors.append(f"{option_prefix} duplicates label {label!r}")
            else:
                labels.add(label)
                words = label.removesuffix(" (Recommended)").split()
                if not 1 <= len(words) <= 5:
                    errors.append(f"{option_prefix} label must contain 1-5 words")
            if (
                not isinstance(description, str)
                or not description.strip().endswith((".", "!", "?"))
            ):
                errors.append(f"{option_prefix} description must be one sentence")

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
        for required in REQUIRED_SKILL_TEXT:
            if required not in skill_text:
                errors.append(f"{skill_file}: missing {required!r}")

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
