# Restore the MIT Skill Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore all fourteen packages removed by PR #12, distribute all 21 repository skills under MIT, and replace copied third-party page dumps with original attributed notes.

**Architecture:** Recover the last pre-deletion package trees from commit `28c2844`, then preserve the authored playbooks while re-authoring raw SRX source extracts in place so existing internal links remain stable. Make the filesystem, package validator, installer, README, and TODO inventory agree on one explicit 21-skill catalog, with automated MIT and raw-dump guards.

**Tech Stack:** Markdown skill packages, YAML frontmatter, Python 3.12 validation scripts, Bash installer, `just`, `mise`, `pre-commit`, Trivy, and Git.

## Global Constraints

- Work only in `.worktrees/restore-mit-skill-catalog` on branch `restore-mit-skill-catalog`.
- Recover package content from commit `28c2844`; do not revert PR #12 or overwrite current files wholesale.
- Restore exactly eight SRX and six compliance packages for a final total of 21.
- Every `SKILL.md` must declare `license: MIT`.
- Delete or independently rewrite raw third-party page dumps; preserve direct attribution and describe the result as `Inspired by`.
- Prefer current authoritative vendor and framework sources; mark unverified behavior unsupported or uncertain.
- Keep direct README links to each package's `SKILL.md`.
- Keep every `SKILL.md` at or below 500 lines and combined descriptions at or below 8,000 characters.
- Preserve byte identity across the four parser copies of `intermediate-schema.md`.
- Installation tests must use disposable directories and must not alter installed user skills.
- Do not contact devices or perform configuration, commit, upgrade, reboot, delete, or failover operations.
- Execute inline in the primary session because the user did not request delegation or parallel agents.

---

### Task 1: Restore the explicit 21-package MIT inventory

**Files:**
- Restore: `skills/{cis-controls-ngfw-compliance,cmmc-nist-800-171-ngfw-compliance,hipaa-ngfw-compliance,iso27001-ngfw-compliance,pci-ngfw-compliance,soc2-ngfw-compliance}/**`
- Restore: `skills/{srx-advpn,srx-autovpn-full-tunnel,srx-dynamic-ip-feed,srx-ipsec-hub-spoke,srx-mnha,srx-mpls-in-flow,srx-nat,srx-policy}/**`
- Modify: `scripts/check-skill-packages.py`

**Interfaces:**
- Consumes: the package trees at Git commit `28c2844`.
- Produces: `EXPECTED_SKILL_NAMES: frozenset[str]` and an exact 21-package filesystem contract used by later tasks.

- [ ] **Step 1: Change the validator contract before restoring files**

Add an immutable expected-name set and replace the old count-only check:

```python
EXPECTED_SKILL_NAMES = frozenset(
    {
        "cis-controls-ngfw-compliance",
        "cmmc-nist-800-171-ngfw-compliance",
        "firewall-best-practices-audit",
        "firewall-config-conversion",
        "firewall-config-diff",
        "hipaa-ngfw-compliance",
        "iso27001-ngfw-compliance",
        "parsing-cisco-configs",
        "parsing-fortinet-configs",
        "parsing-palo-configs",
        "parsing-srx-configs",
        "pci-ngfw-compliance",
        "soc2-ngfw-compliance",
        "srx-advpn",
        "srx-autovpn-full-tunnel",
        "srx-dynamic-ip-feed",
        "srx-ipsec-hub-spoke",
        "srx-mnha",
        "srx-mpls-in-flow",
        "srx-nat",
        "srx-policy",
    }
)
```

Inside `main()`, derive `actual_skill_names` from `skill_files`, report sorted
missing and unexpected names, and require `fields.get("license") == "MIT"` for
every package.

- [ ] **Step 2: Run the validator and observe the expected red result**

Run: `mise exec -- python3 scripts/check-skill-packages.py`

Expected: exit 1 with fourteen missing package names. Existing seven packages
must not report license errors.

- [ ] **Step 3: Recover the fourteen package trees mechanically**

Run this bulk Git recovery from the worktree root:

```bash
git restore --source=28c2844 -- \
  skills/cis-controls-ngfw-compliance \
  skills/cmmc-nist-800-171-ngfw-compliance \
  skills/hipaa-ngfw-compliance \
  skills/iso27001-ngfw-compliance \
  skills/pci-ngfw-compliance \
  skills/soc2-ngfw-compliance \
  skills/srx-advpn \
  skills/srx-autovpn-full-tunnel \
  skills/srx-dynamic-ip-feed \
  skills/srx-ipsec-hub-spoke \
  skills/srx-mnha \
  skills/srx-mpls-in-flow \
  skills/srx-nat \
  skills/srx-policy
```

This is a mechanical recovery only. Do not restore `README.md`, `install.sh`,
`LICENSE-APACHE`, `NOTICE`, or the old project license state from this commit.

- [ ] **Step 4: Change all fourteen recovered package licenses**

In each recovered `SKILL.md`, replace exactly:

```yaml
license: source-derived-summary-local-use
```

with:

```yaml
license: MIT
```

Do not change versions, descriptions, authors, metadata, or behavior in this
step.

- [ ] **Step 5: Verify the recovered portable-package contract**

Run:

```bash
mise exec -- python3 scripts/check-skill-packages.py
rg -n '^license:' skills/*/SKILL.md
```

Expected: `OK: 21 portable skill packages`; exactly 21 `license: MIT` lines;
no local-use license markers.

- [ ] **Step 6: Commit the recovered inventory**

```bash
git add scripts/check-skill-packages.py skills
git commit -m "feat: restore 21-skill MIT catalog"
```

### Task 2: Re-author VPN, feed, MNHA, and MPLS source material

**Files:**
- Modify: `skills/srx-dynamic-ip-feed/references/source-extract.md`
- Modify: `skills/srx-autovpn-full-tunnel/references/{source-design-summary.md,source-index.md}`
- Modify: `skills/srx-ipsec-hub-spoke/references/{source-design-summary.md,source-index.md}`
- Modify: `skills/srx-mnha/references/source-*.md`
- Modify: `skills/srx-mpls-in-flow/references/source-*.md`
- Review: the corresponding five `SKILL.md` files plus `skills/srx-advpn/SKILL.md` and its original field notes.

**Interfaces:**
- Consumes: source metadata and operational facts recovered in Task 1.
- Produces: concise, original references that retain the paths consumed by the recovered skill bodies.

- [ ] **Step 1: Record the current raw-extract baseline**

Run:

```bash
find skills/srx-dynamic-ip-feed skills/srx-mnha skills/srx-mpls-in-flow \
  -path '*/references/source-*.md' -print0 | xargs -0 wc -l
```

Expected: at least one recovered source file exceeds 300 lines, proving the
raw-page cleanup is necessary.

- [ ] **Step 2: Verify the cited sources and identify required facts**

For each source URL already recorded in package frontmatter or `source-index.md`,
check the current authoritative vendor page when available. Retain only facts
that the consuming skill needs: supported topology/release, required objects,
ordering, failure modes, and verification commands. If a claim cannot be
confirmed, label it `Field observation` or `Unverified` rather than presenting
it as vendor-supported behavior.

- [ ] **Step 3: Rewrite each raw page file in place**

Use this exact structure, illustrated with the recovered MNHA DHCP source and
adapted with independently worded facts for each other source:

```markdown
# Inspired by: DHCP on MNHA: Back to Basics

- **Publisher/author:** James Rathbun
- **Source:** https://community.juniper.net/blogs/james-rathbun/2026/04/22/dhcp-on-mnha-back-to-basics
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the MNHA DHCP ownership and failover cautions.

## Original summary

MNHA nodes keep independent control planes and configurations, so DHCP service
placement and address ownership must follow the selected HA topology rather
than chassis-cluster assumptions. Validate which node owns the client-facing
path and how lease service behaves during routing or node failover.

## Verification implications

- Confirm DHCP support and failover behavior on the target Junos release.
- Treat topology-specific behavior from the article as design inspiration until
  it is reproduced on the target platform.
```

Remove copied navigation, article prose, reader comments, acknowledgements,
revision tables, copyright footers, and long configuration transcripts. Keep
individual files below 200 lines.

- [ ] **Step 4: Review authored reference files for provenance wording**

Keep original design summaries, source indexes, lab field notes, advanced MNHA
workflows, and config patterns when they are independently authored. Change
headings or introductions that say content was copied or extracted so they say
`Inspired by` and point to the external source instead.

- [ ] **Step 5: Verify links and package limits**

Run:

```bash
mise exec -- python3 scripts/check-skill-packages.py
find skills/srx-dynamic-ip-feed skills/srx-mnha skills/srx-mpls-in-flow \
  -path '*/references/source-*.md' -print0 | xargs -0 wc -l
git diff --check
```

Expected: package validation passes; each rewritten source note is under 200
lines; no referenced file is missing.

- [ ] **Step 6: Commit the first provenance batch**

```bash
git add skills/srx-advpn skills/srx-autovpn-full-tunnel \
  skills/srx-dynamic-ip-feed skills/srx-ipsec-hub-spoke \
  skills/srx-mnha skills/srx-mpls-in-flow
git commit -m "docs: re-author SRX VPN HA and feed sources"
```

### Task 3: Re-author the NAT source material

**Files:**
- Modify: `skills/srx-nat/references/source-address-persistent-source-nat.md`
- Modify: `skills/srx-nat/references/source-dns64-and-nat64-on-srx-series.md`
- Modify: `skills/srx-nat/references/source-security-nat-overview.md`
- Modify: `skills/srx-nat/references/source-source-nat-part-1.md`
- Modify: `skills/srx-nat/references/source-source-nat-part-3-large-scale.md`
- Modify: `skills/srx-nat/references/source-srx-evpnvxlan-t5-oipsec.md`
- Modify: `skills/srx-nat/references/source-srx340-nat-hairpinning.md`
- Modify: `skills/srx-nat/references/source-srx4600-cgn-configuration-breakdown.md`
- Modify: `skills/srx-nat/references/source-troubleshoot-destination-nat.md`
- Modify: `skills/srx-nat/references/source-troubleshoot-source-nat.md`
- Review: `skills/srx-nat/{SKILL.md,references/advanced-nat.md,references/source-index.md}`

**Interfaces:**
- Consumes: the recovered NAT playbook and its external bibliography.
- Produces: original, cited NAT notes covering only the facts used by `srx-nat`.

- [ ] **Step 1: Prove the NAT reference bundle still contains raw pages**

Run:

```bash
find skills/srx-nat/references -name 'source-*.md' -print0 | xargs -0 wc -l
```

Expected: one or more source files exceed 300 lines.

- [ ] **Step 2: Verify NAT claims against authoritative documentation**

Check current Juniper documentation for NAT rule-set matching and ordering,
proxy ARP, NAT64/DNS64, address persistence, pool behavior, troubleshooting,
and CGN/PBA. Treat community examples as inspiration and lab evidence, not the
sole authority for release support.

- [ ] **Step 3: Rewrite every listed NAT source file**

Use the `Inspired by` structure from Task 2. Retain concise command names and
configuration fragments only when needed to explain interoperability or a
verification step. Explicitly label the EVPN/VXLAN-over-IPsec and SRX340
hairpinning material as community-derived examples that require target-release
validation.

- [ ] **Step 4: Align the NAT source index and authored advanced notes**

Ensure `source-index.md` links to each rewritten note and describes it as an
original summary. Ensure `advanced-nat.md` does not claim that linked external
material is covered by the project license.

- [ ] **Step 5: Verify the NAT package**

Run:

```bash
mise exec -- python3 scripts/check-skill-packages.py
find skills/srx-nat/references -name 'source-*.md' -print0 | xargs -0 wc -l
git diff --check
```

Expected: validation passes and every rewritten NAT source note is below 200
lines.

- [ ] **Step 6: Commit the NAT provenance batch**

```bash
git add skills/srx-nat
git commit -m "docs: re-author SRX NAT source notes"
```

### Task 4: Re-author the security-policy source material

**Files:**
- Modify: every `skills/srx-policy/references/source-*.md`
- Review: `skills/srx-policy/SKILL.md`
- Review: `skills/srx-policy/references/{ngwf-vs-ewf-research.md,service-discovery.md,source-index.md,web-filtering-ngwf-ewf-patterns.md}`

**Interfaces:**
- Consumes: the recovered policy, AppFW, NGWF/EWF, SecIntel, and ATP bibliography.
- Produces: original, cited policy references with explicit product/release verification boundaries.

- [ ] **Step 1: Prove the policy bundle still contains raw pages**

Run:

```bash
find skills/srx-policy/references -name 'source-*.md' -print0 | xargs -0 wc -l
```

Expected: multiple source files exceed 300 lines.

- [ ] **Step 2: Verify current product guidance**

Use authoritative Juniper documentation for security policy structure,
predefined applications, global policy behavior, AppFW, NGWF/EWF, SecIntel,
and ATP. Retain third-party training pages only as attributed inspiration and
mark any syntax not confirmed by Juniper documentation or existing field notes
as release-dependent.

- [ ] **Step 3: Rewrite every policy source file**

Apply the Task 2 `Inspired by` template. Remove copied page prose and long
product datasheets. Retain only the facts needed by `SKILL.md`,
`ngwf-vs-ewf-research.md`, and `web-filtering-ngwf-ewf-patterns.md`.

- [ ] **Step 4: Align authored research and the source index**

Make `source-index.md` a bibliography of external inspiration plus links to the
original notes. Ensure the authored research and patterns distinguish vendor
documentation, live-verified observations, and unverified release behavior.

- [ ] **Step 5: Verify the policy package**

Run:

```bash
mise exec -- python3 scripts/check-skill-packages.py
find skills/srx-policy/references -name 'source-*.md' -print0 | xargs -0 wc -l
git diff --check
```

Expected: validation passes and every rewritten policy source note is below 200
lines.

- [ ] **Step 6: Commit the policy provenance batch**

```bash
git add skills/srx-policy
git commit -m "docs: re-author SRX policy source notes"
```

### Task 5: Add regression guards for MIT metadata and raw page dumps

**Files:**
- Modify: `scripts/check-skill-packages.py`

**Interfaces:**
- Consumes: the clean source-note convention from Tasks 2-4.
- Produces: `raw_reference_error(path: Path, text: str) -> str | None`, used by package validation.

- [ ] **Step 1: Create a temporary raw-dump fixture and observe no rejection**

Run:

```bash
mkdir -p skills/srx-policy/references
printf '%s\n' '# copied page' 'Skip main navigation' 'Powered by Higher Logic' \
  > skills/srx-policy/references/source-raw-dump-test.md
mise exec -- python3 scripts/check-skill-packages.py
rm skills/srx-policy/references/source-raw-dump-test.md
```

Expected before implementation: validator exits 0, demonstrating that the raw
page dump is not yet guarded. The temporary fixture must be removed immediately
and never staged.

- [ ] **Step 2: Implement the raw-reference guard**

Add:

```python
RAW_REFERENCE_MAX_LINES = 200
RAW_DUMP_MARKERS = (
    "Skip main navigation",
    "Powered by Higher Logic",
    "View Only",
    "Jump to Best Answer",
    "New Best Answer",
)


def raw_reference_error(path: Path, text: str) -> str | None:
    if not (path.name.startswith("source-") or path.name == "source-extract.md"):
        return None
    line_count = text.count("\n") + 1
    if line_count > RAW_REFERENCE_MAX_LINES:
        return f"{line_count} lines exceeds the {RAW_REFERENCE_MAX_LINES}-line source-note limit"
    marker = next((value for value in RAW_DUMP_MARKERS if value in text), None)
    if marker:
        return f"contains raw page-dump marker {marker!r}"
    return None
```

Scan every restored package's `references/*.md`, append errors returned by this
helper, and separately reject the string `source-derived-summary-local-use`
anywhere under `skills/`.

- [ ] **Step 3: Recreate the fixture and verify rejection**

Run the Step 1 fixture command again.

Expected after implementation: validator exits 1 and reports
`source-raw-dump-test.md` with `raw page-dump marker`. Remove the fixture.

- [ ] **Step 4: Verify the clean catalog passes**

Run:

```bash
mise exec -- python3 scripts/check-skill-packages.py
test -z "$(rg -l 'source-derived-summary-local-use|Powered by Higher Logic|Skip main navigation' skills || true)"
```

Expected: `OK: 21 portable skill packages`; the shell assertion succeeds.

- [ ] **Step 5: Commit the regression guard**

```bash
git add scripts/check-skill-packages.py
git commit -m "test: guard MIT skill provenance"
```

### Task 6: Restore installer families with disposable installation tests

**Files:**
- Modify: `install.sh`
- Create: `scripts/check-installer.py`
- Modify: `justfile`

**Interfaces:**
- Consumes: the exact 21 package names established by Task 1.
- Produces: installer families `parsers`, `srx`, `tooling`, and `compliance`; an offline e2e checker invoked by `just e2e`.

- [ ] **Step 1: Write the failing installer checker**

Create `scripts/check-installer.py` using `subprocess.run` and
`tempfile.TemporaryDirectory`. It must:

```python
EXPECTED_COUNTS = {"all": 21, "srx": 8, "compliance": 6}
```

For `all`, run `bash install.sh --all --dir "$temporary_root/all" --force -y`;
then run the same command with `--family srx` into `$temporary_root/srx` and
`--family compliance` into `$temporary_root/compliance`.
Assert that the resulting child-directory names equal the expected package
sets, not only the counts. Run `bash install.sh --family invalid -y` and assert
that it fails with `Valid families: parsers, srx, tooling, compliance`.

- [ ] **Step 2: Run the checker and observe the red result**

Run: `mise exec -- python3 scripts/check-installer.py`

Expected: failure because current `install.sh` recognizes only seven packages
and has no `srx` or `compliance` family.

- [ ] **Step 3: Restore SRX and compliance installer integration**

Merge the `SRX` and `COMPLIANCE` arrays and family-selection branches from
`28c2844:install.sh` into the current installer. Update every count, help line,
inventory heading, interactive group, example, and error message to 21 skills
and four families. Preserve current target-directory behavior and do not
restore old licensing text.

- [ ] **Step 4: Make `just e2e` run the disposable checker**

Replace the current recipe with:

```make
e2e:
    ./install.sh --help >/dev/null
    python3 scripts/check-installer.py
```

- [ ] **Step 5: Verify installer behavior**

Run:

```bash
mise exec -- just e2e
./install.sh --list
```

Expected: e2e passes; list output reports 21 total, eight SRX, and six
compliance packages.

- [ ] **Step 6: Commit installer restoration**

```bash
git add install.sh scripts/check-installer.py justfile
git commit -m "feat: restore SRX and compliance installation"
```

### Task 7: Restore the README and project roadmap

**Files:**
- Modify: `README.md`
- Modify: `TODO.md`

**Interfaces:**
- Consumes: the exact package and family inventory from Tasks 1 and 6.
- Produces: the public 21-skill catalog, installation documentation, review matrix, and MIT/inspiration statement.

- [ ] **Step 1: Record failing documentation assertions**

Run:

```bash
rg -n 'skills-21|21 / 21|srx-mnha/SKILL.md|pci-ngfw-compliance/SKILL.md|Inspired by' README.md
```

Expected: no complete match set; current README still advertises seven skills.

- [ ] **Step 2: Merge the four-family catalog into the current README**

Use `28c2844:README.md` as content guidance, not as a replacement file. Make
these exact structural changes:

- badges: `skills-21`, `reviewed-21%2F21`, `license-MIT`;
- intro and summary: parsers, SRX operations, cross-vendor tooling, and
  compliance across 21 packages;
- motivation: restore the SRX commit-safety and honest compliance sections;
- reference: four package families with a direct `SKILL.md` link for each of the
  21 explicit package names;
- quality table: parsers 4, SRX 8, tooling 3, compliance 6, total 21;
- installer flags: `--all` installs 21 and `--family` accepts
  `parsers | srx | tooling | compliance`;
- examples: include `--family srx`, `--family compliance`, `srx-nat`, and one
  compliance package;
- auto-trigger text: include SRX operational and compliance requests;
- license section: keep MIT and add this meaning without claiming linked works:

```markdown
External vendor, community, and standards sources inspired and informed parts
of these skills. The repository includes original summaries and direct source
links, not licenses to the external works themselves.
```

- [ ] **Step 3: Restore completed-package roadmap entries**

In `TODO.md`, restore the SRX-operational comparison language and the `Created`
list for the four compliance packages removed by PR #12. Keep current future
recommendations and do not mark unimplemented skills complete.

- [ ] **Step 4: Verify documentation consistency**

Run:

```bash
rg -n 'skills-21|21 / 21|srx-mnha/SKILL.md|pci-ngfw-compliance/SKILL.md|Inspired by' README.md
test "$(rg -o '\./skills/[a-z0-9-]+/SKILL\.md' README.md | sort -u | wc -l)" -eq 21
git diff --check
```

Expected: all assertions pass and README contains direct links to exactly 21
unique skill packages.

- [ ] **Step 5: Commit documentation restoration**

```bash
git add README.md TODO.md
git commit -m "docs: restore the complete skill catalog"
```

### Task 8: Run release verification and review the complete change

**Files:**
- Review: all files changed since `f101461`.
- Modify only if verification finds an in-scope defect.

**Interfaces:**
- Consumes: completed Tasks 1-7.
- Produces: handoff evidence for the exact skills/files changed, commands, sources, unsupported cases, and remaining risk.

- [ ] **Step 1: Run the required offline checks individually**

Run:

```bash
mise exec -- just fmt
mise exec -- just lint
mise exec -- just test
mise exec -- just guard
mise exec -- just integration
mise exec -- just e2e
```

Expected: every command exits 0. Integration prints that real-device validation
is intentionally opt-in and not automated.

- [ ] **Step 2: Run security and release checks**

Run:

```bash
mise exec -- just security
mise exec -- just release-check
```

Expected: Trivy exits 0 and release-check repeats clean lint, schema, guard, and
security results.

- [ ] **Step 3: Audit inventory and provenance invariants**

Run:

```bash
test "$(find skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l)" -eq 21
test "$(rg -l '^license: MIT$' skills/*/SKILL.md | wc -l)" -eq 21
test -z "$(rg -l 'source-derived-summary-local-use|Powered by Higher Logic|Skip main navigation' skills || true)"
test "$(rg -o '\./skills/[a-z0-9-]+/SKILL\.md' README.md | sort -u | wc -l)" -eq 21
git status --short
```

Expected: every assertion exits 0 and status is clean.

- [ ] **Step 4: Review the branch diff and history**

Run:

```bash
git diff --stat main...HEAD
git diff --check main...HEAD
git log --oneline --decorate main..HEAD
```

Confirm no current parser schema changed, no installed skill copy was added, no
secret/customer data appears, and no Apache/mixed-license project file was
restored.

- [ ] **Step 5: Commit any verification-only corrections**

If Step 1-4 required an in-scope correction, stage only those files and commit:

```bash
git add -u
git commit -m "fix: close skill catalog release checks"
```

If no correction was needed, do not create an empty commit.
