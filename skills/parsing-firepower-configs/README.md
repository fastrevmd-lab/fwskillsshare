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

```
/parsing-firepower-configs
```

## Installation

```bash
cp -r parsing-firepower-configs ~/.claude/skills/
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
└── references/
    ├── config-format.md              # FMC/FDM JSON structure reference
    ├── intermediate-schema.md        # Vendor-neutral output schema
    ├── parsing-patterns.md           # Edge cases, object resolution
    ├── example-sample-parse.md       # Worked example with input/output
    ├── fixture-minimal-input.json    # Minimal test fixture (input)
    └── fixture-expected-output.json  # Minimal test fixture (expected output)
```
