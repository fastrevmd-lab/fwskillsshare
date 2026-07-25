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
    python3 scripts/check-runtime-intake-safety.py
    python3 scripts/test-runtime-intake-safety.py
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
in `scripts/test-runtime-intake-validator.py`. Reject duplicate JSON object
members; unknown keys at every neutral JSON level; native-only question keys
such as `multiSelect`; blank or unstripped `ask_when`, `header`, `question`,
`label`, and `description`; more than one question sentence or question mark;
and more than one sentence-ending boundary in a description. Ignore an
initialism-ending period only when the next non-space token begins with a
lowercase letter or digit; conservatively count it as a boundary before an
uppercase token.

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
option is always the recommended safe default. When the triggering fact is
unresolved, the recommended option must not assert that the missing fact is
known, complete, available, valid, or verified. Rewrite a factual prompt as an
action or workflow decision when necessary so the safe discovery or
verification option directly answers it.

Each two- or three-option set is a mutually exclusive single-select choice
along one material axis. Do not mix evidence availability with collection
method, current state with requested workflow, or address family with special
traffic. Use the free-text `Other` path for exact values. End every serialized
description with a period.

**Task 28 final-review audit:** `scripts/check-runtime-intake-safety.py` parses
all Appendix A rows and all package JSON catalogs. It rejects duplicate
Appendix sections, incorrect A.1 through A.22 number/name pairings, duplicate
package JSON members, and noncanonical same-line tabs or doubled spaces in
Appendix question fields. It requires exact per-skill question-object equality
and locks all 22 complete catalog contents and question order with canonical
SHA-256 digests, in addition to the audited 62 safe first labels and 18
single-axis option tuples.

The optional skill argument limits equality, digest, safe-default, and
option-tuple assertions to the selected package, while every focused run still
parses all 22 plan and package catalogs and resolves all manifest keys.
Focused output must distinguish those whole-corpus checks from selected
assertion counts. `scripts/test-runtime-intake-safety.py`, run immediately
after the checker in `just lint`, uses temporary files and the real parser to
cover the ten audited semantic IDs, duplicate and numbering failures,
same-line question/label/description whitespace, focused output counts,
complete digest coverage, and synchronized content and order mutation.

Update each Appendix row and its package JSON object together, then require
both focused validators to pass before moving to the next independently
installable skill.

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
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configurations, logs, reviews,
  tickets, and operating records before grading; `Assess supplied artifacts` —
  Assess only supplied evidence and disclose coverage gaps; `Build evidence
  request` — List required evidence without grading implementation.
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
  unknown; question `How should an uncertain CUI boundary be handled?`;
  options: `Map boundary first (Recommended)` — Identify CUI assets, flows, and
  protection dependencies before assessing; `Assess supplied boundary` — Use a
  supplied final boundary and disclose unverified assumptions; `Validate
  supplied draft` — Test a supplied draft and mark unresolved scope.
- `cmmc_assets`; header `Assets`; ask when asset classes in scope are unclear;
  question `Which assets should be assessed?`; options: `CUI and SPA
  (Recommended)` — Include CUI assets and security protection assets; `Named
  controls` — Limit review to specified requirements or devices; `Full
  environment` — Include adjacent systems that affect CUI protection.
- `cmmc_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configurations, logs,
  approvals, reviews, and procedures before grading; `Assess supplied
  artifacts` — Assess only supplied evidence and disclose practice gaps;
  `Build evidence request` — List required evidence without grading
  implementation.
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
  availability is unclear; question `How should uncertain operational evidence
  be handled?`; options: `Inventory evidence (Recommended)` — Identify
  available configuration and telemetry coverage before analysis; `Use
  supplied artifacts` — Analyze only supplied artifacts and label runtime
  dependencies; `Approved live collection` — Collect targeted read-only device
  evidence with approval.
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
  syntax or support and is absent; question `How should missing target model or
  release details be handled?`; options: `Discover first (Recommended)` —
  Identify the exact target model and release before conversion; `Exact details
  supplied` — Apply capabilities for the supplied target; `Infer
  conservatively` — Limit output to family-safe syntax and disclose
  uncertainty.
- `convert_scope`; header `Scope`; ask when conversion components are absent;
  question `What should be converted?`; options: `Full migration
  (Recommended)` — Convert all supported components; `Policy and NAT` — Limit
  work to objects, policy, and NAT; `Named sections` — Convert components named
  through Other.
- `convert_base`; header `Baseline`; ask when existing target state is unknown;
  question `How should uncertain target baseline state be handled?`; options:
  `Inspect target first (Recommended)` — Determine whether target state exists
  before generating configuration; `Use supplied clean target` — Generate for a
  supplied empty target baseline; `Use supplied merge target` — Account for a
  supplied existing target configuration.
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
  question `How should ambiguous input roles be resolved?`; options: `Establish
  baseline first (Recommended)` — Determine the authoritative baseline and
  comparison direction before classifying changes; `Use supplied A-to-B` —
  Treat supplied A as baseline and B as new; `Compare as peers` — Treat inputs
  as unordered and report symmetric differences.
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
  absent; question `How should an unspecified HIPAA responsibility be
  handled?`; options: `Confirm responsibility (Recommended)` — Establish the
  organization's HIPAA responsibility before assigning safeguards; `Use
  supplied single-role scope` — Use one exact supplied covered-entity or
  business-associate role from Other; `Use supplied combined scope` — Assess the
  supplied combined covered-entity and business-associate scope.
- `hipaa_goal`; header `Goal`; ask when review purpose is absent; question `What
  is the purpose of this HIPAA review?`; options: `Risk assessment
  (Recommended)` — Identify ePHI risks and remediation; `Audit evidence` —
  Organize audit artifacts; `Design review` — Review architecture without
  operational claims.
- `hipaa_scope`; header `ePHI Scope`; ask when the ePHI boundary is unclear;
  question `How should an uncertain ePHI boundary be handled?`; options: `Map
  ePHI scope (Recommended)` — Identify systems, flows, users, and parties before
  assessing; `Assess supplied boundary` — Use a supplied final boundary and
  disclose unverified assumptions; `Validate supplied draft` — Test a supplied
  preliminary boundary and mark unresolved scope.
- `hipaa_vendor`; header `Vendors`; ask when third-party ePHI paths are unclear;
  question `How should third-party ePHI paths be handled?`; options: `Include
  all paths (Recommended)` — Assess vendors, remote access, cloud, and
  transmission; `Named vendors` — Limit review to identified parties;
  `Technical only` — Exclude contract conclusions and note BAA needs.
- `hipaa_evidence`; header `Evidence`; ask when evidence period is unclear;
  question `How should an uncertain evidence period be handled?`; options:
  `Inventory evidence (Recommended)` — Identify dated records and current
  configuration before making period claims; `Assess current state` — Limit
  conclusions to present technical state; `Build evidence request` — List
  required dated evidence without grading effectiveness.
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
  question `How should an uncertain ISMS boundary be handled?`; options: `Map
  ISMS scope (Recommended)` — Identify organizational and system boundaries
  before assessing; `Assess supplied boundary` — Use a supplied final boundary
  and disclose unverified assumptions; `Validate supplied draft` — Test a
  supplied draft and mark unresolved scope.
- `iso_soa`; header `SoA`; ask when Statement of Applicability evidence is
  absent; question `How should absent Statement of Applicability evidence be
  handled?`; options: `Inventory SoA first (Recommended)` — Determine whether
  current, draft, or supporting applicability records exist; `Use supplied SoA`
  — Apply the supplied organizational decisions and disclose evidence gaps;
  `Use generic mapping` — Map Annex A without organizational applicability
  claims.
- `iso_basis`; header `Basis`; ask when control applicability basis is unclear;
  question `How should an uncertain control-applicability basis be handled?`;
  options: `Confirm basis first (Recommended)` — Establish the governing SoA,
  risk treatment plan, or overlay before conclusions; `Use supplied SoA basis`
  — Follow the supplied organizational applicability decisions; `Use Annex A
  baseline` — Map Annex A without organizational applicability claims.
- `iso_period`; header `Evidence`; ask when operating evidence period is
  unclear; question `How should an uncertain operating-evidence period be
  handled?`; options: `Confirm period first (Recommended)` — Establish the
  assessment period and available dated samples before effectiveness claims;
  `Assess current state` — Limit conclusions to present technical state;
  `Assess control design` — Evaluate intended design without operating
  effectiveness claims.
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
  question `How should uncertain Cisco export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected sections and
  truncation before making completeness claims; `Full artifact supplied` —
  Treat the supplied running configuration as complete; `Partial artifact
  supplied` — Mark omitted sections unknown.
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
  question `How should uncertain FortiGate export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected tables, defaults, and
  truncation before making completeness claims; `Full artifact supplied` —
  Treat the supplied FortiGate backup as complete; `Partial artifact supplied`
  — Mark omitted tables and defaults unknown.
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
  question `How should uncertain PAN-OS export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected hierarchy and
  references before making completeness claims; `Full artifact supplied` —
  Treat the supplied PAN-OS configuration as complete; `Partial artifact
  supplied` — Mark omitted hierarchy and references unknown.
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
  question `How should uncertain Junos export completeness be handled?`;
  options: `Verify first (Recommended)` — Check expected groups, inheritance,
  and sections before making completeness claims; `Full artifact supplied` —
  Treat the supplied Junos configuration as complete; `Partial artifact
  supplied` — Mark missing groups, inheritance, and policy unknown.
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
  question `How should an uncertain CDE boundary be handled?`; options: `Map
  CDE scope (Recommended)` — Identify account-data systems, connected systems,
  and flows before assessing; `Assess supplied boundary` — Use a supplied final
  boundary and disclose unverified assumptions; `Validate supplied draft` —
  Test a supplied preliminary boundary and mark unresolved scope.
- `pci_segment`; header `Segmentation`; ask when segmentation reliance is
  unclear; question `How should uncertain segmentation reliance be handled?`;
  options: `Verify segmentation (Recommended)` — Test segmentation design and
  evidence before reducing scope; `No scope reduction` — Treat connected
  networks as in scope without relying on segmentation; `Use verified
  segmentation` — Apply a supplied validated segmentation boundary.
- `pci_evidence`; header `Evidence`; ask when evidence completeness is unclear;
  question `How should uncertain evidence completeness be handled?`; options:
  `Inventory evidence (Recommended)` — Identify configuration, reviews, logs,
  scans, and records before grading; `Assess supplied artifacts` — Assess only
  supplied evidence and disclose procedural gaps; `Build evidence request` —
  List required artifacts and samples without grading implementation.
- `pci_output`; header `Output`; ask when deliverable is absent; question `What
  deliverable is needed?`; options: `Requirement matrix (Recommended)` — Map
  evidence, gaps, and remediation; `Segmentation report` — Emphasize CDE
  isolation; `Executive brief` — Emphasize scope risk and top actions.

### A.13 `sd-onprem-proxmox-deploy`

- `sd_stage`; header `Stage`; ask when deployment stage is absent; question
  `How should an unspecified deployment stage be resolved?`; options: `Inspect
  stage first (Recommended)` — Inspect deployment evidence to distinguish
  planning, fresh deployment, and troubleshooting before choosing a workflow;
  `Plan supplied fresh deployment` — Plan from a supplied fresh-deployment stage
  without executing changes; `Troubleshoot supplied deployment` — Diagnose a
  supplied existing deployment without assuming a fresh state.
- `sd_release`; header `Release`; ask when exact SD On-Prem release is absent;
  question `How should missing Security Director release details be handled?`;
  options: `Discover first (Recommended)` — Identify the exact release and
  matching guide before deployment planning; `Exact details supplied` — Use the
  exact supplied release and matching guide; `Stop pending details` — Do not
  produce release-dependent deployment steps.
- `sd_media`; header `Artifacts`; ask when media presence or integrity is
  unclear; question `How should uncertain release media integrity be handled?`;
  options: `Verify media first (Recommended)` — Check image and bundle presence,
  versions, and checksums before deployment; `Use supplied verified media` —
  Proceed with supplied artifacts and checksum evidence; `Stop pending media`
  — Block deployment until required artifacts are supplied.
- `sd_size`; header `Sizing`; ask when appliance flavor is absent; question
  `Which supported appliance size should be used?`; options: `Smallest fitting
  (Recommended)` — Select the lowest flavor meeting measured requirements;
  `Known flavor` — Use a flavor supplied through Other; `Need sizing` — Collect
  device, log, retention, and growth requirements.
- `sd_proxmox`; header `Proxmox`; ask when VM placement values are incomplete;
  question `How should incomplete Proxmox VM state be resolved?`; options:
  `Inspect state first (Recommended)` — Inspect Proxmox and VM evidence
  read-only before choosing a new-VM or existing-VM workflow; `Plan supplied new
  VM` — Plan with supplied VMID, node, storage, bridge, and resource values for
  a new VM; `Assess supplied existing VM` — Assess a supplied existing VM
  against deployment requirements.
- `sd_network`; header `Network`; ask when IP, route, or internal CIDR values are
  incomplete; question `How should incomplete IP and routing values be
  handled?`; options: `Map network first (Recommended)` — Identify required
  addresses, gateway, routes, and internal CIDR before deployment; `Use supplied
  network plan` — Apply the complete supplied addressing and routing plan;
  `Stop pending values` — Block deployment and list missing network values.
- `sd_services`; header `DNS and NTP`; ask when supporting service reachability
  is unverified; question `How should unverified supporting-service reachability
  be handled?`; options: `Verify services first (Recommended)` — Run safe DNS
  and NTP reachability checks before deployment; `Use supplied test results` —
  Rely on supplied current DNS and NTP validation evidence; `Stop pending
  readiness` — Treat unverified service reachability as a blocker.
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
  `How should an unspecified SOC 2 evidence period be handled?`; options:
  `Confirm period first (Recommended)` — Establish dates and available samples
  before operating-period conclusions; `Assess point in time` — Limit
  conclusions to current control design and state; `Build evidence plan` —
  Identify retention and sampling needs without grading operation.
- `soc2_system`; header `System Docs`; ask when system description or control
  matrix availability is unclear; question `How should incomplete
  system-boundary evidence be handled?`; options: `Map system first
  (Recommended)` — Identify services, infrastructure, people, data, and control
  ownership before grading; `Use supplied documents` — Assess the supplied
  system description and control matrix while disclosing gaps; `Build discovery
  request` — List missing boundary and ownership evidence without grading.
- `soc2_vendor`; header `Providers`; ask when subservice organization treatment
  is unclear; question `How should uncertain subservice-organization treatment
  be handled?`; options: `Inventory vendors first (Recommended)` — Identify
  subservice organizations and per-vendor governance decisions before
  assessment; `Use supplied uniform treatment` — Apply one supplied carve-out or
  inclusive method consistently across all vendors; `Use supplied mixed
  treatment` — Apply supplied per-vendor carve-out and inclusive treatments and
  document each boundary.
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
  affects support; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before support conclusions; `Exact details
  supplied` — Apply model- and release-specific limits; `Infer conservatively`
  — Limit output to evidence-supported design and disclose uncertainty.
- `advpn_topo`; header `Topology`; ask when site, addressing, NAT, or HA
  topology is incomplete; question `How should incomplete ADVPN topology be
  handled?`; options: `Map topology first (Recommended)` — Identify sites,
  addresses, LANs, NAT, and HA roles before design; `Use supplied complete map`
  — Design from a supplied complete topology; `Design from requirements` —
  Build a new topology from supplied site and traffic requirements.
- `advpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `How should unspecified peer authentication be handled?`; options: `Inventory
  authentication (Recommended)` — Identify existing PKI, enrollment, and peer
  identity constraints before design; `Use supplied PKI` — Use the supplied
  certificate authority and enrollment design; `Assess supplied PSK` — Analyze
  the supplied PSK design and report ADVPN limitations.
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
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, and flow evidence before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.16 `srx-autovpn-full-tunnel`

- `autovpn_task`; header `Task`; ask when requested activity is absent; question
  `What should this AutoVPN run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a full-tunnel design; `Troubleshoot` —
  Diagnose tunnel, routing, or backhaul problems; `Migration` — Plan transition
  from static or split-tunnel VPN.
- `autovpn_release`; header `Platform`; ask when model or release is absent and
  affects support; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before support conclusions; `Exact details
  supplied` — Apply release-specific behavior; `Infer conservatively` — Limit
  output to evidence-supported design and disclose uncertainty.
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
  incomplete; question `How should incomplete spoke LAN allocation be
  handled?`; options: `Map LANs first (Recommended)` — Identify every spoke
  prefix and overlap before route design; `Use supplied scalable ranges` — Use
  supplied non-overlapping summarizable prefixes; `Use supplied explicit
  prefixes` — Handle supplied discontiguous prefixes without summarization.
- `autovpn_nat`; header `Underlay`; ask when NAT between spokes and hub is
  unclear; question `How should uncertain underlay NAT be handled?`; options:
  `Trace NAT first (Recommended)` — Test peer reachability and translation
  behavior before tunnel design; `Use supplied NAT path` — Apply NAT-T to the
  supplied documented translation path; `Use supplied no-NAT path` — Use
  supplied directly reachable peer paths.
- `autovpn_route`; header `Routing`; ask when management and default-route
  separation is unclear; question `How should uncertain management-route
  separation be handled?`; options: `Inspect routes first (Recommended)` —
  Trace management, peer, and default paths before route changes; `Use supplied
  separate path` — Preserve a supplied independent management path; `Analyze
  competing defaults` — Evaluate supplied competing defaults for recursion.
- `autovpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, sessions, and logs before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.17 `srx-dynamic-ip-feed`

- `dif_task`; header `Task`; ask when requested activity is absent; question
  `What should this dynamic-feed run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a safe integration; `Troubleshoot` —
  Diagnose download, parsing, mapping, or policy behavior; `Migration` —
  Convert an existing feed workflow.
- `dif_release`; header `Platform`; ask when model or release is absent and
  affects capability; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify the
  exact model and release before capability conclusions; `Exact details
  supplied` — Apply release-specific capabilities; `Infer conservatively` —
  Limit output to evidence-supported design and disclose uncertainty.
- `dif_source`; header `Feed Source`; ask when feed artifacts or publishing
  design is incomplete; question `How should an incomplete feed source be
  handled?`; options: `Inspect source first (Recommended)` — Determine whether
  an existing endpoint, archive, or publishing workflow can be used; `Use
  supplied endpoint` — Integrate the supplied endpoint and archive layout;
  `Design new endpoint` — Define a new supported HTTPS feed and publishing
  workflow.
- `dif_tls`; header `TLS`; ask when publisher trust method is absent; question
  `How should the HTTPS publisher be authenticated?`; options: `Trusted CA
  (Recommended)` — Validate an approved CA chain; `Private CA` — Include
  controlled CA import and rotation; `Lab unverified` — Classify bypass as
  non-production.
- `dif_auth`; header `Feed Auth`; ask when feed authentication method is absent
  or unclear; question `How should uncertain feed authentication be handled?`;
  options: `Verify endpoint first (Recommended)` — Verify endpoint requirements
  before selecting authentication and risk-classify explicit no-extra-auth
  requests supplied through Other; `Use supplied mutual TLS` — Use supplied
  client-certificate requirements through approved secret delivery; `Use
  supplied basic auth` — Use supplied basic-auth requirements while keeping
  credentials outside chat.
- `dif_route`; header `Routing`; ask when feed-server routing context is absent;
  question `How should an unknown feed-server route be handled?`; options:
  `Trace route first (Recommended)` — Collect route, DNS, source, and connection
  evidence before selecting context; `Use supplied default instance` — Use the
  supplied default-instance path after reachability validation; `Use supplied
  named instance` — Use the supplied routing instance and source address.
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
  affects syntax; question `How should missing SRX model or Junos release
  details be handled?`; options: `Discover first (Recommended)` — Identify
  exact models and releases before syntax conclusions; `Exact details supplied`
  — Apply platform-specific syntax; `Infer conservatively` — Limit output to
  evidence-supported design and disclose uncertainty.
- `hsvpn_topo`; header `Topology`; ask when peer, prefix, NAT, HA, or st0 data
  is incomplete; question `How should incomplete hub-and-spoke topology be
  handled?`; options: `Map topology first (Recommended)` — Identify peers,
  LANs, WANs, NAT, HA, and st0 allocation before design; `Use supplied complete
  map` — Design from a supplied complete topology; `Design from requirements` —
  Build a new topology from supplied site and traffic requirements.
- `hsvpn_traffic`; header `Traffic`; ask when spoke path requirements are
  unclear; question `How should spoke traffic be routed?`; options: `Central
  backhaul (Recommended)` — Route required traffic through the hub; `Split or
  local` — Preserve specified local paths; `Compare models` — Evaluate both.
- `hsvpn_auth`; header `Auth`; ask when peer authentication is absent; question
  `What peer authentication should be used?`; options: `Certificates
  (Recommended)` — Use PKI where available; `Unique PSKs` — Use distinct
  secrets via approved delivery; `Shared lab PSK` — Classify as lab-only.
- `hsvpn_route`; header `Routing`; ask when management reachability and tunnel
  defaults may conflict; question `How should uncertain management-route
  protection be handled?`; options: `Inspect routes first (Recommended)` —
  Trace management, peer, and tunnel-default paths before route changes; `Use
  supplied separate path` — Preserve a supplied independent management path;
  `Analyze competing defaults` — Evaluate supplied competing defaults for
  recursion.
- `hsvpn_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  configuration, SAs, routes, sessions, and logs before diagnosis; `Use supplied
  artifacts` — Diagnose only from supplied artifacts and limit runtime
  conclusions; `Approved live collection` — Collect targeted read-only device
  evidence with approval.

### A.19 `srx-mnha`

- `mnha_task`; header `Task`; ask when requested activity is absent; question
  `What should this MNHA run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess an architecture; `Troubleshoot` — Diagnose
  synchronization, forwarding, or failover; `Migration` — Plan migration from
  chassis cluster or standalone SRX.
- `mnha_release`; header `Platform`; ask when node models or releases are absent;
  question `How should missing node model or Junos release details be handled?`;
  options: `Discover first (Recommended)` — Identify every node model and
  release before support conclusions; `Exact details supplied` — Apply
  release-specific syntax; `Stop pending details` — Avoid implementation-ready
  configuration until exact details are supplied.
- `mnha_mode`; header `MNHA Mode`; ask when forwarding mode is absent; question
  `Which MNHA forwarding model is required?`; options: `Routed mode
  (Recommended)` — Use explicit routing and SRGs; `Gateway mode` — Provide
  default-gateway service behavior; `Hybrid mode` — Combine only for documented
  requirements.
- `mnha_migrate`; header `Migration`; ask when starting state is unclear;
  question `How should an uncertain MNHA starting state be handled?`; options:
  `Inspect starting state (Recommended)` — Inventory the current HA design
  before choosing a workflow; `Design supplied greenfield` — Design from a
  supplied new-deployment baseline; `Plan supplied migration` — Plan migration
  or repair from supplied current-state evidence.
- `mnha_topo`; header `Topology`; ask when inter-node topology is incomplete;
  question `How should incomplete inter-node topology be handled?`; options:
  `Map topology first (Recommended)` — Identify node links, interfaces, and data
  paths before design; `Use supplied symmetric map` — Design from supplied
  matched interfaces and direct links; `Assess supplied asymmetric map` —
  Include supplied inter-cluster data paths and asymmetry.
- `mnha_service`; header `Services`; ask when stateful service scope is absent;
  question `How should unspecified failover-service scope be resolved?`;
  options: `Inventory services first (Recommended)` — Identify every required
  failover service before selecting a bundle; `Use supplied core-only bundle` —
  Use the supplied firewall and NAT failover scope without IPsec or advanced
  services; `Use supplied core-plus-IPsec` — Use firewall and NAT plus the
  complete supplied IPsec failover scope and specify advanced combinations
  through Other.
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
  question `How should missing SRX model or Junos release details be handled?`;
  options: `Discover first (Recommended)` — Identify the exact model and release
  before MPLS flow-mode support conclusions; `Exact details supplied` — Verify
  the supplied platform against minimum support; `Stop pending details` — Treat
  unknown platform support as a blocker.
- `mpls_role`; header `Device Role`; ask when PE, CPE, or transit role is
  unclear; question `How should an uncertain SRX MPLS role be handled?`;
  options: `Confirm role first (Recommended)` — Establish PE, CPE, transit, or
  mixed responsibilities before design; `Use supplied edge role` — Apply
  security for a supplied PE or CPE role; `Assess supplied transit role` —
  Re-evaluate the requested security function for a supplied transit role.
- `mpls_family`; header `IP Family`; ask when required address families are
  absent; question `Which address families are required?`; options: `IPv4 and
  VPNv4 (Recommended)` — Design the common IPv4 L3VPN case; `Dual stack` —
  Include IPv6 and VPNv6; `IPv6 focused` — Limit design to IPv6.
- `mpls_signal`; header `Signaling`; ask when label signaling is absent;
  question `How should unspecified label signaling be handled?`; options:
  `Inspect signaling first (Recommended)` — Identify transport and label
  protocols before MPLS design; `Preserve supplied signaling` — Preserve the
  supplied LDP, RSVP, or BGP label design; `Design new LDP transport` — Build a
  new supported LDP transport from supplied requirements.
- `mpls_vrf`; header `VRF Scope`; ask when VRF or route-target inventory is
  incomplete; question `How should an incomplete VRF inventory be handled?`;
  options: `Inventory VRFs first (Recommended)` — Identify VRFs, RDs, RTs,
  interfaces, and prefixes before policy design; `Use supplied complete matrix`
  — Apply a supplied complete VRF and route-target inventory; `Design new
  service matrix` — Build a new matrix from supplied service requirements.
- `mpls_policy`; header `Policy Model`; ask when VRF-aware policy model is
  absent; question `How should security policy be organized?`; options: `VRF
  policy groups (Recommended)` — Use the scalable supported model; `VRF to
  zone` — Preserve existing zone design where supported; `Need validation` —
  Select after release checks.
- `mpls_service`; header `Services`; ask when inspection services are absent;
  question `How should unspecified security-service scope be handled?`;
  options: `Confirm services first (Recommended)` — Inventory application, NAT,
  inspection, license, and capacity requirements before selecting a bundle;
  `Use supplied base-only bundle` — Apply supplied stateful policy and logging
  without added services; `Use supplied enhanced bundle` — Use a complete
  supplied application, NAT, and inspection list after license and capacity
  validation.

### A.21 `srx-nat`

- `nat_task`; header `Task`; ask when requested activity is absent; question
  `What should this NAT run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess a NAT design; `Troubleshoot` — Diagnose
  translation, routing, proxy, or session failures; `Migration` — Convert NAT
  behavior from another platform.
- `nat_release`; header `Platform`; ask when model or release is absent and
  affects feature support; question `How should missing SRX model or Junos
  release details be handled?`; options: `Discover first (Recommended)` —
  Identify the exact model and release before feature conclusions; `Exact
  details supplied` — Apply supported features and syntax; `Infer
  conservatively` — Limit output to evidence-supported behavior and disclose
  uncertainty.
- `nat_family`; header `NAT Type`; ask when translation family is absent;
  question `How should an unspecified translation family be handled?`; options:
  `Identify family first (Recommended)` — Establish the address-family
  translation before selecting NAT behavior; `NAT44` — Design supplied
  IPv4-to-IPv4 translation requirements; `NAT64` — Design supplied IPv6-to-IPv4
  translation requirements.
- `nat_tuple`; header `Traffic`; ask when pre- or post-translation tuple is
  incomplete; question `How should an incomplete translation tuple be
  handled?`; options: `Trace tuple first (Recommended)` — Identify source,
  destination, service, zones, and translated values before design; `Use
  supplied complete tuple` — Apply the supplied pre- and post-translation
  values; `Build tuple worksheet` — Produce a worksheet for missing tuple
  fields.
- `nat_context`; header `Context`; ask when zone, interface, or routing-instance
  classification is unclear; question `How should uncertain traffic
  classification be handled?`; options: `Inspect full context first
  (Recommended)` — Inspect complementary zone, interface, and routing-instance
  facts before rule selection; `Use supplied complete context` — Apply the
  supplied complete zone, interface, and routing-instance classification; `Stop
  pending context` — Stop rule conclusions until all complementary
  classification facts are supplied.
- `nat_reach`; header `Reachability`; ask when translated-address reachability
  is unclear; question `How should uncertain translated-address reachability be
  handled?`; options: `Trace reachability first (Recommended)` — Validate
  routing and adjacency before choosing advertisement behavior; `Use supplied
  routed prefix` — Use supplied explicit routing for translated addresses; `Use
  supplied neighbor proxy` — Apply supplied proxy ARP or NDP behavior.
- `nat_return`; header `Return Path`; ask when traffic symmetry is unclear;
  question `How should uncertain NAT return symmetry be handled?`; options:
  `Unknown—trace first (Recommended)` — Collect routing, session, and flow
  evidence before assuming symmetry; `Use supplied symmetric path` — Preserve
  the supplied stateful return through the translator; `Assess supplied
  asymmetric path` — Analyze the supplied asymmetric path and session risk.
- `nat_evidence`; header `Evidence`; ask when troubleshooting evidence is
  incomplete; question `How should incomplete troubleshooting evidence be
  handled?`; options: `Inventory evidence (Recommended)` — Identify available
  NAT configuration, routes, counters, sessions, and logs before diagnosis;
  `Use supplied artifacts` — Diagnose only from supplied artifacts and limit
  runtime conclusions; `Approved live collection` — Collect targeted read-only
  device evidence with approval.

### A.22 `srx-policy`

- `policy_task`; header `Task`; ask when requested activity is absent; question
  `What should this policy run accomplish?`; options: `Design or review
  (Recommended)` — Produce or assess security-policy intent; `Troubleshoot` —
  Diagnose lookup, session, or application failures; `Migration` — Convert from
  another platform.
- `policy_release`; header `Platform`; ask when model, release, or licensing is
  absent and affects features; question `How should missing platform or license
  details be handled?`; options: `Discover first (Recommended)` — Identify the
  model, Junos release, and licenses before feature conclusions; `Exact details
  supplied` — Apply supported policy and services from supplied details; `Infer
  conservatively` — Limit output to evidence-supported base policy and disclose
  uncertainty.
- `policy_model`; header `Policy Model`; ask when architecture is absent;
  question `Which policy architecture should be used?`; options: `Global policy
  (Recommended)` — Use global policy where it safely reduces duplication;
  `Preserve zone-pair` — Retain explicit zone organization; `Review existing` —
  Assess the supplied mix first.
- `policy_flow`; header `Traffic`; ask when traffic intent is incomplete;
  question `How should incomplete traffic intent be handled?`; options: `Map
  flow first (Recommended)` — Identify source, destination, application,
  service, zones, and purpose before policy design; `Use supplied complete
  intent` — Design from supplied complete traffic requirements; `Derive from
  migration source` — Derive intent from a supplied normalized source policy.
- `policy_nat`; header `NAT Context`; ask when NAT involvement is unclear;
  question `How should uncertain NAT involvement be handled?`; options: `Trace
  first (Recommended)` — Build a packet-flow trace before selecting policy
  addresses; `Model supplied NAT` — Use the supplied pre- and post-NAT tuple;
  `Model supplied no-NAT` — Use supplied original addresses and routing without
  translation.
- `policy_service`; header `Services`; ask when inspection services are absent;
  question `How should unspecified security-service scope be handled?`;
  options: `Confirm services first (Recommended)` — Inventory application, NAT,
  inspection, license, and capacity requirements before selecting a bundle;
  `Use supplied base-only bundle` — Apply supplied least privilege and logging
  without added services; `Use supplied enhanced bundle` — Use a complete
  supplied application, NAT, and inspection list after license and capacity
  validation.
- `policy_ip`; header `IP Family`; ask when address-family scope is absent;
  question `Which address families should policy cover?`; options: `Dual-stack
  (Recommended)` — Cover IPv4 and IPv6 unicast and specify multicast or
  control-plane scope through Other; `IPv4 only` — Cover only IPv4 unicast and
  specify special traffic scope through Other; `IPv6 only` — Cover only IPv6
  unicast and specify special traffic scope through Other.
- `policy_session`; header `Sessions`; ask when existing-session behavior
  matters and is absent; question `How should existing sessions be treated
  after a policy change?`; options: `Leave existing sessions (Recommended)` —
  Validate new sessions without clearing existing state; `Clear targeted
  sessions` — Clear only separately approved matching sessions;
  `Maintenance-window reset` — Reset broader session state only under separate
  maintenance approval with rollback.
