#!/usr/bin/env python3
"""Unit tests for the skill packages checker.

Tests the YAML frontmatter validation that catches plain-scalar hazards
such as unquoted colons and comment markers.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_skill_packages", ROOT / "scripts" / "check-skill-packages.py"
)
checker = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(checker)

# Minimal valid skill for testing
MINIMAL_VALID_SKILL = """---
name: test-skill
description: A minimal test skill for validation. Use when testing the checker.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill

This is a test skill.
"""

OPENAI_YAML = """display_name: "Test Skill"
short_description: "A minimal test skill for validation"
default_prompt: "Help me with $test-skill"
"""


def create_test_skill(
    tmpdir: Path, name: str, frontmatter: str, inventory: list[dict[str, str]]
) -> None:
    """Create a minimal test skill with given frontmatter."""
    skill_dir = tmpdir / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(frontmatter, encoding="utf-8")

    # Create agents/openai.yaml
    agents_dir = skill_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "openai.yaml").write_text(OPENAI_YAML, encoding="utf-8")

    # Create inventory.json
    (tmpdir / "skills" / "inventory.json").write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )


def run_checker(tmpdir: Path) -> tuple[int, list[str]]:
    """Run the checker against a disposable skill tree."""
    original_root = checker.ROOT
    original_skills = checker.SKILLS_DIR
    original_manifest = checker.MANIFEST

    try:
        checker.ROOT = tmpdir
        checker.SKILLS_DIR = tmpdir / "skills"
        checker.MANIFEST = tmpdir / "skills" / "inventory.json"

        # Capture errors by monkey-patching the errors list
        errors: list[str] = []
        original_main = checker.main

        def patched_main() -> int:
            nonlocal errors
            # Run the real main and capture its error output
            import sys
            import io
            import contextlib

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = original_main()

            # Extract error messages
            output = stderr.getvalue()
            errors = [line.removeprefix("ERROR: ") for line in output.splitlines() if line.startswith("ERROR:")]
            return status

        status = patched_main()
        return status, errors

    finally:
        checker.ROOT = original_root
        checker.SKILLS_DIR = original_skills
        checker.MANIFEST = original_manifest


class YAMLValidationTests(unittest.TestCase):
    """Test YAML frontmatter validation."""

    def test_valid_frontmatter_passes(self) -> None:
        """A normal skill with no YAML hazards should pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                MINIMAL_VALID_SKILL,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            # Filter out errors not related to YAML validation
            yaml_errors = [e for e in errors if "contains" in e or "starts with" in e]
            self.assertEqual(yaml_errors, [], "Valid frontmatter should not have YAML errors")

    def test_unquoted_colon_space_is_rejected(self) -> None:
        """Frontmatter with ': ' in an unquoted value should fail."""
        frontmatter = """---
name: test-skill
description: Build from nodes over a server: routing mode and more. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            self.assertNotEqual(status, 0, "Should fail validation")
            yaml_errors = [e for e in errors if "contains ': '" in e]
            self.assertTrue(len(yaml_errors) > 0, f"Should have YAML colon error. Errors: {errors}")

    def test_unquoted_space_hash_is_rejected(self) -> None:
        """Frontmatter with ' #' in an unquoted value should fail."""
        frontmatter = """---
name: test-skill
description: A test skill with a #hashtag in it. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            self.assertNotEqual(status, 0, "Should fail validation")
            yaml_errors = [e for e in errors if "contains ' #'" in e]
            self.assertTrue(len(yaml_errors) > 0, f"Should have YAML hash error. Errors: {errors}")

    def test_dash_followed_by_space_is_rejected(self) -> None:
        """Frontmatter value starting with '- ' should fail."""
        frontmatter = """---
name: test-skill
description: - x is invalid. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            self.assertNotEqual(status, 0, "Should fail validation")
            yaml_errors = [e for e in errors if "starts with '-'" in e]
            self.assertTrue(len(yaml_errors) > 0, f"Should have dash-space error. Errors: {errors}")

    def test_at_sign_is_rejected(self) -> None:
        """Frontmatter value starting with @ should fail."""
        frontmatter = """---
name: test-skill
description: @mention is invalid. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            self.assertNotEqual(status, 0, "Should fail validation")
            yaml_errors = [e for e in errors if "starts with '@'" in e]
            self.assertTrue(len(yaml_errors) > 0, f"Should have @ error. Errors: {errors}")

    def test_flow_sequence_is_accepted(self) -> None:
        """Flow sequences like [a, b, c] should pass."""
        frontmatter = """---
name: test-skill
description: Valid skill description. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test, validation, flow-sequence]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            yaml_errors = [e for e in errors if "contains" in e or "starts with" in e]
            self.assertEqual(yaml_errors, [], f"Flow sequence should be valid. Errors: {errors}")

    def test_flow_mapping_is_accepted(self) -> None:
        """Flow mappings like {key: value} should pass."""
        frontmatter = """---
name: test-skill
description: Valid skill description. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes: {tags: [test], priority: high}
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            yaml_errors = [e for e in errors if "contains" in e or "starts with" in e]
            self.assertEqual(yaml_errors, [], f"Flow mapping should be valid. Errors: {errors}")

    def test_block_scalar_header_is_accepted(self) -> None:
        """Block scalar headers like | and > should pass YAML validation."""
        frontmatter = """---
name: test-skill
description: |
  This is a literal block scalar that spans multiple lines.
  Use when testing block scalars.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            # Only check for YAML validation errors (contains/starts with), not content validation
            yaml_errors = [e for e in errors if ("contains" in e or "starts with" in e) and "angle brackets" not in e]
            self.assertEqual(yaml_errors, [], f"Block scalar header should be valid YAML. Errors: {errors}")

    def test_plain_scalar_with_dash_no_space_is_accepted(self) -> None:
        """Plain scalars like '-Start here' (dash not followed by space) should pass."""
        frontmatter = """---
name: test-skill
description: -Start here with a valid plain scalar. Use when testing.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [test]
---

# Test Skill
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            create_test_skill(
                Path(tmpdir),
                "test-skill",
                frontmatter,
                [{"name": "test-skill", "family": "test", "reviewed": True}]
            )
            status, errors = run_checker(Path(tmpdir))
            yaml_errors = [e for e in errors if "contains" in e or "starts with" in e]
            self.assertEqual(yaml_errors, [], f"'-Start' plain scalar should be valid. Errors: {errors}")


if __name__ == "__main__":
    unittest.main()
