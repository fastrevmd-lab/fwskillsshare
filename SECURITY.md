# Security Policy

## Reporting a vulnerability or unsafe skill guidance

Please **do not** open a public GitHub issue, discussion, or pull request for a security vulnerability, and please do not open a public issue describing dangerously unsafe skill guidance either — report both privately.

Use GitHub's private vulnerability reporting for this repository:

https://github.com/fastrevmd-lab/fwskillsshare/security/advisories/new

Include what you'd include in a normal report — affected skill or script, version, reproduction steps, and impact — but keep it in the private advisory, not a public issue, PR, comment, or discussion. No email address or third-party reporting service is used for this project; the GitHub Security tab (Security Advisories) is the only channel.

## Scope

This repository is almost entirely Markdown "skills" — instructions loaded into an agent's context (Claude Code, Codex, Hermes) — plus a handful of Python validators and a shell installer. Two different kinds of "security concern" apply here, and a report is welcome for either:

- **Unsafe or dangerous skill guidance.** This is the more likely category. A skill that recommends a command that could take down a production device without warning, that omits an approval/rollback/verification gate around a device-changing action, that would encourage bypassing the deterministic-decides/human-approves boundary described in [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md), or that could be steered by adversarial/injected content in a pasted config into doing something the operator didn't ask for — all of that belongs here, reported the same way as a code vulnerability.
- **A code vulnerability**, in the ordinary sense, in `install.sh` or the `scripts/` validators — e.g., something that lets a maliciously crafted skill directory or config fixture escape its expected path, execute unintended commands, or exfiltrate data when the installer or a checker script runs over it.

If you're not sure which category your finding falls into, or whether it's a vulnerability at all, report it privately anyway and let the maintainer sort it out — that's a better failure mode than a public issue disclosing an unsafe pattern before it's fixed.

## What's out of scope

This repository ships no server, no telemetry, and no network service of its own — the installer copies local files, and skills are static Markdown read by whatever agent runtime you point at them. Reports about a downstream agent runtime's own behavior (Claude Code, Codex, Hermes) belong with that project, not here, unless the issue is specifically in how a skill in this repository is written.

## Response

This is a community-maintained project. There's no guaranteed SLA. A human maintainer is responsible for triaging every report and for all disclosure and fix decisions.
