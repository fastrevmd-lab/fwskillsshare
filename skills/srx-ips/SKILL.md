---
name: srx-ips
description: Manage the complete SRX IDP lifecycle - triage existing detections and propose monitor-to-enforce changes, or design and validate custom signatures for findings the predefined attack database does not cover. Reads IDP policy and logs, reports what fired and what each rule did, stages reviewed changes behind approval gates, checks existing coverage read-only, chooses context/direction/pattern, and validates syntax without activating. Use when reviewing IDP logs, investigating suspicious traffic, deciding which no-action rules to enforce, when a scanner finding needs IDP detection, or when extending IDP coverage. Not for attack database updates or IDP license maintenance.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, idp, ips, idp-policy, rulebase-ips, attack-log, idp-attack-log-event, monitor-mode, enforcement, triage, custom-attack, signature, attack-object, context, pattern, dfa, false-positive, commit-check, approval-gate, mcp]
    related_skills: [srx-license-signature-maintenance, srx-policy, srx-syslog-logging]
    verified_on:
      - platform: vSRX 26.2R1.7
        date: 2026-09-23
        host: infra-vsrx
        attack_db: 3929
        note: Partial validation - commit check behavior, predefined-attack browsing, signature syntax requirements
  sources:
    - title: "Junos CLI: action (Security IDP rulebase-ips then)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-action.html
    - title: "Junos CLI: show security idp policy-commit-status"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-policy-commit-status.html
    - title: "Junos CLI: show security idp status"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-status.html
    - title: "Junos CLI: custom-attack"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-custom-attack.html
    - title: "Junos CLI: attack-type (signature)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-attack-type-signature.html
    - title: "Junos CLI: tcp (protocol binding, custom attack)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-tcp-protocol-binding-custom-attack.html
    - title: "Junos CLI: show security idp attack detail"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-attack-detail.html
    - title: "Junos CLI: show security idp predefined-attacks"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-predefined-attacks.html
    - title: "IDP policies overview (background compile, IDP_COMMIT_COMPLETED)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-policies-overview.html
    - title: "IDP event logging and log suppression"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-event-logging.html
    - title: "IDP attack objects and object groups (mandatory fields, contexts, examples)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-attack-objects-groups.html
    - title: "Custom attack objects for web protocols (HTTP contexts)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-custom-attack-web-protocols.html
    - title: "IDP custom attack DFA pattern syntax"
      url: https://www.juniper.net/documentation/en_US/junos/topics/reference/general/security-idp-custom-attack-object-dfa-pattern.html
    - title: "HPE Threat Labs IPS signature database"
      url: https://www.hpe.com/h41379/threatlabs/ips-signatures
    - title: "Juniper junos-mcp-server (v1.1.1)"
      url: https://github.com/Juniper/junos-mcp-server
    - title: "Juniper MCP server field notes"
      local: references/juniper-mcp-server-notes.md
      note: "Observed with Juniper's junos-mcp-server; verify against your server and version"
    - title: "Lab signature notes"
      local: references/lab-signature-notes.md
      note: "One lab's results against one test application; not production guidance"
---

# SRX IDP Management

> **STATUS: draft (v0.1.0).** Contributed by Javier Grizzuti
> ([@jgrizzuti](https://github.com/jgrizzuti)) from lab work against Juniper's
> junos-mcp-server, then revised against Juniper documentation. Items marked
> **[unverified]** have not yet been checked on a vSRX and must not be relied on
> until they are. Values in `<angle brackets>` are site-specific.
>
> Partial validation performed on vSRX 26.2R1.7 (attack database 3929) on
> 2026-09-23: commit check behavior, predefined-attack browsing, and signature
> syntax requirements were verified on hardware.

## Overview

This skill covers the complete IDP lifecycle on Juniper SRX platforms:

**Triage** reads what an SRX's IDP policy and logs actually show, turns that
into a plain-language finding, and proposes one specific, reviewable change that
moves relevant monitor-mode (`no-action`) rules to enforcement. Use this
workflow when reviewing IDP or screen logs, checking whether attacks were
blocked, investigating suspicious traffic, or deciding which rules to enforce.

**Custom signatures** turn a specific finding — an exposed path, an injection
technique, an auth-bypass pattern — into a custom IDP signature that is checked
against existing coverage, validated without activation, proven in monitor mode,
and only then proposed for enforcement. Use this workflow when a scanner or
pentest finding needs IDP detection, when writing a `custom-attack`, or when
extending IDP coverage beyond the predefined database.

Nothing is changed on the device without explicit approval, and "yes" to an
analysis request is never approval to push configuration. Attack database
updates and IDP license maintenance belong to
`srx-license-signature-maintenance`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and available approved read-only evidence. If unresolved facts could materially change safety, scope, correctness, confidence, or the requested output, read `references/runtime-intake.md`. For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request. Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog. Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist. Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.

# Workflow A: Triage existing detections

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
   **`file copy` may not survive an MCP relay.** On a Rust-based Junos MCP
   server (not Juniper's), two attempts failed with `failed to parse RPC
   response: significant text outside a reply payload`, and the destination
   file was verified absent afterwards — the copy did not happen, on a
   `super-user` account with a readable source. Juniper's own server was not
   tested. Confirm the archive step actually produced a file before relying
   on it, and fall back to a direct CLI/SSH session if it did not. Never run
   `clear log` on the strength of an archive you have not confirmed exists.
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
4. **Verified on vSRX 26.2R1.7, 2026-09-23:** `commit confirmed` works correctly
   with IDP configured. The device auto-rolled back a 1-minute confirmed commit
   cleanly and logged `UI_COMMIT_NOT_CONFIRMED`. **Operational timing:** the
   rollback fires roughly 30–45 seconds AFTER the nominal window expires, not on
   the second — verify a rollback by waiting past the window with margin.
   **[unverified on Branch SRX]** Juniper KB21334 reports that `commit confirmed`
   is unsupported on Branch SRX with IDP. Until checked, treat confirmed commit as
   unavailable on Branch SRX with IDP and use the manual rollback plan.

A successful commit does **not** mean the new policy is enforcing. IDP compiles
and loads in the background after commit, with no fixed duration. Poll, do not
sleep for a fixed time:

```
show security idp policy-commit-status
```

**Verified on vSRX 26.2R1.7, 2026-09-23:** `policy-commit-status` never reached a
"loaded successfully" wording. It reported `Reading set file for compilation` and
stayed there for the entire life of the loaded policy, minutes after the compile
had finished. The authoritative completion signal is the syslog event
`IDP_COMMIT_COMPLETED: IDP policy commit is complete.` `Policy Name` and `Running
Detector Version` in `show security idp status` do NOT confirm a new policy load —
both stayed `none` throughout a verified successful compile. On a cluster, verify
each node.

## Step 7 — Prove the change with traffic

Offer to regenerate the original traffic — with the operator running the tool,
not the agent — and pull the log again. The change is proven when the same
attack now logs the new action (for example `CLOSE` or `DROP` instead of
`NONE`) and the client sees the connection fail.

# Workflow B: Custom signatures

## Step 0 — Is a custom signature the right tool?

### Check existing coverage first, read-only

The predefined database has tens of thousands of entries; a duplicate is wasted
effort and a second source of false positives. **Verified on vSRX 26.2R1.7,
2026-09-23:** Custom attacks do NOT require the IDP-SIG licence or a signature
database. A custom-attack policy compiled and loaded successfully
(`IDP_COMMIT_COMPLETED`) on a device with `IDP-SIG license not installed` and
attack database `N/A`. Custom signatures are authored locally and enforce without
the predefined database.

- **Search offline.** The public database is the HPE Threat Labs IPS signature
  site (formerly `threatlabs.juniper.net`, which now redirects there). If you
  have an export, parse it with a real CSV parser rather than `grep`, and search
  names, descriptions, and keywords for the finding and its synonyms — one
  keyword misses matches such as `gitignore` versus `git-config-disclosure`.
  **[unverified]** whether the site offers a CSV export, and its column names.
- **Look up candidates on the device, read-only:**
  ```
  show security idp attack detail <attack-name>
  show security idp attack description <attack-name>
  show security idp predefined-attacks filters category <category>
  show security idp attack attack-list predefined-group <group-name>
  show security idp attack group-list <attack-name>
  ```
  `attack detail` is the direct existence check for a guessed name: it returns
  severity, category, recommended action, direction, and service for a name in
  the installed database. Note that `show security idp attack-group predefined`
  and `show security idp security-package predefined-attacks` are **not** Junos
  commands — the contributor's syntax errors on those were real errors, not a
  transport limitation.

  **Verified on vSRX 26.2R1.7, 2026-09-23:** The `show security idp
  predefined-attacks filters category` command **requires a category argument**
  (e.g., `category HTTP`). The bare form fails with `syntax error, expecting
  <data>`. The following browse commands are confirmed reachable through
  Juniper's junos-mcp-server and are NOT relay-blocked: `show security idp
  attack detail <name>`, `show security idp attack description <name>`, and pipe
  modifiers (`| match`, `| count`, chained).

- **Do not commit to test a name.** Probing with a real or "throwaway" commit
  changes the device. **Verified on vSRX 26.2R1.7, 2026-09-23:** `commit check`
  does NOT reject an unknown predefined attack name. A rule matching
  `predefined-attacks BOGUS:NOT:A:REAL:ATTACK` passed commit check with
  `outcome: valid` and no error. The attack name is only resolved when the
  policy is compiled/loaded, not at commit-check time. To verify a predefined
  attack name exists, use `show security idp attack detail <name>` read-only
  BEFORE putting it in a rule.
- A matching name is not proof of coverage. Prove it against the actual payload
  in monitor mode before deciding no custom signature is needed.

### Is the finding detectable by pattern at all?

Signatures match bytes that are present in traffic. Three kinds of finding do
not fit; say so plainly instead of forcing a signature that never fires:

- **Absences** — a missing security header or cookie flag. Nothing to match.
  That is an application or reverse-proxy fix.
- **Business-logic and authorization flaws** — changing an ID to view another
  user's data. The request is byte-for-byte legitimate.
- **Fingerprinting** — identifying server software is not itself an attack.

## Step 1 — One signature or two?

If the finding has a **reconnaissance** step and a separate **exploitation**
step — a directory listing that reveals a file, versus fetching that file —
consider two signatures:

- Reconnaissance or disclosure → `severity info`, left in `no-action`, logged.
- Exploitation → `severity major` or higher, a candidate for enforcement after
  validation.

**Name rules for what they do.** Use `DETECT-<NAME>` for a rule that stays in
`no-action` and `BLOCK-<NAME>` only once it enforces. A monitor-only rule named
`BLOCK-…` is a name/action contradiction that auditors — and
`firewall-best-practices-audit` — flag.

## Step 2 — Choose context and direction

Juniper documents **context** and **direction** as mandatory for signature
attacks. **Verified on vSRX 26.2R1.7, 2026-09-23:** `direction` IS mandatory on
a signature attack. Omitting it produces `## Warning: missing mandatory
statement(s): 'direction'` and the commit check fails. A wrong context or
direction does not fail loudly; the signature simply never matches.

- **HTTP contexts.** Method-specific contexts exist: `http-get-url-parsed`,
  `http-post-url-parsed`, `http-head-url-parsed`. `http-url-parsed` is
  documented as "the decoded, normalized URL in an HTTP request" with no method
  restriction, and Juniper's own guidance pairs it with an
  `http-request-method` context to bind a signature to one method. The
  contributor observed `http-url-parsed` not behaving as a catch-all —
  **[unverified]**; test both before relying on either reading.
- **`http-post-variable-parsed`** matches individual POST form-field values — a
  good fit for payloads in form fields.
- **Deprecated contexts.** Juniper removed the `http-*-url-parsed-param*`
  contexts from the HTTP decoder; use `http-url-parsed` with
  `http-variable-parsed` instead.
- **Protocol-agnostic contexts** — `stream`, `packet`, `line`, and variants such
  as `first-data-packet` and `stream256` — avoid HTTP parsing ambiguity at the
  cost of precision and performance. Scope them tightly.
- **Direction** is `client-to-server`, `server-to-client`, or `any`. A signature
  on a server **response** — a directory-listing page's `Index of /` — needs
  `server-to-client`.

### Service or protocol binding

Juniper: specify **either** a service **or** a protocol binding; if both are
set, the service binding wins. HTTP contexts already imply the HTTP service.
For a generic context, bind the port range explicitly:

```
set security idp custom-attack <name> attack-type signature protocol-binding tcp minimum-port <port> maximum-port <port>
```

**Verified on vSRX 26.2R1.7, 2026-09-23:** `minimum-port` is NOT required on
`protocol-binding tcp`. BOTH forms pass commit check with `outcome: valid` —
bare `protocol-binding tcp`, and `protocol-binding tcp minimum-port 80
maximum-port 80`. The port range is optional and narrows the binding when
specified.

## Step 3 — Write the pattern defensively

- **Case.** The DFA pattern language has a case-insensitive operator:
  `\[union\]` matches `UNION`, `Union`, and `union`. Use it rather than
  hand-writing `[Uu][Nn][Ii][Oo][Nn]`. **[unverified]** on-device behavior of
  both forms.
- **Encoding.** In a raw context such as `stream`, special characters (`<`,
  `>`, `=`) may arrive percent-encoded while letters do not. Parsed HTTP
  contexts decode first. Prefer a parsed context over dropping characters from
  the pattern.
- **False positives are the main cost.** A bare word that is a substring of
  ordinary text will fire on legitimate traffic: `script` matches
  `description`, and `;` or `|` appear in normal form input. Make the pattern
  specific first, then scope it.
- **Scope.** Restrict by `destination-address` to limit the blast radius. A
  broad pattern scoped to one lab host is safe; the same pattern device-wide is
  not, and must not leave monitor mode without a false-positive review against
  real production traffic.

## Step 4 — Draft, validate without activating, then stage in monitor mode

Draft the candidate. **Verified on vSRX 26.2R1.7, 2026-09-23:** `direction` is
mandatory (omitting it fails commit check), but no `flow-type` statement is
required. The draft below validates as written for `context packet`, `context
stream`, AND `context http-url-parsed` — no flow-type statement in any case,
and no zone/address match statements needed either in the attack definition.

```
set security idp custom-attack CUSTOM-<NAME> severity <info|minor|major|critical|warning>
set security idp custom-attack CUSTOM-<NAME> attack-type signature context <context>
set security idp custom-attack CUSTOM-<NAME> attack-type signature pattern "<pattern>"
set security idp custom-attack CUSTOM-<NAME> attack-type signature direction <direction>

set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match from-zone <zone>
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match source-address any
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match to-zone <zone>
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match destination-address <host>
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match application default
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> match attacks custom-attacks CUSTOM-<NAME>
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> then action no-action
set security idp idp-policy <policy> rulebase-ips rule DETECT-<NAME> then notification log-attacks
```

Then:

1. **Validate without activating.** Run `commit check` on the candidate —
   through a tool that supports it (for example `render_and_apply_j2_template`
   with `dry_run=true` on Juniper's server) — and discard the candidate.
2. **Get explicit approval** to stage it, stating that it is `no-action` and
   what it is scoped to.
3. **Commit with a rollback window** where available, following the shared
   commit guidance below, including the plain-commit limitation of Juniper's
   `load_and_commit_config` and the **[unverified]** Branch SRX confirmed-commit
   restriction.
4. **Verify the policy loaded** with `show security idp policy-commit-status`,
   polling rather than waiting a fixed time.

## Step 5 — Prove it matches, with real evidence

Have the operator generate the traffic the signature should catch, then read
the IDP log as in the triage workflow Step 2 — archive before reading, never
clear without separate approval.

- **Use a run-unique marker** (a timestamp or PID) in test payloads that leave
  state behind. A fixed marker can match a previous run's stored payload and
  report "it worked" when the current attempt was blocked or never sent.
- **If nothing fires**, check the plumbing before the signature: is the
  idp-policy still attached through `application-services` on the security
  policy carrying the traffic? A missing binding silently disables every
  signature, not just the new one.
- **Also test for false positives**: send ordinary traffic containing the
  pattern's near-misses and confirm the signature stays quiet.

## Step 6 — Propose enforcement, then re-verify

Only after monitor-mode matches are proven and false positives reviewed:

1. Propose renaming `DETECT-<NAME>` to `BLOCK-<NAME>` and setting the action.
   Prefer an action proven in this environment; the contributor's lab found
   `close-client-and-server` most consistent for its HTTP traffic.
2. Get explicit approval, commit with the rollback approach below, and verify
   the policy loaded.
3. Re-run the same test traffic. Done means the client sees the connection
   fail **and** the log shows the new action (for example `CLOSE`).

# Shared commit and verification guidance

## Commit with rollback

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
4. **Verified on vSRX 26.2R1.7, 2026-09-23:** `commit confirmed` works correctly
   with IDP configured. The device auto-rolled back a 1-minute confirmed commit
   cleanly and logged `UI_COMMIT_NOT_CONFIRMED`. **Operational timing:** the
   rollback fires roughly 30–45 seconds AFTER the nominal window expires, not on
   the second — verify a rollback by waiting past the window with margin.
   **[unverified on Branch SRX]** Juniper KB21334 reports that `commit confirmed`
   is unsupported on Branch SRX with IDP. Until checked, treat confirmed commit as
   unavailable on Branch SRX with IDP and use the manual rollback plan.

## Policy load verification

A successful commit does **not** mean the new policy is enforcing. IDP compiles
and loads in the background after commit, with no fixed duration. Poll, do not
sleep for a fixed time:

```
show security idp policy-commit-status
```

**Verified on vSRX 26.2R1.7, 2026-09-23:** `policy-commit-status` never reached a
"loaded successfully" wording. It reported `Reading set file for compilation` and
stayed there for the entire life of the loaded policy, minutes after the compile
had finished. The authoritative completion signal is the syslog event
`IDP_COMMIT_COMPLETED: IDP policy commit is complete.` `Policy Name` and `Running
Detector Version` in `show security idp status` do NOT confirm a new policy load —
both stayed `none` throughout a verified successful compile. On a cluster, verify
each node.

# Verification checklists

## Triage workflow

- [ ] Rule table built from the **active** policy, including actions and scope
- [ ] idp-policy binding through `application-services` confirmed
- [ ] Logs read without deleting evidence; any `clear log` separately approved
- [ ] Finding stated in plain language with raw repeat values
- [ ] One combined proposal with exact lines, blast radius, and rollback
- [ ] Explicit approval received for the push
- [ ] Commit used a rollback window, or the lack of one was approved
- [ ] `policy-commit-status` shows the new policy loaded, per node
- [ ] Before-and-after log evidence shows the new action

## Custom signature workflow

- [ ] Existing coverage checked read-only; no commit used as a lookup
- [ ] Finding confirmed detectable by pattern
- [ ] Context and direction chosen and justified; direction is mandatory
- [ ] Pattern reviewed for false positives, scoped by destination
- [ ] Candidate validated with `commit check`, not a real commit
- [ ] Staged as `DETECT-<NAME>` in `no-action` after explicit approval
- [ ] Monitor-mode match proven with run-unique test traffic
- [ ] False-positive test passed
- [ ] Enforcement separately approved, committed with rollback, and verified

# Hand-offs

| Situation | Skill |
|---|---|
| Traffic matches no existing signature | Use the custom signature workflow in this skill |
| Analyzing detections from existing rules | Use the triage workflow in this skill |
| Attack database stale or IDP license missing | `srx-license-signature-maintenance` |
| Security policy or `application-services` binding design | `srx-policy` |
| IDP logs not reaching a collector | `srx-syslog-logging` |

The contributor's lab signatures and what they matched are in
[`references/lab-signature-notes.md`](references/lab-signature-notes.md) —
a record of one lab, not a library to deploy.
