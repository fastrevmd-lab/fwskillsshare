# Inspired by: Junos NAT Overview

Source: Juniper Networks, Junos OS documentation
URL: https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/security-nat-overview.html
Retrieved: 2026-05-15

This independently written orientation summarizes concepts used by the skill.
Consult the current product documentation for normative syntax and support.

## Processing model

- SRX provides static, destination, and source NAT for different identity and
  reachability goals.
- Rule-set context can be based on interface, zone, or routing instance. A more
  specific context can take precedence over a broader one.
- Within a selected rule set, the first matching rule controls the result, so
  exceptions belong before general rules.
- A useful diagnostic model is: static NAT, destination NAT, route lookup,
  security-policy lookup, reverse static NAT, then source NAT. Confirm details
  against the documentation for the deployed release.

## Verification implications

1. Record original and expected translated tuples before reviewing syntax.
2. Identify the selected rule set as well as the selected rule.
3. Evaluate route and policy using the correct point in the translation pipeline.
4. Inspect counters and extensive sessions rather than inferring from commit success.
5. Use Juniper Feature Explorer for platform and release capacity claims.
