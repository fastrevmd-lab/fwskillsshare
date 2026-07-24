# Portable Runtime Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add conditional, Claude/Codex-compatible runtime intake to all 22 firewall skills without making any package depend on repository-local shared content.

**Architecture:** Put a concise invocation contract in every `SKILL.md` and the complete skill-specific catalog in that package's `references/runtime-intake.md`. Add a Python standard-library validator that checks the shared behavioral contract and the neutral JSON question schema, then execute a separate RED/GREEN cycle for every skill.

**Tech Stack:** Markdown skill packages, JSON catalogs embedded in Markdown, Python 3 standard library validation, YAML UI metadata, `just`, pre-commit, Trivy, and Git.

## Global Constraints

- Work only in `.worktrees/runtime-intake-questions` on branch `runtime-intake-questions`.
- Execute with fresh sequential implementer and reviewer subagents; the user
  explicitly authorized subagent-driven execution after approving the plan.
- Update all 22 packages listed in the approved design.
- Keep each package independently installable; every runtime reference lives below its own skill directory.
- Do not modify any copied `intermediate-schema.md`.
- Keep every `SKILL.md` at or below 500 lines.
- Ask only when an unresolved answer materially changes safety, scope, correctness, confidence, or output.
- Inspect the prompt and approved read-only evidence before asking.
- Never repeat answered questions or present the complete catalog automatically.
- Ask no more than three single-select questions per interaction round.
- Use Claude `AskUserQuestion`, Codex `request_user_input`, or a concise plain-text fallback.
- Keep a free-text `Other` path.
- Never request passwords, PSKs, private keys, tokens, device credentials, or unredacted customer data.
- Treat answers as context, not authorization for configuration, commit, upgrade, reboot, delete, or failover.
- Obtain separate explicit approval immediately before any live or destructive action.
- Use the exact question data in Appendix A. Minor punctuation wrapping is allowed; changing semantic choices is not.
- Do not contact devices or run real-device integration.

Use this exact section in every `SKILL.md` except `srx-mnha` and `srx-policy`,
immediately before its main workflow or first procedural section:

```markdown
## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

Invoke Claude `AskUserQuestion` or Codex `request_user_input` only for those
unresolved facts. Do not repeat answered questions or present the full catalog
automatically. Ask at most three single-select questions per round, then
re-evaluate. If no native interaction tool is available, ask the same questions
in concise plain text and preserve a free-text `Other` path.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.
```

For `srx-mnha`, replace the existing four-line `## Scope and routing` block
with this exact compact form so the file remains below 500 lines:

```markdown
## Runtime intake

Use this skill only for MNHA-specific design and behavior. Use `parsing-srx-configs` for full-config extraction, `srx-nat` for general NAT, and `srx-policy` for general policy design.
Before acting, inspect the request, artifacts, and approved read-only evidence. If unresolved facts materially change safety, scope, correctness, confidence, or output, read `references/runtime-intake.md`. Use Claude `AskUserQuestion` or Codex `request_user_input` only for unresolved facts; do not repeat answered questions, and ask at most three single-select questions per round. If neither tool is available, use concise plain text with a free-text `Other` path. Never request secrets or unredacted customer data. Answers are context, not live-change approval; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover.
```

For `srx-policy`, replace the existing four-line `## Scope and routing` block
with this exact compact form:

```markdown
## Runtime intake

Use this skill for SRX policy behavior after relevant configuration is identified. Use `parsing-srx-configs` for full-config extraction and `srx-nat` when translation changes the policy match.
Before acting, inspect the request, artifacts, and approved read-only evidence. If unresolved facts materially change safety, scope, correctness, confidence, or output, read `references/runtime-intake.md`. Use Claude `AskUserQuestion` or Codex `request_user_input` only for unresolved facts; do not repeat answered questions, and ask at most three single-select questions per round. If neither tool is available, use concise plain text with a free-text `Other` path. Never request secrets or unredacted customer data. Answers are context, not live-change approval; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover.
```

Every `references/runtime-intake.md` must use this structure:

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
      "id": "audit_scope",
      "ask_when": "The requested audit components or boundaries are unclear.",
      "header": "Scope",
      "question": "What should the audit cover?",
      "options": [
        {
          "label": "Full device (Recommended)",
          "description": "Include policy, NAT, objects, zones, routing context, and logging."
        },
        {
          "label": "Rulebase only",
          "description": "Limit analysis to security-policy hygiene."
        }
      ]
    }
  ]
}
```
````

The embedded neutral JSON has exactly the top-level key `questions`. Each
question has exactly `id`, `ask_when`, `header`, `question`, and `options`;
each option has exactly `label` and `description`. All text values are nonblank
and stripped. Each prompt is exactly one question sentence with one question
mark, and each description is exactly one sentence.

---

### Task 1: Repair the Proxmox package baseline

**Files:**
- Modify: `scripts/check-skill-packages.py`
- Modify: `skills/sd-onprem-proxmox-deploy/SKILL.md`
- Create: `skills/sd-onprem-proxmox-deploy/agents/openai.yaml`

**Interfaces:**
- Consumes: the committed `sd-onprem-proxmox-deploy` package at baseline commit `05a2946`.
- Produces: a 22-name package inventory and valid author/UI metadata for the Proxmox skill.

- [ ] **Step 1: Confirm the three baseline failures**

Run:

```bash
python3 scripts/check-skill-packages.py
```

Expected: exit 1 reporting the unexpected Proxmox skill, missing `GPT` author,
and missing Codex UI metadata.

- [ ] **Step 2: Update the expected package inventory**

Add this entry to `EXPECTED_SKILL_NAMES` in sorted position:

```python
"sd-onprem-proxmox-deploy",
```

- [ ] **Step 3: Complete the package metadata**

Add `GPT` to the existing author list:

```yaml
author:
  - fastrevmd-lab
  - Claude
  - GPT
```

Create `skills/sd-onprem-proxmox-deploy/agents/openai.yaml`:

```yaml
interface:
  display_name: "SD On-Prem Proxmox Deploy"
  short_description: "Deploy Security Director On-Prem on Proxmox"
  default_prompt: "Use $sd-onprem-proxmox-deploy to plan or validate this Security Director On-Prem deployment on Proxmox VE."
```

- [ ] **Step 4: Verify and commit the prerequisite repair**

Run:

```bash
python3 scripts/check-skill-packages.py
git diff --check
```

Expected: `OK: 22 portable skill packages`; no whitespace errors.

Commit:

```bash
git add scripts/check-skill-packages.py \
  skills/sd-onprem-proxmox-deploy/SKILL.md \
  skills/sd-onprem-proxmox-deploy/agents/openai.yaml
git commit -m "fix: complete Proxmox skill packaging"
```

### Task 2: Add the runtime-intake validator

**Files:**
- Create: `scripts/check-runtime-intake.py`

**Interfaces:**
- Consumes: one optional positional skill name and package-local Markdown/JSON.
- Produces: exit 0 with an `OK` line for valid packages; exit 1 with one `ERROR` line per violation.

- [ ] **Step 1: Write the validator before any skill intake section exists**

Create `scripts/check-runtime-intake.py` with this complete implementation:

```python
#!/usr/bin/env python3
"""Validate portable runtime-intake instructions and question catalogs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CATALOG_RE = re.compile(r"```json\n(?P<payload>.*?)\n```", re.DOTALL)
REQUIRED_SKILL_TEXT = (
    "## Runtime intake",
    "references/runtime-intake.md",
    "AskUserQuestion",
    "request_user_input",
    "at most three",
    "plain text",
    "Never request secrets",
    "separate explicit approval",
)
REQUIRED_REFERENCE_HEADINGS = (
    "# Runtime Intake",
    "## When to ask",
    "## Tool adaptation",
    "## Question catalog",
)


def selected_skill_files(skill_name: str | None) -> list[Path]:
    if skill_name:
        return [SKILLS_DIR / skill_name / "SKILL.md"]
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def validate_catalog(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_REFERENCE_HEADINGS:
        if heading not in text:
            errors.append(f"{path}: missing {heading!r}")

    matches = list(CATALOG_RE.finditer(text))
    if len(matches) != 1:
        errors.append(f"{path}: expected exactly one JSON catalog")
        return errors

    try:
        payload = json.loads(matches[0].group("payload"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON catalog: {exc}")
        return errors

    if not isinstance(payload, dict):
        errors.append(f"{path}: catalog must be a JSON object")
        return errors

    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"{path}: questions must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, question in enumerate(questions, start=1):
        prefix = f"{path}: question {index}"
        if not isinstance(question, dict):
            errors.append(f"{prefix} must be an object")
            continue

        question_id = question.get("id")
        if not isinstance(question_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]*", question_id
        ):
            errors.append(f"{prefix} has invalid id")
        elif question_id in seen_ids:
            errors.append(f"{prefix} duplicates id {question_id!r}")
        else:
            seen_ids.add(question_id)

        ask_when = question.get("ask_when")
        if not isinstance(ask_when, str) or not ask_when.strip():
            errors.append(f"{prefix} has empty ask_when")

        header = question.get("header")
        if not isinstance(header, str) or not 1 <= len(header) <= 12:
            errors.append(f"{prefix} header must contain 1-12 characters")

        prompt = question.get("question")
        if not isinstance(prompt, str) or not prompt.strip().endswith("?"):
            errors.append(f"{prefix} question must be non-empty and end with '?'")

        options = question.get("options")
        if not isinstance(options, list) or not 2 <= len(options) <= 3:
            errors.append(f"{prefix} must have 2-3 options")
            continue

        labels: set[str] = set()
        for option_index, option in enumerate(options, start=1):
            option_prefix = f"{prefix} option {option_index}"
            if not isinstance(option, dict):
                errors.append(f"{option_prefix} must be an object")
                continue
            label = option.get("label")
            description = option.get("description")
            if not isinstance(label, str) or not label.strip():
                errors.append(f"{option_prefix} has empty label")
            elif label in labels:
                errors.append(f"{option_prefix} duplicates label {label!r}")
            else:
                labels.add(label)
                words = label.removesuffix(" (Recommended)").split()
                if not 1 <= len(words) <= 5:
                    errors.append(f"{option_prefix} label must contain 1-5 words")
            if (
                not isinstance(description, str)
                or not description.strip().endswith((".", "!", "?"))
            ):
                errors.append(f"{option_prefix} description must be one sentence")

        first_label = options[0].get("label") if isinstance(options[0], dict) else ""
        if not isinstance(first_label, str) or not first_label.endswith("(Recommended)"):
            errors.append(f"{prefix} first option must end with '(Recommended)'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?")
    args = parser.parse_args()
    errors: list[str] = []
    skill_files = selected_skill_files(args.skill)

    for skill_file in skill_files:
        if not skill_file.exists():
            errors.append(f"{skill_file}: missing skill")
            continue
        skill_text = skill_file.read_text(encoding="utf-8")
        for required in REQUIRED_SKILL_TEXT:
            if required not in skill_text:
                errors.append(f"{skill_file}: missing {required!r}")

        reference = skill_file.parent / "references" / "runtime-intake.md"
        if not reference.exists():
            errors.append(f"{reference}: missing runtime-intake reference")
            continue
        errors.extend(validate_catalog(reference, reference.read_text(encoding="utf-8")))

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    print(f"OK: {len(skill_files)} runtime-intake catalogs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the first RED test**

Run:

```bash
python3 scripts/check-runtime-intake.py firewall-best-practices-audit
```

Expected: exit 1 reporting the missing `## Runtime intake` section and missing
`references/runtime-intake.md`. This proves the validator detects the absent
feature.

- [ ] **Step 3: Validate the validator itself**

Run:

```bash
python3 -m py_compile scripts/check-runtime-intake.py
git diff --check
```

Expected: both commands exit 0.

- [ ] **Step 4: Commit the RED validator**

```bash
git add scripts/check-runtime-intake.py
git commit -m "test: require portable runtime intake"
```

### Tasks 3-24: Add intake to each skill sequentially

For every task below, use the exact shared `SKILL.md` section and reference
structure from Global Constraints, and the exact catalog rows from Appendix A.
Do not start the next task until the focused validator passes and the current
skill is committed.

Each task follows this complete cycle:

1. Run `python3 scripts/check-runtime-intake.py <skill>` and confirm exit 1 for
   the missing feature.
2. Add the shared `## Runtime intake` section to `<skill>/SKILL.md`.
3. Create `<skill>/references/runtime-intake.md` with the shared reference
   headings and that skill's Appendix A catalog serialized as valid JSON.
4. Run:

   ```bash
   python3 scripts/check-runtime-intake.py <skill>
   python3 scripts/check-skill-packages.py
   git diff --check
   ```

   Expect all three commands to exit 0.
5. Commit only that skill:

   ```bash
   git add skills/<skill>/SKILL.md skills/<skill>/references/runtime-intake.md
   git commit -m "feat(<skill>): add runtime intake"
   ```

### Task 3: `cis-controls-ngfw-compliance`

**Files:** Modify `skills/cis-controls-ngfw-compliance/SKILL.md`; create
`skills/cis-controls-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.1 (`cis_goal`, `cis_version`, `cis_ig`, `cis_scope`,
`cis_evidence`, `cis_output`).

### Task 4: `cmmc-nist-800-171-ngfw-compliance`

**Files:** Modify `skills/cmmc-nist-800-171-ngfw-compliance/SKILL.md`; create
`skills/cmmc-nist-800-171-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.2 (`cmmc_basis`, `cmmc_stage`, `cmmc_boundary`,
`cmmc_assets`, `cmmc_evidence`, `cmmc_output`).

### Task 5: `firewall-best-practices-audit`

**Files:** Modify `skills/firewall-best-practices-audit/SKILL.md`; create
`skills/firewall-best-practices-audit/references/runtime-intake.md`.

**Catalog:** Appendix A.3 (`audit_goal`, `audit_scope`, `audit_evidence`,
`audit_context`, `audit_depth`, `audit_remed`).

### Task 6: `firewall-config-conversion`

**Files:** Modify `skills/firewall-config-conversion/SKILL.md`; create
`skills/firewall-config-conversion/references/runtime-intake.md`.

**Catalog:** Appendix A.4 (`convert_source`, `convert_target`,
`convert_release`, `convert_scope`, `convert_base`, `convert_loss`,
`convert_output`).

### Task 7: `firewall-config-diff`

**Files:** Modify `skills/firewall-config-diff/SKILL.md`; create
`skills/firewall-config-diff/references/runtime-intake.md`.

**Catalog:** Appendix A.5 (`diff_goal`, `diff_direction`, `diff_scope`,
`diff_identity`, `diff_ignore`, `diff_output`).

### Task 8: `hipaa-ngfw-compliance`

**Files:** Modify `skills/hipaa-ngfw-compliance/SKILL.md`; create
`skills/hipaa-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.6 (`hipaa_role`, `hipaa_goal`, `hipaa_scope`,
`hipaa_vendor`, `hipaa_evidence`, `hipaa_output`).

### Task 9: `iso27001-ngfw-compliance`

**Files:** Modify `skills/iso27001-ngfw-compliance/SKILL.md`; create
`skills/iso27001-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.7 (`iso_goal`, `iso_scope`, `iso_soa`, `iso_basis`,
`iso_period`, `iso_output`).

### Task 10: `parsing-cisco-configs`

**Files:** Modify `skills/parsing-cisco-configs/SKILL.md`; create
`skills/parsing-cisco-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.8 (`cisco_goal`, `cisco_platform`, `cisco_coverage`,
`cisco_scope`, `cisco_output`).

### Task 11: `parsing-fortinet-configs`

**Files:** Modify `skills/parsing-fortinet-configs/SKILL.md`; create
`skills/parsing-fortinet-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.9 (`forti_goal`, `forti_coverage`, `forti_vdom`,
`forti_scope`, `forti_output`).

### Task 12: `parsing-palo-configs`

**Files:** Modify `skills/parsing-palo-configs/SKILL.md`; create
`skills/parsing-palo-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.10 (`palo_goal`, `palo_format`, `palo_scope`,
`palo_coverage`, `palo_output`).

### Task 13: `parsing-srx-configs`

**Files:** Modify `skills/parsing-srx-configs/SKILL.md`; create
`skills/parsing-srx-configs/references/runtime-intake.md`.

**Catalog:** Appendix A.11 (`srxp_goal`, `srxp_format`, `srxp_scope`,
`srxp_coverage`, `srxp_output`).

### Task 14: `pci-ngfw-compliance`

**Files:** Modify `skills/pci-ngfw-compliance/SKILL.md`; create
`skills/pci-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.12 (`pci_version`, `pci_stage`, `pci_scope`,
`pci_segment`, `pci_evidence`, `pci_output`).

### Task 15: `sd-onprem-proxmox-deploy`

**Files:** Modify `skills/sd-onprem-proxmox-deploy/SKILL.md`; create
`skills/sd-onprem-proxmox-deploy/references/runtime-intake.md`.

**Catalog:** Appendix A.13 (`sd_stage`, `sd_release`, `sd_media`, `sd_size`,
`sd_proxmox`, `sd_network`, `sd_services`, `sd_transfer`, `sd_secrets`,
`sd_onboard`).

### Task 16: `soc2-ngfw-compliance`

**Files:** Modify `skills/soc2-ngfw-compliance/SKILL.md`; create
`skills/soc2-ngfw-compliance/references/runtime-intake.md`.

**Catalog:** Appendix A.14 (`soc2_type`, `soc2_tsc`, `soc2_period`,
`soc2_system`, `soc2_vendor`, `soc2_output`).

### Task 17: `srx-advpn`

**Files:** Modify `skills/srx-advpn/SKILL.md`; create
`skills/srx-advpn/references/runtime-intake.md`.

**Catalog:** Appendix A.15 (`advpn_task`, `advpn_release`, `advpn_topo`,
`advpn_auth`, `advpn_route`, `advpn_traffic`, `advpn_gateway`,
`advpn_evidence`).

### Task 18: `srx-autovpn-full-tunnel`

**Files:** Modify `skills/srx-autovpn-full-tunnel/SKILL.md`; create
`skills/srx-autovpn-full-tunnel/references/runtime-intake.md`.

**Catalog:** Appendix A.16 (`autovpn_task`, `autovpn_release`,
`autovpn_traffic`, `autovpn_auth`, `autovpn_lans`, `autovpn_nat`,
`autovpn_route`, `autovpn_evidence`).

### Task 19: `srx-dynamic-ip-feed`

**Files:** Modify `skills/srx-dynamic-ip-feed/SKILL.md`; create
`skills/srx-dynamic-ip-feed/references/runtime-intake.md`.

**Catalog:** Appendix A.17 (`dif_task`, `dif_release`, `dif_source`, `dif_tls`,
`dif_auth`, `dif_route`, `dif_effect`, `dif_session`, `dif_poll`).

### Task 20: `srx-ipsec-hub-spoke`

**Files:** Modify `skills/srx-ipsec-hub-spoke/SKILL.md`; create
`skills/srx-ipsec-hub-spoke/references/runtime-intake.md`.

**Catalog:** Appendix A.18 (`hsvpn_task`, `hsvpn_release`, `hsvpn_topo`,
`hsvpn_traffic`, `hsvpn_auth`, `hsvpn_route`, `hsvpn_evidence`).

### Task 21: `srx-mnha`

**Files:** Modify `skills/srx-mnha/SKILL.md`; create
`skills/srx-mnha/references/runtime-intake.md`.

**Catalog:** Appendix A.19 (`mnha_task`, `mnha_release`, `mnha_mode`,
`mnha_migrate`, `mnha_topo`, `mnha_service`, `mnha_route`, `mnha_objective`,
`mnha_test`).

Use the compact replacement form from Global Constraints and preserve the
existing MNHA scope sentence verbatim.

### Task 22: `srx-mpls-in-flow`

**Files:** Modify `skills/srx-mpls-in-flow/SKILL.md`; create
`skills/srx-mpls-in-flow/references/runtime-intake.md`.

**Catalog:** Appendix A.20 (`mpls_task`, `mpls_release`, `mpls_role`,
`mpls_family`, `mpls_signal`, `mpls_vrf`, `mpls_policy`, `mpls_service`).

### Task 23: `srx-nat`

**Files:** Modify `skills/srx-nat/SKILL.md`; create
`skills/srx-nat/references/runtime-intake.md`.

**Catalog:** Appendix A.21 (`nat_task`, `nat_release`, `nat_family`,
`nat_tuple`, `nat_context`, `nat_reach`, `nat_return`, `nat_evidence`).

### Task 24: `srx-policy`

**Files:** Modify `skills/srx-policy/SKILL.md`; create
`skills/srx-policy/references/runtime-intake.md`.

**Catalog:** Appendix A.22 (`policy_task`, `policy_release`, `policy_model`,
`policy_flow`, `policy_nat`, `policy_service`, `policy_ip`, `policy_session`).

Use the compact replacement form from Global Constraints and preserve the
existing policy scope sentence verbatim.

### Task 25: Integrate validation and run the handoff suite

**Files:**
- Modify: `justfile`
- Verify: all files changed by Tasks 1-24

**Interfaces:**
- Consumes: 22 passing focused runtime-intake catalogs.
- Produces: runtime-intake validation in the normal lint/release path and fresh handoff evidence.

- [ ] **Step 1: Add runtime intake to lint**

Update `lint` in `justfile` to run:

```make
lint:
    python3 scripts/check-skill-packages.py
    python3 scripts/test-runtime-intake-validator.py
    python3 scripts/check-runtime-intake.py
    python3 scripts/check-readme-branding.py
```

- [ ] **Step 2: Run the full runtime and package validation**

```bash
python3 scripts/check-runtime-intake.py
python3 scripts/check-skill-packages.py
python3 scripts/check-readme-branding.py
python3 scripts/check-shared-schema.py
python3 scripts/check-installer.py
git diff --check
```

Expected: 22 runtime catalogs, 22 portable skill packages, branding success,
four identical schemas, existing installer success, and no whitespace errors.

- [ ] **Step 3: Run project-required commands**

If `just` is available:

```bash
just fmt
just lint
just test
just guard
just security
just release-check
```

If `just` remains unavailable, record that limitation and run every underlying
command directly. If `trivy` is available, run:

```bash
trivy fs --scanners vuln,misconfig,secret --exit-code 1 .
```

Do not substitute a claimed security pass when Trivy is unavailable.

- [ ] **Step 4: Inspect the final scope**

```bash
git status --short
git diff --stat 05a2946..HEAD
git log --oneline --decorate -30
```

Expected: only the design, plan, validator, justfile, Proxmox prerequisite
metadata, and the 22 runtime-intake package changes are present.

- [ ] **Step 5: Commit validation integration**

```bash
git add justfile
git commit -m "test: integrate runtime intake validation"
```

### Task 26: Enforce the native projection contract

Harden `scripts/check-runtime-intake.py` with standard-library negative tests
in `scripts/test-runtime-intake-validator.py`. Reject unknown keys at every
neutral JSON level; native-only question keys such as `multiSelect`; blank or
unstripped `ask_when`, `header`, `question`, `label`, and `description`; more
than one question sentence or question mark; and more than one sentence-ending
boundary in a description.

Require every reference to state the exact native projections:

- Claude sends only `question`, `header`, `options`, and
  `multiSelect: false`; it sends neither `id` nor `ask_when`.
- Codex sends only `id`, `header`, `question`, and `options`; it sends neither
  `ask_when` nor `multiSelect`.
- The fallback asks the same questions in concise plain text and retains a
  free-text `Other` path.

Run the negative-contract test script from `just lint` before validating all
22 real catalogs.

## Appendix A: Exact question catalogs

Serialize each row as one neutral-contract question. In the `Options` column,
text before `—` is the label and text after it is the description. The first
option is always the recommended option. End every serialized description with
a period.

### A.1 `cis-controls-ngfw-compliance`

- `cis_goal`; header `Goal`; ask when the requested assessment outcome is
  absent; question `What outcome should this CIS assessment produce?`; options:
  `Gap assessment (Recommended)` — Identify safeguards, evidence gaps, and
  remediation priorities; `Evidence package` — Organize evidence for an
  existing assessment; `Control mapping` — Map controls without grading
  implementation.
- `cis_version`; header `CIS Version`; ask when the governing CIS version is
  absent; question `Which CIS Controls version should govern the assessment?`;
  options: `CIS v8.1 (Recommended)` — Use the current v8.1 safeguard structure;
  `CIS v8` — Use the original v8 structure; `Org profile` — Follow a supplied
  organizational crosswalk.
- `cis_ig`; header `CIS Group`; ask when the Implementation Group is absent and
  affects safeguard scope; question `Which Implementation Group should be
  assessed?`; options: `IG2 (Recommended)` — Assess IG1 and IG2 for a typical
  enterprise; `IG1` — Limit scope to essential cyber hygiene; `IG3` — Include
  all three groups.
- `cis_scope`; header `Scope`; ask when device or boundary scope is absent;
  question `What firewall scope should be included?`; options: `Full estate
  (Recommended)` — Assess all supplied devices and boundaries; `Named boundary`
  — Limit the assessment to a specified system or segment; `Evidence only` —
  Assess only controls directly supported by supplied evidence.
- `cis_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `What evidence is available?`; options: `Config plus records
  (Recommended)` — Use configuration, logs, reviews, tickets, and operating
  records; `Configuration only` — Grade technical configuration and mark
  operating gaps; `Design only` — Review design without claiming
  implementation.
- `cis_output`; header `Output`; ask when deliverable emphasis is absent;
  question `What deliverable should be emphasized?`; options: `Matrix and plan
  (Recommended)` — Produce the safeguard matrix, gaps, and remediation plan;
  `Evidence request` — Emphasize missing assessment artifacts; `Executive
  summary` — Emphasize risk, coverage, and top actions.

### A.2 `cmmc-nist-800-171-ngfw-compliance`

- `cmmc_basis`; header `Basis`; ask when the governing framework or revision is
  absent; question `Which assessment basis should be used?`; options: `CMMC
  Level 2 (Recommended)` — Assess CMMC Level 2 readiness; `NIST 800-171` — Map
  to the specified NIST revision; `Contract overlay` — Include supplied DFARS
  or customer requirements.
- `cmmc_stage`; header `Stage`; ask when assessment stage is absent; question
  `What is the assessment being prepared for?`; options: `Readiness review
  (Recommended)` — Identify gaps before formal assessment; `SSP and POAM` —
  Produce SSP and POA&M evidence; `C3PAO support` — Organize defensible external
  assessment evidence.
- `cmmc_boundary`; header `CUI Scope`; ask when the CUI boundary maturity is
  unknown; question `How mature is the CUI boundary definition?`; options:
  `Defined boundary (Recommended)` — Use the supplied CUI enclave boundary;
  `Draft boundary` — Validate and flag assumptions; `Unknown boundary` — Begin
  with discovery and avoid completeness claims.
- `cmmc_assets`; header `Assets`; ask when asset classes in scope are unclear;
  question `Which assets should be assessed?`; options: `CUI and SPA
  (Recommended)` — Include CUI assets and security protection assets; `Named
  controls` — Limit review to specified requirements or devices; `Full
  environment` — Include adjacent systems that affect CUI protection.
- `cmmc_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `What evidence is available?`; options: `Config plus records
  (Recommended)` — Use configurations, logs, approvals, reviews, and
  procedures; `Configuration only` — Assess technical state and mark practice
  gaps; `Request list` — Produce an evidence request without grading.
- `cmmc_output`; header `Output`; ask when the deliverable is absent; question
  `Which deliverable is most useful?`; options: `Assessment matrix
  (Recommended)` — Provide mappings, evidence, gaps, and remediation; `SSP
  narrative` — Emphasize implementer-ready SSP language; `POAM actions` —
  Emphasize owners, milestones, and residual risk.

### A.3 `firewall-best-practices-audit`

- `audit_goal`; header `Goal`; ask when audit purpose is absent; question `What
  is the primary reason for this firewall audit?`; options: `Baseline hygiene
  (Recommended)` — Review the complete rulebase against general practices;
  `Pre-change review` — Focus on planned-change risk; `Incident focus` —
  Prioritize a suspected attack path.
- `audit_scope`; header `Scope`; ask when included components or boundaries are
  unclear; question `What should the audit cover?`; options: `Full device
  (Recommended)` — Include policy, NAT, objects, zones, routing context, and
  logging; `Rulebase only` — Limit analysis to security-policy hygiene; `Named
  boundary` — Limit analysis to specified contexts.
- `audit_evidence`; header `Evidence`; ask when operational evidence
  availability is unclear; question `What evidence can support the audit?`;
  options: `Config and telemetry (Recommended)` — Combine configuration with
  hit counts, logs, and state; `Configuration only` — Perform static analysis
  and label telemetry dependencies; `Live read-only` — Collect approved
  read-only device evidence.
- `audit_context`; header `Context`; ask when business criticality and trust
  context are absent; question `How should business and trust context be
  established?`; options: `Provide key context (Recommended)` — Use identified
  assets, trust levels, and required flows; `Infer cautiously` — Label inferred
  boundaries; `Generic severity` — Avoid environment-specific impact claims.
- `audit_depth`; header `Depth`; ask when finding detail is not specified;
  question `How much finding detail should be returned?`; options: `Full
  findings (Recommended)` — Include evidence, impact, confidence, and
  remediation; `Critical and high` — Return only material findings; `Top
  actions` — Produce a short remediation backlog.
- `audit_remed`; header `Fix Format`; ask when remediation format is absent;
  question `How should remediation be presented?`; options: `Guidance and CLI
  (Recommended)` — Include candidate syntax and verification; `Guidance only`
  — Explain intent without syntax; `Findings only` — Report risk without fixes.

### A.4 `firewall-config-conversion`

- `convert_source`; header `Source`; ask when the source platform cannot be
  determined confidently; question `How should the source platform be
  determined?`; options: `Auto-detect (Recommended)` — Detect vendor and
  platform from syntax; `Prompt value` — Use the user's exact source platform;
  `Unknown source` — Parse conservatively and report ambiguity.
- `convert_target`; header `Target`; ask when the exact target is absent;
  question `What exact target vendor and platform should receive the
  conversion?`; options: `Specify target (Recommended)` — Supply the exact
  target through Other; `Family only` — Generate conservative family-level
  output; `Undecided` — Produce feasibility analysis only.
- `convert_release`; header `Release`; ask when target model or release affects
  syntax or support and is absent; question `Is the target model and software
  release known?`; options: `Exact target known (Recommended)` — Apply
  release-specific capabilities; `Family known` — Use conservative family
  syntax; `Unknown target` — Avoid implementation-ready syntax.
- `convert_scope`; header `Scope`; ask when conversion components are absent;
  question `What should be converted?`; options: `Full migration
  (Recommended)` — Convert all supported components; `Policy and NAT` — Limit
  work to objects, policy, and NAT; `Named sections` — Convert components named
  through Other.
- `convert_base`; header `Baseline`; ask when existing target state is unknown;
  question `Will the output be applied to an existing target configuration?`;
  options: `Clean target (Recommended)` — Generate against a new target; `Merge
  target` — Account for supplied existing state; `Unknown state` — Produce a
  conflict checklist.
- `convert_loss`; header `Fidelity`; ask when unsupported behavior needs a
  disposition; question `How should unsupported source behavior be handled?`;
  options: `Caveat and map (Recommended)` — Use the closest safe behavior and
  document loss; `Manual placeholder` — Emit an engineer-resolved placeholder;
  `Stop on loss` — Stop dependent output after material loss.
- `convert_output`; header `Output`; ask when deliverable format is absent;
  question `What conversion deliverable is required?`; options: `Config and
  report (Recommended)` — Produce candidate configuration and fidelity report;
  `Fidelity report` — Analyze without configuration; `Config only` — Produce
  syntax with compact caveats.

### A.5 `firewall-config-diff`

- `diff_goal`; header `Goal`; ask when comparison intent is absent; question
  `What relationship should the comparison test?`; options: `Planned drift
  (Recommended)` — Treat A as baseline and B as candidate; `HA parity` — Find
  unintended peer differences; `Migration parity` — Compare intent across
  vendors.
- `diff_direction`; header `Direction`; ask when input roles are ambiguous;
  question `How should the two inputs be labeled?`; options: `A base, B new
  (Recommended)` — Classify changes directionally; `Unordered peers` — Treat
  inputs equally; `Custom roles` — Use roles supplied through Other.
- `diff_scope`; header `Scope`; ask when compared components are absent;
  question `Which configuration areas should be compared?`; options: `All
  sections (Recommended)` — Compare every supported component; `Policy and NAT`
  — Focus on traffic behavior; `Named sections` — Restrict comparison through
  Other.
- `diff_identity`; header `Identity`; ask when rename matching policy affects
  results; question `How should renamed elements be matched?`; options:
  `Semantic matching (Recommended)` — Match resolved meaning before names;
  `Stable names` — Use names as primary identity; `Strict values` — Report every
  name or value difference.
- `diff_ignore`; header `Exceptions`; ask when intentional local differences
  may exist; question `Are any differences expected and approved?`; options:
  `No allowlist (Recommended)` — Report all material differences; `Known local
  deltas` — Exclude a supplied allowlist; `Generated noise` — Ignore known
  non-semantic ordering or metadata.
- `diff_output`; header `Output`; ask when result detail is absent; question
  `How detailed should the result be?`; options: `Full diff report
  (Recommended)` — Include equivalence, additions, removals, impact, and
  confidence; `Risk summary` — Return material differences only; `Machine
  output` — Emphasize structured diff data.

### A.6 `hipaa-ngfw-compliance`

- `hipaa_role`; header `Org Role`; ask when HIPAA organizational role is
  absent; question `What HIPAA role applies to the assessed organization?`;
  options: `Covered entity (Recommended)` — Assess from the covered-entity
  perspective; `Business associate` — Include business-associate
  responsibilities; `Both or unsure` — Evaluate both roles and flag ownership.
- `hipaa_goal`; header `Goal`; ask when review purpose is absent; question `What
  is the purpose of this HIPAA review?`; options: `Risk assessment
  (Recommended)` — Identify ePHI risks and remediation; `Audit evidence` —
  Organize audit artifacts; `Design review` — Review architecture without
  operational claims.
- `hipaa_scope`; header `ePHI Scope`; ask when the ePHI boundary is unclear;
  question `How well defined is the ePHI environment?`; options: `Defined scope
  (Recommended)` — Use identified systems, flows, users, and parties; `Draft
  scope` — Validate a preliminary boundary; `Unknown scope` — Begin discovery
  and avoid completeness claims.
- `hipaa_vendor`; header `Vendors`; ask when third-party ePHI paths are unclear;
  question `How should third-party ePHI paths be handled?`; options: `Include
  all paths (Recommended)` — Assess vendors, remote access, cloud, and
  transmission; `Named vendors` — Limit review to identified parties;
  `Technical only` — Exclude contract conclusions and note BAA needs.
- `hipaa_evidence`; header `Evidence`; ask when evidence period is unclear;
  question `What evidence period is available?`; options: `Config plus records
  (Recommended)` — Use current configuration and dated evidence; `Current state
  only` — Avoid period-of-operation claims; `Evidence request` — Produce a
  targeted collection list.
- `hipaa_output`; header `Output`; ask when report emphasis is absent; question
  `What should the report emphasize?`; options: `Safeguard matrix
  (Recommended)` — Map evidence, gaps, risk, and remediation; `Risk register` —
  Emphasize likelihood, impact, owners, and treatment; `Executive brief` —
  Summarize exposure and top actions.

### A.7 `iso27001-ngfw-compliance`

- `iso_goal`; header `Audit Goal`; ask when engagement type is absent; question
  `What kind of ISO 27001 activity is this?`; options: `Internal readiness
  (Recommended)` — Identify evidence and operation gaps; `Certification audit`
  — Prepare certification or surveillance evidence; `Corrective action` —
  Focus on known findings.
- `iso_scope`; header `ISMS Scope`; ask when the ISMS boundary is unclear;
  question `Is the ISMS scope defined?`; options: `Defined scope
  (Recommended)` — Use supplied organizational and system boundaries; `Draft
  scope` — Validate assumptions; `Unknown scope` — Begin discovery and avoid
  conformity claims.
- `iso_soa`; header `SoA`; ask when Statement of Applicability evidence is
  absent; question `What Statement of Applicability evidence is available?`;
  options: `Current SoA (Recommended)` — Use organizational applicability
  decisions; `Partial SoA` — Flag missing applicability evidence; `No SoA` —
  Use generic mapping without organizational claims.
- `iso_basis`; header `Basis`; ask when control applicability basis is
  unclear; question `Which control basis should drive conclusions?`; options:
  `Org risk plan (Recommended)` — Follow the SoA and risk treatment plan; `Annex
  A only` — Map against ISO 27001 Annex A; `Custom overlay` — Include supplied
  ISO 27002 or customer mappings.
- `iso_period`; header `Evidence`; ask when operating evidence period is
  unclear; question `What operating evidence is available?`; options: `Dated
  samples (Recommended)` — Use records covering the assessment period; `Current
  state only` — Avoid effectiveness claims; `Design only` — Assess intended
  control design.
- `iso_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable is needed?`; options: `Control matrix (Recommended)` — Provide
  mapping, evidence, gaps, and actions; `Audit evidence` — Emphasize traceable
  artifacts; `Risk treatment` — Emphasize treatment and residual risk.

### A.8 `parsing-cisco-configs`

- `cisco_goal`; header `Goal`; ask when downstream purpose is absent and affects
  parsing depth; question `What will the parsed result be used for?`; options:
  `Full normalization (Recommended)` — Populate the shared schema and all
  quality gates; `Focused analysis` — Parse sections relevant to the
  investigation; `Downstream task` — Prepare for conversion, diff, audit, or
  compliance.
- `cisco_platform`; header `Platform`; ask when ASA versus FTD cannot be
  established from the artifact; question `Which Cisco platform produced the
  configuration?`; options: `Auto-detect (Recommended)` — Infer ASA versus FTD
  and report uncertainty; `Cisco ASA` — Apply ASA parsing assumptions; `Cisco
  FTD` — Account for FTD-managed gaps.
- `cisco_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How complete is the supplied configuration?`; options: `Full export
  (Recommended)` — Treat it as a complete running configuration; `Partial
  excerpt` — Mark absent sections unknown; `Unsure` — Detect likely omissions.
- `cisco_scope`; header `Scope`; ask when requested normalized components are
  absent; question `Which components should be normalized?`; options: `All
  sections (Recommended)` — Include all supported components; `Policy and NAT`
  — Focus on traffic selection; `Named sections` — Restrict parsing through
  Other.
- `cisco_output`; header `Output`; ask when output form is absent; question
  `What output should be returned?`; options: `JSON and gates (Recommended)` —
  Return normalized JSON and quality gates; `Normalized JSON` — Return the
  schema only; `Quality report` — Return coverage and ambiguity only.

### A.9 `parsing-fortinet-configs`

- `forti_goal`; header `Goal`; ask when downstream purpose is absent and affects
  parsing depth; question `What will the parsed result be used for?`; options:
  `Full normalization (Recommended)` — Populate the schema and quality gates;
  `Focused analysis` — Parse relevant sections only; `Downstream task` —
  Prepare for conversion, diff, audit, or compliance.
- `forti_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How complete is the FortiGate export?`; options: `Full backup
  (Recommended)` — Treat it as a full configuration; `Partial excerpt` — Mark
  omitted tables and defaults unknown; `Unsure` — Detect likely omissions.
- `forti_vdom`; header `VDOM Scope`; ask when included VDOMs are unclear;
  question `Which VDOM scope should be included?`; options: `All detected
  (Recommended)` — Parse global state and every VDOM; `Named VDOMs` — Limit
  parsing through Other; `Global only` — Exclude VDOM policy.
- `forti_scope`; header `Sections`; ask when included configuration tables are
  absent; question `Which configuration areas should be normalized?`; options:
  `All sections (Recommended)` — Include all supported components; `Policy and
  NAT` — Focus on policy and translation; `Named sections` — Restrict parsing
  through Other.
- `forti_output`; header `Output`; ask when output form is absent; question
  `What output should be returned?`; options: `JSON and gates (Recommended)` —
  Return normalized JSON and quality results; `Normalized JSON` — Return the
  schema only; `Quality report` — Emphasize unresolved references and defaults.

### A.10 `parsing-palo-configs`

- `palo_goal`; header `Goal`; ask when downstream purpose is absent and affects
  parsing depth; question `What will the parsed result be used for?`; options:
  `Full normalization (Recommended)` — Populate the schema and quality gates;
  `Focused analysis` — Parse relevant sections only; `Downstream task` —
  Prepare for conversion, diff, audit, or compliance.
- `palo_format`; header `Format`; ask when XML versus set format or management
  context is ambiguous; question `What type of PAN-OS configuration was
  supplied?`; options: `Auto-detect (Recommended)` — Detect format and
  management context; `PAN-OS XML` — Parse XML hierarchy; `Set format` — Parse
  CLI set statements.
- `palo_scope`; header `Hierarchy`; ask when Panorama inheritance scope is
  unclear; question `How should Panorama or inherited configuration be
  handled?`; options: `Resolve all (Recommended)` — Combine applicable shared,
  device-group, template, and local values; `Named context` — Limit resolution
  through Other; `Local only` — Avoid effective inherited-policy claims.
- `palo_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How complete is the supplied configuration?`; options: `Full export
  (Recommended)` — Treat it as complete; `Partial excerpt` — Mark omitted
  hierarchy unknown; `Unsure` — Detect missing hierarchy and references.
- `palo_output`; header `Output`; ask when output form is absent; question `What
  output should be returned?`; options: `JSON and gates (Recommended)` — Return
  normalized JSON and quality results; `Normalized JSON` — Return the schema
  only; `Quality report` — Emphasize inheritance and reference ambiguity.

### A.11 `parsing-srx-configs`

- `srxp_goal`; header `Goal`; ask when downstream purpose is absent and affects
  parsing depth; question `What will the parsed result be used for?`; options:
  `Full normalization (Recommended)` — Populate the schema and quality gates;
  `Focused analysis` — Parse relevant sections only; `Downstream task` —
  Prepare for conversion, diff, audit, or compliance.
- `srxp_format`; header `Format`; ask when display-set versus hierarchical
  syntax is ambiguous; question `Which Junos configuration format was
  supplied?`; options: `Auto-detect (Recommended)` — Detect the syntax form;
  `Display set` — Parse line-oriented set commands; `Hierarchical` — Parse
  brace-delimited configuration.
- `srxp_scope`; header `Context`; ask when logical-system scope is unclear;
  question `Which Junos contexts should be included?`; options: `All detected
  (Recommended)` — Parse main and detected logical contexts; `Named context` —
  Limit parsing through Other; `Main only` — Ignore logical systems.
- `srxp_coverage`; header `Coverage`; ask when export completeness is unclear;
  question `How complete is the supplied configuration?`; options: `Full config
  (Recommended)` — Treat it as complete; `Partial excerpt` — Mark missing
  groups and policy unknown; `Unsure` — Detect unresolved inheritance.
- `srxp_output`; header `Output`; ask when output form is absent; question `What
  output should be returned?`; options: `JSON and gates (Recommended)` — Return
  normalized JSON and quality results; `Normalized JSON` — Return the schema
  only; `Quality report` — Emphasize groups, references, and unsupported syntax.

### A.12 `pci-ngfw-compliance`

- `pci_version`; header `PCI Version`; ask when the governing PCI version is
  absent; question `Which PCI DSS version should govern the assessment?`;
  options: `PCI DSS 4.0.1 (Recommended)` — Use PCI DSS 4.0.1; `Specified
  version` — Use a version supplied through Other; `Custom overlay` — Include
  QSA or customer interpretations.
- `pci_stage`; header `Assess Type`; ask when assessment type is absent;
  question `What kind of PCI assessment is this?`; options: `Readiness review
  (Recommended)` — Identify gaps before formal assessment; `ROC support` —
  Organize QSA evidence; `SAQ support` — Tailor evidence to self-assessment.
- `pci_scope`; header `CDE Scope`; ask when the CDE boundary is unclear;
  question `How mature is the CDE boundary?`; options: `Defined CDE
  (Recommended)` — Use identified account-data and connected systems; `Draft
  CDE` — Validate proposed scope; `Unknown CDE` — Begin with data-flow
  discovery.
- `pci_segment`; header `Segmentation`; ask when segmentation reliance is
  unclear; question `Is network segmentation relied upon for scope reduction?`;
  options: `Scope reduction (Recommended)` — Test segmentation design and
  evidence; `Not relied upon` — Treat connected networks as in scope; `Unknown`
  — Identify evidence needed to decide.
- `pci_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `What evidence is available?`; options: `Config plus records
  (Recommended)` — Include configuration, reviews, logs, scans, and records;
  `Configuration only` — Mark procedural gaps; `Evidence request` — Produce
  required artifacts and sampling.
- `pci_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable is needed?`; options: `Requirement matrix (Recommended)` — Map
  evidence, gaps, and remediation; `Segmentation report` — Emphasize CDE
  isolation; `Executive brief` — Emphasize scope risk and top actions.

### A.13 `sd-onprem-proxmox-deploy`

- `sd_stage`; header `Stage`; ask when deployment stage is absent; question
  `What stage is the deployment in?`; options: `Plan or dry-run (Recommended)`
  — Validate prerequisites and produce a plan; `Fresh deployment` — Prepare
  candidate commands; `Troubleshooting` — Diagnose an existing deployment.
- `sd_release`; header `Release`; ask when exact SD On-Prem release is absent;
  question `Which Security Director On-Prem release is being deployed?`;
  options: `Verified release (Recommended)` — Use the exact release and guide;
  `Different release` — Supply the release through Other; `Unknown release` —
  Identify media and documentation first.
- `sd_media`; header `Artifacts`; ask when media presence or integrity is
  unclear; question `Are the required release artifacts available and
  verified?`; options: `Both verified (Recommended)` — Disk image and bundle
  checksums are valid; `One missing` — Identify the missing artifact;
  `Unverified` — Stop and verify integrity.
- `sd_size`; header `Sizing`; ask when appliance flavor is absent; question
  `Which supported appliance size should be used?`; options: `Smallest fitting
  (Recommended)` — Select the lowest flavor meeting measured requirements;
  `Known flavor` — Use a flavor supplied through Other; `Need sizing` — Collect
  device, log, retention, and growth requirements.
- `sd_proxmox`; header `Proxmox`; ask when VM placement values are incomplete;
  question `Are the Proxmox placement values known?`; options: `Values ready
  (Recommended)` — VMID, node, storage, bridge, and resources are known; `Need
  selection` — Inspect capacity read-only; `Existing VM` — Validate an existing
  VM.
- `sd_network`; header `Network`; ask when IP, route, or internal CIDR values are
  incomplete; question `Is the complete IP and routing plan available?`;
  options: `Plan ready (Recommended)` — Required addresses, gateway, and
  internal CIDR are defined; `Partial plan` — Identify missing values; `Need
  design` — Produce a connectivity worksheet.
- `sd_services`; header `DNS and NTP`; ask when supporting service reachability
  is unverified; question `Have supporting services been validated?`; options:
  `Both verified (Recommended)` — DNS and NTP tests pass; `Need tests` — Provide
  safe validation commands; `Not ready` — Treat service readiness as a blocker.
- `sd_transfer`; header `Transfer`; ask when bundle delivery method is absent;
  question `How will the installer bundle reach the appliance?`; options:
  `Approved HTTPS (Recommended)` — Use controlled HTTPS and checksums; `SCP
  transfer` — Use approved SCP without exposing credentials; `Existing method`
  — Validate the supplied mechanism.
- `sd_secrets`; header `Secrets`; ask when secret delivery is needed for a later
  step; question `How will deployment secrets be supplied?`; options:
  `Interactive entry (Recommended)` — Enter secrets at a trusted console;
  `Secret manager` — Use an approved delivery workflow; `Supply later` — Use
  placeholders and stop before secret-dependent execution.
- `sd_onboard`; header `Onboarding`; ask when post-deployment scope is absent;
  question `How far should the runbook go after deployment?`; options: `Health
  validation (Recommended)` — Validate the platform without production
  onboarding; `Device onboarding` — Include approved device connectivity;
  `Full operations` — Include logging, licensing, backup, and monitoring.

### A.14 `soc2-ngfw-compliance`

- `soc2_type`; header `Report Type`; ask when engagement type is absent;
  question `What SOC 2 engagement is being supported?`; options: `Readiness
  review (Recommended)` — Identify gaps before examination; `Type I` — Assess a
  point in time; `Type II` — Assess operation over a period.
- `soc2_tsc`; header `TSC Scope`; ask when Trust Services categories are absent;
  question `Which Trust Services Criteria categories apply?`; options:
  `Security only (Recommended)` — Assess the Common Criteria; `Security plus
  A/C` — Include availability or confidentiality; `Custom scope` — Use
  categories supplied through Other.
- `soc2_period`; header `Period`; ask when evidence period is absent; question
  `What evidence period should be used?`; options: `Defined period
  (Recommended)` — Use dated evidence for the stated period; `Point in time` —
  Avoid operating-period conclusions; `Not established` — Identify retention
  and sampling needs.
- `soc2_system`; header `System Docs`; ask when system description or control
  matrix availability is unclear; question `What system-description and
  control-matrix evidence is available?`; options: `Both available
  (Recommended)` — Use both current documents; `Partial documents` — Flag
  missing ownership; `None available` — Produce discovery questions.
- `soc2_vendor`; header `Providers`; ask when subservice organization treatment
  is unclear; question `How are subservice organizations treated?`; options:
  `Carve-out method (Recommended)` — Identify complementary controls; `Inclusive
  method` — Include provider evidence; `Unknown method` — Flag the governance
  decision.
- `soc2_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable should be emphasized?`; options: `Control matrix (Recommended)` —
  Provide criteria mapping, evidence, gaps, and remediation; `Evidence request`
  — Emphasize period artifacts and samples; `Management brief` — Summarize
  exceptions and top actions.

### A.15 `srx-advpn`

- `advpn_task`; header `Task`; ask when the requested activity is absent;
  question `What should this ADVPN run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a read-only architecture and candidate
  configuration; `Troubleshoot` — Diagnose shortcut or forwarding problems;
  `Migration` — Plan transition from static or hub-only IPsec.
- `advpn_release`; header `Platform`; ask when model or release is absent and
  affects support; question `Are the SRX models and Junos releases known?`;
  options: `Exact details (Recommended)` — Apply model- and release-specific
  limits; `Infer outputs` — Infer cautiously from supplied evidence; `Unknown`
  — Produce discovery checks first.
- `advpn_topo`; header `Topology`; ask when site, addressing, NAT, or HA
  topology is incomplete; question `Is the hub, spoke, addressing, and NAT
  topology complete?`; options: `Complete map (Recommended)` — Use supplied
  sites, addresses, LANs, NAT, and HA roles; `Partial map` — Mark unresolved
  elements; `Need design` — Build a topology worksheet.
- `advpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `What authentication design is available?`; options: `PKI available
  (Recommended)` — Use certificate authentication; `PKI planned` — Include
  enrollment prerequisites; `PSK only` — Report ADVPN limitations.
- `advpn_route`; header `Routing`; ask when overlay routing is absent; question
  `Which overlay routing model should be used?`; options: `OSPF P2MP
  (Recommended)` — Use the documented point-to-multipoint model; `Existing
  routing` — Preserve and assess the supplied protocol; `Need design` — Compare
  supported models.
- `advpn_traffic`; header `Traffic`; ask when branch path requirements are
  unclear; question `What branch traffic behavior is required?`; options:
  `Shortcuts plus hub (Recommended)` — Support hub paths and spoke shortcuts;
  `Shortcuts only` — Focus on spoke-to-spoke formation; `Central backhaul` —
  Re-evaluate AutoVPN fit.
- `advpn_gateway`; header `Gateway`; ask when release-specific gateway form is
  unresolved; question `How should release-specific gateway limitations be
  handled?`; options: `Conservative static (Recommended)` — Use the documented
  safe form; `Dynamic gateway` — Use only with confirmed support; `Validate
  first` — Run read-only checks before selecting syntax.
- `advpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `What troubleshooting evidence is available?`;
  options: `Config and SAs (Recommended)` — Use redacted configuration, SAs,
  routes, and flow evidence; `Configuration only` — Limit runtime conclusions;
  `Error output` — Begin with errors and request targeted evidence.

### A.16 `srx-autovpn-full-tunnel`

- `autovpn_task`; header `Task`; ask when requested activity is absent; question
  `What should this AutoVPN run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a full-tunnel design; `Troubleshoot` —
  Diagnose tunnel, routing, or backhaul problems; `Migration` — Plan transition
  from static or split-tunnel VPN.
- `autovpn_release`; header `Platform`; ask when model or release is absent and
  affects support; question `Are the SRX models and Junos releases known?`;
  options: `Exact details (Recommended)` — Apply release-specific behavior;
  `Infer outputs` — Infer cautiously from supplied evidence; `Unknown` —
  Produce discovery checks first.
- `autovpn_traffic`; header `Traffic`; ask when backhaul behavior is unclear;
  question `What traffic model is required?`; options: `Full backhaul
  (Recommended)` — Send spoke traffic through the hub; `Split tunnel` —
  Preserve specified local paths; `Compare models` — Evaluate both designs.
- `autovpn_auth`; header `Auth`; ask when peer authentication is absent;
  question `What peer authentication model should be used?`; options: `PKI
  zero-touch (Recommended)` — Use certificates and scalable group identity;
  `Unique PSKs` — Use a distinct secret per spoke; `Existing legacy` — Assess a
  shared-secret design and document risk.
- `autovpn_lans`; header `LAN Prefixes`; ask when spoke prefix allocation is
  incomplete; question `How are spoke LAN prefixes allocated?`; options:
  `Summarizable (Recommended)` — Use non-overlapping scalable ranges;
  `Discontiguous` — Generate explicit handling and capacity caveats;
  `Overlapping` — Stop and resolve overlap.
- `autovpn_nat`; header `Underlay`; ask when NAT between spokes and hub is
  unclear; question `What NAT exists between spokes and the hub?`; options:
  `Known NAT path (Recommended)` — Apply NAT-T to a documented path; `No NAT` —
  Use directly reachable peers; `Unknown or double` — Require NAT behavior
  tests.
- `autovpn_route`; header `Routing`; ask when management and default-route
  separation is unclear; question `How is hub management and default routing
  separated?`; options: `Separate management (Recommended)` — Keep management
  independent of tunnel defaults; `Competing defaults` — Analyze recursion;
  `Unknown state` — Collect routing evidence.
- `autovpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `What troubleshooting evidence is available?`;
  options: `Config and SAs (Recommended)` — Use configuration, SAs, routes,
  sessions, and logs; `Configuration only` — Limit findings to static design;
  `Error output` — Begin with failures and collect targeted evidence.

### A.17 `srx-dynamic-ip-feed`

- `dif_task`; header `Task`; ask when requested activity is absent; question
  `What should this dynamic-feed run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a safe integration; `Troubleshoot` —
  Diagnose download, parsing, mapping, or policy behavior; `Migration` —
  Convert an existing feed workflow.
- `dif_release`; header `Platform`; ask when model or release is absent and
  affects capability; question `Are the SRX model and Junos release known?`;
  options: `Exact details (Recommended)` — Apply release-specific capabilities;
  `Infer outputs` — Infer cautiously from evidence; `Unknown` — Produce
  prerequisite checks.
- `dif_source`; header `Feed Source`; ask when feed artifacts or publishing
  design is incomplete; question `What feed artifacts are available?`; options:
  `URL and archive (Recommended)` — Use documented URLs and archive layout;
  `Existing failing feed` — Diagnose the supplied implementation; `Need feed
  design` — Define structure and publishing first.
- `dif_tls`; header `TLS`; ask when publisher trust method is absent; question
  `How should the HTTPS publisher be authenticated?`; options: `Trusted CA
  (Recommended)` — Validate an approved CA chain; `Private CA` — Include
  controlled CA import and rotation; `Lab unverified` — Classify bypass as
  non-production.
- `dif_auth`; header `Feed Auth`; ask when application authentication is
  required but unspecified; question `What application authentication is
  required?`; options: `No extra auth (Recommended)` — Rely on authenticated
  TLS and network controls; `Mutual TLS` — Use client certificates via approved
  secret delivery; `Basic auth` — Protect credentials outside chat.
- `dif_route`; header `Routing`; ask when feed-server routing context is absent;
  question `Which routing context reaches the feed server?`; options: `Default
  instance (Recommended)` — Use default routing after reachability validation;
  `Named instance` — Use the specified instance and source; `Unknown` — Collect
  route, DNS, and connection evidence.
- `dif_effect`; header `Policy Use`; ask when feed enforcement intent is absent;
  question `How will feed entries affect security policy?`; options: `Blocklist
  deny (Recommended)` — Deny new matching sessions with logging; `Allowlist
  permit` — Permit members within constrained policy; `Both uses` — Define
  separate objects and precedence.
- `dif_session`; header `Sessions`; ask when existing-session behavior matters
  and is absent; question `What should happen to existing sessions when the feed
  changes?`; options: `New sessions only (Recommended)` — Apply changes to new
  evaluations; `Clear matches` — Include separately approved targeted clearing;
  `Need decision` — Explain enforcement timing first.
- `dif_poll`; header `Polling`; ask when refresh requirements are absent;
  question `What refresh behavior is required?`; options: `Standard interval
  (Recommended)` — Use a conservative supported interval; `Faster updates` —
  Validate load and reliability; `Custom cadence` — Use a value supplied
  through Other.

### A.18 `srx-ipsec-hub-spoke`

- `hsvpn_task`; header `Task`; ask when requested activity is absent; question
  `What should this hub-and-spoke run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a static route-based design; `Troubleshoot`
  — Diagnose IKE, IPsec, routing, or policy; `Migration` — Plan transition from
  policy-based or shared-tunnel VPN.
- `hsvpn_release`; header `Platform`; ask when model or release is absent and
  affects syntax; question `Are all SRX models and Junos releases known?`;
  options: `Exact details (Recommended)` — Apply platform-specific syntax;
  `Infer outputs` — Infer cautiously from evidence; `Unknown` — Produce
  discovery checks.
- `hsvpn_topo`; header `Topology`; ask when peer, prefix, NAT, HA, or st0 data is
  incomplete; question `Is the complete hub-and-spoke topology available?`;
  options: `Complete map (Recommended)` — Use supplied peers, LANs, WANs, NAT,
  HA, and st0 allocation; `Partial map` — Mark unresolved selectors and routes;
  `Need design` — Create a topology worksheet.
- `hsvpn_traffic`; header `Traffic`; ask when spoke path requirements are
  unclear; question `How should spoke traffic be routed?`; options: `Central
  backhaul (Recommended)` — Route required traffic through the hub; `Split or
  local` — Preserve specified local paths; `Compare models` — Evaluate both.
- `hsvpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `What peer authentication should be used?`; options: `Certificates
  (Recommended)` — Use PKI where available; `Unique PSKs` — Use distinct
  secrets via approved delivery; `Shared lab PSK` — Classify as lab-only.
- `hsvpn_route`; header `Routing`; ask when management reachability and tunnel
  defaults may conflict; question `Is management reachability protected from
  tunnel defaults?`; options: `Separate route path (Recommended)` — Keep
  management and peer paths independent; `Competing defaults` — Analyze
  recursion; `Unknown state` — Collect route evidence.
- `hsvpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `What troubleshooting evidence is available?`;
  options: `Config and SAs (Recommended)` — Use configuration, SAs, routes,
  sessions, and logs; `Configuration only` — Limit runtime conclusions; `Error
  output` — Begin with failures and request targeted evidence.

### A.19 `srx-mnha`

- `mnha_task`; header `Task`; ask when requested activity is absent; question
  `What should this MNHA run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess an architecture; `Troubleshoot` — Diagnose
  synchronization, forwarding, or failover; `Migration` — Plan migration from
  chassis cluster or standalone SRX.
- `mnha_release`; header `Platform`; ask when node models or releases are absent;
  question `Are every node model and Junos release known?`; options: `Exact
  details (Recommended)` — Apply release-specific syntax; `Infer outputs` —
  Infer cautiously from evidence; `Unknown` — Avoid implementation-ready
  configuration.
- `mnha_mode`; header `MNHA Mode`; ask when forwarding mode is absent; question
  `Which MNHA forwarding model is required?`; options: `Routed mode
  (Recommended)` — Use explicit routing and SRGs; `Gateway mode` — Provide
  default-gateway service behavior; `Hybrid mode` — Combine only for documented
  requirements.
- `mnha_migrate`; header `Migration`; ask when starting state is unclear;
  question `What is the starting state?`; options: `New deployment
  (Recommended)` — Design without legacy cluster constraints; `Chassis cluster`
  — Include staged migration and rollback; `Existing MNHA` — Audit or repair.
- `mnha_topo`; header `Topology`; ask when inter-node topology is incomplete;
  question `What inter-node topology exists?`; options: `Symmetric links
  (Recommended)` — Use matched interfaces and direct links; `Asymmetric links`
  — Include inter-cluster data paths; `Unknown topology` — Collect diagrams.
- `mnha_service`; header `Services`; ask when stateful service scope is absent;
  question `Which stateful services must survive failover?`; options: `Firewall
  and NAT (Recommended)` — Preserve core session and NAT behavior; `IPsec
  services` — Include tunnel ownership and rekey; `Advanced services` — Include
  DHCP or security services.
- `mnha_route`; header `Routing`; ask when upstream failover signaling is
  absent; question `How will upstream failover be signaled?`; options: `Dynamic
  routing (Recommended)` — Use supported routing and fast detection; `Static or
  VIP` — Use explicit tracking and ownership; `Need design` — Compare
  convergence models.
- `mnha_objective`; header `Objectives`; ask when resilience priority is
  absent; question `What resilience objective matters most?`; options:
  `Stateful failover (Recommended)` — Prioritize session continuity; `Fast
  routing` — Prioritize convergence; `Active-active use` — Validate placement
  and symmetry.
- `mnha_test`; header `Test Plan`; ask when validation depth is absent; question
  `What validation depth is required?`; options: `Full failure matrix
  (Recommended)` — Test node, link, service, routing, and recovery; `Named
  failures` — Test specified cases; `One failure` — Reproduce the reported case
  safely.

### A.20 `srx-mpls-in-flow`

- `mpls_task`; header `Task`; ask when requested activity is absent; question
  `What should this MPLS-in-flow run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a secure MPLS design; `Troubleshoot` —
  Diagnose label, VRF, routing, or policy failures; `Migration` — Plan
  conversion to flow mode.
- `mpls_release`; header `Platform`; ask when model or release is absent;
  question `Are the SRX model and Junos release known?`; options: `Exact
  supported (Recommended)` — Verify minimum supported release; `Infer outputs`
  — Infer cautiously from evidence; `Unknown` — Treat support as a blocker.
- `mpls_role`; header `Device Role`; ask when PE, CPE, or transit role is
  unclear; question `What role does the SRX perform?`; options: `Secure PE or
  CPE (Recommended)` — Apply security at the VPN edge; `Transit P role` —
  Re-evaluate requested security function; `Existing mixed role` — Document
  current responsibilities.
- `mpls_family`; header `IP Family`; ask when required address families are
  absent; question `Which address families are required?`; options: `IPv4 and
  VPNv4 (Recommended)` — Design the common IPv4 L3VPN case; `Dual stack` —
  Include IPv6 and VPNv6; `IPv6 focused` — Limit design to IPv6.
- `mpls_signal`; header `Signaling`; ask when label signaling is absent;
  question `Which label and transport protocols are used?`; options: `Existing
  protocols (Recommended)` — Preserve documented LDP, RSVP, or BGP label
  design; `LDP design` — Build an LDP transport; `Need selection` — Compare
  supported options.
- `mpls_vrf`; header `VRF Scope`; ask when VRF or route-target inventory is
  incomplete; question `Is the VRF and route-target inventory complete?`;
  options: `Complete inventory (Recommended)` — Use supplied VRFs, RDs, RTs,
  interfaces, and prefixes; `Partial inventory` — Mark import/export unresolved;
  `Need design` — Create a service matrix.
- `mpls_policy`; header `Policy Model`; ask when VRF-aware policy model is
  absent; question `How should security policy be organized?`; options: `VRF
  policy groups (Recommended)` — Use the scalable supported model; `VRF to
  zone` — Preserve existing zone design where supported; `Need validation` —
  Select after release checks.
- `mpls_service`; header `Services`; ask when inspection services are absent;
  question `Which security services must apply to MPLS traffic?`; options: `Base
  policy (Recommended)` — Start with stateful policy and logging; `NAT or App-ID`
  — Include explicitly required controls; `Full inspection` — Include IPS or
  advanced services with capacity validation.

### A.21 `srx-nat`

- `nat_task`; header `Task`; ask when requested activity is absent; question
  `What should this NAT run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a NAT design; `Troubleshoot` — Diagnose
  translation, routing, proxy, or session failures; `Migration` — Convert NAT
  behavior from another platform.
- `nat_release`; header `Platform`; ask when model or release is absent and
  affects feature support; question `Are the SRX model and Junos release
  known?`; options: `Exact details (Recommended)` — Apply supported features and
  syntax; `Infer outputs` — Infer cautiously from evidence; `Unknown` — Avoid
  release-dependent claims.
- `nat_family`; header `NAT Type`; ask when translation family is absent;
  question `Which NAT behavior is required?`; options: `Source NAT
  (Recommended)` — Design outbound or inter-zone source translation;
  `Destination or static` — Design inbound or bidirectional mapping; `Advanced
  NAT` — Cover NAT64, CGN, persistent NAT, or hairpinning.
- `nat_tuple`; header `Traffic`; ask when pre- or post-translation tuple is
  incomplete; question `Is the pre- and post-translation traffic tuple
  complete?`; options: `Complete tuple (Recommended)` — Use source,
  destination, service, zones, and translated values; `Partial tuple` — Mark
  unresolved fields; `Need discovery` — Build a flow worksheet.
- `nat_context`; header `Context`; ask when zone, interface, or routing-instance
  classification is unclear; question `How is traffic classified?`; options:
  `Zones and interfaces (Recommended)` — Use explicit ingress and egress;
  `Routing instances` — Include tenant-aware translation; `Both contexts` —
  Model all classification inputs.
- `nat_reach`; header `Reachability`; ask when translated-address reachability
  is unclear; question `How will translated addresses be reachable?`; options:
  `Routed prefix (Recommended)` — Use explicit routing; `Proxy ARP or NDP` —
  Include neighbor-proxy behavior; `Unknown` — Validate routing and adjacency.
- `nat_return`; header `Return Path`; ask when traffic symmetry is unclear;
  question `Does return traffic traverse the same SRX?`; options: `Symmetric
  return (Recommended)` — Preserve stateful return through the translator;
  `Asymmetric return` — Redesign or validate session risk; `Unknown path` —
  Collect routing and flow evidence.
- `nat_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `What troubleshooting evidence is available?`;
  options: `Config and sessions (Recommended)` — Use NAT config, routes,
  counters, sessions, and logs; `Configuration only` — Limit conclusions to
  static logic; `Error or trace` — Begin with observed failure evidence.

### A.22 `srx-policy`

- `policy_task`; header `Task`; ask when requested activity is absent; question
  `What should this policy run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess security-policy intent; `Troubleshoot` —
  Diagnose lookup, session, or application failures; `Migration` — Convert from
  another platform.
- `policy_release`; header `Platform`; ask when model, release, or licensing is
  absent and affects features; question `Are the SRX model, Junos release, and
  licenses known?`; options: `Exact details (Recommended)` — Apply supported
  policy and services; `Read-only check` — Determine capabilities from approved
  evidence; `Unknown` — Mark feature conclusions unresolved.
- `policy_model`; header `Policy Model`; ask when architecture is absent;
  question `Which policy architecture should be used?`; options: `Global policy
  (Recommended)` — Use global policy where it safely reduces duplication;
  `Preserve zone-pair` — Retain explicit zone organization; `Review existing` —
  Assess the supplied mix first.
- `policy_flow`; header `Traffic`; ask when traffic intent is incomplete;
  question `How complete are the traffic requirements?`; options: `Complete
  intent (Recommended)` — Use source, destination, application, service, zones,
  and purpose; `Partial intent` — Produce discovery gaps; `Migration source` —
  Derive intent from normalized source policy.
- `policy_nat`; header `NAT Context`; ask when NAT involvement is unclear;
  question `Is NAT involved in the policy flow?`; options: `No NAT
  (Recommended)` — Evaluate original addresses and routing; `NAT involved` —
  Model the correct pre/post-NAT tuple; `Unknown` — Build a packet-flow trace.
- `policy_service`; header `Services`; ask when inspection services are absent;
  question `Which inspection services are required?`; options: `Base policy
  (Recommended)` — Start with least privilege and logging; `App-ID or AppFW` —
  Include application enforcement; `Advanced security` — Include licensed UTM,
  NGFW, ATP, or IPS.
- `policy_ip`; header `IP Family`; ask when address-family scope is absent;
  question `Which traffic families must be covered?`; options: `IPv4 and IPv6
  (Recommended)` — Evaluate controls for both; `IPv4 only` — Report IPv6
  exposure; `Special traffic` — Include multicast, discovery, or control-plane
  needs.
- `policy_session`; header `Sessions`; ask when existing-session behavior
  matters and is absent; question `How should existing sessions be treated
  after a policy change?`; options: `New sessions only (Recommended)` —
  Validate newly established sessions; `Existing sessions matter` — Include
  separately approved targeted handling; `Maintenance window` — Build
  verification and rollback around the change.
