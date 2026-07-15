# Inspired by: Multi-Node High Availability Basics

- **Author:** Steven Jacques
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the MNHA mental model, ICL/ICD roles, SRGs,
  deployment modes, runtime state, and validation approach.

## Original summary

MNHA pairs independent SRX control planes with selected runtime-state
synchronization. Each node retains its own hostname, interfaces, routing
protocols, management, and configuration. The design therefore uses normal
routing and explicit service ownership rather than treating two devices as one
extended chassis.

The inter-chassis link is a routed path used for runtime-object synchronization.
It must be reachable, correctly sized, and protected according to the network
design. The optional inter-chassis data link supports designs where asymmetric
packets need to reach the node performing session setup or deeper inspection.
ICD use, encapsulation, MTU, and inspection behavior are release and feature
dependent.

Security redundancy groups express service state. SRG0 is associated with
general flow processing, while SRG1 and later groups can own VIP/vMAC service,
IPsec termination, or route-advertisement conditions. Deployment can be routed,
default-gateway, or hybrid:

- routed mode gives each node unique addresses and relies on routing
  convergence;
- default-gateway mode presents a shared gateway identity on an L2 segment;
- hybrid mode combines a shared gateway side with independent routed uplinks.

Runtime synchronization is not complete configuration synchronization. Keep
common security objects, policy, NAT, and service intent aligned through a
controlled configuration-management method while preserving node-local
networking differences.

## Verification implications

- Verify platform, release, node-count, deployment-mode, ICD, IPsec, NAT, and
  asymmetric-flow support in current Juniper documentation or Feature Explorer.
- Test ICL reachability and MTU, runtime synchronization, SRG monitoring,
  routing convergence, session continuity, and failback.
- Validate capacity against the single surviving node; active/active forwarding
  does not remove the post-failure sizing requirement.
- Keep unconfirmed scale values and release-specific feature claims out of the
  production design.

This repository contains an original summary and direct source link, not the
TechPost article or its illustrations.
