# parsing-srx-configs

Claude Code skill for parsing and analyzing **Juniper SRX / Junos** firewall configurations.

## What it does

Detects and parses two config formats:
1. **Set command format**: `set security zones ...` (from `show configuration | display set`)
2. **Hierarchical curly-brace format**: Nested blocks with `{ }` and `;` terminators

Extracts:

- Zones and address books
- Address objects (ip-prefix, dns-name, range-address, wildcard-address)
- Address groups / address-sets
- Applications and application-sets (with predefined application mapping)
- Security policies (from-zone/to-zone pairs and global policies)
- NAT rules (source, destination, static)
- Schedules
- Static routes, BGP, OSPF/OSPFv3
- HA / chassis cluster configuration
- Screen/IDS protections
- VPN tunnels
- Syslog configuration
- DHCP settings
- Logical-systems and tenant support for multi-context deployments

## Auto-trigger keywords

`SRX`, `Junos`, `Juniper`, `set security`, `security zones`, `address-book`, `applications`, `security policies`, `from-zone`, `to-zone`, `nat rule-set`, `chassis cluster`, `logical-systems`, `routing-instances`

## Manual invocation

```
/parsing-srx-configs
```

## Installation

```bash
cp -r parsing-srx-configs ~/.claude/skills/
```

## Security audit checks

- Unused address/service objects
- Shadowed policies
- Overly permissive rules
- Missing logging on permit policies
- Disabled / deactivated policies
- Duplicate objects
- Empty groups
- Bracket list `[val1 val2]` expansion handling

## File structure

```
parsing-srx-configs/
├── SKILL.md                          # Main skill instructions
├── references/
│   ├── config-format.md              # Set format, hierarchical format, predefined apps
│   ├── intermediate-schema.md        # Vendor-neutral output schema
│   └── parsing-patterns.md           # Name sanitization, IP detection, app mapping
└── examples/
    └── sample-parse.md               # Worked example with input/output
```
