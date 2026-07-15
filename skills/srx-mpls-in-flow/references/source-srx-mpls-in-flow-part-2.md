# Inspired by: SRX MPLS in Flow—Part 2

- **Author:** Karel Hendrych
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/karel-hendrych/2026/04/22/srx-mpls-in-flow-part-2
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the Junos 25.4R1 SRX4600/SRX4700 additions,
  VRF-to-zone policy model, and hardware-platform verification cautions.

## Original summary

Part 2 extends the MPLS-in-flow design to features described for Junos 25.4R1.
The article calls out MPLS L3VPN support on SRX4600 and SRX4700 and demonstrates
mapping VRFs to security zones. That model can simplify policy because routing
context follows zone membership instead of being repeated as an L3VPN VRF-group
match on each rule.

The physical lab evaluates SRX4600 forwarding through the hardware PFE and SPU
path. Its observations about inner-header hashing, Express Path, PowerMode,
drop-flow, and single-flow performance are test results from that topology, not
generic throughput commitments. Overlapping tenant addresses also require
careful VRF, zone, policy, session, and NAT inspection so output is interpreted
in the correct context.

## Verification implications

- Confirm SRX4600/SRX4700 MPLS L3VPN and VRF-to-zone support on the exact Junos
  release and hardware variant.
- Verify zone-to-VRF bindings, policy lookup, sessions, NAT/AppID, route labels,
  and tenant overlap independently.
- Treat performance, hashing, Express Path, PowerMode, and drop-flow statements
  as lab observations until reproduced with the intended packet sizes, flow
  counts, services, and topology.
- Size the design from current official specifications and representative tests,
  not the article's single lab result.

This repository contains this original summary and attribution, not the
TechPost text, performance tables, diagrams, or physical-lab configurations.
