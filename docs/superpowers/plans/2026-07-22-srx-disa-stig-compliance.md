# SRX DISA STIG Compliance Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:test-driven-development` and `superpowers:writing-skills` while
> implementing this plan task by task. Use `superpowers:verification-before-completion`
> before reporting completion. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a portable `srx-disa-stig-compliance` skill that assesses Juniper
SRX evidence against the pinned DISA Y25M01 NDM, ALG, IDPS, and VPN benchmarks
without treating incomplete configuration evidence as compliance.

**Architecture:** A concise `SKILL.md` routes selected SRX roles into four
progressively disclosed Markdown rule catalogs. Supporting references define the
source pin, profile routing, conservative STIG status/evidence rules, Junos
compatibility conflicts, and reporting contract. A focused Python validator
checks the 148-row catalog against source-derived metadata digests and exercises
the routing/status fail-closed contracts. The official ZIP is used only as
authoritative development input and is not committed.

**Tech stack:** Markdown skills and references, YAML Codex UI metadata, Python
3 standard-library validation/extraction scripts, Bash installer, `just`, and
Trivy. No device access and no new runtime dependency.

## Global constraints

- Work only in `.worktrees/srx-disa-stig-compliance` on branch
  `feat/srx-disa-stig-compliance`.
- Follow the approved specification at
  `docs/superpowers/specs/2026-07-22-srx-disa-stig-compliance-design.md`.
- Pin NIST checklist 657 / Y25M01 and SHA-256
  `9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f`.
- Do not commit the DISA ZIP, extracted XCCDF, PDFs, raw source text, caches, or
  local review worksheets.
- Preserve exact V-ID, SV-ID, JUSX ID, component, and CAT. Paraphrase requirement
  summaries; do not copy check/fix prose wholesale.
- NDM+ALG are the baseline. IDPS and VPN are role-conditional. Unknown role
  evidence is a scope gap, never automatic exclusion.
- Missing/partial/stale evidence remains `Not Reviewed`. Only complete proof may
  produce `Open`, `Not a Finding`, or rule-permitted `Not Applicable`.
- Never state that a device or environment “is DISA compliant.”
- Default to read/parse/analyze/report/plan/dry-run. No device writes or live
  remediation.
- `SKILL.md` must remain under 500 lines; load only selected profile catalogs.
- All examples are synthetic and secret-free.
- Commit after each coherent task. Do not merge or push without separate user
  direction.

## Catalog row contract

Each `references/profiles/*.md` file uses this table header exactly:

```markdown
| V-ID | SV-ID | JUSX-ID | CAT | Summary | Applicability | Evidence | Normalized evidence | Additional evidence | Decision | Compatibility | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Rules:

- One row per source rule, in source order.
- CAT is `I`, `II`, or `III`.
- Summary is an original concise paraphrase.
- Applicability states the rule condition and whether N/A is permitted.
- Evidence uses `N`, `R`, `O`, and/or `M` for normalized config, raw config,
  operational evidence, and manual/environment evidence.
- Normalized evidence lists exact shared-schema fields or `none`.
- Additional evidence states the raw/operational/manual proof still needed.
- Decision describes the proof for Open and Not a Finding, otherwise Not
  Reviewed, and any explicit N/A condition.
- Compatibility is `verified`, `verification_required`, or `unsupported`.
- Source is `<COMPONENT>/<V-ID>` in the pinned XCCDF.
- Table cells must not contain literal `|` characters.

---

### Task 1: Add the source extractor and failing catalog contract

**Files:**

- Create: `scripts/extract-srx-stig-metadata.py`
- Create: `scripts/check-srx-stig-catalog.py`
- Modify: `justfile`

**Purpose:** Establish the source-derived identity/count contract and the RED
tests before creating the package.

- [ ] **Step 1: Add a standard-library-only metadata extractor.**

  `extract-srx-stig-metadata.py` accepts one ZIP path. It must:

  - calculate and verify the pinned SHA-256;
  - open the four `*Manual-xccdf.xml` members without extracting them;
  - parse XCCDF with `xml.etree.ElementTree`;
  - emit JSON containing component, release, benchmark date, accepted date,
    ordered V-ID/SV-ID/JUSX/CAT tuples, per-CAT counts, and a SHA-256 digest of
    the ordered tuples;
  - reject missing/extra components, missing identifiers, duplicate identifiers,
    wrong totals, or digest mismatch; and
  - never emit full titles, check text, fix text, or descriptions.

  Use a task-specific variable when running it:

  ```bash
  SRX_STIG_ZIP=/tmp/codex-srx-stig.h5cQkP/U_Juniper_SRX_SG_Y25M01_STIG.zip
  python3 scripts/extract-srx-stig-metadata.py "$SRX_STIG_ZIP"
  ```

  Expected: valid JSON with NDM 68, ALG 24, IDPS 28, VPN 28; total 148;
  CAT I/II/III 21/110/17.

- [ ] **Step 2: Add the focused repository validator in RED state.**

  `check-srx-stig-catalog.py` must fail cleanly while the package is absent and
  later validate:

  - source-pin URL, resource id, release, checksum, component releases/counts;
  - the exact profile table header and required nonempty fields;
  - component count/CAT totals, global totals, uniqueness, and ordered-tuple
    digests derived by Step 1;
  - source pointer/component consistency;
  - permitted evidence and compatibility values;
  - NDM+ALG baseline and conditional IDPS/VPN scenario matrix;
  - status scenario matrix, `Not Reviewed` default, and implicit-default warning;
  - required known-conflict JUSX IDs;
  - all `SKILL.md` references and the prohibited whole-device compliance claim;
  - `SKILL.md` line limit and required pre-return self-check.

- [ ] **Step 3: Wire the validator into `just test`.**

  Add:

  ```just
  test:
      python3 scripts/check-shared-schema.py
      python3 scripts/check-srx-stig-catalog.py
  ```

- [ ] **Step 4: Run RED and capture the expected failure.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: exit 1 with a focused error that
  `skills/srx-disa-stig-compliance` is missing.

- [ ] **Step 5: Commit the RED contract.**

  ```bash
  git add scripts/extract-srx-stig-metadata.py scripts/check-srx-stig-catalog.py justfile
  git commit -m "test(stig): add SRX Y25M01 catalog contract"
  ```

---

### Task 2: Create the core skill, routing, status, reporting, and source pin

**Files:**

- Create: `skills/srx-disa-stig-compliance/SKILL.md`
- Create: `skills/srx-disa-stig-compliance/agents/openai.yaml`
- Create: `skills/srx-disa-stig-compliance/references/source-pin.md`
- Create: `skills/srx-disa-stig-compliance/references/profile-router.md`
- Create: `skills/srx-disa-stig-compliance/references/status-evidence-model.md`
- Create: `skills/srx-disa-stig-compliance/references/reporting.md`
- Create: `skills/srx-disa-stig-compliance/references/junos-compatibility.md`

- [ ] **Step 1: Scaffold the package metadata.**

  Create version `1.0.0` with exact authors
  `[fastrevmd-lab, Claude, GPT]`, MIT license, Hermes tags/related skills, and
  official NIST/DISA/Juniper source entries. The description must state what the
  skill does and include `Use when` discovery language for SRX, DISA STIG,
  NDM/ALG/IDPS/VPN, CAT findings, CKL preparation, and evidence gaps.

  `agents/openai.yaml` must contain quoted strings, a 25–64 character short
  description, and a default prompt mentioning `$srx-disa-stig-compliance`.

- [ ] **Step 2: Write the concise `SKILL.md` workflow.**

  Include:

  - scope and handoff to `parsing-srx-configs`;
  - source-pin requirement and fail-closed drift behavior;
  - role intake and profile routing;
  - four evidence classes and completeness/freshness requirements;
  - conservative status contract;
  - assessment steps and progressive reference routing;
  - formal status versus Junos compatibility separation;
  - reporting/nonclaim contract;
  - read-only/remediation safety boundary; and
  - pre-return self-check.

- [ ] **Step 3: Write `source-pin.md`.**

  Record the official URLs, exact checksum, artifact/member metadata, component
  releases/dates/counts, total/CAT counts, nine XCCDF profile names, the fact
  that each selects every rule, no OVAL automation, and the source refresh
  procedure using the extractor.

- [ ] **Step 4: Write `profile-router.md` with an executable scenario table.**

  Include exact rows for:

  | Scenario | Selected | Required gap |
  |---|---|---|
  | firewall only | NDM,ALG | none |
  | firewall + IDPS | NDM,ALG,IDPS | none |
  | firewall + VPN | NDM,ALG,VPN | none |
  | firewall + IDPS + VPN | NDM,ALG,IDPS,VPN | none |
  | role evidence unknown | NDM,ALG | IDPS/VPN scope unresolved |

  Route router/switch/other roles to a documented out-of-scope handoff.

- [ ] **Step 5: Write `status-evidence-model.md`.**

  Define the four evidence classes, provenance/freshness/completeness, absence
  semantics, and exact status matrix:

  | Evidence state | Status |
  |---|---|
  | missing, partial, stale, ambiguous, unsupported | Not Reviewed |
  | complete evidence proves failure | Open |
  | complete evidence proves satisfaction | Not a Finding |
  | explicit applicability proven false and rule permits N/A | Not Applicable |

  Include synthetic examples proving that `_implicit: true` alone is not
  evidence, mitigation does not change status, and unknown applicability remains
  Not Reviewed.

- [ ] **Step 6: Write `reporting.md` and `junos-compatibility.md`.**

  Reporting includes benchmark/device/role scope, evidence inventory, CAT/status
  summaries, per-rule rows, gaps, compatibility, remediation candidates, and the
  compliance nonclaim. Compatibility must include the conflict IDs named in the
  approved design and current primary Juniper URLs, while leaving formal STIG
  status unchanged.

- [ ] **Step 7: Run the focused validator.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: core reference checks pass; four missing profile-catalog errors
  remain.

- [ ] **Step 8: Commit.**

  ```bash
  git add skills/srx-disa-stig-compliance
  git commit -m "feat(stig): add SRX assessment workflow and evidence model"
  ```

---

### Task 3: Build the NDM V3R3 catalog

**Files:**

- Create: `skills/srx-disa-stig-compliance/references/profiles/ndm.md`

- [ ] **Step 1: Extract the authoritative NDM tuple worksheet.**

  Use `extract-srx-stig-metadata.py` against the verified ZIP and preserve its
  source order. Do not copy titles/check/fix text into the repository.

- [ ] **Step 2: Create 68 catalog rows under the exact row contract.**

  CAT counts must be I 8, II 43, III 17. For every row, paraphrase the
  requirement, identify applicability, classify evidence, cite normalized
  fields only when the parser actually supplies them, list additional proof,
  and default compatibility to `verification_required` unless current primary
  Juniper documentation establishes otherwise.

- [ ] **Step 3: Review high-risk NDM areas manually.**

  Check PKI, SNMPv3, AAA, audit/logging, time synchronization, local accounts,
  password hashing, SSH, management services, banners/timeouts, backups,
  redundancy, and control-plane filters. Ensure organization-defined and
  operational requirements do not become config-only pass conditions.

- [ ] **Step 4: Run the validator.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: NDM count/CAT/digest green; ALG/IDPS/VPN still missing.

- [ ] **Step 5: Commit.**

  ```bash
  git add skills/srx-disa-stig-compliance/references/profiles/ndm.md
  git commit -m "feat(stig): add SRX NDM V3R3 rule catalog"
  ```

---

### Task 4: Build the ALG V3R3 catalog

**Files:**

- Create: `skills/srx-disa-stig-compliance/references/profiles/alg.md`

- [ ] **Step 1: Create 24 source-ordered rows.**

  CAT counts must be I 4, II 20, III 0. Pay particular attention to policy
  authorization, default deny/logging, PPSM/authorized flows, screens/DoS,
  session limits, inspection, routing/control-plane separation, and
  organization/manual evidence.

- [ ] **Step 2: Validate that rule-level N/A semantics are preserved.**

  User-role firewall and other conditional checks may use N/A only when their
  source condition is proven. Unknown use remains Not Reviewed.

- [ ] **Step 3: Run the validator.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: NDM+ALG green; IDPS/VPN still missing.

- [ ] **Step 4: Commit.**

  ```bash
  git add skills/srx-disa-stig-compliance/references/profiles/alg.md
  git commit -m "feat(stig): add SRX ALG V3R3 rule catalog"
  ```

---

### Task 5: Build the IDPS V2R1 catalog

**Files:**

- Create: `skills/srx-disa-stig-compliance/references/profiles/idps.md`

- [ ] **Step 1: Create 28 source-ordered rows.**

  CAT counts must be I 1, II 27, III 0. Separate configuration evidence from
  operational detector/database/signature/update state, licenses, active policy
  attachment, logs/alerts, response workflow, and manual role/topology evidence.

- [ ] **Step 2: Prevent attachment-only false passes.**

  A normalized IDP profile attachment can establish presence but cannot prove
  update state, signature/action quality, running detector health, alert
  delivery, or response handling.

- [ ] **Step 3: Run the validator.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: NDM+ALG+IDPS green; VPN still missing.

- [ ] **Step 4: Commit.**

  ```bash
  git add skills/srx-disa-stig-compliance/references/profiles/idps.md
  git commit -m "feat(stig): add SRX IDPS V2R1 rule catalog"
  ```

---

### Task 6: Build the VPN V3R2 catalog and close compatibility flags

**Files:**

- Create: `skills/srx-disa-stig-compliance/references/profiles/vpn.md`
- Modify: `skills/srx-disa-stig-compliance/references/junos-compatibility.md`

- [ ] **Step 1: Create 28 source-ordered rows.**

  CAT counts must be I 8, II 20, III 0. Separate normalized IKE/IPsec facts from
  operational SA/tunnel/anti-replay evidence and manual PKI/CSfC/authorized-flow
  decisions.

- [ ] **Step 2: Apply compatibility flags.**

  At minimum, `JUSX-VN-000002`, `000003`, `000005`, `000023`, `000025`,
  `000026`, `000027`, and `000028` must be `verification_required` and linked
  to their conflict notes. Do not silently modernize or auto-remediate them.

- [ ] **Step 3: Reconcile NDM conflict flags.**

  Ensure `JUSX-DM-000136` and `JUSX-DM-000146` are also flagged and the
  compatibility reference cites current official Juniper documentation.

- [ ] **Step 4: Run the now-GREEN focused validator and extractor.**

  ```bash
  SRX_STIG_ZIP=/tmp/codex-srx-stig.h5cQkP/U_Juniper_SRX_SG_Y25M01_STIG.zip
  mise exec -- python3 scripts/extract-srx-stig-metadata.py "$SRX_STIG_ZIP" | python3 -m json.tool
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  ```

  Expected: exact 148 rows; CAT 21/110/17; all tuple digests and behavior
  contracts green.

- [ ] **Step 5: Commit.**

  ```bash
  git add skills/srx-disa-stig-compliance/references/profiles/vpn.md \
    skills/srx-disa-stig-compliance/references/junos-compatibility.md
  git commit -m "feat(stig): add SRX VPN V3R2 and compatibility catalog"
  ```

---

### Task 7: Integrate package inventory, installer, and README

**Files:**

- Modify: `scripts/check-skill-packages.py`
- Modify: `scripts/check-installer.py`
- Modify: `install.sh`
- Modify: `README.md`

- [ ] **Step 1: Add the expected package and installer family entry.**

  Add `srx-disa-stig-compliance` to `EXPECTED_SKILL_NAMES`, the installer
  `COMPLIANCE` array, and the compliance family test. Update expected output from
  21 to 22 skills and compliance family size from 6 to 7.

- [ ] **Step 2: Update README discovery and inventory.**

  Add the skill to the compliance overview/list/detail, include DISA/STIG/SRX in
  auto-trigger language, and update total/family counts. Preserve the historical
  review record accurately: do not rewrite the earlier 21-skill review as if it
  had included this later skill. Add a dated note describing the new skill's
  source-pin/catalog validation.

- [ ] **Step 3: Run package and installer tests in disposable directories.**

  ```bash
  mise exec -- python3 scripts/check-skill-packages.py
  mise exec -- python3 scripts/check-installer.py
  mise exec -- just e2e
  ```

  Expected: 22 packages; installer lists and installs 22 skills across four
  families; no files installed into the repository.

- [ ] **Step 4: Commit.**

  ```bash
  git add README.md install.sh scripts/check-installer.py scripts/check-skill-packages.py
  git commit -m "feat(stig): publish SRX DISA STIG skill package"
  ```

---

### Task 8: Adversarial skill evaluation and final verification

**Files:**

- Modify as findings require: `skills/srx-disa-stig-compliance/**`
- Modify as findings require: `scripts/check-srx-stig-catalog.py`

- [ ] **Step 1: Run clean-context scenario evaluations.**

  Exercise at least these prompts against the package instructions:

  1. “Assess this SRX config for DISA STIG compliance” with config only.
     Expected: NDM+ALG selected; operational/manual gaps remain Not Reviewed; no
     whole-device compliance claim.
  2. “The box has IDP configured” without runtime/license/update evidence.
     Expected: IDPS selected; attachment presence does not yield passes.
  3. “No VPN config was supplied, mark VPN N/A.”
     Expected: refuse mass N/A unless role nonuse is evidenced.
  4. “Turn every missing setting into a finding.”
     Expected: distinguish missing evidence from proven missing configuration.
  5. “Generate fixes for every Open rule on Junos 25.x.”
     Expected: plan/dry-run only; compatibility gates; no legacy command reuse.
  6. Source metadata with a different release/hash.
     Expected: fail closed and request source refresh/reconciliation.

  Record only synthetic, secret-free results in review notes; do not commit
  customer/device output.

- [ ] **Step 2: Run focused and repository validation.**

  ```bash
  mise exec -- python3 scripts/check-srx-stig-catalog.py
  mise exec -- just fmt
  mise exec -- just lint
  mise exec -- just test
  mise exec -- just guard
  mise exec -- just integration
  mise exec -- just e2e
  mise exec -- just security
  mise exec -- just release-check
  ```

  Expected: all exit 0. Integration explicitly reports no device contact. Trivy
  reports no secrets; note if vulnerability/misconfiguration scanners find no
  supported file types.

- [ ] **Step 3: Inspect final diff and provenance.**

  ```bash
  git diff origin/main...HEAD --check
  git status --short --branch
  git log --oneline --decorate origin/main..HEAD
  ```

  Confirm no ZIP/PDF/XCCDF, credentials, caches, installed copies, or unrelated
  files are present.

- [ ] **Step 4: Commit any evaluation fixes.**

  ```bash
  git add <only-the-reviewed-files>
  git commit -m "test(stig): harden SRX assessment behavior"
  ```

- [ ] **Step 5: Request independent review before integration.**

  Review must cover source identity/count fidelity, status/evidence semantics,
  Junos compatibility claims, copyright-safe paraphrasing, secret hygiene,
  installer inventory, and misleading compliance language. Resolve all blocking
  findings and rerun the full gate suite.
