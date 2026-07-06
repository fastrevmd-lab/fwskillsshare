# Firewall Skills

Unofficial / community project. This repository is an independent, community-driven project. It is not affiliated with, endorsed by, sponsored by, or supported by Hewlett Packard Enterprise, Cisco, Palo Alto Networks, or Juniper Networks. "HPE", "Juniper", "Cisco", "Fortinet", "Palo Alto Networks", and "Juniper SRX" are trademarks of their respective owners and are used here only to describe what this software interoperates with. Please direct support and licensing questions about those products to the respective vendors

A collection of Claude Code / Hermes skills for parsing, auditing, converting, and analyzing enterprise firewall configurations, plus Juniper SRX operational playbooks derived from field/research material.

## Skills Included

**21 skills** across four families — 4 config parsers, 8 Juniper SRX operational playbooks, 6 NGFW compliance assessment playbooks, and 3 vendor-neutral cross-vendor tooling skills (audit, conversion, and diff):

| Skill | Vendor / Platform | Trigger Keywords |
|-------|-------------------|------------------|
| [parsing-cisco-configs](skills/parsing-cisco-configs/) | Cisco ASA & FTD | `ASA`, `FTD`, `access-list`, `object network`, `nameif` |
| [parsing-fortinet-configs](skills/parsing-fortinet-configs/) | Fortinet FortiGate / FortiOS | `FortiGate`, `FortiOS`, `config firewall policy`, `set srcintf` |
| [parsing-palo-configs](skills/parsing-palo-configs/) | Palo Alto PAN-OS & Panorama | `PAN-OS`, `Palo Alto`, `Panorama`, `vsys`, `<entry name=` |
| [parsing-srx-configs](skills/parsing-srx-configs/) | Juniper SRX / Junos | `SRX`, `Junos`, `Juniper`, `set security`, `from-zone` |
| [srx-dynamic-ip-feed](skills/srx-dynamic-ip-feed/) | Juniper SRX / Junos dynamic-address feed servers | `dynamic-address`, `feed-server`, `IPFD`, `show security dynamic-address`, `ipfd` |
| [srx-mpls-in-flow](skills/srx-mpls-in-flow/) | Juniper SRX / Junos MPLS L3VPN in flow mode | `MPLS in Flow`, `family mpls mode packet-based`, `inet-vpn`, `vrf-table-label`, `VRF-to-zone` |
| [srx-mnha](skills/srx-mnha/) | Juniper SRX / Junos Multi-Node High Availability | `MNHA`, `Multi-Node High Availability`, `chassis high-availability`, `SRG`, `ICL`, `ICD` |
| [srx-nat](skills/srx-nat/) | Juniper SRX / Junos NAT | `source nat`, `destination nat`, `static nat`, `NAT64`, `CGN`, `PBA`, `hairpin`, `proxy-arp` |
| [srx-policy](skills/srx-policy/) | Juniper SRX / Junos security policy | `security policies global`, `from-zone`, `to-zone`, `AppFW`, `AppID`, `NGWF`, `EWF`, `web-filtering`, `SecIntel`, `ATP` |
| [srx-autovpn-full-tunnel](skills/srx-autovpn-full-tunnel/) | Juniper SRX / Junos AutoVPN full-tunnel backhaul | `AutoVPN`, `full-tunnel`, `backhaul`, `traffic-selector`, `ARI`, `group-ike-id`, `centralized egress`, `anti-recursion` |
| [srx-ipsec-hub-spoke](skills/srx-ipsec-hub-spoke/) | Juniper SRX / Junos static P2P IPsec hub-and-spoke | `route-based IPsec`, `hub-and-spoke`, `point-to-point`, `per-spoke tunnel`, `st0`, `full-tunnel`, `backhaul`, `anti-recursion` |
| [srx-advpn](skills/srx-advpn/) | Juniper SRX / Junos Auto Discovery VPN (dynamic spoke-to-spoke) | `ADVPN`, `Auto Discovery VPN`, `suggester`, `partner`, `shortcut`, `multipoint st0`, `OSPF p2mp`, `dynamic-neighbors`, `PKI` |
| [firewall-best-practices-audit](skills/firewall-best-practices-audit/) | Vendor-neutral (Cisco/Palo/FortiGate/SRX via parsers) — v1.1 (adds mgmt/control-plane/auth/security-service checks) | `firewall audit`, `best practices`, `hardening`, `rulebase review`, `shadowed rules`, `any-any`, `least privilege`, `unused objects` |
| [firewall-config-conversion](skills/firewall-config-conversion/) | Cross-vendor (Cisco/FortiGate/Palo/SRX via parsers) | `convert firewall config`, `migrate`, `ASA to SRX`, `FortiGate to Palo`, `cross-vendor`, `fidelity report` |
| [firewall-config-diff](skills/firewall-config-diff/) | Cross-vendor (Cisco/FortiGate/Palo/SRX via parsers) | `diff firewall config`, `compare`, `config drift`, `HA-pair`, `parity`, `migration validation`, `round-trip` |
| [pci-ngfw-compliance](skills/pci-ngfw-compliance/) | PCI DSS / NGFW compliance support | `PCI DSS`, `CDE`, `Requirement 1`, `PCI compliant firewall`, `PCI markers`, `audit evidence` |
| [hipaa-ngfw-compliance](skills/hipaa-ngfw-compliance/) | HIPAA Security Rule / NGFW compliance support | `HIPAA`, `HIPPA`, `ePHI`, `Security Rule`, `164.312`, `HIPAA markers`, `audit evidence` |
| [cmmc-nist-800-171-ngfw-compliance](skills/cmmc-nist-800-171-ngfw-compliance/) | CMMC Level 2 / NIST SP 800-171 CUI compliance support | `CMMC`, `NIST 800-171`, `CUI`, `CUI enclave`, `3.13.1`, `CMMC markers`, `SSP evidence` |
| [cis-controls-ngfw-compliance](skills/cis-controls-ngfw-compliance/) | CIS Controls v8/v8.1 / NGFW compliance support | `CIS Controls`, `CIS v8`, `Implementation Group`, `Control 12`, `Control 13`, `CIS markers`, `audit evidence` |
| [iso27001-ngfw-compliance](skills/iso27001-ngfw-compliance/) | ISO/IEC 27001:2022 / ISMS firewall support | `ISO 27001`, `Annex A`, `ISMS`, `SoA`, `network security`, `supplier access`, `ISO markers` |
| [soc2-ngfw-compliance](skills/soc2-ngfw-compliance/) | SOC 2 Trust Services Criteria firewall support | `SOC 2`, `Trust Services Criteria`, `CC6`, `CC7`, `CC8`, `Type II`, `SOC2 markers` |

The four `parsing-*` skills parse vendor-specific configs into a **common vendor-neutral intermediate JSON schema**, enabling cross-vendor comparison, conversion, and unified auditing. They now share common parser quality gates: schema conformance, object counts, unresolved-reference reporting, ordering/state preservation, residual capture, warnings/assumptions, and explicit conversion caveats.

The SRX operational skills are actionable Junos playbooks with commands, design guidance, verification steps, troubleshooting matrices, source attribution, and reference extracts.

The compliance skills are research-backed NGFW/firewall assessment playbooks. They map firewall capabilities to compliance-control evidence, include assessor/auditor output templates, and recommend short config description/tag markers for policies, NAT, zones, VPNs, objects, and profiles where the platform supports them.

## License and Provenance

Original skill/playbook text in this repository is released under the MIT License; see [LICENSE](LICENSE).

Some `references/` files contain source-derived notes or extracts from Juniper, Cisco, Fortinet, Palo Alto Networks, community posts, blogs, support portals, or other third-party material. Those excerpts are included for local operational context, attribution, and verification. Upstream source material remains subject to its original owners' terms. Before redistributing, bundling commercially, or publishing a derivative catalog, review the upstream licenses/terms and replace long excerpts with citations or concise notes where required.

## Quality and Review

All **21 / 21 skills** have passed independent technical review — first on 2026-06-30, then re-reviewed on 2026-07-02 with a two-stage process: an OpenAI Codex CLI review per skill (vendor command/syntax correctness for Cisco ASA/FTD, FortiGate, PAN-OS, and Junos SRX; schema/field accuracy; standards/control-ID accuracy; secret hygiene) followed by per-skill application QA tests (fixture execution for the parsers, engineer-walkthrough scenarios for the playbooks, control-ID spot-checks for the compliance skills). Disputed Junos syntax claims were settled empirically by commit-checking on a live vSRX 24.4R1. All findings were remediated and the four `parsing-*` skills share one byte-identical intermediate schema (verified by `scripts/check-shared-schema.py`).

A third round on 2026-07-04/05 applied an authoring-quality pass across all 21 skills (frontmatter, discovery keywords, secret redaction, cross-skill hand-offs, progressive disclosure into `references/` files), then closed it out with fresh clean-context retrieval tests against the restructured skills — every question had to be answerable from the SKILL.md pointers alone. The tests passed and surfaced a handful of fixes (including two operational-command syntax errors caught and corrected by live verification on vSRX 24.4R1), all remediated.

| Family | Skills | Reviewed |
|--------|-------:|:--------:|
| Config parsers | 4 | 4 / 4 |
| SRX operational playbooks | 8 | 8 / 8 |
| NGFW compliance playbooks | 6 | 6 / 6 |
| Cross-vendor tooling (audit · convert · diff) | 3 | 3 / 3 |
| **Total** | **21** | **21 / 21** |

These are research/operational and assessment-support skills, not certified products: review their output against current vendor documentation, live device behavior, and (for compliance work) a qualified assessor before relying on it.

## Installation

### Quick Install (all skills)

Copy the skill directories into your Claude Code skills folder:

```bash
# Clone the repo
git clone git@github.com:fastrevmd-lab/fwskillsshare.git

# Copy all skills into your Claude Code skills directory
cp -r fwskillsshare/skills/* ~/.claude/skills/
```

### Install a single skill

```bash
# Example: install only the Cisco ASA skill
cp -r fwskillsshare/skills/parsing-cisco-configs ~/.claude/skills/

# Example: install only the SRX MNHA skill
cp -r fwskillsshare/skills/srx-mnha ~/.claude/skills/

# Example: install only the SRX MPLS in Flow skill
cp -r fwskillsshare/skills/srx-mpls-in-flow ~/.claude/skills/

# Example: install only the SRX NAT skill
cp -r fwskillsshare/skills/srx-nat ~/.claude/skills/

# Example: install only the SRX Policy skill
cp -r fwskillsshare/skills/srx-policy ~/.claude/skills/

# Example: install only the SRX AutoVPN full-tunnel backhaul skill
cp -r fwskillsshare/skills/srx-autovpn-full-tunnel ~/.claude/skills/

# Example: install only the SRX static P2P IPsec hub-and-spoke skill
cp -r fwskillsshare/skills/srx-ipsec-hub-spoke ~/.claude/skills/

# Example: install only the SRX ADVPN (Auto Discovery VPN) skill
cp -r fwskillsshare/skills/srx-advpn ~/.claude/skills/

# Example: install only the PCI NGFW compliance skill
cp -r fwskillsshare/skills/pci-ngfw-compliance ~/.claude/skills/

# Example: install only the HIPAA NGFW compliance skill
cp -r fwskillsshare/skills/hipaa-ngfw-compliance ~/.claude/skills/

# Example: install only the CMMC / NIST 800-171 NGFW compliance skill
cp -r fwskillsshare/skills/cmmc-nist-800-171-ngfw-compliance ~/.claude/skills/

# Example: install only the CIS Controls NGFW compliance skill
cp -r fwskillsshare/skills/cis-controls-ngfw-compliance ~/.claude/skills/

# Example: install only the ISO 27001 NGFW compliance skill
cp -r fwskillsshare/skills/iso27001-ngfw-compliance ~/.claude/skills/

# Example: install only the SOC 2 NGFW compliance skill
cp -r fwskillsshare/skills/soc2-ngfw-compliance ~/.claude/skills/

# Example: install only the vendor-neutral firewall best-practices audit skill
cp -r fwskillsshare/skills/firewall-best-practices-audit ~/.claude/skills/

# Example: install only the cross-vendor firewall config conversion skill
cp -r fwskillsshare/skills/firewall-config-conversion ~/.claude/skills/

# Example: install only the cross-vendor firewall config diff skill
cp -r fwskillsshare/skills/firewall-config-diff ~/.claude/skills/
```

### Verify installation

After copying, your `~/.claude/skills/` directory should look like:

```
~/.claude/skills/
├── parsing-cisco-configs/
│   ├── SKILL.md
│   └── references/
│       ├── config-format.md
│       ├── intermediate-schema.md
│       ├── parsing-patterns.md
│       ├── example-sample-parse.md
│       ├── fixture-minimal-input.md
│       └── fixture-expected-output.json
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
├── srx-mnha/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       ├── mnha-config-patterns.md
│       ├── source-dhcp-on-mnha-back-to-basics.md
│       ├── source-multi-node-high-availability-basics.md
│       ├── source-hybrid-mnha-with-ebgp.md
│       ├── source-mnha-ipsec-and-multiple-routing-instances.md
│       └── source-srx-from-chassis-cluster-to-mnha.md
├── srx-nat/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       ├── source-dns64-and-nat64-on-srx-series.md
│       ├── source-srx4600-cgn-configuration-breakdown.md
│       ├── source-security-nat-overview.md
│       ├── source-troubleshoot-source-nat.md
│       └── source-troubleshoot-destination-nat.md
├── srx-policy/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       ├── source-configuring-security-policies-junos-os.md
│       ├── source-security-global-policies.md
│       ├── source-security-policy-applications-and-application-sets-junos-os.md
│       ├── source-juniper-srx-enhanced-web-filtering-configuration.md
│       ├── ngwf-vs-ewf-research.md
│       └── source-secintel-feeds-overview-and-benefits.md
├── srx-autovpn-full-tunnel/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       └── source-design-summary.md
├── srx-ipsec-hub-spoke/
│   ├── SKILL.md
│   └── references/
│       ├── source-index.md
│       └── source-design-summary.md
├── srx-advpn/
│   ├── SKILL.md
│   └── references/
│       └── field-notes-vsrx-advpn-lab.md
├── firewall-best-practices-audit/
│   ├── SKILL.md
│   └── references/
│       ├── check-catalog.md
│       ├── remediation-patterns.md
│       └── example-audit.md
├── firewall-config-conversion/
│   ├── SKILL.md
│   └── references/
│       ├── feature-mapping.md
│       ├── emit-srx.md
│       ├── emit-palo.md
│       ├── emit-fortinet.md
│       ├── emit-cisco.md
│       └── example-conversion.md
├── firewall-config-diff/
│   ├── SKILL.md
│   └── references/
│       ├── equivalence-rules.md
│       └── example-diff.md
├── pci-ngfw-compliance/
│   ├── SKILL.md
│   └── references/
│       ├── control-mapping.md
│       └── assessment-workflow.md
├── hipaa-ngfw-compliance/
│   ├── SKILL.md
│   └── references/
│       ├── control-mapping.md
│       └── assessment-workflow.md
├── cmmc-nist-800-171-ngfw-compliance/
│   ├── SKILL.md
│   └── references/
│       ├── control-mapping.md
│       └── assessment-workflow.md
├── cis-controls-ngfw-compliance/
│   ├── SKILL.md
│   └── references/
│       ├── control-mapping.md
│       └── assessment-workflow.md
├── iso27001-ngfw-compliance/
│   ├── SKILL.md
│   └── references/
│       ├── control-mapping.md
│       └── assessment-workflow.md
└── soc2-ngfw-compliance/
    ├── SKILL.md
    └── references/
        ├── control-mapping.md
        └── assessment-workflow.md
```

Restart Claude Code after installing. The skills will auto-trigger when they detect vendor-specific keywords, SRX operational topics, or PCI/HIPAA/CMMC/NIST 800-171/CIS Controls/ISO 27001/SOC 2 compliance language in your messages or pasted configs.

### Hermes local install

For Hermes Agent, copy the skill directories into your local Hermes skills tree, usually under `~/.hermes/skills/devops/`:

```bash
mkdir -p ~/.hermes/skills/devops
cp -r fwskillsshare/skills/parsing-* ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-dynamic-ip-feed ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-mpls-in-flow ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-mnha ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-nat ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-policy ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-autovpn-full-tunnel ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/srx-ipsec-hub-spoke ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/pci-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/hipaa-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/cmmc-nist-800-171-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/cis-controls-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/iso27001-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/soc2-ngfw-compliance ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/firewall-best-practices-audit ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/firewall-config-conversion ~/.hermes/skills/devops/
cp -r fwskillsshare/skills/firewall-config-diff ~/.hermes/skills/devops/

hermes skills list | grep -E 'parsing-|srx-dynamic-ip-feed|srx-mpls-in-flow|srx-mnha|srx-nat|srx-policy|srx-autovpn-full-tunnel|srx-ipsec-hub-spoke|pci-ngfw-compliance|hipaa-ngfw-compliance|cmmc-nist-800-171-ngfw-compliance|cis-controls-ngfw-compliance|iso27001-ngfw-compliance|soc2-ngfw-compliance|firewall-best-practices-audit|firewall-config-conversion|firewall-config-diff'
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
/srx-nat
/srx-policy
/srx-autovpn-full-tunnel
/srx-ipsec-hub-spoke
/srx-advpn
/pci-ngfw-compliance
/hipaa-ngfw-compliance
/cmmc-nist-800-171-ngfw-compliance
/cis-controls-ngfw-compliance
/iso27001-ngfw-compliance
/soc2-ngfw-compliance
/firewall-best-practices-audit
/firewall-config-conversion
/firewall-config-diff
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
- **Operate SRX NAT** — Configure and troubleshoot source NAT, destination NAT, static NAT, NAT64/DNS64, CGN/PBA, persistent NAT, hairpin NAT, and proxy ARP
- **Design SRX security policy** — Prefer `security policies global` for greenfield and vendor migrations, then layer AppID/AppFW, NGWF-first web filtering, SecIntel, and ATP controls
- **Assess PCI firewall evidence** — Map NGFW policies, NAT, zones, logging, IDS/IPS, WAF/WAAP, and CDE segmentation to PCI DSS evidence expectations
- **Assess HIPAA firewall safeguards** — Map NGFW controls to HIPAA Security Rule ePHI access control, audit controls, transmission security, incident response, documentation, and business associate evidence
- **Assess CMMC / NIST 800-171 firewall safeguards** — Map NGFW controls to CUI enclave scoping, boundary protection, remote access, external connections, audit logging, SSP evidence, and POA&M-style gaps
- **Assess CIS Controls firewall safeguards** — Map NGFW controls to CIS Controls v8/v8.1 secure configuration, network infrastructure management, access control, audit logging, monitoring/defense, service-provider access, incident response, and testing evidence
- **Assess ISO 27001 firewall controls** — Map NGFW controls to ISMS scope, Statement of Applicability, Annex A network security, access control, logging/monitoring, supplier access, change management, and incident-management evidence
- **Assess SOC 2 firewall controls** — Map NGFW controls to Trust Services Criteria such as CC6 logical access, CC7 system operations, CC8 change management, CC9 risk mitigation, Availability, and Confidentiality evidence

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

# SRX NAT troubleshooting
"Help me troubleshoot this SRX destination NAT rule: hits increment, but the policy denies the translated web server session"

# SRX global policy migration
"Convert this vendor rulebase into an SRX 23.x global security policy design with AppFW, NGWF-first web filtering, SecIntel, logging, and a final deny"

# PCI NGFW compliance review
"Review this firewall export for PCI DSS CDE segmentation evidence and recommend policy/NAT/zone description markers"

# HIPAA NGFW compliance review
"Review this NGFW design for HIPAA Security Rule ePHI access control, audit logging, transmission security, and config description markers"

# CMMC / NIST 800-171 NGFW compliance review
"Review this firewall design for CMMC Level 2 CUI boundary protection, remote access, external connections, audit logging, SSP evidence, and config description markers"

# CIS Controls NGFW compliance review
"Review this firewall estate against CIS Controls v8 for secure configuration, network infrastructure management, audit logging, monitoring/defense, vendor access, and config description markers"

# ISO 27001 NGFW compliance review
"Review this firewall estate against ISO/IEC 27001:2022 for ISMS scope, SoA alignment, network security, supplier access, logging, change management, and config description markers"

# SOC 2 NGFW compliance review
"Review this production firewall estate for SOC 2 Type II evidence around CC6 access, CC7 monitoring, CC8 change management, availability, confidentiality, and config description markers"
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
  - **SRX NAT**: collect `show configuration security nat | display set`, `show security nat source rule all`, `show security nat destination rule all`, `show security nat static rule all`, `show security nat source pool all`, `show security nat proxy-arp`, and `show security flow session ... extensive`
  - **SRX security policy**: collect `show configuration security policies | display set`, `show configuration security policies global | display set`, `show security policies hit-count global`, `show security application-firewall rule-set <name>`, `show security utm web-filtering status`, `show security utm web-filtering statistics`, and `show security flow session ... extensive`
  - **PCI NGFW compliance**: collect firewall policy/NAT/zone/object exports, CDE network and data-flow diagrams, rule-review evidence, change tickets, logging/SIEM evidence, IDS/IPS/WAF evidence, and segmentation test results
  - **HIPAA NGFW compliance**: collect ePHI asset/data-flow diagrams, firewall policy/NAT/zone/VPN/object exports, risk analysis references, vendor/business associate access evidence, logging/SIEM evidence, encryption/VPN settings, and incident response runbooks
  - **CMMC / NIST 800-171 NGFW compliance**: collect SSP boundary sections, CUI asset/data-flow diagrams, firewall policy/NAT/zone/VPN/object exports, remote-access and external-connection evidence, logging/SIEM evidence, rule-review records, and POA&M/gap records
  - **CIS Controls NGFW compliance**: collect target CIS version/Implementation Group, network infrastructure inventory, firewall policy/NAT/zone/VPN/object exports, secure baseline evidence, admin/access records, logging/SIEM evidence, vulnerability/firmware records, service-provider access evidence, incident response runbooks, and penetration/segmentation test results
  - **ISO 27001 NGFW compliance**: collect ISMS scope, SoA, risk treatment entries, firewall policy/NAT/zone/VPN/object exports, secure baseline evidence, supplier access evidence, logging/SIEM records, change samples, incident records, and management-system corrective actions
  - **SOC 2 NGFW compliance**: collect system description, report period, Trust Services Categories, control matrix, firewall policy/NAT/zone/VPN/object exports, change samples, rule reviews, access reviews, alert/incident evidence, vendor evidence, and Type II operating-effectiveness samples
- For large configs, save to a file and point Claude at the file path
- Each `parsing-*` skill includes `references/fixture-minimal-input.md` and `references/fixture-expected-output.json` as a small smoke-test fixture for parser behavior and schema shape

## Conversion Caveats

- Application-level rules (Palo Alto apps, FortiGate app control) don't map 1:1 to port-based platforms (ASA)
- User-ID / FSSO source-user rules have no equivalent on most platforms
- Dynamic address groups (PAN-OS) have no static equivalent
- Geography/GeoIP objects have limited cross-platform support

## Compliance Skills

### pci-ngfw-compliance

`pci-ngfw-compliance` is a PCI DSS v4.0.1 NGFW/firewall assessment playbook. It explains that an NGFW can support PCI DSS network security control evidence, but the device is not independently “PCI compliant.”

Use it for:

- mapping firewall policy, NAT, zones, IDS/IPS, WAF/WAAP, logging, and segmentation controls to PCI DSS evidence expectations
- reviewing CDE inbound/outbound restrictions, default deny, payment processor paths, and public-facing service exposure
- preparing assessor-ready evidence requests, findings, and gap-analysis summaries
- adding short PCI evidence markers to firewall descriptions/tags for policies, NAT, zones, objects, and profiles where supported

Reference files:

```text
skills/pci-ngfw-compliance/SKILL.md
```

### hipaa-ngfw-compliance

`hipaa-ngfw-compliance` is a HIPAA Security Rule NGFW/firewall assessment playbook. It explains that an NGFW can support reasonable and appropriate safeguards for ePHI, but HIPAA compliance is assessed at the covered entity or business associate program/environment level.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, WAF/WAAP, logging, and segmentation controls to HIPAA Security Rule safeguards
- reviewing ePHI access control, audit controls, person/entity authentication, transmission security, incident response, documentation, and business associate/vendor access evidence
- preparing compliance-ready evidence requests, findings, and risk-treatment recommendations
- adding short HIPAA evidence markers to firewall descriptions/tags for policies, NAT, zones, VPNs, objects, and profiles where supported

Reference files:

```text
skills/hipaa-ngfw-compliance/SKILL.md
```

### cmmc-nist-800-171-ngfw-compliance

`cmmc-nist-800-171-ngfw-compliance` is a CMMC Level 2 / NIST SP 800-171 NGFW/firewall assessment playbook. It explains that an NGFW can support CUI protection requirements, but CMMC/NIST 800-171 compliance is assessed at the contractor environment and CUI protection program level, not by certifying the firewall product alone.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, logging, segmentation, and remote-access controls to NIST 800-171 / CMMC evidence expectations
- reviewing CUI enclave scope, CUI data flows, boundary protection, external connections, public-system separation, audit controls, and system security plan evidence
- preparing assessor-ready evidence requests, findings, POA&M-style gaps, and remediation recommendations
- adding short CMMC/CUI evidence markers to firewall descriptions/tags for policies, NAT, zones, VPNs, objects, and profiles where supported

Reference files:

```text
skills/cmmc-nist-800-171-ngfw-compliance/SKILL.md
```

### cis-controls-ngfw-compliance

`cis-controls-ngfw-compliance` is a CIS Critical Security Controls v8/v8.1 NGFW/firewall assessment playbook. It explains that an NGFW can support CIS safeguards, but CIS alignment is assessed across the implemented environment and security program, not by certifying the firewall product alone.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, logging, secure configuration, vulnerability management, and network monitoring controls to CIS Controls evidence expectations
- reviewing network infrastructure inventory, secure firewall baselines, administrative access, service-provider/vendor access, logging, malware/threat defenses, backup/recovery, incident response, and penetration/segmentation testing evidence
- preparing practical CIS-aligned evidence requests, findings, prioritized remediation actions, and risk-based roadmap items
- adding short CIS evidence markers to firewall descriptions/tags for policies, NAT, zones, VPNs, objects, and profiles where supported

Reference files:

```text
skills/cis-controls-ngfw-compliance/SKILL.md
```

### iso27001-ngfw-compliance

`iso27001-ngfw-compliance` is an ISO/IEC 27001:2022 ISMS and Annex A firewall-control playbook. It explains that an NGFW can support selected controls, but certification applies to the scoped ISMS and its risk assessment, Statement of Applicability, policies, operation, audit, and continual-improvement evidence.

Use it for:

- mapping firewall policy, NAT, VPN, zones, logging, secure configuration, supplier access, change management, backups, and incident response to SoA/risk-treatment evidence
- reviewing network security, access control, configuration management, logging/monitoring, supplier access, vulnerability management, and corrective-action records
- preparing ISO audit evidence requests, firewall findings, corrective actions, and management-system caveats
- adding short ISO/ISMS evidence markers to firewall descriptions/tags where supported

Reference files:

```text
skills/iso27001-ngfw-compliance/SKILL.md
```

### soc2-ngfw-compliance

`soc2-ngfw-compliance` is a SOC 2 Trust Services Criteria firewall-control playbook for service organizations, SaaS platforms, MSPs, and cloud providers. It focuses on system boundaries, report period, control matrix mapping, design, and Type II operating-effectiveness evidence.

Use it for:

- mapping firewall policy, NAT, VPN, WAF, security groups, logging, access review, change management, vendor access, and incident-response evidence to SOC 2 controls
- reviewing Trust Services Criteria support such as CC6 logical access, CC7 system operations, CC8 change management, CC9 risk mitigation, Availability, Confidentiality, and Privacy-supporting controls
- preparing SOC 2 evidence requests, control descriptions, findings, sample expectations, and exception remediation
- adding short SOC 2 evidence markers to firewall descriptions/tags where supported

Reference files:

```text
skills/soc2-ngfw-compliance/SKILL.md
```

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

### srx-nat

`srx-nat` is an operational playbook for Juniper SRX NAT. It was synthesized from Juniper Community NAT/CGN/NAT64 articles, Juniper NAT documentation, and support troubleshooting guides. It includes source attribution plus extracted or condensed references under `references/`.

Use it for:

- source NAT with interface or pool translation
- destination NAT and static NAT for published servers and overlapping networks
- NAT rule processing order, rule-set specificity, and first-match behavior
- proxy ARP decisions for public NAT addresses
- hairpin NAT / NAT reflection for inside clients using public server addresses
- NAT64 with DNS64 using `static-nat inet` and IPv4 source NAT
- CGN/PBA design, paired address pooling, persistent NAT, and pool exhaustion troubleshooting
- `address-persistent` symptoms, removal, and TCP MSS caveats
- source/destination/static NAT troubleshooting with counters, sessions, and traceoptions

Key verification commands:

```text
show configuration security nat | display set
show security nat source rule all
show security nat destination rule all
show security nat static rule all
show security nat source pool all
show security nat proxy-arp
show security flow session source-prefix <source> extensive
show security flow session destination-prefix <destination> extensive
```

Reference files:

```text
skills/srx-nat/SKILL.md
skills/srx-nat/references/source-index.md
skills/srx-nat/references/source-dns64-and-nat64-on-srx-series.md
skills/srx-nat/references/source-srx4600-cgn-configuration-breakdown.md
skills/srx-nat/references/source-security-nat-overview.md
skills/srx-nat/references/source-troubleshoot-source-nat.md
skills/srx-nat/references/source-troubleshoot-destination-nat.md
```

### srx-policy

`srx-policy` is an SRX security policy design, migration, and troubleshooting playbook for Junos 23.x+ non-Branch SRX platforms. It strongly recommends `security policies global` for greenfield deployments and migrations from other firewall vendors, using zone-to-zone policy mainly for legacy compatibility or tightly scoped exceptions. For URL filtering on supported Junos 23.4R1+ SRX/cSRX targets, it recommends Juniper NextGen Web Filtering (NGWF / `ng-juniper`) as the preferred path and treats Enhanced Web Filtering (EWF / `juniper-enhanced`) as an existing-estate or compatibility path unless NGWF is unavailable.

Use it for:

- deciding between `security policies global` and legacy `from-zone ... to-zone ...` policy contexts
- converting vendor rulebases into ordered SRX global policies with `match from-zone` and `match to-zone`
- global address-book and application/application-set design
- AppID / Application Firewall rule-sets and policy attachment
- NGWF-first web filtering design, EWF compatibility, EWF-to-NGWF migration cautions, UTM profile attachment, and verification
- SecIntel and ATP placement relative to deterministic base policy
- policy logging, counts, final deny, session verification, and commit safety
- troubleshooting policy hit-counts, AppFW counters, web-filtering counters, and flow sessions

Key verification commands:

```text
show configuration security policies global | display set
show security policies hit-count global
show security flow session source-prefix <source> extensive
show security application-firewall rule-set <rule-set-name>
show security utm web-filtering status
show security utm web-filtering statistics
show log messages | match -i "secintel|atp|utm|web-filter|threat"
```

Web filtering guidance in this skill is intentionally opinionated but conservative:

- Prefer NGWF for Junos 23.4R1+ greenfield and vendor-migration designs when platform, release, license, and cloud connectivity support it.
- Keep EWF for existing-estate continuity, older unsupported deployments, or documented constraints.
- Do not call EWF formally deprecated unless current Juniper documentation says so.
- Plan EWF-to-NGWF migration during downtime, preserve policy names during migration, and verify `show security utm web-filtering category migrate-to-ng-juniper status`.
- Verify engine type, license, cloud reachability, DNS/routing, UTM policy attachment, hit counts, and logs after change.

Reference files:

```text
skills/srx-policy/SKILL.md
skills/srx-policy/references/source-index.md
skills/srx-policy/references/source-configuring-security-policies-junos-os.md
skills/srx-policy/references/source-security-global-policies.md
skills/srx-policy/references/source-security-policy-applications-and-application-sets-junos-os.md
skills/srx-policy/references/source-juniper-srx-enhanced-web-filtering-configuration.md
skills/srx-policy/references/ngwf-vs-ewf-research.md
skills/srx-policy/references/source-secintel-feeds-overview-and-benefits.md
```

### srx-mnha

`srx-mnha` is a conservative SRX Multi-Node High Availability research/playbook skill built from five Juniper Community TechPosts. The source articles contained some conflicting or ambiguous details, so the main skill intentionally includes only non-conflicting operational guidance and keeps the extracted source material in `references/` for provenance.

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
skills/srx-mnha/references/source-mnha-ipsec-and-multiple-routing-instances.md
skills/srx-mnha/references/source-srx-from-chassis-cluster-to-mnha.md
skills/srx-mnha/references/mnha-config-patterns.md
```

### srx-autovpn-full-tunnel

`srx-autovpn-full-tunnel` is an SRX AutoVPN hub-and-spoke playbook for full-tunnel backhaul, where spokes send all non-local traffic up the tunnel and the hub provides centralized internet egress. It covers the dynamic `group-ike-id` gateway, traffic selectors + Auto Route Insertion (ARI), the single shared `st0.0`, hub source-NAT egress, spoke-to-spoke hairpin, and the anti-recursion route. Derived (with attribution) from Jason Anderson's `srx-autovpn-backhaul-public` lab.

Reference files:

```text
skills/srx-autovpn-full-tunnel/SKILL.md
skills/srx-autovpn-full-tunnel/references/source-index.md
skills/srx-autovpn-full-tunnel/references/source-design-summary.md
```

### srx-ipsec-hub-spoke

`srx-ipsec-hub-spoke` is an SRX static point-to-point route-based IPsec hub-and-spoke playbook with the same full-tunnel backhaul, but using one explicit IKE gateway, IPsec VPN, `st0` unit, and static route per spoke (no traffic selectors, no ARI) — routing alone scopes each tunnel. It covers per-spoke peering by WAN IP, hub source-NAT egress, spoke-to-spoke hairpin across `st0` units, the anti-recursion route, and when to switch to AutoVPN. Derived (with attribution) from Jason Anderson's `srx-p2p-ipsec-public` lab.

Reference files:

```text
skills/srx-ipsec-hub-spoke/SKILL.md
skills/srx-ipsec-hub-spoke/references/source-index.md
skills/srx-ipsec-hub-spoke/references/source-design-summary.md
```


## Shared Schema Maintenance

The `intermediate-schema.md` file is intentionally duplicated in each `parsing-*` skill so every skill remains self-contained when copied alone. Treat `skills/parsing-srx-configs/references/intermediate-schema.md` as the canonical editing copy, then sync the same content to the other parser skills and run:

```bash
python3 scripts/check-shared-schema.py
```

See `skills/SHARED-SCHEMA.md` for the full policy.

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
rm -rf ~/.claude/skills/srx-nat
rm -rf ~/.claude/skills/srx-policy
rm -rf ~/.claude/skills/srx-autovpn-full-tunnel
rm -rf ~/.claude/skills/srx-ipsec-hub-spoke
rm -rf ~/.claude/skills/pci-ngfw-compliance
rm -rf ~/.claude/skills/hipaa-ngfw-compliance
rm -rf ~/.claude/skills/cmmc-nist-800-171-ngfw-compliance
rm -rf ~/.claude/skills/cis-controls-ngfw-compliance
rm -rf ~/.claude/skills/iso27001-ngfw-compliance
rm -rf ~/.claude/skills/soc2-ngfw-compliance
rm -rf ~/.claude/skills/firewall-best-practices-audit
rm -rf ~/.claude/skills/firewall-config-conversion
rm -rf ~/.claude/skills/firewall-config-diff

rm -rf ~/.hermes/skills/devops/pci-ngfw-compliance
rm -rf ~/.hermes/skills/devops/hipaa-ngfw-compliance
rm -rf ~/.hermes/skills/devops/cmmc-nist-800-171-ngfw-compliance
rm -rf ~/.hermes/skills/devops/cis-controls-ngfw-compliance
rm -rf ~/.hermes/skills/devops/iso27001-ngfw-compliance
rm -rf ~/.hermes/skills/devops/soc2-ngfw-compliance
rm -rf ~/.hermes/skills/devops/srx-dynamic-ip-feed
rm -rf ~/.hermes/skills/devops/srx-mpls-in-flow
rm -rf ~/.hermes/skills/devops/srx-mnha
rm -rf ~/.hermes/skills/devops/srx-nat
rm -rf ~/.hermes/skills/devops/srx-policy
rm -rf ~/.hermes/skills/devops/srx-autovpn-full-tunnel
rm -rf ~/.hermes/skills/devops/srx-ipsec-hub-spoke
rm -rf ~/.hermes/skills/devops/firewall-best-practices-audit
rm -rf ~/.hermes/skills/devops/firewall-config-conversion
rm -rf ~/.hermes/skills/devops/firewall-config-diff
```
