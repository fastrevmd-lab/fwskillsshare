# Inspired by: Configuring Security Policies in Junos OS

Source: Juniper Networks, Junos OS documentation
URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html
Retrieved: 2026-05-15

This original summary is an orientation, not a copy of the product documentation.
Use the linked current page for normative syntax and release behavior.

## Policy model

- Policies match traffic by context, addresses, applications, and optional advanced
  criteria, then apply permit, reject, deny, logging, counting, or security services.
- Evaluation order is operational behavior. Put explicit exceptions before broader
  matches and re-display the final order after every insertion or migration.
- Address objects, application objects, zones, routes, NAT, and policy all participate
  in the packet path; a correct policy cannot compensate for a wrong route or zone.
- Global and zone policies have distinct scopes and precedence. Choose intentionally.

Validate with commit checking, policy hit counts, sessions, logs, and controlled
positive and negative traffic tests.
