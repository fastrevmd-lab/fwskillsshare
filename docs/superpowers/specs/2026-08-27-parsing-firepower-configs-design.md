# Design: parsing-firepower-configs

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-08-27.
Author: fastrevmd-lab, Claude.

## Purpose

A fifth `parsing-*` skill owning **FMC- and FDM-managed Cisco Secure Firewall
(Firepower) policy exports** — a JSON object model that shares no parseable
syntax with the ASA-style LINA CLI that `parsing-cisco-configs` owns. It emits
the same byte-identical shared intermediate schema, so `firewall-best-practices-audit`,
`firewall-config-conversion`, and `firewall-config-diff` consume it unchanged.

The repository currently claims FTD coverage (`skills/parsing-cisco-configs/SKILL.md:3`)
and delivers it *only* for the LINA form. Everywhere the NGFW layer comes up, the
repo defers it: `firewall-config-conversion/references/emit-cisco.md:30-33` states
these are ASA-style LINA snippets and that FMC-managed FTD rebuilds policy in FMC;
`firewall-config-conversion/references/feature-mapping.md:147` records "FTD differs
and is out of scope." This skill closes that gap without disturbing the LINA path.

## Decisions (from brainstorming)

1. **Separate skill, split on grammar — not on product name.** Both artifacts are
   "Cisco FTD" to a human. They have zero token overlap. Descriptions key on
   grammar tokens, which is how `parsing-palo-configs` already discriminates XML
   from set-format.
2. **Scope.** Primary: FMC REST API JSON and FDM REST API JSON. Secondary: the FDM
   `configexport` bundle. Best-effort with heavy warnings: FMC CSV rule export.
   **Explicitly out of scope:** `.sfo` policy bundles and PDF policy reports.
3. **No schema change.** Follow the Panorama precedent at
   `parsing-palo-configs/SKILL.md:386` — flatten the merged evaluation order into
   `_rule_index` and record section/category/inheritance provenance in `metadata`
   rather than inventing a context field.
4. **One schema document per Access Control Policy.** An FTD device is assigned
   exactly one ACP, so an ACP *is* the evaluation population the audit skill needs.
5. **`parsing-cisco-configs` keeps ASA + FTD-LINA**, with routing text sharpened in
   both directions.

## Boundary

| | `parsing-cisco-configs` (existing) | `parsing-firepower-configs` (new) |
|---|---|---|
| Artifact | ASA / FTD LINA `show running-config` | FMC + FDM REST JSON, FDM `configexport` |
| Shape | line-oriented CLI, indented sub-commands | nested JSON objects, UUID references |
| Zones | derived from `nameif` | first-class `securityZones` objects |
| Policy | `access-list` + `access-group` | Access Control Policy rules + Prefilter |
| Ordering | ACL line order per binding | Prefilter → ACP sections → inherited ancestors |
| L7 | none — port→app inference only | applications, filters, URL categories/reputation |
| Inspection | none | intrusion policies, file policies, variable sets |
| Trigger tokens | `access-list`, `nameif`, `object network`, `access-group`, `security-level` | `accessrules`, `securityZones`, `intrusionPolicy`, `filePolicy`, `variableSet`, `prefilterpolicies`, `ftdnatpolicies` |

## Input assembly

Unlike every existing parser, the input is **not one document**. FMC data arrives as
many API responses. The skill accepts three packagings and must detect which:

1. **Bundle** — a directory or concatenated set of JSON documents, one per endpoint.
   The expected form for a complete parse.
2. **Keyed envelope** — a single JSON object whose keys are endpoint paths and whose
   values are the corresponding responses. Convenient for pasting.
3. **Single response** — one endpoint's JSON. Parses what is present, emits a
   partial-input warning, and populates only the sections that response can fill.

FMC paginates (`paging.offset` / `limit` / `count`). A response whose `paging.count`
exceeds the number of `items` present is a **truncated collection**: record it in
`metadata.warnings` and never treat the short list as the complete object set.
Silently parsing page 1 of 7 as a whole rulebase is the highest-consequence failure
mode this skill has, because every downstream audit conclusion inherits it.

## Detection and routing

Detect Firepower JSON on the presence of FMC/FDM type discriminators — `"type":
"AccessRule"`, `"type": "AccessPolicy"`, `"type": "SecurityZone"`, `"type":
"FTDNatPolicy"`, `metadata.accessPolicy`, `metadata.section`, an FMC
`/api/fmc_config/v1/domain/` path, or an FDM `/api/fdm/` path. Hand off to
`parsing-cisco-configs` on `access-list` / `nameif` / `object network` text, to the
Fortinet, Palo, and SRX parsers on their own grammars.

## Extraction pipeline

Endpoint families → schema sections. **Exact endpoint names and field spellings must
be pinned against the FMC/FDM API Explorer for the target version during
implementation** — they vary across releases and are not asserted here as verified.

| Source | Schema section |
|---|---|
| `object/networks`, `hosts`, `ranges`, `fqdns` | `address_objects` |
| `object/networkgroups` | `address_groups` |
| `object/protocolportobjects`, `icmpv4objects`, `icmpv6objects` | `service_objects` |
| `object/portobjectgroups` | `service_groups` |
| `object/applications`, `applicationfilters` | `applications`, `application_groups` |
| `object/urls`, `urlgroups`, `urlcategories` | policy `url_categories` |
| `object/securityzones`, `interfacegroups` | `zones` |
| `object/timeranges` | `schedules` |
| `object/variablesets`, `policy/intrusionpolicies`, `policy/filepolicies` | `security_profile_objects` |
| `policy/accesspolicies/{id}/accessrules` | `security_policies` |
| `policy/accesspolicies/{id}/defaultaction` | final `_implicit: true` policy |
| `policy/prefilterpolicies/{id}/prefilterrules` | `security_policies` (ahead of ACP) |
| `policy/ftdnatpolicies/{id}/autonatrules`, `manualnatrules` | `nat_rules` |
| `devices/devicerecords/{id}/physicalinterfaces`, `subinterfaces`, `etherchannelinterfaces` | `interfaces` |
| `.../routing/ipv4staticroutes`, `ipv6staticroutes` | `static_routes` |
| `.../routing/ospfv2interfaces`, `bgp` | `ospf_config`, `bgp_config` |
| `devicehapairs/ftddevicehapairs` | `ha_config` |
| `policy/ftds2svpns` + ike/ipsec settings | `vpn_tunnels` |
| unmapped / unrecognized payloads | `residual_raw` |

Interfaces map more directly than on ASA: `ifname` is the `nameif` equivalent, and
`securityZone` gives the zone binding without inference. Record `mode`
(ROUTED / SWITCHPORT / PASSIVE / INLINE) — passive and inline-set interfaces do not
carry policy the way routed ones do, and an audit that assumes otherwise is wrong.

## Rule ordering — the merged evaluation order

Firepower evaluates, in order: **Prefilter policy → ACP Mandatory section → ACP
Default section → ACP default action**, with ancestor policies contributing rules to
both sections when the ACP inherits.

The skill flattens all of it into one continuous `_rule_index` and records
provenance — policy name, section, category, inheriting ancestor — in `metadata`,
per the precedent set for Panorama pre/post rulebases. Downstream consumers already
sort by `_rule_index` and already treat unknown `_`-prefixed fields as invisible
(`firewall-config-diff/references/equivalence-rules.md:36`).

**The exact nesting direction of inherited Default-section rules must be confirmed
against current Cisco documentation before the ordering logic is written.** The
general shape — ancestor Mandatory before the child's rules, ancestor Default after
them — is well established; the precise interleaving across a multi-level hierarchy
is not asserted here.

## Action mapping — and the one semantic the schema cannot hold

| Firepower action | Schema `action` | Note |
|---|---|---|
| `ALLOW` | `allow` | |
| `TRUST` | `allow` | bypasses deep inspection — record in `metadata` |
| `BLOCK` | `deny` | |
| `BLOCK_RESET` | `reset-both` | |
| `BLOCK_INTERACTIVE`, `BLOCK_RESET_INTERACTIVE` | `deny` / `reset-both` | interactive-block prompt not representable |
| `MONITOR` | `allow` + mandatory warning | **non-terminal** |
| Prefilter `FASTPATH` | `allow` + mandatory warning | bypasses Snort entirely |
| Prefilter `ANALYZE` | — | not a terminal action; hands off to the ACP |

**`MONITOR` is the load-bearing risk.** A MONITOR rule logs and *continues* to the
next rule; it does not terminate evaluation. The shared schema has no non-terminal
action, so a naive `allow` mapping tells the audit skill that a rule matches and
stops when it does not. That is the same class of defect the live-SRX round found
with `match dynamic-application` — dropped narrowing turned distinct rules into
false duplicates and made a scoped deny read as a terminal deny-all
(`QUALITY.md`, 2026-07-31 entry). Every MONITOR rule therefore emits a
`metadata.warnings` entry naming the rule, and the skill states plainly that
shadowing and terminal-deny conclusions are unreliable across a MONITOR rule.

The ACP default action becomes the single trailing `_implicit: true` policy — cleaner
than the ASA path, which has to synthesize one per `access-group` binding.

## Reference resolution

Rules reference objects as `{"objects": [{type, id, name}], "literals": [{type, value}]}`.

- **`objects`** — resolve by `id` against the parsed object sets; prefer the parsed
  object's name. A reference whose `id` resolves to nothing goes in
  `metadata.warnings` as an unresolved reference with its rule name, never dropped.
- **`literals`** — inline values with no named object. Mint anonymous objects using
  the same `anon-N-host` / `anon-N-net` convention `parsing-cisco-configs` already
  uses, so both Cisco parsers behave identically downstream.

## Multi-domain FMC

FMC subdomains are analogous to vsys/VDOM, but the schema has no `_domain` field and
this design does not add one. Because policy is scoped per ACP and a device gets one
ACP, the partition that matters is the ACP — so the skill emits **one schema document
per ACP**, with the policy and domain named in `metadata`. An export covering several
ACPs yields several documents rather than one merged rulebase, which would be a
fiction no device ever evaluates.

## Non-isomorphic constructs

Recorded in `metadata.warnings` and `residual_raw`, never silently dropped: Snort
intrusion rule content and variable-set values (referenced by name only), file/malware
policy internals, SSL/decryption policy, identity policy and realm/user mappings,
Security Group Tags, correlation policies, network discovery, QoS, and the
`analyze`/`fastpath` prefilter semantics above.

## Explicitly out of scope

- **`.sfo` policy bundles** — Cisco's import/export format is undocumented for
  third-party parsing. Claiming support would violate the repository's evidence rule
  (`AGENTS.md`, "Vendor syntax and compliance claims require authoritative evidence
  or an explicit unsupported/uncertain classification").
- **PDF policy reports** — presentation artifacts, unstable across versions.

Both are detected and refused with a pointer to the supported export paths, rather
than attempted and half-parsed.

## Secret handling

Matching the existing parsers: S2S VPN pre-shared keys, certificate material, SNMP
communities, and any credential field are masked as `"****"` with a
`metadata.warnings` entry. FMC JSON commonly omits secrets on GET, so record the
distinction between *absent* and *redacted* rather than implying a key was found.

## Downstream ripple

Small and additive.

- `firewall-best-practices-audit/SKILL.md:77-80` lists per-vendor evaluation-population
  partitions (`_vsys` for PAN-OS, `_vdom` for FortiGate). Add a Firepower line:
  partition by ACP, with the MONITOR caveat above.
- `firewall-config-conversion` gains Firepower as a **source** for free via the shared
  schema. It is **not** added as a target — no `emit-firepower.md`. FMC is configured
  through its API, not by pasting CLI, so a generated artifact would be unusable.
- `firewall-config-diff` needs nothing; it already ignores unknown `_` fields.

## File structure

```
skills/parsing-firepower-configs/
  SKILL.md
  README.md
  agents/openai.yaml
  references/
    config-format.md              # FMC/FDM JSON shapes, endpoint families, paging
    intermediate-schema.md        # byte-identical copy of the SRX canonical
    parsing-patterns.md           # action mapping, MONITOR, ordering, UUID resolution
    example-sample-parse.md       # worked end-to-end: JSON bundle -> schema
    fixture-minimal-input.md      # synthetic minimal FMC bundle
    fixture-expected-output.json  # expected schema for that fixture
    runtime-intake.md             # intake catalog
```

Mirrors the other four parsers exactly, so `check-skill-packages.py` and
`check-shared-schema.py` apply without modification to their logic.

## Testing

- **Fixture round-trip** — the synthetic minimal bundle parses to
  `fixture-expected-output.json`, matching how the other four parsers are tested.
- **`check-shared-schema.py`** — globs `skills/parsing-*/`, so it picks the new copy
  up automatically and fails on any drift. No script edit needed.
- **Ordering fixture** — an ACP with inherited Mandatory and Default rules plus a
  Prefilter policy, asserting one continuous `_rule_index`.
- **MONITOR fixture** — asserts the warning fires and the rule is not treated as
  terminal.
- **Truncated-paging fixture** — asserts a `paging.count` greater than the item count
  produces a partial-input warning.
- **No live device.** Validation is fixture-based; `just integration` does not contact
  devices by design. Real FMC validation is a separate, explicitly approved task.

## Risks

1. **Endpoint and field drift across FMC versions.** Mitigated by pinning the version
   the reference was written against and classifying uncertain fields explicitly.
2. **A 29th skill against a soft description budget.** `AGENTS.md` prefers
   consolidating overlapping skills when the combined warning fires. Run
   `check-skill-packages.py` early; the two Cisco descriptions are disjoint by
   construction, so they should not compete, but the combined figure should be
   measured rather than assumed.
3. **Ships unreviewed.** Lands outside the two-stage `QUALITY.md` gate, at 25/29
   reviewed alongside `srx-initial-setup` and `srx-syslog-logging`. The README and
   QUALITY tables must say so rather than implying parity.
4. **Trigger competition with `parsing-cisco-configs`.** Mitigated by grammar-keyed
   descriptions and an explicit hand-off clause in both directions; verified by
   retrieval tests in the plan.
