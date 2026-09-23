# Firewall Skills Roadmap

This file tracks repository remediation, validation debt, and proposed skills
that have not yet been built. Completed work belongs in the repository history
and release notes; live-device validation work should also have a GitHub issue
with its safety boundary and acceptance criteria.

## Open work

Ordered by readiness, not importance. Each entry says what unblocks it.

### Ready now

- [ ] **Independent technical review of `srx-syslog-logging` 1.1.0.** The
  2026-09-12 work was expansion and live validation, which is not review. The
  README count stays 26/31 until someone other than its author reviews it.
- [ ] **Why `show security log transport` reports nothing under `mode stream`**
  on 25.4R1.12 and 26.2R1.7, while `show security log statistics` returns real
  counters. Needs either documentation on the counter's scope or an activated
  `mode event` configuration — the latter is a device write and outside the
  read-only + `commit check` boundary used so far.
- [ ] **`srx-license-signature-maintenance` mutating paths.**
  `request system license add` and `security-package install` remain
  unexercised against hardware. That is the only outstanding work on a skill
  that otherwise reached 1.0.0 on 2026-08-05 after independent review and a
  read-only live validation across 9 devices / 10 node records —
  [skill-test record](docs/skill-tests/2026-08-05-srx-license-signature-live-validation.md).

### Next new skill — unblocked 2026-09-12

- [ ] Build `firewall-policy-path`. It was gated on the P0 correction and the
  P3 review debt; both closed on 2026-09-12, so nothing blocks it now. The
  scope below is unchanged from when it was written.

  - Accept vendor/context, ingress interface or zone, source and destination
    addresses, source and destination ports, protocol, and optional application.
  - Report the evidence and confidence at each stage: ingress interface and
    zone, routing context, destination NAT, route and egress zone, policy
    precedence and match, source NAT, profile/ALG/screen handling, existing
    session state, and final allow/drop reason.
  - Start with offline analysis of the normalized schema for all four vendors.
    Add vendor-native operational evidence as independently tested modules,
    classifying each command as passive/read-only or active but non-persistent.
  - Use the available vendor primitives rather than inventing a generic
    simulation:
    - [Cisco ASA `packet-tracer`](https://www.cisco.com/c/en/us/td/docs/security/asa/asa-cli-reference/I-R/asa-command-ref-I-R/pa-pn-commands.html)
    - [FortiGate packet-flow debugging](https://docs.fortinet.com/document/fortigate/7.0.0/administration-guide/54688/debugging-the-packet-flow)
    - [PAN-OS policy-match tests](https://docs.paloaltonetworks.com/ngfw/pan-os-cli-quick-start/use-the-cli/test-the-configuration)
    - [Junos policy matching](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-match-policies.html)
    - [Junos packet-drop monitoring](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/monitor-security-packet-drop.html)
  - Default to passive show and policy-match tests. Treat FortiGate debug flow
    and Junos packet-drop monitoring as active diagnostic state: require an
    explicit gate, narrow filters, a packet/time bound, cleanup, and post-checks.
    Keep Cisco `packet-tracer transmit` prohibited by default; require separate
    approval before any packet-producing option.

### Needs hardware or an environment this repository does not have

- [ ] `palo-operational` (PAN-OS operational playbook)
  - Add Palo Alto operational depth comparable to the SRX operational skills.
  - Author and validate against the available Palo VM.
  - Cover security and NAT policy structure, App-ID and security profiles,
    decryption, zones and interfaces, candidate configuration and commits,
    logging, and CLI or operational verification.
- [ ] Remaining `parsing-firepower-configs` unverified items — literal value
  formats, mixed reference/literal containers, and several endpoint families.
  These need a live FMC/FDM or sanitized API Explorer exports. Everything
  reachable from documentation was verified on 2026-09-12.

## Closed — 2026-09-11 and 2026-09-12

The 2026-09-11 repository review (P0-P3 plus the follow-ups it opened) is
complete. Landed in PRs [#66](https://github.com/fastrevmd-lab/fwskillsshare/pull/66),
[#67](https://github.com/fastrevmd-lab/fwskillsshare/pull/67) and
[#68](https://github.com/fastrevmd-lab/fwskillsshare/pull/68); the reasoning
lives in those commits and in the skill-test records under `docs/skill-tests/`.

Three findings are worth keeping visible here, because each contradicts
something this file previously asserted:

- **P0's own premise was wrong.** It called for relaxing the
  "security logs need a revenue interface" rule for `mode event`. Junos rejects
  `security log source-interface fxp0.0` regardless of mode, measured on SRX345
  and vSRX. Implementing the item as written would have made the skill
  incorrect. The real distinction is which statement governs delivery per mode —
  [record](docs/skill-tests/2026-09-12-srx-syslog-logging-mode-and-transport.md).
- **`show security log transport` exists from 25.4R1 but returned empty** on
  every device that accepted it, under `mode stream`. Still unexplained; see
  Open work above.
- **The audit remediation templates were more wrong than the checks.** One told
  operators that `cert-chain-max` prevents feed MITM; it sets chain depth.
  Another contradicted this repository's own live-validated SRX feed pattern.
  Remediation is the part an operator applies to a firewall, so it warrants the
  same evidence bar as the checks themselves.

Inventory drift is now enforced rather than periodically rediscovered:
`skills/inventory.json` is authoritative, `scripts/check-inventory.py` fails on
disagreement with disk, `install.sh`, the README counts and the parser/schema
counts, and `just lint` runs it.

## Tracked validation

- [Issue #15: Re-run `firewall-best-practices-audit` v1.1 against policy-light
  and policy-heavy SRX devices](https://github.com/fastrevmd-lab/fwskillsshare/issues/15)
  defines the read-only test scope, safety boundary, evidence to collect, and
  acceptance criteria. The prior result is documented in
  [the 2026-06-29 vSRX production audit](docs/skill-tests/2026-06-29-vsrx-production-audit.md).
  The live-device rerun was completed on 2026-07-31 —
  [live SRX audit](docs/skill-tests/2026-07-31-firewall-best-practices-audit-live-srx.md).
  It closed the outstanding acceptance item and surfaced four follow-ups.
  All four follow-ups are now complete: modeling `security dynamic-address`,
  extracting `match dynamic-application`, and — as of 2026-09-12 — the
  rule-name-versus-action and plaintext-feed-transport checks in
  `firewall-best-practices-audit` 1.3.0.

### vSRX validation gate — `srx-ips`

The skill ships as a **v0.1.0 draft** and must not be marked reviewed until
every `[unverified]` item is checked on a vSRX with an IDP license and a current
attack database. Read-only commands and non-activating `commit check` only,
unless a write is separately approved.

**Partial validation completed 2026-09-23** across two runs on `vsrx-ci` (vSRX
26.2R1.7, IDP-SIG license not installed, attack database N/A) and `infra-vsrx`
(vSRX 26.2R1.7, IDP-SIG licensed through 2027-07-29, attack database 3929/23 Jul
2026, detector 12.6.180260106). **Six items closed and four falsifications**
corrected in the skill; two further items were answered only against the lab's
Rust-based Junos MCP rather than Juniper's junos-mcp-server, which is the server
they name, and are marked `[~]` rather than closed. Tested via read-only
operational commands, non-activating `commit check`, and actual policy loads
(both devices returned to their original configuration).

- [x] `commit check` with a bogus predefined attack name (KB31478) — **Falsified.**
  A rule matching `predefined-attacks BOGUS:NOT:A:REAL:ATTACK` passed `commit check`
  with `outcome: valid` and no error. `commit check` does not validate predefined
  attack names; they resolve only at policy compile/load time. The skill's advice
  to use `commit check` to test a name was unsound and has been corrected.

- [x] `commit check` of the Step 4 draft as written, including the flow-type
  statement for `stream` and `http-*` contexts — **Falsified.** The draft commits
  exactly as written (`outcome: valid`) with **no** flow-type statement, for
  `context packet`, `context stream` and `context http-url-parsed` alike. No zone
  or address match statements were required either. The flow-type instruction has
  been removed from the skill.

- [x] Bare `protocol-binding tcp` versus `tcp minimum-port … maximum-port …`
  under `commit check` — **Falsified.** Both forms pass `commit check` with
  `outcome: valid`. `minimum-port` is not required. Separately discovered:
  `direction` IS mandatory — omitting it yields `## Warning: missing mandatory
  statement(s): 'direction'` and the check fails. That was the real cause of the
  first failed attempt, and it was undocumented.

- [~] `show security idp attack detail|description <name>` and
  `show security idp predefined-attacks filters category` through the
  junos-mcp-server — **answered for the wrong server; see the caveat below.**
  Through the lab's Rust-based Junos MCP these are **not relay-blocked**:
  `show security idp attack detail <name>` and `... description <name>` both
  returned full output. One genuine Junos syntax correction, which holds on any
  transport: the bare `predefined-attacks filters category` form is a syntax
  error (`syntax error, expecting <data>`) and requires a category argument —
  `... filters category HTTP` returned 11,214 lines.
  **Juniper's junos-mcp-server v1.1.1 was NOT exercised**, so the relay-blocking
  question this item actually asks is still open for that server.

- [~] Pipe modifiers through junos-mcp-server `execute_junos_command` —
  **confirmed working on the lab's Rust-based Junos MCP**, including chained
  modifiers (`| match "…" | count`). **Not tested against Juniper's
  junos-mcp-server v1.1.1**, which is the server this item names.

- [ ] `repeat=N` in `IDP_ATTACK_LOG_EVENT` — **blocked: needs an active policy
  and live attack traffic** (a device write plus traffic generation).

- [x] `commit confirmed` with IDP configured, on vSRX and one Branch SRX
  (Juniper KB21334 reports it unsupported on Branch SRX with IDP) — **vSRX half:
  confirmed working.** A confirmed commit carrying a custom-attack IDP policy was
  accepted and auto-rolled back on both `vsrx-ci` (5-minute window) and
  `infra-vsrx` (1-minute window). `infra-vsrx` logged `UI_COMMIT_NOT_CONFIRMED:
  Commit was not confirmed; automatic rollback complete` and the configuration
  reverted cleanly. **Operational detail:** the rollback fires roughly 30–45
  seconds AFTER the nominal window expires (measured ~40s past a 1-minute window),
  not on the second — verify a rollback by waiting past the window with margin.
  **Branch SRX half remains OPEN** — `srx345` (192.168.1.210) was unreachable on
  2026-09-23 ("No route to host"), so KB21334's claim that confirmed commit is
  unsupported on Branch SRX with IDP is still unverified.

- [x] `show security idp policy-commit-status` output before, during, and after
  a policy load — **Falsified.** Captured across a real policy load on `vsrx-ci`:
  before the load it reported `Active policy not configured or Active policy not
  modified`; during and after it reported `Reading set file for compilation` and
  stayed there for the entire life of the loaded policy, minutes after the compile
  had finished. **The wording "loaded successfully" never appeared.** The compile
  genuinely succeeded: `idpd` logged `IDP_COMMIT_COMPLETED: IDP policy commit is
  complete.` The authoritative completion signal is that syslog event, not
  `policy-commit-status`. Also falsified: `show security idp status` reported
  `Policy Name : none` throughout, even after the successful compile, so it does
  not confirm a load either.

- [ ] `http-url-parsed` versus `http-get-url-parsed` against GET and POST test
  requests in `no-action` — **blocked: needs traffic.**

- [ ] `\[union\]` case-insensitive operator against `UNION`, `Union`, `union` —
  **pattern is syntactically valid** at commit check in an `http-url-parsed`
  context; **match behavior blocked: needs traffic.**

- [x] `file copy /var/log/<file> /var/tmp/<file>-<ts>` for the archive step —
  **Fails through the lab's Rust-based Junos MCP.** Attempted twice on `infra-vsrx` with different target
  basenames. Both times the call failed with `netconf error: RPC error: failed to
  parse RPC response: significant text outside a reply payload`, and the
  destination file was verified absent afterwards, so the copy did not happen. The
  source exists (`/var/log/messages`, 330079 bytes), `/var/tmp/` exists and holds
  other files, and the account is `class 'super-user'` with full permissions — so
  this is not authorisation. Juniper's junos-mcp-server was not tested.
  `fetch_file` cannot substitute: it accepts only a
  basename already under the device's `/var/tmp/` and rejects anything containing
  `/`, so it cannot move a file out of `/var/log/`. **Consequence for the skill:**
  the safety gate requiring log archival before `clear log` is NOT executable over
  this MCP path. The archive must be done over a direct CLI/SSH session, or the log
  left uncleared.

**Custom attacks need neither a licence nor an attack database.** On `vsrx-ci`,
which has `IDP-SIG license not installed` and attack database `N/A`, a
custom-attack IDP policy compiled and loaded successfully (`IDP_COMMIT_COMPLETED`).
Custom signatures are authored locally, so neither the signature database nor the
IDP-SIG licence is required to author, commit, compile and load them. This proves
the policy compiles and loads; it does NOT prove inspection matches traffic, which
was not tested.

**Environmental blocker:** the remaining three items — `repeat=N`,
`http-url-parsed` vs `http-get-url-parsed`, and `\[union\]` match behaviour — all
require live traffic through the device. Custom attacks also widen the usable
device set: the predefined attack database is required only for items involving
**predefined** attacks. The Branch SRX half of item 2 is blocked on `srx345` being
unreachable.

## Tooling and operational skills

`srx-license-signature-maintenance` shipped 2026-07-31 (issue #26) and reached
**1.0.0** on 2026-08-05 after an independent review round and a read-only live
validation across 9 devices / 10 node records —
[skill-test record](docs/skill-tests/2026-08-05-srx-license-signature-live-validation.md).
Its **mutating** paths (`request system license add`,
`security-package install`) remain unexercised against hardware; that is the
only outstanding work on it.


**Branch SRX policy scope — RESOLVED 2026-09-12.** `srx-policy` excluded
"non-Branch SRX platforms" from its first commit (`95d247e`) with **no recorded
rationale anywhere** — no design document, no reference file, no commit message
— and no Branch hardware had ever been tested against it. The exclusion is now
removed for core policy design, on measurement rather than argument.

Validated on SRX345 hardware (Junos 26.2R1.7) by `commit check` —
[record](docs/skill-tests/2026-09-12-srx-policy-branch-srx345-validation.md).
Zone-pair and global policies, `match dynamic-application` unified policies,
`default-policy deny-all`, address books and address-sets, applications and
application-sets, session logging and counters all validate on Branch. The
unified-policy result settles it: the most advanced construct Junos offers
behaves the same there.

**The widening stops at the policy layer.** Licence-gated service attachments
(AppID/AppFW, NGWF, EWF, SecIntel, ATP, IDP) were *not* validated — the test
device holds no licences, and all three `application-services` checks returned
no commit-check verdict. The schema accepts them; that proves nothing about
entitlement. `srx-policy` now carries
`references/platform-and-licensing.md` drawing that line, and
`srx-initial-setup` routes Branch zone-pair work to `srx-policy` instead of
telling operators to design it by hand.

A separate `srx-branch-policy` skill was rejected and remains rejected: it would
duplicate 90%+ of identical content, split lexical discovery for the same
question, and run against `AGENTS.md`'s rule to prefer consolidating overlapping
skills over adding them.

The repository-wide first-priority new skill is `firewall-policy-path`, scoped
under **Recommended next new skill** above. After it:

- [ ] `palo-operational` (PAN-OS operational playbook)
  - Add Palo Alto operational depth comparable to the SRX operational skills.
  - Author and validate against the available Palo VM.
  - Cover security and NAT policy structure, App-ID and security profiles,
    decryption, zones and interfaces, candidate configuration and commits,
    logging, and CLI or operational verification.

## Compliance skills

1. [ ] `cjis-ngfw-compliance`
   - Serve law-enforcement and public-sector environments handling Criminal
     Justice Information.
   - Cover CJI segmentation, encryption, advanced authentication and MFA,
     remote access, logging, agency and vendor connectivity, wireless and
     mobile access, and CJIS Security Policy evidence.

2. [ ] `glba-ftc-safeguards-ngfw-compliance`
   - Serve financial institutions, lenders, insurance-adjacent organizations,
     and fintech.
   - Cover customer information systems, access controls, encryption,
     monitoring, vendor access, incident response, and risk-assessment linkage
     under GLBA and FTC Safeguards Rule expectations.

3. [ ] `nerc-cip-ngfw-compliance`
   - Serve electric utility and bulk electric system environments.
   - Cover Electronic Security Perimeters, BES Cyber Systems, Interactive
     Remote Access, access control, logging, change management, and mappings to
     CIP-005, CIP-007, CIP-010, and CIP-011.
   - Use strict NERC terminology and avoid generic IT-security shortcuts.

4. [ ] `iec62443-ngfw-compliance`
   - Serve industrial and operational-technology firewall and segmentation
     work.
   - Cover zones and conduits, security levels, industrial DMZs, IT/OT
     segmentation, remote vendor access, legacy-system compensating controls,
     and firewall evidence.

5. [ ] `gdpr-ngfw-compliance`
   - Focus on how firewalls support GDPR Article 32 security of processing,
     data minimization through access restriction, breach detection and
     evidence, processor access, and third-party connectivity.
   - Avoid claims that a firewall alone makes an environment GDPR compliant.

6. [ ] `fedramp-ngfw-compliance`
   - Map NGFW controls to NIST SP 800-53 Rev. 5 families such as AC, AU, CM,
     CP, IR, SC, SI, and RA.
   - Treat this as a larger implementation with reuse across cloud and
     public-sector environments.

## Lower priority or conditional

- [ ] `sox-ngfw-compliance`
  - Build only for a concrete financial-reporting-system network-control use
    case.
  - Keep the scope on firewall evidence around financially relevant systems;
    SOX is less network-control-specific than the frameworks above.

## Suggested compliance-skill creation order

1. `cjis-ngfw-compliance`
2. `glba-ftc-safeguards-ngfw-compliance`
3. `nerc-cip-ngfw-compliance` or `iec62443-ngfw-compliance`, depending on
   whether utility and energy or broader OT is the next priority
4. `gdpr-ngfw-compliance`
5. `fedramp-ngfw-compliance`
