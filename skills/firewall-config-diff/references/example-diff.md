# Worked Examples: Firewall Config Diff

Three worked diffs produced by the `firewall-config-diff` skill, each emitting the exact
**Output & Verdict** template from `SKILL.md` and applying the pairing/classification rules
in `references/equivalence-rules.md`. Every comparison is **semantic** (by meaning, not text):
items pair by value / member-set / match-and-action tuple, never by name or position.

The diff markers are fixed:

- `+ [B]` — added (present only in B)
- `- [A]` — removed (present only in A)
- `~ [A→B]` — changed (same semantic identity, ≥1 differing attribute)

Each scenario ends with a single `Parity verdict:` line. Secrets (PSK / certs / passwords)
are never printed — only a presence/changed flag.

- **Scenario 1** — same-vendor **drift** (Cisco ASA baseline vs a modified copy).
- **Scenario 2** — cross-vendor **parity** (ASA-shaped vs SRX-shaped, semantically equal on
  comparable sections; VPN + threat profiles `not-comparable`).
- **Scenario 3** — **round-trip** conversion self-test (Cisco schema A vs the schema from
  re-parsing the SRX that the `firewall-config-conversion` skill emits for that fixture).

---

## Scenario 1 — Same-vendor drift (Cisco ASA → Cisco ASA)

**Source for A:** the real parsed Cisco fixture (`parsing-cisco-configs`
`references/fixture-expected-output.json`, `metadata.vendor: cisco-asa`). It contains exactly:
zones `outside` / `inside`; interfaces `GigabitEthernet0/0` (203.0.113.2/24) /
`GigabitEthernet0/1` (10.0.0.1/24); address objects `WEB` (10.0.1.10/32) and `INSIDE-NET`
(10.0.0.0/16); service object `HTTPS-ALT` (tcp/8443); security policy `OUTSIDE-IN-1`
(any → WEB, tcp/443, allow, log at session-end); source NAT `INSIDE-NET-auto-nat`
(inside → outside, INSIDE-NET behind egress interface); one default static route.

**B is that exact fixture with three clearly-labeled edits — nothing else changes:**

1. **Add one permit policy** `INSIDE-WEB-1`: inside → outside, src `INSIDE-NET`, dst `any`,
   service `HTTPS-ALT` (tcp/8443, the previously-unreferenced fixture service object), allow.
2. **Change one address object value:** `WEB` 10.0.1.10/32 → 10.0.1.20/32.
3. **Toggle logging on `OUTSIDE-IN-1`:** `log_end` true → false.

This is a drift framing (A = baseline, B = current). Because both sides are the same vendor
and the object names are stable, pairs are anchored by their stable identity and an attribute
delta is reported as `~ changed` (vs cross-vendor, where addresses pair strictly by value).

```text
Section: address_objects     unchanged 1  added 0  removed 0  changed 1
  ~ [A→B] WEB: value 10.0.1.10/32 → 10.0.1.20/32
    (INSIDE-NET 10.0.0.0/16 unchanged; the WEB value shift propagates to every policy that
     references WEB — see OUTSIDE-IN-1 effective destination below)
Section: service_objects     unchanged 1  added 0  removed 0  changed 0
    (HTTPS-ALT tcp/8443 unchanged — it is now referenced by the new policy, but the object
     definition itself did not change)
Section: security_policies   unchanged 0  added 1  removed 0  changed 1  | order: 0 reordered
  + [B] INSIDE-WEB-1: inside → outside, INSIDE-NET → any, tcp/8443 (HTTPS-ALT), allow
  ~ [A→B] OUTSIDE-IN-1 (any → WEB, tcp/443, allow): log_end true → false
    (effective destination also moved with WEB: 10.0.1.10/32 → 10.0.1.20/32)
Section: nat_rules           unchanged 1  added 0  removed 0  changed 0
Section: zones               unchanged 2  added 0  removed 0  changed 0
Section: interfaces          unchanged 2  added 0  removed 0  changed 0
Section: static_routes       unchanged 1  added 0  removed 0  changed 0
Not comparable: none (same vendor — all sections isomorphic)

Parity verdict: DIFFERENCES FOUND (3)  (A=cisco-asa, B=cisco-asa)
```

The verdict count is 3: one added policy, one changed address object, one changed policy
(logging). Rule order did not change (the new policy appended), so no reorder is reported.

---

## Scenario 2 — Cross-vendor parity (Cisco ASA-shaped vs Juniper SRX-shaped)

Two **different-vendor** sides describing the same intent. Per `equivalence-rules.md`, the
constructs the vendors model differently are normalized to a common form *before* pairing,
and features with no equivalent on the other side are flagged `not-comparable` — never a
false diff.

**A — ASA-shaped snippet:**

```text
object network web-srv
 host 10.0.1.10
access-list OUTSIDE_in extended permit tcp any object web-srv eq https
access-group OUTSIDE_in in interface outside
crypto map OUT_MAP 10 match address VPN_TRAFFIC
crypto map OUT_MAP 10 set peer 198.51.100.7
crypto map OUT_MAP 10 set ikev2 ipsec-proposal AES256-SHA
! pre-shared-key <redacted>            (secret never compared by value)
! classic ASA has no NGFW / UTM profile object
```

**B — SRX-shaped snippet:**

```text
set security address-book global address host-A 10.0.1.10/32
set security policies global policy ALLOW-WEB match source-address any
set security policies global policy ALLOW-WEB match destination-address host-A
set security policies global policy ALLOW-WEB match application junos-https
set security policies global policy ALLOW-WEB then permit
set security policies global policy ALLOW-WEB then permit application-services security-intelligence-policy SECINTEL
set security ipsec vpn VPN-SITEB bind-interface st0.0
set security ipsec vpn VPN-SITEB ike gateway GW-SITEB address 198.51.100.7
set security ipsec vpn VPN-SITEB ike gateway GW-SITEB ike-policy IKE-POL
# pre-shared-key <redacted>            (secret never compared by value)
```

**Normalization applied before pairing:**

- `web-srv host 10.0.1.10` (A) and `host-A 10.0.1.10/32` (B) carry the **same value**
  10.0.1.10/32 — different names, equal object.
- ASA `eq https` (tcp/443) and SRX `junos-https` both normalize to canonical app `https` —
  equal, not a diff.
- ASA `nameif outside` and the SRX `from-zone/to-zone` derive to the same pseudo-zone pairing
  for the comparable policy; the ASA `security-level` trust ordering itself is
  `not-comparable`.

```text
Section: address_objects     unchanged 1  added 0  removed 0  changed 0
    (10.0.1.10/32 present on both — paired by value, not name)
Section: security_policies   unchanged 1  added 0  removed 0  changed 0
    (any → 10.0.1.10/32, https, allow — identical tuple after app + zone normalization)
Section: vpn_tunnels         not-comparable
    (peer 198.51.100.7 + AES256/SHA proposal fields are normalizable, but the tunnel MODEL
     differs: ASA policy-based crypto-map vs SRX route-based st0 / proxy-id; secret compared
     by presence only, never value)
Section: security_services   not-comparable
    (SRX `permit application-services` SecIntel/IDP/AppFW has no classic-ASA equivalent —
     coarse "threat inspection attached?" boolean only; A=none, B=present)
Not comparable: vpn_tunnels (crypto-map vs route-based st0 model), security_services
  (SRX application-services vs ASA: no UTM on classic ASA), physical interface names,
  ASA security-level trust ordering

Parity verdict: EQUIVALENT  (A=cisco-asa, B=srx)
```

The comparable sections are equivalent; the non-isomorphic VPN and threat-profile features
are excluded from add/removed/changed rather than reported as false differences.

---

## Scenario 3 — Round-trip conversion self-test (Cisco schema A vs re-parsed SRX schema B)

This measures **conversion fidelity**. A is the original Cisco fixture schema. B is produced
by taking the SRX `set` config that the `firewall-config-conversion` skill emits for that same
fixture, then re-parsing it with `parsing-srx-configs` back into the intermediate schema. If
the conversion were lossless, A and B would be `EQUIVALENT` on every comparable section. The
diff surfaces exactly where fidelity is lost. (Per `SKILL.md`, this example stays
self-contained — the conversion skill is named, never path-referenced.)

**A — original Cisco fixture (schema, abridged):**

```json
{
  "address_objects": [
    {"name": "WEB", "type": "host", "value": "10.0.1.10/32"},
    {"name": "INSIDE-NET", "type": "subnet", "value": "10.0.0.0/16"}
  ],
  "service_objects": [
    {"name": "HTTPS-ALT", "protocol": "tcp", "port_range": "8443"}
  ],
  "security_policies": [
    {"name": "OUTSIDE-IN-1", "src_zones": ["outside"], "dst_zones": ["outside"],
     "src_addresses": ["any"], "dst_addresses": ["WEB"], "services": ["tcp/443"],
     "action": "allow", "log_end": true}
  ],
  "interfaces": [
    {"name": "GigabitEthernet0/0", "zone": "outside", "ip": "203.0.113.2/24"},
    {"name": "GigabitEthernet0/1", "zone": "inside",  "ip": "10.0.0.1/24"}
  ]
}
```

**B — schema from re-parsing the emitted SRX (abridged):** the conversion emits
`set security address-book global address WEB 10.0.1.10/32`, the policy as
`junos-https` with `then log session-close`, `HTTPS-ALT` as a **custom application**
(not a service object), and interfaces remapped to `ge-0/0/0` / `ge-0/0/1`. Re-parsed:

```json
{
  "address_objects": [
    {"name": "WEB", "type": "host", "value": "10.0.1.10/32"},
    {"name": "INSIDE-NET", "type": "subnet", "value": "10.0.0.0/16"}
  ],
  "service_objects": [],
  "applications": [
    {"name": "HTTPS-ALT", "protocol": "tcp", "port_range": "8443"}
  ],
  "security_policies": [
    {"name": "010-OUTSIDE-IN-1", "src_zones": ["outside"], "dst_zones": ["outside"],
     "src_addresses": ["any"], "dst_addresses": ["WEB"], "applications": ["https"],
     "action": "permit", "log_end": true}
  ],
  "interfaces": [
    {"name": "ge-0/0/0.0", "zone": "outside", "ip": "203.0.113.2/24"},
    {"name": "ge-0/0/1.0", "zone": "inside",  "ip": "10.0.0.1/24"}
  ]
}
```

**Pairing notes (semantic):** addresses pair by value (both 10.0.1.10/32, 10.0.0.0/16);
the policy tuple matches after normalization — `junos-https` == canonical `https` == ASA
tcp/443, `permit` == `allow`, `log session-close` == `log_end: true`, and the rename
`OUTSIDE-IN-1` → `010-OUTSIDE-IN-1` is **not** a diff (name-insensitive); interfaces pair by
**address**, since physical names are `not-comparable`.

```text
Section: address_objects     unchanged 2  added 0  removed 0  changed 0
    (WEB 10.0.1.10/32, INSIDE-NET 10.0.0.0/16 — clean round-trip by value)
Section: security_policies   unchanged 1  added 0  removed 0  changed 0  | order: 0 reordered
    (tuple any → WEB/https/allow/log preserved; junos-https↔tcp/443, permit↔allow,
     log session-close↔log_end all normalize equal; numeric-prefix rename is not a diff)
Section: nat_rules           unchanged 1  added 0  removed 0  changed 0
Section: static_routes       unchanged 1  added 0  removed 0  changed 0
Section: zones               unchanged 2  added 0  removed 0  changed 0
    (zone names outside/inside preserved by the conversion — isomorphic)
Section: service_objects     unchanged 0  added 0  removed 1  changed 0
  - [A] HTTPS-ALT tcp/8443: ASA `object service` re-emitted by the conversion as an SRX
        custom `application`, so it lands in B's applications section, not service_objects.
        Recovered by value (tcp/8443) under applications — section-shape fidelity gap, not a
        true loss of the object.
Section: interfaces          unchanged 2  added 0  removed 0  changed 0  (paired by address)
  ~ [A→B] interface @203.0.113.2/24: name GigabitEthernet0/0 → ge-0/0/0.0  (lossy rename —
        name is not-comparable across platforms; reported as a fidelity note, not a true diff)
  ~ [A→B] interface @10.0.0.1/24:   name GigabitEthernet0/1 → ge-0/0/1.0  (same)
Not comparable: physical interface names (GigabitEthernet0/x vs ge-0/0/x — paired by IP);
  ASA `nameif` + `security-level` semantics (implicit high→low permit has no SRX equivalent —
  the conversion drops it, so SRX default-deny would block inside→outside until an explicit
  permit policy is added; this intent loss is a fidelity gap, not a schema add/remove)

Parity verdict: DIFFERENCES FOUND (3)  (A=cisco-asa, B=srx)
```

**Fidelity read-out:** the security-relevant content round-trips cleanly — addresses,
the policy match-and-action tuple, NAT, zones, and routes are all `EQUIVALENT`. The gaps are
**representational, not behavioral mismatches in the comparable rule set**: (1) the ASA
`object service` migrates into SRX's custom-application section; (2) interface names are
platform-bound and remap; (3) the ASA `security-level` implicit-permit semantics have no SRX
equivalent and are dropped by the conversion — the single biggest fidelity risk, since it
means an explicit inside→outside permit must be added on SRX. None of these are false diffs:
each is either recovered by value in another section or flagged `not-comparable`.
