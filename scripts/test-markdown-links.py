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


class BalancedParensTests(unittest.TestCase):
    """Gap 1: balanced parentheses in destinations."""

    def test_balanced_parens_in_destination(self) -> None:
        self.assertEqual(targets("[a](file(1).md)\n"), ["file(1).md"])

    def test_nested_balanced_parens(self) -> None:
        self.assertEqual(targets("[a](dir(a)/file(b).md)\n"), ["dir(a)/file(b).md"])

    def test_escaped_parens_in_destination(self) -> None:
        # Backslash escapes are removed by clean_destination
        self.assertEqual(targets(r"[a](file\(1\).md)" + "\n"), ["file(1).md"])

    def test_escaped_underscore(self) -> None:
        # Test another escape: underscore
        self.assertEqual(targets(r"[a](we\_ird.md)" + "\n"), ["we_ird.md"])

    def test_unbalanced_parens_stop_at_closing(self) -> None:
        # A bare ) not matched by ( closes the link
        self.assertEqual(targets("[a](file).md)\n"), ["file"])

    def test_balanced_parens_inside_fence_are_skipped(self) -> None:
        self.assertEqual(targets("```\n[a](file(1).md)\n```\n"), [])


class QueryStringTests(unittest.TestCase):
    """Gap 2: query strings are stripped during resolution."""

    def test_query_string_is_preserved_in_extraction(self) -> None:
        # Extraction preserves the query; stripping happens in main()
        self.assertEqual(targets("[a](README.md?raw=1)\n"), ["README.md?raw=1"])

    def test_fragment_is_preserved_in_extraction(self) -> None:
        # Fragments are also preserved during extraction
        self.assertEqual(targets("[a](README.md#section)\n"), ["README.md#section"])

    def test_query_and_fragment_both_preserved(self) -> None:
        self.assertEqual(
            targets("[a](README.md?raw=1#section)\n"), ["README.md?raw=1#section"]
        )

    def test_query_inside_fence_is_skipped(self) -> None:
        self.assertEqual(targets("```\n[a](README.md?raw=1)\n```\n"), [])


class MultiLineTests(unittest.TestCase):
    """Gap 3: links whose destinations span multiple lines."""

    def test_destination_on_next_line(self) -> None:
        self.assertEqual(targets("[a](\nREADME.md\n)"), ["README.md"])

    def test_destination_with_leading_whitespace(self) -> None:
        self.assertEqual(targets("[a](\n  README.md\n)"), ["README.md"])

    def test_multiline_with_title(self) -> None:
        self.assertEqual(targets('[a](\nREADME.md\n"title"\n)'), ["README.md"])

    def test_multiline_reports_label_line_number(self) -> None:
        # Multi-line link should report the line where [label] starts
        markdown = "intro\n[a](\nREADME.md\n)\n"
        self.assertEqual(checker.extract_links(markdown), [(2, "README.md")])

    def test_multiline_inside_fence_is_skipped(self) -> None:
        self.assertEqual(targets("```\n[a](\nREADME.md\n)\n```\n"), [])

    def test_multiline_with_balanced_parens(self) -> None:
        # Combining gap 1 and gap 3
        self.assertEqual(targets("[a](\nfile(1).md\n)"), ["file(1).md"])


class ExtractionBoundaryTests(unittest.TestCase):
    """A link's own title and a blank line are both hard boundaries."""

    def test_title_containing_a_link_is_not_rescanned(self) -> None:
        """finditer resuming after "](" would parse the title as Markdown."""
        markdown = '[outer](README.md "See [example](missing.md)")\n'
        self.assertEqual(targets(markdown), ["README.md"])

    def test_parenthesised_title_with_unescaped_paren_is_not_a_link(self) -> None:
        """CommonMark forbids an unescaped ( in a (...) title.

        The outer construct is therefore not a link, and the inner one must
        still be checked -- accepting it would skip a real broken link.
        """
        markdown = "[outer](README.md (see [x](missing.md)))\n"
        self.assertIn("missing.md", targets(markdown))

    def test_blank_line_between_label_and_destination_is_not_a_link(self) -> None:
        """A blank line ends the block, so these brackets are ordinary text."""
        self.assertEqual(targets("[a](\n\nmissing.md\n)\n"), [])

    def test_blank_line_before_closing_paren_is_not_a_link(self) -> None:
        self.assertEqual(targets("[a](\nmissing.md\n\n)\n"), [])

    def test_single_line_break_link_still_resolves(self) -> None:
        self.assertEqual(targets("[a](\nreal.md\n)\n"), ["real.md"])

    def test_two_links_on_one_line_are_both_found(self) -> None:
        self.assertEqual(targets("[a](x.md) and [b](y.md)\n"), ["x.md", "y.md"])


class MalformedDestinationTests(unittest.TestCase):
    """Malformed Markdown must not become a link, nor hide one."""

    def test_title_may_not_span_a_blank_line(self) -> None:
        """A runaway title would swallow a real link and silence the gate."""
        markdown = '[a](README.md "title\n\n[real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_unmatched_open_paren_is_not_a_destination(self) -> None:
        self.assertEqual(targets("[a](missing( )\n"), [])

    def test_backslash_does_not_escape_whitespace(self) -> None:
        """CommonMark allows escapes only before ASCII punctuation."""
        self.assertEqual(targets("[a](missing\\ file.md)\n"), [])

    def test_escapes_before_punctuation_still_work(self) -> None:
        self.assertEqual(targets("[a](x\\(1\\).md)\n"), ["x(1).md"])
        self.assertEqual(targets("[a](we\\_ird.md)\n"), ["we_ird.md"])

    def test_balanced_parens_still_accepted(self) -> None:
        self.assertEqual(targets("[a](x(1).md)\n"), ["x(1).md"])


class BlankLineBoundaryTests(unittest.TestCase):
    """A blank line ends a Markdown block, for every part of a link."""

    def test_label_may_not_span_a_blank_line(self) -> None:
        self.assertEqual(targets("[text\n\n](missing.md)\n"), [])

    def test_destination_may_not_span_a_blank_line(self) -> None:
        self.assertEqual(targets("[a](\n\nmissing.md\n)\n"), [])

    def test_title_may_not_span_a_blank_line_and_must_not_hide_a_link(self) -> None:
        markdown = '[a](README.md "t\n\n[r](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_valid_single_break_link_survives_all_three_rules(self) -> None:
        self.assertEqual(targets("[a](\nreal.md\n)\n"), ["real.md"])


class FailSafeCursorTests(unittest.TestCase):
    """A rejected candidate must never hide a link that follows it.

    These all share one root cause: the scan advancing past text it did not
    actually consume. Each was a real hidden broken link before the cursor was
    made fail-safe.
    """

    def test_rejected_label_does_not_swallow_a_later_link(self) -> None:
        self.assertEqual(
            targets("[unfinished\n\n[broken](missing.md)\n"), ["missing.md"]
        )

    def test_backslash_in_title_cannot_consume_a_newline(self) -> None:
        markdown = '[a](README.md "t\\\n\n[real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_title_requires_whitespace_after_the_destination(self) -> None:
        markdown = '[a](<README.md>"See [real](missing.md)")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_unclosed_bracket_does_not_hide_following_links(self) -> None:
        self.assertEqual(targets("[oops [a](x.md)\n"), ["x.md"])


class ConservativeAcceptanceTests(unittest.TestCase):
    """Accepting malformed input is as dangerous as rejecting valid input.

    The fail-safe cursor protects rejections. These cover the other half:
    constructs the parser must refuse to accept, because accepting them
    advances past a genuine link and leaves the gate green.
    """

    def test_bare_destination_rejects_angle_brackets(self) -> None:
        markdown = "[outer](<bad<[real](missing.md)>)\n"
        self.assertIn("missing.md", targets(markdown))

    def test_atx_heading_interrupts_a_title(self) -> None:
        markdown = '[a](README.md "title\n# [real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_list_item_interrupts_a_title(self) -> None:
        markdown = '[a](README.md "t\n- [real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_blockquote_interrupts_a_title(self) -> None:
        markdown = '[a](README.md "t\n> [real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_ordinary_headings_and_lists_still_carry_links(self) -> None:
        self.assertEqual(targets("# Title\n\n[a](x.md)\n"), ["x.md"])
        self.assertEqual(targets("- item [a](x.md)\n"), ["x.md"])


class BlockBoundaryTests(unittest.TestCase):
    """Labels and titles both end where a new Markdown block begins."""

    def test_setext_underline_interrupts_a_title(self) -> None:
        markdown = '[a](README.md "title\n===\n[real](missing.md)\n")\n'
        self.assertIn("missing.md", targets(markdown))

    def test_short_setext_underlines_of_either_kind_interrupt_a_title(self) -> None:
        """A setext underline is one-or-more = or -, not three-or-more."""
        for underline in ("=", "==", "-", "--", "---"):
            markdown = f'[a](README.md "t\n{underline}\n[real](missing.md)\n")\n'
            self.assertIn("missing.md", targets(markdown), underline)

    def test_label_may_not_cross_a_block_boundary(self) -> None:
        """Prose plus a heading is not a link; reporting one fails a good doc."""
        self.assertEqual(targets("[text\n# heading](missing.md)\n"), [])

    def test_setext_document_still_carries_links(self) -> None:
        self.assertEqual(targets("Title\n===\n\n[a](x.md)\n"), ["x.md"])


if __name__ == "__main__":
    unittest.main()
