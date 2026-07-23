# Design: srx-disa-stig-compliance

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-07-22.
Author: fastrevmd-lab, Codex.

## Purpose

Add a Juniper SRX-specific DISA STIG assessment skill that is traceable to the
official Y25M01 checklist while remaining honest about evidence gaps. The skill
will route the assessment by SRX role, preserve rule identifiers and CAT
severity, and produce evidence-backed statuses. It will not infer compliance
from configuration alone or turn legacy benchmark examples into unverified
device changes.

The package name is `srx-disa-stig-compliance`. Cross-vendor STIG coverage is
deferred until the SRX implementation proves the evidence and maintenance model.

## Authoritative source pin

Version 1.0.0 is pinned to the following official source:

- NIST National Checklist Program checklist: 657
- NIST record: `https://ncp.nist.gov/checklist/657`
- Checklist release: Y25M01, Final
- DISA package: `U_Juniper_SRX_SG_Y25M01_STIG.zip`
- Official package URL:
  `https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_Juniper_SRX_SG_Y25M01_STIG.zip`
- NIST resource id: 12977
- NIST download record: `https://ncp.nist.gov/checklist/657/download/12977`
- SHA-256:
  `9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f`
- Package contents: four Manual_STIG XCCDF 1.1.4 benchmarks plus overview,
  revision-history, and readme documents

The package contains no OVAL checks or executable assessment automation. The
skill must never combine rule data from different releases. A source update
requires downloading the official artifact, verifying the published digest,
recounting rules and severities, reviewing identifier churn and compatibility
flags, and rerunning catalog validation before changing the pin.

The four component catalogs are:

| Component | Applicability | Release | Rules | CAT I | CAT II | CAT III |
|---|---|---:|---:|---:|---:|---:|
| NDM | Required SRX management/RE baseline | V3R3 | 68 | 8 | 43 | 17 |
| ALG | Required SRX firewall/PFE baseline | V3R3 | 24 | 4 | 20 | 0 |
| IDPS | Conditional when SRX supplies IDPS | V2R1 | 28 | 1 | 27 | 0 |
| VPN | Conditional when SRX supplies network IPsec VPN | V3R2 | 28 | 8 | 20 | 0 |
| **Total** |  |  | **148** | **21** | **110** | **17** |

The nine MAC/classification XCCDF profiles select every rule in their component,
so they are recorded as source metadata rather than treated as meaningful
tailoring. Component role and per-rule applicability drive assessment.

## Design choice

Use a **profile-routed rule catalog**.

This is the middle of three considered approaches:

1. A short summary playbook would match the existing compliance packages but
   would not provide defensible traceability for 148 individual STIG rules.
2. A profile-routed rule catalog preserves rule-level identifiers, evidence
   needs, status logic, compatibility flags, and progressive disclosure without
   claiming that a Markdown package is a scanner. This is the selected design.
3. Full XCCDF/CKL automation would add import/export and scoring machinery before
   the evidence model is proven. The source checks are manual, many require
   operational or assessor evidence, and some contain legacy or contradictory
   guidance, so this is deferred.

## Package structure

```text
skills/srx-disa-stig-compliance/
  SKILL.md
  agents/openai.yaml
  references/
    source-pin.md
    profile-router.md
    status-evidence-model.md
    junos-compatibility.md
    reporting.md
    profiles/
      ndm.md
      alg.md
      idps.md
      vpn.md
```

Repository-level changes add the skill to README inventory and install examples,
add a focused catalog validator under `scripts/`, and wire that validator into
`just test`.

`SKILL.md` remains the concise control plane: intake, profile selection,
assessment workflow, safety, output contract, and reference routing. The four
component catalogs load only when selected. Compatibility and reporting
references load only when needed.

## Profile routing and scope

Assessment begins by establishing device and environment roles before evaluating
rules:

1. Select NDM and ALG for every SRX firewall assessment.
2. Add IDPS only when the device implements the IDPS function.
3. Add VPN only when the device implements network IPsec VPN.
4. Record but do not assess router, switching, remote-access, or other active
   roles whose applicable generic/product STIGs are outside v1.
5. Treat unknown role evidence as a scope gap, not as evidence that a component
   is unused.

An unused component is omitted from selected scope rather than filled with mass
`Not Applicable` statuses. Per-rule N/A handling follows the exact applicability
semantics recorded for that rule.

## Rule-catalog contract

Each derived rule entry contains:

- component and component release;
- V-ID, SV-ID/rule id, and stable `JUSX-*` identifier;
- CAT severity without local downgrading;
- a short original paraphrase of the requirement;
- applicability and allowed N/A semantics;
- required evidence classes;
- normalized-schema predicates when the shared parser can establish them;
- raw-configuration, operational, and manual evidence requirements;
- status decision requirements;
- compatibility state (`verified`, `verification_required`, or `unsupported`);
- source pointer into the pinned XCCDF; and
- related SRX skills for remediation planning.

The catalog will not reproduce DISA titles, check text, or fix text wholesale.
Short derived summaries and exact source pointers provide traceability while the
official artifact remains authoritative.

## Evidence model

No selected component can be completed from normalized configuration alone.
Every evidence item records provenance, collection time, device/context scope,
completeness, and freshness.

| Evidence class | Typical facts |
|---|---|
| Normalized configuration | Zones, interfaces, policies, logging flags, screens, SSH/auth settings, syslog/NTP targets, VPN algorithms and lifetimes, HA and IDP attachment presence |
| Raw configuration | SNMPv3, AAA order, login classes, banners/timeouts, PKI and revocation settings, firewall-filter semantics, complete IDP policy, DPD/anti-replay, platform-specific syntax |
| Operational evidence | Running release, licenses, IDP detector/database state, active logs/alerts, NTP synchronization, SAs/tunnels, counters, active policy and component health |
| Manual/environment evidence | Device roles, topology, PPSM CAL/authorized flows, organization-defined values, retention, DoD PKI/CSfC approval, recipients/processes, redundancy requirements, AO exceptions |

Parser-generated defaults, including an appended `_implicit: true` deny, never
independently prove that an explicit STIG requirement is satisfied. Absence is
interpreted as a failure only when the input is proven complete for the required
evidence surface.

## Status model

Use the four DISA STIG Viewer statuses conservatively:

- **Not Reviewed**: the default when evidence is missing, incomplete,
  ambiguous, stale, unsupported, or outside parser coverage.
- **Not a Finding**: every applicable predicate is supported by complete,
  current evidence.
- **Open**: complete evidence demonstrates that the requirement is not met.
- **Not Applicable**: the rule's explicit applicability condition is proven
  false and that rule permits N/A.

Missing input is never equivalent to missing configuration. Approved mitigation,
POA&M placement, or risk acceptance does not change the technical STIG status.
CAT severity is preserved separately from confidence and evidence completeness.

## Assessment workflow

1. Pin and report the benchmark release and digest.
2. Establish device identity, Junos/platform release, logical-system/tenant
   scope, collection dates, input completeness, and selected roles.
3. Parse raw configuration with `parsing-srx-configs` when available; retain raw
   and operational evidence as distinct sources.
4. Route to NDM+ALG and conditionally IDPS/VPN.
5. Evaluate each selected rule against all required evidence classes.
6. Assign a status only under the conservative status contract.
7. Separate formal STIG status from Junos compatibility warnings and stronger
   current-vendor recommendations.
8. Produce findings, coverage gaps, unsupported cases, and remediation planning.
9. Run a pre-return self-check for source pin, selected-role counts, status
   justification, missing-evidence handling, and prohibited compliance claims.

## Reporting contract

Every report contains:

- artifact name, release, component versions, checksum, and assessment date;
- device/context identity and explicitly selected or excluded roles;
- evidence inventory with provenance, freshness, and completeness;
- counts by component, CAT, and status;
- one row per selected rule with all three identifiers, CAT, status, evidence,
  compatibility flags, and rationale;
- `Not Reviewed` and unsupported-evidence queues;
- source conflicts or release/platform verification requirements;
- POA&M-style remediation candidates without changing formal status;
- residual scope, generic-role handoffs, and assessor decisions; and
- a nonclaim stating that the report does not by itself establish device,
  environment, authorization, or product compliance.

The skill may report “aligned with the selected Y25M01 rule evidence” or similar
bounded language. It must not state that an SRX, enclave, or organization “is
DISA compliant.”

## Junos compatibility and source conflicts

The artifact targets an old minimum Junos generation and contains examples or
requirements that may conflict with current Junos behavior. Formal STIG status
and vendor compatibility are separate fields; the skill never silently rewrites
the benchmark requirement.

The compatibility reference initially flags at least:

- lifetime/default inconsistencies in `JUSX-VN-000002` and `JUSX-VN-000003`;
- proposal/check hierarchy mismatch in `JUSX-VN-000005`;
- incomplete CSfC hierarchy in `JUSX-VN-000023`;
- PKI/AES category mismatch in `JUSX-VN-000026`;
- authorized-flow versus DoS-screen mismatch in `JUSX-VN-000027`;
- legacy Dynamic VPN guidance in `JUSX-VN-000028`;
- SHA-1 allowance versus current Junos deprecation in `JUSX-VN-000025`;
- SNMP SHA-256 release support conflict in `JUSX-DM-000146`;
- explicit password-hash requirement versus current default behavior in
  `JUSX-DM-000136`; and
- release/platform/FIPS-sensitive SSH algorithms and defaults.

These entries use `verification_required`; they do not emit automatic fixes.
Any remediation syntax requires current primary Juniper evidence for the target
platform and release.

## Safety and remediation boundary

The default operating modes are read, parse, analyze, report, plan, and dry-run.
The skill never performs configuration, commit, upgrade, reboot, delete,
failover, or other device mutation on its own.

Remediation output is a plan with rule identifiers, intended control, likely
configuration areas, compatibility caveats, validation commands, rollback
requirements, and the relevant SRX skill. Applying a change requires explicit
approval, target validation, rollback protection, and post-change verification.
Secrets, private keys, credentials, customer configuration, and unredacted
assessment evidence must not be stored in fixtures or output examples.

## Validation design

A focused repository validator will enforce:

- exact source pin and checksum;
- four component releases and rule counts;
- total and per-component CAT counts;
- exactly 148 unique V-IDs, SV-IDs, and `JUSX-*` IDs;
- required fields on every catalog entry;
- no rule mixing across component/source releases;
- NDM+ALG baseline and conditional IDPS/VPN routing;
- conservative status language and `Not Reviewed` default;
- explicit compatibility flags for the known conflict set;
- direct reference reachability and package metadata; and
- prohibited whole-device compliance claims.

Behavior fixtures will cover at least:

- firewall-only routing to NDM+ALG;
- VPN and IDPS role additions;
- unknown-role evidence producing a scope gap;
- missing evidence remaining `Not Reviewed`;
- proven failure becoming `Open`;
- complete proof becoming `Not a Finding`;
- rule-specific N/A handling;
- normalized implicit defaults not proving a rule;
- source-version/hash mismatch failing closed; and
- compatibility conflicts remaining separate from formal status.

The full repository gates remain `just fmt`, `just lint`, `just test`,
`just guard`, `just integration`, `just security`, and `just release-check`.
Integration remains offline and does not contact devices.

## Out of scope for v1

- Other firewall vendors.
- CKL/CKLB, eMASS, or SCAP import/export and round-trip fidelity.
- XCCDF scoring or OVAL execution.
- Automated device remediation or live configuration validation.
- Generic router, switching, or other non-SRX role STIGs.
- AO decisions, POA&M approval, severity overrides, ATO, or DoD product
  approval.
- Validation of every legacy command across every Junos platform, release, and
  FIPS image.

## Known remaining risks

- DISA source drift beyond Y25M01.
- False N/A or false pass if input completeness is overstated.
- Defaults that vary by platform, release, or FIPS image.
- Incomplete IDPS/license/runtime evidence.
- Logical-system or tenant aggregation errors.
- Legacy Dynamic VPN and cryptographic guidance.
- Accidental disclosure in raw evidence or PKI material.
- Manual assessor decisions that cannot be encoded safely.
