# Inspired by: DNS64 and NAT64 on SRX Series

Source: Steven Jacques, Juniper Community TechPost
URL: https://community.juniper.net/blogs/steven-jacques/2025/02/12/dns64-and-nat64-on-srx-series
Retrieved: 2026-05-15

This original note distills design questions prompted by the attributed lab. It
does not reproduce the post or its configuration.

## Design takeaways

- DNS64 synthesizes an IPv6 answer for an IPv4-only destination. The translator
  must use the same NAT64 prefix; `64:ff9b::/96` is the well-known default, not a
  mandatory choice for every deployment.
- On SRX, static NAT with an `inet` translation can extract the embedded IPv4
  destination. Source NAT can then provide an IPv4-reachable source identity.
- Security policy, routing, and zones must be evaluated using the addresses and
  packet family present at each stage of the flow.
- Native IPv6 answers should remain native. DNS64 behavior and DNSSEC validation
  require deliberate resolver design.

## Verification implications

1. Query A and AAAA records through the intended resolver.
2. Confirm the synthesized prefix equals the SRX NAT64 match prefix.
3. Check static- and source-NAT rule counters and the extensive flow session.
4. Validate the IPv4 route, translated-source reachability, and symmetric return.
5. Test native IPv6, IPv4-only, negative, fragmented, and large-packet cases.
