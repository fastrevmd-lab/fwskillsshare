# Violet skills branding design

**Date:** 2026-07-14
**Repositories:** `fwskillsshare`, `mechubsite`
**Status:** approved

## Goal

Identify agent skills as an LLM-facing element using the violet/plum treatment
defined by the mechub brand system v1.1, and make the official brand guide easy
to find from both the skill catalog and public website.

## Changes

### fwskillsshare

- Change the README `skills` shield background from teal to brand plum
  `#7C3AED`; white shield text remains readable because this is a graphic-scale
  treatment.
- Add a concise link to <https://command.mechub.org/branding> in the README
  project-branding area.

### mechubsite

- Give the `Skills` badge on the `fwskillsshare` card a dedicated AI badge
  class using plum-light `#C4B5FD` for text on ink, a plum border, and a subtle
  plum surface.
- Add an official brand-guide link to the public footer.
- Update the site README to identify brand system v1.1 and link its canonical
  guide.

## Boundaries

- Do not recolor unrelated skill prose, status badges, or primary actions.
- Do not change layout, copy beyond the brand references, or deploy the site.
- Commit directly to each repository's clean `main` branch as explicitly
  requested.

## Verification

- Run each repository's existing offline checks and `git diff --check`.
- Confirm both repositories are clean and synchronized after their commits are
  pushed.
- Production deployment remains a separate explicit operation.
