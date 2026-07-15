# Inspired by: Source NAT Part 1

Source: Maxim Tveritnev, Juniper Community discussion
URL: https://community.juniper.net/discussion/source-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx
Retrieved: 2026-05-15

This original design note is inspired by the attributed lab and does not copy its
configuration or prose.

## Design takeaways

- Interface source NAT is simple but couples translations to an interface address.
  Pools make address ownership, capacity, and operational intent explicit.
- Size pools for concurrent translated endpoints and ports, not only subscriber
  count. Include bursts, long-lived sessions, and failure-domain changes.
- Translation does not grant access: a matching security policy and viable route
  are still required.
- A public pool must be routed toward SRX or represented by proxy ARP where the
  adjacent IPv4 network expects layer-2 resolution.

## Verification implications

1. Confirm the rule-set context matches the ingress packet.
2. Check the intended rule and pool counters.
3. Inspect the session's original and translated source tuples.
4. Validate upstream return routing or proxy ARP.
5. Test pool exhaustion alarms and the behavior when no address is available.
