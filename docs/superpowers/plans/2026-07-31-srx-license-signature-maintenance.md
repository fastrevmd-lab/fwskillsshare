# Plan: srx-license-signature-maintenance

- **Issue:** [#26](https://github.com/fastrevmd-lab/fwskillsshare/issues/26)
- **Date:** 2026-07-31
- **Outcome:** shipped at v0.1.0 draft 2026-07-31; promoted to **v1.0.0** on
  2026-08-05 after live read-only validation
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

## Independent review (2026-08-05)

Five parallel reviewers covered AGENTS.md compliance, a diff bug scan, Junos
technical accuracy, prose-versus-validator consistency, and secret handling.
Findings acted on:

| Finding | Verdict | Action |
|---|---|---|
| `show system license node 0` is invalid | **Confirmed, and the proposed fix was also wrong** | Rewritten — see below |
| `normalize_version` regex accepts `3929.`, `1..2` | Real | Tightened to `[0-9]+(?:\.[0-9]+)*`, malformed inputs now asserted |
| Secret detection missed `license-key` / `licensekey` | Real | Replaced substring match with separator-tolerant patterns |
| README badge still read `skills-23` | Real | Badges and prose count corrected to 24 |
| Cleanup failure had no defined behavior | Real | Now an explicit stop-and-report security finding |
| License file *path* leaks via history and tool descriptions | Real | Added history suppression and generic-reference guidance |
| Gate B could be inferred from a combined instruction | Reasonable | Verification checklist now requires Gate B answered on its own |
| AGENTS.md compliance | Clean | No action |

Two reviewer suggestions were **not** taken: preferring MCP over raw SSH for
secret handling (speculative, no evidence either path leaks differently), and
adding non-ASCII/base64 report fixtures (the separator-tolerant patterns
already cover the realistic cases).

## Live-device verification (2026-08-05)

The lab chassis cluster was brought up and the **read-only** command surface was
verified against it (2-node vSRX, Junos 24.4R1.9, cluster ID 2). This settled a
syntax question that neither the original text nor the reviewer got right:

| Command | Result on a real cluster |
|---|---|
| `show system license node 0` \| `node node0` \| `node 1` \| `node all` | **all four are syntax errors** — this command has no per-node form |
| `show system license` | works; fields `used` / `installed` / `needed` / `Expiry` confirmed, permanent vs date-based confirmed |
| `show security idp security-package-version node 0` | works, output prefixed `node0:` |
| `show services application-identification version node 0` | works |
| `show version invoke-on all-routing-engines` | works, lists both nodes |

Also corrected from live output: the version qualifier is
`3929(Minor, Thu Jul 23 13:53:38 2026 UTC)` — no space before the paren, and the
parenthetical carries a timestamp, not just a severity word. The documented
example was `3929(Minor)`, which would have misled a parser.

Real license feature names are `IDP-SIG` and `APPID Signature`.

## What was *not* done

- **The mutating paths remain untested.** `request system license add` and
  `request security idp security-package install` were never executed — doing so
  needs a real entitlement file and would change device state. Only the
  read-only inventory and verification commands are live-verified.
- **The RED baselines were not run as live agent trials.** The eight failure
  modes were encoded directly as assertions rather than first demonstrated
  against an unaided agent. This is weaker evidence than an observed baseline
  failure: it proves the shipped logic holds the line, not that an unaided agent
  would have crossed it.
- **The Codex gate never produced a verdict.** It was unusable at first because
  `.codex/config.toml` failed to load (fixed separately in #32). Even after
  that, seven runs — `--base`, `--commit`, and scoped `codex exec` variants,
  including one with a full 9-minute deadline — all terminated without a final
  `agent_message`. Neither `--commit` nor `--base` accepts a scoping prompt, and
  each run spent its budget on the injected `~/.codex` preamble before reaching
  the diff. The independent review above was run in-repo instead.

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

1. ~~Live validation against a lab SRX and a chassis cluster, then promote from
   draft.~~ **Done 2026-08-05** — read-only audit across 9 devices / 10 node
   records on three Junos releases; caught a real per-node AppID mismatch on the
   cluster and four documentation defects. See
   [the skill-test record](../../skill-tests/2026-08-05-srx-license-signature-live-validation.md).
   Promoted to v1.0.0. The mutating paths remain unexercised.
2. Independent Junos and secret-safety review once the Codex allowance returns.
3. Consider extending the contract validator with a fixture that exercises the
   full mode matrix (audit / license-only / signature-only / end-to-end) rather
   than the per-decision assertions it holds today.
