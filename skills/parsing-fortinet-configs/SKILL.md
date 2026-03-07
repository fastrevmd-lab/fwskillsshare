---
name: parsing-fortinet-configs
description: >
  Parse and analyze Fortinet FortiGate / FortiOS firewall configurations. Use this skill
  when the user pastes, uploads, or references a FortiGate config — the "config/edit/set/next/end"
  block format from "show full-configuration" or backup exports. Trigger on keywords: FortiGate,
  FortiOS, Fortinet, VDOM, "config firewall policy", "config firewall address",
  "config firewall service custom", "config system interface", "edit", "set srcintf",
  "set dstintf", "set srcaddr", "set dstaddr", "set action accept", "set utm-status enable",
  "set av-profile", "set webfilter-profile", "set ips-sensor". Also trigger when the user asks
  to convert, audit, summarize, or explain a FortiGate config.
version: 1.0.0
---

# Parsing Fortinet FortiGate Configurations

You are an expert at parsing Fortinet FortiGate / FortiOS firewall configurations. When given
raw FortiOS config text, extract all components into a structured intermediate
format.

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
- `config <section>` opens a section
- `edit <name>` or `edit <id>` creates/selects an entry (name may be quoted)
- `set <key> <value>` sets a property (value may contain spaces if quoted)
- `next` closes the current `edit` entry
- `end` closes the current `config` section
- Values with spaces are quoted: `set comment "Allow web traffic"`
- Multi-value fields use space-separated values: `set srcaddr "addr1" "addr2"`

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

**Critical: Interface-as-Zone Merging**
FortiGate can use interface names directly as zones in policies (via `srcintf`/`dstintf`).
If a policy references an interface name not in any zone, treat that interface as its own zone.
Merge zones and interfaces: create a zone entry for each interface used as a zone.

### 2. Address Objects
Path: `config firewall address` → `edit <name>`

Types — detect from `set type` or infer from fields:
- `set type ipmask` + `set subnet <ip> <mask>` → type: "subnet" (convert mask to CIDR)
- `set type iprange` + `set start-ip` / `set end-ip` → type: "range", value: "start-end"
- `set type fqdn` + `set fqdn <domain>` → type: "fqdn"
- `set type geography` + `set country <code>` → type: "geo" (warn: limited cross-platform support)
- `set type wildcard` + `set wildcard <ip> <mask>` → type: "wildcard" (warn)
- `set type wildcard-fqdn` + `set wildcard-fqdn <pattern>` → type: "wildcard-fqdn" (warn)

Also extract: `set comment`, `set associated-interface`.
Convert subnet mask notation (`255.255.255.0`) to CIDR (`/24`).
Auto-detect IP version.

### 3. Address Groups
Path: `config firewall addrgrp` → `edit <name>`
Extract: `set member <list>` (space-separated quoted names)

### 4. Service Objects
Path: `config firewall service custom` → `edit <name>`
Extract from:
- `set protocol TCP/UDP/SCTP` + `set tcp-portrange <range>` / `set udp-portrange <range>`
- `set protocol ICMP` + `set icmptype` / `set icmpcode`
- Port range format: `80` or `80-443` or `80:1024-65535` (dst:src)

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
- **log_start** — `set logtraffic-start enable`
- **log_end** — inferred from `set logtraffic all` or `set logtraffic utm`
- **disabled** — `set status disable`
- **description** — `set comments <value>`
- **schedule** — `set schedule <value>`
- **source_users** — `set groups <list>` (FSSO groups)
- **nat** — `set nat enable` (source NAT toggle on the policy)

**UTM / Security Profiles** — when `set utm-status enable`:
- `set av-profile <name>` → antivirus
- `set webfilter-profile <name>` → URL filtering
- `set ips-sensor <name>` → IPS/IDP
- `set application-list <name>` → application control
- `set ssl-ssh-profile <name>` → SSL inspection
- `set dnsfilter-profile <name>` → DNS filtering
- `set emailfilter-profile <name>` → email filtering
- `set dlp-profile <name>` → DLP
- `set profile-group <name>` → profile group (overrides individual profiles)

### 7. NAT Rules
**Source NAT (IP Pools):** `config firewall ippool` → `edit <name>`
  Extract: `set startip`, `set endip`, `set type` (overload, one-to-one, fixed-port-range)

**Central SNAT:** `config firewall central-snat-map` → `edit <id>`
  Extract: src/dst interfaces, src/dst addresses, NAT IP pool

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

### 9. Security Profile Definitions
Parse full profile objects for reference:
- `config antivirus profile`
- `config webfilter profile`
- `config ips sensor`
- `config application list`
- `config firewall ssl-ssh-profile`

### 10. Routing
- **Static routes:** `config router static` → `edit <id>` with `set dst`, `set gateway`, `set device`
- **BGP:** `config router bgp` with `set as`, `set router-id`, neighbor entries
- **OSPF:** `config router ospf` with `set router-id`, area entries, network entries
- **OSPFv3:** `config router ospf6`
- **Policy routing:** `config router policy` → PBF rules

### 11. Infrastructure
- **HA:** `config system ha` — `set mode` (a-p/a-a), `set group-id`, `set priority`,
  `set hbdev`, `set monitor`
- **Screen/DoS:** `config firewall DoS-policy` + IPS sensor definitions
- **Syslog:** `config log syslogd setting`
- **DHCP:** `config system dhcp server`

### 12. Multi-VDOM
Detect VDOM context: `config vdom` / `edit <vdom-name>`.
Each interface has `set vdom <name>`. Parse per-VDOM, tag items, merge.

### 13. Implicit Rules
After parsing all explicit policies, append:
- Per-zone **Intra-zone** rules (check zone config: `set intrazone allow|deny`)
  - Default is deny unless explicitly set to allow
- **Implicit: Default Deny** — action: "deny", all any, `_implicit: true`

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.

## Analysis Checks

After extraction, report:
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
