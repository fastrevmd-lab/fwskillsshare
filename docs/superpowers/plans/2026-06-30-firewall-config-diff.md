# firewall-config-diff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a skill that semantically diffs two firewall configs via the shared `parsing-*` intermediate schema (same- or cross-vendor), producing a per-section report + parity verdict, and enabling the round-trip conversion self-test.

**Architecture:** A documentation skill (Markdown) under `skills/firewall-config-diff/`. Lean SKILL.md holds input routing, the semantic-identity matching rules, and the output/verdict templates; `references/equivalence-rules.md` carries per-section semantic identity + the cross-vendor not-comparable catalog; `references/example-diff.md` shows three worked scenarios. Read-only consumer of the schema — no shared-schema edits.

**Tech Stack:** Markdown + YAML frontmatter. Verification is structural (frontmatter, reference-pointer resolution, content greps) — same as the other tooling skills. No pytest; no device needed.

## Global Constraints

- New skill dir/name `firewall-config-diff`; frontmatter `name` == dir; description starts "Use when", ≤1024 chars; `author: [fastrevmd-lab, Claude]`; `license: MIT`; `version: 1.0.0`.
- **Semantic diff only** (meaning-based, order- and name-insensitive) — never a textual/line diff.
- Full-config scope: compare all schema sections (objects/groups, security policies, NAT, zones, interfaces, static/OSPF/BGP routing, system, admin, DHCP, HA, VPN, screens, schedules, security_services).
- Input model: two inputs A and B, each an intermediate schema or raw config; raw → run the matching `parsing-*` skill first; never re-implement parsing.
- Cross-vendor: compare by meaning; a feature with no cross-vendor equivalent is reported `not-comparable` (`vendor-specific / not directly comparable`), never a false diff.
- Output = per-section report (`unchanged`/`added`/`removed`/`changed`, rule order reported separately) + a parity verdict; two framings (drift / parity) one mechanism; always list what could not be compared.
- **Self-contained:** reference only files inside this skill's own `references/`. The round-trip example must use INLINE schema snippets and cite `firewall-config-conversion` by name — never path-reference another skill's files.
- Canonical schema section names: `skills/parsing-srx-configs/references/intermediate-schema.md`. Worked-example source fixture: `skills/parsing-cisco-configs/references/fixture-expected-output.json`.
- Re-sync the new skill into `~/.claude/skills/` at the end. No real secrets in any example.

---

### Task 1: Skill skeleton (SKILL.md)

**Files:**
- Create: `skills/firewall-config-diff/SKILL.md`

**Interfaces:**
- Produces: body sections `Overview`, `When to Use`, `Input Handling`, `Semantic Identity`, `Diff Workflow`, `Output & Verdict`, `Reference Material`, `Common Pitfalls`, `Verification Checklist`. Names `references/equivalence-rules.md` and `references/example-diff.md` (Tasks 2–3). Defines the exact Output & Verdict templates and the semantic-identity rules that Tasks 2–3 reuse.

- [ ] **Step 1: Write frontmatter exactly**

```yaml
---
name: firewall-config-diff
description: Use when comparing two firewall / NGFW configurations to find differences, drift, or parity — same-vendor (config drift, HA-pair consistency, pre/post-change) or cross-vendor (migration parity, round-trip conversion validation). Operates on the parsing-* intermediate schema; for raw config, run the matching parsing-cisco/fortinet/palo/srx skill first. Compares by meaning (order- and name-insensitive), not text: pairs objects/policies/NAT/zones/routing/etc. by semantic identity and reports added / removed / changed per section plus a parity verdict. Cross-vendor features with no equivalent are flagged not-comparable, never a false diff.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
license: MIT
metadata:
  hermes:
    tags: [firewall, ngfw, diff, compare, drift, parity, ha-pair, migration-validation, round-trip, cross-vendor, intermediate-schema, semantic-diff]
    related_skills: [parsing-cisco-configs, parsing-fortinet-configs, parsing-palo-configs, parsing-srx-configs, firewall-config-conversion, firewall-best-practices-audit]
---
```

- [ ] **Step 2: Write the body sections** (real prose):
  - `Overview` — semantic comparison over the schema pivot; same- and cross-vendor are one mechanism; output is a per-section report + parity verdict; a textual diff would add nothing.
  - `When to Use` — "diff/compare these two configs", config drift, HA-pair consistency, pre/post-change or pre/post-migration parity, round-trip conversion validation. When NOT: emitting a target config (→ firewall-config-conversion), best-practice assessment (→ firewall-best-practices-audit), a textual line diff (use `diff`).
  - `Input Handling` — two inputs A and B; each a schema or raw config (raw → matching parsing-* skill first); the source vendor may be in `metadata.source_vendor` (canonical) or `metadata.vendor` (some fixtures); never re-implement parsing.
  - `Semantic Identity` — the matching rules from Step 3.
  - `Diff Workflow` — 1. normalize A and B to schema. 2. for each section, pair items by semantic identity. 3. classify unchanged/changed/added/removed; note rule-order changes separately. 4. for cross-vendor, normalize via `references/equivalence-rules.md` and flag not-comparable features. 5. emit the per-section report + verdict.
  - `Reference Material` — point to equivalence-rules.md and example-diff.md.
  - `Common Pitfalls` and `Verification Checklist` — from Steps 5–6.

- [ ] **Step 3: Write the Semantic Identity section** (exact rules):
```
Items pair across A and B by MEANING, not name or order:
- address objects: by value (e.g. 10.0.1.10/32), not object name.
- service objects: by protocol + port(s). applications: by canonical app name.
- address/service groups: by their expanded member set.
- security policies: by the tuple (src_addresses, dst_addresses, service/app, action, src_zones, dst_zones), addresses compared by value.
- nat_rules: by (match addresses/zones + translation).
- interfaces: by name/unit + address. static routes: by prefix + next-hop. OSPF/BGP: by area/AS + neighbor.
- system / admin_users / dhcp / ha / screens / schedules / security_services: by their natural key (name or the field identity).
A matched pair is `unchanged` (all attributes equal) or `changed` (same identity, ≥1 differing attribute — e.g. logging, profile, description). Unmatched in A only = `removed`; in B only = `added`.
Security-policy ORDER differences are reported separately (order affects shadowing) and do NOT count as add/remove.
```

- [ ] **Step 4: Add the exact Output & Verdict templates** (Tasks 2–3 reuse verbatim):

````markdown
## Output & Verdict

```text
Parity verdict: <EQUIVALENT | DIFFERENCES FOUND (<n>)>  (A=<vendor>, B=<vendor>)
Section: <name>   unchanged <n>  added <n>  removed <n>  changed <n>[  | order: <n> reordered]
  + [B] <added item — semantic summary>
  - [A] <removed item — semantic summary>
  ~ [A→B] <identity>: <attribute change, e.g. logging off → on>
Not comparable: <sections/features with no cross-vendor equivalent>
```

Framings: **drift** (A=old, B=new → what changed) and **parity** (A vs B → equivalent?) — same mechanism. Never claim more than the schema supports; always list what could not be compared.
````

- [ ] **Step 5: Fill Common Pitfalls** (prose bullets):
```
- Doing a textual/line diff — this skill compares by MEANING over the schema; never diff raw text.
- Treating a rename or reorder as add+remove — match by semantic identity; report order separately.
- Emitting false diffs on cross-vendor non-isomorphic features — flag them not-comparable.
- Re-implementing parsing instead of delegating to the matching parsing-* skill.
- Comparing object NAMES instead of VALUES (two configs can use different names for the same subnet).
- Forgetting NAT can change effective meaning when reasoning about policy equivalence.
- Path-referencing another skill's files in the round-trip example — keep this skill self-contained (inline snippets).
```

- [ ] **Step 6: Fill Verification Checklist**:
```
- [ ] Confirm both inputs are intermediate schema (parse raw first); note each side's vendor.
- [ ] Items paired by semantic identity (value/tuple), not name or order.
- [ ] Each section reports unchanged/added/removed/changed; rule-order changes reported separately.
- [ ] Cross-vendor non-isomorphic features flagged not-comparable, not as false diffs.
- [ ] Output has a parity verdict and lists everything that could not be compared.
- [ ] No textual line-diff; no secrets surfaced in the report.
```

- [ ] **Step 7: Verify frontmatter loadable + valid**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
p=Path("skills/firewall-config-diff/SKILL.md"); t=p.read_text()
assert t.startswith("---"); fm=yaml.safe_load(t[3:t.find("\n---",3)])
assert fm["name"]=="firewall-config-diff"
d=re.sub(r'\s+',' ',re.search(r'^description:\s*(.*?)(?=^\w[\w-]*:|\Z)',t[3:t.find(chr(10)+"---",3)],re.M|re.S).group(1)).strip()
assert 0<len(d)<=1024, len(d)
assert isinstance(fm["author"],list) and len(fm["author"])==2 and fm["license"]=="MIT" and fm["version"]=="1.0.0"
for s in ["Semantic Identity","Output & Verdict"]:
    assert s in t, f"missing section {s}"
print("OK frontmatter; desc",len(d),"chars")
EOF
```
Expected: `OK frontmatter; desc <N> chars`, N ≤ 1024.

- [ ] **Step 8: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-config-diff/SKILL.md
git commit -m "feat: scaffold firewall-config-diff skill body"
```

---

### Task 2: Equivalence rules reference

**Files:**
- Create: `skills/firewall-config-diff/references/equivalence-rules.md`

**Interfaces:**
- Consumes: schema section names; the Semantic Identity rules (Task 1).
- Produces: the per-section equivalence detail + the cross-vendor not-comparable catalog the diff workflow cites.

- [ ] **Step 1: Write `equivalence-rules.md`** with a title/blurb and two parts:
  1. **Per-section semantic identity & attribute comparison.** For each schema section, state (a) the identity key items pair on, and (b) which attributes, when different, make a pair `changed` rather than `unchanged`. Cover all sections: address_objects (identity=value; attrs=type), address_groups (identity=expanded member set), service_objects (identity=proto+port), applications (identity=canonical name), security_policies (identity=src/dst/app/action/zones tuple; change-attrs=logging, security_profiles, description, schedule, disabled), nat_rules (identity=match+translation), interfaces, static/OSPF/BGP routing, system, admin_users, dhcp, ha_config, screens, schedules, security_services.
  2. **Cross-vendor not-comparable catalog.** Canonical-app normalization (junos-https == Palo ssl/web-browsing == FortiGate HTTPS == Cisco tcp/443 compare equal). Then per concept, what has NO cross-vendor equivalent and is flagged `not-comparable`: SRX application-services vs Palo security-profile-group vs FortiGate UTM vs ASA none; IKE/IPsec crypto specifics; zone model differences (named zones vs ASA nameif/security-level vs FortiGate interface-zones); routing-instances/VRF vs vsys/contexts; vendor-only screen/DoS options. This is informed by the `firewall-config-conversion` skill's feature-mapping knowledge but is written self-contained here (do NOT path-reference that skill's files).

- [ ] **Step 2: Verify coverage.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
from pathlib import Path
t=Path("skills/firewall-config-diff/references/equivalence-rules.md").read_text().lower()
for sec in ["address","service","application","security_polic","nat","zone","interface","route","vpn","screen","schedule"]:
    assert sec in t, f"missing section {sec}"
assert "not-comparable" in t or "not comparable" in t, "missing not-comparable catalog"
for v in ["srx","palo","forti","cisco"]:
    assert v in t, f"missing vendor {v}"
# self-contained: no cross-skill path
assert "skills/firewall-config-conversion" not in t, "cross-skill path reference present"
assert len(t.split())>=200, "too thin"
print("OK equivalence-rules: sections + cross-vendor catalog, self-contained")
EOF
```
Expected: `OK equivalence-rules: sections + cross-vendor catalog, self-contained`.

- [ ] **Step 3: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-config-diff/references/equivalence-rules.md
git commit -m "feat: add semantic-identity + cross-vendor not-comparable rules for diff"
```

---

### Task 3: Worked examples (drift + parity + round-trip)

**Files:**
- Create: `skills/firewall-config-diff/references/example-diff.md`
- Read (input, do not modify): `skills/parsing-cisco-configs/references/fixture-expected-output.json`

**Interfaces:**
- Consumes: the Output/Verdict templates + Semantic Identity rules (Task 1); equivalence-rules.md (Task 2).

- [ ] **Step 1: Read the source fixture**

Run:
```bash
cd /home/mharman/fwskillsshare && sed -n '1,200p' skills/parsing-cisco-configs/references/fixture-expected-output.json
```

- [ ] **Step 2: Write `example-diff.md`** with three scenarios, each using the exact Output & Verdict template:
  1. **Same-vendor drift:** config A = the Cisco fixture's real objects/policies/NAT; config B = the same with a small realistic change (e.g. add one permit policy, change one address object's value, toggle logging on OUTSIDE-IN-1). Show the per-section report: the added policy as `+`, the object as `~`, the logging change as `~`, everything else `unchanged`; verdict `DIFFERENCES FOUND (n)`. Use only fixture-real items as the base; the B-side changes are clearly labeled as the modified copy.
  2. **Cross-vendor parity (short):** a small ASA-shaped vs SRX-shaped pair (inline snippets) that is semantically equivalent for the comparable sections, with `vpn_tunnels` / security-profiles flagged `not-comparable`. Verdict notes equivalence on comparable sections.
  3. **Round-trip conversion self-test:** original Cisco fixture schema (A) vs the schema you get by re-parsing the SRX config that `firewall-config-conversion` emits for that fixture (B). Show the inline before/after schema snippets (do NOT path-reference the conversion skill's files — cite it by name), and a diff that surfaces the fidelity gaps (e.g. ASA nameif/security-level → SRX zone names differ; any lossy mapping). Frame it as measuring conversion fidelity.
  Redact secrets; every section line uses the template.

- [ ] **Step 3: Verify the example structure + self-containment.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
from pathlib import Path
ex=Path("skills/firewall-config-diff/references/example-diff.md").read_text()
assert ex.count("Parity verdict:")>=3, "expected 3 scenarios with verdicts"
for marker in ["+ [B]","- [A]","~ [A→B]"]:
    assert marker in ex, f"missing diff marker {marker}"
assert "not-comparable" in ex.lower() or "not comparable" in ex.lower(), "cross-vendor not-comparable not shown"
assert "round-trip" in ex.lower() or "round trip" in ex.lower(), "round-trip scenario missing"
assert "skills/firewall-config-conversion" not in ex, "cross-skill path reference present (must be self-contained)"
print("OK example: 3 scenarios incl round-trip, self-contained")
EOF
```
Expected: `OK example: 3 scenarios incl round-trip, self-contained`.

- [ ] **Step 4: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-config-diff/references/example-diff.md
git commit -m "feat: add worked diff examples (drift, cross-vendor parity, round-trip)"
```

---

### Task 4: Validation + housekeeping

**Files:**
- Modify: `README.md` (skill table + install/uninstall + verify-grep + tree + count), `TODO.md` (tick `firewall-config-diff`), the four `skills/parsing-*/SKILL.md` (cross-link)

- [ ] **Step 1: Full repo validation (frontmatter + reference pointers).**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
fail=0
for p in sorted(Path("skills").glob("*/SKILL.md")):
    d=p.parent.name; t=p.read_text(); e=t.find("\n---",3); yaml.safe_load(t[3:e]); body=t[e+4:]
    for ref in set(re.findall(r'references/([A-Za-z0-9._-]+)', body)):
        if not (p.parent/"references"/ref).exists(): print("dangling",d,ref); fail+=1
print(("OK" if not fail else f"{fail} FAIL"),"—",len(list(Path('skills').glob('*/SKILL.md'))),"skills")
EOF
```
Expected: `OK — 20 skills`.

- [ ] **Step 2: README skill-table row** (after the `firewall-config-conversion` row):
```markdown
| [firewall-config-diff](skills/firewall-config-diff/) | Cross-vendor (Cisco/FortiGate/Palo/SRX via parsers) | `diff firewall config`, `compare`, `config drift`, `HA-pair`, `parity`, `migration validation`, `round-trip` |
```

- [ ] **Step 3:** Add Claude + Hermes install examples and uninstall lines for `firewall-config-diff` mirroring existing per-skill blocks; add it to the hermes verify-grep alternation; add a `firewall-config-diff/` entry to the "Verify installation" directory tree (SKILL.md + references/ listing equivalence-rules.md, example-diff.md) after the `firewall-config-conversion/` block; bump the "## Skills Included" count to **20 skills** and fold the diff skill into the tooling family wording.

- [ ] **Step 4: Tick TODO.** In `TODO.md` change `3. [ ] \`firewall-config-diff\`` to `3. [x]`.

- [ ] **Step 5: Cross-link** — append `, firewall-config-diff` inside the `related_skills: [...]` list in each of the four `parsing-*/SKILL.md`.

- [ ] **Step 6: Re-sync + parity.**

Run:
```bash
cd /home/mharman/fwskillsshare
DEST="$HOME/.claude/skills/firewall-config-diff"
rm -rf "$DEST" && cp -r skills/firewall-config-diff "$DEST"
diff -rq skills/firewall-config-diff "$DEST" && echo "PARITY OK"
```
Expected: `PARITY OK`.

- [ ] **Step 7: Commit**

```bash
cd /home/mharman/fwskillsshare
git add README.md TODO.md skills/parsing-*/SKILL.md
git commit -m "docs: register firewall-config-diff (README, TODO, cross-links)"
```

---

## Notes for the executor

- Author Markdown in full prose at execution time; the plan fixes structure, the section list, the exact templates/identity rules, and the verification gates.
- Do NOT invent schema fields — section names come from `skills/parsing-srx-configs/references/intermediate-schema.md`.
- Semantic diff only; never a textual line diff. Keep the skill self-contained — the round-trip example uses inline snippets and cites `firewall-config-conversion` by name, never by file path.
