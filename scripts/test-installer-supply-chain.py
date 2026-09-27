#!/usr/bin/env python3
"""Regression tests for install.sh's checksum manifest and pinned-ref checks.

Builds a disposable copy of install.sh plus one real skill under a temp
"repo" root (never the real skills/ checkout) so tests can tamper with
files and pass bogus --ref values without touching this repository.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "install.sh"
GEN_CHECKSUMS = ROOT / "scripts" / "gen-checksums.py"
SKILL_NAME = "srx-policy"


class SupplyChainInstallTests(unittest.TestCase):
    def _build_fake_repo(self, tmp: Path) -> Path:
        repo = tmp / "repo"
        repo.mkdir()
        installer = repo / "install.sh"
        shutil.copy2(INSTALL_SH, installer)
        installer.chmod(0o755)

        skills_dir = repo / "skills"
        skills_dir.mkdir()
        shutil.copytree(ROOT / "skills" / SKILL_NAME, skills_dir / SKILL_NAME)

        subprocess.run(
            ["python3", str(GEN_CHECKSUMS), "--skills-dir", str(skills_dir)],
            check=True,
            capture_output=True,
        )
        return repo

    def _run_install(self, repo: Path, dest: Path, *extra_args: str):
        return subprocess.run(
            ["./install.sh", "--skill", SKILL_NAME, "--dir", str(dest), "-y", *extra_args],
            cwd=repo,
            capture_output=True,
            text=True,
        )

    def test_untampered_payload_installs_after_checksum_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            dest = tmp_path / "dest"

            result = self._run_install(repo, dest)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("matched the checksum manifest", result.stdout)
            self.assertTrue((dest / SKILL_NAME / "SKILL.md").is_file())

    def test_tampered_skill_file_fails_checksum_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            skill_md = repo / "skills" / SKILL_NAME / "SKILL.md"
            skill_md.write_bytes(skill_md.read_bytes() + b"\ntampered\n")
            dest = tmp_path / "dest"

            result = self._run_install(repo, dest)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("checksum mismatch", result.stderr)
            self.assertFalse(dest.exists() and any(dest.iterdir()))

    def test_missing_manifest_refuses_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            (repo / "skills" / "CHECKSUMS.sha256").unlink()
            dest = tmp_path / "dest"

            result = self._run_install(repo, dest)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no checksum manifest", result.stderr)
            self.assertFalse(dest.exists() and any(dest.iterdir()))

    def test_moving_ref_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            dest = tmp_path / "dest"

            for moving_ref in ("main", "HEAD", "master"):
                with self.subTest(ref=moving_ref):
                    result = self._run_install(repo, dest, "--ref", moving_ref)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("moving ref", result.stderr)
                    self.assertFalse(dest.exists() and any(dest.iterdir()))

    def test_pinned_tag_ref_is_accepted_by_validation(self) -> None:
        # This only exercises argument validation: the fake repo has a local
        # skills/ directory, so find_skills_source() never reaches the
        # network. A real download is covered by manual verification against
        # GitHub, not by this offline test suite.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            dest = tmp_path / "dest"

            result = self._run_install(repo, dest, "--ref", "v1.7.0")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest / SKILL_NAME / "SKILL.md").is_file())

    def test_require_signature_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = self._build_fake_repo(tmp_path)
            dest = tmp_path / "dest"

            env_result = subprocess.run(
                ["./install.sh", "--skill", SKILL_NAME, "--dir", str(dest), "-y"],
                cwd=repo,
                capture_output=True,
                text=True,
                env={**os.environ, "FWSKILLS_REQUIRE_SIGNATURE": "1"},
            )

            self.assertNotEqual(env_result.returncode, 0)
            self.assertIn("signature verification is not implemented", env_result.stderr)
            self.assertFalse(dest.exists() and any(dest.iterdir()))


if __name__ == "__main__":
    unittest.main()
