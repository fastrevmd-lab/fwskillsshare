---
name: parsing-srx-configs
description: 'Parse and analyze Juniper SRX / Junos firewall configurations. Use this skill when the user pastes, uploads, or references an SRX configuration — either in "set" command format (show configuration | display set) or hierarchical curly-brace format (show configuration). Trigger on keywords: SRX, Junos, Juniper, "set security", "security zones", "address-book", "applications", "security policies", "from-zone", "to-zone", "nat rule-set", "chassis cluster", "logical-systems", "routing-instances". Also trigger when the user asks to convert, audit, summarize, or explain an SRX config.

  '
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - firewall
    - config-parsing
    - juniper
    - srx
    - junos
    - security-policy
    - nat
    - zones
    - address-book
    - migration
    - audit
    related_skills:
    - srx-policy
    - srx-nat
    - srx-mnha
    - srx-mpls-in-flow
    - srx-dynamic-ip-feed
---

# Parsing Juniper SRX Configurations

## Overview

Use this skill to parse Juniper SRX / Junos firewall configurations into the shared vendor-neutral firewall intermediate schema. It supports both `show configuration | display set` lines and hierarchical curly-brace configuration, including zones, address books, applications, security policies, NAT, logical-systems, routing-instances, interfaces, routing protocols, VPN, chassis cluster, and system settings.

For design interpretation after extraction, load the adjacent SRX operational skill that matches the topic: `srx-policy`, `srx-nat`, `srx-mnha`, `srx-mpls-in-flow`, or `srx-dynamic-ip-feed`.

## When to Use

Use this skill when:

- the user pastes or references SRX, Junos, Juniper, `show configuration`, or `display set` output
- the task is to parse, audit, summarize, compare, or convert an SRX configuration
- the config contains `set security`, `security zones`, `address-book`, `security policies`, `from-zone`, `to-zone`, `nat rule-set`, `logical-systems`, or `routing-instances`
- you need vendor-neutral JSON before cross-vendor migration or deeper SRX-specific interpretation

Do not use this skill as a substitute for device-specific validation. When the parse result will drive production changes, verify against current vendor documentation and live device output where available.

You are an expert at parsing Juniper SRX / Junos firewall configurations. When given raw SRX
config text, extract all components into a structured intermediate format.

## Input Format Detection

SRX configs come in two formats. Detect which one:

1. **Set commands** — Lines starting with `set ` or `deactivate `. Example:
   ```
   set security zones security-zone trust interfaces ge-0/0/0.0
   set security policies from-zone trust to-zone untrust policy allow-web match source-address any
   ```

2. **Hierarchical (curly-brace)** — Nested blocks with `{ }` and `;` terminators. Example:
   ```
   security {
       zones {
           security-zone trust {
               interfaces {
                   ge-0/0/0.0;
               }
           }
       }
   }
   ```

**Detection heuristic:** Check the first 2000 characters for known top-level stanza names followed by `{` (e.g., `system {`, `security {`, `interfaces {`, `routing-options {`). If found, treat as hierarchical. Otherwise treat as set-command format.

### Hierarchical to Set Conversion

If hierarchical format is detected, mentally convert to flat set commands before parsing:
- Track the current path as you descend into `{ }` blocks
- Each leaf value terminated by `;` becomes: `set <path> <value>`
- Handle `inactive:` prefix → convert to `deactivate <path>`
  Note: `inactive:` (hierarchical format) and `deactivate` (set format) are equivalent. In hierarchical parsing, strip `inactive:` and set `enabled: false` on the affected object. Handle the re-parse: strip the prefix, rebuild as a normal set line, re-tokenize to extract the target object name.
- Handle bracket lists `[val1 val2]` → expand to one set command per value
- Handle quoted strings as single tokens
- Handle backslash escapes inside quoted strings
- Strip block comments `/* ... */`

**Hierarchical-to-set normalization:** After conversion, normalize these impedance mismatches:
1. `range-address X to range-high Y` → `range-address X to Y`
2. `address NAME ip-prefix CIDR` → `address NAME CIDR`
3. `then static-nat prefix name CIDR` → `then static-nat prefix CIDR`
4. `then source-nat pool pool-name NAME` → `then source-nat pool NAME`
5. `then destination-nat pool pool-name NAME` → `then destination-nat pool NAME`
6. `then destination-nat ip addr X` → `then destination-nat ip X`

## Extraction Pipeline

Parse the following sections in order. For each, read the reference files as needed.

### 1. Zones
Path: `security.zones.security-zone.<name>`
Extract: zone name, interfaces list, description, host-inbound-traffic services/protocols

### 1b. Interfaces
Path: `interfaces.<name>` with units at `interfaces.<name>.unit.<id>`

Extract per-interface/unit:
- IPv4 address: `family inet address <cidr>`
- IPv6 address: `family inet6 address <cidr>`
- DHCP client: `family inet dhcp`
- VLAN tagging: `vlan-tagging` / `flexible-vlan-tagging`
- VLAN ID per unit: `vlan-id <id>`
- MTU: `mtu <value>`
- Description at both physical and unit level
- LAG membership: `ether-options 802.3ad <ae-name>` → set `lag_parent`
- LAG master: `aggregated-ether-options lacp` config

**Interface type derivation:** `ae*`=lag, `lo*`=loopback, `st0/gr-/ip-/lt-`=tunnel, `fxp0/fxp1/me0/em0/em1`=management.
**Management interface zone exclusion:** Remove management interfaces (fxp0, me0, em0, etc.) from security zones with a warning.
**Unit-0 normalization:** When resolving zone membership, normalize `.0` suffixed names (e.g., `ge-0/0/0.0` → `ge-0/0/0`) for matching.
**Cluster interface exclusion:** Skip chassis-cluster-specific interfaces (`reth*`, `fab*`) with a warning.
After all interfaces parsed, back-populate `lag_members` on ae interfaces.

### 2. Address Objects
Path: `security.address-book.global.address.<name>`
Types to handle:
- `ip-prefix` (e.g., `10.0.0.0/24`) — type: "subnet"
- `dns-name` — type: "fqdn"
- `range-address` with `to` — type: "range", value: "start-end"
- `wildcard-address` — type: "wildcard"
- Plain IP with `/32` — type: "host"

- `ip-prefix <cidr>` / `ipv6-prefix <cidr>` — explicit keywords in hierarchical format (normalize away during hierarchical-to-set conversion)

**Zone-attached address books:**
Path: `security.address-book.<zone-name>.address.<name>` (in addition to `global`)
Zone-attached books are common in older Junos configs. Migrate to global scope with a warning.

Auto-detect IP version (v4 vs v6) from the value.

### 3. Address Groups
Path: `security.address-book.global.address-set.<name>`
Extract members from `address` and nested `address-set` references.

### 4. Service Objects (Applications)
Path: `applications.application.<name>`
Extract: protocol (from `protocol` field), destination port (from `destination-port`),
source port if present, ICMP type/code, inactivity-timeout, description.

Map `protocol` values: `6` or `tcp` → TCP, `17` or `udp` → UDP, `1` or `icmp` → ICMP.

### 5. Application Mapping (L7 → Canonical)

JunOS uses predefined `junos-*` applications that are matched by name in security policies.
These are L7-aware on SRX and must be resolved to canonical names for cross-vendor conversion.

**JunOS predefined application names to canonical:**

| JunOS Name | Protocol/Port | Canonical App | Category |
|------------|---------------|---------------|----------|
| `junos-https` | TCP/443 | `https` | web |
| `junos-http` | TCP/80 | `http` | web |
| `junos-ssh` | TCP/22 | `ssh` | remote-access |
| `junos-telnet` | TCP/23 | `telnet` | remote-access |
| `junos-ftp` | TCP/21 | `ftp` | file-transfer |
| `junos-tftp` | UDP/69 | `tftp` | file-transfer |
| `junos-dns-udp` | UDP/53 | `dns` | network-mgmt |
| `junos-dns-tcp` | TCP/53 | `dns` | network-mgmt |
| `junos-ntp` | UDP/123 | `ntp` | network-mgmt |
| `junos-snmp` | UDP/161 | `snmp` | network-mgmt |
| `junos-snmptrap` | UDP/162 | `snmp-trap` | network-mgmt |
| `junos-smtp` | TCP/25 | `smtp` | email |
| `junos-smtps` | TCP/465 | `smtps` | email |
| `junos-imap` | TCP/143 | `imap` | email |
| `junos-imaps` | TCP/993 | `imaps` | email |
| `junos-pop3` | TCP/110 | `pop3` | email |
| `junos-ldap` | TCP/389 | `ldap` | auth |
| `junos-bgp` | TCP/179 | `bgp` | network-mgmt |
| `junos-ospf` | ANY | `ospf` | network-mgmt |
| `junos-sip` | UDP/5060 | `sip` | voip |
| `junos-h323` | TCP/1720 | `h323` | voip |
| `junos-ms-rpc` | TCP/135 | `msrpc` | other |
| `junos-ms-sql` | TCP/1433 | `mssql` | database |
| `junos-mysql` | TCP/3306 | `mysql` | database |
| `junos-smb` | TCP/445 | `smb` | file-transfer |
| `junos-ike` | UDP/500 | `ipsec` | tunnel |
| `junos-ike-nat-t` | UDP/4500 | `ipsec-nat-t` | tunnel |
| `junos-pptp` | TCP/1723 | `pptp` | tunnel |
| `junos-icmp-all` | ICMP | `ping` | network-mgmt |
| `junos-icmpv6-all` | ICMPv6 | `ping6` | network-mgmt |
| `junos-nntp` | TCP/119 | `nntp` | other |
| `junos-rdp` | TCP/3389 | `rdp` | remote-access |
| `junos-syslog` | UDP/514 | `syslog` | network-mgmt |

**Resolution in policies:** When `match application` lists a predefined app:
1. Look up in the table above
2. Populate policy's `apps` array: `{ vendor_name: "junos-https", canonical: "https", confidence: 1.0, category: "web" }`
3. The `services` array keeps `application-default` or explicit port references separately

**Custom applications** (`applications.application.<name>`): These are user-defined with explicit
protocol and port. Extract as service objects AND attempt canonical resolution from protocol+port.
If the port matches a known app, set `confidence: 0.9`.

**Unresolvable apps:** For `any` application match or custom apps without a canonical mapping,
set `confidence: 0.0`, preserve the vendor_name, and warn.

### 5b. Service Groups (Application Sets)
Path: `applications.application-set.<name>`
Extract member applications and nested application-sets.

**Application-Set vs Application-Group distinction:**
- Determine member types: for each member, check if it is a predefined `junos-*` L7 app or a
  user-defined port-based application
- Application-sets containing **all L7/predefined apps** → promote to `application_groups` with
  canonical member names
- Sets containing **user-defined port-based apps** → keep as `service_groups`
- **Mixed sets** → split: L7 members → `application_groups`, port-based → `service_groups`

Resolve each L7 member from JunOS name to canonical before storing in `application_groups`.

### 6. Security Policies
Path: `security.policies.from-zone.<src>.to-zone.<dst>.policy.<name>`
Also: `security.policies.global.policy.<name>` (global policies, src/dst zones = ["any"])

For each policy extract:
- **name** and **description**
- **src_zones** / **dst_zones** — from the path (or ["any"] for global)
- **src_addresses** / **dst_addresses** — from `match source-address` / `match destination-address`
- **applications** — from `match application`
- **action** — `permit` → "allow", `deny` → "deny", `reject` → "deny" (with info warning: "reject converted to deny — target may not support TCP reset")
- **log_start** — true if `then log session-init`
- **log_end** — true if `then log session-close`
- **security_profiles** — extract from `then permit application-services`:
  - `utm-policy` → profile_group
  - `idp-policy` → IDP profile
  - `ssl-proxy` → SSL proxy profile
- **disabled** — true if `deactivate` prefix on the policy path
- **schedule** — from `scheduler-name`
- **source_users** — from `match source-identity`
- Handle `then count` and `then permit firewall-authentication` as no-ops (do not misinterpret as action modifiers)

### 7. NAT Rules
Paths:
- `security.nat.source.rule-set.<name>.rule.<name>` — source NAT
- `security.nat.destination.rule-set.<name>.rule.<name>` — destination NAT
- `security.nat.static.rule-set.<name>.rule.<name>` — static NAT

Extract: type, src/dst zones (from rule-set `from`/`to`), match addresses,
translated source/destination/port.

**Source NAT specifics:**
- `then source-nat interface` → translate to egress interface
- `then source-nat pool <poolname>` → translate to named pool (emit as `pool:<name>`)

**Destination NAT specifics:**
- `destination-port <port>` → original service match
- `then destination-nat pool <poolname>` → translated destination from pool
- `then destination-nat pool <poolname> port <port>` → translated destination + port
- Handle hierarchical `ip addr <ip>` form for inline destination translation

**Static NAT specifics:**
- `then static-nat prefix <cidr>` → bidirectional static translation

### 8. Schedules
Path: `schedulers.scheduler.<name>`
Extract: name, type (daily-except/daily), start-date, stop-date, days of week, time ranges.

### 9. Routing
- **Static routes (IPv4):** `routing-options.static.route.<prefix>` with `next-hop`, `qualified-next-hop` (floating statics), or `discard` (null routes)
- **Static routes (IPv6):** `routing-options.rib.inet6.0.static.route.<prefix>` — same structure
- **Routing Instances / VRF:** `routing-instances.<name>` — extract interface membership, per-VR static routes (IPv4+IPv6), per-VR OSPF/BGP config
- **BGP:** `protocols.bgp` — extract:
  - Local-AS, router-ID
  - Per-group: type (ebgp/ibgp), peer-as, local-address, authentication-key, hold-time, keepalive
  - Per-neighbor overrides: peer-as, description, local-address, authentication-key, hold/keepalive timers, next-hop-self, route-reflector-client
  - `deactivate` support for disabled neighbors
  - Merge group-level defaults with neighbor-level overrides
- **OSPF:** `protocols.ospf` — extract:
  - Router-ID, reference-bandwidth (with unit parsing: g/m/k suffixes)
  - Areas: area ID, type (normal/stub/nssa with no-summary), default-cost
  - Area authentication type and key
  - Per-interface: passive, metric, priority, hello/dead intervals, link-type (p2p/broadcast), per-interface authentication
  - Redistribute: source, metric, metric-type
  - `deactivate` support for disabled OSPF interfaces
  - Normalize area IDs to dotted-decimal
- **OSPFv3:** `protocols.ospf3` — same structure as OSPF via `ospf3` instances

### 10. System Configuration
Path: `system`
Extract:
- `system.host-name` → hostname
- `system.domain-name` → domain
- `system.name-server` → DNS servers
- `system.ntp.server` → NTP servers with `prefer` flag
- `system.services` → management services: ssh, telnet, netconf, https, http
- `system.login.user` → admin users with class and SSH public keys
  - Class mapping: super-user→super-admin, operator→operator, read-only→read-only

### 11. Infrastructure
- **Version:** `set version <X.Y>` → metadata.source_version
- **HA Chassis Cluster:** `chassis.cluster` — redundancy-groups, node priorities, heartbeat interfaces, fab links
- **HA MNHA:** `chassis.high-availability` — newer HA method on SRX4600/SRX5000 platforms
- **Screen/IDS:** `security.screen.ids-option.<name>` — TCP/UDP/ICMP/IP protections
- **VPN/IPsec:** Full IKE/IPsec chain resolution:
  - IKE proposals: encryption, integrity, DH group, lifetime, auth method (PSK vs certificate including RSA/DSA/ECDSA)
  - IKE policies: mode, proposals list, PSK value, local certificate
  - IKE gateways: peer address, external interface, IKE version (v1-only/v2-only), local/remote identity
  - IPsec proposals: encryption, integrity, lifetime
  - IPsec policies: proposals list, PFS group
  - IPsec VPNs: bind-interface, IKE gateway reference, IPsec policy reference, establish-tunnels
  - Resolve full chain: ipsecVpn → ikeGateway → ikePolicy → ikeProposal(s) → ipsecPolicy → ipsecProposal(s)
  - Associate tunnel interfaces (st0, gr-, ip-) with their IPs, collect routes through tunnels
  - Canonicalize algorithm names (e.g., aes-256-cbc → aes-256, hmac-sha-256-128 → sha256)
  - Flag weak algorithms (DES/3DES, MD5, DH group ≤ 5)
- **Syslog:** `system.syslog.host` — remote logging targets
- **DHCP Server:** `access.address-assignment.pool` — network, address ranges (low/high), router (gateway), name-server, maximum-lease-time, domain-name. Match pools to interfaces via `dhcp-local-server` group bindings using IP prefix matching.
- **DHCP Relay:** Two forms:
  - Legacy: `forwarding-options.helpers.bootp.server`
  - Modern: `forwarding-options.dhcp-relay.server-group` / `group` / `active-server-group` / `interface`
  Link relay server groups to per-interface `dhcp_relay` fields.

### 12. Multi-Context
Detect `logical-systems.<name>` and `tenants.<name>` in the config tree.
Parse each context independently, tag all extracted items with `_logical_system` or `_tenant`.

### 13. Residual Config Capture
Capture all unhandled `set` lines. Categorize into: IDS Screens, PKI/Certificates, QoS, SNMP, VLANs, Firewall Filters, Bridge Domains, Groups, Other. Store in `residual_raw` for manual review.

### 14. Implicit Rules
After parsing all explicit policies, append:
- **Implicit: Default Deny** — action: "deny", src/dst zones: ["any"], src/dst addresses: ["any"],
  applications: ["any"], disabled: false, `_implicit: true`

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.


## Parser Quality Gates

Before returning a parse, run these common quality gates and include the results in the response:

1. **Format and scope detection** — report detected vendor, platform family, config format, version clues, virtual context names (VDOM/vsys/logical-system/routing-instance), and whether input appears complete or partial.
2. **Schema conformance** — emit the vendor-neutral JSON sections defined in `references/intermediate-schema.md`; use empty arrays/objects for absent sections rather than omitting expected top-level keys.
3. **Object counts** — summarize counts for zones, interfaces, address objects/groups, service/application objects/groups, policies, NAT rules, routes, VPNs, HA, admin users, and residual blocks.
4. **Reference resolution** — list unresolved object, service/application, zone/interface, profile, route, VPN, and NAT references with source rule/context where possible.
5. **Ordering preservation** — preserve security policy order, NAT order, route order when relevant, and inherited/pre/post/global ordering metadata with `_rule_index` or a vendor-specific context field.
6. **State preservation** — preserve disabled/inactive objects and rules, comments/descriptions, tags, schedules/time-ranges, negation flags, logging settings, and profile attachments.
7. **Residual capture** — put unsupported or ambiguous source lines/blocks into `residual_raw` with enough context for manual review. Do not silently drop unknown syntax.
8. **Warnings and assumptions** — populate `metadata.warnings` with parser limitations, partial-input assumptions, ambiguous conversions, and version-specific caveats.
9. **Conversion readiness** — if the user asks for migration/conversion, explicitly separate parsed facts from proposed target-platform design choices and call out non-isomorphic features.

A high-quality parse is not just valid JSON: it must make uncertainty visible. Prefer a complete parse with warnings and residuals over a clean-looking parse that hides unsupported constructs.

## Analysis Checks

After extraction, run these checks and report findings:

1. **Unused objects** — address/service objects not referenced by any policy
2. **Shadowed policies** — rules that can never match because an earlier rule fully covers them
3. **Overly permissive** — rules with any/any source+destination or any/any zone+address+application
4. **Missing logging** — permit rules without `log session-close`
5. **Disabled policies** — rules with `deactivate` prefix
6. **Duplicate objects** — different names, same value
7. **Empty groups** — address-sets or application-sets with no members

## Reference Files

- `references/config-format.md` — Detailed SRX config syntax reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, predefined apps, and name sanitization

- `references/fixture-minimal-input.md` — Minimal parser fixture input
- `references/fixture-expected-output.json` — Expected high-level intermediate-schema output for the minimal fixture

## Common Pitfalls

1. Do not skip hierarchical-to-set normalization; inactive prefixes, bracket lists, and quoted strings affect extraction.
2. Zone-local address books are valid in older designs; migrate or normalize to global only with a warning.
3. Logical-systems and routing-instances are separate contexts; preserve them instead of merging names blindly.
4. Policy matching can depend on NAT order and translated addresses; load `srx-nat` for interpretation.
5. Management, cluster, reth, fab, and HA interfaces need special handling and should not be naively treated as ordinary security-zone interfaces.

## Verification Checklist

- [ ] Input vendor/platform and config format were detected correctly
- [ ] All major object counts are reported: zones, interfaces, addresses, services/applications, policies, NAT, routes, VPN, HA, and system settings
- [ ] Output conforms to `references/intermediate-schema.md`
- [ ] Disabled/inactive rules and objects are preserved with explicit state
- [ ] Unresolved references, unsupported blocks, and parser assumptions are listed in `metadata.warnings` and/or `residual_raw`
- [ ] Rule order and NAT order are preserved with `_rule_index` or equivalent ordering metadata
- [ ] Cross-vendor conversion caveats are called out before suggesting target-platform config
