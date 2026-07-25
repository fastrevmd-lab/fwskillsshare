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
FENCE_LINE_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)"
    r"(?P<ending>\r\n|\n|\r)?\Z"
)
LIST_ITEM_FENCE_LINE_RE = re.compile(
    r"^(?P<container> {0,3}(?:[-+*]|[0-9]{1,9}[.)]) {1,4})"
    r"(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)"
    r"(?P<ending>\r\n|\n|\r)?\Z"
)
COMMONMARK_TYPE6_TAGS = (
    "address",
    "article",
    "aside",
    "base",
    "basefont",
    "blockquote",
    "body",
    "caption",
    "center",
    "col",
    "colgroup",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "iframe",
    "legend",
    "li",
    "link",
    "main",
    "menu",
    "menuitem",
    "nav",
    "noframes",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "search",
    "section",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "track",
    "ul",
)
COMMONMARK_TYPE6_TAG_PATTERN = "|".join(COMMONMARK_TYPE6_TAGS)
RAW_HTML_TYPE1_RE = re.compile(
    r"^ {0,3}</?(?:pre|script|style|textarea)(?=[ \t>]|\r?$)",
    re.ASCII | re.IGNORECASE | re.MULTILINE,
)
RAW_HTML_PROCESSING_INSTRUCTION_RE = re.compile(r"^ {0,3}<\?", re.MULTILINE)
RAW_HTML_DECLARATION_RE = re.compile(r"^ {0,3}<![A-Za-z]", re.MULTILINE)
RAW_HTML_CDATA_RE = re.compile(r"^ {0,3}<!\[CDATA\[", re.MULTILINE)
RAW_HTML_TYPE6_RE = re.compile(
    rf"^ {{0,3}}</?(?:{COMMONMARK_TYPE6_TAG_PATTERN})"
    rf"(?=[ \t>]|\r?$|/>)",
    re.ASCII | re.IGNORECASE | re.MULTILINE,
)
RAW_HTML_TAG_NAME_PATTERN = r"[A-Za-z][A-Za-z0-9-]*"
RAW_HTML_ATTRIBUTE_NAME_PATTERN = r"[A-Za-z_:][A-Za-z0-9_.:-]*"
RAW_HTML_UNQUOTED_VALUE_PATTERN = r"""[^ \t\n\r"'=<>`]+"""
RAW_HTML_ATTRIBUTE_VALUE_PATTERN = (
    rf"""(?:{RAW_HTML_UNQUOTED_VALUE_PATTERN}|'[^']*'|"[^"]*")"""
)
RAW_HTML_ATTRIBUTE_PATTERN = (
    rf"[ \t]+{RAW_HTML_ATTRIBUTE_NAME_PATTERN}"
    rf"(?:[ \t]*=[ \t]*{RAW_HTML_ATTRIBUTE_VALUE_PATTERN})?"
)
RAW_HTML_TYPE7_OPEN_TAG_PATTERN = (
    r"<(?!(?i:pre|script|style|textarea)(?=[ \t/>]))"
    rf"{RAW_HTML_TAG_NAME_PATTERN}(?:{RAW_HTML_ATTRIBUTE_PATTERN})*[ \t]*/?>"
)
RAW_HTML_TYPE7_CLOSING_TAG_PATTERN = (
    rf"</{RAW_HTML_TAG_NAME_PATTERN}[ \t]*>"
)
RAW_HTML_TYPE7_RE = re.compile(
    rf"^ {{0,3}}(?:{RAW_HTML_TYPE7_OPEN_TAG_PATTERN}|"
    rf"{RAW_HTML_TYPE7_CLOSING_TAG_PATTERN})[ \t]*\r?$",
    re.MULTILINE,
)
RAW_HTML_BLOCK_OPENERS = (
    RAW_HTML_TYPE1_RE,
    RAW_HTML_PROCESSING_INSTRUCTION_RE,
    RAW_HTML_DECLARATION_RE,
    RAW_HTML_CDATA_RE,
    RAW_HTML_TYPE6_RE,
    RAW_HTML_TYPE7_RE,
)
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
STANDARD_INTRO = (
    "Before starting the workflow, inspect the request, supplied artifacts, and "
    "available approved read-only evidence. If unresolved facts could materially "
    "change safety, scope, correctness, confidence, or the requested output, read "
    "`references/runtime-intake.md`."
)
STANDARD_SAFETY = (
    "Never request secrets or unredacted customer data. Treat intake answers as "
    "task context, not approval for a live change; obtain separate explicit "
    "approval before configuration, commit, upgrade, reboot, delete, or failover "
    "actions."
)
COMPACT_INTRO = (
    "Before acting, inspect the request, artifacts, and approved read-only "
    "evidence. If unresolved facts materially change safety, scope, correctness, "
    "confidence, or output, read `references/runtime-intake.md`."
)
COMPACT_SAFETY = (
    "Never request secrets or unredacted customer data. Answers are context, not "
    "live-change approval; obtain separate explicit approval before configuration, "
    "commit, upgrade, reboot, delete, or failover."
)
STANDARD_RUNTIME_TEMPLATE = " ".join(
    (
        STANDARD_INTRO,
        INVOCATION_CLAUSE,
        ROUNDS_CLAUSE,
        FALLBACK_CLAUSE,
        STANDARD_SAFETY,
    )
)
COMPACT_SCOPE_TEXT = {
    "srx-mnha": (
        "Use this skill only for MNHA-specific design and behavior. Use "
        "`parsing-srx-configs` for full-config extraction, `srx-nat` for general "
        "NAT, and `srx-policy` for general policy design."
    ),
    "srx-policy": (
        "Use this skill for SRX policy behavior after relevant configuration is "
        "identified. Use `parsing-srx-configs` for full-config extraction and "
        "`srx-nat` when translation changes the policy match."
    ),
}
APPROVED_RUNTIME_TEMPLATES = {
    skill_name: " ".join(
        (
            scope_text,
            COMPACT_INTRO,
            INVOCATION_CLAUSE,
            ROUNDS_CLAUSE,
            FALLBACK_CLAUSE,
            COMPACT_SAFETY,
        )
    )
    for skill_name, scope_text in COMPACT_SCOPE_TEXT.items()
}
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


def approved_runtime_template(path: Path) -> str:
    return APPROVED_RUNTIME_TEMPLATES.get(
        path.parent.name,
        STANDARD_RUNTIME_TEMPLATE,
    )


def mask_non_newline_characters(text: str) -> str:
    return "".join(char if char in "\r\n" else " " for char in text)


def mask_html_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    """Mask HTML comments on one physical line without changing offsets."""
    masked_parts: list[str] = []
    cursor = 0
    while cursor < len(line):
        if in_comment:
            comment_end = line.find("-->", cursor)
            if comment_end == -1:
                masked_parts.append(mask_non_newline_characters(line[cursor:]))
                return "".join(masked_parts), True
            end = comment_end + len("-->")
            masked_parts.append(mask_non_newline_characters(line[cursor:end]))
            cursor = end
            in_comment = False
            continue

        comment_start = line.find("<!--", cursor)
        if comment_start == -1:
            masked_parts.append(line[cursor:])
            break
        masked_parts.append(line[cursor:comment_start])
        cursor = comment_start
        in_comment = True

    return "".join(masked_parts), in_comment


def mask_inactive_markdown(text: str) -> str:
    """Blank HTML comments and fenced code while preserving offsets/newlines."""
    masked_lines: list[str] = []
    in_comment = False
    fence_character: str | None = None
    fence_length = 0
    fence_container_indent = 0

    for line in text.splitlines(keepends=True):
        if fence_character is not None:
            list_container_ended = (
                fence_container_indent > 0
                and bool(line.strip(" \t\r\n"))
                and not line.startswith(" " * fence_container_indent)
            )
            if list_container_ended:
                fence_character = None
                fence_length = 0
                fence_container_indent = 0
            else:
                closing_candidate = (
                    line[fence_container_indent:]
                    if line.startswith(" " * fence_container_indent)
                    else ""
                )
                fence_match = FENCE_LINE_RE.fullmatch(closing_candidate)
                masked_lines.append(mask_non_newline_characters(line))
                if (
                    fence_match is not None
                    and fence_match.group("fence")[0] == fence_character
                    and len(fence_match.group("fence")) >= fence_length
                    and not fence_match.group("rest").strip(" \t")
                ):
                    fence_character = None
                    fence_length = 0
                    fence_container_indent = 0
                continue

        fence_match = FENCE_LINE_RE.fullmatch(line)
        list_fence_match = LIST_ITEM_FENCE_LINE_RE.fullmatch(line)
        opener_match = fence_match or list_fence_match
        if not in_comment and opener_match is not None:
            fence = opener_match.group("fence")
            info = opener_match.group("rest")
            valid_opener = fence[0] == "~" or "`" not in info
            if valid_opener:
                fence_character = fence[0]
                fence_length = len(fence)
                fence_container_indent = (
                    len(list_fence_match.group("container"))
                    if list_fence_match is not None
                    else 0
                )
                masked_lines.append(mask_non_newline_characters(line))
                continue

        masked_line, in_comment = mask_html_comments(line, in_comment)
        masked_lines.append(masked_line)

    return "".join(masked_lines)


def extract_runtime_section(path: Path, text: str) -> tuple[str | None, list[str]]:
    active_markdown = mask_inactive_markdown(text)
    matches = list(RUNTIME_HEADING_RE.finditer(active_markdown))
    if len(matches) != 1:
        return None, [f"{path}: expected exactly one '## Runtime intake' section"]

    start = matches[0].end()
    next_heading = SECTION_HEADING_RE.search(active_markdown, start)
    end = next_heading.start() if next_heading else len(text)
    return text[start:end], []


def validate_ambiguous_markup(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    if "<!--" in text or "-->" in text:
        errors.append(f"{path}: HTML comment delimiters are not allowed")
    active_markdown = mask_inactive_markdown(text)
    if any(pattern.search(active_markdown) for pattern in RAW_HTML_BLOCK_OPENERS):
        errors.append(f"{path}: raw HTML block syntax is not allowed")
    return errors


def validate_skill(path: Path, text: str) -> list[str]:
    markup_errors = validate_ambiguous_markup(path, text)
    if markup_errors:
        return markup_errors

    runtime_section, errors = extract_runtime_section(path, text)
    if runtime_section is None:
        return errors

    normalized_section = normalize_whitespace(runtime_section)
    if normalized_section != approved_runtime_template(path):
        errors.append(f"{path}: runtime intake does not match approved template")
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
