---
name: srx-mnha
description: Design, configure, audit, or troubleshoot Juniper SRX Multi-Node High Availability (MNHA). Use for routed, default-gateway, or hybrid modes; chassis-cluster migration; SRGs; ICL or ICD; session sync; BGP or BFD failover; VIPs; IPsec or IKED; NAT or proxy ARP; routing instances; or DHCP behavior.
version: 1.2.3
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [srx, junos, mnha, high-availability, chassis-cluster, srg, icl, icd, bgp, bfd, ipsec, ike, nat, routing-instance, dhcp]
    related_skills: [parsing-srx-configs, srx-nat, srx-policy, srx-autovpn-full-tunnel, srx-ipsec-hub-spoke]
  sources:
    - title: "DHCP on MNHA: Back to Basics"
      author: James Rathbun
      url: https://community.juniper.net/blogs/james-rathbun/2026/04/22/dhcp-on-mnha-back-to-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
      retrieved: "2026-05-14"
    - title: Multi-Node High Availability Basics
      author: Steven Jacques
      url: https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
      retrieved: "2026-05-14"
    - title: Hybrid MNHA with eBGP
      author: James Rathbun
      url: https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
      retrieved: "2026-05-14"
    - title: "SRX clustering: from Chassis Cluster to MultiNode High Availability"
      author: Laurent Paumelle
      url: https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha
      retrieved: "2026-05-14"
    - title: "MNHA, IPSec and Multiple Routing Instances"
      author: James Rathbun
      url: https://community.juniper.net/blogs/james-rathbun/2026/03/30/mnha-ipsec-and-multiple-routing-instances?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
      retrieved: "2026-05-14"
---

# SRX Multi-Node High Availability (MNHA)

## Overview

Multi-Node High Availability (MNHA) is Juniper SRX high availability built around independent SRX nodes that synchronize runtime state over routed HA links. Unlike chassis cluster, MNHA nodes do not become a single logical chassis. Each node keeps its own control plane, hostname, management, routing protocols, interface addressing, and node-specific configuration. Stateful firewall/NAT/IPsec runtime objects can still synchronize so traffic can survive a path or node failover when the design keeps routing, interfaces, policy, and HA state aligned.

Use MNHA as an L3-first HA design. Routing policy, BFD, link monitoring, service redundancy groups, and optional VIP behavior determine which node handles traffic. Avoid treating MNHA as a drop-in chassis-cluster clone; it solves different problems and has different failure modes.

## When to Use

Use this skill when the user asks about:

- Juniper SRX MNHA, Multi-Node High Availability, or `chassis high-availability`
- choosing MNHA versus chassis cluster
- migrating SRX chassis cluster designs toward MNHA
- SRG0, SRG1+, Services Redundancy Groups, VIPs, vMACs, or signal routes
- ICL, ICD, runtime object synchronization, Active/Warm session state, or failover behavior
- routed MNHA, default-gateway MNHA, or hybrid MNHA
- eBGP/BFD designs for MNHA active/backup or active/active forwarding
- IPsec VPNs on MNHA, including floating loopback tunnel anchors, `managed-services ipsec`, IKED, remote access VPN, site-to-site VPN, or multiple routing instances
- NAT/SNAT, proxy ARP, RPF/RRL, and deterministic routing concerns in MNHA
- DHCP relay or DHCP local-server behavior on MNHA
- troubleshooting `show chassis high-availability`, `show security flow session`, BGP/BFD convergence, VIP installation, IPsec SAs, or IKE gateway lookup failures

Do not use this as the primary skill for parsing a full SRX configuration. Load `parsing-srx-configs` first when the task is to extract or audit an arbitrary SRX config, then use this skill for MNHA-specific interpretation. For general SRX NAT design detail use srx-nat; for security-policy design/migration use srx-policy — this skill covers only their MNHA-specific behavior.

## Chassis Cluster vs MNHA

Chassis cluster is the traditional SRX L2 HA model:

- two nodes form one logical chassis
- active/backup control plane behavior
- shared cluster configuration
- reth interfaces with virtual IP/MAC behavior
- redundancy group ownership changes during failover
- nodes usually need the same L2 domains for clustered interfaces
- failover may depend on gratuitous ARP and L2 convergence

MNHA is different:

- nodes remain independent SRX devices
- each node has its own routing process and control plane
- both nodes can maintain routing adjacencies at the same time
- forwarding preference is normally driven by routing policy, BFD, and SRG state
- state synchronization is separate from full configuration synchronization
- ICL/ICD are logical routed links, not chassis-cluster HA/fabric ports
- designs can be routed, default-gateway/L2-like, or hybrid

Key design translation:

| Chassis cluster habit | MNHA interpretation |
|---|---|
| One shared config | Independent configs; synchronize only what should match |
| Reth/VIP everywhere | Use routed node IPs where possible; use VIPs only when the design requires them |
| RG master owns traffic | Routing and SRG state influence traffic path |
| Active/passive control plane | Independent active control planes |
| Dedicated HA/fabric assumptions | Routed ICL/ICD paths with security/routing/MTU planning |

Always verify platform and Junos support in Juniper Pathfinder / Feature Explorer and current Juniper documentation before deployment. MNHA feature support, scale, asymmetric-flow support, multi-node support, and platform support are release-dependent.

## Chassis-Cluster to MNHA Interface Migration

"Use routed node IPs where possible" hides the actual migration mechanic. A chassis-cluster **reth** is a cluster construct with **child links contributed by each node**; on MNHA there is no cluster, so each node's children must collapse into node-local interfaces. This is the biggest and most error-prone step of a cluster→MNHA conversion.

Per-node reth conversion:

- Each node's reth member links become either a **local `ae` bundle** (LACP) **or** one or more **single physical interfaces** on that node. There is no reth on MNHA.
- **This is a customer/upstream question, not an automatic choice.** The source config does not tell you what the upstream switch expects.

Do not assume LACP survives:

- A source `set interfaces reth0 ... lacp active` (or redundant-ether-options LACP) is a **cluster-reth** construct. It does **not** prove the upstream is a real LAG toward a single node.
- Before recreating `ae` + LACP on each MNHA node, **confirm the upstream is actually a LAG** to that node. In real migrations the customer may want single physical interfaces per node even though `reth0`/`reth1` carried `lacp active`.
- Tradeoff to state explicitly: single physical = **no LAG bandwidth aggregation and no local link redundancy**; a per-node `ae` keeps both but requires the upstream to be configured as a LAG to that node.

Sketch — a source `reth1` (two child links per node) becoming a per-node `ae` on each MNHA node:

```junos
# Source (chassis cluster): reth1 with one child per node
# set interfaces ge-0/0/4 gigether-options redundant-parent reth1   # node0 child
# set interfaces ge-7/0/4 gigether-options redundant-parent reth1   # node1 child
# set interfaces reth1 redundant-ether-options lacp active

# MNHA node0 (standalone) — only if the upstream is a real LAG to node0:
set interfaces ae1 aggregated-ether-options lacp active
set interfaces xe-0/0/4 ether-options 802.3ad ae1
set interfaces ae1 unit 0 family inet address <NODE0_IP>/<PLEN>

# MNHA node0 — single physical instead, if the customer does NOT want a LAG:
# set interfaces xe-0/0/4 unit 0 family inet address <NODE0_IP>/<PLEN>
```

Repeat independently on node1 with its own local child interfaces and IP. Each node's interface names, member ports, and addresses are node-specific configuration (see Configuration Synchronization) and are intentionally *not* synchronized.

## Deployment Modes

### Routed / L3 MNHA

Routed MNHA is the cleanest MNHA model.

Characteristics:

- no interface VIP required for normal forwarding
- each node has unique interface IP addresses
- each node peers with upstream/downstream routers independently
- BGP, OSPF, static metrics, or policy decide preferred paths
- SRG0 is commonly involved for default active/active service behavior
- symmetry is strongly preferred for stateful inspection

Use routed MNHA when:

- the network can route to either SRX node
- you want fast failover with routing/BFD
- geo-redundancy or L3 separation matters
- you want to avoid L2 stretch and virtual MAC dependencies

### Default-Gateway MNHA

Default-gateway mode provides L2-like gateway behavior with VIP/vMAC semantics.

Characteristics:

- a VIP is installed on the active node for an SRG
- clients use the VIP as their default gateway
- backup node does not install that VIP
- failover moves the VIP and sends ARP/GARP behavior to update the L2 domain
- requires shared L2 where the VIP is used

Use default-gateway mode when:

- hosts cannot be changed away from a shared default gateway address
- migrating from chassis cluster and preserving gateway addressing is important
- L2 gateway semantics are required on one or more segments

L2-adjacency caveats for `deployment-type switching` / default-gateway mode:

- The VIP rides on the `aeN.unit` (or physical unit) directly — no IRB/bridge-domain is introduced. The gateway is an interface VIP, not a routed SVI.
- The gateway vMAC **moves** on failover. Adjacent switches must accept that MAC move: check **MAC-move limits**, **Dynamic ARP Inspection (DAI)**, **storm-control**, and **EVPN/MLAG duplicate-MAC protection** — any of these can suppress or block the moved vMAC and silently break failover even though the SRG shows ACTIVE.
- Use an SRG monitor-object to tie the segment's uplink to failover (interface
  monitoring hangs off a named monitor-object with weights and thresholds, not
  a bare `monitor interface` knob):
  ```junos
  set chassis high-availability services-redundancy-group <SRG> monitor monitor-object <NAME> interface interface-name <IFD> weight 100
  set chassis high-availability services-redundancy-group <SRG> monitor monitor-object <NAME> interface threshold 100
  set chassis high-availability services-redundancy-group <SRG> monitor monitor-object <NAME> object-threshold 100
  set chassis high-availability services-redundancy-group <SRG> monitor srg-threshold 100
  ```
  `interface-name` takes the physical IFD (e.g. `ge-0/0/2`). Failover fires
  when accumulated weight reaches the interface threshold, the object
  threshold, and the SRG threshold — size weights accordingly (see
  `references/source-hybrid-mnha-with-ebgp.md` for a weighted BFD + interface
  example).
- Chassis-cluster `interface-monitor` **weights do not map 1:1** to SRG monitoring. Do not port cluster monitor weights directly; redesign monitoring around SRG active/backup semantics and test failover explicitly.

### Hybrid MNHA

Hybrid mode combines routed and default-gateway behavior.

Common pattern:

- one side uses VIP/default-gateway behavior for an attached L2 segment
- the other side uses routed eBGP/OSPF/static paths
- SRG1+ controls active/backup service ownership for VIPs and route signaling
- BFD and interface monitoring can drive failover decisions

Use hybrid MNHA when:

- internal clients need a shared gateway VIP
- external/upstream connectivity is routed and redundant
- branch, campus, or mixed L2/L3 migration designs require both models

## Services Redundancy Groups

Juniper articles refer to Services Redundancy Groups, abbreviated SRGs. Use the Junos hierarchy under `chassis high-availability services-redundancy-group`.

### SRG0

SRG0 is the default forwarding group for routed MNHA behavior.

Operational model:

- no active/backup ownership model like a VIP group
- both nodes can be ready to forward
- no VIP/vMAC ownership is normally involved
- routing determines which node sees traffic
- runtime state can synchronize over ICL

If ICL is lost, state synchronization is affected. Routing may still deliver packets to either node, but stateful continuity is at risk until synchronization is restored.

### SRG1 and Higher

SRG1+ provides active/backup service behavior.

Use SRG1+ for:

- default gateway VIPs
- hybrid mode VIPs
- route signaling based on active/backup status
- interface/BFD/object monitoring tied to failover
- IPsec termination designs that require synchronized tunnel/SAs, where supported
- active/active distribution by using different SRGs active on different nodes

Common SRG1+ attributes:

```junos
set chassis high-availability services-redundancy-group <SRG> deployment-type <routing|hybrid|switching>
# deployment-type: routed/L3 = routing; hybrid = hybrid; default-gateway/L2 = switching
set chassis high-availability services-redundancy-group <SRG> peer-id <PEER_ID>
set chassis high-availability services-redundancy-group <SRG> activeness-priority <PRIORITY>
```

Verify:

```text
show chassis high-availability services-redundancy-group <SRG>
```

Look for:

- deployment type
- ACTIVE or BACKUP status
- activeness priority
- preemption state
- peer status
- health status
- failover readiness
- VIP status when configured

## ICL: Inter-Chassis Link

The ICL is the MNHA cluster communication and state-synchronization path. It is logical and routed; it does not require the physical HA/fabric ports used by chassis cluster.

ICL carries or supports:

- liveness / cluster communication
- cold sync after reconnect
- runtime object synchronization
- firewall session sync
- NAT state sync
- IPsec state sync where applicable
- HA-related control exchange

Design guidance:

- source ICL from stable loopback or dedicated interface addresses
- place ICL in a dedicated routing instance when practical
- when using MNHA IPsec with floating loopback tunnel anchors, the ICL routing instance and the floating loopback/external-interface routing instance must align; route leaking is not a safe substitute for IKE gateway lookup
- allow HA-related host-inbound services on the ICL zone
- if encrypting ICL, allow IKE and use the Junos HA link encryption model
- keep ICL RTT under the platform/release requirement for geo designs; the supplied sources use less than 100 ms as the design bound
- use redundant paths where possible
- do not assume ICL must be back-to-back; it can traverse routed infrastructure
- size the encrypted ICL for RTO/session-sync bursts, not just steady state; James Rathbun's field rule of thumb is roughly 1 Gbps per 100,000 concurrent sessions and keeping utilization below about 75% for resync and connection-per-second bursts

Minimal conceptual stanza:

```junos
set chassis high-availability local-id local-ip <LOCAL_ICL_IP>
set chassis high-availability peer-id <PEER_ID> peer-ip <PEER_ICL_IP>
set chassis high-availability peer-id <PEER_ID> interface <ICL_SOURCE_INTERFACE>
set chassis high-availability peer-id <PEER_ID> routing-instance <ICL_RI>
set chassis high-availability peer-id <PEER_ID> liveness-detection minimum-interval <MS>
set chassis high-availability peer-id <PEER_ID> liveness-detection multiplier <COUNT>
set chassis high-availability services-redundancy-group 0 peer-id <PEER_ID>
```

Security-zone example for an ICL interface:

```junos
set security zones security-zone ICL interfaces <ICL_INTERFACE>
set security zones security-zone ICL host-inbound-traffic system-services high-availability
set security zones security-zone ICL host-inbound-traffic system-services ssh
set security zones security-zone ICL host-inbound-traffic protocols all
```

For production, restrict host-inbound services and protocols to the exact required set. Do not copy broad lab `all` permissions without review.

## ICD: Inter-Chassis Datalink

ICD is an optional datapath used when asymmetric routing can deliver packets for one flow to different SRX nodes.

Use ICD when:

- ECMP or routed topology can produce asymmetry
- hybrid designs may send one direction to one node and return traffic to the other
- L7 inspection needs one node to see enough packets to classify or inspect a flow
- you cannot guarantee symmetric routing during normal or failure states
- multiple SRGs can be active on different nodes and create sustained cross-node, Z-mode-like forwarding

Design notes:

- prefer symmetric routing first
- use ICD deliberately when asymmetry is part of the design
- account for encapsulation overhead and MTU
- validate platform/release support for asymmetric flow and ICD behavior
- test with real application traffic, not only ping
- ICD may be used during the initial TCP 3-way handshake and while advanced inspection services need bidirectional visibility; do not assume every packet of every asymmetric flow will traverse ICD forever
- sustained cross-node flows with advanced inspection/plugin services are not a good steady-state design; engineer traffic so complete bidirectional flows normally land on one active node
- if ICD is down, asymmetric SYN/SYN-ACK or return traffic can fail even while synchronized sessions appear valid; check `show chassis high-availability data-plane statistics` and packet drops

ICD configuration pattern:

```junos
set chassis high-availability local-id local-forwarding-ip <LOCAL_ICD_IP>
set chassis high-availability peer-id <PEER_ID> peer-forwarding-ip <PEER_ICD_IP>
set chassis high-availability peer-id <PEER_ID> peer-forwarding-ip interface <ICD_INTERFACE.UNIT>
set chassis high-availability peer-id <PEER_ID> peer-forwarding-ip liveness-detection minimum-interval <MS>
set chassis high-availability peer-id <PEER_ID> peer-forwarding-ip liveness-detection multiplier <COUNT>
```

ICD verification:

```text
show chassis high-availability data-plane statistics
show security flow session source-prefix <SRC> destination-prefix <DST> pretty
show log messages | match "MNHA forward|re-route failed|reject NH|ICD"
```

(these strings come from flow traceoptions output — they appear in the configured security flow trace file, not the default messages log, unless traceoptions target messages)

Look for `ICD Data` counters when traffic is actually crossing the ICD. A valid Active/Warm session with packet counters split across nodes does not by itself prove the ICD is forwarding every packet.

## IPsec VPNs on MNHA with Multiple Routing Instances

IPsec on MNHA is mostly an alignment problem: the SRG, floating loopback address, physical underlay interface, security zone, routing instance, and BGP advertisement must agree about which node and table should receive IKE/ESP traffic.

Key requirements from the Juniper TechPost:

- use SRG1 or higher for synchronized IPsec; do not try to anchor IPsec on SRG0
- install and validate the newer IKE package where required by release/platform:
  ```text
  request system software add optional://junos-ike.tgz
  show system processes | match "iked|ikemd|kmd"
  ```
- identify IPsec as an MNHA managed service on the SRG:
  ```junos
  set chassis high-availability services-redundancy-group <SRG> managed-services ipsec
  ```
- define the VPN endpoint as a floating IP on a loopback that is present on both nodes and tracked by the SRG prefix list
- configure the IKE gateway `external-interface` as that loopback unit and set the expected `local-address`
- if `process-packet-on-backup` is used, verify the routing and inspection consequences; it is optional, not a cure for bad path design

Floating loopback / IKE gateway pattern:

```junos
set interfaces lo0 unit <UNIT> family inet address <FLOATING_VPN_IP>/32
set policy-options prefix-list <IKE_GW_PREFIX_LIST> <FLOATING_VPN_IP>/32
set chassis high-availability services-redundancy-group <SRG> prefix-list <IKE_GW_PREFIX_LIST> routing-instance <RI>
set chassis high-availability services-redundancy-group <SRG> managed-services ipsec
set security ike gateway <GW> external-interface lo0.<UNIT>
set security ike gateway <GW> local-address <FLOATING_VPN_IP>
```

Routing-instance and zone rules that commonly get missed:

- an interface can belong to only one security zone and one routing instance; this includes loopback units
- the loopback used as the IKE `external-interface` and the physical interface receiving IKE/ESP must be in the same security zone
- add an intra-zone policy for IKE and ESP when IKE/ESP arrives on a physical interface and is internally rerouted to the loopback anchor
- the ICL's MNHA routing-instance context must match the floating loopback routing instance used by the IKE gateway; IKE gateway lookup is control-plane/self-traffic behavior and imported routes from another RI may not satisfy it
- route leaking between RIs can be valid for transit traffic or st0 reachability, but do not rely on it to fix IKE gateway lookup to a floating loopback in a different RI

Intra-zone IKE/ESP policy pattern:

```junos
set security policies from-zone <EXT_ZONE> to-zone <EXT_ZONE> policy ALLOW-IKE-ESP match source-address <REMOTE_PEER>
set security policies from-zone <EXT_ZONE> to-zone <EXT_ZONE> policy ALLOW-IKE-ESP match destination-address <FLOATING_VPN_IP>
set security policies from-zone <EXT_ZONE> to-zone <EXT_ZONE> policy ALLOW-IKE-ESP match application junos-ike
set security policies from-zone <EXT_ZONE> to-zone <EXT_ZONE> policy ALLOW-IKE-ESP match application <ESP_APPLICATION>
# define <ESP_APPLICATION> as a custom application for ESP (IP protocol 50), or use a release-validated predefined app; bare "ESP" is not a Junos built-in
set security policies from-zone <EXT_ZONE> to-zone <EXT_ZONE> policy ALLOW-IKE-ESP then permit
```

Symptoms of a bad RI/zone anchor:

```text
'external-interface'(lo0.<UNIT>) and 'routing-interface'(<PHY_IFL>) belong to different zones
Re-route failed, pkt dropped
unable to make the tunnel ready
Gateway lookup failed
```

### Remote Access VPN Notes

- IKEv1 aggressive mode sessions are not synchronized; expect clients to reauthenticate/reestablish after failover.
- Certificates can synchronize to the peer when ICL cold sync is complete; still verify both nodes after enrollment.
- RADIUS and other control-plane dependencies are node-local. Configure and test source addresses, routes, secrets, and reachability from both nodes.
- For one SRG, a common address-assignment pool can move with failover. For active/active designs with multiple SRGs, use separate shared ranges per SRG or split pools to avoid address collisions.
- `st0` counters are node-local and are not synchronized; use them to identify which node is actually forwarding tunnel traffic.
- On Junos 23.1R1 and later, remote-access `default-profile` behavior is deprecated in favor of profile names based on FQDNs or IPs.

Remote-access verification:

```text
show security ike security-associations
show security ike security-associations srg-id <SRG>
show security ike security-associations <REMOTE> detail | match "AAA assigned IP|Local|Remote|State"
show network-access address-assignment pool <POOL>
show interfaces st0.<UNIT> | match packets
```

### Site-to-Site VPN Notes

- Tunnel interfaces such as `st0.<UNIT>` can live in a different routing instance from the IKE floating loopback, but then route import/export between the protected RI and VPN RI must be explicit and verified.
- Auto Route Insertion (ARI) from traffic selectors may install routes in the protected RI on both MNHA nodes. Confirm the table where ARI routes land before writing policies.
- If the floating IP for the IKE gateway is advertised conditionally with SRG signal routes, pin the preferred ingress path to the active node and avoid receiving tunnel-initiation traffic in a non-MNHA/non-ICL RI.

Site-to-site verification:

```text
show security ike security-associations srg-id <SRG>
show security ipsec security-associations
show security flow session tunnel
show route table <PROTECTED_RI>.inet.0 <REMOTE_TS_PREFIX>
show route table <VPN_RI>.inet.0 <LOCAL_PROTECTED_PREFIX>
```

## NAT, Proxy ARP, and Deterministic Routing

NAT in MNHA has to be deterministic across both nodes. Keep NAT policy and pools equivalent where stateful failover is expected, but avoid designs where both independent control planes answer for the same translated address at L2.

Design guidance:

- prefer routed next-hop reachability to SNAT pools over proxy ARP
- do not rely on proxy ARP for upstream reachability to translated addresses in MNHA; both nodes can answer ARP and upstream devices keep only one MAC per IP
- if using multiple ISPs, avoid shared SNAT pools unless return routing is deterministic and the prefix is advertised consistently
- unique per-ISP SNAT pools can work, but active sessions will fail if failover changes the translated source range
- `set security nat source rule-set <RS> to interface <IFL>` can make SNAT selection more predictable, but only if the pool, egress interface, and route advertisement all align
- account for RPF and reverse route lookup before NAT; incorrect route selection can create `Dropped by IDS:IP spoofing` or other flow drops
- if an upstream needs a next hop for a shared SNAT prefix, point it at a routed VIP or node interface deliberately; do not assume chassis-cluster proxy-ARP behavior transfers cleanly to MNHA

Useful NAT/routing checks:

```text
show security nat source rule all
show security nat source pool all
show route table <RI>.inet.0 <SNAT_POOL_PREFIX>
show route table <RI>.inet.0 0.0.0.0/0 exact
show security packet-drop records | match "MNHA|IP spoofing|reroute|proxy|FLOW"
```

If packet drops include `Dropped by FLOW:error info in MNHA flow meta header`, suspect a cross-node/asymmetric MNHA flow where NAT or proxy-ARP return traffic landed on the wrong node.

## Runtime Object and Session Synchronization

MNHA synchronizes runtime state rather than making the devices a single chassis.

Runtime objects include state such as:

- firewall sessions
- NAT translations
- IPsec SAs where applicable
- other stateful security runtime data supported by the platform/release

In MNHA session output, expect Active/Warm semantics:

- `Active` means this node currently owns/handles that session state
- `Warm` means a synchronized standby copy exists
- if traffic moves to the warm node and state is valid, that node can become active for the session

Verification:

```text
show security flow session destination-prefix <PREFIX>
show security flow session source-prefix <PREFIX>
show security flow session | match "Session ID|HA State|HA Wing State|In:|Out:"
```

Design requirements:

- keep shared security policy and NAT logic consistent across nodes
- keep relevant zones and logical forwarding paths consistent for flows that must fail over statefully
- avoid asymmetric routing unless ICD/asymmetric-flow support has been planned and tested
- confirm sessions appear on both nodes before declaring stateful failover ready

## Configuration Synchronization

MNHA does not automatically synchronize the entire configuration. This is a feature, not a bug: node-specific routing and interface configuration must often differ.

Usually node-specific:

- hostnames
- management IPs
- interface addresses
- BGP neighbor addresses and local addresses
- OSPF interface details
- routing policies that intentionally differ per node
- local monitoring targets

Usually synchronized or kept equivalent:

- security policies
- address books and address sets
- application/application-set definitions
- NAT policy structure
- UTM/IDP/AppSecure profiles used by synchronized policies
- IPsec definitions when failover/sync is required
- shared SRG logic, adjusted for peer/local IDs and priorities

Safe methods:

- Junos groups plus commit peer synchronization
- automation using NETCONF/PyEZ/Ansible
- Security Director / Security Director Cloud for supported policy/security management use cases
- rigorous config-diff checks in CI or change management

Commit peer synchronization pattern: key statements are `groups <NAME> when peers [ ... ]` + `apply-groups`, `system commit peers-synchronize`, and `system commit peers <PEER_HOSTNAME>` with authentication and static-host-mapping. Full stanza in `references/mnha-config-patterns.md`.

Do not store real secrets in skill files, tickets, or chat. Replace them with placeholders.

## Hybrid MNHA with eBGP Pattern

A common hybrid pattern uses SRG1+ to control VIP ownership and signal BGP policy.

Core pieces:

1. SRG active/backup state
2. VIPs installed only on active node
3. active and backup signal routes installed according to SRG role
4. BGP export policy that changes route attributes based on signal-route presence
5. BFD and interface monitoring to detect failure
6. routers prefer the active SRX path but retain backup reachability

### Signal Routes

Signal routes are arbitrary local routes used as policy conditions. Use prefixes that cannot collide with production routes.

If no routing instance is specified for the signal route, expect Junos to install it in `inet.0`; make the `policy-options condition ... if-route-exists ... table` match the table where the signal route actually appears.

```junos
set chassis high-availability services-redundancy-group <SRG> active-signal-route 169.254.200.1
set chassis high-availability services-redundancy-group <SRG> backup-signal-route 169.254.200.2
```

Verify:

```text
show route 169.254.200.0/30
```

Expected:

- active node has the active signal route
- backup node has the backup signal route
- neither route should be used for real traffic

### BGP Export Policy from Signal Routes

Use explicit route filters. Do not export every direct route unless that is intentionally part of the routing design.

Example pattern for a protected prefix:

```junos
set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet 169.254.200.1/32
set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet table inet.0
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet 169.254.200.2/32
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet table inet.0
```

Skeleton — an `active` term at the better metric gated on ACTIVE_SRG1 and a `backup` term at a worse metric gated on BACKUP_SRG1, both route-filtered to the protected prefix, with a final reject term:

```junos
set policy-options policy-statement MNHA-SRG1-EXPORT term active from condition ACTIVE_SRG1
set policy-options policy-statement MNHA-SRG1-EXPORT term active then metric 10
set policy-options policy-statement MNHA-SRG1-EXPORT term backup from condition BACKUP_SRG1
set policy-options policy-statement MNHA-SRG1-EXPORT term backup then metric 20
set protocols bgp group <GROUP> export MNHA-SRG1-EXPORT
```

Full route-filtered export policy example in `references/mnha-config-patterns.md`.

MED works predictably when compared between routes from the same neighboring AS and with the expected BGP decision behavior. If SRXs use different ASNs or the upstream BGP policy differs, choose a route-control mechanism appropriate to the environment.

### OSPF Variant of Signal-Route Steering

The signal-route examples above assume eBGP. OSPF shops need the same active/backup steering without a BGP export policy. The pattern maps as follows:

- Each node has its own `router-id` and a **passive loopback** carrying the protected `/32` (do not form adjacencies on the loopback).
- **Both roles advertise, at different metrics** — mirror the eBGP pattern: an `active` term at the low metric gated on the active signal route, and a `backup` term at a higher metric gated on the backup signal route. That keeps a standby path in the OSPF database while both nodes are up; on failover the signal routes swap and metrics follow.
- Instead of a BGP export policy, **export the SRG-signal-route-conditioned `/32` into OSPF** with a policy gated on the `if-route-exists` conditions.

The OSPF export policy (`MNHA-SRG1-OSPF`) mirrors the BGP one — reuse the same if-route-exists conditions as the BGP pattern above — full config in `references/mnha-config-patterns.md`.

Verify with `show route <PROTECTED_PREFIX>` and `show ospf database` on both nodes; confirm the active node's advertisement is preferred and the backup path appears only as a higher-cost alternative. The same BFD guidance below applies to OSPF (`set protocols ospf area 0 interface <IFL> bfd-liveness-detection ...`).

### BFD

Use BFD for fast routing failure detection where supported and stable.

Example BGP BFD pattern:

```junos
set protocols bgp group <GROUP> bfd-liveness-detection minimum-interval <MS>
set protocols bgp group <GROUP> bfd-liveness-detection minimum-receive-interval <MS>
set protocols bgp group <GROUP> bfd-liveness-detection multiplier <COUNT>
```

Verification:

```text
show bfd session
show bgp summary
show route <PROTECTED_PREFIX>
show route <PROTECTED_PREFIX> receive-protocol bgp <NEIGHBOR>
show route <PROTECTED_PREFIX> advertising-protocol bgp <NEIGHBOR>
```

Operational caution:

- test BFD timers on the actual platform
- overly aggressive timers can cause instability
- BFD hold-down can intentionally stabilize neighbors but can also extend failback outage
- preemption/failback must be tested with routing convergence, not only SRG status
- for VPN floating IPs in multiple routing-instance designs, inbound routing policy must steer IKE/ESP to the physical interface and RI that align with the floating loopback and ICL context, or IKE may fail with gateway lookup errors
- if a route advertisement uses a VIP as next hop, BGP multihop or upstream static routing may be required so the advertised next hop is the VIP instead of BGP self

### VIPs in Hybrid or Default-Gateway Mode

VIP example:

```junos
set chassis high-availability services-redundancy-group <SRG> virtual-ip 1 ip <VIP>/<PREFIXLEN>
set chassis high-availability services-redundancy-group <SRG> virtual-ip 1 interface <INTERFACE.UNIT>
```

Verify:

```text
show chassis high-availability services-redundancy-group <SRG>
show interfaces <INTERFACE> | match "address:"
show arp no-resolve | match <VIP>
```

Expected:

- VIP is `INSTALLED` on active
- VIP is `NOT INSTALLED` on backup
- failover moves the VIP
- clients or routers using the VIP must refresh ARP/MAC state after failover

## DHCP on MNHA

The safest DHCP design with MNHA is usually DHCP relay to an external DHCP service.

Prefer DHCP relay when:

- continuity matters
- a central DHCP server is available
- avoiding split local lease databases is important
- avoiding node-specific local lease loss is important

Relay pattern:

```junos
set routing-instances <RI> forwarding-options dhcp-relay server-group DHCP-SERVERS <DHCP_SERVER_IP>
set routing-instances <RI> forwarding-options dhcp-relay group RELAY-GROUP active-server-group DHCP-SERVERS
set routing-instances <RI> forwarding-options dhcp-relay group RELAY-GROUP interface <CLIENT_INTERFACE>
```

If local DHCP on the SRX nodes is required, use conservative design:

- each node runs its own DHCP process
- do not assume lease database synchronization
- use non-overlapping split pools
- use each node's physical/client-facing IP as DHCP server-identifier
- use the VIP as the DHCP router/default-gateway option where clients need the floating gateway
- mirror reservations on both nodes
- exclude infrastructure addresses from pools
- keep lease times aligned with operational failure behavior

Local DHCP pattern: per-node dhcp-local-server with a non-overlapping range per node, the VIP as the router option, and each node's own interface IP as `server-identifier`. Full node-A config (and the node-B variation) in `references/mnha-config-patterns.md`.

DHCP verification:

```text
show dhcp server binding routing-instance <RI>
show dhcp server statistics routing-instance <RI>
show chassis high-availability services-redundancy-group <SRG>
clear dhcp server binding routing-instance <RI> all
```

Use destructive clear commands only inside an approved maintenance procedure.

DHCP pitfalls:

- forgetting `host-inbound-traffic system-services dhcp` silently breaks DHCP
- overlapping local pools can create duplicate leases
- static reservations must be mirrored or clients may get different behavior depending on which node answers
- using the VIP as DHCP server-identifier can make renewals land on a node that did not issue the lease; avoid this unless you have deliberately accepted and tested the behavior
- DHCP local-server on MNHA has different state behavior from chassis cluster

## Verification Checklist

Before production cutover:

- [ ] Platform and Junos release support verified in current Juniper docs.
- [ ] Deployment mode selected: routed, default-gateway, or hybrid.
- [ ] SRG usage documented: SRG0 only, SRG1+, or multiple SRGs.
- [ ] ICL reachability verified in the intended routing instance.
- [ ] ICL zone host-inbound services are restricted but sufficient.
- [ ] If ICL encryption is required, IKED/IPsec HA link encryption is validated before cutover.
- [ ] Shared security policy, NAT, application, and profile config are equivalent where stateful failover is expected.
- [ ] Node-specific routing/interface configuration is intentionally different and documented.
- [ ] Forwarding interface/logical-unit design is compatible with stateful failover expectations.
- [ ] Symmetric routing is preferred or ICD/asymmetric-flow design is explicitly validated.
- [ ] If advanced inspection services are in policy, steady-state cross-node/Z-mode forwarding has been eliminated or explicitly validated against Juniper support guidance.
- [ ] IPsec on MNHA uses SRG1+, has `managed-services ipsec`, and IKED/package requirements are verified for the Junos release.
- [ ] VPN floating loopbacks, ICL context, physical underlay interfaces, security zones, and routing instances align; IKE gateway lookup has been tested from both nodes.
- [ ] Intra-zone IKE/ESP policy exists when VPN traffic is received on a physical interface and terminates on a loopback in the same zone.
- [ ] Remote-access pools are common per SRG or split per active/active SRG design to prevent address collisions after failover.
- [ ] NAT/SNAT pools, route advertisements, and upstream next hops produce deterministic return paths; proxy ARP is avoided unless explicitly tested.
- [ ] Sessions show Active/Warm state across both nodes.
- [ ] BGP/OSPF/static route preference selects the intended node.
- [ ] BFD sessions are stable and timers are realistic for the platform.
- [ ] SRG1+ VIPs install only on the active node.
- [ ] Signal-route export policy uses explicit route filters.
- [ ] Failover tests cover single-link, dual-link, node reboot, ICL loss, and failback/preemption if used.
- [ ] DHCP uses relay when possible; if local DHCP is used, pools are split and non-overlapping.

## Troubleshooting Commands

MNHA state:

```text
show chassis high-availability information
show chassis high-availability services-redundancy-group 0
show chassis high-availability services-redundancy-group <SRG>
show configuration chassis high-availability | display set
```

ICL and HA liveness:

```text
show route <PEER_ICL_IP>
ping routing-instance <ICL_RI> <PEER_ICL_IP>
show security ipsec security-associations    # only when ICL encryption is enabled
show security ike security-associations      # only when ICL encryption is enabled
```

Session, IPsec, routing, VIP, and DHCP checks are listed inline in their sections above.

## Common Pitfalls

1. Treating MNHA like chassis cluster. MNHA nodes are independent devices with synchronized runtime state, not one logical chassis.

2. Forgetting configuration synchronization. Security policy and NAT differences can break stateful failover even when sessions synchronize.

3. Building routed MNHA but allowing asymmetric flows accidentally. Prefer symmetry; use ICD only when planned and tested.

4. Using broad lab security settings in production. Avoid `default-policy permit-all`, `host-inbound all`, or broad direct-route export unless explicitly intended.

5. Exporting too many routes from signal-route policy. Put route filters on every accept term.

6. Using production prefixes as signal routes. Use reserved, non-routed, non-conflicting prefixes.

7. Assuming BFD timers from a lab are safe everywhere. Tune timers per hardware, topology, and operational tolerance.

8. Enabling preemption without testing routing readiness. Failback can blackhole traffic if SRG ownership returns before BGP/forwarding is converged.

9. Assuming DHCP state is shared. For local DHCP, split pools and use node-specific server identifiers; prefer relay when possible.

10. Ignoring ICL security and reachability. If ICL fails, sync fails; if ICL is exposed, HA state can become a security risk.

11. Anchoring MNHA IPsec on a floating loopback in a different routing instance from the ICL/MNHA context. IKE gateway lookup is control-plane/self-traffic behavior; route leaking that fixes transit traffic may not fix IKE.

12. Putting the VPN loopback and receiving physical interface in different security zones. The tunnel can fail with reroute errors even when basic IP reachability exists.

13. Assuming `process-packet-on-backup` or ICD makes all asymmetric designs safe. Advanced inspection services need bidirectional visibility; sustained cross-node flows should be engineered out of steady state.

14. Using proxy ARP for NAT pool reachability as if MNHA were chassis cluster. Both independent nodes can answer ARP, and return traffic can land on the wrong node.

15. Reusing the same remote-access address pool across independently active SRGs without splitting ranges. Failover may preserve a pool, but active/active SRGs can collide.

16. Forgetting to dissolve `groups node0` / `groups node1`. On a chassis cluster those per-node groups carried node-specific config; on MNHA each node is a standalone device, so that config must become direct `system`/interface configuration on the respective node. Leaving it as `apply-groups node0/node1` (which has no cluster context to key on) drops the settings.

17. Forgetting that management/enrollment identity is per-node. `outbound-ssh`, EMS, and Security Director Cloud `device-id` are node-local: after migration each SRX re-enrolls as a **separate** managed device. Plan the re-enrollment and update inventory/licensing per node rather than expecting the cluster's single managed-device identity to carry over.

18. Leaving a stray static default route via an unzoned management/extra leg — black-holes transit return traffic. See Field-Confirmed Behaviors below.

## Field-Confirmed Behaviors

Two behaviors independently confirmed on a live MNHA pair (vSRX3, Junos
24.4R1.9, SRG0+SRG1 hybrid, ICL on a dedicated VLAN, VIP as downstream
gateway — [fwskillsshare issue #7](https://github.com/fastrevmd-lab/fwskillsshare/issues/7)):

- **Unzoned-leg default route black-holes transit** (pitfall 18): nodes
  shipped with a static default via an unzoned `ge-0/0/3` management leg;
  transit return traffic silently disappeared. Removing the static default so
  the BGP-learned default from the upstream won fixed transit immediately.
- **The backup node does not service SRG data traffic**: a datapath test
  sourced from the *backup* node's interface fails (0 replies) while the same
  test via the VIP / active node works. `show chassis high-availability
  services-redundancy-group 1` shows `Process Packet In Backup State: NO` —
  expected behavior, not a fault. Test through the VIP or the active node
  before chasing a non-bug.
- The host-inbound-traffic system-services high-availability zone knob
  commit-checks clean on vSRX 24.4R1 (live-verified 2026-07).

## Source Notes

This skill is a synthesized operational playbook based on five Juniper Community TechPosts by James Rathbun, Steven Jacques, and Laurent Paumelle. Full extracted source references are stored under `references/` for local provenance.

Sections on chassis-cluster interface migration, SRG monitor-object syntax, and pitfalls 16-18 are field/QA additions beyond the five source articles; live-verified items are called out in Field-Confirmed Behaviors.

Per user instruction, ambiguous or conflicting article details were not encoded as hard guidance. Where support depends on platform or Junos release, this skill points operators to current Juniper documentation instead of freezing a source-specific matrix.
