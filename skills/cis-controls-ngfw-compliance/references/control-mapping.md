# CIS Controls NGFW Compliance Research — Control Mapping

> Reference material for the `cis-controls-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

## CIS Control Mapping for NGFW Controls

Use this table as a first-pass mapping. Always verify exact safeguard wording against the current CIS Controls publication during formal work.

Representative safeguard IDs are shown for the most firewall-central controls; always
confirm exact safeguard numbering and wording against the licensed CIS Controls v8/v8.1
document before citing in formal deliverables.

| CIS area | What the NGFW/firewall estate can support | Evidence to request |
|---|---|---|
| Control 1: Inventory and Control of Enterprise Assets | Identify firewalls, VPN gateways, cloud firewalls, WAFs, IDS/IPS, SASE/ZTNA, and management systems | Network asset inventory, CMDB, cloud inventory, owner/platform/version list |
| Control 2: Inventory and Control of Software Assets | Track firewall OS, firmware, plugins, content/signature packages, and management software | Version inventory, license/content status, software approval records |
| Control 3: Data Protection | Restrict network paths to sensitive data systems and control exfiltration routes | Data-flow diagrams, egress policy, DLP/threat logs, segmentation rules |
| Control 4: Secure Configuration (e.g. Safeguards 4.2 secure process for network infrastructure, 4.4 firewall on servers, 4.5 host firewall) | Harden firewall baselines and disable unnecessary services | Baseline standards, config exports, management-service review, hardening checklist |
| Control 5: Account Management | Manage firewall admin accounts and remote-access identities | Admin user list, AAA/SSO integration, stale-account review, break-glass process |
| Control 6: Access Control Management | Enforce least privilege for user/admin/VPN/application access | RBAC, MFA, rule ownership, VPN groups, user-ID policy, access reviews |
| Control 7: Continuous Vulnerability Management | Patch firewall OS/content and scan exposed services | Firmware/advisory tracking, vulnerability scan results, remediation tickets |
| Control 8: Audit Log Management (e.g. Safeguards 8.1 log management process, 8.2 collect logs, 8.5 detailed logging, 8.9 centralize) | Generate and centralize firewall/VPN/admin/threat logs | Syslog/SIEM config, NTP, log retention, sample events, review workflow |
| Control 9: Email and Web Browser Protections | Support web filtering, DNS security, TLS policy, and risky-category blocking | URL/DNS security profiles, proxy paths, web filtering logs |
| Control 10: Malware Defenses | Block or detect malware callbacks and malicious content where NGFW features support it | Anti-malware/IPS/DNS signatures, update status, alert examples |
| Control 11: Data Recovery | Protect firewall configs and support recovery of network enforcement points | Config backups, restore tests, HA/failover evidence, backup access controls |
| Control 12: Network Infrastructure Management (e.g. Safeguards 12.2 secure architecture, 12.3 secure management, 12.8 dedicated admin resources) | Securely manage network infrastructure and architecture | Diagrams, secure protocols, admin ACLs, out-of-band/management network, config standards |
| Control 13: Network Monitoring and Defense (e.g. Safeguards 13.3 network IDS, 13.4 filter between segments, 13.6 flow logs, 13.8 network IPS) | Monitor traffic and security events at key boundaries | IDS/IPS placement, threat logs, deny/permit alerts, SIEM detections, packet capture process |
| Control 15: Service Provider Management | Control MSP/MSSP/vendor/cloud firewall access and responsibilities | Contracts, access lists, provider evidence, shared responsibility matrix |
| Control 16: Application Software Security | Support application segmentation and public-app protection; not a substitute for app security | WAF/WAAP placement, app-ID rules, API gateway/firewall evidence |
| Control 17: Incident Response Management | Provide firewall evidence for detection, containment, eradication, and lessons learned | IR runbooks, sample investigations, containment change tickets |
| Control 18: Penetration Testing | Validate firewall boundaries, segmentation, and exposed services | Pen test reports, segmentation test results, remediation evidence |
