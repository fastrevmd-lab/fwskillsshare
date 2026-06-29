# Skill Test: firewall-best-practices-audit v1.0 on vSRX-Production

- **Date:** 2026-06-29
- **Skill under test:** `firewall-best-practices-audit` v1.0 (30-check catalog)
- **Target:** `vSRX-Production`, Junos OS **25.4R1.12**, live device via `rust-junosmcp`
- **Flow:** raw config (MCP `get_junos_config`) → `parsing-srx-configs` → intermediate schema → `firewall-best-practices-audit`
- **Result:** **1 finding from 30 checks** — a deliberate stress test that exposed real coverage gaps. Secrets in the source config are redacted throughout.

## Why this device is a good stress test

The config is **control-plane hardened but policy-light**:

- **Zero `security policies`** — only `policies { policy-rematch; }`. No from-zone/to-zone or global policies.
- Full security stack configured but **attached to nothing**: AppID, IDP (auto security-package), SecIntel, Advanced Anti-Malware (AAMW), UTM custom objects, `dynamic-address`.
- 3 zones (`trust` = ge-0/0/1.0+ge-0/0/3.0, `untrust` = ge-0/0/0.0, `IoT` = ge-0/0/2.0).
- Source NAT for `trust → untrust` and `IoT → untrust` (both match `0.0.0.0/0`, translate to egress interface).
- Strong control-plane hardening the audit can't see: a `PROTECT-RE` stateless filter on `lo0.0`, `untrust-screen` IDS options, a security log **stream** to `192.168.1.150:514`, pinned NTP/DNS servers, SSH/NETCONF rate-limits, login retry/lockout + password policy, and SDcloud `outbound-ssh` phone-home.

Because SRX implicitly denies unmatched inter-zone traffic, "no policies" is not automatically wrong — but a production device with zones + NAT + a full inspection stack and **no policy to permit or inspect anything** is a loud signal the audit should surface. It largely didn't.

## What the audit produced

```text
[SEC-NO-DENY-ALL] MEDIUM (heuristic) — No explicit, logged inter-zone deny-all
Category: security / hygiene
Affected: security_policies = [] (only policy-rematch); security log stream SSDF configured but no policy logs to it
Why it matters: SRX implicitly denies unmatched inter-zone traffic, but that implicit drop is unlogged. With zero policies AND a configured syslog stream, denied traffic produces no security visibility.
Remediation: add an explicit terminal global deny with logging.
Fix (SRX):
  set security policies global policy 999-DENY-REST match from-zone any
  set security policies global policy 999-DENY-REST match to-zone any
  set security policies global policy 999-DENY-REST match source-address any
  set security policies global policy 999-DENY-REST match destination-address any
  set security policies global policy 999-DENY-REST match application any
  set security policies global policy 999-DENY-REST then deny
  set security policies global policy 999-DENY-REST then log session-init
```

```text
Posture: Audit largely inconclusive — the rulebase-centric checks have almost no input because this device defines no security policies. Not a clean bill of health; a coverage gap.
Findings: Critical 0  High 0  Medium 1  Low 0  Info 0
Checks skipped (no data): SEC-WEAK-IKE/IPSEC/PSK (no vpn_tunnels), OPS-ZERO-HIT (no hit counts), all policy-dependent SEC checks and all object/group OPS checks (no policies/objects parsed)
Top fixes:
  1. SEC-NO-DENY-ALL — add explicit logged deny-all (and the actual permit policies this device presumably needs)
```

The thinness **is** the finding: ~28 of 30 checks key off `security_policies[]` or address/service objects, both empty here.

## Shortcomings captured

| # | Shortcoming | Evidence on this device | Impact |
|---|-------------|-------------------------|--------|
| 1 | **Policy-centric blindness.** ~28/30 checks need `security_policies[]`/objects; 0 policies → near-empty audit instead of "security stack wired to nothing." | UTM/IDP/SecIntel/AAMW configured but no policy references them; NAT translates flows no policy permits | High |
| 2 | **No SSH root-login / auth-hardening checks.** | `system services ssh root-login allow`; `root-authentication` set; strong password-policy + lockout present but uncredited | High |
| 3 | **Stateless RE-protection filters not modeled.** Schema carries only stateful `security_policies`; `firewall { filter PROTECT-RE }` lands in `residual_raw`. | `PROTECT-RE` on `lo0.0` (a strong control) is invisible — neither credited nor required | High |
| 4 | **`host-inbound-traffic` under-audited** — the real "what can reach the box" surface on SRX; only the narrow SEC-MGMT-DATAZONE touches it. | untrust = ping-only (good), trust/IoT = dns+dhcp+ping — none assessed | Medium |
| 5 | **No checks for screens/IDS, security-log completeness, NTP/DNS pinning, phone-home.** | `untrust-screen`, `stream SSDF→192.168.1.150:514`, pinned NTP, SDcloud `outbound-ssh` — none audited | Medium |
| 6 | **No cross-object consistency** — can't see "NAT/zones/services exist but no policy uses them." | source-NAT for trust→untrust with no permitting policy | Medium |
| 7 | **Empty `security_policies` is silent, not warned** — can't distinguish default-deny-by-design from partial config / policies in a logical-system/tenant. | n/a — should emit a coverage warning | Medium |
| 8 | **No IPv6/dual-stack posture, no admin-user/AAA hardening checks.** | ge-0/0/0 has inet6; 4 login users + root | Low |

## Root cause

The skill — and the `parsing-*` intermediate schema it consumes — models a **stateful policy rulebase**. SRX security also lives in zones / `host-inbound-traffic`, stateless RE filters, screens, system & SSH services, and auth, none of which the schema fully carries, so the audit cannot see them. On a policy-heavy config the skill would shine; on this control-plane-hardened, policy-light box it is mostly blind.

## Follow-up

Tracked as a grouped priority effort in [`TODO.md`](../../TODO.md) →
**"PRIORITY PROJECT: firewall-best-practices-audit v1.1 — SRX coverage gaps"**
(schema/parser extensions + new v1.1 checks). Re-run this exact test (and a
policy-heavy device) after v1.1 to confirm the catalog exercises more than one
check.
