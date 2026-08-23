# Gap Model

A gap is a structured record, not prose. Every proposed change to the device exists as a gap first.

## Schema

| Field | Meaning |
|---|---|
| `id` | Stable identifier, namespaced by stage, e.g. `mgmt.ntp-absent` |
| `stage` | Owning stage |
| `severity` | `blocking` (later stages cannot proceed) or `advisory` |
| `depends_on` | Gap ids that must close first |
| `lockout_risk` | Whether closing this gap can cost management reachability |
| `evidence` | What was read that established the gap |
| `proposal` | Candidate configuration, emitted as a diff |

## Namespaces

`access.*`, `mgmt.*`, `zone.*`, `screen.*`, `policy.*`, `factory.*`

**Namespace ownership:**

- `access.*` — Management-plane access stage: root authentication, SSH keys, system services
- `mgmt.*` — Management-plane infrastructure: NTP, DNS, hostname, time zone
- `zone.*` — Security zones and interface placement
- `screen.*` — IDS screen profiles and zone bindings
- `policy.*` — Security policies and application matching
- `factory.*` — Vendor-shipped configuration removal or adoption (Branch platforms only)

Each stage reference (Tasks 8-12) populates its own namespace. The factory-default reference (Task 5) populates `factory.*`.

## Severity values

Exactly two values are valid:

- **`blocking`** — Later stages cannot proceed until this gap closes. Example: `mgmt.ntp-absent` is blocking because accurate timestamps are required for log analysis and troubleshooting in later stages.
- **`advisory`** — Recommended but not required for later stages. Example: a missing timezone setting may be advisory if NTP is configured and working.

## Ordering

Gaps close in dependency order. A gap whose `depends_on` is unsatisfied is not offered.

**Dependency rules:**

1. All `factory.*` gaps depend on management-plane stage completion. Factory-default removal is a lockout-risk change; the replacement management path must be established and verified first.
2. Zone creation may depend on interface configuration.
3. Screen application depends on the screen profile and zone both existing.
4. Policy creation depends on zones existing.

Any gap with `lockout_risk: true` requires the protocol in `write-safety.md` without exception. This protocol includes commit-confirmed with explicit rollback time, pre-commit reachability verification, and post-commit re-verification.

## Idempotency

Re-running against a device with no open gaps produces the verification matrix and proposes nothing. A gap already closed is never re-proposed; assessment reads current state rather than trusting a prior run.

**Implementation:**

The assessment phase (entry-state-assessment.md) runs every time. It reads current device state via the evidence-collection commands and compares against the requirements for each stage. If a requirement is satisfied, no gap is generated for it. If unsatisfied, a gap record is created with the seven required fields.

This means:

- An operator can run the skill, close some gaps manually via CLI, then re-run the skill. Only the remaining gaps are proposed.
- An operator can close gaps in any order (subject to dependency constraints) and the skill adapts.
- No persistent state file is needed; the device itself is the source of truth.

## Reporting a gap that cannot be closed

When a gap is real but out of scope, record it as a gap with a routing target rather than silently dropping it.

**Examples:**

- **Cluster membership detected**: The device is part of a chassis cluster. Gap id: `access.cluster-detected`. Severity: `blocking`. Proposal: "Cluster formation detected. Route to `srx-chassis-cluster-proxmox` for Proxmox-hosted clusters or `srx-mnha` for Multi-Node High Availability. This skill covers single-node and pre-cluster baseline only."

- **Unlicensed feature required**: A required security feature (IDP-SIG or AppID) is not entitled. Gap id: `mgmt.idp-unlicensed` or `mgmt.appid-unlicensed`. Severity: `advisory` (if optional) or `blocking` (if mandatory for the deployment). Proposal: "Feature not licensed. Obtain entitlement from Juniper Networks, then use `srx-license-signature-maintenance` to install and activate."

- **Platform behavior cannot be sourced**: A platform-specific factory-default element was observed but could not be verified against Juniper documentation. Gap id: `factory.unsourced-element`. Severity: `advisory`. Proposal: "Unverified factory-default element found. Review manually and remove if unwanted. Element: [description]. Platform: [model]. This element could not be verified against current Juniper documentation."

The routing target goes in the `proposal` field. The gap is reported to the operator, who can then invoke the correct skill or obtain the missing entitlement.

## Gap record example

```json
{
  "id": "mgmt.ntp-absent",
  "stage": "management-plane",
  "severity": "blocking",
  "depends_on": [],
  "lockout_risk": false,
  "evidence": "show configuration system ntp returned no servers configured",
  "proposal": "set system ntp server 0.pool.ntp.org\nset system ntp server 1.pool.ntp.org"
}
```

This gap has no dependencies, is not a lockout risk, and proposes adding two NTP servers. It blocks later stages because accurate time is required for log correlation and troubleshooting.
