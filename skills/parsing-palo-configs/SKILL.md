---
name: parsing-palo-configs
description: >
  Parse and analyze Palo Alto PAN-OS firewall configurations in XML format. Use this skill
  when the user pastes, uploads, or references a PAN-OS or Panorama configuration export.
  Trigger on keywords: PAN-OS, Palo Alto, Panorama, NGFW, "vsys", "security rulebase",
  "address-group", "application-default", "security-profile-group", "device-group",
  "<entry name=", "<member>", "tag-based", "User-ID". Also trigger when the user asks to
  convert, audit, summarize, or explain a Palo Alto config.
version: 1.1.0
---

# Parsing Palo Alto PAN-OS Configurations

You are an expert at parsing Palo Alto PAN-OS firewall configurations in XML format.
When given raw PAN-OS XML config, extract all components into a structured
intermediate format.

## Input Format

PAN-OS configs come in two formats. Auto-detect which one:

1. **XML format** — `show running-config`, `running-config.xml` export, or Panorama config
2. **Set format** — `show config flat` output with `set <path> <value>` lines

**Detection:** Check if input starts with `<` or contains XML tags → XML mode. Lines starting with `set ` → set-format mode.

**Set-format tokenization:** Handle double-quoted strings (preserve as single tokens), `[ ]` bracket list notation (expand to multiple values), and inline `#` comments. Example: `set deviceconfig system hostname fw1` maps to XML path `deviceconfig.system.hostname = fw1`.

### XML Structure Conventions

PAN-OS XML uses two critical element patterns:

1. **`<entry name="...">`** — Named objects. Always treat as arrays even when single.
   ```xml
   <address>
     <entry name="web-server">
       <ip-netmask>10.0.1.10/32</ip-netmask>
     </entry>
   </address>
   ```

2. **`<member>`** — List items in groups, rules, etc. Always treat as arrays.
   ```xml
   <source>
     <member>any</member>
   </source>
   ```

### Locating Config Sections

**Device config path:** `config.devices.entry.vsys.entry[].`
**Panorama shared path:** `config.shared.`
**Direct vsys path:** `config.vsys.entry[].` (older formats)

Use `findVsysEntries()` logic: try each path, collect all vsys entries.

## Extraction Pipeline

### 1. Zones
Path: `zone.entry[]`
Extract: zone name (from `@name` attribute), zone type (from child element: `network.layer3`,
`network.layer2`, `network.virtual-wire`, `network.tap`), interfaces list.

### 2. Address Objects
Path: `address.entry[]`
Types — detect by which child element exists:
- `<ip-netmask>` → type: "subnet" (or "host" if /32)
- `<ip-range>` → type: "range"
- `<fqdn>` → type: "fqdn"
- `<ip-wildcard>` → type: "wildcard" (warn: limited SRX support)
- `<ipv6-netmask>` → type: "subnet" (or "host" if /128)
- `<ipv6-range>` → type: "range"

Also extract: `<description>`, `<tag><member>` tags.
Auto-detect IP version from value.

### 3. Address Groups
Path: `address-group.entry[]`
Two kinds:
- **Static** — `<static><member>` lists member names
- **Dynamic** — `<dynamic><filter>` has tag-based filter expression
  - Warn: dynamic address groups have no direct equivalent in most platforms

### 4. Service Objects
Path: `service.entry[]`
Extract from `<protocol>`:
- `<tcp><port>` / `<tcp><source-port>` → protocol: "tcp"
- `<udp><port>` / `<udp><source-port>` → protocol: "udp"
- `<sctp><port>` → protocol: "sctp" (warn: limited support)
- `<icmp>` → protocol: "icmp" (extract type/code if present)
- `<icmp6>` → protocol: "icmpv6"
Also extract `<description>` from service objects.

### 5. Service Groups
Path: `service-group.entry[]`
Extract `<members><member>` list.
Also extract `<description>` from service groups.

### 6. Applications (Custom)
Path: `application.entry[]`
Extract: name, description, default port from `<default><port><member>`.
Port format: `tcp/80,443` or `udp/53` — parse protocol and port range.

### 7. Application Groups
Path: `application-group.entry[]`
Extract `<members><member>` list.

### 8. Security Policies
Path: `rulebase.security.rules.entry[]` or `pre-rulebase/post-rulebase.security.rules.entry[]`

For each rule extract:
- **name** — from `@name`
- **src_zones** — `<from><member>` list
- **dst_zones** — `<to><member>` list
- **src_addresses** — `<source><member>` list
- **dst_addresses** — `<destination><member>` list
- **negate_source** — `<negate-source>yes</negate-source>` → true
- **negate_destination** — `<negate-destination>yes</negate-destination>` → true
- **applications** — `<application><member>` list
- **services** — `<service><member>` list (often "application-default")
- **action** — `<action>` child element name: allow, deny, drop, reset-client, reset-server, reset-both
  Map `drop` to `deny` with info warning (silent deny → deny since some targets don't distinguish)
- **log_start** — `<log-start>yes</log-start>`
- **log_end** — `<log-end>yes</log-end>`
- **disabled** — `<disabled>yes</disabled>`
- **description** — `<description>` text
- **tags** — `<tag><member>` list
- **schedule** — `<schedule>` text
- **source_users** — `<source-user><member>` list (User-ID)
  - Warn if non-"any" values found: User-ID has no direct equivalent on most platforms
- **url_categories** — `<category><member>` list

**Security profiles** — check `<profile-setting>`:
- `<group><member>` → profile_group name, then resolve from profile-group definitions
- `<profiles>` → individual profiles:
  - `<virus><member>` → antivirus
  - `<spyware><member>` → anti-spyware
  - `<vulnerability><member>` → IPS/IDP
  - `<url-filtering><member>` → URL filtering
  - `<file-blocking><member>` → file blocking
  - `<wildfire-analysis><member>` → WildFire
  - `<data-filtering><member>` → DLP

### 9. NAT Rules
Path: `rulebase.nat.rules.entry[]`

For each rule:
- Determine NAT type from `<source-translation>` and/or `<destination-translation>` presence
- **Source NAT:** `<source-translation>` with `<dynamic-ip-and-port>` (interface or translated-address)
  or `<static-ip>` with `<translated-address>`
- **Destination NAT:** `<destination-translation>` with `<translated-address>` and optional `<translated-port>`
- **Both:** has both source and destination translation → type: "source-and-destination"

### 10. Decryption Rules
Path: `rulebase.decryption.rules.entry[]`
Extract: name, zones, addresses, action (decrypt/no-decrypt), SSL type (forward-proxy, inbound-inspection).

### 11. Interfaces
Parse from `network.interface` entries (both XML and set-format):

**Interface types:**
- **Ethernet** (`ethernet1/1`): IP, IPv6, MTU, DHCP client, aggregate-group (LAG parent), description, subinterfaces (units with IP/VLAN tag/IPv6)
- **Aggregate-ethernet** (`ae1`): LAG with layer3 IP, MTU, sub-units
- **Loopback** (`loopback.N`): IP and description
- **VLAN** (`vlan.N`): IP and VLAN tag
- **Tunnel** (`tunnel.N`): IP for VPN binding

Derive interface type from name: `ae*`=lag, `loopback*`=loopback, `tunnel*`=tunnel, `vlan*`=vlan.
Back-populate `lag_members` on aggregate interfaces after parsing all interfaces.
Subinterface zone inheritance: if a subinterface has no zone but its parent does, inherit the parent's zone.

### 12. System Configuration
Path: `deviceconfig.system`
Extract:
- `hostname`, `domain`, `sw-version` (→ metadata.source_version)
- `dns-setting.servers` → primary/secondary DNS
- `ntp-servers` → NTP servers with prefer flag
- Management IP + netmask → synthetic `mgmt` interface with `is_mgmt: true`
- Management services: SSH, HTTPS, HTTP, Telnet — PAN-OS uses `disable-*` flags where `yes` = disabled (invert)

### 13. Admin Users
Path: `mgt-config.users.entry[]`
Extract: username, SSH public key (`ssh-public-key` or older `public-key`), role from permissions (`superuser`→super-admin, `devicereader`→read-only, `deviceadmin`→admin).
Only migrate users with SSH keys; warn about others.

### 14. DHCP Server and Relay
Path: `network.dhcp.interface.entry[]`
Extract per-interface:
- **Server:** enable state, IP pools (start-end), gateway, primary/secondary DNS, domain, lease timeout
- **Relay:** relay server IP addresses
Derive network CIDR from the interface IP for the DHCP scope.

### 15. Routing & Infrastructure
- **Virtual Routers:** `network.virtual-router.entry[]` — extract name and interface list
- **Static routes (IPv4):** `routing-table.ip.static-route.entry[]` with destination, nexthop (IP or discard), interface, metric
- **Static routes (IPv6):** `routing-table.ip6.static-route.entry[]` (note: `ip6` not `ipv6` in XML path)
- Routes through tunnel interfaces are separated and associated with VPN tunnels
- **BGP:** `protocol.bgp` — extract:
  - Local AS, router-ID, enable/disable
  - Peer groups: type (ebgp/ibgp), group-level peer-as
  - Per-peer: address, remote-as (fallback to group AS), description, update-source, password, keepalive/hold timers, next-hop-self, route-reflector-client, enabled
  - Advertise-network entries
  - Redistribution rules
- **OSPF:** `protocol.ospf` — extract:
  - Router-ID, reference-bandwidth
  - Areas: area ID, type (normal/stub/nssa), no-summary, default-cost
  - Area authentication: type (md5), key
  - Interfaces per area: passive, enabled, metric, priority, hello/dead intervals, link-type, per-interface auth
  - Redistribute: source, metric, metric-type
- **OSPFv3:** `protocol.ospfv3` — same structure as OSPFv2
- **HA:** `deviceconfig.high-availability` — enabled flag, mode (active-passive/active-active), group-id
- **VPN/IPsec:**
  - IKE crypto profiles: encryption, integrity, DH groups, lifetime
  - IPsec crypto profiles: ESP encryption/authentication, DH group (PFS), lifetime
  - IKE gateways: version (IKEv1/v2), auth method (PSK or certificate), PSK, local/peer address, local/peer ID, crypto profile reference, local cert + CA profile
  - IPsec tunnels: IKE gateway reference, IPsec crypto profile reference, tunnel interface binding
  - Resolve tunnel IPs, find VR containing tunnel, collect routes through tunnel interfaces
  - Flag weak algorithms (DES/3DES, MD5, DH group ≤ 5)
- **Zone protection:** `network.profiles.zone-protection-profile.entry[]`
- **Syslog:** `shared.log-settings.syslog.entry[]`
- **Virtual wire:** `network.virtual-wire.entry[]`

### 16. Application Resolution
When a policy references an application name:
1. Check if it is actually a service object/group misplaced in the `application` field → promote to service match
2. Check if it is an application group → record in `app_groups`
3. Otherwise resolve through cross-vendor app mapping with confidence scores

### 17. Multi-vsys
If multiple vsys entries found:
- Parse each independently
- Tag all policies and objects with `_vsys: "vsys1"` etc.
- Merge into flat arrays
- Re-index `_rule_index` sequentially

### 18. Implicit Rules
After parsing all explicit policies, append per-context:
- **Implicit: Intra-zone Allow** — per zone, action: "allow", `_implicit: true`
  (for each zone, src_zones = dst_zones = [zone_name])
- **Implicit: Interzone Default Deny** — action: "deny", src/dst zones: ["any"], `_implicit: true`

### 19. Residual Config Capture
Capture unhandled configuration sections. In XML mode, serialize unhandled elements back to XML strings. Categorize into: VPN Tunnels, IKE, IPsec Crypto, QoS, DNS Proxy, Shared Objects, PKI/Certificates, Security Profiles, Custom Applications, Policy-Based Forwarding, Panorama Config, Other. Store in `residual_raw`.

## Output Format

Present results in the **intermediate schema** format documented in `references/intermediate-schema.md`.

## Analysis Checks

After extraction, run these checks and report findings:

1. **Unused objects** — address/service objects not referenced by any policy
2. **Shadowed policies** — rules fully covered by earlier rules
3. **Overly permissive** — rules with any/any or negate patterns covering everything
4. **Missing logging** — permit rules without log-end enabled
5. **Disabled policies** — rules with `<disabled>yes</disabled>`
6. **Duplicate objects** — same value, different names
7. **Empty groups** — groups with no members
8. **Dynamic groups** — flag for manual review (no static equivalent)
9. **User-ID dependencies** — rules relying on source-user for access control
10. **URL category dependencies** — rules using URL categories for access control

## Reference Files

- `references/config-format.md` — PAN-OS XML structure reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, app mapping, profile resolution
