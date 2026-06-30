# CMMC / NIST 800-171 NGFW Compliance Research — Control Mapping

> Reference material for the `cmmc-nist-800-171-ngfw-compliance` skill, moved out of SKILL.md for token-efficient progressive disclosure. Load this when building the firewall-to-requirement matrix.

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
| 3.13.6 Deny by default | Deny network traffic by default; allow only by explicit exception | Final deny rules, implicit-deny documentation, deny logs |
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
| 3.13.11 FIPS-validated cryptography | When the firewall uses cryptography (VPN/TLS/IPsec) to protect CUI confidentiality, it must be FIPS-validated | FIPS mode enabled, validated module/cert, approved cipher/algorithm config |
| 3.13.13 Mobile code | Control/monitor risky mobile code and content paths | Egress filtering, URL/app controls, sandbox/threat-prevention profiles |
| 3.13.16 CUI at rest | Confidentiality of stored CUI; the firewall provides only indirect support (segmentation/access restriction), not storage encryption | Indirect: CUI-enclave segmentation + access-restriction evidence |
| 3.14.3 Security alerts/advisories | Use firewall/IPS/vendor alerts in vulnerability response | Firmware/advisory tracking, signature updates, emergency changes |
| 3.14.6 Monitor communications | Monitor inbound/outbound traffic for attacks and indicators | IDS/IPS/threat logs, SIEM alerts, detection tuning |
| 3.14.7 Identify unauthorized use | Detect unauthorized access or anomalous CUI network use | Deny events, impossible travel/VPN anomalies, egress anomalies |
