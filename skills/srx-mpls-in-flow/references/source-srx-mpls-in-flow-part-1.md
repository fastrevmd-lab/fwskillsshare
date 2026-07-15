# SRX MPLS in Flow

Source: https://community.juniper.net/blogs/karel-hendrych/2025/08/01/srx-mpls-in-flow
Author: Karel Hendrych
Retrieved: 2026-05-14

## Extracted Article Text

Junos 24.2R1 brings improvement for selected Juniper SRX series devices, particularly on MPLS and packet-mode/flow-mode processing. This post includes a simple example of an MPLS-enabled SRX device processing 'family inet' in flow mode without relying on selective packet services, as was common previously. Yes, MPLS in SRX flow mode!
Introduction
Historically, selected SRX models supported MPLS capabilities through either pure packet-mode or selective packet-mode processing. In selective packet-mode, stateless firewall filters select traffic for packet-mode processing, effectively bypassing the default stateful firewall behaviour of the SRX Flow module. Junos 24.2R1 introduced new handling of traffic types, decoupling 'family mpls' from the IPv4 protocol 'family inet' and the IPv6 protocol 'family inet6'.
This change enables stateful handling of IPv4 and IPv6 traffic while supporting advanced MPLS capabilities, such as MPLS VRF-enabled secure CPE devices for L3 VPNs with L4/L7 features, including stateful firewall, NAT, IPS, AppID, and more. Additional use cases, such as secure PE mixed with IPSEC and stateful high availability capabilities, may also be addressed.
Consolidating MPLS and security features into a single device offers advantages in terms of reducing operational costs and minimizing the solution's footprint. There are likely not many devices available on the market that can deliver such a mixture of advanced security and networking functionalities, ranging from small form factors like the SRX300 to high-performance models such as the SRX4300 or the flexible virtual SRX. An essential measure-the stateful firewall-combined with MPLS addresses fundamental concerns about unauthorized connections and limits the attack surface when the uplink is not necessarily completely trusted. The Layer 7 security features further enhance security. Additionally, the single device perfectly addresses scenarios involving both MPLS uplink and local Internet breakout.
More precisely, explicit flow mode for 'family mpls' was supported since Junos 21.4 for specific PE use-cases on vSRX3. However, starting with Junos 24.2, this feature is deprecated and replaced by decoupled controls for 'family mpls' and 'family inet'.
The new mode applies to the :
SRX3xx,
SRX1500,
SRX4100/4200,
SRX1600/2300(4210)/4300,
SRX4600, SRX4700 (as of Junos 25.4)
and vSRX.
As of July 2025, global packet mode is not supported on the new mid-range SRX series:
SRX1600/
2300(4120)/4300
SRX4600/4700,
SRX5K series.
Global packet mode remains supported on
SRX3xx,
SRX1500,
vSRX,
and SRX4100/4200 platforms.
To preserve global packet mode on these platforms after upgrading to Junos 24.2R1 or later, 'family inet' must be explicitly configured for packet mode.
The Demo Topology
The minimal SRX setup consists of three vSRX 24.2R2 instances: vSRX-left, vSRX-router, and vSRX-right, where the goal is to transport overlapping IP spaces between vrf-1 and vrf-2 hosts with VRF-aware L4-L7 services.
All vSRX instances use OSPF to propagate loopback IPs, with BGP enabled for 'family inet-vpn' and LDP-signaled MPLS between them (could also be BGP-LU).
The vSRX-left, configured in flow mode, uses the simplest possible setup.
The vSRX-router operates in pure packet mode for all supported protocol families.
The most complex instance, vSRX-right, also in flow mode, includes basic firewall policies, application recognition, and applies source NAT in vrf-1 and static NAT in vrf-2 to the same IP address.
Platform hardening is outside the scope of this article, although basic zone host-inbound measures are in place on vSRX-right.
Figure 1 - Demo topology
Sidenote - the left and right hosts are implemented as Linux network namespaces as described in the
SRX EVPN/VXLAN T5 oIPSEC Tech Post
, Appendix 2: Linux Network Namespace Sample Configurations.
Configuration Break-down
The following sections detail the configurations of individual vSRX devices. The complete configuration for all devices, suitable for copying and pasting, is provided in Appendix 1.
vSRX-left
As previously described, vSRX-left is configured as simply as possible, serving as a self-explanatory cornerstone for the evolving configuration. The following sections detail a portion of its configuration file.
set security forwarding-options family mpls mode packet-based
The key setting above configures the vSRX instance to operate in flow mode, with inet/inet6 families enabled for flow-based processing, MPLS processed in packet mode, and family ISO (representing IS-IS) discarded, as reflected in the flow status output:
> show security flow status
Flow forwarding mode:
Inet forwarding mode: flow based
Inet6 forwarding mode: flow based
MPLS forwarding mode: packet based
ISO forwarding mode: drop
The MPLS-enabled interface ge-0/0/0 is configured with a higher MTU, allowing the addition of MPLS labels to traffic sourced from hosts with regular MTU settings. The IP interface toward the left-host is VLAN-tagged, with overlapping IP addresses. Finally, the loopback interface configuration is self-explanatory:
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.1.1/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 vlan-tagging
set interfaces ge-0/0/1 unit 10 vlan-id 10
set interfaces ge-0/0/1 unit 10 family inet address 10.0.0.1/24
set interfaces ge-0/0/1 unit 11 vlan-id 11
set interfaces ge-0/0/1 unit 11 family inet address 10.0.0.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.1/32
The VRF configuration binds the interface to the VRF, sets a route distinguisher to ensure prefix uniqueness, and configures the vrf-target and vrf-table-label. The vrf-table-label, a mandatory setting on SRX platforms, enables together with vrf-target traffic to and from the local interface to be processed within the VRF:
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 interface ge-0/0/1.10
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 interface ge-0/0/1.11
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set routing-instances vrf-2 vrf-table-label
OSPF is configured to propagate the loopback IP address. BGP is set up for peering with the vSRX-router loopback address. LDP-signaled MPLS is enabled on interface ge-0/0/0.0:
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.1
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface ge-0/0/0.0
set protocols mpls interface ge-0/0/0.0
set routing-options autonomous-system 65500
Sidenote - RSVP-signalled LSP is also supported, but it is outside the scope of this document.
The next setting pertains to power-mode (vector processing), which is intended to increase performance for most use cases through parallel processing and the leveraging of CPU instruction caches. Since traffic subjected to MPLS handling is processed in the SRX Regular Flow Path (RFP) mode rather than in power mode, disabling power mode globally avoids the performance overhead of qualification checks to determine if the traffic is eligible for power-mode processing:
set security flow power-mode-disable
Sidenote - power-mode applicable to x86-based SRX platforms is enabled by default since Junos 21.3
The security zone configuration maps interface(s) to zones and defines minimal host-inbound services and protocols. VRF traffic is evaluated in the MPLS zone, which hosts the underlay interface (ge-0/0/0.0). An additional policy evaluation dimension is provided by from/to VRF policy matching (as detailed in the vSRX-right configuration breakdown covered later):
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ldp
set security zones security-zone vrf-1 interfaces ge-0/0/1.10 host-inbound-traffic system-services ping
set security zones security-zone vrf-2 interfaces ge-0/0/1.11 host-inbound-traffic system-services ping
Sidenote - in the case of a virtual setup, the increased MTU also needs to be configured as part of the virtual machine and networking bridge configurations. A sample Linux/KVM libvirt VM and Linux bridge configuration is provided in Appendix 2 and Appendix 3 respectively.
Security policies are configured to permit incoming and outgoing traffic. Unlike the default permit policy, the global policy includes counters for tracking policy hits:
set security policies global policy all match source-address any
set security policies global policy all match destination-address any
set security policies global policy all match application any
set security policies global policy all then permit
Sidenote - cross-VRF traffic between vrf-1 and vrf-2 would still require route leaking to be configured.
vSRX-router
The minimal vSRX-router configuration serves as an MPLS router for inet-vpn VRF transit between vSRX-left and vSRX-right.
The configuration below sets the vSRX-router instance to operate as a pure router for all supported protocol families, disabling stateful processing entirely:
set security forwarding-options family inet mode packet-based
set security forwarding-options family inet6 mode packet-based
set security forwarding-options family mpls mode packet-based
set security forwarding-options family iso mode packet-based
Both the vSRX-left and vSRX-right facing interfaces have inet and MPLS families configured, along with an increased MTU and an IP-addressed loopback:
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.1.2/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 mtu 1600
set interfaces ge-0/0/1 unit 0 family inet address 10.0.2.1/24
set interfaces ge-0/0/1 unit 0 family mpls
set interfaces lo0 unit 0 family inet address 1.1.1.2/32
Route distinguishers and vrf-target ensure uniqueness and proper placement into the VRF based on the corresponding community:
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
Sidenote - VRF configuration is not needed for classical P-router functionality. In this case, it serves the purpose of providing visibility by having routes present in individual VRFs. Normally, the bgp.l3vpn.0 routing table would be referenced.
OSPF propagates loopback addresses, BGP operates in route reflector mode, and LDP-signaled MPLS is configured on the vSRX-left and vSRX-right facing interfaces:
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols ospf area 0.0.0.0 interface ge-0/0/1.0 interface-type p2p
set protocols bgp group rr type internal
set protocols bgp group rr local-address 1.1.1.2
set protocols bgp group rr family inet-vpn unicast
set protocols bgp group rr cluster 1.1.1.2
set protocols bgp group rr neighbor 1.1.1.1
set protocols bgp group rr neighbor 1.1.1.3
set protocols ldp interface ge-0/0/0.0
set protocols ldp interface ge-0/0/1.0
set protocols mpls interface ge-0/0/0.0
set protocols mpls interface ge-0/0/1.0
set routing-options autonomous-system 65500
vSRX-right
The demo configuration of vSRX-right is designed to be slightly more complex than that of vSRX-left to facilitate further evolution toward real-world applicability.
For platform tunables, vSRX-right is configured for stateful handling of MPLS traffic with power mode disabled. Unlike vSRX-left, strict TCP handshake checks are enabled to showcase stricter TCP handling (disallowing data segments until the handshake is complete), along with MPLS:
set security forwarding-options family mpls mode packet-based
set security flow tcp-session strict-syn-check
set security flow power-mode-disable
The MPLS-enabled interface ge-0/0/0 uses a higher MTU and the 'family mpls' setting. Classical IP interfaces are VLAN-tagged, with overlapping IP addresses, and the loopback interface is self-explanatory.
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.2.2/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 vlan-tagging
set interfaces ge-0/0/1 unit 10 vlan-id 10
set interfaces ge-0/0/1 unit 10 family inet address 10.0.3.1/24
set interfaces ge-0/0/1 unit 11 vlan-id 11
set interfaces ge-0/0/1 unit 11 family inet address 10.0.3.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.3/32
Similarly, as on vSRX-left, VRF settings bind interface, set route distinguisher ensuring uniqueness of prefixes, and along with vrf-table-label serve to place traffic from/to local interface into VRF with VRF-specific community in import policies. Finally, discard routes are configured for the purpose of exporting routes for overlapping source / static NAT pools:
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 routing-options static route 10.10.3.0/24 discard
set routing-instances vrf-1 interface ge-0/0/1.10
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-import import-to-vrf-1
set routing-instances vrf-1 vrf-export export-to-vrf-1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 routing-options static route 10.10.3.0/24 discard
set routing-instances vrf-2 interface ge-0/0/1.11
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-import import-to-vrf-2
set routing-instances vrf-2 vrf-export export-to-vrf-2
set routing-instances vrf-2 vrf-table-label
The corresponding export and import policies add communities to routes on the specified interfaces associated with VRF-1 or VRF-2, including matches for the NAT pool routes defined in the VRF configuration:
set policy-options policy-statement export-to-vrf-1 term 1 from interface ge-0/0/1.10
set policy-options policy-statement export-to-vrf-1 term 1 then community add vrf-1
set policy-options policy-statement export-to-vrf-1 term 1 then accept
set policy-options policy-statement export-to-vrf-1 term 2 from route-filter 10.10.3.0/24 exact
set policy-options policy-statement export-to-vrf-1 term 2 then community add vrf-1
set policy-options policy-statement export-to-vrf-1 term 2 then accept
set policy-options policy-statement export-to-vrf-1 term 100 then reject
set policy-options policy-statement export-to-vrf-2 term 1 from interface ge-0/0/1.11
set policy-options policy-statement export-to-vrf-2 term 1 then community add vrf-2
set policy-options policy-statement export-to-vrf-2 term 1 then accept
set policy-options policy-statement export-to-vrf-2 term 2 from route-filter 10.10.3.0/24 exact
set policy-options policy-statement export-to-vrf-2 term 2 then community add vrf-2
set policy-options policy-statement export-to-vrf-2 term 2 then accept
set policy-options policy-statement export-to-vrf-2 term 100 then reject
set policy-options policy-statement import-to-vrf-1 term 1 from community vrf-1
set policy-options policy-statement import-to-vrf-1 term 1 then accept
set policy-options policy-statement import-to-vrf-1 term 100 then reject
set policy-options policy-statement import-to-vrf-2 term 1 from community vrf-2
set policy-options policy-statement import-to-vrf-2 term 1 then accept
set policy-options policy-statement import-to-vrf-2 term 100 then reject
set policy-options community vrf-1 members target:65500:1
set policy-options community vrf-2 members target:65500:2
OSPF is configured to propagate the loopback IP address, BGP is peering with the vSRX router's loopback, and LDP-signaled MPLS is enabled on interface ge-0/0/0.0:
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.3
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface ge-0/0/0.0
set protocols mpls interface ge-0/0/0.0
set routing-options autonomous-system 65500
The VRFs are assigned to a group used in match criteria for VRF-aware firewall and NAT rules:
set security l3vpn vrf-group vrf-1 vrf vrf-1
set security l3vpn vrf-group vrf-2 vrf vrf-2
Zone-to-interface mapping is configured with minimal host-inbound services and protocols. VRF traffic is evaluated in the MPLS zone hosting the underlay interface, as described in the following sections. Zone-level TCP-RST flags ensure that TCP resets are sent for ingress out-of-state TCP traffic, facilitating interactive session termination.
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ldp
set security zones security-zone vrf-1 tcp-rst
set security zones security-zone vrf-1 interfaces ge-0/0/1.10 host-inbound-traffic system-services ping
set security zones security-zone vrf-2 tcp-rst
set security zones security-zone vrf-2 interfaces ge-0/0/1.11 host-inbound-traffic system-services ping
VRF-aware policies permit all traffic to and from VRFs while recognizing Layer 7 applications by using dynamic-application match (the deployment of Layer 7 visibility related license and software is detailed in Appendix 4). However, even if route leaking occurs between VRFs, policy controls prevent such traffic:
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match source-address any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match destination-address any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match application any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match dynamic-application any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match destination-l3vpn-vrf-group vrf-1
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 then permit
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match source-address any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match destination-address any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match application any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match dynamic-application any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match source-l3vpn-vrf-group vrf-1
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 then permit
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match source-address any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match destination-address any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match application any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match dynamic-application any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match destination-l3vpn-vrf-group vrf-2
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 then permit
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match source-address any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match destination-address any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match application any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match dynamic-application any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match source-l3vpn-vrf-group vrf-2
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 then permit
Sidenote - there is a feature for the SRX in planning that will map VRFs to a zone for classical zone policies, potentially removing the need for source and destination VRF matching in policies.
Security policies within the MPLS zone intrazone context (typically, stricter source address controls would be applied) permit control plane traffic for LDP, BGP, and PING to the loopback interface:
set security policies from-zone mpls to-zone mpls policy control match source-address any
set security policies from-zone mpls to-zone mpls policy control match destination-address any
set security policies from-zone mpls to-zone mpls policy control match application junos-bgp
set security policies from-zone mpls to-zone mpls policy control match application junos-icmp-ping
set security policies from-zone mpls to-zone mpls policy control match application junos-ldp-tcp
set security policies from-zone mpls to-zone mpls policy control then permit
Finally, cleanup (reject action notifying the source) firewall rules are implemented primarily to track traffic using policy hit counters or logs when enabled:
set security policies global policy reject match source-address any
set security policies global policy reject match destination-address any
set security policies global policy reject match application any
set security policies global policy reject match dynamic-application any
set security policies global policy reject then reject
VRF-aware NAT settings translate VRF-1 right-host sourced traffic using source NAT with port translation. For demonstration purposes, the VRF-2 right-host host has a static NAT address matching the VRF-1 source NAT pool IP address:
set security nat source pool pool-1 address 10.10.3.10/32
set security nat source rule-set source-1 from zone vrf-1
set security nat source rule-set source-1 to routing-group vrf-1
set security nat source rule-set source-1 rule source-1-1 match source-address 0.0.0.0/0
set security nat source rule-set source-1 rule source-1-1 match destination-address 0.0.0.0/0
set security nat source rule-set source-1 rule source-1-1 then source-nat pool pool-1
set security nat static rule-set static-1 from routing-group vrf-2
set security nat static rule-set static-1 rule static-1-1 match destination-address 10.10.3.10/32
set security nat static rule-set static-1 rule static-1-1 then static-nat prefix 10.0.3.10/32
set security nat static rule-set static-1 rule static-1-1 then static-nat prefix routing-instance vrf-2
With application identification enabled, it is recommended to track sessions that cannot be identified and may remain in the pre-identification stage (for example during resource shortage):
set security policies pre-id-default-policy then log session-close
set security policies pre-id-default-policy then log session-update 1
As a best practice, unnecessary Application Layer Gateways (ALG) are disabled in the vSRX3-specific default configuration, leaving only the FTP and DNS ALGs enabled:
set security alg h323 disable
set security alg mgcp disable
set security alg msrpc disable
set security alg sunrpc disable
set security alg rtsp disable
set security alg sccp disable
set security alg sip disable
set security alg talk disable
set security alg tftp disable
set security alg pptp disable
Verification
This section of the Tech-Post outlines the basic steps to validate the vSRX-based demo setup.
Routing information
The first step in validation is to check the vSRX-router's inet.3 table to confirm the presence of LSPs represented by the loopback addresses of vSRX-left and vSRX-right:
vSRX-router> show route table inet.3
inet.3: 2 destinations, 2 routes (2 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
1.1.1.1/32         *[LDP/9] 03:17:17, metric 1
>  to 10.0.1.1 via ge-0/0/0.0
1.1.1.3/32         *[LDP/9] 03:17:24, metric 1
>  to 10.0.2.2 via ge-0/0/1.0
Similarly, on vSRX-left, the inet.3 table confirms the presence of LSPs represented by the loopback addresses of vSRX-router and vSRX-right:
vSRX-left> show route table inet.3
inet.3: 2 destinations, 2 routes (2 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
1.1.1.2/32         *[LDP/9] 1d 01:32:04, metric 1
>  to 10.0.1.2 via ge-0/0/0.0
1.1.1.3/32         *[LDP/9] 1d 01:32:04, metric 1
>  to 10.0.1.2 via ge-0/0/0.0, Push 299776
Additionally, the vSRX-router's LDP database confirms that LSPs for the loopback addresses of vSRX-left and vSRX-right are correctly established:
vSRX-router> show ldp database
Input label database, 1.1.1.2:0--1.1.1.1:0
Labels received: 3
Label     Prefix
3      1.1.1.1/32
299776      1.1.1.2/32
299792      1.1.1.3/32
Output label database, 1.1.1.2:0--1.1.1.1:0
Labels advertised: 3
Label     Prefix
299792      1.1.1.1/32
3      1.1.1.2/32
299776      1.1.1.3/32
Input label database, 1.1.1.2:0--1.1.1.3:0
Labels received: 3
Label     Prefix
299792      1.1.1.1/32
299776      1.1.1.2/32
3      1.1.1.3/32
Output label database, 1.1.1.2:0--1.1.1.3:0
Labels advertised: 3
Label     Prefix
299792      1.1.1.1/32
3      1.1.1.2/32
299776      1.1.1.3/32
To check the vSRX-router's routing tables for vrf-1 and vrf-2, including NAT prefixes exported by vSRX-right:
root@vSRX-router> show route protocol bgp table vrf-1.inet.0
vrf-1.inet.0: 3 destinations, 3 routes (3 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
10.0.0.0/24        *[BGP/170] 02:59:04, localpref 100, from 1.1.1.1
AS path: I, validation-state: unverified
>  to 10.0.1.1 via ge-0/0/0.0, Push 16
10.0.3.0/24        *[BGP/170] 02:59:11, localpref 100, from 1.1.1.3
AS path: I, validation-state: unverified
>  to 10.0.2.2 via ge-0/0/1.0, Push 16
10.10.3.0/24       *[BGP/170] 02:59:11, localpref 100, from 1.1.1.3
AS path: I, validation-state: unverified
>  to 10.0.2.2 via ge-0/0/1.0, Push 16
root@vSRX-router> show route protocol bgp table vrf-2.inet.0
vrf-2.inet.0: 3 destinations, 3 routes (3 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
10.0.0.0/24        *[BGP/170] 02:59:16, localpref 100, from 1.1.1.1
AS path: I, validation-state: unverified
>  to 10.0.1.1 via ge-0/0/0.0, Push 17
10.0.3.0/24        *[BGP/170] 02:59:23, localpref 100, from 1.1.1.3
AS path: I, validation-state: unverified
>  to 10.0.2.2 via ge-0/0/1.0, Push 17
10.10.3.0/24       *[BGP/170] 02:59:23, localpref 100, from 1.1.1.3
AS path: I, validation-state: unverified
>  to 10.0.2.2 via ge-0/0/1.0, Push 17
Packet captures
Packet capture of ICMP echo-request and echo-response packets between overlapping endpoints 10.0.0.10 and 10.0.3.10 with VLAN 10 for vrf-1 and VLAN 11 for vrf-2 on the link between left-host and vSRX-left:
# tcpdump -n -e -i br-lab-1 icmp
<SNIP> vlan 10, p 0, ethertype IPv4 (0x0800), 10.0.0.10 > 10.0.3.10: ICMP echo request, id 674, seq 1, length 64
<SNIP> vlan 10, p 0, ethertype IPv4 (0x0800), 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 674, seq 1, length 64
<SNIP> vlan 11, p 0, ethertype IPv4 (0x0800), 10.0.0.10 > 10.0.3.10: ICMP echo request, id 675, seq 1, length 64
<SNIP> vlan 11, p 0, ethertype IPv4 (0x0800), 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 675, seq 1, length 64
Sidenote - packet captures are performed on the Linux bridges from the Linux/KVM host.
ICMP echo-request and echo-response packets between vSRX-left and vSRX-router, now carrying MPLS labels for the corresponding VRFs:
# tcpdump -n -i br-lab-2 mpls
<SNIP> MPLS (label 299776, tc 0, ttl 63) (label 16, tc 0, [S], ttl 63) IP 10.0.0.10 > 10.0.3.10: ICMP echo request, id 674, seq 1, length 64
<SNIP> MPLS (label 16, tc 0, [S], ttl 62) IP 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 674, seq 1, length 64
<SNIP> MPLS (label 299776, tc 0, ttl 63) (label 17, tc 0, [S], ttl 63) IP 10.0.0.10 > 10.0.3.10: ICMP echo request, id 675, seq 1, length 64
<SNIP> MPLS (label 17, tc 0, [S], ttl 62) IP 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 675, seq 1, length 64
Next, ICMP echo-request and echo-response packets between vSRX-router and vSRX-right, carrying MPLS labels for vrf-1 and vrf-2:
# tcpdump -n -i br-lab-3 mpls
<SNIP> MPLS (label 16, tc 0, [S], ttl 62) IP 10.0.0.10 > 10.0.3.10: ICMP echo request, id 674, seq 1, length 64
<SNIP> MPLS (label 299792, tc 0, ttl 63) (label 16, tc 0, [S], ttl 63) IP 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 674, seq 1, length 64
<SNIP> MPLS (label 17, tc 0, [S], ttl 62) IP 10.0.0.10 > 10.0.3.10: ICMP echo request, id 675, seq 1, length 64
<SNIP> MPLS (label 299792, tc 0, ttl 63) (label 17, tc 0, [S], ttl 63) IP 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 675, seq 1, length 64
Finally, ICMP echo-request and echo-response packets between vSRX-right and right-host, tagged with VLAN 10 for vrf-1 and VLAN 11 for vrf-2:
# tcpdump -n -e -i br-lab-4 icmp
<SNIP> vlan 10, p 0, ethertype IPv4 (0x0800), 10.0.0.10 > 10.0.3.10: ICMP echo request, id 674, seq 1, length 64
<SNIP> vlan 10, p 0, ethertype IPv4 (0x0800), 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 674, seq 1, length 64
<SNIP> vlan 11, p 0, ethertype IPv4 (0x0800), 10.0.0.10 > 10.0.3.10: ICMP echo request, id 675, seq 1, length 64
<SNIP> vlan 11, p 0, ethertype IPv4 (0x0800), 10.0.3.10 > 10.0.0.10: ICMP echo reply, id 675, seq 1, length 64<
NAT and AppID validation
Two SSH sessions are initiated from right-host to left-host, identified using Junos Application Identification. The first session, routed via vrf-1, undergoes source NAT with port translation to 10.10.3.10. The second session, routed via vrf-2, undergoes static NAT to 10.10.3.10 (with the source port preserved):
vSRX-right> show security flow session dynamic-application junos:SSH
Session ID: 19587, Policy name: vrf-1/4, Timeout: 1796, Session State: Valid
In: 10.0.3.10/43274 --> 10.0.0.10/22;tcp, Conn Tag: 0x0, If: ge-0/0/1.10, Pkts: 21, Bytes: 5032,
Out: 10.0.0.10/22 --> 10.10.3.10/11077;tcp, Conn Tag: 0x0, L3VPN VRF Group: vrf-1, If: ge-0/0/0.0, Pkts: 19, Bytes: 5548,
Session ID: 19588, Policy name: vrf-2/6, Timeout: 1798, Session State: Valid
In: 10.0.3.10/43286 --> 10.0.0.10/22;tcp, Conn Tag: 0x0, If: ge-0/0/1.11, Pkts: 21, Bytes: 5032,
Out: 10.0.0.10/22 --> 10.10.3.10/43286;tcp, Conn Tag: 0x0, L3VPN VRF Group: vrf-2, If: ge-0/0/0.0, Pkts: 20, Bytes: 5600
Basic Performance Check
On a Debian Linux 12 compute node with dual Xeon E5-2680 v4 CPUs, three KVM-based vSRX VMs, with one PFE core each, process the same TCP traffic between left and right hosts. The nuttcp tool, running in a VRF specific Linux namespace, measured an average throughput of 4 Gbps for a single TCP session, as shown in the output below. Typically the Linux bridges are the primary performance bottleneck, as the vSRX PFE cores are not fully utilized. To achieve optimal vSRX performance, SR-IOV would be the first thing to look at. Practically speaking, the specific SRX platform ability to distribute MPLS traffic to CPU cores would need to be evaluated as well.
Linux namespaces where the nuttcp tool is executed:
left-host:~# alias
alias v1='ip netns exec vrf-1'
alias v2='ip netns exec vrf-2'
Server side of nuttcp on the left-host in the vrf-2 namespace:
left-host:~# v2 nuttcp -S --nofork
Client side of nuttcp on the right host in the vrf-2 namespace; the client is effectively pushing data towards the server, with a one-minute run and a 10-second reporting interval:
right-host:~# v2 nuttcp -i10 -T1m 10.0.0.10
5215.8125 MB /  10.00 sec = 4375.2991 Mbps     0 retrans
4848.8750 MB /  10.00 sec = 4067.5234 Mbps     0 retrans
4843.0000 MB /  10.00 sec = 4062.6423 Mbps     0 retrans
4972.4375 MB /  10.00 sec = 4171.1508 Mbps     0 retrans
4499.8125 MB /  10.00 sec = 3774.7450 Mbps     0 retrans
4388.1875 MB /  10.00 sec = 3681.0807 Mbps     0 retrans
28769.7500 MB /  60.00 sec = 4022.0229 Mbps 31 %TX 19 %RX 0 retrans 1.54 msRTT
vSRX-right CPU load:
vSRX-right> show security monitoring
Flow session   Flow session     CP session     CP session
FPC PIC CPU Mem        current        maximum        current        maximum
0   0  63  71              6         524288            N/A            N/A
vSRX-router CPU load:
vSRX-router> show security monitoring
Flow session   Flow session     CP session     CP session
FPC PIC CPU Mem        current        maximum        current        maximum
0   0  39  70              0         524288            N/A            N/A
vSRX-right packet rate:
vSRX-right                        Seconds: 33                  Time: 13:21:45
Interface    Link  Input packets        (pps)     Output packets        (pps)
ge-0/0/0      Up         112415          (0)       2121820275       (359742)
gr-0/0/0      Up              0          (0)                0            (0)
ip-0/0/0      Up              0          (0)                0            (0)
lsq-0/0/0     Up              0          (0)                0            (0)
lt-0/0/0      Up              0          (0)                0            (0)
mt-0/0/0      Up              0          (0)                0            (0)
sp-0/0/0      Up              0          (0)                0            (0)
ge-0/0/1      Up     2121710542     (359562)       4486101908        (10804)
vSRX-right bit rate:
vSRX-right                        Seconds: 93                  Time: 13:22:45
Interface    Link     Input bytes        (bps)      Output bytes        (bps)
ge-0/0/0      Up         7663088        (592)     3006615480272 (4434026688)
gr-0/0/0      Up               0          (0)                 0          (0)
ip-0/0/0      Up               0          (0)                 0          (0)
lsq-0/0/0     Up               0          (0)                 0          (0)
lt-0/0/0      Up               0          (0)                 0          (0)
mt-0/0/0      Up               0          (0)                 0          (0)
sp-0/0/0      Up               0          (0)                 0          (0)
ge-0/0/1      Up   2989485845757 (4408659664)     6635701115948    (4408112)
Sidenote - no input rates on ge-0/0/0 matching ge-0/0/1 output appear to be a software issue
Appendix 1 - Complete Configuration
vSRX-left
set security forwarding-options family mpls mode packet-based
set security flow power-mode-disable
set security policies global policy all match source-address any
set security policies global policy all match destination-address any
set security policies global policy all match application any
set security policies global policy all then permit
set security zones security-zone vrf-1 interfaces ge-0/0/1.10 host-inbound-traffic system-services ping
set security zones security-zone vrf-2 interfaces ge-0/0/1.11 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic system-services ping
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ldp
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.1.1/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 vlan-tagging
set interfaces ge-0/0/1 unit 10 vlan-id 10
set interfaces ge-0/0/1 unit 10 family inet address 10.0.0.1/24
set interfaces ge-0/0/1 unit 11 vlan-id 11
set interfaces ge-0/0/1 unit 11 family inet address 10.0.0.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.1/32
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 interface ge-0/0/1.10
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 interface ge-0/0/1.11
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set routing-instances vrf-2 vrf-table-label
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.1
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface ge-0/0/0.0
set protocols mpls interface ge-0/0/0.0
set routing-options autonomous-system 65500
vSRX-router
set security forwarding-options family inet mode packet-based
set security forwarding-options family inet6 mode packet-based
set security forwarding-options family mpls mode packet-based
set security forwarding-options family iso mode packet-based
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.1.2/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 mtu 1600
set interfaces ge-0/0/1 unit 0 family inet address 10.0.2.1/24
set interfaces ge-0/0/1 unit 0 family mpls
set interfaces lo0 unit 0 family inet address 1.1.1.2/32
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-target target:65500:1
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-target target:65500:2
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols ospf area 0.0.0.0 interface ge-0/0/1.0 interface-type p2p
set protocols bgp group rr type internal
set protocols bgp group rr local-address 1.1.1.2
set protocols bgp group rr family inet-vpn unicast
set protocols bgp group rr cluster 1.1.1.2
set protocols bgp group rr neighbor 1.1.1.1
set protocols bgp group rr neighbor 1.1.1.3
set protocols ldp interface ge-0/0/0.0
set protocols ldp interface ge-0/0/1.0
set protocols mpls interface ge-0/0/0.0
set protocols mpls interface ge-0/0/1.0
set routing-options autonomous-system 65500
vSRX-right
set security alg h323 disable
set security alg mgcp disable
set security alg msrpc disable
set security alg sunrpc disable
set security alg rtsp disable
set security alg sccp disable
set security alg sip disable
set security alg talk disable
set security alg tftp disable
set security alg pptp disable
set security forwarding-options family mpls mode packet-based
set security flow tcp-session strict-syn-check
set security flow power-mode-disable
set security nat source pool pool-1 address 10.10.3.10/32
set security nat source rule-set source-1 from zone vrf-1
set security nat source rule-set source-1 to routing-group vrf-1
set security nat source rule-set source-1 rule source-1-1 match source-address 0.0.0.0/0
set security nat source rule-set source-1 rule source-1-1 match destination-address 0.0.0.0/0
set security nat source rule-set source-1 rule source-1-1 then source-nat pool pool-1
set security nat static rule-set static-1 from routing-group vrf-2
set security nat static rule-set static-1 rule static-1-1 match destination-address 10.10.3.10/32
set security nat static rule-set static-1 rule static-1-1 then static-nat prefix 10.0.3.10/32
set security nat static rule-set static-1 rule static-1-1 then static-nat prefix routing-instance vrf-2
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match source-address any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match destination-address any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match application any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match dynamic-application any
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 match destination-l3vpn-vrf-group vrf-1
set security policies from-zone vrf-1 to-zone mpls policy vrf-1 then permit
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match source-address any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match destination-address any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match application any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match dynamic-application any
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 match source-l3vpn-vrf-group vrf-1
set security policies from-zone mpls to-zone vrf-1 policy vrf-1 then permit
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match source-address any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match destination-address any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match application any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match dynamic-application any
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 match destination-l3vpn-vrf-group vrf-2
set security policies from-zone vrf-2 to-zone mpls policy vrf-2 then permit
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match source-address any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match destination-address any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match application any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match dynamic-application any
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 match source-l3vpn-vrf-group vrf-2
set security policies from-zone mpls to-zone vrf-2 policy vrf-2 then permit
set security policies from-zone mpls to-zone mpls policy control match source-address any
set security policies from-zone mpls to-zone mpls policy control match destination-address any
set security policies from-zone mpls to-zone mpls policy control match application junos-bgp
set security policies from-zone mpls to-zone mpls policy control match application junos-icmp-ping
set security policies from-zone mpls to-zone mpls policy control match application junos-ldp-tcp
set security policies from-zone mpls to-zone mpls policy control then permit
set security policies global policy reject match source-address any
set security policies global policy reject match destination-address any
set security policies global policy reject match application any
set security policies global policy reject match dynamic-application any
set security policies global policy reject then reject
set security policies pre-id-default-policy then log session-close
set security policies pre-id-default-policy then log session-update 1
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols ldp
set security zones security-zone mpls interfaces lo0.0 host-inbound-traffic protocols bgp
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ospf
set security zones security-zone mpls interfaces ge-0/0/0.0 host-inbound-traffic protocols ldp
set security zones security-zone vrf-1 tcp-rst
set security zones security-zone vrf-2 tcp-rst
set security l3vpn vrf-group vrf-1 vrf vrf-1
set security l3vpn vrf-group vrf-2 vrf vrf-2
set interfaces ge-0/0/0 mtu 1600
set interfaces ge-0/0/0 unit 0 family inet address 10.0.2.2/24
set interfaces ge-0/0/0 unit 0 family mpls
set interfaces ge-0/0/1 vlan-tagging
set interfaces ge-0/0/1 unit 10 vlan-id 10
set interfaces ge-0/0/1 unit 10 family inet address 10.0.3.1/24
set interfaces ge-0/0/1 unit 11 vlan-id 11
set interfaces ge-0/0/1 unit 11 family inet address 10.0.3.1/24
set interfaces lo0 unit 0 family inet address 1.1.1.3/32
set policy-options policy-statement export-to-vrf-1 term 1 from interface ge-0/0/1.10
set policy-options policy-statement export-to-vrf-1 term 1 then community add vrf-1
set policy-options policy-statement export-to-vrf-1 term 1 then accept
set policy-options policy-statement export-to-vrf-1 term 2 from route-filter 10.10.3.0/24 exact
set policy-options policy-statement export-to-vrf-1 term 2 then community add vrf-1
set policy-options policy-statement export-to-vrf-1 term 2 then accept
set policy-options policy-statement export-to-vrf-1 term 100 then reject
set policy-options policy-statement export-to-vrf-2 term 1 from interface ge-0/0/1.11
set policy-options policy-statement export-to-vrf-2 term 1 then community add vrf-2
set policy-options policy-statement export-to-vrf-2 term 1 then accept
set policy-options policy-statement export-to-vrf-2 term 2 from route-filter 10.10.3.0/24 exact
set policy-options policy-statement export-to-vrf-2 term 2 then community add vrf-2
set policy-options policy-statement export-to-vrf-2 term 2 then accept
set policy-options policy-statement export-to-vrf-2 term 100 then reject
set policy-options policy-statement import-to-vrf-1 term 1 from community vrf-1
set policy-options policy-statement import-to-vrf-1 term 1 then accept
set policy-options policy-statement import-to-vrf-1 term 100 then reject
set policy-options policy-statement import-to-vrf-2 term 1 from community vrf-2
set policy-options policy-statement import-to-vrf-2 term 1 then accept
set policy-options policy-statement import-to-vrf-2 term 100 then reject
set policy-options community vrf-1 members target:65500:1
set policy-options community vrf-2 members target:65500:2
set routing-instances vrf-1 instance-type vrf
set routing-instances vrf-1 routing-options static route 10.10.3.0/24 discard
set routing-instances vrf-1 interface ge-0/0/1.10
set routing-instances vrf-1 route-distinguisher 65500:1
set routing-instances vrf-1 vrf-import import-to-vrf-1
set routing-instances vrf-1 vrf-export export-to-vrf-1
set routing-instances vrf-1 vrf-table-label
set routing-instances vrf-2 instance-type vrf
set routing-instances vrf-2 routing-options static route 10.10.3.0/24 discard
set routing-instances vrf-2 interface ge-0/0/1.11
set routing-instances vrf-2 route-distinguisher 65500:2
set routing-instances vrf-2 vrf-import import-to-vrf-2
set routing-instances vrf-2 vrf-export export-to-vrf-2
set routing-instances vrf-2 vrf-table-label
set protocols ospf area 0.0.0.0 interface lo0.0 passive
set protocols ospf area 0.0.0.0 interface ge-0/0/0.0 interface-type p2p
set protocols bgp group mp-bgp type internal
set protocols bgp group mp-bgp local-address 1.1.1.3
set protocols bgp group mp-bgp family inet-vpn unicast
set protocols bgp group mp-bgp neighbor 1.1.1.2
set protocols ldp interface ge-0/0/0.0
set protocols mpls interface ge-0/0/0.0
set routing-options autonomous-system 65500
Appendix 2 - Sample vSRX VM libvirt XML
<domain type='kvm' id='140'>
<name>m51</name>
<uuid>57084539-2ed0-4a77-8b5d-f5a9def111d7</uuid>
<memory unit='KiB'>4194304</memory>
<currentMemory unit='KiB'>4194304</currentMemory>
<vcpu placement='static'>2</vcpu>
<resource>
<partition>/machine</partition>
</resource>
<os>
<type arch='x86_64' machine='pc-i440fx-5.2'>hvm</type>
<boot dev='hd'/>
</os>
<features>
<acpi/>
<apic/>
</features>
<cpu mode='custom' match='exact' check='full'>
<model fallback='forbid'>Broadwell-IBRS</model>
<vendor>Intel</vendor>
<feature policy='require' name='vme'/>
<feature policy='require' name='ss'/>
<feature policy='require' name='vmx'/>
<feature policy='require' name='pdcm'/>
<feature policy='require' name='f16c'/>
<feature policy='require' name='rdrand'/>
<feature policy='require' name='hypervisor'/>
<feature policy='require' name='arat'/>
<feature policy='require' name='tsc_adjust'/>
<feature policy='require' name='umip'/>
<feature policy='require' name='md-clear'/>
<feature policy='require' name='stibp'/>
<feature policy='require' name='arch-capabilities'/>
<feature policy='require' name='ssbd'/>
<feature policy='require' name='xsaveopt'/>
<feature policy='require' name='pdpe1gb'/>
<feature policy='require' name='abm'/>
<feature policy='require' name='ibpb'/>
<feature policy='require' name='ibrs'/>
<feature policy='require' name='amd-stibp'/>
<feature policy='require' name='amd-ssbd'/>
<feature policy='require' name='pschange-mc-no'/>
</cpu>
<clock offset='utc'>
<timer name='rtc' tickpolicy='catchup'/>
<timer name='pit' tickpolicy='delay'/>
<timer name='hpet' present='no'/>
</clock>
<on_poweroff>destroy</on_poweroff>
<on_reboot>restart</on_reboot>
<on_crash>restart</on_crash>
<pm>
<suspend-to-mem enabled='no'/>
<suspend-to-disk enabled='no'/>
</pm>
<devices>
<emulator>/usr/bin/qemu-system-x86_64</emulator>
<disk type='file' device='disk'>
<driver name='qemu' type='qcow2'/>
<source file='/mnt/storage-hdd/kvm/m51.qcow2' index='2'/>
<backingStore/>
<target dev='vda' bus='virtio'/>
<alias name='virtio-disk0'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
</disk>
<disk type='file' device='cdrom'>
<driver name='qemu' type='raw'/>
<source file='/mnt/storage-hdd/kvm/m51.iso' index='1'/>
<backingStore/>
<target dev='hda' bus='ide'/>
<readonly/>
<alias name='ide0-0-0'/>
<address type='drive' controller='0' bus='0' target='0' unit='0'/>
</disk>
<controller type='pci' index='0' model='pci-root'>
<alias name='pci.0'/>
</controller>
<controller type='usb' index='0' model='piix3-uhci'>
<alias name='usb'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
</controller>
<controller type='ide' index='0'>
<alias name='ide'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
</controller>
<interface type='bridge'>
<mac address='52:54:00:7d:25:40'/>
<source bridge='br-int-mgmt'/>
<target dev='vnet353'/>
<model type='virtio'/>
<alias name='net0'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
</interface>
<interface type='bridge'>
<mac address='52:54:00:76:4d:a8'/>
<source bridge='br-lab-2'/>
<target dev='vnet354'/>
<model type='virtio'/>
<mtu size='9000'/>
<alias name='net1'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
</interface>
<interface type='bridge'>
<mac address='52:54:00:d3:e9:c8'/>
<source bridge='br-lab-1'/>
<target dev='vnet355'/>
<model type='virtio'/>
<mtu size='9000'/>
<alias name='net2'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
</interface>
<serial type='pty'>
<source path='/dev/pts/0'/>
<target type='isa-serial' port='0'>
<model name='isa-serial'/>
</target>
<alias name='serial0'/>
</serial>
<console type='pty' tty='/dev/pts/0'>
<source path='/dev/pts/0'/>
<target type='serial' port='0'/>
<alias name='serial0'/>
</console>
<input type='mouse' bus='ps2'>
<alias name='input0'/>
</input>
<input type='keyboard' bus='ps2'>
<alias name='input1'/>
</input>
<graphics type='vnc' port='5900' autoport='yes' listen='127.0.0.1'>
<listen type='address' address='127.0.0.1'/>
</graphics>
<audio id='1' type='none'/>
<video>
<model type='cirrus' vram='16384' heads='1' primary='yes'/>
<alias name='video0'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
</video>
<memballoon model='virtio'>
<stats period='5'/>
<alias name='balloon0'/>
<address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
</memballoon>
</devices>
<seclabel type='dynamic' model='apparmor' relabel='yes'>
<label>libvirt-57084539-2ed0-4a77-8b5d-f5a9def111d7</label>
<imagelabel>libvirt-57084539-2ed0-4a77-8b5d-f5a9def111d7</imagelabel>
</seclabel>
<seclabel type='dynamic' model='dac' relabel='yes'>
<label>+64055:+64055</label>
<imagelabel>+64055:+64055</imagelabel>
</seclabel>
</domain>
Appendix 3 - Linux bridge configuration
Sample Linux bridge configuration for Debian Linux in /etc/network/interfaces, with increased MTU to support jumbo frames for VirtIO VM interfaces and MPLS-enabled Junos interfaces:
# Automatic start of the bridge interface
auto br-lab-3
# Configure the interface to use manual IP addressing (none in this case)
iface br-lab-3 inet manual
# Specify that no physical interfaces are connected to this bridge
bridge_ports none
# Disable Spanning Tree Protocol (STP) for this bridge
bridge_stp off
# Set the wait time for port activation to 0 seconds
bridge_waitport 0
# Set the forwarding delay to 0 seconds
bridge_fd 0
# Set the MTU (Maximum Transmission Unit) for the bridge to 9000 bytes after the interface is up
post-up ip link set br-lab-3 mtu 9000
Appendix 4 - SRX Application Identification
To enable NGFW features on the SRX, AppID license (Application Identification) must be present. For example:
> show system license
License usage:
Licensed     Licensed    Licensed
Feature      Feature     Feature
Feature name                       used    installed      needed    Expiry
IDP-SIG                               0            1           0    2026-02-17 00:00:00 UTC
APPID Signature                       0            1           0    2026-02-17 00:00:00 UTC
For easy trials, Juniper offers content security licenses as part of the vSRX evaluation package
here
; alternatively, sales representatives may provide trial licenses as well. To install the license(s) from the CLI:
> request system license add terminal
[Type ^D at a new line to end input,
enter blank line between each license key]
<REDACTED-LICENSE-KEY-SAMPLE>
embrgu ydgmbz bqihmu 2slawu u5lonf ygk4sf
<SNIP>
If both AppID and IPS (referred to as IDP - Intrusion Detection and Prevention - in Juniper terminology) licenses are deployed, there are two options to download and install the AppID database for application recognition in the context of this article. Either the standalone AppID database can be downloaded and installed:
> request services application-identification download
> request services application-identification download status
> request services application-identification install
> request services application-identification install status
Alternatively, AppID can be installed as part of the IPS software package:
> request security idp security-package download
> request security idp security-package download status
> request security idp security-package install
> request security idp security-package install status
Recognized applications and attacks can be viewed on the Juniper Threat Labs page.
Conclusion
This simplified SRX MPLS setup with LDP-signaled Layer 3 VPNs can serve as a foundation for advanced routing and security scenarios on the SRX platform. The setup can be implemented not only on traditional physical hardware but also in a virtual environment using vSRX on computers or low-spec PCs (1, 2) for evaluation or small-scale deployment. It is strongly recommended to validate performance, scalability, and feature support for the specific scenario on the chosen SRX platform, whether physical or virtual.
Acknowledgements
I would like to thank Nicolas Fevrier for overseeing the Tech Posts site and handling all the publishing tasks. I also want to acknowledge all the colleagues who provided valuable feedback, namely Mark Barrett, Anton Elita, Steven Jacques, and Matthijs Nagel. A special thanks goes to the vSRX/SRX development and product teams for delivering the Swiss Army knife of security and networking! Finally, things would be complicated without all the brilliant open-source software.
Useful links
https://community.juniper.net/blogs/karel-hendrych/2024/04/21/vsrx-on-mini-pc-with-linux-kvm
https://community.juniper.net/blogs/karel-hendrych/2025/05/22/industrial-srx-mk1-project-taco
https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec
https://libvirt.org/formatdomain.html
https://manpages.debian.org/buster/ifupdown/interfaces.5.en.html
https://manpages.debian.org/testing/bridge-utils/bridge-utils-interfaces.5.en.html
https://wiki.debian.org/KVM
https://www.debian.org/distrib/
https://www.juniper.net/documentation/product/us/en/vsrx/
https://www.juniper.net/documentation/us/en/software/vsrx/vsrx-kvm/topics/concept/security-vsrx-kvm-understanding.html
https://www.juniper.net/us/en/dm/download-next-gen-vsrx-firewall-trial.html
https://www.juniper.net/documentation/us/en/software/junos/application-identification/topics/topic-map/security-application-identification-predefined-signatures.html
https://threatlabs.juniper.net/home/#/
Glossary
ALG: Application Layer Gateway
AppID: Application Identification
BGP: Border Gateway Protocol
BGP-LU: Border Gateway Protocol Labeled Unicast
CLI: Command Line Interface
CPE: Customer Premise Equipment
DNS: Domain Name System
FTP: File Transfer Protocol
ICMP: Internet Control Message Protocol
IP: Internet Protocol
IDP: Intrusion Detection and Prevention
IPS: Intrusion Protection System
IS-IS: Intermediate System to Intermediate System
LDP: Label Discovery Protocol
LSP: Label Switched Path
MPLS: Multiprotocol Label Switching
MTU: Maximum Transmission Unit
NAT: Network Address Translation
OSPF: Open Shortest Path First
PE: Provider Edge
PFE: Packet Forwarding Engine
RFP: Regular Flow Path
RST: Reset (TCP)
RSVP: Resource Reservation Protocol
SR-IOV: Single Root Input Output Virtualization
SSH: Secure Shell
TCP: Transmission Control Protocol
VLAN: Virtual Local Area Network
VRF: Virtual Routing and Forwarding
Comments
If you want to reach out for comments, feedback, or questions, drop us an email at:
Revision History
Version
Author(s)
Date
Comments
1
Karel Hendrych
August 2025
Initial Publication
#SolutionsandTechnology
#SRXSeries
