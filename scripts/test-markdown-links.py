#!/usr/bin/env python3
"""Unit tests for the Markdown link checker's extraction rules."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_markdown_links", ROOT / "scripts" / "check-markdown-links.py"
)
checker = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(checker)


def targets(markdown: str) -> list[str]:
    return [target for _, target in checker.extract_links(markdown)]


class ExtractionTests(unittest.TestCase):
    def test_plain_relative_link_is_checked(self) -> None:
        self.assertEqual(targets("[a](x.md)\n"), ["x.md"])

    def test_absolute_urls_are_skipped(self) -> None:
        self.assertEqual(targets("[a](https://example.com)\n"), [])

    def test_image_and_reference_links_are_checked(self) -> None:
        self.assertEqual(targets("![i](img.png)\n"), ["img.png"])
        self.assertEqual(targets("[lbl]: target.md\n"), ["target.md"])

    def test_fenced_links_are_skipped(self) -> None:
        self.assertEqual(targets("```markdown\n[a](x.md)\n```\n"), [])

    def test_inline_code_span_is_skipped(self) -> None:
        self.assertEqual(targets("see `[a](x.md)` ok\n"), [])


class FenceLengthTests(unittest.TestCase):
    """A shorter fence must not close a longer one."""

    def test_nested_shorter_fence_does_not_close_outer_block(self) -> None:
        markdown = (
            "````markdown\n[a](x.md)\n```json\n[b](y.md)\n```\n[c](z.md)\n````\n"
            "[real](out.md)\n"
        )
        self.assertEqual(targets(markdown), ["out.md"])

    def test_tilde_does_not_close_backtick_fence(self) -> None:
        self.assertEqual(
            targets("```\n[a](x.md)\n~~~\n[b](y.md)\n```\n[real](out.md)\n"),
            ["out.md"],
        )

    def test_longer_closing_fence_closes_shorter_opening(self) -> None:
        self.assertEqual(targets("```\n[a](x.md)\n````\n[real](out.md)\n"), ["out.md"])

    def test_fence_markers_survive_code_span_masking(self) -> None:
        """Masking spans before fences would pair ``` with ``` and expose links."""
        markdown = "intro `tick`\n\n```markdown\n[a](nope.md)\n```\n\n[real](out.md)\n"
        self.assertEqual(targets(markdown), ["out.md"])


class DestinationTests(unittest.TestCase):
    """Titles and angle brackets are not part of the filename."""

    def test_double_quoted_title_is_not_part_of_target(self) -> None:
        self.assertEqual(targets('[a](README.md "Overview")\n'), ["README.md"])

    def test_single_quoted_title_is_not_part_of_target(self) -> None:
        self.assertEqual(targets("[a](README.md 'Overview')\n"), ["README.md"])

    def test_parenthesised_title_is_not_part_of_target(self) -> None:
        self.assertEqual(targets("[a](README.md (Overview))\n"), ["README.md"])

    def test_angle_brackets_are_stripped(self) -> None:
        self.assertEqual(targets("[a](<README.md>)\n"), ["README.md"])
        self.assertEqual(targets('[a](<R E.md> "t")\n'), ["R E.md"])


class CodeSpanTests(unittest.TestCase):
    """Backtick runs pair only with runs of equal length."""

    def test_double_backtick_span_is_skipped(self) -> None:
        self.assertEqual(targets("``[a](x.md)`` and ` tick\n"), [])

    def test_multiline_span_is_skipped(self) -> None:
        self.assertEqual(targets("``\n[a](x.md)\n``\n[real](out.md)\n"), ["out.md"])

    def test_triple_backtick_span_at_line_start_is_not_a_fence(self) -> None:
        """```x``` opens a code span, not a fence; the rest of the line still counts."""
        self.assertEqual(targets("```label``` and [real](out.md)\n"), ["out.md"])

    def test_rejected_fence_line_still_yields_its_links(self) -> None:
        markdown = "```a``` [one](x.md)\n\n```\n[hidden](y.md)\n```\n[two](z.md)\n"
        self.assertEqual(targets(markdown), ["x.md", "z.md"])

    def test_lone_backtick_does_not_open_a_span(self) -> None:
        self.assertEqual(targets("a ` b\n[real](out.md)\n"), ["out.md"])


class LineNumberTests(unittest.TestCase):
    def test_line_numbers_survive_masking(self) -> None:
        markdown = "\n\n`span`\n\n[a](x.md)\n"
        self.assertEqual(checker.extract_links(markdown), [(5, "x.md")])


if __name__ == "__main__":
    unittest.main()
