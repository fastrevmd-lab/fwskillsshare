---
name: parsing-srx-configs
description: >
  Parse and analyze Juniper SRX / Junos firewall configurations. Use this skill when the user
  pastes, uploads, or references an SRX configuration — either in "set" command format
  (show configuration | display set) or hierarchical curly-brace format (show configuration).
  Trigger on keywords: SRX, Junos, Juniper, "set security", "security zones", "address-book",
  "applications", "security policies", "from-zone", "to-zone", "nat rule-set", "chassis cluster",
  "logical-systems", "routing-instances". Also trigger when the user asks to convert, audit,
  summarize, or explain an SRX config.
version: 1.0.0
---

# Parsing Juniper SRX Configurations

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

**Detection heuristic:** Count lines starting with `set `. If > 30% of non-empty lines, treat as
set-command format. Otherwise treat as hierarchical.

### Hierarchical to Set Conversion

If hierarchical format is detected, mentally convert to flat set commands before parsing:
- Track the current path as you descend into `{ }` blocks
- Each leaf value terminated by `;` becomes: `set <path> <value>`
- Handle `inactive:` prefix → convert to `deactivate <path>`
- Handle bracket lists `[val1 val2]` → expand to one set command per value
- Handle quoted strings as single tokens

## Extraction Pipeline

Parse the following sections in order. For each, read the reference files as needed.

### 1. Zones
Path: `security.zones.security-zone.<name>`
Extract: zone name, interfaces list, description, host-inbound-traffic services/protocols

### 2. Address Objects
Path: `security.address-book.global.address.<name>`
Types to handle:
- `ip-prefix` (e.g., `10.0.0.0/24`) — type: "subnet"
- `dns-name` — type: "fqdn"
- `range-address` with `to` — type: "range", value: "start-end"
- `wildcard-address` — type: "wildcard"
- Plain IP with `/32` — type: "host"

Auto-detect IP version (v4 vs v6) from the value.

### 3. Address Groups
Path: `security.address-book.global.address-set.<name>`
Extract members from `address` and nested `address-set` references.

### 4. Service Objects (Applications)
Path: `applications.application.<name>`
Extract: protocol (from `protocol` field), destination port (from `destination-port`),
source port if present, ICMP type/code, inactivity-timeout, description.

Map `protocol` values: `6` or `tcp` → TCP, `17` or `udp` → UDP, `1` or `icmp` → ICMP.

### 5. Service Groups (Application Sets)
Path: `applications.application-set.<name>`
Extract member applications and nested application-sets.

### 6. Security Policies
Path: `security.policies.from-zone.<src>.to-zone.<dst>.policy.<name>`
Also: `security.policies.global.policy.<name>` (global policies, src/dst zones = ["any"])

For each policy extract:
- **name** and **description**
- **src_zones** / **dst_zones** — from the path (or ["any"] for global)
- **src_addresses** / **dst_addresses** — from `match source-address` / `match destination-address`
- **applications** — from `match application`
- **action** — `permit` → "allow", `deny` → "deny", `reject` → "reset-both"
- **log_start** — true if `then log session-init`
- **log_end** — true if `then log session-close`
- **security_profiles** — extract from `then permit application-services`:
  - `utm-policy` → profile_group
  - `idp-policy` → IDP profile
  - `ssl-proxy` → SSL proxy profile
- **disabled** — true if `deactivate` prefix on the policy path
- **schedule** — from `scheduler-name`
- **source_users** — from `match source-identity`

### 7. NAT Rules
Paths:
- `security.nat.source.rule-set.<name>.rule.<name>` — source NAT
- `security.nat.destination.rule-set.<name>.rule.<name>` — destination NAT
- `security.nat.static.rule-set.<name>.rule.<name>` — static NAT

Extract: type, src/dst zones (from rule-set `from`/`to`), match addresses,
translated source/destination/port.

### 8. Schedules
Path: `schedulers.scheduler.<name>`
Extract: name, type (daily-except/daily), start-date, stop-date, days of week, time ranges.

### 9. Routing
- **Static routes:** `routing-options.static.route.<prefix>.next-hop`
- **BGP:** `protocols.bgp.group.<name>` — local-as, peer-as, neighbors, export/import policies
- **OSPF:** `protocols.ospf.area.<id>` — interfaces, area type, reference-bandwidth
- **OSPFv3:** `protocols.ospf3.area.<id>`

### 10. Infrastructure
- **HA:** `chassis.cluster` — redundancy-groups, node priorities, heartbeat interfaces, fab links
- **Screen/IDS:** `security.screen.ids-option.<name>` — TCP/UDP/ICMP/IP protections
- **VPN:** `security.ike` and `security.ipsec` — gateways, proposals, tunnels
- **Syslog:** `system.syslog.host` — remote logging targets
- **DHCP:** `system.services.dhcp-local-server` or `forwarding-options.dhcp-relay`

### 11. Multi-Context
Detect `logical-systems.<name>` and `tenants.<name>` in the config tree.
Parse each context independently, tag all extracted items with `_logical_system` or `_tenant`.

### 12. Implicit Rules
After parsing all explicit policies, append:
- **Implicit: Default Deny** — action: "deny", src/dst zones: ["any"], src/dst addresses: ["any"],
  applications: ["any"], disabled: false, `_implicit: true`

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.

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
