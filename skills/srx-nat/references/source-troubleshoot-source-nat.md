# Inspired by: Troubleshoot Source NAT

Source: Juniper Support, KB21611
URL: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Source-NAT
Retrieved: 2026-05-15

This original diagnostic checklist is inspired by the support workflow. It does
not copy the article.

## Diagnostic sequence

1. Record the original five-tuple, ingress context, intended egress, and expected
   translated source.
2. Verify route and security policy, then identify the selected source-NAT rule set
   and first matching rule.
3. Check rule and pool counters, available addresses and ports, and allocation errors.
4. Inspect the extensive session for the translated tuple and selected policy.
5. Confirm the upstream network routes the pool back to SRX or resolves it through
   the intended proxy ARP design.
6. Validate return traffic and asymmetric-routing risks.
7. If necessary, collect a tightly filtered flow trace and remove it promptly.

Test no-NAT exceptions separately because a broad earlier rule can make an otherwise
correct source-NAT rule unreachable.
