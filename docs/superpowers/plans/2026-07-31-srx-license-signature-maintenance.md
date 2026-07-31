# Plan: srx-license-signature-maintenance

- **Issue:** [#26](https://github.com/fastrevmd-lab/fwskillsshare/issues/26)
- **Date:** 2026-07-31
- **Outcome:** skill shipped at v0.1.0, labeled draft
- **Worktree:** implemented in an isolated worktree, per the issue's requirement

## File responsibilities

| File | Responsibility |
|---|---|
| `SKILL.md` | Triggering, the two approval gates, mode selection, phase order, failure table, output contract. Routes detail to references. |
| `references/licensing.md` | Read-only baseline commands and entitlement parsing; staging and secret handling; the SFTP probe and legacy-SCP fallback; per-node licensing; cleanup. |
| `references/offline-signatures.md` | Bundle validation, extraction and install commands, terminal-state polling rules, pilot-then-batch rollout, cluster sequencing, stop conditions. |
| `references/verification-troubleshooting.md` | Per-node verification matrix, version-qualifier normalization, no-active-policy handling, disabled-secondary handling, troubleshooting table, reporting discipline. |
| `references/runtime-intake.md` | Eight-question intake catalog. |
| `agents/openai.yaml` | Codex UI metadata. |
| `scripts/check-srx-license-signature-contract.py` | Offline behavioral contract + documentation guards; runs from `just test`. |

## Behavioral contract encoded as tests

The issue's RED baseline enumerated eight failure modes. Each is now an
executable assertion rather than a prose requirement:

| Baseline failure mode | Encoded as |
|---|---|
| Leaks or mishandles license material | `report_is_sanitized`, plus a doc scan for key-block markers |
| Treats one approval as authorization for both phases | `gate_satisfied` — neither gate implies the other; read-only implies neither |
| Licenses or verifies only the primary | `cluster_evidence_complete` — an aggregate never substitutes for per-node evidence |
| Fans out before pilot verification | Documented stop conditions; `Stop conditions` guard term required |
| Treats `In progress` as completion | `is_terminal` / `is_terminal_success` reject it, plus empty, blank, `pending`, `timeout` |
| Uses time alone as success evidence | Polling section requires condition-based checks; `condition` guard term required |
| Mishandles `(Minor)` version qualifiers | `normalize_version` splits comparable token from qualifier and retains both |
| Overclaims data-plane protection | `install_outcome` returns `success-with-warning` and never claims enforcement |

### RED → GREEN evidence

Each assertion was mutation-checked against the shipped logic. Reverting any one
of these individually reproduces its own error, so none of the tests is vacuous:

| Mutation | Error produced |
|---|---|
| `gate_satisfied` returns `bool(approvals)` | licensing approval leaked into the signature gate |
| `in progress` added to `TERMINAL_SUCCESS` | non-terminal status ended the poll |
| `cluster_evidence_complete` honors `aggregate_ok` | cluster aggregate substituted for missing secondary evidence |
| `normalize_version` drops the qualifier | qualifier was discarded instead of retained |
| `install_outcome` returns `("success", True)` with no policy | enforcement was claimed active with no active IDP policy |

## What was *not* done

- **No live-device forward test.** The issue prohibits live devices in
  repository CI, and none were used. The skill is therefore unvalidated against
  real licensing or signature installation, and is labeled draft accordingly.
- **The RED baselines were not run as live agent trials.** The eight failure
  modes were encoded directly as assertions rather than first demonstrated
  against an unaided agent. This is weaker evidence than an observed baseline
  failure: it proves the shipped logic holds the line, not that an unaided agent
  would have crossed it.
- **No independent Junos or secret-safety review** — the issue asks for one, and
  the Codex gate is quota-blocked until 2026-08-05.

## Registration points

Adding a skill touches seven registries; all were updated:

`scripts/check-skill-packages.py` · `scripts/check-runtime-intake.py`
(`COMPACT_SCOPE_TEXT` for the compact intake template) ·
`scripts/check-runtime-intake-safety.py` (skill list, Appendix-A `the`-fragment
ids, catalog SHA256, safe-default and exact-option pins) ·
`scripts/test-runtime-intake-safety.py` and
`scripts/test-runtime-intake-validator.py` (inventory counts) ·
`scripts/check-installer.py` · `install.sh` (`SRX` family) · `README.md`.

The Appendix A section in
`docs/superpowers/plans/2026-07-24-runtime-intake-questions.md` was **generated
from the catalog JSON** rather than hand-written, so the plan and the package
reference cannot drift; the validator's equality check passed on the first run
against a generated section.

## Follow-ups

1. Live validation against a lab SRX and a chassis cluster, then promote from
   draft.
2. Independent Junos and secret-safety review once the Codex allowance returns.
3. Consider extending the contract validator with a fixture that exercises the
   full mode matrix (audit / license-only / signature-only / end-to-end) rather
   than the per-decision assertions it holds today.
