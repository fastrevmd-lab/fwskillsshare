# ISO 27001 NGFW Compliance Research — Control Mapping

> Reference material for the `iso27001-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

## ISO 27001 / Annex A Mapping for Firewall Work

Use this as a practical mapping. Exact control numbering and wording should be verified against the organization’s licensed ISO 27001/27002 materials and SoA.

| ISO / Annex A theme | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| Organizational controls and risk treatment | Firewall requirements driven by risk assessment, SoA, policies, ownership, and control objectives | ISMS scope, SoA, risk register, risk treatment plan, firewall policy standard |
| Information security roles and responsibilities | Defined owners for firewall platforms, rules, reviews, exceptions, and alerts | RACI, owners, rule metadata, review approvals |
| Asset and information inventory | Identify firewall assets, protected networks, services, data flows, and management systems | CMDB, firewall inventory, network diagrams, data-flow diagrams |
| Access control (A.5.15), Access rights (A.5.18), Privileged access rights (A.8.2) | Least-privilege network/VPN/vendor/app access (A.5.15/A.5.18); privileged firewall admin RBAC (A.8.2) | Rulebase exports, access reviews, admin RBAC, VPN groups, identity integration |
| Secure authentication (A.8.5) + Authentication information (A.5.17) | MFA/AAA for firewall admin and remote access (A.8.5); credential/key/break-glass handling (A.5.17) | MFA/AAA evidence, password/key policy, break-glass process, local-account review |
| Information access restriction (A.5.12, A.8.3, A.8.22) | Segment sensitive systems and restrict inbound/outbound/east-west paths | Zone model, segmentation rules, data-flow evidence, egress controls |
| Supplier and service-provider relationships (A.5.19–A.5.22) | Control MSP/MSSP/vendor/cloud-provider firewall access and shared responsibilities | Contracts, provider access records, shared responsibility matrix, supplier review |
| ICT supply chain / cloud service usage (A.5.21, A.5.23) | Govern cloud firewalls, WAFs, security groups, SASE/ZTNA, and managed SOC controls | Cloud architecture, provider responsibilities, managed-rule evidence |
| Configuration management (A.8.9) | Maintain secure baseline, rule standards, naming, descriptions/tags, backups, and version control | Baselines, config exports, backup records, diff/change evidence |
| Change management (A.8.32) | Approve, test, implement, and review firewall changes | Change tickets, emergency-change records, peer review, rollback plans |
| Logging and monitoring (A.8.15, A.8.16, A.8.17) | Generate, forward, protect, retain, alert on, and review firewall/VPN/admin/threat logs | Syslog/SIEM config, NTP, sample logs, alert rules, review records |
| Network security (A.8.20, A.8.21, A.8.22) | Manage network boundaries, segregation, routing, VPNs, DNS, WAF, IDS/IPS, and secure management | Network diagrams, policy/NAT/VPN exports, security profiles, admin ACLs |
| Malware / technical vulnerability management (A.8.7, A.8.8) | Support threat prevention and maintain patched firewall platforms/signatures | Firmware tracking, advisory review, signature/content status, vulnerability tickets |
| Backup and ICT readiness (A.8.13, A.5.30) | Back up firewall configs and maintain HA/DR for enforcement points | Backup jobs, restore tests, HA/failover tests, DR runbooks |
| Incident management (A.5.24–A.5.26) | Provide evidence and containment actions for security events | IR runbooks, sample investigations, containment tickets, post-incident reviews |
| Compliance and audit (A.5.35, A.5.36) | Demonstrate operating effectiveness, periodic review, and corrective action | Internal audit samples, corrective actions, management review inputs |
