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

### P0 — correct technical guidance

- [ ] Expand and independently review `srx-syslog-logging`.
  - Make source-interface guidance mode-aware. The current blanket statement
    that security logs always require a revenue interface is documented only
    for `mode stream`; `event` uses the control plane and `stream-event` uses
    both planes.
  - Cover UDP, TCP, and TLS stream transport, including `tls-profile` and
    transport-specific verification.
  - Prefer `show security log transport` on Junos 25.4R1 and later for
    delivered and undelivered transport counters.
  - Require explicit approval before generating a commit as a test event, or
    use an already-occurring non-mutating event.
  - Add the authoritative Juniper sources to the package metadata:
    - [Security log modes](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-mode-security-logging.html)
    - [Security log stream transport](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-stream-security-log.html)
    - [`show security log`](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-log.html)
  - Before live validation, create or link a GitHub issue that records the
    read/write boundary, test events, collector handling, cleanup, evidence,
    and acceptance criteria.
  - Validate the corrected decision tree on vSRX and at least one Branch SRX,
    recording platform, Junos release, mode, routing instance, interface,
    transport, and collector evidence.

### P1 — repair documentation drift

- [ ] Correct README inventory values.
  - Review badge: `25/29` -> `26/29`.
  - Installer help example: `Install all 24 skills` -> `Install all 29 skills`.
  - Combined description surface: `~8,400` -> measured `9,719`, or remove the
    mutable literal and point readers to `scripts/check-skill-packages.py`.
  - Intermediate-schema wording: four parsers -> five parsers. Keep the
    separate "four vendors" statement because Firepower is another Cisco
    grammar, not a fifth vendor.
- [ ] Update `QUALITY.md` to say that five schema copies are checked.
- [ ] Update `skills/SHARED-SCHEMA.md` and every copied schema preamble to list
  all five parsers and include `parsing-firepower-configs` in the synchronization
  instructions.
- [ ] Modernize all five parser READMEs.
  - Describe Claude Code, Codex, and Hermes installation/invocation.
  - Include `agents/openai.yaml` and `references/runtime-intake.md` in each file
    tree.
  - Correct the Firepower fixture name from `fixture-minimal-input.json` to
    `fixture-minimal-input.md`.
- [ ] Resolve release metadata ambiguity: the repository declares 1.5.0 while
  the latest tag and GitHub release are v1.3.0. Either publish v1.5.0 or move
  post-v1.3.0 entries beneath an explicit `Unreleased` heading.

### P2 — strengthen automated documentation checks

- [ ] Add one authoritative inventory manifest and derive or validate the
  package total, family counts, reviewed count, parser/schema count, and
  installer help examples from it.
- [ ] Make duplicate inventory entries fail validation. Remove the duplicate
  `sd-onprem-proxmox-deploy` entry currently hidden by the `frozenset` in
  `scripts/check-skill-packages.py`.
- [ ] Add a Markdown link checker for current user-facing documentation. Repair
  the broken skill-table links in the historical audit, conversion, and diff
  implementation plans when those plans are included in the check.
- [ ] Add `shellcheck` to linting or document intentional suppressions.
  - Replace seven SC2207 command-substitution array assignments with `mapfile`
    or another whitespace-safe implementation.
  - Replace or explicitly justify the three SC2076 quoted `=~` membership
    tests.
- [ ] Clarify the `just security` result: Trivy currently scans secrets, but it
  finds no supported dependency or configuration files for vulnerability or
  misconfiguration scanning.

### P3 — close known package review debt

- [ ] Re-source and validate `parsing-firepower-configs`.
  - Replace the obsolete statement that Cisco's official documentation is
    inaccessible where the current documentation is now retrievable.
  - Verify pagination, expansion, endpoint families, literal objects, policy
    inheritance, and FMC-versus-FDM structural differences against current
    official documentation and sanitized FMC/FDM API Explorer exports.
  - Retain an explicit unsupported or unverified classification wherever live
    evidence is unavailable.
  - Starting reference: [Cisco FMC REST API object model](https://www.cisco.com/c/en/us/td/docs/security/firepower/10-0/API/REST/firepower_management_center_rest_api_quick_start_guide_10_0/Objects_In_The_REST_API.html).
- [ ] Add the remaining `firewall-best-practices-audit` follow-ups:
  - Detect rule names that contradict their configured action.
  - Detect plaintext threat-feed transport and report it with appropriate
    platform and parser confidence.

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

- `just fmt`, `just lint`, `just test`, `just guard`, `just security`,
  `just release-check`, and `just e2e` exited successfully on 2026-09-11.
- The validation included 189 Python tests, 29 package inventories, 29 runtime
  intake catalogs, and byte-identity checking of five schema copies.
- Supplemental `shellcheck install.sh scripts/*.sh` exited 1 with the ten
  warnings recorded under P2; Bash syntax validation passed.

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
