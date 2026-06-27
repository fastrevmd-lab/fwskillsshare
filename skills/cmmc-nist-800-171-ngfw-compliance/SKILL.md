---
name: cmmc-nist-800-171-ngfw-compliance
description: Use when researching, designing, auditing, or explaining what it takes for a next-generation firewall or firewall estate to support CMMC Level 2 and NIST SP 800-171 protection of Controlled Unclassified Information. Covers CUI enclave scoping, boundary protection, least-privilege network access, remote access, external connections, audit logging, incident response, media/system boundaries, security assessment evidence, POA&M-style gaps, and audit-ready firewall description/tag markers. Emphasizes that CMMC/NIST 800-171 compliance is assessed for the contractor environment, not certified by an NGFW alone.
version: 0.1.0
author: Hermes Agent
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [cmmc, nist-800-171, cui, compliance, firewall, ngfw, boundary-protection, audit, evidence, segmentation, access-control, remote-access, logging]
    related_skills: [srx-policy, srx-nat, parsing-srx-configs, parsing-palo-configs, parsing-fortinet-configs, parsing-cisco-configs, pci-ngfw-compliance, hipaa-ngfw-compliance, cis-controls-ngfw-compliance]
  sources:
    - title: "NIST SP 800-171 Rev. 2: Protecting Controlled Unclassified Information in Nonfederal Systems and Organizations"
      author: National Institute of Standards and Technology
      url: https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final
      retrieved: "2026-06-27"
    - title: "NIST SP 800-171 Rev. 3: Protecting Controlled Unclassified Information in Nonfederal Systems and Organizations"
      author: National Institute of Standards and Technology
      url: https://csrc.nist.gov/pubs/sp/800/171/r3/final
      retrieved: "2026-06-27"
    - title: "Cybersecurity Maturity Model Certification (CMMC) Program and Documentation"
      author: U.S. Department of Defense Chief Information Officer
      url: https://dodcio.defense.gov/CMMC/
      retrieved: "2026-06-27"
---

# CMMC / NIST 800-171 NGFW Compliance Research

## Overview

Use this skill to answer questions like “what does an NGFW need to do for CMMC Level 2?” or “is this firewall design sufficient for NIST 800-171 boundary protection around CUI?” The core answer is: a next-generation firewall is not CMMC compliant by itself. CMMC and NIST SP 800-171 are assessed against the contractor environment, the systems that store, process, or transmit Controlled Unclassified Information (CUI), and the policies, procedures, people, evidence, and technical controls used to protect that CUI.

An NGFW can be a major supporting control. It can enforce CUI enclave segmentation, boundary protection, default-deny access, remote-access restrictions, external connection control, secure administrative access, IDS/IPS, threat prevention, logging, and incident response visibility. It only supports CMMC/NIST 800-171 when it is selected through risk and scope decisions, configured according to documented policy, monitored, reviewed, maintained, and tied to System Security Plan (SSP), assessment objective, and remediation evidence.

Treat this as research and assessment guidance, not legal advice and not a C3PAO, assessor, DoD, or contracting-officer determination. When producing formal compliance language, cite NIST SP 800-171 requirement IDs and CMMC practice language where applicable, label assumptions, and defer final interpretation to the organization’s CMMC lead, compliance team, legal counsel, prime/customer, or authorized assessor.

## When to Use

Use this skill when the user asks about:

- CMMC Level 2 or NIST SP 800-171 firewall, NGFW, perimeter firewall, internal segmentation firewall, VPN, cloud firewall, IDS/IPS, or remote-access requirements
- CUI enclave design, contractor networks, defense industrial base (DIB) environments, or supplier compliance evidence
- mapping firewall capabilities to NIST 800-171 Access Control, Audit and Accountability, Configuration Management, Identification and Authentication, Incident Response, Risk Assessment, Security Assessment, System and Communications Protection, or System and Information Integrity requirements
- boundary protection, external system connections, public-access systems, wireless boundaries, cloud security groups, zero-trust segmentation, or vendor/third-party access to CUI systems
- preparing SSP language, assessment evidence, gap findings, POA&M-style remediation tasks, or rule-review evidence for CMMC/NIST 800-171
- comparing Palo Alto, FortiGate, Juniper SRX, Cisco ASA/FTD, Check Point, cloud security groups, host firewalls, ZTNA/SASE, or microsegmentation controls against CUI protection needs

Do not use this skill as a substitute for parsing a vendor config. Load the relevant parser skill first when raw config is provided, then use this skill to interpret CMMC/NIST 800-171 implications.

## Baseline Interpretation

### What “CMMC-Compliant NGFW” Really Means

Avoid saying “this NGFW is CMMC compliant” as a standalone claim. More accurate phrasing:

- “This NGFW can support CMMC Level 2 / NIST 800-171 security requirements if configured and operated appropriately for the CUI environment.”
- “This firewall design appears aligned with selected NIST 800-171 access control, audit, and boundary-protection requirements, subject to SSP, evidence, and assessment review.”
- “The firewall is one control in the contractor’s CUI protection program; compliance depends on scope, documented practices, configuration, monitoring, access governance, incident response, and evidence.”

A CMMC-supporting firewall estate needs more than product features. It needs:

1. identified CUI assets, CUI data flows, and CUI security protection assets;
2. a documented system boundary and CUI enclave scope;
3. an SSP that describes how firewall controls implement relevant requirements;
4. network diagrams and data-flow diagrams that match the implemented firewall policy;
5. least-privilege access paths to systems that store, process, or transmit CUI;
6. controlled external connections and boundary protection between CUI systems and external/untrusted networks;
7. secure remote access using approved encryption and authentication;
8. logging, monitoring, alerting, and review of CUI-relevant firewall/VPN/admin/security events;
9. configuration management, change control, backups, and periodic review of firewall rules and security profiles;
10. incident response processes that use firewall evidence for detection, analysis, containment, and reporting;
11. evidence retained and organized by requirement and assessment objective.

### CUI Scope Comes First

Before evaluating firewall controls, determine what is in scope:

- systems that store, process, or transmit CUI;
- systems that provide security protection for CUI systems, including firewalls, VPNs, identity, logging, monitoring, vulnerability scanning, endpoint management, backups, virtualization/cloud control planes, jump hosts, and firewall managers;
- systems that can affect CUI confidentiality, integrity, or availability;
- external systems and connections used by customers, primes, subcontractors, vendors, cloud providers, MSP/MSSP/SOC providers, remote workers, and administrators;
- public-facing systems that are separated from internal CUI systems;
- wireless, guest, lab, OT, manufacturing, engineering, developer, build, test, and management networks that can reach or influence CUI systems.

Do not assume a VLAN, zone, VPC/VNet, subnet, tag, “CUI enclave” label, or “corporate internal” label is enough. The question is whether only authorized users, processes, and services can reach CUI systems, and whether the boundary is documented, monitored, tested, and maintained.

### CMMC Level 2 and NIST 800-171 Version Awareness

CMMC Level 2 has historically aligned to the 110 security requirements in NIST SP 800-171 Rev. 2. NIST SP 800-171 Rev. 3 changes organization and requirement text. When answering, confirm which contractual or assessment basis applies. If the user does not specify, default to CMMC Level 2 / NIST SP 800-171 Rev. 2 style requirement IDs for CMMC work, while noting that Rev. 3 exists and may matter for non-CMMC or future alignment work.

Do not mix Rev. 2 and Rev. 3 IDs without labeling them. Do not claim a Rev. 3 mapping satisfies a CMMC assessment unless the user’s assessment basis says so.

## Requirement Mapping for NGFW Controls

Use this table as a first-pass mapping for CMMC Level 2 / NIST SP 800-171 Rev. 2-oriented work. Always verify exact requirement text, current CMMC program rules, and contractual requirements during formal assessment work.

| NIST 800-171 / CMMC area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| 3.1.1 Authorized access control | Limit network access to CUI systems to authorized users, processes, and services | Rulebase, identity/VPN mapping, source/destination/service justification |
| 3.1.2 Transaction/function control | Restrict permitted traffic to authorized functions and roles | App/service allowlists, admin path separation, role-based access design |
| 3.1.3 Control CUI flow | Enforce CUI enclave boundaries and approved CUI data paths | CUI data-flow diagrams, segmentation rules, egress rules, deny logs |
| 3.1.5 Least privilege | Permit only necessary access and services | Rule owner, business purpose, hit counts, temporary access expiry |
| 3.1.7 Privileged functions | Separate and protect administrative firewall/VPN/management access | Management zone design, admin ACLs, MFA/AAA/RBAC, audit logs |
| 3.1.8 Unsuccessful login attempts | Support monitoring of failed admin/VPN logins | AAA/VPN logs, SIEM alerts, lockout evidence |
| 3.1.12 Remote access monitoring/control | Control and monitor remote access sessions into CUI environments | VPN/ZTNA policy, MFA, logs, session restrictions, alert rules |
| 3.1.13 Cryptographic remote access | Protect remote access with approved cryptography | IPsec/TLS/SSH settings, certificate/cipher evidence, weak protocol removal |
| 3.1.14 Route remote access through managed points | Force remote access through controlled access points | VPN concentrator/firewall path, split-tunnel rules, route controls |
| 3.1.16 Wireless access authorization | Restrict wireless paths to CUI networks | Wireless-to-CUI firewall policy, NAC/WLAN diagrams, deny evidence |
| 3.1.18 Mobile device connection control | Restrict mobile/device paths to CUI systems | VPN/posture policy, device groups, firewall segmentation |
| 3.1.20 External connections | Verify and control external system connections | Partner/vendor VPNs, interconnect agreements, firewall rules, approvals |
| 3.1.22 Public information posting | Separate public systems from internal/CUI systems | DMZ design, NAT/policy exports, no direct CUI storage exposure |
| 3.3.1 Audit logging | Generate records for firewall/VPN/admin/security events | Syslog/SIEM forwarding, traffic/threat/admin logs, sample events |
| 3.3.2 User accountability | Correlate admin/VPN activity to named users where possible | AAA, SSO, MFA, admin accounts, VPN user logs |
| 3.3.3 Audit review | Support review and analysis of CUI-relevant security events | SIEM detections, alert workflow, review records |
| 3.3.4 Audit reduction/reporting | Provide searchable, normalized firewall evidence | Log parsing, dashboards, saved searches, reports |
| 3.3.5 Audit correlation | Synchronize time and correlate across systems | NTP, SIEM timestamps, firewall/VPN/identity correlation |
| 3.3.8 Audit protection | Protect logs from unauthorized access or modification | SIEM RBAC, immutable storage, log pipeline controls |
| 3.4.1 Baseline configuration | Firewall configuration standards and secure baselines | Baseline template, hardening standard, approved config snapshot |
| 3.4.3 Change tracking | Track and approve firewall rule/config changes | Change tickets, diffs, approvals, emergency change records |
| 3.4.6 Least functionality | Disable unnecessary firewall services and broad rules | Management services, insecure protocol removal, service allowlists |
| 3.4.7 Restrict nonessential ports/protocols | Block unnecessary ports and protocols to CUI systems | Rule review evidence, app/service inventory, deny policy |
| 3.4.8 Deny by exception | Default-deny approach for traffic not explicitly permitted | Final deny rules, implicit deny documentation, deny logs |
| 3.5.3 Multifactor authentication | Support MFA on remote/admin access paths where applicable | VPN/admin MFA config, IdP policy, authentication logs |
| 3.5.4 Replay-resistant authentication | Use secure admin/VPN authentication mechanisms | Certificate/SSH/TLS/IPsec details, disabled weak auth |
| 3.6.1 Incident response capability | Firewall events feed incident identification and containment | IR runbooks, alert mappings, sample investigations |
| 3.6.2 Incident tracking/reporting | Firewall evidence supports incident tracking and lessons learned | Tickets, timelines, firewall logs, containment changes |
| 3.11.2 Vulnerability scanning | Firewall interfaces/rules are included in scan planning | Scan scope, remediation tickets, management-plane exposure review |
| 3.12.1 Security control assessment | Firewall controls are assessed for effectiveness | Assessment plan, test results, rule review, segmentation validation |
| 3.12.2 Remediation | Firewall gaps become tracked remediation items | POA&M/gap register, owners, due dates, status evidence |
| 3.12.4 System Security Plan | SSP describes firewall implementation of requirements | SSP sections, diagrams, control narratives, evidence references |
| 3.13.1 Boundary protection | Monitor, control, and protect communications at boundaries | Boundary diagrams, firewall policy, IDS/IPS, deny logs, external paths |
| 3.13.3 Separate user/functionality | Separate user functions from system management functions | Management network, jump hosts, admin policy separation |
| 3.13.5 Public-access separation | Keep public-access systems separate from internal systems | DMZ, NAT, reverse proxy/WAF, no direct CUI database exposure |
| 3.13.8 Transmission confidentiality | Protect CUI in transit with cryptography where required | VPN/TLS/IPsec/SSH evidence, cipher/protocol inventory |
| 3.13.11 CUI encryption at rest/in transit adjunct | Firewall supports in-transit enforcement; not storage encryption | Rules requiring secure protocols, blocked plaintext alternatives |
| 3.13.12 Collaborative/mobile code restrictions | Control network paths for risky content/services | Egress filtering, URL/app controls, sandbox/threat profiles |
| 3.13.13 Mobile code execution | Monitor/block unauthorized mobile code channels where relevant | App control, URL filtering, threat prevention logs |
| 3.13.16 CUI at external systems | Control CUI transmissions to external systems | Partner VPNs, egress allowlists, cloud/private link paths |
| 3.14.3 Security alerts/advisories | Use firewall/IPS/vendor alerts in vulnerability response | Firmware/advisory tracking, signature updates, emergency changes |
| 3.14.6 Monitor communications | Monitor inbound/outbound traffic for attacks and indicators | IDS/IPS/threat logs, SIEM alerts, detection tuning |
| 3.14.7 Identify unauthorized use | Detect unauthorized access or anomalous CUI network use | Deny events, impossible travel/VPN anomalies, egress anomalies |

## NGFW Feature Expectations

A CMMC-supporting firewall estate does not need every feature enabled everywhere, but it should clearly show how each relevant risk and requirement is handled.

### Core Network Security Control Features

Minimum expectations:

- stateful traffic filtering between CUI systems and less-trusted networks;
- explicit zone/interface/segment model for CUI, non-CUI, public/DMZ, guest, wireless, vendor, remote-access, management, backup, logging, and cloud networks;
- default-deny behavior between CUI and non-CUI segments unless a documented business need exists;
- specific source, destination, application/service, user/device, and zone criteria where technically possible;
- controlled outbound CUI egress for updates, DNS, NTP, logging, backup, cloud services, customer/primes, and approved business systems;
- controlled inbound paths for remote access, support, public services, file transfer, and partner/customer connections;
- NAT rules documented so reviewers can understand actual exposure and path selection;
- CMMC/CUI evidence markers in supported description/comment/tag fields for policies, NAT rules, zones/segments, objects, VPNs, and security profiles;
- management-plane isolation, encrypted admin protocols, MFA/AAA/RBAC where applicable, and no direct untrusted management exposure;
- centralized logging, time synchronization, log protection, and SIEM forwarding;
- configuration backup, restore, high availability, and change-integrity controls.

### NGFW “Next-Generation” Features

Useful features that may support CMMC/NIST 800-171 evidence:

- application identification to reduce broad port-only permits;
- user identity integration for VPN, ZTNA, admin, and controlled user access paths;
- IDS/IPS, anti-malware, sandboxing, DNS security, URL filtering, and reputation controls;
- TLS inspection where legally and operationally justified, and where it does not expose CUI improperly to logs or analysts;
- data-loss or exfiltration detection features where appropriate for CUI egress risk;
- device posture, certificate, or conditional-access integration for remote access;
- dynamic address groups/tags for cloud or endpoint-driven segmentation, provided tag sources are governed and evidenced;
- WAF/WAAP or API protection for public-facing portals that bridge to internal CUI systems.

Do not overclaim NGFW features. CMMC/NIST 800-171 does not mandate a specific firewall brand or “next-generation” feature set. The relevant question is whether the implemented controls satisfy the requirements and assessment objectives for the scoped CUI environment.

## Assessment Workflow

### 1. Establish CUI Scope and Architecture

Collect:

- CUI asset inventory and CUI data-flow diagrams;
- SSP boundary description and diagrams;
- network diagrams showing CUI, non-CUI, public/DMZ, cloud, wireless, management, logging, backup, remote-access, and vendor/customer networks;
- firewall/NSC inventory, including physical, virtual, cloud-native, host-based, VPN, ZTNA/SASE, IDS/IPS, WAF/WAAP, microsegmentation, and firewall managers;
- external connection inventory: customers, primes, subcontractors, vendors, cloud services, MSP/MSSP/SOC, remote users, support paths, file exchanges, APIs, and email/file transfer paths;
- system security protection assets and CUI security protection assets that provide boundary, identity, logging, monitoring, and management functions.

Questions to answer:

- Where is CUI stored, processed, or transmitted?
- Which systems provide security protection for CUI systems?
- Which firewalls enforce the CUI boundary?
- Which networks can initiate access to CUI systems?
- Which CUI egress paths are approved and why?
- Which external systems connect to the environment, and are those connections authorized and documented?
- Are cloud security groups, Kubernetes policies, service meshes, NAC, endpoint firewalls, ZTNA policies, or SDN constructs part of the evidence set?

### 2. Build a Firewall-to-Requirement Matrix

For each in-scope firewall/NSC, map:

- hostname/device ID;
- platform and version;
- owner/team;
- role: CUI enclave boundary, Internet edge, internal segmentation, VPN/ZTNA, public DMZ, cloud security control, management-plane control, IDS/IPS, WAF/WAAP, logging path;
- CUI systems or segments protected;
- relevant NIST 800-171 / CMMC practices;
- log destination and retention;
- change-control system;
- backup/config repository;
- HA/DR role;
- last rule review date;
- last assessment/test date;
- known exceptions, accepted risks, or POA&M items.

Output example:

```text
Firewall: SRX-CUI-EDGE-01
Scope: CUI engineering enclave, VPN remote access, vendor SFTP DMZ
NIST/CMMC mapping: 3.1.3, 3.1.12, 3.1.13, 3.1.20, 3.3.1, 3.4.7, 3.13.1, 3.13.8, 3.14.6
Evidence: SSP-SEC-BOUNDARY-02, CHG-20441, SIEM-CUI-FW, VPN-MFA-2026Q2, RULE-REVIEW-2026Q2
Open gap: Legacy vendor tunnel uses broad destination group; remediation POAM-117 narrows access by 2026-08-15
```

### 3. Review Rulebase for CUI Intent

For each policy/rule touching CUI systems, CUI security protection assets, or external CUI paths, capture:

- rule name and UUID;
- source zone/interface/network/user/device;
- destination zone/interface/network/object;
- application/service/port;
- action and security profile;
- NAT relationship;
- logging enabled/disabled;
- owner and business purpose;
- ticket/change reference;
- SSP/control/evidence reference;
- CMMC/CUI evidence marker;
- expiry or review date for temporary/vendor access;
- hit count and last-hit timestamp if available;
- whether the rule is CUI inbound, CUI outbound, CUI enclave segmentation, remote access, admin/management, vendor/customer, backup, logging, monitoring, update, public DMZ, cloud, or incident-response emergency access;
- whether the rule violates the standard, requires remediation, or has documented risk treatment.

### 4. Add CMMC/CUI Evidence Markers to Firewall Configs

Where the firewall platform supports descriptions, comments, annotations, labels, or tags, mark CMMC/CUI-relevant configuration directly in the firewall. This makes assessments easier because policy exports, NAT exports, zone lists, VPN lists, object inventories, and security-profile exports carry visible evidence markers instead of requiring a reviewer to infer CUI relevance from spreadsheets alone.

Use markers as configuration hygiene and audit-evidence pointers, not proof of compliance. The marker should point to evidence; it does not replace the SSP, diagrams, change tickets, assessment evidence, rule recertification, incident records, or assessor review.

Recommended marker pattern:

```text
CMMC:<scope-or-control> NIST:<req-id> OWNER:<team-or-app> REF:<ticket-or-evidence-id> PURPOSE:<short-business-purpose>
```

Examples:

```text
CMMC:CUI NIST:3.1.3 OWNER:Engineering REF:CHG12345 PURPOSE:CUI app to license server
CMMC:BOUNDARY NIST:3.13.1 OWNER:NetSec REF:SSP-BND-02 PURPOSE:CUI enclave default deny boundary
CMMC:REMOTE NIST:3.1.12 OWNER:IT REF:VPN-2026Q2 PURPOSE:MFA VPN to CUI jump host
CMMC:EXTERNAL NIST:3.1.20 OWNER:Contracts REF:IAA-CUST01 PURPOSE:Customer CUI SFTP exchange
CMMC:AUDIT NIST:3.3.1 OWNER:SecOps REF:SIEM-CUI-01 PURPOSE:Forward firewall and VPN logs
CMMC:EGRESS NIST:3.13.8 OWNER:Build REF:CHG45678 PURPOSE:Encrypted artifact upload to approved cloud
```

Apply markers where possible:

- security policies/rules that permit, deny, inspect, log, or segment CUI traffic;
- final explicit deny rules protecting CUI segments;
- NAT rules that publish CUI-adjacent services, DMZ services, remote-access endpoints, or translate CUI-system traffic;
- zones, interfaces, VRFs, virtual routers, VPC/VNet constructs, address books, dynamic groups, security groups, and NAC segments representing CUI, public, guest, wireless, vendor, management, backup, logging, or monitoring segments;
- VPN, ZTNA, remote-access, third-party, customer, subcontractor, vendor, backup, logging, monitoring, DNS, NTP, update, and emergency access paths involving CUI systems;
- IDS/IPS, WAF/WAAP, URL filtering, anti-malware, TLS inspection, DLP, DNS security, or threat profiles attached to CUI-relevant traffic.

Marker rules:

- Keep markers short enough to survive platform field-length limits and exports.
- Never put CUI content, export-controlled technical data, contract details beyond a stable reference, customer-sensitive data, secrets, credentials, private keys, vulnerability details, or incident details in descriptions.
- Prefer stable references: change ticket, CMDB CI, SSP section, NIST requirement ID, CMMC practice ID, POA&M item, application ID, customer/contract evidence ID, interconnection agreement ID, or rule-review ID.
- Use consistent tokens (`CMMC:CUI`, `CMMC:BOUNDARY`, `NIST:3.13.1`) so exports can be searched deterministically.
- If the platform has both a tag field and a description field, use tags for machine filtering and descriptions for human assessment context.
- If the platform lacks descriptions for a construct, maintain the marker in the adjacent object/rule name, tag, external source-of-truth, or rule-review export.
- Do not let markers justify bad policy. A rule with `CMMC:CUI` still needs authorized access, least privilege, logging, approval, and periodic review.

Red flags:

- broad `any any allow` into or out of CUI segments;
- unrestricted CUI-system Internet egress;
- direct Internet access to CUI file shares, repositories, databases, engineering systems, backup systems, or management interfaces;
- CUI enclave reachable from guest, public, wireless, lab, dev/test, OT/manufacturing, or general user networks without documented need;
- vendor/customer/subcontractor VPN access without MFA, source restriction, named owner, approval, monitoring, or expiry;
- remote access that bypasses managed access points or uses weak encryption;
- split tunneling that permits unmanaged paths to CUI without documented control rationale;
- unlogged high-risk access or disabled logging on CUI-relevant rules;
- firewall admins using shared accounts or management access from untrusted networks;
- rules with no owner, business purpose, ticket, SSP/control reference, or review date;
- temporary rules without expiry;
- NAT exposing more services than policy intent suggests;
- CMMC/CUI-relevant policies, NAT rules, zones, VPNs, or objects with no description/tag/marker and no external evidence reference;
- object groups hiding broad networks or shadowing intended restrictions;
- policy shadowing or rule order that bypasses intended controls;
- IDS/IPS/threat profiles attached but disabled, outdated, or alert-only without documented rationale.

### 5. Validate Access Control and CUI Flow

For 3.1.x practices, validate:

- CUI systems are reachable only from authorized user, app, service, management, remote-access, and vendor/customer segments;
- source and destination objects are specific enough to support authorized access decisions;
- traffic from non-CUI to CUI is default-deny except documented business paths;
- outbound CUI egress is restricted to approved destinations and secure protocols;
- CUI data flows match the SSP and diagrams;
- administrative paths are separated from user traffic and protected by MFA/AAA/RBAC;
- emergency access paths exist only if documented, logged, reviewed, and cleaned up;
- guest, public, wireless, lab, OT/manufacturing, and general user networks cannot initiate CUI access without explicit approval.

### 6. Validate Remote Access and External Connections

For 3.1.12, 3.1.13, 3.1.14, 3.1.20, and 3.13.8, validate:

- remote access terminates through managed access points such as VPN, ZTNA, bastion/jump host, or SASE control;
- remote users and admins use MFA where required by the environment and assessment basis;
- remote access uses approved secure protocols and current cryptographic settings;
- routes and split-tunnel behavior do not bypass monitoring or boundary controls;
- external connections to customers, primes, subcontractors, cloud services, vendors, and MSP/MSSP/SOC providers are documented and authorized;
- third-party and vendor access is least privilege, named, logged, approved, time-bound, and periodically reviewed;
- customer or contractual connection requirements are captured as evidence references, not embedded as sensitive details in firewall descriptions.

### 7. Validate Boundary Protection and Public Systems

For 3.13.1 and 3.13.5, validate:

- communications at CUI enclave boundaries are monitored, controlled, and protected;
- public-facing systems are isolated in DMZ or equivalent segments;
- public systems do not directly expose internal CUI stores unless a documented architecture and compensating controls justify the path;
- NAT and security policy together reflect intended exposure;
- IDS/IPS, WAF/WAAP, reverse proxy, or threat prevention is placed where the design relies on those controls;
- boundary deny logs and high-risk permit logs feed monitoring and incident response;
- cloud security groups/NACLs/firewalls and on-prem firewalls are considered together for hybrid environments.

### 8. Validate Audit Logging and Monitoring

For 3.3.x and 3.14.x, validate:

- allow and deny logs are enabled for CUI-relevant boundaries where operationally appropriate;
- VPN authentication, admin logins, failed logins, policy changes, threat events, NAT hits, IDS/IPS events, and denied CUI access are logged;
- logs are sent to centralized SIEM/log management with reliable time synchronization;
- log retention and protection align to organizational policy and assessment needs;
- review or alerting covers high-risk events such as CUI-boundary denies, unexpected egress, vendor VPN access, malware/IPS hits, admin login failures, policy changes, and new public exposure;
- sample events can be retrieved for the assessment period and tied to named users or systems where possible;
- log pipelines avoid leaking CUI content into analyst tools or tickets unless authorized and protected.

### 9. Validate Configuration Management and Assessment Evidence

For 3.4.x and 3.12.x, validate:

- firewall configuration baselines exist and are implemented;
- changes are approved, reviewed, and traceable;
- startup/running or candidate/active configs are protected and backed up;
- unnecessary management services and insecure protocols are disabled;
- broad rules, stale rules, and unused objects are reviewed and remediated;
- rule review findings become tracked remediation or accepted-risk items;
- SSP narratives accurately describe the implemented firewall architecture;
- assessment evidence is organized by requirement/objective with dates, owners, artifacts, and open gaps.

## Evidence Request Checklist

Ask for:

- current SSP sections covering system boundary, network architecture, remote access, external connections, logging, incident response, and configuration management;
- CUI asset inventory and CUI data-flow diagrams;
- network diagrams with CUI, non-CUI, public/DMZ, cloud, wireless, vendor/customer, management, logging, backup, and remote-access boundaries;
- firewall inventory and management-plane architecture;
- firewall/security standards, secure baselines, and rule naming/description/tagging standard;
- firewall policy exports, NAT exports, zone/interface/object exports, VPN/ZTNA exports, routing exports, and security-profile exports;
- evidence that CMMC/CUI markers/descriptions exist for relevant policies, NAT, zones, VPNs, objects, and profiles where supported;
- change tickets, approvals, emergency changes, and policy diffs for sampled rules;
- rule review/recertification evidence, including owner, business purpose, hit count, last-hit, expiry, and remediation notes;
- external connection inventory, customer/prime/subcontractor/vendor connection approvals, and interconnection evidence;
- remote-access MFA, admin RBAC, certificate, and authentication evidence;
- syslog/SIEM forwarding configuration, time synchronization, sample firewall/VPN/admin/threat logs, and alert workflow evidence;
- vulnerability scan, penetration test, segmentation test, and remediation evidence where available;
- incident response runbooks and sample firewall-related investigations;
- firewall backup, restore, HA/failover, and DR evidence;
- cloud shared-responsibility evidence for cloud firewalls/security groups/WAF/SASE/ZTNA/SIEM providers;
- POA&M/gap register entries for firewall-related findings, with owner, target date, status, and compensating controls where applicable.

## Output Templates

### Short Assessment Summary

```text
Summary: The NGFW/firewall estate can support CMMC Level 2 / NIST SP 800-171 requirements, but compliance is assessed for the contractor environment and CUI protection program, not for the NGFW alone. The firewall evidence reviewed supports [strong/partial/weak] alignment with access control, audit logging, configuration management, remote access, boundary protection, and system/information integrity requirements. Key gaps are [gaps]. Required next steps are [actions]. Final assessment determination belongs to the authorized assessor/customer/compliance authority.
```

### Firewall Finding

```text
Finding: Broad vendor VPN access to CUI engineering enclave
NIST/CMMC mapping: 3.1.1, 3.1.3, 3.1.5, 3.1.12, 3.1.20, 3.3.1, 3.13.1
Evidence: Rule VPN-VENDOR-CUI permits vendor subnet 10.50.0.0/16 to CUI-ENG-SERVERS on multiple services. No rule description, owner, expiry, external-connection reference, or recent review evidence was provided.
Risk: Excessive vendor access could permit unauthorized access to CUI systems and may not align with least privilege, external connection control, or CUI flow restrictions.
Recommendation: Restrict source users/devices, destinations, and services; require MFA; add owner/ref/purpose markers; log sessions; document external connection authorization; recertify access; set expiry for temporary support paths.
```

### SSP / Evidence Narrative

```text
Control area: NIST SP 800-171 3.13.1 Boundary Protection
Scope: Firewalls FW-CUI-A/FW-CUI-B enforce the boundary between CUI-ENG, CUI-MGMT, DMZ-SFTP, VPN-USERS, CLOUD-CUI, and non-CUI corporate networks.
Implementation: CUI ingress and egress are default-deny with explicit business-approved permits. Remote access terminates on MFA VPN and reaches CUI systems only through jump hosts and approved application paths. Public file exchange terminates in DMZ-SFTP and does not directly expose internal CUI repositories.
Evidence reviewed: SSP section 10.2, network diagram v2026-06, CUI data-flow diagram v2026-05, policy export 2026-06-20, changes CHG001-CHG014, SIEM log samples, rule review 2026-Q2.
Open gaps: Rule 221 lacks owner; vendor SFTP path lacks current external-connection approval; FW-B IPS signature update evidence missing.
Conclusion: Substantially aligned pending remediation/evidence for listed gaps; final determination belongs to the assessor/customer authority.
```

### Evidence Marker Recommendation

```text
Recommended description:
CMMC:REMOTE NIST:3.1.12 OWNER:IT REF:CHG12345 PURPOSE:MFA VPN to CUI jump host

Do not include CUI, contract-sensitive detail, secrets, credentials, vulnerability details, or incident detail in the description. Put detailed justification in the ticket/evidence repository.
```

## Common Pitfalls

1. **Saying the firewall is CMMC compliant.** Say it supports CMMC/NIST 800-171 controls when configured and operated as part of the scoped environment.

2. **Skipping CUI scope.** Firewall conclusions are weak without CUI assets, CUI data flows, SSP boundary, and security protection asset identification.

3. **Mixing NIST 800-171 Rev. 2, Rev. 3, and CMMC Level 2 without labels.** Confirm the assessment basis and cite the right IDs.

4. **Treating segmentation labels as evidence.** VLANs, zones, and cloud tags need policy, diagrams, access tests, monitoring, and maintenance evidence.

5. **Ignoring outbound CUI egress.** CUI exfiltration risk often lives in broad outbound rules, cloud sync tools, unmanaged file transfer, and update/proxy exceptions.

6. **Overlooking security protection assets.** Firewalls, VPNs, identity, SIEM, backups, management hosts, vulnerability scanners, and cloud control planes may be in scope because they protect or affect CUI systems.

7. **Ignoring external connections.** Customer, prime, subcontractor, vendor, MSP/MSSP/SOC, cloud, and remote-access paths need authorization, restriction, logging, and review.

8. **Putting CUI or sensitive contract detail in descriptions.** Use stable evidence references and control markers, not regulated content, export-controlled details, secrets, or incident details.

9. **Logging too little or logging sensitive content carelessly.** Firewall logs should support review and incident response without unnecessarily exposing CUI in URLs, payload captures, or analyst workflows.

10. **Assuming VPN equals compliant remote access.** Validate MFA, cryptography, route control, split-tunnel behavior, managed access points, logging, and user/device authorization.

11. **Reviewing only the Internet edge.** Internal segmentation, cloud security groups, wireless, management, backup, logging, public DMZ, and vendor/customer paths matter.

12. **Treating POA&M-style gaps as closure.** Open gaps need owner, target date, status, risk/compensating controls, and evidence of completion when remediated.

13. **Leaving CMMC/CUI-relevant firewall config unmarked.** Where possible, policy, NAT, zone/segment, object, VPN, and security-profile descriptions/tags should carry concise `CMMC:`/`NIST:` evidence markers.

## Verification Checklist

Before finalizing a CMMC/NIST 800-171 NGFW answer:

- [ ] Confirm the assessment basis: CMMC Level 2 / NIST 800-171 Rev. 2, NIST 800-171 Rev. 3, contractual overlay, or other requirement set.
- [ ] State that compliance applies to the contractor environment/CUI protection program, not the NGFW alone.
- [ ] Identify CUI systems, CUI data flows, CUI boundary, and relevant security protection assets.
- [ ] Map claims to NIST 800-171 requirement IDs and CMMC practices/objectives where applicable.
- [ ] Check inbound, outbound, remote-access, external-connection, admin, logging, and public-system paths separately.
- [ ] Verify all allowed services/protocols/ports have business need, owner, approval, and review evidence.
- [ ] Verify CMMC/CUI-relevant policy, NAT, zone/segment, VPN, object, and profile entries include concise evidence markers where the platform supports descriptions/tags/comments.
- [ ] Verify change control, baseline configuration, backup, and periodic rule review evidence.
- [ ] Verify logging, time sync, alerting, review, log protection, and incident response evidence.
- [ ] Verify IDS/IPS/threat monitoring placement, update status, and alert response where claimed.
- [ ] Verify external connection approvals and third-party/vendor access restrictions where applicable.
- [ ] Verify gaps are recorded with owner, due date, risk, compensating control, and remediation status.
- [ ] Label assumptions and defer final determination to the authorized assessor/customer/compliance authority when appropriate.
