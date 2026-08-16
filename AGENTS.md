# Firewall skills repository instructions

## Purpose and architecture

This repository packages firewall parsing, conversion, diff, audit, compliance,
and Juniper SRX operational skills. Each `skills/<name>/` subtree contains a
`SKILL.md`, references, metadata, and optional fixtures/scripts. The parsing
skills share a normalized schema whose copies must remain byte-identical.

## Setup and development

- Install the golden workstation baseline and run `just setup`.
- Skills are Markdown-first; use repository validation scripts instead of
  inventing a build system. Installation tests must target disposable paths.
- Vendor syntax and compliance claims require authoritative evidence or an
  explicit unsupported/uncertain classification.

## Required checks

- Run `just fmt`, `just lint`, `just test`, and `just guard` offline.
- `just integration` intentionally does not contact devices; real-device
  validation requires a separate explicit task and approval.
- Run `just security` and `just release-check` before handoff.

## Skill description constraints

Two different limits, often confused:

- **Per skill: 1,024 characters, hard.** Codex enforces this. Verified against
  codex-cli **0.147.0**, whose binary carries
  `Description is too long ({n} characters). Maximum is 1024 characters.`
  `scripts/check-skill-packages.py` errors on it.
- **Combined across all skills: soft, warn only.** There is no cliff. Codex
  0.147.0 truncates skill metadata to fit its context budget and reports what it
  did — `ext/skills/src/render_observability.rs` emits `budget_limit`,
  `included_skills`, `omitted_skills`, `truncated_description_chars_per_skill`
  and `truncated_skill_descriptions`. Discovery also runs through a dynamic
  selector (`ext/skills/src/dynamic_skill_selector/`), so the flat concatenated
  list is a fallback, not the primary path. The checker warns above
  `COMBINED_DESCRIPTION_WARN` and never fails on it.

A hard combined cap was previously enforced at 8,000 characters with no recorded
provenance. It scaled the ceiling with skill count — at 26 skills the repo sat at
7,998 of 8,000 — and would have blocked the next skill for a limit the runtime
degrades gracefully around. If you change these numbers, **cite the Codex version
you measured against**, as above.

When the combined warning does fire, prefer **consolidating overlapping skills**
over shortening descriptions. The `Use when ...` clauses are ~71% of the surface
and are exactly what lexical discovery matches on; trimming them makes skills
harder to find, which fails silently.

## Generated files and dependencies

- Keep skill frontmatter, references, bundled assets, and UI metadata valid.
- Do not hand-edit copied shared schemas independently; update the source and
  synchronize all parser copies.
- Do not commit installed skill copies, caches, review scratch, or generated
  customer output.

## Secrets and device safety

- Never commit customer configs, device credentials, tokens, keys, private
  feeds, or unredacted audit evidence.
- Skill examples default to parse/read/analyze/plan/dry-run behavior.
- Configuration, commits, upgrades, reboots, deletes, and failovers require
  explicit approval, rollback protection, and post-change verification.

## Codex review gate

Run it with `scripts/codex-review.sh` — not `codex exec review` directly.

`~/.agents/skills/superpowers` symlinks into `~/.codex/superpowers/skills`, so
Codex loads it as a skill on every run. Its preamble makes the reviewer read
skill files and attempt subagent dispatch instead of the diff; seven consecutive
runs ended with no verdict. The wrapper parks that symlink for the duration and
restores it on exit, including on failure.

- **A run with no final `agent_message` is not a pass.** The wrapper exits
  non-zero and says so; report that the gate did not run.
- **Keep commits small.** `--commit` and `--base` both reject a custom prompt,
  so the only way to scope a review is commit size. A ~1,300-line commit never
  returned; ~80-line commits returned every time.

## Completion evidence

Report skills/files changed, validation commands/results, vendor or framework
evidence used, unsupported cases, and remaining risk.
