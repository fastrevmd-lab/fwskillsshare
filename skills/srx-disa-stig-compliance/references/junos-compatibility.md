# Junos Compatibility and Source Conflicts

## Interpretation rule

Formal STIG status follows the pinned artifact. Current Junos compatibility is a
separate field. A stronger modern recommendation does not silently change the
formal requirement, and a contradictory legacy example is never copied directly
to a device. Entries below remain `verification_required` until target model,
release, FIPS mode, licenses, and current primary Juniper documentation are
checked.

## Known Y25M01 conflicts

| Rule | Conflict | Handling |
|---|---|---|
| JUSX-IP-000027 | The title requires real-time monitoring of externally sourced files, but the check marks the presence of its matching custom dynamic attack group as a finding. | Keep Not Reviewed until assessor interpretation; do not silently choose either predicate. |
| JUSX-VN-000002 | The rule treats an absent IPsec lifetime as a finding while its check and current default discussion identify 3600 seconds, within the stated limit. | Preserve formal result; verify effective and explicit lifetime on target. |
| JUSX-VN-000003 | Title/fix, check language, idle-time wording, and default duration use inconsistent thresholds. | Do not auto-evaluate or remediate; obtain assessor interpretation. |
| JUSX-VN-000005 | An IPsec proposal requirement directs the reviewer to inspect IKE proposals. | Verify both hierarchies; report the source mismatch. |
| JUSX-VN-000023 | CSfC example hierarchy is incomplete or malformed and cannot establish an approved capability package. | Require manual CSfC/approval evidence and current target validation. |
| JUSX-VN-000025 | The artifact permits SHA-1-or-better while current Junos deprecates SHA-1 families on newer releases. | Preserve formal result; recommend SHA-256+ only as separate current-vendor guidance. |
| JUSX-VN-000026 | A DoD PKI authentication check refers to AES, an encryption algorithm. | Require PKI/authentication evidence and assessor interpretation. |
| JUSX-VN-000027 | An authorized-flow check diverts into outbound DoS-screen validation. | Assess authorized flows and screen posture separately; do not infer equivalence. |
| JUSX-VN-000028 | The fix uses legacy `security dynamic-vpn` guidance. | Verify current remote-access architecture and Juniper Secure Connect migration guidance. |
| JUSX-DM-000136 | The artifact expects an explicit SHA-256-or-later password hash setting while current Junos documentation describes a stronger default on supported releases. | Report explicit versus effective behavior separately. |
| JUSX-DM-000146 | The artifact requires SNMPv3 SHA-256, but Juniper documents `authentication-sha256` support beginning in 21.1R1, later than the checklist's old minimum target. | Verify platform/release support; do not emit unsupported syntax. |

## Current primary Juniper references

- IDP package/runtime evidence:
  https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-basic-configuration.html
- Dynamic VPN to Juniper Secure Connect migration:
  https://www.juniper.net/documentation/us/en/software/secure-connect/secure-connect-administrator-guide/
- Junos 25.2 SRX cryptographic deprecations:
  https://www.juniper.net/documentation/us/en/software/junos/release-notes/25.2/junos-release-notes-25.2r1/topics/what-changed/srx-what-change-cover.html
- SNMP `authentication-sha256` release support:
  https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/authentication-sha256-edit-snmp.html
- System login password hashing behavior:
  https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/password-edit-system-login.html
- SSH configuration and release-sensitive algorithms:
  https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/ssh-edit-system.html

## Remediation gate

No entry above authorizes an automatic fix. For any `verification_required`
rule, state the formal result first, identify the compatibility question, verify
the exact target using current primary Juniper evidence, then prepare a dry-run
plan through the relevant SRX skill. Device configuration still requires explicit
approval, rollback protection, and post-change verification.
