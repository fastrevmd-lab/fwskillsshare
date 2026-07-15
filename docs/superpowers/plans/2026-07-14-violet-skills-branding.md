# Violet Skills Branding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the official mechub violet treatment to the `Skills` label and link the canonical brand guide from the skill catalog and public website.

**Architecture:** Keep the change presentation-only. The GitHub README uses a static Shields badge color; the static website adds one reusable AI badge modifier and a footer link, with no JavaScript or layout changes.

**Tech Stack:** Markdown, static HTML, CSS, Shields.io

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
- Produces: violet `skills` badge segment and canonical brand-guide link

- [ ] **Step 1: Verify the current README treatment**

Run: `rg -n "skills-21|command.mechub.org/branding" README.md`

Expected: the badge uses teal `0D9488`; no branding URL is present.

- [ ] **Step 2: Apply the minimal README change**

Use this badge URL so the label surface is plum and the count remains ink:

```html
<img alt="skills" src="https://img.shields.io/badge/skills-21-262B38?labelColor=7C3AED">
```

Add this sentence directly after the badge block:

```markdown
Brand system: [mechub v1.1](https://command.mechub.org/branding).
```

- [ ] **Step 3: Verify and commit fwskillsshare**

Run: `mise exec -- just fmt lint test guard`

Expected: package validator reports 21 skills; all commands exit 0.

Run:

```bash
git add README.md
git commit -m "docs: apply violet skills branding"
```

### Task 2: Update the mechub public site

**Files:**
- Modify: `/home/mharman/Projects/mechub-site/index.html:223`
- Modify: `/home/mharman/Projects/mechub-site/assets/site.css:135`
- Modify: `/home/mharman/Projects/mechub-site/README.md:7`

**Interfaces:**
- Consumes: existing `--plum` and `--plum-light` CSS variables
- Produces: `.badge.ai` visual modifier and canonical public brand-guide links

- [ ] **Step 1: Verify the current site treatment**

Run: `rg -n "badge.*Skills|command.mechub.org/branding|brand system v1" index.html README.md assets/site.css`

Expected: `Skills` has only the base badge class; no public guide link exists; the README says v1.0.

- [ ] **Step 2: Add the AI badge modifier**

Add to `assets/site.css` after `.badge.teal`:

```css
.badge.ai {
  color: var(--plum-light);
  border-color: rgba(124,58,237,.5);
  background: rgba(124,58,237,.09);
}
```

Change the card label in `index.html` to:

```html
<span class="badge ai">Skills</span>
```

Add a `brand guide ↗` link to the public footer pointing at
`https://command.mechub.org/branding`, and add the same canonical guide URL to
the repository README while changing “brand system v1.0” to “v1.1”.

- [ ] **Step 3: Verify and commit mechubsite**

Run: `git diff --check && python3 test_links.py`

Expected: no whitespace errors and link tests pass.

Run:

```bash
git add README.md index.html assets/site.css
git commit -m "docs: apply violet skills branding"
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
