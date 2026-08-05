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
