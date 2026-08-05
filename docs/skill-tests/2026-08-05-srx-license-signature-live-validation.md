# Skill Test: srx-license-signature-maintenance on live SRX devices

- **Validation date:** 2026-08-05
- **Issue:** [#26](https://github.com/fastrevmd-lab/fwskillsshare/issues/26)
- **Skill under test:** `srx-license-signature-maintenance` **1.0.0**
  (promoted from 0.1.0 draft on the strength of this run)
- **Collection:** live devices over NETCONF via `rust-junosmcp`
- **Mode:** **audit only** — read-only throughout. No `request`-class command,
  no configuration change, no license or signature installation.
- **Outcome:** the read-only surface is validated and four documentation
  defects were found and fixed. The mutating paths remain unexercised.

Device names are lab aliases; entitlement identifiers, serials, and customer
fields are excluded by the skill's own output contract and do not appear here.

## Scope

| Population | Count |
|---|---|
| Logical devices audited | 9 |
| Node records audited | 10 (8 standalone + 1 two-node cluster) |
| Junos releases covered | 24.4R1.9, 25.4R1.12, 26.2R1.7 |

Every device reported `IDP-SIG` and `APPID Signature` installed, `needed 0`,
with date-based expiry — so the entitlement path was exercised against real
`show system license` output on all three releases.

## The finding that justifies the per-node rule

On the two-node cluster, the nodes **disagreed**:

```text
show services application-identification version node 0
  node0:  Application package version: 0
show services application-identification version node 1
  node1:  Application package version: 3929 (Minor)
```

AppID was installed on the secondary and **absent on the primary**, while the
IDP attack database matched on both nodes (3929). Every available shortcut
would have missed this:

| Shortcut | What it would have reported |
|---|---|
| Cluster-level read | a single consistent-looking answer |
| Primary-only read | "AppID not installed" for the whole cluster |
| IDP-only read | "cluster consistent at 3929" |

Only reading **both components on both nodes** surfaced it. This is the
skill's `cluster_evidence_complete` requirement demonstrated against hardware
rather than a fixture.

## Defects found and fixed

### 1. IDP and AppID use different version formats

The skill documented one format and asserted it generally. Live output:

```text
  Attack database version:3929(Minor, Thu Jul 23 13:53:38 2026 UTC)   # IDP
  Application package version: 3929 (Minor)                            # AppID
  Release date: Thu Jul 23 13:53:38 2026 UTC                           # AppID
```

| | IDP | AppID |
|---|---|---|
| Space before `(` | no | **yes** |
| Qualifier contents | severity + timestamp | severity only |
| Build date | inside the qualifier | separate `Release date:` line |

A single parser written to the documented IDP shape would mis-handle AppID.
Fixed in `references/verification-troubleshooting.md`.

### 2. `Application package version: 0` was undocumented

`0` means **no AppID package installed**. Previously the skill had no guidance,
so it would read as a version differing from target rather than as an absence.
Now documented as a gap, not a mismatch.

### 3. `N/A(N/A)` rollback values were undocumented

Devices with no rollback point report `Rollback Attack database version :N/A(N/A)`.
Normalization correctly yields an empty token, but the skill never said so.
Now documented as expected, and as a fact worth reporting (no fallback exists)
rather than a failure.

### 4. A false correlation was avoided

`show system license` reports a `used` counter per feature. It is tempting to
read `IDP-SIG used 1` as "IDP is active". It is not: one device reported
`used 1` while `show security idp status` reported `Policy Name : none`.
The skill now states explicitly that enforcement must be read from the policy
name, never inferred from the license counter.

## No-active-policy condition

Confirmed live and distinguishable:

| Device | `show security idp status` |
|---|---|
| one standalone | `Policy Name : idp-policy-unified` |
| three others, and the cluster primary | `Policy Name : none` |

This is the condition behind the skill's "successful install plus operational
warning" rule — a device can hold current signature content and still enforce
nothing. Now demonstrated rather than asserted.

## Command-surface verification

Carried over from the 2026-08-05 review round and re-confirmed here:

| Command | Result |
|---|---|
| `show system license` | works; `used` / `installed` / `needed` / `Expiry`, permanent vs date-based |
| `show system license node 0` \| `node node0` \| `node 1` \| `node all` | **all syntax errors** — this command has no per-node form |
| `show security idp security-package-version node 0` | works, `node0:`-prefixed |
| `show services application-identification version node 0` | works, `node0:`-prefixed |
| `show services application-identification status` | works |
| `show security idp status` | works |
| `show version invoke-on all-routing-engines` | works, lists both nodes |

## What remains unverified

- **`request system license add`** — never executed. Needs a real entitlement
  file; the staging, transport-probe, install, and cleanup sequence is
  therefore still only offline-tested.
- **`request security idp security-package offline-download` / `install`** —
  never executed. Needs a trusted offline bundle. Extraction, asynchronous
  terminal-state polling, pilot-then-batch rollout, and cluster install
  sequencing remain unexercised against hardware.
- The cluster's node0/node1 AppID mismatch was **left in place**, not repaired —
  fixing it would have meant a Gate B mutation, which was out of scope for this
  read-only run.

Promotion to 1.0.0 reflects a validated read-only surface, a corrected command
set, and an offline behavioral contract whose assertions are mutation-checked.
It does not claim the mutating paths have been run.

## Safety statement

Read-only throughout. Commands issued were `show`-class only, plus `| match`
and `| count` filters. No `request`, `configure`, `commit`, `rollback`, or
`restart` was invoked. The two lab cluster guests were started and later
gracefully shut down; neither was tagged `protected`, and both were returned to
their prior stopped state.
