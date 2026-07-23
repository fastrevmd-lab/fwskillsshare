# SRX STIG Reporting Contract

## Assessment header

```text
Benchmark: Juniper SRX Services Gateway Y25M01
Source: NIST NCP checklist 657 / resource 12977
Checksum: 9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f
Selected components: NDM V3R3, ALG V3R3[, IDPS V2R1][, VPN V3R2]
Device/context: <safe identifier, model, Junos, logical-system/tenant/node scope>
Assessment date: <date>
Evidence cutoff: <date/time>
Scope gaps: <roles, contexts, or sources not established>
```

## Evidence inventory

| Evidence ID | Class | Source and scope | Collected | Complete/current? | Limitations |
|---|---|---|---|---|---|
| E-N-001 | N | normalized root config | YYYY-MM-DD | partial | parser residuals listed |
| E-R-001 | R | complete redacted display-set export | YYYY-MM-DD | yes | node 0 only |
| E-O-001 | O | version/license/runtime commands | YYYY-MM-DD | partial | IDP status absent |
| E-M-001 | M | approved role and flow matrix | YYYY-MM-DD | yes | owner attested |

Never place secrets, credentials, private keys, PSKs, customer-sensitive raw
configuration, or unredacted incident/evidence content in the report.

## Summary

Provide counts by component, CAT, and status. Reconcile each total to the selected
catalog rule count. Keep Not Reviewed visible; do not omit it from a compliance
percentage.

| Component | CAT I | CAT II | CAT III | Open | Not a Finding | Not Applicable | Not Reviewed |
|---|---:|---:|---:|---:|---:|---:|---:|
| NDM | 8 | 43 | 17 | 0 | 0 | 0 | 68 |

## Rule result

```text
V-ID / SV-ID / JUSX: <all three identifiers>
Component / CAT: <component> / <I|II|III>
Status: <Open|Not a Finding|Not Applicable|Not Reviewed>
Applicability: <decision and supporting evidence IDs>
Evidence: <evidence IDs and exact facts>
Rationale: <why the evidence meets the catalog decision contract>
Compatibility: <verified|verification_required|unsupported; notes>
Mitigation / POA&M: <separate from formal status>
Assessor/AO decision: <if supplied; separate from formal status>
```

## Queues and residuals

- List every Not Reviewed rule with the missing evidence class and next safe
  collection step.
- List unsupported parser/platform cases and source conflicts separately.
- List other-role STIG handoffs outside selected totals.
- Provide POA&M-style remediation candidates with owner/due date only when
  supplied; do not invent governance data.
- State whether current Juniper syntax/platform support was verified.

## Required nonclaim

```text
This report records evidence alignment with the selected DISA Y25M01 SRX rules.
It does not by itself establish device, product, enclave, authorization, or
organizational compliance. Final scope, applicability, risk, and authorization
decisions belong to the qualified assessor and Authorizing Official.
```
