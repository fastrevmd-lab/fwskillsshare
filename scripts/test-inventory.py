#!/usr/bin/env python3
"""Unit tests for the inventory manifest checker.

Every negative case drives the real `main()` against a disposable tree and
asserts on its exit status and diagnostics. Re-implementing the detection
logic inside a test proves only that the test can count; it passes just as
happily when the production rejection branch is deleted.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_inventory", ROOT / "scripts" / "check-inventory.py"
)
checker = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(checker)

REAL_MANIFEST = json.loads((ROOT / "skills" / "inventory.json").read_text(encoding="utf-8"))


def run_checker(manifest: list[dict[str, object]]) -> tuple[int, str]:
    """Run the checker against a manifest written to a disposable directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_path = Path(tmpdir) / "inventory.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        original = checker.MANIFEST
        buffer = io.StringIO()
        try:
            checker.MANIFEST = manifest_path
            with contextlib.redirect_stdout(buffer):
                status = checker.main()
        finally:
            checker.MANIFEST = original
        return status, buffer.getvalue()


class RealManifestTests(unittest.TestCase):
    def test_repository_manifest_passes(self) -> None:
        status, output = run_checker(REAL_MANIFEST)
        self.assertEqual(status, 0, output)
        self.assertIn("OK:", output)


class RejectionTests(unittest.TestCase):
    """Each mutation must be rejected by the checker itself."""

    def test_duplicate_entry_is_rejected(self) -> None:
        manifest = [dict(entry) for entry in REAL_MANIFEST]
        manifest.append(dict(manifest[0]))
        status, output = run_checker(manifest)
        self.assertEqual(status, 1)
        self.assertIn("duplicate manifest entry", output)
        self.assertIn(str(manifest[0]["name"]), output)

    def test_missing_skill_is_rejected(self) -> None:
        manifest = [dict(entry) for entry in REAL_MANIFEST][1:]
        status, output = run_checker(manifest)
        self.assertEqual(status, 1)
        self.assertIn(str(REAL_MANIFEST[0]["name"]), output)

    def test_extra_skill_is_rejected(self) -> None:
        manifest = [dict(entry) for entry in REAL_MANIFEST]
        manifest.append({"name": "not-a-real-skill", "family": "tooling", "reviewed": True})
        status, output = run_checker(manifest)
        self.assertEqual(status, 1)
        self.assertIn("not-a-real-skill", output)

    def test_wrong_family_is_rejected(self) -> None:
        manifest = [dict(entry) for entry in REAL_MANIFEST]
        for entry in manifest:
            if entry["name"] == "parsing-cisco-configs":
                entry["family"] = "srx"
                break
        status, output = run_checker(manifest)
        self.assertEqual(status, 1)
        self.assertIn("mismatch", output)

    def test_wrong_reviewed_count_is_rejected(self) -> None:
        manifest = [dict(entry) for entry in REAL_MANIFEST]
        for entry in manifest:
            if entry["reviewed"]:
                entry["reviewed"] = False
                break
        status, output = run_checker(manifest)
        self.assertEqual(status, 1)
        self.assertIn("reviewed count", output)




class ReadmeCountTests(unittest.TestCase):
    """The body counts are required; the review badge is upstream-only.

    The downstream distribution replaces the README header with a neutral one
    that carries skills, license and vendor badges but deliberately no
    reviewed badge. This test ships downstream too, so asserting the badge
    exists would fail there and take `just test`, `guard` and `release-check`
    with it. The checker already treats an absent badge as "nothing to
    compare"; this mirrors that, while still pinning the badge and the body to
    each other wherever both are present.
    """

    def test_body_counts_are_present(self) -> None:
        _, _, body_reviewed, body_total = checker.get_readme_reviewed_count()
        self.assertIsNotNone(body_reviewed)
        self.assertIsNotNone(body_total)

    def test_badge_agrees_with_body_when_the_badge_exists(self) -> None:
        badge_reviewed, badge_total, body_reviewed, body_total = (
            checker.get_readme_reviewed_count()
        )
        if badge_reviewed is None and badge_total is None:
            self.skipTest("no review badge in this README (downstream distribution)")
        self.assertEqual(badge_total, body_total)
        self.assertEqual(badge_reviewed, body_reviewed)


if __name__ == "__main__":
    unittest.main()
