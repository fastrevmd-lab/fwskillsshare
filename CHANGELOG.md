# Changelog

## 1.3.0 — srx-initial-setup policy model opt-out

**srx-initial-setup** v1.1.0 — adds explicit zone-to-zone policy opt-out to align with `srx-policy` skill's enforced global-policy contract. The baseline policy is generated as global policy; when a zone-pair exception applies (existing-estate compatibility, isolated exceptions clearer as zone-pair policies, or customer standards requiring zone-pair contexts), the policy stage routes to `srx-policy` for zone-pair design. Adds runtime intake question `sis_policy_model` to confirm the architecture before generating the baseline.

## 1.2.0 — srx-initial-setup skill

New skill: **[srx-initial-setup](./skills/srx-initial-setup/SKILL.md)** v1.0.0 — first-time SRX bring-up from factory-default or zeroized state to a reachable, zoned, screened, and minimally policied device. Automates Day-0 and Day-1 setup for Branch SRX300/400, campus SRX1600/4120, and datacenter SRX4300/4700/5000 platforms. At 1.0.0 this skill is written from vendor documentation and existing verified repository references; no device validation has been performed. Validation against vSRX and against SRX345, SRX1600, and SRX4700 hardware is deferred to a later release. Key features:

- Assess-first architecture: read-only entry-state assessment classifies device into one of five states before proposing any writes
- Dependency-ordered gap model: closes only the gaps that are actually open, making the skill idempotent
- Per-stage approval gates with confirmed commit and rollback timers on all lockout-risk changes
- Branch factory-default handling: removal of shipped zones, DHCP server, and permissive policy only after replacement management path is verified
- Five stages: access and recovery, management plane, interfaces and zones with host-inbound-traffic, starter IDS screens, and minimal baseline policy
- Entitlement readout across three independent axes (entitled, configured, active) that routes to sibling skills for license mutation and feature configuration

## 1.1.1 — README split

Documentation only. No skill content changed, and every skill keeps the version it
carried in 1.1.0.

- `README.md` trimmed from 783 to 494 lines.
- Per-skill detail for the compliance and SRX operational playbooks moved to
  [`SKILLS.md`](./SKILLS.md).
- The v1.1.0 parser notes below moved out of the README into this file.
- The 21-row intermediate-schema table condensed to prose plus a link at its canonical
  copy, `skills/parsing-srx-configs/references/intermediate-schema.md`.
- Usage examples cut from eleven to five; each skill's own `SKILL.md` carries worked
  examples for its topic.
- `SKILLS.md` and `CHANGELOG.md` added to the downstream publish allowlist, without
  which the published README would link to two files that were never published.

## 1.1.0 — parser improvements from fatcat/converter

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
- MNHA (multi-node HA) detection
- Unit-0 interface name normalization
- Cluster interface (reth/fab) exclusion
