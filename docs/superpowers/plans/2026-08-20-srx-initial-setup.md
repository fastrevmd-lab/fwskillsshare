# srx-initial-setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `skills/srx-initial-setup`, an assess-first, gate-driven skill that brings a new or factory-reset Juniper SRX from its shipped state to a reachable, zoned, screened, minimally-policied device and then routes onward to the existing SRX skill family.

**Architecture:** A Markdown skill package following the repository's established shape — `SKILL.md` under 600 lines with progressive-disclosure `references/`, an `agents/openai.yaml`, and a runtime-intake catalog. The skill always opens with a read-only entry-state assessment, computes a dependency-ordered gap list, and closes only open gaps through per-stage approval gates, every remote commit protected by `commit confirmed`.

**Tech Stack:** Markdown, YAML frontmatter, JSON question catalogs, Python validation scripts under `scripts/`, `just` recipes.

**Spec:** `docs/superpowers/specs/2026-08-20-srx-initial-setup-design.md`

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from the spec and from the repository's validators.

- **Skill name:** `srx-initial-setup`. Must match its directory name, be hyphen-case, at most 64 characters.
- **`SKILL.md` frontmatter:** `name`, `description`, `version`, `author`, `license`, `metadata` are all required.
- **`license` must be exactly `MIT`.**
- **`author` must be exactly** `["fastrevmd-lab", "Claude", "GPT"]`, in that order.
- **Description: at most 1,024 characters**, must contain the literal substring `". Use when "`, must contain no `<` or `>`.
- **`SKILL.md` at most 600 lines.** This is the progressive-disclosure limit and is enforced.
- **`references/source-*.md` at most 200 lines** and must contain no page-dump markers (`Skip main navigation`, `Powered by Higher Logic`, `View Only`, `Jump to Best Answer`, `New Best Answer`).
- **Every `references/...` path mentioned anywhere in `SKILL.md` must exist**, or the package checker errors.
- **`agents/openai.yaml`** needs a quoted `display_name`, a quoted `short_description` of **25–64 characters**, and a quoted `default_prompt` containing the literal `$srx-initial-setup`.
- **`## Runtime intake` in `SKILL.md` must byte-match the approved standard template** after whitespace normalization. Do not paraphrase it.
- **`references/runtime-intake.md` must contain exactly these headings**, in this order: `# Runtime Intake`, `## When to ask`, `## Tool adaptation`, `## Question catalog`.
- **Intake question objects use only these keys:** `id`, `ask_when`, `header`, `question`, `options`. Option objects use only `label` and `description`.
- **No HTML comments and no raw HTML blocks** anywhere in skill Markdown.
- **Combined descriptions warn only above 12,000 characters.** The catalogue is at 8,376 across 27 skills; this skill adds roughly 370. No warning will fire. **Do not shorten `Use when` clauses for budget reasons** — they are what lexical discovery matches on.
- **Platform scope:** Branch SRX300/400; campus SRX1600/4120; datacenter SRX4300/4700/5000. SRX1500 is EOS and is not a validation target.
- **Chassis cluster is out of scope.** Route to `srx-chassis-cluster-proxmox` or `srx-mnha`.
- **Licensing mutation is out of scope.** Route to `srx-license-signature-maintenance`.
- **Secret handling:** never emit license keys, entitlement blobs, license identifiers, software serial numbers, or customer identifiers.
- **Commit size:** keep commits small. A ~1,300-line commit never returned from the Codex review gate; ~80-line commits returned every time. One task, one commit.

## Vendor evidence rule — read before writing any command

**This plan deliberately does not contain Junos command syntax or factory-default content.**

The repository requires authoritative evidence for every vendor claim. Commands recalled from memory are not evidence. Where a task says "retrieve and record", that is a real research step with a defined output and acceptance criteria — it is not a placeholder to be filled with a plausible guess.

For every Junos command, configuration stanza, or factory-default behavior written into this skill, the implementer must either:

1. cite current Juniper documentation, recording title, URL, and retrieval date in `SKILL.md` frontmatter `sources`; or
2. record it as observed live, naming the platform and Junos release; or
3. mark it explicitly as unverified.

A task is not complete if it contains an unsourced command. If documentation cannot be found for a claim, the correct output is the explicit unverified marking, not omission and not invention.

---

### Task 1: Package skeleton and registration

Creates the directory and registers it everywhere the validators expect, so the package validates as an empty-but-well-formed skill before any content exists.

**Files:**
- Create: `skills/srx-initial-setup/SKILL.md`
- Create: `skills/srx-initial-setup/agents/openai.yaml`
- Modify: `scripts/check-skill-packages.py` (`EXPECTED_SKILL_NAMES`)
- Modify: `install.sh` (skills array, near line 43)
- Modify: `scripts/check-installer.py` (expected skills list, near line 31)

**Interfaces:**
- Consumes: nothing.
- Produces: a validating skill package named `srx-initial-setup` with frontmatter fields `name`, `description`, `version: 0.1.0`, `author`, `license: MIT`, `metadata.hermes.tags`, `metadata.hermes.related_skills`. Later tasks append body sections and `metadata.sources` entries.

- [ ] **Step 1: Create the directory and a minimal SKILL.md to trigger the failing check**

```bash
mkdir -p skills/srx-initial-setup/agents skills/srx-initial-setup/references/stages
```

Write `skills/srx-initial-setup/SKILL.md`:

```markdown
---
name: srx-initial-setup
description: Bring a new or factory-reset Juniper SRX from its shipped state to a reachable, zoned, screened, and minimally policied device. Use when performing first-time setup or Day-0 and Day-1 bring-up on SRX300 or SRX400 Branch, SRX1600 or SRX4120 campus, or SRX4300, SRX4700, or SRX5000 datacenter platforms, when removing or adopting factory-default configuration, when establishing management access, NTP, DNS, and system services, when creating interfaces, zones, and host-inbound-traffic, when applying starter screens, or when reading which licensed feature sets are entitled, configured, and active. Not for chassis-cluster formation, ZTP, Junos upgrades, or full policy design.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, initial-setup, day-zero, day-one, bring-up, factory-default, zeroize, management-plane, zones, host-inbound-traffic, screens, ids-option, commit-confirmed, rollback, entitlement, branch-srx]
    related_skills: [srx-policy, srx-nat, srx-syslog-logging, srx-license-signature-maintenance, srx-chassis-cluster-proxmox, srx-mnha, parsing-srx-configs]
---

# SRX first-time setup

## Overview

Placeholder body replaced in Task 15.
```

- [ ] **Step 2: Run the package checker to verify it fails**

Run: `python3 scripts/check-skill-packages.py`
Expected: FAIL with `ERROR: unexpected skills: srx-initial-setup`

- [ ] **Step 3: Register the name in the package checker**

In `scripts/check-skill-packages.py`, add `"srx-initial-setup",` to the `EXPECTED_SKILL_NAMES` frozenset, keeping the existing alphabetical grouping (immediately before `"srx-ipsec-hub-spoke",`).

- [ ] **Step 4: Run the package checker to verify the next failure**

Run: `python3 scripts/check-skill-packages.py`
Expected: FAIL with `ERROR: skills/srx-initial-setup/agents/openai.yaml: missing Codex UI metadata`

- [ ] **Step 5: Create the Codex UI metadata**

Write `skills/srx-initial-setup/agents/openai.yaml`:

```yaml
interface:
  display_name: "SRX First-Time Setup"
  short_description: "Bring a new or reset SRX up to a usable baseline"
  default_prompt: "Use $srx-initial-setup to assess this SRX and bring it to a usable baseline."
```

`short_description` above is 46 characters, inside the required 25–64 range.

- [ ] **Step 6: Run the package checker to verify it passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS, printing `OK: 28 portable skill packages`. Confirm the printed description-character total is under 12,000.

- [ ] **Step 7: Register the skill in the installer and its checker**

In `install.sh`, add `"srx-initial-setup"` to the skills array, preserving the file's existing ordering convention. In `scripts/check-installer.py`, add `"srx-initial-setup",` to the expected skills list, matching the same ordering.

- [ ] **Step 8: Run the installer checks**

Run: `python3 scripts/check-installer.py && python3 scripts/test-installer.py`
Expected: PASS for both.

- [ ] **Step 9: Commit**

```bash
git add skills/srx-initial-setup scripts/check-skill-packages.py scripts/check-installer.py install.sh
git commit -m "feat(srx-initial-setup): register skill package skeleton"
```

---

### Task 2: Runtime intake section and question catalog

**Files:**
- Modify: `skills/srx-initial-setup/SKILL.md` (add `## Runtime intake`)
- Create: `skills/srx-initial-setup/references/runtime-intake.md`

**Interfaces:**
- Consumes: the package skeleton from Task 1.
- Produces: intake question ids `sis_entry_state`, `sis_task`, `sis_platform`, `sis_change_authority`, `sis_console`. Task 3 pins their canonical digest; Tasks 4–14 reference these ids when a stage needs an unresolved fact.

- [ ] **Step 1: Add the Runtime intake section to SKILL.md**

The validator compares this against an approved template after whitespace normalization. **Copy it verbatim from a passing skill rather than retyping it.**

```bash
sed -n '/^## Runtime intake$/,/^## /p' skills/srx-syslog-logging/SKILL.md | head -n -1
```

Insert that output into `skills/srx-initial-setup/SKILL.md` after the `## Overview` section.

- [ ] **Step 2: Run the structural validator to verify it fails on the missing catalog**

Run: `python3 scripts/check-runtime-intake.py`
Expected: FAIL, reporting the missing `skills/srx-initial-setup/references/runtime-intake.md`.

- [ ] **Step 3: Write the intake catalog**

Write `skills/srx-initial-setup/references/runtime-intake.md`. Copy the `# Runtime Intake`, `## When to ask`, and `## Tool adaptation` sections verbatim from `skills/srx-syslog-logging/references/runtime-intake.md` — they are fixed boilerplate the validator checks. Then write `## Question catalog` as a single ```json fenced block:

```json
{
  "questions": [
    {
      "id": "sis_entry_state",
      "ask_when": "The device entry state is unknown and no read-only assessment output was supplied.",
      "header": "Entry state",
      "question": "What state is this SRX in right now?",
      "options": [
        {
          "label": "Assess the device first (Recommended)",
          "description": "Run the read-only entry-state assessment and report what is present before proposing any change."
        },
        {
          "label": "Factory default or freshly zeroized",
          "description": "The device still carries its shipped or reset configuration."
        },
        {
          "label": "Partially configured",
          "description": "Some setup was already done and the remaining gaps should be closed."
        }
      ]
    },
    {
      "id": "sis_change_authority",
      "ask_when": "A device write is in scope and no approval boundary was stated.",
      "header": "Authority",
      "question": "What may this run do to the device?",
      "options": [
        {
          "label": "Read-only assessment (Recommended)",
          "description": "Assess and report gaps with candidate configuration, applying nothing."
        },
        {
          "label": "Staged writes with per-stage approval",
          "description": "Apply approved stages under commit confirmed, pausing for approval at each gate."
        }
      ]
    },
    {
      "id": "sis_console",
      "ask_when": "A change with lockout risk is in scope and out-of-band access was not confirmed.",
      "header": "Recovery",
      "question": "Is console or out-of-band access available if in-band reachability is lost?",
      "options": [
        {
          "label": "Confirm console access first (Recommended)",
          "description": "Do not propose lockout-risk changes until an out-of-band recovery path is confirmed."
        },
        {
          "label": "Console access is confirmed available",
          "description": "An out-of-band path exists and a lost in-band session is recoverable."
        }
      ]
    },
    {
      "id": "sis_platform",
      "ask_when": "The platform class is unknown and cannot be read from supplied evidence.",
      "header": "Platform",
      "question": "Which SRX platform is being set up?",
      "options": [
        {
          "label": "Read the platform from the device (Recommended)",
          "description": "Determine platform and Junos release from device output rather than assuming."
        },
        {
          "label": "Branch SRX300 or SRX400",
          "description": "Ships with a factory-default configuration that must be understood before it is removed."
        },
        {
          "label": "Campus or datacenter SRX",
          "description": "SRX1600, SRX4120, SRX4300, SRX4700, or SRX5000."
        }
      ]
    },
    {
      "id": "sis_task",
      "ask_when": "The requested activity is absent.",
      "header": "Task",
      "question": "What should this setup run accomplish?",
      "options": [
        {
          "label": "Assess and report gaps (Recommended)",
          "description": "Produce the entry-state assessment, gap list, and entitlement readout without changing the device."
        },
        {
          "label": "Close open setup gaps",
          "description": "Walk the open stage gates and bring the device to a usable baseline."
        },
        {
          "label": "Verify a finished setup",
          "description": "Confirm an already-configured device against the verification matrix."
        }
      ]
    }
  ]
}
```

Every question's first option is a read-only or confirm-first default. That is required by Task 3's safety registration and is not stylistic.

- [ ] **Step 4: Run the structural validators to verify they pass**

Run: `python3 scripts/check-runtime-intake.py && python3 scripts/test-runtime-intake-validator.py`
Expected: PASS, reporting `OK: 28 runtime-intake catalogs`.

- [ ] **Step 5: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add runtime intake section and catalog"
```

---

### Task 3: Runtime intake safety registration

`check-runtime-intake-safety.py` cross-checks each catalog against Appendix A of the runtime-intake plan and pins a SHA-256 of the canonical catalog. A new skill must be added to all four structures or the checker will not cover it.

**Files:**
- Modify: `docs/superpowers/plans/2026-07-24-runtime-intake-questions.md` (Appendix A)
- Modify: `scripts/check-runtime-intake-safety.py` (`EXPECTED_SKILLS`, digest map, `SAFE_FIRST_LABELS`)

**Interfaces:**
- Consumes: the five question ids from Task 2.
- Produces: safety coverage for this skill. No later task depends on its output, but no later task may change the catalog without re-running Step 4 and re-pinning the digest.

- [ ] **Step 1: Compute the canonical digest**

The checker hashes the canonical serialization of the catalog's `questions` list. Compute it with the checker's own function so the two cannot disagree:

```bash
python3 - <<'EOF'
import importlib.util, json, re, pathlib
spec = importlib.util.spec_from_file_location("safety", "scripts/check-runtime-intake-safety.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
text = pathlib.Path("skills/srx-initial-setup/references/runtime-intake.md").read_text()
payload = re.search(r"```json[ \t]*\n(.*?)\n```", text, re.S).group(1)
print(mod.catalog_sha256(json.loads(payload)["questions"]))
EOF
```

Record the printed digest; Step 3 uses it.

- [ ] **Step 2: Add the Appendix A section**

In `docs/superpowers/plans/2026-07-24-runtime-intake-questions.md`, under `## Appendix A: Exact question catalogs`, add a new `### A.N \`srx-initial-setup\`` section, where `N` is one past the current highest section number. Each row must match the parser's exact grammar:

```text
- `sis_entry_state`; header `Entry state`; ask when the device entry state is unknown and no read-only assessment output was supplied; question `What state is this SRX in right now?`; options: `Assess the device first (Recommended)` — Run the read-only entry-state assessment and report what is present before proposing any change; `Factory default or freshly zeroized` — The device still carries its shipped or reset configuration; `Partially configured` — Some setup was already done and the remaining gaps should be closed.
```

Write one such row per question, in catalog order, with option labels and descriptions matching the JSON exactly. Note the grammar: backticked id, `; header `, `; ask when `, `; question `, `; options: `, em-dash separated option pairs, terminating period.

- [ ] **Step 3: Register the skill in the safety checker**

In `scripts/check-runtime-intake-safety.py`:

- add `"srx-initial-setup",` to `EXPECTED_SKILLS`, in alphabetical position immediately before `"srx-ipsec-hub-spoke",`
- add the digest from Step 1 to the digest map, in the same alphabetical position
- add these `SAFE_FIRST_LABELS` entries, each naming a question whose recommended default must stay read-only:

```python
    ("srx-initial-setup", "sis_entry_state"):
        "Assess the device first (Recommended)",
    ("srx-initial-setup", "sis_change_authority"):
        "Read-only assessment (Recommended)",
    ("srx-initial-setup", "sis_console"):
        "Confirm console access first (Recommended)",
    ("srx-initial-setup", "sis_platform"):
        "Read the platform from the device (Recommended)",
    ("srx-initial-setup", "sis_task"):
        "Assess and report gaps (Recommended)",
```

- [ ] **Step 4: Run the safety checks to verify they pass**

Run: `python3 scripts/check-runtime-intake-safety.py && python3 scripts/test-runtime-intake-safety.py`
Expected: PASS, reporting 27 selected plan/reference catalogs.

If Appendix A and the JSON disagree, the checker reports the mismatching field. Fix Appendix A to match the JSON — the JSON is the shipped artifact and is authoritative.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-07-24-runtime-intake-questions.md scripts/check-runtime-intake-safety.py
git commit -m "feat(srx-initial-setup): register intake catalog in safety checker"
```

---

### Task 4: Entry-state assessment reference

**Files:**
- Create: `skills/srx-initial-setup/references/entry-state-assessment.md`

**Interfaces:**
- Consumes: intake id `sis_entry_state`.
- Produces: the five entry-state names `factory-default`, `bare`, `partial`, `configured`, `unreachable`, used by `gap-model.md` in Task 6 and by every stage reference in Tasks 8–12. Produces the assessment evidence list consumed by `verification.md` in Task 14.

- [ ] **Step 1: Retrieve and record the assessment commands**

Find current Juniper documentation for the read-only commands that establish: platform model and Junos release; chassis-cluster membership; configured interfaces and units; security zones and their `host-inbound-traffic`; screen profiles and zone bindings; security policies; management-plane state including root authentication, system services, name servers, and NTP; and entitlement state.

For each command record title, URL, and retrieval date. Commands already verified live elsewhere in this repository may be reused by citing that skill's reference — `skills/srx-license-signature-maintenance/references/licensing.md` already carries verified entitlement commands, including the finding that the entitlement command takes no `node` argument.

Acceptance: every command in the file carries a source, a live-observation note, or an explicit unverified marking.

- [ ] **Step 2: Write the reference**

Structure the file as:

```markdown
# Entry-State Assessment

Read-only. Runs before any question about intent and before any write is proposed.

## Entry states

| Entry state | Signature | Consequence |
|---|---|---|
| `factory-default` | Vendor-shipped configuration still present | Load `factory-default-branch.md`; removal steps become gap entries |
| `bare` | Minimal or zeroized configuration, no zones or policy | Build every stage from zero |
| `partial` | Some stages complete, others absent | Close only the open gaps |
| `configured` | All stages satisfied | Report the verification matrix; propose no writes |
| `unreachable` | No usable management channel | Emit the console recovery path; propose no writes |

## Evidence to collect

[the sourced command list from Step 1, grouped by what each establishes]

## Classification rules

[how the collected evidence maps to exactly one entry state, including
the tie-break when a device shows both factory-default remnants and
operator configuration — classify as `partial` and list the remnants as
gaps, because a half-removed factory default is more dangerous than
either clean state]

## Chassis cluster

If cluster membership is found, stop. Cluster formation is out of scope:
route to `srx-chassis-cluster-proxmox` for Proxmox-hosted lab clusters or
`srx-mnha` for Multi-Node High Availability. This skill covers the
single-node case and the pre-cluster baseline only.
```

- [ ] **Step 3: Reference it from SKILL.md and verify the path resolves**

Add a `references/entry-state-assessment.md` mention to `SKILL.md`. The package checker errors on any referenced path that does not exist, so this is the check that the wiring is correct.

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add entry-state assessment reference"
```

---

### Task 5: Branch factory-default reference

This is requirement #1 from the repository owner and the highest-value content in the skill.

**Files:**
- Create: `skills/srx-initial-setup/references/factory-default-branch.md`

**Interfaces:**
- Consumes: entry state `factory-default` from Task 4.
- Produces: named factory-default gap ids in the `factory.*` namespace, consumed by the gap list in Task 6.

- [ ] **Step 1: Retrieve and record the factory-default content**

Find current Juniper documentation describing the shipped configuration for SRX300 and SRX400 Branch platforms: which zones exist, which interfaces are placed in them, what DHCP service is running, what security policies are present, what management access is preconfigured, and what the documented reset procedure is.

Record title, URL, and retrieval date per claim.

Acceptance: each documented element states which platforms it applies to. Where documentation covers a platform generation the owner does not have, say so rather than generalizing silently. Campus and datacenter platforms do not ship this configuration — state that explicitly rather than leaving it implied.

- [ ] **Step 2: Write the reference**

Structure the file as:

```markdown
# Branch Factory-Default Configuration

Applies to SRX300 and SRX400 Branch platforms. Campus and datacenter
platforms do not ship this configuration; on those, an entry state of
`factory-default` means something else and this file does not apply.

## What ships on the device

[sourced table of zones, interface placement, DHCP service, policies,
and preconfigured management access]

## Why removal is a lockout-risk change

The shipped configuration may be what is currently providing the
operator's address. Removing it before the replacement management path
is established and verified costs reachability. Every gap in this file
carries `lockout_risk: true`.

## Adopt or remove

[the decision, per element: which shipped elements are worth keeping for
a given deployment and which must go, with the reasoning stated so an
operator can disagree deliberately]

## Gap entries

[one entry per removable element, in the `factory.*` id namespace, each
with its dependency on the management-plane stage completing first]
```

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): document Branch factory-default handling"
```

---

### Task 6: Gap model reference

**Files:**
- Create: `skills/srx-initial-setup/references/gap-model.md`

**Interfaces:**
- Consumes: entry states from Task 4; the `factory.*` ids from Task 5.
- Produces: the gap record schema — fields `id`, `stage`, `severity`, `depends_on`, `lockout_risk`, `evidence`, `proposal` — and the id namespaces `access.*`, `mgmt.*`, `zone.*`, `screen.*`, `policy.*`, `factory.*`. Tasks 8–12 each populate their own namespace using exactly these field names.

- [ ] **Step 1: Write the reference**

```markdown
# Gap Model

A gap is a structured record, not prose. Every proposed change to the
device exists as a gap first.

## Schema

| Field | Meaning |
|---|---|
| `id` | Stable identifier, namespaced by stage, e.g. `mgmt.ntp-absent` |
| `stage` | Owning stage |
| `severity` | `blocking` (later stages cannot proceed) or `advisory` |
| `depends_on` | Gap ids that must close first |
| `lockout_risk` | Whether closing this gap can cost management reachability |
| `evidence` | What was read that established the gap |
| `proposal` | Candidate configuration, emitted as a diff |

## Namespaces

`access.*`, `mgmt.*`, `zone.*`, `screen.*`, `policy.*`, `factory.*`

## Ordering

Gaps close in dependency order. A gap whose `depends_on` is unsatisfied
is not offered. Any gap with `lockout_risk: true` requires the protocol
in `write-safety.md` without exception.

## Idempotency

Re-running against a device with no open gaps produces the verification
matrix and proposes nothing. A gap already closed is never re-proposed;
assessment reads current state rather than trusting a prior run.

## Reporting a gap that cannot be closed

[when a gap is real but out of scope — cluster membership, an unlicensed
feature, a platform behavior that could not be sourced — record it as a
gap with a routing target rather than silently dropping it]
```

- [ ] **Step 2: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add gap model reference"
```

---

### Task 7: Write-safety reference

Specified once here and referenced everywhere else, so the protocol cannot drift between stages. This file is also what `srx-atp-cloud` will reuse.

**Files:**
- Create: `skills/srx-initial-setup/references/write-safety.md`

**Interfaces:**
- Consumes: `lockout_risk` from Task 6.
- Produces: the named gate protocol steps referenced by Tasks 8–12. Stage files reference this file; they do not restate it.

- [ ] **Step 1: Retrieve and record the rollback mechanics**

Find current Juniper documentation for confirmed-commit behavior: the syntax, the timer semantics, what happens when the confirming commit does not arrive, and how rollback points are addressed.

Acceptance: the timer default recommended by this skill is stated as a number with a reason, and the reason references verifying reachability before the timer expires.

- [ ] **Step 2: Write the reference**

```markdown
# Write Safety

This repository's skills default to read, parse, plan, and dry-run. This
skill writes. The exception is bounded here and nowhere else.

## The gate protocol

1. Assess read-only. Never propose a change from an assumption about
   current state.
2. Show the candidate change as a configuration diff before applying it.
3. Obtain explicit approval for this stage. Approval of one gate never
   implies approval of the next.
4. Apply under confirmed commit with a rollback timer.
5. Verify reachability and the stage's success criteria.
6. Issue the confirming commit only after verification succeeds.

**Never issue a bare commit on a remote session.**

## Timer default

[the sourced default from Step 1, with its reasoning]

## Lockout-risk changes

Before proposing any change with `lockout_risk: true`, state to the
operator what their recovery path is if reachability is lost. If the
operator has not confirmed out-of-band access, ask `sis_console` and do
not proceed on an assumption.

Never propose a change that removes the management path currently in use
without first establishing and verifying the replacement.

## Rollback points

[how a pre-stage rollback point is recorded and addressed, sourced]

## What this protocol does not cover

Junos upgrades, reboots, cluster failover, and license installation.
Those route to their owning skills.
```

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add write-safety gate protocol"
```

---

### Task 8: Stage 1 — access and recovery

**Files:**
- Create: `skills/srx-initial-setup/references/stages/access-and-recovery.md`

**Interfaces:**
- Consumes: `write-safety.md` protocol; intake id `sis_console`.
- Produces: gap ids in the `access.*` namespace. `access.*` gaps are `blocking` for every later stage.

- [ ] **Step 1: Retrieve and record the syntax**

Source the configuration for: setting root authentication, creating a named administrative login account with a class, and enabling the management access services this stage turns on. Record title, URL, and retrieval date.

Acceptance: the file states that a Junos commit is rejected until root authentication is set, if and only if that is confirmed by documentation. Do not assert it from memory.

- [ ] **Step 2: Write the stage file**

Sections: `# Stage 1 — Access and Recovery`; `## What this stage establishes`; `## Gaps` (each `access.*` entry with the schema fields from `gap-model.md`); `## Out-of-band path` (why this stage confirms console access before any later lockout-risk stage runs); `## Verification` (what proves the stage succeeded).

Every gap entry names its `severity`, `depends_on`, and `lockout_risk` explicitly.

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add access and recovery stage"
```

---

### Task 9: Stage 2 — management plane

**Files:**
- Create: `skills/srx-initial-setup/references/stages/management-plane.md`

**Interfaces:**
- Consumes: `access.*` gaps closed (Task 8).
- Produces: gap ids in the `mgmt.*` namespace, including `mgmt.ntp-absent`. `factory.*` gaps from Task 5 depend on this stage completing.

- [ ] **Step 1: Retrieve and record the syntax**

Source: hostname and domain, name servers, NTP, management addressing, system services, and login accounts.

- [ ] **Step 2: Write the stage file, routing the source-interface question rather than re-deriving it**

`srx-syslog-logging` already owns the analysis of `fxp0` versus a revenue interface, `mgmt_junos`, and the management VRF. This stage **routes there** and does not restate that reasoning — restating it is how the two skills drift into disagreeing.

Sections: `# Stage 2 — Management Plane`; `## What this stage establishes`; `## Choosing the management interface` (a short statement of the decision plus a pointer to `srx-syslog-logging`); `## Gaps`; `## Verification`.

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add management plane stage"
```

---

### Task 10: Stage 3 — interfaces and zones

The highest lockout risk in the skill.

**Files:**
- Create: `skills/srx-initial-setup/references/stages/interfaces-and-zones.md`

**Interfaces:**
- Consumes: `mgmt.*` gaps closed (Task 9); the gate protocol from Task 7.
- Produces: gap ids in the `zone.*` namespace. Task 11 screens bind to the zones this stage creates; Task 12 policies reference them.

- [ ] **Step 1: Retrieve and record the syntax**

Source: interface unit addressing, security zone creation, interface-to-zone assignment, and `host-inbound-traffic` for both system services and protocols.

Acceptance: the file explains what `host-inbound-traffic` controls and why omitting it is the most common way a correctly-addressed interface becomes unreachable.

- [ ] **Step 2: Write the stage file**

Sections: `# Stage 3 — Interfaces and Zones`; `## What this stage establishes`; `## Why this stage is the lockout stage`; `## Gaps`; `## Ordering within the stage` (establish and verify the replacement path before removing the old one); `## Verification`.

Every `zone.*` gap that touches the interface currently carrying management traffic is marked `lockout_risk: true`.

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add interfaces and zones stage"
```

---

### Task 11: Stage 4 — starter screens

**Files:**
- Create: `skills/srx-initial-setup/references/stages/screens.md`

**Interfaces:**
- Consumes: zones created in Task 10.
- Produces: gap ids in the `screen.*` namespace.

- [ ] **Step 1: Retrieve and record the screen options**

Source the available screen options, their defaults, and their zone binding. Record title, URL, and retrieval date.

Acceptance: for every option the skill proposes turning on, the file states what it does **and its false-positive risk**. An option whose false-positive behavior cannot be sourced is not in the starter profile.

- [ ] **Step 2: Write the stage file**

Sections: `# Stage 4 — Starter Screens`; `## What screens are and are not` (they are not a substitute for policy — state this plainly); `## The starter profile` (a table: option, what it blocks, false-positive risk, in or out of the starter profile, and why); `## Binding to zones`; `## Gaps`; `## Verification`.

The starter profile is conservative: an option that can drop legitimate traffic in a normal branch deployment is proposed as advisory, not applied by default.

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add starter screens stage"
```

---

### Task 12: Stage 5 — baseline policy

This stage deliberately stops short. Guarding that boundary is the point of the task.

**Files:**
- Create: `skills/srx-initial-setup/references/stages/baseline-policy.md`

**Interfaces:**
- Consumes: zones from Task 10.
- Produces: gap ids in the `policy.*` namespace, and the routing handoff to `srx-policy`.

- [ ] **Step 1: Retrieve and record the syntax**

Source: minimal security policy structure, the default-deny behavior, and policy logging.

Cross-check against `skills/srx-policy/SKILL.md` before writing. That skill takes a documented position on global versus zone-pair policy for greenfield and day-one onboarding. **This stage must agree with it.** If the two would disagree, stop and raise it rather than shipping a contradiction.

- [ ] **Step 2: Write the stage file**

Sections: `# Stage 5 — Baseline Policy`; `## The minimum, and why it is the minimum`; `## Default deny and logging`; `## Gaps`; `## Where this stage stops` (an explicit list of what belongs to `srx-policy`: AppFW, NGWF, EWF, SecIntel, ATP placement, rule design beyond the baseline); `## Verification`.

- [ ] **Step 3: Verify the boundary claim against srx-policy**

Run: `python3 scripts/check-srx-policy-global-default.py`
Expected: PASS. This check exists because the repository already pins `srx-policy`'s global-policy default; a baseline that contradicts it will surface here.

- [ ] **Step 4: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add baseline policy stage"
```

---

### Task 13: Entitlement readout and routing

**Files:**
- Create: `skills/srx-initial-setup/references/entitlement-readout.md`

**Interfaces:**
- Consumes: assessment evidence from Task 4.
- Produces: the five result states `active`, `licensed but not configured`, `configured but not licensed`, `neither`, `indeterminate`, and the routing table consumed by `SKILL.md` in Task 15.

- [ ] **Step 1: Reuse the existing verified licensing evidence**

Read `skills/srx-license-signature-maintenance/references/licensing.md` first. It already carries live-verified entitlement commands and two findings this file must preserve rather than rediscover:

- a license counter reporting used does **not** mean the feature is enforcing; a live device reported `IDP-SIG` with `used 1` while the IDP policy was `none`
- the entitlement command takes **no** `node` argument; per-node state requires reaching each routing engine

Cite that reference rather than duplicating its content.

- [ ] **Step 2: Write the reference**

```markdown
# Entitlement Readout

Read-only. This skill never installs, modifies, or removes a license.
All mutating license work routes to `srx-license-signature-maintenance`.

## The three axes

| Axis | Source |
|---|---|
| Entitled | Entitlement output |
| Configured | Running configuration |
| Active | Operational status for that feature |

A license counter alone is never treated as proof a feature is active.

## Result states

`active`, `licensed but not configured`, `configured but not licensed`,
`neither`, `indeterminate`.

`indeterminate` is a first-class result. When any axis cannot be read,
the result is `indeterminate` and is reported as such. Do not round it to
a cleaner state.

## Routing table

| Feature area | Routes to |
|---|---|
| AppID, IDP/IPS entitlement and signature content | `srx-license-signature-maintenance` |
| Security policy, AppFW, NGWF, EWF, SecIntel placement | `srx-policy` |
| ATP Cloud | `srx-atp-cloud` |
| NAT | `srx-nat` |
| Logging to a collector or SIEM | `srx-syslog-logging` |
| Chassis cluster / MNHA | `srx-chassis-cluster-proxmox`, `srx-mnha` |
| IPsec | `srx-ipsec-hub-spoke`, `srx-autovpn-full-tunnel`, `srx-advpn` |

## Secret handling

Report entitlement fields only. License keys, entitlement blobs, license
identifiers, software serial numbers, and customer identifiers never
appear in output.
```

`srx-atp-cloud` does not exist yet. Reference it as the planned owner; the routing row is why the second package exists. Do not add it to `related_skills` frontmatter until it ships.

- [ ] **Step 3: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add entitlement readout and routing"
```

---

### Task 14: Verification reference

**Files:**
- Create: `skills/srx-initial-setup/references/verification.md`

**Interfaces:**
- Consumes: the per-stage verification sections from Tasks 8–12.
- Produces: the verification matrix that the `configured` entry state emits.

- [ ] **Step 1: Write the reference**

Sections: `# Verification`; `## Per-stage criteria` (one row per stage: what is checked, what output proves it, what a failure looks like); `## The finished-device matrix` (what a `configured` device reports when the skill is re-run and finds no gaps); `## When verification fails after a commit` (the confirmed-commit timer has not yet expired — do not issue the confirming commit; let it roll back, then re-assess).

That last section is the reason confirmed commit is used at all. State it explicitly.

- [ ] **Step 2: Verify packaging still passes**

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): add verification reference"
```

---

### Task 15: Assemble SKILL.md

Replaces the Task 1 placeholder body with the real skill, staying under the 600-line limit by pointing at the references rather than inlining them.

**Files:**
- Modify: `skills/srx-initial-setup/SKILL.md`

**Interfaces:**
- Consumes: every reference from Tasks 4–14.
- Produces: the shipped skill. Bumps `version` to `1.0.0`.

- [ ] **Step 1: Write the body**

Keep `## Runtime intake` exactly as Task 2 left it. Section order:

```text
# SRX first-time setup
## Overview
## Scope and routing
## Runtime intake            <- unchanged from Task 2
## 1. Entry-state assessment (read-only)
## 2. Gap list
## Gate protocol
## 3. Stages
## 4. Entitlement readout
## 5. Verification
## Failure handling
## Output contract
## Reference material (load on demand)
## Verification checklist
```

`## Scope and routing` states the three hard boundaries up front: chassis cluster routes away, licensing mutation routes away, policy design beyond the baseline routes away.

`## Reference material (load on demand)` lists every file created in Tasks 4–14. Follow the shape used by `skills/srx-license-signature-maintenance/SKILL.md`, which has the same structure.

- [ ] **Step 2: Add the collected sources to frontmatter**

Add a `metadata.sources` list with every source retrieved in Tasks 4–13, each with `title`, `author`, `url`, and `retrieved`. Local references use the `local:` form. Follow the shape in `skills/srx-syslog-logging/SKILL.md`.

- [ ] **Step 3: Bump the version**

Change `version: 0.1.0` to `version: 1.0.0`.

- [ ] **Step 4: Verify the line limit and full packaging**

Run: `wc -l skills/srx-initial-setup/SKILL.md`
Expected: 600 or fewer.

Run: `python3 scripts/check-skill-packages.py`
Expected: PASS, `OK: 28 portable skill packages`.

If over 600 lines, move detail into the reference files rather than deleting it. That is what progressive disclosure is for.

- [ ] **Step 5: Run the full offline gate**

Run: `mise exec -- just guard`
Expected: PASS for every check.

- [ ] **Step 6: Commit**

```bash
git add skills/srx-initial-setup
git commit -m "feat(srx-initial-setup): assemble SKILL.md and release 1.0.0"
```

---

### Task 16: Catalog and documentation

**Files:**
- Modify: `README.md` (skill count near line 192, catalog entry near line 219, review-status prose near line 253)
- Modify: `SKILLS.md` (new `### srx-initial-setup` under `## SRX Operational Skills (detail)`)
- Modify: `QUALITY.md` (review status near line 7)
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: the shipped skill from Task 15.
- Produces: no code interface.

- [ ] **Step 1: Update the README**

Change `**27 skills**` to `**28 skills**` and update the accompanying review-count sentence. Add the catalog bullet in the SRX operational family, matching the existing one-line format:

```markdown
- **[srx-initial-setup](./skills/srx-initial-setup/SKILL.md)** — *(v1.0.0, not yet reviewed)* First-time SRX bring-up: read-only entry-state assessment, Branch factory-default handling, management plane, interfaces and zones, starter screens, a minimal baseline policy, and an entitlement readout that routes onward. Every device write runs under a per-stage gate and confirmed commit.
```

Add `srx-initial-setup` to the not-yet-reviewed list near line 253.

- [ ] **Step 2: Update SKILLS.md and QUALITY.md**

Add a `### srx-initial-setup` detail section under `## SRX Operational Skills (detail)`, matching the depth of the neighboring entries. State plainly that hardware validation is deferred and that Branch claims are documentation-sourced at 1.0.0.

Add the skill to the `QUALITY.md` review-status prose near line 7.

- [ ] **Step 3: Update the CHANGELOG**

Add an entry describing the new skill and stating its validation status honestly: released against documentation and vSRX, with hardware validation deferred.

- [ ] **Step 4: Verify branding and packaging checks**

Run: `python3 scripts/check-readme-branding.py && python3 scripts/check-skill-packages.py`
Expected: PASS for both.

- [ ] **Step 5: Commit**

```bash
git add README.md SKILLS.md QUALITY.md CHANGELOG.md
git commit -m "docs: add srx-initial-setup to the skill catalog"
```

---

### Task 17: Full gate and review

**Files:** none created; this task gates everything above.

- [ ] **Step 1: Run the complete offline gate**

Run: `mise exec -- just release-check`
Expected: PASS for `lint`, `test`, `guard`, and `security`.

`just` is not on `PATH` directly in this environment; invoke it through `mise exec --`.

- [ ] **Step 2: Run the Codex review gate per commit**

Run, for each commit created by Tasks 1–16:

```bash
scripts/codex-review.sh "$(git rev-parse <sha>)"
```

Use the wrapper, never `codex exec review` directly. The wrapper parks the superpowers skill symlink that previously caused seven consecutive runs to end with no verdict, and it exits non-zero when no verdict is produced.

**A run with no final `agent_message` is not a pass.** Report that the gate did not run. If the failure is `Review was interrupted. Please re-run /review` within seconds, check the raw `--json` for `You've hit your usage limit` — that is a spent allowance, not a transient error, and `codex login status` will not diagnose it.

- [ ] **Step 3: Act on findings**

Read the cited lines before accepting or rejecting any finding. A rejected finding needs stated evidence, not an opinion.

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix(srx-initial-setup): address review findings"
```

---

### Task 18 (deferred phase): SRX345 hardware validation

Runs **after** Task 17, as its own phase. Do not interleave with authoring.

**Files:**
- Create: `docs/skill-tests/YYYY-MM-DD-srx-initial-setup-srx345-validation.md`
- Modify: `skills/srx-initial-setup/**` as findings require

**Interfaces:**
- Consumes: the shipped 1.0.0 skill.
- Produces: Branch claims upgraded from documentation-sourced to verified-live, or corrected.

- [ ] **Step 1: Confirm the safety preconditions**

Confirm with the owner, before any device contact: the SRX345 is not carrying production traffic, console access is confirmed reachable, and the device may be reset. Record the confirmation in the test document.

- [ ] **Step 2: Validate the read-only path first**

Run the entry-state assessment against the device and record actual output. This alone tests Task 4 and Task 5 without writing anything.

- [ ] **Step 3: Compare observed factory default against the documented claims**

For each claim in `factory-default-branch.md`, record confirmed, contradicted, or not observed.

- [ ] **Step 4: Validate the write path under the skill's own protocol**

Walk the stage gates using the skill as written, under the confirmed-commit protocol it specifies. Record each gate, the diff shown, the timer used, and the verification result.

- [ ] **Step 5: Write the test record**

Follow `docs/skill-tests/2026-08-05-srx-license-signature-live-validation.md` for structure and depth.

- [ ] **Step 6: Revise the skill for every contradiction**

A contradicted claim results in a skill revision and a version bump, not a footnote. Upgrade confirmed Branch claims to verified-live, naming the platform and Junos release. Generalizing an SRX345 observation to the rest of the SRX300/400 line is still an inference — keep it labeled as one.

- [ ] **Step 7: Re-run the gate and commit**

Run: `mise exec -- just release-check`
Expected: PASS.

```bash
git add docs/skill-tests skills/srx-initial-setup README.md CHANGELOG.md
git commit -m "test(srx-initial-setup): validate against SRX345 hardware"
```

---

### Task 19 (deferred phase): SRX1600 and SRX4700 validation

Runs when that hardware arrives, once per platform. The steps are repeated in full here because the executor of this task may never have read Task 18.

**Files:**
- Create: `docs/skill-tests/YYYY-MM-DD-srx-initial-setup-srx1600-validation.md`
- Create: `docs/skill-tests/YYYY-MM-DD-srx-initial-setup-srx4700-validation.md`
- Modify: `skills/srx-initial-setup/**` as findings require
- Modify: `SKILLS.md`, `docs/superpowers/specs/2026-08-20-srx-initial-setup-design.md`

**Interfaces:**
- Consumes: the shipped skill, as revised by Task 18.
- Produces: campus and datacenter claims upgraded from documentation-sourced to verified-live, or corrected.

- [ ] **Step 1: Confirm the safety preconditions, per platform**

Confirm with the owner, before any device contact: the device is not carrying production traffic, console access is confirmed reachable, and the device may be reset. Record the confirmation in that platform's test document.

- [ ] **Step 2: Validate the read-only path first, per platform**

Run the entry-state assessment and record actual output. Campus and datacenter platforms do not ship the Branch factory-default configuration; confirm that `factory-default-branch.md`'s scope statement is correct on this hardware rather than assuming it.

- [ ] **Step 3: Validate the write path under the skill's own protocol, per platform**

Walk the stage gates using the skill as written, under the confirmed-commit protocol it specifies. Record each gate, the diff shown, the timer used, and the verification result.

- [ ] **Step 4: Write one test record per platform**

Follow `docs/skill-tests/2026-08-05-srx-license-signature-live-validation.md` for structure and depth.

- [ ] **Step 5: Revise the skill for every contradiction**

A contradicted claim results in a skill revision and a version bump, not a footnote.

- [ ] **Step 6: Update the platform confidence table**

In both `SKILLS.md` and the spec's validation table, move the validated platforms from documentation-sourced to verified-live. SRX4120, SRX4300, and SRX5000 remain documentation-sourced and must stay labeled as such.

- [ ] **Step 7: Re-run the gate and commit**

Run: `mise exec -- just release-check`
Expected: PASS.

```bash
git add docs/skill-tests skills/srx-initial-setup SKILLS.md docs/superpowers/specs CHANGELOG.md
git commit -m "test(srx-initial-setup): validate against SRX1600 and SRX4700"
```

---

## Follow-on work

`srx-atp-cloud` is the second package in the spec and gets its own plan after this one ships. It reuses `write-safety.md` and the assessment shape proven here rather than restating them. Its enrolment mechanics must be written from Juniper ATP Cloud documentation retrieved at implementation time.
