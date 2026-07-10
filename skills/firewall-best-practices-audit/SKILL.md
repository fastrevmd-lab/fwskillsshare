---
name: firewall-best-practices-audit
description: Audit normalized Cisco, Fortinet, Palo Alto, and Juniper firewall rulebases for security hygiene. Use when finding any-any, shadowed, redundant, or orphaned rules, missing deny or logging, exposed management, weak VPN crypto, hardening gaps, or unused objects. Parse raw configs first.
version: 1.1.2
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [firewall, ngfw, audit, best-practices, hardening, rulebase-review, security-hygiene, shadowed-rules, least-privilege, logging, vpn-crypto, object-cleanup, vendor-neutral, ssh-hardening, host-inbound, screens, device-hardening, ipv6-posture]
    related_skills: [parsing-cisco-configs, parsing-fortinet-configs, parsing-palo-configs, parsing-srx-configs, firewall-config-conversion, firewall-config-diff, pci-ngfw-compliance, hipaa-ngfw-compliance, cmmc-nist-800-171-ngfw-compliance, cis-controls-ngfw-compliance, iso27001-ngfw-compliance, soc2-ngfw-compliance]
---

# Firewall Best-Practices Audit

## Overview

Use this skill to audit a firewall or NGFW rulebase for security and operational hygiene, vendor-neutrally, over the `parsing-*` intermediate JSON schema. The audit reads normalized `security_policies`, `nat_rules`, address/service objects and groups, `zones`, `vpn_tunnels`, `system`, and `admin_users`, then emits prioritized findings across the security and operational check families (full catalog: `references/check-catalog.md`). Each finding carries a severity, a confidence, the affected references, why it matters, and remediation.

This skill is deliberately framework-agnostic. It answers "is this rulebase hardened by general best practice" — not "does this satisfy PCI/HIPAA/CMMC/CIS/ISO/SOC 2." That mapping is the job of the `*-ngfw-compliance` skills, which take a framework's control IDs and produce assessor-ready evidence. This skill stays in the lane of general hygiene: it never cites a control ID and never claims an environment is compliant. Use it before or alongside a compliance review, or on its own when someone just wants the rulebase cleaned up and tightened.

The audit reports findings, not verdicts. It never claims a config is "secure" — at best it reports "no in-scope findings" with caveats about what could not be checked (for example, hit-count or last-used data that the static schema does not carry). The output is decision-grade: a short posture line, a severity tally, the list of checks that were skipped for missing data, and a prioritized list of top fixes.

## Scope and routing

Operate on the normalized `parsing-*` schema; do not hand-audit raw vendor text when a parser exists. Route framework mappings to the matching compliance skill, migrations to `firewall-config-conversion`, and parity or drift comparisons to `firewall-config-diff`.

## Input Handling

Route on what you were given:

- **Parsed intermediate schema** (the vendor-neutral JSON produced by any `parsing-*` skill; the schema definition lives in the `parsing-srx-configs` skill) — audit directly. Read `metadata.source_vendor` to drive vendor-specific remediation snippets. `metadata.source_vendor` is the canonical schema field; for robustness also accept a legacy `metadata.vendor` key if a non-conformant parse provides one — read whichever is present.
- **Raw config** — identify the vendor from the syntax, run the matching `parsing-*` skill (`parsing-cisco-configs`, `parsing-fortinet-configs`, `parsing-palo-configs`, `parsing-srx-configs`) to produce the intermediate schema, then audit the result. Never re-implement parsing in this skill. For a single live device pulled via NETCONF/MCP, parsing-srx-configs permits auditing from the extracted hierarchical sections without full schema emission — still route the extraction through that skill; never hand-parse raw text ad hoc.
- **Unsupported vendor with no parser** — say so plainly: there is no parser for this vendor, so a structured audit cannot be produced; offer to audit a manually-normalized schema or to reason about pasted excerpts without finding IDs.

As of v1.1 the audit also reads `system.ssh`, `system.auth`, `system.control_plane_protection`, `zones[].screen`, and `security_services` to cover device-plane hardening (SSH/management hardening, password/lockout policy, screen presence, and unreferenced security services); any of these fields that is absent simply skips its dependent check.

Graceful degradation: the schema is static, so some checks have no input (for example, anything depending on hit counts or last-used timestamps, and any check needing a field the source parser did not populate). When a field is missing, skip the dependent check rather than guessing, and record every skipped check in the audit summary so the gap is visible.

## Severity & Confidence

| Severity | One-line criterion |
|----------|--------------------|
| Critical | Direct, exploitable exposure — any-any-allow across a trust boundary, dangerous service open to untrust, plaintext admin reachable externally, broken/keyless VPN. |
| High | Strong weakness — overly permissive allow, shadowed rules hiding later policy, weak VPN/IKE crypto (DES/3DES/MD5/SHA1/DH<14), no logging on permit-to-untrust. |
| Medium | Material hygiene gap — missing explicit deny-all, redundant/overlapping rules, oversized any in one field, missing logging on internal allows. |
| Low | Minor hardening or correctness nit — overlapping objects, weak naming, narrow over-broad object. |
| Info | Operational cleanup with no direct risk — unused/duplicate objects, oversized groups, missing descriptions, consolidation opportunities, disabled rules. |

This table is the general scale with context-adjusted examples; the per-check default severities in `references/check-catalog.md` are the authoritative defaults (a check's catalog severity wins over any example here, since real severity is adjusted by logging, scope, and trust-boundary context).

Confidence is one of two values:

- **definitive** — the schema fully supports the conclusion (e.g. `src_addresses` and `dst_addresses` both contain `any` with `action: allow`).
- **heuristic** — the conclusion depends on something the schema does not fully guarantee. Downgrade to heuristic when rule order is incomplete or ambiguous (shadow/redundancy claims), when object references are unresolved (orphan/unused claims), or when NAT could change real exposure. Label these as heuristic so reviewers verify before acting.

## Audit Workflow

1. **Establish input + vendor.** Confirm you have the intermediate schema (parse first if raw). Read `metadata.source_vendor` and `metadata` counts to size the audit.
2. **Resolve objects and zones.** Expand `address_groups`, `service_groups`, and `application_groups` to members; map `security_policies` `src_zones`/`dst_zones` to `zones` and their interfaces; note `nat_rules` that change effective exposure. Flag references that do not resolve (drives heuristic confidence later).
3. **Run the security checks.** Permissiveness/any-any, shadow/redundancy/overlap, missing deny-all and logging, dangerous exposed services, plaintext management, weak VPN/IKE/IPsec crypto. Also run the v1.1 device-plane families: SSH/management hardening (`SEC-SSH-ROOT-LOGIN`), security-services-unreferenced (`SEC-SERVICES-UNREFERENCED`), zone/NAT-without-policy (`SEC-ZONES-NAT-NO-POLICY`) plus the empty-policyset coverage warning (`SEC-EMPTY-POLICYSET`), host-inbound exposure (`SEC-HOST-INBOUND-EXPOSURE`), screen presence (`SEC-NO-SCREEN`), auth hardening (`SEC-AUTH-HARDENING`), control-plane/RE-filter protection (`SEC-NO-CONTROL-PLANE-PROTECTION`), IPv6 posture (`SEC-IPV6-POSTURE`), and remote-log completeness (`OPS-LOG-COMPLETENESS`). See `references/check-catalog.md` for the full check definitions, schema fields, and severity rationale.
4. **Run the operational checks.** Unused/duplicate objects, oversized groups, naming/description gaps, rule consolidation, disabled-rule cleanup. Also from `references/check-catalog.md`.
5. **Assign severity + confidence.** Apply the rubric above; downgrade to heuristic where rule order or object resolution is incomplete or NAT may alter exposure.
6. **Attach remediation.** Give vendor-neutral guidance plus a concrete snippet in the source vendor's syntax. See `references/remediation-patterns.md` for per-vendor fix patterns keyed by finding category.
7. **Produce the output.** Emit each finding with the Finding template, then the Audit Summary with the posture line, severity tally, skipped checks, and prioritized top fixes.

## Reference Material (load on demand)

- `references/check-catalog.md` — full catalog of security + operational checks (id, what it detects, schema fields, severity rationale).
- `references/remediation-patterns.md` — per-vendor (Cisco/Palo/FortiGate/SRX) fix snippets keyed by finding category.
- `references/example-audit.md` — a worked audit against a parsing-* fixture.

## Output Templates

### Finding

```text
[<id>] <CRITICAL|HIGH|MEDIUM|LOW|INFO> (<definitive|heuristic>) — <title>
Category: <security|operational> / <subcategory>
Affected: <rule names/IDs, object names, zones>
Why it matters: <1–3 lines>
Remediation: <vendor-neutral guidance>
Fix (<source-vendor>):
  <concrete snippet in the source vendor's syntax>
```

### Audit Summary

```text
Posture: <one line; never "secure" — say "no in-scope findings" with caveats>
Findings: Critical <n>  High <n>  Medium <n>  Low <n>  Info <n>
Checks skipped (no data): <e.g. hit-count-dependent checks>
Top fixes (prioritized):
  1. <id> — <one line>
  2. <id> — <one line>
```

## Common Pitfalls

- Claiming a config is "secure" or "compliant" — only report "no in-scope findings" with caveats about what could not be checked.
- Mapping findings to PCI/HIPAA/etc. — that is the compliance skills' job; stay framework-agnostic and cite no control IDs.
- Re-implementing parsing instead of delegating to the matching `parsing-*` skill.
- Reporting heuristic findings (possible shadow) as definitive when rule order or object references are incomplete.
- Auditing only the internet edge — include internal, management, VPN, and inter-zone rules.
- Ignoring NAT when reasoning about real exposure — a translated address can change what a rule actually permits.
- Flagging disabled rules as active risk — note them as cleanup, not exposure.
- Treating an unreferenced object as a finding without confirming the schema captured all references.
- Putting real secrets or PSKs in example output — always redact.
- Silently dropping checks when a schema field is missing — list them as skipped in the summary.

## Verification Checklist

- [ ] Confirm input type (parsed schema vs raw config) and source vendor.
- [ ] For raw config, the matching parsing-* skill was run first.
- [ ] Every finding has id, severity, confidence, affected refs, rationale, remediation.
- [ ] Remediation includes vendor-neutral guidance + a source-vendor snippet.
- [ ] Heuristic findings are labeled; definitive vs heuristic is correct.
- [ ] Skipped checks (missing schema fields) are listed in the summary.
- [ ] Output makes no "secure"/"compliant" claim and no compliance-framework mapping.
- [ ] No real secrets in any snippet.
