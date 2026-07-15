# Inspired by: SRX MPLS in Flow

- **Author:** Karel Hendrych
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/karel-hendrych/2025/08/01/srx-mpls-in-flow
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the Junos 24.2R1 decoupled forwarding-family
  model and the secure MPLS L3VPN PE/CPE workflow.

## Original summary

The article describes a Junos 24.2R1 model in which MPLS label processing can be
packet based while IPv4 and IPv6 remain in normal SRX flow mode. This differs
from making the entire device packet based: customer traffic can still enter
stateful security processing after label disposition.

An SRX used as a secure PE or CPE still needs the complete MPLS control plane:
adequate MTU, loopback reachability, an IGP, a label distribution mechanism,
MP-BGP VPN families, route distinguishers, route targets, and VRF interfaces.
The article's lab uses `vrf-table-label` where local VRF interfaces require a
VPN label lookup path.

Security policy must include the VRF context in addition to addresses and
applications. The 24.2-era example uses L3VPN VRF-group matching. NAT and AppID
also need to be verified in the correct routing instance; label reachability by
itself does not prove that flow services see the intended tenant.

## Verification implications

- Verify the forwarding mode for inet, inet6, and MPLS with operational output,
  not only configuration presence.
- Confirm platform and release support in current Juniper documentation; the
  platform list and legacy packet-mode behavior are release dependent.
- Check interface MTU, IGP/LDP or alternative transport labels, MP-BGP VPN
  routes, VRF import/export, policy hits, sessions, NAT translations, and AppID.
- Treat the vSRX lab topology and performance observations as examples rather
  than platform guarantees.
- Validate upgrade behavior explicitly when an older deployment relied on
  global or selective packet mode.

This repository contains this independently written operational summary and a
direct source link, not the article text, appendices, or lab configurations.
