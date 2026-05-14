# SRX MPLS in Flow - Part 2

Source: https://community.juniper.net/blogs/karel-hendrych/2026/04/22/srx-mpls-in-flow-part-2?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
Author: Karel Hendrych
Retrieved: 2026-05-14

## Extracted Article Text

The Junos 25.4R1 release expanded the list of SRX platforms supporting MPLS L3 VPN to include the SRX4600 and SRX4700. This brief tech post extends the previous 'SRX MPLS in Flow' article by presenting performance test of the SRX4600 using the 25.4R1 VRF-to-zone-mapping-based security policies.
Introduction
Prerequisite: read the
SRX MPLS in Flow post
for a thorough introduction.
In 25.4R1, in addition to
new platform support
, Junos adds the ability
to bind VRFs to zones
, simplifying policy constructs by setting VRF context by zone instead of by rule match criteria.
For NAT use cases the VRF-groups approach still applies as of 25.4R1. The VRF-to-zone-mapping topic is also covered more broadly in the
SRX Secure Fabric Entry Point write-up
(focused on EVPN/VXLAN T5 type VRFs).
The SRX4600 and SRX4700, equipped with HPE Juniper's in house Packet Forwarding Engine (PFE), handle MPLS traffic with up to 16 labels. Traffic is hashed using inner L4 headers to distribute load across SPU resources (SPU refers to the Security Processing Unit; both SRX4600 and SRX4700 use two physical CPUs and these constitute the single platform SPU). As of 25.4R1, MPLS traffic is not subject to Express Path acceleration, but the hardware PFE does SPU load balancing by ignoring MPLS headers and using the inner IP headers. Relying on MPLS labels for traffic distribution alone would produce uneven CPU-core utilization resulting in some cores idle and others overloaded.
The Demo Topology
The demo topology is similar to the original article but for performance testing purposes has been moved to physical devices. The vSRX devices have been replaced by SRX4600s as the PE devices, the MX204 as the P device, and tester ports as the Linux namespace entities. Overall link capacity is limited to 100 Gbps because the MX204 uses only one physical 100GE interface; however, the effective bottleneck is the maximum throughput between the hardware PFE and the SPU on the SRX4600, which is just below 100 Gbps. Another change is the addition of external zones that bind VRFs. For illustration, the overlapping IP address space from the original article between VRF-1 and VRF-2 has been preserved. Tester traffic flows between left and right hosts within the same VRF (effectively traversing the SRX's internal and external zones). Tester prefixes are, from the SRX devices' perspective, routed via the tester as the next hop. Debian Linux machines serve for the purpose of single TCP session performance evaluation.
Figure 1 Demo topology
Configuration Break-down
Let's break down the nuances of the SRX4600-5 configuration compared to vSRX-left from
the original Tech Post
. The SRX4600-6 is essentially identical to the SRX4600-5, differing only in IP addressing. The same applies to the MX204 compared with the vSRX-router. Complete configuration files are available in Appendix 1.
Internal zones are essentially the same; only the interface-zone mapping differs because the lab setup uses VLAN units on the et-1/0/1 physical interface. The mpls zone binding the underlay MPLS interface is intended only for protocol signalling and is no longer used in transit policies:
edit security zones
set security-zone vrf-1-int interfaces et-1/0/1.1110 host-inbound-traffic system-services ping
set security-zone vrf-2-int interfaces et-1/0/1.1111 host-inbound-traffic system-services ping
set security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic system-services ping
set security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic protocols ospf
set security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic protocols ldp
The tester relies on static next-hop routing rather than a routing protocol, so matching static routes must exist on the SRX and are automatically exported into each VRF:
set routing-instances vrf-1 routing-options static route 10.0.0.0/16 next-hop 10.255.254.10
The VRF-to-zone mapping is as simple as this:
edit security zones
set security-zone
vrf-1-ext vrf vrf-1
set security-zone
vrf-2-ext vrf vrf-2
The signaling part with mpls zone intrazone policy:
edit security policies
set from-zone mpls to-zone mpls policy signalling match source-address any
set from-zone mpls to-zone mpls policy signalling match destination-address any
set from-zone mpls to-zone mpls policy signalling match application junos-bgp
set from-zone mpls to-zone mpls policy signalling match application junos-icmp-ping
set from-zone mpls to-zone mpls policy signalling match application junos-ldp-tcp
set from-zone mpls to-zone mpls policy signalling then permit
Transit-zone policies allow traffic in both directions within the VRFs. As a sidenote, the 25.4R1 VRF-to-zone mapping doesn't permit mixing interfaces and VRFs, so policies can't be simplified into intrazone matches. The final policy is used solely to count denied traffic:
edit security policies
set from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match source-address any
set from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match destination-address any
set from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match application any
set from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext then permit
set from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match source-address any
set from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match destination-address any
set from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match application any
set from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext then permit
set from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match source-address any
set from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match destination-address any
set from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match application any
set from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int then permit
set from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match source-address any
set from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match destination-address any
set from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match application any
set from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int then permit
set global policy final match source-address any
set global policy final match destination-address any
set global policy final match application any
set global policy final then deny
Finally, disabling
drop-flow
is best practice for arbitrary testing, due to the potential logging load when tester traffic is denied by policies. Drop-flow inserts an arbitrary short-lived session-table record for dropped traffic. When a match occurs, the packet is dropped without policy evaluation in the slow path. To disable:
set security flow drop-flow max-sessions 0
Performance Evaluation
Now the interesting part - performance. The impacting factor is
PowerMode (PM)
- essentially the SRX leveraging vector-processing CPU capabilities, where the same instruction processes multiple data elements. Because traffic subjected to MPLS processing is not eligible for PM, you can avoid the extra cost of determining eligibility by disabling PM. Both overall and single session performance tests include data points with PM on and PM off. Whether a session is PM eligible can be seen in the detailed session listing. Although PM is enabled by default since Junos 21.3:
> show security flow status
Flow forwarding mode:
Inet forwarding mode: flow based
Inet6 forwarding mode: flow based
MPLS forwarding mode: packet based
ISO forwarding mode: drop
Tap mode: disabled (default)
Flow scaled L3L4 mode:
Scaled L3L4 mode: Disabled
Flow default policy profile:
Selective session sync: Enabled
Session sync min age: 0
Flow trace status
Flow tracing status: off
Flow session distribution
Distribution mode: Hash-based
GTP-U distribution: Disabled
SCTP distribution: Enabled
Flow gre performance acceleration: off
Flow packet ordering
Ordering mode: Hardware
Flow power mode: Enabled
Flow power mode IPsec: Enabled
Flow power mode IPsec QAT: Disabled
Fat core group status: off
Flow inline fpga crypto: Disabled
Flow multicast strict-order: Disabled
Flow Drop-flow Summary:
Maximum Drop-flow sessions: 0
Timeout: 4s
Logging: Disabled
The session (both wings) are not being processed in PM, instead in Regular Flow Path (RFP):
> show security flow session destination-port 1025 extensive
Session ID: 124596564000, Status: Normal
Flags: 0x40/0x0/0x2/0x3/0x8
Policy name: vrf-1-int-ext/4
Source NAT pool: Null
Dynamic application: junos:UNKNOWN,
Encryption:  Unknown
Url-category:  Unknown
Application traffic control rule-set: INVALID, Rule: INVALID
Maximum timeout: 60, Current timeout: 60
Session State: Valid
Start time: 1774653973, Duration: 984
In: 10.0.0.1/1025 --> 10.1.0.1/1025;udp,
Conn Tag: 0x0, Attachment Id: 0, GW Endpoint Id: 0, Flow Cookie: 0, Interface: et-1/0/1.1110,
Session token: 0x5007, Flag: 0x21,
Power-Mode Active: False
Route: 0xc0010, Gateway: 10.255.255.10, Tunnel ID: 0, Tunnel type: None,
Port sequence: 0, FIN sequence: 0,
FIN state: 0,
Pkts: 342386902, Bytes: 19173666512
Out: 10.1.0.1/1025 --> 10.0.0.1/1025;udp,
Conn Tag: 0x0, VRF: vrf-1, VRF Zone: vrf-1-ext, Interface: et-1/0/0.1112,
Session token: 0x9, Flag: 0x20,
Power-Mode Active: False
Route: 0xa0010, Gateway: 192.168.0.2, Tunnel ID: 0, Tunnel type: None,
Port sequence: 0, FIN sequence: 0,
FIN state: 0,
Pkts: 349910746, Bytes: 19595001776
Total sessions: 1
To globally disable PM mode, the following command can be used:
set security flow power-mode-disable
Sidenote - in some cases one session wing may be subject to PM while the other is not - for example, in EVPN/VXLAN T5 setups. Whether to keep PM enabled depends on tradeoffs. One reason to keep PM enabled is when the device also functions as an IPSEC concentrator for non MPLS traffic as
PowerMode IPSEC
(PMI) can substantially improve IPSEC performance.
For assessing performance on 1500 bytes MTU links, it makes most sense to consider mid sized frames (about 750 bytes) as a conservative average; IMIX is seen in networks with small packets applications - e.g., heavy VoIP, IoT. What matters most for the SRX in terms of software processing across packet sizes up to 1500 bytes is packet rate, not packet size - at the same packet rate, larger packets deliver more bandwidth. Packet rates are lower with jumbo packets, however.
Finally, mileage may vary: real world results will differ depending on traffic patterns and enabled features. It is strongly recommended to evaluate the exact scenarios.
Overall performance
UDP Performance
Overall forwarding performance with UDP is an arbitrary test of best-case forwarding capacity when connection establishment is excluded and no features are configured. Exact scenario:
SRX4600, Junos 25.4R1-S1.4
UDP sessions using source and destination port 1024
Each VRF has 256 endpoints sending traffic to each other in a full mesh
Overall session count: 130,050
Bi directional traffic with a 50/50 split
IMIX 7:4:1 with 78 : 570 : 1500 Bytes packet sizes (78 Bytes reflects tester-added signatures)
0.000% packet loss tolerance
Frame Size
(Bytes)
PMI
MPPS
L2 Gbps
SPU
Core Load
78
ON
12
7.49
97
IMIX
ON
12
34.6
98
750
ON
12
72
99
1500
ON
8
96*
75*
78
OFF
14
8.73
97
IMIX
OFF
13.6
39.2
96
750
OFF
13.6
81.6
98
1500
OFF
8
96*
66*
*SRX4600 Eagle chipset - Intel SPU complex interlink FPGA bandwidth limit
TCP Performance
Overall forwarding performance with TCP traffic is closer to real life because of additional factors - connection setup/teardown and the resulting concurrent-connection counts. TCP is also subject to state checks and sequence validation (although on the SRX, the TCP packet rate without connection setups doesn't differ much from UDP). KPIs were collected on SRX4600-5; SPU load was also measured on SRX4600-6 because handling the dominant server-to-client traffic from interface-to-VRF is less CPU-intensive than the VRF-to-interface direction.
SRX4600, Junos 25.4R1 S1.4
HTTP clients on the SRX4600 5 side, servers behind the SRX4600 6
HTTP GET transactions with 60kB random file payloads (~64kB on the wire)
64k HTTP clients connecting to 2k servers (32,768 clients to 1,024 servers per VRF)
0.000% packet loss tolerance
PMI
Transaction Rate
Concurrent Connections
MPPS (C2S/S2C)
L2 Gbps
(C2S/S2C)
SPU core SRX4600-5
SPU core SRX4600-6
ON
170,000
670,000
9.0 (1.4 / 7.6)
89 (1 / 88)
92
84
OFF
180,000
750,000
9.5 (1.4 / 8.1)
94 (1 / 93)
89
77
Sidenote - concurrent connections depend on transaction rate, transaction duration, and the time it takes to remove the session from the sessions table (about 4 s on the SRX by default).
Single Session Performance
Single session performance (relevant for highspeed WAN links) is the device's ability to forward elephant flows typical in inter-Data Centre scenarios. Specifically, the SRX4600 has 24 cores dedicated to software processing; a single core is used for single session processing, selected via an L4 hash.
UDP Single Session Performance
Exact scenario:
SRX4600, Junos 25.4R1 S1.4
Single UDP session using source and destination port 1025
Bi directional traffic with a 50/50 split
IMIX 7:4:1 with 78 : 570 : 1500 Bytes packet sizes (78 Bytes reflects tester added signatures)
0.000% packet loss tolerance
Frame Size
(Bytes)
PMI
kPPS
L2 Mbps
CPU
Core Load
78
ON
700
437
99
IMIX
ON
680
1960
99
750
ON
680
4080
99
1500
ON
680
8160
99
78
OFF
820
511
99
IMIX
OFF
820
2365
99
750
OFF
800
4800
99
1500
OFF
800
9600
99
TCP Single Session Performance
TCP single session performance testing is more applicable to real life because, with TCP, small ACK flagged segments count toward packet rates. Professional stateful test tools typically excel at many concurrent transactions but not at maximizing a single TCP session, so the opensource tool
nuttcp
was used. This test also includes jumbo frames for large data transfers. Exact scenario:
Debian Linux 13 VMs
4x AMD EPYC 7543 core
32 GB RAM
100GE NIC, Intel E810, PCI-Passthrough
Default networking stack settings
nuttcp 8.2.2 from Debian repositories
nuttcp server side on Debian-right, client side on Debian-left
Server-side command - uppercase S for server and nofork to avoid forking to background:
nuttcp -S -nofork
Client-side command - reporting interval every 10 seconds, duration 1 minute:
nuttcp -i10 -T1m 10.255.255.20
Sample client summary for 9000 byte MTU with PMI off - nuttcp transferred (uploaded to the the server) more than 180 GB of data over 60 seconds:
nuttcp -i10 -T1m 10.255.255.20
30355.3750 MB /  10.00 sec = 25463.8425 Mbps     0 retrans   4666 KB-cwnd
30616.7500 MB /  10.00 sec = 25683.2659 Mbps     0 retrans   4666 KB-cwnd
30652.0000 MB /  10.00 sec = 25712.7638 Mbps     0 retrans   4666 KB-cwnd
30618.6250 MB /  10.00 sec = 25684.6795 Mbps     0 retrans   4666 KB-cwnd
30618.6250 MB /  10.00 sec = 25684.8439 Mbps     0 retrans   4666 KB-cwnd
30622.1250 MB /  10.00 sec = 25687.7003 Mbps     0 retrans   4666 KB-cwnd
183484.5000 MB /  60.00 sec = 25652.5302 Mbps
79 %TX 88 %RX 0 retrans 4666 KB-cwnd 0.50 msRTT
Similarly, for 1500 byte MTU with PMI off - 53 GB transferred over 60 seconds:
nuttcp -i10 -T1m 10.255.255.20
8855.6250 MB /  10.00 sec = 7428.6248 Mbps    21 retrans   2534 KB-cwnd
8968.2500 MB /  10.00 sec = 7523.1216 Mbps    47 retrans   2321 KB-cwnd
8918.1250 MB /  10.00 sec = 7481.0191 Mbps    29 retrans   2060 KB-cwnd
8902.8750 MB /  10.00 sec = 7468.2833 Mbps    15 retrans   2601 KB-cwnd
8885.1875 MB /  10.00 sec = 7453.4638 Mbps    22 retrans   2418 KB-cwnd
8899.3750 MB /  10.00 sec = 7465.3376 Mbps    26 retrans   2179 KB-cwnd
53431.3108 MB /  60.00 sec = 7469.8266 Mbps
14 %TX 25 %RX 160 retrans 2179 KB-cwnd 0.36 msRTT
Detailed data points, where the bottleneck for the 9000 byte MTU test with PMI off is the CPU on the Debian-right machine hosting the
nuttcp
tool server:
PMI
Linux MTU
kPPS (C2S/S2C)
L2 Gbps
Nuttcp CPU
(Left/Right)
CPU core SRX4600-5
CPU core SRX4600-6
ON
1500
600 (584 / 16)
7
15 / 30
94
99
ON
9000
379 (357 / 22)
25.6
75 / 95
76
85
OFF
1500
669 (651 / 18)
7.88
17 / 30
87
100
OFF
9000
385 (360 / 25)
25.8
75 / 98
72
83
Appendix 1 - complete configurations
SRX4600-5
set security zones security-zone vrf-1-int interfaces et-1/0/1.1110 host-inbound-traffic system-services ping
set security zones security-zone vrf-2-int interfaces et-1/0/1.1111 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces et-1/0/0.1112 host-inbound-traffic protocols ldp
set security zones security-zone vrf-1-ext vrf vrf-1
set security zones security-zone vrf-2-ext vrf vrf-2
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match source-address any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match destination-address any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match application any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext then permit
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match source-address any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match destination-address any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match application any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext then permit
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match source-address any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match destination-address any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match application any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int then permit
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match source-address any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match destination-address any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match application any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int then permit
set security policies from-zone mpls to-zone mpls policy signalling match source-address any
set security policies from-zone mpls to-zone mpls policy signalling match destination-address any
set security policies from-zone mpls to-zone mpls policy signalling match application junos-bgp
set security policies from-zone mpls to-zone mpls policy signalling match application junos-icmp-ping
set security policies from-zone mpls to-zone mpls policy signalling match application junos-ldp-tcp
set security policies from-zone mpls to-zone mpls policy signalling then permit
set security policies global policy final match source-address any
set security policies global policy final match destination-address any
set security policies global policy final match application any
set security policies global policy final then deny
set security alg dns disable
set security alg ftp disable
set security alg msrpc disable
set security alg sunrpc disable
set security alg talk disable
set security alg tftp disable
set security alg pptp disable
set security forwarding-options family mpls mode packet-based
set security flow drop-flow max-sessions 0
set security flow power-mode-disable
set interfaces et-1/0/0 vlan-tagging
set interfaces et-1/0/0 mtu 9192
set interfaces et-1/0/0 unit 1112 vlan-id 1112
set interfaces et-1/0/0 unit 1112 family inet address 192.168.0.1/24
set interfaces et-1/0/0 unit 1112 family mpls
set interfaces et-1/0/1 vlan-tagging
set interfaces et-1/0/1 mtu 9192
set interfaces et-1/0/1 unit 1110 vlan-id 1110
set interfaces et-1/0/1 unit 1110 family inet address 10.255.254.1/24
set interfaces et-1/0/1 unit 1111 vlan-id 1111
set interfaces et-1/0/1 unit 1111 family inet address 10.255.254.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.1/32
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 routing-options static route 10.0.0.0/16 next-hop 10.255.254.10
set routing-instances vrf-1 interface et-1/0/1.1110
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 routing-options static route 10.0.0.0/16 next-hop 10.255.254.10
set routing-instances vrf-2 interface et-1/0/1.1111
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set routing-instances vrf-2 vrf-table-label
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface et-1/0/0.1112 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.1
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface et-1/0/0.1112
set protocols mpls interface et-1/0/0.1112
set routing-options autonomous-system 65500
SRX4600-6
set security zones security-zone vrf-1-int interfaces et-1/0/1.1114 host-inbound-traffic system-services ping
set security zones security-zone vrf-2-int interfaces et-1/0/1.1115 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces et-1/0/0.1113 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces et-1/0/0.1113 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces et-1/0/0.1113 host-inbound-traffic protocols ldp
set security zones security-zone vrf-1-ext vrf vrf-1
set security zones security-zone vrf-2-ext vrf vrf-2
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match source-address any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match destination-address any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext match application any
set security policies from-zone vrf-1-int to-zone vrf-1-ext policy vrf-1-int-ext then permit
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match source-address any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match destination-address any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext match application any
set security policies from-zone vrf-2-int to-zone vrf-2-ext policy vrf-2-int-ext then permit
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match source-address any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match destination-address any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int match application any
set security policies from-zone vrf-1-ext to-zone vrf-1-int policy vrf-1-ext-int then permit
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match source-address any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match destination-address any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int match application any
set security policies from-zone vrf-2-ext to-zone vrf-2-int policy vrf-2-ext-int then permit
set security policies from-zone mpls to-zone mpls policy signalling match source-address any
set security policies from-zone mpls to-zone mpls policy signalling match destination-address any
set security policies from-zone mpls to-zone mpls policy signalling match application junos-bgp
set security policies from-zone mpls to-zone mpls policy signalling match application junos-icmp-ping
set security policies from-zone mpls to-zone mpls policy signalling match application junos-ldp-tcp
set security policies from-zone mpls to-zone mpls policy signalling then permit
set security policies global policy final match source-address any
set security policies global policy final match destination-address any
set security policies global policy final match application any
set security policies global policy final then deny
set security alg dns disable
set security alg ftp disable
set security alg msrpc disable
set security alg sunrpc disable
set security alg talk disable
set security alg tftp disable
set security alg pptp disable
set security forwarding-options family mpls mode packet-based
set security flow drop-flow max-sessions 0
set security flow power-mode-disable
set interfaces et-1/0/0 vlan-tagging
set interfaces et-1/0/0 mtu 9192
set interfaces et-1/0/0 unit 1113 vlan-id 1113
set interfaces et-1/0/0 unit 1113 family inet address 192.168.1.2/24
set interfaces et-1/0/0 unit 1113 family mpls
set interfaces et-1/0/1 vlan-tagging
set interfaces et-1/0/1 mtu 9192
set interfaces et-1/0/1 unit 1114 vlan-id 1114
set interfaces et-1/0/1 unit 1114 family inet address 10.255.255.1/24
set interfaces et-1/0/1 unit 1115 vlan-id 1115
set interfaces et-1/0/1 unit 1115 family inet address 10.255.255.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.3/32
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 routing-options static route 10.1.0.0/16 next-hop 10.255.255.10
set routing-instances vrf-1 interface et-1/0/1.1114
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 routing-options static route 10.1.0.0/16 next-hop 10.255.255.10
set routing-instances vrf-2 interface et-1/0/1.1115
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set routing-instances vrf-2 vrf-table-label
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface et-1/0/0.1113 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.3
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface et-1/0/0.1113
set protocols mpls interface et-1/0/0.1113
set routing-options autonomous-system 65500
MX204-21
set interfaces et-0/0/0 vlan-tagging
set interfaces et-0/0/0 mtu 9192
set interfaces et-0/0/0 unit 1112 vlan-id 1112
set interfaces et-0/0/0 unit 1112 family inet address 192.168.0.2/24
set interfaces et-0/0/0 unit 1112 family mpls
set interfaces et-0/0/0 unit 1113 vlan-id 1113
set interfaces et-0/0/0 unit 1113 family inet address 192.168.1.1/24
set interfaces et-0/0/0 unit 1113 family mpls
set interfaces lo0 unit 0 family inet address 1.1.1.2/32
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set routing-options autonomous-system 65500
set protocols bgp group rr type internal
set protocols bgp group rr local-address 1.1.1.2
set protocols bgp group rr family inet-vpn unicast
set protocols bgp group rr cluster 1.1.1.2
set protocols bgp group rr neighbor 1.1.1.1
set protocols bgp group rr neighbor 1.1.1.3
set protocols ldp interface et-0/0/0.1112
set protocols ldp interface et-0/0/0.1113
set protocols mpls interface et-0/0/0.1112
set protocols mpls interface et-0/0/0.1113
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface et-0/0/0.1112 interface-type p2p
set protocols ospf area 0.0.0.0 interface et-0/0/0.1113 interface-type p2p
Conclusion
The SRX4600 and SRX4700 in Junos 25.4R1 supports MPLS L3 VPN with VRF-to-zone mapping simplifying security policies and delivers strong forwarding performance: overall throughput approaches the SRX4600 hardware PFE-SPU interlink limit (~96 Gbps for large frames) while single session rates reach the SPU/core UDP packet rate forwarding limits (~680-820 kPPS depending on PowerMode status). PM affects results- for environments that are solely MPLS focused, users should consider globally disabling PM for best performance.
Acknowledgements
Thanks to Nicolas Fevrier for tirelessly overseeing the Tech Posts site and handling all publishing tasks. Thanks also to colleagues who provided valuable feedback, including Mark Barrett, Steven Jacques, Henri Kalliosaari, Pawel Rabiej and James Rathbun. There would be no physical kit testing without the Amsterdam Proof of Concept lab, and in particular Matthijs Nagel. Finally, special thanks to the vSRX/SRX development and product teams for delivering a versatile, high performance security and networking platform.
Useful links
https://www.juniper.net/us/en/products/security/srx-series/compare.html?p=SRX4600,SRX4700
https://www.juniper.net/documentation/us/en/software/junos/release-notes/25.4/junos-release-notes-25.4r1/topics/new-features/feature-descriptions/mpls-4.html
https://community.juniper.net/blogs/karel-hendrych/2025/08/01/srx-mpls-in-flow
https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec
https://community.juniper.net/blogs/karel-hendrych/2026/03/04/srx-secure-fabric-entry-point
https://www.debian.org/
Glossary
ACK: Acknowledge (TCP)
BGP: Border Gateway Protocol
CPU: Central Processing Unit
EVPN: Ethernet VPN
FPGA: Field Programmable Gate Array
HTTP: Hyper Text Transfer Protocol
IMIX: Internet MIX
IoT: Internet of Things
IP: Internet Protocol
LDP: Label Discovery Protocol
MPLS: Multiprotocol Label Switching
MPPS: Millions Packets Per Second
MTU: Maximum Transmission Unit
NIC: Network Interface Card
OSPF: Open Shortest Path First
P: Provider Router (MPLS)
PE: Provider Edge Router (MPLS)
PCI: Peripheral Component Interconnect
PFE: Packet Forwarding Engine
PM: PowerMode
PMI: PowerMode IPSEC
PPS: Packets Per Second
RAM: Random Access Memory
RFP: Regular Flow Path
SPU: Security Processing Unit
TCP: Transmission Control Protocol
UDP: User Datagram Protocol
VLAN: Virtual Local Area Network
VoIP: Voice over IP
VPN: Virtual Private Network
VRF: Virtual Routing and Forwarding
VXLAN: Virtual Extensible Local Area Network
WAN: Wide Area Network
Comments
If you want to reach out for comments, feedback or questions, drop us a mail at:
Revision History
Version
Author(s)
Date
Comments
1
Karel Hendrych
April 2026
Initial Publication
