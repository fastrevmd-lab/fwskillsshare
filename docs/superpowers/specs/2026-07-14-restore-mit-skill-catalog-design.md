# Restore the MIT Skill Catalog

## Objective

Restore the fourteen skill packages removed by PR #12, return the repository to
a 21-skill catalog, and license all original repository content under MIT. Keep
the operational value of the deleted skills without republishing copied vendor,
community, or standards pages as though the project owned them.

## Recovery source

Use commit `28c2844` (the last `main` commit before PR #12) as the recovery
source. Restore package content selectively rather than reverting PR #12 or
replacing current files wholesale. This preserves later changes, including the
current MIT project license and direct README links to each `SKILL.md`.

Restore these SRX packages:

- `srx-advpn`
- `srx-autovpn-full-tunnel`
- `srx-dynamic-ip-feed`
- `srx-ipsec-hub-spoke`
- `srx-mnha`
- `srx-mpls-in-flow`
- `srx-nat`
- `srx-policy`

Restore these compliance packages:

- `cis-controls-ngfw-compliance`
- `cmmc-nist-800-171-ngfw-compliance`
- `hipaa-ngfw-compliance`
- `iso27001-ngfw-compliance`
- `pci-ngfw-compliance`
- `soc2-ngfw-compliance`

## Package and licensing design

Restore each package's `SKILL.md`, `agents/openai.yaml`, and original supporting
references. Set each restored `SKILL.md` frontmatter license to `MIT` and retain
the existing project author attribution.

Treat third-party material as inspiration and evidence, not repository-owned
content:

- Delete raw or near-verbatim page dumps recovered from Git history.
- Replace useful page-dump references with concise, independently written
  `Inspired by` notes.
- Record the source title, author or publisher when known, direct URL, and
  retrieval date in each note.
- Summarize only the facts, constraints, and verification implications needed
  by the skill. Do not reproduce article prose, navigation, comments, tables,
  diagrams, or long command listings.
- Preserve short product names, protocol terms, public control identifiers, and
  command syntax when necessary for interoperability or verification.
- Prefer authoritative vendor and framework sources for technical and
  compliance claims. Classify claims as unsupported or uncertain when they
  cannot be verified.

Original repository-authored playbooks, field notes, mappings, examples, and
concise summaries may remain after review. All packaged files must be compatible
with distribution under the repository's MIT license. The README will explain
that external sources inspired and informed the work but are not included or
licensed by the project.

## Catalog integration

Update `README.md` by merging the useful pre-deletion catalog content into the
current README rather than restoring the old file wholesale:

- Change catalog and review counts from seven to 21.
- Restore the SRX operational and compliance families.
- Add all fourteen direct links to their `SKILL.md` files.
- Restore the SRX and compliance motivation, usage, and installation examples.
- Keep the single MIT license presentation and current trademark disclaimer.
- Add concise `Inspired by` provenance language without reviving the deleted
  Apache license or obsolete mixed-license notice.

Update `install.sh` to restore the SRX and compliance arrays and family
selection. All totals, help text, interactive selection, examples, and allowed
family errors must consistently describe 21 packages across four families.

## Validation design

Strengthen `scripts/check-skill-packages.py` before restoring the packages so
the initial failing result demonstrates the missing catalog:

- Require exactly 21 skill packages.
- Require every package to declare `license: MIT`.
- Continue checking names, descriptions, authors, versions, metadata, referenced
  files, Codex UI metadata, line limits, and the discovery-character budget.
- Reject the obsolete `source-derived-summary-local-use` marker.
- Reject recognizable raw page-dump boilerplate retained under skill
  references while allowing concise original source notes.

Use disposable install targets to verify `--all`, `--family srx`, and
`--family compliance` without changing installed user skills. Ensure unknown
families and unknown skills still fail safely.

Run all repository-required checks before handoff:

```text
just fmt
just lint
just test
just guard
just integration
just e2e
just security
just release-check
```

`just integration` remains offline and must not contact a firewall. No live
device changes, commit checks, upgrades, failovers, or real-device validation
are part of this restoration.

## Acceptance criteria

- The repository contains exactly 21 portable skill packages.
- All fourteen deleted packages are restored and discoverable.
- Every `SKILL.md` declares `license: MIT`.
- No raw third-party page dumps or obsolete local-use license markers remain.
- All external inspiration is represented by concise original notes and direct
  attribution links.
- README inventory, installer inventory, and filesystem inventory agree.
- SRX and compliance families install successfully into disposable paths.
- Shared parser schemas remain byte-identical.
- Every required offline, security, and release command passes, or any external
  tooling limitation is reported with its exact output.

## Risks and boundaries

Rewriting copied extracts can accidentally remove a useful caveat. Mitigate
that risk by comparing each replacement note with the consuming `SKILL.md`,
retaining only facts the skill actually needs, and preserving direct source
links for deeper reading. Do not expand feature behavior during restoration;
separate factual corrections required for licensing or validation from future
skill enhancements.

MIT labeling covers original repository content only. It does not grant rights
in external websites, standards, product documentation, trademarks, or linked
materials.
