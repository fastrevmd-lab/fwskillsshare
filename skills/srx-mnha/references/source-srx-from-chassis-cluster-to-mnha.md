# Inspired by: SRX clustering—from Chassis Cluster to MNHA

- **Author:** Laurent Paumelle
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the architectural comparison and staged
  migration from shared chassis-cluster constructs to independent MNHA nodes.

## Original summary

Chassis cluster presents two devices as one logical chassis with shared
configuration, extended interface numbering, redundant Ethernet interfaces,
and active/backup control-plane behavior. MNHA keeps each SRX independent and
adds synchronization and service-ownership mechanisms around ordinary routed
or L2/L3 network designs.

A migration must translate intent instead of renaming commands. For every
`reth`, determine what each independent node will connect to and whether the
target should use a node-local physical interface, a node-local aggregate, or a
shared VIP/vMAC service. A cluster LAG spread across both chassis does not prove
that either upstream switch accepts a standalone-node aggregate after the split.

Replace cluster-specific management and routing assumptions with per-node
addresses and adjacencies. Decide which configuration is common, which remains
node-local, how it will be synchronized, and how ICL/ICD reachability is
provided. Translate redundancy-group intent into SRGs, route preference,
monitored objects, and explicit service identities.

## Verification implications

- Build a per-interface migration matrix covering cabling, VLANs, LAG members,
  addressing, zones, policy, NAT, routing, and rollback.
- Verify upstream/downstream LAG behavior and routing adjacencies on one
  independent node before removing cluster dependencies.
- Stage management access and ICL connectivity before service cutover.
- Test every protected path, runtime synchronization, failover, and rollback;
  do not assume chassis-cluster state or configuration automatically transfers.
- Confirm the target platform and Junos release support the selected MNHA mode.

This repository includes this original migration summary and source link, not
the TechPost text, diagrams, or command transcript.
