# parsing-srx-configs

Claude Code skill for parsing and analyzing **Juniper SRX / Junos** firewall configurations.

## What it does

Detects and parses two config formats:
1. **Set command format**: `set security zones ...` (from `show configuration | display set`)
2. **Hierarchical curly-brace format**: Nested blocks with `{ }` and `;` terminators

Extracts:

- Zones and address books
- Zone-attached address books
- Address objects (ip-prefix, dns-name, range-address, wildcard-address)
- Address groups / address-sets
- Applications and application-sets (with predefined application mapping)
- Security policies (from-zone/to-zone pairs and global policies)
- NAT rules (source, destination, static) with port matching and pool-based translations
- Interfaces (IPv4/IPv6, LAG, DHCP client, VLAN, MTU)
- System config (hostname, DNS, NTP, admin users)
- Schedules
- Static routes, BGP, OSPF/OSPFv3
- IPv6 static routes
- Routing instances/VRF
- HA / chassis cluster configuration
- MNHA HA detection
- Screen/IDS protections
- VPN full IKE/IPsec chain resolution
- Syslog configuration
- DHCP server pools and relay
- Logical-systems and tenant support for multi-context deployments
- Residual config capture
- Version detection

## Auto-trigger keywords

`SRX`, `Junos`, `Juniper`, `set security`, `security zones`, `address-book`, `applications`, `security policies`, `from-zone`, `to-zone`, `nat rule-set`, `chassis cluster`, `logical-systems`, `routing-instances`

## Manual invocation

- **Claude Code / Hermes**: `/parsing-srx-configs`
- **Codex**: `$parsing-srx-configs`

## Installation

Use the repository installer to install into one or more runtimes:

```bash
# Install to Claude Code
./install.sh --skill parsing-srx-configs --target claude

# Install to Codex
./install.sh --skill parsing-srx-configs --target codex

# Install to Hermes
./install.sh --skill parsing-srx-configs --target hermes

# Install to all three
./install.sh --skill parsing-srx-configs --target all

# Or install the whole parsers family
./install.sh --family parsers --target all
```

Manual installation (copy the skill directory to the runtime's skills directory):

```bash
# Claude Code
cp -r parsing-srx-configs ~/.claude/skills/

# Codex
cp -r parsing-srx-configs ~/.agents/skills/

# Hermes
cp -r parsing-srx-configs ~/.hermes/skills/devops/
```

## Security audit checks

- Unused address/service objects
- Shadowed policies
- Overly permissive rules
- Missing logging on permit policies
- Disabled / deactivated policies
- Duplicate objects
- Empty groups
- Weak VPN algorithms (DES/3DES, MD5, DH ≤ 5)

## File structure

```
parsing-srx-configs/
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
