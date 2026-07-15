# Inspired by: SRX340 NAT Hairpinning

Source: Juniper Community discussion
URL: https://community.juniper.net/discussion/srx340-nat-hairpinning
Retrieved: 2026-05-15

This independently written troubleshooting note is inspired by the discussion. It
does not reproduce participant answers.

## Design takeaways

- An internal client using a server's public address must be eligible for the same
  destination-NAT mapping; include the internal ingress context deliberately.
- Hairpin source NAT is commonly needed so the server returns through SRX instead
  of replying directly to the client with an unexpected source address.
- The translated flow may remain in one zone. An explicit same-zone security policy
  can therefore be part of the solution.
- Split-horizon DNS may be simpler when clients do not require public-address parity.

## Verification implications

Confirm the destination-NAT and source-NAT rule counters both increment. Inspect an
extensive session for both translated directions, verify the selected same-zone
policy, and capture client/server traffic if return-path symmetry is uncertain.
