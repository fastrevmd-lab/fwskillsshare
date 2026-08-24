# Firewall Skills Roadmap

This file tracks proposed skills that have not yet been built. Completed work
belongs in the repository history and release notes; actionable validation work
is tracked in GitHub issues.

## Tracked validation

- [Issue #15: Re-run `firewall-best-practices-audit` v1.1 against policy-light
  and policy-heavy SRX devices](https://github.com/fastrevmd-lab/fwskillsshare/issues/15)
  defines the read-only test scope, safety boundary, evidence to collect, and
  acceptance criteria. The prior result is documented in
  [the 2026-06-29 vSRX production audit](docs/skill-tests/2026-06-29-vsrx-production-audit.md).
  The live-device rerun was completed on 2026-07-31 —
  [live SRX audit](docs/skill-tests/2026-07-31-firewall-best-practices-audit-live-srx.md).
  It closed the outstanding acceptance item and surfaced four follow-ups: model
  `security dynamic-address` in the parser, extract `match dynamic-application`,
  add a rule-name-versus-action check, and add a feed-transport check.

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

1. [ ] `palo-operational` (PAN-OS operational playbook)
   - Add Palo Alto operational depth comparable to the SRX operational skills.
   - Author and validate against the available Palo VM.
   - Cover security and NAT policy structure, App-ID and security profiles,
     decryption, zones and interfaces, candidate configuration and commits,
     logging, and CLI or operational verification.

2. [ ] `firewall-policy-path`
   - Explain why a flow is allowed or blocked from its source, destination,
     port, and application.
   - Trace zone selection, matching policy, NAT, and profile actions through a
     parsed configuration.
   - Complement `firewall-best-practices-audit` with an operational
     troubleshooting workflow.

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

## Suggested creation order

1. `cjis-ngfw-compliance`
2. `glba-ftc-safeguards-ngfw-compliance`
3. `nerc-cip-ngfw-compliance` or `iec62443-ngfw-compliance`, depending on
   whether utility and energy or broader OT is the next priority
4. `gdpr-ngfw-compliance`
5. `fedramp-ngfw-compliance`
