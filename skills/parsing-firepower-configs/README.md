# parsing-firepower-configs

Claude Code skill for parsing **Cisco Firepower** policy exported from FMC or FDM as **JSON**. For LINA running-config (ASA-style CLI), use `parsing-cisco-configs` instead.

## What it does

Parses JSON-formatted policy exports from Firepower Management Center (FMC) or Firepower Device Manager (FDM) and extracts:

- Access Control Policy (ACP) rules (Prefilter, Mandatory, Default sections)
- Security zones (ingress/egress)
- Network objects and groups
- Port objects and groups
- URL objects and categories
- Security Intelligence feed objects
- Intrusion Policy (IPS) assignments
- File Policy assignments
- Variable sets and their overrides
- NAT rules and sections
- Static routes
- High Availability pairs
- Device-level settings
- VPN (site-to-site and remote access)
- Platform settings (interfaces, VLAN, routing)
- Identity policy and realms
- SSL policy
- DNS policy
- Prefilter policy rules

## Auto-trigger keywords

`Firepower`, `FMC`, `FDM`, `FTD`, `Access Control Policy`, `accessPolicy`, `prefilterPolicies`, `securityZones`, `networkObjects`, `portObjects`, `intrusionPolicy`, `filePolicy`

## Manual invocation

- **Claude Code / Hermes**: `/parsing-firepower-configs`
- **Codex**: `$parsing-firepower-configs`

## Installation

Use the repository installer to install into one or more runtimes:

```bash
# Install to Claude Code
./install.sh --skill parsing-firepower-configs --target claude

# Install to Codex
./install.sh --skill parsing-firepower-configs --target codex

# Install to Hermes
./install.sh --skill parsing-firepower-configs --target hermes

# Install to all three
./install.sh --skill parsing-firepower-configs --target all

# Or install the whole parsers family
./install.sh --family parsers --target all
```

Manual installation (copy the skill directory to the runtime's skills directory):

```bash
# Claude Code
cp -r parsing-firepower-configs ~/.claude/skills/

# Codex
cp -r parsing-firepower-configs ~/.agents/skills/

# Hermes
cp -r parsing-firepower-configs ~/.hermes/skills/devops/
```

## Security audit checks

- Shadowed ACP rules (rules unreachable due to earlier broad matches)
- Overly permissive rules (`any` source/dest with `Allow` action)
- Missing terminal `Block All` in Default section
- MONITOR rules (non-terminal, affect shadowing analysis)
- Unused network/port objects
- Duplicate objects
- Empty object groups
- Weak VPN algorithms
- Identity policy gaps
- SSL decryption policy coverage

## File structure

```
parsing-firepower-configs/
├── SKILL.md                          # Main skill instructions
├── agents/
│   └── openai.yaml                   # Codex agent manifest
└── references/
    ├── config-format.md              # FMC/FDM JSON structure reference
    ├── intermediate-schema.md        # Vendor-neutral output schema
    ├── parsing-patterns.md           # Edge cases, object resolution
    ├── runtime-intake.md             # Interactive question catalog for ambiguous requests
    ├── example-sample-parse.md       # Worked example with input/output
    ├── fixture-minimal-input.md      # Minimal test fixture (input)
    └── fixture-expected-output.json  # Minimal test fixture (expected output)
```
