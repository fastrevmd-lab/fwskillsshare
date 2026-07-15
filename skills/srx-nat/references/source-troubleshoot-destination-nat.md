# Inspired by: Troubleshoot Destination NAT

Source: Juniper Support, KB21839
URL: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Destination-NAT
Retrieved: 2026-05-15

This is an independently written diagnostic checklist, not a copy of the support
article.

## Diagnostic sequence

1. Record the received source, destination, protocol, port, ingress interface, and
   routing instance.
2. Identify the selected destination-NAT rule set and first matching rule; confirm
   its counter changes for a controlled test.
3. Resolve the translated destination, route lookup, egress zone, and security
   policy in that order.
4. Confirm the real server has a symmetric path through SRX, or add a deliberately
   scoped source-NAT design where symmetry cannot otherwise be guaranteed.
5. Inspect the extensive session, pool state, ARP/ND as relevant, and packet captures.
6. Use narrowly filtered flow traceoptions only when counters and sessions do not
   explain the drop; remove them after collection.

Commit success proves syntax, not packet-path correctness.
