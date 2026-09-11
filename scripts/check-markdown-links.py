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
INLINE_LINK_RE = re.compile(
    r"""!?\[(?:[^\]\\]|\\.)*\]\(\s*
        (<[^<>\n]*>|[^\s()]*)
        (?:\s+(?:"[^"]*"|'[^']*'|\([^()]*\)))?
        \s*\)""",
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


def mask_code_spans(text: str) -> str:
    """Blank out inline code spans, preserving newlines so line numbers hold.

    A target inside backticks is being displayed, not linked.
    """
    return CODE_SPAN_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def clean_destination(target: str) -> str:
    """Strip Markdown destination delimiters from a captured link target."""
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
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
        # Mask each unfenced run as one block so a code span may cross lines
        # without ever seeing a fence marker.
        masked = mask_code_spans("\n".join(line for _, line in run)).splitlines()
        for (line_number, _), text in zip(run, masked):
            links.extend(_links_in_line(line_number, text))

    return links


def _links_in_line(line_number: int, raw_line: str) -> list[tuple[int, str]]:
    """Extract checkable relative links from one already-masked line."""
    links: list[tuple[int, str]] = []

    for match in INLINE_LINK_RE.finditer(raw_line):
        target = clean_destination(match.group(1))
        if target and not target.startswith(SKIPPED_SCHEMES):
            links.append((line_number, target))

    reference = REFERENCE_LINK_RE.match(raw_line)
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
            target_path = unquote(target.split("#", 1)[0])
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
