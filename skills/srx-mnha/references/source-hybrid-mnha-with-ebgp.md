# Inspired by: Hybrid MNHA with eBGP

- **Author:** James Rathbun
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs hybrid-mode route steering with eBGP, BFD,
  monitored objects, and security redundancy group state.

## Original summary

Hybrid MNHA combines a shared L2-facing gateway on one side with independent
routed uplinks on the other. The client or server segment follows a VIP/vMAC
owned by an active SRG, while both SRX nodes can maintain their own eBGP control
planes toward upstream routers.

Routing policy should express the same service preference as the SRG. The
preferred node advertises the protected prefix with a better attribute; the
backup either advertises a less-preferred path or withholds the route according
to the design. BFD and interface monitoring can influence SRG state, but route
policy must consume a stable, observable condition and include a final reject
to avoid leaking unintended prefixes.

The routing and SRG mechanisms do not replace each other. SRG ownership controls
the shared service identity; BGP controls reachability to that identity. A
design must account for both directions so failover does not produce a VIP on
one node while upstream traffic still prefers the other.

## Verification implications

- Verify the exact SRG condition syntax and routing-policy evaluation on the
  target Junos release.
- Confirm BFD transitions, interface-monitor weights, and route advertisements
  independently before combining them.
- Compare both nodes' RIB, FIB, advertised routes, VIP ownership, ARP state,
  sessions, and runtime synchronization during failure and recovery.
- Test failback as carefully as failover; avoid oscillation when links or BFD
  sessions flap.
- Treat topology-specific timers and attributes from the article as examples,
  not universal production values.

This repository contains an original design summary and source link, not the
TechPost prose, diagrams, or complete lab configuration.
