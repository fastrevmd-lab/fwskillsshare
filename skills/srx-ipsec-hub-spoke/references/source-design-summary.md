# Static P2P IPsec Hub-and-Spoke Full-Tunnel Backhaul — Derived Design Summary

Derived summary of Jason Anderson's lab
[`srx-p2p-ipsec-public`](https://github.com/anderson-jason573/srx-p2p-ipsec-public)
(author: Jason Anderson). Built on four vSRX firewalls (Junos OS **23.2R2.21**)
plus a Cisco IOS-XE router as WAN transit / simulated internet. This is a
paraphrased technical summary for local operational reference, not a verbatim copy.

## Reference addressing (lab)

| Device | Role | fxp0 (mgmt) | WAN (ge-0/0/0) | WAN peer | LAN (ge-0/0/1) |
|--------|------|-------------|----------------|----------|----------------|
| srx01 | Hub + egress | 172.27.1.50 | 10.0.0.2/30 | 10.0.0.1 | 192.168.1.1/24 |
| srx02 | Spoke | 172.27.1.51 | 10.0.1.2/30 | 10.0.1.1 | 192.168.2.1/24 |
| srx03 | Spoke | 172.27.1.52 | 10.0.2.2/30 | 10.0.2.1 | 192.168.3.1/24 |
| srx04 | Spoke | 172.27.1.54 | 10.0.3.2/30 | 10.0.3.1 | 192.168.4.1/24 |
| CSR1 | WAN transit / sim-internet | 172.27.1.53 | four `/30` links | — | loopback 10.100.100.1 |

Tunnel map: `srx01 st0.0 ↔ srx02`, `srx01 st0.1 ↔ srx03`, `srx01 st0.2 ↔ srx04`;
each spoke uses a single `st0.0` to the hub. `st0` units are unnumbered P2P.

## Crypto parameters (same as the AutoVPN lab)

- **Phase 1 (IKE):** pre-shared key, DH group 14, SHA-256, AES-256-CBC, IKEv2
  (`v2-only`), lifetime 86400 s, `mode main`.
- **Phase 2 (IPsec):** ESP, AES-256-GCM, PFS group 14, lifetime 3600 s.
- **MSS clamp:** `set security flow tcp-mss ipsec-vpn mss 1350`.

## Per-spoke gateway and VPN (no dynamic gateway, no selectors)

Hub, one block per spoke (srx02 example):

```
set security ike gateway GW-srx02 ike-policy IKE-POL
set security ike gateway GW-srx02 address 10.0.1.2          # spoke WAN IP (pinned by IP)
set security ike gateway GW-srx02 external-interface ge-0/0/0.0
set security ike gateway GW-srx02 version v2-only
set security ipsec vpn VPN-srx02 bind-interface st0.0
set security ipsec vpn VPN-srx02 ike gateway GW-srx02
set security ipsec vpn VPN-srx02 ike ipsec-policy IPSEC-POL
set security ipsec vpn VPN-srx02 establish-tunnels immediately
```

Spoke (srx02) pins the hub by IP: `set security ike gateway GW-hub address
10.0.0.2`. No `local-identity`/`remote-identity`, no `traffic-selector`. The
negotiated proxy-id defaults to `0.0.0.0/0 ↔ 0.0.0.0/0`, so one SA per spoke carries
internet and inter-spoke traffic; **routing** scopes each `st0`.

## Static vs. AutoVPN — same backhaul, different mechanism

| | AutoVPN backhaul ([`srx-autovpn-backhaul-public`](https://github.com/anderson-jason573/srx-autovpn-backhaul-public)) | Static P2P (this lab) |
|---|---|---|
| Hub gateways | One dynamic `group-ike-id` | One static gateway per spoke (by IP) |
| Hub tunnel interfaces | Single shared `st0.0` | One `st0` unit per spoke |
| Peer identity | `hostname *.homelab.local` | Peer WAN IP address |
| What scopes the tunnel | Traffic selectors | Routing only — no selectors |
| Hub → spoke-LAN routes | ARI (`ARI-TS`) | Static, one per spoke |
| Add a new spoke | Zero hub change | Hub change: +gateway +VPN +`st0` +route |
| Spoke-to-spoke | Hairpin on shared `st0.0` | Hairpin across two `st0` units |
| Backhaul behavior, NAT, anti-recursion | — | Identical |

## Routing (the entire story here)

**Spoke:** `0.0.0.0/0 → st0.0` (default into tunnel); anti-recursion `10.0.0.2/32 →
10.0.1.1` (ESP to hub WAN stays out of the tunnel); WAN `/30`s via underlay.

**Hub:** explicit `192.168.2.0/24 → st0.0`, `192.168.3.0/24 → st0.1`,
`192.168.4.0/24 → st0.2`; `0.0.0.0/0 → 10.0.0.1` egress default; WAN `/30`s via
`10.0.0.1`.

Spoke-to-spoke: srx02→srx03 follows srx02 default into `st0.0`, hits hub
`192.168.3.0/24 → st0.1`, leaves on the srx03 tunnel — an intra-zone `VPN → VPN`
flow.

**Management-default ECMP caveat:** vSRX `0.0.0.0/0 → 172.27.1.1 via fxp0` ECMPs
with the new defaults (traffic leaks out `fxp0`, NAT does not apply). Production
fix: management routing-instance. Lab shortcut (validated): `10.100.100.1/32 →
st0.0` on spokes, `10.100.100.1/32 → 10.0.0.1` on the hub, plus `192.168.0.0/16 →
st0.0` on each spoke for hub-LAN and spoke-to-spoke.

## Hub source NAT (internet egress only)

```
set security nat source rule-set VPN-BACKHAUL from zone VPN
set security nat source rule-set VPN-BACKHAUL to zone untrust
set security nat source rule-set VPN-BACKHAUL rule SNAT-INTERNET match source-address 192.168.0.0/16
set security nat source rule-set VPN-BACKHAUL rule SNAT-INTERNET match destination-address 0.0.0.0/0
set security nat source rule-set VPN-BACKHAUL rule SNAT-INTERNET then source-nat interface
```

All three spoke tunnels share the VPN zone, so one rule-set covers every spoke.
Spoke-to-spoke (`VPN → VPN`) and spoke-to-hub-LAN (`VPN → trust`) stay un-NAT'd.

## Hub security policies

Added for full tunnel: `VPN → untrust` permit (internet egress) and `VPN → VPN`
permit (spoke-to-spoke hairpin across `st0` units). All `st0` units in one VPN zone
make the hairpin a single intra-zone policy. Unchanged: `trust → untrust`,
`trust → VPN`, `VPN → trust`. Return traffic is stateful.

## Validation (lab)

Hub bring-up: three IKE SAs UP (one per spoke), three IPsec SAs bound to
`st0.0/1/2`, and the three static spoke-LAN routes resolving via the correct tunnel
interfaces; stable data plane (no core dumps). Internet backhaul and spoke-to-spoke
data paths verified (`show security flow session` shows internet flows xlated to the
hub WAN IP; spoke-to-spoke enters one `st0` unit and leaves another, no NAT).

## Deployment order

1. CSR1 (WAN transit) — up first
2. srx01 (hub)
3. srx02 / srx03 / srx04 (spokes, any order)

PSK kept out of config as `$IPSEC_PSK`, substituted at deploy time from a
git-ignored `secrets.env`; same PSK on hub and every spoke (production: prefer
per-tunnel PSKs or PKI).

## Juniper references (from the lab)

- IPsec VPN User Guide | Junos OS
- Route-Based IPsec VPNs | Junos OS
- IPsec VPN with Multiple Sites (Hub-and-Spoke) | Junos OS
- IPsec VPN Configuration Overview | Junos OS
