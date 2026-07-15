# TechPost

Source: https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec
HTTP: 200 OK
Extractor: body
Retrieved: 2026-05-15

---

Skip main navigation (Press Enter).

[](home)

_[Join Elevate](https://userregistration.juniper.net/)_

# TechPost

×

  * [ Community Home ](/communities/community-home?communitykey=44efd17a-81a6-4306-b5f3-e5f82402d8d3)
  * [ Blogs 235 ](/communities/community-home/recent-community-blogs?communitykey=44efd17a-81a6-4306-b5f3-e5f82402d8d3)
  * [ Events 0 ](/communities/community-home/recent-community-events?communitykey=44efd17a-81a6-4306-b5f3-e5f82402d8d3)
  * [ Members 96 ](/communities/community-home/community-members?communitykey=44efd17a-81a6-4306-b5f3-e5f82402d8d3&Execute=1)

View Only

##  SRX EVPN/VXLAN T5 oIPSEC

####

[](https://community.juniper.net/people/karel-hendrych) By [Karel Hendrych](https://community.juniper.net/people/karel-hendrych) posted 05-27-2024 00:00

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl05$ucPermission$BlogItemRating$lbLike',''\) "Recommend this item.")

[](https://community.juniper.net/home/techpost "Back to main page")

A practical yet simple demonstration of the SRX EVPN/VXLAN Type 5 ip-prefix-routes feature and related firewall policy processing across multiple tenants, including an example of communication between overlapping IP prefixes. By utilizing an IPSEC underlay in an otherwise data center-centric feature set, this TechPost article effectively demonstrates the potential expansion into WAN scenarios.

# Introduction

Prior to Junos 22.4R1 [EVPN/VXLAN Type 5 support](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/concept/evpn-route-type5-understanding.html "https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/concept/evpn-route-type5-understanding.html"), SRX had a phased roll-out in Junos 20.4-21.1 of the feature set for [L4-L7 inspection of transit VXLAN tunnels](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-vxlan-support-srx-series.html "https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-vxlan-support-srx-series.html"), as briefly demonstrated in Appendix 1. However, things became more interesting with 22.4R1 due to the ability to significantly reduce the number of BGP peerings when connecting to EVPN fabric in a role of intra/inter VRF segmentation firewall, where VXLAN VNI is mapped into VRF. Type 5 is very efficient because it sends subnets in BGP advertisements rather than MAC/IP ones as with Type 2.

In a traditional design without EVPN/VXLAN, one BGP peering per interface belonging to a routing instance is required, potentially creating scalability challenges. However, everything comes at a price, and in this case, there is slightly more configuration required initially compared to a classic L3 firewall. Nevertheless, adding subsequent tenants in an EVPN/VXLAN SRX setup dramatically reduces configuration overhead of the classic approach.

Previously, without additional encapsulations like MPLSoGRE, achieving multi-tenancy using IPSEC was not straightforward, requiring various tricks with multiple IKE/CHILD security associations originating from alias addresses. With VXLAN host-to-host (effectively loopback-to-loopback overlay) communication, securing transit by folding all tenant traffic into IPSEC becomes easy. Type 5 support is entirely handled in SRX Flow mode, eliminating the need for selective packet services as seen in MPLSoGRE designs.

# The Demo Setup

Let’s consider the following setup – basically two vSRX instances, each with three EVPN/VXLAN T5 stretched tenant VRFs – blue, green, red - connected by vSRX based underlay router.

_Figure 1 - demo topology_

Demo setup features:

  * vSRX-left acts more like a spoke, permitting any traffic in/out of individual VRFs and local interfaces for individual tenants, with no route leaking between VRFs.

  * vSRX-right, in a sort of hub role, filters traffic between tenants. For example, traffic from left blue (VNI 1) to left green (VNI 2) is enforced on vSRX-right, effectively causing traffic to always U-turn on vSRX-right.

  * Tenant-1 can reach tenant-2 and tenant-3 on specific protocols, but not the other way around.

  * Tenant-3 has overlapping IP address space with tenant-1. The communication between them is facilitated on vSRX-right using static NAT.

  * Communication between loopbacks sourcing VXLAN traffic is encrypted using route-based IPSEC VPN, with one CHILD SA handling all loopback-loopback VXLAN traffic.

  * Decapsulated traffic originates in the infra zone, the zone where the underlay interfaces are bound to.

  * For convenience, two Linux endpoints simulating all the tenants are using network namespaces.

  * By disabling IPSEC, traffic shifts to clear-text underlay without any loss.

  * Non-encrypted VXLAN communication is inspected and enforced on vSRX-r1

# Brief Look at EVPN/VXLAN Type 5 Settings

In the example below, vSRX-left is configured with two BGP underlay peerings, vSRX-r1 and towards vSRX-right IPSEC tunnel, where to the local lo0.0 IP is exported. vSRX-right takes precedence when the IPSEC VPN is up. A new part of the SRX configuration involves EVPN signaling, establishing a loopback-to-loopback overlay peering with vSRX-right.
Sidenote - complete configuration files are present in Appendix 3, in the latest part of this article.


    set protocols bgp group underlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group underlay bfd-liveness-detection multiplier 3
    set protocols bgp group underlay neighbor 10.0.1.1 description r1
    set protocols bgp group underlay neighbor 10.0.1.1 export export-underlay
    set protocols bgp group underlay neighbor 10.0.1.1 peer-as 65000
    set protocols bgp group underlay neighbor 10.0.1.1 local-as 65002
    set protocols bgp group underlay neighbor 100.70.0.1 description vsrx-right-st0
    set protocols bgp group underlay neighbor 100.70.0.1 export export-underlay
    set protocols bgp group underlay neighbor 100.70.0.1 peer-as 65001
    set protocols bgp group underlay neighbor 100.70.0.1 local-as 65002

    set protocols bgp group overlay multihop
    set protocols bgp group overlay local-address 100.65.0.2
    set protocols bgp group overlay family evpn signaling
    set protocols bgp group overlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group overlay bfd-liveness-detection multiplier 5
    set protocols bgp group overlay neighbor 100.65.0.1 peer-as 65101
    set protocols bgp group overlay neighbor 100.65.0.1 local-as 65102

Next part is configuration of individual tenant VRFs, where:

  * ip-prefix-routes knobs

    * enable Type 5 support

    * define VXLAN encapsulation

    * assign unique VNI

    * refer to export policy

  * local interface gets bound to VRF

  * route distinguisher is ensuring uniqueness of routes in case of overlaps

  * vrf-target is for purpose of automatic import into matching VRFs across the topology



    set routing-instances tenant-1 instance-type vrf
    set routing-instances tenant-1 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances tenant-1 protocols evpn ip-prefix-routes encapsulation vxlan
    set routing-instances tenant-1 protocols evpn ip-prefix-routes vni 1
    set routing-instances tenant-1 protocols evpn ip-prefix-routes export export-tenant-1
    set routing-instances tenant-1 interface ge-0/0/1.71
    set routing-instances tenant-1 route-distinguisher 100.65.0.1:1
    set routing-instances tenant-1 vrf-target target:65001:1
    set policy-options policy-statement export-tenant-1 term 1 from interface ge-0/0/1.71
    set policy-options policy-statement export-tenant-1 term 1 then accept
    set policy-options policy-statement export-tenant-1 term 100 then reject

    set routing-instances tenant-2 instance-type vrf
    set routing-instances tenant-2 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances tenant-2 protocols evpn ip-prefix-routes encapsulation vxlan
    set routing-instances tenant-2 protocols evpn ip-prefix-routes vni 2
    set routing-instances tenant-2 protocols evpn ip-prefix-routes export export-tenant-2
    set routing-instances tenant-2 interface ge-0/0/1.72
    set routing-instances tenant-2 route-distinguisher 100.65.0.1:2
    set routing-instances tenant-2 vrf-target target:65001:2
    set policy-options policy-statement export-tenant-2 term 1 from interface ge-0/0/1.72
    set policy-options policy-statement export-tenant-2 term 1 then accept
    set policy-options policy-statement export-tenant-2 term 100 then reject

# Tenant-1 (blue) intra-VRF Traffic

_Figure 2 - blue tenant VRF traffic_

vSRX-left tenant-1 is receiving default gateway from vSRX-right and exports local interface prefix.


    vsrx-left> show evpn ip-prefix-database l3-context tenant-1  
    L3 context: tenant-1

    IPv4->EVPN Exported Prefixes
    Prefix                                       EVPN route status
    10.1.2.0/24                                  Created

    EVPN->IPv4 Imported Prefixes
    Prefix                                       Etag
    0.0.0.0/0                                    0       
      Route distinguisher    VNI/Label  Router MAC         Nexthop/Overlay GW/ESI   
      100.65.0.1:1           1          4c:96:14:a8:1b:b0  100.65.0.1    

Correspondingly vSRX-right is exporting default gateway and imports prefix of locally connected network to vSRX-left, for example:


    vsrx-right> show evpn ip-prefix-database l3-context tenant-1  
    L3 context: tenant-1

    IPv4->EVPN Exported Prefixes
    Prefix                                       EVPN route status
    0.0.0.0/0                                    Created

    EVPN->IPv4 Imported Prefixes
    Prefix                                       Etag
    10.1.2.0/24                                  0       
      Route distinguisher    VNI/Label  Router MAC         Nexthop/Overlay GW/ESI   
      100.65.0.1:1           1          4c:96:14:2e:cf:b0  100.65.0.2  

For completeness BGP, routing information from vSRX-1, including EVPN control plane – underlay is preferred via IPSEC tunnel interface st0.0, tenant-2 and tenant-3 have similar layout as tenant-1


    vsrx-left> show route protocol bgp 

    inet.0: 10 destinations, 11 routes (10 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    10.0.0.0/24        *[BGP/170] 1d 07:57:12, localpref 100
                          AS path: 65000 I, validation-state: unverified
                        >  to 10.0.1.1 via ge-0/0/0.101
    100.65.0.1/32      *[BGP/170] 1d 00:33:39, localpref 100
                          AS path: 65001 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0
                        [BGP/170] 1d 07:57:12, localpref 100
                          AS path: 65000 65001 I, validation-state: unverified
                        >  to 10.0.1.1 via ge-0/0/0.101

    bgp.evpn.0: 6 destinations, 6 routes (6 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    5:100.65.0.1:1::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0
    5:100.65.0.1:2::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0
    5:100.65.0.1:3::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0

    tenant-1.evpn.0: 2 destinations, 2 routes (2 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    5:100.65.0.1:1::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0

    tenant-2.evpn.0: 2 destinations, 2 routes (2 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    5:100.65.0.1:2::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0

    tenant-3.evpn.0: 2 destinations, 2 routes (2 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    5:100.65.0.1:3::0::0.0.0.0::0/248               
                       *[BGP/170] 1d 00:44:58, localpref 100, from 100.65.0.1
                          AS path: 65101 I, validation-state: unverified
                        >  to 100.70.0.1 via st0.0

Permissive security policies within tenant-1 – notice the use of Destination and Source VRF group match for traffic sourced or destined to the infra zone binding underlay interface. That’s how in the current design the source and destination zone are determined with an option to narrow down using VRF matching. The firewall policy on vSRX-right is the same.


    [edit security policies from-zone tenant-1-trust to-zone infra]
    vsrx-left# show | display set relative | display inheritance no-comments 
    set policy tenant-1 match source-address any
    set policy tenant-1 match destination-address any
    set policy tenant-1 match application any
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set policy tenant-1 then permit
    set policy tenant-1 then log session-close

    [edit security policies from-zone infra to-zone tenant-1-trust]
    vsrx-left# show | display set relative | display inheritance no-comments               
    set policy tenant-1 match source-address any
    set policy tenant-1 match destination-address any
    set policy tenant-1 match application any
    set policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set policy tenant-1 then permit
    set policy tenant-1 then log session-close

Finally, this is Linux-left establishing an SSH connection to Linux-right in the tenant-1 network namespace and related session listing from both the left and right vSRX instances. Sample Linux network namespace configuration for easy lab work (avoiding the need to have many endpoints) is described in Appendix 2.


    linux-left:~# alias t1
    alias t1='ip netns exec tenant-1'

    linux-left:~# t1 ssh 10.1.1.10 
    Linux linux-right 5.10.0-29-amd64 #1 SMP Debian 5.10.216-1 (2024-05-03) x86_64
    linux-right:~#

    vsrx-left> show security flow session destination-port 22    
    Session ID: 1414, Policy name: tenant-1/4, Timeout: 1798, Session State: Valid
      In: 10.1.2.10/49832 --> 10.1.1.10/22;tcp, If: ge-0/0/1.71, Pkts: 22, Bytes: 3928, 
      Out: 10.1.1.10/22 --> 10.1.2.10/49832;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 23, Bytes: 4952
    Total sessions: 1

    vsrx-right> show security flow session destination-port 22                         
    Session ID: 1401, Policy name: tenant-1/6, Timeout: 1792, Session State: Valid
      In: 10.1.2.10/49832 --> 10.1.1.10/22;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 22, Bytes: 3928, 
      Out: 10.1.1.10/22 --> 10.1.2.10/49832;tcp, If: ge-0/0/2.81, Pkts: 23, Bytes: 4952, 
    Total sessions: 1

Corresponding close log record from vSRX-right:


    RT_FLOW - RT_FLOW_SESSION_CLOSE [junos@2636.1.1.1.2.129 reason="TCP FIN" source-address="10.1.2.10" source-port="49832" destination-address="10.1.1.10" destination-port="22" connection-tag="0" service-name="junos-ssh" nat-source-address="10.1.2.10" nat-source-port="49832" nat-destination-address="10.1.1.10" nat-destination-port="22" nat-connection-tag="0" src-nat-rule-type="N/A" src-nat-rule-name="N/A" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="tenant-1" source-zone-name="infra" destination-zone-name="tenant-1-trust" session-id="1401" packets-from-client="169" bytes-from-client="16708" packets-from-server="305" bytes-from-server="28408" elapsed-time="16953" application="UNKNOWN" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="st0.0" encrypted="UNKNOWN" application-category="N/A" application-sub-category="N/A" application-risk="-1" application-characteristics="N/A" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="tenant-1" dst-vrf-grp="N/A" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

_Sidenote: to reduce log verbosity, a custom log format with selected columns could be used._

# Tenant-1 (blue) to Tenant-2 (green)

Next example is tenant-1 connecting to tenant-2 VRF where vSRX-right in a hub role is exchanging routing information between routing instances and enforces firewall policies.

The first example is Linux-left in the tenant-1-trust zone connecting to Linux-right in the tenant-2-trust zone.

_Figure 3 - blue tenant VRF to green tenant VRF (vSRX-right handled)_

Inter VRF routing is achieved using a shared instance named common-1 on vSRX-right, where the default routes from tenant-1 and tenant-2 VRFs are pointing. The use of the common instance addresses potential m:n route scalability issues if routes were full-mesh imported/exported directly. The layout of tenant and common VR route propagation:

_Figure 4 - vSRX right interlinking tenant VRFs using common-1 instance_

Routing table:


    common-1.inet.0: 6 destinations, 6 routes (6 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    10.1.1.0/24        *[Direct/0] 1d 21:24:54
                        >  via ge-0/0/2.81
    10.1.1.1/32        *[Local/0] 1d 21:24:54
                           Local via ge-0/0/2.81
    10.1.2.0/24        *[EVPN/170] 1d 14:12:22
                        >  to 100.70.0.2 via st0.0
    10.2.1.0/24        *[Direct/0] 1d 21:24:54
                        >  via ge-0/0/2.82
    10.2.1.1/32        *[Local/0] 1d 21:24:54
                           Local via ge-0/0/2.82
    10.2.2.0/24        *[EVPN/170] 1d 14:12:22
                        >  to 100.70.0.2 via st0.0

    tenant-1.inet.0: 4 destinations, 4 routes (4 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    0.0.0.0/0          *[Static/5] 1d 21:25:21
                           to table common-1.inet.0
    10.1.1.0/24        *[Direct/0] 1d 21:24:54
                        >  via ge-0/0/2.81
    10.1.1.1/32        *[Local/0] 1d 21:24:54
                           Local via ge-0/0/2.81
    10.1.2.0/24        *[EVPN/170] 1d 14:12:22
                        >  to 100.70.0.2 via st0.0

    tenant-2.inet.0: 4 destinations, 4 routes (4 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    0.0.0.0/0          *[Static/5] 1d 21:25:21
                           to table common-1.inet.0
    10.2.1.0/24        *[Direct/0] 1d 21:24:54
                        >  via ge-0/0/2.82
    10.2.1.1/32        *[Local/0] 1d 21:24:54
                           Local via ge-0/0/2.82
    10.2.2.0/24        *[EVPN/170] 1d 14:12:22

Security policies permit intra-tenant traffic for tenant-2 like for tenant-1 in the previous example (1st policy below); however, tenant-1 can reach the local tenant-2 zone only using SSH (defined as a dynamic application based on Application Identification) and ICMP echo-request (2nd policy).


    [edit security policies from-zone infra to-zone tenant-2-trust]
    vsrx-right# show | display set relative 
    set policy tenant-2 match source-address any
    set policy tenant-2 match destination-address any
    set policy tenant-2 match application any
    set policy tenant-2 match source-l3vpn-vrf-group tenant-2
    set policy tenant-2 then permit
    set policy tenant-2 then log session-close

    set policy tenant-1 match source-address any
    set policy tenant-1 match destination-address any
    set policy tenant-1 match application any
    set policy tenant-1 match dynamic-application junos:SSH
    set policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set policy tenant-1 then permit
    set policy tenant-1 then log session-close

Session listing on vSRX-right – tenant-1 on Linux-left connecting to tenant-2 endpoint on Linux-right:


    vsrx-right> show security flow session dynamic-application junos:SSH    
    Session ID: 1438, Policy name: tenant-1/10, Timeout: 1798, Session State: Valid
      In: 10.1.2.10/34762 --> 10.2.1.10/22;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 18, Bytes: 3612, 
      Out: 10.2.1.10/22 --> 10.1.2.10/34762;tcp, If: ge-0/0/2.82, Pkts: 22, Bytes: 4800, 
    Total sessions: 1

And corresponding vSRX-right session close log:


    RT_FLOW - RT_FLOW_SESSION_CLOSE [junos@2636.1.1.1.2.129 reason="TCP FIN" source-address="10.1.2.10" source-port="34762" destination-address="10.2.1.10" destination-port="22" connection-tag="0" service-name="junos-ssh" nat-source-address="10.1.2.10" nat-source-port="34762" nat-destination-address="10.2.1.10" nat-destination-port="22" nat-connection-tag="0" src-nat-rule-type="N/A" src-nat-rule-name="N/A" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="tenant-1" source-zone-name="infra" destination-zone-name="tenant-2-trust" session-id="1438" packets-from-client="24" bytes-from-client="4056" packets-from-server="27" bytes-from-server="5332" elapsed-time="118" application="SSH" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="st0.0" encrypted="No" application-category="Remote-Access" application-sub-category="Command" application-risk="4" application-characteristics="Supports File Transfer;Known Vulnerabilities;Capable of Tunneling;" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="tenant-1" dst-vrf-grp="N/A" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

Things get more interesting when vSRX-left tenant-1 is connecting to tenant-2 also bound to vSRX-left. Traffic is heading towards vSRX-right for policy enforcement and inter-VRF communication and U-turns back to vSRX-left.

_Sidenote: without IPSEC, and vSRX-left being, for example, a Juniper QFX device, this would have been a firewall between VRFs in a DC scenario._

_Figure 5 - U-turn on vSRX-right blue - green tenant VRF_

Policy on vSRX-right is evaluated in the infra to infra intra-zone context (another option would have been global policy with an option to narrow down to zones using from-zone to-zone matching). Application Identification based SSH, HTTP, and ICMP ping are permitted.


    [edit security policies from-zone infra to-zone infra]
    vsrx-right# show | display set relative 
    set policy tenant-1 apply-groups any-permit-log
    set policy tenant-1 match dynamic-application junos:SSH
    set policy tenant-1 match dynamic-application junos:HTTP
    set policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-2
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-3

Session listing on vSRX-right shows the effective U-turn of the traffic on the st0.0 IPSEC underlay tunnel adapter and tenant-1 / tenant-2 VRFs. SRX handles that as a single session across routing instances:


    vsrx-right> show security flow session dynamic-application junos:SSH    
    Session ID: 1441, Policy name: tenant-1/7, Timeout: 1796, Session State: Valid
      In: 10.1.2.10/55526 --> 10.2.2.10/22;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 18, Bytes: 3612, 
      Out: 10.2.2.10/22 --> 10.1.2.10/55526;tcp, L3VPN VRF Group: tenant-2, If: st0.0, Pkts: 17, Bytes: 4388,

Implication on vSRX-left is tracking the same session twice due to different ingress interface/zone.


    vsrx-left> show security flow session destination-port 22 
    Session ID: 1454, Policy name: tenant-1/4, Timeout: 1782, Session State: Valid
      In: 10.1.2.10/55526 --> 10.2.2.10/22;tcp, If: ge-0/0/1.71, Pkts: 18, Bytes: 3612, 
      Out: 10.2.2.10/22 --> 10.1.2.10/55526;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 17, Bytes: 4388, 

    Session ID: 1455, Policy name: tenant-2/7, Timeout: 1782, Session State: Valid
      In: 10.1.2.10/55526 --> 10.2.2.10/22;tcp, L3VPN VRF Group: tenant-2, If: st0.0, Pkts: 18, Bytes: 3612, 
      Out: 10.2.2.10/22 --> 10.1.2.10/55526;tcp, If: ge-0/0/1.72, Pkts: 17, Bytes: 4388,
    Total sessions: 2

Two related vSRX-left session close logs:


    RT_FLOW_SESSION_CLOSE [junos@2636.1.1.1.2.129 reason="TCP FIN" source-address="10.1.2.10" source-port="55526" destination-address="10.2.2.10" destination-port="22" connection-tag="0" service-name="junos-ssh" nat-source-address="10.1.2.10" nat-source-port="55526" nat-destination-address="10.2.2.10" nat-destination-port="22" nat-connection-tag="0" src-nat-rule-type="N/A" src-nat-rule-name="N/A" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="tenant-1" source-zone-name="tenant-1-trust" destination-zone-name="infra" session-id="1454" packets-from-client="28" bytes-from-client="4372" packets-from-server="28" bytes-from-server="5376" elapsed-time="477" application="UNKNOWN" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="ge-0/0/1.71" encrypted="UNKNOWN" application-category="N/A" application-sub-category="N/A" application-risk="-1" application-characteristics="N/A" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="N/A" dst-vrf-grp="tenant-1" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

    RT_FLOW - RT_FLOW_SESSION_CLOSE [junos@2636.1.1.1.2.129 reason="TCP FIN" source-address="10.1.2.10" source-port="55526" destination-address="10.2.2.10" destination-port="22" connection-tag="0" service-name="junos-ssh" nat-source-address="10.1.2.10" nat-source-port="55526" nat-destination-address="10.2.2.10" nat-destination-port="22" nat-connection-tag="0" src-nat-rule-type="N/A" src-nat-rule-name="N/A" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="tenant-2" source-zone-name="infra" destination-zone-name="tenant-2-trust" session-id="1455" packets-from-client="28" bytes-from-client="4372" packets-from-server="28" bytes-from-server="5376" elapsed-time="477" application="UNKNOWN" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="st0.0" encrypted="UNKNOWN" application-category="N/A" application-sub-category="N/A" application-risk="-1" application-characteristics="N/A" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="tenant-2" dst-vrf-grp="N/A" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

# Tenant-1 (blue) to Tenant-3 (red) – Overlapping IP Prefixes

Enhancement of the previous example is cross-tenant communication when IP prefixes overlap - specifically, tenant-1 and tenant-2 communication:

_Figure 6 - Overlapping prefix handling on vSRX-right for blue/red tenant VRFs_

The solution for tenant-1 connecting to tenant-2 is to leverage the bi-directional nature of static NAT, where tenant-1 10.1.0.0/16 is represented by the arbitrary prefix 10.21/16 and correspondingly tenant-3 10.1.0.0/16 by the 10.23/16 prefix

_Figure 7 - Details of vSRX-right NAT approach_

vSRX-right static NAT settings (complete config in Appendix 3. also covers traffic from local interface):


    [edit security nat static]
    vsrx-right# show | display set relative 
    set rule-set tenant-1-vrf from routing-group tenant-1
    set rule-set tenant-1-vrf rule tenant-1-vrf match source-address 10.1.0.0/16
    set rule-set tenant-1-vrf rule tenant-1-vrf match destination-address 10.23.0.0/16
    set rule-set tenant-1-vrf rule tenant-1-vrf then static-nat prefix 10.1.0.0/16
    set rule-set tenant-1-vrf rule tenant-1-vrf then static-nat prefix routing-instance tenant-3

    set rule-set tenant-3-vrf from routing-group tenant-3
    set rule-set tenant-3-vrf rule tenant-3-vrf match source-address 10.1.0.0/16
    set rule-set tenant-3-vrf rule tenant-3-vrf match destination-address 10.21.0.0/16
    set rule-set tenant-3-vrf rule tenant-3-vrf then static-nat prefix 10.1.0.0/16
    set rule-set tenant-3-vrf rule tenant-3-vrf then static-nat prefix routing-instance tenant-1

The same security policy as in the previous example in the infra to infra zone context, matching on tenant-3 VRF:


    [edit security policies from-zone infra to-zone infra]
    vsrx-right# show | display set relative 
    set policy tenant-1 apply-groups any-permit-log
    set policy tenant-1 match dynamic-application junos:SSH
    set policy tenant-1 match dynamic-application junos:HTTP
    set policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-2
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-3

Sample session listing on vSRX-right with static NAT in action:


    srx-right> show security flow session dynamic-application junos:SSH    
    Session ID: 127, Policy name: tenant-1/7, Timeout: 1706, Session State: Valid
      In: 10.1.2.10/50440 --> 10.23.2.10/22;tcp, L3VPN VRF Group: tenant-1, If: st0.0, Pkts: 19, Bytes: 3672, 
      Out: 10.1.2.10/22 --> 10.21.2.10/50440;tcp, L3VPN VRF Group: tenant-3, If: st0.0, Pkts: 18, Bytes: 4476, 
    Total sessions: 1o

Session listing from vSRX-left where naturally two sessions are seen as in the previous example:


    vsrx-left> show security flow session destination-port 22 
    Session ID: 128, Policy name: tenant-1/4, Timeout: 1718, Session State: Valid
      In: 10.1.2.10/50440 --> 10.23.2.10/22;tcp, If: ge-0/0/1.71, Pkts: 19, Bytes: 3672, 
      Out: 10.23.2.10/22 --> 10.1.2.10/50440;tcp, L3VPN VRF Group: tenant-1, If: ge-0/0/0.101, Pkts: 18, Bytes: 4476, 

    Session ID: 129, Policy name: tenant-3/9, Timeout: 1718, Session State: Valid
      In: 10.21.2.10/50440 --> 10.1.2.10/22;tcp, L3VPN VRF Group: tenant-3, If: ge-0/0/0.101, Pkts: 19, Bytes: 3672, 
      Out: 10.1.2.10/22 --> 10.21.2.10/50440;tcp, If: ge-0/0/1.73, Pkts: 18, Bytes: 4476,
    Total sessions: 2

And related close-log from vSRX-right:


    RT_FLOW_SESSION_CLOSE [junos@2636.1.1.1.2.129 reason="TCP FIN" source-address="10.1.2.10" source-port="50440" destination-address="10.23.2.10" destination-port="22" connection-tag="0" service-name="junos-ssh" nat-source-address="10.21.2.10" nat-source-port="50440" nat-destination-address="10.1.2.10" nat-destination-port="22" nat-connection-tag="0" src-nat-rule-type="static rule" src-nat-rule-name="tenant-3-vrf" dst-nat-rule-type="static rule" dst-nat-rule-name="tenant-1-vrf" protocol-id="6" policy-name="tenant-1" source-zone-name="infra" destination-zone-name="infra" session-id="127" packets-from-client="27" bytes-from-client="4292" packets-from-server="27" bytes-from-server="5300" elapsed-time="243" application="SSH" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="st0.0" encrypted="No" application-category="Remote-Access" application-sub-category="Command" application-risk="4" application-characteristics="Supports File Transfer;Known Vulnerabilities;Capable of Tunneling;" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="tenant-1" dst-vrf-grp="tenant-3" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

# MTU Considerations

Due to the VXLAN header and IPSEC header + trailer overhead, the effective MTU for endpoint traffic is reduced. This is not a concern in a DC scenario where large MTUs must be used. There are a couple of ways to address this in scenarios where a large MTU can't be configured.

This is the header size breakdown for an MTU of 1500 bytes in the specific setup:

**Header Type** | **Size (B)**
---|---
Ether | 14
802.1q | 4
IPv4 | 20
ESP | 54
UDP | 8
VXLAN | 8
Ether | 14
IPv4 | 20
TCP header | 32
TCP payload | 1344


TCP can be easily influenced by adjusting the TCP Maximum Segment Size (MSS). In a scenario with VXLAN and IPSEC AES256-GCM transform, the exact TCP-MSS value is 1356B (effectively on the wire 1344B due to an extra 12B in the TCP header above the minimum of 20B). For clear-text without the IPSEC header, MSS would have been 1410B. These settings can be configured on the SRX either globally or per policy.

Global MSS settings for IPSEC scenario:


    set security flow tcp-mss ipsec-vpn mss 1356

Global MSS settings for clear-text scenario (not applicable to DC with appropriate MTU!):


    set security flow tcp-mss all-tcp mss 1410

Without MSS or for non-TCP traffic, Path MTU discovery by host OS is next. Oversized Don’t Fragment flagged IP packets get ICMP need frag needed message:


    14:16:56.765270 52:54:00:18:ce:48 > 52:54:00:c2:78:8f, ethertype 802.1Q (0x8100), length 1606: vlan 81, p 0, ethertype IPv4 (0x0800), (tos 0x0, ttl 64, id 56951, offset 0, flags [DF], proto TCP (6), length 1588)
        10.1.1.10.53000 > 10.1.2.10.22: Flags [P.], seq 41:1577, ack 41, win 502, options [nop,nop,TS val 4180791614 ecr 4000098031], length 1536

    14:16:56.765395 52:54:00:c2:78:8f > 52:54:00:18:ce:48, ethertype 802.1Q (0x8100), length 74: vlan 81, p 0, ethertype IPv4 (0x0800), (tos 0x0, ttl 254, id 14449, offset 0, flags [none], proto ICMP (1), length 56)
        10.1.1.1 > 10.1.1.10: ICMP 10.1.2.10 unreachable - need to frag (mtu 1396), length 36
            (tos 0x0, ttl 64, id 56951, offset 0, flags [DF], proto TCP (6), length 1500)
        10.1.1.10.53000 > 10.1.2.10.22:  [|tcp]

And IP stack caches the PMTU information:


    linux-right:~# t1 ip rou get 10.1.2.10
    10.1.2.10 via 10.1.1.1 dev eth1.81 src 10.1.1.10 uid 0 
        cache expires 273sec mtu 1396

It should be noted that ICMP type 3 code 4 replies are rate-limited on SRX firewalls due to the potential for abuse as a DoS attack vector. Relying on this method for production is NOT recommended. Using MSS clamping, as described above, is the most efficient mechanism. Alternatively, using flow fragmentation and reassembly is another method, which is described next.

In this specific example setup, the maximum UDP payload that can be passed via a 1500B MTU is 1368B. Pre-fragmentation occurs when crossing this boundary. For instance, if 2B oversized UDP packets are sent from Linux-right to Linux-left using the hping tool and captured on Linux-left using tcpdump:


    linux-right:~# t1 hping3 -2 -s 1024 --keep 10.1.2.10 -d 1370 -p 1024 
    HPING 10.1.2.10 (eth1.81 10.1.2.10): udp mode set, 28 headers + 1370 data bytes

    linux-left:~# tcpdump -n -i eth1 not arp -v
    tcpdump: listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
    16:34:22.042015 IP (tos 0x0, ttl 63, id 38195, offset 0, flags [+], proto UDP (17), length 1396)
        10.1.1.10.1024 > 10.1.2.10.1024: UDP, length 1370
    16:34:22.042017 IP (tos 0x0, ttl 63, id 38195, offset 1376, flags [none], proto UDP (17), length 22)
        10.1.1.10 > 10.1.2.10: ip-proto-17

If fragmentation is not desirable, SRX can reassemble the packets towards egress:


    set security flow force-ip-reassembly

Then unlike capture above, receiving side gets reassembled traffic. However, please note that there are performance implications of using both pre-fragmentation and reassembly.


    linux-left:~# tcpdump -n -i eth1 not arp -v
    tcpdump: listening on eth1, link-type EN10MB (Ethernet), snapshot length 262144 bytes
    16:40:35.099305 IP (tos 0x0, ttl 63, id 49943, offset 0, flags [none], proto UDP (17), length 1398)
        10.1.1.10.1024 > 10.1.2.10.1024: UDP, length 1370
    16:40:36.099391 IP (tos 0x0, ttl 63, id 15129, offset 0, flags [none], proto UDP (17), length 1398)
        10.1.1.10.1024 > 10.1.2.10.1024: UDP, length 1370

# Appendix 1 – SRX Transit VXLAN Tunnel Inspection

Let’s have a brief look at the transit EVPN VXLAN tunnel inspection feature. For this purpose, IPSEC underlay is disabled, and vSRX-r1 is performing the inspections of VXLAN encapsulated traffic between vSRX-left and vSRX-right loopback interfaces. The scenario looked at is vSRX-left blue tenant-1 talking to green tenant-2:

_Figure 8 - vSRX-r1 inspection and enforcement of unencrypted VXLAN_

The security policy on vSRX-right from infra to infra zone looks as follows, permitting, besides others, also HTTP. In our arbitrary scenario, HTTP is not a concern if the transit is encrypted; however, it becomes problematic when passing unencrypted towards the WAN:


    [edit security policies from-zone infra to-zone infra]
    vsrx-right# show | display set relative 
    set policy tenant-1 apply-groups any-permit-log
    set policy tenant-1 match dynamic-application junos:SSH
    set policy tenant-1 match dynamic-application junos:HTTP
    set policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-2
    set policy tenant-1 match destination-l3vpn-vrf-group tenant-3

To address this, vSRX-r1 prohibits VXLAN encapsulated HTTP communication and permits the rest. Global router like any/any/permit policy pointing to the VXLAN tunnel inspection profile:


    [edit security policies global]
    vsrx-r1# show | display set 
    set security policies global policy all match source-address any
    set security policies global policy all match destination-address any
    set security policies global policy all match application any
    set security policies global policy all then permit tunnel-inspection insp-prof-1

Inspection profile matching on any VNI and related policy-set – effectively rule-base for inspected transit VXLAN traffic:


    [edit security tunnel-inspection]
    vsrx-r1# show | display set relative 
    set inspection-profile insp-prof-1 vxlan pol-set-1 policy-set pol-set-1
    set inspection-profile insp-prof-1 vxlan pol-set-1 vni any

    [edit security policies policy-set pol-set-1]
    vsrx-r1# show | display set relative 
    set policy reject-some match source-address any
    set policy reject-some match destination-address any
    set policy reject-some match application any
    set policy reject-some match dynamic-application junos:HTTP
    set policy reject-some then reject
    set policy reject-some then log session-init
    set policy permit-all match source-address any
    set policy permit-all match destination-address any
    set policy permit-all match application any
    set policy permit-all match dynamic-application any
    set policy permit-all then permit
    set policy permit-all then log session-close

vSRX-r1 discarding the HTTP traffic:


    vsrx-r1> monitor security packet-drop    
    Starting packet drop:
    10:56:18.761458:LSYS-ID-00 10.2.2.10/80-->10.1.2.10/46284;tcp,ipid-38722,ge-0/0/0.101,Dropped by POLICY:discarded by dynapp policy reject-some

Related log of rejected HTTP communication:


    RT_FLOW_SESSION_DENY [junos@2636.1.1.1.2.129 source-address="10.1.2.10" source-port="46284" destination-address="10.2.2.10" destination-port="80" connection-tag="fcd" service-name="junos-http" protocol-id="6" icmp-type="0" policy-name="reject-some" source-zone-name="all" destination-zone-name="all" application="HTTP" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="ge-0/0/0.101" encrypted="No" reason="Rejected by policy" session-id="409" application-category="Web" application-sub-category="N/A" application-risk="4" application-characteristics="Can Leak Information;Supports File Transfer;Prone to Misuse;Known Vulnerabilities;Carrier of Malware;Capable of Tunneling;" src-vrf-grp="N/A" dst-vrf-grp="N/A" source-tenant="N/A" destination-service="N/A" user-type="N/A"]

For completeness, example session listing of permitted SSH session (matching permit-all policy) between tenant-1 left and tenant-2 right:


    vsrx-r1> show security flow session tunnel-inspection-type vxlan    
    Total sessions: 0

    root@vsrx-r1> show security flow session tunnel-inspection-type vxlan    
    Session ID: 392, Policy name: permit-all/6, Timeout: 1796, Session State: Valid
      In: 10.1.2.10/55412 --> 10.2.2.10/22;tcp, Conn Tag: 0xfcd, If: ge-0/0/0.101, Pkts: 36, Bytes: 7224, 
      Type: VXLAN, VNI: 2, Tunnel Session ID: 393
      Out: 10.2.2.10/22 --> 10.1.2.10/55412;tcp, Conn Tag: 0xfcd, If: ge-0/0/1.100, Pkts: 32, Bytes: 8672, 
      Type: VXLAN, VNI: 1, Tunnel Session ID: 395

# Appendix 2 – Linux Network Namespace Sample Configs

For convenience, execution of commands in Linux network namespaces is done using shell aliases folding complete command line into two characters (t1, t2, t3) with a parameter of command to be executed. For example:


    linux-right:~# cat .bashrc
    alias t1='ip netns exec tenant-1'
    alias t2='ip netns exec tenant-2'
    alias t3='ip netns exec tenant-3'

    linux-right:~# alias
    alias t1='ip netns exec tenant-1'
    alias t2='ip netns exec tenant-2'
    alias t3='ip netns exec tenant-3'

    linux-right:~# t1 ping 10.1.2.10
    PING 10.1.2.10 (10.1.2.10) 56(84) bytes of data.
    64 bytes from 10.1.2.10: icmp_seq=1 ttl=63 time=2.24 ms

Namespaces can be configured for example as part of interface settings (on Debian Linux typically in /etc/network/interfaces). For testing purposes there are also SSH, nginx and inetd daemons spawn in namespaces, otherwise namespace doesn’t have any bound service by default. Self-explanatory example from the demo setup:


    linux-right:~# cat /etc/network/interfaces
    source /etc/network/interfaces.d/*

    auto lo
    iface lo inet loopback

    auto eth0
    iface eth0 inet static
            address 172.30.100.208/24
            dns-nameservers 172.30.100.105
            gateway 172.30.100.1

    auto eth1
    iface eth1 inet manual

    #tenant-1
            up ip netns add tenant-1
            up ip link add link eth1 name eth1.81 type vlan id 81
            up ip link set eth1.81 netns tenant-1
            up ip netns exec tenant-1 ip link set eth1.81 up
            up ip netns exec tenant-1 ip addr add 10.1.1.10/24 dev eth1.81 
            up ip netns exec tenant-1 ip rou add default via 10.1.1.1
            up $( sleep 3; ip netns exec tenant-1 /usr/sbin/sshd -o PidFile=/run/sshd-tenant-1.pid ) &
            up $( sleep 3; ip netns exec tenant-1 /usr/sbin/nginx ) &
            up $( sleep 3; ip netns exec tenant-1 /usr/sbin/inetd ) &

    #tenant-2
            up ip netns add tenant-2
            up ip link add link eth1 name eth1.82 type vlan id 82
            up ip link set eth1.82 netns tenant-2
            up ip netns exec tenant-2 ip link set eth1.82 up
            up ip netns exec tenant-2 ip addr add 10.2.1.10/24 dev eth1.82
            up ip netns exec tenant-2 ip rou add default via 10.2.1.1
            up $( sleep 3; ip netns exec tenant-2 /usr/sbin/sshd -o PidFile=/run/sshd-tenant-2.pid ) &
            up $( sleep 3; ip netns exec tenant-2 /usr/sbin/nginx ) &
            up $( sleep 3; ip netns exec tenant-2 /usr/sbin/inetd ) &

    #tenant-3
            up ip netns add tenant-3
            up ip link add link eth1 name eth1.83 type vlan id 83
            up ip link set eth1.83 netns tenant-3
            up ip netns exec tenant-3 ip link set eth1.83 up
            up ip netns exec tenant-3 ip addr add 10.1.1.10/24 dev eth1.83 
            up ip netns exec tenant-3 ip rou add default via 10.1.1.1
            up $( sleep 3; ip netns exec tenant-3 /usr/sbin/sshd -o PidFile=/run/sshd-tenant-3.pid ) &
            up $( sleep 3; ip netns exec tenant-3 /usr/sbin/nginx ) &
            up $( sleep 3; ip netns exec tenant-3 /usr/sbin/inetd ) &

# Appendix 3 – SRX Configuration Files

Please note that configuration files are pristine, demo/testbed grade, real life requires tuning, hardening, and appropriate qualification. vSRX-left has tenants configured in a form of Junos groups and takes different sample approach to tighten BGP signaling than vSRX-right.

vSRX-left:


    set version 23.2R2.21
    set groups tenant-1 security policies from-zone tenant-1-trust to-zone infra apply-groups any-permit
    set groups tenant-1 security policies from-zone tenant-1-trust to-zone infra policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set groups tenant-1 security policies from-zone infra to-zone tenant-1-trust apply-groups any-permit
    set groups tenant-1 security policies from-zone infra to-zone tenant-1-trust policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set groups tenant-1 security zones security-zone tenant-1-trust tcp-rst
    set groups tenant-1 security zones security-zone tenant-1-trust interfaces ge-0/0/1.71 host-inbound-traffic system-services ping
    set groups tenant-1 security l3vpn vrf-group tenant-1 vrf tenant-1
    set groups tenant-1 interfaces ge-0/0/1 vlan-tagging
    set groups tenant-1 interfaces ge-0/0/1 unit 71 description tenant-1
    set groups tenant-1 interfaces ge-0/0/1 unit 71 vlan-id 71
    set groups tenant-1 interfaces ge-0/0/1 unit 71 family inet address 10.1.2.1/24
    set groups tenant-1 policy-options policy-statement export-tenant-1 term 1 from interface ge-0/0/1.71
    set groups tenant-1 policy-options policy-statement export-tenant-1 term 1 then accept
    set groups tenant-1 policy-options policy-statement export-tenant-1 term 100 then reject
    set groups tenant-1 routing-instances tenant-1 instance-type vrf
    set groups tenant-1 routing-instances tenant-1 protocols evpn ip-prefix-routes advertise direct-nexthop
    set groups tenant-1 routing-instances tenant-1 protocols evpn ip-prefix-routes encapsulation vxlan
    set groups tenant-1 routing-instances tenant-1 protocols evpn ip-prefix-routes vni 1
    set groups tenant-1 routing-instances tenant-1 protocols evpn ip-prefix-routes export export-tenant-1
    set groups tenant-1 routing-instances tenant-1 interface ge-0/0/1.71
    set groups tenant-1 routing-instances tenant-1 route-distinguisher 100.65.0.1:1
    set groups tenant-1 routing-instances tenant-1 vrf-target target:65001:1
    set groups tenant-2 security policies from-zone tenant-2-trust to-zone infra apply-groups any-permit
    set groups tenant-2 security policies from-zone tenant-2-trust to-zone infra policy tenant-2 match destination-l3vpn-vrf-group tenant-2
    set groups tenant-2 security policies from-zone infra to-zone tenant-2-trust apply-groups any-permit
    set groups tenant-2 security policies from-zone infra to-zone tenant-2-trust policy tenant-2 match source-l3vpn-vrf-group tenant-2
    set groups tenant-2 security zones security-zone tenant-2-trust tcp-rst
    set groups tenant-2 security zones security-zone tenant-2-trust interfaces ge-0/0/1.72 host-inbound-traffic system-services ping
    set groups tenant-2 security l3vpn vrf-group tenant-2 vrf tenant-2
    set groups tenant-2 interfaces ge-0/0/1 unit 72 description tenant-2
    set groups tenant-2 interfaces ge-0/0/1 unit 72 vlan-id 72
    set groups tenant-2 interfaces ge-0/0/1 unit 72 family inet address 10.2.2.1/24
    set groups tenant-2 policy-options policy-statement export-tenant-2 term 1 from interface ge-0/0/1.72
    set groups tenant-2 policy-options policy-statement export-tenant-2 term 1 then accept
    set groups tenant-2 policy-options policy-statement export-tenant-2 term 100 then reject
    set groups tenant-2 routing-instances tenant-2 instance-type vrf
    set groups tenant-2 routing-instances tenant-2 protocols evpn ip-prefix-routes advertise direct-nexthop
    set groups tenant-2 routing-instances tenant-2 protocols evpn ip-prefix-routes encapsulation vxlan
    set groups tenant-2 routing-instances tenant-2 protocols evpn ip-prefix-routes vni 2
    set groups tenant-2 routing-instances tenant-2 protocols evpn ip-prefix-routes export export-tenant-2
    set groups tenant-2 routing-instances tenant-2 interface ge-0/0/1.72
    set groups tenant-2 routing-instances tenant-2 route-distinguisher 100.65.0.1:2
    set groups tenant-2 routing-instances tenant-2 vrf-target target:65001:2
    set groups tenant-3 security policies from-zone tenant-3-trust to-zone infra apply-groups any-permit
    set groups tenant-3 security policies from-zone tenant-3-trust to-zone infra policy tenant-3 match destination-l3vpn-vrf-group tenant-3
    set groups tenant-3 security policies from-zone infra to-zone tenant-3-trust apply-groups any-permit
    set groups tenant-3 security policies from-zone infra to-zone tenant-3-trust policy tenant-3 match source-l3vpn-vrf-group tenant-3
    set groups tenant-3 security zones security-zone tenant-3-trust tcp-rst
    set groups tenant-3 security zones security-zone tenant-3-trust interfaces ge-0/0/1.73 host-inbound-traffic system-services ping
    set groups tenant-3 security l3vpn vrf-group tenant-3 vrf tenant-3
    set groups tenant-3 interfaces ge-0/0/1 unit 73 description tenant-3
    set groups tenant-3 interfaces ge-0/0/1 unit 73 vlan-id 73
    set groups tenant-3 interfaces ge-0/0/1 unit 73 family inet address 10.1.2.1/24
    set groups tenant-3 policy-options policy-statement export-tenant-3 term 1 from interface ge-0/0/1.73
    set groups tenant-3 policy-options policy-statement export-tenant-3 term 1 then accept
    set groups tenant-3 policy-options policy-statement export-tenant-3 term 100 then reject
    set groups tenant-3 routing-instances tenant-3 instance-type vrf
    set groups tenant-3 routing-instances tenant-3 protocols evpn ip-prefix-routes advertise direct-nexthop
    set groups tenant-3 routing-instances tenant-3 protocols evpn ip-prefix-routes encapsulation vxlan
    set groups tenant-3 routing-instances tenant-3 protocols evpn ip-prefix-routes vni 3
    set groups tenant-3 routing-instances tenant-3 protocols evpn ip-prefix-routes export export-tenant-3
    set groups tenant-3 routing-instances tenant-3 interface ge-0/0/1.73
    set groups tenant-3 routing-instances tenant-3 route-distinguisher 100.65.0.1:3
    set groups tenant-3 routing-instances tenant-3 vrf-target target:65001:3
    set groups any-permit security policies from-zone <*> to-zone <*> policy <*> match source-address any
    set groups any-permit security policies from-zone <*> to-zone <*> policy <*> match destination-address any
    set groups any-permit security policies from-zone <*> to-zone <*> policy <*> match application any
    set groups any-permit security policies from-zone <*> to-zone <*> policy <*> then permit
    set groups any-permit security policies from-zone <*> to-zone <*> policy <*> then log session-close
    set apply-groups tenant-1
    set apply-groups tenant-2
    set apply-groups tenant-3
    set system host-name vsrx-left
    set system services ssh root-login allow
    set system services ssh sftp-server
    set system services ssh client-alive-interval 120
    set system time-zone Europe/Amsterdam
    set system name-server 172.30.100.105
    set system syslog file messages any any
    set system syslog file messages archive size 5m
    set system syslog file messages archive files 5
    set system syslog file traffic any any
    set system syslog file traffic match RT_
    set system syslog file traffic archive size 1m
    set system syslog file traffic archive files 4
    set system syslog file traffic structured-data brief
    set system ntp server 172.30.100.105
    set services application-identification
    set security ike proposal ike-prop authentication-method pre-shared-keys
    set security ike proposal ike-prop dh-group group20
    set security ike proposal ike-prop encryption-algorithm aes-256-gcm
    set security ike proposal ike-prop lifetime-seconds 28800
    set security ike policy ike-policy proposals ike-prop
    set security ike policy ike-policy pre-shared-key ascii-text "<REDACTED_STRONG_PSK>"
    set security ike gateway vsrx-right ike-policy ike-policy
    set security ike gateway vsrx-right address 10.0.0.10
    set security ike gateway vsrx-right dead-peer-detection probe-idle-tunnel
    set security ike gateway vsrx-right external-interface ge-0/0/0.101
    set security ike gateway vsrx-right version v2-only
    set security ipsec proposal ipsec-prop encryption-algorithm aes-256-gcm
    set security ipsec proposal ipsec-prop lifetime-seconds 3600
    set security ipsec policy ipsec-policy perfect-forward-secrecy keys group20
    set security ipsec policy ipsec-policy proposals ipsec-prop
    set security ipsec vpn vsrx-right bind-interface st0.0
    set security ipsec vpn vsrx-right ike gateway vsrx-right
    set security ipsec vpn vsrx-right ike ipsec-policy ipsec-policy
    set security ipsec vpn vsrx-right establish-tunnels immediately
    set security alg dns disable
    set security alg ftp disable
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
    set security flow tcp-mss ipsec-vpn mss 1356
    set security flow tcp-session strict-syn-check
    set security forwarding-process enhanced-services-mode
    set security address-book global address vSRX-r1 10.0.1.1/32
    set security address-book global address vSRX1-lo0 100.65.0.1/32
    set security address-book global address vSRX1-st0 100.70.0.1/32
    set security address-book global address-set EVPN address vSRX-r1
    set security address-book global address-set EVPN address vSRX1-lo0
    set security address-book global address-set EVPN address vSRX1-st0
    set security policies global policy infra match source-address EVPN
    set security policies global policy infra match destination-address any
    set security policies global policy infra match application junos-bgp
    set security policies global policy infra match application bfd-mhop
    set security policies global policy infra match from-zone infra
    set security policies global policy infra match to-zone infra
    set security policies global policy infra then permit
    set security policies global policy infra-ping match source-address any
    set security policies global policy infra-ping match destination-address any
    set security policies global policy infra-ping match application junos-icmp-ping
    set security policies global policy infra-ping then permit
    set security policies global policy drop-log match source-address any
    set security policies global policy drop-log match destination-address any
    set security policies global policy drop-log match application any
    set security policies global policy drop-log then deny
    set security policies global policy drop-log then log session-init
    set security zones security-zone infra host-inbound-traffic system-services ping
    set security zones security-zone infra host-inbound-traffic system-services ike
    set security zones security-zone infra host-inbound-traffic protocols bgp
    set security zones security-zone infra host-inbound-traffic protocols bfd
    set security zones security-zone infra interfaces ge-0/0/0.101
    set security zones security-zone infra interfaces lo0.0
    set security zones security-zone infra interfaces st0.0
    set interfaces ge-0/0/0 description r1
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 101 description underlay-phy
    set interfaces ge-0/0/0 unit 101 vlan-id 101
    set interfaces ge-0/0/0 unit 101 family inet address 10.0.1.10/24
    set interfaces fxp0 unit 0 family inet address 172.30.100.215/24
    set interfaces lo0 unit 0 description overlay
    set interfaces lo0 unit 0 family inet address 100.65.0.2/32
    set interfaces st0 unit 0 description underlay-ipsec
    set interfaces st0 unit 0 family inet address 100.70.0.2/24
    set policy-options policy-statement export-underlay term 1 from interface lo0.0
    set policy-options policy-statement export-underlay term 1 then accept
    set policy-options policy-statement export-underlay term 100 then reject
    set applications application bfd-mhop term 1 protocol udp
    set applications application bfd-mhop term 1 destination-port 4784
    set protocols bgp group underlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group underlay bfd-liveness-detection multiplier 3
    set protocols bgp group underlay neighbor 10.0.1.1 description r1 
    set protocols bgp group underlay neighbor 10.0.1.1 export export-underlay
    set protocols bgp group underlay neighbor 10.0.1.1 peer-as 65000
    set protocols bgp group underlay neighbor 10.0.1.1 local-as 65002
    set protocols bgp group underlay neighbor 100.70.0.1 export export-underlay
    set protocols bgp group underlay neighbor 100.70.0.1 description vsrx-right-st0
    set protocols bgp group underlay neighbor 100.70.0.1 peer-as 65001
    set protocols bgp group underlay neighbor 100.70.0.1 local-as 65002
    set protocols bgp group overlay multihop
    set protocols bgp group overlay local-address 100.65.0.2
    set protocols bgp group overlay family evpn signaling
    set protocols bgp group overlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group overlay bfd-liveness-detection multiplier 5
    set protocols bgp group overlay neighbor 100.65.0.1 peer-as 65101
    set protocols bgp group overlay neighbor 100.65.0.1 local-as 65102
    set routing-options static route 0.0.0.0/0 next-hop 172.30.100.1

vSRX-right:


    set version 23.2R2.21
    set groups any-permit-log security policies from-zone <*> to-zone <*> policy <*> match source-address any
    set groups any-permit-log security policies from-zone <*> to-zone <*> policy <*> match destination-address any
    set groups any-permit-log security policies from-zone <*> to-zone <*> policy <*> match application any
    set groups any-permit-log security policies from-zone <*> to-zone <*> policy <*> then permit
    set groups any-permit-log security policies from-zone <*> to-zone <*> policy <*> then log session-close
    set system host-name vsrx-right
    set system services ssh root-login allow
    set system services ssh sftp-server
    set system services ssh client-alive-interval 120
    set system time-zone Europe/Amsterdam
    set system name-server 172.30.100.105
    set system syslog file messages any any
    set system syslog file messages archive size 5m
    set system syslog file messages archive files 5
    set system syslog file traffic any any
    set system syslog file traffic match RT_
    set system syslog file traffic archive size 1m
    set system syslog file traffic archive files 4
    set system syslog file traffic structured-data brief
    set system ntp server 172.30.100.105
    set security log mode stream-event
    set security log report
    set security ike proposal ike-prop authentication-method pre-shared-keys
    set security ike proposal ike-prop dh-group group20
    set security ike proposal ike-prop encryption-algorithm aes-256-gcm
    set security ike proposal ike-prop lifetime-seconds 28800
    set security ike policy ike-policy proposals ike-prop
    set security ike policy ike-policy pre-shared-key ascii-text "<REDACTED_STRONG_PSK>"
    set security ike gateway vsrx-left ike-policy ike-policy
    set security ike gateway vsrx-left address 10.0.1.10
    set security ike gateway vsrx-left dead-peer-detection probe-idle-tunnel
    set security ike gateway vsrx-left external-interface ge-0/0/1.100
    set security ike gateway vsrx-left version v2-only
    set security ipsec proposal ipsec-prop encryption-algorithm aes-256-gcm
    set security ipsec proposal ipsec-prop lifetime-seconds 3600
    set security ipsec policy ipsec-policy perfect-forward-secrecy keys group20
    set security ipsec policy ipsec-policy proposals ipsec-prop
    set security ipsec vpn vsrx-left bind-interface st0.0
    set security ipsec vpn vsrx-left ike gateway vsrx-left
    set security ipsec vpn vsrx-left ike ipsec-policy ipsec-policy
    set security address-book global address n_tenant-1 10.1.0.0/16
    set security address-book global address n_tenant-3 10.2.0.0/16
    set security address-book global address n_tenant-2 10.2.0.0/16
    set security alg dns disable
    set security alg ftp disable
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
    set security flow tcp-mss ipsec-vpn mss 1356
    set security flow tcp-session strict-syn-check
    set security nat static rule-set tenant-1-vrf from routing-group tenant-1
    set security nat static rule-set tenant-1-vrf rule tenant-1-vrf match source-address 10.1.0.0/16
    set security nat static rule-set tenant-1-vrf rule tenant-1-vrf match destination-address 10.23.0.0/16
    set security nat static rule-set tenant-1-vrf rule tenant-1-vrf then static-nat prefix 10.1.0.0/16
    set security nat static rule-set tenant-1-vrf rule tenant-1-vrf then static-nat prefix routing-instance tenant-3
    set security nat static rule-set tenant-3-vrf from routing-group tenant-3
    set security nat static rule-set tenant-3-vrf rule tenant-3-vrf match source-address 10.1.0.0/16
    set security nat static rule-set tenant-3-vrf rule tenant-3-vrf match destination-address 10.21.0.0/16
    set security nat static rule-set tenant-3-vrf rule tenant-3-vrf then static-nat prefix 10.1.0.0/16
    set security nat static rule-set tenant-3-vrf rule tenant-3-vrf then static-nat prefix routing-instance tenant-1
    set security nat static rule-set tenant-1-loc from zone tenant-1-trust
    set security nat static rule-set tenant-1-loc rule tenant-1-loc match source-address 10.1.0.0/16
    set security nat static rule-set tenant-1-loc rule tenant-1-loc match destination-address 10.23.0.0/16
    set security nat static rule-set tenant-1-loc rule tenant-1-loc then static-nat prefix 10.1.0.0/16
    set security nat static rule-set tenant-1-loc rule tenant-1-loc then static-nat prefix routing-instance tenant-3
    set security nat static rule-set tenant-3-loc from zone tenant-3-trust
    set security nat static rule-set tenant-3-loc rule tenant-3-loc match source-address 10.1.0.0/16
    set security nat static rule-set tenant-3-loc rule tenant-3-loc match destination-address 10.21.0.0/16
    set security nat static rule-set tenant-3-loc rule tenant-3-loc then static-nat prefix 10.1.0.0/16
    set security nat static rule-set tenant-3-loc rule tenant-3-loc then static-nat prefix routing-instance tenant-1
    set security forwarding-process enhanced-services-mode
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-any apply-groups any-permit-log
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-any match destination-l3vpn-vrf-group tenant-1
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-limited apply-groups any-permit-log
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-limited match dynamic-application junos:SSH
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-limited match dynamic-application junos:ICMP-ECHO
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-limited match destination-l3vpn-vrf-group tenant-2
    set security policies from-zone tenant-1-trust to-zone infra policy tenant-1-limited match destination-l3vpn-vrf-group tenant-3
    set security policies from-zone infra to-zone tenant-1-trust policy tenant-1 apply-groups any-permit-log
    set security policies from-zone infra to-zone tenant-1-trust policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set security policies from-zone infra to-zone infra policy tenant-1 apply-groups any-permit-log
    set security policies from-zone infra to-zone infra policy tenant-1 match dynamic-application junos:SSH
    set security policies from-zone infra to-zone infra policy tenant-1 match dynamic-application junos:HTTP
    set security policies from-zone infra to-zone infra policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set security policies from-zone infra to-zone infra policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set security policies from-zone infra to-zone infra policy tenant-1 match destination-l3vpn-vrf-group tenant-1
    set security policies from-zone infra to-zone infra policy tenant-1 match destination-l3vpn-vrf-group tenant-2
    set security policies from-zone infra to-zone infra policy tenant-1 match destination-l3vpn-vrf-group tenant-3
    set security policies from-zone tenant-2-trust to-zone infra policy tenant-2 apply-groups any-permit-log
    set security policies from-zone tenant-2-trust to-zone infra policy tenant-2 match destination-l3vpn-vrf-group tenant-2
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-2 apply-groups any-permit-log
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-2 match source-l3vpn-vrf-group tenant-2
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-1 apply-groups any-permit-log
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-1 match dynamic-application junos:SSH
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set security policies from-zone infra to-zone tenant-2-trust policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set security policies from-zone tenant-3-trust to-zone infra policy tenant-3 apply-groups any-permit-log
    set security policies from-zone tenant-3-trust to-zone infra policy tenant-3 match destination-l3vpn-vrf-group tenant-3
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-3 apply-groups any-permit-log
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-3 match source-l3vpn-vrf-group tenant-3
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-1 apply-groups any-permit-log
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-1 match dynamic-application junos:SSH
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set security policies from-zone infra to-zone tenant-3-trust policy tenant-1 match source-l3vpn-vrf-group tenant-1
    set security policies from-zone tenant-1-trust to-zone tenant-2-trust policy tenant-1 apply-groups any-permit-log
    set security policies from-zone tenant-1-trust to-zone tenant-2-trust policy tenant-1 match dynamic-application junos:SSH
    set security policies from-zone tenant-1-trust to-zone tenant-2-trust policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set security policies from-zone tenant-1-trust to-zone tenant-3-trust policy tenant-1 apply-groups any-permit-log
    set security policies from-zone tenant-1-trust to-zone tenant-3-trust policy tenant-1 match dynamic-application junos:SSH
    set security policies from-zone tenant-1-trust to-zone tenant-3-trust policy tenant-1 match dynamic-application junos:ICMP-ECHO
    set security policies global policy cleanup-src-vrfs match source-address any
    set security policies global policy cleanup-src-vrfs match destination-address any
    set security policies global policy cleanup-src-vrfs match application any
    set security policies global policy cleanup-src-vrfs match dynamic-application any
    set security policies global policy cleanup-src-vrfs match source-l3vpn-vrf-group tenant-1
    set security policies global policy cleanup-src-vrfs match source-l3vpn-vrf-group tenant-2
    set security policies global policy cleanup-src-vrfs match source-l3vpn-vrf-group tenant-3
    set security policies global policy cleanup-src-vrfs then reject
    set security policies global policy cleanup-src-vrfs then log session-init
    set security policies global policy cleanup-dst-vrfs match source-address any
    set security policies global policy cleanup-dst-vrfs match destination-address any
    set security policies global policy cleanup-dst-vrfs match application any
    set security policies global policy cleanup-dst-vrfs match dynamic-application any
    set security policies global policy cleanup-dst-vrfs match destination-l3vpn-vrf-group tenant-1
    set security policies global policy cleanup-dst-vrfs match destination-l3vpn-vrf-group tenant-2
    set security policies global policy cleanup-dst-vrfs match destination-l3vpn-vrf-group tenant-3
    set security policies global policy cleanup-dst-vrfs then reject
    set security policies global policy cleanup-dst-vrfs then log session-init
    set security policies global policy infra description "control plane permit"
    set security policies global policy infra match source-address any
    set security policies global policy infra match destination-address any
    set security policies global policy infra match application junos-bgp
    set security policies global policy infra match application junos-icmp-ping
    set security policies global policy infra match application bfd-mhop
    set security policies global policy infra match dynamic-application any
    set security policies global policy infra match from-zone infra
    set security policies global policy infra match to-zone infra
    set security policies global policy infra then permit
    set security policies global policy infra then log session-init
    set security policies global policy infra then log session-close
    set security policies global policy infra-reject-log description "final touch"
    set security policies global policy infra-reject-log match source-address any
    set security policies global policy infra-reject-log match destination-address any
    set security policies global policy infra-reject-log match application any
    set security policies global policy infra-reject-log match dynamic-application any
    set security policies global policy infra-reject-log then reject
    set security policies global policy infra-reject-log then log session-init
    set security policies pre-id-default-policy then log session-close
    set security zones security-zone infra host-inbound-traffic system-services ping
    set security zones security-zone infra host-inbound-traffic system-services ike
    set security zones security-zone infra host-inbound-traffic protocols bgp
    set security zones security-zone infra host-inbound-traffic protocols bfd
    set security zones security-zone infra interfaces lo0.0
    set security zones security-zone infra interfaces ge-0/0/1.100
    set security zones security-zone infra interfaces st0.0
    set security zones security-zone infra enable-reverse-reroute
    set security zones security-zone tenant-1-trust tcp-rst
    set security zones security-zone tenant-1-trust interfaces ge-0/0/2.81 host-inbound-traffic system-services ping
    set security zones security-zone tenant-2-trust tcp-rst
    set security zones security-zone tenant-2-trust interfaces ge-0/0/2.82 host-inbound-traffic system-services ping
    set security zones security-zone tenant-3-trust tcp-rst
    set security zones security-zone tenant-3-trust interfaces ge-0/0/2.83 host-inbound-traffic system-services ping
    set security l3vpn vrf-group tenant-1 vrf tenant-1
    set security l3vpn vrf-group tenant-2 vrf tenant-2
    set security l3vpn vrf-group tenant-3 vrf tenant-3
    set interfaces ge-0/0/1 vlan-tagging
    set interfaces ge-0/0/1 unit 100 description underlay-phy
    set interfaces ge-0/0/1 unit 100 vlan-id 100
    set interfaces ge-0/0/1 unit 100 family inet address 10.0.0.10/24
    set interfaces ge-0/0/2 vlan-tagging
    set interfaces ge-0/0/2 unit 81 description tenant-1
    set interfaces ge-0/0/2 unit 81 vlan-id 81
    set interfaces ge-0/0/2 unit 81 family inet address 10.1.1.1/24
    set interfaces ge-0/0/2 unit 82 description tenant-2
    set interfaces ge-0/0/2 unit 82 vlan-id 82
    set interfaces ge-0/0/2 unit 82 family inet address 10.2.1.1/24
    set interfaces ge-0/0/2 unit 83 description tenant-3
    set interfaces ge-0/0/2 unit 83 vlan-id 83
    set interfaces ge-0/0/2 unit 83 family inet address 10.1.1.1/24
    set interfaces fxp0 unit 0 family inet address 172.30.193.193/24
    set interfaces lo0 unit 0 description overlay
    set interfaces lo0 unit 0 family inet address 100.65.0.1/32
    set interfaces st0 unit 0 description underlay-ipsec
    set interfaces st0 unit 0 multipoint
    set interfaces st0 unit 0 family inet address 100.70.0.1/24
    set policy-options policy-statement export-tenant-1 term 1 from route-filter 0.0.0.0/0 exact
    set policy-options policy-statement export-tenant-1 term 1 then accept
    set policy-options policy-statement export-tenant-1 term 100 then reject
    set policy-options policy-statement export-tenant-2 term 1 from route-filter 0.0.0.0/0 exact
    set policy-options policy-statement export-tenant-2 term 1 then accept
    set policy-options policy-statement export-tenant-2 term 100 then reject
    set policy-options policy-statement export-tenant-3 term 1 from route-filter 0.0.0.0/0 exact
    set policy-options policy-statement export-tenant-3 term 1 then accept
    set policy-options policy-statement export-tenant-3 term 100 then reject
    set policy-options policy-statement export-underlay term 1 from route-filter 100.65.0.1/32 exact
    set policy-options policy-statement export-underlay term 1 then accept
    set policy-options policy-statement export-underlay term 100 then reject
    set policy-options policy-statement reject-defaults term 1 from route-filter 0.0.0.0/0 exact
    set policy-options policy-statement reject-defaults term 1 then reject
    set policy-options policy-statement reject-defaults term 100 then accept
    set routing-instances common-1 instance-type virtual-router
    set routing-instances tenant-1 instance-type vrf
    set routing-instances tenant-1 routing-options rib tenant-1.inet.0 static route 0.0.0.0/0 next-table common-1.inet.0
    set routing-instances tenant-1 routing-options auto-export family inet unicast rib-group to-common-1
    set routing-instances tenant-1 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances tenant-1 protocols evpn ip-prefix-routes encapsulation vxlan
    set routing-instances tenant-1 protocols evpn ip-prefix-routes vni 1
    set routing-instances tenant-1 protocols evpn ip-prefix-routes export export-tenant-1
    set routing-instances tenant-1 interface ge-0/0/2.81
    set routing-instances tenant-1 route-distinguisher 100.65.0.1:1
    set routing-instances tenant-1 vrf-target target:65001:1
    set routing-instances tenant-2 instance-type vrf
    set routing-instances tenant-2 routing-options rib tenant-2.inet.0 static route 0.0.0.0/0 next-table common-1.inet.0
    set routing-instances tenant-2 routing-options auto-export family inet unicast rib-group to-common-1
    set routing-instances tenant-2 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances tenant-2 protocols evpn ip-prefix-routes encapsulation vxlan
    set routing-instances tenant-2 protocols evpn ip-prefix-routes vni 2
    set routing-instances tenant-2 protocols evpn ip-prefix-routes export export-tenant-2
    set routing-instances tenant-2 interface ge-0/0/2.82
    set routing-instances tenant-2 route-distinguisher 100.65.0.1:2
    set routing-instances tenant-2 vrf-target target:65001:2
    set routing-instances tenant-3 instance-type vrf
    set routing-instances tenant-3 routing-options static route 0.0.0.0/0 discard
    set routing-instances tenant-3 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances tenant-3 protocols evpn ip-prefix-routes encapsulation vxlan
    set routing-instances tenant-3 protocols evpn ip-prefix-routes vni 3
    set routing-instances tenant-3 protocols evpn ip-prefix-routes export export-tenant-3
    set routing-instances tenant-3 interface ge-0/0/2.83
    set routing-instances tenant-3 route-distinguisher 100.65.0.1:3
    set routing-instances tenant-3 vrf-target target:65001:3
    set applications application bfd-mhop term 1 protocol udp
    set applications application bfd-mhop term 1 destination-port 4784
    set protocols bgp group underlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group underlay bfd-liveness-detection multiplier 3
    set protocols bgp group underlay neighbor 10.0.0.1 description r1
    set protocols bgp group underlay neighbor 10.0.0.1 export export-underlay
    set protocols bgp group underlay neighbor 10.0.0.1 peer-as 65000
    set protocols bgp group underlay neighbor 10.0.0.1 local-as 65001
    set protocols bgp group underlay neighbor 100.70.0.2 description vsrx-left-st0
    set protocols bgp group underlay neighbor 100.70.0.2 export export-underlay
    set protocols bgp group underlay neighbor 100.70.0.2 peer-as 65002
    set protocols bgp group underlay neighbor 100.70.0.2 local-as 65001
    set protocols bgp group overlay multihop
    set protocols bgp group overlay local-address 100.65.0.1
    set protocols bgp group overlay family evpn signaling
    set protocols bgp group overlay bfd-liveness-detection minimum-interval 500
    set protocols bgp group overlay bfd-liveness-detection multiplier 5
    set protocols bgp group overlay neighbor 100.65.0.2 peer-as 65102
    set protocols bgp group overlay neighbor 100.65.0.2 local-as 65101
    set routing-options static route 0.0.0.0/0 next-hop 172.30.193.1
    set routing-options rib-groups to-common-1 import-rib common-1.inet.0
    set routing-options rib-groups to-common-1 import-policy reject-defaults

vSRX-r1


    set version 23.2R2.21
    set system host-name vsrx-r1
    set system services ssh root-login allow
    set system services ssh sftp-server
    set system services ssh client-alive-interval 120
    set system time-zone Europe/Amsterdam
    set system name-server 172.30.100.105
    set system syslog file messages any any
    set system syslog file messages archive size 5m
    set system syslog file messages archive files 5
    set system syslog file traffic any any
    set system syslog file traffic match RT_
    set system syslog file traffic archive size 1m
    set system syslog file traffic archive files 4
    set system syslog file traffic structured-data brief
    set system ntp server 172.30.100.105
    set services application-identification
    set security log mode stream-event
    set security log report
    set security alg dns disable
    set security alg ftp disable
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
    set security flow tcp-session no-syn-check
    set security flow tcp-session no-sequence-check
    set security flow power-mode-disable
    set security forwarding-process enhanced-services-mode
    set security policies global policy all match source-address any
    set security policies global policy all match destination-address any
    set security policies global policy all match application any
    set security policies global policy all then permit tunnel-inspection insp-prof-1
    set security policies policy-set pol-set-1 policy reject-some match source-address any
    set security policies policy-set pol-set-1 policy reject-some match destination-address any
    set security policies policy-set pol-set-1 policy reject-some match application any
    set security policies policy-set pol-set-1 policy reject-some match dynamic-application junos:HTTP
    set security policies policy-set pol-set-1 policy reject-some then reject
    set security policies policy-set pol-set-1 policy reject-some then log session-init
    set security policies policy-set pol-set-1 policy permit-all match source-address any
    set security policies policy-set pol-set-1 policy permit-all match destination-address any
    set security policies policy-set pol-set-1 policy permit-all match application any
    set security policies policy-set pol-set-1 policy permit-all match dynamic-application any
    set security policies policy-set pol-set-1 policy permit-all then permit
    set security policies policy-set pol-set-1 policy permit-all then log session-close
    set security zones security-zone all host-inbound-traffic system-services ping
    set security zones security-zone all host-inbound-traffic protocols bgp
    set security zones security-zone all host-inbound-traffic protocols bfd
    set security zones security-zone all interfaces ge-0/0/0.101
    set security zones security-zone all interfaces ge-0/0/1.100
    set security tunnel-inspection inspection-profile insp-prof-1 vxlan pol-set-1 policy-set pol-set-1
    set security tunnel-inspection inspection-profile insp-prof-1 vxlan pol-set-1 vni any
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 101 description left
    set interfaces ge-0/0/0 unit 101 vlan-id 101
    set interfaces ge-0/0/0 unit 101 family inet address 10.0.1.1/24
    set interfaces ge-0/0/1 vlan-tagging
    set interfaces ge-0/0/1 unit 100 description right
    set interfaces ge-0/0/1 unit 100 vlan-id 100
    set interfaces ge-0/0/1 unit 100 family inet address 10.0.0.1/24
    set interfaces fxp0 unit 0 family inet address 172.30.100.192/24
    set policy-options policy-statement export-hub term 1 from interface ge-0/0/0.101
    set policy-options policy-statement export-hub term 1 then accept
    set policy-options policy-statement export-hub term 2 from route-filter 100.65.0.0/16 orlonger
    set policy-options policy-statement export-hub term 2 then accept
    set policy-options policy-statement export-hub term 100 then reject
    set policy-options policy-statement export-spokes term 1 from interface ge-0/0/1.100
    set policy-options policy-statement export-spokes term 1 then accept
    set policy-options policy-statement export-spokes term 2 from route-filter 100.65.0.0/16 orlonger
    set policy-options policy-statement export-spokes term 2 then accept
    set policy-options policy-statement export-spokes term 100 then reject
    set routing-instances vr instance-type virtual-router
    set routing-instances vr protocols bgp group underlay bfd-liveness-detection minimum-interval 500
    set routing-instances vr protocols bgp group underlay bfd-liveness-detection multiplier 3
    set routing-instances vr protocols bgp group underlay neighbor 10.0.1.10 export export-spokes
    set routing-instances vr protocols bgp group underlay neighbor 10.0.1.10 peer-as 65002
    set routing-instances vr protocols bgp group underlay neighbor 10.0.1.10 local-as 65000
    set routing-instances vr protocols bgp group underlay neighbor 10.0.0.10 export export-hub
    set routing-instances vr protocols bgp group underlay neighbor 10.0.0.10 peer-as 65001
    set routing-instances vr protocols bgp group underlay neighbor 10.0.0.10 local-as 65000
    set routing-instances vr interface ge-0/0/0.101
    set routing-instances vr interface ge-0/0/1.100
    set routing-options static route 0.0.0.0/0 next-hop 172.30.100.1

### Useful links

  * [https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/concept/evpn-route-type5-understanding.html](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/concept/evpn-route-type5-understanding.html "https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/concept/evpn-route-type5-understanding.html")
  * [https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-vxlan-support-srx-series.html](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-vxlan-support-srx-series.html "https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/topics/topic-map/evpn-vxlan-support-srx-series.html")
  * [https://www.juniper.net/documentation/us/en/software/junos/nat/index.html](https://www.juniper.net/documentation/us/en/software/junos/nat/index.html "https://www.juniper.net/documentation/us/en/software/junos/nat/index.html")
  * [https://www.debian.org/distrib/](https://www.debian.org/distrib/ "https://www.debian.org/distrib/")
  * [https://lwn.net/Articles/580893/](https://lwn.net/Articles/580893/ "https://lwn.net/Articles/580893/")

### Glossary

  * BGP Border Gateway Protocol

  * ESP Encapsulating Security Payload

  * EVPN Ethernet VPN

  * GRE Generic Routing Encapsulation

  * HTTP Hyper Text Transfer Protocol

  * ICMP Internet Control Message Protocol

  * IKE Internet Key Exchange

  * IPSEC IP security

  * MPLS Multi-Protocol Layer Switching

  * MSS Maximum Segment Size

  * MTU Maximum Transmission Unit

  * NAT Network Adress Translation

  * PMTU Path Maximum Transmission Unit

  * SA Security Association

  * SSH Secure Shell

  * TCP Transmission Control Protocol

  * UDP User Datagram Protocol

  * VNI Virtual Network Identifier

  * VRF Virtual Routing Forwarding

  * VXLAN Virtual Extensible LAN

  * WAN Wide Area Network

### Acknowledgements

All the brilliant people who have been involved in the exploration of SRX EVPN/VXLAN Type 5 since the early days, namely: Mark Barrett, Ben Griffin, Damian Holdcroft, Pawel Kocimowski, Matthijs Nagel, Teddy Nicoghosian, Elisabeth Rodrigues, and Thorbjoern Zieger. A special shoutout goes to Mark and Matthijs for reviewing and providing valuable feedback. Finally, kudos to Juniper SRX engineering and product line management for pushing the envelope.

### Comments

If you want to reach out for comments, feedback or questions, drop us a mail at:

### Revision History

**Version** | **Author(s)** | **Date** | **Comments**
---|---|---|---
1 |  Karel Hendrych | May2024 | Initial Publication

[](https://community.juniper.net/home/techpost "Back to main page")


[#SolutionsandTechnology](https://community.juniper.net/search?s=tags%3A%22Solutions and Technology%22&executesearch=true)
[#SRXSeries](https://community.juniper.net/search?s=tags%3A%22SRX Series%22&executesearch=true)

0 comments

105 views

##  Permalink

https://community.juniper.net/blogs/karel-hendrych/2024/05/27/srx-evpnvxlan-t5-oipsec

© 2025 Hewlett Packard Enterprise Development LP

[Powered by Higher Logic](http://www.higherlogic.com)
