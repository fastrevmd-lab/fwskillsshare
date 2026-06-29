# ISO 27001 NGFW Compliance Research — Control Mapping

> Reference material for the `iso27001-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

## ISO 27001 / Annex A Mapping for Firewall Work

Use this as a practical mapping. Exact control numbering and wording should be verified against the organization’s licensed ISO 27001/27002 materials and SoA.

| ISO / Annex A theme | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| Organizational controls and risk treatment | Firewall requirements driven by risk assessment, SoA, policies, ownership, and control objectives | ISMS scope, SoA, risk register, risk treatment plan, firewall policy standard |
| Information security roles and responsibilities | Defined owners for firewall platforms, rules, reviews, exceptions, and alerts | RACI, owners, rule metadata, review approvals |
| Asset and information inventory | Identify firewall assets, protected networks, services, data flows, and management systems | CMDB, firewall inventory, network diagrams, data-flow diagrams |
| Access control and access rights | Enforce least-privilege network, admin, VPN, vendor, and application access | Rulebase exports, access reviews, admin RBAC, VPN groups, identity integration |
| Authentication information | Protect firewall admin and remote-access authentication | MFA/AAA evidence, password/key policy, break-glass process, local-account review |
| Information access restriction | Segment sensitive systems and restrict inbound/outbound/east-west paths | Zone model, segmentation rules, data-flow evidence, egress controls |
| Supplier and service-provider relationships | Control MSP/MSSP/vendor/cloud-provider firewall access and shared responsibilities | Contracts, provider access records, shared responsibility matrix, supplier review |
| ICT supply chain / cloud service usage | Govern cloud firewalls, WAFs, security groups, SASE/ZTNA, and managed SOC controls | Cloud architecture, provider responsibilities, managed-rule evidence |
| Configuration management | Maintain secure baseline, rule standards, naming, descriptions/tags, backups, and version control | Baselines, config exports, backup records, diff/change evidence |
| Change management | Approve, test, implement, and review firewall changes | Change tickets, emergency-change records, peer review, rollback plans |
| Logging and monitoring | Generate, forward, protect, retain, alert on, and review firewall/VPN/admin/threat logs | Syslog/SIEM config, NTP, sample logs, alert rules, review records |
| Network security | Manage network boundaries, segregation, routing, VPNs, DNS, WAF, IDS/IPS, and secure management | Network diagrams, policy/NAT/VPN exports, security profiles, admin ACLs |
| Malware / technical vulnerability management | Support threat prevention and maintain patched firewall platforms/signatures | Firmware tracking, advisory review, signature/content status, vulnerability tickets |
| Backup and ICT readiness | Back up firewall configs and maintain HA/DR for enforcement points | Backup jobs, restore tests, HA/failover tests, DR runbooks |
| Incident management | Provide evidence and containment actions for security events | IR runbooks, sample investigations, containment tickets, post-incident reviews |
| Compliance and audit | Demonstrate operating effectiveness, periodic review, and corrective action | Internal audit samples, corrective actions, management review inputs |
