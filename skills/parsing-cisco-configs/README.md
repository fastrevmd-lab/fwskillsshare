# parsing-cisco-configs

Claude Code skill for parsing and analyzing **Cisco ASA and FTD** LINA running configurations. For FMC/FDM JSON exports, use `parsing-firepower-configs`.

## What it does

Parses line-oriented config output from `show running-config` and extracts:

- Interfaces and security zones (via `nameif` / `security-level`)
- Network objects and object groups
- Service objects and groups
- Access lists (ACLs) and access group bindings
- NAT rules (object NAT and twice NAT)
- IPv6 addresses and routes
- Static routes
- DHCP server/relay
- DNS/NTP servers
- Admin users with SSH keys
- Management access protocols
- Time ranges and schedules
- HA/failover configuration
- Threat detection settings
- VPN/IPsec (IKE policies, proposals, VTI tunnel assembly)
- Detailed OSPF/BGP
- LAG/port-channel
- Tunnel/loopback interfaces
- ACL remarks
- Residual config capture

## Auto-trigger keywords

`ASA`, `FTD`, `Cisco`, `access-list`, `access-group`, `object network`, `object-group`, `object service`, `nameif`, `security-level`, `nat (`, `interface GigabitEthernet`, `interface Management`, `failover`, `threat-detection`

## Manual invocation

- **Claude Code / Hermes**: `/parsing-cisco-configs`
- **Codex**: `$parsing-cisco-configs`

## Installation

Use the repository installer to install into one or more runtimes:

```bash
# Install to Claude Code
./install.sh --skill parsing-cisco-configs --target claude

# Install to Codex
./install.sh --skill parsing-cisco-configs --target codex

# Install to Hermes
./install.sh --skill parsing-cisco-configs --target hermes

# Install to all three
./install.sh --skill parsing-cisco-configs --target all

# Or install the whole parsers family
./install.sh --family parsers --target all
```

Manual installation (copy the skill directory to the runtime's skills directory):

```bash
# Claude Code
cp -r parsing-cisco-configs ~/.claude/skills/

# Codex
cp -r parsing-cisco-configs ~/.agents/skills/

# Hermes
cp -r parsing-cisco-configs ~/.hermes/skills/devops/
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
- Weak VPN algorithms (DES/3DES, MD5, DH ≤ 5)

## File structure

```
parsing-cisco-configs/
├── SKILL.md                          # Main skill instructions
├── agents/
│   └── openai.yaml                   # Codex agent manifest
└── references/
    ├── config-format.md              # Vendor config syntax reference
    ├── intermediate-schema.md        # Vendor-neutral output schema
    ├── parsing-patterns.md           # Edge cases, port mappings
    ├── runtime-intake.md             # Interactive question catalog for ambiguous requests
    ├── example-sample-parse.md       # Worked example with input/output
    ├── fixture-minimal-input.md      # Minimal test fixture (input)
    └── fixture-expected-output.json  # Minimal test fixture (expected output)
```
