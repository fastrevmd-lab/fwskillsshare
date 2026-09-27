## Summary

<!-- What does this PR do, and why? -->

## Type of change

- [ ] New skill
- [ ] Update to an existing skill (`skills/<name>/`)
- [ ] Cross-skill / shared infrastructure (installer, scripts, shared schema, CI, docs)

## Verification

<!-- Exact commands you ran and their result. "Should work" is not verification. -->

```sh

```

## Checklist

- [ ] `just lint` passes (skill packaging/frontmatter, inventory manifest, markdown links, README branding)
- [ ] `just test` passes (fixtures, shared-schema byte-identity, behavioral contracts)
- [ ] If this adds or renames a skill: `skills/inventory.json` is updated, and `install.sh`'s family arrays match it (`python3 scripts/sync-installer-inventory.py --check`)
- [ ] If this touches a `parsing-*` skill's intermediate schema: all five copies stay byte-identical (`python3 scripts/check-shared-schema.py`)
- [ ] Every example command, config snippet, or device output in this change is **synthetic** — no real hostnames, serial numbers, credentials, tokens, or customer configs
- [ ] Any device-changing step the skill describes (commit, upgrade, reboot, delete, failover) still requires **explicit human approval**, and keeps its dry-run/diff, rollback, and post-change verification steps intact — this PR does not let a model output act on a device unsupervised
- [ ] Vendor syntax or standards/compliance claims are backed by a cited source or verified evidence (commit-check output, live-device run, current vendor doc), not assumed
- [ ] No new telemetry, analytics, or outbound network call added

## Anything you're unsure about

<!-- Flag it here rather than hoping review catches it -->
