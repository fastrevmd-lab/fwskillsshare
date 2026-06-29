# SOC 2 NGFW Compliance Research — Control Mapping

> Reference material for the `soc2-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

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
