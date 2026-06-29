---
name: firewall-config-conversion
description: Use when converting or migrating a firewall / NGFW configuration from one vendor to another (Cisco ASA/FTD, FortiGate, Palo Alto PAN-OS, Juniper SRX) — translating objects, security policies, NAT, zones, interfaces, routing, system, HA, and VPN from a parsed config into a target vendor's native config. Operates on the parsing-* intermediate schema; for raw config, run the matching parsing-cisco/fortinet/palo/srx skill first. Emits the target's native CLI plus a per-section fidelity report (converted / converted-with-caveats / manual-not-converted) flagging everything that does not translate cleanly. Output is a migration draft requiring review, never production-ready; secrets are never emitted.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
license: MIT
metadata:
  hermes:
    tags: [firewall, ngfw, conversion, migration, cross-vendor, cisco, fortigate, panos, srx, intermediate-schema, fidelity-report, vendor-neutral]
    related_skills: [parsing-cisco-configs, parsing-fortinet-configs, parsing-palo-configs, parsing-srx-configs, firewall-config-diff, firewall-best-practices-audit]
---

# Firewall Config Conversion

## Overview

Use this skill to convert a firewall or NGFW configuration from one vendor to another by pivoting through the `parsing-*` intermediate JSON schema. Any source vendor that has a parser (Cisco ASA/FTD, FortiGate, Palo Alto PAN-OS, Juniper SRX) can be converted to any of the four supported targets, because every conversion reads the same normalized schema — `address_objects`, `address_groups`, `service_objects`, `service_groups`, `security_policies`, `nat_rules`, `zones`, `interfaces`, `static_routes` / `virtual_routers` / routing, `vpn_tunnels`, `ha_config`, and `system` — and re-emits it in the target's native CLI. This schema-pivot design means there is one emitter per target rather than one translator per source/target pair.

The output is always two parts: the target vendor's native configuration, followed by a per-section fidelity report. The config carries inline `# CAVEAT:` comments wherever a translation is lossy or approximate, and the fidelity report classifies each schema section as converted, converted-with-caveats, or manual-not-converted, then lists the manual follow-up items that a human must complete on the target device.

This skill produces a migration draft, never a production-ready config. Vendor security models differ enough — zones versus security-levels, App-ID versus port-based services, routing-instances versus contexts or vsys — that no automated conversion is safe to commit unreviewed. Secrets are never emitted: VPN pre-shared keys, certificates, and admin passwords are always replaced with placeholders and flagged as manual items, so the draft can be shared and reviewed without leaking credentials.

## When to Use

Use this skill when the user asks to:

- "convert / migrate / translate this <vendor> config to <vendor>" (e.g. "turn this ASA config into SRX")
- perform a vendor refresh or hardware replacement onto a different platform
- consolidate firewalls after a merger or acquisition onto one vendor
- migrate off an end-of-life or end-of-support platform to a current one

Do NOT use this skill when:

- The ask is to audit or harden a rulebase — route to `firewall-best-practices-audit`.
- The ask is to compare or diff two configs — route to `firewall-config-diff`.
- The requested target vendor has no emitter in `references/` — say so plainly; do not improvise a target syntax this skill cannot support.
- You were handed raw vendor config — run the matching `parsing-*` skill first to produce the schema, then convert (see Input Handling).

## Input Handling

Route on what you were given:

- **Parsed intermediate schema** (the vendor-neutral JSON produced by any `parsing-*` skill; the schema definition lives in the `parsing-srx-configs` skill) — convert directly. Read `metadata.source_vendor` to label the draft and to choose source-aware caveats.
- **Raw config** — identify the vendor from the syntax, run the matching `parsing-*` skill (`parsing-cisco-configs`, `parsing-fortinet-configs`, `parsing-palo-configs`, `parsing-srx-configs`) to produce the intermediate schema, then convert the result. Never re-implement parsing in this skill.
- **Target vendor** — the user must pick the target (Cisco ASA/FTD, FortiGate, PAN-OS, or SRX). If they did not, ask before emitting; there is one emitter per target and the wrong one produces unusable output.

## Conversion Workflow

1. **Confirm inputs.** Verify you have the intermediate schema (parse raw config first), read `metadata.source_vendor` for the source, and confirm the user's chosen target vendor.
2. **Load references.** Load `references/feature-mapping.md` for the cross-vendor concept map, plus the target's emitter `references/emit-<target>.md` for the native syntax of each section.
3. **Emit each section.** Walk the schema sections in the output order below and emit each in the target's native CLI. Where a construct does not map cleanly, emit the closest equivalent and insert an inline `# CAVEAT: ...` comment explaining the approximation.
4. **Classify for the report.** As you emit, classify each section as converted, converted-with-caveats, or manual-not-converted, and collect the manual follow-up items.
5. **Placeholder all secrets.** Replace every PSK, key, certificate, and password with a clearly-marked placeholder and add a manual item to re-key on the target — never emit a real or parsed secret.
6. **Produce the output.** Emit the labeled draft config first, then the fidelity report, in the templates below.

## Output & Fidelity Report

### Conversion output (emit in this order)

```text
# Conversion DRAFT: <source-vendor> -> <target-vendor>
# Review required. Not production-ready. Manual items listed in the fidelity report.
<target-native config, with inline "# CAVEAT: ..." comments where lossy/approximate>
```

### Fidelity report (after the config)

```text
Fidelity report (<source> -> <target>)
Section: address_objects     → <converted|converted-with-caveats|manual-not-converted> (<n/m or note>)
Section: security_policies   → ...
Section: nat_rules           → ...
Section: interfaces          → ...
Section: routing             → ...
Section: vpn_tunnels         → ...
Section: system / admin      → ...
Manual items (must do on target):
  1. <e.g. re-key all VPN PSKs — secrets are not emitted>
  2. ...
```

## Reference Material (load on demand)

- `references/feature-mapping.md` — cross-vendor concept map (zones vs security-levels, App-ID vs port services, routing-instances vs contexts/vsys, NAT models) and what is lossy in each direction.
- `references/emit-srx.md` — emit the schema as Juniper SRX `set` configuration.
- `references/emit-palo.md` — emit the schema as Palo Alto PAN-OS configuration.
- `references/emit-fortinet.md` — emit the schema as FortiGate `config` blocks.
- `references/emit-cisco.md` — emit the schema as Cisco ASA/FTD configuration.
- `references/example-conversion.md` — a worked conversion against a parsing-* fixture, with its fidelity report.

## Common Pitfalls

- Claiming the converted config is production-ready — it is a draft; require review plus the manual items.
- Emitting secrets — PSKs, keys, and passwords are always placeholders plus a manual caveat.
- Silently dropping a section with no target equivalent — report it as manual-not-converted.
- Re-implementing parsing instead of delegating to the matching `parsing-*` skill.
- Forcing a 1:1 mapping where the target model differs (zones vs security-levels, App-ID vs port services, routing-instances vs contexts/vsys) — emit the closest form plus a CAVEAT.
- Converting interface, routing, and system sections verbatim — these are platform-bound; remap and flag naming and protocol semantics.
- Losing rule or NAT order — preserve order in the emitted config.

## Verification Checklist

- [ ] Confirm input is the intermediate schema (parse raw first) and the target vendor is chosen.
- [ ] Every emittable schema section is either converted or explicitly reported (no silent drops).
- [ ] Inline CAVEAT comments mark every lossy/approximate translation.
- [ ] No secrets in the output (PSKs/keys/passwords placeholdered).
- [ ] Rule and NAT order preserved.
- [ ] Output labeled a migration draft; fidelity report lists all manual items.
