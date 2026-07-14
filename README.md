<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/mechub-mark.svg">
    <img src="docs/assets/mechub-mark-light.svg" width="72" alt="mechub mark">
  </picture>
</p>

<h1 align="center">fwskillsshare</h1>

<p align="center"><strong>Firewall skills for network &amp; security engineers</strong><br>
<em>a mechub project — sovereign network-security automation</em></p>

<p align="center">
  <img alt="skills" src="https://img.shields.io/badge/skills-7-0D9488">
  <img alt="reviewed" src="https://img.shields.io/badge/reviewed-7%2F7-262B38">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-262B38">
  <img alt="vendors" src="https://img.shields.io/badge/vendors-Cisco%20%C2%B7%20Fortinet%20%C2%B7%20Palo%20Alto%20%C2%B7%20Juniper-262B38">
</p>

Agent skills for the firewall work you actually do — four config parsers plus audit, conversion, and diff — not vibe configuring.

Firewall work is unforgiving. A confidently wrong `access-list` line or a Junos stanza that won't commit isn't cosmetic. Coding agents are astonishingly good at producing *plausible* firewall config and astonishingly bad at knowing when it's wrong.

These skills exist to close that gap. They pin the agent to vendor syntax that's been reviewed and to one shared schema so four vendors speak the same language. They're small, self-contained, and composable — copy the two you need or all seven. Hack around with them. Make them your own.

> **Unofficial / community project.** Not affiliated with, endorsed by, or supported by Cisco, Fortinet, Palo Alto Networks, Juniper Networks, or HPE. See [License](#license) for the full trademark disclaimer.

## Quickstart (30-second setup)

1. Run the installer and pick what you want:

```bash
curl -fsSL https://raw.githubusercontent.com/fastrevmd-lab/fwskillsshare/main/install.sh | bash
```

2. Choose your skills (space/numbers to toggle, `a` for all) and where to install them — **Claude Code** (`~/.claude/skills/`), **Codex** (`~/.agents/skills/`), **Hermes**, or all three.

3. Restart the selected agent only if it does not detect the new skills automatically.

4. Done. Paste a config or name a vendor and the right skill loads itself.

Prefer flags, or installing from a clone? See [Installation](#installation).

## Why These Skills Exist

I built these to fix the failure modes I kept hitting when I let Claude Code, Codex, and other agents touch firewalls.

### #1: Every Vendor Speaks A Different Dialect

> "All problems in computer science can be solved by another level of indirection."
>
> David Wheeler

**The Problem.** A Cisco ACL, a FortiGate policy block, a PAN-OS `<entry>`, and an SRX `set security` line all express the same idea four incompatible ways. Ask an agent to compare or convert them and it hand-waves the parts that don't line up.

**The Fix** is a shared language. The four [`parsing-*`](./skills/) skills normalize every vendor into **one vendor-neutral intermediate JSON schema** — zones, objects, policies, NAT, routing, VPN, HA, the lot — with a 240+ entry canonical L7 application map and confidence scores. Once a config is in the schema, cross-vendor [audit](./skills/firewall-best-practices-audit/SKILL.md), [conversion](./skills/firewall-config-conversion/SKILL.md), and [diff](./skills/firewall-config-diff/SKILL.md) all operate by *meaning*, not text. Features with no equivalent are flagged, never silently dropped.

This is the piece that makes the rest composable. See the [Intermediate Schema](#intermediate-schema) below.

### #2: Rulebases Rot, And Agents Accelerate The Rot

> "Complexity is the worst enemy of security."
>
> Bruce Schneier

**The Problem.** Every rulebase drifts toward `any-any`, shadowed rules, orphaned objects, and plaintext management. Agents make firewall changes faster, which means they make the rot faster too, unless something keeps them honest.

**The Fix** is [`firewall-best-practices-audit`](./skills/firewall-best-practices-audit/SKILL.md) — overly permissive and shadowed/redundant rules, missing deny-all and logging, exposed telnet/http/SNMPv1-2c, weak IKE/IPsec crypto, device-plane hardening, unused objects — and [`firewall-config-diff`](./skills/firewall-config-diff/SKILL.md) for drift and HA-pair parity. Prioritized findings with severity and confidence, vendor-neutral plus source-vendor remediation. Run them before you ship a change, not after the incident.

### Summary

Firewall fundamentals don't get easier in the AI age — the blast radius just gets bigger. These skills are my attempt to hand the agent the discipline: reviewed syntax, a shared schema, and a hygiene checklist. Use them, break them, and make them yours.

## Reference

**Seven skills** across two families: four config parsers plus audit, conversion, and diff. All of them are **model-invoked** — the agent reaches for them automatically when it sees supported vendor syntax or a matching analysis task. Invoke one explicitly as `/parsing-srx-configs` in Claude Code or Hermes, or `$parsing-srx-configs` in Codex.

### Config parsers

Normalize a vendor config into the shared intermediate schema. Everything else composes on top.

- **[parsing-cisco-configs](./skills/parsing-cisco-configs/SKILL.md)** — Cisco ASA & FTD (`show running-config`): access-lists, object/object-group, NAT, failover, port-to-app inference.
- **[parsing-fortinet-configs](./skills/parsing-fortinet-configs/SKILL.md)** — FortiGate / FortiOS (`show full-configuration`): the config/edit/set block format, VDOMs, UTM profiles, compound IPsec proposals.
- **[parsing-palo-configs](./skills/parsing-palo-configs/SKILL.md)** — Palo Alto PAN-OS & Panorama: XML *or* flat set-format, vsys, app-default decomposition, device-groups.
- **[parsing-srx-configs](./skills/parsing-srx-configs/SKILL.md)** — Juniper SRX / Junos: `display set` or curly-brace, address-book migration to global, `junos-*` app mapping, routing-instances.

### Cross-vendor tooling

Vendor-neutral, driven off the parsed schema.

- **[firewall-best-practices-audit](./skills/firewall-best-practices-audit/SKILL.md)** — Rulebase hygiene independent of any framework: any-any, shadowed/orphaned rules, missing deny/logging, exposed plaintext services, weak crypto, device-plane hardening.
- **[firewall-config-conversion](./skills/firewall-config-conversion/SKILL.md)** — Migrate between Cisco/FortiGate/Palo/SRX with a per-section fidelity report (converted / caveats / manual). A reviewed draft, never production-ready.
- **[firewall-config-diff](./skills/firewall-config-diff/SKILL.md)** — Compare two configs by meaning (order- and name-insensitive) — same-vendor drift & HA parity, or cross-vendor migration validation.

---

## Quality and Review

All **7 / 7 skills** have passed independent technical review for vendor command/syntax correctness, schema/field accuracy, secret hygiene, and application behavior. All findings were remediated and the four `parsing-*` skills share one byte-identical intermediate schema (verified by `scripts/check-shared-schema.py`).

An authoring-quality pass covered frontmatter, discovery keywords, secret redaction, cross-skill hand-offs, and progressive disclosure into `references/` files, then closed with clean-context retrieval tests against the restructured skills.

| Family | Skills | Reviewed |
|--------|-------:|:--------:|
| Config parsers | 4 | 4 / 4 |
| Cross-vendor tooling (audit · convert · diff) | 3 | 3 / 3 |
| **Total** | **7** | **7 / 7** |

These are parsing and analysis skills, not certified products: review their output against current vendor documentation and live device behavior before relying on it.

Each skill also includes optional `agents/openai.yaml` UI metadata for Codex. Claude Code and Hermes continue to use the portable `SKILL.md` content and ignore that product-specific folder.

Run `python3 scripts/check-skill-packages.py` to validate portable frontmatter, reference paths, the combined Codex discovery budget, and all Codex UI metadata. Run `python3 scripts/check-shared-schema.py` to verify the four parser schemas remain byte-identical.

## Installation

### Installer (recommended)

The [`install.sh`](./install.sh) installer runs interactively when piped from curl, or with flags for scripted/non-interactive use:

```bash
# Interactive: pick skills + target
curl -fsSL https://raw.githubusercontent.com/fastrevmd-lab/fwskillsshare/main/install.sh | bash

# Or from a clone
git clone git@github.com:fastrevmd-lab/fwskillsshare.git
cd fwskillsshare
./install.sh
```

Flags:

```text
--all                 Install all 7 skills
--skill NAME          Install a specific skill (repeatable)
--family NAME         parsers | tooling (repeatable)
--target WHERE        claude | codex | hermes | both | all
                      (`both` keeps the legacy Claude+Hermes meaning; default: prompt, or claude with -y)
--dir PATH            Explicit install directory (overrides --target)
--list                List the skill inventory and exit
--uninstall           Remove the selected skills instead of installing
--force               Overwrite existing skill directories without prompting
-y, --yes             Non-interactive; assume defaults
-h, --help            Show help
```

Examples:

```bash
./install.sh --all --target claude              # everything, into ~/.claude/skills
./install.sh --all --target codex               # everything, into ~/.agents/skills
./install.sh --family parsers                    # just the four config parsers
./install.sh --family tooling --target all      # tooling skills into all three agents
./install.sh --skill parsing-srx-configs --skill firewall-config-diff
./install.sh --list                             # see what's available
```

### Manual install

The skills are plain directories — copy the ones you want:

```bash
git clone git@github.com:fastrevmd-lab/fwskillsshare.git

# All of them
cp -r fwskillsshare/skills/* ~/.claude/skills/

# Or a single skill
cp -r fwskillsshare/skills/parsing-srx-configs ~/.claude/skills/
```

For **Codex**, copy into the user skill tree. Codex normally detects changes automatically; restart it if a new skill does not appear:

```bash
mkdir -p ~/.agents/skills
cp -r fwskillsshare/skills/* ~/.agents/skills/
```

For **Hermes**, copy into your local Hermes skills tree (usually `~/.hermes/skills/devops/`) and confirm with `hermes skills list`:

```bash
mkdir -p ~/.hermes/skills/devops
cp -r fwskillsshare/skills/* ~/.hermes/skills/devops/
hermes skills list | grep -E 'parsing-|firewall-'
```

Skills auto-trigger when they detect supported vendor syntax or audit, conversion, and diff requests in your messages or pasted configs.

### Managing context

Skill *bodies* only load when a skill is invoked, but each skill's short description stays in context so the agent knows when to reach for it. You can drop a description from context while keeping the skill invocable via `skillOverrides` in `~/.claude/settings.json`:

```json
{ "skillOverrides": { "firewall-config-diff": "name-only" } }
```

`"name-only"` keeps the skill listed and invocable but hides its description; `"user-invocable-only"` hides it from the model entirely (slash-command only); `"off"` hides it completely.

For **Codex**, disable an installed skill without deleting it by adding its `SKILL.md` path to `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/home/you/.agents/skills/firewall-config-diff/SKILL.md"
enabled = false
```

## Usage

### What you can do

- **Parse** — Extract all objects, policies, NAT rules, and routes into structured JSON
- **Audit** — Find unused objects, shadowed rules, overly permissive policies, missing logging
- **Convert** — Transform configs between vendors (e.g., SRX to PAN-OS)
- **Compare** — Diff two configs by meaning, not text
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
- Each `parsing-*` skill includes `references/fixture-minimal-input.md` and `references/fixture-expected-output.json` as a smoke-test fixture for parser behavior and schema shape

## Conversion Caveats

- Application-level rules (Palo Alto apps, FortiGate app control) don't map 1:1 to port-based platforms (ASA)
- User-ID / FSSO source-user rules have no equivalent on most platforms
- Dynamic address groups (PAN-OS) have no static equivalent
- Geography/GeoIP objects have limited cross-platform support

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

### Shared schema maintenance

The `intermediate-schema.md` file is intentionally duplicated in each `parsing-*` skill so every skill stays self-contained when copied alone. Treat `skills/parsing-srx-configs/references/intermediate-schema.md` as the canonical editing copy, sync the same content to the other parser skills, then run:

```bash
python3 scripts/check-shared-schema.py
```

See `skills/SHARED-SCHEMA.md` for the full policy.

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
- MNHA (multi-node HA) detection
- Unit-0 interface name normalization
- Cluster interface (reth/fab) exclusion

## Uninstall

```bash
# Remove everything the installer put down from Claude Code and Hermes
./install.sh --uninstall --all --target both

# Remove everything from Claude Code, Codex, and Hermes
./install.sh --uninstall --all --target all

# Or remove a single skill
./install.sh --uninstall --skill firewall-config-diff --target codex
```

Manual equivalent — the skills are just directories, so remove the selected skill directory under `~/.claude/skills/`, `~/.agents/skills/`, or `~/.hermes/skills/devops/` for the corresponding agent.

## License

Original content in this repository is licensed under the [MIT License](LICENSE).

**Trademark / affiliation disclaimer.** This repository is an independent, community-driven project. It is not affiliated with, endorsed by, sponsored by, or supported by Hewlett Packard Enterprise, Cisco, Palo Alto Networks, Fortinet, or Juniper Networks. "HPE", "Juniper", "Cisco", "Fortinet", "Palo Alto Networks", and "Juniper SRX" are trademarks of their respective owners and are used here only to describe what this software interoperates with. Please direct support and licensing questions about those products to the respective vendors.

## Contributing

Unless explicitly stated otherwise, contributions submitted for inclusion in this project are licensed under the [MIT License](LICENSE).

---

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/mechub-mark.svg">
    <img src="docs/assets/mechub-mark-light.svg" width="28" alt="">
  </picture><br>
  <sub><code>a mechub project</code> · deterministic decides · the model explains · a human approves<br>
  <a href="https://github.com/fastrevmd-lab">github.com/fastrevmd-lab</a></sub>
</p>
