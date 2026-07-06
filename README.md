# Firewall Skills For Network & Secuirty Engineers

![skills](https://img.shields.io/badge/skills-21-1f6feb) ![reviewed](https://img.shields.io/badge/reviewed-21%2F21-2ea043) ![license](https://img.shields.io/badge/license-MIT-blue) ![vendors](https://img.shields.io/badge/vendors-Cisco%20%C2%B7%20Fortinet%20%C2%B7%20Palo%20Alto%20%C2%B7%20Juniper-8957e5)

Agent skills for the firewall work you actually do — parsing, auditing, converting, and running Juniper SRX — not vibe configuring.

Firewall work is unforgiving. A confidently wrong `access-list` line, a Junos stanza that won't commit, a compliance claim you can't back up in an audit — these aren't cosmetic. Coding agents are astonishingly good at producing *plausible* firewall config and astonishingly bad at knowing when it's wrong.

These skills exist to close that gap. They pin the agent to vendor syntax that's been checked against real devices, to one shared schema so four vendors speak the same language, and to control-to-evidence maps that don't overpromise. They're small, self-contained, and composable — copy the two you need or all 21. Hack around with them. Make them your own.

> **Unofficial / community project.** Not affiliated with, endorsed by, or supported by Cisco, Fortinet, Palo Alto Networks, Juniper Networks, or HPE. See [License and Provenance](#license-and-provenance) for the full notice and the trademark disclaimer.

## Quickstart (30-second setup)

1. Run the installer and pick what you want:

```bash
curl -fsSL https://raw.githubusercontent.com/fastrevmd-lab/fwskillsshare/main/install.sh | bash
```

2. Choose your skills (space/numbers to toggle, `a` for all) and where to install them — **Claude Code** (`~/.claude/skills/`), **Hermes**, or both.

3. Restart Claude Code.

4. Done. Paste a config or name a vendor and the right skill loads itself.

Prefer flags, or installing from a clone? See [Installation](#installation).

## Why These Skills Exist

I built these to fix the failure modes I kept hitting when I let Claude Code, Codex, and other agents touch firewalls.

### #1: The Agent Invents CLI That Won't Commit

> "It Has To Work."
>
> Ross Callon, [RFC 1925 — The Twelve Networking Truths](https://www.rfc-editor.org/rfc/rfc1925), truth (1)

**The Problem.** Ask an agent for an SRX ADVPN config or a Junos 24.4R1 IKE gateway and you'll get something that *reads* perfectly and then throws a commit error — or worse, commits and silently doesn't forward. The model has seen a decade of blog posts, including the wrong ones and the ones for the wrong release.

**The Fix** is playbooks pinned to syntax that's been proven on real hardware. The SRX skills carry the gotchas that only show up in production: the Junos 24.4R1+ `IKEv2 with authentication-method pre-shared-key is not allowed` commit error, the `Remote-ip 0.0.0.0/0 in traffic-selector is not supported` split, the ADVPN `No public key found` IKE_AUTH failure root-caused to the dynamic cert-gateway responder path. Disputed syntax was settled by commit-checking on a live vSRX 24.4R1, not by vibes.

Reach for [`srx-policy`](./skills/srx-policy/), [`srx-nat`](./skills/srx-nat/), [`srx-mnha`](./skills/srx-mnha/), [`srx-advpn`](./skills/srx-advpn/) and friends whenever you're designing or debugging real Junos.

### #2: Every Vendor Speaks A Different Dialect

> "All problems in computer science can be solved by another level of indirection."
>
> David Wheeler

**The Problem.** A Cisco ACL, a FortiGate policy block, a PAN-OS `<entry>`, and an SRX `set security` line all express the same idea four incompatible ways. Ask an agent to compare or convert them and it hand-waves the parts that don't line up.

**The Fix** is a shared language. The four [`parsing-*`](./skills/) skills normalize every vendor into **one vendor-neutral intermediate JSON schema** — zones, objects, policies, NAT, routing, VPN, HA, the lot — with a 240+ entry canonical L7 application map and confidence scores. Once a config is in the schema, cross-vendor [audit](./skills/firewall-best-practices-audit/), [conversion](./skills/firewall-config-conversion/), and [diff](./skills/firewall-config-diff/) all operate by *meaning*, not text. Features with no equivalent are flagged, never silently dropped.

This is the piece that makes the rest composable. See the [Intermediate Schema](#intermediate-schema) below.

### #3: "Is It Compliant?" Gets A Confident, Unfounded Yes

> "Trust, but verify."
>
> Russian proverb

**The Problem.** Point an agent at a firewall and ask if it's "PCI compliant" and it will happily tell you yes. That answer is worthless to a QSA, and dangerous to you. A firewall *supports* evidence for a control; it is never itself "certified."

**The Fix** is six compliance playbooks ([PCI](./skills/pci-ngfw-compliance/), [HIPAA](./skills/hipaa-ngfw-compliance/), [CMMC / NIST 800-171](./skills/cmmc-nist-800-171-ngfw-compliance/), [CIS](./skills/cis-controls-ngfw-compliance/), [ISO 27001](./skills/iso27001-ngfw-compliance/), [SOC 2](./skills/soc2-ngfw-compliance/)) that map firewall capabilities to specific control evidence, produce assessor-ready findings and gap lists, and are explicit at every turn that compliance is assessed for the *environment and program*, not conferred by the box. They tell you what evidence to collect and where the gaps are — the honest version of the answer.

### #4: Rulebases Rot, And Agents Accelerate The Rot

> "Complexity is the worst enemy of security."
>
> Bruce Schneier

**The Problem.** Every rulebase drifts toward `any-any`, shadowed rules, orphaned objects, and plaintext management. Agents make firewall changes faster, which means they make the rot faster too, unless something keeps them honest.

**The Fix** is [`firewall-best-practices-audit`](./skills/firewall-best-practices-audit/) — overly permissive and shadowed/redundant rules, missing deny-all and logging, exposed telnet/http/SNMPv1-2c, weak IKE/IPsec crypto, device-plane hardening, unused objects — and [`firewall-config-diff`](./skills/firewall-config-diff/) for drift and HA-pair parity. Prioritized findings with severity and confidence, vendor-neutral plus source-vendor remediation. Run them before you ship a change, not after the incident.

### Summary

Firewall fundamentals don't get easier in the AI age — the blast radius just gets bigger. These skills are my attempt to hand the agent the discipline: verified syntax, a shared schema, honest compliance mapping, and a hygiene checklist. Use them, break them, and make them yours.

## Reference

**21 skills** across four families. All of them are **model-invoked** — the agent reaches for them automatically when it sees vendor keywords, an SRX operational topic, or compliance language in your message or a pasted config — and every one is also typeable as a slash command (`/srx-nat`) when you want to force it.

### Config parsers

Normalize a vendor config into the shared intermediate schema. Everything else composes on top.

- **[parsing-cisco-configs](./skills/parsing-cisco-configs/)** — Cisco ASA & FTD (`show running-config`): access-lists, object/object-group, NAT, failover, port-to-app inference.
- **[parsing-fortinet-configs](./skills/parsing-fortinet-configs/)** — FortiGate / FortiOS (`show full-configuration`): the config/edit/set block format, VDOMs, UTM profiles, compound IPsec proposals.
- **[parsing-palo-configs](./skills/parsing-palo-configs/)** — Palo Alto PAN-OS & Panorama: XML *or* flat set-format, vsys, app-default decomposition, device-groups.
- **[parsing-srx-configs](./skills/parsing-srx-configs/)** — Juniper SRX / Junos: `display set` or curly-brace, address-book migration to global, `junos-*` app mapping, routing-instances.

### SRX operational playbooks

Actionable Junos playbooks — commands, design guidance, verification, troubleshooting matrices, source attribution.

- **[srx-policy](./skills/srx-policy/)** — Global vs zone-to-zone policy on 23.x+, AppID/AppFW, NGWF-first web filtering, SecIntel, ATP, hit-count troubleshooting.
- **[srx-nat](./skills/srx-nat/)** — Source/destination/static NAT, NAT64/DNS64, CGN/PBA, persistent NAT, hairpin, proxy-ARP, session verification.
- **[srx-mnha](./skills/srx-mnha/)** — Multi-Node High Availability: routed/default-gateway/hybrid modes, SRGs, ICL/ICD, eBGP/BFD failover, VIPs, DHCP caveats.
- **[srx-advpn](./skills/srx-advpn/)** — Auto Discovery VPN dynamic spoke-to-spoke shortcuts, suggester/partner roles, multipoint st0, OSPF p2mp, the cert-auth requirement and the `No public key found` fix.
- **[srx-autovpn-full-tunnel](./skills/srx-autovpn-full-tunnel/)** — AutoVPN hub-and-spoke full-tunnel backhaul: dynamic `group-ike-id`, traffic selectors + ARI, shared st0.0, anti-recursion route.
- **[srx-ipsec-hub-spoke](./skills/srx-ipsec-hub-spoke/)** — Static point-to-point route-based IPsec hub-and-spoke, one explicit tunnel per spoke, hub source-NAT egress, spoke-to-spoke hairpin.
- **[srx-mpls-in-flow](./skills/srx-mpls-in-flow/)** — MPLS L3VPN in flow mode (secure PE/CPE): decoupled `family mpls` packet-based with inet/inet6 flow-mode, VRF-aware policy/NAT/AppID.
- **[srx-dynamic-ip-feed](./skills/srx-dynamic-ip-feed/)** — Dynamic IP objects from HTTPS feed servers: `.tgz` bundles, cert validation, basic-auth / mTLS, `ipfd` log interpretation.

### Cross-vendor tooling

Vendor-neutral, driven off the parsed schema.

- **[firewall-best-practices-audit](./skills/firewall-best-practices-audit/)** — Rulebase hygiene independent of any framework: any-any, shadowed/orphaned rules, missing deny/logging, exposed plaintext services, weak crypto, device-plane hardening.
- **[firewall-config-conversion](./skills/firewall-config-conversion/)** — Migrate between Cisco/FortiGate/Palo/SRX with a per-section fidelity report (converted / caveats / manual). A reviewed draft, never production-ready.
- **[firewall-config-diff](./skills/firewall-config-diff/)** — Compare two configs by meaning (order- and name-insensitive) — same-vendor drift & HA parity, or cross-vendor migration validation.

### NGFW compliance playbooks

Map firewall capability to control evidence — assessor/auditor output templates, description/tag markers, honest scoping.

- **[pci-ngfw-compliance](./skills/pci-ngfw-compliance/)** — PCI DSS v4.0.1: CDE segmentation, Requirement 1 network security controls, six-month rule review, QSA/ROC/SAQ evidence.
- **[hipaa-ngfw-compliance](./skills/hipaa-ngfw-compliance/)** — HIPAA Security Rule (45 CFR 164.312): ePHI segmentation, access/audit controls, transmission security, BAA considerations.
- **[cmmc-nist-800-171-ngfw-compliance](./skills/cmmc-nist-800-171-ngfw-compliance/)** — CMMC Level 2 / NIST SP 800-171: CUI enclave scoping, boundary protection, SSP boundary language, POA&M-style gaps.
- **[cis-controls-ngfw-compliance](./skills/cis-controls-ngfw-compliance/)** — CIS Controls v8/v8.1: secure configuration, network infrastructure management, IG1/IG2/IG3 safeguards, audit evidence.
- **[iso27001-ngfw-compliance](./skills/iso27001-ngfw-compliance/)** — ISO/IEC 27001:2022 ISMS & Annex A (A.8.20–A.8.23), Statement of Applicability support, supplier access, corrective actions.
- **[soc2-ngfw-compliance](./skills/soc2-ngfw-compliance/)** — SOC 2 Trust Services Criteria (CC6/CC7/CC8), Type I/II examinations, operating-effectiveness samples.

---

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
--all                 Install all 21 skills
--skill NAME          Install a specific skill (repeatable)
--family NAME         parsers | srx | tooling | compliance (repeatable)
--target WHERE        claude | hermes | both   (default: prompt; claude with -y)
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
./install.sh --family parsers --family srx      # just the parsers + SRX playbooks
./install.sh --skill parsing-srx-configs --skill srx-nat -y
./install.sh --list                             # see what's available
```

### Manual install

The skills are plain directories — copy the ones you want:

```bash
git clone git@github.com:fastrevmd-lab/fwskillsshare.git

# All of them
cp -r fwskillsshare/skills/* ~/.claude/skills/

# Or a single skill
cp -r fwskillsshare/skills/srx-mnha ~/.claude/skills/
```

For **Hermes**, copy into your local Hermes skills tree (usually `~/.hermes/skills/devops/`) and confirm with `hermes skills list`:

```bash
mkdir -p ~/.hermes/skills/devops
cp -r fwskillsshare/skills/* ~/.hermes/skills/devops/
hermes skills list | grep -E 'parsing-|srx-|firewall-|-ngfw-compliance'
```

Restart Claude Code after installing. Skills auto-trigger when they detect vendor-specific keywords, SRX operational topics, or PCI/HIPAA/CMMC/NIST 800-171/CIS/ISO 27001/SOC 2 compliance language in your messages or pasted configs.

### Managing context

Skill *bodies* only load when a skill is invoked, but each skill's short description stays in context so the agent knows when to reach for it. If you rarely use certain skills (e.g. compliance frameworks you don't work with), you can drop just their descriptions from context while keeping them invocable, via `skillOverrides` in `~/.claude/settings.json`:

```json
{ "skillOverrides": { "soc2-ngfw-compliance": "name-only" } }
```

`"name-only"` keeps the skill listed and invocable but hides its description; `"user-invocable-only"` hides it from the model entirely (slash-command only); `"off"` hides it completely.

## Usage

### What you can do

- **Parse** — Extract all objects, policies, NAT rules, and routes into structured JSON
- **Audit** — Find unused objects, shadowed rules, overly permissive policies, missing logging
- **Convert** — Transform configs between vendors (e.g., SRX to PAN-OS)
- **Compare** — Diff two configs by meaning, not text
- **Summarize** — Get a high-level overview of zones, policy counts, and security profiles
- **Operate SRX dynamic feeds** — Configure, validate, and troubleshoot SRX dynamic-address feed servers
- **Design SRX MPLS in flow mode** — Keep inet/inet6 in stateful flow mode for policy, NAT, and AppID while `family mpls` is packet-based
- **Design SRX MNHA** — Reason about MNHA modes, SRGs, ICL/ICD, eBGP/BFD failover, VIPs, and DHCP caveats
- **Operate SRX NAT** — Source/destination/static NAT, NAT64/DNS64, CGN/PBA, persistent NAT, hairpin, proxy ARP
- **Design SRX security policy** — Prefer `security policies global` for greenfield/migrations, then layer AppID/AppFW, NGWF-first web filtering, SecIntel, ATP
- **Assess compliance evidence** — Map NGFW policies, NAT, zones, logging, IDS/IPS, and segmentation to PCI / HIPAA / CMMC-NIST 800-171 / CIS / ISO 27001 / SOC 2 evidence expectations

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

# Compliance review (any of the six frameworks)
"Review this firewall export for PCI DSS CDE segmentation evidence and recommend policy/NAT/zone description markers"
"Review this NGFW design for HIPAA Security Rule ePHI access control, audit logging, and transmission security"
"Review this firewall estate against CIS Controls v8 for secure configuration, logging, and vendor access"
```

## Tips

- Paste the **full config** — partial configs may produce unresolved reference warnings
- Use the appropriate show command output for each vendor:
  - **Cisco ASA**: `show running-config`
  - **FortiGate**: `show full-configuration`
  - **PAN-OS**: XML config export or `show config flat` (set-format)
  - **SRX**: `show configuration | display set` or `show configuration`
  - **SRX dynamic feeds**: `show security dynamic-address summary`, `show security dynamic-address`, `show log messages | match ipfd`
  - **SRX MPLS in Flow**: `show security flow status`, `show route table bgp.l3vpn.0`, `show route table <vrf>.inet.0`, `show ldp neighbor`, `show mpls interface`, `show security flow session extensive`, `show security policies hit-count`
  - **SRX MNHA**: `show chassis high-availability information`, `show chassis high-availability services-redundancy-group <id>`, `show security flow session`, `show bgp summary`, `show bfd session`
  - **SRX NAT**: `show security nat source/destination/static rule all`, `show security nat source pool all`, `show security nat proxy-arp`, `show security flow session ... extensive`
  - **SRX security policy**: `show configuration security policies global | display set`, `show security policies hit-count global`, `show security application-firewall rule-set <name>`, `show security utm web-filtering status/statistics`
  - **Compliance reviews**: collect the firewall policy/NAT/zone/VPN/object exports plus the framework-specific evidence (CDE/ePHI/CUI/ISMS-scope diagrams, rule-review records, logging/SIEM evidence, change tickets, segmentation/pen-test results) — each compliance skill lists exactly what it needs
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

## Compliance Skills (detail)

### pci-ngfw-compliance

`pci-ngfw-compliance` is a PCI DSS v4.0.1 NGFW/firewall assessment playbook. It explains that an NGFW can support PCI DSS network security control evidence, but the device is not independently "PCI compliant."

Use it for:

- mapping firewall policy, NAT, zones, IDS/IPS, WAF/WAAP, logging, and segmentation controls to PCI DSS evidence expectations
- reviewing CDE inbound/outbound restrictions, default deny, payment processor paths, and public-facing service exposure
- preparing assessor-ready evidence requests, findings, and gap-analysis summaries
- adding short PCI evidence markers to firewall descriptions/tags for policies, NAT, zones, objects, and profiles where supported

### hipaa-ngfw-compliance

`hipaa-ngfw-compliance` is a HIPAA Security Rule NGFW/firewall assessment playbook. It explains that an NGFW can support reasonable and appropriate safeguards for ePHI, but HIPAA compliance is assessed at the covered entity or business associate program/environment level.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, WAF/WAAP, logging, and segmentation controls to HIPAA Security Rule safeguards
- reviewing ePHI access control, audit controls, person/entity authentication, transmission security, incident response, documentation, and business associate/vendor access evidence
- preparing compliance-ready evidence requests, findings, and risk-treatment recommendations
- adding short HIPAA evidence markers to firewall descriptions/tags where supported

### cmmc-nist-800-171-ngfw-compliance

`cmmc-nist-800-171-ngfw-compliance` is a CMMC Level 2 / NIST SP 800-171 NGFW/firewall assessment playbook. It explains that an NGFW can support CUI protection requirements, but CMMC/NIST 800-171 compliance is assessed at the contractor environment and CUI protection program level, not by certifying the firewall product alone.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, logging, segmentation, and remote-access controls to NIST 800-171 / CMMC evidence expectations
- reviewing CUI enclave scope, CUI data flows, boundary protection, external connections, public-system separation, audit controls, and system security plan evidence
- preparing assessor-ready evidence requests, findings, POA&M-style gaps, and remediation recommendations
- adding short CMMC/CUI evidence markers to firewall descriptions/tags where supported

### cis-controls-ngfw-compliance

`cis-controls-ngfw-compliance` is a CIS Critical Security Controls v8/v8.1 NGFW/firewall assessment playbook. It explains that an NGFW can support CIS safeguards, but CIS alignment is assessed across the implemented environment and security program, not by certifying the firewall product alone.

Use it for:

- mapping firewall policy, NAT, VPN, zones, IDS/IPS, logging, secure configuration, vulnerability management, and network monitoring controls to CIS Controls evidence expectations
- reviewing network infrastructure inventory, secure firewall baselines, administrative access, service-provider/vendor access, logging, malware/threat defenses, backup/recovery, incident response, and penetration/segmentation testing evidence
- preparing practical CIS-aligned evidence requests, findings, prioritized remediation actions, and risk-based roadmap items
- adding short CIS evidence markers to firewall descriptions/tags where supported

### iso27001-ngfw-compliance

`iso27001-ngfw-compliance` is an ISO/IEC 27001:2022 ISMS and Annex A firewall-control playbook. It explains that an NGFW can support selected controls, but certification applies to the scoped ISMS and its risk assessment, Statement of Applicability, policies, operation, audit, and continual-improvement evidence.

Use it for:

- mapping firewall policy, NAT, VPN, zones, logging, secure configuration, supplier access, change management, backups, and incident response to SoA/risk-treatment evidence
- reviewing network security, access control, configuration management, logging/monitoring, supplier access, vulnerability management, and corrective-action records
- preparing ISO audit evidence requests, firewall findings, corrective actions, and management-system caveats
- adding short ISO/ISMS evidence markers to firewall descriptions/tags where supported

### soc2-ngfw-compliance

`soc2-ngfw-compliance` is a SOC 2 Trust Services Criteria firewall-control playbook for service organizations, SaaS platforms, MSPs, and cloud providers. It focuses on system boundaries, report period, control matrix mapping, design, and Type II operating-effectiveness evidence.

Use it for:

- mapping firewall policy, NAT, VPN, WAF, security groups, logging, access review, change management, vendor access, and incident-response evidence to SOC 2 controls
- reviewing Trust Services Criteria support such as CC6 logical access, CC7 system operations, CC8 change management, CC9 risk mitigation, Availability, Confidentiality, and Privacy-supporting controls
- preparing SOC 2 evidence requests, control descriptions, findings, sample expectations, and exception remediation
- adding short SOC 2 evidence markers to firewall descriptions/tags where supported

## SRX Operational Skills (detail)

### srx-dynamic-ip-feed

`srx-dynamic-ip-feed` is an operational playbook for Juniper SRX dynamic IP objects backed by HTTPS feed servers, synthesized from a Juniper Community TechPost with source attribution under `references/source-extract.md`.

Use it for: configuring `security dynamic-address feed-server`; building `.tgz` bundle archive feeds and mapping `feed-name` paths; exposing feeds as policy objects; validating HTTPS server certificates with SRX PKI / SSL initiation profiles; HTTP basic-auth and mutual TLS client-certificate patterns; checking update behavior via access logs; troubleshooting `ipfd` download/auth/certificate/path errors; and `session-scan` / routing-instance reachability.

Key verification commands:

```text
show security dynamic-address summary
show security dynamic-address
show log messages | match ipfd
```

### srx-mpls-in-flow

`srx-mpls-in-flow` is an SRX MPLS L3VPN operational playbook synthesized from two Juniper Community TechPosts. It covers the Junos 24.2R1+ model where `family mpls` is packet-based while `family inet`/`inet6` remain flow-based, allowing stateful security services on MPLS VPN traffic.

Use it for: SRX secure PE / secure CPE designs; decoupled family forwarding controls; VRFs with route distinguishers, route targets, and SRX-required `vrf-table-label`; OSPF/LDP/MP-BGP `family inet-vpn` transport; Junos 24.2-style VRF-aware policy (`source-l3vpn-vrf-group` / `destination-l3vpn-vrf-group`); Junos 25.4R1+ VRF-to-zone mapping; VRF-aware NAT/AppID; PowerMode/RFP decisions; and MTU/label/BGP/policy/NAT troubleshooting.

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

### srx-nat

`srx-nat` is an operational playbook for Juniper SRX NAT, synthesized from Juniper Community NAT/CGN/NAT64 articles, Juniper NAT documentation, and support troubleshooting guides, with source attribution/extracts under `references/`.

Use it for: source NAT with interface or pool translation; destination and static NAT for published servers and overlapping networks; rule processing order, rule-set specificity, and first-match behavior; proxy-ARP decisions; hairpin NAT / NAT reflection; NAT64 with DNS64 (`static-nat inet` + IPv4 source NAT); CGN/PBA design, paired address pooling, persistent NAT, and pool-exhaustion troubleshooting; `address-persistent` symptoms and TCP MSS caveats; and source/destination/static NAT troubleshooting with counters, sessions, and traceoptions.

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

### srx-policy

`srx-policy` is an SRX security policy design, migration, and troubleshooting playbook for Junos 23.x+ non-Branch SRX platforms. It recommends `security policies global` for greenfield deployments and migrations from other vendors, using zone-to-zone policy mainly for legacy compatibility or tightly scoped exceptions. For URL filtering on supported Junos 23.4R1+ targets it recommends NextGen Web Filtering (NGWF / `ng-juniper`) as the preferred path, treating Enhanced Web Filtering (EWF / `juniper-enhanced`) as an existing-estate/compatibility path.

Use it for: deciding between global and legacy `from-zone ... to-zone ...` contexts; converting vendor rulebases into ordered SRX global policies; global address-book and application/application-set design; AppID / Application Firewall rule-sets; NGWF-first web filtering, EWF compatibility, and EWF-to-NGWF migration cautions; SecIntel and ATP placement; policy logging, counts, final deny, and commit safety; and troubleshooting hit-counts, AppFW counters, web-filtering counters, and flow sessions.

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

Web-filtering guidance is intentionally opinionated but conservative: prefer NGWF for Junos 23.4R1+ greenfield/migration when platform, release, license, and cloud connectivity support it; keep EWF for existing-estate continuity or documented constraints; don't call EWF formally deprecated unless current Juniper docs say so; plan EWF-to-NGWF migration during downtime, preserve policy names, and verify `show security utm web-filtering category migrate-to-ng-juniper status`.

### srx-mnha

`srx-mnha` is a conservative SRX Multi-Node High Availability research/playbook skill built from five Juniper Community TechPosts. Because the sources contained some conflicting or ambiguous details, the main skill includes only non-conflicting operational guidance and keeps the extracted source material in `references/` for provenance.

Use it for: comparing chassis cluster and MNHA models; routed/default-gateway/hybrid MNHA design; SRG0 and SRG1+ behavior; ICL design, security, reachability, and liveness checks; ICD/asymmetric-routing caveats; runtime object synchronization and Active/Warm session verification; config synchronization patterns; hybrid MNHA with eBGP, BFD, VIPs, and signal-route export policies; DHCP relay vs local DHCP behavior; and pre-cutover / troubleshooting checklists.

Key verification commands:

```text
show chassis high-availability information
show chassis high-availability services-redundancy-group <id>
show security flow session | match "HA State|HA Wing State|Session ID|In:|Out:"
show bgp summary
show bfd session
show dhcp server binding routing-instance <RI>
```

### srx-autovpn-full-tunnel

`srx-autovpn-full-tunnel` is an SRX AutoVPN hub-and-spoke playbook for full-tunnel backhaul, where spokes send all non-local traffic up the tunnel and the hub provides centralized internet egress. It covers the dynamic `group-ike-id` gateway, traffic selectors + Auto Route Insertion (ARI), the single shared `st0.0`, hub source-NAT egress, spoke-to-spoke hairpin, and the anti-recursion route. Derived (with attribution) from Jason Anderson's `srx-autovpn-backhaul-public` lab.

### srx-ipsec-hub-spoke

`srx-ipsec-hub-spoke` is an SRX static point-to-point route-based IPsec hub-and-spoke playbook with the same full-tunnel backhaul, but using one explicit IKE gateway, IPsec VPN, `st0` unit, and static route per spoke (no traffic selectors, no ARI) — routing alone scopes each tunnel. It covers per-spoke peering by WAN IP, hub source-NAT egress, spoke-to-spoke hairpin across `st0` units, the anti-recursion route, and when to switch to AutoVPN. Derived (with attribution) from Jason Anderson's `srx-p2p-ipsec-public` lab.

### srx-advpn

`srx-advpn` is an SRX Auto Discovery VPN playbook — hub-and-spoke IPsec that dynamically builds direct spoke-to-spoke shortcut tunnels so branch-to-branch traffic bypasses the hub. It covers suggester/partner roles, the shortcut lifecycle, the multipoint `st0` overlay, OSPF p2mp with dynamic-neighbors, the certificate-authentication requirement (IKEv2 PSK with dynamic `ike-user-type` is rejected on modern Junos), PKI enrollment, the chassis-cluster certificate-load gotcha, and the vSRX `No public key found` IKE_AUTH failure root-caused to the dynamic cert-gateway responder path (use per-spoke static-address cert gateways). Includes field notes from a vSRX ADVPN lab under `references/`.

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
# Remove everything the installer put down, from both targets
./install.sh --uninstall --all --target both

# Or remove a single skill
./install.sh --uninstall --skill srx-mnha --target claude
```

Manual equivalent — the skills are just directories, so `rm -rf ~/.claude/skills/<skill-name>` (and `~/.hermes/skills/devops/<skill-name>` for Hermes) removes any of them.

## License and Provenance

Original skill/playbook text in this repository is released under the MIT License; see [LICENSE](LICENSE).

Some `references/` files contain source-derived notes or extracts from Juniper, Cisco, Fortinet, Palo Alto Networks, community posts, blogs, support portals, or other third-party material. Those excerpts are included for local operational context, attribution, and verification. Upstream source material remains subject to its original owners' terms. Before redistributing, bundling commercially, or publishing a derivative catalog, review the upstream licenses/terms and replace long excerpts with citations or concise notes where required.

**Trademark / affiliation disclaimer.** This repository is an independent, community-driven project. It is not affiliated with, endorsed by, sponsored by, or supported by Hewlett Packard Enterprise, Cisco, Palo Alto Networks, Fortinet, or Juniper Networks. "HPE", "Juniper", "Cisco", "Fortinet", "Palo Alto Networks", and "Juniper SRX" are trademarks of their respective owners and are used here only to describe what this software interoperates with. Please direct support and licensing questions about those products to the respective vendors.
