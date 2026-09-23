# Firewall Skills Roadmap

This file tracks repository remediation, validation debt, and proposed skills
that have not yet been built. Completed work belongs in the repository history
and release notes; live-device validation work should also have a GitHub issue
with its safety boundary and acceptance criteria.

## Repository review follow-ups — 2026-09-11

The repository is structurally healthy: all 29 skill packages validate, all
five parser schemas are byte-identical, and the required checks pass. The
remaining work is documentation integrity, technical review debt, and coverage
gaps. Complete the existing-skill work below before adding a 30th package.

### P0 — correct technical guidance — COMPLETE 2026-09-12

- [x] Expand `srx-syslog-logging` (1.0.0 -> 1.1.0). Live-validated read-only
  plus non-activating `commit check` across SRX345 hardware (26.2R1.7) and
  vSRX on 24.4R1.9, 25.4R1.12 and 26.2R1.7 —
  [validation record](docs/skill-tests/2026-09-12-srx-syslog-logging-mode-and-transport.md).

  **This item's premise was wrong, and the devices disproved it.** It asserted
  that the blanket "security logs need a revenue interface" claim was
  stream-only and should be relaxed for `mode event`. Junos rejects
  `security log source-interface fxp0.0` *irrespective of mode* — measured on
  both SRX345 and vSRX — with `This interface cannot be configured for log,
  only revenue port is allowed`. Implementing this item as written would have
  told operators to do something the CLI refuses.

  The real mode-awareness is about **which statement governs delivery**:
  `security log source-interface` is a forwarding-plane knob that never accepts
  fxp0, while in `mode event` the RE delivers over the system syslog path where
  `system syslog source-address` applies. Juniper's CLI reference scopes the
  fxp0 prohibition to stream mode, so the CLI is stricter than the docs; both
  facts are now in the skill.

  Also delivered: UDP/TCP/TLS stream transport with `tls-profile` (and the
  `SSL profile must be defined under [services ssl initiation profile]`
  rejection); the `show security log transport` 25.4R1+ gate, **with the
  measured caveat that it returns empty under `mode stream` on 25.4 and 26.2**
  while `show security log statistics` returns real counters; explicit approval
  now required before generating a test event, with a passive alternative
  preferred; and the three authoritative Juniper sources in package metadata.

- [ ] **Independent technical review of `srx-syslog-logging` remains open.**
  This work was expansion and live validation, not review. The README review
  count stays 26/29 and the skill is still listed as not independently
  reviewed.

- [ ] Unresolved from the validation: why `show security log transport` reports
  nothing under `mode stream` on 25.4R1.12 and 26.2R1.7. Needs either
  documentation on the counter's scope or an activated `mode event`
  configuration, which was outside the read-only + `commit check` authorization.

### P1 — repair documentation drift — COMPLETE 2026-09-11

All five items landed. See CHANGELOG 1.5.0, "Documentation integrity and
inventory enforcement".

- [x] Correct README inventory values — badge `25/29` -> `26/29`; installer
  help block reconciled against real `./install.sh --help` output (`24` -> `29`);
  the `~8,400` literal replaced with a pointer to
  `scripts/check-skill-packages.py`, which reports the measured figure
  (9,719 today) so the number cannot go stale again. The "four vendors"
  statement was deliberately kept — Firepower is a second Cisco grammar.
- [x] Update `QUALITY.md` to say five schema copies are checked.
- [x] Update `skills/SHARED-SCHEMA.md` and all five copied schema preambles to
  list five parsers and include `parsing-firepower-configs` in the
  synchronization instructions.
- [x] Modernize all five parser READMEs — per-runtime invocation and
  installation, `agents/openai.yaml` and `references/runtime-intake.md` added
  to every file tree, Firepower fixture corrected to
  `fixture-minimal-input.md`.
- [x] Release metadata: VERSION 1.5.0 published as tag v1.5.0. v1.4.0 was
  deliberately not tagged retroactively; its CHANGELOG section remains.

### P2 — strengthen automated documentation checks — COMPLETE 2026-09-11

- [x] One authoritative inventory manifest: `skills/inventory.json`, validated
  by `scripts/check-inventory.py` against the directories on disk,
  `install.sh`, `check-installer.py`, the README badge and body counts, the
  parser and schema counts, and `install.sh --help`.
- [x] Duplicate inventory entries now fail validation. The duplicate
  `sd-onprem-proxmox-deploy` hidden by the `frozenset` in
  `scripts/check-skill-packages.py` is gone; that script reads the manifest.
- [x] Markdown link checker: `scripts/check-markdown-links.py`. It ignores
  fenced blocks and inline code by design — the historical plans embed
  snippets whose link targets belong to README.md at the repository root, so
  "repairing" them against the plan's own directory corrupts the instruction.
  No repairs were needed; the repository has zero broken navigational links.
- [x] `shellcheck` added to linting as `just shell`, included in `guard`.
  Seven SC2207 sites use `read -r -a` or a read-loop helper as the producer
  requires; three SC2076 sites use a literal `contains_element` helper rather
  than unquoted regexes over filesystem paths.
- [x] `just security` scope clarified in QUALITY.md: Trivy runs all three
  scanners but only the secret scanner has anything to act on here.

#### Follow-ups opened by this work — COMPLETE 2026-09-11

- [x] `check-installer.py` now exercises `--all -y --dir`, rejection of an
  unknown `--family` and an unknown `--skill`, and the `--all` uninstall path.
  Both original defects were reproduced to prove the new assertions bite:
  collapsing the `--all` array assignment makes the installer exit 1 with an
  empty target, and making an unknown family return the parsers list trips
  "unknown installer family was not rejected". Both previously passed.
- [x] `check-markdown-links.py` parses balanced and escaped parentheses in
  destinations, strips `?query` as well as `#fragment`, and matches a
  destination on the line following its label. 62 tests, each gap covered in
  both directions. The link count is unchanged at 101, as expected — none of
  the three constructs occurs in this repository.

  Matching across a run rather than a line means the scan can walk past text,
  so the parser is built around two rules: a rejected candidate resumes inside
  its own opening bracket and can never skip what follows, and each part of a
  link is bounded the way CommonMark bounds it rather than accepted loosely.
  Seven review rounds went into those bounds and every finding was the same
  shape — malformed input hiding or inventing a link. **This was stopped
  deliberately, not because the surface was exhausted.** Every repository link
  is a plain `[text](path.md)`; not one finding across those rounds
  corresponded to anything in this repository or to anything a person would
  plausibly write. Treat further adversarial Markdown edge cases as out of
  scope unless a real document trips one.
- [x] The inventory is derived rather than compared. `check-installer.py`
  loads its families from `skills/inventory.json` at runtime, so that copy is
  gone. `install.sh` cannot derive at runtime — it is curl-able standalone and
  `--list` works before anything is downloaded — so its arrays are generated
  by `scripts/sync-installer-inventory.py`, whose `--check` mode runs in
  `just lint`. The now-circular manifest-versus-`check-installer.py`
  comparison was removed rather than left as dead weight.

### P3 — close known package review debt — COMPLETE 2026-09-12

- [x] Re-source and validate `parsing-firepower-configs`. Cisco's documentation
  is retrievable again; the obsolete "403 Forbidden / inaccessible" statement is
  replaced with the guides actually retrieved on 2026-09-12 —
  [verification record](docs/skill-tests/2026-09-12-parsing-firepower-configs-documentation-verification.md).
  Pagination, expansion, endpoint families, policy inheritance and the FMC/FDM
  structural differences are now documentation-verified with citations.
  **Literal objects remain `[unverified]`** along with mixed reference/literal
  containers and some endpoint families — those need a live FMC/FDM or
  sanitized API Explorer exports, which were not available. Unverified markers
  went from 14 to 8: six upgraded on evidence, eight deliberately retained.

- [x] `firewall-best-practices-audit` follow-ups (1.2.0 -> 1.3.0):
  `SEC-NAME-ACTION-MISMATCH` detects rule names that contradict their action,
  with whole-word matching that excludes negations ("do-not-deny") and names
  containing both verbs; `SEC-PLAINTEXT-FEED-TRANSPORT` detects threat feeds
  fetched over `http://`, definitive for SRX and classified per-platform
  elsewhere. Both proven to fire on contradictions and stay silent on clean and
  edge-case inputs —
  [test record](docs/skill-tests/2026-09-12-audit-name-action-and-plaintext-feed-checks.md).

### Recommended next new skill

- [ ] Build `firewall-policy-path` after the P0 correction and P3 review debt
  are closed. P1 and P2 can proceed in parallel.
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

### Review verification record

- Original review: `just fmt`, `just lint`, `just test`, `just guard`,
  `just security`, `just release-check`, and `just e2e` exited successfully on
  2026-09-11, covering 189 Python tests, 29 package inventories, 29 runtime
  intake catalogs, and byte-identity checking of five schema copies.
- Supplemental `shellcheck install.sh scripts/*.sh` exited 1 with ten warnings.
  All ten are now resolved and shellcheck runs as `just shell` inside `guard`.
- After the P1/P2 work: `just lint`, `test`, `shell`, `guard`, `security`,
  `release-check` and `e2e` all exit 0, now additionally running the inventory
  manifest check, the Markdown link check, and their unit suites.

## Tracked validation

- [Issue #15: Re-run `firewall-best-practices-audit` v1.1 against policy-light
  and policy-heavy SRX devices](https://github.com/fastrevmd-lab/fwskillsshare/issues/15)
  defines the read-only test scope, safety boundary, evidence to collect, and
  acceptance criteria. The prior result is documented in
  [the 2026-06-29 vSRX production audit](docs/skill-tests/2026-06-29-vsrx-production-audit.md).
  The live-device rerun was completed on 2026-07-31 —
  [live SRX audit](docs/skill-tests/2026-07-31-firewall-best-practices-audit-live-srx.md).
  It closed the outstanding acceptance item and surfaced four follow-ups.
  Modeling `security dynamic-address` and extracting
  `match dynamic-application` are complete; the rule-name-versus-action and
  feed-transport checks remain under P3 above.

### vSRX validation gate — `srx-idp`

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


**Unowned scope:** Branch SRX (SRX300 series, SRX400 series) zone-pair policy
design. `srx-initial-setup` targets Branch platforms and reaches the
baseline-policy stage; when a zone-pair exception applies, that stage routes to
`srx-policy`. But `srx-policy` scopes itself to "non-Branch SRX platforms" and
disclaims Branch. Until this is closed, operators on Branch platforms needing
zone-pair policy design it manually, and both `srx-initial-setup` and this file
say so rather than implying coverage.

**Decision: narrow `srx-policy`'s exclusion. Do not build a separate
`srx-branch-policy` skill.** Blocked on SRX345 hardware validation — see below.

Investigated 2026-08-24. Findings:

- The `non-Branch` scope has been present since `srx-policy`'s first commit
  (`95d247e`) with **no recorded rationale anywhere** — no design document, no
  reference file, no commit message explains it. It appears in exactly two
  places: the `description` frontmatter field and `SKILL.md`'s Overview.
- No Branch hardware has ever been tested against `srx-policy`. Its validation
  records name vSRX and unspecified devices only, so the exclusion is not
  backed by a negative result either.
- Juniper documentation (retrieved 2026-08-24) records **no** Branch exclusion
  for policy structure. Global policies, zone-pair policies, and unified
  policies with `match dynamic-application` are documented for "SRX Series"
  generically. Unified policies — the most advanced construct — have been
  Branch-supported since Junos 18.2R1.
- Address and application objects, rule order, default-deny, session logging,
  and hit counts show no documented Branch-specific difference.
- The NGFW service-attachment features are all Branch-available and
  license-gated, by the same gates that apply to higher-end SRX: AppID/AppFW,
  NGWF, EWF, SecIntel, ATP, and IDP/IPS. UTM is in fact **Branch-oriented** —
  Juniper publishes "Understanding UTM for Branch SRX Series".
- A separate Branch policy skill would duplicate 90%+ of identical content and
  runs against this repository's own rule in `AGENTS.md` to prefer
  consolidating overlapping skills over adding them. Two policy skills would
  also split lexical discovery for the same question.

**What closing it requires:** widen `srx-policy`'s stated scope to cover Branch
for core policy design, add a licensing/feature-gate reference section, and
qualify service-attachment claims per platform. Because that widens a mature
skill's scope, the Branch claims must be labelled documentation-sourced until
they are exercised on the SRX345. **Do not widen the scope before that
validation** — widening on documentation alone, in a skill that has never seen
Branch hardware, is the overclaiming this repository forbids.

The absence of a recorded rationale is evidence the exclusion was never
justified, not proof it was wrong; the original author may simply have never
validated Branch and hedged. The SRX345 settles it either way.

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
