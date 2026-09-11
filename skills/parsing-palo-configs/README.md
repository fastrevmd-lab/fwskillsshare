# parsing-palo-configs

Claude Code skill for parsing and analyzing **Palo Alto PAN-OS and Panorama** firewall configurations in XML format.

## What it does

Parses both XML and set-format (`show config flat`) configs from device-level or Panorama device-group configurations and extracts:

- Zones (layer3, layer2, virtual-wire, tap)
- Address objects (ip-netmask, ip-range, fqdn, ip-wildcard)
- Address groups (static and dynamic tag-based)
- Service objects (TCP/UDP, plus SCTP on 9.0+ platforms with SCTP security enabled) and service groups
- Custom applications
- Security policies with profile settings
- NAT rules (source and destination)
- Decryption rules
- Routing configuration
- HA configuration
- Zone protection profiles
- IPv6 address types and routes
- Interfaces (ethernet, LAG, loopback, tunnel, VLAN)
- System config (hostname, DNS, NTP, management services)
- Admin users
- DHCP server/relay
- Detailed OSPF/OSPFv3/BGP
- VPN/IPsec with full crypto chain
- URL categories on policies
- Application group resolution
- Virtual-wire configurations
- Multiple vsys support with per-vsys tagging
- Panorama pre-rulebase and post-rulebase handling
- Residual config capture

## Auto-trigger keywords

`PAN-OS`, `Palo Alto`, `Panorama`, `NGFW`, `vsys`, `security rulebase`, `address-group`, `application-default`, `security-profile-group`, `device-group`, `<entry name=`, `<member>`, `tag-based`, `User-ID`

## Manual invocation

- **Claude Code / Hermes**: `/parsing-palo-configs`
- **Codex**: `$parsing-palo-configs`

## Installation

Use the repository installer to install into one or more runtimes:

```bash
# Install to Claude Code
./install.sh --skill parsing-palo-configs --target claude

# Install to Codex
./install.sh --skill parsing-palo-configs --target codex

# Install to Hermes
./install.sh --skill parsing-palo-configs --target hermes

# Install to all three
./install.sh --skill parsing-palo-configs --target all

# Or install the whole parsers family
./install.sh --family parsers --target all
```

Manual installation (copy the skill directory to the runtime's skills directory):

```bash
# Claude Code
cp -r parsing-palo-configs ~/.claude/skills/

# Codex
cp -r parsing-palo-configs ~/.agents/skills/

# Hermes
cp -r parsing-palo-configs ~/.hermes/skills/devops/
```

## Security audit checks

- Unused address/service objects
- Shadowed policies
- Overly permissive rules
- Missing logging on allow rules
- Disabled policies still in config
- Dynamic address group dependency warnings
- User-ID dependency flags
- Profile group resolution validation
- Implicit intra-zone allow and interzone default deny rules
- URL category dependencies
- Weak VPN algorithms

## File structure

```
parsing-palo-configs/
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
