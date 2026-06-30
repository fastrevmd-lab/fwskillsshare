# PCI NGFW Compliance Research — Control Mapping

> Reference material for the `pci-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

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
| 8.2.1 Unique IDs | No shared admin accounts on the firewall or management system; every administrator has a unique, individual account | Admin account list showing no shared/generic accounts; per-admin account evidence |
| 8.2.4 Account lifecycle | Admin account additions, changes, and removals processed through formal change control | Change tickets for account provisioning/deprovisioning; account audit records |
| 8.2.5 Terminated users | Admin and VPN access revoked promptly on termination or role change | Offboarding checklist, account-deletion evidence tied to HR separation dates |
| 8.2.6 Inactive accounts | Admin accounts not used within 90 days disabled or removed | Account last-login report; evidence of 90-day inactive-account review |
| 8.2.7 Third-party/vendor remote access | Third-party and vendor remote access enabled only when needed, monitored during use, and disabled when complete | VPN/jump-host policies; session monitoring/recording evidence; access-enable/disable logs |
| 8.3.1 Authentication factors | Strong authentication credentials required for all firewall and manager administrative access | Authentication policy config; password/key complexity settings; AAA/RADIUS/TACACS+ config |
| 8.4.1 MFA — non-console admin | MFA required for all non-console administrative access to the firewall and CDE network security controls | MFA config on management platforms (Panorama, FortiManager, etc.); RADIUS/TACACS+ MFA integration evidence |
| 8.4.2 MFA — all CDE access | MFA required for all access into the CDE | CDE access path diagrams; MFA enforcement evidence for all CDE entry paths |
| 8.4.3 MFA — remote/VPN access | MFA required for all remote access originating from outside the entity's network into the CDE, including VPN | VPN gateway MFA config; authentication logs showing MFA enforcement for remote sessions |
| 8.5.1 MFA system protections | MFA implementation is not bypassable, is replay-resistant, and is protected against MFA fatigue/push-bombing attacks | MFA system config review; evidence of replay-resistance and anti-bypass controls |
| 10.2.x Audit logs | Logs enabled and capture required security events | Syslog/SIEM forwarding, log categories, sample events |
| 10.3.x Log protection | Logs protected from unauthorized modification and disclosure | SIEM RBAC, immutable storage, retention config |
| 10.4.x Daily review | Relevant security logs reviewed at least daily or via automated mechanisms | SIEM use cases, alert workflow, daily review evidence |
| 11.3.x Vulnerability scans | Internal/external scans run and findings remediated | ASV reports, internal scan results, remediation tickets |
| 11.4.x Pen testing | CDE perimeter and segmentation controls tested | Pen test methodology/results, segmentation test evidence |
| 11.5.1 IDS/IPS | Intrusion detection/prevention monitors CDE perimeter and critical points; signatures current | IPS profiles, update status, alert routing, incident examples |
| 12.3.3 Crypto inventory | Cipher suites/protocols documented and reviewed annually | Firewall VPN/admin/TLS inventory and review record |
| 12.10.5 Incident response | Alerts from security monitoring systems are included in IR plan | Firewall/IPS/WAF alert handling runbooks and escalation records |
