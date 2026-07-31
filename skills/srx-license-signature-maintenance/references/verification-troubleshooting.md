# Verification and Troubleshooting

Reference for the `srx-license-signature-maintenance` skill; load on demand.
Read-only throughout — nothing here changes device state.

## Per-target verification matrix

Run against **every logical device and every node**:

```text
show security idp security-package-version
show services application-identification version
show services application-identification status
show system license
```

| Check | Pass condition |
|---|---|
| IDP/IPS attack database | equals the target version |
| Detector | a version is present |
| AppID package | equals the target version |
| AppID status | active |
| Cluster parity | every node reports matching versions |
| Entitlement | still active after the change |
| Install state | no target reports incomplete or failed |
| Cleanup | temporary installer and license files absent |

**Count logical devices and node records separately.** A fleet report of "34
devices updated" is not evidence about a cluster's 36 node records, and the two
totals should both appear in the output.

## Version-token normalization

Version fields can carry qualifiers:

```text
3929(Minor)
```

Normalize the numeric token for comparison against the target, but **keep the
qualifier in the report**. Stripping it silently loses information the operator
may need; comparing without stripping produces a false mismatch. Do both:
compare on `3929`, report `3929 (Minor)`.

## No active IDP policy

Junos may report that the **data-plane** update was not performed because no
active IDP policy exists. This is not an install failure.

- Classify the package installation as **successful**.
- Attach an **operational warning**.
- **Do not claim IDP enforcement is active.** The signatures are present;
  nothing is inspecting traffic with them until a policy activates IDP.

This distinction matters more than it looks: reporting "IDP updated" on a device
with no active policy tells the operator they are protected when they are not.

## Disabled or unhealthy cluster secondary

A secondary can complete the package installation while its HA state is
disabled or unhealthy. Report these as **two separate facts**:

1. content state — versions verified per node; and
2. HA health — reported as-is, and not repaired by this skill.

Merging them either overstates HA health or understates a successful content
update.

## Troubleshooting table

| Symptom | Likely reading | Response |
|---|---|---|
| Status stays `In progress` past the timeout | Slow device, or a stalled job | Report a timeout as a timeout; stop fan-out; do not guess an outcome |
| Extraction succeeds, install fails | Bundle/platform mismatch, or space | Stop fan-out, preserve sanitized status, follow vendor rollback guidance |
| Post-install version below target | Wrong bundle staged, or a partial install | Re-verify the archive; treat as a stop condition |
| Nodes disagree after install | Secondary did not complete | Verify the secondary directly; do not accept the cluster aggregate |
| AppID active, IDP version unchanged | Only one component installed | Verify each component separately; both must equal target |
| Entitlement lapses mid-run | Date-based grant expired | Stop the signature phase for that device and report |
| Version token has a qualifier | Normal | Normalize for comparison, retain in report |
| Cleanup command returns success but file remains | Path or permission issue | Verify absence explicitly; report residue rather than assuming |

## Reporting discipline

The output table is sanitized by construction. Before returning it, confirm it
contains **no** license keys, raw entitlement blobs, credentials, internal
addresses, or local secret paths — including inside error strings and notes
columns, which is where they most often leak.

State plainly what was **not** verified. A device that could not be reached, a
node that did not answer, or a check that was skipped belongs in the report as
an explicit gap, never as an assumed pass.
