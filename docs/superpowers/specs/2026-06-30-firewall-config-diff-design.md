# Design: firewall-config-diff

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-06-30.
Author: fastrevmd-lab, Claude.

## Purpose

The fourth tooling skill and the validation counterpart to
`firewall-config-conversion`: compare two firewall configurations by **meaning**
(not text). Both inputs normalize to the shared `parsing-*` intermediate schema,
then a semantic, order- and name-insensitive diff produces a per-section report
plus a parity verdict. Same-vendor (drift, HA-pair consistency) and cross-vendor
(parity, pre/post-migration) are the same mechanism. It also enables the
**round-trip conversion self-test** the conversion skill deferred.

A textual `diff` would add nothing — the value is semantic comparison over the
pivot schema.

## Decisions (from brainstorming)

1. **Scope — full config.** Diff every schema section: objects/groups, security
   policies, NAT, zones, interfaces, routing (static/OSPF/BGP), system, admin,
   DHCP, HA, VPN, screens, schedules, security_services. Matches the conversion
   skill's full scope so the round-trip self-test covers everything conversion
   emits.
2. **Cross-vendor — semantic match + non-isomorphic flag.** Compare by meaning;
   where a feature has no cross-vendor equivalent, mark it `vendor-specific / not
   directly comparable` rather than emit a false diff.
3. **Round-trip self-test — kept.** Documented use case AND a worked demonstration
   in the example.

## Architecture and data flow

```
config A ─┐
          ├─ front door (each: schema, or raw → parse) → semantic diff → per-section report + parity verdict
config B ─┘
```

- **Front door:** two inputs A and B; each is an intermediate schema or raw config
  (raw → run the matching `parsing-*` skill first). Same- or cross-vendor — one
  mechanism. Never re-implement parsing.
- **Semantic diff:** normalize both to the schema, then compare by meaning,
  order- and name-insensitive.
- **Graceful degradation:** a section present in neither input is skipped; a
  feature with no cross-vendor equivalent is reported `not-comparable`, never a
  false diff.

## Semantic identity (the core algorithm)

Items pair across A and B by **meaning, not name or order**:

- address objects match by value (`10.0.1.10/32`), not object name;
- service objects by protocol + port; applications by canonical name;
- security policies by the `(src, dst, service/app, action, src_zones, dst_zones)`
  semantic tuple;
- NAT rules by match + translation;
- interfaces by name/unit + address; routes by prefix + next-hop; etc.

Each matched pair is `unchanged` or `changed` (same identity, differing
attributes — e.g. logging toggled, profile changed). Unmatched items are `added`
(in B only) or `removed` (in A only). Rule **order** differences are reported
separately (order affects shadowing) but do not count as add/remove.

## Cross-vendor equivalence (`references/equivalence-rules.md`)

A diff-specific equivalence reference — distinct in purpose from the conversion
skill's *emission* mapping; this one answers "are these equivalent?". Self-contained
(not a cross-skill reference; informed by, but not importing,
`firewall-config-conversion`'s feature-mapping). Contains:

- **Canonical-app normalization** so `junos-https` == Palo `ssl`/`web-browsing` ==
  FortiGate `HTTPS` == Cisco `tcp/443` compare equal.
- **Not-comparable catalog** — per schema concept, what has no cross-vendor
  equivalent and is therefore flagged `vendor-specific / not directly comparable`
  (SRX `application-services` vs Palo security-profile-group vs FortiGate UTM vs
  ASA none; IKE/IPsec crypto; zones model differences; routing-instances vs
  vsys/contexts).

## Output — per-section report + parity verdict

```
Parity verdict: <EQUIVALENT | DIFFERENCES FOUND (<n>)>  (A=<vendor>, B=<vendor>)
Section: address_objects    unchanged <n>  added <n>  removed <n>  changed <n>
Section: security_policies  unchanged <n>  added <n>  removed <n>  changed <n>  | order: <n> reordered
  + [B] <added item, semantic summary>
  - [A] <removed item>
  ~ [A→B] <name>: <attribute change, e.g. logging off → on>
Section: vpn_tunnels        not-comparable (IKE/IPsec crypto — vendor-specific)
Not comparable: <list of sections/features that could not be compared>
```

Two framings, one mechanism: **drift** (A=old, B=new → "what changed") and
**parity** (A vs B → "are they equivalent?"). The report never claims more than the
schema supports and always lists what could not be compared.

## File structure

```
skills/firewall-config-diff/
  SKILL.md                 # input routing, diff workflow, semantic-identity rules,
                           # output/verdict template, pitfalls, verification
  references/
    equivalence-rules.md   # per-section semantic identity + cross-vendor not-comparable catalog
    example-diff.md        # worked examples: same-vendor drift, cross-vendor parity, round-trip
```

Lean SKILL.md; `equivalence-rules.md` loads when needed (progressive disclosure).

## Testing / worked examples (`example-diff.md`)

- **Same-vendor drift (primary):** config A = the `parsing-cisco-configs` fixture
  schema; config B = a realistically modified copy (one policy added, one object
  changed, logging toggled). Show the per-section report + verdict. Grounded, no
  device needed.
- **Cross-vendor parity (illustration):** a short snippet comparing an ASA-shaped
  schema vs an equivalent SRX-shaped schema — semantically equivalent except the
  flagged `not-comparable` items.
- **Round-trip self-test (the tie-in):** original Cisco fixture schema (A) vs the
  schema obtained by re-parsing the SRX config that the `firewall-config-conversion`
  skill emits for that fixture (B). The diff measures what the Cisco→SRX conversion
  preserved vs lost — a concrete fidelity metric. Demonstrated in `example-diff.md`
  with the relevant before/after schema snippets shown **inline** (cite the
  conversion skill by name; do NOT path-reference another skill's files — keep this
  skill self-contained). No live device required.

## Relationship to existing skills and housekeeping

- `related_skills`: `parsing-cisco-configs`, `parsing-fortinet-configs`,
  `parsing-palo-configs`, `parsing-srx-configs` (input producers),
  `firewall-config-conversion` (round-trip validation), `firewall-best-practices-audit`.
- Body states the separation: diff *compares* two configs; it does not emit
  (conversion) or assess against best practice (audit).
- Housekeeping: README skill-table row + Claude/Hermes install + uninstall +
  verify-grep + directory tree; "## Skills Included" count → 20; tick the
  `firewall-config-diff` item in `TODO.md`; cross-link from the 4 parsing skills.
  Author `fastrevmd-lab` + `Claude`, `license: MIT`, version `1.0.0`.

## Out of scope (YAGNI)

- Re-implementing config parsing (owned by the `parsing-*` skills).
- Emitting target config (owned by `firewall-config-conversion`).
- Best-practice assessment (owned by `firewall-best-practices-audit`).
- A textual/line diff — the skill is semantic-only.
- Auto-merging or three-way merge — this is a two-way comparison/report only.

## Implementation note (for the plan)

Smaller surface than conversion → ~5 tasks: SKILL.md skeleton + output/verdict
templates, `equivalence-rules.md`, the worked example (3 scenarios incl.
round-trip), and validation/housekeeping. No new shared-schema edits (read-only
consumer).
