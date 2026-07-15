# Inspired by: SRX EVPN/VXLAN Type 5 over IPsec

Source: Karel Hendrych, Juniper Community TechPost
URL: https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec
Retrieved: 2026-05-15

This is an original interoperability note inspired by the attributed lab. The
upstream article and configuration are not bundled or relicensed here.

## Design takeaways

- Static NAT can disambiguate overlapping tenant prefixes before routes cross an
  EVPN/VXLAN and IPsec boundary.
- Translation, VRF import/export, zone assignment, route-type 5 advertisement, and
  tunnel reachability are separate control points. A working lab validates their
  combination, not a universal deployment recipe.
- Document which address form is advertised, routed, matched by policy, carried in
  the tunnel, and returned by the remote tenant.

## Verification implications

Verify the pre- and post-NAT routes in the correct routing instances, the selected
static-NAT rule, security-policy counters, EVPN route presence, IPsec selectors and
SAs, and the extensive flow session. Test identical tenant prefixes concurrently
to prove that neither control-plane nor return-path ambiguity remains.
