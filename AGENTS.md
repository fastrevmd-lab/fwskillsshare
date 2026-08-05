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
