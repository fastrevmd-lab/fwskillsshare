---
name: srx-custom-signature-builder
description: Design, validate, and stage a custom Juniper SRX IDP signature for a finding the predefined attack database does not cover. Checks existing coverage read-only, chooses context, direction, and pattern, validates syntax without activating, and stages in monitor mode before any enforcement. Use when a scanner or pentest finding needs IDP detection, when writing a custom-attack, or when extending IDP coverage. Not for triaging existing detections.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, idp, ips, custom-attack, signature, attack-object, context, pattern, dfa, false-positive, monitor-mode, commit-check, approval-gate]
    related_skills: [srx-idp-triage, srx-license-signature-maintenance, srx-policy]
  sources:
    - title: "Junos CLI: custom-attack"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-custom-attack.html
    - title: "Junos CLI: attack-type (signature)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-attack-type-signature.html
    - title: "Junos CLI: tcp (protocol binding, custom attack)"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-tcp-protocol-binding-custom-attack.html
    - title: "IDP attack objects and object groups (mandatory fields, contexts, examples)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-attack-objects-groups.html
    - title: "Custom attack objects for web protocols (HTTP contexts)"
      url: https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-custom-attack-web-protocols.html
    - title: "IDP custom attack DFA pattern syntax"
      url: https://www.juniper.net/documentation/en_US/junos/topics/reference/general/security-idp-custom-attack-object-dfa-pattern.html
    - title: "Junos CLI: show security idp attack detail"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-attack-detail.html
    - title: "Junos CLI: show security idp predefined-attacks"
      url: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-idp-predefined-attacks.html
    - title: "HPE Threat Labs IPS signature database"
      url: https://www.hpe.com/h41379/threatlabs/ips-signatures
    - title: "Lab signature notes"
      local: references/lab-signature-notes.md
      note: "One lab's results against one test application; not production guidance"
---

# SRX Custom IDP Signature Builder

> **STATUS: draft (v0.1.0).** Contributed by Javier Grizzuti
> ([@jgrizzuti](https://github.com/jgrizzuti)) from lab work against Juniper's
> junos-mcp-server, then revised against Juniper documentation. Items marked
> **[unverified]** have not yet been checked on a vSRX and must not be relied on
> until they are. Values in `<angle brackets>` are site-specific.

## Overview

Turns a specific finding — an exposed path, an injection technique, an
auth-bypass pattern — into a custom IDP signature that is checked against
existing coverage, validated without activation, proven in monitor mode, and
only then proposed for enforcement.

Triage of detections that already exist belongs to `srx-idp-triage`. Attack
database updates belong to `srx-license-signature-maintenance`. Transport
behavior of Juniper's junos-mcp-server — no confirmed commit, idle connection
drops, unreliable pipe modifiers — is documented in the Juniper MCP server
field notes shipped with `srx-idp-triage`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.
Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.

## Step 0 — Is a custom signature the right tool?

### Check existing coverage first, read-only

The predefined database has tens of thousands of entries; a duplicate is wasted
effort and a second source of false positives.

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
  show security idp predefined-attacks filters category
  show security idp attack attack-list predefined-group <group-name>
  show security idp attack group-list <attack-name>
  ```
  `attack detail` is the direct existence check for a guessed name: it returns
  severity, category, recommended action, direction, and service for a name in
  the installed database. Note that `show security idp attack-group predefined`
  and `show security idp security-package predefined-attacks` are **not** Junos
  commands — the contributor's syntax errors on those were real errors, not a
  transport limitation.
- **Do not commit to test a name.** Probing with a real or "throwaway" commit
  changes the device. If you need commit-time validation, use `commit check`,
  which validates without activating. **[unverified]** whether `commit check`
  reliably rejects an unknown predefined attack name: Juniper KB31478 describes
  such a commit error, and also that it is not always displayed.
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

Juniper documents **context**, **flow type**, and **direction** as mandatory
for signature attacks. A wrong context or direction does not fail loudly; the
signature simply never matches.

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

`minimum-port` is required by the documented syntax. A bare `protocol-binding
tcp` does not match it — **[unverified]** whether commit rejects it.

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

Draft the candidate:

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

Add the flow-type statement required for your context. **[unverified]** the
exact flow-type statement and whether the draft above commits as written on
the target release.

Then:

1. **Validate without activating.** Run `commit check` on the candidate —
   through a tool that supports it (for example `render_and_apply_j2_template`
   with `dry_run=true` on Juniper's server) — and discard the candidate.
2. **Get explicit approval** to stage it, stating that it is `no-action` and
   what it is scoped to.
3. **Commit with a rollback window** where available, following `srx-idp-triage`
   Step 6, including the plain-commit limitation of Juniper's
   `load_and_commit_config` and the **[unverified]** Branch SRX confirmed-commit
   restriction.
4. **Verify the policy loaded** with `show security idp policy-commit-status`,
   polling rather than waiting a fixed time.

## Step 5 — Prove it matches, with real evidence

Have the operator generate the traffic the signature should catch, then read
the IDP log as in `srx-idp-triage` Step 2 — archive before reading, never clear
without separate approval.

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
2. Get explicit approval, commit with the rollback approach above, and verify
   the policy loaded.
3. Re-run the same test traffic. Done means the client sees the connection
   fail **and** the log shows the new action (for example `CLOSE`).

## Verification checklist

- [ ] Existing coverage checked read-only; no commit used as a lookup
- [ ] Finding confirmed detectable by pattern
- [ ] Context, direction, and binding chosen and justified
- [ ] Pattern reviewed for false positives, scoped by destination
- [ ] Candidate validated with `commit check`, not a real commit
- [ ] Staged as `DETECT-<NAME>` in `no-action` after explicit approval
- [ ] Monitor-mode match proven with run-unique test traffic
- [ ] False-positive test passed
- [ ] Enforcement separately approved, committed with rollback, and verified

## Hand-offs

| Situation | Skill |
|---|---|
| Analyzing detections from existing rules | `srx-idp-triage` |
| Attack database stale or IDP license missing | `srx-license-signature-maintenance` |
| Security policy or `application-services` binding design | `srx-policy` |

The contributor's lab signatures and what they matched are in
[`references/lab-signature-notes.md`](references/lab-signature-notes.md) —
a record of one lab, not a library to deploy.
