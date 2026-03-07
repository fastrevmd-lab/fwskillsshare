---
name: parsing-cisco-configs
description: >
  Parse and analyze Cisco ASA and FTD firewall configurations. Use this skill when the user
  pastes, uploads, or references a Cisco ASA or FTD config — line-oriented format with
  indented sub-commands from "show running-config". Trigger on keywords: ASA, FTD, Cisco,
  "access-list", "access-group", "object network", "object-group", "object service",
  "nameif", "security-level", "nat (", "object network", "subnet", "host", "range",
  "interface GigabitEthernet", "interface Management", "failover", "threat-detection".
  Also trigger when the user asks to convert, audit, summarize, or explain a Cisco ASA/FTD config.
version: 1.0.0
---

# Parsing Cisco ASA / FTD Configurations

You are an expert at parsing Cisco ASA and FTD firewall configurations. When given raw
ASA/FTD config text, extract all components into a structured intermediate
format.

## Input Format

Cisco ASA configs are line-oriented with indented sub-commands:
```
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address 203.0.113.1 255.255.255.0
!
object network web-server
 host 10.0.1.10
 nat (inside,outside) static 203.0.113.10
!
access-list outside_in extended permit tcp any object web-server eq 443
access-group outside_in in interface outside
```

Key syntax rules:
- Top-level commands start at column 0
- Sub-commands are indented with one space
- `!` separates logical sections
- Named interfaces use `nameif` (e.g., `inside`, `outside`, `dmz`)
- `security-level` (0-100) determines trust level

### Building Command Blocks

Group indented lines under their parent top-level command:
1. Lines starting with no indentation → new block
2. Indented lines → children of the current block
3. `!` lines → section separator (ignore)
4. Result: array of `{ command: "<top-level>", children: ["<sub1>", "<sub2>", ...] }`

## Extraction Pipeline

### 1. Interfaces
Source: `interface <hardware-id>` blocks
Extract from sub-commands:
- `nameif <name>` — the logical name used everywhere else
- `security-level <0-100>` — trust level
- `ip address <ip> <mask>` — IP and subnet mask
- `vlan <id>` — VLAN assignment
- `shutdown` — interface is administratively down
- `description <text>`
- `bridge-group <id>` — transparent mode bridge group membership

### 2. Zones (Derived from Interfaces)
ASA doesn't have explicit zones. Derive them from `nameif` values:
- Each unique `nameif` becomes a zone
- Zone trust level comes from `security-level`
- Associate the interface with its zone

### 3. Network Objects
Source: `object network <name>` blocks
Types from sub-commands:
- `host <ip>` → type: "host", value: ip + "/32"
- `subnet <ip> <mask>` → type: "subnet", value: ip + "/cidr" (convert mask to CIDR)
- `range <start> <end>` → type: "range", value: "start-end"
- `fqdn v4 <domain>` or `fqdn v6 <domain>` → type: "fqdn"

Also extract: `description`, inline `nat` statement (for object/auto NAT).

### 4. Network Object Groups
Source: `object-group network <name>` blocks
Members from sub-commands:
- `network-object host <ip>` → inline host
- `network-object <ip> <mask>` → inline subnet
- `network-object object <name>` → reference to named object
- `group-object <name>` → nested group reference

### 5. Service Objects
Source: `object service <name>` blocks
Parse: `service <protocol> [source <op> <port>] [destination <op> <port>]`
Operators: `eq`, `range`, `gt`, `lt`, `neq`

### 6. Service Object Groups
Source: `object-group service <name> [<protocol>]` blocks
Members:
- `port-object eq <port>` / `port-object range <start> <end>`
- `service-object <protocol> [destination <op> <port>]`
- `service-object object <name>`
- `group-object <name>`

### 7. Protocol Object Groups
Source: `object-group protocol <name>` blocks
Members: `protocol-object <protocol-name-or-number>`

### 8. Access Lists (Security Policies)
Source: `access-list <name> extended <action> <protocol> <src> <dst> [<svc>]`

**ACL Line Parsing — Token by Token:**

Format: `access-list <id> extended <permit|deny> <protocol> <source> <dest> [<service>] [log] [time-range <name>]`

**Protocol field:**
- `ip` — any IP protocol
- `tcp`, `udp`, `icmp`, `sctp` — specific protocols
- `object-group <name>` — protocol group reference

**Address parsing** (for both source and destination):
- `any` / `any4` / `any6` → "any"
- `host <ip>` → specific host
- `object <name>` → named network object
- `object-group <name>` → network object group
- `<network> <mask>` → network/subnet-mask pair (convert standard subnet mask to CIDR)
- `interface <nameif>` → the IP of that interface

**Service/port parsing** (after destination address, for TCP/UDP):
- `eq <port>` → single port (use name or number)
- `range <start> <end>` → port range
- `gt <port>` → greater than
- `lt <port>` → less than
- `neq <port>` → not equal (warn: limited cross-platform support)
- `object-group <name>` → service group reference

**ICMP parsing** (for ICMP protocol):
- Optional ICMP type after destination: `icmp <src> <dst> <type> [<code>]`

**Flags:**
- `log [<level>] [interval <secs>]` → enable logging
- `time-range <name>` → schedule reference
- `inactive` → disabled

### 9. Access Groups (Binding ACLs to Interfaces/Zones)
Source: `access-group <acl-name> <in|out> interface <nameif>`
Also: `access-group <acl-name> global` (applies to all interfaces)

**Critical: Deriving Zone-Based Policies from ACLs**

ACLs alone don't have zone info. Combine with access-groups:
- `access-group outside_in in interface outside` → policies from this ACL have:
  - `src_zones: ["outside"]` (traffic enters on this interface, so it is the source zone)
  - `dst_zones:` must be inferred (often "any" unless the ACL destination addresses map to a zone)
- For `in` direction: traffic is entering the named interface, so that interface is the **source zone**
- For `out` direction: traffic is leaving the named interface
- For `global`: applies regardless of interface

Build security policies by iterating ACL entries and attaching zone information from access-groups.

### 10. NAT Rules

**Object NAT (Auto NAT):**
Found inside `object network` blocks as `nat (<real-iface>,<mapped-iface>) <type> <mapped-addr>`
- `nat (inside,outside) static 203.0.113.10` → static 1:1 NAT
- `nat (inside,outside) dynamic interface` → dynamic PAT to interface
- `nat (inside,outside) dynamic pat-pool <name>` → dynamic PAT to pool

**Twice NAT (Manual NAT):**
Top-level: `nat (<real-iface>,<mapped-iface>) [<section>] source <type> <real-src> <mapped-src> [destination <type> <real-dst> <mapped-dst>] [service <real-svc> <mapped-svc>]`

Parse `source static|dynamic` and optional `destination static` components.
Section numbers (1, 2, after-auto) determine NAT rule ordering.

### 11. Time Ranges (Schedules)
Source: `time-range <name>` blocks
Sub-commands:
- `absolute start <time> <date> end <time> <date>`
- `periodic <days> <start-time> to <end-time>`

### 12. Routing
- **Static routes:** `route <nameif> <dest> <mask> <gateway> [<metric>]`
- **BGP:** `router bgp <asn>` block with neighbor, network statements
- **OSPF:** `router ospf <pid>` block with network, area statements

### 13. Infrastructure
- **HA/Failover:** `failover` command presence + `failover lan unit primary|secondary`,
  `failover interface ip`, `failover link`
- **Screen/Threat Detection:** `threat-detection basic-threat` + `threat-detection rate` entries
  Map to screen/IDS profiles
- **VPN:** `crypto ikev1|ikev2` policies, `tunnel-group`, `crypto ipsec` transform-sets
- **Syslog:** `logging host <nameif> <ip>`
- **DHCP:** `dhcpd address <range> <nameif>` / `dhcprelay server <ip> <nameif>`

### 14. Transparent Mode
Detect: `firewall transparent` in config
When in transparent mode:
- Interfaces are in bridge-groups instead of having IPs
- `bridge-group <id>` on interfaces
- BVI interfaces (`interface BVI<id>`) carry the management IP
- Zones derived from nameifs still work the same way

### 15. Implicit Rules
After building all policies from ACLs + access-groups, append:
- **Implicit: Default Deny** — action: "deny", all any, `_implicit: true`

Note: ASA has implicit rules based on security-level (higher-to-lower is permitted by default
without ACLs), but since configs with ACLs override this behavior, the implicit deny is the
standard final rule.

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.

## Analysis Checks

After extraction, report:
1. **Unused objects** — network/service objects not referenced in any ACL
2. **Shadowed ACL entries** — rules that can never match due to earlier entries
3. **Overly permissive** — `permit ip any any` or broad rules
4. **Missing logging** — permit ACL entries without `log` keyword
5. **Inactive entries** — ACL entries with `inactive` flag
6. **Duplicate objects** — same value, different names
7. **Empty groups** — object-groups with no members
8. **Unbound ACLs** — access-lists without matching access-group (never applied)
9. **Wildcard mask conversion** — flag any non-contiguous wildcard masks (rare but problematic)

## Reference Files

- `references/config-format.md` — Cisco ASA config syntax reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, port name mapping, security-level logic
