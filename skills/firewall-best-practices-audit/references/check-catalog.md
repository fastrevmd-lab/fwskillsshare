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

## Policy population contract

Before applying any entry that reads `security_policies`, partition the parser
output by marker, never by rule name:

- `explicit_rules` = rules whose `_implicit` value is not `true`;
- `enabled_explicit_rules` = enabled members of `explicit_rules`;
- `disabled_explicit_rules` = disabled members of `explicit_rules`; and
- `implicit_rules` = rules marked `_implicit: true`.

Active-risk, order, logging, exposure, shadow, redundancy, and overlap checks
use `enabled_explicit_rules`. Cleanup/state checks use `explicit_rules` or
`disabled_explicit_rules` as their entries specify. Reference and object-usage
checks exclude `implicit_rules` and must state whether disabled explicit rules
count as references. No check emits a finding against an implicit rule or
compares it with an explicit rule. `implicit_rules` are consulted only to
describe effective enforcement where a vendor default applies; they never
provide explicit logging or satisfy an explicit-rule requirement.

### Vendor evaluation population and phase

For comparison checks, partition `enabled_explicit_rules` into a vendor
evaluation population before sorting by numeric `_rule_index`:

- SRX uses root/`_logical_system`/`_tenant`, then a separate population for each
  concrete zone pair; global `any`→`any` policy is a distinct later phase.
- PAN-OS uses `_vsys` and the parser's complete merged Panorama/local order;
  source/destination zones are match fields, not separate rulebases.
- FortiGate uses `_vdom`; zones remain match fields in the VDOM rulebase.
- Cisco ASA may use a concrete parser-derived inbound binding/source zone. The
  schema has no ACL name/direction field, so do not flatten ambiguous bindings.

Never compare rules from different populations or flatten SRX zone-pair and
global phases. If vendor context, binding, complete merged-order provenance,
unique `_rule_index`, or required object resolution is unavailable, skip or
downgrade the affected check and record an **evidence-gap warning**. The shared
schema has no generic phase/origin field, so do not invent one.

---

## Security Checks

- SEC-ANY-ANY — enabled explicit permit rule with any source AND any destination AND any service — `enabled_explicit_rules[].{src_addresses, dst_addresses, services, applications, action}` — CRITICAL (HIGH if logged) — definitive

- SEC-ANY-SVC — enabled explicit permit rule with any/any-service but specific src+dst — `enabled_explicit_rules[].{services, applications, action}` — MEDIUM — definitive

- SEC-BROAD-SRC — enabled explicit permit with overly broad source (0.0.0.0/0 or very large supernet) — `enabled_explicit_rules[].src_addresses, address_objects` — HIGH — definitive

- SEC-BROAD-DST — enabled explicit permit with overly broad destination — `enabled_explicit_rules[].dst_addresses, address_objects` — MEDIUM — definitive

- SEC-LARGE-PORTRANGE — service spanning a very large port range — `service_objects` — LOW — definitive

- SEC-SHADOW — enabled explicit rule fully shadowed by an earlier broader enabled explicit rule in the same vendor evaluation population — `enabled_explicit_rules` ordered by `_rule_index`, resolved `address_objects`, `address_groups` — HIGH — heuristic (needs full order + resolution)

- SEC-REDUNDANT — duplicate enabled explicit rule (same match + action as another) in the same vendor evaluation population — `enabled_explicit_rules` — LOW — definitive only with complete population/context evidence; otherwise heuristic or skipped

- SEC-OVERLAP — overlapping enabled explicit rules with differing actions (ordering risk) in the same vendor evaluation population — `enabled_explicit_rules` ordered by `_rule_index` — MEDIUM — heuristic

- SEC-ORPHAN-REF — explicit rule (enabled or disabled) references a missing/undefined object — `explicit_rules` vs `address_objects`, `service_objects`, `applications` — MEDIUM — definitive

- SEC-DISABLED — disabled-but-present explicit rule (cleanup) — `disabled_explicit_rules` — INFO — definitive

- SEC-NO-DENY-ALL — no reachable explicit logged match-all action of `deny` or `drop` at the `_rule_index` tail of each applicable enabled explicit policy context or reachable SRX global fallback; `reset-both` is not a deny alias, and an implicit vendor default can provide effective enforcement but never explicit log visibility — `enabled_explicit_rules`, `implicit_rules`, `metadata.source_vendor` — MEDIUM — heuristic

- SEC-NO-LOG — enabled explicit permit rule without logging — `enabled_explicit_rules[].log_end`, `enabled_explicit_rules[].log_start` — LOW (MEDIUM if broad) — definitive

- SEC-NO-DESC — explicit rule (enabled or disabled) missing description/owner — `explicit_rules[].description` — INFO — definitive

- SEC-EXPOSED-MGMT — device management service reachable through an enabled explicit rule from untrusted/any — `enabled_explicit_rules`, `zones`, `service_objects` — HIGH — definitive

- SEC-EXPOSED-RISKY — risky services (RDP/SMB/DB/telnet) reachable through an enabled explicit rule from untrusted/any — `enabled_explicit_rules`, `service_objects`, `zones` — HIGH — definitive

- SEC-INBOUND-ANY — enabled explicit inbound any-from-internet permit — `enabled_explicit_rules`, `zones` — HIGH — definitive

- SEC-PLAINTEXT-MGMT — plaintext management enabled (telnet or http are definitively detectable from `system.mgmt_services` and `zones[].host_inbound`; SNMPv1/v2c version detection is data-dependent — the schema carries only a boolean `snmp` with no version field, so flag/skip SNMP-version checks per the skill's graceful-degradation rule) — `system.mgmt_services`, `zones[].host_inbound` — HIGH — definitive

- SEC-MGMT-DATAZONE — management services exposed to data/untrusted zones — `zones[].host_inbound` — MEDIUM — definitive

- SEC-WEAK-IKE — weak IKE — DH-group (<14), encryption (3DES/DES), and authentication/integrity (MD5/SHA-1) weakness are definitively detectable from the crypto fields. IKEv1 aggressive-mode detection is data-dependent: the canonical schema carries `ike.version` but has no IKE mode/aggressive field, so skip aggressive-mode detection unless the parser captured it elsewhere (e.g. in residual/raw) — `vpn_tunnels[].ike` (`ike.proposal.dh_group`, `ike.proposal.encryption`, `ike.proposal.integrity`, `ike.version`) — HIGH — definitive

- SEC-WEAK-IPSEC — weak IPsec (no PFS, weak ESP enc/auth) — `vpn_tunnels[].ipsec` (`ipsec.proposal.dh_group`, `ipsec.proposal.encryption`, `ipsec.proposal.integrity`) — MEDIUM — definitive

- SEC-PSK-WEAK — reused/weak PSK indicators where visible — `vpn_tunnels[].ike.psk` — MEDIUM — heuristic

- SEC-SSH-ROOT-LOGIN — SSH permits root login or uses weak ciphers / no rate-limit — `system.ssh` (`root_login`, `ciphers`, `rate_limit`) — HIGH — definitive

- SEC-SERVICES-UNREFERENCED — a configured security service is attached to no enabled explicit policy (inert security stack) — `security_services` vs `enabled_explicit_rules[].security_profiles` — HIGH — heuristic (depends on profile capture)

- SEC-ZONES-NAT-NO-POLICY — a NAT flow has no enabled explicit `action: allow` capable of carrying it in the same vendor context, proven by source/destination zone overlap and resolved source/destination address overlap; deny-only, disabled, unrelated-zone, or textual-reference-only policy does not count — `zones`, `nat_rules`, `enabled_explicit_rules` — HIGH — heuristic (unresolved objects require an evidence-gap warning and skip/downgrade)

- SEC-EMPTY-POLICYSET — `explicit_rules` is empty after excluding `_implicit: true`: emit a coverage warning rather than staying silent; distinguish default-deny-by-design from partial config / logical-system / tenant — `explicit_rules`, `implicit_rules`, `_logical_system`/`_tenant` markers — MEDIUM — definitive

- SEC-HOST-INBOUND-EXPOSURE — management/sensitive host-inbound services on an untrusted/data zone — `zones[].host_inbound.system_services` — MEDIUM — heuristic

- SEC-NO-SCREEN — an external/untrust zone has no screen bound (binding absence is definitive; classifying a zone as external is heuristic — key off zone name and the default-route-facing interface) — `zones[].screen`, `zones[].interfaces`, `static_routes` — MEDIUM — heuristic

- SEC-AUTH-HARDENING — missing/weak password policy or login lockout — `system.auth` (`password_policy`, `login_lockout`) — MEDIUM — definitive

- SEC-IPV6-POSTURE — interfaces have inet6 addresses but no corresponding enabled explicit v6 controls/policies — `interfaces[].ipv6`, `enabled_explicit_rules` — LOW — heuristic
- SEC-NO-CONTROL-PLANE-PROTECTION — no stateless control-plane / RE-protection filter applied (SRX lo0 input filter; Cisco CoPP; Palo/FortiGate mgmt profile) on a device with an untrusted-facing interface — `system.control_plane_protection` (`re_filter_present`, `applied_to`), `zones`/`interfaces` — MEDIUM — heuristic

---

## Operational Checks

- OPS-UNUSED-OBJ — address/service object defined but unreferenced by any explicit rule (enabled or disabled), NAT rule, or group — `address_objects`, `service_objects` vs `explicit_rules`, `nat_rules`, `address_groups`, `service_groups` — LOW — heuristic (needs complete ref capture)

- OPS-DUP-OBJ — duplicate objects (same value, different name) — `address_objects`, `service_objects` — LOW — definitive

- OPS-LARGE-GROUP — oversized group (member count over threshold) — `address_groups`, `service_groups`, `application_groups` — INFO — definitive

- OPS-NESTED-GROUP — deeply nested group (depth over threshold) — `address_groups`, `service_groups`, `application_groups` — INFO — definitive

- OPS-NO-DESC-OBJ — object/group missing description — `address_objects[].description`, `address_groups[].description`, `service_objects[].description` — INFO — definitive

- OPS-NAMING — non-standard / inconsistent naming — `address_objects[].name`, `service_objects[].name`, `explicit_rules[].name` — INFO — heuristic

- OPS-CONSOLIDATE — enabled explicit rules in the same vendor evaluation population are consolidatable (same action, contiguous by `_rule_index`, differ only by one field) — `enabled_explicit_rules` — LOW — heuristic

- OPS-REDUNDANT-OBJ — redundant objects (subset/superset duplicates) — `address_objects`, `service_objects` — LOW — heuristic

- OPS-ZERO-HIT — zero-hit enabled explicit rule (only when usage/hit-count data is present) — `enabled_explicit_rules[].hit_count` (NOT part of the base intermediate schema — it requires external hit-count telemetry, so this check is data-dependent and is skipped unless that data is supplied) — LOW — definitive (skip if no data)

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
