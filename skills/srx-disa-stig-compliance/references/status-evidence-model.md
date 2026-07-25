# Status and Evidence Model

## Evidence classes

- **N — normalized configuration:** shared-schema fields produced by
  `parsing-srx-configs`.
- **R — raw configuration:** complete source syntax, residuals, and constructs
  not represented precisely by the schema.
- **O — operational evidence:** running software, licenses, installed packages,
  active policy/state, logs, counters, alerts, time sync, SAs, or health.
- **M — manual/environment evidence:** role, topology, authorized flows,
  organization-defined values, retention, approvals, recipients, response
  procedures, external systems, or AO decisions.

Every evidence item needs an identifier, provenance, device/context scope,
collection time, freshness judgment, and completeness judgment. Evidence for one
node, tenant, logical system, or time period does not automatically cover another.

## Status matrix

| Evidence state | Status |
|---|---|
| missing, partial, stale, ambiguous, unsupported | Not Reviewed |
| complete evidence proves failure | Open |
| complete evidence proves satisfaction | Not a Finding |
| explicit applicability proven false and rule permits N/A | Not Applicable |

Not Reviewed is the fail-closed default. Missing input is not missing
configuration. A rule can require several evidence classes; all required
predicates must be proved before Open or Not a Finding.

## Absence and parser-default semantics

- A complete raw configuration can prove an explicit setting is absent only
  when the parser/source scope and inheritance are understood.
- A partial stanza, filtered command, normalized projection, or failed command
  cannot prove absence.
- A parser-added `_implicit: true` rule describes an effective vendor default;
  it does not prove an explicit policy, logging, review, or documentation
  requirement.
- A Junos default can be relevant evidence only when the formal rule accepts
  effective behavior and the platform/release default is verified. Otherwise
  retain Not Reviewed or Open according to the pinned rule.

## Applicability and mitigation

Use Not Applicable only when the catalog row allows it and evidence proves the
condition false. Unknown applicability stays Not Reviewed. An unselected
component is omitted from scope; it is not a collection of N/A rules.

An approved mitigation does not change the technical status. Risk acceptance,
POA&M, compensating control, waiver, and AO decision are separate report fields.
CAT severity also remains unchanged.

## Synthetic decision examples

1. Only normalized SSH settings were supplied for a rule that also requires
   operational login/audit proof: **Not Reviewed**.
2. A complete scoped raw configuration proves an applicable required leaf is
   absent: **Open**.
3. Complete raw plus operational evidence proves all applicable predicates:
   **Not a Finding**.
4. The rule explicitly permits N/A when user-role firewalling is unused, and
   complete architecture/configuration evidence proves it unused:
   **Not Applicable**.
5. The owner says a role is probably unused but no configuration or architecture
   proof exists: unknown applicability, therefore **Not Reviewed**.
