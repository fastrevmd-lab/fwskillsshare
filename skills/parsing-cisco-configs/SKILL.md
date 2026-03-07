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
version: 1.1.0
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
- `ip address dhcp` — DHCP client mode (no static IP)
- `ipv6 address <ipv6/prefix> [eui-64]` — IPv6 address
- `mtu <value>` — MTU setting
- `management-only` — management-only interface flag
- `channel-group <N>` — LAG/EtherChannel membership (Port-channel parent)
- `tunnel source interface <name>` — VPN tunnel source
- `tunnel destination <ip>` — VPN tunnel destination
- `tunnel protection ipsec profile <name>` — IPsec profile binding

Interface types: detect `Port-channel*` as lag, `Tunnel*` as tunnel, `Loopback*` as loopback, `Management*` as management. Sub-interfaces contain `.` in name (e.g., `GigabitEthernet0/0.100`) — derive parent from name before the dot.

### 2. Zones (Derived from Interfaces)
ASA doesn't have explicit zones. Derive them from `nameif` values:
- Each unique `nameif` becomes a zone
- Zone trust level comes from `security-level`
- Associate the interface with its zone

### 3. Network Objects
Source: `object network <name>` blocks
Types from sub-commands:
- `host <ip>` → type: "host", value: ip + "/32" (or "/128" for IPv6)
- `subnet <ip> <mask>` → type: "subnet", value: ip + "/cidr" (convert mask to CIDR)
- `range <start> <end>` → type: "range", value: "start-end"
- `fqdn v4 <domain>` or `fqdn v6 <domain>` → type: "fqdn"

Note: bare `fqdn <domain>` (without v4/v6 qualifier) is also valid.

- `subnet <ipv6-prefix>` → for IPv6 subnets the value is already in CIDR form, no mask conversion needed.

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

**ACL Remarks:**
`access-list <name> remark <text>` — attach as `comment` to the NEXT ACL entry.

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

**Source port parsing** (after source address, for TCP/UDP — optional):
- `eq <port>` / `range <start> <end>` → source port match (less common)

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
- **Static routes (IPv4):** `route <nameif> <dest> <mask> <gateway> [<metric>]`
- **Static routes (IPv6):** `ipv6 route <nameif> <dest/prefix> <gateway> [<metric>]`
- **BGP:** `router bgp <asn>` block — extract:
  - `router-id`, `address-family ipv4 unicast`
  - Per-neighbor: `remote-as`, `description`, `update-source`, `password`, `timers` (keepalive/hold), `next-hop-self`, `soft-reconfiguration`, `route-reflector-client`, `shutdown`
  - `network` statements (convert mask to CIDR)
  - `redistribute` (connected/static)
  - Note: route-map and prefix-list references are not converted (warn)
- **OSPF:** `router ospf <pid>` block — extract:
  - `router-id`, `auto-cost reference-bandwidth`
  - `network <ip> <wildcard> area <id>` — match interfaces to areas via wildcard mask comparison
  - Area types: stub, nssa, with `no-summary`; area default-cost; area authentication
  - `passive-interface default` + `no passive-interface <nameif>` exceptions
  - `redistribute` (connected/static with metric/metric-type)
  - Interface-level: `ip ospf cost`, `ip ospf priority`, `ip ospf hello-interval`, `ip ospf dead-interval`, `ip ospf network point-to-point`, `ip ospf authentication message-digest` + key
  - Normalize area IDs to dotted-decimal (0 → 0.0.0.0)
- **OSPFv3:** `router ospfv3` block with `address-family ipv6 unicast` — similar structure to OSPFv2

### 13. Infrastructure
- **Hostname:** `hostname <name>` and `domain-name <domain>` → system metadata
- **Version:** `asa version <X.Y>` or `firepower version <X.Y>` → metadata.source_version
- **HA/Failover:** `failover` presence + `failover lan unit primary|secondary` (capture unit role),
  `failover interface ip`, `failover link`
- **Screen/Threat Detection:** `threat-detection basic-threat` + `threat-detection rate` entries
- **DNS:** `dns server-group DefaultDNS` block → extract `name-server` entries
- **NTP:** `ntp server <ip> [prefer]`
- **Management Access:** `ssh|http|telnet <source> <mask> <nameif>` — track which management protocols are accessible per zone
- **Admin Users:** `username <name> password ... privilege <level>` — map privilege 15=super-admin, 1-14=operator, 0=read-only. `username <name> attributes` block with `ssh authentication publickey <key>` for SSH keys.
- **VPN/IPsec:**
  - `crypto ikev2 policy <seq>` blocks: encryption, integrity, DH group, lifetime
  - `crypto ikev1 policy <seq>` blocks: authentication, encryption, hash, DH group, lifetime
  - `crypto ipsec ikev2 ipsec-proposal <name>`: protocol esp encryption/integrity
  - `crypto ipsec ikev1 transform-set <name> <enc> <integ>`
  - `crypto ipsec profile <name>`: link proposals to PFS groups
  - `tunnel-group <ip> ipsec-attributes`: PSK, certificates, authentication method
  - VTI assembly: match Tunnel interfaces to IPsec profiles, resolve tunnel source/destination, collect routes through tunnel nameifs
  - Canonicalize algorithm names (e.g., aes-256 → aes-256, sha → sha1)
  - Flag weak algorithms (DES/3DES, MD5, DH group ≤ 5)
- **Syslog:** `logging host <nameif> <ip>`
- **DHCP Server:** `dhcpd address <start>-<end> <nameif>` (pool range),
  `dhcpd dns <ip1> [<ip2>]`, `dhcpd domain <domain>`, `dhcpd lease <seconds>`,
  `dhcpd enable <nameif>` (commit trigger — binds staged options to interface).
  Derive network CIDR from the interface IP.
- **DHCP Relay:** `dhcprelay server <ip> <iface>` + `dhcprelay enable <nameif>`

### 14. Application Mapping (L7 → Canonical)

ASA/FTD is a port-based platform — it does not have native L7 application awareness in ACLs.
However, when converting FROM ASA to an app-aware platform (PAN-OS, FortiGate), or comparing
configs, the parser should attempt to resolve well-known port/protocol combinations to canonical
application names.

**Resolution from port-based services:**
For each service object or inline port match, check if the protocol+port maps to a known application:

| Protocol | Port(s) | Canonical App | Category |
|----------|---------|---------------|----------|
| TCP | 443 | `https` | web |
| TCP | 80 | `http` | web |
| TCP | 22 | `ssh` | remote-access |
| TCP | 3389 | `rdp` | remote-access |
| UDP | 53 | `dns` | network-mgmt |
| TCP | 25 | `smtp` | email |
| TCP | 465 | `smtps` | email |
| TCP | 993 | `imaps` | email |
| TCP | 143 | `imap` | email |
| UDP | 123 | `ntp` | network-mgmt |
| UDP | 161 | `snmp` | network-mgmt |
| UDP | 162 | `snmp-trap` | network-mgmt |
| TCP | 21 | `ftp` | file-transfer |
| TCP | 23 | `telnet` | remote-access |
| TCP | 389 | `ldap` | auth |
| TCP | 636 | `ldaps` | auth |
| UDP | 69 | `tftp` | file-transfer |
| TCP | 1433 | `mssql` | database |
| TCP | 3306 | `mysql` | database |
| TCP | 5432 | `postgresql` | database |
| TCP | 445 | `smb` | file-transfer |
| UDP | 500 | `ipsec` | tunnel |
| UDP | 4500 | `ipsec-nat-t` | tunnel |
| TCP | 5060 | `sip` | voip |
| UDP | 5060 | `sip` | voip |

**ASA named port keywords:** Map ASA port names to numbers before resolving:
`www`→80, `https`→443, `ssh`→22, `telnet`→23, `ftp`→21, `ftp-data`→20, `smtp`→25,
`pop3`→110, `imap4`→143, `domain`→53, `ntp`→123, `snmp`→161, `snmptrap`→162,
`tftp`→69, `syslog`→514, `tacacs`→49, `radius`→1812, `ldap`→389, `ldaps`→636,
`sqlnet`→1521, `h323`→1720, `sip`→5060, `rtsp`→554, `kerberos`→88, `msrpc`→135,
`netbios-ssn`→139, `microsoft-ds`→445, `bgp`→179, `lpd`→515, `pptp`→1723

**On policy output:** When a service match resolves to a known application, populate the policy's
`apps` array with `{ vendor_name: "tcp/443", canonical: "https", confidence: 1.0, category: "web" }`.
The `services` array still keeps the port-based match. This enables downstream converters to use
the app-aware rule on platforms that support it.

**Unresolvable services:** Complex port ranges, non-standard ports, or protocol groups that don't
map to a single known application → keep as port-based services only, no `apps` entry.

### 15. Application Groups

ASA does not have application groups. However, when converting FROM an app-aware platform,
object-group service entries that resolve entirely to known applications should be flagged
as potential `application_groups` in the IR for downstream use.

### 16. Anonymous Objects
When inline addresses/services appear in ACLs or object groups without a named reference (e.g., `host 10.0.1.10` directly in an ACL line), create anonymous objects with auto-generated names (e.g., `anon-1-host`, `anon-2-net`). This ensures every IR reference points to a named object.

### 17. Residual Config Capture
Capture unrecognized top-level commands verbatim. Categorize into: VPN/IPsec, AAA, QoS, PKI/Certificates, IPv6, Other. Store in `residual_raw` for manual review.

### 18. Transparent Mode
Detect: `firewall transparent` in config
When in transparent mode:
- Interfaces are in bridge-groups instead of having IPs
- `bridge-group <id>` on interfaces
- BVI interfaces (`interface BVI<id>`) carry the management IP
- Zones derived from nameifs still work the same way

### 19. Implicit Rules
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
9. **Subnet mask validation** — flag any non-standard subnet masks

## Reference Files

- `references/config-format.md` — Cisco ASA config syntax reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, port name mapping, security-level logic
