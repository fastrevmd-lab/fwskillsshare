#!/usr/bin/env python3
"""Validate portable skill packaging and Codex discovery metadata."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---(?:\n|$)", re.DOTALL)
EXPECTED_AUTHORS = ["fastrevmd-lab", "Claude", "GPT"]
RAW_REFERENCE_MAX_LINES = 200
RAW_DUMP_MARKERS = (
    "Skip main navigation",
    "Powered by Higher Logic",
    "View Only",
    "Jump to Best Answer",
    "New Best Answer",
)
OBSOLETE_LICENSE_MARKERS = (
    "source-derived-summary-local-use",
    "CC-BY-NC-SA-4.0-source-derived-summary",
)
EXPECTED_SKILL_NAMES = frozenset(
    {
        "cis-controls-ngfw-compliance",
        "cmmc-nist-800-171-ngfw-compliance",
        "firewall-best-practices-audit",
        "firewall-config-conversion",
        "firewall-config-diff",
        "hipaa-ngfw-compliance",
        "iso27001-ngfw-compliance",
        "parsing-cisco-configs",
        "parsing-fortinet-configs",
        "parsing-palo-configs",
        "parsing-srx-configs",
        "pci-ngfw-compliance",
        "soc2-ngfw-compliance",
        "srx-disa-stig-compliance",
        "srx-advpn",
        "srx-autovpn-full-tunnel",
        "srx-dynamic-ip-feed",
        "srx-ipsec-hub-spoke",
        "srx-mnha",
        "srx-mpls-in-flow",
        "srx-nat",
        "srx-policy",
    }
)


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value[:1] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value
        return parsed if isinstance(parsed, str) else value
    return value


def top_level_frontmatter(frontmatter: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key] = parse_scalar(value)
    return values


def quoted_yaml_field(text: str, key: str) -> str | None:
    match = re.search(rf'^  {re.escape(key)}:\s*("(?:[^"\\]|\\.)*")\s*$', text, re.MULTILINE)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def list_field(frontmatter: str, key: str) -> list[str] | None:
    match = re.search(
        rf"^{re.escape(key)}:\s*\n((?:  - .+(?:\n|$))+)",
        frontmatter,
        re.MULTILINE,
    )
    if not match:
        return None
    return [parse_scalar(line.removeprefix("  - ")) for line in match.group(1).splitlines()]


def raw_reference_errors(path: Path, text: str) -> list[str]:
    """Reject recovered web-page dumps while allowing concise attributed notes."""
    if not (path.name.startswith("source-") or path.name == "source-extract.md"):
        return []

    errors: list[str] = []
    line_count = text.count("\n") + 1
    if line_count > RAW_REFERENCE_MAX_LINES:
        errors.append(
            f"{path}: {line_count} lines exceeds the {RAW_REFERENCE_MAX_LINES}-line "
            "source-note limit"
        )
    for marker in RAW_DUMP_MARKERS:
        if marker in text:
            errors.append(f"{path}: contains raw page-dump marker {marker!r}")
    return errors


def main() -> int:
    errors: list[str] = []
    description_characters = 0
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    actual_skill_names = {skill_file.parent.name for skill_file in skill_files}

    missing_skills = sorted(EXPECTED_SKILL_NAMES - actual_skill_names)
    unexpected_skills = sorted(actual_skill_names - EXPECTED_SKILL_NAMES)
    if missing_skills:
        errors.append(f"missing expected skills: {', '.join(missing_skills)}")
    if unexpected_skills:
        errors.append(f"unexpected skills: {', '.join(unexpected_skills)}")

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        text = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            errors.append(f"{skill_file}: missing or malformed YAML frontmatter")
            continue

        fields = top_level_frontmatter(match.group(1))
        authors = list_field(match.group(1), "author")
        name = fields.get("name", "")
        description = fields.get("description", "")

        if name != skill_dir.name:
            errors.append(f"{skill_file}: name {name!r} does not match directory {skill_dir.name!r}")
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            errors.append(f"{skill_file}: name must be hyphen-case and at most 64 characters")
        if not description:
            errors.append(f"{skill_file}: description is required")
        if len(description) > 1024:
            errors.append(f"{skill_file}: description exceeds 1024 characters")
        if ". Use when " not in description:
            errors.append(
                f"{skill_file}: description must state what the skill does, then include 'Use when'"
            )
        if "<" in description or ">" in description:
            errors.append(f"{skill_file}: description contains angle brackets")
        if not fields.get("version"):
            errors.append(f"{skill_file}: version is required for Hermes package metadata")
        if fields.get("license") != "MIT":
            errors.append(f"{skill_file}: license must be MIT")
        if authors != EXPECTED_AUTHORS:
            errors.append(
                f"{skill_file}: author must be exactly {EXPECTED_AUTHORS!r}; found {authors!r}"
            )
        if "metadata" not in fields:
            errors.append(f"{skill_file}: metadata is required for Hermes compatibility")
        description_characters += len(description)

        for reference in sorted(set(re.findall(r"references/[A-Za-z0-9._/-]+", text))):
            if not (skill_dir / reference).exists():
                errors.append(f"{skill_file}: missing referenced path {reference}")

        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            errors.append(f"{openai_yaml}: missing Codex UI metadata")
            continue

        openai_text = openai_yaml.read_text(encoding="utf-8")
        display_name = quoted_yaml_field(openai_text, "display_name")
        short_description = quoted_yaml_field(openai_text, "short_description")
        default_prompt = quoted_yaml_field(openai_text, "default_prompt")

        if not display_name:
            errors.append(f"{openai_yaml}: display_name must be a quoted string")
        if not short_description or not 25 <= len(short_description) <= 64:
            errors.append(f"{openai_yaml}: short_description must be a quoted 25-64 character string")
        if not default_prompt or f"${name}" not in default_prompt:
            errors.append(f"{openai_yaml}: default_prompt must be quoted and mention ${name}")

        line_count = text.count("\n") + 1
        if line_count > 500:
            errors.append(
                f"{skill_file}: {line_count} lines exceeds the 500-line progressive-disclosure limit"
            )

    if description_characters > 8000:
        errors.append(
            "combined descriptions exceed Codex's 8,000-character fallback discovery budget "
            f"({description_characters})"
        )

    for markdown_file in sorted(SKILLS_DIR.rglob("*.md")):
        markdown_text = markdown_file.read_text(encoding="utf-8")
        errors.extend(raw_reference_errors(markdown_file, markdown_text))
        for marker in OBSOLETE_LICENSE_MARKERS:
            if marker in markdown_text:
                errors.append(f"{markdown_file}: contains obsolete license marker {marker!r}")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1

    print(
        f"OK: {len(skill_files)} portable skill packages; "
        f"{description_characters} description characters; Codex UI metadata present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
