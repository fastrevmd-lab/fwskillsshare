#!/usr/bin/env python3
"""Regression test: the Codex review gate must not run without explicit opt-in.

scripts/codex-review.sh sends the diff being reviewed to OpenAI's Codex
service. It must refuse to run -- before doing anything else, including
touching the superpowers symlink or invoking `codex` -- unless
FWSKILLS_ALLOW_CODEX_REVIEW=1 is set.
"""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "codex-review.sh"


class CodexReviewOptInTests(unittest.TestCase):
    def _run(self, env_overrides: dict[str, str]):
        env = {k: v for k, v in os.environ.items() if k != "FWSKILLS_ALLOW_CODEX_REVIEW"}
        env.update(env_overrides)
        return subprocess.run(
            [str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_refuses_by_default(self) -> None:
        result = self._run({})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("off-box", result.stderr)
        self.assertIn("FWSKILLS_ALLOW_CODEX_REVIEW", result.stderr)

    def test_refuses_when_opt_in_is_not_exactly_one(self) -> None:
        for bogus in ("0", "true", "yes", ""):
            with self.subTest(value=bogus):
                result = self._run({"FWSKILLS_ALLOW_CODEX_REVIEW": bogus})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("off-box", result.stderr)


if __name__ == "__main__":
    unittest.main()
