# Portable Runtime Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add conditional, Claude/Codex-compatible runtime intake to all 22 firewall skills without making any package depend on repository-local shared content.

**Architecture:** Put a concise invocation contract in every `SKILL.md` and the complete skill-specific catalog in that package's `references/runtime-intake.md`. Add a Python standard-library validator that checks the shared behavioral contract and the neutral JSON question schema, then execute a separate RED/GREEN cycle for every skill.

**Tech Stack:** Markdown skill packages, JSON catalogs embedded in Markdown, Python 3 standard library validation, YAML UI metadata, `just`, pre-commit, Trivy, and Git.

## Global Constraints

- Work only in `.worktrees/runtime-intake-questions` on branch `runtime-intake-questions`.
- Execute with fresh sequential implementer and reviewer subagents; the user
  explicitly authorized subagent-driven execution after approving the plan.
- Update all 22 packages listed in the approved design.
- Keep each package independently installable; every runtime reference lives below its own skill directory.
- Do not modify any copied `intermediate-schema.md`.
- Keep every `SKILL.md` at or below 500 lines.
- Ask only when an unresolved answer materially changes safety, scope, correctness, confidence, or output.
- Inspect the prompt and approved read-only evidence before asking.
- For each unresolved material fact whose catalog condition is true, ask its catalog question before continuing or issuing an open-ended request.
- Never repeat answered questions or show the full catalog.
- Ask no more than three single-select catalog questions per interaction round.
- After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain.
- Use Claude `AskUserQuestion`, Codex `request_user_input`, or a concise plain-text fallback.
- In plain text, preserve each selected catalog question's 2-3 labeled choices and free-text `Other` path; do not substitute a generic checklist.
- Never request passwords, PSKs, private keys, tokens, device credentials, or unredacted customer data.
- Treat answers as context, not authorization for configuration, commit, upgrade, reboot, delete, or failover.
- Obtain separate explicit approval immediately before any live or destructive action.
- Use the exact question data in Appendix A. Minor punctuation wrapping is allowed; changing semantic choices is not.
- Do not contact devices or run real-device integration.

Use this exact section in every `SKILL.md` except `srx-mnha` and `srx-policy`,
immediately before its main workflow or first procedural section:

```markdown
## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.
```

For `srx-mnha`, replace the existing four-line `## Scope and routing` block
with this exact compact form so the file remains below 500 lines:

```markdown
## Runtime intake

Use this skill only for MNHA-specific design and behavior. Use `parsing-srx-configs` for full-config extraction, `srx-nat` for general NAT, and `srx-policy` for general policy design.
Before acting, inspect the request, artifacts, and approved read-only evidence. If unresolved facts materially change safety, scope, correctness, confidence, or output, read `references/runtime-intake.md`. For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request. Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog. Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist. Never request secrets or unredacted customer data. Answers are context, not live-change approval; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover.
```

For `srx-policy`, replace the existing four-line `## Scope and routing` block
with this exact compact form:

```markdown
## Runtime intake

Use this skill for SRX policy behavior after relevant configuration is identified. Use `parsing-srx-configs` for full-config extraction and `srx-nat` when translation changes the policy match.
Before acting, inspect the request, artifacts, and approved read-only evidence. If unresolved facts materially change safety, scope, correctness, confidence, or output, read `references/runtime-intake.md`. For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request. Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog. Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist. Never request secrets or unredacted customer data. Answers are context, not live-change approval; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover.
```

Every `references/runtime-intake.md` must use this structure:

````markdown
# Runtime Intake

## When to ask

Use this catalog only after inspecting the request and evidence. Ask an entry
when its `ask_when` condition is true and the answer would materially affect
the result. Skip answered or irrelevant entries. Prioritize safety, scope,
platform or framework basis, evidence quality, then output preference.

## Tool adaptation

- Claude: select at most three neutral entries, project each to only `question`,
  `header`, and `options`, then add `multiSelect: false`; do not send `id` or
  `ask_when`.
- Codex: select at most three neutral entries and project each to only `id`,
  `header`, `question`, and `options`; do not send `ask_when` or `multiSelect`.
- Fallback: ask the same questions in concise plain text with a free-text
  `Other` path.
- Never request secrets.

## Question catalog

```json
{
  "questions": [
    {
      "id": "audit_scope",
      "ask_when": "The requested audit components or boundaries are unclear.",
      "header": "Scope",
      "question": "What should the audit cover?",
      "options": [
        {
          "label": "Full device (Recommended)",
          "description": "Include policy, NAT, objects, zones, routing context, and logging."
        },
        {
          "label": "Rulebase only",
          "description": "Limit analysis to security-policy hygiene."
        }
      ]
    }
  ]
}
```
````

The embedded neutral JSON has exactly the top-level key `questions`. Each
question has exactly `id`, `ask_when`, `header`, `question`, and `options`;
each option has exactly `label` and `description`. All text values are nonblank
and stripped. Each prompt is exactly one question sentence with one question
mark, and each description is exactly one sentence.

---

### Task 1: Repair the Proxmox package baseline

**Files:**
- Modify: `scripts/check-skill-packages.py`
- Modify: `skills/sd-onprem-proxmox-deploy/SKILL.md`
- Create: `skills/sd-onprem-proxmox-deploy/agents/openai.yaml`

**Interfaces:**
- Consumes: the committed `sd-onprem-proxmox-deploy` package at baseline commit `05a2946`.
- Produces: a 22-name package inventory and valid author/UI metadata for the Proxmox skill.

- [ ] **Step 1: Confirm the three baseline failures**

Run:

```bash
python3 scripts/check-skill-packages.py
```

Expected: exit 1 reporting the unexpected Proxmox skill, missing `GPT` author,
and missing Codex UI metadata.

- [ ] **Step 2: Update the expected package inventory**

Add this entry to `EXPECTED_SKILL_NAMES` in sorted position:

```python
"sd-onprem-proxmox-deploy",
```

- [ ] **Step 3: Complete the package metadata**

Add `GPT` to the existing author list:

```yaml
author:
  - fastrevmd-lab
  - Claude
  - GPT
```

Create `skills/sd-onprem-proxmox-deploy/agents/openai.yaml`:

```yaml
interface:
  display_name: "SD On-Prem Proxmox Deploy"
  short_description: "Deploy Security Director On-Prem on Proxmox"
  default_prompt: "Use $sd-onprem-proxmox-deploy to plan or validate this Security Director On-Prem deployment on Proxmox VE."
```

- [ ] **Step 4: Verify and commit the prerequisite repair**

Run:

```bash
python3 scripts/check-skill-packages.py
git diff --check
```

Expected: `OK: 22 portable skill packages`; no whitespace errors.

Commit:

```bash
git add scripts/check-skill-packages.py \
  skills/sd-onprem-proxmox-deploy/SKILL.md \
  skills/sd-onprem-proxmox-deploy/agents/openai.yaml
git commit -m "fix: complete Proxmox skill packaging"
```

### Task 2: Add the runtime-intake validator

**Files:**
- Create: `scripts/check-runtime-intake.py`

**Interfaces:**
- Consumes: one optional positional skill name and package-local Markdown/JSON.
- Produces: exit 0 with an `OK` line for valid packages; exit 1 with one `ERROR` line per violation.

- [ ] **Step 1: Write the validator before any skill intake section exists**

Create `scripts/check-runtime-intake.py` with this complete implementation:

```python
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
RUNTIME_ATX_HEADING_RE = re.compile(
    r"^(?P<indent> {0,3})##(?P<spacing>[ \t]+)Runtime intake"
    r"(?P<closing>[ \t]+#+)?[ \t]*\r?$",
    re.MULTILINE,
)
RUNTIME_SETEXT_HEADING_RE = re.compile(
    r"^ {0,3}Runtime intake[ \t]*\r?\n"
    r" {0,3}(?:=+|-+)[ \t]*\r?$",
    re.MULTILINE,
)
SECTION_HEADING_RE = re.compile(r"^ {0,3}## [^\r\n]+\r?$", re.MULTILINE)
FENCE_LINE_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)"
    r"(?P<ending>\r\n|\n|\r)?\Z"
)
LIST_ITEM_FENCE_LINE_RE = re.compile(
    r"^(?P<container> {0,3}(?:(?P<bullet>[-+*])|"
    r"(?P<ordered>[0-9]{1,9})[.)]) {1,4})"
    r"(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)"
    r"(?P<ending>\r\n|\n|\r)?\Z"
)
ATX_BLOCK_BOUNDARY_RE = re.compile(
    r"^ {0,3}#{1,6}(?:[ \t]+|(?=\r?$))"
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
    paragraph_open = False

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
        list_fence_can_open = (
            list_fence_match is not None
            and (
                list_fence_match.group("bullet") is not None
                or not paragraph_open
                or int(list_fence_match.group("ordered")) == 1
            )
        )
        opener_match = fence_match or (
            list_fence_match if list_fence_can_open else None
        )
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
                paragraph_open = False
                masked_lines.append(mask_non_newline_characters(line))
                continue

        masked_line, in_comment = mask_html_comments(line, in_comment)
        masked_lines.append(masked_line)
        if not masked_line.strip(" \t\r\n"):
            paragraph_open = False
        elif ATX_BLOCK_BOUNDARY_RE.match(masked_line):
            paragraph_open = False
        else:
            # Conservatively keep unfamiliar active syntax in paragraph
            # context so it cannot make a later non-1 marker hide content.
            paragraph_open = True

    return "".join(masked_lines)


def extract_runtime_section(path: Path, text: str) -> tuple[str | None, list[str]]:
    active_markdown = mask_inactive_markdown(text)
    runtime_headings = [
        ("atx", match)
        for match in RUNTIME_ATX_HEADING_RE.finditer(active_markdown)
    ]
    runtime_headings.extend(
        ("setext", match)
        for match in RUNTIME_SETEXT_HEADING_RE.finditer(active_markdown)
    )
    runtime_headings.sort(key=lambda item: item[1].start())
    if len(runtime_headings) != 1:
        return None, [f"{path}: expected exactly one '## Runtime intake' section"]

    heading_kind, heading_match = runtime_headings[0]
    if heading_kind == "atx" and heading_match.group("indent"):
        return None, [
            f"{path}: primary '## Runtime intake' heading must start at column zero"
        ]
    if (
        heading_kind != "atx"
        or heading_match.group("spacing") != " "
        or heading_match.group("closing") is not None
    ):
        return None, [
            f"{path}: primary '## Runtime intake' heading must use canonical "
            "column-zero ATX form"
        ]

    start = heading_match.end()
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
    active_markdown = mask_inactive_markdown(text)
    if "<!--" in text or "-->" in text:
        errors.append(f"{path}: HTML comment delimiters are not allowed")
    if any(pattern.search(active_markdown) for pattern in RAW_HTML_BLOCK_OPENERS):
        errors.append(f"{path}: raw HTML block syntax is not allowed")
    for heading in REQUIRED_REFERENCE_HEADINGS:
        heading_matches = re.findall(
            rf"^{re.escape(heading)}[ \t]*\r?$",
            active_markdown,
            re.MULTILINE,
        )
        if not heading_matches:
            errors.append(f"{path}: missing {heading!r}")
        elif len(heading_matches) != 1:
            errors.append(
                f"{path}: expected exactly one active {heading!r} heading"
            )
    required_adaptation = (
        ("Claude projection", CLAUDE_ADAPTATION),
        ("Codex projection", CODEX_ADAPTATION),
        ("fallback and free-text Other", FALLBACK_ADAPTATION),
    )
    for name, required_text in required_adaptation:
        if required_text not in active_markdown:
            errors.append(f"{path}: missing exact {name} language")

    matches = list(CATALOG_RE.finditer(text))
    if len(matches) != 1:
        errors.append(f"{path}: expected exactly one JSON catalog")
        return errors

    try:
        payload = json.loads(matches[0].group("payload"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON catalog: {exc}")
        return errors

    if not isinstance(payload, dict):
        errors.append(f"{path}: catalog must be a JSON object")
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
```

- [ ] **Step 2: Run the first RED test**

Run:

```bash
python3 scripts/check-runtime-intake.py firewall-best-practices-audit
```

Expected: exit 1 reporting the missing `## Runtime intake` section and missing
`references/runtime-intake.md`. This proves the validator detects the absent
feature.

- [ ] **Step 3: Validate the validator itself**

Run:

```bash
python3 -m py_compile scripts/check-runtime-intake.py
git diff --check
```

Expected: both commands exit 0.

- [ ] **Step 4: Commit the RED validator**

```bash
git add scripts/check-runtime-intake.py
git commit -m "test: require portable runtime intake"
```

### Tasks 3-24: Add intake to each skill sequentially

For every task below, use the exact shared `SKILL.md` section and reference
structure from Global Constraints, and the exact catalog rows from Appendix A.
Do not start the next task until the focused validator passes and the current
skill is committed.

Each task follows this complete cycle:

1. Run `python3 scripts/check-runtime-intake.py <skill>` and confirm exit 1 for
   the missing feature.
2. Add the shared `## Runtime intake` section to `<skill>/SKILL.md`.
3. Create `<skill>/references/runtime-intake.md` with the shared reference
   headings and that skill's Appendix A catalog serialized as valid JSON.
4. Run:

   ```bash
   python3 scripts/check-runtime-intake.py <skill>
   python3 scripts/check-skill-packages.py
   git diff --check
   ```

   Expect all three commands to exit 0.
5. Commit only that skill:

   ```bash
   git add skills/<skill>/SKILL.md skills/<skill>/references/runtime-intake.md
   git commit -m "feat(<skill>): add runtime intake"
   ```

### Task 3: `cis-controls-ngfw-compliance`

**Files:** Modify `skills/cis-controls-ngfw-compliance/SKILL.md`; create
`skills/cis-controls-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.1 (`cis_goal`, `cis_version`, `cis_ig`, `cis_scope`,
`cis_evidence`, `cis_output`).

### Task 4: `cmmc-nist-800-171-ngfw-compliance`

**Files:** Modify `skills/cmmc-nist-800-171-ngfw-compliance/SKILL.md`; create
`skills/cmmc-nist-800-171-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.2 (`cmmc_basis`, `cmmc_overlay`, `cmmc_stage`,
`cmmc_boundary`, `cmmc_assets`, `cmmc_evidence`, `cmmc_output`).

### Task 5: `firewall-best-practices-audit`

**Files:** Modify `skills/firewall-best-practices-audit/SKILL.md`; create
`skills/firewall-best-practices-audit/references/runtime-intake.md`.

**Catalog:** Appendix A.3 (`audit_goal`, `audit_scope`, `audit_boundary`,
`audit_evidence`, `audit_context`, `audit_depth`, `audit_remed`).

### Task 6: `firewall-config-conversion`

**Files:** Modify `skills/firewall-config-conversion/SKILL.md`; create
`skills/firewall-config-conversion/references/runtime-intake.md`.

**Catalog:** Appendix A.4 (`convert_source`, `convert_target`,
`convert_release`, `convert_scope`, `convert_base`, `convert_loss`,
`convert_output`).

### Task 7: `firewall-config-diff`

**Files:** Modify `skills/firewall-config-diff/SKILL.md`; create
`skills/firewall-config-diff/references/runtime-intake.md`.

**Catalog:** Appendix A.5 (`diff_goal`, `diff_direction`, `diff_scope`,
`diff_identity`, `diff_ignore`, `diff_output`).

### Task 8: `hipaa-ngfw-compliance`

**Files:** Modify `skills/hipaa-ngfw-compliance/SKILL.md`; create
`skills/hipaa-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.6 (`hipaa_role`, `hipaa_goal`, `hipaa_scope`,
`hipaa_vendor`, `hipaa_evidence`, `hipaa_output`).

### Task 9: `iso27001-ngfw-compliance`

**Files:** Modify `skills/iso27001-ngfw-compliance/SKILL.md`; create
`skills/iso27001-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.7 (`iso_goal`, `iso_scope`, `iso_soa`, `iso_basis`,
`iso_period`, `iso_output`).

### Task 10: `parsing-cisco-configs`

**Files:** Modify `skills/parsing-cisco-configs/SKILL.md`; create
`skills/parsing-cisco-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.8 (`cisco_goal`, `cisco_platform`, `cisco_coverage`,
`cisco_scope`, `cisco_output`).

### Task 11: `parsing-fortinet-configs`

**Files:** Modify `skills/parsing-fortinet-configs/SKILL.md`; create
`skills/parsing-fortinet-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.9 (`forti_goal`, `forti_coverage`, `forti_vdom`,
`forti_scope`, `forti_output`).

### Task 12: `parsing-palo-configs`

**Files:** Modify `skills/parsing-palo-configs/SKILL.md`; create
`skills/parsing-palo-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.10 (`palo_goal`, `palo_format`, `palo_scope`,
`palo_inheritance`, `palo_coverage`, `palo_output`).

### Task 13: `parsing-srx-configs`

**Files:** Modify `skills/parsing-srx-configs/SKILL.md`; create
`skills/parsing-srx-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.11 (`srxp_goal`, `srxp_format`, `srxp_scope`,
`srxp_coverage`, `srxp_output`).

### Task 14: `pci-ngfw-compliance`

**Files:** Modify `skills/pci-ngfw-compliance/SKILL.md`; create
`skills/pci-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.12 (`pci_version`, `pci_overlay`, `pci_stage`,
`pci_scope`, `pci_segment`, `pci_evidence`, `pci_output`).

### Task 15: `sd-onprem-proxmox-deploy`

**Files:** Modify `skills/sd-onprem-proxmox-deploy/SKILL.md`; create
`skills/sd-onprem-proxmox-deploy/references/runtime-intake.md`.

**Catalog:** Appendix A.13 (`sd_stage`, `sd_release`, `sd_media`, `sd_size`,
`sd_proxmox`, `sd_network`, `sd_services`, `sd_transfer`, `sd_secrets`,
`sd_onboard`).

### Task 16: `soc2-ngfw-compliance`

**Files:** Modify `skills/soc2-ngfw-compliance/SKILL.md`; create
`skills/soc2-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.14 (`soc2_type`, `soc2_tsc`, `soc2_period`,
`soc2_system`, `soc2_vendor`, `soc2_output`).

### Task 17: `srx-advpn`

**Files:** Modify `skills/srx-advpn/SKILL.md`; create
`skills/srx-advpn/references/runtime-intake.md`.

**Catalog:** Appendix A.15 (`advpn_task`, `advpn_release`, `advpn_topo`,
`advpn_auth`, `advpn_route`, `advpn_traffic`, `advpn_gateway`,
`advpn_evidence`).

### Task 18: `srx-autovpn-full-tunnel`

**Files:** Modify `skills/srx-autovpn-full-tunnel/SKILL.md`; create
`skills/srx-autovpn-full-tunnel/references/runtime-intake.md`.

**Catalog:** Appendix A.16 (`autovpn_task`, `autovpn_release`,
`autovpn_traffic`, `autovpn_auth`, `autovpn_lans`, `autovpn_nat`,
`autovpn_route`, `autovpn_evidence`).

### Task 19: `srx-dynamic-ip-feed`

**Files:** Modify `skills/srx-dynamic-ip-feed/SKILL.md`; create
`skills/srx-dynamic-ip-feed/references/runtime-intake.md`.

**Catalog:** Appendix A.17 (`dif_task`, `dif_release`, `dif_source`, `dif_tls`,
`dif_auth`, `dif_route`, `dif_effect`, `dif_session`, `dif_poll`).

### Task 20: `srx-ipsec-hub-spoke`

**Files:** Modify `skills/srx-ipsec-hub-spoke/SKILL.md`; create
`skills/srx-ipsec-hub-spoke/references/runtime-intake.md`.

**Catalog:** Appendix A.18 (`hsvpn_task`, `hsvpn_release`, `hsvpn_topo`,
`hsvpn_traffic`, `hsvpn_auth`, `hsvpn_route`, `hsvpn_evidence`).

### Task 21: `srx-mnha`

**Files:** Modify `skills/srx-mnha/SKILL.md`; create
`skills/srx-mnha/references/runtime-intake.md`.

**Catalog:** Appendix A.19 (`mnha_task`, `mnha_release`, `mnha_mode`,
`mnha_migrate`, `mnha_topo`, `mnha_service`, `mnha_route`, `mnha_objective`,
`mnha_test`).

Use the compact replacement form from Global Constraints and preserve the
existing MNHA scope sentence verbatim.

### Task 22: `srx-mpls-in-flow`

**Files:** Modify `skills/srx-mpls-in-flow/SKILL.md`; create
`skills/srx-mpls-in-flow/references/runtime-intake.md`.

**Catalog:** Appendix A.20 (`mpls_task`, `mpls_release`, `mpls_role`,
`mpls_family`, `mpls_signal`, `mpls_vrf`, `mpls_policy`, `mpls_service`).

### Task 23: `srx-nat`

**Files:** Modify `skills/srx-nat/SKILL.md`; create
`skills/srx-nat/references/runtime-intake.md`.

**Catalog:** Appendix A.21 (`nat_task`, `nat_release`, `nat_family`,
`nat_tuple`, `nat_context`, `nat_reach`, `nat_return`, `nat_evidence`).

### Task 24: `srx-policy`

**Files:** Modify `skills/srx-policy/SKILL.md`; create
`skills/srx-policy/references/runtime-intake.md`.

**Catalog:** Appendix A.22 (`policy_task`, `policy_release`, `policy_model`,
`policy_flow`, `policy_nat`, `policy_service`, `policy_ip`, `policy_session`).

Use the compact replacement form from Global Constraints and preserve the
existing policy scope sentence verbatim.

### Task 25: Integrate validation and run the handoff suite

**Files:**
- Modify: `justfile`
- Verify: all files changed by Tasks 1-24

**Interfaces:**
- Consumes: 22 passing focused runtime-intake catalogs.
- Produces: runtime-intake validation in the normal lint/release path and fresh handoff evidence.

- [ ] **Step 1: Add runtime intake to lint**

Update `lint` in `justfile` to run:

```make
lint:
    python3 scripts/check-skill-packages.py
    python3 scripts/test-runtime-intake-validator.py
    python3 scripts/check-runtime-intake.py
    python3 scripts/check-runtime-intake-safety.py
    python3 scripts/test-runtime-intake-safety.py
    python3 scripts/check-readme-branding.py
```

- [ ] **Step 2: Run the full runtime and package validation**

```bash
python3 scripts/check-runtime-intake.py
python3 scripts/check-skill-packages.py
python3 scripts/check-readme-branding.py
python3 scripts/check-shared-schema.py
python3 scripts/check-installer.py
git diff --check
```

Expected: 22 runtime catalogs, 22 portable skill packages, branding success,
four identical schemas, existing installer success, and no whitespace errors.

- [ ] **Step 3: Run project-required commands**

If `just` is available:

```bash
just fmt
just lint
just test
just guard
just security
just release-check
```

If `just` remains unavailable, record that limitation and run every underlying
command directly. If `trivy` is available, run:

```bash
trivy fs --scanners vuln,misconfig,secret --exit-code 1 .
```

Do not substitute a claimed security pass when Trivy is unavailable.

- [ ] **Step 4: Inspect the final scope**

```bash
git status --short
git diff --stat 05a2946..HEAD
git log --oneline --decorate -30
```

Expected: only the design, plan, validator, justfile, Proxmox prerequisite
metadata, and the 22 runtime-intake package changes are present.

- [ ] **Step 5: Commit validation integration**

```bash
git add justfile
git commit -m "test: integrate runtime intake validation"
```

### Task 26: Enforce the native projection contract

Harden `scripts/check-runtime-intake.py` with standard-library negative tests
in `scripts/test-runtime-intake-validator.py`. Reject duplicate JSON object
members; unknown keys at every neutral JSON level; native-only question keys
such as `multiSelect`; blank or unstripped `ask_when`, `header`, `question`,
`label`, and `description`; more than one question sentence or question mark;
and more than one sentence-ending boundary in a description. Ignore an
initialism-ending period only when the next non-space token begins with a
lowercase letter or digit; conservatively count it as a boundary before an
uppercase token.

Require every reference to state the exact native projections:

- Claude sends only `question`, `header`, `options`, and
  `multiSelect: false`; it sends neither `id` nor `ask_when`.
- Codex sends only `id`, `header`, `question`, and `options`; it sends neither
  `ask_when` nor `multiSelect`.
- The fallback asks the same questions in concise plain text and retains a
  free-text `Other` path.

Run the negative-contract test script from `just lint` before validating all
22 real catalogs.

## Appendix A: Exact question catalogs

Serialize each row as one neutral-contract question. In the `Options` column,
text before `—` is the label and text after it is the description. The first
option is always the recommended safe default. When the triggering fact is
unresolved, the recommended option must not assert that the missing fact is
known, complete, available, valid, or verified. Rewrite a factual prompt as an
action or workflow decision when necessary so the safe discovery or
verification option directly answers it.

Each two- or three-option set is a mutually exclusive single-select choice
along one material axis. Do not mix evidence availability with collection
method, current state with requested workflow, or address family with special
traffic. Use the free-text `Other` path for exact values. End every serialized
description with a period.

**Task 28 final-review audit:** `scripts/check-runtime-intake-safety.py` parses
all Appendix A rows and all package JSON catalogs. It rejects duplicate
Appendix sections, noncanonical lexical numbering such as `A.01`, incorrect
A.1 through A.22 number/name pairings, duplicate package JSON members, and
noncanonical same-line tabs or doubled spaces in Appendix question fields. It
requires exact per-skill question-object equality and locks all 22 complete
catalog contents and question order with canonical SHA-256 digests, in
addition to the safe-first and single-axis option manifests.

**Task 29 catalog-fallback audit:** the shared `SKILL.md` contract requires each
true unresolved material catalog condition to be asked before continuing or
issuing an open-ended request. Every native-tool round remains limited to at
most three single-select catalog questions. After every response, another round
is required whenever any unresolved material catalog condition remains true;
the workflow continues only when none remain. A plain-text fallback preserves
each selected question's 2-3 labeled choices and free-text `Other` path and
must not substitute a generic checklist. Before heading extraction, the
structural validator conservatively rejects either literal HTML comment
delimiter anywhere in `SKILL.md`, including escaped and inline-code forms, and
keeps that prohibition global even inside fences. It then masks standard
backtick or tilde fenced-code regions, including direct list-item fence
openers, while preserving length, newline positions, and offsets. The separate
list-item opener path permits zero to three spaces before `-`/`+`/`*` or an
ordered marker of one to nine digits plus `.`/`)`, then one to four spaces. It
captures the resulting continuation indentation. The masker tracks whether
active prose has opened a paragraph: document start, blank lines, accepted
fences, and zero-to-three-space ATX headings establish block boundaries, while
unfamiliar active syntax conservatively keeps the paragraph open. Bullet
markers may interrupt that paragraph. Ordered markers may interrupt it only
when their parsed numeric value is `1`, including a leading-zero spelling
within the one-to-nine-digit limit; non-`1` markers open list-item fences only
at a recognized block boundary. Blank lines remain masked inside the list
fence without requiring the captured indentation. A nonblank line lacking the
captured prefix implicitly ends the list container and its unclosed fence,
then falls through for processing as an ordinary fence opener, comment, or
active Markdown on the same iteration. There is no retry loop.
Correctly indented list-item closers are checked by the unchanged ordinary
fence matcher only after that exact prefix is removed; top-level unclosed
fences still mask through end of file. Prose with a later fence sequence or
ten-digit ordered marker, four-space-indented marker, invalid marker spacing,
and backtick info strings containing a backtick remain active rather than
becoming fences. In that active-Markdown view the validator rejects every
CommonMark 0.31.2 raw HTML
block opener family: case-insensitive type 1 `pre`, `script`, `style`, or
`textarea` tags; processing instructions; declarations; CDATA; every type 6
block tag with the specified tag-name boundary; and complete generic type 7
opening or closing tag lines, each with at most three leading spaces.
Raw-looking fenced content and inline placeholders that do not meet a
block-start rule remain valid. The validator discovers runtime and following
section headings with zero to three leading spaces only in that same
active-Markdown view; a four-space-indented form remains code. Discovery
therefore catches active indented duplicates, but the sole approved primary
`## Runtime intake` heading must remain at column zero. The validator slices
the original section by the preserved offsets, normalizes whitespace, selects
the approved standard or skill-specific compact template by skill path, and
requires equality across the complete section. Validator-API mutation probes
reject discretionary
invocation, open-ended native questions, a one-summary fallback, contract
clauses outside the runtime section, complete runtime regions hidden in a
comment, any raw HTML block family, or either fence form, HTML-comment decoys,
escaped and inline-code comment delimiters, fence wrappers around a complete
region, inactive wrappers inside an active section, contradictory trailing
prose, missing approved text, and duplicate active runtime sections. Boundary
probes cover every type 6 tag, generic type 7 attributes and closers, CRLF,
case, indentation, fenced raw syntax, and inline placeholders. List-container
probes cover all bullet markers, both ordered delimiters, one- and nine-digit
boundaries, one-to-four-space marker padding, correctly indented continuations
and closers, all non-comment raw HTML families, offset preservation, invalid
near-markers, and unchanged top-level closer behavior. Container-boundary
probes reject a deindented duplicate runtime section and active raw HTML,
retain unindented blank lines, keep correctly indented content and closers
masked, preserve top-level unclosed-fence behavior, and prove that sibling,
ordinary-fence, and comment transitions are reprocessed. Heading probes cover
one-to-three-space active duplicates, indented following sections, a
column-zero approved primary, and four-space code. Paragraph-interruption
probes keep indented raw HTML and Runtime headings active after `0`, `2`, and
`9` ordered markers, while accepting value `1`, a nine-digit leading-zero
value `1`, bullets, and non-`1` markers at document, blank-line, and
ATX-heading boundaries across both ordered delimiters and both fence
characters. Fenced decoys may coexist with one active valid section. A masker
probe locks CRLF
length/newline/offset preservation, a positive probe permits whitespace-only
variation, and the real-file test applies the same validator to all 22 skills.

The optional skill argument limits equality, digest, safe-default, and
option-tuple assertions to the selected package, while every focused run still
parses all 22 plan and package catalogs and resolves all manifest keys.
Focused output must distinguish those whole-corpus checks from selected
assertion counts.

**Task 30 whole-branch audit:** at that checkpoint, the safety manifests
covered 76 safe first labels and 32 exact single-axis option tuples.
Twenty-four explicit semantic contracts included the separated scope,
framework/overlay, asset, allowlist, third-party-path, parsing-depth,
version/overlay, transfer-method, and CA-source decisions. The two
additive-overlay decisions were independent catalog questions, and every Task
30 rewrite or addition had exact question/option tuple coverage plus a locked
catalog digest.

Structural heading discovery treats optional-closing-hash ATX and Setext
`Runtime intake` headings as equivalents for duplicate detection, while only
the exact column-zero `## Runtime intake` form can be the approved primary.
Reference headings must each be one exact active heading line, exact
adaptation clauses must remain active, and HTML comment or raw-HTML block
syntax is rejected. Raw JSON catalog fences continue to parse from the
original reference.

The Appendix parser reuses the structural active-Markdown mask, so unclosed
fences and comments hide decoy headings and rows. It scans every active H3
whose content begins `A.` as an Appendix lookalike, checks duplicate identities
before requiring an exact canonical heading full match, and retains the exact
22-section lexical number/name order. Active raw-HTML block syntax is rejected.
Installer validation checks every family install and every explicit skill
selection for `SKILL.md`, `references/runtime-intake.md`, and source-present
`agents/openai.yaml` in disposable destinations.

`scripts/test-runtime-intake-safety.py`, run immediately after the checker in
`just lint`, uses temporary files and the real parsers to cover semantic
contracts, inactive and noncanonical Appendix headings, duplicate,
number/name-pairing, lexical-numbering, raw-wrapper, same-line
question/label/description whitespace, focused-output, complete-digest, and
synchronized content/order mutations.

**Task 31 final-review audit:** the 12 named legacy questions now isolate only
their lifecycle, detail, sizing workflow, routing/traffic model, session,
cadence, signaling-workflow, or policy-architecture axis. The new
`diff_format` question preserves the independent result-format decision. All
13 Task 31 objects have exact question/option contracts, safe recommended
discovery or confirmation choices, mutually exclusive supplied-state choices,
and synchronized Appendix/package content plus locked digests. The complete
manifests contain 89 safe first labels and 45 exact option tuples; the semantic
test inventory pins 37 IDs, including all 13 Task 31 objects.

Task 31 structural RED added container, ordering, section-bound, inactive JSON,
and complete-Setext-paragraph probes: 105 tests ran with 46 failures before the
parser change. GREEN passes all 105. Active list and blockquote prefixes are
normalized only after fenced/commented content is masked, so Runtime-heading
equivalents and every raw-HTML block family remain visible without changing
the canonical column-zero primary requirement. Setext duplicate detection
evaluates the complete paragraph, reference headings must be unique and
canonically ordered, adaptation clauses must be inside Tool adaptation, and
the sole line-anchored catalog opener must be active, top-level, and inside
Question catalog.

The safety RED ran 22 tests with eight failures and two errors before Appendix
and package-parser changes. GREEN passes all 22: container-nested Appendix
headings/lookalikes and raw HTML are rejected, inactive fenced/commented decoy
rows cannot contaminate active row slices, and standalone package parsing
reuses structural validation plus active top-level catalog extraction. The
installer RED ran two tests with three artifact-mutation failures; GREEN passes
both mutation tests and verifies byte-identical `SKILL.md`,
`references/runtime-intake.md`, and source-present `agents/openai.yaml` files
across all five family installs and all 22 explicit installs.

Update each Appendix row and its package JSON object together, then require
both focused validators to pass before moving to the next independently
installable skill.

### A.1 `cis-controls-ngfw-compliance`

- `cis_goal`; header `Goal`; ask when the requested assessment outcome is
  absent; question `What outcome should this CIS assessment produce?`; options:
  `Gap assessment (Recommended)` — Identify safeguards, evidence gaps, and
  remediation priorities; `Evidence package` — Organize evidence for an
  existing assessment; `Control mapping` — Map controls without grading
  implementation.
- `cis_version`; header `CIS Version`; ask when the governing CIS version is
  absent; question `Which CIS Controls version should govern the assessment?`;
  options: `CIS v8.1 (Recommended)` — Use the current v8.1 safeguard structure;
  `CIS v8` — Use the original v8 structure; `Org profile` — Follow a supplied
  organizational crosswalk.
- `cis_ig`; header `CIS Group`; ask when the Implementation Group is absent and
  affects safeguard scope; question `Which Implementation Group should be
  assessed?`; options: `IG2 (Recommended)` — Assess IG1 and IG2 for a typical
  enterprise; `IG1` — Limit scope to essential cyber hygiene; `IG3` — Include
  all three groups.
- `cis_scope`; header `Scope`; ask when firewall estate scope is absent;
  question `How should an unspecified firewall estate scope be resolved?`;
  options: `Inventory estate first (Recommended)` — Inventory relevant devices
  and boundaries before selecting assessment scope; `Use supplied full estate`
  — Assess the supplied complete firewall estate and all its boundaries; `Use
  supplied named boundary` — Limit assessment to the supplied named system or
  segment.
- `cis_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configurations, logs, reviews,
  tickets, and operating records before grading; `Assess supplied artifacts` —
  Assess only supplied evidence and disclose coverage gaps; `Build evidence
  request` — List required evidence without grading implementation.
- `cis_output`; header `Output`; ask when deliverable emphasis is absent;
  question `What deliverable should be emphasized?`; options: `Matrix and plan
  (Recommended)` — Produce the safeguard matrix, gaps, and remediation plan;
  `Evidence request` — Emphasize missing assessment artifacts; `Executive
  summary` — Emphasize risk, coverage, and top actions.

### A.2 `cmmc-nist-800-171-ngfw-compliance`

- `cmmc_basis`; header `Basis`; ask when the governing framework or revision is
  absent; question `How should an unspecified assessment framework be
  resolved?`; options: `Confirm framework first (Recommended)` — Confirm the
  governing framework and revision before mapping controls; `Use supplied CMMC
  Level 2` — Assess against the supplied CMMC Level 2 requirements; `Use
  supplied NIST revision` — Assess against the supplied NIST SP 800-171
  revision.
- `cmmc_overlay`; header `Overlay`; ask when applicable DFARS or customer
  overlays are unclear; question `How should an unspecified contractual
  overlay be handled?`; options: `Inventory overlays first (Recommended)` —
  Confirm applicable DFARS and customer requirements before adding controls;
  `Use supplied overlay` — Apply the complete supplied DFARS or customer
  overlay; `Standard only` — Use the selected standard without an additive
  contractual overlay.
- `cmmc_stage`; header `Stage`; ask when assessment stage is absent; question
  `How should an unspecified assessment stage be resolved?`; options: `Confirm
  stage first (Recommended)` — Confirm the lifecycle stage before selecting an
  assessment workflow; `Use supplied pre-assessment` — Treat the supplied stage
  as readiness work before formal assessment; `Use supplied formal assessment`
  — Treat the supplied stage as formal-assessment preparation.
- `cmmc_boundary`; header `CUI Scope`; ask when the CUI boundary maturity is
  unknown; question `How should an uncertain CUI boundary be handled?`;
  options: `Map boundary first (Recommended)` — Identify CUI assets, flows, and
  protection dependencies before assessing; `Assess supplied boundary` — Use a
  supplied final boundary and disclose unverified assumptions; `Validate
  supplied draft` — Test a supplied draft and mark unresolved scope.
- `cmmc_assets`; header `Assets`; ask when asset classes in scope are unclear;
  question `How should an unspecified CUI asset scope be resolved?`; options:
  `Inventory assets first (Recommended)` — Identify CUI assets, security
  protection assets, and adjacent dependencies before selecting scope; `Use
  supplied CUI boundary` — Assess the supplied complete set of CUI and security
  protection assets; `Use supplied enterprise scope` — Assess the supplied
  complete environment including systems that affect CUI protection.
- `cmmc_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configurations, logs,
  approvals, reviews, and procedures before grading; `Assess supplied
  artifacts` — Assess only supplied evidence and disclose practice gaps;
  `Build evidence request` — List required evidence without grading
  implementation.
- `cmmc_output`; header `Output`; ask when the deliverable is absent; question
  `Which deliverable is most useful?`; options: `Assessment matrix
  (Recommended)` — Provide mappings, evidence, gaps, and remediation; `SSP
  narrative` — Emphasize implementer-ready SSP language; `POAM actions` —
  Emphasize owners, milestones, and residual risk.

### A.3 `firewall-best-practices-audit`

- `audit_goal`; header `Goal`; ask when audit purpose is absent; question `What
  is the primary reason for this firewall audit?`; options: `Baseline hygiene
  (Recommended)` — Review the complete rulebase against general practices;
  `Pre-change review` — Focus on planned-change risk; `Incident focus` —
  Prioritize a suspected attack path.
- `audit_scope`; header `Components`; ask when audit component coverage is
  unclear; question `How should unspecified audit component coverage be
  resolved?`; options: `Inventory components first (Recommended)` — Inventory
  policy, NAT, objects, zones, routing, and logging before selecting coverage;
  `Use supplied full-component scope` — Audit the complete supplied component
  set; `Use supplied limited-component scope` — Audit only the supplied
  component subset specified through Other.
- `audit_boundary`; header `Boundary`; ask when audit boundary breadth is
  unclear; question `How should an unspecified audit boundary be resolved?`;
  options: `Map boundary first (Recommended)` — Map every device context and
  trust boundary before selecting breadth; `Use supplied all-context boundary`
  — Audit every context in the supplied boundary; `Use supplied named-context
  boundary` — Audit only the supplied named-context subset specified through
  Other.
- `audit_evidence`; header `Evidence`; ask when operational evidence
  availability is unclear; question `How should uncertain operational evidence
  be handled?`; options: `Inventory evidence (Recommended)` — Identify
  available configuration and telemetry coverage before analysis; `Use
  supplied artifacts` — Analyze only supplied artifacts and label runtime
  dependencies; `Approved live collection` — Collect targeted read-only device
  evidence with approval.
- `audit_context`; header `Context`; ask when business criticality and trust
  context are absent; question `How should business and trust context be
  established?`; options: `Provide key context (Recommended)` — Use identified
  assets, trust levels, and required flows; `Infer cautiously` — Label inferred
  boundaries; `Generic severity` — Avoid environment-specific impact claims.
- `audit_depth`; header `Depth`; ask when finding detail is not specified;
  question `How should an unspecified finding-detail tier be resolved?`;
  options: `Confirm detail first (Recommended)` — Confirm the required
  finding-detail tier before producing findings; `Use supplied full detail` —
  Return every in-scope finding with complete supporting detail; `Use supplied
  material-only detail` — Return only material findings with supporting detail.
- `audit_remed`; header `Fix Format`; ask when remediation format is absent;
  question `How should remediation be presented?`; options: `Guidance and CLI
  (Recommended)` — Include candidate syntax and verification; `Guidance only`
  — Explain intent without syntax; `Findings only` — Report risk without fixes.

### A.4 `firewall-config-conversion`

- `convert_source`; header `Source`; ask when the source platform cannot be
  determined confidently; question `How should the source platform be
  determined?`; options: `Auto-detect (Recommended)` — Detect vendor and
  platform from syntax; `Prompt value` — Use the user's exact source platform;
  `Unknown source` — Parse conservatively and report ambiguity.
- `convert_target`; header `Target`; ask when the exact target is absent;
  question `What exact target vendor and platform should receive the
  conversion?`; options: `Specify target (Recommended)` — Supply the exact
  target through Other; `Family only` — Generate conservative family-level
  output; `Undecided` — Produce feasibility analysis only.
- `convert_release`; header `Release`; ask when target model or release affects
  syntax or support and is absent; question `How should missing target model or
  release details be handled?`; options: `Discover first (Recommended)` —
  Identify the exact target model and release before conversion; `Exact details
  supplied` — Apply capabilities for the supplied target; `Infer
  conservatively` — Limit output to family-safe syntax and disclose
  uncertainty.
- `convert_scope`; header `Scope`; ask when conversion components are absent;
  question `What should be converted?`; options: `Full migration
  (Recommended)` — Convert all supported components; `Policy and NAT` — Limit
  work to objects, policy, and NAT; `Named sections` — Convert components named
  through Other.
- `convert_base`; header `Baseline`; ask when existing target state is unknown;
  question `How should uncertain target baseline state be handled?`; options:
  `Inspect target first (Recommended)` — Determine whether target state exists
  before generating configuration; `Use supplied clean target` — Generate for a
  supplied empty target baseline; `Use supplied merge target` — Account for a
  supplied existing target configuration.
- `convert_loss`; header `Fidelity`; ask when unsupported behavior needs a
  disposition; question `How should unsupported source behavior be handled?`;
  options: `Caveat and map (Recommended)` — Use the closest safe behavior and
  document loss; `Manual placeholder` — Emit an engineer-resolved placeholder;
  `Stop on loss` — Stop dependent output after material loss.
- `convert_output`; header `Output`; ask when deliverable format is absent;
  question `What conversion deliverable is required?`; options: `Config and
  report (Recommended)` — Produce candidate configuration and fidelity report;
  `Fidelity report` — Analyze without configuration; `Config only` — Produce
  syntax with compact caveats.

### A.5 `firewall-config-diff`

- `diff_goal`; header `Goal`; ask when comparison intent is absent; question
  `What relationship should the comparison test?`; options: `Planned drift
  (Recommended)` — Treat A as baseline and B as candidate; `HA parity` — Find
  unintended peer differences; `Migration parity` — Compare intent across
  vendors.
- `diff_direction`; header `Direction`; ask when input roles are ambiguous;
  question `How should ambiguous input roles be resolved?`; options: `Establish
  baseline first (Recommended)` — Determine the authoritative baseline and
  comparison direction before classifying changes; `Use supplied A-to-B` —
  Treat supplied A as baseline and B as new; `Compare as peers` — Treat inputs
  as unordered and report symmetric differences.
- `diff_scope`; header `Scope`; ask when compared components are absent;
  question `Which configuration areas should be compared?`; options: `All
  sections (Recommended)` — Compare every supported component; `Policy and NAT`
  — Focus on traffic behavior; `Named sections` — Restrict comparison through
  Other.
- `diff_identity`; header `Identity`; ask when rename matching policy affects
  results; question `How should renamed elements be matched?`; options:
  `Semantic matching (Recommended)` — Match resolved meaning before names;
  `Stable names` — Use names as primary identity; `Strict values` — Report every
  name or value difference.
- `diff_ignore`; header `Exceptions`; ask when difference allowlist is absent;
  question `How should an unspecified difference allowlist be handled?`;
  options: `Stop pending allowlist (Recommended)` — Stop filtering decisions
  until intentional and generated exceptions are confirmed; `Use supplied
  complete allowlist` — Exclude every intentional or generated exception in
  the supplied complete allowlist; `Use no exclusions` — Report all material
  differences without an allowlist.
- `diff_output`; header `Output`; ask when result detail is absent; question
  `How should an unspecified result-detail tier be resolved?`; options:
  `Confirm detail first (Recommended)` — Confirm the result-detail tier before
  producing the comparison; `Use supplied full report` — Return the complete
  comparison with all supported difference detail; `Use supplied material
  summary` — Return only material differences and their risk.
- `diff_format`; header `Format`; ask when result format is absent; question
  `How should an unspecified result format be resolved?`; options: `Confirm
  format first (Recommended)` — Confirm the required result format before
  rendering the comparison; `Use supplied human-readable` — Render the result
  in the supplied human-readable format; `Use supplied machine-readable` —
  Render the result in the supplied machine-readable format.

### A.6 `hipaa-ngfw-compliance`

- `hipaa_role`; header `Org Role`; ask when HIPAA organizational role is
  absent; question `How should an unspecified HIPAA responsibility be
  handled?`; options: `Confirm responsibility (Recommended)` — Establish the
  organization's HIPAA responsibility before assigning safeguards; `Use
  supplied single-role scope` — Use one exact supplied covered-entity or
  business-associate role from Other; `Use supplied combined scope` — Assess the
  supplied combined covered-entity and business-associate scope.
- `hipaa_goal`; header `Goal`; ask when review purpose is absent; question `What
  is the purpose of this HIPAA review?`; options: `Risk assessment
  (Recommended)` — Identify ePHI risks and remediation; `Audit evidence` —
  Organize audit artifacts; `Design review` — Review architecture without
  operational claims.
- `hipaa_scope`; header `ePHI Scope`; ask when the ePHI boundary is unclear;
  question `How should an uncertain ePHI boundary be handled?`; options: `Map
  ePHI scope (Recommended)` — Identify systems, flows, users, and parties before
  assessing; `Assess supplied boundary` — Use a supplied final boundary and
  disclose unverified assumptions; `Validate supplied draft` — Test a supplied
  preliminary boundary and mark unresolved scope.
- `hipaa_vendor`; header `Vendors`; ask when third-party ePHI path scope is
  unclear; question `How should unresolved third-party ePHI path scope be
  handled?`; options: `Inventory paths first (Recommended)` — Identify vendor,
  remote-access, cloud, and transmission paths before selecting scope; `Use
  supplied all paths` — Assess the supplied complete set of third-party ePHI
  paths; `Use supplied named paths` — Limit assessment to the supplied named
  third-party paths.
- `hipaa_evidence`; header `Evidence`; ask when evidence period is unclear;
  question `How should an uncertain evidence period be handled?`; options:
  `Inventory evidence (Recommended)` — Identify dated records and current
  configuration before making period claims; `Assess current state` — Limit
  conclusions to present technical state; `Build evidence request` — List
  required dated evidence without grading effectiveness.
- `hipaa_output`; header `Output`; ask when report emphasis is absent; question
  `What should the report emphasize?`; options: `Safeguard matrix
  (Recommended)` — Map evidence, gaps, risk, and remediation; `Risk register` —
  Emphasize likelihood, impact, owners, and treatment; `Executive brief` —
  Summarize exposure and top actions.

### A.7 `iso27001-ngfw-compliance`

- `iso_goal`; header `Audit Goal`; ask when engagement type is absent; question
  `What kind of ISO 27001 activity is this?`; options: `Internal readiness
  (Recommended)` — Identify evidence and operation gaps; `Certification audit`
  — Prepare certification or surveillance evidence; `Corrective action` —
  Focus on known findings.
- `iso_scope`; header `ISMS Scope`; ask when the ISMS boundary is unclear;
  question `How should an uncertain ISMS boundary be handled?`; options: `Map
  ISMS scope (Recommended)` — Identify organizational and system boundaries
  before assessing; `Assess supplied boundary` — Use a supplied final boundary
  and disclose unverified assumptions; `Validate supplied draft` — Test a
  supplied draft and mark unresolved scope.
- `iso_soa`; header `SoA`; ask when Statement of Applicability evidence is
  absent; question `How should absent Statement of Applicability evidence be
  handled?`; options: `Inventory SoA first (Recommended)` — Determine whether
  current, draft, or supporting applicability records exist; `Use supplied SoA`
  — Apply the supplied organizational decisions and disclose evidence gaps;
  `Use generic mapping` — Map Annex A without organizational applicability
  claims.
- `iso_basis`; header `Basis`; ask when control applicability basis is unclear;
  question `How should an uncertain control-applicability basis be handled?`;
  options: `Confirm basis first (Recommended)` — Establish the governing SoA,
  risk treatment plan, or overlay before conclusions; `Use supplied SoA basis`
  — Follow the supplied organizational applicability decisions; `Use Annex A
  baseline` — Map Annex A without organizational applicability claims.
- `iso_period`; header `Evidence`; ask when operating evidence period is
  unclear; question `How should an uncertain operating-evidence period be
  handled?`; options: `Confirm period first (Recommended)` — Establish the
  assessment period and available dated samples before effectiveness claims;
  `Assess current state` — Limit conclusions to present technical state;
  `Assess control design` — Evaluate intended design without operating
  effectiveness claims.
- `iso_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable is needed?`; options: `Control matrix (Recommended)` — Provide
  mapping, evidence, gaps, and actions; `Audit evidence` — Emphasize traceable
  artifacts; `Risk treatment` — Emphasize treatment and residual risk.

### A.8 `parsing-cisco-configs`

- `cisco_goal`; header `Parse Depth`; ask when required parsing depth is absent;
  question `How should unspecified parsing depth be resolved?`; options:
  `Confirm depth first (Recommended)` — Confirm whether full normalization or
  focused extraction is required; `Use full normalization` — Populate the
  complete shared schema and run all quality gates; `Use focused extraction` —
  Extract only the sections required for the supplied investigation.
- `cisco_platform`; header `Platform`; ask when ASA versus FTD remains
  ambiguous after artifact inspection; question `How should an ambiguous Cisco
  platform be resolved?`; options: `Confirm platform first (Recommended)` —
  Confirm ASA versus FTD before applying platform-specific parsing assumptions;
  `Use supplied Cisco ASA` — Apply Cisco ASA parsing behavior from the supplied
  platform identity; `Use supplied Cisco FTD` — Apply Cisco FTD parsing
  behavior from the supplied platform identity.
- `cisco_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How should uncertain Cisco export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected sections and
  truncation before making completeness claims; `Full artifact supplied` —
  Treat the supplied running configuration as complete; `Partial artifact
  supplied` — Mark omitted sections unknown.
- `cisco_scope`; header `Scope`; ask when requested normalized components are
  absent; question `Which components should be normalized?`; options: `All
  sections (Recommended)` — Include all supported components; `Policy and NAT`
  — Focus on traffic selection; `Named sections` — Restrict parsing through
  Other.
- `cisco_output`; header `Output`; ask when output form is absent; question
  `What output should be returned?`; options: `JSON and gates (Recommended)` —
  Return normalized JSON and quality gates; `Normalized JSON` — Return the
  schema only; `Quality report` — Return coverage and ambiguity only.

### A.9 `parsing-fortinet-configs`

- `forti_goal`; header `Parse Depth`; ask when required parsing depth is absent;
  question `How should unspecified parsing depth be resolved?`; options:
  `Confirm depth first (Recommended)` — Confirm whether full normalization or
  focused extraction is required; `Use full normalization` — Populate the
  complete shared schema and run all quality gates; `Use focused extraction` —
  Extract only the sections required for the supplied investigation.
- `forti_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How should uncertain FortiGate export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected tables, defaults, and
  truncation before making completeness claims; `Full artifact supplied` —
  Treat the supplied FortiGate backup as complete; `Partial artifact supplied`
  — Mark omitted tables and defaults unknown.
- `forti_vdom`; header `VDOM Scope`; ask when included VDOMs are unclear;
  question `Which VDOM scope should be included?`; options: `All detected
  (Recommended)` — Parse global state and every VDOM; `Named VDOMs` — Limit
  parsing through Other; `Global only` — Exclude VDOM policy.
- `forti_scope`; header `Sections`; ask when included configuration tables are
  absent; question `Which configuration areas should be normalized?`; options:
  `All sections (Recommended)` — Include all supported components; `Policy and
  NAT` — Focus on policy and translation; `Named sections` — Restrict parsing
  through Other.
- `forti_output`; header `Output`; ask when output form is absent; question
  `What output should be returned?`; options: `JSON and gates (Recommended)` —
  Return normalized JSON and quality results; `Normalized JSON` — Return the
  schema only; `Quality report` — Emphasize unresolved references and defaults.

### A.10 `parsing-palo-configs`

- `palo_goal`; header `Parse Depth`; ask when required parsing depth is absent;
  question `How should unspecified parsing depth be resolved?`; options:
  `Confirm depth first (Recommended)` — Confirm whether full normalization or
  focused extraction is required; `Use full normalization` — Populate the
  complete shared schema and run all quality gates; `Use focused extraction` —
  Extract only the sections required for the supplied investigation.
- `palo_format`; header `Format`; ask when XML versus set format remains
  ambiguous after artifact inspection; question `How should an ambiguous
  PAN-OS format be resolved?`; options: `Confirm format first (Recommended)` —
  Confirm XML versus set format before selecting a parser; `Use supplied
  PAN-OS XML` — Parse the supplied PAN-OS XML hierarchy; `Use supplied set
  format` — Parse the supplied PAN-OS set statements.
- `palo_scope`; header `Context`; ask when PAN-OS configuration-context
  selection is unclear; question `How should an unspecified PAN-OS context
  scope be resolved?`; options: `Confirm context first (Recommended)` — Confirm
  the complete configuration-context selection before parsing; `Use supplied
  all-context scope` — Parse every configuration context in the supplied
  artifact; `Use supplied named-context scope` — Parse only the supplied named
  contexts specified through Other.
- `palo_inheritance`; header `Inheritance`; ask when inheritance treatment is
  unclear; question `How should unspecified PAN-OS inheritance treatment be
  resolved?`; options: `Confirm inheritance first (Recommended)` — Confirm
  inheritance treatment before making effective-configuration claims; `Use
  supplied effective resolution` — Resolve the supplied shared, device-group,
  template, and local inheritance; `Use supplied local-only treatment` — Treat
  only supplied local values and avoid inherited-state claims.
- `palo_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How should uncertain PAN-OS export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected hierarchy and
  references before making completeness claims; `Full artifact supplied` —
  Treat the supplied PAN-OS configuration as complete; `Partial artifact
  supplied` — Mark omitted hierarchy and references unknown.
- `palo_output`; header `Output`; ask when output form is absent; question `What
  output should be returned?`; options: `JSON and gates (Recommended)` — Return
  normalized JSON and quality results; `Normalized JSON` — Return the schema
  only; `Quality report` — Emphasize inheritance and reference ambiguity.

### A.11 `parsing-srx-configs`

- `srxp_goal`; header `Parse Depth`; ask when required parsing depth is absent;
  question `How should unspecified parsing depth be resolved?`; options:
  `Confirm depth first (Recommended)` — Confirm whether full normalization or
  focused extraction is required; `Use full normalization` — Populate the
  complete shared schema and run all quality gates; `Use focused extraction` —
  Extract only the sections required for the supplied investigation.
- `srxp_format`; header `Format`; ask when display-set versus hierarchical
  syntax remains ambiguous after artifact inspection; question `How should an
  ambiguous Junos format be resolved?`; options: `Confirm format first
  (Recommended)` — Confirm display-set versus hierarchical syntax before
  selecting a parser; `Use supplied display set` — Parse the supplied
  line-oriented display-set commands; `Use supplied hierarchical` — Parse the
  supplied brace-delimited hierarchical configuration.
- `srxp_scope`; header `Context`; ask when logical-system scope is unclear;
  question `Which Junos contexts should be included?`; options: `All detected
  (Recommended)` — Parse main and detected logical contexts; `Named context` —
  Limit parsing through Other; `Main only` — Ignore logical systems.
- `srxp_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How should uncertain Junos export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected groups, inheritance,
  and sections before making completeness claims; `Full artifact supplied` —
  Treat the supplied Junos configuration as complete; `Partial artifact
  supplied` — Mark missing groups, inheritance, and policy unknown.
- `srxp_output`; header `Output`; ask when output form is absent; question `What
  output should be returned?`; options: `JSON and gates (Recommended)` — Return
  normalized JSON and quality results; `Normalized JSON` — Return the schema
  only; `Quality report` — Emphasize groups, references, and unsupported syntax.

### A.12 `pci-ngfw-compliance`

- `pci_version`; header `PCI Version`; ask when the governing PCI version is
  absent; question `How should an unspecified PCI DSS version be resolved?`;
  options: `Confirm version first (Recommended)` — Confirm the governing PCI
  DSS version before mapping requirements; `Use supplied PCI DSS 4.0.1` —
  Assess against the supplied PCI DSS 4.0.1 requirements; `Use supplied other
  version` — Assess against the other version supplied through Other.
- `pci_overlay`; header `Overlay`; ask when applicable QSA or customer overlays
  are unclear; question `How should an unspecified assessment overlay be
  handled?`; options: `Inventory overlays first (Recommended)` — Confirm
  applicable QSA and customer requirements before adding interpretations; `Use
  supplied overlay` — Apply the complete supplied QSA or customer overlay;
  `Standard only` — Use the selected PCI DSS version without an additive
  assessment overlay.
- `pci_stage`; header `Assess Type`; ask when assessment type is absent;
  question `What kind of PCI assessment is this?`; options: `Readiness review
  (Recommended)` — Identify gaps before formal assessment; `ROC support` —
  Organize QSA evidence; `SAQ support` — Tailor evidence to self-assessment.
- `pci_scope`; header `CDE Scope`; ask when the CDE boundary is unclear;
  question `How should an uncertain CDE boundary be handled?`; options: `Map
  CDE scope (Recommended)` — Identify account-data systems, connected systems,
  and flows before assessing; `Assess supplied boundary` — Use a supplied final
  boundary and disclose unverified assumptions; `Validate supplied draft` —
  Test a supplied preliminary boundary and mark unresolved scope.
- `pci_segment`; header `Segmentation`; ask when segmentation reliance is
  unclear; question `How should uncertain segmentation reliance be handled?`;
  options: `Verify segmentation (Recommended)` — Test segmentation design and
  evidence before reducing scope; `No scope reduction` — Treat connected
  networks as in scope without relying on segmentation; `Use verified
  segmentation` — Apply a supplied validated segmentation boundary.
- `pci_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configuration, reviews, logs,
  scans, and records before grading; `Assess supplied artifacts` — Assess only
  supplied evidence and disclose procedural gaps; `Build evidence request` —
  List required artifacts and samples without grading implementation.
- `pci_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable is needed?`; options: `Requirement matrix (Recommended)` — Map
  evidence, gaps, and remediation; `Segmentation report` — Emphasize CDE
  isolation; `Executive brief` — Emphasize scope risk and top actions.

### A.13 `sd-onprem-proxmox-deploy`

- `sd_stage`; header `Stage`; ask when deployment stage is absent; question
  `How should an unspecified deployment stage be resolved?`; options: `Inspect
  stage first (Recommended)` — Inspect deployment evidence to distinguish
  planning, fresh deployment, and troubleshooting before choosing a workflow;
  `Plan supplied fresh deployment` — Plan from a supplied fresh-deployment stage
  without executing changes; `Troubleshoot supplied deployment` — Diagnose a
  supplied existing deployment without assuming a fresh state.
- `sd_release`; header `Release`; ask when exact SD On-Prem release is absent;
  question `How should missing Security Director release details be handled?`;
  options: `Discover first (Recommended)` — Identify the exact release and
  matching guide before deployment planning; `Exact details supplied` — Use the
  exact supplied release and matching guide; `Stop pending details` — Do not
  produce release-dependent deployment steps.
- `sd_media`; header `Artifacts`; ask when media presence or integrity is
  unclear; question `How should uncertain release media integrity be handled?`;
  options: `Verify media first (Recommended)` — Check image and bundle presence,
  versions, and checksums before deployment; `Use supplied verified media` —
  Proceed with supplied artifacts and checksum evidence; `Stop pending media`
  — Block deployment until required artifacts are supplied.
- `sd_size`; header `Sizing`; ask when appliance flavor is absent; question
  `How should unresolved appliance sizing be handled?`; options: `Measure
  requirements first (Recommended)` — Measure device, traffic, log, retention,
  and growth requirements before selecting a flavor; `Use supplied final
  flavor` — Use the supplied final supported flavor without reselecting its
  size.
- `sd_proxmox`; header `Proxmox`; ask when VM placement values are incomplete;
  question `How should incomplete Proxmox VM state be resolved?`; options:
  `Inspect state first (Recommended)` — Inspect Proxmox and VM evidence
  read-only before choosing a new-VM or existing-VM workflow; `Plan supplied new
  VM` — Plan with supplied VMID, node, storage, bridge, and resource values for
  a new VM; `Assess supplied existing VM` — Assess a supplied existing VM
  against deployment requirements.
- `sd_network`; header `Network`; ask when IP, route, or internal CIDR values are
  incomplete; question `How should incomplete IP and routing values be
  handled?`; options: `Map network first (Recommended)` — Identify required
  addresses, gateway, routes, and internal CIDR before deployment; `Use supplied
  network plan` — Apply the complete supplied addressing and routing plan;
  `Stop pending values` — Block deployment and list missing network values.
- `sd_services`; header `DNS and NTP`; ask when supporting service reachability
  is unverified; question `How should unverified supporting-service reachability
  be handled?`; options: `Verify services first (Recommended)` — Run safe DNS
  and NTP reachability checks before deployment; `Use supplied test results` —
  Rely on supplied current DNS and NTP validation evidence; `Stop pending
  readiness` — Treat unverified service reachability as a blocker.
- `sd_transfer`; header `Transfer`; ask when bundle transfer method is absent;
  question `How should an unspecified bundle transfer method be resolved?`;
  options: `Confirm method first (Recommended)` — Confirm the approved transfer
  method before moving the bundle; `Use supplied HTTPS` — Transfer the bundle
  with the supplied approved HTTPS method and checksums; `Use supplied SCP` —
  Transfer the bundle with the supplied approved SCP method without exposing
  credentials.
- `sd_secrets`; header `Secrets`; ask when secret delivery is needed for a later
  step; question `How will deployment secrets be supplied?`; options:
  `Interactive entry (Recommended)` — Enter secrets at a trusted console;
  `Secret manager` — Use an approved delivery workflow; `Supply later` — Use
  placeholders and stop before secret-dependent execution.
- `sd_onboard`; header `Onboarding`; ask when post-deployment scope is absent;
  question `How far should the runbook go after deployment?`; options: `Health
  validation (Recommended)` — Validate the platform without production
  onboarding; `Device onboarding` — Include approved device connectivity;
  `Full operations` — Include logging, licensing, backup, and monitoring.

### A.14 `soc2-ngfw-compliance`

- `soc2_type`; header `Report Type`; ask when engagement type is absent;
  question `What SOC 2 engagement is being supported?`; options: `Readiness
  review (Recommended)` — Identify gaps before examination; `Type I` — Assess a
  point in time; `Type II` — Assess operation over a period.
- `soc2_tsc`; header `TSC Scope`; ask when Trust Services categories are absent;
  question `How should unspecified Trust Services categories be resolved?`;
  options: `Confirm categories first (Recommended)` — Confirm every applicable
  Trust Services category before mapping criteria; `Use supplied security-only
  scope` — Assess only the supplied Security category scope; `Use supplied
  expanded scope` — Assess Security plus the exact supplied additional
  categories specified through Other.
- `soc2_period`; header `Period`; ask when evidence period is absent; question
  `How should an unspecified SOC 2 evidence period be handled?`; options:
  `Confirm period first (Recommended)` — Establish dates and available samples
  before operating-period conclusions; `Assess point in time` — Limit
  conclusions to current control design and state; `Build evidence plan` —
  Identify retention and sampling needs without grading operation.
- `soc2_system`; header `System Docs`; ask when system description or control
  matrix availability is unclear; question `How should incomplete
  system-boundary evidence be handled?`; options: `Map system first
  (Recommended)` — Identify services, infrastructure, people, data, and control
  ownership before grading; `Use supplied documents` — Assess the supplied
  system description and control matrix while disclosing gaps; `Build discovery
  request` — List missing boundary and ownership evidence without grading.
- `soc2_vendor`; header `Providers`; ask when subservice organization treatment
  is unclear; question `How should uncertain subservice-organization treatment
  be handled?`; options: `Inventory vendors first (Recommended)` — Identify
  subservice organizations and per-vendor governance decisions before
  assessment; `Use supplied uniform treatment` — Apply one supplied carve-out or
  inclusive method consistently across all vendors; `Use supplied mixed
  treatment` — Apply supplied per-vendor carve-out and inclusive treatments and
  document each boundary.
- `soc2_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable should be emphasized?`; options: `Control matrix (Recommended)` —
  Provide criteria mapping, evidence, gaps, and remediation; `Evidence request`
  — Emphasize period artifacts and samples; `Management brief` — Summarize
  exceptions and top actions.

### A.15 `srx-advpn`

- `advpn_task`; header `Task`; ask when the requested activity is absent;
  question `What should this ADVPN run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a read-only architecture and candidate
  configuration; `Troubleshoot` — Diagnose shortcut or forwarding problems;
  `Migration` — Plan transition from static or hub-only IPsec.
- `advpn_release`; header `Platform`; ask when model or release is absent and
  affects support; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before support conclusions; `Exact details
  supplied` — Apply model- and release-specific limits; `Infer conservatively`
  — Limit output to evidence-supported design and disclose uncertainty.
- `advpn_topo`; header `Topology`; ask when site, addressing, NAT, or HA
  topology is incomplete; question `How should incomplete ADVPN topology be
  handled?`; options: `Map topology first (Recommended)` — Identify sites,
  addresses, LANs, NAT, and HA roles before design; `Use supplied complete map`
  — Design from a supplied complete topology; `Design from requirements` —
  Build a new topology from supplied site and traffic requirements.
- `advpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `How should unspecified peer authentication be handled?`; options: `Inventory
  authentication (Recommended)` — Identify existing PKI, enrollment, and peer
  identity constraints before design; `Use supplied PKI` — Use the supplied
  certificate authority and enrollment design; `Assess supplied PSK` — Analyze
  the supplied PSK design and report ADVPN limitations.
- `advpn_route`; header `Routing`; ask when overlay routing is absent; question
  `How should an unspecified ADVPN routing model be resolved?`; options:
  `Confirm model first (Recommended)` — Confirm the routing model before
  designing the overlay; `Use supplied OSPF P2MP` — Use the supplied OSPF
  point-to-multipoint routing model; `Use supplied other model` — Use the
  complete alternative routing model specified through Other.
- `advpn_traffic`; header `Traffic`; ask when branch path requirements are
  unclear; question `What branch traffic behavior is required?`; options:
  `Shortcuts plus hub (Recommended)` — Support hub paths and spoke shortcuts;
  `Shortcuts only` — Focus on spoke-to-spoke formation; `Central backhaul` —
  Re-evaluate AutoVPN fit.
- `advpn_gateway`; header `Gateway`; ask when release-specific gateway support is
  unresolved; question `How should unresolved ADVPN gateway support be
  handled?`; options: `Verify support first (Recommended)` — Verify model and
  release support before selecting a gateway form; `Use supplied supported
  static` — Use the supplied static form after support is established; `Use
  supplied supported dynamic` — Use the supplied dynamic form after support is
  established.
- `advpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, and flow evidence before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.16 `srx-autovpn-full-tunnel`

- `autovpn_task`; header `Task`; ask when requested activity is absent; question
  `What should this AutoVPN run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a full-tunnel design; `Troubleshoot` —
  Diagnose tunnel, routing, or backhaul problems; `Migration` — Plan transition
  from static or split-tunnel VPN.
- `autovpn_release`; header `Platform`; ask when model or release is absent and
  affects support; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before support conclusions; `Exact details
  supplied` — Apply release-specific behavior; `Infer conservatively` — Limit
  output to evidence-supported design and disclose uncertainty.
- `autovpn_traffic`; header `Traffic`; ask when backhaul behavior is unclear;
  question `How should an unspecified AutoVPN traffic model be resolved?`;
  options: `Confirm model first (Recommended)` — Confirm the traffic model
  before designing spoke forwarding; `Use supplied full backhaul` — Backhaul
  all scoped spoke traffic through the hub as supplied; `Use supplied split
  tunnel` — Preserve the supplied split-tunnel and local path requirements.
- `autovpn_auth`; header `Auth`; ask when peer authentication is absent;
  question `What peer authentication model should be used?`; options: `PKI
  zero-touch (Recommended)` — Use certificates and scalable group identity;
  `Unique PSKs` — Use a distinct secret per spoke; `Existing legacy` — Assess a
  shared-secret design and document risk.
- `autovpn_lans`; header `LAN Prefixes`; ask when spoke prefix allocation is
  incomplete; question `How should incomplete spoke LAN allocation be
  handled?`; options: `Map LANs first (Recommended)` — Identify every spoke
  prefix and overlap before route design; `Use supplied scalable ranges` — Use
  supplied non-overlapping summarizable prefixes; `Use supplied explicit
  prefixes` — Handle supplied discontiguous prefixes without summarization.
- `autovpn_nat`; header `Underlay`; ask when NAT between spokes and hub is
  unclear; question `How should uncertain underlay NAT be handled?`; options:
  `Trace NAT first (Recommended)` — Test peer reachability and translation
  behavior before tunnel design; `Use supplied NAT path` — Apply NAT-T to the
  supplied documented translation path; `Use supplied no-NAT path` — Use
  supplied directly reachable peer paths.
- `autovpn_route`; header `Routing`; ask when management and default-route
  separation is unclear; question `How should uncertain management-route
  separation be handled?`; options: `Inspect routes first (Recommended)` —
  Trace management, peer, and default paths before route changes; `Use supplied
  separate path` — Preserve a supplied independent management path; `Analyze
  competing defaults` — Evaluate supplied competing defaults for recursion.
- `autovpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, sessions, and logs before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.17 `srx-dynamic-ip-feed`

- `dif_task`; header `Task`; ask when requested activity is absent; question
  `What should this dynamic-feed run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a safe integration; `Troubleshoot` —
  Diagnose download, parsing, mapping, or policy behavior; `Migration` —
  Convert an existing feed workflow.
- `dif_release`; header `Platform`; ask when model or release is absent and
  affects capability; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify the
  exact model and release before capability conclusions; `Exact details
  supplied` — Apply release-specific capabilities; `Infer conservatively` —
  Limit output to evidence-supported design and disclose uncertainty.
- `dif_source`; header `Feed Source`; ask when feed artifacts or publishing
  design is incomplete; question `How should an incomplete feed source be
  handled?`; options: `Inspect source first (Recommended)` — Determine whether
  an existing endpoint, archive, or publishing workflow can be used; `Use
  supplied endpoint` — Integrate the supplied endpoint and archive layout;
  `Design new endpoint` — Define a new supported HTTPS feed and publishing
  workflow.
- `dif_tls`; header `CA Source`; ask when publisher CA source or trust anchor is
  absent; question `How should an unspecified publisher CA source be
  resolved?`; options: `Verify chain first (Recommended)` — Verify the
  publisher chain and required trust anchor before configuration; `Use supplied
  public CA` — Validate the publisher with the supplied public CA chain; `Use
  supplied private CA` — Import the supplied private CA as a controlled trust
  anchor before validation.
- `dif_auth`; header `Feed Auth`; ask when feed authentication method is absent
  or unclear; question `How should uncertain feed authentication be handled?`;
  options: `Verify endpoint first (Recommended)` — Verify endpoint requirements
  before selecting authentication and risk-classify explicit no-extra-auth
  requests supplied through Other; `Use supplied single auth` — Use one exact
  supplied mTLS or Basic mechanism specified via Other while keeping
  credentials outside chat; `Use supplied combined auth` — Use supplied mTLS
  plus Basic authentication when both are required while keeping credentials
  outside chat.
- `dif_route`; header `Routing`; ask when feed-server routing context is absent;
  question `How should an unknown feed-server route be handled?`; options:
  `Trace route first (Recommended)` — Collect route, DNS, source, and connection
  evidence before selecting context; `Use supplied default instance` — Use the
  supplied default-instance path after reachability validation; `Use supplied
  named instance` — Use the supplied routing instance and source address.
- `dif_effect`; header `Policy Use`; ask when feed enforcement intent is absent;
  question `How will feed entries affect security policy?`; options: `Blocklist
  deny (Recommended)` — Deny new matching sessions with logging; `Allowlist
  permit` — Permit members within constrained policy; `Both uses` — Define
  separate objects and precedence.
- `dif_session`; header `Sessions`; ask when existing-session behavior matters
  and is absent; question `How should unspecified existing-session behavior be
  resolved?`; options: `Confirm behavior first (Recommended)` — Confirm
  existing-session behavior before accounting for enforcement timing; `Use
  supplied new-sessions-only` — Apply feed changes only to new session
  evaluations; `Use supplied targeted clear` — Record targeted-clear intent and
  require separate live approval before clearing.
- `dif_poll`; header `Polling`; ask when refresh requirements are absent;
  question `How should an unspecified polling cadence be resolved?`; options:
  `Confirm cadence first (Recommended)` — Confirm the polling cadence before
  selecting an interval; `Use supplied standard interval` — Use the supplied
  conservative supported standard interval; `Use supplied custom interval` —
  Use the supplied custom interval after validating load and reliability.

### A.18 `srx-ipsec-hub-spoke`

- `hsvpn_task`; header `Task`; ask when requested activity is absent; question
  `What should this hub-and-spoke run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a static route-based design; `Troubleshoot`
  — Diagnose IKE, IPsec, routing, or policy; `Migration` — Plan transition from
  policy-based or shared-tunnel VPN.
- `hsvpn_release`; header `Platform`; ask when model or release is absent and
  affects syntax; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before syntax conclusions; `Exact details supplied`
  — Apply platform-specific syntax; `Infer conservatively` — Limit output to
  evidence-supported design and disclose uncertainty.
- `hsvpn_topo`; header `Topology`; ask when peer, prefix, NAT, HA, or st0 data
  is incomplete; question `How should incomplete hub-and-spoke topology be
  handled?`; options: `Map topology first (Recommended)` — Identify peers,
  LANs, WANs, NAT, HA, and st0 allocation before design; `Use supplied complete
  map` — Design from a supplied complete topology; `Design from requirements` —
  Build a new topology from supplied site and traffic requirements.
- `hsvpn_traffic`; header `Traffic`; ask when spoke path requirements are
  unclear; question `How should an unspecified hub-spoke traffic model be
  resolved?`; options: `Confirm model first (Recommended)` — Confirm the
  traffic model before designing spoke forwarding; `Use supplied central
  backhaul` — Backhaul all scoped spoke traffic through the hub as supplied;
  `Use supplied split tunnel` — Preserve the supplied split-tunnel paths and
  specify local variants through Other.
- `hsvpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `What peer authentication should be used?`; options: `Certificates
  (Recommended)` — Use PKI where available; `Unique PSKs` — Use distinct
  secrets via approved delivery; `Shared lab PSK` — Classify as lab-only.
- `hsvpn_route`; header `Routing`; ask when management reachability and tunnel
  defaults may conflict; question `How should uncertain management-route
  protection be handled?`; options: `Inspect routes first (Recommended)` —
  Trace management, peer, and tunnel-default paths before route changes; `Use
  supplied separate path` — Preserve a supplied independent management path;
  `Analyze competing defaults` — Evaluate supplied competing defaults for
  recursion.
- `hsvpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, sessions, and logs before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.19 `srx-mnha`

- `mnha_task`; header `Task`; ask when requested activity is absent; question
  `What should this MNHA run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess an architecture; `Troubleshoot` — Diagnose
  synchronization, forwarding, or failover; `Migration` — Plan migration from
  chassis cluster or standalone SRX.
- `mnha_release`; header `Platform`; ask when node models or releases are absent;
  question `How should missing node model or Junos release details be handled?`;
  options: `Discover first (Recommended)` — Identify every node model and
  release before support conclusions; `Exact details supplied` — Apply
  release-specific syntax; `Stop pending details` — Avoid implementation-ready
  configuration until exact details are supplied.
- `mnha_mode`; header `MNHA Mode`; ask when forwarding mode is absent; question
  `Which MNHA forwarding model is required?`; options: `Routed mode
  (Recommended)` — Use explicit routing and SRGs; `Gateway mode` — Provide
  default-gateway service behavior; `Hybrid mode` — Combine only for documented
  requirements.
- `mnha_migrate`; header `Migration`; ask when starting state is unclear;
  question `How should an uncertain MNHA starting state be handled?`; options:
  `Inspect starting state (Recommended)` — Inventory the current HA design
  before choosing a workflow; `Design supplied greenfield` — Design from a
  supplied new-deployment baseline; `Plan supplied migration` — Plan migration
  or repair from supplied current-state evidence.
- `mnha_topo`; header `Topology`; ask when inter-node topology is incomplete;
  question `How should incomplete inter-node topology be handled?`; options:
  `Map topology first (Recommended)` — Identify node links, interfaces, and data
  paths before design; `Use supplied symmetric map` — Design from supplied
  matched interfaces and direct links; `Assess supplied asymmetric map` —
  Include supplied inter-cluster data paths and asymmetry.
- `mnha_service`; header `Services`; ask when stateful service scope is absent;
  question `How should unspecified failover-service scope be resolved?`;
  options: `Inventory services first (Recommended)` — Identify every required
  failover service before selecting a bundle; `Use supplied core-only bundle` —
  Use the supplied firewall and NAT failover scope without IPsec or advanced
  services; `Use supplied core-plus-IPsec` — Use firewall and NAT plus the
  complete supplied IPsec failover scope and specify advanced combinations
  through Other.
- `mnha_route`; header `Routing`; ask when a complete upstream failover
  signaling design is absent; question `How should unresolved MNHA signaling
  design be handled?`; options: `Design from topology first (Recommended)` —
  Derive a complete signaling design from topology and convergence
  requirements; `Use supplied complete design` — Use the supplied complete
  signaling, tracking, ownership, and convergence design.
- `mnha_objective`; header `Objectives`; ask when resilience priority is
  absent; question `How should an unspecified resilience objective be
  resolved?`; options: `Confirm objective first (Recommended)` — Confirm the
  primary resilience objective before design; `Use supplied continuity
  priority` — Prioritize session and state continuity as supplied; `Use
  supplied convergence priority` — Prioritize routing convergence as supplied.
- `mnha_test`; header `Test Plan`; ask when validation depth is absent; question
  `What validation depth is required?`; options: `Full failure matrix
  (Recommended)` — Test node, link, service, routing, and recovery; `Named
  failures` — Test specified cases; `One failure` — Reproduce the reported case
  safely.

### A.20 `srx-mpls-in-flow`

- `mpls_task`; header `Task`; ask when requested activity is absent; question
  `What should this MPLS-in-flow run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a secure MPLS design; `Troubleshoot` —
  Diagnose label, VRF, routing, or policy failures; `Migration` — Plan
  conversion to flow mode.
- `mpls_release`; header `Platform`; ask when model or release is absent;
  question `How should missing SRX model or Junos release details be handled?`;
  options: `Discover first (Recommended)` — Identify the exact model and release
  before MPLS flow-mode support conclusions; `Exact details supplied` — Verify
  the supplied platform against minimum support; `Stop pending details` — Treat
  unknown platform support as a blocker.
- `mpls_role`; header `Device Role`; ask when PE, CPE, or transit role is
  unclear; question `How should an uncertain SRX MPLS role be handled?`;
  options: `Confirm role first (Recommended)` — Establish PE, CPE, transit, or
  mixed responsibilities before design; `Use supplied edge role` — Apply
  security for a supplied PE or CPE role; `Assess supplied transit role` —
  Re-evaluate the requested security function for a supplied transit role.
- `mpls_family`; header `IP Family`; ask when required address families are
  absent; question `Which address families are required?`; options: `IPv4 and
  VPNv4 (Recommended)` — Design the common IPv4 L3VPN case; `Dual stack` —
  Include IPv6 and VPNv6; `IPv6 focused` — Limit design to IPv6.
- `mpls_signal`; header `Signaling`; ask when label signaling is absent;
  question `How should unspecified label signaling be handled?`; options:
  `Inspect signaling first (Recommended)` — Identify transport and label
  protocols before MPLS design; `Preserve supplied signaling` — Preserve the
  supplied LDP, RSVP, or BGP label design; `Design new LDP transport` — Build a
  new supported LDP transport from supplied requirements.
- `mpls_vrf`; header `VRF Scope`; ask when VRF or route-target inventory is
  incomplete; question `How should an incomplete VRF inventory be handled?`;
  options: `Inventory VRFs first (Recommended)` — Identify VRFs, RDs, RTs,
  interfaces, and prefixes before policy design; `Use supplied complete matrix`
  — Apply a supplied complete VRF and route-target inventory; `Design new
  service matrix` — Build a new matrix from supplied service requirements.
- `mpls_policy`; header `Policy Model`; ask when VRF-aware policy model is
  absent; question `How should an unspecified VRF policy architecture be
  resolved?`; options: `Confirm architecture first (Recommended)` — Confirm the
  VRF policy architecture before organizing policy; `Use supplied policy
  groups` — Use the supplied VRF policy-group architecture; `Use supplied
  VRF-to-zone` — Use the supplied VRF-to-zone architecture.
- `mpls_service`; header `Services`; ask when inspection services are absent;
  question `How should unspecified security-service scope be handled?`;
  options: `Confirm services first (Recommended)` — Inventory application, NAT,
  inspection, license, and capacity requirements before selecting a bundle;
  `Use supplied base-only bundle` — Apply supplied stateful policy and logging
  without added services; `Use supplied enhanced bundle` — Use a complete
  supplied application, NAT, and inspection list after license and capacity
  validation.

### A.21 `srx-nat`

- `nat_task`; header `Task`; ask when requested activity is absent; question
  `What should this NAT run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a NAT design; `Troubleshoot` — Diagnose
  translation, routing, proxy, or session failures; `Migration` — Convert NAT
  behavior from another platform.
- `nat_release`; header `Platform`; ask when model or release is absent and
  affects feature support; question `How should missing SRX model or Junos
  release details be handled?`; options: `Discover first (Recommended)` —
  Identify the exact model and release before feature conclusions; `Exact
  details supplied` — Apply supported features and syntax; `Infer
  conservatively` — Limit output to evidence-supported behavior and disclose
  uncertainty.
- `nat_family`; header `NAT Type`; ask when translation family is absent;
  question `How should an unspecified translation family be handled?`; options:
  `Identify family first (Recommended)` — Establish the address-family
  translation before selecting NAT behavior; `NAT44` — Design supplied
  IPv4-to-IPv4 translation requirements; `NAT64` — Design supplied IPv6-to-IPv4
  translation requirements.
- `nat_tuple`; header `Traffic`; ask when pre- or post-translation tuple is
  incomplete; question `How should an incomplete translation tuple be
  handled?`; options: `Trace tuple first (Recommended)` — Identify source,
  destination, service, zones, and translated values before design; `Use
  supplied complete tuple` — Apply the supplied pre- and post-translation
  values; `Build tuple worksheet` — Produce a worksheet for missing tuple
  fields.
- `nat_context`; header `Context`; ask when zone, interface, or routing-instance
  classification is unclear; question `How should uncertain traffic
  classification be handled?`; options: `Inspect full context first
  (Recommended)` — Inspect complementary zone, interface, and routing-instance
  facts before rule selection; `Use supplied complete context` — Apply the
  supplied complete zone, interface, and routing-instance classification; `Stop
  pending context` — Stop rule conclusions until all complementary
  classification facts are supplied.
- `nat_reach`; header `Reachability`; ask when translated-address reachability
  is unclear; question `How should uncertain translated-address reachability be
  handled?`; options: `Trace reachability first (Recommended)` — Validate
  routing and adjacency before choosing advertisement behavior; `Use supplied
  routed prefix` — Use supplied explicit routing for translated addresses; `Use
  supplied neighbor proxy` — Apply supplied proxy ARP or NDP behavior.
- `nat_return`; header `Return Path`; ask when traffic symmetry is unclear;
  question `How should uncertain NAT return symmetry be handled?`; options:
  `Unknown—trace first (Recommended)` — Collect routing, session, and flow
  evidence before assuming symmetry; `Use supplied symmetric path` — Preserve
  the supplied stateful return through the translator; `Assess supplied
  asymmetric path` — Analyze the supplied asymmetric path and session risk.
- `nat_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  NAT configuration, routes, counters, sessions, and logs before diagnosis;
  `Use supplied artifacts` — Diagnose only from supplied artifacts and limit
  runtime conclusions; `Approved live collection` — Collect targeted read-only
  device evidence with approval.

### A.22 `srx-policy`

- `policy_task`; header `Task`; ask when requested activity is absent; question
  `What should this policy run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess security-policy intent; `Troubleshoot` —
  Diagnose lookup, session, or application failures; `Migration` — Convert from
  another platform.
- `policy_release`; header `Platform`; ask when model, release, or licensing is
  absent and affects features; question `How should missing platform or license
  details be handled?`; options: `Discover first (Recommended)` — Identify the
  model, Junos release, and licenses before feature conclusions; `Exact details
  supplied` — Apply supported policy and services from supplied details; `Infer
  conservatively` — Limit output to evidence-supported base policy and disclose
  uncertainty.
- `policy_model`; header `Policy Model`; ask when architecture is absent;
  question `How should an unspecified policy architecture be resolved?`;
  options: `Confirm architecture first (Recommended)` — Confirm the policy
  architecture before organizing rules; `Use supplied global policy` — Use the
  supplied global-policy architecture; `Use supplied zone-pair policy` — Use
  the supplied zone-pair architecture and specify a complete mixed architecture
  through Other.
- `policy_flow`; header `Traffic`; ask when traffic intent is incomplete;
  question `How should incomplete traffic intent be handled?`; options: `Map
  flow first (Recommended)` — Identify source, destination, application,
  service, zones, and purpose before policy design; `Use supplied complete
  intent` — Design from supplied complete traffic requirements; `Derive from
  migration source` — Derive intent from a supplied normalized source policy.
- `policy_nat`; header `NAT Context`; ask when NAT involvement is unclear;
  question `How should uncertain NAT involvement be handled?`; options: `Trace
  first (Recommended)` — Build a packet-flow trace before selecting policy
  addresses; `Model supplied NAT` — Use the supplied pre- and post-NAT tuple;
  `Model supplied no-NAT` — Use supplied original addresses and routing without
  translation.
- `policy_service`; header `Services`; ask when inspection services are absent;
  question `How should unspecified security-service scope be handled?`;
  options: `Confirm services first (Recommended)` — Inventory application, NAT,
  inspection, license, and capacity requirements before selecting a bundle;
  `Use supplied base-only bundle` — Apply supplied least privilege and logging
  without added services; `Use supplied enhanced bundle` — Use a complete
  supplied application, NAT, and inspection list after license and capacity
  validation.
- `policy_ip`; header `IP Family`; ask when address-family scope is absent;
  question `Which address families should policy cover?`; options: `Dual-stack
  (Recommended)` — Cover IPv4 and IPv6 unicast and specify multicast or
  control-plane scope through Other; `IPv4 only` — Cover only IPv4 unicast and
  specify special traffic scope through Other; `IPv6 only` — Cover only IPv6
  unicast and specify special traffic scope through Other.
- `policy_session`; header `Sessions`; ask when existing-session behavior
  matters and is absent; question `How should existing sessions be treated
  after a policy change?`; options: `Leave existing sessions (Recommended)` —
  Validate new sessions without clearing existing state; `Clear targeted
  sessions` — Clear only separately approved matching sessions;
  `Maintenance-window reset` — Reset broader session state only under separate
  maintenance approval with rollback.
