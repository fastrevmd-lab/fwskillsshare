# Claude Code Firewall Config Parsing Skills

A collection of Claude Code skills for parsing, auditing, converting, and analyzing enterprise firewall configurations across four major vendors.

## Skills Included

| Skill | Vendor / Platform | Trigger Keywords |
|-------|-------------------|------------------|
| [parsing-cisco-configs](skills/parsing-cisco-configs/) | Cisco ASA & FTD | `ASA`, `FTD`, `access-list`, `object network`, `nameif` |
| [parsing-fortinet-configs](skills/parsing-fortinet-configs/) | Fortinet FortiGate / FortiOS | `FortiGate`, `FortiOS`, `config firewall policy`, `set srcintf` |
| [parsing-palo-configs](skills/parsing-palo-configs/) | Palo Alto PAN-OS & Panorama | `PAN-OS`, `Palo Alto`, `Panorama`, `vsys`, `<entry name=` |
| [parsing-srx-configs](skills/parsing-srx-configs/) | Juniper SRX / Junos | `SRX`, `Junos`, `Juniper`, `set security`, `from-zone` |

All skills parse vendor-specific configs into a **common vendor-neutral intermediate JSON schema**, enabling cross-vendor comparison, conversion, and unified auditing.

## Installation

### Quick Install (all skills)

Copy the skill directories into your Claude Code skills folder:

```bash
# Clone the repo
git clone git@github.com:fastrevmd-lab/claudeskillsshare.git

# Copy all skills into your Claude Code skills directory
cp -r claudeskillsshare/skills/parsing-* ~/.claude/skills/
```

### Install a single skill

```bash
# Example: install only the Cisco ASA skill
cp -r claudeskillsshare/skills/parsing-cisco-configs ~/.claude/skills/
```

### Verify installation

After copying, your `~/.claude/skills/` directory should look like:

```
~/.claude/skills/
├── parsing-cisco-configs/
│   ├── SKILL.md
│   ├── references/
│   │   ├── config-format.md
│   │   ├── intermediate-schema.md
│   │   └── parsing-patterns.md
│   └── examples/
│       └── sample-parse.md
├── parsing-fortinet-configs/
│   └── (same structure)
├── parsing-palo-configs/
│   └── (same structure)
└── parsing-srx-configs/
    └── (same structure)
```

Restart Claude Code after installing. The skills will auto-trigger when they detect vendor-specific keywords in your messages or pasted configs.

## Usage

### Auto-trigger

Just paste a firewall config or mention a vendor by name — Claude will automatically load the appropriate skill.

### Manual invocation

Use slash commands to explicitly invoke a skill:

```
/parsing-cisco-configs
/parsing-fortinet-configs
/parsing-palo-configs
/parsing-srx-configs
```

### What you can do

- **Parse** — Extract all objects, policies, NAT rules, and routes into structured JSON
- **Audit** — Find unused objects, shadowed rules, overly permissive policies, missing logging
- **Convert** — Transform configs between vendors (e.g., SRX to PAN-OS)
- **Compare** — Diff two configs side-by-side
- **Summarize** — Get a high-level overview of zones, policy counts, and security profiles

### Examples

```
# Parse and audit
"Here's my ASA config, parse it and show me security issues:"
[paste running-config]

# Convert between vendors
"Convert this SRX config to Palo Alto format"
[paste SRX config]

# Summarize
"Summarize this FortiGate config — how many policies, what zones, any UTM profiles?"
[paste config]

# Read from file
"Read /path/to/running-config.txt and audit it"
```

## Tips

- Paste the **full config** — partial configs may produce unresolved reference warnings
- Use the appropriate show command output for each vendor:
  - **Cisco ASA**: `show running-config`
  - **FortiGate**: `show full-configuration`
  - **PAN-OS**: XML config export or `show config flat` (set-format)
  - **SRX**: `show configuration | display set` or `show configuration`
- For large configs, save to a file and point Claude at the file path

## Conversion Caveats

- Application-level rules (Palo Alto apps, FortiGate app control) don't map 1:1 to port-based platforms (ASA)
- User-ID / FSSO source-user rules have no equivalent on most platforms
- Dynamic address groups (PAN-OS) have no static equivalent
- Geography/GeoIP objects have limited cross-platform support

## Intermediate Schema

All skills output to a common schema with these sections:

| Section | Contents |
|---------|----------|
| `zones` | Security zones and their interfaces |
| `address_objects` | Hosts, subnets, FQDNs, ranges |
| `address_groups` | Groups of address objects |
| `service_objects` | Service/port definitions |
| `service_groups` | Groups of service objects |
| `security_policies` | Firewall rules (the core output) |
| `nat_rules` | NAT translations (source, dest, static) |
| `static_routes` | Routing table entries |
| `virtual_routers` | Routing namespace / VRF separation |
| `ospf_config` | OSPF areas, interfaces, redistribution |
| `bgp_config` | BGP neighbors, networks, redistribution |
| `ha_config` | High availability / failover |
| `vpn_tunnels` | Route-based IPsec VPN with IKE/IPsec detail |
| `interfaces` | Physical/logical interfaces with IPs, IPv6, LAG |
| `admin_users` | Users with roles and SSH keys |
| `system` | Hostname, DNS, NTP, management services |
| `dhcp_config` | DHCP server pools and relay |
| `residual_raw` | Unparsed config sections for manual review |
| `metadata` | Source vendor, version, parse timestamp, warnings |

## Improvements from fatcat/converter

Version 1.1.0 of these skills incorporates parsing improvements identified by analyzing the [fatcat/converter](https://github.com/fatcat/converter) JavaScript parsers. The following areas were significantly enhanced based on fatcat's implementation:

**All Skills:**
- Expanded intermediate schema with `system`, `virtual_routers`, `admin_users`, `vpn_tunnels`, `ospf_config`, `bgp_config`, `dhcp_config`, `residual_raw` definitions
- IPv6 support throughout (addresses, routes, interface IPs, ICMPv6 services)
- Full VPN/IPsec parsing with IKE/IPsec proposal chain resolution and weak algorithm detection
- Detailed OSPF/OSPFv3 parsing (areas, interface-level settings, authentication, redistribution)
- Detailed BGP parsing (per-neighbor attributes, timers, route-reflector, redistribution)
- DHCP server and relay configuration with pool/reservation detail
- System config extraction (hostname, DNS, NTP, management services)
- Admin user parsing with SSH key migration and role mapping
- Interface parsing (types: LAG, loopback, tunnel, VLAN; IPv6, MTU, DHCP client, subinterfaces)
- Residual/unhandled config capture and categorization
- Version detection from config headers

**Cisco ASA (parsing-cisco-configs):**
- ACL remark attachment to next rule as comment
- Anonymous object creation for inline ACL addresses
- Source port parsing in ACLs
- DHCP server commit trigger pattern (`dhcpd enable`)
- Management access protocol tracking per zone
- VTI tunnel interface assembly with IPsec profile resolution

**FortiGate (parsing-fortinet-configs):**
- Wildcard/wildcard-fqdn type conversion (to network/fqdn)
- FortiLink interface filtering
- Allowaccess classification into management services vs routing protocols
- Zone building priority 3 for unzoned interfaces with IPs
- Policy field defaults documentation
- Central SNAT field name variants (`natippool`)
- Tokenizer documentation for quoted multi-value lines
- VPN IPsec phase1/phase2 compound proposal parsing (`aes256-sha256`)

**PAN-OS (parsing-palo-configs):**
- Set-format (`show config flat`) input support with auto-detection
- URL categories on security policies
- Application group vs service object resolution in policy application field
- `drop` → `deny` action mapping with warning
- Management interface construction from deviceconfig
- Subinterface zone backfill from parent
- Service and service-group description extraction

**SRX (parsing-srx-configs):**
- Improved format detection heuristic (stanza-name check vs line counting)
- 6 hierarchical-to-set normalization rules for impedance mismatches
- Zone-attached address book migration to global scope
- `ip-prefix`/`ipv6-prefix` keyword handling
- `reject` → `deny` action mapping fix (was incorrectly mapped to `reset-both`)
- Routing instances / VRF support
- `qualified-next-hop` (floating statics) and `discard` (null routes)
- Full IKE/IPsec object chain resolution
- NAT destination port matching and pool-based translations
- Application-set vs application-group distinction
- MNHA (multi-node HA) detection
- Unit-0 interface name normalization
- Cluster interface (reth/fab) exclusion

## Uninstall

```bash
rm -rf ~/.claude/skills/parsing-cisco-configs
rm -rf ~/.claude/skills/parsing-fortinet-configs
rm -rf ~/.claude/skills/parsing-palo-configs
rm -rf ~/.claude/skills/parsing-srx-configs
```
