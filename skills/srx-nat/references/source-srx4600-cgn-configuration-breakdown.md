# Inspired by: SRX4600 CGN Configuration Breakdown

Source: Karel Hendrych, Juniper Community TechPost
URL: https://community.juniper.net/blogs/karel-hendrych/2024/11/15/srx4600-cgn-configuration-breakdown
Retrieved: 2026-05-15

This original checklist is inspired by the attributed lab. Its figures and
configuration are not portable capacity guarantees.

## Design takeaways

- Carrier-grade NAT design couples pool sizing, port block allocation, address
  pairing, persistence, timeouts, logging, and hardware acceleration.
- Port blocks can reduce per-session logging, but attribution still needs accurate
  subscriber identity, allocation time, public address, block, and timezone.
- Persistence should be limited to traffic that needs it; broad persistence can
  reduce utilization and change abuse containment.
- Offload eligibility and limits are platform-, service-, and release-specific.

## Verification implications

Establish telemetry for active sessions, pool and port utilization, allocation
failures, block churn, offload state, and log delivery. Load-test steady state,
bursts, exhaustion, routing failure, and HA events. Validate lawful traceability
with a sample public tuple and timestamp before declaring the design ready.
