# HIPAA NGFW Compliance Research — Control Mapping

> Reference material for the `hipaa-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

## Requirement Mapping for NGFW Controls

Use this table as a first-pass mapping. Always verify exact text against current 45 CFR Part 164 Subpart C and the entity’s policies during formal work.

| HIPAA Security Rule area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| 164.306(a) General requirements | Protect confidentiality, integrity, and availability of ePHI against reasonably anticipated threats and impermissible uses/disclosures | Architecture, threat model, firewall standards, risk analysis linkage |
| 164.306(b) Flexibility of approach | Safeguards selected based on size, complexity, capabilities, cost, and risk | Risk acceptance, control selection rationale, compensating or alternative controls |
| 164.306(e) Maintenance | Review and modify safeguards as needed | Firewall review cadence, change records, rule recertification, standard updates |
| 164.308(a)(1)(ii)(A) Risk analysis | Network paths, segmentation gaps, remote access, ePHI exposure, and firewall weaknesses included in risk analysis | Risk assessment, network diagrams, vulnerability/pen test findings |
| 164.308(a)(1)(ii)(B) Risk management | Firewall controls reduce risks to reasonable and appropriate level | Remediation plan, firewall hardening, rule cleanup, accepted residual risks |
| 164.308(a)(1)(ii)(D) Information system activity review | Firewall, VPN, IDS/IPS, WAF, and SIEM records reviewed where relevant | Log review procedure, SIEM rules, alerts, sample investigations |
| 164.308(a)(4) Information access management | Network access to ePHI systems follows authorized access decisions | Rule ownership, source/destination/service justification, identity/VPN mapping |
| 164.308(a)(5) Security awareness and training | Firewall alerts and phishing/malware controls feed awareness where applicable | User training references, blocked threat examples, security reminders |
| 164.308(a)(6) Security incident procedures | Firewall/IPS/VPN alerts integrated into incident identification, response, and reporting | IR runbooks, escalation rules, incident tickets, test exercises |
| 164.308(a)(7) Contingency plan | Firewall and VPN controls support emergency operations and recovery access | DR diagrams, emergency access paths, backup firewall configs, failover tests |
| 164.308(a)(8) Evaluation | Periodic technical and nontechnical evaluation includes firewall safeguards | Assessment reports, firewall audit reports, remediation tracking |
| 164.308(b) Business associate arrangements | Vendor/firewall provider/MSP/cloud provider roles and incident duties defined | BAA, contracts, shared responsibility matrix, provider logs/evidence |
| 164.310(a) Facility access controls | Firewall management consoles and network equipment protected physically | Datacenter controls, console server restrictions, management network controls |
| 164.312(a) Access control | Network and remote access to ePHI systems limited to authorized users, processes, services | Firewall rules, VPN policies, zone model, zero-trust/identity policy evidence |
| 164.312(b) Audit controls | Hardware/software/procedures record and examine activity in systems containing/using ePHI | Syslog/SIEM forwarding, log categories, retention, sample firewall/VPN events |
| 164.312(c) Integrity | Controls reduce improper alteration/destruction of ePHI and firewall config | Config change control, admin RBAC, policy diff review, threat prevention logs |
| 164.312(d) Person or entity authentication | Administrative, VPN, API, and partner access paths authenticate entities | MFA, certificate auth, SSO, VPN auth logs, device posture checks |
| 164.312(e)(1) Transmission security | ePHI in transit over electronic communications networks protected from unauthorized access | TLS/IPsec/VPN design, allowed protocols, weak protocol removal, inspection policy |
| 164.312(e)(2)(i) Integrity controls | Transmitted ePHI protected against improper modification without detection | TLS/IPsec settings, secure routing paths, application-layer integrity evidence |
| 164.312(e)(2)(ii) Encryption | ePHI encrypted in transit whenever deemed appropriate | Encryption decision record, VPN/TLS configs, exceptions and alternatives |
| 164.314(a) Business associate contracts | Security incidents and subcontractor safeguards covered for managed firewall/cloud/security providers | BAA, incident notification language, vendor SOC/security evidence |
| 164.316(a) Policies and procedures | Firewall procedures are reasonable and appropriate and align to standards | Firewall policy standard, change procedure, remote-access procedure |
| 164.316(b) Documentation | Firewall decisions, reviews, policies, and assessments retained and updated | Evidence repository, 6-year retention mapping, review/update records |
