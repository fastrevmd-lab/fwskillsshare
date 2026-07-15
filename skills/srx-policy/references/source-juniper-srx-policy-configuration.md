# Inspired by: Juniper SRX Policy Configuration

Source: Rayka technical training page
URL: https://rayka-co.com/lesson/juniper-srx-policy-configuration/
Retrieved: 2026-05-15

This independent checklist credits the tutorial but does not reproduce it.

## Design takeaways

- Start with business intent, then resolve zones, addresses, applications, action,
  logging, and order. Avoid beginning with copied CLI.
- Prefer reusable global objects. Evaluate global policy for greenfield or migration
  designs, while retaining zone policy where its narrower context is intentional.
- A final deny with appropriate logging makes the residual policy explicit, but log
  volume and platform defaults must be reviewed.

Before activation, display final rule order, run commit checking, use rollback-safe
change control, and validate positive and negative flows with counters and sessions.
