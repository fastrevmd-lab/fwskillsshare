---
name: pci-ngfw-compliance
description: Use when researching, designing, auditing, or explaining what it takes for a next-generation firewall or firewall estate to support PCI DSS v4.0.1 compliance. Covers PCI scoping, CDE segmentation, network security controls, inbound and outbound restriction, rule review evidence, logging, IDS/IPS, WAF-adjacent controls, admin access, change control, and assessor-ready evidence. Emphasizes that PCI DSS compliance is assessed for the entity/environment, not certified by an NGFW alone.
version: 0.1.0
author: Hermes Agent
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [pci-dss, compliance, firewall, ngfw, network-security-controls, cde, segmentation, audit, evidence, ids, ips, waf, logging]
    related_skills: [srx-policy, srx-nat, parsing-srx-configs, parsing-palo-configs, parsing-fortinet-configs, parsing-cisco-configs, hipaa-ngfw-compliance, cmmc-nist-800-171-ngfw-compliance, cis-controls-ngfw-compliance]
  sources:
    - title: "Payment Card Industry Data Security Standard: Requirements and Testing Procedures, v4.0.1"
      author: PCI Security Standards Council
      url: https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf
      retrieved: "2026-06-27"
    - title: PCI Security Standards Council Document Library metadata
      author: PCI Security Standards Council
      url: https://docs-pub.pcisecuritystandards.org/doc_library.json
      retrieved: "2026-06-27"
---

# PCI NGFW Compliance Research

## Overview

Use this skill to answer questions like “what does an NGFW need to do to be PCI compliant?” or “is this firewall design sufficient for PCI DSS?” The core answer is: a next-generation firewall is not PCI compliant by itself. PCI DSS compliance is assessed for the entity, the cardholder data environment (CDE), connected-to/security-impacting systems, processes, people, evidence, and compensating or customized controls. An NGFW can be a major network security control (NSC), but it must be configured, maintained, monitored, reviewed, and evidenced as part of the whole PCI DSS program.

For PCI DSS v4.0.1, the most directly relevant NGFW areas are Requirement 1 (Install and Maintain Network Security Controls), Requirement 2 (secure configuration of system components), Requirement 4 (strong cryptography over open/public networks), Requirement 6.4.2 (automated technical solution for public-facing web applications), Requirement 10 (logging and monitoring), Requirement 11 (vulnerability scanning, penetration testing, segmentation testing, IDS/IPS), and Requirement 12 (policies, risk, incident response, and operational governance).

Treat this as research and assessment guidance, not legal advice and not a QSA decision. When producing final compliance language, cite PCI DSS v4.0.1 requirement IDs and defer final interpretation to the entity’s QSA/ISA, acquirer, or payment brand.

## When to Use

Use this skill when the user asks about:

- PCI DSS firewall, NGFW, perimeter firewall, internal segmentation firewall, or cloud firewall requirements
- “PCI compliant firewall” or “PCI compliant NGFW” claims
- designing or auditing CDE segmentation with firewalls
- mapping firewall features to PCI DSS controls
- evidence needed for PCI firewall review or ROC/AOC support
- rulebase review cadence, least privilege, default deny, inbound/outbound restrictions, DMZ design, wireless-to-CDE controls, admin access, logging, IDS/IPS, or WAF-related expectations
- comparing Palo Alto, FortiGate, Juniper SRX, Cisco ASA/FTD, Check Point, cloud security groups, or other firewalls against PCI DSS needs
- writing an audit checklist, gap analysis, or assessor-ready evidence request list for firewall controls

Do not use this skill as a substitute for parsing a vendor config. Load the relevant parser skill first when raw config is provided, then use this skill to interpret PCI implications.

## Baseline Interpretation

### What “PCI compliant NGFW” Really Means

Avoid saying “this NGFW is PCI compliant” unless you mean a narrow vendor marketing claim that still needs validation in the entity’s environment. More accurate phrasing:

- “This NGFW can support PCI DSS network security control requirements if configured and operated correctly.”
- “This firewall design appears aligned with PCI DSS Requirement 1, subject to evidence review and validation.”
- “The device is one control in the PCI DSS scope; compliance depends on rules, segmentation, logging, review, change control, vulnerability management, monitoring, and incident response.”

A compliant firewall estate needs more than product features. It needs:

1. defined CDE scope and connected networks;
2. accurate network and data-flow diagrams;
3. documented configuration standards;
4. approved business need for every allowed service, protocol, and port;
5. inbound and outbound least-privilege rules;
6. explicit deny behavior for unauthorized traffic;
7. stateful boundary controls between trusted and untrusted networks;
8. segmentation controls that are tested if used for scope reduction;
9. secure admin access and hardened management plane;
10. logging, retention, review, alerting, and incident response;
11. change control and periodic rule review;
12. evidence showing the above is implemented and maintained.

### PCI DSS Scope Comes First

Before evaluating firewall controls, determine what is in scope:

- systems that store, process, or transmit account data;
- systems in the CDE;
- systems connected to the CDE;
- systems that can impact CDE security, including management, logging, identity, vulnerability scanning, jump hosts, backup, monitoring, virtualization/cloud control planes, and firewall managers;
- networks or devices that can reach the CDE unless segmentation is strong enough and tested.

If segmentation is used to reduce PCI scope, the firewall must be treated as a segmentation control and validated by penetration testing. Do not assume VLANs, zones, tags, security groups, or “internal” labels reduce scope without evidence.

## Requirement Mapping for NGFW Controls

Use this table as the first-pass mapping. Always verify exact text against the current PCI DSS standard during formal work.

| PCI DSS area | What the NGFW/firewall estate must support | Evidence to request |
|---|---|---|
| 1.1.2 Roles/responsibilities | Named owners for firewall/NSC activities | RACI, job descriptions, operations runbooks |
| 1.2.1 Configuration standards | Defined, implemented, maintained NSC ruleset standards | Firewall standard, baseline template, rule naming/logging conventions |
| 1.2.2 Change control | All network connection and NSC config changes approved and managed | Change tickets, approvals, diffs, emergency-change records |
| 1.2.3 Network diagrams | Accurate diagrams showing CDE connections, including wireless | Current diagrams mapped to interfaces/zones/cloud constructs |
| 1.2.4 Data-flow diagrams | Current cardholder data flow documentation | Data-flow diagrams tied to firewall policy paths |
| 1.2.5 Services/ports | Every allowed service, protocol, and port identified, approved, and business-justified | Rule review export with owner, justification, expiry, ticket |
| 1.2.6 Insecure services | Security features for insecure protocols/ports | TLS termination design, compensating controls, risk acceptance |
| 1.2.7 Six-month NSC review | Configs reviewed at least every six months for relevance/effectiveness | Review records, stale-rule cleanup, recertification output |
| 1.2.8 Config file protection | NSC configuration files secured from unauthorized access and consistent with active config | RBAC, backups, config repo controls, startup/running comparison |
| 1.3.1 Inbound to CDE | Only necessary inbound traffic; all other inbound traffic specifically denied | Rulebase proving least privilege and final deny |
| 1.3.2 Outbound from CDE | Only necessary outbound traffic; all other outbound traffic specifically denied | Egress allowlist, DNS/NTP/update/proxy paths, deny logs |
| 1.3.3 Wireless to CDE | NSCs between all wireless networks and CDE | Wireless zone diagrams, policy denies/allows, test results |
| 1.4.1 Trusted/untrusted boundaries | NSCs between trusted and untrusted networks | Internet/DMZ/VPN/cloud edge architecture and configs |
| 1.4.2 Inbound from untrusted | Only authorized public services or stateful responses; all else denied | DMZ policy, NAT, published services, stateful inspection proof |
| 1.4.4 CHD storage exposure | Systems storing cardholder data not directly accessible from untrusted networks | Asset list + inbound path review + external scan results |
| 1.5.1 Dual-connected devices | Controls for devices connecting to untrusted networks and CDE | Endpoint firewall/VPN posture/route control evidence |
| 2.2.7 Admin encryption | Non-console admin access encrypted using strong cryptography | SSH/HTTPS config, disabled Telnet/HTTP, cipher standards |
| 4.2.1 PAN over public networks | Strong cryptography/security protocols protect PAN in transit | TLS/IPsec configs, certificate/cipher reviews, weak protocol removal |
| 6.4.2 Public web app protection | Automated technical solution in front of public-facing web apps to detect/prevent web attacks | WAF/WAAP/NGFW app protection config, logs, update evidence |
| 10.2.x Audit logs | Logs enabled and capture required security events | Syslog/SIEM forwarding, log categories, sample events |
| 10.3.x Log protection | Logs protected from unauthorized modification and disclosure | SIEM RBAC, immutable storage, retention config |
| 10.4.x Daily review | Relevant security logs reviewed at least daily or via automated mechanisms | SIEM use cases, alert workflow, daily review evidence |
| 11.3.x Vulnerability scans | Internal/external scans run and findings remediated | ASV reports, internal scan results, remediation tickets |
| 11.4.x Pen testing | CDE perimeter and segmentation controls tested | Pen test methodology/results, segmentation test evidence |
| 11.5.1 IDS/IPS | Intrusion detection/prevention monitors CDE perimeter and critical points; signatures current | IPS profiles, update status, alert routing, incident examples |
| 12.3.3 Crypto inventory | Cipher suites/protocols documented and reviewed annually | Firewall VPN/admin/TLS inventory and review record |
| 12.10.5 Incident response | Alerts from security monitoring systems are included in IR plan | Firewall/IPS/WAF alert handling runbooks and escalation records |

## NGFW Feature Expectations

A PCI-supporting NGFW does not need every feature enabled everywhere, but the design should clearly explain which control covers each PCI need.

### Core Network Security Control Features

Minimum expectations:

- stateful traffic filtering between CDE and non-CDE networks;
- zone/interface/segment model aligned to CDE scope;
- explicit inbound and outbound allowlists;
- specific source, destination, application/service, user/device, and zone criteria where technically possible;
- final explicit deny/reject with logging where operationally appropriate;
- NAT rules documented so assessor can understand actual exposure and policy match behavior;
- configuration standards and secure baseline for every firewall platform;
- PCI evidence markers in supported description/comment/tag fields for policies, NAT rules, zones/segments, objects, and security profiles that are in PCI scope or enforce PCI segmentation;
- management-plane isolation, MFA where applicable, admin RBAC, and encrypted admin protocols;
- backup, restore, and config-integrity controls;
- centralized logging and time synchronization.

### NGFW “Next-Generation” Features

Useful features that may support PCI evidence:

- application identification / App-ID to reduce broad port-only permits;
- URL/category filtering for controlled outbound access;
- threat prevention, IPS, anti-malware, DNS security, sandboxing, or equivalent controls;
- TLS inspection where justified, documented, lawful, and operationally supportable;
- user identity integration for administrative or controlled access paths;
- geolocation or reputation blocking as defense-in-depth, not a substitute for allowlisting;
- dynamic address groups/tags for cloud or endpoint-driven segmentation, provided evidence shows correctness and change control;
- WAF/WAAP functions for public-facing web applications if they satisfy PCI DSS 6.4.2 expectations.

Do not overclaim NGFW features. PCI DSS Requirement 1 can be met with firewalls and other NSCs; “next-generation” functions often support Requirements 5, 6, 10, 11, and 12, but only if configured, monitored, updated, and evidenced.

## Assessment Workflow

### 1. Establish Scope and Architecture

Collect:

- CDE asset inventory;
- account data flow diagrams;
- network diagrams showing all CDE connections;
- firewall/NSC inventory, including physical, virtual, cloud-native, host-based, WAF/WAAP, IDS/IPS, VPN concentrators, and managed firewall controllers;
- wireless networks and their relationship to CDE;
- third-party, vendor, remote access, backup, monitoring, and administration paths;
- public-facing services and DMZ design.

Questions to answer:

- Where is PAN stored, processed, or transmitted?
- Which systems can impact CDE security even if they do not store PAN?
- Which firewalls enforce CDE boundaries?
- Which boundaries are trusted/untrusted?
- Which segmentation controls are being relied upon for scope reduction?
- Are cloud security groups, NACLs, Kubernetes policies, service meshes, or SDN constructs part of the firewall evidence set?

### 2. Build a Firewall-to-Requirement Matrix

For each in-scope firewall/NSC, map:

- hostname/device ID;
- platform/version;
- PCI role: perimeter, internal segmentation, wireless boundary, VPN, WAF/WAAP, IDS/IPS, cloud NSC, management-plane control;
- CDE zones/interfaces/security groups it protects;
- relevant PCI requirements;
- logging destination;
- management access path;
- configuration standard;
- review owner;
- change-control system;
- last rule review date;
- last backup date;
- last vulnerability scan/pen test coverage;
- known gaps.

### 3. Review Rulebase for PCI Intent

For each policy that touches CDE or CDE-impacting systems, record:

- rule ID/name;
- source zone/interface/network/object;
- destination zone/interface/network/object;
- source and destination addresses;
- service, port, and application;
- action;
- logging setting;
- security profiles attached;
- NAT relationship;
- business owner;
- ticket/change reference;
- business justification;
- PCI evidence marker in the native description/comment/tag field where the platform supports it;
- expiry/review date;
- hit count and last-hit timestamp if available;
- whether rule is inbound to CDE, outbound from CDE, management, backup, monitoring, payment processor, third-party, or public DMZ;
- whether the rule violates the standard or needs compensating/customized treatment.

### 4. Add PCI Evidence Markers to Firewall Configs

Where the firewall platform supports descriptions, comments, annotations, labels, or tags, mark PCI-relevant configuration directly in the firewall. This makes audits easier because policy exports, NAT exports, zone lists, and object inventories carry visible evidence markers instead of requiring an assessor to infer PCI relevance from external spreadsheets alone.

Use this as a configuration hygiene standard, not as the only source of truth. The marker should point to evidence; it does not replace diagrams, change tickets, rule recertification, or assessor review.

Recommended marker pattern:

```text
PCI:<scope-or-control> REQ:<requirement-id-or-control-area> OWNER:<team-or-app> REF:<ticket-or-evidence-id> PURPOSE:<short-business-purpose>
```

Examples:

```text
PCI:CDE REQ:1.3.1 OWNER:Payments REF:CHG12345 PURPOSE:Payment API inbound from DMZ
PCI:CDE-EGRESS REQ:1.3.2 OWNER:Payments REF:CHG12346 PURPOSE:Processor settlement HTTPS
PCI:SEGMENTATION REQ:11.4.5 OWNER:NetSec REF:SEGTEST-2026Q2 PURPOSE:Non-CDE to CDE deny boundary
PCI:PUBLIC-WEB REQ:6.4.2 OWNER:Ecommerce REF:WAF-2026Q2 PURPOSE:WAF/WAAP in front of checkout
```

Apply markers where possible:

- security policies/rules that permit, deny, inspect, log, or segment CDE traffic;
- final explicit deny rules protecting the CDE;
- NAT rules that publish CDE/DMZ services or translate CDE outbound traffic;
- zones, interfaces, VRFs, virtual routers, VPC/VNet constructs, address books, dynamic groups, and security groups that represent CDE, DMZ, management, wireless, untrusted, or non-CDE segments;
- VPN, remote-access, third-party, vendor, backup, monitoring, logging, DNS, NTP, and payment-processor paths involving the CDE;
- IDS/IPS, WAF/WAAP, URL filtering, anti-malware, TLS inspection, or threat profiles attached to PCI-relevant traffic.

Marker rules:

- Keep markers short enough to survive platform field-length limits and exports.
- Never put PAN, cardholder names, customer data, secrets, credentials, private keys, or sensitive incident detail in descriptions.
- Prefer stable references: change ticket, CMDB CI, control ID, application ID, evidence package ID, or rule-review ID.
- Use consistent tokens (`PCI:CDE`, `PCI:SEGMENTATION`, `REQ:1.3.1`) so exports can be searched deterministically.
- If the platform has both a tag field and a description field, use tags for machine filtering and descriptions for human audit context.
- If the platform lacks descriptions for a construct, maintain the marker in the adjacent object/rule name, tag, external source-of-truth, or rule-review export.
- Do not let markers justify bad policy. A rule with `PCI:CDE` still needs least privilege, approval, logging, and periodic review.

Red flags:

- `any any allow` into or out of CDE;
- broad CDE outbound Internet access;
- direct Internet access to systems that store cardholder data;
- unused rules with old hit counts;
- disabled rules kept without reason;
- rule names with no owner or business purpose;
- temporary rules without expiry;
- unlogged high-risk access;
- management access from user networks or untrusted networks;
- NAT exposing more services than policy intent suggests;
- PCI-relevant policies, NAT rules, zones, or objects with no description/tag/marker and no external evidence reference;
- object groups hiding broad networks;
- default vendor services enabled on management interfaces;
- policy shadowing or rule order that bypasses intended controls;
- IDS/IPS/WAF profiles attached but set to alert-only without documented rationale.

### 5. Validate Inbound Controls

Inbound to the CDE must be limited to necessary traffic, and all other traffic must be specifically denied. Validate:

- public services land in a DMZ or approved segment;
- only authorized ports/services are published;
- inbound from untrusted networks to trusted networks is limited to authorized public services or stateful responses;
- systems storing cardholder data are not directly accessible from untrusted networks;
- source restrictions are used where possible;
- VPN and vendor access terminate into controlled zones and require strong authentication;
- admin access is not exposed directly from the Internet;
- default deny is explicit and visible in policy;
- deny logs are useful enough for monitoring without overwhelming the SIEM.

### 6. Validate Outbound Controls

Outbound from the CDE must be limited to necessary traffic, and all other traffic must be specifically denied. Validate:

- CDE hosts do not have unrestricted Internet access;
- DNS, NTP, CRL/OCSP, update, logging, backup, monitoring, and payment processor flows are explicitly documented;
- outbound web access uses approved proxy/inspection paths when required;
- egress filtering blocks direct exfiltration paths where practical;
- service accounts and automated jobs have known destinations;
- deny events are monitored for unexpected outbound attempts;
- cloud metadata/API access is controlled when CDE workloads run in cloud.

### 7. Validate Segmentation

If segmentation reduces PCI scope, the controls must be tested. Validate:

- segmentation design is documented;
- non-CDE networks cannot reach CDE except through authorized policy;
- CDE cannot initiate unnecessary access to non-CDE networks;
- management and monitoring paths are included in scope analysis;
- identity, DNS, logging, virtualization, cloud control plane, backup, and jump systems are considered CDE-impacting where applicable;
- segmentation tests are performed by qualified personnel, cover both inside and outside perspectives, and are repeated after significant changes and at required intervals;
- test evidence includes methodology, source networks, destination networks, allowed/blocked results, findings, and remediation.

### 8. Validate Logging and Monitoring

Firewall/NGFW logs are part of PCI DSS monitoring evidence. Validate:

- traffic logs are enabled for CDE-relevant permits and denies according to risk;
- admin/system/config logs are enabled;
- IDS/IPS/WAF/threat logs are generated when those features are used;
- logs are sent to centralized log management/SIEM;
- time synchronization is correct;
- log access is restricted;
- log retention meets the entity’s PCI logging standard;
- alerts exist for high-risk events: CDE inbound deny spikes, new public exposure, admin login failures, policy changes, IPS critical alerts, WAF blocks, malware callbacks, unexpected CDE outbound traffic;
- daily review or automated alert review evidence exists;
- incident response procedures include firewall, IPS, WAF, and SIEM alerts.

### 9. Validate IDS/IPS and Web-App Protection

PCI DSS 11.5.1 expects intrusion-detection and/or intrusion-prevention techniques to monitor all traffic at the perimeter of the CDE and at critical points in the CDE, alert personnel to suspected compromises, and keep engines/baselines/signatures up to date. NGFW IPS can satisfy some or all of this if placement, visibility, signatures, alert routing, and response are evidenced.

PCI DSS 6.4.2 applies to public-facing web applications. It requires an automated technical solution deployed in front of public-facing web applications that continually detects and prevents web-based attacks, is actively running/up to date as applicable, generates audit logs, and is configured to block web-based attacks or generate an alert that is immediately investigated. A generic firewall policy is not automatically enough. Confirm whether the NGFW provides WAF/WAAP-grade controls, whether it is actually in front of the application, and whether application-layer attacks are detected/prevented.

## Evidence Request Checklist

Ask for these artifacts before claiming alignment:

- [ ] PCI scope statement and CDE asset inventory
- [ ] current network diagrams showing CDE, non-CDE, wireless, untrusted, trusted, DMZ, remote access, cloud, and third-party connections
- [ ] current cardholder data-flow diagrams
- [ ] firewall/NSC inventory and role map
- [ ] firewall configuration standards/baselines
- [ ] exported firewall configurations and policy/rulebase exports
- [ ] NAT, VPN, routing, and management-plane configurations
- [ ] rule owner/business justification/ticket data
- [ ] PCI markers in supported policy, NAT, zone, object, tag, and profile description/comment fields, plus an explanation for any platform where markers cannot be embedded
- [ ] last six-month firewall review evidence and remediation output
- [ ] change tickets for recent firewall/network changes
- [ ] admin access list, roles, MFA/encryption evidence, and authentication source
- [ ] syslog/SIEM forwarding configuration and sample logs
- [ ] daily log review or alert workflow evidence
- [ ] IDS/IPS profile placement, update status, and alert examples
- [ ] WAF/WAAP or equivalent 6.4.2 evidence for public-facing web applications
- [ ] vulnerability scan reports, including ASV reports where applicable
- [ ] penetration test and segmentation test methodology/results/remediation
- [ ] incident response plan sections covering firewall/IPS/WAF/SIEM alerts
- [ ] cryptographic protocol/cipher inventory for VPN, admin UI, TLS inspection, and public services
- [ ] configuration backups and restore/integrity controls

## Output Patterns

### Short Answer to “Is This NGFW PCI Compliant?”

Use language like:

```text
An NGFW is not PCI DSS compliant by itself; PCI DSS compliance is assessed for the entity and its in-scope environment. This NGFW can support PCI DSS if it is configured and operated as an effective network security control: documented CDE scope, least-privilege inbound and outbound rules, explicit deny, secure management, change control, six-month rule reviews, centralized logging, IDS/IPS or equivalent monitoring where required, segmentation testing if used for scope reduction, and evidence tying each rule to business need.
```

### Gap Finding Format

```text
Finding: Broad outbound CDE Internet access
PCI DSS mapping: 1.3.2, 1.2.5, 10.2/10.4 if logs are insufficient
Evidence: Rule 220 allows CDE-SERVERS to Internet on any service; no owner/justification; 90-day hit count active.
Risk: Compromised CDE hosts can establish arbitrary outbound sessions, increasing exfiltration and command-and-control risk.
Recommendation: Replace with documented egress allowlist for payment processor, DNS, NTP, update, logging, and proxy paths; add explicit deny logging; record owner/business need; process through change control.
Assessor note: Validate with QSA whether any customized or compensating control is required for residual broad egress.
```

### Assessor-Ready Summary Format

```text
Control area: PCI DSS Requirement 1 - Network Security Controls
Scope: Firewalls FW-A/FW-B protect CDE zones CARD-APP, CARD-DB, CARD-MGMT and DMZ-PAYMENT.
Design: Inbound and outbound CDE access is default-deny with explicit business-approved permits. Public services terminate in DMZ-PAYMENT. No systems storing cardholder data are directly reachable from untrusted networks.
Evidence reviewed: network diagram v2026-06, data-flow diagram v2026-05, policy export 2026-06-20, change tickets CHG001-CHG017, six-month review record 2026-Q2, SIEM log samples, segmentation test report 2026-04.
Open gaps: Rule 145 lacks owner; IPS signature update evidence missing for FW-B; outbound update rule needs destination narrowing.
Conclusion: Substantially aligned with Requirement 1 pending remediation/evidence for listed gaps; final determination belongs to the assessor.
```

## Common Pitfalls

1. Saying a product is “PCI compliant.” Prefer “supports PCI DSS controls when properly configured and operated.”
2. Starting with firewall rules before establishing CDE scope and data flows.
3. Treating segmentation as valid without penetration test evidence.
4. Ignoring outbound CDE traffic. PCI DSS v4.0.1 explicitly addresses outbound restriction from the CDE.
5. Assuming an NGFW IPS profile automatically satisfies 11.5.1 without verifying traffic coverage, alerting, update status, and response.
6. Assuming a firewall URL filtering or IPS feature automatically satisfies 6.4.2 for public-facing web applications. Confirm WAF/WAAP or equivalent web-attack detection/prevention.
7. Reviewing only Internet edge firewalls while ignoring internal segmentation, cloud security groups, VPN, wireless, management, and third-party paths.
8. Ignoring NAT. Published services and translated addresses often change what is actually exposed.
9. Keeping broad object groups without expanding them during audit.
10. Accepting “business need: required” as justification. Every allowed service/protocol/port needs a specific business purpose.
11. Relying on hit counts alone. Unused rules may still be required for DR or seasonal processing, but they need owner approval and documented rationale.
12. Forgetting management-plane controls: admin encryption, RBAC, MFA, AAA, management interface exposure, logging, and backups.
13. Logging too little for audit or too much for operations. Align logging to detection and review processes.
14. Missing service-provider/shared-responsibility boundaries for managed firewalls, cloud firewalls, WAF, SIEM, or SOC.
15. Producing compliance conclusions without evidence IDs, dates, and open gaps.
16. Leaving PCI-relevant firewall config unmarked. Where possible, policy, NAT, zone/segment, object, and security-profile descriptions/tags should carry concise `PCI:`/`REQ:` evidence markers.
17. Putting sensitive data in descriptions. Markers should reference evidence IDs and business purpose, never PAN, customer data, credentials, or incident details.

## Verification Checklist

Before finalizing a PCI/NGFW answer:

- [ ] Confirm the PCI DSS version being used, defaulting to v4.0.1 when current.
- [ ] State that PCI compliance applies to the entity/environment, not the NGFW alone.
- [ ] Identify CDE scope and whether segmentation is used for scope reduction.
- [ ] Map claims to PCI DSS requirement IDs, especially 1.x, 2.2.7, 4.2.1, 6.4.2, 10.x, 11.x, and 12.x.
- [ ] Check inbound and outbound restrictions separately.
- [ ] Verify all allowed services/protocols/ports have business need and approval.
- [ ] Verify PCI-relevant policy, NAT, zone/segment, object, and profile entries include concise PCI evidence markers where the platform supports descriptions/tags/comments.
- [ ] Verify change control and six-month NSC review evidence.
- [ ] Verify logging, alerting, review, and incident response evidence.
- [ ] Verify IDS/IPS placement, signatures/baselines, and alert response where claimed.
- [ ] Verify WAF/WAAP or equivalent controls for public-facing web applications where applicable.
- [ ] Verify segmentation testing evidence if scope reduction is claimed.
- [ ] Label assumptions and defer final determination to QSA/ISA/acquirer/payment brand when appropriate.
