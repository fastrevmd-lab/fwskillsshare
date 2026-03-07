---
name: parsing-palo-configs
description: >
  Parse and analyze Palo Alto PAN-OS firewall configurations in XML format. Use this skill
  when the user pastes, uploads, or references a PAN-OS or Panorama configuration export.
  Trigger on keywords: PAN-OS, Palo Alto, Panorama, NGFW, "vsys", "security rulebase",
  "address-group", "application-default", "security-profile-group", "device-group",
  "<entry name=", "<member>", "tag-based", "User-ID". Also trigger when the user asks to
  convert, audit, summarize, or explain a Palo Alto config.
version: 1.0.0
---

# Parsing Palo Alto PAN-OS Configurations

You are an expert at parsing Palo Alto PAN-OS firewall configurations in XML format.
When given raw PAN-OS XML config, extract all components into a structured
intermediate format.

## Input Format

PAN-OS configs are XML exports from either:
- **Device-level** — `show running-config` or `running-config.xml` export
- **Panorama** — device-group and template configs pushed to firewalls

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

### 5. Service Groups
Path: `service-group.entry[]`
Extract `<members><member>` list.

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
- **log_start** — `<log-start>yes</log-start>`
- **log_end** — `<log-end>yes</log-end>`
- **disabled** — `<disabled>yes</disabled>`
- **description** — `<description>` text
- **tags** — `<tag><member>` list
- **schedule** — `<schedule>` text
- **source_users** — `<source-user><member>` list (User-ID)
  - Warn if non-"any" values found: User-ID has no direct equivalent on most platforms

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

### 11. Routing & Infrastructure
- **Static routes:** `network.virtual-router.entry[].routing-table.ip.static-route.entry[]`
- **BGP:** `network.virtual-router.entry[].protocol.bgp`
- **OSPF:** `network.virtual-router.entry[].protocol.ospf`
- **HA:** `deviceconfig.high-availability` — mode (active-passive, active-active), group-id, peer-ip
- **Zone protection:** `network.profiles.zone-protection-profile.entry[]`
- **VPN:** `network.ike` and `network.tunnel.ipsec`
- **Syslog:** `shared.log-settings.syslog.entry[]`
- **Virtual wire:** `network.virtual-wire.entry[]`

### 12. Multi-vsys
If multiple vsys entries found:
- Parse each independently
- Tag all policies and objects with `_vsys: "vsys1"` etc.
- Merge into flat arrays
- Re-index `_rule_index` sequentially

### 13. Implicit Rules
After parsing all explicit policies, append per-context:
- **Implicit: Intra-zone Allow** — per zone, action: "allow", `_implicit: true`
  (for each zone, src_zones = dst_zones = [zone_name])
- **Implicit: Interzone Default Deny** — action: "deny", src/dst zones: ["any"], `_implicit: true`

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

## Reference Files

- `references/config-format.md` — PAN-OS XML structure reference
- `references/intermediate-schema.md` — Output schema specification
- `references/parsing-patterns.md` — Edge cases, app mapping, profile resolution
