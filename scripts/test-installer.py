#!/usr/bin/env python3
"""Regression tests for installed artifact integrity checks."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-installer.py"
SPEC = importlib.util.spec_from_file_location("installer_checker", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import installer checker from {CHECKER_PATH}")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class InstallerArtifactTests(unittest.TestCase):
    SKILL_NAME = "srx-policy"

    def copy_installed_skill(self, destination: Path) -> Path:
        installed = destination / self.SKILL_NAME
        shutil.copytree(ROOT / "skills" / self.SKILL_NAME, installed)
        return installed

    def test_exact_required_artifacts_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp)
            self.copy_installed_skill(destination)

            CHECKER.assert_installed_artifacts(
                destination,
                {self.SKILL_NAME},
                "exact-copy probe",
            )

    def test_required_artifact_byte_mutations_are_rejected(self) -> None:
        required_paths = (
            Path("SKILL.md"),
            Path("references/runtime-intake.md"),
            Path("agents/openai.yaml"),
        )
        for relative_path in required_paths:
            with self.subTest(path=relative_path):
                with tempfile.TemporaryDirectory() as temp:
                    destination = Path(temp)
                    installed = self.copy_installed_skill(destination)
                    artifact = installed / relative_path
                    artifact.write_bytes(artifact.read_bytes() + b"\nmutation\n")

                    with self.assertRaisesRegex(
                        SystemExit,
                        rf"content mismatch.*{relative_path}",
                    ):
                        CHECKER.assert_installed_artifacts(
                            destination,
                            {self.SKILL_NAME},
                            "mutation probe",
                        )


if __name__ == "__main__":
    unittest.main()
