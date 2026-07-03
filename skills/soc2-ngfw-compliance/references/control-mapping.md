# SOC 2 NGFW Compliance Research — Control Mapping

> Reference material for the `soc2-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

## SOC 2 Criteria Mapping for Firewall Work

Use this practical mapping as a starting point. Exact criteria and points of focus should be verified against the current AICPA materials and the organization’s control matrix.

| SOC 2 area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| CC1 / control environment support | Defined owners, responsibilities, and governance for firewall controls | RACI, policy ownership, control matrix, training/acknowledgment records |
| CC2 / communication and information | Firewall controls documented and communicated through policies/procedures | Network security policy, change procedure, rule standard, evidence repository |
| CC3 / risk assessment | Network risks drive firewall requirements and exceptions | Risk register, threat model, exception/risk acceptance records |
| CC4 / monitoring activities | Periodic firewall rule reviews, control self-assessments, and internal-audit style evaluations of firewall controls | Rule-review records, self-assessment reports, tracked remediation of identified deficiencies |
| CC5 / control activities | Firewall rules, baselines, reviews, approvals, and alerts operate as control activities | Config exports, rule reviews, tickets, samples, approvals |
| CC6 logical and physical access (esp. CC6.1 access security, CC6.6 external boundary protection, CC6.7 data-in-transit) | Restrict network, admin, remote, service, vendor, and customer-data access | Rulebase, VPN groups, MFA/AAA/RBAC, admin reviews, vendor access evidence |
| CC7 system operations | Detect firewall vulnerabilities/misconfigurations (CC7.1); monitor firewall/VPN/admin/threat events (CC7.2); evaluate and respond to events/incidents (CC7.3/CC7.4) | Vulnerability scans, misconfiguration/firmware-advisory tracking + remediation; SIEM logs, alert rules, triage records, incident tickets, periodic reviews |
| CC8 change management | Authorize, test, approve, implement, and review firewall changes | Change tickets, diffs, approvals, emergency changes, rollback evidence |
| CC9 risk mitigation | Mitigate business-disruption risk (CC9.1) and vendor/business-partner risk (CC9.2) affecting firewall controls | Vendor/partner reviews, DR/failover tests, risk treatment plans |
| Availability category (A1.1 capacity, A1.2 environmental/backup/recovery, A1.3 recovery testing) | Protect production availability with segmentation, DDoS/WAF paths, HA, backups, and DR | HA/failover evidence, backup/restore tests, monitoring alerts, capacity records |
| Confidentiality category | Restrict and monitor paths to confidential customer data | Segmentation rules, egress controls, encryption/VPN paths, data-flow diagrams |
| Privacy category support | Limit and monitor network access to personal information systems | Data-flow maps, access restrictions, logging, third-party access evidence |
