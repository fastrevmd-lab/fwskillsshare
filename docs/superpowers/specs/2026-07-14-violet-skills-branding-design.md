# Violet skills branding design

**Date:** 2026-07-14
**Repositories:** `fwskillsshare`, `mechubsite`
**Status:** approved

## Goal

Set the `skills` substring inside the `fwskillsshare` project title in the
violet/plum treatment defined by the mechub brand system v1.1, and make the
official brand guide easy to find from both the skill catalog and public
website.

## Changes

### fwskillsshare

- Replace the plain-text README title with theme-aware SVG wordmarks that set
  `skills` to plum-light `#C4B5FD` on dark backgrounds and plum `#7C3AED` on
  light backgrounds. Keep `fw` and `share` in the normal title color.
- Keep the standalone skill-count badge in its original teal treatment.
- Add a concise link to <https://command.mechub.org/branding> in the README
  project-branding area.

### mechubsite

- Wrap only the `skills` substring in the `fwskillsshare` card title with the
  existing `.llm` class, matching the site's other AI-fragment wordmarks.
- Keep the standalone `Skills` metadata badge in its ordinary badge treatment.
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
