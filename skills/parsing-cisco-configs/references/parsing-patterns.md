# Cisco ASA Parsing Patterns and Edge Cases

## Building Command Blocks

Parse the config into structured blocks:

```
Input:
  interface GigabitEthernet0/0
   nameif outside
   security-level 0
   ip address 203.0.113.1 255.255.255.0
  !
  object network web-server
   host 10.0.1.10

Output:
  [
    { command: "interface GigabitEthernet0/0",
      children: ["nameif outside", "security-level 0", "ip address 203.0.113.1 255.255.255.0"] },
    { command: "object network web-server",
      children: ["host 10.0.1.10"] }
  ]
```

Rules:
1. Lines with no leading space → new block's `command`
2. Lines with leading space → append to current block's `children`
3. `!` lines → separator (ignore, finalize current block)
4. Empty lines → ignore

## Zone Derivation from Security Levels

ASA doesn't have explicit zones. Derive from interfaces:

| nameif | security-level | Zone Role |
|---|---|---|
| inside | 100 | trust (highest trust) |
| outside | 0 | untrust (lowest trust) |
| dmz | 50 | dmz (intermediate) |
| management | 100 | management |

Each unique `nameif` becomes a zone. The zone name IS the nameif value.

## ACL Token Parsing — State Machine

Parse ACL lines token by token. Order matters:

```
access-list <name> extended <action> <protocol> <src-addr> [<src-port>] <dst-addr> [<dst-port>] [flags]
```

**State transitions:**
1. Read `access-list` → read ACL name
2. Read `extended` → expect action
3. Read `permit`/`deny` → action
4. Read protocol token → protocol (could be `ip`, `tcp`, `udp`, `icmp`, `object-group <name>`)
5. Parse source address (see address parsing rules)
6. If TCP/UDP: optionally parse source port
7. Parse destination address
8. If TCP/UDP: optionally parse destination port
9. If ICMP: optionally parse ICMP type and code
10. Parse trailing flags: `log`, `time-range`, `inactive`

**Key challenge:** Distinguishing port tokens from address tokens.
- If current token is `eq`, `range`, `gt`, `lt`, `neq` → it's a port specification
- If current token is `any`, `host`, `object`, `object-group`, or looks like an IP → it's an address
- Port parsing only applies to TCP and UDP protocols

## Subnet Mask Conversion

ASA uses standard subnet masks (NOT wildcard masks like IOS):

```
10.0.0.0 255.255.0.0  → 10.0.0.0/16  (standard mask)
```

This is different from IOS ACLs which use wildcard masks:
```
10.0.0.0 0.0.255.255  → 10.0.0.0/16  (wildcard mask — NOT used in ASA)
```

Convert standard mask to CIDR by counting consecutive 1-bits.

## Port Name Resolution

ASA accepts named ports. Map to numbers:

| Name | Number | Protocol |
|---|---|---|
| www / http | 80 | tcp |
| https | 443 | tcp |
| ssh | 22 | tcp |
| telnet | 23 | tcp |
| ftp | 21 | tcp |
| ftp-data | 20 | tcp |
| domain | 53 | tcp/udp |
| smtp | 25 | tcp |
| pop3 | 110 | tcp |
| imap4 | 143 | tcp |
| ntp | 123 | udp |
| snmp | 161 | udp |
| snmptrap | 162 | udp |
| syslog | 514 | udp |
| ldap | 389 | tcp |
| ldaps | 636 | tcp |
| sqlnet | 1521 | tcp |
| h323 | 1720 | tcp |
| sip | 5060 | tcp/udp |
| rtsp | 554 | tcp |

## Combining ACLs with Access-Groups

ACLs define the rules, access-groups bind them to interfaces:

```
access-list outside_in extended permit tcp any object web-server eq 443
access-group outside_in in interface outside
```

**Zone assignment algorithm:**

For `access-group <acl> in interface <nameif>`:
- The `nameif` interface is where traffic enters
- For `in` direction: this interface is the **source zone** for matched traffic
- Destination zone: typically the opposite interface (derived from destination addresses)
  - If destination is a known object in a specific zone's subnet → use that zone
  - Otherwise → set as "any" or attempt inference from routing

For `access-group <acl> global`:
- Applies to all interfaces
- Source and destination zones should be "any"

**Simplified practical approach:**
- `in interface X` → source_zone = X, destination_zone = inferred or "any"
- This is a simplification — real ASA processes traffic differently than zone-based firewalls

## Object NAT Extraction

Object NAT is defined inside `object network` blocks:

```
object network web-server
 host 10.0.1.10
 nat (inside,outside) static 203.0.113.10
```

Parse the `nat` line:
1. Extract real interface and mapped interface from `(<real>,<mapped>)`
2. Determine NAT type: `static`, `dynamic`
3. Extract translated address: IP, `interface`, or `pat-pool <name>`

Map to NAT rule:
- type: depends on `static` vs `dynamic`
- src_zones: [real-interface-nameif]
- dst_zones: [mapped-interface-nameif]
- src_addresses or dst_addresses: the object's address
- translated_src or translated_dst: the mapped address

## Twice NAT Parsing

```
nat (inside,outside) source dynamic internal-net interface
nat (inside,outside) 1 source static web-server pub-web-server service tcp-80 tcp-80
```

Token parsing:
1. `nat` keyword
2. `(<real-iface>,<mapped-iface>)` — interfaces
3. Optional `after-auto` keyword — places the rule in Section 3 (after object/auto NAT)
4. Optional line number (`1`, `2`, ...) — the rule's position within its manual NAT section, NOT a section number
5. `source <static|dynamic> <real-src> <mapped-src>`
6. Optional: `destination <static> <real-dst> <mapped-dst>`
7. Optional: `service <real-svc> <mapped-svc>`

Derive the NAT section from rule form, never from the numeric token:
- Manual/twice NAT without `after-auto` → Section 1
- Object/auto NAT (`nat` inside `object network` blocks) → Section 2
- Manual/twice NAT with `after-auto` → Section 3

## Threat Detection to Screen Mapping

```
threat-detection basic-threat
threat-detection rate dos-drop rate-interval 600 average-rate 100 burst-rate 400
threat-detection rate syn-attack rate-interval 600 average-rate 100 burst-rate 200
```

Map to screen config:
- `dos-drop` → generic DoS detection
- `syn-attack` → tcp.syn-flood
- `scanning-threat` → IP sweep/port scan detection
- `inspect-drop` → inspection engine drop rate

## Time Range Parsing

```
time-range business-hours
 periodic weekdays 08:00 to 18:00
!
time-range maintenance
 absolute start 22:00 01 January 2024 end 06:00 02 January 2024
```

Map to schedule objects:
- `periodic <days> <start> to <end>` → type: "recurring"
- `absolute start <time> <date> end <time> <date>` → type: "onetime"

Day keywords: `weekdays`, `weekend`, `daily`, `Monday`, `Tuesday`, etc.

## Common Warnings

| Condition | Severity | Message |
|---|---|---|
| `neq` port operator | warning | "Not-equal port operator has limited cross-platform support" |
| Non-contiguous wildcard mask | warning | "Non-contiguous masks not supported — review manually" |
| `object-group protocol` in ACL | info | "Protocol group reference in ACL" |
| ACL without access-group | warning | "ACL is not bound to any interface (never applied)" |
| `inactive` ACL entry | info | "ACL entry is inactive" |
| Transparent mode | info | "Firewall in transparent (bridge) mode" |
| Failover detected | info | "HA failover configuration present" |
| Object NAT + Twice NAT | info | "Mixed NAT types — review ordering (section 1 manual → section 2 auto → section 3 after-auto)" |
| `interface` as NAT target | info | "NAT translates to interface IP (PAT)" |
| Security-level based permit | warning | "Implicit high-to-low permit may exist without ACLs" |
