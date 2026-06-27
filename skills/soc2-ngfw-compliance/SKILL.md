---
name: soc2-ngfw-compliance
description: Use when researching, designing, auditing, or explaining how a next-generation firewall or firewall estate can support SOC 2 Trust Services Criteria for service organizations, SaaS platforms, MSPs, and cloud providers. Covers security, availability, confidentiality, privacy-supporting network controls, logical access, system operations, change management, risk mitigation, logging/monitoring, vendor access, incident response, audit evidence, operating effectiveness samples, and firewall description/tag markers. Emphasizes that SOC 2 reports cover system controls over a period, not certification of an NGFW product alone.
version: 0.1.0
author: Hermes Agent
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [soc2, trust-services-criteria, compliance, firewall, ngfw, audit, evidence, logical-access, system-operations, change-management, availability, confidentiality]
    related_skills: [srx-policy, srx-nat, parsing-srx-configs, parsing-palo-configs, parsing-fortinet-configs, parsing-cisco-configs, pci-ngfw-compliance, hipaa-ngfw-compliance, cmmc-nist-800-171-ngfw-compliance, cis-controls-ngfw-compliance, iso27001-ngfw-compliance]
  sources:
    - title: "SOC Suite of Services"
      author: AICPA & CIMA
      url: https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services
      retrieved: "2026-06-27"
    - title: "Trust Services Criteria"
      author: AICPA & CIMA
      url: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
      retrieved: "2026-06-27"
---

# SOC 2 NGFW Compliance Research

## Overview

Use this skill to answer questions like “what firewall evidence do we need for SOC 2?” or “how should our NGFW controls map to Trust Services Criteria?” The core answer is: SOC 2 reports cover controls over a defined system, criteria, and period of time. A firewall or NGFW is not “SOC 2 compliant” by itself. It can support the service organization’s controls for logical access, system operations, change management, risk mitigation, monitoring, incident response, availability, confidentiality, and privacy-supporting restrictions when it is configured, monitored, reviewed, and evidenced consistently.

SOC 2 work is especially common for SaaS, MSP, MSSP, cloud-hosted services, platforms that process customer data, and organizations preparing for Type I or Type II examinations. Firewall evidence must align to the service description, system boundaries, applicable Trust Services Categories, control design, control owners, and operating effectiveness samples.

Treat this as audit-readiness and control-mapping guidance, not legal advice and not an auditor’s opinion. For formal reporting, defer to the organization’s CPA firm, audit lead, control owners, legal/compliance team, and customer commitments.

## When to Use

Use this skill when the user asks about:

- SOC 2 Type I or Type II firewall, NGFW, VPN, WAF, IDS/IPS, SASE/ZTNA, security group, or cloud network controls
- AICPA Trust Services Criteria, especially common criteria around logical access, system operations, change management, risk mitigation, and monitoring
- service organizations, SaaS platforms, MSP/MSSP environments, cloud providers, managed firewalls, production network boundaries, customer data, availability, confidentiality, or privacy support
- preparing firewall evidence for auditors: control descriptions, evidence requests, samples, screenshots, exports, logs, tickets, rule reviews, alerts, and exceptions
- assessing whether firewall policy, NAT, remote access, admin access, vendor access, change control, logging, or incident response evidence is SOC 2 ready
- adding concise SOC 2 evidence markers to firewall rules, NAT, zones, VPN entries, objects, security profiles, or external source-of-truth records

Do not use this skill as a substitute for parsing a raw firewall configuration. Load the relevant parser skill first, then use this skill to interpret SOC 2 implications.

## Baseline Interpretation

### What “SOC 2-Ready Firewall” Means

Use precise language:

- “This firewall estate supports controls that may be included in the SOC 2 system description and mapped to Trust Services Criteria.”
- “This design appears aligned with logical access, system operations, change management, monitoring, and availability/confidentiality objectives, subject to auditor and evidence review.”
- “Firewall evidence must show both design and operation for the examination period, especially for Type II reports.”

Avoid saying:

- “This NGFW is SOC 2 certified.”
- “The firewall makes the service SOC 2 compliant.”
- “A single screenshot is enough for a Type II control.”

### Scope, Criteria, and Report Type Come First

Before assessing firewall controls, establish:

1. report type: Type I design at a point in time or Type II design and operating effectiveness over a period;
2. Trust Services Categories in scope: Security is common to all SOC 2 reports; Availability, Confidentiality, Processing Integrity, and Privacy may be added;
3. system description boundaries, production services, customer data flows, cloud accounts, regions, and supporting systems;
4. whether firewall managers, cloud security groups, WAFs, VPN/ZTNA, identity, SIEM, monitoring, vulnerability management, and managed service providers are part of the system;
5. control matrix/control IDs used by the audit team;
6. evidence period, sample size expectations, and exceptions process.

If scope and criteria are unknown, provide a typical SOC 2 firewall evidence baseline and label assumptions.

## SOC 2 Criteria Mapping for Firewall Work

Use this practical mapping as a starting point. Exact criteria and points of focus should be verified against the current AICPA materials and the organization’s control matrix.

| SOC 2 area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| CC1 / control environment support | Defined owners, responsibilities, and governance for firewall controls | RACI, policy ownership, control matrix, training/acknowledgment records |
| CC2 / communication and information | Firewall controls documented and communicated through policies/procedures | Network security policy, change procedure, rule standard, evidence repository |
| CC3 / risk assessment | Network risks drive firewall requirements and exceptions | Risk register, threat model, exception/risk acceptance records |
| CC5 / control activities | Firewall rules, baselines, reviews, approvals, and alerts operate as control activities | Config exports, rule reviews, tickets, samples, approvals |
| CC6 logical and physical access | Restrict network, admin, remote, service, vendor, and customer-data access | Rulebase, VPN groups, MFA/AAA/RBAC, admin reviews, vendor access evidence |
| CC7 system operations | Monitor firewall/VPN/admin/threat events and respond to anomalies | SIEM logs, alert rules, triage records, incident tickets, daily/weekly reviews |
| CC8 change management | Authorize, test, approve, implement, and review firewall changes | Change tickets, diffs, approvals, emergency changes, rollback evidence |
| CC9 risk mitigation | Manage vendor, cloud, vulnerability, and continuity risks affecting firewall controls | Vendor reviews, vulnerability tickets, DR/failover tests, risk treatment |
| Availability category | Protect production availability with segmentation, DDoS/WAF paths, HA, backups, and DR | HA/failover evidence, backup/restore tests, monitoring alerts, capacity records |
| Confidentiality category | Restrict and monitor paths to confidential customer data | Segmentation rules, egress controls, encryption/VPN paths, data-flow diagrams |
| Privacy category support | Limit and monitor network access to personal information systems | Data-flow maps, access restrictions, logging, third-party access evidence |

## Assessment Workflow

### 1. Establish SOC 2 Scope and Control Matrix

Collect:

- system description and service boundaries;
- Trust Services Categories in scope;
- Type I or Type II report period;
- control matrix with control IDs and mapped criteria;
- network diagrams, data-flow diagrams, cloud architecture, and customer-data paths;
- production firewall/WAF/VPN/ZTNA/security-group inventory;
- firewall/network/security policies and procedures;
- audit evidence request list and sampling expectations.

Questions to answer:

- Which firewall controls are explicit controls in the matrix, and which are supporting evidence for broader controls?
- Which systems and customer data flows are in scope?
- Which service commitments mention availability, confidentiality, security, privacy, or incident response?
- Which providers operate or can access firewall controls?
- What evidence proves the control operated across the full period?

### 2. Build a Firewall-to-SOC 2 Matrix

For each firewall or enforcement point, capture:

- device/control name and platform/version;
- role: production perimeter, internal segmentation, cloud security group, WAF/WAAP, VPN/ZTNA, IDS/IPS, DNS/web security, management-plane enforcement;
- SOC 2 system boundary relationship;
- protected services and customer-data paths;
- control IDs and Trust Services Criteria mapping;
- control owner and reviewer;
- change ticket system and evidence repository;
- logging/SIEM destination, alert owner, retention;
- rule review cadence and last review;
- admin/vendor access review cadence;
- HA/DR/backup role;
- open exceptions, deviations, or audit findings.

Example:

```text
Firewall: PA-SAAS-PROD-EDGE
SOC 2 scope: Production SaaS platform, Security + Availability + Confidentiality
SOC 2 mapping: NET-01 / CC6, NET-02 / CC7, CHG-04 / CC8, AV-03 / Availability
Evidence: CHG-22119, SIEM-FW-PROD, RULE-REVIEW-2026Q2, VPN-ACCESS-2026Q2, DR-FAILOVER-2026
Open exception: Temporary support rule lacks expiry; exception EXC-044 expires 2026-07-31
```

### 3. Review Firewall Policy for SOC 2 Control Operation

For each in-scope or supporting rule, verify:

- owner, reviewer, and business purpose;
- customer-data path or production service protected;
- source/destination zone/network/user/device;
- application/service/port and whether broad access is justified;
- NAT/public exposure relationship;
- logging and alerting expectations;
- attached security profiles or compensating controls;
- change ticket and approval;
- control ID/evidence reference;
- temporary/vendor access expiry;
- hit count/last-hit and stale-rule review;
- exceptions, deviations, or risk acceptance.

### 4. Add SOC 2 Evidence Markers to Firewall Configs

Where the platform supports descriptions, comments, tags, or labels, add concise markers that help auditors connect config exports to control evidence.

Pattern:

```text
SOC2:<theme> CTRL:<control-id> OWNER:<team> REF:<ticket-or-evidence-id> PURPOSE:<short-purpose>
```

Examples:

```text
SOC2:ACCESS CTRL:NET-01 OWNER:NetSec REF:CHG-22119 PURPOSE:Prod app to DB least privilege
SOC2:MONITOR CTRL:SEC-07 OWNER:SecOps REF:SIEM-FW-01 PURPOSE:Forward firewall threat logs
SOC2:CHANGE CTRL:CHG-04 OWNER:NetOps REF:CHG-22119 PURPOSE:Approved production firewall change
SOC2:AVAIL CTRL:AV-03 OWNER:SRE REF:DR-FW-2026 PURPOSE:HA firewall path for SaaS production
SOC2:VENDOR CTRL:VND-02 OWNER:IT REF:SUPPORT-2026Q2 PURPOSE:Time-bound vendor support access
SOC2:CONF CTRL:CONF-01 OWNER:AppOps REF:DATAFLOW-07 PURPOSE:Restrict confidential data path
```

Marker rules:

- Use the organization’s actual SOC 2 control IDs where available.
- Keep markers short enough for platform field limits and exports.
- Do not include customer names, personal data, confidential customer data, credentials, secrets, vulnerability detail, incident detail, or sensitive architecture.
- Treat markers as evidence pointers, not auditor conclusions.
- Keep detailed evidence in tickets, GRC, audit folders, CMDB, or source-of-truth systems.

### 5. Validate Type II Operating Effectiveness

For Type II reports, collect samples over the examination period:

- sampled firewall changes show authorization, testing/validation, implementation, and approval;
- emergency changes have post-implementation review;
- rule reviews happened at the required cadence and tracked remediation;
- admin/VPN/vendor access reviews were completed and exceptions resolved;
- logs were forwarded continuously or exceptions were documented;
- alerts were triaged according to procedure;
- incidents involving firewall/VPN/WAF/IDS were documented and resolved;
- backups, HA, failover, or DR tests support availability commitments;
- vulnerabilities and firmware/security advisories were tracked;
- deviations have management review and remediation.

## Evidence Request Checklist

Ask for:

- SOC 2 report type, period, Trust Services Categories, and system description;
- control matrix with control IDs and criteria mappings;
- production firewall/WAF/VPN/ZTNA/security group inventory;
- architecture, network, data-flow, and customer-data diagrams;
- firewall/network security policies, secure configuration standards, rule standards, and change procedures;
- firewall policy, NAT, zone/interface, object, routing, VPN/ZTNA, WAF, IDS/IPS, DNS/security-profile, and cloud security group exports;
- sampled firewall change tickets, approvals, diffs, validation notes, and emergency-change reviews;
- rule review/recertification evidence, stale-rule remediation, exception lists, and risk acceptances;
- admin, VPN, privileged, vendor, MSP/MSSP, and service-account access review evidence;
- MFA/AAA/RBAC evidence for firewall admin and remote access;
- syslog/SIEM forwarding configuration, NTP, sample firewall/VPN/admin/threat logs, alert rules, triage records, retention settings, and review records;
- incident response tickets and firewall-related investigations;
- vulnerability/advisory tracking, firmware/content update evidence, and remediation tickets;
- HA/failover, backup/restore, DR, monitoring, capacity, or DDoS/WAF evidence when Availability is in scope;
- confidentiality/privacy data-flow restrictions and third-party access evidence when those categories are in scope;
- subservice organization/provider shared responsibility evidence and complementary user entity controls if applicable.

## Output Templates

### Short Assessment Summary

```text
Summary: The NGFW/firewall estate can support SOC 2 controls for the scoped service system, but SOC 2 reporting covers control design and operating effectiveness over a defined period, not certification of the firewall product alone. Evidence reviewed supports [strong/partial/weak] alignment with logical access, system operations, change management, risk mitigation, and [Availability/Confidentiality/Privacy if applicable]. Key gaps are [gaps]. Recommended remediation is [actions]. Final conclusions depend on the system description, criteria in scope, control matrix, period, sample results, and CPA auditor judgment.
```

### Firewall Finding

```text
Finding: Production firewall changes lack validation evidence
SOC 2 mapping: CC8 change management; supporting CC6 logical access and CC7 system operations
Evidence: Sampled changes CHG-22011 and CHG-22042 include approval but no implementation validation, peer review, or rollback notes.
Risk: Unauthorized or erroneous firewall changes could affect production security or availability without sufficient evidence of controlled change operation.
Recommendation: Require pre-approval, documented implementation plan, peer review or automated validation, rollback plan, post-change verification, and evidence attachment for production firewall changes. Sample changes during the SOC 2 period to confirm operation.
```

### Evidence Marker Recommendation

```text
Recommended description:
SOC2:ACCESS CTRL:NET-01 OWNER:NetSec REF:CHG-22119 PURPOSE:Prod app to DB least privilege

Do not include customer data, personal data, secrets, credentials, vulnerability details, incident detail, or sensitive architecture. Store detailed support in the audit evidence repository.
```

## Common Pitfalls

1. **Calling a firewall SOC 2 compliant.** SOC 2 reports cover system controls, criteria, and period. The firewall supports those controls.

2. **Ignoring Type I vs Type II.** Type I focuses on design at a point in time; Type II needs operating evidence across a period.

3. **Collecting only current screenshots.** Auditors often need sampled tickets, reviews, logs, and alerts from the report period.

4. **Mapping every firewall feature to SOC 2.** Start with the control matrix and system description, then map evidence.

5. **Forgetting customer-data paths.** Confidentiality and Privacy support require data-flow and access-path evidence, not just perimeter rules.

6. **Overlooking subservice organizations.** Cloud providers, MSSPs, MSPs, SOC providers, and managed firewall providers may require carve-out/inclusive treatment and responsibility evidence.

7. **Treating broad production access as normal.** Broad access needs documented business need, compensating controls, monitoring, and review.

8. **Leaving temporary/vendor rules open.** SOC 2 samples often expose missing expiry, review, or access-removal evidence.

9. **Assuming logs prove monitoring.** Verify alert logic, routing, triage, retention, and review evidence.

10. **Putting sensitive information in descriptions.** Use short control markers and stable references only.

## Verification Checklist

Before finalizing a SOC 2 NGFW answer:

- [ ] Confirm report type, period, system boundary, Trust Services Categories, and control matrix when possible.
- [ ] State that SOC 2 covers system controls over a defined scope/period, not the NGFW product alone.
- [ ] Identify firewall/security infrastructure assets supporting the scoped service.
- [ ] Map claims to control IDs and criteria such as CC6, CC7, CC8, CC9, Availability, Confidentiality, or Privacy as applicable.
- [ ] Check inbound, outbound, east-west, admin, VPN/ZTNA, vendor, cloud, WAF, backup, logging, and public-exposure paths separately.
- [ ] Verify owner, business purpose, approval, logging, review date, evidence reference, and expiry for important rules.
- [ ] Verify change-management evidence for firewall changes across the report period.
- [ ] Verify admin/VPN/vendor access reviews and MFA/AAA/RBAC evidence.
- [ ] Verify log forwarding, alerting, triage, incident response, retention, and review evidence.
- [ ] Verify availability/confidentiality/privacy evidence where those categories are in scope.
- [ ] Label assumptions and distinguish design adequacy from Type II operating effectiveness.
