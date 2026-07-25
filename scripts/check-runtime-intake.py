#!/usr/bin/env python3
"""Validate portable runtime-intake instructions and question catalogs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG_RE = re.compile(
    r"^```json[ \t]*\r?\n(?P<payload>.*?)\r?\n```[ \t]*\r?$",
    re.MULTILINE | re.DOTALL,
)
RUNTIME_ATX_HEADING_RE = re.compile(
    r"^(?P<indent> {0,3})##(?P<spacing>[ \t]+)Runtime intake"
    r"(?P<closing>[ \t]+#+)?[ \t]*\r?$",
    re.MULTILINE,
)
SETEXT_UNDERLINE_RE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
FENCE_LINE_RE = re.compile(
    r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<rest>[^\r\n]*)"
    r"(?P<ending>\r\n|\n|\r)?\Z"
)
ATX_HEADING_RE = re.compile(r"^ {0,3}(?P<marker>#{1,6})(?:[ \t]+|$)")
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
    r"^ {0,3}<(?:pre|script|style|textarea)(?=[ \t>]|\r?$)",
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
LINK_TITLE_CLOSERS = {'"': '"', "'": "'", "(": ")"}
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


def normalize_line_endings(text: str) -> str:
    """Normalize every CommonMark line ending at a public parse boundary."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


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


class MarkdownContainer(NamedTuple):
    """One active CommonMark container block."""

    serial: int
    kind: str
    content_indent: int = 0


class ListMarker(NamedTuple):
    """A parsed CommonMark list marker and its content indentation."""

    content_start: int
    content_indent: int
    ordered: int | None
    empty: bool


class MarkdownLine(NamedTuple):
    """An active logical line mapped to its physical source position."""

    source_start: int
    source_end: int
    content_start: int
    content: str
    normalized: str
    containers: tuple[MarkdownContainer, ...]
    block_kind: str
    heading_level: int | None = None

    @property
    def top_level(self) -> bool:
        return not self.containers


class MarkdownHeading(NamedTuple):
    """An ATX or Setext heading with complete logical content."""

    source_start: int
    source_end: int
    level: int
    content: str
    containers: tuple[MarkdownContainer, ...]
    style: str

    @property
    def top_level(self) -> bool:
        return not self.containers


class MarkdownParagraph(NamedTuple):
    """The open paragraph that can receive lazy continuation lines."""

    source_start: int
    containers: tuple[MarkdownContainer, ...]
    lines: list[str]


class MarkdownFence(NamedTuple):
    """An open fenced code block scoped to its container path."""

    character: str
    length: int
    containers: tuple[MarkdownContainer, ...]


class MarkdownLinkReference(NamedTuple):
    """Continuation state for a multiline link reference definition."""

    containers: tuple[MarkdownContainer, ...]
    phase: str
    pending_source_start: int | None = None
    pending_lines: tuple[str, ...] = ()
    label_length: int = 0
    label_nonblank: bool = False
    title_closer: str | None = None


class ContainerParse(NamedTuple):
    """Container prefix result for one physical Markdown line."""

    cursor: int
    containers: tuple[MarkdownContainer, ...]


class MarkdownAnalysis:
    """CommonMark-aware block view used by every structural probe."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.lines: list[MarkdownLine] = []
        self.headings: list[MarkdownHeading] = []
        self.raw_html_lines: list[MarkdownLine] = []
        self._active_parts: list[str] = []
        self._normalized_parts: list[str] = []
        self._containers: tuple[MarkdownContainer, ...] = ()
        self._paragraph: MarkdownParagraph | None = None
        self._fence: MarkdownFence | None = None
        self._comment_containers: tuple[MarkdownContainer, ...] | None = None
        self._link_reference: MarkdownLinkReference | None = None
        self._next_container_serial = 1
        self._analyze()
        self.active_text = "".join(self._active_parts)
        self.normalized_text = "".join(self._normalized_parts)

    @staticmethod
    def _split_ending(line: str) -> tuple[str, str]:
        content = line.rstrip("\r\n")
        return content, line[len(content) :]

    @staticmethod
    def _expand_block_tabs(content: str) -> str:
        """Expand tabs to CommonMark's four-column block tab stops."""
        return content.expandtabs(4)

    @staticmethod
    def _source_index_for_column(content: str, column: int) -> int:
        """Map an expanded block column back to a physical source index."""
        visual_column = 0
        for index, character in enumerate(content):
            if visual_column >= column:
                return index
            if character == "\t":
                next_column = visual_column + (4 - visual_column % 4)
            else:
                next_column = visual_column + 1
            if next_column >= column:
                return index + 1
            visual_column = next_column
        return len(content)

    @staticmethod
    def _consume_indentation(
        content: str,
        cursor: int,
        width: int,
    ) -> int | None:
        end = cursor + width
        if content[cursor:end] == " " * width:
            return end
        return None

    @staticmethod
    def _quote_prefix_end(content: str, cursor: int) -> int | None:
        probe = cursor
        indentation = 0
        while (
            indentation < 3
            and probe < len(content)
            and content[probe] == " "
        ):
            probe += 1
            indentation += 1
        if probe >= len(content) or content[probe] != ">":
            return None
        probe += 1
        if probe < len(content) and content[probe] in " \t":
            probe += 1
        return probe

    @staticmethod
    def _list_marker(
        content: str,
        cursor: int,
    ) -> ListMarker | None:
        probe = cursor
        indentation = 0
        while (
            indentation < 3
            and probe < len(content)
            and content[probe] == " "
        ):
            probe += 1
            indentation += 1

        marker_match = re.match(
            r"(?:(?P<bullet>[-+*])|(?P<ordered>[0-9]{1,9})[.)])",
            content[probe:],
        )
        if marker_match is None:
            return None
        marker_end = probe + marker_match.end()
        spacing_end = marker_end
        while (
            spacing_end < len(content)
            and content[spacing_end] in " \t"
        ):
            spacing_end += 1
        spacing_width = spacing_end - marker_end
        empty = spacing_end == len(content)
        if spacing_width == 0 and not empty:
            return None

        marker_width = marker_match.end()
        if empty:
            content_start = spacing_end
            content_indent = indentation + marker_width + 1
        elif spacing_width <= 4:
            padding = spacing_width
            content_start = spacing_end
            content_indent = indentation + marker_width + padding
        else:
            # Five or more following spaces count as one space of list
            # padding; the rest remains content indentation.
            padding = 1
            content_start = marker_end + 1
            content_indent = indentation + marker_width + padding
        ordered = marker_match.group("ordered")
        return ListMarker(
            content_start,
            content_indent,
            int(ordered) if ordered is not None else None,
            empty,
        )

    def _new_container(
        self,
        kind: str,
        content_indent: int = 0,
    ) -> MarkdownContainer:
        container = MarkdownContainer(
            self._next_container_serial,
            kind,
            content_indent,
        )
        self._next_container_serial += 1
        return container

    @staticmethod
    def _is_thematic_break(content: str, cursor: int = 0) -> bool:
        remainder = content[cursor:]
        indentation = len(remainder) - len(remainder.lstrip(" "))
        if indentation > 3:
            return False
        marks = remainder[indentation:].replace(" ", "").replace("\t", "")
        return (
            len(marks) >= 3
            and marks[0] in "*-_"
            and all(mark == marks[0] for mark in marks)
        )

    @staticmethod
    def _atx_heading_content(
        logical: str,
        match: re.Match[str],
    ) -> str:
        content = logical[match.end() :].strip(" \t")
        return re.sub(r"[ \t]+#+[ \t]*$", "", content).strip(" \t")

    @staticmethod
    def _scan_link_label_segment(
        segment: str,
    ) -> tuple[str, str, int, bool]:
        """Scan one physical segment of a CommonMark link label."""
        cursor = 0
        while cursor < len(segment):
            character = segment[cursor]
            if character == "\\" and cursor + 1 < len(segment):
                cursor += 2
                continue
            if character == "[":
                return "invalid", "", cursor, False
            if character == "]":
                if segment[cursor + 1 : cursor + 2] != ":":
                    return "invalid", "", cursor, False
                label = segment[:cursor]
                return (
                    "closed",
                    segment[cursor + 2 :],
                    len(label),
                    any(not char.isspace() for char in label),
                )
            cursor += 1
        return (
            "open",
            "",
            len(segment),
            any(not char.isspace() for char in segment),
        )

    @staticmethod
    def _scan_link_title(
        text: str,
        closer: str | None = None,
    ) -> tuple[str, str | None]:
        candidate = text
        if closer is None:
            indentation = len(candidate) - len(candidate.lstrip(" "))
            if indentation > 3:
                return "invalid", None
            candidate = candidate[indentation:]
            if not candidate or candidate[0] not in LINK_TITLE_CLOSERS:
                return "invalid", None
            closer = LINK_TITLE_CLOSERS[candidate[0]]
            cursor = 1
        else:
            cursor = 0

        while cursor < len(candidate):
            character = candidate[cursor]
            if character == "\\" and cursor + 1 < len(candidate):
                cursor += 2
                continue
            if character == closer:
                if candidate[cursor + 1 :].strip(" \t"):
                    return "invalid", None
                return "complete", closer
            cursor += 1
        return "open", closer

    @classmethod
    def _scan_link_destination(
        cls,
        text: str,
    ) -> tuple[str, str | None]:
        candidate = text.lstrip(" \t")
        if not candidate:
            return "destination", None

        if candidate[0] == "<":
            cursor = 1
            while cursor < len(candidate):
                character = candidate[cursor]
                if character == "\\" and cursor + 1 < len(candidate):
                    cursor += 2
                    continue
                if character == "<":
                    return "invalid", None
                if character == ">":
                    cursor += 1
                    break
                cursor += 1
            else:
                return "invalid", None
        else:
            cursor = 0
            depth = 0
            while cursor < len(candidate) and candidate[cursor] not in " \t":
                character = candidate[cursor]
                if character == "\\" and cursor + 1 < len(candidate):
                    cursor += 2
                    continue
                if character == "(":
                    depth += 1
                    if depth > 32:
                        return "invalid", None
                elif character == ")":
                    if depth == 0:
                        return "invalid", None
                    depth -= 1
                cursor += 1
            if cursor == 0 or depth:
                return "invalid", None

        remainder = candidate[cursor:]
        if not remainder:
            return "optional-title", None
        if remainder[0] not in " \t":
            return "invalid", None
        title = remainder.lstrip(" \t")
        if not title:
            return "optional-title", None
        title_status, closer = cls._scan_link_title(title)
        if title_status == "complete":
            return "complete", None
        if title_status == "open":
            return "title", closer
        return "invalid", None

    @staticmethod
    def _raw_html_kind(content: str) -> int | None:
        if RAW_HTML_TYPE1_RE.match(content):
            return 1
        if RAW_HTML_PROCESSING_INSTRUCTION_RE.match(content):
            return 3
        if RAW_HTML_DECLARATION_RE.match(content):
            return 4
        if RAW_HTML_CDATA_RE.match(content):
            return 5
        if RAW_HTML_TYPE6_RE.match(content):
            return 6
        if RAW_HTML_TYPE7_RE.fullmatch(content):
            return 7
        return None

    @staticmethod
    def _valid_fence_opener(content: str) -> re.Match[str] | None:
        match = FENCE_LINE_RE.fullmatch(content)
        if match is None:
            return None
        fence = match.group("fence")
        info = match.group("rest")
        if fence[0] == "`" and "`" in info:
            return None
        return match

    def _line_interrupts_paragraph(self, content: str, cursor: int) -> bool:
        remainder = content[cursor:]
        if not remainder.strip(" \t"):
            return True
        if self._quote_prefix_end(content, cursor) is not None:
            return True
        if self._is_thematic_break(content, cursor):
            return True
        marker = self._list_marker(content, cursor)
        if marker is not None:
            if marker.empty:
                return False
            return marker.ordered is None or marker.ordered == 1
        if ATX_HEADING_RE.match(remainder):
            return True
        if self._valid_fence_opener(remainder) is not None:
            return True
        if re.match(r"^ {0,3}<!--", remainder):
            return True
        html_kind = self._raw_html_kind(remainder)
        if html_kind is not None:
            return html_kind != 7
        # A Setext underline completes the current paragraph.
        if SETEXT_UNDERLINE_RE.fullmatch(remainder):
            return False
        return False

    def _continue_existing_containers(
        self,
        content: str,
        *,
        allow_lazy: bool,
    ) -> ContainerParse:
        if not content.strip(" \t"):
            return ContainerParse(len(content), self._containers)

        cursor = 0
        matched: list[MarkdownContainer] = []
        for container in self._containers:
            if container.kind == "quote":
                next_cursor = self._quote_prefix_end(content, cursor)
            else:
                next_cursor = self._consume_indentation(
                    content,
                    cursor,
                    container.content_indent,
                )
            if next_cursor is None:
                sibling_marker = (
                    self._list_marker(content, cursor)
                    if container.kind == "list"
                    else None
                )
                is_list_sibling = (
                    sibling_marker is not None
                )
                if (
                    allow_lazy
                    and not is_list_sibling
                    and self._paragraph is not None
                    and self._paragraph.containers == self._containers
                    and not self._line_interrupts_paragraph(content, cursor)
                ):
                    return ContainerParse(cursor, self._containers)
                break
            cursor = next_cursor
            matched.append(container)
        return ContainerParse(cursor, tuple(matched))

    def _parse_containers(
        self,
        content: str,
        *,
        allow_lazy: bool,
    ) -> ContainerParse:
        continued = self._continue_existing_containers(
            content,
            allow_lazy=allow_lazy,
        )
        cursor = continued.cursor
        containers = list(continued.containers)

        while cursor < len(content):
            quote_end = self._quote_prefix_end(content, cursor)
            if quote_end is not None:
                containers.append(self._new_container("quote"))
                cursor = quote_end
                continue

            if self._is_thematic_break(content, cursor):
                break
            marker = self._list_marker(content, cursor)
            if marker is None:
                break
            current_path = tuple(containers)
            if (
                (
                    marker.empty
                    or (
                        marker.ordered is not None
                        and marker.ordered != 1
                    )
                )
                and self._paragraph is not None
                and self._paragraph.containers == current_path
            ):
                break
            containers.append(
                self._new_container(
                    "list",
                    marker.content_indent,
                )
            )
            cursor = marker.content_start

        return ContainerParse(cursor, tuple(containers))

    def _append_masked_line(self, line: str) -> None:
        masked = mask_non_newline_characters(line)
        self._active_parts.append(masked)
        self._normalized_parts.append(masked)

    def _close_paragraph(self) -> None:
        self._paragraph = None

    def _append_logical_line(
        self,
        *,
        source_start: int,
        raw_line: str,
        masked_line: str,
        block_content: str,
        parsed: ContainerParse,
        block_kind: str,
        heading_level: int | None = None,
    ) -> MarkdownLine:
        source_content, ending = self._split_ending(masked_line)
        logical = block_content[parsed.cursor:]
        normalized = logical + ending
        line = MarkdownLine(
            source_start,
            source_start + len(raw_line),
            source_start
            + self._source_index_for_column(
                source_content,
                parsed.cursor,
            ),
            logical,
            normalized,
            parsed.containers,
            block_kind,
            heading_level,
        )
        self.lines.append(line)
        self._active_parts.append(masked_line)
        self._normalized_parts.append(normalized)
        return line

    def _record_setext_heading(
        self,
        *,
        source_end: int,
        underline: str,
    ) -> None:
        if self._paragraph is None:
            return
        raw_content = " ".join(
            line.strip(" \t") for line in self._paragraph.lines
        ).strip()
        self.headings.append(
            MarkdownHeading(
                self._paragraph.source_start,
                source_end,
                1 if underline.lstrip().startswith("=") else 2,
                raw_content,
                self._paragraph.containers,
                "setext",
            )
        )

    def _classify_active_line(
        self,
        *,
        source_start: int,
        raw_line: str,
        masked_line: str,
        block_content: str,
        parsed: ContainerParse,
    ) -> None:
        logical = block_content[parsed.cursor:]
        path = parsed.containers

        if not logical.strip(" \t"):
            self._link_reference = None
            self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind="blank",
            )
            self._close_paragraph()
            return

        same_paragraph = (
            self._paragraph is not None
            and self._paragraph.containers == path
        )
        if not same_paragraph:
            self._close_paragraph()

        # CommonMark block indicators take precedence over speculative
        # multiline reference parsing. Restore the buffered lines as the
        # paragraph they form before classifying the interrupting line.
        pending_reference = self._link_reference
        if (
            pending_reference is not None
            and pending_reference.pending_lines
            and pending_reference.containers == path
            and self._line_interrupts_paragraph(
                block_content,
                parsed.cursor,
            )
        ):
            assert pending_reference.pending_source_start is not None
            self._paragraph = MarkdownParagraph(
                pending_reference.pending_source_start,
                path,
                list(pending_reference.pending_lines),
            )
            self._link_reference = None
            same_paragraph = True

        if self._link_reference is not None:
            link_reference = self._link_reference
            pending_lines = link_reference.pending_lines + (logical,)
            if link_reference.containers == path:
                if link_reference.phase == "label":
                    status, suffix, length, nonblank = (
                        self._scan_link_label_segment(logical)
                    )
                    label_length = link_reference.label_length + 1 + length
                    label_nonblank = (
                        link_reference.label_nonblank or nonblank
                    )
                    if status == "open" and label_length <= 999:
                        self._append_logical_line(
                            source_start=source_start,
                            raw_line=raw_line,
                            masked_line=masked_line,
                            block_content=block_content,
                            parsed=parsed,
                            block_kind="link-reference-definition",
                        )
                        self._link_reference = MarkdownLinkReference(
                            path,
                            "label",
                            link_reference.pending_source_start,
                            pending_lines,
                            label_length,
                            label_nonblank,
                        )
                        self._close_paragraph()
                        return
                    if (
                        status == "closed"
                        and label_length <= 999
                        and label_nonblank
                    ):
                        next_phase, title_closer = (
                            self._scan_link_destination(suffix)
                        )
                        if next_phase != "invalid":
                            self._append_logical_line(
                                source_start=source_start,
                                raw_line=raw_line,
                                masked_line=masked_line,
                                block_content=block_content,
                                parsed=parsed,
                                block_kind="link-reference-definition",
                            )
                            if next_phase == "destination":
                                self._link_reference = MarkdownLinkReference(
                                    path,
                                    "destination",
                                    link_reference.pending_source_start,
                                    pending_lines,
                                )
                            elif next_phase == "optional-title":
                                self._link_reference = MarkdownLinkReference(
                                    path,
                                    "optional-title",
                                )
                            elif next_phase == "title":
                                self._link_reference = MarkdownLinkReference(
                                    path,
                                    "title",
                                    link_reference.pending_source_start,
                                    pending_lines,
                                    title_closer=title_closer,
                                )
                            else:
                                self._link_reference = None
                            self._close_paragraph()
                            return
                elif link_reference.phase == "destination":
                    next_phase, title_closer = self._scan_link_destination(
                        logical
                    )
                    if next_phase not in ("invalid", "destination"):
                        self._append_logical_line(
                            source_start=source_start,
                            raw_line=raw_line,
                            masked_line=masked_line,
                            block_content=block_content,
                            parsed=parsed,
                            block_kind="link-reference-definition",
                        )
                        if next_phase == "optional-title":
                            self._link_reference = MarkdownLinkReference(
                                path,
                                "optional-title",
                            )
                        elif next_phase == "title":
                            self._link_reference = MarkdownLinkReference(
                                path,
                                "title",
                                link_reference.pending_source_start,
                                pending_lines,
                                title_closer=title_closer,
                            )
                        else:
                            self._link_reference = None
                        self._close_paragraph()
                        return
                elif link_reference.phase == "optional-title":
                    title_status, closer = self._scan_link_title(logical)
                    if title_status in ("complete", "open"):
                        line = self._append_logical_line(
                            source_start=source_start,
                            raw_line=raw_line,
                            masked_line=masked_line,
                            block_content=block_content,
                            parsed=parsed,
                            block_kind="link-reference-definition",
                        )
                        self._link_reference = (
                            None
                            if title_status == "complete"
                            else MarkdownLinkReference(
                                path,
                                "title",
                                line.content_start,
                                (logical,),
                                title_closer=closer,
                            )
                        )
                        self._close_paragraph()
                        return
                elif link_reference.phase == "title":
                    assert link_reference.title_closer is not None
                    title_status, _closer = self._scan_link_title(
                        logical,
                        link_reference.title_closer,
                    )
                    if title_status in ("complete", "open"):
                        self._append_logical_line(
                            source_start=source_start,
                            raw_line=raw_line,
                            masked_line=masked_line,
                            block_content=block_content,
                            parsed=parsed,
                            block_kind="link-reference-definition",
                        )
                        self._link_reference = (
                            None
                            if title_status == "complete"
                            else link_reference._replace(
                                pending_lines=pending_lines
                            )
                        )
                        self._close_paragraph()
                        return

            if link_reference.pending_lines:
                assert link_reference.pending_source_start is not None
                self._paragraph = MarkdownParagraph(
                    link_reference.pending_source_start,
                    link_reference.containers,
                    list(link_reference.pending_lines),
                )
                same_paragraph = link_reference.containers == path
                if not same_paragraph:
                    self._close_paragraph()
            self._link_reference = None

        if not same_paragraph and logical.startswith("    "):
            self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind="indented-code",
            )
            return

        if not same_paragraph:
            indentation = len(logical) - len(logical.lstrip(" "))
            candidate = logical[indentation:] if indentation <= 3 else ""
            if candidate.startswith("["):
                status, suffix, length, nonblank = (
                    self._scan_link_label_segment(candidate[1:])
                )
                next_phase = "invalid"
                title_closer: str | None = None
                if status == "closed" and length <= 999 and nonblank:
                    next_phase, title_closer = (
                        self._scan_link_destination(suffix)
                    )
                if (
                    (status == "open" and length <= 999)
                    or next_phase != "invalid"
                ):
                    line = self._append_logical_line(
                        source_start=source_start,
                        raw_line=raw_line,
                        masked_line=masked_line,
                        block_content=block_content,
                        parsed=parsed,
                        block_kind="link-reference-definition",
                    )
                    if status == "open":
                        self._link_reference = MarkdownLinkReference(
                            path,
                            "label",
                            line.content_start,
                            (logical,),
                            length,
                            nonblank,
                        )
                    elif next_phase == "destination":
                        self._link_reference = MarkdownLinkReference(
                            path,
                            "destination",
                            line.content_start,
                            (logical,),
                        )
                    elif next_phase == "optional-title":
                        self._link_reference = MarkdownLinkReference(
                            path,
                            "optional-title",
                        )
                    elif next_phase == "title":
                        self._link_reference = MarkdownLinkReference(
                            path,
                            "title",
                            line.content_start,
                            (logical,),
                            title_closer=title_closer,
                        )
                    else:
                        self._link_reference = None
                    self._close_paragraph()
                    return

        atx_match = ATX_HEADING_RE.match(logical)
        if atx_match is not None:
            level = len(atx_match.group("marker"))
            line = self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind="atx",
                heading_level=level,
            )
            self.headings.append(
                MarkdownHeading(
                    source_start,
                    line.source_end,
                    level,
                    self._atx_heading_content(logical, atx_match),
                    path,
                    "atx",
                )
            )
            self._close_paragraph()
            return

        if (
            same_paragraph
            and SETEXT_UNDERLINE_RE.fullmatch(logical) is not None
        ):
            level = 1 if logical.lstrip().startswith("=") else 2
            line = self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind="setext-underline",
                heading_level=level,
            )
            self._record_setext_heading(
                source_end=line.source_end,
                underline=logical,
            )
            self._close_paragraph()
            return

        if self._is_thematic_break(logical):
            self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind="thematic-break",
            )
            self._close_paragraph()
            return

        html_kind = self._raw_html_kind(logical)
        if html_kind is not None and not (
            html_kind == 7 and same_paragraph
        ):
            line = self._append_logical_line(
                source_start=source_start,
                raw_line=raw_line,
                masked_line=masked_line,
                block_content=block_content,
                parsed=parsed,
                block_kind=f"raw-html-{html_kind}",
            )
            self.raw_html_lines.append(line)
            self._close_paragraph()
            return

        line = self._append_logical_line(
            source_start=source_start,
            raw_line=raw_line,
            masked_line=masked_line,
            block_content=block_content,
            parsed=parsed,
            block_kind="paragraph",
        )
        if same_paragraph:
            assert self._paragraph is not None
            self._paragraph.lines.append(logical)
        else:
            self._paragraph = MarkdownParagraph(
                line.content_start,
                path,
                [logical],
            )

    def _process_line(self, source_start: int, raw_line: str) -> None:
        source_content, _ending = self._split_ending(raw_line)
        block_content = self._expand_block_tabs(source_content)

        if self._fence is not None:
            continued = self._continue_existing_containers(
                block_content,
                allow_lazy=False,
            )
            fence_path = self._fence.containers
            if (
                not block_content.strip(" ")
                or continued.containers == fence_path
            ):
                logical = block_content[continued.cursor:]
                closing = FENCE_LINE_RE.fullmatch(logical)
                self._append_masked_line(raw_line)
                if (
                    closing is not None
                    and closing.group("fence")[0]
                    == self._fence.character
                    and len(closing.group("fence"))
                    >= self._fence.length
                    and not closing.group("rest").strip(" \t")
                ):
                    self._fence = None
                self._containers = continued.containers
                return
            # Exiting a quote/list closes its fenced child. Reprocess this
            # deindented physical line as a new active block.
            self._fence = None
            self._containers = continued.containers

        handled_comment = False
        if self._comment_containers is not None:
            continued = self._continue_existing_containers(
                block_content,
                allow_lazy=False,
            )
            comment_path = self._comment_containers
            if (
                not block_content.strip(" ")
                or continued.containers == comment_path
            ):
                masked_line, in_comment = mask_html_comments(raw_line, True)
                if not in_comment:
                    self._comment_containers = None
                handled_comment = True
            else:
                # An HTML comment block opened inside a container ends when
                # that container exits. Reprocess this physical line active.
                self._comment_containers = None
                self._containers = continued.containers

        if handled_comment:
            masked_content = self._split_ending(masked_line)[0]
            block_content = self._expand_block_tabs(masked_content)
            parsed = self._parse_containers(
                block_content,
                allow_lazy=True,
            )
        else:
            parsed = self._parse_containers(block_content, allow_lazy=True)
            logical = block_content[parsed.cursor:]
            opener = self._valid_fence_opener(logical)
            if opener is not None:
                fence = opener.group("fence")
                self._containers = parsed.containers
                self._close_paragraph()
                self._link_reference = None
                self._fence = MarkdownFence(
                    fence[0],
                    len(fence),
                    parsed.containers,
                )
                self._append_masked_line(raw_line)
                return

            masked_line, in_comment = mask_html_comments(
                raw_line,
                False,
            )
            if masked_line != raw_line:
                self._containers = parsed.containers
                masked_content = self._split_ending(masked_line)[0]
                block_content = self._expand_block_tabs(masked_content)
                parsed = self._parse_containers(
                    block_content,
                    allow_lazy=True,
                )
            if in_comment:
                self._comment_containers = parsed.containers

        self._containers = parsed.containers
        self._classify_active_line(
            source_start=source_start,
            raw_line=raw_line,
            masked_line=masked_line,
            block_content=block_content,
            parsed=parsed,
        )

    def _analyze(self) -> None:
        source_start = 0
        for raw_line in self.text.splitlines(keepends=True):
            self._process_line(source_start, raw_line)
            source_start += len(raw_line)
        if source_start < len(self.text):
            self._process_line(source_start, self.text[source_start:])

    def normalized_from(self, source_start: int) -> str:
        return "".join(
            line.normalized
            for line in self.lines
            if line.source_start >= source_start
        )

    def next_top_level_heading(
        self,
        source_start: int,
        *,
        maximum_level: int,
    ) -> MarkdownHeading | None:
        return next(
            (
                heading
                for heading in self.headings
                if heading.top_level
                and heading.level <= maximum_level
                and heading.source_start >= source_start
            ),
            None,
        )


def analyze_markdown(text: str) -> MarkdownAnalysis:
    """Build the shared source-mapped active Markdown block view."""
    return MarkdownAnalysis(text)


def mask_inactive_markdown(text: str) -> str:
    """Blank comments and container-scoped fences without changing offsets."""
    return analyze_markdown(text).active_text


def active_top_level_catalog_matches(text: str) -> list[re.Match[str]]:
    """Return column-zero JSON fences whose opener is active Markdown."""
    active_matches: list[re.Match[str]] = []
    sentinel = "CATJSON"
    for match in CATALOG_RE.finditer(text):
        opener_start = match.start()
        probe = (
            text[:opener_start]
            + sentinel
            + text[opener_start + len(sentinel) :]
        )
        active_probe = mask_inactive_markdown(probe)
        if (
            active_probe[opener_start : opener_start + len(sentinel)]
            == sentinel
        ):
            active_matches.append(match)
    return active_matches


def extract_runtime_section(path: Path, text: str) -> tuple[str | None, list[str]]:
    analysis = analyze_markdown(text)
    active_markdown = analysis.active_text
    equivalent_headings = [
        heading
        for heading in analysis.headings
        if heading.content == "Runtime intake"
        and (
            heading.style == "setext"
            or heading.level == 2
        )
    ]
    if len(equivalent_headings) != 1:
        return None, [f"{path}: expected exactly one '## Runtime intake' section"]

    active_atx = list(RUNTIME_ATX_HEADING_RE.finditer(active_markdown))
    if len(active_atx) != 1:
        return None, [
            f"{path}: primary '## Runtime intake' heading must use canonical "
            "column-zero ATX form"
        ]
    heading_match = active_atx[0]
    if heading_match.group("indent"):
        return None, [
            f"{path}: primary '## Runtime intake' heading must start at column zero"
        ]
    if (
        heading_match.group("spacing") != " "
        or heading_match.group("closing") is not None
    ):
        return None, [
            f"{path}: primary '## Runtime intake' heading must use canonical "
            "column-zero ATX form"
        ]

    start = heading_match.end()
    next_heading = analysis.next_top_level_heading(
        start,
        maximum_level=2,
    )
    end = (
        next_heading.source_start
        if next_heading is not None
        else len(text)
    )
    return text[start:end], []


def validate_ambiguous_markup(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    if "<!--" in text or "-->" in text:
        errors.append(f"{path}: HTML comment delimiters are not allowed")
    if analyze_markdown(text).raw_html_lines:
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
    text = normalize_line_endings(text)
    errors: list[str] = []
    analysis = analyze_markdown(text)
    active_markdown = analysis.active_text
    if "<!--" in text or "-->" in text:
        errors.append(f"{path}: HTML comment delimiters are not allowed")
    if analysis.raw_html_lines:
        errors.append(f"{path}: raw HTML block syntax is not allowed")

    canonical_heading_matches: dict[str, re.Match[str]] = {}
    for required_heading in REQUIRED_REFERENCE_HEADINGS:
        marker, required_content = required_heading.split(" ", 1)
        required_level = len(marker)
        heading_matches = list(
            re.finditer(
                rf"^{re.escape(required_heading)}[ \t]*\r?$",
                active_markdown,
                re.MULTILINE,
            )
        )
        equivalent_headings = [
            heading
            for heading in analysis.headings
            if heading.level == required_level
            and heading.content == required_content
        ]
        if not heading_matches:
            errors.append(f"{path}: missing {required_heading!r}")
        elif (
            len(heading_matches) != 1
            or len(equivalent_headings) != 1
        ):
            errors.append(
                f"{path}: expected exactly one active "
                f"{required_heading!r} heading"
            )
        else:
            canonical_heading_matches[required_heading] = heading_matches[0]

    if len(canonical_heading_matches) == len(REQUIRED_REFERENCE_HEADINGS):
        heading_positions = [
            canonical_heading_matches[heading].start()
            for heading in REQUIRED_REFERENCE_HEADINGS
        ]
        if heading_positions != sorted(heading_positions):
            errors.append(
                f"{path}: required headings are not in canonical order"
            )

    tool_heading = canonical_heading_matches.get("## Tool adaptation")
    catalog_heading = canonical_heading_matches.get("## Question catalog")

    required_adaptation = (
        ("Claude projection", CLAUDE_ADAPTATION),
        ("Codex projection", CODEX_ADAPTATION),
        ("fallback and free-text Other", FALLBACK_ADAPTATION),
    )
    tool_section = ""
    if tool_heading is not None:
        tool_start = tool_heading.end()
        next_heading = analysis.next_top_level_heading(
            tool_start,
            maximum_level=2,
        )
        tool_end = (
            next_heading.source_start
            if next_heading is not None
            else len(active_markdown)
        )
        tool_section = active_markdown[tool_start:tool_end]
    for name, required_text in required_adaptation:
        if required_text not in active_markdown:
            errors.append(f"{path}: missing exact {name} language")
        elif required_text not in tool_section:
            errors.append(
                f"{path}: {name} must be inside '## Tool adaptation'"
            )

    matches = active_top_level_catalog_matches(text)
    if len(matches) != 1:
        errors.append(
            f"{path}: expected exactly one active top-level JSON catalog"
        )
        return errors
    if catalog_heading is not None:
        catalog_start = catalog_heading.end()
        next_heading = analysis.next_top_level_heading(
            catalog_start,
            maximum_level=2,
        )
        catalog_end = (
            next_heading.source_start
            if next_heading is not None
            else len(active_markdown)
        )
        if not catalog_start <= matches[0].start() < catalog_end:
            errors.append(
                f"{path}: JSON catalog must be inside "
                "'## Question catalog'"
            )

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
