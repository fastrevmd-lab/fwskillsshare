# parsing-firepower-configs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fifth `parsing-*` skill that parses FMC- and FDM-managed Cisco Secure Firewall (Firepower) JSON exports into the shared firewall intermediate schema.

**Architecture:** A Markdown-first skill package mirroring the four existing parsers exactly — `SKILL.md`, `README.md`, `agents/openai.yaml`, and seven `references/` files including a byte-identical copy of the canonical schema. No schema change: Firepower's rule sections and policy inheritance flatten into a single merged `_rule_index`, with provenance recorded in `metadata`, following the Panorama precedent at `skills/parsing-palo-configs/SKILL.md:386`.

**Tech Stack:** Markdown + YAML frontmatter. Validation is the repository's Python checkers driven by `just`; there is no build system and no runtime code. "Tests" throughout this plan means the validator scripts and the fixture pair.

**Spec:** `docs/superpowers/specs/2026-08-27-parsing-firepower-configs-design.md`

## Global Constraints

Copied verbatim from `AGENTS.md`, `skills/AGENTS.md`, and the validators. Every task's requirements implicitly include these.

- **Skill description: 1,024 characters maximum, hard.** Enforced by Codex and by `scripts/check-skill-packages.py`.
- **Description must contain the exact substring `. Use when `** and must contain no `<` or `>` characters.
- **`author` must be exactly** `["fastrevmd-lab", "Claude", "GPT"]`.
- **`license` must be `MIT`**; `version`, `metadata`, and `name` are required; `name` must equal the directory name and be hyphen-case.
- **`SKILL.md` must be at most 600 lines** (progressive-disclosure limit).
- **Every `references/...` path mentioned in `SKILL.md` must exist**, or `check-skill-packages.py` errors.
- **`agents/openai.yaml` requires** a quoted `display_name`, a quoted `short_description` of **25–64 characters**, and a quoted `default_prompt` containing the literal `$parsing-firepower-configs`.
- **Shared schema copies must be byte-identical.** Canonical copy is `skills/parsing-srx-configs/references/intermediate-schema.md`. Never hand-edit a copy.
- **Fixtures must be synthetic and secret-free.**
- **Keep commits small — target ~80 lines.** `AGENTS.md` records that a ~1,300-line commit never returned a Codex verdict while ~80-line commits returned every time.
- **A Codex run with no final `agent_message` is not a pass.** Use `scripts/codex-review.sh`, never `codex exec review` directly.
- **Vendor claims require authoritative evidence or an explicit uncertain classification.** There is no live FMC in this environment, so the evidence path is Cisco's published FMC/FDM REST API documentation. Do not assert an endpoint name or field spelling that was not checked against a named document and product version; mark everything else `unverified`.

**Pre-existing count drift to correct, not propagate.** Measured on 2026-08-27: the repository has **28** skill directories, but the catalog documents disagree with each other. Six locations say 27 and two say 28:

| Location | Current | Correct after this work |
|---|---|---|
| `README.md:20` badge | `skills-27` | `skills-29` |
| `README.md:21` badge | `reviewed-25%2F27` | `reviewed-25%2F29` |
| `README.md:31` prose | "all 27" | "all 29" |
| `README.md:106` prose | "all 27" | "all 29" |
| `README.md:192` prose | "28 skills" / "25 of the 28" | "29 skills" / "25 of the 29" |
| `README.md:253` prose | "25 of the 27 skills" | "25 of the 29 skills" |
| `SKILLS.md:5` prose | "all 27 skills" | "all 29 skills" |
| `QUALITY.md` opening + family table | 28 / 25-of-28 | 29 / 25-of-29 |

Task 12 fixes all eight. Re-measure before editing rather than trusting this table — it is a snapshot.

**Branch:** the current branch is `chore/declare-version`. Cut a fresh branch (e.g. `feat/parsing-firepower-configs`) before Task 1.

---

### Task 1: Register the skill and scaffold the package

Registration first, so the validators fail for the right reason before any content exists.

**Files:**
- Modify: `scripts/check-skill-packages.py:36-66` (`EXPECTED_SKILL_NAMES`)
- Modify: `scripts/check-installer.py:14-19` (`EXPECTED_FAMILIES["parsers"]`)
- Modify: `install.sh:25-30` (`PARSERS` array)
- Create: `skills/parsing-firepower-configs/SKILL.md`
- Create: `skills/parsing-firepower-configs/agents/openai.yaml`

**Interfaces:**
- Consumes: nothing.
- Produces: the skill name `parsing-firepower-configs`, registered in all three inventories. Every later task adds files under `skills/parsing-firepower-configs/`.

- [ ] **Step 1: Add the name to the three inventories**

In `scripts/check-skill-packages.py`, inside `EXPECTED_SKILL_NAMES`, add after `"parsing-cisco-configs",`:

```python
        "parsing-firepower-configs",
```

In `scripts/check-installer.py`, inside `EXPECTED_FAMILIES["parsers"]`, add after `"parsing-cisco-configs",`:

```python
        "parsing-firepower-configs",
```

In `install.sh`, inside `declare -a PARSERS=(`, add after `"parsing-cisco-configs"`:

```bash
    "parsing-firepower-configs"
```

- [ ] **Step 2: Run the validators to verify they fail**

Run: `python3 scripts/check-skill-packages.py && python3 scripts/check-installer.py`
Expected: FAIL with `missing expected skills: parsing-firepower-configs`

- [ ] **Step 3: Create the minimal skill package**

Create `skills/parsing-firepower-configs/SKILL.md`. The description below was measured at **544 characters** — under the 1,024 hard limit, contains `. Use when `, and contains no angle brackets:

```markdown
---
name: parsing-firepower-configs
description: Parse Cisco Secure Firewall (Firepower) FMC and FDM management exports into the shared firewall schema. Use when input is JSON from the FMC or FDM REST API or an FDM configexport bundle and contains accessPolicy, accessrules, securityZones, prefilterpolicies, intrusionPolicy, filePolicy, variableSet, ftdnatpolicies, applicationFilters, or urlCategories, including audit, conversion, diff, summary, and explanation tasks. For ASA-style LINA running-config text such as access-list, nameif, or object network, use parsing-cisco-configs instead.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags:
    - firewall
    - config-parsing
    - cisco
    - firepower
    - ftd
    - fmc
    - fdm
    - secure-firewall
    - threat-defense
    - access-control-policy
    - security-zone
    - intrusion-policy
    - prefilter
    - migration
    - audit
    related_skills:
    - parsing-cisco-configs
    - parsing-srx-configs
    - parsing-palo-configs
    - parsing-fortinet-configs
    - firewall-best-practices-audit
    - firewall-config-conversion
    - firewall-config-diff
---

# Parsing Cisco Firepower (FMC / FDM) Exports

## Overview

Placeholder body replaced in Task 6.
```

Create `skills/parsing-firepower-configs/agents/openai.yaml`. `short_description` below was measured at **48 characters**, inside the required 25–64 range:

```yaml
interface:
  display_name: "Parsing Firepower Configs"
  short_description: "Parse Cisco Firepower FMC and FDM policy exports"
  default_prompt: "Use $parsing-firepower-configs to parse this Cisco FMC or FDM export into the shared schema."
```

- [ ] **Step 4: Run the validators to verify they pass**

Run: `python3 scripts/check-skill-packages.py && python3 scripts/check-installer.py`
Expected: PASS, no errors. A combined-description warning is acceptable; an error is not.

- [ ] **Step 5: Commit**

```bash
git add scripts/check-skill-packages.py scripts/check-installer.py install.sh skills/parsing-firepower-configs/
git commit -m "feat(firepower): register parsing-firepower-configs skill package"
```

---

### Task 2: Add the byte-identical shared schema copy

**Files:**
- Create: `skills/parsing-firepower-configs/references/intermediate-schema.md`
- Read only: `skills/parsing-srx-configs/references/intermediate-schema.md`

**Interfaces:**
- Consumes: the skill directory from Task 1.
- Produces: the schema copy that `scripts/check-shared-schema.py` globs via `skills/parsing-*/references/intermediate-schema.md`.

- [ ] **Step 1: Write a deliberately-drifted copy to prove the check bites**

`check-shared-schema.py` globs the parser directories, so a *missing* copy passes vacuously. Only a *drifted* copy is a real RED.

```bash
mkdir -p skills/parsing-firepower-configs/references
cp skills/parsing-srx-configs/references/intermediate-schema.md \
   skills/parsing-firepower-configs/references/intermediate-schema.md
printf '\nDRIFT MARKER\n' >> skills/parsing-firepower-configs/references/intermediate-schema.md
```

- [ ] **Step 2: Run the check to verify it fails**

Run: `python3 scripts/check-shared-schema.py`
Expected: FAIL, reporting the Firepower copy differs, and naming `skills/parsing-srx-configs/references/intermediate-schema.md` as the canonical edit copy.

- [ ] **Step 3: Replace with the exact copy**

```bash
cp skills/parsing-srx-configs/references/intermediate-schema.md \
   skills/parsing-firepower-configs/references/intermediate-schema.md
```

- [ ] **Step 4: Verify byte identity two ways**

Run:
```bash
python3 scripts/check-shared-schema.py
diff -q skills/parsing-srx-configs/references/intermediate-schema.md \
        skills/parsing-firepower-configs/references/intermediate-schema.md
```
Expected: PASS from the checker, and `diff -q` prints nothing.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/references/intermediate-schema.md
git commit -m "feat(firepower): add byte-identical shared intermediate schema copy"
```

---

### Task 3: Add the runtime-intake catalog

**Files:**
- Create: `skills/parsing-firepower-configs/references/runtime-intake.md`
- Modify: `skills/parsing-firepower-configs/SKILL.md` (add the `## Runtime intake` section)

**Interfaces:**
- Consumes: the skill package from Task 1.
- Produces: a `## Runtime intake` heading in `SKILL.md` and a JSON question catalog whose entries carry `id`, `ask_when`, `header`, `question`, and `options[].{label, description}`.

- [ ] **Step 1: Run the intake validators to verify they fail**

Run: `python3 scripts/check-runtime-intake.py`
Expected: FAIL for `parsing-firepower-configs` — no `## Runtime intake` section and no catalog.

- [ ] **Step 2: Create the catalog**

Create `skills/parsing-firepower-configs/references/runtime-intake.md`:

````markdown
# Runtime Intake

## When to ask

Use this catalog only after inspecting the request and evidence. Ask an entry
when its `ask_when` condition is true and the answer would materially affect
the result. Skip answered or irrelevant entries. Prioritize safety, scope,
platform or framework basis, evidence quality, then output preference.

## Tool adaptation

- Claude: select at most three neutral entries, project each to only `question`,
  `header`, and `options`, then add `multiSelect: false`; do not send `id` or
  `ask_when`.
- Codex: select at most three neutral entries and project each to only `id`,
  `header`, `question`, and `options`; do not send `ask_when` or `multiSelect`.
- Fallback: ask the same questions in concise plain text with a free-text
  `Other` path.
- Never request secrets.

## Question catalog

```json
{
  "questions": [
    {
      "id": "firepower_manager",
      "ask_when": "FMC versus FDM origin remains ambiguous after artifact inspection.",
      "header": "Manager",
      "question": "How should an ambiguous Firepower management origin be resolved?",
      "options": [
        {
          "label": "Confirm manager first (Recommended)",
          "description": "Confirm whether the export came from FMC or from FDM before parsing."
        },
        {
          "label": "Treat as FMC export",
          "description": "Parse using FMC object and policy shapes, including rule sections and inheritance."
        },
        {
          "label": "Treat as FDM export",
          "description": "Parse using the flatter FDM object model with no rule sections."
        }
      ]
    },
    {
      "id": "firepower_completeness",
      "ask_when": "The supplied bundle may be a partial or paginated collection.",
      "header": "Completeness",
      "question": "How should a possibly incomplete export be handled?",
      "options": [
        {
          "label": "Confirm completeness first (Recommended)",
          "description": "Confirm whether every endpoint and page was collected before drawing conclusions."
        },
        {
          "label": "Parse as partial",
          "description": "Parse what is present and mark absent sections as unknown rather than empty."
        },
        {
          "label": "Parse as complete",
          "description": "Treat the supplied bundle as the full configuration."
        }
      ]
    },
    {
      "id": "firepower_policy_scope",
      "ask_when": "The export contains more than one access control policy.",
      "header": "Policy Scope",
      "question": "How should multiple access control policies be scoped?",
      "options": [
        {
          "label": "Confirm target policy first (Recommended)",
          "description": "Confirm which access control policy the requested analysis concerns."
        },
        {
          "label": "Emit one document per policy",
          "description": "Produce a separate schema document for each access control policy."
        },
        {
          "label": "Limit to one named policy",
          "description": "Parse only the policy the request names and ignore the others."
        }
      ]
    },
    {
      "id": "firepower_output",
      "ask_when": "The required parsing depth is absent.",
      "header": "Parse Depth",
      "question": "How should unspecified parsing depth be resolved?",
      "options": [
        {
          "label": "Confirm depth first (Recommended)",
          "description": "Confirm whether full normalization or focused extraction is required."
        },
        {
          "label": "Use full normalization",
          "description": "Populate the complete shared schema and run all quality gates."
        },
        {
          "label": "Use focused extraction",
          "description": "Extract only the sections required for the supplied investigation."
        }
      ]
    }
  ]
}
```
````

- [ ] **Step 3: Add the Runtime intake section to SKILL.md**

Insert into `skills/parsing-firepower-configs/SKILL.md`, immediately after the Overview section. The wording matches the other four parsers verbatim so the safety validator's guard terms are present:

```markdown
## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.
```

- [ ] **Step 4: Run the intake validators to verify they pass**

Run:
```bash
python3 scripts/check-runtime-intake.py
python3 scripts/check-runtime-intake-safety.py
python3 scripts/test-runtime-intake-validator.py
python3 scripts/test-runtime-intake-safety.py
```
Expected: all four PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/references/runtime-intake.md skills/parsing-firepower-configs/SKILL.md
git commit -m "feat(firepower): add runtime-intake catalog and SKILL.md intake section"
```

---

### Task 4: Write `references/config-format.md`

The FMC/FDM JSON shape reference. **Pin the version you verify against and classify anything unverified.**

**Files:**
- Create: `skills/parsing-firepower-configs/references/config-format.md`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: the endpoint-family table and the input-packaging contract that Task 6's `SKILL.md` pipeline cites, and the paging rule Task 7's truncation fixture asserts.

- [ ] **Step 1: Verify endpoint and field names against a named version**

There is no live FMC in this environment, so the evidence path is Cisco's **published** FMC and FDM REST API documentation, reached with WebSearch/WebFetch. Record at the top of the file which document and which product version you consulted. Any endpoint or field you cannot confirm against that document gets marked `unverified` inline.

Do not carry endpoint or field names over from memory. The repository's evidence rule accepts authoritative evidence **or** an explicit uncertain classification — the second branch is available and is the honest answer for anything the published docs do not settle.

- [ ] **Step 2: Write the reference**

Cover, in this order:

1. **Version pin** — a header line naming the FMC and FDM versions the file was verified against.
2. **Input packaging** — the three accepted forms from the spec: bundle, keyed envelope, single response. State that a single response yields a partial parse with a warning.
3. **Paging** — `paging.count` versus the number of `items` present. State the rule explicitly: a `count` greater than the item count is a truncated collection, is recorded in `metadata.warnings`, and is never treated as a complete object set.
4. **Reference shape** — the `{"objects": [...], "literals": [...]}` container, with `objects` entries carrying `type`, `id`, and usually `name`, and `literals` carrying `type` and `value`.
5. **Endpoint families** — the table from the spec's Extraction pipeline section, each row marked verified or unverified.
6. **FDM differences** — flatter object model, `ruleAction` instead of `action`, `eventLogAction` instead of `logBegin`/`logEnd`, no Mandatory/Default sections, no policy inheritance.
7. **Out of scope** — `.sfo` bundles and PDF policy reports, with the reason: undocumented for third-party parsing, so support cannot be claimed under the repository's evidence rule.

- [ ] **Step 3: Verify no unverified claim is stated as fact**

Run: `grep -n 'unverified' skills/parsing-firepower-configs/references/config-format.md`
Expected: at least one hit if any endpoint could not be confirmed, and every such endpoint appears in the output. If the grep is empty, confirm every endpoint really was checked in the API Explorer.

- [ ] **Step 4: Run the package validator**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/references/config-format.md
git commit -m "docs(firepower): add FMC and FDM JSON config-format reference"
```

---

### Task 5: Write `references/parsing-patterns.md`

The behavioral core: action mapping, the MONITOR hazard, merged ordering, and UUID resolution.

**Files:**
- Create: `skills/parsing-firepower-configs/references/parsing-patterns.md`

**Interfaces:**
- Consumes: the reference shape and endpoint families from Task 4.
- Produces: the action-mapping table, the merged-ordering algorithm, and the `anon-N-host` / `anon-N-net` literal-minting convention that Tasks 6, 7, and 8 all depend on.

- [ ] **Step 1: Write the action-mapping table**

```markdown
## Action mapping

| Firepower action | Schema `action` | Note |
|---|---|---|
| `ALLOW` | `allow` | |
| `TRUST` | `allow` | bypasses deep inspection — record in `metadata` |
| `BLOCK` | `deny` | |
| `BLOCK_RESET` | `reset-both` | |
| `BLOCK_INTERACTIVE` | `deny` | interactive-block prompt not representable |
| `BLOCK_RESET_INTERACTIVE` | `reset-both` | interactive-block prompt not representable |
| `MONITOR` | `allow` + mandatory warning | **non-terminal — see below** |
| Prefilter `FASTPATH` | `allow` + mandatory warning | bypasses Snort entirely |
| Prefilter `ANALYZE` | not emitted as a policy | hands off to the ACP; record in `metadata` |

FDM uses `ruleAction` with values `PERMIT`, `TRUST`, and `DENY`, mapping to
`allow`, `allow`, and `deny` respectively. FDM has no `MONITOR`.
```

- [ ] **Step 2: Write the MONITOR hazard section**

```markdown
## MONITOR is non-terminal

A `MONITOR` rule logs and **continues** to the next rule. It does not terminate
evaluation. The shared schema has no non-terminal action, so mapping MONITOR to
`allow` tells a downstream consumer that the rule matches and stops — which it
does not.

This is the same defect class the 2026-07-31 live-SRX round found with
`match dynamic-application`: dropped narrowing collapsed distinct rules into
false duplicates and made a scoped deny read as a terminal deny-all.

Required behavior:

- Emit one `metadata.warnings` entry per MONITOR rule, naming the rule.
- State in the parse output that shadowing and terminal-deny conclusions are
  unreliable across a MONITOR rule.
- Never silently map MONITOR to a plain `allow` with no warning.
```

- [ ] **Step 3: Write the merged-ordering algorithm**

```markdown
## Merged evaluation order

Firepower evaluates: Prefilter policy, then the ACP Mandatory section, then the
ACP Default section, then the ACP default action. Ancestor policies contribute
rules to both sections when the ACP inherits.

Flatten all of it into one continuous `_rule_index` starting at 1. Record
provenance — policy name, section, category, and inheriting ancestor — in
`metadata`, not in a new schema field. This follows the Panorama precedent:
`parsing-palo-configs/SKILL.md` records device-group and pre-versus-post origin
in `metadata` rather than inventing a context field, because the schema defines
no such field and downstream consumers ignore unknown `_`-prefixed keys.

The ACP default action becomes the single trailing policy with `_implicit: true`.

**Unresolved at authoring time:** the exact nesting direction of inherited
Default-section rules across a multi-level hierarchy. The general shape —
ancestor Mandatory before the child's rules, ancestor Default after them — is
established. Confirm the multi-level interleaving against current Cisco
documentation and record the version consulted before relying on it.
```

- [ ] **Step 4: Write the reference-resolution section**

```markdown
## Reference resolution

Rules reference objects as
`{"objects": [{type, id, name}], "literals": [{type, value}]}`.

- **objects** — resolve by `id` against the parsed object sets and prefer the
  parsed object's name. An `id` that resolves to nothing produces a
  `metadata.warnings` entry naming the unresolved reference and its rule. Never
  drop it.
- **literals** — mint anonymous objects using `anon-N-host` and `anon-N-net`,
  the same convention `parsing-cisco-configs` uses, so both Cisco parsers behave
  identically downstream.

## Interface modes

Record `mode` on every interface: `ROUTED`, `SWITCHPORT`, `PASSIVE`, or
`INLINE`. Passive and inline-set interfaces do not carry policy the way routed
interfaces do; an audit that assumes otherwise is wrong. `ifname` is the
`nameif` equivalent, and `securityZone` gives the zone binding directly — no
inference is needed, unlike the ASA path.
```

- [ ] **Step 5: Run the package validator and commit**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

```bash
git add skills/parsing-firepower-configs/references/parsing-patterns.md
git commit -m "docs(firepower): add parsing patterns, action mapping, and MONITOR hazard"
```

---

### Task 6: Write the full `SKILL.md` body

**Files:**
- Modify: `skills/parsing-firepower-configs/SKILL.md`

**Interfaces:**
- Consumes: `references/config-format.md` (Task 4), `references/parsing-patterns.md` (Task 5), `references/intermediate-schema.md` (Task 2), `references/runtime-intake.md` (Task 3).
- Produces: the finished skill body. Tasks 7 and 8 add the two reference paths it cites but does not yet have.

- [ ] **Step 1: Replace the placeholder body**

Keep the frontmatter and the `## Runtime intake` section from Tasks 1 and 3 unchanged. Write these sections, in order, mirroring `skills/parsing-cisco-configs/SKILL.md`:

1. **Overview** — what the skill parses and that it emits the shared schema.
2. **Scope and routing** — owns FMC/FDM JSON. Hand off ASA-style LINA text (`access-list`, `nameif`, `object network`) to `parsing-cisco-configs`; FortiOS to `parsing-fortinet-configs`; PAN-OS to `parsing-palo-configs`; Junos to `parsing-srx-configs`. Downstream consumers are the audit, conversion, and diff skills.
3. **Runtime intake** — already present, leave as is.
4. **Input Format** — the three packagings and the detection discriminators: `"type": "AccessRule"`, `"type": "AccessPolicy"`, `"type": "SecurityZone"`, `"type": "FTDNatPolicy"`, `metadata.accessPolicy`, `metadata.section`, an FMC `/api/fmc_config/v1/domain/` path, an FDM `/api/fdm/` path.
5. **Extraction Pipeline** — one numbered subsection per schema section, following the spec's endpoint table.
6. **Rule ordering** — summarize and point to `references/parsing-patterns.md`.
7. **Multi-domain and policy scope** — one schema document per Access Control Policy; the policy and domain named in `metadata`.
8. **Output Format** — point to `references/intermediate-schema.md`.
9. **Parser Quality Gates** — the same nine gates the other parsers carry.
10. **Analysis Checks** — unused objects, shadowed rules (with the MONITOR caveat), overly permissive rules, missing logging, disabled rules, duplicate objects, empty groups, unresolved references.
11. **Reference Files** — list all seven.
12. **Secret Handling** — mask as `"****"` with a `metadata.warnings` entry; record the distinction between *absent* and *redacted*, because FMC commonly omits secrets on GET.
13. **Common Pitfalls** — MONITOR non-termination; truncated paging read as a complete rulebase; `.sfo` and PDF refusal; passive/inline interfaces; `id`-only references.
14. **Verification Checklist** — mirroring the Cisco skill's.

- [ ] **Step 2: Verify the 600-line limit**

Run: `wc -l skills/parsing-firepower-configs/SKILL.md`
Expected: 600 or fewer. If over, move detail into `references/parsing-patterns.md`.

- [ ] **Step 3: Verify every referenced path exists**

Run: `python3 scripts/check-skill-packages.py`
Expected: FAIL listing the reference paths SKILL.md cites that do not exist yet — `references/fixture-minimal-input.md`, `references/fixture-expected-output.json`, and `references/example-sample-parse.md`. Those three arrive in Tasks 7 and 8. Any *other* missing-path error is a real defect; fix it now.

- [ ] **Step 4: Create the three placeholder targets so the gate is green at commit time**

The validator requires every `references/...` path cited anywhere in `SKILL.md` to exist, and the Reference Files section cites all three. Two placeholders is not enough — the fixture JSON is cited too.

```bash
printf '# Fixture: Minimal Firepower Input\n\nPopulated in Task 7.\n' \
  > skills/parsing-firepower-configs/references/fixture-minimal-input.md
printf '{}\n' \
  > skills/parsing-firepower-configs/references/fixture-expected-output.json
printf '# Worked Example\n\nPopulated in Task 8.\n' \
  > skills/parsing-firepower-configs/references/example-sample-parse.md
python3 scripts/check-skill-packages.py
```
Expected: PASS. Tasks 7 and 8 overwrite all three placeholders with real content.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/SKILL.md skills/parsing-firepower-configs/references/
git commit -m "feat(firepower): write SKILL.md extraction pipeline and quality gates"
```

---

### Task 7: Build the fixture pair

**Files:**
- Modify: `skills/parsing-firepower-configs/references/fixture-minimal-input.md`
- Create: `skills/parsing-firepower-configs/references/fixture-expected-output.json`

**Interfaces:**
- Consumes: the action mapping and ordering algorithm from Task 5.
- Produces: the fixture pair the other four parsers each carry, exercising ordering, MONITOR, and truncated paging.

- [ ] **Step 1: Write the minimal synthetic input**

Replace `fixture-minimal-input.md` with a synthetic FMC bundle. **No real addresses, no real names, no secrets.** It must contain at minimum:

- two `securityZones` (`inside-zone`, `outside-zone`)
- one `networks` object and one `networkgroups` object
- one `protocolportobjects` entry
- one access control policy with **one Mandatory rule, one Default rule, and one MONITOR rule**
- one prefilter rule
- one rule using a `literals` entry so anonymous-object minting is exercised
- one rule referencing an `id` that resolves to nothing, to exercise unresolved-reference warning
- a `paging` block whose `count` exceeds the number of `items`, to exercise the truncation warning
- a `defaultaction` of `BLOCK`

- [ ] **Step 2: Write the expected output**

Create `fixture-expected-output.json` as the high-level expected schema. It must assert:

- `_rule_index` is continuous from 1, with the prefilter rule first, then Mandatory, then Default
- the MONITOR rule has `action: "allow"` **and** a matching `metadata.warnings` entry naming it
- the literal produced an `anon-1-host` (or `anon-1-net`) address object
- the unresolved `id` produced a `metadata.warnings` entry, and the reference was not dropped
- the truncated paging produced a partial-input `metadata.warnings` entry
- the `BLOCK` default action produced exactly one trailing policy with `_implicit: true` and `action: "deny"`

- [ ] **Step 3: Verify the fixture JSON parses**

Run: `python3 -c "import json,pathlib; json.loads(pathlib.Path('skills/parsing-firepower-configs/references/fixture-expected-output.json').read_text()); print('valid json')"`
Expected: `valid json`

- [ ] **Step 4: Verify the fixture is secret-free and synthetic**

Run: `grep -nEi 'password|secret|psk|preshared|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key' skills/parsing-firepower-configs/references/fixture-minimal-input.md skills/parsing-firepower-configs/references/fixture-expected-output.json`
Expected: no output, or only the masked literal `"****"`.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/references/fixture-minimal-input.md skills/parsing-firepower-configs/references/fixture-expected-output.json
git commit -m "test(firepower): add fixture pair covering ordering, MONITOR, and paging"
```

---

### Task 8: Write the worked example

**Files:**
- Modify: `skills/parsing-firepower-configs/references/example-sample-parse.md`

**Interfaces:**
- Consumes: the fixture pair from Task 7.
- Produces: the end-to-end narrative the other four parsers each carry.

- [ ] **Step 1: Write the example**

Take the Task 7 fixture input through to the Task 7 expected output, narrating each stage: detection, input assembly, object extraction, UUID resolution, rule flattening with the running `_rule_index`, action mapping, implicit-rule append, and the warnings block. Match the structure of `skills/parsing-cisco-configs/references/example-sample-parse.md`.

Show the warnings block in full, including the MONITOR, unresolved-reference, and truncated-paging entries. The example is where a reader learns that these warnings are mandatory rather than optional.

- [ ] **Step 2: Verify consistency with the fixture**

Run:
```bash
python3 -c "import json,pathlib; d=json.loads(pathlib.Path('skills/parsing-firepower-configs/references/fixture-expected-output.json').read_text()); print('\n'.join(sorted(d.keys())))"
```
Expected: the fixture's top-level schema keys print, one per line.

Then confirm by eye, against that printed list: every key the worked example claims to emit appears in it, and the example's `_rule_index` sequence matches the fixture's. This is a read-and-compare step, not an automated assertion — the two documents are prose and JSON, so no diff command can check them against each other.

- [ ] **Step 3: Run the package validator**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Verify SKILL.md is still within its line limit**

Run: `wc -l skills/parsing-firepower-configs/SKILL.md`
Expected: 600 or fewer.

- [ ] **Step 5: Commit**

```bash
git add skills/parsing-firepower-configs/references/example-sample-parse.md
git commit -m "docs(firepower): add worked end-to-end parse example"
```

---

### Task 9: Write the skill README

**Files:**
- Create: `skills/parsing-firepower-configs/README.md`

**Interfaces:**
- Consumes: the finished skill body from Task 6.
- Produces: the per-skill README the other four parsers each carry.

- [ ] **Step 1: Write it**

Follow `skills/parsing-cisco-configs/README.md` structure: title, one-line summary, "What it does" bullet list of extracted sections, the boundary against `parsing-cisco-configs`, and usage.

State the boundary in the first three lines. A reader who lands here from a search for "Cisco FTD" needs to know immediately whether their artifact is JSON or LINA CLI.

- [ ] **Step 2: Run the validators and commit**

Run: `python3 scripts/check-skill-packages.py && python3 scripts/check-readme-branding.py`
Expected: PASS.

```bash
git add skills/parsing-firepower-configs/README.md
git commit -m "docs(firepower): add skill README with boundary statement"
```

---

### Task 10: Sharpen the `parsing-cisco-configs` boundary

**Files:**
- Modify: `skills/parsing-cisco-configs/SKILL.md:3` (description)
- Modify: `skills/parsing-cisco-configs/SKILL.md` ("Scope and routing" section, and the Overview's FMC paragraph)
- Modify: `skills/parsing-cisco-configs/README.md`

**Interfaces:**
- Consumes: the registered name `parsing-firepower-configs` from Task 1.
- Produces: disjoint, grammar-keyed descriptions across the two Cisco skills.

- [ ] **Step 1: Replace the description**

Replace the `description:` value at `skills/parsing-cisco-configs/SKILL.md:3` with:

```yaml
description: Parse Cisco ASA and FTD LINA running configurations into the shared firewall schema. Use when input contains show running-config, access-list, access-group, object network, object-group, nameif, security-level, NAT, interfaces, or failover, including audit, conversion, diff, summary, and explanation tasks. For FMC- or FDM-managed Firepower policy exported as JSON, use parsing-firepower-configs instead.
```

- [ ] **Step 2: Replace the Overview's FMC paragraph**

The current paragraph reads "Treat FMC-managed FTD exports and API data as adjacent but not identical inputs…". Replace it with an explicit hand-off:

```markdown
FMC- and FDM-managed policy is **not** parsed here. An FMC or FDM JSON export has
no syntactic overlap with LINA CLI — its policy lives in Access Control Policy
rules, security-zone objects, and intrusion/file policies rather than in
`access-list` and `access-group` lines. Route those exports to
`parsing-firepower-configs`. If an FMC-managed device's LINA running-config is
supplied, parse it here and warn that it is the compiled result of an FMC policy,
not the policy source.
```

- [ ] **Step 3: Add the hand-off to Scope and routing**

In the "Scope and routing" section, after the existing hand-off sentence, add:

```markdown
Hand off FMC or FDM JSON exports to `parsing-firepower-configs`.
```

- [ ] **Step 4: Update the skill README and add the related-skill link**

In `skills/parsing-cisco-configs/README.md`, add a line under the title noting that FMC/FDM JSON exports are handled by `parsing-firepower-configs`. In `skills/parsing-cisco-configs/SKILL.md` frontmatter, add `parsing-firepower-configs` to `metadata.hermes.related_skills`.

- [ ] **Step 5: Verify and commit**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS — confirms the re-cut description is still under 1,024 characters and still contains `. Use when `.

```bash
git add skills/parsing-cisco-configs/SKILL.md skills/parsing-cisco-configs/README.md
git commit -m "docs(cisco): scope parsing-cisco-configs to LINA and hand off FMC/FDM"
```

---

### Task 11: Add the audit partition rule

**Files:**
- Modify: `skills/firewall-best-practices-audit/SKILL.md:77-80`
- Modify: `skills/firewall-best-practices-audit/references/check-catalog.md:41-46`

**Interfaces:**
- Consumes: the merged-ordering and MONITOR behavior from Task 5.
- Produces: a Firepower entry in the audit skill's evaluation-population partition list.

- [ ] **Step 1: Read the existing partition list**

Run: `sed -n '70,95p' skills/firewall-best-practices-audit/SKILL.md`
Expected: the per-vendor list showing `_vsys` for PAN-OS and `_vdom` for FortiGate.

- [ ] **Step 2: Add the Firepower line**

Insert alongside the existing per-vendor entries, matching their wording:

```markdown
- **Cisco Firepower (FMC/FDM):** partition by access control policy — a device is
  assigned exactly one, so the policy is the evaluation population. Use the
  parser's merged Prefilter-plus-ACP order via `_rule_index`. A `MONITOR` rule is
  **non-terminal**: it logs and continues. Shadowing and `SEC-NO-DENY-ALL`
  conclusions are unreliable across one, so report them as qualified rather than
  confirmed when the parser warned about a MONITOR rule.
```

Add the equivalent line to the parallel list in `references/check-catalog.md`.

- [ ] **Step 3: Verify the audit contract still holds**

Run: `python3 scripts/check-audit-rule-contract.py`
Expected: PASS.

- [ ] **Step 4: Verify no other consumer needs changing**

Run: `grep -rn '_vsys\|_vdom' skills/firewall-config-diff/ skills/firewall-config-conversion/`
Expected: only `equivalence-rules.md:36` (which already ignores unknown `_` fields) and the `emit-palo.md` hits. Confirms the diff skill needs no change, as the spec states.

- [ ] **Step 5: Commit**

```bash
git add skills/firewall-best-practices-audit/SKILL.md skills/firewall-best-practices-audit/references/check-catalog.md
git commit -m "docs(audit): add Firepower ACP partition rule and MONITOR caveat"
```

---

### Task 12: Update repository catalog and counts

**Files:**
- Modify: `README.md` — lines 20, 21, 31, 106, 192, 253, plus the Reference list at the `parsing-cisco-configs` bullet (line 200 region)
- Modify: `SKILLS.md:5`
- Modify: `QUALITY.md` — opening count sentence and the family table

**Interfaces:**
- Consumes: the completed skill from Tasks 1–9.
- Produces: one consistent skill count across all three documents.

- [ ] **Step 1: Measure the real count before changing any number**

Run: `ls -d skills/*/ | wc -l`
Expected: `29` after this work (measured at 28 before Task 1).

The counts currently disagree with each other — see the table in Global Constraints. Set every location to the measured number; do not increment whatever each file happens to say.

- [ ] **Step 2: Find every stale count**

Run: `grep -n '27 skills\|all 27\|25 of the 27\|28 skills\|25 of the 28\|badge/skills-\|badge/reviewed-' README.md SKILLS.md QUALITY.md`
Expected: eight or more hits across the three files. Every hit must be updated in Steps 3–5; re-run this grep at Step 6 and confirm no stale count remains.

- [ ] **Step 3: Update the README badges and prose counts**

```bash
sed -i 's|badge/skills-27-|badge/skills-29-|' README.md
sed -i 's|badge/reviewed-25%2F27-|badge/reviewed-25%2F29-|' README.md
sed -i 's|or all 27\.|or all 29.|' README.md
sed -i 's|all 27$|all 29|' README.md
sed -i 's|\*\*28 skills\*\*|**29 skills**|' README.md
sed -i 's|25 of the 28 packages|25 of the 29 packages|' README.md
sed -i 's|\*\*25 of the 27 skills\*\*|**25 of the 29 skills**|' README.md
grep -n 'badge/skills-\|badge/reviewed-\|29 skills\|all 29\|25 of the 29' README.md
```
Expected: every count now reads 29. Inspect each `sed` result by eye — line 106's "all 27" wraps across a line break, so confirm it actually changed rather than assuming.

- [ ] **Step 4: Add the Reference row**

After the `parsing-cisco-configs` bullet in the README Reference list, add:

```markdown
- **[parsing-firepower-configs](./skills/parsing-firepower-configs/SKILL.md)** — Cisco Secure Firewall / Firepower (FMC & FDM JSON exports): access control policies, security zones, prefilter, intrusion & file policies, FTD NAT.
```

In the same section's prose, add `parsing-firepower-configs` to the sentence naming skills that have not completed review, alongside `srx-syslog-logging` and `srx-initial-setup`.

- [ ] **Step 5: Update SKILLS.md and QUALITY.md**

In `SKILLS.md:5`, change "all 27 skills" to "all 29 skills". No new detail section is required — that file covers only the compliance and SRX playbooks.

In `QUALITY.md`: update the opening count sentence to 25-of-29, add `parsing-firepower-configs` to the list of skills that have not been through the two-stage review, change the family table's "Config parsers" row from `4 | 4 / 4` to `5 | 4 / 5`, and recompute the Total row to `29 | 25 / 29`.

- [ ] **Step 6: Confirm no stale count survives**

Run: `grep -n '27 skills\|all 27\|25 of the 27\|28 skills\|25 of the 28\|skills-27\|2F27' README.md SKILLS.md QUALITY.md`
Expected: no output.

- [ ] **Step 7: Verify and commit**

Run: `python3 scripts/check-readme-branding.py && just lint`
Expected: PASS.

```bash
git add README.md SKILLS.md QUALITY.md
git commit -m "docs: add parsing-firepower-configs to catalog and correct skill counts"
```

---

### Task 13: Trigger-token overlap analysis

The spec's risk 4 — evidence that the two Cisco descriptions do not compete for the same artifacts.

**Files:**
- Create: `docs/skill-tests/2026-08-27-parsing-firepower-configs-retrieval.md`

**Interfaces:**
- Consumes: the descriptions from Tasks 1 and 10.
- Produces: a recorded retrieval result, matching how the 2026-07-04/05 round documented its clean-context retrieval tests.

- [ ] **Step 1: Measure the combined description budget**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS. Record the combined-description character count from any warning line, and whether it crossed the 12,000 soft budget. If it did, note it in the test document — `AGENTS.md` says to prefer consolidating overlapping skills over trimming `Use when` clauses, so a crossing is a finding to report, not something to fix by shortening.

- [ ] **Step 2: Run a trigger-token overlap analysis over four artifacts**

This is **not** a live clean-context retrieval test — nothing in this environment can produce that condition, and the document must say so in its title and opening line. It is a mechanical analysis of which description's trigger tokens each artifact matches.

For each artifact below, list the tokens it contains that appear in the `parsing-firepower-configs` description, and the tokens it contains that appear in the `parsing-cisco-configs` description. The skill with strictly more matched tokens is the predicted selection.

1. An FMC access rule JSON snippet → must predict `parsing-firepower-configs`
2. An ASA `access-list` / `nameif` block → must predict `parsing-cisco-configs`
3. An FTD LINA `show running-config` excerpt → must predict `parsing-cisco-configs`
4. An FDM `accessrules` JSON snippet → must predict `parsing-firepower-configs`

Artifact 3 is the sharp case: it contains the word "FTD", which appears in *both* descriptions. It must still predict `parsing-cisco-configs` on the strength of `show running-config`, `access-list`, and `nameif`. If it does not, the Firepower description is over-claiming FTD and its trigger tokens need re-cutting.

- [ ] **Step 3: Record the results**

Write the four artifacts, the matched-token lists for each, the predicted selection, and pass/fail into the test document. State plainly in the opening paragraph that this is token-overlap analysis and that a live clean-context retrieval test was not performed, so `QUALITY.md` does not overclaim what was verified.

A wrong prediction is a description defect: re-cut the losing description's trigger tokens and re-run, rather than accepting the miss.

- [ ] **Step 4: Verify all four passed**

Expected: 4 of 4 correct. If any failed, fix the description and return to Step 2 before proceeding.

- [ ] **Step 5: Commit**

```bash
git add docs/skill-tests/2026-08-27-parsing-firepower-configs-retrieval.md
git commit -m "test(firepower): record retrieval and trigger-competition results"
```

---

### Task 14: Full gate

**Files:**
- No new files. Runs the repository's complete validation surface.

**Interfaces:**
- Consumes: everything from Tasks 1–13.
- Produces: a green gate and a Codex verdict per commit.

- [ ] **Step 1: Run the offline gate**

Run: `just fmt && just lint && just test && just guard`
Expected: all PASS. A combined-description warning is acceptable; any error is not.

- [ ] **Step 2: Run the installer end-to-end**

Run: `just e2e`
Expected: PASS — confirms `install.sh --help` works and the parsers family now offers five skills into a disposable path.

- [ ] **Step 3: Run the security scan**

Run: `just security`
Expected: PASS with no secret findings. The fixture is synthetic; a hit here means Task 7's fixture needs scrubbing.

- [ ] **Step 4: Run the Codex review gate per commit**

For each commit made in Tasks 1–13:

```bash
just review <sha>
```

Expected: a final `agent_message` verdict for every commit. **A run producing no verdict is not a pass** — report that the gate did not run rather than treating silence as approval. If a commit is too large to return a verdict, split it and re-review.

Check each finding against the cited lines before acting on it. A rejected finding needs stated evidence, not an opinion.

- [ ] **Step 5: Run the release check and report**

Run: `just release-check`
Expected: PASS.

Report: skills and files changed, validation commands and their results, the FMC/FDM versions the references were verified against, everything classified unverified, and remaining risk — specifically that the skill ships outside the two-stage `QUALITY.md` review.

---

## Self-Review

**Spec coverage** — every spec section maps to a task: boundary → 1, 10; input assembly and paging → 4, 7; detection/routing → 6; extraction pipeline → 4, 6; ordering → 5, 7; action mapping and MONITOR → 5, 7, 11; reference resolution → 5; multi-domain → 6; non-isomorphic and out-of-scope → 4, 6; secret handling → 6, 7; downstream ripple → 11; file structure → 1–9; testing → 7, 8, 13, 14; risks → 4 (drift), 13 (budget, trigger competition), 12 (unreviewed status).

**Placeholder scan** — the two intentional placeholder files created in Task 6 Step 4 are both replaced by name in Tasks 7 and 8. No task defers work to an unnamed later step.

**Type consistency** — `parsing-firepower-configs` is spelled identically in the frontmatter `name`, the directory, `EXPECTED_SKILL_NAMES`, `EXPECTED_FAMILIES["parsers"]`, the `PARSERS` array, and the `default_prompt`'s `$parsing-firepower-configs`. The anonymous-object convention is `anon-N-host` / `anon-N-net` in Tasks 5, 7, and 8. `_rule_index` and `_implicit` match the schema's spelling throughout.
