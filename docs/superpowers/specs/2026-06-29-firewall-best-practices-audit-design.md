# Design: firewall-best-practices-audit

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-06-29.
Author: fastrevmd-lab, Claude.

## Purpose

A vendor-neutral firewall **best-practices / rulebase hardening audit** skill. It
reviews a firewall configuration for security and operational hygiene and emits
prioritized, actionable findings. It is the first *consumer* of the `parsing-*`
intermediate schema, realizing the "unified auditing" the parsers were built for.

It is deliberately **framework-agnostic**: general hygiene, not compliance-control
mapping. The compliance skills (pci/hipaa/cmmc/cis/iso27001/soc2) map firewall
state to named control frameworks; this skill flags risk and cleanup regardless of
any framework. The two are complementary and must not overlap.

## Skill type, metadata, provenance

- Claude Code / Hermes **technique skill**: `SKILL.md` + `references/`.
- Original content (not source-derived) → `license: MIT OR Apache-2.0` (matching the `parsing-*`
  skills).
- `author: [fastrevmd-lab, Claude]`.
- `name: firewall-best-practices-audit`.
- Applies progressive disclosure from the start: lean `SKILL.md` body, heavy
  catalog and per-vendor remediation in `references/` (loaded on demand).

## Decisions (from brainstorming)

1. **Input model — schema-first engine, raw config via delegation.** One
   vendor-neutral analysis engine that operates on the `parsing-*` intermediate
   JSON schema. It accepts either:
   - a parsed schema (audit directly), or
   - raw config — identify the vendor and delegate to the matching `parsing-*`
     skill to produce the schema, then audit.
   The skill does **not** re-implement parsing. Raw-config support is therefore
   inherently bounded to the four vendors with parsers: Cisco ASA/FTD, Palo
   PAN-OS, FortiGate, Juniper SRX. Unsupported vendor → report "no parser
   available; supply a parsed schema or a supported vendor."
2. **Check scope — security + operational hygiene, framework-agnostic.** No
   compliance cross-hints (kept separate from the compliance skills).
3. **Remediation — hybrid.** Each finding carries vendor-neutral guidance **plus**
   a concrete fix snippet in the **source vendor's** syntax (known from the
   schema). Per-vendor fix patterns live in `references/remediation-patterns.md`.

## Architecture and data flow

```
input ──> front door ──> audit engine ──> findings ──> report
          (detect type)   (schema checks)
```

- **Front door:** detect parsed-schema JSON vs raw config; for raw config,
  identify vendor and delegate to the matching `parsing-*` skill; reject
  unsupported vendors with the message above.
- **Audit engine:** run the check catalog against the schema's normalized objects
  — rules/policies, address/service objects, NAT, zones, VPN/crypto, logging,
  management services.
- **Graceful degradation:** a check that needs a schema field not present (e.g.,
  rule hit counts) is **skipped with a noted caveat**, not failed. The audit
  states which checks were skipped for lack of data.

## Check catalog (`references/check-catalog.md`)

Heavy reference, lazy-loaded. Each entry: check id, what it detects, the schema
fields it reads, and the severity rationale.

**Security hygiene**
- Overly permissive rules: any source / any destination / any service; any-service
  permits; very large port ranges; broad src or dst with permit.
- Rule anomalies: shadowed rules (earlier rule fully covers a later one);
  redundant/duplicate rules; overlapping rules; orphaned rules (reference missing
  objects); disabled-but-present rules.
- Hygiene: missing terminal explicit deny-all; permit rules without logging;
  rules missing description/owner.
- Exposure: dangerous services reachable from untrusted/any (RDP, SSH, SMB,
  common DB ports, device management); inbound any-from-internet permits.
- Management plane: plaintext management (telnet, http, SNMPv1/2c); management
  services exposed to data/untrusted zones.
- VPN/crypto: weak IKE/IPsec (DH group < 14, 3DES/DES, MD5/SHA-1, IKE aggressive
  mode, missing PFS), and reused/weak PSK indicators where visible in the schema.

**Operational hygiene**
- Object/group sprawl: unused address/service objects; duplicate objects (same
  value, different name); oversized or deeply nested groups.
- Naming/description: missing or empty descriptions; non-standard naming.
- Optimization: consolidatable rules; redundant objects; zero-hit rules (only when
  usage/hit-count data is present in the schema).

## Severity model

`Critical / High / Medium / Low / Info`. A compact rubric lives in the body; the
catalog assigns a default severity per check with rationale. Examples:
- Critical: permit any→any inbound from an untrusted zone with no logging.
- High: dangerous management service exposed to untrusted; weak VPN crypto on an
  active tunnel.
- Medium: broad rule with logging; plaintext management on an internal-only path.
- Low/Info: naming/description gaps; object sprawl.

Each finding also carries a **confidence flag**: *definitive* (e.g., any-any
permit, plaintext telnet) vs *heuristic* (e.g., possible shadow — best-effort,
flagged when rule order or object resolution is incomplete in the schema).

## Output (templates in body)

**Finding**

```text
[id] <severity> (<confidence>) — <title>
Category: <security|operational> / <subcategory>
Affected: <rule names/IDs, object names, zones>
Why it matters: <1-3 lines>
Remediation: <vendor-neutral guidance>
Fix (<source-vendor>):
  <concrete snippet in the source vendor's syntax>
```

**Audit summary**

```text
Posture: <one line; never "secure" — state "no in-scope findings" with caveats>
Findings: Critical <n>  High <n>  Medium <n>  Low <n>  Info <n>
Checks skipped (no data): <list, e.g. hit-count-dependent checks>
Top fixes (prioritized):
  1. ...
  2. ...
```

The summary must never assert a config is "secure" or "compliant" — only that no
in-scope findings were detected, with stated caveats and skipped checks.

## File layout

```
skills/firewall-best-practices-audit/
  SKILL.md                    # overview, when-to-use, input routing, severity rubric,
                              # audit workflow, output templates, pitfalls, verification
  references/
    check-catalog.md          # full check catalog (heavy, lazy-loaded)
    remediation-patterns.md   # per-vendor fix snippets (cisco/palo/fortinet/srx) by category
    example-audit.md          # one worked example against a parsing fixture
```

## Testing / verification

- Reuse the parsers' existing `fixture-expected-output.json` files as schema
  inputs. `example-audit.md` audits one such fixture end-to-end and shows the
  expected findings — a concrete, re-runnable demonstration (the "one excellent
  example").
- Per writing-skills: the skill is verified by exercising it on a realistic input
  (a fixture schema) and confirming it finds the planted issues and produces a
  coherent report, before deployment.

## Relationship to existing skills and housekeeping

- `related_skills`: `parsing-cisco-configs`, `parsing-fortinet-configs`,
  `parsing-palo-configs`, `parsing-srx-configs` (input producers) + the six
  `*-ngfw-compliance` skills (complementary). Body states the clean separation.
- Housekeeping on completion: add a README skill-table row and install examples;
  optional cross-link from the parsing skills' `related_skills`; tick the item in
  `TODO.md` (Tooling & Operational Skills).

## Out of scope (YAGNI)

- Compliance-framework mapping (owned by the compliance skills).
- Re-implementing config parsing (owned by the `parsing-*` skills).
- Vendors without a parser (no raw-config path until a parser exists).
- Live device interrogation or automated remediation application (the skill emits
  guidance/snippets; it does not push config).
