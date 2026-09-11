#!/usr/bin/env python3
"""Check relative links in tracked Markdown files resolve to existing targets."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

# A link destination is either <bracketed> or bare, optionally followed by a
# title in double quotes, single quotes, or parentheses. Parsing the title
# separately matters: folding it into the destination turns a perfectly good
# [readme](README.md "Overview") into a hunt for a file named 'README.md "Overview"'.
# The bare destination part is parsed via _parse_bare_destination to handle
# balanced parens and escaped parens as CommonMark requires.
INLINE_LINK_RE = re.compile(
    r"""!?\[(?:[^\]\\]|\\.)*\]\(""",
    re.VERBOSE,
)
REFERENCE_LINK_RE = re.compile(r"^\[(?:[^\]\\]|\\.)+\]:\s+(<[^<>\n]*>|\S+)")
# Opening fence: up to three spaces of indent, then >=3 backticks or tildes.
# The length is captured because a closing fence must be at least as long --
# a ```json block nested inside a ````markdown block does not close it.
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# A backtick run of length N is closed only by a run of exactly N, and a span
# may cross lines.
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
SKIPPED_SCHEMES = ("http://", "https://", "mailto:", "#")
ASCII_PUNCTUATION = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
# CommonMark: a backslash may escape any ASCII punctuation.
BACKSLASH_ESCAPE_RE = re.compile(r"\\([!-/:-@\[-`{-~])")


def mask_code_spans(text: str) -> str:
    """Blank out inline code spans, preserving newlines so line numbers hold.

    A target inside backticks is being displayed, not linked.
    """
    return CODE_SPAN_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def _parse_bare_destination(text: str, start: int) -> tuple[str, int] | None:
    """Parse a bare link destination starting at position start.

    Returns (destination, end_position) or None if no valid destination found.
    Handles balanced parentheses and backslash-escaped characters per CommonMark.
    """
    i = start
    dest = []
    paren_depth = 0

    while i < len(text):
        ch = text[i]

        # CommonMark bare destinations cannot hold unescaped angle brackets.
        # Accepting them lets malformed text such as `[o](<bad<[r](x.md)>)`
        # be swallowed whole: the scan invents a target that cannot exist AND
        # advances past the genuine link nested inside it.
        if ch in "<>":
            return None

        # Whitespace always ends a bare destination. A backslash cannot escape
        # it: CommonMark allows backslash escapes only before ASCII
        # punctuation, so `[a](missing\\ file.md)` is prose, not a link, and
        # swallowing the space reports a broken file that was never linked.
        if ch in " \t\n\r\f\v":
            break

        if ch == "\\":
            if i + 1 < len(text) and text[i + 1] in ASCII_PUNCTUATION:
                dest.append(ch)
                dest.append(text[i + 1])
                i += 2
                continue
            # A backslash before anything else is a literal backslash.
            dest.append(ch)
            i += 1
            continue

        # Track paren depth
        if ch == "(":
            paren_depth += 1
            dest.append(ch)
            i += 1
        elif ch == ")":
            if paren_depth > 0:
                paren_depth -= 1
                dest.append(ch)
                i += 1
            else:
                # Closing paren for the link itself
                break
        else:
            dest.append(ch)
            i += 1

    if not dest:
        return None

    # An unmatched "(" means this was never a well-formed destination --
    # `[a](missing( )` is ordinary text. Returning `missing(` invents a broken
    # link and fails the gate on a document that has none.
    if paren_depth != 0:
        return None

    return "".join(dest), i


def _parse_angle_destination(text: str, start: int) -> tuple[str, int] | None:
    """Parse an angle-bracketed destination <...>.

    Returns (destination, end_position) or None.
    """
    if start >= len(text) or text[start] != "<":
        return None

    i = start + 1
    while i < len(text):
        ch = text[i]
        if ch == ">":
            return text[start + 1 : i], i + 1
        if ch == "\n" or ch == "<":
            return None
        i += 1

    return None


def clean_destination(target: str) -> str:
    r"""Strip Markdown destination delimiters and unescape backslash escapes.

    CommonMark allows backslash to escape any ASCII punctuation; those escapes
    must be removed before resolving the path, or [link](file\(1\).md) fails
    to resolve to file(1).md.
    """
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    # Unescape backslash-escaped ASCII punctuation
    target = BACKSLASH_ESCAPE_RE.sub(r"\1", target)
    return target


def extract_links(content: str) -> list[tuple[int, str]]:
    """Return (line_number, target) for each checkable relative link.

    Links inside fenced code blocks are skipped. Those blocks are illustrative
    -- historical implementation plans embed snippets destined for a file
    elsewhere in the tree, so their targets are relative to that destination,
    not to the plan quoting them. Resolving them against the quoting file
    reports false positives, and "fixing" those reports corrupts the snippet.
    """
    fence_char: str | None = None
    fence_length = 0
    # Fences are resolved on raw lines BEFORE code spans are masked. Doing it
    # the other way round is subtly wrong: a ``` fence is itself a run of three
    # backticks, so the code-span matcher pairs an opening fence with its
    # closing one, blanks both, and silently exposes every link between them.
    runs: list[list[tuple[int, str]]] = [[]]

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        fence_match = FENCE_RE.match(raw_line)
        if fence_match:
            marker = fence_match.group(1)
            trailing = fence_match.group(2)
            if fence_char is None:
                # A backtick info string may not itself contain backticks, so
                # a line like ```x``` is NOT an opening fence — it is an inline
                # code span. Only consume the line when the fence is actually
                # accepted; otherwise let it fall through to masking and link
                # extraction, or a real link sharing that line is lost.
                if not (marker[0] == "`" and "`" in trailing):
                    fence_char = marker[0]
                    fence_length = len(marker)
                    runs.append([])
                    continue
            else:
                # Closing fence: same character, at least as long, no trailing text.
                if (
                    marker[0] == fence_char
                    and len(marker) >= fence_length
                    and not trailing.strip()
                ):
                    fence_char = None
                    fence_length = 0
                    runs.append([])
                continue

        if fence_char is not None:
            continue

        runs[-1].append((line_number, raw_line))

    links: list[tuple[int, str]] = []
    for run in runs:
        if not run:
            continue
        # Build position-to-line-number map for this run
        line_map: list[tuple[int, int]] = []  # (offset, line_number)
        offset = 0
        for line_number, line in run:
            line_map.append((offset, line_number))
            offset += len(line) + 1  # +1 for the newline

        # Mask each unfenced run as one block so a code span may cross lines
        # without ever seeing a fence marker, and so link destinations can
        # span lines per CommonMark.
        masked = mask_code_spans("\n".join(line for _, line in run))
        links.extend(_links_in_text(masked, line_map))

    return links


BLOCK_START_RE = re.compile(
    r"""^[ ]{0,3}(?:
        \#{1,6}(?:\s|$)      # ATX heading
      | >                    # blockquote
      | (?:[-*+])\s          # bullet list
      | \d{1,9}[.)]\s        # ordered list
      | (?:`{3,}|~{3,})      # fence
      | (?:=+|-+)[ ]*$       # setext heading underline (any length, = or -)
      | (?:\*\s*){3,}$       # thematic break
      | (?:-\s*){3,}$
      | (?:_\s*){3,}$
    )""",
    re.VERBOSE,
)


def _starts_new_block(text: str, pos: int) -> bool:
    """True if the line beginning at pos starts a new Markdown block."""
    end = text.find("\n", pos)
    line = text[pos:] if end == -1 else text[pos:end]
    return bool(BLOCK_START_RE.match(line))


def _crosses_block_boundary(text: str) -> bool:
    """True if the text spans a blank line or a line that starts a new block.

    Applied to labels for the same reason it is applied to titles: a heading or
    list interrupts the paragraph, so `[text\n# heading](missing.md)` is prose
    plus a heading, not a link, and reporting its "target" fails a document
    that has nothing wrong with it.
    """
    if _crosses_blank_line(text):
        return True
    pos = text.find("\n")
    while pos != -1:
        if _starts_new_block(text, pos + 1):
            return True
        pos = text.find("\n", pos + 1)
    return False


def _crosses_blank_line(text: str) -> bool:
    """True if the text contains a blank line, which ends a Markdown block."""
    newlines = 0
    for ch in text:
        if ch == "\n":
            newlines += 1
            if newlines >= 2:
                return True
        elif not ch.isspace():
            newlines = 0
    return False


def _skip_link_whitespace(text: str, pos: int) -> int | None:
    """Advance past whitespace inside a link, refusing to cross a blank line.

    A blank line ends the Markdown block, so a "[" before it and a ")" after it
    are not parts of one link. Skipping newlines without bound makes ordinary
    prose parse as a multi-line link and reports a broken target that was never
    a link — `[a](` followed by a blank line and some text is not a link.
    """
    newlines = 0
    while pos < len(text) and text[pos] in " \t\n\r\f\v":
        if text[pos] == "\n":
            newlines += 1
            if newlines >= 2:
                return None
        pos += 1
    return pos


def _position_to_line(pos: int, line_map: list[tuple[int, int]]) -> int:
    """Map a character position in joined text to its source line number."""
    for i in range(len(line_map) - 1, -1, -1):
        offset, line_number = line_map[i]
        if pos >= offset:
            return line_number
    return line_map[0][1] if line_map else 1


def _links_in_text(
    text: str, line_map: list[tuple[int, int]]
) -> list[tuple[int, str]]:
    """Extract checkable relative links from already-masked text.

    Handles multi-line links by matching across the entire text and mapping
    match positions back to source line numbers.
    """
    links: list[tuple[int, str]] = []

    # Find inline/image links: ![label](destination) or [label](destination)
    #
    # Uses an explicit cursor rather than finditer. finditer resumes just after
    # the label's "](", so the destination and title it just consumed get
    # rescanned as Markdown: the title in
    # [outer](README.md "See [example](missing.md)") would yield a spurious
    # missing.md and fail a document that has no broken link at all.
    pos = 0
    while True:
        match = INLINE_LINK_RE.search(text, pos)
        if not match:
            break

        line_number = _position_to_line(match.start(), line_map)
        # Fail-safe cursor. Every rejection path below leaves `pos` here, just
        # inside the opening bracket, so a candidate that turns out not to be a
        # link can never carry the scan past text it did not consume. Advancing
        # to match.end() instead lets one piece of malformed prose swallow a
        # genuine broken link further along -- the parser goes quiet exactly
        # where it failed. Only an accepted link advances past itself.
        pos = match.start() + 1

        # The label is subject to the same blank-line rule as the destination
        # and title. Matching across a whole unfenced run means the pattern can
        # otherwise span paragraphs: `[text\n\n](missing.md)` is two blocks of
        # ordinary prose, not a link to a missing file.
        if _crosses_block_boundary(match.group(0)):
            continue

        start_pos = _skip_link_whitespace(text, match.end())
        if start_pos is None or start_pos >= len(text):
            continue

        result = _parse_angle_destination(text, start_pos)
        if not result:
            result = _parse_bare_destination(text, start_pos)
        if not result:
            continue
        target, end_pos = result

        after = _skip_link_whitespace(text, end_pos)
        if after is None:
            continue
        had_whitespace = after != end_pos
        end_pos = after

        # Optional title: "...", '...', or (...). CommonMark requires
        # whitespace between the destination and the title; without that check
        # `[a](<README.md>"...")` parses as a titled link and the scan jumps
        # past a real link nested in that text.
        if end_pos < len(text) and text[end_pos] in "\"'(" and had_whitespace:
            close = {'"': '"', "'": "'", "(": ")"}[text[end_pos]]
            end_pos += 1
            # A title cannot span a blank line. Letting it run past one lets
            # malformed prose swallow whatever follows -- including a real
            # broken link, which the checker would then never report. A false
            # negative here is worse than a false positive: the gate goes
            # quiet exactly when it has stopped looking.
            blank_run = 0
            invalid_title = False
            while end_pos < len(text) and text[end_pos] != close:
                ch = text[end_pos]
                # A backslash escapes only ASCII punctuation. Letting it
                # consume a newline hides that newline from blank-line
                # detection, so a malformed title runs on and swallows any
                # real link inside it.
                if (
                    ch == "\\"
                    and end_pos + 1 < len(text)
                    and text[end_pos + 1] in ASCII_PUNCTUATION
                ):
                    end_pos += 2
                    blank_run = 0
                    continue
                # CommonMark forbids an unescaped "(" inside a (...) title, so
                # the whole construct is not a link. Accepting it would skip
                # past a real link nested in that text and never report it.
                if ch == "(" and close == ")":
                    invalid_title = True
                    break
                if ch == "\n":
                    blank_run += 1
                    if blank_run >= 2:
                        break
                    # A heading, list item, blockquote or fence interrupts the
                    # paragraph, so the title ended at the previous line and
                    # anything after it -- including a real link -- is not part
                    # of this construct.
                    if _starts_new_block(text, end_pos + 1):
                        invalid_title = True
                        break
                elif not ch.isspace():
                    blank_run = 0
                end_pos += 1
            if invalid_title or end_pos >= len(text) or text[end_pos] != close:
                continue
            end_pos += 1
            after = _skip_link_whitespace(text, end_pos)
            if after is None:
                continue
            end_pos = after

        if end_pos < len(text) and text[end_pos] == ")":
            # Resume after the whole link so its own title is never rescanned.
            pos = end_pos + 1
            target = clean_destination(target)
            if target and not target.startswith(SKIPPED_SCHEMES):
                links.append((line_number, target))

    # Find reference-style links: [label]: destination
    for line_start, line_number in line_map:
        # Find the line end
        line_end = text.find("\n", line_start)
        if line_end == -1:
            line_end = len(text)

        line_text = text[line_start:line_end]
        reference = REFERENCE_LINK_RE.match(line_text)
        if reference:
            target = clean_destination(reference.group(1))
            if target and not target.startswith(SKIPPED_SCHEMES):
                links.append((line_number, target))

    return links


IGNORED_DIRS = {".git", ".worktrees", ".superpowers", "__pycache__", ".venv"}


def tracked_markdown() -> tuple[list[Path], str]:
    """Enumerate Markdown to check, preferring git so ignored scratch is excluded.

    Falls back to a filesystem walk when git is unavailable. The downstream
    distribution is staged as a plain directory before it is committed into its
    clone, and `git ls-files` exits 128 there; failing hard would break the
    published `just lint` for a reason that has nothing to do with links.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        paths = [ROOT / line for line in result.stdout.splitlines() if line]
        if paths:
            return paths, "tracked"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    walked = [
        path
        for path in sorted(ROOT.rglob("*.md"))
        if not IGNORED_DIRS.intersection(path.relative_to(ROOT).parts)
    ]
    return walked, "discovered"


def main() -> int:
    tracked_files, discovery = tracked_markdown()

    if not tracked_files:
        print("ERROR: no Markdown files found to check")
        return 1

    errors: list[str] = []
    checked = 0

    for md_file in tracked_files:
        if not md_file.is_file():
            continue

        for line_number, target in extract_links(md_file.read_text(encoding="utf-8")):
            # Strip fragment (#...) and query string (?...) before resolution.
            # Query strings and fragments are used by browsers/renderers but don't
            # affect filesystem paths. A literal ? in a filename is rare; if needed,
            # it should be percent-encoded in the link.
            target_path = target
            # Strip fragment first
            if "#" in target_path:
                target_path = target_path.split("#", 1)[0]
            # Strip query string
            if "?" in target_path:
                target_path = target_path.split("?", 1)[0]
            # URL-decode
            target_path = unquote(target_path)

            if not target_path:
                continue

            checked += 1
            if not (md_file.parent / target_path).resolve().exists():
                relative = md_file.relative_to(ROOT)
                errors.append(f"{relative}:{line_number}: broken link -> {target}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    print(
        f"OK: {checked} relative links resolve across "
        f"{len(tracked_files)} {discovery} Markdown files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
