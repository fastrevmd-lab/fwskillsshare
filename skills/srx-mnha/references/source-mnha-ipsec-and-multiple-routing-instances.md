# Inspired by: MNHA, IPSec and Multiple Routing Instances

- **Author:** James Rathbun
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/james-rathbun/2026/03/30/mnha-ipsec-and-multiple-routing-instances
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs synchronized IPsec design when IKE, underlay,
  tunnel, ICL, and protected routes span multiple routing instances.

## Original summary

An MNHA VPN is a system design rather than an isolated IKE/IPsec stanza. The IKE
gateway must resolve its local and remote endpoints in the intended routing
context, the physical underlay must stay reachable without recursive use of the
tunnel, and the protected prefixes must follow the node that owns the relevant
service redundancy group.

Synchronized VPN service normally ties a shared or floating termination identity
to an SRG. Both nodes need equivalent IKE/IPsec objects, security policy, zones,
and routing intent, while node-local interfaces and next hops remain distinct.
The ICL must carry the runtime state needed for takeover and have capacity for
normal synchronization plus resynchronization after a fault.

Multiple routing instances create several common failure modes: the IKE daemon
looks up the peer in the wrong table, return traffic follows a different node,
route leaking fixes data reachability but not control-plane lookup, or a route to
the peer recursively points into the VPN. Keep endpoint reachability, protected
routes, tunnel-interface placement, and route advertisements explicit.

## Verification implications

- Confirm the target release's routing-instance support for the IKE gateway,
  IPsec VPN, tunnel interface, ICL, and service redundancy group.
- Verify IKE and IPsec SAs, active/warm synchronization state, route tables, and
  sessions on both nodes before and after takeover.
- Test failures of the active node, an ISP path, the ICL, and a protected-side
  route separately.
- Size the ICL with resynchronization and connection-rate headroom; do not copy
  an article-specific utilization percentage as a universal limit.
- Treat complex bow-tie and route-leaking examples as design inspiration until
  reproduced on the target topology.

This repository contains this independently written note and attribution, not
the TechPost text or full configurations.
