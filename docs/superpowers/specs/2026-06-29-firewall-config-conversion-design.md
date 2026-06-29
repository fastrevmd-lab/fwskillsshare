# Design: firewall-config-conversion

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-06-29.
Author: fastrevmd-lab, Claude.

## Purpose

The marquee consumer of the shared `parsing-*` intermediate schema: translate a
firewall configuration from one vendor to another. The schema is the pivot, so it
is **any-source → any-target**. Output is the target vendor's native config plus a
**per-section fidelity report** that makes every lossy or non-portable translation
visible. This is the third schema consumer (after `firewall-best-practices-audit`),
realizing the "conversion" the parsers were built for.

A converted config is a **migration draft requiring review**, never a
drop-in/production-ready artifact. The skill never claims otherwise.

## Decisions (from brainstorming)

1. **Scope — full config.** Convert every schema section: objects/groups (address,
   service, application), security policies, NAT, zones, interfaces, routing
   (static/OSPF/BGP), system/management, HA, VPN/IPsec, screens, schedules, DHCP.
   The portable layers (objects/policies/NAT/zones) convert with high fidelity; the
   platform-bound layers (interfaces, routing, mgmt, HA, VPN crypto) are emitted
   best-effort and carry most caveats.
2. **Targets — all 4.** Emit to Cisco ASA/FTD, FortiGate/FortiOS, Palo PAN-OS, and
   Juniper SRX. Any of the 4 parsers can be the source; any of the 4 a target.
3. **Fidelity — per-section report.** Each schema section is tagged `converted` /
   `converted-with-caveats` / `manual-not-converted` with specifics, plus inline
   `# CAVEAT:` comments in the emitted config.

## Architecture and data flow

```
input ──> front door ──> emit(target) ──> target config + per-section fidelity report
          (schema, or                      (+ inline CAVEAT comments)
           raw → parse first)
```

- **Front door:** an intermediate schema → emit directly. Raw config → identify the
  vendor and run the matching `parsing-*` skill first, then emit. The user picks the
  target vendor. Never re-implement parsing.
- **Emit:** walk every schema section and render it in the target vendor's native
  syntax, consulting `feature-mapping.md` for cross-vendor equivalences.
- **Fidelity:** classify each section and attach caveats; emit inline `# CAVEAT:`
  comments where a translation is approximate or lossy.
- **Graceful degradation:** a schema section that is empty or that has no target
  equivalent is reported (`manual-not-converted`), never silently dropped.

## Output format

Target's **native CLI / set format**: SRX `set`, Cisco ASA CLI, FortiGate
`config/edit/set/next/end`, Palo PAN-OS `set`. Matches the existing
`parsing-*/references/config-format.md` references and is the most usable form for a
migration. **Secrets are never emitted** — PSKs, keys, and passwords become
placeholders with a `manual-not-converted` caveat (re-key/re-secret on the target).

## File structure

```
skills/firewall-config-conversion/
  SKILL.md                  # routing, conversion workflow, fidelity-report template,
                            # output conventions, pitfalls, verification
  references/
    feature-mapping.md      # cross-vendor equivalence + non-isomorphic catalog
    emit-srx.md             # per-target emission patterns (schema section -> SRX set)
    emit-palo.md            # -> PAN-OS set
    emit-fortinet.md        # -> FortiOS config/edit/set
    emit-cisco.md           # -> ASA/FTD CLI
    example-conversion.md   # one worked end-to-end conversion (validated on a vSRX)
```

Only the chosen target's `emit-*.md` plus `feature-mapping.md` load per conversion
(progressive disclosure). SKILL.md stays lean.

## feature-mapping.md (the cross-vendor brain)

The shared fidelity knowledge:

- **Canonical → target application names.** Reuse the parsers' canonical app mapping
  in reverse (e.g. canonical `https` → SRX `junos-https`, Palo `ssl`/`web-browsing`,
  FortiGate `HTTPS`, Cisco service `tcp/443`). The parsing skills already maintain the
  forward table.
- **Feature equivalence + non-isomorphic catalog.** For each schema concept, record:
  maps 1:1 / maps-with-loss / no target equivalent (manual). Examples: zones (SRX/Palo
  native; FortiGate interfaces-as-zones; ASA security-levels/nameif), NAT models, SRX
  `application-services` / Palo security-profile-groups / FortiGate UTM profiles,
  VPN/IKE crypto, interface naming conventions, routing-instances/VRF vs contexts/vsys.
- Drives both the emitted `# CAVEAT:` comments and the per-section fidelity report
  classification.

## Fidelity report (the heart)

Emitted after the config. Per schema section: a status and specifics, e.g.:

```
Section: address_objects     → converted (24/24)
Section: security_policies   → converted (12/12)
Section: nat_rules           → converted-with-caveats (SRX persistent-NAT has no
                               FortiGate 1:1 — emitted as VIP + note)
Section: vpn_tunnels         → manual-not-converted (IKE/IPsec crypto + PSK do not
                               port; re-key on the target)
Section: interfaces          → converted-with-caveats (ge-0/0/0 → ethernet1/1 —
                               naming remapped; verify physical mapping)
Section: routing (OSPF/BGP)  → converted-with-caveats (protocol config emitted; verify
                               areas/AS and redistribution semantics)
```

A short header states the config is a migration draft requiring review and lists the
top manual items. The report never asserts production-readiness.

## Testing

- **Worked example** (`example-conversion.md`): convert a real parsed config **→ SRX**
  and show the emitted config + the fidelity report.
- **Live commit-check (the strong gate):** validate the emitted SRX config on a vSRX
  via `rust-junosmcp` — `load_and_commit_config` in check mode (or `commit check`) and
  `junos_config_diff` — confirming the emitted config actually parses/commits on a real
  device. Secrets redacted.
- **Other targets:** validated structurally (syntax conforms to the vendor's
  `config-format.md`); no live devices for Cisco/Forti/Palo in this lab.
- **Round-trip self-test (deferred):** parse → convert back to the *same* vendor →
  diff against the original to measure fidelity. Deferred until `firewall-config-diff`
  exists (the next TODO item); noted as a future validation, not built here.

## Relationship to existing skills and housekeeping

- `related_skills`: `parsing-cisco-configs`, `parsing-fortinet-configs`,
  `parsing-palo-configs`, `parsing-srx-configs` (input producers),
  `firewall-config-diff` (round-trip validation, when it exists),
  `firewall-best-practices-audit` (audit before/after migration).
- Body states the clean separation: this skill *emits* a target config; it does not
  audit (that is the audit skill) or compare (that is the diff skill).
- Housekeeping: README skill-table row + Claude/Hermes install + uninstall + the
  hermes verify-grep; optional cross-link from the parsing skills; tick the
  `firewall-config-conversion` item in `TODO.md`. Author `fastrevmd-lab` + `Claude`,
  `license: MIT`, version `1.0.0`.

## Out of scope (YAGNI)

- Re-implementing config parsing (owned by the `parsing-*` skills).
- Auditing or diffing (owned by the audit and diff skills).
- Live push of the converted config to a production device (the skill emits a draft;
  the live SRX test is commit-*check* only).
- Emitting secrets — always placeholdered.
- Targets without a vendor emission reference (only the 4 listed).

## Implementation note (for the plan)

Large surface → structure the plan as ~8 tasks: SKILL.md skeleton, feature-mapping.md
(shared brain), four `emit-*.md` (parallelizable per target), the worked example with
the live vSRX commit-check, and validation/housekeeping. Progressive disclosure keeps
per-conversion token cost bounded (one emitter + mapping load at a time).
