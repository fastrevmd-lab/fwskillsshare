# Inspired by: Address-persistent Source NAT

Source: Juniper Support, KB101182, “Understanding and Using address-persistent in Source NAT on Juniper SRX”
URL: https://supportportal.juniper.net/s/article/SRX-Understanding-and-Using-address-persistent-in-Source-NAT-on-Juniper-SRX
Retrieved: 2026-05-15

This is an independently written operational note inspired by the source. It is
not a copy or substitute for the support article.

## Design takeaways

- `address-persistent` is appropriate when a client must continue using the same
  translated pool address across separately created sessions.
- Persistence reduces the allocator's freedom. Model pool occupancy and failure
  behavior before enabling it for broad populations.
- Do not confuse address persistence with endpoint-independent filtering or
  persistent NAT mappings; each feature solves a different application problem.
- Treat any workaround mentioned in a case-specific support article as a
  hypothesis to validate, not as a universal configuration requirement.

## Verification implications

1. Confirm the intended source-NAT rule is selected and its counter increments.
2. Open multiple sessions from one client and inspect their translated addresses.
3. Test several clients to detect uneven pool use or exhaustion.
4. Check application behavior after failover and after mappings age out.
5. Verify release and platform support in current Juniper documentation.
