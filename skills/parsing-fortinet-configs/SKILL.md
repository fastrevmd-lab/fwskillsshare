---
name: parsing-fortinet-configs
description: 'Use when the user pastes, uploads, or references a Fortinet FortiGate / FortiOS config to parse and analyze — the "config/edit/set/next/end" block format from "show full-configuration" or backup exports. Trigger on keywords: FortiGate, FortiOS, Fortinet, VDOM, "config firewall policy", "config firewall address", "config firewall service custom", "config system interface", "edit", "set srcintf", "set dstintf", "set srcaddr", "set dstaddr", "set action accept", "set utm-status enable", "set av-profile", "set webfilter-profile", "set ips-sensor". Also trigger when the user asks to convert, audit, summarize, or explain a FortiGate config.'
version: 1.1.3
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - firewall
    - config-parsing
    - fortinet
    - fortigate
    - fortios
    - vdom
    - policy
    - vip
    - nat
    - utm
    - migration
    - audit
    related_skills:
    - parsing-srx-configs
    - parsing-palo-configs
    - parsing-cisco-configs
    - firewall-best-practices-audit
    - firewall-config-conversion
    - firewall-config-diff
---

# Parsing Fortinet FortiGate Configurations

## Overview

Use this skill to parse Fortinet FortiGate / FortiOS backup or `show full-configuration` output into the shared vendor-neutral firewall intermediate schema. It focuses on nested `config` / `edit` / `set` / `next` / `end` blocks, including VDOMs, interfaces, zones, firewall addresses and services, policies, central SNAT, VIPs, routes, VPN, HA, profiles, and system settings.

FortiOS behavior is version- and feature-dependent. Preserve unknown blocks in `residual_raw`, capture VDOM context, and flag policy/NAT/profile constructs that cannot be mapped cleanly to the intermediate schema.

## When to Use

Use this skill when:

- the user pastes or references FortiGate, FortiOS, or backup configuration output
- the task is to parse, audit, summarize, compare, or convert a FortiGate configuration
- the config contains `config firewall policy`, `config firewall address`, `config system interface`, `config vdom`, `set srcintf`, or `set dstintf`
- you need vendor-neutral JSON before migration to SRX, PAN-OS, ASA/FTD, or another platform

Do not use this skill as a substitute for device-specific validation. When the parse result will drive production changes, verify against current vendor documentation and live device output where available.

Not this skill: for Cisco ASA/FTD configs use parsing-cisco-configs, PAN-OS/Panorama use parsing-palo-configs, Juniper SRX use parsing-srx-configs. Format tripwire — stop and hand off if the input shows column-0 commands with space-indented sub-commands and `nameif`/`access-list`/`object network` (Cisco ASA/FTD), XML `<entry name=` or flat `set deviceconfig`/`set rulebase` (PAN-OS), or curly-brace hierarchy / `set security zones|policies` (SRX). Downstream consumers of this parse: firewall-best-practices-audit, firewall-config-conversion, firewall-config-diff.

## Input Format

FortiOS configs use a hierarchical block format:
```
config <section>
    edit <name-or-id>
        set <key> <value>
        set <key> <value>
        config <sub-section>
            edit <sub-name>
                set <key> <value>
            next
        end
    next
    edit <name-or-id>
        ...
    next
end
```

Key syntax rules:
- Values with spaces are quoted: `set comment "Allow web traffic"`
- Multi-value fields use space-separated values: `set srcaddr "addr1" "addr2"`
- Full block-syntax rules: `references/config-format.md`

### Building the Config Tree

Parse the block format into a nested object tree:
1. Track a stack of current context (section path + edit name)
2. `config <X>` → push section name
3. `edit <N>` → push entry name (strip quotes)
4. `set <key> <value>` → store key-value at current depth
5. `next` → pop entry
6. `end` → pop section

## Extraction Pipeline

### 1. Zones and Interfaces
**Zones:** `config system zone` → `edit <name>` with `set interface <list>`
**Interfaces:** `config system interface` → `edit <name>` with `set vdom`, `set ip`, `set type`, `set vlanid`
Additional interface fields to extract:
- `set ip6 <addr/prefix>` (inside nested `config ipv6` sub-block) — IPv6 address
- `set mtu <value>` — MTU
- `set type aggregate` → type: "lag" (with `set member` for LAG members)
- `set type loopback` → type: "loopback"
- `set type tunnel` → type: "tunnel"
- `set mode dhcp` — DHCP client (no static IP)
- `set dhcp-relay-ip <ips>` — DHCP relay server IPs
- `set allowaccess <list>` — management access protocols
- `set fortilink enable` — FortiLink interface (exclude from output along with child interfaces)
- `set description <text>`
- Subinterface detection: dot-notation (`port1.100` → parent=`port1`) or VLAN-bound (`set interface <parent>` + `set vlanid <id>`)
- Management interface detection: names matching `/^(mgmt\d*|management\d*)/i` → `is_mgmt: true`
- After all interfaces parsed, back-populate `lag_members` on aggregate interfaces

**Critical: Interface-as-Zone Merging**
FortiGate can use interface names directly as zones in policies (via `srcintf`/`dstintf`).
If a policy references an interface name not in any zone, treat that interface as its own zone.
Merge zones and interfaces: create a zone entry for each interface used as a zone.

**Zone Building Priority 3: Unzoned Interfaces**
After explicit zones and policy-referenced interfaces, create auto-zones for any interface that has an IP address (or is a DHCP client) but was not yet assigned to a zone.

**Allowaccess Classification:**
Classify `allowaccess` values into management services (ssh, https, http, telnet, ping, snmp, netconf, fgfm, fmg-access, ftm, radius-acct, security-fabric, fabric, capwap, speed-test) and routing protocols (ospf, bgp, rip, isis, bfd). Attach to zones as `host_inbound` data.

### 2. Address Objects
Path: `config firewall address` → `edit <name>`

Types — detect from `set type` or infer from fields:
- `set type ipmask` + `set subnet <ip> <mask>` → type: "subnet" (convert mask to CIDR); promote a /32 (or IPv6 /128) result to type: "host"
- `set type iprange` + `set start-ip` / `set end-ip` → type: "range", value: "start-end"
- `set type fqdn` + `set fqdn <domain>` → type: "fqdn"
- `set type geography` + `set country <code>` → type: "geo" (warn: limited cross-platform support)
- `set type wildcard` + `set wildcard <ip> <mask>` → type: "wildcard" (preserve the `<ip> <mask>` wildcard value; "network" is NOT a valid schema type) with info warning
- `set type wildcard-fqdn` + `set wildcard-fqdn <pattern>` → type: "fqdn" (convert from wildcard-fqdn with info warning)

Also extract: `set comment`, `set associated-interface`.
Convert subnet mask notation (`255.255.255.0`) to CIDR (`/24`).
Auto-detect IP version.

**IPv6 Address Objects:** `config firewall address6` → `edit <name>`
- `set ip6 <ipv6prefix/len>` → type: "subnet" (or "host" if /128)
**IPv6 Address Groups:** `config firewall addrgrp6` → `edit <name>`
- `set member <list>`

### 3. Address Groups
Path: `config firewall addrgrp` → `edit <name>`
Extract: `set member <list>` (space-separated quoted names)

### 4. Service Objects
Path: `config firewall service custom` → `edit <name>`
Extract from:
- `set protocol TCP/UDP/SCTP` + `set tcp-portrange <range>` / `set udp-portrange <range>` / `set sctp-portrange <range>`
- `set protocol ICMP` + `set icmptype` / `set icmpcode`
- `set protocol IP` + `set protocol-number <n>` → preserve the IP protocol number `<n>` (e.g. GRE=47, ESP=50) as the service object's protocol (the numeric value, or via a warning). Only emit protocol: "any" when `set protocol IP` genuinely means all IP protocols (no `protocol-number`, or `protocol-number 0`).
- `set protocol ICMP6` → protocol: "icmpv6"
- Port range format: `80` or `80-443` or `80:1024-65535` (dst:src)
- Note: A single custom service can set ANY combination of `tcp-portrange`, `udp-portrange`, and `sctp-portrange` simultaneously. Split into separate service objects — one TCP, one UDP, and/or one SCTP — according to which ranges are present.

### 5. Service Groups
Path: `config firewall service group` → `edit <name>`
Extract: `set member <list>`

### 6. Security Policies
Path: `config firewall policy` → `edit <id>`

For each policy extract:
- **name** — `set name <value>` (FortiGate uses numeric IDs as primary key, name is optional)
- **src_zones** — `set srcintf <list>` (interface or zone names)
- **dst_zones** — `set dstintf <list>`
- **src_addresses** — `set srcaddr <list>`
- **dst_addresses** — `set dstaddr <list>`
- **services** — `set service <list>`
- **applications** — `set application <list>` (application control IDs/names)
- **action** — `set action accept` → "allow", `set action deny` → "deny"
- **log_start** — `set logtraffic-start enable` (start logging is controlled separately from `logtraffic`)
- **log_end** — `set logtraffic all`. `set logtraffic utm` logs UTM/security events only, NOT end-of-session traffic — map to log_end: false and note UTM-only logging in `metadata.warnings`
- **disabled** — `set status disable`
- **description** — `set comments <value>`
- **schedule** — `set schedule <value>`
- **source_users** — `set groups <list>` (FSSO groups)

**Policy NAT (do NOT emit a policy `nat` field — the policy schema has no `nat` field):**
FortiGate per-policy source NAT (`set nat enable`, optionally with `set ippool enable` + `set poolname <pool>`) must be translated into a `nat_rules[]` source-NAT entry, NOT a flag on the policy:
- `set nat enable` alone → source-NAT (interface/egress overload) on the policy's `dstintf`, scoped to the policy's `srcaddr`/`dstaddr`.
- `set nat enable` + `set ippool enable` + `set poolname <pool>` → source-NAT using the named IP pool `<pool>` (cross-reference `config firewall ippool`).
- If the source-NAT intent cannot be resolved to a concrete `nat_rules[]` entry, preserve it as a `metadata.warnings` / `residual_raw` note rather than inventing a policy field.

**Default values** when fields are omitted from config:
- `action` defaults to `accept` (→ "allow")
- `logtraffic` defaults to `utm` on accept policies (→ log_end: false; UTM-event logging only)
- `status` defaults to `enable` (→ disabled: false)

**UTM / Security Profiles** — when `set utm-status enable`:
- `set av-profile <name>` → antivirus
- `set webfilter-profile <name>` → URL filtering
- `set ips-sensor <name>` → IPS/IDP
- `set application-list <name>` → application control (do NOT emit an `application-list` security-profile key — it is not a schema-supported profile key; signal app-control presence via `security_services.app_id` at device level and/or store the profile reference in `security_profile_objects` / `metadata.warnings`)
- `set ssl-ssh-profile <name>` → SSL inspection
- `set dnsfilter-profile <name>` → DNS filtering
- `set emailfilter-profile <name>` → email filtering
- `set dlp-profile <name>` → DLP
- `set profile-group <name>` → profile group (overrides individual profiles)

### 7. NAT Rules
**Source NAT (IP Pools):** `config firewall ippool` → `edit <name>`
  Extract: `set startip`, `set endip`, `set type` (overload, one-to-one, fixed-port-range), `set associated-interface <name>` — binds pool to specific egress interface

**Central SNAT:** `config firewall central-snat-map` → `edit <id>`
  Extract the full FortiOS central-SNAT field set so real rules are not missed:
  - `set srcintf <list>` — source interface(s)
  - `set dstintf <list>` — destination/egress interface(s)
  - `set orig-addr <list>` — original (pre-NAT) source addresses
  - `set dst-addr <list>` — destination addresses the rule matches
  - `set nat enable|disable` — whether this entry performs NAT (a disabled entry = no-NAT exemption; preserve it)
  - `set nat-ippool <list>` (also `set natippool` variant) — translated source pool; absent → egress-interface overload
  - `set protocol <n>` and `set orig-port` / `set nat-port` where present — protocol/port scoping
  Map to a `nat_rules[]` source-NAT entry (or a no-NAT exemption when `nat disable`).

**Destination NAT (VIPs):** `config firewall vip` → `edit <name>`
  Extract: `set extip` (original dest), `set mappedip` (translated dest),
  `set extintf`, `set portforward enable` + `set extport` / `set mappedport`
  Note: VIPs are referenced in policies via `set dstaddr <vip-name>`

### 8. Schedules
**Recurring:** `config firewall schedule recurring` → `edit <name>`
  Extract: `set day`, `set start`, `set end`
**One-time:** `config firewall schedule onetime` → `edit <name>`
  Extract: `set start`, `set end`
**Group:** `config firewall schedule group` → `edit <name>`
  Extract: `set member`

### 9. Application Mapping (L7 → Canonical)

FortiGate supports L7 application control via `set application <list>` on policies. These reference
FortiOS application IDs or names from the application control database.

**Extracting application references from policies:**
- `set application <list>` — space-separated application IDs or names
- `set application-list <name>` — references an application control list profile (separate from direct app match)

**Resolving FortiOS application names to canonical:**

| FortiOS Name | Canonical App | Category |
|-------------|---------------|----------|
| `HTTPS` | `https` | web |
| `HTTP` | `http` | web |
| `SSH` | `ssh` | remote-access |
| `RDP` | `rdp` | remote-access |
| `DNS` | `dns` | network-mgmt |
| `SMTP` | `smtp` | email |
| `NTP` | `ntp` | network-mgmt |
| `SNMP` | `snmp` | network-mgmt |
| `FTP` | `ftp` | file-transfer |
| `TFTP` | `tftp` | file-transfer |
| `SIP` | `sip` | voip |
| `LDAP` | `ldap` | auth |
| `Kerberos` | `kerberos` | auth |
| `SMB` | `smb` | file-transfer |
| `MySQL` | `mysql` | database |
| `MSSQL` | `mssql` | database |
| `PostgreSQL` | `postgresql` | database |
| `MongoDB` | `mongodb` | database |
| `Zoom` | `zoom` | collaboration |
| `Microsoft.Teams` | `ms-teams` | collaboration |
| `Slack` | `slack` | collaboration |
| `YouTube` | `youtube` | streaming |
| `Netflix` | `netflix` | streaming |

**On policy output:** When `set application` values are resolved, populate the policy's `apps` array
with `{ vendor_name: "HTTPS", canonical: "https", confidence: 1.0, category: "web" }`.
The `services` array keeps any `set service` matches separately.

**Application control list profiles** (`config application list`) define grouped app-control
policies. These do not map 1:1 to application groups — they are UTM profiles that filter
applications by category, risk, or specific app ID. The schema has no `application-list`
profile key — represent app-control presence via `security_services.app_id` (device-level)
and store the profile reference in `security_profile_objects` and/or `metadata.warnings`.
Do not try to decompose the list into individual apps.

**Unresolvable apps:** FortiOS numeric app IDs without a known name mapping → set `confidence: 0.0`,
preserve the ID as `vendor_name`, and warn.

### 9b. Application Groups

FortiOS does not have explicit application groups in the same way PAN-OS does. The closest
equivalent is `config application group` which groups application control signatures.

Path: `config application group` → `edit <name>`
Extract: `set application <list>` — member application IDs/names.
Resolve each member to canonical. Store in `application_groups` array.

If a group contains a mix of L7 apps and port-based services, split them appropriately.

### 10. Security Profile Definitions
Parse full profile objects for reference:
- `config antivirus profile`
- `config webfilter profile`
- `config ips sensor`
- `config application list`
- `config firewall ssl-ssh-profile`

### 11. Routing
- **Static routes (IPv4):** `config router static` → `edit <id>` with `set dst`, `set gateway`, `set device`, `set distance`
- **Static routes (IPv6):** `config router static6` → `edit <id>` with same fields using IPv6 prefixes
- **BGP:** `config router bgp` — extract:
  - `set as`, `set router-id`, global `set keepalive-timer`/`set holdtime-timer`
  - Per-neighbor (in `config neighbor`): `remote-as`, `description`, `update-source`, `password` (record presence only — redact the value, never emit it), per-neighbor timers (override global), `next-hop-self`, `soft-reconfiguration`, `route-reflector-client`, `status enable|disable`
  - `config network` entries (prefix advertisements)
  - `config redistribute` with `set status enable|disable`
  - Warn: route-map/prefix-list references are not converted
- **OSPF:** `config router ospf` — extract:
  - `set router-id`, `set auto-cost-reference-bandwidth`
  - `config area`: area ID, type (stub/nssa with no-summary), default-cost, authentication
  - `config ospf-interface`: area assignment, passive flag, cost, priority, hello/dead intervals, network-type (point-to-point/broadcast), MD5 authentication with key ID (record key presence only — redact the key value)
  - `config redistribute`: source, status, metric, metric-type
  - Warn: MD5 keys in cleartext in source config (key values are never emitted in output)
- **OSPFv3:** `config router ospf6` — same structure but uses `config ospf6-interface` (not `ospf-interface`)
- **Policy routing:** `config router policy` → PBF rules

### 12. Infrastructure
- **Version:** Extract from `#config-version=<version>:` comment line at top of config
- **System Global:** `config system global` → extract `set hostname`
- **DNS:** `config system dns` → extract `set primary`, `set secondary`, `set domain`
- **NTP:** `config system ntp` with nested `config ntpserver` → extract server entries
- **Admin Users:** `config system admin` → extract access profile (super_admin→super-admin, prof_admin→admin), SSH public keys (ssh-public-key1/2/3). Warn when users lack SSH keys.
- **HA:** `config system ha` — `set mode` (a-p/a-a), `set group-id`, `set priority`,
  `set hbdev`, `set monitor`
- **Screen/DoS:** `config firewall DoS-policy` + IPS sensor definitions
- **Syslog:** `config log syslogd setting`
- **DHCP Server:** `config system dhcp server` — extract top-level fields (`set default-gateway`, `set netmask`, `set interface`, `set domain`, `set lease-time`, `set dns-server1/dns-server2`) plus nested `config ip-range` (start-ip/end-ip) and `config reserved-address` (mac, ip, description). Derive network CIDR from gateway + netmask.
**FortiOS compound proposal parsing for VPN:**
FortiOS encodes IKE/IPsec proposals as compound strings. Do NOT assume every proposal is a simple
`encryption-integrity` pair — parse encryption / integrity / prf separately:
- **Simple enc-integrity:** `aes256-sha256` → encryption (`aes256` → canonical `aes-256`) + integrity (`sha256`).
- **AEAD GCM (no separate integrity):** `aes256gcm`, `aes128gcm`, `chacha20poly1305` carry their own
  authentication — integrity is N/A. Phase2 GCM is the bare token (e.g. `aes256gcm`, no integrity suffix).
- **IKEv2 phase1 PRF suffix (phase1-only):** `aes256gcm-prfsha384` → encryption `aes256gcm`, prf `sha384`,
  no separate integrity. The `prf*` suffix appears only on phase1 proposals, never phase2.
- **null:** `null` encryption (no confidentiality) and `null` integrity also exist — flag as weak.
Multiple proposals are space-separated: `aes256-sha256 aes128-sha1 aes256gcm`. Tokenize each on `-`,
then classify each segment as encryption, integrity, or prf rather than assuming a fixed two-part split.

- **VPN IPsec:**
  - `config vpn ipsec phase1-interface`: IKE version, remote-gw, proposal (compound strings — see "FortiOS compound proposal parsing" above), DH group, key lifetime, PSK presence (mask the value as `"****"` per the schema — never emit the raw key), certificate auth detection
  - `config vpn ipsec phase2-interface`: phase1name reference, proposal, PFS, DH group, key lifetime
  - Phase1 name auto-creates a tunnel interface of the same name
  - Resolve tunnel IP from matching interface, associate static routes through tunnel interfaces
  - Flag weak algorithms (DES/3DES, MD5, DH group ≤ 5)
  - Warn: certificate-based auth not fully converted

### 13. Tokenizer
Handle quoted multi-value lines correctly: `set member "HOST_A" "HOST_B"` → `['set', 'member', 'HOST_A', 'HOST_B']`. Strip quotes during tokenization. Values containing spaces must be kept as single tokens when quoted.

### 14. Residual Config Capture
Capture unrecognized `config` sections verbatim with depth tracking. Categorize into: VPN/IPsec, Routing Protocols, AAA/Users, PKI/Certificates, Wireless, Switching, DNS, NTP, SNMP, Other. Store in `residual_raw` for manual review.

### 15. Multi-VDOM
Detect VDOM context: `config vdom` / `edit <vdom-name>`.
Each interface has `set vdom <name>`. Parse per-VDOM, tag items, merge.

### 16. Implicit Rules
After parsing all explicit policies, append:
- Per-zone **Intra-zone** rules ONLY for explicit `config system zone` entries carrying
  `set intrazone deny|allow`. Do NOT fabricate intra-zone rules for raw interface auto-zones
  (interfaces never declared in `config system zone`).
- **Implicit: Default Deny** — action: "deny", all any, `_implicit: true`

Implicit-rule `name` values (e.g. "default-deny", "Implicit: Default Deny") are free-form labels; consumers must match implicit rules on `_implicit: true`, never on the name.

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.

Note: schema sections not yet populated by this pipeline (e.g., `security_profile_objects`, `routing_contexts`) are emitted empty (`[]`/`{}`); any unhandled source constructs are captured in `residual_raw` rather than dropped.

**Full intermediate-schema emission is optional for single live-device work.** The complete JSON schema exists primarily for cross-vendor conversion and multi-config diffing. When interpreting or auditing a *single* live device pulled via SSH/API for an ops/audit task, it is fine to reason directly from the raw FortiOS config and skip full schema emission — extract the sections relevant to the question. Emit the full schema when the parse will feed `firewall-config-conversion`, `firewall-config-diff`, or another config for comparison.


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
1. **Unused objects** — addresses/services not referenced by any policy
2. **Shadowed policies** — rules fully covered by earlier rules
3. **Overly permissive** — rules with "all" in src+dst addresses and services
4. **Missing logging** — `set logtraffic disable` or `set logtraffic utm` on permit rules
5. **Disabled policies** — `set status disable`
6. **Duplicate objects** — same value, different names
7. **Empty groups** — groups with no members
8. **VIP references** — VIPs used as dst addresses (flag for NAT review)
9. **Geography objects** — limited cross-platform support

## Reference Files

- `references/config-format.md` — FortiOS config block syntax reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, mask conversion, application mapping
- `references/example-sample-parse.md` — Worked end-to-end example (input config → parsed JSON)
- `references/fixture-minimal-input.md` — Minimal parser fixture input
- `references/fixture-expected-output.json` — Expected high-level intermediate-schema output for the minimal fixture

## Secret Handling

Never emit secrets raw. IKE/VPN pre-shared keys, routing-protocol authentication keys (BGP/OSPF), and user password hashes must be masked as `"****"` (or reduced to a presence flag) with a `metadata.warnings` entry noting the redaction — matching the shared-schema convention (`"psk": "****"`).

## Common Pitfalls

1. Do not assume every policy interface is a zone; FortiGate policies can reference zones or raw interfaces.
2. VIP objects often imply destination NAT when referenced by policies; preserve both policy and NAT intent.
3. Central SNAT and per-policy NAT are different models; detect both and warn when both are present.
4. Quoted multi-value fields require tokenizer-aware parsing; whitespace splitting corrupts names with spaces.
5. Profile groups and individual UTM profiles must be expanded while preserving unmapped FortiGate-specific profile fields.
6. Never emit raw secrets: mask VPN PSKs as `"****"` and represent BGP neighbor passwords and OSPF MD5 keys as presence flags plus a `metadata.warnings` note — shared secrets, passwords, and keys must never appear verbatim in parse output.

## Verification Checklist

- [ ] Input vendor/platform and config format were detected correctly
- [ ] All major object counts are reported: zones, interfaces, addresses, services/applications, policies, NAT, routes, VPN, HA, and system settings
- [ ] Output conforms to `references/intermediate-schema.md`
- [ ] Disabled/inactive rules and objects are preserved with explicit state
- [ ] Unresolved references, unsupported blocks, and parser assumptions are listed in `metadata.warnings` and/or `residual_raw`
- [ ] Rule order and NAT order are preserved with `_rule_index` or equivalent ordering metadata
- [ ] Cross-vendor conversion caveats are called out before suggesting target-platform config
- [ ] No raw secrets in output — PSKs masked as `"****"`, BGP/OSPF passwords and keys reduced to presence flags with warnings
