---
name: srx-idp-triage
description: Triage Juniper SRX IDP detections and propose moving monitor-mode rules to enforcement. Reads the IDP policy and logs, reports what fired and what each rule did, and stages one reviewed change behind an approval gate. Use when reviewing IDP or screen logs, checking whether attacks were blocked, investigating suspicious traffic an SRX flagged, or deciding which no-action IDP rules to enforce. Not for writing new signatures or updating the attack database.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, idp, ips, idp-policy, rulebase-ips, attack-log, idp-attack-log-event, monitor-mode, enforcement, triage, mcp, approval-gate]
    related_skills: [srx-custom-signature-builder, srx-license-signature-maintenance, srx-policy, srx-syslog-logging]
  sources:
    - title: "Junos CLI: action (Security IDP rulebase-ips then)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-action.html
    - title: "Junos CLI: show security idp policy-commit-status"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-policy-commit-status.html
    - title: "Junos CLI: show security idp status"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-status.html
    - title: "IDP policies overview (background compile, IDP_COMMIT_COMPLETED)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-policies-overview.html
    - title: "IDP event logging and log suppression"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-event-logging.html
    - title: "Juniper junos-mcp-server (v1.1.1)"
      url: https://github.com/Juniper/junos-mcp-server
    - title: "Juniper MCP server field notes"
      local: references/juniper-mcp-server-notes.md
      note: "Observed with Juniper's junos-mcp-server; verify against your server and version"
---

# SRX IDP Log Triage

> **STATUS: draft (v0.1.0).** Contributed by Javier Grizzuti
> ([@jgrizzuti](https://github.com/jgrizzuti)) from lab work against Juniper's
> junos-mcp-server, then revised against Juniper documentation. Items marked
> **[unverified]** have not yet been checked on a vSRX and must not be relied on
> until they are. Values in `<angle brackets>` are site-specific.

## Overview

Reads what an SRX's IDP policy and logs actually show, turns that into a
plain-language finding, and proposes one specific, reviewable change that moves
relevant monitor-mode (`no-action`) rules to enforcement. Nothing is changed on
the device without explicit approval, and "yes" to an analysis request is never
approval to push configuration.

This skill triages **detection that already exists**. If the traffic in the logs
matches no configured rule, say so plainly and hand off to
`srx-custom-signature-builder`; do not improvise a signature mid-triage. Attack
database and license problems belong to `srx-license-signature-maintenance`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.
Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.

## Step 0 — Identify the target and the transport

List the devices the tooling can reach (for example `get_router_list` on
Juniper's junos-mcp-server) and confirm the target is registered. Record the
model, Junos release, and whether it is a chassis cluster; IDP state is per node
on a cluster.

Know your transport's limits before you rely on it. Server-specific behavior —
idle connection drops, pipe modifiers, binary output — is in
[`references/juniper-mcp-server-notes.md`](references/juniper-mcp-server-notes.md).
If a basic call fails, do not retry blindly; read that file first.

## Step 1 — Establish current state (read-only)

```
show security idp status
show security idp policy-commit-status
show security idp security-package-version
show configuration security idp
show configuration security policies
```

Filter the policies output for `application-services idp-policy` locally
rather than with `| match`, which some transports do not honor.

From this, build a table of every `rulebase-ips` rule in the **active** policy:
name, matched attack objects or groups, match scope (zones, addresses), and the
current `then action`. Rules with `no-action` are candidates; rules already
enforcing are not.

Also confirm the idp-policy is actually attached through
`application-services` on the security policies carrying the traffic. A
missing binding means **nothing** is inspected, which looks identical to "no
attacks".

## Step 2 — Pull logs, small and attributable

Prefer a dedicated IDP log file over `messages`, which fills with unrelated
management-plane noise. Find it with `show configuration system syslog`.
Detections may also already be off-box — a collector or SIEM is often the
better source; see `srx-syslog-logging`.

Check size before pulling:

```
file list detail /var/log/<logfile>
```

If it is small, read it with `show log <logfile>`. If it is large, **do not
count on pipe modifiers** (`| match`, `| last`, `| count`) to shrink it — see
the MCP notes. In order of preference:

1. Read the same detections from the collector or SIEM.
2. **Archive, then read the copy.** Nothing is lost:
   ```
   file copy /var/log/<logfile> /var/tmp/<logfile>-<timestamp>
   ```
3. Only if a fresh, attributable slice is genuinely needed: archive first as
   above, then ask for **separate explicit approval** to run
   `clear log <logfile>`. Clearing permanently deletes the on-box evidence;
   never clear a log you have not archived and read.

## Step 3 — Parse and cross-reference

For each `IDP_ATTACK_LOG_EVENT`, record source, destination and port, matched
policy and rule, attack name, action, and the `repeat=` value.

IDP log suppression is on by default: repeated matches are coalesced into one
line that carries a count. Juniper documents the `repeat-count` field but not
whether `repeat=0` means one occurrence — **[unverified]** the reading
"`repeat=N` means N+1 matches". Until it is checked, report the raw value
("1 line, repeat=3") rather than a derived total.

Cross-reference every attack name against the Step 1 table to confirm which
rules are in monitor mode.

## Step 4 — State the finding in plain language first

Before any configuration, say which source did what, which signatures fired,
over what window, how many log lines and repeat values, and what each rule
actually did:

> Source `<source-ip>` triggered `<signature-A>` (3 lines, repeat=0) and
> `<signature-B>` (1 line, repeat=2) against `<destination-ip>:<port>` between
> `<start>` and `<end>`. Both rules are in monitor mode (`action=NONE`) —
> nothing was blocked.

## Step 5 — One combined, reviewed proposal

Propose all relevant monitor-to-enforce changes as **one** block rather than a
rule-by-rule back-and-forth. `then action` is a single choice, so setting a new
action replaces `no-action`; no `delete` is needed:

```
set security idp idp-policy <policy> rulebase-ips rule <rule> then action <action>
```

Choose `<action>` deliberately. Valid values are `close-client`,
`close-client-and-server`, `close-server`, `drop-connection`, `drop-packet`,
`ignore-connection`, `mark-diffserv`, `no-action`, and `recommended`. Prefer an
action already proven in **this** environment by before-and-after logs; the
contributor's lab found `close-client-and-server` most consistent for its HTTP
test traffic, which is a lab result, not a general rule.

Present the exact lines, the expected effect, the blast radius (which traffic
the rule scope covers), and the rollback. Then **stop** until the user
explicitly approves the push.

## Step 6 — After approval: commit with rollback, then verify the data plane

Every commit here follows the repository write policy:

1. Show the candidate with `show | compare` and confirm it matches the approved
   lines exactly.
2. Commit with a rollback window — `commit confirmed <minutes>` — and confirm
   with a second commit only after verification passes.
3. **Check whether your transport can do that.** Juniper's junos-mcp-server
   v1.1.1 `load_and_commit_config` performs a plain `commit` with no confirmed
   or dry-run option. If the tool cannot do a confirmed commit, say so, and get
   approval that explicitly accepts a manual rollback plan
   (`rollback 1` then `commit`) before pushing.
4. **[unverified]** Juniper KB21334 reports that `commit confirmed` is not
   supported on Branch SRX with IDP. Until checked, treat confirmed commit as
   unavailable on Branch SRX with IDP and use the manual rollback plan.

A successful commit does **not** mean the new policy is enforcing. IDP compiles
and loads in the background after commit, with no fixed duration. Poll, do not
sleep for a fixed time:

```
show security idp policy-commit-status
```

Done means it reports the policy and detector **loaded successfully**. `Policy
Name` and `Running Detector Version` in `show security idp status` are already
filled in by the **previous** policy, so they alone prove nothing about the new
one. On a cluster, verify each node.

## Step 7 — Prove the change with traffic

Offer to regenerate the original traffic — with the operator running the tool,
not the agent — and pull the log again. The change is proven when the same
attack now logs the new action (for example `CLOSE` or `DROP` instead of
`NONE`) and the client sees the connection fail.

## Verification checklist

- [ ] Rule table built from the **active** policy, including actions and scope
- [ ] idp-policy binding through `application-services` confirmed
- [ ] Logs read without deleting evidence; any `clear log` separately approved
- [ ] Finding stated in plain language with raw repeat values
- [ ] One combined proposal with exact lines, blast radius, and rollback
- [ ] Explicit approval received for the push
- [ ] Commit used a rollback window, or the lack of one was approved
- [ ] `policy-commit-status` shows the new policy loaded, per node
- [ ] Before-and-after log evidence shows the new action

## Hand-offs

| Situation | Skill |
|---|---|
| Traffic matches no existing signature | `srx-custom-signature-builder` |
| Attack database stale, IDP license missing | `srx-license-signature-maintenance` |
| Security policy or `application-services` binding design | `srx-policy` |
| IDP logs not reaching a collector | `srx-syslog-logging` |
