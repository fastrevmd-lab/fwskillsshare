# Inspired by: Global Policy Overview

Source: Juniper Networks, Junos OS documentation
URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-global-policies.html
Retrieved: 2026-07-22

This independently written orientation does not replace the normative documentation.

## Design takeaways

- Global policies can express intent across multiple zone pairs and reduce duplicated
  rules. Repeated `match from-zone` and `match to-zone` statements are documented set
  syntax, but multizone grouping is safe only with identical criteria and action.
- Juniper documents lookup order as intra-zone, inter-zone, then global. Regular
  policies therefore must be removed or deactivated at an approved migration cutover
  after parity checks, or matching legacy rules will shadow the global table.
- Centralization magnifies ordering mistakes. Exceptions, broad permits, and final
  denies need deterministic placement and regression tests.
- Junos supports both models; this skill enforces global policy as its generated-output
  default and requires an explicit, scoped opt-out before emitting zone-pair policy.

Display the effective configuration and policy order, then test representative zone
pairs, excluded pairs, exceptions, and default-deny behavior with counters and logs.
