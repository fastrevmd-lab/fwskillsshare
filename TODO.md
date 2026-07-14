# Recommended Skills TODO

Recommended future skills for this firewall / NGFW skill collection. The
[Tooling & Operational Skills](#tooling--operational-skills-non-compliance)
section covers non-compliance skills; the rest tracks compliance playbooks.

## PRIORITY PROJECT: firewall-best-practices-audit v1.1 — SRX coverage gaps

Completed 2026-06-29 — see docs/superpowers/plans/2026-06-29-firewall-best-practices-audit-v1.1.md.

Surfaced by testing the v1.0 audit skill against a real device (`vSRX-Production`,
Junos 25.4R1, via rust-junosmcp, 2026-06-29). The device was control-plane-hardened
but **policy-light** (zero `security policies`, only `policy-rematch`), and the audit
produced just **1 finding from its 30-check catalog** — exposing that the skill (and
the `parsing-*` intermediate schema it consumes) models a *stateful policy rulebase*
and is blind to where SRX security actually lives. Group these as one v1.1 effort
(audit-skill checks + schema extensions to feed them).

Schema/parser extensions (prereqs — most checks need new fields):
- [x] Parse `system.services.ssh` options (root-login, protocol/ciphers, connection/rate-limit) into the schema.
- [x] Parse `zones[].host_inbound` (per-zone host-inbound-traffic system-services/protocols) into the schema.
- [x] Parse `security.screen` / IDS options (DoS protections) into the schema.
- [x] Carry stateless RE-protection firewall filters (`firewall { family inet filter }`, e.g. lo0 input) at least as a presence flag, not only `residual_raw`.
- [x] Parse auth/AAA hardening: `system.login` retry-options/lockout, password policy, `root-authentication` presence, admin users + key types.

New audit checks (v1.1):
- [x] **SEC-SSH-ROOT-LOGIN** — `ssh root-login allow` (and weak SSH ciphers/no rate-limit) — High.
- [x] **SEC-SERVICES-UNREFERENCED** — UTM/IDP/SecIntel/AAMW (or any security service) configured but attached to no policy → inert security stack — High.
- [x] **SEC-ZONES-NAT-NO-POLICY** — zones/NAT present but no `security_policies` reference them (NAT translating flows no policy permits) — High.
- [x] **SEC-EMPTY-POLICYSET** — `security_policies = []`: emit an explicit coverage warning instead of staying silent; distinguish "default-deny by design" from "partial config / policies in a logical-system/tenant" — Medium.
- [x] **SEC-HOST-INBOUND-EXPOSURE** — management/sensitive host-inbound-traffic on untrusted/data zones (broaden beyond the narrow SEC-MGMT-DATAZONE) — Medium.
- [x] **SEC-NO-SCREEN** / **OPS-LOG-COMPLETENESS** — untrust zone with no screen bound; security-log stream/host completeness — Medium.
- [x] **SEC-AUTH-HARDENING** — missing password policy/login lockout; weak admin auth — Medium/Low.
- [x] **IPv6/dual-stack posture** — flag inet6 interfaces with no corresponding v6 controls — Low.
- [x] Make `SEC-NO-DENY-ALL` credit/account for SRX implicit-deny vs. the recommended explicit *logged* deny-all (visibility, not just enforcement).

Process note: re-run the real-device test (rust-junosmcp `vSRX-Production` and a
policy-heavy device) after v1.1 to confirm the catalog now exercises >1 check.
Full test write-up: `docs/skill-tests/2026-06-29-vsrx-production-audit.md`.

## Tooling & Operational Skills (non-compliance)

These consume the existing `parsing-*` intermediate schema (or vendor configs)
to realize the "cross-vendor comparison, conversion, and unified auditing" the
parsers were built for, plus vendor-operational breadth.

1. [x] `firewall-best-practices-audit` — **next up (brainstorming).** Vendor-neutral
   rulebase hardening / security-hygiene review over a parsed config: any-any and
   overly broad rules, shadowed/redundant/unused rules, missing deny-all,
   no-logging rules, plaintext management (telnet/http), dangerous exposed
   services, object/rule sprawl, weak VPN/crypto. The "unified auditing" payoff;
   stays framework-agnostic and does not map findings to control IDs. Highest
   recurring-use frequency.

2. [x] `firewall-config-conversion` — Cross-vendor migration via the intermediate
   schema (schema → target vendor; e.g. ASA→FTD, ASA/FortiGate→Palo, any→SRX).
   The marquee use of the shared schema. Pair with a conversion fidelity report
   (what did not translate cleanly / manual follow-ups). High per-event value.

3. [x] `firewall-config-diff` — Cross-vendor (via schema) or same-vendor snapshot
   comparison: rule parity, drift, HA-pair consistency, and pre/post-migration
   validation. Small; the validation half of `firewall-config-conversion`.

4. [ ] `palo-operational` (PAN-OS operational playbook) — Vendor-operational depth
   for Palo Alto. Author/validate against the
   available Palo VM. Likely areas: security/NAT policy structure, App-ID /
   security profiles, decryption, zones/interfaces, commit/candidate config,
   logging, and CLI/operational verification.

5. [ ] `firewall-policy-path` — Policy-path / "why is this traffic allowed or
   blocked" analysis: given a flow (src/dst/port/app) and a parsed config, trace
   zone selection, matching rule, NAT, and profile actions to explain the outcome.
   Operational troubleshooting companion to the audit skill.

## Recommended Compliance Skills

Future compliance playbooks for this collection.

## Recommended next skills

1. [ ] `cjis-ngfw-compliance`
   - Law-enforcement and public-sector environments handling Criminal Justice Information.
   - Cover CJI segmentation, encryption, advanced authentication/MFA, remote access, logging, agency/vendor connectivity, wireless/mobile access, and CJIS Security Policy evidence.

2. [ ] `glba-ftc-safeguards-ngfw-compliance`
   - Financial institutions, lenders, insurance-adjacent organizations, and fintech.
   - Cover customer information systems, access controls, encryption, monitoring, vendor access, incident response, and risk-assessment linkage under GLBA / FTC Safeguards Rule expectations.

3. [ ] `nerc-cip-ngfw-compliance`
   - Electric utility / bulk electric system environments.
   - Cover Electronic Security Perimeters, BES Cyber Systems, Interactive Remote Access, access control, logging, change management, and mappings to CIP-005, CIP-007, CIP-010, and CIP-011.
   - Use strict NERC terminology and avoid generic IT-security shortcuts.

4. [ ] `iec62443-ngfw-compliance`
   - Industrial / OT firewall and segmentation work.
   - Cover zones and conduits, security levels, industrial DMZs, IT/OT segmentation, remote vendor access, legacy-system compensating controls, and firewall evidence.

5. [ ] `gdpr-ngfw-compliance`
   - Privacy/security-of-processing support.
   - Focus on how firewalls support GDPR Article 32 security of processing, data minimization by access restriction, breach detection/evidence, processor access, and third-party connectivity.
   - Avoid overclaiming “GDPR compliant firewall.”

6. [ ] `fedramp-ngfw-compliance`
   - Federal/cloud security work.
   - Map NGFW/firewall controls to NIST SP 800-53 Rev. 5 families such as AC, AU, CM, CP, IR, SC, SI, and RA.
   - Larger lift, but highly reusable for cloud and public-sector environments.

## Lower priority / conditional

- [ ] `sox-ngfw-compliance`
  - Consider only if there is a specific financial-reporting-system network-control use case.
  - SOX can involve firewall evidence around financially relevant systems, but it is less network-control-specific than PCI, HIPAA, CMMC, CIS, ISO 27001, SOC 2, CJIS, NERC CIP, or IEC 62443.

## Suggested creation order

1. `cjis-ngfw-compliance`
2. `glba-ftc-safeguards-ngfw-compliance`
3. `nerc-cip-ngfw-compliance` or `iec62443-ngfw-compliance`, depending on whether utility/energy or broader OT is the next priority
4. `gdpr-ngfw-compliance`
5. `fedramp-ngfw-compliance`
