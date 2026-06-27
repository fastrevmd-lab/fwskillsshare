---
name: cis-controls-ngfw-compliance
description: Use when researching, designing, auditing, or explaining how a next-generation firewall or firewall estate can support CIS Critical Security Controls v8/v8.1 safeguards. Covers CIS-aligned network inventory, secure firewall configuration, network infrastructure management, access control, logging, malware/threat prevention, data protection, vulnerability management, service-provider access, incident response, penetration testing, audit evidence, and firewall description/tag markers. Emphasizes that CIS alignment is assessed for the implemented environment and security program, not certified by an NGFW alone.
version: 0.1.0
author: Hermes Agent
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [cis-controls, cis-v8, compliance, firewall, ngfw, safeguards, audit, evidence, network-infrastructure, logging, access-control, incident-response]
    related_skills: [srx-policy, srx-nat, parsing-srx-configs, parsing-palo-configs, parsing-fortinet-configs, parsing-cisco-configs, pci-ngfw-compliance, hipaa-ngfw-compliance, cmmc-nist-800-171-ngfw-compliance, iso27001-ngfw-compliance, soc2-ngfw-compliance]
  sources:
    - title: "CIS Critical Security Controls v8"
      author: Center for Internet Security
      url: https://www.cisecurity.org/controls/v8
      retrieved: "2026-06-27"
    - title: "CIS Critical Security Controls List"
      author: Center for Internet Security
      url: https://www.cisecurity.org/controls/cis-controls-list
      retrieved: "2026-06-27"
---

# CIS Controls NGFW Compliance Research

## Overview

Use this skill to answer questions like “how should my firewall support CIS Controls v8?” or “is this NGFW design aligned with CIS Critical Security Controls?” The core answer is: an NGFW is not “CIS compliant” by itself. CIS Controls alignment is assessed across the organization’s implemented safeguards, processes, assets, people, evidence, and operating practices. A firewall estate can be a major technical control and evidence source, but it must be configured, monitored, reviewed, maintained, and tied to the organization’s CIS implementation group, risk, and operational context.

The CIS Controls are prioritized cyber defense practices. They are useful as a practical baseline even when the organization is not pursuing a formal regulatory certification. For firewall work, the most directly relevant areas are Control 3 (Data Protection), Control 4 (Secure Configuration), Control 5 and 6 (Account and Access Control Management), Control 7 (Continuous Vulnerability Management), Control 8 (Audit Log Management), Control 10 (Malware Defenses), Control 11 (Data Recovery), Control 12 (Network Infrastructure Management), Control 13 (Network Monitoring and Defense), Control 15 (Service Provider Management), Control 17 (Incident Response), and Control 18 (Penetration Testing).

Treat this as security-control assessment guidance, not legal advice and not a certification claim. When producing final language, cite CIS Control and Safeguard IDs where known, label assumptions, and distinguish “supports CIS Controls” from “fully implemented across the enterprise.”

## When to Use

Use this skill when the user asks about:

- CIS Controls v8 or v8.1 firewall, NGFW, perimeter firewall, internal segmentation firewall, cloud firewall, IDS/IPS, VPN, or network infrastructure expectations
- mapping firewall features to CIS Critical Security Controls safeguards
- creating a practical security baseline for organizations that do not have a more specific framework requirement
- assessing firewall rulebases, NAT, zones, VPN, routing, IDS/IPS, DNS security, URL filtering, malware defense, logging, SIEM forwarding, or incident-response evidence against CIS
- reviewing network infrastructure management, secure configuration, administrative access, service-provider access, or cloud security group controls
- preparing audit-ready evidence requests, gap findings, roadmap items, or prioritized remediation plans using CIS language
- comparing Palo Alto, FortiGate, Juniper SRX, Cisco ASA/FTD, Check Point, cloud-native firewalls, host firewalls, SASE/ZTNA, or microsegmentation controls against CIS baseline needs

Do not use this skill as a substitute for parsing a vendor config. Load the relevant parser skill first when raw config is provided, then use this skill to interpret CIS implications.

## Baseline Interpretation

### What “CIS-Aligned NGFW” Really Means

Avoid saying “this firewall is CIS compliant” as a standalone product claim. More accurate phrasing:

- “This firewall estate can support CIS Controls safeguards if configured and operated according to documented policy.”
- “This NGFW design appears aligned with selected CIS Controls around secure configuration, network infrastructure management, audit logging, monitoring, and incident response, subject to evidence review.”
- “The device is one technical safeguard; CIS alignment depends on inventory, configuration standards, access management, monitoring, vulnerability management, incident response, testing, and service-provider governance.”

A CIS-supporting firewall estate needs more than product features. It needs:

1. an inventory of network infrastructure assets and enforcement points;
2. documented network diagrams and data-flow paths for important systems;
3. secure baseline configuration standards for each firewall platform;
4. least-privilege inbound, outbound, east-west, management, VPN, and service-provider access rules;
5. protected administrative accounts, MFA/AAA/RBAC where appropriate, and encrypted management protocols;
6. centralized logs, time synchronization, alerting, and review;
7. IDS/IPS, threat prevention, DNS/URL security, anti-malware, or equivalent monitoring where justified;
8. change management, configuration backups, and periodic rule review;
9. vulnerability management for firewall software, exposed services, and management planes;
10. incident response playbooks that use firewall, VPN, IPS, and SIEM evidence;
11. penetration/segmentation testing and remediation evidence.

### Implementation Group Awareness

CIS Controls are organized into Implementation Groups (IG1, IG2, IG3). Do not assume every safeguard applies equally to every organization. When answering, ask or infer from context whether the organization is targeting IG1, IG2, or IG3:

- IG1: essential cyber hygiene; focus on inventory, secure configuration, basic logging, patching, backups, and clear incident response.
- IG2: adds more mature governance, monitoring, access control, vulnerability management, and service-provider control.
- IG3: adds advanced monitoring, automation, segmentation, threat detection, and testing for higher-risk environments.

If the user does not specify, provide a practical baseline and label it as “CIS-aligned firewall baseline; tailor by Implementation Group.” Do not overburden small environments with IG3-only expectations unless risk justifies it.

## CIS Control Mapping for NGFW Controls

Use this table as a first-pass mapping. Always verify exact safeguard wording against the current CIS Controls publication during formal work.

| CIS area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| Control 1: Inventory and Control of Enterprise Assets | Identify firewalls, VPN gateways, cloud firewalls, WAFs, IDS/IPS, SASE/ZTNA, and management systems | Network asset inventory, CMDB, cloud inventory, owner/platform/version list |
| Control 2: Inventory and Control of Software Assets | Track firewall OS, firmware, plugins, content/signature packages, and management software | Version inventory, license/content status, software approval records |
| Control 3: Data Protection | Restrict network paths to sensitive data systems and control exfiltration routes | Data-flow diagrams, egress policy, DLP/threat logs, segmentation rules |
| Control 4: Secure Configuration | Harden firewall baselines and disable unnecessary services | Baseline standards, config exports, management-service review, hardening checklist |
| Control 5: Account Management | Manage firewall admin accounts and remote-access identities | Admin user list, AAA/SSO integration, stale-account review, break-glass process |
| Control 6: Access Control Management | Enforce least privilege for user/admin/VPN/application access | RBAC, MFA, rule ownership, VPN groups, user-ID policy, access reviews |
| Control 7: Continuous Vulnerability Management | Patch firewall OS/content and scan exposed services | Firmware/advisory tracking, vulnerability scan results, remediation tickets |
| Control 8: Audit Log Management | Generate and centralize firewall/VPN/admin/threat logs | Syslog/SIEM config, NTP, log retention, sample events, review workflow |
| Control 9: Email and Web Browser Protections | Support web filtering, DNS security, TLS policy, and risky-category blocking | URL/DNS security profiles, proxy paths, web filtering logs |
| Control 10: Malware Defenses | Block or detect malware callbacks and malicious content where NGFW features support it | Anti-malware/IPS/DNS signatures, update status, alert examples |
| Control 11: Data Recovery | Protect firewall configs and support recovery of network enforcement points | Config backups, restore tests, HA/failover evidence, backup access controls |
| Control 12: Network Infrastructure Management | Securely manage network infrastructure and architecture | Diagrams, secure protocols, admin ACLs, out-of-band/management network, config standards |
| Control 13: Network Monitoring and Defense | Monitor traffic and security events at key boundaries | IDS/IPS placement, threat logs, deny/permit alerts, SIEM detections, packet capture process |
| Control 15: Service Provider Management | Control MSP/MSSP/vendor/cloud firewall access and responsibilities | Contracts, access lists, provider evidence, shared responsibility matrix |
| Control 16: Application Software Security | Support application segmentation and public-app protection; not a substitute for app security | WAF/WAAP placement, app-ID rules, API gateway/firewall evidence |
| Control 17: Incident Response Management | Provide firewall evidence for detection, containment, eradication, and lessons learned | IR runbooks, sample investigations, containment change tickets |
| Control 18: Penetration Testing | Validate firewall boundaries, segmentation, and exposed services | Pen test reports, segmentation test results, remediation evidence |

## NGFW Feature Expectations

A CIS-aligned firewall estate does not need every feature enabled everywhere, but the design should explain which safeguard covers each risk and how firewall evidence proves operation.

### Core Firewall and Network Infrastructure Features

Minimum expectations:

- complete inventory of firewall, VPN, WAF/WAAP, IDS/IPS, cloud firewall, security group, SASE/ZTNA, and management-plane assets;
- documented zone/interface/segment model for Internet, DMZ, user, server, management, cloud, remote-access, vendor, guest, wireless, OT/IoT, backup, and logging networks;
- explicit allowlists for critical systems and sensitive data paths;
- default deny behavior between trust zones unless a documented business need exists;
- rule descriptions or external records containing owner, business purpose, ticket/reference, review date, and control marker;
- NAT rules documented so reviewers can understand actual exposure and policy match behavior;
- management-plane isolation, encrypted protocols, MFA/AAA/RBAC where applicable, and no direct untrusted management exposure;
- time synchronization, centralized logging, protected log storage, and alert/review workflow;
- backup/restore procedures, HA/failover validation, and protected configuration repositories;
- vulnerability, firmware, content/signature, and end-of-life tracking for firewall platforms.

### NGFW “Next-Generation” Features

Useful features that may support CIS safeguards:

- application identification to reduce broad port-only permits;
- user and device identity integration for VPN, admin, and controlled access paths;
- IDS/IPS, anti-malware, sandboxing, DNS security, URL filtering, and reputation controls;
- TLS inspection where lawful, documented, risk-justified, and operationally supportable;
- DLP or exfiltration detection features for sensitive-data egress where available;
- geolocation/reputation blocking as defense-in-depth, not a substitute for least privilege;
- dynamic address groups/tags for cloud, endpoint, or identity-driven segmentation, provided tag sources are governed and evidenced;
- WAF/WAAP or API protection for public-facing applications, while recognizing application security remains broader than the firewall.

Do not overclaim NGFW features. CIS Controls describe safeguards and outcomes, not a requirement to buy a specific firewall brand or feature license.

## Assessment Workflow

### 1. Establish Scope, Inventory, and Implementation Group

Collect:

- target CIS Controls version and Implementation Group;
- network infrastructure asset inventory;
- firewall/NSC inventory, including physical, virtual, cloud-native, host-based, VPN, ZTNA/SASE, WAF/WAAP, IDS/IPS, and firewall managers;
- network diagrams and critical data-flow diagrams;
- sensitive data systems and high-value services protected by firewalls;
- external service-provider, vendor, remote-access, cloud, backup, logging, monitoring, and administration paths;
- configuration baseline standards and change-control process.

Questions to answer:

- Which CIS Implementation Group is the organization targeting?
- Which firewalls enforce critical boundaries or sensitive data paths?
- Which systems can administer or bypass firewall controls?
- Which external providers have access to firewall management or protected networks?
- Which logs and alerts prove controls are operating?
- Which firewalls, rules, firmware versions, or signatures are out of support, unreviewed, or unmanaged?

### 2. Build a Firewall-to-CIS Matrix

For each in-scope firewall/NSC, map:

- hostname/device ID;
- platform and version;
- owner/team;
- role: perimeter, internal segmentation, cloud control, VPN/ZTNA, WAF/WAAP, IDS/IPS, DNS/web security, management-plane control;
- protected systems or segments;
- relevant CIS Controls/Safeguards;
- log destination and retention;
- change-control system;
- backup/config repository;
- HA/DR role;
- last rule review date;
- last firmware/content update date;
- last vulnerability scan/pen test coverage;
- known exceptions, accepted risks, or remediation items.

Output example:

```text
Firewall: PA-EDGE-01
Scope: Internet edge, DMZ, remote access, critical server segmentation
CIS mapping: Controls 4, 6, 7, 8, 12, 13, 15, 17, 18
Evidence: FWSTD-001, CHG-10421, SIEM-FW-EDGE, RULE-REVIEW-2026Q2, PEN-2026-04
Open gap: Vendor VPN rule lacks expiry and recent access review; remediation NET-242 due 2026-08-30
```

### 3. Review Rulebase for CIS Intent

For each policy/rule touching sensitive systems, critical services, management paths, remote access, vendor access, or Internet exposure, capture:

- rule name and UUID;
- source zone/interface/network/user/device;
- destination zone/interface/network/object;
- application/service/port;
- action and security profile;
- NAT relationship;
- logging setting;
- owner and business purpose;
- ticket/change reference;
- CIS evidence marker;
- expiry or review date for temporary/vendor access;
- hit count and last-hit timestamp if available;
- whether the rule supports inbound exposure, outbound egress, internal segmentation, remote access, admin/management, vendor/service-provider, backup, logging, monitoring, DNS/NTP/update, or incident-response emergency access;
- whether the rule violates the baseline, requires remediation, or has documented risk treatment.

### 4. Add CIS Evidence Markers to Firewall Configs

Where the firewall platform supports descriptions, comments, annotations, labels, or tags, mark CIS-relevant configuration directly in the firewall. This makes audits easier because policy exports, NAT exports, zone lists, VPN lists, object inventories, and security-profile exports carry visible evidence markers instead of requiring reviewers to infer CIS relevance from spreadsheets alone.

Use markers as configuration hygiene and audit-evidence pointers, not proof of compliance. The marker should point to evidence; it does not replace policies, diagrams, change tickets, rule recertification, vulnerability management, incident records, or security leadership review.

Recommended marker pattern:

```text
CIS:<control-or-scope> CTRL:<control-id> OWNER:<team-or-app> REF:<ticket-or-evidence-id> PURPOSE:<short-business-purpose>
```

Examples:

```text
CIS:BOUNDARY CTRL:12 OWNER:NetSec REF:FWSTD-001 PURPOSE:Internet edge default deny
CIS:MONITOR CTRL:13 OWNER:SecOps REF:SIEM-FW-01 PURPOSE:Forward traffic/threat logs to SIEM
CIS:ACCESS CTRL:6 OWNER:IT REF:VPN-2026Q2 PURPOSE:MFA VPN to admin jump host
CIS:DATA CTRL:3 OWNER:DataEng REF:CHG12345 PURPOSE:Restrict sensitive DB access
CIS:VENDOR CTRL:15 OWNER:NetOps REF:MSP-ACCESS-01 PURPOSE:Time-bound MSP firewall admin access
CIS:BACKUP CTRL:11 OWNER:NetOps REF:BKUP-FW-01 PURPOSE:Encrypted config backup path
```

Apply markers where possible:

- security policies/rules that permit, deny, inspect, log, or segment critical or sensitive traffic;
- final explicit deny rules at important boundaries;
- NAT rules that publish services or translate traffic from sensitive systems;
- zones, interfaces, VRFs, virtual routers, VPC/VNet constructs, address books, dynamic groups, security groups, and NAC segments representing important boundaries;
- VPN, ZTNA, remote-access, third-party, service-provider, vendor, backup, logging, monitoring, DNS, NTP, update, and emergency access paths;
- IDS/IPS, WAF/WAAP, URL filtering, anti-malware, TLS inspection, DLP, DNS security, or threat profiles.

Marker rules:

- Keep markers short enough to survive platform field-length limits and exports.
- Never put regulated data, customer data, secrets, credentials, private keys, vulnerability details, incident details, or sensitive architecture detail in descriptions.
- Prefer stable references: change ticket, CMDB CI, control ID, risk ID, application ID, evidence package ID, service-provider ID, or rule-review ID.
- Use consistent tokens (`CIS:BOUNDARY`, `CTRL:12`, `CIS:MONITOR`) so exports can be searched deterministically.
- If the platform has both a tag field and a description field, use tags for machine filtering and descriptions for human audit context.
- If the platform lacks descriptions for a construct, maintain the marker in the adjacent object/rule name, tag, external source-of-truth, or rule-review export.
- Do not let markers justify bad policy. A rule with `CIS:ACCESS` still needs least privilege, approval, logging, and periodic review.

Red flags:

- broad `any any allow` into or out of sensitive or critical segments;
- unrestricted server or sensitive-data Internet egress;
- direct Internet exposure of databases, file shares, backups, management interfaces, or identity services;
- management access from untrusted or general user networks;
- vendor/MSP access without MFA, named users, source restriction, approval, monitoring, or expiry;
- unlogged high-risk access or disabled logging on important boundary rules;
- rules with no owner, business purpose, ticket, control reference, review date, or hit data;
- temporary rules without expiry;
- NAT exposing more services than policy intent suggests;
- unsupported firewall software, stale threat signatures, or missing advisory tracking;
- firewall backups missing, unencrypted, untested, or accessible to too many users;
- policy shadowing or rule order that bypasses intended controls;
- IDS/IPS/threat profiles attached but disabled, outdated, or alert-only without rationale;
- service-provider access paths not covered by contract, responsibility matrix, or access review.

### 5. Validate Secure Configuration and Network Infrastructure Management

For Controls 4 and 12, validate:

- firewall secure baselines exist and are platform-specific;
- insecure management services such as Telnet, plaintext HTTP, weak SNMP, or broad API access are disabled or justified;
- management access is restricted to approved networks and named roles;
- default accounts, weak local accounts, and stale admins are removed or controlled;
- rule naming, description/tagging, logging, and review standards are implemented;
- configuration changes are approved and traceable;
- firewall firmware/content/signatures are supported and tracked;
- backups are protected and restore procedures are tested.

### 6. Validate Access Control and Data Protection

For Controls 3, 5, and 6, validate:

- sensitive systems are reachable only from authorized user, app, service, admin, vendor, and remote-access segments;
- outbound egress from sensitive systems is restricted to approved destinations and protocols;
- admin and remote access use MFA/AAA/RBAC where appropriate;
- user identity, group, or device posture is used where it materially improves least privilege;
- service-provider access is named, approved, monitored, restricted, and reviewed;
- data-flow diagrams match policy paths;
- exceptions and compensating controls are documented.

### 7. Validate Logging, Monitoring, and Malware Defense

For Controls 8, 10, and 13, validate:

- allow and deny logs are enabled for important boundaries where operationally appropriate;
- admin login, failed login, configuration change, VPN, NAT, threat, IDS/IPS, malware, DNS, and URL events are logged;
- logs are forwarded to centralized log management/SIEM with reliable time synchronization;
- logs are protected from unauthorized modification and retained according to policy;
- alerting covers high-risk events such as new public exposure, admin failures, vendor VPN access, malware callbacks, IPS critical events, unexpected egress, and boundary deny spikes;
- threat prevention, IPS, anti-malware, DNS security, URL filtering, and sandboxing are updated where used;
- sample events can be retrieved and tied to investigations.

### 8. Validate Vulnerability Management, Incident Response, and Testing

For Controls 7, 17, and 18, validate:

- firewall management interfaces and exposed services are in vulnerability scan scope;
- firmware, content/signature, and end-of-life risks are tracked;
- remediation tickets exist for firewall vulnerabilities, broad rules, exposed services, and weak protocols;
- incident response runbooks include firewall, VPN, IPS, DNS, URL, WAF, and SIEM alert handling;
- containment procedures can rapidly block indicators, quarantine segments, disable vendor access, or tighten egress;
- penetration tests and segmentation tests validate important firewall boundaries;
- findings are tracked to closure or documented risk acceptance.

## Evidence Request Checklist

Ask for:

- target CIS Controls version and Implementation Group;
- network infrastructure inventory and CMDB export;
- current network diagrams and sensitive data-flow diagrams;
- firewall inventory and management-plane architecture;
- firewall configuration standards, secure baselines, rule naming/description/tagging standard, and change procedure;
- firewall policy exports, NAT exports, zone/interface/object exports, VPN/ZTNA exports, routing exports, and security-profile exports;
- evidence that CIS markers/descriptions exist for relevant policies, NAT, zones, VPNs, objects, and profiles where supported;
- admin account list, AAA/MFA/RBAC evidence, local account review, and service account controls;
- remote-access and service-provider/vendor access records;
- change tickets, approvals, emergency changes, and policy diffs for sampled rules;
- rule review/recertification evidence, including owner, business purpose, hit count, last-hit, expiry, and remediation notes;
- syslog/SIEM forwarding configuration, time synchronization, sample firewall/VPN/admin/threat logs, and alert workflow evidence;
- vulnerability scan reports, firmware/advisory tracking, content/signature update evidence, and remediation tickets;
- firewall backup, restore, HA/failover, and DR evidence;
- incident response runbooks and sample firewall-related investigations;
- penetration test and segmentation test methodology/results/remediation;
- service-provider contracts, shared responsibility matrices, and provider evidence where managed firewalls/SOC/cloud controls are used.

## Output Templates

### Short Assessment Summary

```text
Summary: The NGFW/firewall estate can support CIS Controls v8 safeguards, but CIS alignment is assessed across the implemented environment and security program, not by the NGFW alone. The firewall evidence reviewed supports [strong/partial/weak] alignment with secure configuration, access control, audit logging, network infrastructure management, monitoring/defense, incident response, and testing controls. Key gaps are [gaps]. Recommended next steps are [actions]. Tailor final priority by CIS Implementation Group and organizational risk.
```

### Firewall Finding

```text
Finding: Broad server Internet egress
CIS mapping: Controls 3, 4, 6, 8, 12, 13
Evidence: Rule SERVER-OUT permits SERVER-NETS to Internet on any service. No owner, business purpose, review date, egress proxy path, or alerting evidence was provided.
Risk: Compromised servers could establish arbitrary outbound command-and-control or exfiltration sessions, weakening data protection and network monitoring objectives.
Recommendation: Replace broad egress with documented allowlist for DNS, NTP, update, logging, backup, proxy, and approved application paths; log denied attempts; add owner/ref/purpose markers; track exception approvals.
```

### Evidence Marker Recommendation

```text
Recommended description:
CIS:MONITOR CTRL:13 OWNER:SecOps REF:SIEM-FW-01 PURPOSE:Forward firewall threat logs to SIEM

Do not include secrets, customer data, vulnerability details, incident detail, or sensitive architecture in the description. Put detailed justification in the ticket/evidence repository.
```

## Common Pitfalls

1. **Saying the firewall is CIS compliant.** Say it supports CIS Controls safeguards when configured and operated as part of the environment.

2. **Ignoring Implementation Groups.** IG1/IG2/IG3 affect depth and priority. Tailor recommendations instead of treating every safeguard as equally mandatory.

3. **Starting with rule cleanup before inventory.** CIS-aligned firewall work needs asset inventory, ownership, diagrams, baselines, and scope first.

4. **Reviewing only Internet-edge firewalls.** Internal segmentation, cloud security groups, VPN, WAF, SASE/ZTNA, management, backup, logging, and service-provider paths also matter.

5. **Ignoring outbound egress.** Data protection, malware defense, and network monitoring often depend on controlling outbound paths.

6. **Treating logging as enabled/disabled only.** Validate forwarding, time sync, protection, retention, alerting, review, and incident use.

7. **Assuming IDS/IPS profile attachment equals monitoring.** Verify placement, traffic visibility, signature updates, alert routing, and response.

8. **Forgetting firewall backups and recovery.** Firewall configs are part of resilient network enforcement and should be protected and restorable.

9. **Ignoring service providers.** Managed firewall providers, MSSPs, SOCs, cloud providers, and support vendors need access governance and responsibility evidence.

10. **Putting sensitive data in descriptions.** Use short markers and stable evidence IDs, not customer data, secrets, vulnerabilities, or incident detail.

11. **Leaving CIS-relevant config unmarked.** Where possible, policy, NAT, zone/segment, object, VPN, and security-profile descriptions/tags should carry concise `CIS:`/`CTRL:` evidence markers.

12. **Producing control conclusions without evidence dates.** CIS assessment output should include artifacts, owners, dates, open gaps, and assumptions.

## Verification Checklist

Before finalizing a CIS Controls NGFW answer:

- [ ] Confirm target CIS Controls version and Implementation Group when possible.
- [ ] State that CIS alignment applies to the implemented environment/security program, not the NGFW alone.
- [ ] Identify network infrastructure assets, firewall roles, sensitive systems, data flows, and management paths.
- [ ] Map claims to CIS Controls/Safeguards, especially Controls 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 17, and 18.
- [ ] Check inbound, outbound, east-west, remote-access, admin, service-provider, logging, and public-exposure paths separately.
- [ ] Verify all allowed services/protocols/ports have business need, owner, approval, and review evidence.
- [ ] Verify CIS-relevant policy, NAT, zone/segment, VPN, object, and profile entries include concise evidence markers where the platform supports descriptions/tags/comments.
- [ ] Verify secure baseline, change control, firmware/content update, backup, and periodic rule review evidence.
- [ ] Verify logging, time sync, alerting, review, log protection, and incident response evidence.
- [ ] Verify IDS/IPS/threat monitoring placement, update status, and alert response where claimed.
- [ ] Verify vulnerability scan, penetration test, and segmentation test evidence where applicable.
- [ ] Label assumptions and prioritize remediation by risk and Implementation Group.
