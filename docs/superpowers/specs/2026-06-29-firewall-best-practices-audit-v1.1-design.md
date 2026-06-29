# Design: firewall-best-practices-audit v1.1 + schema/parser extensions

Status: approved design (brainstorming output), pending implementation plan.
Date: 2026-06-29.
Author: fastrevmd-lab, Claude.

## Purpose

Close the coverage gaps in `firewall-best-practices-audit` v1.0 surfaced by the
real-device test in `docs/skill-tests/2026-06-29-vsrx-production-audit.md`: on a
control-plane-hardened but policy-light SRX (`vSRX-Production`, Junos 25.4R1), the
audit produced **1 finding from 30 checks** because the skill — and the shared
`parsing-*` intermediate schema it consumes — model only a *stateful policy
rulebase*. SRX security also lives in zones / host-inbound-traffic, stateless
control-plane (RE) filters, screens, system & SSH services, auth hardening, and
configured-but-unreferenced security services. v1.1 makes those visible.

## Decisions (from brainstorming)

1. **Modeling — generic fields, SRX populates first.** The new concepts are
   cross-vendor in disguise (management-plane services, device/control-plane
   protection, host-inbound/management ACLs, auth hardening). Add **generic**
   fields to the shared intermediate schema; the SRX parser populates them now;
   the other three parsers emit them empty so dependent checks skip gracefully.
   Keeps the audit skill vendor-neutral; forward-compatible.
2. **Output philosophy — findings-only, flag absence.** Keep the audit a findings
   list that never claims "secure". A *missing* control (no screen on an external
   zone, no RE filter, `ssh root-login allow`) is a finding; a *present* good
   control yields no finding (the audit does not enumerate strengths). No
   "observed controls" section.
3. **Scope — full set, schema-first.** All schema extensions + all new checks ship
   in this v1.1; the plan sequences schema/parser changes first, then the checks
   that consume them.

## Scope / sequencing

One coherent release, built schema-first:

1. Extend the shared intermediate schema (generic fields).
2. Extend the `parsing-srx-configs` parser to populate them.
3. Add the new checks to `firewall-best-practices-audit`.
4. Rebuild the worked example to demonstrate the new checks firing.
5. Re-run the live `vSRX-Production` audit via `rust-junosmcp` to confirm the
   regression is closed (catalog now exercises many checks, not 1).

## 1. Schema extensions (generic, vendor-neutral)

Added to the canonical schema doc
`skills/parsing-srx-configs/references/intermediate-schema.md`, then propagated
byte-identical to the cisco/fortinet/palo copies (see §4). All fields are
**optional/additive**: a parser that does not populate a field omits it or emits
an empty value, and the dependent check skips with a noted caveat.

- `system.ssh` — object: `{ root_login: "allow"|"deny"|"deny-password"|null,
  rate_limit: int|null, ciphers: [string], protocol_version: string|null,
  connection_limit: int|null }`.
- `system.auth` — object: `{ password_policy: { min_length: int|null, complexity:
  string|null }, login_lockout: { tries: int|null, lockout_period: int|null },
  root_authentication_present: bool }`.
- `system.control_plane_protection` — object: `{ re_filter_present: bool,
  applied_to: [string] }`. SRX = stateless `firewall filter` applied to `lo0.0`
  input; documented generic analogs: Cisco CoPP, Palo/Forti management profiles.
- `zones[].screen` — string|null: the bound screen / DoS-protection profile name
  for that zone (SRX `screen <name>`). Absent/null when no screen is bound.
- `security_services` — object of presence flags: `{ app_id: bool, idp: bool,
  secintel: bool, aamw: bool, utm: bool }`. Drives the
  configured-but-unreferenced check.
- `zones[].host_inbound` — **already present and populated** by the SRX parser;
  reused as-is, not added.

Schema doc must state, for each new field, that population is vendor-parser
dependent and that absence means the dependent audit check is skipped.

## 2. Parser extensions (`parsing-srx-configs`, → v1.2.0)

Promote the following from `residual_raw` into the structured fields above:

- **SSH options** — `system.services.ssh` `root-login`, `rate-limit`,
  `ciphers`/`protocol-version`, `connection-limit` → `system.ssh`.
- **Auth hardening** — `system.login` `password { minimum-length / change-type /
  minimum-changes }`, `retry-options { tries-before-disconnect / lockout-period }`,
  and `system.root-authentication` presence → `system.auth`.
- **Control-plane protection** — detect a stateless `firewall { family inet filter
  <name> }` applied as `lo0` unit `family inet filter input <name>` →
  `system.control_plane_protection { re_filter_present: true, applied_to:
  ["lo0.0"] }`.
- **Screens** — `security.screen.ids-option.<name>` presence and each
  `zones[].screen` binding → populate `zones[].screen`.
- **Security services** — presence of `services { application-identification /
  advanced-anti-malware / security-intelligence }` and `security { idp / utm }` →
  `security_services` flags.

Update the parser's extraction pipeline sections and the
`config-format.md`/`parsing-patterns.md` references as needed. The implicit
default-deny rule the parser already appends stays; the new
`security_services`/`zones` data feeds the audit's cross-object checks.

## 3. New audit checks (`firewall-best-practices-audit`, → v1.1.0)

Added to `references/check-catalog.md` (with id, detected condition, schema fields,
default severity, confidence), surfaced in the body where relevant, and given a
remediation family in `references/remediation-patterns.md` (SRX snippet
authoritative; note the cross-vendor mapping where the concept applies).

| ID | Fires when | Severity | Confidence |
|----|-----------|----------|------------|
| SEC-SSH-ROOT-LOGIN | `system.ssh.root_login == "allow"`, or weak ciphers / no rate-limit | High | definitive |
| SEC-SERVICES-UNREFERENCED | a `security_services` flag is true but no `security_policies[].security_profiles` reference it | High | heuristic (depends on profile capture) |
| SEC-ZONES-NAT-NO-POLICY | `zones`/`nat_rules` present but `security_policies` is empty or none reference the zones | High | heuristic |
| SEC-EMPTY-POLICYSET | `security_policies == []` — emit explicit coverage warning; distinguish default-deny-by-design from partial config / logical-system / tenant | Medium | definitive |
| SEC-HOST-INBOUND-EXPOSURE | management/sensitive services in `zones[].host_inbound` on an untrusted/data zone | Medium | heuristic |
| SEC-NO-SCREEN | an external/untrust zone has no `zones[].screen` bound (screen-binding absence is definitive; classifying a zone as "external" is heuristic — key off zone name conventions and the default-route-facing interface) | Medium | heuristic |
| OPS-LOG-COMPLETENESS | no remote security-log stream/host target present | Medium/Info | definitive |
| SEC-AUTH-HARDENING | missing/weak `system.auth.password_policy` or `login_lockout` | Medium/Low | definitive |
| SEC-IPV6-POSTURE | interfaces with `inet6` addresses but no corresponding v6 controls/policies | Low | heuristic |

Refine the existing **SEC-NO-DENY-ALL**: account for the SRX implicit-deny and
frame the recommendation as adding an explicit *logged* deny-all for visibility,
not just enforcement.

Every check must follow v1.0 conventions: graceful degradation (skip + list when a
field is absent), definitive vs heuristic labeling, no "secure"/"compliant" claim,
no compliance-control mapping.

## 4. Shared-schema handling

The intermediate schema is intentionally duplicated byte-identical across the four
`parsing-*` skills (canonical = `parsing-srx-configs`; policy in
`skills/SHARED-SCHEMA.md`). Procedure:

1. Edit only the canonical copy
   `skills/parsing-srx-configs/references/intermediate-schema.md`.
2. Copy its exact content to the cisco, fortinet, and palo
   `references/intermediate-schema.md`.
3. Run `python3 scripts/check-shared-schema.py` — it must report all 4 identical.

The new fields are additive, so the cisco/fortinet/palo parsers remain valid
without immediately populating them (their checks skip).

## 5. Worked example + live regression test

- Rebuild `references/example-audit.md` (or add a second worked example) from a
  `vSRX-Production`-shaped schema so the example demonstrates the new checks firing
  (at minimum SEC-SSH-ROOT-LOGIN, SEC-SERVICES-UNREFERENCED,
  SEC-ZONES-NAT-NO-POLICY, SEC-EMPTY-POLICYSET, SEC-NO-SCREEN). Every finding id
  must exist in the catalog; no fabricated data.
- Final plan step: re-run the live `vSRX-Production` audit through
  `rust-junosmcp` (`get_junos_config` → `parsing-srx-configs` →
  `firewall-best-practices-audit`) and confirm the catalog now produces multiple
  findings (the regression the test write-up requires). Capture the result; secrets
  redacted.

## 6. Housekeeping

- Tick the 14 v1.1 items in `TODO.md` (PRIORITY PROJECT section) as completed.
- Note v1.1 / v1.2.0 versions in `README.md` where skill versions or the schema
  are described.
- Re-sync the changed skills into `~/.claude/skills/` (user-scoped install).
- Validate: all skills' frontmatter + reference pointers resolve; shared schema in
  sync.

## Out of scope (YAGNI)

- Populating the new fields in the cisco/fortinet/palo parsers (they stay empty;
  a later effort generalizes them).
- An "observed controls / strengths" section (findings-only stands).
- Compliance-framework mapping (owned by the `*-ngfw-compliance` skills).
- Auto-remediation or live config push.
