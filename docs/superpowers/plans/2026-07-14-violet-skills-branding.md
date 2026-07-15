# Violet Skills Branding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the official mechub violet treatment to the `skills` substring inside the `fwskillsshare` title and link the canonical brand guide from the skill catalog and public website.

**Architecture:** Keep the change presentation-only. The GitHub README uses theme-aware SVG wordmarks; the static website reuses its existing `.llm` fragment class and adds a footer link, with no JavaScript or layout changes.

**Tech Stack:** Markdown, SVG, static HTML, CSS

## Global Constraints

- Use brand plum `#7C3AED` for graphic-scale surfaces and plum-light `#C4B5FD` for text on ink.
- Do not recolor unrelated prose, statuses, or primary actions.
- Link to `https://command.mechub.org/branding` from both requested surfaces.
- Commit directly to each clean `main` branch; do not deploy the website.

---

### Task 1: Update the firewall skills README

**Files:**
- Modify: `README.md:14`

**Interfaces:**
- Consumes: mechub brand system v1.1 color tokens
- Produces: a theme-aware `fw[skills]share` title and canonical brand-guide link

- [ ] **Step 1: Verify the current README treatment**

Run: `python3 scripts/check-readme-branding.py`

Expected before implementation: FAIL because the title wordmark assets are absent.

- [ ] **Step 2: Apply the minimal README change**

Use a `<picture>` inside the centered title to select these assets by theme:

```html
<source media="(prefers-color-scheme: dark)" srcset="docs/assets/fwskillsshare-wordmark.svg">
<img src="docs/assets/fwskillsshare-wordmark-light.svg" width="390" alt="fwskillsshare">
```

Set the `skills` tspan to `#C4B5FD` in the dark asset and `#7C3AED` in
the light asset. Restore the skill-count badge to teal, and retain this sentence:

```markdown
Brand system: [mechub v1.1](https://command.mechub.org/branding).
```

- [ ] **Step 3: Verify and commit fwskillsshare**

Run: `mise exec -- just fmt lint test guard`

Expected: package validator reports 21 skills; all commands exit 0.

Run:

```bash
git add README.md docs/assets/fwskillsshare-wordmark.svg \
  docs/assets/fwskillsshare-wordmark-light.svg scripts/check-readme-branding.py justfile
git commit -m "fix: color skills in project title"
```

### Task 2: Update the mechub public site

**Files:**
- Modify: `/home/mharman/Projects/mechub-site/index.html:223`
- Modify: `/home/mharman/Projects/mechub-site/test_links.py`
- Modify: `/home/mharman/Projects/mechub-site/README.md:7`

**Interfaces:**
- Consumes: existing `--plum` and `--plum-light` CSS variables
- Produces: an `.llm`-marked title fragment and canonical public brand-guide links

- [ ] **Step 1: Verify the current site treatment**

Run: `python3 test_links.py`

Expected before implementation: FAIL because the title is plain text.

- [ ] **Step 2: Add the AI badge modifier**

Change the card title in `index.html` to:

```html
fw<span class="llm">skills</span>share
```

Restore the metadata badge to `<span class="badge">Skills</span>`. Retain the
`brand guide ↗` link in the public footer pointing at
`https://command.mechub.org/branding`, and add the same canonical guide URL to
the repository README while changing “brand system v1.0” to “v1.1”.

- [ ] **Step 3: Verify and commit mechubsite**

Run: `git diff --check && python3 test_links.py`

Expected: no whitespace errors and link tests pass.

Run:

```bash
git add index.html assets/site.css test_links.py
git commit -m "fix: color skills in project title"
```

### Task 3: Publish and confirm

**Files:** None

**Interfaces:**
- Consumes: the two verified local `main` commits
- Produces: synchronized `origin/main` branches

- [ ] **Step 1: Push each repository**

Run `git push origin main` in `fwskillsshare`, then in `mechub-site`.

Expected: both pushes advance `origin/main` without force.

- [ ] **Step 2: Confirm clean synchronized repositories**

Run `git status -sb` in both repositories.

Expected: `main...origin/main` with no modified or untracked files.
