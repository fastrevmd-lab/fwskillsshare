# parsing-cisco-configs

Claude Code skill for parsing and analyzing **Cisco ASA and FTD** firewall configurations.

## What it does

Parses line-oriented config output from `show running-config` and extracts:

- Interfaces and security zones (via `nameif` / `security-level`)
- Network objects and object groups
- Service objects and groups
- Access lists (ACLs) and access group bindings
- NAT rules (object NAT and twice NAT)
- Static routes
- Time ranges and schedules
- HA/failover configuration
- Threat detection settings
- VPN configuration

## Auto-trigger keywords

`ASA`, `FTD`, `Cisco`, `access-list`, `access-group`, `object network`, `object-group`, `object service`, `nameif`, `security-level`, `nat (`, `interface GigabitEthernet`, `interface Management`, `failover`, `threat-detection`

## Manual invocation

```
/parsing-cisco-configs
```

## Installation

```bash
cp -r parsing-cisco-configs ~/.claude/skills/
```

## Security audit checks

- Unused network/service objects
- Shadowed ACL entries (rules that never match)
- Overly permissive rules (`permit ip any any`)
- Missing logging on permit rules
- Inactive entries
- Duplicate objects
- Empty object groups
- Unbound ACLs (not applied to any interface)

## File structure

```
parsing-cisco-configs/
├── SKILL.md                          # Main skill instructions
├── references/
│   ├── config-format.md              # ASA config syntax reference
│   ├── intermediate-schema.md        # Vendor-neutral output schema
│   └── parsing-patterns.md           # Edge cases, port mappings
└── examples/
    └── sample-parse.md               # Worked example with input/output
```
