# Design: srx-initial-setup and srx-atp-cloud

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-08-20.
Author: fastrevmd-lab, Claude.

## Purpose

Every SRX skill in this repository begins with a device that is already up,
reachable, and zoned. `srx-policy` assumes zones exist. `srx-nat` assumes
interfaces exist. `srx-syslog-logging` assumes you can already log in. Nothing
covers Day-0 and Day-1.

This design adds the missing on-ramp as **two packages**:

- **`srx-initial-setup`** — bring a new or reset SRX from its entry state to a
  reachable, zoned, screened, minimally-policied device, then read entitlements
  and route onward.
- **`srx-atp-cloud`** — enrol an SRX into Juniper ATP Cloud, verify feed and
  telemetry state, and route policy attachment back to `srx-policy`.

They are separate because ATP Cloud enrolment is a distinct workflow with its
own portal dependency, realm/region model, and failure modes. Folding it into
bring-up would make one oversized skill whose two halves fail for unrelated
reasons.

## Scope decisions

These were settled during brainstorming and are inputs to the design, not open
questions.

| Decision | Resolution |
|---|---|
| Package split | Two: `srx-initial-setup` + `srx-atp-cloud` |
| Licensing | **Not duplicated.** `srx-license-signature-maintenance` already owns entitlement and signature work. `srx-initial-setup` performs a read-only entitlement readout and routes all mutating license work to that skill. |
| Device-write posture | Staged approval gates, every remote commit under `commit confirmed` with a rollback timer |
| Feature sets | Report a three-way matrix, then route to sibling skills. Do **not** configure feature sets. |
| Internal architecture | Assess-first convergence (idempotent gap closure), not a linear script |

### Platform scope

Recorded as stated by the repository owner:

| Class | Platforms |
|---|---|
| Branch | SRX300 series, SRX400 series |
| Campus | SRX1600, SRX4120 |
| Datacenter | SRX4300, SRX4700, SRX5000 series |

SRX1500 is end-of-sale and receives few new first-time setups; it is documented
where behavior is shared but is not a validation target.

Requirement #1 from the owner: **handle any factory configuration through to
first deployment.** Factory-default handling is therefore structural to the
design, not a caveat.

> The campus-versus-datacenter tier labels above are the owner's operational
> taxonomy. What the skill actually branches on is entry state, factory-default
> content, and Junos release — never the marketing tier. The tier table exists
> to scope validation targets and set reader expectations.

## Design choice

Use **assess-first convergence**.

Three approaches were considered:

1. **Linear staged pipeline.** Fixed stage order with approval gates, directly
   mirroring the Gate A / Gate B shape in `srx-license-signature-maintenance`.
   Rejected: it assumes an untouched device. Bring-up is the workflow most
   likely to be interrupted and resumed, and re-running a linear script against
   a half-configured device either redoes work or misreads state.
2. **Assess-first convergence.** Always open with a read-only state assessment,
   compute a dependency-ordered gap list, then walk only the gates that are
   actually open. Re-running against a finished device yields "no gaps" plus a
   verification matrix. **Selected.**
3. **Interview-driven generator.** Collect every input up front, emit one
   complete configuration, apply under a single `commit confirmed`. Rejected:
   one large commit is the worst failure mode for bring-up. An error in the
   management stanza costs reachability, and every mistake surfaces at once.

Approach 2 is the only one where factory-default handling is structural: the
Branch pre-built configuration becomes one branch of the assessment and its
removal becomes ordinary gap-list entries, rather than a special case bolted on
to a fixed stage.

## Package structure

```text
skills/srx-initial-setup/
  SKILL.md
  agents/openai.yaml
  references/
    runtime-intake.md
    entry-state-assessment.md
    factory-default-branch.md
    gap-model.md
    stages/
      access-and-recovery.md
      management-plane.md
      interfaces-and-zones.md
      screens.md
      baseline-policy.md
    entitlement-readout.md
    write-safety.md
    verification.md

skills/srx-atp-cloud/
  SKILL.md
  agents/openai.yaml
  references/
    runtime-intake.md
    enrollment.md
    realms-and-regions.md
    verification-troubleshooting.md
```

Both packages follow the existing repository conventions: `SKILL.md` with
frontmatter carrying `name`, `description`, `version`, `author`, `license`, and
`metadata.hermes` tags plus `related_skills`; an `agents/openai.yaml`; and
progressive-disclosure references loaded on demand.

## Entry-state assessment

The assessment is **read-only and unconditional**. It runs before any question
about intent and before any write is proposed.

It classifies the device into exactly one entry state:

| Entry state | Signature | Consequence |
|---|---|---|
| `factory-default` | Vendor-shipped configuration still present | Load `factory-default-branch.md`; removal steps become gap entries |
| `bare` | Minimal or zeroized configuration, no zones or policy | Build every stage from zero |
| `partial` | Some stages complete, others absent | Close only the open gaps |
| `configured` | All stages satisfied | Report the verification matrix; propose no writes |
| `unreachable` | No usable management channel | Emit the console recovery path; propose no writes |

Assessment collects, at minimum: platform and Junos release, chassis-cluster
membership, configured interfaces and their units, security zones and their
`host-inbound-traffic`, screen profiles and zone bindings, security policies,
management-plane state (root authentication, system services, name servers,
NTP), and entitlement state.

> **Exact operational commands are deliberately not fixed in this spec.** Every
> command written into the skill must be confirmed against current Juniper
> documentation or observed on a live device during implementation, per the
> repository's vendor-evidence rule. Commands recalled from memory are not
> acceptable evidence.

### Chassis-cluster interaction

If assessment finds chassis-cluster membership, the skill declares bring-up
out of scope for the cluster-forming steps and routes to
`srx-chassis-cluster-proxmox` for lab clusters or `srx-mnha` for Multi-Node
High Availability. `srx-initial-setup` covers the single-node case and the
pre-cluster baseline only. This boundary is stated in `SKILL.md`, not buried in
a reference.

## Gap model

A gap is a structured record, not prose:

| Field | Meaning |
|---|---|
| `id` | Stable identifier, e.g. `mgmt.ntp-absent` |
| `stage` | Owning stage |
| `severity` | `blocking` (later stages cannot proceed) or `advisory` |
| `depends_on` | Gap ids that must close first |
| `lockout_risk` | Whether closing this gap can cost management reachability |
| `evidence` | What was read that established the gap |
| `proposal` | Candidate configuration, emitted as a diff |

Gaps are closed in dependency order. Any gap with `lockout_risk: true` requires
the write-safety protocol below, without exception.

## Stage contracts

Stages define ordering and ownership. Only open gaps execute.

1. **Access and recovery** — administrative credentials, recovery path,
   confirmation that a console or out-of-band path exists before any
   lockout-risk change. `blocking` for everything downstream.
2. **Management plane** — hostname, domain, name servers, NTP, management
   addressing and its interface choice, system services, and login accounts.
   Interacts with `srx-syslog-logging`, which already owns the fxp0 versus
   revenue-interface and `mgmt_junos` analysis; this stage **routes there**
   rather than re-deriving it.
3. **Interfaces and zones** — revenue interface addressing, zone creation, zone
   membership, and `host-inbound-traffic`. Highest lockout risk in the skill.
4. **Screens** — screen profiles and zone bindings. A conservative starting
   profile is proposed, with each option's rationale and its false-positive
   risk stated. The skill must not present screens as a substitute for policy.
5. **Baseline policy** — the minimum policy needed for the device to pass
   intended traffic and be managed, plus explicit default-deny and logging.
   Anything beyond that minimum routes to `srx-policy`.

Stage 5 stops deliberately short. `srx-policy` owns policy design; this skill
owns only enough policy to make the device usable and reachable.

## Write safety

The repository default is read/plan/dry-run. This skill writes, so the
exception is bounded explicitly.

- Every stage is an approval gate. Approval of one gate never implies approval
  of the next.
- Every proposed change is shown as a configuration diff before it is applied.
- **Every remote commit uses `commit confirmed` with a rollback timer**, and
  the skill confirms reachability before issuing the confirming commit. The
  timer is operator-confirmable with a stated default, and the default is
  chosen to exceed the time the skill needs to verify reachability. The skill
  never issues a bare `commit` on a remote session.
- Any gap with `lockout_risk: true` requires the skill to state, before
  proposing the write, what the operator's recovery path is if reachability is
  lost.
- The skill never proposes a change that removes the management path it is
  currently using without first establishing the replacement.
- Rollback points are recorded so an operator can return to the pre-stage
  state.
- Factory-default removal is treated as a lockout-risk change, because on
  Branch platforms the shipped configuration may be what is currently providing
  the operator's address.

## Entitlement readout and routing

The readout is the three-way matrix. A license counter alone is never treated
as proof a feature is active — `srx-license-signature-maintenance` documented a
live device reporting `IDP-SIG` with `used 1` while `show security idp status`
reported `Policy Name : none`.

| Axis | Source |
|---|---|
| Entitled | Entitlement output |
| Configured | Running configuration |
| Active | Operational status for that feature |

Each feature resolves to one of: `active`, `licensed but not configured`,
`configured but not licensed`, `neither`, or `indeterminate`. `indeterminate`
is a first-class result and must not be rounded to a cleaner one.

Routing table:

| Feature area | Routes to |
|---|---|
| AppID, IDP/IPS entitlement and signature content | `srx-license-signature-maintenance` |
| Security policy, AppFW, NGWF, EWF, SecIntel placement | `srx-policy` |
| ATP Cloud | `srx-atp-cloud` |
| NAT | `srx-nat` |
| Logging to a collector or SIEM | `srx-syslog-logging` |
| Chassis cluster / MNHA | `srx-chassis-cluster-proxmox`, `srx-mnha` |
| IPsec | `srx-ipsec-hub-spoke`, `srx-autovpn-full-tunnel`, `srx-advpn` |

Secret handling follows the existing licensing skill: report entitlement
fields only. License keys, entitlement blobs, license identifiers, software
serial numbers, and customer identifiers never appear in output.

## srx-atp-cloud design

Same shape, smaller scale:

1. **Assess** — current enrolment and connectivity state, read-only.
2. **Intake** — realm and region, which are operator-supplied and cannot be
   inferred.
3. **Enrol** — under an approval gate, with the same commit-confirmed
   protection where enrolment touches configuration.
4. **Verify** — enrolment status, feed state, and telemetry.
5. **Route** — policy attachment to `srx-policy`, which already owns where ATP
   sits relative to deterministic policy.

Naming: the skill is `srx-atp-cloud`. "Sky ATP" is a legacy product name and
appears only as a discovery alias in the description and tags, never as the
current name in body text.

Enrolment mechanics are **not specified here**. They are portal-driven and
region-specific, and must be written from current Juniper documentation
retrieved at implementation time.

## Evidence and sourcing plan

Per repository rules, every vendor claim needs an authoritative source or an
explicit unsupported/uncertain classification.

- Factory-default content per platform class: vendor documentation, recorded
  per platform, with the retrieval date in frontmatter `sources`.
- Screen options and defaults: vendor documentation.
- ATP Cloud enrolment: current Juniper ATP Cloud documentation, retrieved at
  implementation time. Anything not confirmable is marked unverified rather
  than guessed.
- Commands and output shapes: vendor documentation, upgraded to "verified live"
  only where actually observed.

## Validation design

| Target | Reach | Confidence label |
|---|---|---|
| vSRX | Owner's lab, available now | Verifiable live; may carry "verified live" claims |
| **SRX345** | **Owner hardware, available now** | **Verifiable live — the Branch factory-default reference platform** |
| **SRX1600** | **Owner hardware, arriving later** | **Deferred; documentation-sourced until it lands** |
| **SRX4700** | **Owner hardware, arriving later** | **Deferred; documentation-sourced until it lands** |
| SRX300/320/340/380 | Not available | Documentation-sourced, generalized from the SRX345 where the platform genuinely shares behavior |
| SRX4120 / SRX4300 / SRX5000 | Not available | Documentation-sourced only |

This asymmetry is a first-class constraint. Claims validated only against vSRX
must not be presented as validated across the platform matrix. Where behavior
is expected to differ by platform and cannot be confirmed, the skill says so.

The SRX345 substantially reduces the largest risk in this design. Branch
factory-default content — the pre-built zones, the DHCP server, and the default
policy that requirement #1 exists to handle — becomes directly observable
rather than inferred from documentation. Generalizing an SRX345 observation to
the rest of the SRX300/400 line is still an inference and is labeled as one.

### Hardware validation is a deferred final phase

All hardware validation runs **after** the documentation-sourced skill is
complete and passing offline checks, not interleaved with authoring:

- The skill is written and released from vendor documentation and existing
  verified repository references. **No device validation is claimed at 1.0.0** —
  vSRX exercise is itself a validation phase, not a precondition of release.
- SRX345 validation follows as a distinct phase, upgrading Branch claims from
  documentation-sourced to verified-live and correcting whatever it contradicts.
- SRX1600 and SRX4700 validation follows when that hardware arrives, as its own
  phase against the same procedure.

Each hardware phase produces a record under `docs/skill-tests/`, matching the
existing convention set by the 2026-08-05 licensing validation. A phase that
contradicts a documented claim results in a skill revision, not a footnote.

Bring-up validation on real hardware writes to a device. Every hardware phase
runs under the same write-safety protocol the skill itself specifies, on a
device the owner has confirmed is not carrying production traffic, with the
console path confirmed reachable beforehand.

Offline validation for both packages: `just fmt`, `just lint`, `just test`,
`just guard`, `just security`, `just release-check`, all run before handoff.
`scripts/check-skill-packages.py` enforces the 1,024-character per-skill
description limit.

Codex review runs via `scripts/codex-review.sh` with small commits. A run
producing no final `agent_message` is reported as "the gate did not run", never
as a pass.

## Description budget

Combined skill descriptions currently total 8,376 characters across 27 skills,
confirmed by `scripts/check-skill-packages.py`. Two new packages add roughly
700, reaching about 9,076.

`COMBINED_DESCRIPTION_WARN` in that script is **12,000**, so the addition stays
well under the soft budget and **no warning fires**. The combined limit is a
trend signal, not a gate: Codex truncates skill metadata to fit its context
budget and reports what it truncated, and discovery also runs through a dynamic
selector, so the flat concatenated list is a fallback rather than the primary
path.

The binding limit is the **per-skill 1,024-character** description cap, which
Codex enforces and the checker errors on. Each new description must also
contain the literal string `". Use when "` and must not contain angle
brackets.

`Use when` clauses are what lexical discovery matches on, so they are written
for coverage, not brevity. There is no budget pressure to trim them.

## Implementation sequencing

This spec covers two packages, which is more than one implementation plan
should carry. They decompose cleanly and are built in order:

1. **`srx-initial-setup`** first. It is the larger package, it establishes the
   entry-state assessment, gap model, and write-safety protocol that the second
   package reuses, and it is independently useful without ATP Cloud.
2. **`srx-atp-cloud`** second, reusing the assessment and gate patterns proven
   by the first.

Each package gets its own implementation plan and its own release. The shared
write-safety protocol is authored once in `srx-initial-setup` and referenced by
`srx-atp-cloud` rather than restated, so the two cannot drift.

## Out of scope for v1

- Zero Touch Provisioning and autoinstallation.
- Junos software upgrade during bring-up; `srx-license-signature-maintenance`
  and existing upgrade tooling own that.
- Cluster formation, which routes to `srx-chassis-cluster-proxmox` or
  `srx-mnha`.
- Routing protocol configuration beyond the static reachability needed for
  management and the initial uplink.
- Full policy design, which is `srx-policy`.
- Vendor-neutral first-time setup across PAN-OS, FortiGate, and ASA. The
  repository's operational skills are SRX-specific by design, and PAN-OS
  operational depth is already tracked as `palo-operational` in `TODO.md`.
- J-Web-driven setup. The skills are CLI and configuration oriented.

## Known remaining risks

1. **Platform validation asymmetry.** Reduced but not eliminated by the
   SRX345, which makes the Branch factory-default path directly observable, and
   further reduced when the SRX1600 and SRX4700 arrive. The SRX4120, SRX4300,
   and SRX5000 remain documentation-sourced, and generalizing SRX345 behavior
   across the SRX300/400 line remains an inference. Mitigated by explicit
   per-platform confidence labels, not by hedged prose. Because hardware
   validation is deliberately a deferred final phase, the first release ships
   with Branch claims still marked documentation-sourced.
2. **ATP Cloud drift.** Portal-driven enrolment changes without notice and is
   region-dependent. The skill pins retrieval dates and prefers device-side
   verification commands, which are more stable than portal steps.
3. **Factory-default variance.** Shipped configuration differs across platform
   classes and Junos releases. The assessment reads actual state rather than
   assuming a known default, which contains but does not eliminate the risk.
4. **Boundary drift with `srx-policy`.** Stage 5 deliberately stops at a
   minimum baseline. If that boundary blurs, the two skills will give
   conflicting policy advice. The boundary is stated in both `SKILL.md` files.
5. **Write posture precedent.** This is the repository's first skill whose
   primary purpose is device configuration. If the gate-and-confirm protocol is
   weak, it becomes a bad precedent for later skills. It is specified once, in
   `write-safety.md`, and referenced rather than restated.
