#!/usr/bin/env python3
"""Test the Codex review gate's verdict detection and error handling.

The wrapper must detect and fail on:
1. Non-zero exit from codex (timeout, auth failure, etc.)
2. Error events in JSONL (usage limit, turn.failed)
3. "Review was interrupted" message
4. Missing verdict

It must pass only when a clean verdict is produced with no [P0]/[P1] findings.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "codex-review.sh"


class CodexReviewVerdictTests(unittest.TestCase):
    """Test verdict detection against canned JSONL from a fake codex executable."""

    def setUp(self) -> None:
        # Isolated environment: temp HOME, temp CODEX_SKILLS_DIR (so the real
        # ~/.agents/skills/superpowers symlink is never touched), and a fake
        # codex executable placed first on PATH.
        self.temp_home = tempfile.TemporaryDirectory()
        self.temp_skills = tempfile.TemporaryDirectory()
        self.temp_bin = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_home.cleanup)
        self.addCleanup(self.temp_skills.cleanup)
        self.addCleanup(self.temp_bin.cleanup)

        self.fake_codex = Path(self.temp_bin.name) / "codex"
        self.fake_codex.touch(mode=0o755)

        # Store real superpowers link state to verify it's unchanged after the run.
        self.real_link = Path.home() / ".agents" / "skills" / "superpowers"
        self.real_link_before = (
            self.real_link.resolve() if self.real_link.exists() else None
        )

    def tearDown(self) -> None:
        # Verify the real superpowers link state is unchanged.
        real_link_after = (
            self.real_link.resolve() if self.real_link.exists() else None
        )
        self.assertEqual(
            self.real_link_before,
            real_link_after,
            f"real superpowers link state changed: {self.real_link_before} -> {real_link_after}",
        )

    def _write_fake_codex(self, script: str) -> None:
        """Write a fake codex executable that emits canned JSONL."""
        self.fake_codex.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                {script}
                """
            )
        )

    def _run_gate(self, commit_sha: str = "HEAD") -> subprocess.CompletedProcess:
        """Run the gate wrapper in isolated mode against a fake codex."""
        env = os.environ.copy()
        env.update(
            {
                "FWSKILLS_ALLOW_CODEX_REVIEW": "1",
                "CODEX_SKILLS_DIR": self.temp_skills.name,
                "HOME": self.temp_home.name,
                "PATH": f"{self.temp_bin.name}:{env['PATH']}",
            }
        )
        return subprocess.run(
            [str(SCRIPT), commit_sha],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_usage_limit_error_event_fails(self) -> None:
        """Usage-limit error event => GATE DID NOT RUN, exit != 0."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"error","message":"You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at 7:42 PM."}
                {"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"Review was interrupted. Please re-run /review and wait for it to complete."}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE DID NOT RUN", result.stderr)
        self.assertIn("error events present", result.stderr)
        self.assertIn("usage limit", result.stderr.lower())
        self.assertIn("quota exhausted", result.stderr)

    def test_turn_failed_event_fails(self) -> None:
        """turn.failed event => GATE DID NOT RUN, exit != 0."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"turn.failed","error":{"message":"Internal server error (code: 500)"}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE DID NOT RUN", result.stderr)
        self.assertIn("error events present", result.stderr)
        self.assertIn("Internal server error", result.stderr)

    def test_interrupted_message_fails(self) -> None:
        """'Review was interrupted' verdict => GATE DID NOT RUN, exit != 0."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"Review was interrupted. Please re-run /review and wait for it to complete."}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE DID NOT RUN", result.stderr)
        self.assertIn("review was interrupted", result.stderr.lower())

    def test_codex_nonzero_exit_fails(self) -> None:
        """codex exits non-zero => GATE DID NOT RUN, exit != 0."""
        self._write_fake_codex("exit 1")
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE DID NOT RUN", result.stderr)
        self.assertIn("codex exited 1", result.stderr)

    def test_no_verdict_fails(self) -> None:
        """No final agent_message => GATE DID NOT RUN, exit != 0."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"turn.started"}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE DID NOT RUN", result.stderr)
        self.assertIn("no final agent_message", result.stderr)

    def test_clean_verdict_no_findings_passes(self) -> None:
        """Clean verdict with no [P0]/[P1] => exit 0."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"No actionable regressions were found. The change is safe to merge."}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertEqual(result.returncode, 0)
        self.assertIn("No [P0]/[P1] findings", result.stderr)
        self.assertIn("No actionable regressions", result.stdout)

    def test_verdict_with_p1_finding_fails(self) -> None:
        """Verdict containing [P1] => BLOCKING, exit 1."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"[P1] The function does not validate input. Fix before merging."}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BLOCKING", result.stderr)
        self.assertIn("[P1]", result.stdout)

    def test_verdict_with_p0_finding_fails(self) -> None:
        """Verdict containing [P0] => BLOCKING, exit 1."""
        self._write_fake_codex(
            textwrap.dedent(
                """\
                cat <<'EOF'
                {"type":"thread.started"}
                {"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"[P0] Critical security vulnerability in authentication. Do not merge."}}
                EOF
                """
            )
        )
        result = self._run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("BLOCKING", result.stderr)
        self.assertIn("[P0]", result.stdout)


if __name__ == "__main__":
    unittest.main()
