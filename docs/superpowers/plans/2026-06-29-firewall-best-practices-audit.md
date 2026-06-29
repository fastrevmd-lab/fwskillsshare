# firewall-best-practices-audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a vendor-neutral firewall best-practices / rulebase hardening audit skill that consumes the `parsing-*` intermediate schema and emits prioritized security + operational findings.

**Architecture:** A Claude Code / Hermes documentation skill (`SKILL.md` + `references/`) under `skills/firewall-best-practices-audit/`. A lean body holds routing, the severity rubric, the audit workflow, and output templates; a heavy `check-catalog.md` and per-vendor `remediation-patterns.md` load on demand (progressive disclosure). One vendor-neutral engine operates on the intermediate schema; raw config is handled by delegating to the matching `parsing-*` skill (bounded to Cisco/Palo/FortiGate/SRX).

**Tech Stack:** Markdown + YAML frontmatter. Verification is structural (Python one-liners validating frontmatter and reference pointers — the same checks used elsewhere in this repo) plus a behavioral pass auditing a real `parsing-*` fixture. No pytest; this repo has no skill test framework, only `scripts/check-shared-schema.py`.

## Global Constraints

- Skill dir name `firewall-best-practices-audit`; frontmatter `name:` MUST equal the dir name (kebab-case `[a-z0-9-]`, ≤64 chars).
- `description:` starts with "Use when…", keyword-rich, ≤1024 characters.
- `license: MIT`. `author: [fastrevmd-lab, Claude]` (YAML list).
- Skill must be **self-contained** when its dir is copied alone; reference only files inside its own `references/`. No cross-skill file paths.
- **Progressive disclosure:** keep the body lean; heavy catalog + per-vendor remediation live in `references/` and are pointed to from the body.
- **Framework-agnostic:** general hygiene only. State the clean separation from the `*-ngfw-compliance` skills; do NOT map findings to named compliance controls.
- **Input model:** operate on the `parsing-*` intermediate schema; for raw config, delegate to the matching parser; unsupported vendor → "no parser available; supply a parsed schema or a supported vendor (Cisco ASA/FTD, Palo PAN-OS, FortiGate, Juniper SRX)." Never re-implement parsing.
- **Graceful degradation:** a check needing an absent schema field is skipped with a noted caveat, not failed.
- **No overclaiming:** output never asserts a config is "secure" or "compliant" — only "no in-scope findings," with caveats + skipped checks listed.
- **No secrets** in any example (no real PSKs/keys; use placeholders).
- After any content change, re-sync the skill into `~/.claude/skills/` (user-scoped install) as the final step.

---

### Task 1: Skill skeleton — frontmatter + lean body with reference pointers

**Files:**
- Create: `skills/firewall-best-practices-audit/SKILL.md`
- Create (empty dir placeholder via the reference tasks): `skills/firewall-best-practices-audit/references/`

**Interfaces:**
- Produces: the skill `name: firewall-best-practices-audit`; body sections `Overview`, `When to Use`, `Input Handling`, `Severity & Confidence`, `Audit Workflow`, `Reference Material`, `Output Templates`, `Common Pitfalls`, `Verification Checklist`. The `Reference Material` section names `references/check-catalog.md`, `references/remediation-patterns.md`, `references/example-audit.md` (created in Tasks 2–4).

- [ ] **Step 1: Write `SKILL.md` with this exact frontmatter and section skeleton**

```markdown
---
name: firewall-best-practices-audit
description: Use when auditing or reviewing a firewall or NGFW rulebase for security and operational best-practice hygiene, independent of any compliance framework. Covers overly permissive and any-any rules, shadowed/redundant/overlapping/orphaned rules, missing deny-all and logging, dangerous exposed services, plaintext management (telnet/http/SNMPv1-2c), weak VPN/IKE/IPsec crypto, and operational cleanup (unused/duplicate objects, oversized groups, naming/description gaps, rule consolidation). Operates on the parsing-* intermediate schema; for raw config, run the matching parsing-cisco/fortinet/palo/srx skill first. Emits prioritized findings with severity, confidence, and vendor-neutral plus source-vendor remediation.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
license: MIT
metadata:
  hermes:
    tags: [firewall, ngfw, audit, best-practices, hardening, rulebase-review, security-hygiene, shadowed-rules, least-privilege, logging, vpn-crypto, object-cleanup, vendor-neutral]
    related_skills: [parsing-cisco-configs, parsing-fortinet-configs, parsing-palo-configs, parsing-srx-configs, pci-ngfw-compliance, hipaa-ngfw-compliance, cmmc-nist-800-171-ngfw-compliance, cis-controls-ngfw-compliance, iso27001-ngfw-compliance, soc2-ngfw-compliance]
---

# Firewall Best-Practices Audit

## Overview

[2–3 paragraphs: vendor-neutral hardening audit over the parsing-* intermediate
schema; framework-agnostic (state the clean split from the *-ngfw-compliance
skills: this = general hygiene, those = framework-mapped evidence); emits
prioritized findings with remediation. Never claims a config is "secure".]

## When to Use

[Bullets of triggering asks: "audit/review this firewall rulebase", "is this
config hardened", "find permissive/shadowed/unused rules", "firewall hygiene
review", cross-vendor rulebase audit. When NOT to use: compliance-framework
mapping -> compliance skills; raw config for a vendor with no parser.]

## Input Handling

[Routing logic: parsed intermediate schema -> audit directly. Raw config ->
identify vendor, run the matching parsing-* skill to produce the schema, then
audit. Unsupported vendor -> the no-parser message. Never re-implement parsing.
Graceful degradation: list any checks skipped for missing schema fields.]

## Severity & Confidence

[Compact rubric table: Critical/High/Medium/Low/Info with one-line criteria.
Confidence: definitive vs heuristic, and when a finding is downgraded to
heuristic (incomplete rule order or unresolved object refs).]

## Audit Workflow

[Numbered: 1. Establish input + vendor. 2. Resolve objects/zones. 3. Run the
security checks (point to references/check-catalog.md). 4. Run the operational
checks. 5. Assign severity + confidence. 6. Attach remediation (point to
references/remediation-patterns.md). 7. Produce the summary + prioritized fixes.]

## Reference Material (load on demand)

- `references/check-catalog.md` — full catalog of security + operational checks (id, what it detects, schema fields, severity rationale).
- `references/remediation-patterns.md` — per-vendor (Cisco/Palo/FortiGate/SRX) fix snippets keyed by finding category.
- `references/example-audit.md` — a worked audit against a parsing-* fixture.

## Output Templates

[Finding template + Audit summary template — see Step 2.]

## Common Pitfalls

[8–12 bullets — see Step 3.]

## Verification Checklist

[Pre-finalize checklist — see Step 4.]
```

- [ ] **Step 2: Fill the Output Templates section with these two exact templates**

````markdown
### Finding

```text
[<id>] <CRITICAL|HIGH|MEDIUM|LOW|INFO> (<definitive|heuristic>) — <title>
Category: <security|operational> / <subcategory>
Affected: <rule names/IDs, object names, zones>
Why it matters: <1–3 lines>
Remediation: <vendor-neutral guidance>
Fix (<source-vendor>):
  <concrete snippet in the source vendor's syntax>
```

### Audit Summary

```text
Posture: <one line; never "secure" — say "no in-scope findings" with caveats>
Findings: Critical <n>  High <n>  Medium <n>  Low <n>  Info <n>
Checks skipped (no data): <e.g. hit-count-dependent checks>
Top fixes (prioritized):
  1. <id> — <one line>
  2. <id> — <one line>
```
````

- [ ] **Step 3: Fill Common Pitfalls** (write these as prose bullets)

```
- Claiming a config is "secure"/"compliant" — only report "no in-scope findings" with caveats.
- Mapping findings to PCI/HIPAA/etc. — that is the compliance skills' job; stay framework-agnostic.
- Re-implementing parsing instead of delegating to the parsing-* skill.
- Reporting heuristic findings (possible shadow) as definitive when rule order/object refs are incomplete.
- Auditing only the internet edge; include internal, mgmt, VPN, and inter-zone rules.
- Ignoring NAT when reasoning about real exposure.
- Flagging disabled rules as active risk (note them as cleanup, not exposure).
- Treating an unreferenced object as a finding without confirming the schema captured all references.
- Putting real secrets/PSKs in example output.
- Silently dropping checks when a schema field is missing — list them as skipped.
```

- [ ] **Step 4: Fill Verification Checklist** (pre-finalize list)

```
- [ ] Confirm input type (parsed schema vs raw config) and source vendor.
- [ ] For raw config, the matching parsing-* skill was run first.
- [ ] Every finding has id, severity, confidence, affected refs, rationale, remediation.
- [ ] Remediation includes vendor-neutral guidance + a source-vendor snippet.
- [ ] Heuristic findings are labeled; definitive vs heuristic is correct.
- [ ] Skipped checks (missing schema fields) are listed in the summary.
- [ ] Output makes no "secure"/"compliant" claim and no compliance-framework mapping.
- [ ] No real secrets in any snippet.
```

- [ ] **Step 5: Verify frontmatter is valid and loadable**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
p=Path("skills/firewall-best-practices-audit/SKILL.md"); t=p.read_text()
assert t.startswith("---"); e=t.find("\n---",3); fm=t[3:e]
y=yaml.safe_load(fm)
assert y["name"]=="firewall-best-practices-audit", y["name"]
d=re.sub(r'\s+',' ',re.search(r'^description:\s*(.*?)(?=^\w[\w-]*:|\Z)',fm,re.M|re.S).group(1)).strip()
assert 0<len(d)<=1024, len(d)
assert isinstance(y["author"],list) and len(y["author"])==2
assert y["license"]=="MIT"
print("OK frontmatter; desc",len(d),"chars")
EOF
```
Expected: `OK frontmatter; desc <N> chars` with N ≤ 1024.

- [ ] **Step 6: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/SKILL.md
git commit -m "feat: scaffold firewall-best-practices-audit skill body"
```

---

### Task 2: Check catalog reference

**Files:**
- Create: `skills/firewall-best-practices-audit/references/check-catalog.md`

**Interfaces:**
- Consumes: the `Audit Workflow` section points here.
- Produces: a stable set of check IDs the body and `example-audit.md` reference. The IDs below are the contract — do not rename them later without updating Task 4.

- [ ] **Step 1: Write `check-catalog.md` with a title, a provenance blurb, and one entry per check**

Header:
```markdown
# Firewall Best-Practices Audit — Check Catalog

> Reference material for the `firewall-best-practices-audit` skill; loaded on
> demand. Each entry: id, what it detects, the intermediate-schema fields it
> reads, default severity, and confidence notes.
```

Include exactly these checks (id — detects — primary schema fields — default severity — confidence):

Security:
```
- SEC-ANY-ANY — permit rule with any source AND any destination AND any service — rules[].{src,dst,service,action} — CRITICAL (HIGH if logged) — definitive
- SEC-ANY-SVC — permit rule with any/any-service but specific src+dst — rules[].{service,action} — MEDIUM — definitive
- SEC-BROAD-SRC — permit with overly broad source (0.0.0.0/0 or very large supernet) — rules[].src, objects — HIGH — definitive
- SEC-BROAD-DST — permit with overly broad destination — rules[].dst, objects — MEDIUM — definitive
- SEC-LARGE-PORTRANGE — service spanning a very large port range — service objects — LOW — definitive
- SEC-SHADOW — rule fully shadowed by an earlier broader rule — ordered rules[], resolved objects — HIGH — heuristic (needs full order + resolution)
- SEC-REDUNDANT — duplicate rule (same match + action as another) — rules[] — LOW — definitive
- SEC-OVERLAP — overlapping rules with differing actions (ordering risk) — ordered rules[] — MEDIUM — heuristic
- SEC-ORPHAN-REF — rule references a missing/undefined object — rules[] vs objects — MEDIUM — definitive
- SEC-DISABLED — disabled-but-present rule (cleanup) — rules[].enabled — INFO — definitive
- SEC-NO-DENY-ALL — no terminal explicit deny-all where the vendor model expects it — rules[] tail, vendor — MEDIUM — heuristic
- SEC-NO-LOG — permit rule without logging — rules[].log — LOW (MEDIUM if broad) — definitive
- SEC-NO-DESC — rule missing description/owner — rules[].description — INFO — definitive
- SEC-EXPOSED-MGMT — device management service reachable from untrusted/any — rules[], zones, service — HIGH — definitive
- SEC-EXPOSED-RISKY — risky services (RDP/SMB/DB/telnet) reachable from untrusted/any — rules[], service, zones — HIGH — definitive
- SEC-INBOUND-ANY — inbound any-from-internet permit — rules[], zones — HIGH — definitive
- SEC-PLAINTEXT-MGMT — plaintext management enabled (telnet/http/SNMPv1-2c) — mgmt/system services — HIGH — definitive
- SEC-MGMT-DATAZONE — management services exposed to data/untrusted zones — zones, host-inbound/mgmt — MEDIUM — definitive
- SEC-WEAK-IKE — weak IKE (DH<14, 3DES/DES, MD5/SHA-1, aggressive mode) — vpn.ike — HIGH — definitive
- SEC-WEAK-IPSEC — weak IPsec (no PFS, weak ESP enc/auth) — vpn.ipsec — MEDIUM — definitive
- SEC-PSK-WEAK — reused/weak PSK indicators where visible — vpn.psk — MEDIUM — heuristic
```

Operational:
```
- OPS-UNUSED-OBJ — address/service object defined but unreferenced — objects vs rules[]/nat/groups — LOW — heuristic (needs complete ref capture)
- OPS-DUP-OBJ — duplicate objects (same value, different name) — objects — LOW — definitive
- OPS-LARGE-GROUP — oversized group (member count over threshold) — groups — INFO — definitive
- OPS-NESTED-GROUP — deeply nested group (depth over threshold) — groups — INFO — definitive
- OPS-NO-DESC-OBJ — object/group missing description — objects/groups.description — INFO — definitive
- OPS-NAMING — non-standard / inconsistent naming — objects/rules names — INFO — heuristic
- OPS-CONSOLIDATE — rules consolidatable (same action, contiguous, differ only by one field) — rules[] — LOW — heuristic
- OPS-REDUNDANT-OBJ — redundant objects (subset/superset duplicates) — objects — LOW — heuristic
- OPS-ZERO-HIT — zero-hit rule (only when usage/hit-count data is present) — rules[].hit_count — LOW — definitive (skip if no data)
```

End with a short "Thresholds" note defining the tunable thresholds referenced above (broad supernet, large port range, large/nested group) with default values, e.g. broad source ≥ /8 or 0.0.0.0/0; large port range ≥ 1024 ports; large group ≥ 50 members; nesting depth ≥ 3.

- [ ] **Step 2: Verify the catalog covers every spec category and IDs are unique**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re
from pathlib import Path
t=Path("skills/firewall-best-practices-audit/references/check-catalog.md").read_text()
ids=re.findall(r'^- ((?:SEC|OPS)-[A-Z-]+) —', t, re.M)
assert len(ids)==len(set(ids)), "duplicate ids: "+str([i for i in ids if ids.count(i)>1])
assert sum(i.startswith("SEC-") for i in ids)>=20, "missing security checks"
assert sum(i.startswith("OPS-") for i in ids)>=9, "missing operational checks"
assert len(t.split())>=80, "catalog too thin"
print("OK catalog:",len(ids),"checks")
EOF
```
Expected: `OK catalog: 30 checks` (21 SEC + 9 OPS; or more if you add checks).

- [ ] **Step 3: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/references/check-catalog.md
git commit -m "feat: add firewall audit check catalog"
```

---

### Task 3: Per-vendor remediation patterns reference

**Files:**
- Create: `skills/firewall-best-practices-audit/references/remediation-patterns.md`

**Interfaces:**
- Consumes: finding categories / IDs from Task 2 (`check-catalog.md`).
- Produces: per-vendor fix snippets the body's Finding template draws on for the `Fix (<source-vendor>)` line.

- [ ] **Step 1: Write `remediation-patterns.md`** with a title/blurb and a subsection per finding family, each giving a concrete fix snippet for all four vendors (Cisco ASA/FTD, Palo PAN-OS, FortiGate, Juniper SRX). Cover at minimum these families: overly-permissive/any-any (tighten src/dst/service), missing logging (enable per-rule logging), plaintext management (replace telnet/http with ssh/https; disable SNMPv1/2c), exposed risky/mgmt services (scope source, move mgmt off data zones), weak IKE/IPsec (raise DH≥14, AES-GCM, SHA-256, enable PFS, disable aggressive mode), shadowed/redundant rules (reorder/remove), object cleanup (remove unused/duplicate, flatten oversized groups).

Use this structure (example for one family — write all families this way; **placeholders only, no real secrets**):

```markdown
## Overly permissive / any-any (SEC-ANY-ANY, SEC-ANY-SVC, SEC-BROAD-SRC, SEC-BROAD-DST)

Vendor-neutral: replace any with the specific source zones/subnets, destination
hosts, and named services required by business need; add logging; record owner.

- Cisco ASA/FTD: `access-list OUTSIDE_IN extended permit tcp <src-obj> <dst-obj> eq <port>` then `access-group OUTSIDE_IN in interface outside` (remove the any/any ACE).
- Palo PAN-OS: set the security rule `source`, `destination`, and `service` to specific objects; set `action allow` with `log-end yes`; remove `any` members.
- FortiGate: `config firewall policy / edit <id> / set srcaddr <obj> / set dstaddr <obj> / set service <svc> / set logtraffic all / next / end`.
- Juniper SRX: `set security policies from-zone <z> to-zone <z> policy <name> match source-address <obj> destination-address <obj> application <app>` then `then permit log session-close`.
```

- [ ] **Step 2: Verify each required family has all four vendors**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re
from pathlib import Path
t=Path("skills/firewall-best-practices-audit/references/remediation-patterns.md").read_text()
sections=re.split(r'(?m)^## ', t)[1:]
assert len(sections)>=7, f"need >=7 families, got {len(sections)}"
for s in sections:
    title=s.splitlines()[0]
    for v in ["Cisco","Palo","FortiGate","SRX"]:
        assert v in s, f"family '{title}' missing {v}"
print("OK remediation:",len(sections),"families x 4 vendors")
EOF
```
Expected: `OK remediation: <N> families x 4 vendors` with N ≥ 7.

- [ ] **Step 3: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/references/remediation-patterns.md
git commit -m "feat: add per-vendor remediation patterns for firewall audit"
```

---

### Task 4: Worked example against a real parsing fixture (behavioral test)

**Files:**
- Create: `skills/firewall-best-practices-audit/references/example-audit.md`
- Read (input, do not modify): `skills/parsing-cisco-configs/references/fixture-expected-output.json`

**Interfaces:**
- Consumes: check IDs from Task 2; templates from Task 1; remediation families from Task 3.

- [ ] **Step 1: Read the fixture to audit**

Run:
```bash
cd /home/mharman/fwskillsshare && sed -n '1,200p' skills/parsing-cisco-configs/references/fixture-expected-output.json
```
Note the rules/objects present so the example's findings are grounded in real fixture content.

- [ ] **Step 2: Write `example-audit.md`** that: (a) names the input fixture, (b) walks the audit workflow over it, (c) emits 3–6 findings using the exact Finding template (each with a real `SEC-*`/`OPS-*` id from the catalog, severity, confidence, affected refs taken from the fixture, vendor-neutral remediation, and a `Fix (Cisco ASA/FTD)` snippet), and (d) ends with the Audit Summary template including a "Checks skipped (no data)" line (e.g. SEC/OPS checks needing hit counts if the fixture lacks them). Every id used MUST exist in `check-catalog.md`. No invented rule names — use only what the fixture contains.

- [ ] **Step 3: Verify the example only uses catalog IDs and references a real fixture**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re
from pathlib import Path
cat=Path("skills/firewall-best-practices-audit/references/check-catalog.md").read_text()
catalog_ids=set(re.findall(r'(?:SEC|OPS)-[A-Z-]+', cat))
ex=Path("skills/firewall-best-practices-audit/references/example-audit.md").read_text()
used=set(re.findall(r'\[((?:SEC|OPS)-[A-Z-]+)\]', ex))
assert used, "no findings in example"
unknown=used-catalog_ids
assert not unknown, f"example uses unknown ids: {unknown}"
assert "fixture-expected-output.json" in ex, "example must name its input fixture"
assert "Posture:" in ex and "Top fixes" in ex, "missing summary"
print("OK example: findings",sorted(used))
EOF
```
Expected: `OK example: findings [...]` listing 3–6 valid IDs.

- [ ] **Step 4: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/references/example-audit.md
git commit -m "feat: add worked firewall audit example against cisco fixture"
```

---

### Task 5: Integration verification + housekeeping

**Files:**
- Modify: `README.md` (skill table + Claude/Hermes install examples + uninstall lists + verify-grep)
- Modify: `TODO.md` (tick the `firewall-best-practices-audit` item)
- Modify: `skills/parsing-cisco-configs/SKILL.md`, `skills/parsing-fortinet-configs/SKILL.md`, `skills/parsing-palo-configs/SKILL.md`, `skills/parsing-srx-configs/SKILL.md` (add `firewall-best-practices-audit` to each `related_skills`)

**Interfaces:**
- Consumes: the finished skill from Tasks 1–4.

- [ ] **Step 1: Full skill validation (frontmatter + reference pointers resolve) across the repo**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
fail=0
for p in sorted(Path("skills").glob("*/SKILL.md")):
    d=p.parent.name; t=p.read_text(); e=t.find("\n---",3); fm=t[3:e]; body=t[e+4:]
    y=yaml.safe_load(fm)
    if y["name"]!=d: print("name!=dir",d); fail+=1
    for ref in set(re.findall(r'references/([A-Za-z0-9._-]+)', body)):
        if not (p.parent/"references"/ref).exists(): print("dangling",d,ref); fail+=1
print("OK" if not fail else f"{fail} FAIL", "—", len(list(Path('skills').glob('*/SKILL.md'))), "skills")
EOF
```
Expected: `OK — 18 skills`.

- [ ] **Step 2: Behaviorally verify the skill loads and audits the fixture**

Invoke the skill (Skill tool: `firewall-best-practices-audit`) and confirm: the body loads; following `references/check-catalog.md` and `references/example-audit.md` resolves; the example's findings are coherent against the fixture. Record the observation in the commit message.

- [ ] **Step 3: Add README skill-table row** (after the `srx-ipsec-hub-spoke` row)

```markdown
| [firewall-best-practices-audit](skills/firewall-best-practices-audit/) | Vendor-neutral (Cisco/Palo/FortiGate/SRX via parsers) | `firewall audit`, `best practices`, `hardening`, `rulebase review`, `shadowed rules`, `any-any`, `least privilege`, `unused objects` |
```

- [ ] **Step 4: Add Claude + Hermes install examples and uninstall lines** mirroring the existing per-skill blocks, and add `firewall-best-practices-audit` to the README verify-grep alternation.

- [ ] **Step 5: Tick the TODO item** — in `TODO.md`, change `1. [ ] \`firewall-best-practices-audit\`` to `1. [x] \`firewall-best-practices-audit\``.

- [ ] **Step 6: Cross-link from the four parsing skills** — append `, firewall-best-practices-audit` inside the `related_skills: [...]` list in each of the four `parsing-*/SKILL.md` files.

- [ ] **Step 7: Re-sync into the user skills dir and confirm parity**

Run:
```bash
cd /home/mharman/fwskillsshare
DEST="$HOME/.claude/skills/firewall-best-practices-audit"
rm -rf "$DEST" && cp -r skills/firewall-best-practices-audit "$DEST"
diff -rq skills/firewall-best-practices-audit "$DEST" && echo "PARITY OK"
```
Expected: `PARITY OK`.

- [ ] **Step 8: Commit**

```bash
cd /home/mharman/fwskillsshare
git add README.md TODO.md skills/parsing-*/SKILL.md
git commit -m "docs: register firewall-best-practices-audit (README, TODO, cross-links)"
```

---

## Notes for the executor

- Author each Markdown file in full prose at execution time; the plan fixes the structure, the exact check IDs, the templates, and the verification gates, but you write the explanatory text.
- Keep the body lean — if a section grows large, it belongs in `references/`.
- Do not invent schema fields. If a field named in the catalog is not in the actual intermediate schema, note the check as data-dependent (skipped) rather than inventing structure; cross-check against `skills/parsing-srx-configs/references/intermediate-schema.md` (the canonical schema).
