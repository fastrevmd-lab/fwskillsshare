# parsing-fortinet-configs

Claude Code skill for parsing and analyzing **Fortinet FortiGate / FortiOS** firewall configurations.

## What it does

Parses the hierarchical `config/edit/set/next/end` block format from `show full-configuration` or backup exports and extracts:

- Zones and interfaces (with interface-as-zone merging)
- Address objects (ipmask, iprange, fqdn, geography, wildcard)
- Address groups
- Service objects and service groups
- Security policies
- VIPs (destination NAT) and IP pools (source NAT)
- UTM/security profiles (antivirus, URL filtering, IPS, SSL inspection, DLP)
- IPv6 address objects/groups and routes
- Schedules
- HA configuration
- Multi-VDOM support
- VPN IPsec phase1/phase2
- Detailed OSPF/OSPFv3/BGP
- DHCP server with pools and reservations
- System global/DNS/NTP
- Admin users
- FortiLink filtering
- Allowaccess classification
- Residual config capture
- Version detection

## Auto-trigger keywords

`FortiGate`, `FortiOS`, `Fortinet`, `VDOM`, `config firewall policy`, `config firewall address`, `config firewall service custom`, `config system interface`, `edit`, `set srcintf`, `set dstintf`, `set srcaddr`, `set dstaddr`, `set action accept`, `set utm-status enable`, `set av-profile`, `set webfilter-profile`, `set ips-sensor`

## Manual invocation

```
/parsing-fortinet-configs
```

## Installation

```bash
cp -r parsing-fortinet-configs ~/.claude/skills/
```

## Security audit checks

- Unused address/service objects
- Shadowed policies
- Overly permissive rules
- Missing logging on permit policies
- Disabled policies still in config
- VIP reference validation
- Geography object usage warnings
- Implicit intra-zone rule generation
- Weak VPN algorithms

## File structure

```
parsing-fortinet-configs/
├── SKILL.md                          # Main skill instructions
├── references/
│   ├── config-format.md              # FortiOS block syntax, predefined services
│   ├── intermediate-schema.md        # Vendor-neutral output schema
│   └── parsing-patterns.md           # Interface-zone merging, mask conversion
└── examples/
    └── sample-parse.md               # Worked example with input/output
```
