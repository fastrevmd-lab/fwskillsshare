# srx-policy — Branch SRX (SRX345) scope validation

**Date:** 2026-09-12
**Skill:** `srx-policy` (1.2.5 → 1.3.0)
**Scope:** read-only operational commands plus non-activating `commit check`.
Nothing was activated. No policy was committed to the device.
**Authorization:** read-only + `commit check`, explicitly granted.

This closes the long-standing question recorded in `TODO.md` under **Unowned
scope**: whether `srx-policy`'s "non-Branch SRX platforms" exclusion was
justified, and whether it could be widened. `TODO.md` required SRX345 hardware
validation before any widening, on the grounds that widening on documentation
alone would be overclaiming.

## Device

| Device | Model | Junos | Policies | Licences |
|---|---|---|---|---|
| `srx345` | SRX345-dual-ac (physical Branch) | 26.2R1.7 | none configured | **none installed** |

`show system license` reported an empty feature table: no features used,
installed, or needed. That matters for the conclusion below — it means service
attachments could not have been exercised on this device even if validation had
returned a verdict.

## Core policy constructs — all valid on Branch

Each was loaded into a candidate and `commit check`ed, then discarded.

| Construct | Result |
|---|---|
| Zone-pair policy, `from-zone`/`to-zone`, with `then permit` | valid |
| `then log session-close` | valid |
| `then count` | valid |
| Global policy (`security policies global policy`) | valid |
| **`match dynamic-application any`** — the unified-policy construct | valid |
| `default-policy deny-all` | valid |
| `address-book` with `attach zone`, `address`, `address-set` | valid |
| `applications application` + `application-set` | valid |

The unified-policy result is the decisive one. Unified policies are the most
advanced policy construct Junos offers, and they validate on Branch hardware
exactly as they do elsewhere. There is no structural difference in the policy
layer that would justify excluding Branch from core policy design.

## Service attachments — NOT validated

| Construct | Result |
|---|---|
| `then permit application-services security-intelligence-policy` | **no verdict** |
| `then permit application-services application-firewall rule-set` | **no verdict** |
| `then permit application-services idp-policy` | **no verdict** |

All three produced `failed to parse RPC response: unknown element directly
inside rpc-error` — the tool reports this as neither a pass nor a failure, and
it is recorded that way here.

What *can* be said: the configuration schema accepts these statements, because
the returned candidate diff contains the full `application-services` hierarchy
in each case. What cannot be said is whether the device would accept them at
commit, and the device holds no licences for any of the services in question.

So service attachments on Branch remain **unvalidated by this run**, and the
skill continues to qualify them rather than assert Branch support.

## Conclusion

`TODO.md` set out what closing this required: widen the scope for core policy
design, add a licensing/feature-gate reference, and qualify service-attachment
claims per platform. This run supports exactly that split, and no more:

- **Core policy design is widened to include Branch**, on measured evidence
  from SRX345 hardware.
- **Service attachments stay qualified.** Their availability is documented by
  Juniper as licence-gated on Branch as elsewhere, but this run did not exercise
  them, and the test device is unlicensed.

The original exclusion had no recorded rationale anywhere in the repository —
no design document, no reference file, no commit message. This run does not
prove it was wrong at the time it was written; it establishes that the policy
layer behaves the same on Branch today, on 26.2R1.7.

## Not covered

- **No runtime behaviour.** `commit check` validates syntax and constraints; it
  does not activate configuration, so no traffic was matched against any policy.
- **No licensed service was exercised**, and none could be on this device.
- **Chassis-cluster Branch behaviour** was not tested. `srx345` is
  `srx345-dual-ac`, which refers to dual AC power supplies, not clustering.
