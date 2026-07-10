---
name: srx-nat
description: Design, configure, audit, or troubleshoot Juniper SRX NAT. Use for source, destination, static, NAT64 or DNS64, CGN or PBA, persistent or address-persistent NAT, hairpinning, proxy ARP, rule order, session verification, pool exhaustion, security nat configuration, show security nat output, or RT_NAT logs.
version: 1.1.2
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [srx, junos, nat, source-nat, destination-nat, static-nat, nat64, dns64, cgn, pba, persistent-nat, hairpin, proxy-arp]
    related_skills: [parsing-srx-configs, srx-policy, srx-mnha, srx-mpls-in-flow, srx-autovpn-full-tunnel, srx-ipsec-hub-spoke]
  sources:
    - title: DNS64 and NAT64 on SRX Series
      author: Steven Jacques
      url: https://community.juniper.net/blogs/steven-jacques/2025/02/12/dns64-and-nat64-on-srx-series?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
      retrieved: "2026-05-15"
    - title: SRX4600 CGN Configuration Breakdown
      author: Karel Hendrych
      url: https://community.juniper.net/blogs/karel-hendrych/2024/11/15/srx4600-cgn-configuration-breakdown
      retrieved: "2026-05-15"
    - title: SRX EVPN/VXLAN T5 oIPSEC
      author: Karel Hendrych
      url: https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec
      retrieved: "2026-05-15"
    - title: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX
      author: Maxim Tveritnev
      url: https://community.juniper.net/discussion/source-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx
      retrieved: "2026-05-15"
    - title: Source NAT Part 3 - Large Scale Configuration, Design and Lab Demo using Juniper SRX
      author: Maxim Tveritnev
      url: https://community.juniper.net/discussion/source-nat-part-3-large-scale-configuration-design-and-lab-demo-using-juniper-srx
      retrieved: "2026-05-15"
    - title: SRX340 NAT hairpinning
      url: https://community.juniper.net/discussion/srx340-nat-hairpinning
      retrieved: "2026-05-15"
    - title: NAT Overview
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/security-nat-overview.html
      retrieved: "2026-05-15"
    - title: "[SRX] Understanding and Using address-persistent in Source NAT on Juniper SRX"
      author: Juniper Networks Support
      url: https://supportportal.juniper.net/s/article/SRX-Understanding-and-Using-address-persistent-in-Source-NAT-on-Juniper-SRX
      retrieved: "2026-05-15"
    - title: Resolution Guide - SRX - Troubleshoot Destination NAT
      author: Juniper Networks Support
      url: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Destination-NAT
      retrieved: "2026-05-15"
    - title: Resolution Guide - SRX - Troubleshoot Source NAT
      author: Juniper Networks Support
      url: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Source-NAT
      retrieved: "2026-05-15"
---

# SRX NAT

## Overview

SRX NAT is flow-based translation performed during first-packet session setup. Use this skill to reason about how Junos chooses a NAT rule, how translated addresses affect route and policy lookup, and how to verify the resulting session wings.

Core SRX NAT types:

- **Source NAT** changes the client/source address after route and security policy lookup. It is used for Internet access, carrier-grade NAT, NAT64 source translation, and hairpin return symmetry.
- **Destination NAT** changes the destination before route and security policy lookup. It is used for publishing inside servers behind public or shared addresses.
- **Static NAT** is bidirectional 1:1 or prefix translation. It has higher precedence than destination NAT, and reverse static NAT has higher precedence than source NAT.
- **NAT64** on SRX is usually built with static NAT `inet` destination extraction from `64:ff9b::/96` plus a normal source NAT action to a reachable IPv4 source.

Always inspect the translated session, not only the configuration. Correct NAT configuration with wrong routes, policy, proxy ARP, or return path still fails.

## When to Use

Use this skill when the user asks about:

- Juniper SRX NAT design, validation, migration, audit, or troubleshooting
- `security nat source`, `security nat destination`, `security nat static`, or `security nat proxy-arp`
- interface source NAT, pool source NAT, PAT, NAT pools, address pooling, or address persistence
- published servers, port forwarding, destination NAT, or static NAT
- source NAT or destination NAT rule counters and translation hits
- NAT rule order, rule-set specificity, static NAT precedence, or policy lookup after NAT
- hairpin NAT / NAT reflection / inside users accessing an inside server through its public IP
- DNS64 and NAT64 on SRX
- CGN, SRX4600 carrier-grade NAT, port block allocation, paired address pooling, persistent NAT, endpoint-independent mapping, or NAT logging
- address-persistent problems, VPN over NAT problems, speedtest issues, or TCP MSS workarounds
- troubleshooting with `show security nat ...`, `show security flow session ...`, flow traceoptions, or proxy ARP checks

Do not use this as the primary skill for parsing an entire SRX config. Load `parsing-srx-configs` first for extraction, then use this skill to interpret and fix the NAT behavior. For policy design on the post-NAT path, load `srx-policy`.

## NAT Processing Order

For the first packet of a flow, SRX processes NAT and lookup in this order:

1. Static NAT rules
2. Destination NAT rules
3. Route lookup
4. Security policy lookup
5. Reverse mapping of static NAT rules
6. Source NAT rules

Operational consequences:

- Static NAT takes precedence over destination NAT.
- Destination NAT and static NAT happen before route lookup. Their rule sets match source interface, source zone, or source routing instance; they cannot match destination zone/interface/routing-instance because that has not been resolved yet.
- Security policy lookup happens after destination/static NAT, so the policy usually matches the translated destination and the post-NAT egress zone.
- Source NAT happens after route and policy lookup, so source NAT rule sets use both `from` and `to` contexts.
- Reverse static NAT takes precedence over source NAT for return traffic.
- NAT64 source NAT must match an IPv4 destination because static NAT64 translated the destination from `64:ff9b::/96` to IPv4 before source NAT evaluation.

## Rule-Set Selection and Rule Order

### Static and Destination NAT Rule-Set Specificity

For static NAT and destination NAT, if multiple rule sets match, SRX chooses the more specific source-side match:

1. Source interface
2. Source zone
3. Source routing instance

### Source NAT Rule-Set Specificity

Source NAT rule-set choice considers source and destination context. In decreasing specificity:

1. Source interface + destination interface
2. Source zone + destination interface
3. Source routing instance + destination interface
4. Source interface + destination zone
5. Source zone + destination zone
6. Source routing instance + destination zone
7. Source interface + destination routing instance
8. Source zone + destination routing instance
9. Source routing instance + destination routing instance

### Rule Order Within a Rule Set

Within the chosen rule set, rules are evaluated top-down and the first matching rule wins.

Design rules:

- Put no-NAT and exception rules above broad NAT rules.
- Put persistent NAT / gaming / special application rules above normal CGN rules.
- Put specific host/server rules above subnet or `any` rules.
- Use distinct rule-set names that encode direction, such as `TRUST_TO_UNTRUST`, `DNAT_IN`, or `HAIRPIN`.
- After reordering, generate traffic and check translation hits rather than assuming the intended rule is used.

## Basic Source NAT Patterns

### Interface Source NAT

Use this when inside clients should overload on the egress interface address.

```junos
set security nat source rule-set TRUST_TO_UNTRUST from zone trust
set security nat source rule-set TRUST_TO_UNTRUST to zone untrust
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_NAT match source-address 192.168.1.0/24
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_NAT match destination-address 0.0.0.0/0
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_NAT then source-nat interface
```

Verify:

```text
show security nat source rule all
show security flow session source-prefix 192.168.1.10 extensive
```

### Pool Source NAT

Use a pool when the translated source must be a specific address or prefix.

```junos
set security nat source pool SRC_POOL address 203.0.113.10/32
set security nat source rule-set TRUST_TO_UNTRUST from zone trust
set security nat source rule-set TRUST_TO_UNTRUST to zone untrust
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_POOL_NAT match source-address 192.168.1.0/24
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_POOL_NAT match destination-address 0.0.0.0/0
set security nat source rule-set TRUST_TO_UNTRUST rule SRC_POOL_NAT then source-nat pool SRC_POOL
```

If the pool address is on a directly connected external subnet and the upstream device expects ARP for it, configure proxy ARP or, preferably, route the pool prefix to the SRX.

```junos
set security nat proxy-arp interface ge-0/0/0.0 address 203.0.113.10/32
```

## Destination NAT and Static NAT Patterns

### Destination NAT for a Published Server

Example: public `203.0.113.20:443` to inside server `192.168.10.20:443`.

```junos
set security nat destination pool WEB_SERVER address 192.168.10.20/32
set security nat destination rule-set DNAT_IN from zone untrust
set security nat destination rule-set DNAT_IN rule WEB_HTTPS match destination-address 203.0.113.20/32
set security nat destination rule-set DNAT_IN rule WEB_HTTPS match destination-port 443
set security nat destination rule-set DNAT_IN rule WEB_HTTPS then destination-nat pool WEB_SERVER
```

Port translation (port forwarding, e.g. public `:8443` → inside `:443`) is
configured on the **pool**, not the rule (verified on vSRX 24.4R1 — `... pool
<name> port <port>` on the rule is a syntax error):

```junos
set security nat destination pool WEB_SERVER_443 address 192.168.10.20/32 port 443
set security nat destination rule-set DNAT_IN rule WEB_ALT match destination-port 8443
set security nat destination rule-set DNAT_IN rule WEB_ALT match destination-address 203.0.113.20/32
set security nat destination rule-set DNAT_IN rule WEB_ALT then destination-nat pool WEB_SERVER_443
```

Security policy must permit the translated path:

```junos
set security policies from-zone untrust to-zone trust policy ALLOW_WEB match source-address any
set security policies from-zone untrust to-zone trust policy ALLOW_WEB match destination-address WEB_SERVER_ADDR
set security policies from-zone untrust to-zone trust policy ALLOW_WEB match application junos-https
set security policies from-zone untrust to-zone trust policy ALLOW_WEB then permit
set security policies from-zone untrust to-zone trust policy ALLOW_WEB then log session-init
set security policies from-zone untrust to-zone trust policy ALLOW_WEB then log session-close
```

Important checks:

- Is the public IP routed to the SRX, assigned to the external interface, or answered by proxy ARP?
- Does `show security nat destination rule all` show translation hits?
- Does the session show the post-DNAT destination and expected egress zone?
- Does the inside server route its return traffic back through the SRX?

### Static NAT One-to-One

```junos
set security nat static rule-set STATIC_IN from zone untrust
set security nat static rule-set STATIC_IN rule SERVER_1 match destination-address 203.0.113.30/32
set security nat static rule-set STATIC_IN rule SERVER_1 then static-nat prefix 192.168.10.30/32
```

Use static NAT when both inbound and outbound flows should map predictably. Remember that static NAT can override destination NAT for overlapping public addresses.

### Static NAT for Overlapping Networks

For tenant or VPN designs with overlapping prefixes, use static NAT prefixes and explicit routing-instance/routing-group context. Keep the synthetic prefixes routable and documented.

Conceptual pattern:

```junos
set security l3vpn vrf-group VRF-GRP-TENANT-1 vrf tenant-1
set security nat static rule-set TENANT1_TO_TENANT3 from routing-group VRF-GRP-TENANT-1
set security nat static rule-set TENANT1_TO_TENANT3 rule T1_TO_T3 match source-address 10.1.0.0/16
set security nat static rule-set TENANT1_TO_TENANT3 rule T1_TO_T3 match destination-address 10.23.0.0/16
set security nat static rule-set TENANT1_TO_TENANT3 rule T1_TO_T3 then static-nat prefix 10.1.0.0/16
set security nat static rule-set TENANT1_TO_TENANT3 rule T1_TO_T3 then static-nat prefix routing-instance tenant-3
```

Live-verified on vSRX 24.4R1: `from routing-group` references a `security l3vpn vrf-group` name, not a routing-instance — pointing it at a routing instance fails commit with `Vrf-group must be defined`.

Verify route tables and session wings in every routing instance involved.

## Proxy ARP Decision

Use proxy ARP only when the upstream L2 segment expects the SRX to answer ARP for translated public addresses that are not configured on the SRX interface.

```junos
set security nat proxy-arp interface ge-0/0/0.0 address 203.0.113.20/32
set security nat proxy-arp interface ge-0/0/0.0 address 203.0.113.30/32
```

Prefer routing a NAT pool prefix to the SRX when possible. Proxy ARP is easy to forget, hard to see in the session table, and risky in HA/MNHA designs where multiple nodes can answer for the same translated address.

## Hairpin NAT

Hairpin NAT is needed when inside clients access an inside server through its public/NAT address.

Required pieces:

1. A destination NAT rule that matches the inside source zone as well as the outside zone.
2. A source NAT rule for the inside-to-inside hairpin flow so the server replies to the SRX, not directly to the client.
3. A security policy for the resulting inside-to-inside path.
4. Correct server default gateway or route back to the SRX.

Destination NAT from inside:

```junos
set security nat destination rule-set DNAT_HAIRPIN from zone trust
set security nat destination rule-set DNAT_HAIRPIN rule WEB_HAIRPIN match destination-address 203.0.113.20/32
set security nat destination rule-set DNAT_HAIRPIN rule WEB_HAIRPIN match destination-port 443
set security nat destination rule-set DNAT_HAIRPIN rule WEB_HAIRPIN then destination-nat pool WEB_SERVER
```

Source NAT for return symmetry:

```junos
set security nat source pool HAIRPIN_SRC address 192.168.10.1/32
set security nat source rule-set HAIRPIN_SNAT from zone trust
set security nat source rule-set HAIRPIN_SNAT to zone trust
set security nat source rule-set HAIRPIN_SNAT rule HAIRPIN match source-address 192.168.1.0/24
set security nat source rule-set HAIRPIN_SNAT rule HAIRPIN match destination-address 192.168.10.20/32
set security nat source rule-set HAIRPIN_SNAT rule HAIRPIN then source-nat pool HAIRPIN_SRC
```

Policy:

```junos
set security address-book global address LAN_CLIENTS 192.168.1.0/24
set security address-book global address WEB_SERVER_ADDR 192.168.10.20/32
set security policies from-zone trust to-zone trust policy PERMIT_HAIRPIN match source-address LAN_CLIENTS
set security policies from-zone trust to-zone trust policy PERMIT_HAIRPIN match destination-address WEB_SERVER_ADDR
set security policies from-zone trust to-zone trust policy PERMIT_HAIRPIN match application junos-https
set security policies from-zone trust to-zone trust policy PERMIT_HAIRPIN then permit
set security policies from-zone trust to-zone trust policy PERMIT_HAIRPIN then log session-close
```

For CGN or persistent NAT hairpin cases, use a dedicated inside-to-inside policy and inspect session-close/update logs. Avoid broad `any any permit` hairpin policy without logging and a change record.

## NAT64 with DNS64

DNS64 synthesizes an IPv6 AAAA record from an IPv4 A record. With the well-known prefix `64:ff9b::/96`, the last 32 bits encode the IPv4 destination. SRX NAT64 extracts those last 32 bits and translates the IPv6 destination to IPv4.

Process:

1. IPv6-only client queries a DNS64 resolver.
2. DNS64 returns an address under `64:ff9b::/96` with the IPv4 address embedded in the last 32 bits.
3. SRX static NAT64 matches the NAT64 prefix and uses `static-nat inet` to extract the IPv4 destination.
4. SRX source NAT translates the IPv6 client source to an IPv4 source.
5. Return traffic maps back through the SRX session.

Static NAT64 destination extraction:

```junos
set security nat static rule-set NAT64 from zone trust
set security nat static rule-set NAT64 rule NAT64 match source-address ::/0
set security nat static rule-set NAT64 rule NAT64 match destination-address 64:ff9b::/96
set security nat static rule-set NAT64 rule NAT64 then static-nat inet
```

Source NAT for NAT64:

```junos
set security nat source rule-set NAT64_SNAT from zone trust
set security nat source rule-set NAT64_SNAT to zone untrust
set security nat source rule-set NAT64_SNAT rule NAT64_SNAT match source-address ::/0
set security nat source rule-set NAT64_SNAT rule NAT64_SNAT match destination-address 0.0.0.0/0
set security nat source rule-set NAT64_SNAT rule NAT64_SNAT then source-nat interface
```

The `destination-address 0.0.0.0/0` is intentional. Static NAT64 has already translated the destination to IPv4 before source NAT rule evaluation. If you match `64:ff9b::/96` in the source NAT rule, the source NAT rule will not match the translated flow.

Verification:

```text
host www.juniper.net
ping www.juniper.net
curl -6 https://www.juniper.net
show security nat static rule all
show security nat source rule all
show security flow session destination-port 443 extensive
```

Expected session pattern:

```text
In:  <IPv6-client> --> 64:ff9b::<embedded-v4>/443
Out: <real-IPv4-destination>/443 --> <translated-IPv4-source>/<port>
```

NAT64 caveats:

- DNS64 is required for hostname-based access unless the client explicitly uses embedded NAT64 notation.
- Native IPv6 destinations should not be caught by the NAT64 source NAT rule.
- Per the Juniper NAT overview, NAT64 traffic is not processed on the PowerMode IPsec (PMI) fast path; with PMI enabled, NAT64 flows are handled in the normal processing path instead. Verify current release/platform behavior before relying on it.

## CGN, PBA, and Persistent NAT

Carrier-grade NAT on SRX should be treated as a capacity-managed service, not just a large source NAT pool.

### Port Block Allocation

PBA allocates blocks of ports to subscribers. Example pattern from the SRX4600 CGN source:

```junos
set security nat source pool POOL_1 address 1.2.84.0/24
set security nat source pool POOL_1 address 1.2.85.0/24
set security nat source pool POOL_1 address 1.2.86.0/24
set security nat source pool POOL_1 address 1.2.87.0/24
set security nat source pool POOL_1 port block-allocation block-size 1280
set security nat source pool POOL_1 port block-allocation maximum-blocks-per-host 3
set security nat source pool POOL_1 port block-allocation last-block-recycle-timeout 300
set security nat source pool POOL_1 address-pooling paired
```

Guidance:

- `address-pooling paired` keeps a subscriber paired with the same NAT pool address and overrides global hash-based `address-persistent` behavior.
- `last-block-recycle-timeout` prevents the final allocated block from remaining allocated forever after the subscriber has no sessions.
- Start with realistic subscriber/session telemetry. Do not blindly copy lab block sizes.
- Active/active chassis cluster behavior can effectively reserve port ranges and reduce usable ports per public IP; size using observed platform behavior, not theoretical 65k ports.

### Selective Persistent NAT

**Pool port behavior:** source-NAT pools PAT by default (source ports are
translated). `set security nat source pool <name> port no-translation` keeps
original source ports (needs enough pool IPs); `port-overloading-factor <n>`
multiplies port capacity per pool IP at the cost of shared-port ambiguity.

Persistent NAT / endpoint-independent behavior helps selected applications such as gaming, STUN, and peer-to-peer flows, but it consumes extra state. Put persistent NAT rules before broad normal NAT rules and match only the necessary applications.

```junos
set security nat source rule-set LAN_TO_WAN from zone LAN
set security nat source rule-set LAN_TO_WAN to zone WAN
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match source-address 100.64.0.0/10
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match destination-address 0.0.0.0/0
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match application GAMING_CONSOLES_TUNED
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool POOL_1
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool persistent-nat permit any-remote-host
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match source-address 100.64.0.0/10
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match destination-address 0.0.0.0/0
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 then source-nat pool POOL_1
```

Optional hardening:

```junos
set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool persistent-nat block-ext-session
```

`block-ext-session` is a valid `persistent-nat` sibling knob (verified on vSRX
24.4R1); it requires `persistent-nat permit ...` on the same rule (already set
above) — alone it fails commit with `Missing mandatory statement: 'permit'`.

### Address-Persistent Symptoms

`address-persistent` keeps translated source mapping stable for a source IP. It can help protocols that require stable NAT mapping but can also cause symptoms such as:

- speedtest.net or similar services failing or underperforming
- intermittent website element failures
- VPN tunnels failing through NAT with persistent mappings

If persistence is not required, remove it globally (address-persistent lives at `[edit security nat source]`, not under a rule action; pool-level persistence is `pool <name> address-persistent subscriber ...`):

```text
delete security nat source address-persistent
```

If failures are related to tunnel/WAN MTU, consider a TCP MSS change after validating path MTU:

```junos
set security flow tcp-mss all-tcp mss 1350
```

## Verification Commands

Configuration:

```text
show configuration security nat | display set
show configuration security policies | display set
show configuration security zones | display set
show route <destination>
show route table <ri>.inet.0 <destination>
```

Rule counters:

```text
show security nat source rule all
show security nat destination rule all
show security nat static rule all
show security nat proxy-arp
```

Sessions:

```text
show security flow session source-prefix <source> extensive
show security flow session destination-prefix <destination> extensive
show security flow session destination-port <port> extensive
show security flow session | match "Session ID|In:|Out:|NAT|Policy name|Timeout"
```

CGN/PBA:

```text
show security nat source pool all
show security nat source persistent-nat-table summary
show security flow statistics
show security log statistics
show snmp mib walk jnxUtil ascii | match block | match value
```

Traceoptions, when counters and sessions do not explain the drop:

```junos
set security flow traceoptions file flow-nat-debug size 10m files 5
set security flow traceoptions flag basic-datapath
set security flow traceoptions packet-filter NAT-DEBUG source-prefix <source-ip>/32
set security flow traceoptions packet-filter NAT-DEBUG destination-prefix <destination-ip>/32
```

Use traceoptions for short maintenance windows only. Remove or deactivate them after collecting evidence.

## Troubleshooting Matrix

| Symptom | Likely Cause | Check | Fix |
|---|---|---|---|
| Source NAT translation hits do not increase | Wrong rule-set context or rule order | `show security nat source rule all` | Fix `from`/`to` context, move specific rule above catch-all |
| Source NAT hits increase but traffic fails | Route, policy, return path, or egress filtering | Session extensive, route table, policy log | Fix policy/route/upstream path |
| Pool source NAT fails on connected public subnet | Missing proxy ARP | `show security nat proxy-arp`, upstream ARP table | Add proxy ARP or route the prefix to SRX |
| Destination NAT hits do not increase | Wrong public IP/port/source zone, traffic not reaching SRX | `show security nat destination rule all`, ingress filter counters | Fix DNAT match or upstream forwarding |
| DNAT hits but policy denies | Policy matches wrong destination or zone | `show security flow session extensive` | Permit translated destination in post-DNAT zone |
| DNAT is ignored | Overlapping static NAT takes precedence | `show security nat static rule all` | Remove or redesign overlapping static NAT |
| Published server replies directly | Asymmetric return path | Server gateway and flow session | Route return traffic through SRX |
| Hairpin fails | Missing inside DNAT, source NAT, or trust-to-trust policy | Session In/Out tuples | Add inside-sourced DNAT, hairpin SNAT, and policy |
| NAT64 DNS works but traffic fails | Static NAT64 or source NAT rule mismatch | Static/source NAT counters and session | Match `64:ff9b::/96` in static NAT, IPv4 destination in source NAT |
| Native IPv6 breaks after NAT64 change | Over-broad source NAT | Session table | Ensure source NAT only matches post-static-NAT IPv4 destination |
| Source pool port exhaustion | Too few pool IPs for the session load | `show security nat source pool all` (ports used/available), `show security nat source summary`, RT_NAT syslog drops | Add pool IPs, raise `port-overloading-factor`, or narrow the rule match |
| PBA users cannot open new sessions | Pool/block exhaustion or max blocks per host | `show security nat source pool all`, PBA stats | Add public IPs, tune block size/max blocks/recycle timeout |
| Gaming/P2P fails behind CGN | No persistent NAT or rule too low in order | Persistent NAT table, rule hits | Add selective persistent NAT before broad NAT rule |
| Persistent NAT table high | Persistent NAT applied too broadly | `show security nat source persistent-nat-table summary` | Restrict to selected applications and consider `block-ext-session` |
| Speed tests or VPNs fail with address-persistent | Stable mapping harms application behavior or MTU issue | Rule config and path MTU | Remove `address-persistent` if not needed; consider TCP MSS tuning |

## Common Pitfalls

1. **Matching policy against the public DNAT address.** Security policy normally sees the translated destination and post-DNAT zone.

2. **Forgetting static NAT precedence.** Static NAT is evaluated before destination NAT, and reverse static NAT precedes source NAT.

3. **Assuming the selected rule-set is the visually nearest one.** Rule-set specificity can choose an interface-based rule set over a zone-based rule set before rule order inside the set matters.

4. **Leaving broad NAT rules above exceptions.** First matching rule in the chosen rule set wins.

5. **Missing proxy ARP for same-subnet public NAT IPs.** If the upstream sends ARP rather than routing the prefix, the SRX must answer on the correct interface.

6. **Troubleshooting only NAT and ignoring return routing.** NAT can be correct while the server/default route sends replies around the SRX.

7. **Building hairpin DNAT without hairpin SNAT.** If the inside server sees the real inside client, it can reply directly and bypass the SRX session.

8. **Writing NAT64 source NAT to match the NAT64 IPv6 prefix.** Source NAT is evaluated after static NAT64, so match the translated IPv4 destination.

9. **Applying persistent NAT too broadly.** Persistent NAT is useful for selected applications but can exhaust binding tables in CGN designs.

10. **Copying CGN PBA block sizes from a lab.** Size blocks and max blocks from subscriber telemetry, burst behavior, logging capacity, and platform behavior.

11. **Leaving flow traceoptions enabled.** Traceoptions can be expensive and noisy; use filtered traces and remove them after capture.

12. **Using proxy ARP casually in HA/MNHA.** Routed NAT prefixes are cleaner. Proxy ARP can create wrong-node return paths in independent-node HA designs.

## Verification Checklist

- [ ] NAT type chosen intentionally: source, destination, static, or NAT64 combination.
- [ ] Rule-set context matches the packet at the point SRX evaluates that NAT type.
- [ ] Specific rules and no-NAT exceptions precede broad catch-all rules.
- [ ] Static NAT overlap with destination/source NAT is intentional and documented.
- [ ] Destination NAT/static NAT policy matches the translated destination and post-NAT zone.
- [ ] Source NAT pools (and static/destination translated addresses) are either routed to SRX or covered by proxy ARP (IPv4) / proxy NDP (IPv6) on the correct interface.
- [ ] Return path from translated destinations goes back through SRX.
- [ ] Hairpin flows include inside DNAT, hairpin source NAT, and inside-to-inside policy.
- [ ] NAT64 static NAT uses `static-nat inet`; NAT64 source NAT matches IPv4 destination.
- [ ] CGN pools/PBA blocks are sized with telemetry and have recycle behavior configured.
- [ ] Persistent NAT and address-persistent are limited to applications that require them.
- [ ] `show security nat ... rule all` counters increase on the intended rule.
- [ ] `show security flow session ... extensive` shows expected In/Out translated tuples and policy.
- [ ] Flow traceoptions are removed/deactivated after troubleshooting.

## Source Notes

This skill is a synthesized operational playbook from Juniper Community TechPosts, Juniper NAT documentation, and Juniper Support resolution guides. Full source extracts and condensed support portal notes are stored under `references/` (see `references/source-index.md`) for provenance.
