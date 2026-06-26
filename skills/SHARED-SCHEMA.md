# Shared Firewall Intermediate Schema Policy

The four `parsing-*` skills intentionally carry a copy of the same vendor-neutral intermediate schema at:

- `skills/parsing-cisco-configs/references/intermediate-schema.md`
- `skills/parsing-fortinet-configs/references/intermediate-schema.md`
- `skills/parsing-palo-configs/references/intermediate-schema.md`
- `skills/parsing-srx-configs/references/intermediate-schema.md`

Why duplicate instead of linking one file:

1. Skills are often copied individually into `~/.claude/skills/` or `~/.hermes/skills/devops/`.
2. A single skill must remain self-contained when installed alone.
3. Hermes linked-file discovery expects support files under each skill's `references/`, `templates/`, `scripts/`, or `assets/` directory.

Maintenance rule:

- Treat `skills/parsing-srx-configs/references/intermediate-schema.md` as the canonical editing copy.
- After changing it, copy the same content to the Cisco, Fortinet, and Palo Alto parsing skills.
- Run `scripts/check-shared-schema.py` before committing to confirm all schema copies are byte-identical.

If the schema diverges intentionally for a vendor, do not edit `intermediate-schema.md` differently. Keep the shared schema identical and put vendor-specific extensions or caveats in that skill's `references/parsing-patterns.md` or SKILL.md body.
