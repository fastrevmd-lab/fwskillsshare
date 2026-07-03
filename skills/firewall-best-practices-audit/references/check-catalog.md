# Firewall Best-Practices Audit — Check Catalog

> Reference material for the `firewall-best-practices-audit` skill; loaded on
> demand. Each entry: id, what it detects, the intermediate-schema fields it
> reads, default severity, and confidence notes.
>
> The per-check default severities listed here are the **authoritative** defaults;
> the SKILL.md "Severity & Confidence" table shows the general scale with
> context-adjusted examples. Where they appear to differ, this catalog wins.

Schema field names use the vendor-neutral intermediate schema (canonical reference:
the copy documented in the `parsing-srx-configs` skill). The brief used
shorthand aliases (e.g. `rules[]`, `objects`, `vpn.ike`) which are mapped here to
their real top-level keys: `security_policies[]`, `address_objects` / `service_objects`,
`vpn_tunnels[].ike`, etc.

---

## Security Checks

- SEC-ANY-ANY — permit rule with any source AND any destination AND any service — `security_policies[].{src_addresses, dst_addresses, services, applications, action}` — CRITICAL (HIGH if logged) — definitive

- SEC-ANY-SVC — permit rule with any/any-service but specific src+dst — `security_policies[].{services, applications, action}` — MEDIUM — definitive

- SEC-BROAD-SRC — permit with overly broad source (0.0.0.0/0 or very large supernet) — `security_policies[].src_addresses, address_objects` — HIGH — definitive

- SEC-BROAD-DST — permit with overly broad destination — `security_policies[].dst_addresses, address_objects` — MEDIUM — definitive

- SEC-LARGE-PORTRANGE — service spanning a very large port range — `service_objects` — LOW — definitive

- SEC-SHADOW — rule fully shadowed by an earlier broader rule — `security_policies[]` ordered by `_rule_index`, resolved `address_objects`, `address_groups` — HIGH — heuristic (needs full order + resolution)

- SEC-REDUNDANT — duplicate rule (same match + action as another) — `security_policies[]` — LOW — definitive

- SEC-OVERLAP — overlapping rules with differing actions (ordering risk) — `security_policies[]` ordered by `_rule_index` — MEDIUM — heuristic

- SEC-ORPHAN-REF — rule references a missing/undefined object — `security_policies[]` vs `address_objects`, `service_objects`, `applications` — MEDIUM — definitive

- SEC-DISABLED — disabled-but-present rule (cleanup) — `security_policies[].disabled` — INFO — definitive

- SEC-NO-DENY-ALL — no explicit logged deny-all at the tail of the policy set; on SRX the implicit-deny already enforces block, but an explicit logged deny-all is recommended for visibility — `security_policies[]` tail (`_rule_index`), `metadata.source_vendor` — MEDIUM — heuristic

- SEC-NO-LOG — permit rule without logging — `security_policies[].log_end`, `security_policies[].log_start` — LOW (MEDIUM if broad) — definitive

- SEC-NO-DESC — rule missing description/owner — `security_policies[].description` — INFO — definitive

- SEC-EXPOSED-MGMT — device management service reachable from untrusted/any — `security_policies[]`, `zones`, `service_objects` — HIGH — definitive

- SEC-EXPOSED-RISKY — risky services (RDP/SMB/DB/telnet) reachable from untrusted/any — `security_policies[]`, `service_objects`, `zones` — HIGH — definitive

- SEC-INBOUND-ANY — inbound any-from-internet permit — `security_policies[]`, `zones` — HIGH — definitive

- SEC-PLAINTEXT-MGMT — plaintext management enabled (telnet or http are definitively detectable from `system.mgmt_services` and `zones[].host_inbound`; SNMPv1/v2c version detection is data-dependent — the schema carries only a boolean `snmp` with no version field, so flag/skip SNMP-version checks per the skill's graceful-degradation rule) — `system.mgmt_services`, `zones[].host_inbound` — HIGH — definitive

- SEC-MGMT-DATAZONE — management services exposed to data/untrusted zones — `zones[].host_inbound` — MEDIUM — definitive

- SEC-WEAK-IKE — weak IKE — DH-group (<14), encryption (3DES/DES), and authentication/integrity (MD5/SHA-1) weakness are definitively detectable from the crypto fields. IKEv1 aggressive-mode detection is data-dependent: the canonical schema carries `ike.version` but has no IKE mode/aggressive field, so skip aggressive-mode detection unless the parser captured it elsewhere (e.g. in residual/raw) — `vpn_tunnels[].ike` (`ike.proposal.dh_group`, `ike.proposal.encryption`, `ike.proposal.integrity`, `ike.version`) — HIGH — definitive

- SEC-WEAK-IPSEC — weak IPsec (no PFS, weak ESP enc/auth) — `vpn_tunnels[].ipsec` (`ipsec.proposal.dh_group`, `ipsec.proposal.encryption`, `ipsec.proposal.integrity`) — MEDIUM — definitive

- SEC-PSK-WEAK — reused/weak PSK indicators where visible — `vpn_tunnels[].ike.psk` — MEDIUM — heuristic

- SEC-SSH-ROOT-LOGIN — SSH permits root login or uses weak ciphers / no rate-limit — `system.ssh` (`root_login`, `ciphers`, `rate_limit`) — HIGH — definitive

- SEC-SERVICES-UNREFERENCED — a configured security service is attached to no policy (inert security stack) — `security_services` vs `security_policies[].security_profiles` — HIGH — heuristic (depends on profile capture)

- SEC-ZONES-NAT-NO-POLICY — zones/NAT exist but no security_policies reference them — `zones`, `nat_rules`, `security_policies` — HIGH — heuristic

- SEC-EMPTY-POLICYSET — security_policies is empty: emit a coverage warning rather than staying silent; distinguish default-deny-by-design from partial config / logical-system / tenant — `security_policies`, `_logical_system`/`_tenant` markers — MEDIUM — definitive

- SEC-HOST-INBOUND-EXPOSURE — management/sensitive host-inbound services on an untrusted/data zone — `zones[].host_inbound.system_services` — MEDIUM — heuristic

- SEC-NO-SCREEN — an external/untrust zone has no screen bound (binding absence is definitive; classifying a zone as external is heuristic — key off zone name and the default-route-facing interface) — `zones[].screen`, `zones[].interfaces`, `static_routes` — MEDIUM — heuristic

- SEC-AUTH-HARDENING — missing/weak password policy or login lockout — `system.auth` (`password_policy`, `login_lockout`) — MEDIUM — definitive

- SEC-IPV6-POSTURE — interfaces have inet6 addresses but no corresponding v6 controls/policies — `interfaces[].ipv6`, `security_policies` — LOW — heuristic
- SEC-NO-CONTROL-PLANE-PROTECTION — no stateless control-plane / RE-protection filter applied (SRX lo0 input filter; Cisco CoPP; Palo/FortiGate mgmt profile) on a device with an untrusted-facing interface — `system.control_plane_protection` (`re_filter_present`, `applied_to`), `zones`/`interfaces` — MEDIUM — heuristic

---

## Operational Checks

- OPS-UNUSED-OBJ — address/service object defined but unreferenced — `address_objects`, `service_objects` vs `security_policies[]`, `nat_rules`, `address_groups`, `service_groups` — LOW — heuristic (needs complete ref capture)

- OPS-DUP-OBJ — duplicate objects (same value, different name) — `address_objects`, `service_objects` — LOW — definitive

- OPS-LARGE-GROUP — oversized group (member count over threshold) — `address_groups`, `service_groups`, `application_groups` — INFO — definitive

- OPS-NESTED-GROUP — deeply nested group (depth over threshold) — `address_groups`, `service_groups`, `application_groups` — INFO — definitive

- OPS-NO-DESC-OBJ — object/group missing description — `address_objects[].description`, `address_groups[].description`, `service_objects[].description` — INFO — definitive

- OPS-NAMING — non-standard / inconsistent naming — `address_objects[].name`, `service_objects[].name`, `security_policies[].name` — INFO — heuristic

- OPS-CONSOLIDATE — rules consolidatable (same action, contiguous, differ only by one field) — `security_policies[]` — LOW — heuristic

- OPS-REDUNDANT-OBJ — redundant objects (subset/superset duplicates) — `address_objects`, `service_objects` — LOW — heuristic

- OPS-ZERO-HIT — zero-hit rule (only when usage/hit-count data is present) — `security_policies[].hit_count` (NOT part of the base intermediate schema — it requires external hit-count telemetry, so this check is data-dependent and is skipped unless that data is supplied) — LOW — definitive (skip if no data)

- OPS-LOG-COMPLETENESS — no remote security-log stream/host target configured — top-level `syslog_config[]` (SRX `security log stream`/host may land in `residual_raw`; skip if neither is captured) — MEDIUM — definitive

---

## Thresholds

Default tunable thresholds referenced by checks above:

| Threshold | Default |
|-----------|---------|
| Broad source (SEC-BROAD-SRC) | Prefix length ≤ /8, or 0.0.0.0/0 |
| Large port range (SEC-LARGE-PORTRANGE) | Span ≥ 1024 ports |
| Large group (OPS-LARGE-GROUP) | Member count ≥ 50 |
| Nesting depth (OPS-NESTED-GROUP) | Depth ≥ 3 levels |

These values can be overridden per engagement in the audit invocation context.
