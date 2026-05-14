# Claude Code Firewall Config Parsing Skills

A collection of Claude Code / Hermes skills for parsing, auditing, converting, and analyzing enterprise firewall configurations, plus Juniper SRX operational playbooks derived from field/research material.

## Skills Included

| Skill | Vendor / Platform | Trigger Keywords |
|-------|-------------------|------------------|
| [parsing-cisco-configs](skills/parsing-cisco-configs/) | Cisco ASA & FTD | `ASA`, `FTD`, `access-list`, `object network`, `nameif` |
| [parsing-fortinet-configs](skills/parsing-fortinet-configs/) | Fortinet FortiGate / FortiOS | `FortiGate`, `FortiOS`, `config firewall policy`, `set srcintf` |
| [parsing-palo-configs](skills/parsing-palo-configs/) | Palo Alto PAN-OS & Panorama | `PAN-OS`, `Palo Alto`, `Panorama`, `vsys`, `<entry name=` |
| [parsing-srx-configs](skills/parsing-srx-configs/) | Juniper SRX / Junos | `SRX`, `Junos`, `Juniper`, `set security`, `from-zone` |
| [srx-dynamic-ip-feed](skills/srx-dynamic-ip-feed/) | Juniper SRX / Junos dynamic-address feed servers | `dynamic-address`, `feed-server`, `IPFD`, `show security dynamic-address`, `ipfd` |
| [srx-mpls-in-flow](skills/srx-mpls-in-flow/) | Juniper SRX / Junos MPLS L3VPN in flow mode | `MPLS in Flow`, `family mpls mode packet-based`, `inet-vpn`, `vrf-table-label`, `VRF-to-zone` |
| [srx-mnha](skills/srx-mnha/) | Juniper SRX / Junos Multi-Node High Availability | `MNHA`, `Multi-Node High Availability`, `chassis high-availability`, `SRG`, `ICL`, `ICD` |

The four `parsing-*` skills parse vendor-specific configs into a **common vendor-neutral intermediate JSON schema**, enabling cross-vendor comparison, conversion, and unified auditing.

The SRX operational skills are actionable Junos playbooks with commands, design guidance, verification steps, troubleshooting matrices, source attribution, and reference extracts.

## Installation

### Quick Install (all skills)

Copy the skill directories into your Claude Code skills folder:

```bash
# Clone the repo
git clone git@github.com:fastrevmd-lab/claudeskillsshare.git

# Copy all skills into your Claude Code skills directory
cp -r claudeskillsshare/skills/* ~/.claude/skills/
```

### Install a single skill

```bash
# Example: install only the Cisco ASA skill
cp -r claudeskillsshare/skills/parsing-cisco-configs ~/.claude/skills/

# Example: install only the SRX MNHA skill
cp -r claudeskillsshare/skills/srx-mnha ~/.claude/skills/

# Example: install only the SRX MPLS in Flow skill
cp -r claudeskillsshare/skills/srx-mpls-in-flow ~/.claude/skills/
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
├── parsing-srx-configs/
│   └── (same structure)
├── srx-dynamic-ip-feed/
│   ├── SKILL.md
│   └── references/
│       └── source-extract.md
├── srx-mpls-in-flow/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       ├── source-srx-mpls-in-flow-part-1.md
│       └── source-srx-mpls-in-flow-part-2.md
└── srx-mnha/
    ├── SKILL.md
    └── references/
        ├── source-index.md
        ├── source-dhcp-on-mnha-back-to-basics.md
        ├── source-multi-node-high-availability-basics.md
        ├── source-hybrid-mnha-with-ebgp.md
        └── source-srx-from-chassis-cluster-to-mnha.md
```

Restart Claude Code after installing. The skills will auto-trigger when they detect vendor-specific keywords or SRX operational topics in your messages or pasted configs.

### Hermes local install

For Hermes Agent, copy the skill directories into your local Hermes skills tree, usually under `~/.hermes/skills/devops/`:

```bash
mkdir -p ~/.hermes/skills/devops
cp -r claudeskillsshare/skills/parsing-* ~/.hermes/skills/devops/
cp -r claudeskillsshare/skills/srx-dynamic-ip-feed ~/.hermes/skills/devops/
cp -r claudeskillsshare/skills/srx-mpls-in-flow ~/.hermes/skills/devops/
cp -r claudeskillsshare/skills/srx-mnha ~/.hermes/skills/devops/

hermes skills list | grep -E 'parsing-|srx-dynamic-ip-feed|srx-mpls-in-flow|srx-mnha'
```

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
/srx-dynamic-ip-feed
/srx-mpls-in-flow
/srx-mnha
```

### What you can do

- **Parse** — Extract all objects, policies, NAT rules, and routes into structured JSON
- **Audit** — Find unused objects, shadowed rules, overly permissive policies, missing logging
- **Convert** — Transform configs between vendors (e.g., SRX to PAN-OS)
- **Compare** — Diff two configs side-by-side
- **Summarize** — Get a high-level overview of zones, policy counts, and security profiles
- **Operate SRX dynamic feeds** — Configure, validate, and troubleshoot SRX dynamic-address feed servers
- **Design SRX MPLS in flow mode** — Configure SRX MPLS L3VPN while keeping inet/inet6 traffic in stateful flow mode for policy, NAT, and AppID
- **Design SRX MNHA** — Reason about MNHA modes, SRGs, ICL/ICD, eBGP/BFD failover, VIPs, and DHCP caveats

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

# SRX dynamic IP feed server
"Help me configure an SRX dynamic-address feed-server with HTTPS certificate validation and show me the verification commands"

# SRX MPLS in Flow
"Review this SRX MPLS L3VPN config and verify that family mpls is packet-based while inet traffic remains flow-based with VRF-aware policies"

# SRX MNHA design/troubleshooting
"Review this SRX MNHA hybrid eBGP design and tell me what to verify before failover testing"
```

## Tips

- Paste the **full config** — partial configs may produce unresolved reference warnings
- Use the appropriate show command output for each vendor:
  - **Cisco ASA**: `show running-config`
  - **FortiGate**: `show full-configuration`
  - **PAN-OS**: XML config export or `show config flat` (set-format)
  - **SRX**: `show configuration | display set` or `show configuration`
  - **SRX dynamic feeds**: collect `show security dynamic-address summary`, `show security dynamic-address`, and `show log messages | match ipfd`
  - **SRX MPLS in Flow**: collect `show security flow status`, `show route table bgp.l3vpn.0`, `show route table <vrf>.inet.0`, `show ldp neighbor`, `show mpls interface`, `show security flow session extensive`, and `show security policies hit-count`
  - **SRX MNHA**: collect `show chassis high-availability information`, `show chassis high-availability services-redundancy-group <id>`, `show security flow session`, `show bgp summary`, and `show bfd session`
- For large configs, save to a file and point Claude at the file path

## Conversion Caveats

- Application-level rules (Palo Alto apps, FortiGate app control) don't map 1:1 to port-based platforms (ASA)
- User-ID / FSSO source-user rules have no equivalent on most platforms
- Dynamic address groups (PAN-OS) have no static equivalent
- Geography/GeoIP objects have limited cross-platform support

## SRX Operational Skills

### srx-dynamic-ip-feed

`srx-dynamic-ip-feed` is an operational playbook for Juniper SRX dynamic IP objects backed by HTTPS feed servers. It was synthesized from a Juniper Community TechPost and includes source attribution plus the extracted article text under `references/source-extract.md`.

Use it for:

- configuring `security dynamic-address feed-server`
- building `.tgz` bundle archive feeds and mapping `feed-name` paths
- exposing feeds as `security dynamic-address address-name` policy objects
- validating HTTPS server certificates with SRX PKI / SSL initiation profiles
- HTTP basic authentication and mutual TLS client-certificate patterns
- applying dynamic-address objects in security policies
- checking update behavior with HTTP `HEAD` / `GET` access logs
- troubleshooting `ipfd` download, auth, certificate, and path errors
- understanding `session-scan` and routing-instance reachability for feed servers

Key verification commands:

```text
show security dynamic-address summary
show security dynamic-address
show log messages | match ipfd
```

Reference files:

```text
skills/srx-dynamic-ip-feed/SKILL.md
skills/srx-dynamic-ip-feed/references/source-extract.md
```

### srx-mpls-in-flow

`srx-mpls-in-flow` is an SRX MPLS L3VPN operational playbook synthesized from two Juniper Community TechPosts. It covers the Junos 24.2R1+ model where `family mpls` is packet-based while `family inet` and `family inet6` remain flow-based, allowing stateful security services on MPLS VPN traffic.

Use it for:

- designing SRX secure PE / secure CPE MPLS L3VPN deployments
- replacing older selective packet-mode patterns with decoupled family forwarding controls
- configuring VRFs with route distinguishers, route targets, and SRX-required `vrf-table-label`
- validating OSPF/LDP/MP-BGP `family inet-vpn` transport and VPN routes
- writing Junos 24.2-style VRF-aware policy using `source-l3vpn-vrf-group` and `destination-l3vpn-vrf-group`
- writing Junos 25.4R1+ VRF-to-zone-mapping policies where supported
- handling VRF-aware source NAT, static NAT, AppID, and pre-identification logging
- deciding whether to disable PowerMode for MPLS-only RFP workloads
- troubleshooting MTU, labels, BGP VPN routes, policy matching, NAT, and session details
- interpreting SRX4600/SRX4700 Junos 25.4R1 platform and performance notes conservatively

Key verification commands:

```text
show security flow status
show mpls interface
show ldp neighbor
show route table bgp.l3vpn.0
show route table <vrf>.inet.0
show security policies hit-count
show security flow session extensive
show security nat source rule all
show security nat static rule all
```

Reference files:

```text
skills/srx-mpls-in-flow/SKILL.md
skills/srx-mpls-in-flow/references/source-index.md
skills/srx-mpls-in-flow/references/source-srx-mpls-in-flow-part-1.md
skills/srx-mpls-in-flow/references/source-srx-mpls-in-flow-part-2.md
```

### srx-mnha

`srx-mnha` is a conservative SRX Multi-Node High Availability research/playbook skill built from four Juniper Community TechPosts. The source articles contained some conflicting or ambiguous details, so the main skill intentionally includes only non-conflicting operational guidance and keeps the extracted source material in `references/` for provenance.

Use it for:

- comparing chassis cluster and MNHA design models
- routed, default-gateway, and hybrid MNHA design
- SRG0 and SRG1+ behavior
- ICL design, security, reachability, and liveness checks
- ICD/asymmetric-routing caveats
- runtime object synchronization and Active/Warm session verification
- configuration synchronization patterns and safe separation of shared vs node-specific config
- hybrid MNHA with eBGP, BFD, VIPs, and signal-route export policies
- DHCP relay vs local DHCP behavior on MNHA
- pre-cutover and troubleshooting checklists

Key verification commands:

```text
show chassis high-availability information
show chassis high-availability services-redundancy-group <id>
show security flow session | match "HA State|HA Wing State|Session ID|In:|Out:"
show bgp summary
show bfd session
show dhcp server binding routing-instance <RI>
```

Reference files:

```text
skills/srx-mnha/SKILL.md
skills/srx-mnha/references/source-index.md
skills/srx-mnha/references/source-dhcp-on-mnha-back-to-basics.md
skills/srx-mnha/references/source-multi-node-high-availability-basics.md
skills/srx-mnha/references/source-hybrid-mnha-with-ebgp.md
skills/srx-mnha/references/source-srx-from-chassis-cluster-to-mnha.md
```

## Intermediate Schema

The four `parsing-*` skills output to a common schema with these sections:

| Section | Contents |
|---------|----------|
| `zones` | Security zones and their interfaces |
| `address_objects` | Hosts, subnets, FQDNs, ranges |
| `address_groups` | Groups of address objects |
| `service_objects` | Service/port definitions |
| `service_groups` | Groups of service objects |
| `security_policies` | Firewall rules with resolved apps, services, profiles |
| `applications` | Resolved L7 apps with canonical names and confidence scores |
| `application_groups` | Groups of L7 applications (canonical keys) |
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
- Cross-vendor L7 application mapping with 240+ canonical apps, confidence scores, and categories (web, collaboration, email, remote-access, network-mgmt, database, cloud-storage, streaming, voip, auth, tunnel, security, and more)
- Application and Application Group schema definitions with resolution algorithm (vendor-name → canonical → target-vendor)
- Per-vendor application name mapping tables (JunOS `junos-*`, FortiOS uppercase names, PAN-OS unique names like `ssl`/`web-browsing`, ASA port-to-app inference)
- Expanded intermediate schema with `applications`, `application_groups`, `system`, `virtual_routers`, `admin_users`, `vpn_tunnels`, `ospf_config`, `bgp_config`, `dhcp_config`, `residual_raw` definitions
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
- Port-to-application inference table (protocol+port → canonical app) for cross-platform conversion
- ASA named port keyword mapping (www→80, domain→53, etc.)
- ACL remark attachment to next rule as comment
- Anonymous object creation for inline ACL addresses
- Source port parsing in ACLs
- DHCP server commit trigger pattern (`dhcpd enable`)
- Management access protocol tracking per zone
- VTI tunnel interface assembly with IPsec profile resolution

**FortiGate (parsing-fortinet-configs):**
- FortiOS application name resolution table with application groups and compound proposal parsing
- Wildcard/wildcard-fqdn type conversion (to network/fqdn)
- FortiLink interface filtering
- Allowaccess classification into management services vs routing protocols
- Zone building priority 3 for unzoned interfaces with IPs
- Policy field defaults documentation
- Central SNAT field name variants (`natippool`)
- Tokenizer documentation for quoted multi-value lines
- VPN IPsec phase1/phase2 compound proposal parsing (`aes256-sha256`)

**PAN-OS (parsing-palo-configs):**
- Full PAN-OS application resolution with 4-step pipeline (service check → app-group check → custom app check → canonical lookup)
- `application-default` service decomposition guidance
- Set-format (`show config flat`) input support with auto-detection
- URL categories on security policies
- Application group vs service object resolution in policy application field
- `drop` → `deny` action mapping with warning
- Management interface construction from deviceconfig
- Subinterface zone backfill from parent
- Service and service-group description extraction

**SRX (parsing-srx-configs):**
- 33-entry JunOS predefined application mapping table (`junos-*` → canonical)
- Application-set vs application-group distinction with mixed-set splitting
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
rm -rf ~/.claude/skills/srx-dynamic-ip-feed
rm -rf ~/.claude/skills/srx-mpls-in-flow
rm -rf ~/.claude/skills/srx-mnha

rm -rf ~/.hermes/skills/devops/srx-dynamic-ip-feed
rm -rf ~/.hermes/skills/devops/srx-mpls-in-flow
rm -rf ~/.hermes/skills/devops/srx-mnha
```
