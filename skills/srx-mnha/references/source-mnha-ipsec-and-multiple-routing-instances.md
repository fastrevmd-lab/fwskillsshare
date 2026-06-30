# MNHA IPSec and Multiple Routing Instances

Source: https://community.juniper.net/blogs/james-rathbun/2026/03/30/mnha-ipsec-and-multiple-routing-instances?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3
Author: James Rathbun
Retrieved: 2026-05-14

## Extracted Article Text

INET.0 - What? MNHA, IPSec and Multiple Routing Instances
Introduction
There is a lot of good documentation available on designing and implementing MultiNode High Availability (MNHA) and Virtual Private Networks (VPNs) on SRXs - even AI generated configuration snippets that might lead a novice or experience professional astray. AI is a wonderful tool, but who hasn't been a little frustrated by some AI output that includes commands or configuration recommendations that aren't available on the platform.
This post is not intended to be a 100% exhaustive guide on designing or configuring MNHA or VPNs with SRX deployments. The goal is to provide working solutions with explanations and call-out caveats relative to MNHA as well as with VPN deployments. Starting with a review of the fundamentals, then building to common deployments for remote access and site-to-site VPNs with a more holistic, integrated focus, not just spot configurations.
Of course, it goes without saying, "Mileage varies...". The examples may fit some potential uses cases well, however, there may also be additional complexities not optimal for certain production environments. This content is intended to align with a planning motion to aid in understanding aspects of MNHA related to common IPSec implementations. When in doubt, document, document, document and follow one of the best design principles - keep the design as simple as possible to meet the requirements without adding undue complexity.
The figure below will represent the high-level topology- incorporating a pair of SRX with two different ISP connections and an Extranet (or partner) connection.
Figure 1. 10,000ft view
Focus will be centric considering flows and impacts incorporating diverse upstream providers and redundant ISP connections creating the classic "bow-tie" design. Initially this added level of redundancy may seem appealing, from a routing, connectivity point of view. SRXs deployed as security devices have more rigid requirements when processing flows than just routing packets. When you get to the "Keeping it Simple" section, with the topology we'll discuss, you'll probably realize that those extra redundant connections are just for show, added complexity and no real function. During that journey from here to there, the main topics and observations that will be covered throughout include:
SRX Fundamentals
Inclusion of multiple routing instances
MNHA
ICD and Asymmetric flows
Network Address Translations (NAT) implications
IPSec VPNs
This post assumes familiarity with MNHA fundamentals. If you're new to MNHA or need a refresher, do yourself a favor and read these first - in order:
1.
Multi-Node High Availability Basics
: Steven Jacques covers the foundational concepts: ICL mechanics, SRG0, Active/Warm session synchronization, and config sync via Junos groups. If those terms aren't familiar, start here.
2.
Hybrid MNHA with eBGP
: covers hybrid deployment mode, BFD-driven failover, signal routes, and MED-based BGP traffic engineering. The topology in this post builds directly on those concepts.
3.
SRX clustering: from Chassis Cluster to MultiNode High Availability
: Laurent Paumelle's architectural overview of MNHA modes, SRG taxonomy, and platform support. Good context if you're evaluating MNHA or migrating from Chassis Cluster.
This post doesn't repeat what those cover. The intent is to build on them, not restate them. Consider this your homework assignment before diving in.
Foundations
It's imperative to have a strong grasp of the basic building blocks of the SRX beyond security policies to have a successful MNHA deployment. While it may seem obvious in certain green-field deployments, migrating or adding MNHA in an existing deployment may provide some challenges and potential redesign to glean the benefits.
The topology used represents a pair of MNHA clustered SRX in the center with two northbound connections to separate ISP providers where hosts will use remote access VPN, a protected "DMZ" and internal subnets, south bound connections to additional internal networks including Extranet/partner site-to-site VPN connections.
Figure 2. High Level Topology Diagram
For readability, in-line example configurations may omit additional statements. Refer to complete configurations located at the end of this post.
SRX
Interfaces are mapped to security zones.
Interfaces also map to routing instances.
You cannot have an interface assigned to more than one zone or routing instance. This includes loopback interfaces.
Why is this an important? Consider if you have multiple routing-instances and you want to configure MNHA, leveraging a loopback interface as your external interface for anchoring VPNs. The concept of IKE Gateway lookups is from the perspective where the Inter Chassis Link (ICL), what routing instance, it is configured in. More on this later...
Mapping routing instances (RI), security zones (SZ) and interfaces (INT) in Figure 3 may seem like excessive segmentation but the level segmentation used is to highlight operational dependencies and flexibility.
Figure 3. RI, SZ, INT Mapping
Interfaces
Reiterating, the purpose of this post is to illustrate features/functionality and doesn't constitute best practices for network design/placement of organizational elements or resources. Explanation of the interfaces and function for the lab simulation follows:
Public (ISP) connections:
GE-0/0/1 - L3 ISP-1 connection with single-hop BGP peering (192.168.99.0/24).
GE-0/0/2 - L3 ISP-2 connection with multi-hop BGP peering (192.168.98.0/24).
Private "DMZ" subnets - directly connected to the SRXs without any additional L3 hops.
GE-0/0/0 - Source NAT pools required to reach public resources (192.168.252.0/24).
GE-0/0/3 - Static NAT required for access from public or private connections (192.168.97.0/24).
Additional private internal connections. Routed connectivity representing a larger internal network. This is where connectivity for the site-to-site VPNs exists.
GE-0/0/4 - L3 BGP connected (192.168.251.0/25 (SRX-A) and 192.168.251.128/25 (SRX-B))
MNHA
GE-0/0/5 - ICL (100.64.0.0/27)
GE-0/0/6 - ICD (100.64.10.0/27)
It is recommended to use redundancy for the ICL/ICD interfaces. These L3 interfaces are not required to be directly connected. In this topology, they are simply directly connected single interfaces providing L3 functionality between the two SRXs.
Secure Tunnel Interfaces
ST0.100 - supporting remote access VPN connections.
ST0.200 - Site-to-Site (S2S) VPN
Loopback interfaces
Loopback0.0 - used for self-traffic originating default traffic from inet0. Unique per SRX:
10.0.0.33/32 = SRX-A
10.0.0.44/32 = SRX-B
Loopback0.2 - used for eBGP multi-hop peering from SRX-A to ISP-2 - 10.12.12.12/32.
Loopback0.10 - multi-purpose, primarily used for "floating-IP" addresses used with MNHA and eBGP peering. Floating addresses are configured identically on both SRXs.
10.13.13.13/32 - used for eBGP multi-hop peering from SRX-B to ISP-2
203.0.113.100/32 - used for anchoring remote access VPN connections
10.165.251.200/32 - used for anchoring site-to-site VPN connection(s).
For those unfamiliar with loopback interfaces in JUNOS - the loopback interface is a logical interface. It appears to the system that only one loopback interface available - Loopback0; unlike other platforms where you can create many logical loopback interfaces, assigning them different identifiers and associated IP addresses. To achieve similar results with the SRX, you carve up the loopback interface with different unit numbers - e.g. sub-interfaces. You can assign multiple IP addresses to each of the different units. However, only 1 loopback (sub-interface) can be configured in a routing-instance (1:1 relationship).
Interface configurations for MNHA-VSRX-A
set interfaces ge-0/0/0 unit 0 description INT
set interfaces ge-0/0/0 unit 0 family inet address 192.168.252.9/24
set interfaces ge-0/0/1 unit 0 description ISP-1_UPLINK
set interfaces ge-0/0/1 unit 0 family inet address 192.168.99.9/24
set interfaces ge-0/0/2 unit 0 description ISP-2_UPLINK
set interfaces ge-0/0/2 unit 0 family inet address 192.168.98.9/24
set interfaces ge-0/0/3 unit 0 description DMZ
set interfaces ge-0/0/3 unit 0 family inet address 192.168.97.9/24
set interfaces ge-0/0/4 unit 0 description EXTRANET _RTR-A
set interfaces ge-0/0/4 unit 0 family inet address 192.168.251.1/25
set interfaces ge-0/0/5 description MNHA-ICL
set interfaces ge-0/0/5 unit 0 family inet address 100.64.0.9/27
set interfaces ge-0/0/6 description MNHA-ICD
set interfaces ge-0/0/6 unit 0 family inet address 100.64.10.9/27
set interfaces lo0 unit 0 description SRX-SERVICES_SELF-TRAFFIC
set interfaces lo0 unit 0 family inet address 10.0.0.33/32
set interfaces lo0 unit 2 description EBGP-MH-ISP-2
set interfaces lo0 unit 2 family inet address 10.12.12.12/32
set interfaces lo0 unit 10 description PROD_LOOPBACKS
set interfaces lo0 unit 10 family inet address 10.165.251.200/32
set interfaces lo0 unit 10 family inet address 203.0.113.100/32
set interfaces lo0 unit 10 family inet address 10.165.251.222/32
set interfaces st0 unit 100 description REMOTE_ACCESS_VPN
set interfaces st0 unit 100 family inet mtu 1420
set interfaces st0 unit 200 description SITE-TO-SITE-VPN_PROD
set interfaces st0 unit 200 family inet mtu 1420
Interface configurations for MNHA-VSRX-B:
set interfaces ge-0/0/0 unit 0 description INT
set interfaces ge-0/0/0 unit 0 family inet address 192.168.252.10/24
set interfaces ge-0/0/1 unit 0 description ISP-1_UPLINK
set interfaces ge-0/0/1 unit 0 family inet address 192.168.99.10/24
set interfaces ge-0/0/2 unit 0 description ISP-2_UPLINK
set interfaces ge-0/0/2 unit 0 family inet address 192.168.98.10/24
set interfaces ge-0/0/3 unit 0 description DMZ
set interfaces ge-0/0/3 unit 0 family inet address 192.168.97.10/24
set interfaces ge-0/0/4 unit 0 description EXTRANET_RTR-B
set interfaces ge-0/0/4 unit 0 family inet address 192.168.251.129/25
set interfaces ge-0/0/5 description MNHA-ICL
set interfaces ge-0/0/5 unit 0 family inet address 100.64.0.10/27
set interfaces ge-0/0/6 description MNHA-ICD
set interfaces ge-0/0/6 unit 0 family inet address 100.64.10.10/27
set interfaces lo0 unit 0 description SRX-SERVICES_SELF-TRAFFIC
set interfaces lo0 unit 0 family inet address 10.0.0.44/32
set interfaces lo0 unit 10 description PROD_LOOPBACKS
set interfaces lo0 unit 10 family inet address 10.165.251.200/32
set interfaces lo0 unit 10 family inet address 203.0.113.100/32
set interfaces lo0 unit 10 family inet address 10.13.13.13/32
set interfaces lo0 unit 10 family inet address 10.165.251.222/32
set interfaces st0 unit 100 description REMOTE_ACCESS_VPN
set interfaces st0 unit 100 family inet mtu 1420
set interfaces st0 unit 200 description SITE-TO-SITE-VPN_PROD
set interfaces st0 unit 200 family inet mtu 1420
Security Zones
Security zones form logical groups that we associate with security policies to provide granular protections. Security zones are especially important when creating VPNs and anchoring them with floating IPs (loopback interfaces). Why? Because the loopback interface and the physical interface used for the VPN connections are required to be in the same security zone. Additional details provided in the VPN section.
For this environment, let's clarify the EXT and EXT-1 | 2 variant zones. The EXT-1 and EXT-2 security zones are 100% associated with our ISP traffic; no other interfaces explicitly configured other than required for connectivity via the ISP uplinks. Not the case with the EXT zone. There is a constraint of having the floating-ip for anchoring VPN connections to be in the same RI as the MNHA ICL link as well as an additional constraint of having the loopback and physical interfaces for VPN terminations to be the same zone.
Figure 4. EXT, EXT-1 and EXT-2 Security Zones
There is no requirement to have different zone names between the variant EXT-1 and EXT-2 zones, for illustration purposes only, the security zones EXT-1 align with "ISP-1" and EXT-2 with "ISP-2". A variation could be something like ALT-ISP(RI) and ALT-ISP(SZ) on both SRXs.
Security Zone Configurations:
MNHA-VSRX-A & MNHA-VSRX-B
set security zones functional-zone management
set security zones security-zone INT interfaces ge-0/0/0.0
set security zones security-zone RA-VPN interfaces st0.100
set security zones security-zone DMZ interfaces ge-0/0/3.0
set security zones security-zone HA-ICL interfaces ge-0/0/5.0
set security zones security-zone HA-ICD interfaces ge-0/0/6.0
set security zones security-zone
EXT
interfaces ge-0/0/4.0
set security zones security-zone
EXT
interfaces lo0.10
set security zones security-zone VPN-1 interfaces st0.200
MNHA-VSRX-A
set security zones security-zone
EXT
interfaces ge-0/0/1.0
set security zones security-zone
EXT-2
interfaces ge-0/0/2.0
set security zones security-zone
EXT-2
interfaces lo0.2
MNHA-VSRX-B
set security zones security-zone EXT interfaces ge-0/0/2.0
set security zones security-zone
EXT-1
interfaces ge-0/0/1.0
Routing Instances
Routing instances create isolated Layer 3 routing constructs. Common use cases include segmentation methods for overlapping/duplicate IP addresses, multi-tenancy, and macro segmentation for different networks. You may want to just keep it simple and have a single routing table (e.g. inet0) for all forwarding decisions.
Figure 5. RI Logical Representation
Mgmt_junos is to isolate management traffic from other traffic types; doesn't support transit traffic. Inet0 is used for self-traffic by default. Connecting to services for antimalware, antivirus, DNS queries, etc. By default, all traffic is permitted in and out of the junos-host zone that passes the host-inbound-traffic settings applied to each security zone. Additional security policies specifying junos-host as a source or destination zone can be applied for additional security controls.
set system management-instance
HA-ICD - separates the ICD traffic from other routing instances.
PROD - routing table supports most of the interfaces and security zones including one of the two ISP connections. ISP connections are L3 separated for control and support for NAT scenarios.
VPN - additional RIs like VPN aren't a requirement to keep flows isolated while crossing security zones. This is easily accomplished with applicable security policies.
ISP-1/ISP-2 - discrete routing tables used for connecting with ISP-1 or ISP-2.
Routing Instance Configurations
MNHA-VSRX-A & MNHA-VSRX-B
set routing-instances mgmt_junos description MANAGEMENT_VRF
set routing-instances HA-ICD instance-type virtual-router
set routing-instances HA-ICD interface ge-0/0/6.0
set routing-instances PROD instance-type virtual-router
set routing-instances PROD interface ge-0/0/0.0
set routing-instances PROD interface ge-0/0/3.0
set routing-instances PROD interface ge-0/0/4.0
set routing-instances PROD interface lo0.10
set routing-instances PROD interface st0.100
set routing-instances VPN interface st0.200
MNHA-VSRX-A
set routing-instances PROD interface ge-0/0/1.0
set routing-instances ISP-2 instance-type virtual-router
set routing-instances ISP-2 interface ge-0/0/2.0
set routing-instances ISP-2 interface lo0.2
MNHA-VSRX-B
set routing-instances PROD interface ge-0/0/2.0
set routing-instances ISP-1 instance-type virtual-router
set routing-instances ISP-1 interface ge-0/0/1.0
set routing-instances ISP-1 interface lo0.1<
VPN
There is plenty of great documentation for the myriad of configuration settings available under the VPN umbrella. With that said, here is a high-level review of the basic steps required to configure IPSec VPNs on SRX:
Reviewing the steps required to configure IPSec VPNs on SRX:
1. Interfaces and Security Zones
2. Phase 1, IKE Proposals, IKE Policies and IKE Gateway (external interface)
3. Phase 2, IPSec Proposals, IPSec Policies, binding VPN tunnel interface (ST0) and IKE gateway, and specifying interesting
traffic to route and encrypt across the tunnel.
4. Authentication, Address Pools, etc.
5. Security Policies
Figure 6. RI, SZ, Interface relationships
The primary point to convey relating to VPN with MNHA, is the relationship of the floating IP and consideration of routing instances. Previous sections covered the correlation with physical interfaces, security zones and routing instances. The same applies to the external interfaces used with VPNs.
When using multiple routing instances, understanding the relationships and dependencies for successful tunnel establishment is critical. Obviously, the physical interface is the point at which packets are sent and received between our tunnel endpoints. In non-MNHA deployments, the physical interface can also be the external interface. IKE negotiations occur with the external interface, as such, the VPN is essentially being terminated or anchored on the loopback interface.
With MNHA (synced tunnels), the external interface needs to have the capability to be serviced by either node in the cluster, dependent on which is active - a "floating IP address". The floating IP is assigned to a loopback interface, subsequently advertised towards the external network(s) to anchor the tunnel. In this scenario, there are two configuration requirements due to internal packet processing from a physical interface to a loopback interface.
1) The loopback interface and the external physical interface used in the VPN configuration for the gateway
must
be configured in the same security zone. The below flow traceoptions exhibits the behavior if the loopback interface and the physical interface are in different security zones.
'external-interface'(lo0.10) and 'routing-interface'(ge-0/0/4.0) belong to different zones.
Re-route failed, pkt dropped
.
unable to make the tunnel ready
2) An intra-zone security policy
must
allow for both IKE and ESP traffic to allow the IPSec tunnel to build.
set security policies from-zone EXT to-zone EXT policy IKE-ESP match source-address H10.177.177.77
set security policies from-zone EXT to-zone EXT policy IKE-ESP match destination-address H10.165.251.200
set security policies from-zone EXT to-zone EXT policy IKE-ESP match application junos-ike
set security policies from-zone EXT to-zone EXT policy IKE-ESP match application ESP
set security policies from-zone EXT to-zone EXT policy IKE-ESP then permit
How do we get IKE packets to and from the SRX to build the tunnel? The answer seems straightforward... but it's not just a reachability answer. The IKE gateway lookup process is centric with the external interface and its associated routing instance. Include MNHA and we need to consider that the external interface (the floating IP) MNHA is tracking, is also associated with a routing instance. These two routing instances need to be the same. MNHA's perspective routing instance is from where the Inter Chassis Link (ICL) is configured.
Route leaking between two different instances isn't viable in the situation where the ICL and the floating IP-based loopback are in different routing instances.
The IKE gateway lookup is a control plane operation. While data plane flows can leverage route leaking to forward transit traffic across L3 boundaries, the IKE daemon initiates or responds to packets based on "local" routes (IPs configured directly on interfaces within that instance). It bypasses imported routes from other instances for this type of self-traffic decision. The floating IP and the ICL's management context need to be aligned within the same routing table to maintain session state and synchronization.
MNHA
Common acronyms and terms with basic definitions used in MNHA deployments below are for orientation.
Inter Chassis Link (ICL) - to synchronize state (RTO - Real Time Objects) for stateful failover, health/status check.
Inter Chassis Datapath (ICD) - to support asymmetric traffic flows.
Service Redundancy Group (SRG) - is a logical grouping that can be selectively serviced based upon node priority.
Activeness - concept of priority, which node is going to be the active node for a given SRG (higher priority is preferred).
Signal Routes - routes installed (locally significant) based on node priority (activeness) to trigger conditional route advertisements.
Conditional Route Advertisements - the basis for steering traffic to the active node, tightly coupled with signal routes.
An easy rule o f thumb for initial provisioning of an encrypted ICL is 1 Gbps per 100,000 concurrent sessions.
RTOs for session synchronization include session creation, session deletion, TCP state changes and additional request and response messaging. The minimum RTO message size is 320 bytes; with encapsulation and encryption overhead each RTO is approximately 400 bytes. A typical TCP session lifecycle generates 5-7 RTOS - accounting for session open,
state changes, and close.
Factor in MNHA control heartbeats, IKEv2 keepalives, and potential retransmissions. New session establishment rate (connections per second) contributes burst overhead above the sustained concurrent session baseline - maintain ICL utilization below 75% to preserve headroom for post-failover resync and CPS bursts
Figure 7. MNHA Operational Modes
MNHA Operational Modes
Layer 3 (L3) Mode - provides stateful security for through traffic; no "directly" connected L2 resources or resources that use the SRX for a gateway. Conditional route advertisements are key.
Default Gateway Mode - provides "directly" connected L2 resources via a VIP function like any First Hop Redundancy Protocol (e.g. VRRP).
Hybrid Mode - combination of L3 and Default Gateway modes; when we want to associate (influence) traffic flows to the node that is actively for a VIP.
Floating IP - An IP prefix on a loopback interface within a designated routing instance, used as the external interface for IKE gateway configurations and as the source for SRG activeness probes in L3 deployments. IKE gateway lookup, activeness probe resolution, and BGP conditional advertisement all resolve against the routing instance in which this prefix resides - mismatches will result in lookup failures.
I like to think of the floating IP as it's used with MNHA deployments more as an anycast IP versus a floating IP; the same (duplicate) IP address assigned to both nodes and advertised towards the network.  Where a floating IP address is more of a single IP that shifts between nodes as in any first hop redundancy protocol (FHRP) or a virtual IP (VIP) typically leveraging some GARP-like mechanism to update L2 tables.
Though, unlike other anycast solutions, we use traffic steering methods and map activeness to a node to use for a specific function.  Versus, either node can process ingress traffic and apply the function based on which node receives it (e.g anycast Rendezvous Point in Multicast/PIM networks).
Documentation references floating IPs - so we'll stick with that to avoid confusion.
Specific requirements when configuring IPSec with MNHA:
Install new IKE package
Must use SRG1+
Identify IPSEC as a managed service
Floating Address(es)
Process packets on backup node (optional)
Installing the new IKE package with the following exec command you can validate the IKE process versus prior KMD process:
request system software add optional://junos-ike.tgz
MNHA
show system processes | grep ike
14228  -  S        0:03.17 /usr/sbin/ikemd -N
14236  -  R       14:57.15 /usr/sbin/iked -N
Non MNHA
show system processes | grep kmd
9875  -  S        0:23.72 /usr/sbin/kmd -N
Beginning with the base MNHA configurations, identify local and remote peers, BFD detection, and encrypt the ICL with a VPN profile. Also, the routing instance and interface where the peering between the two nodes will occur for the
ICL
link.
MNHA-VSRX-A
set chassis high-availability local-id 1
set chassis high-availability local-id local-ip 100.64.0.9
set chassis high-availability peer-id 2 peer-ip 100.64.0.10
set chassis high-availability peer-id 2 interface ge-0/0/5.0
set chassis high-availability peer-id 2
routing-instance PROD
set chassis high-availability peer-id 2 vpn-profile ICL
set chassis high-availability peer-id 2 liveness-detection minimum-interval 400
set chassis high-availability peer-id 2 liveness-detection multiplier 5
MNHA-VSRX-B
set chassis high-availability local-id 2
set chassis high-availability local-id local-ip 100.64.0.10
set chassis high-availability peer-id 1 peer-ip 100.64.0.9
set chassis high-availability peer-id 1 interface ge-0/0/5.0
set chassis high-availability peer-id 1
routing-instance PROD
set chassis high-availability peer-id 1 vpn-profile ICL
set chassis high-availability peer-id 1 liveness-detection minimum-interval 400
set chassis high-availability peer-id 1 liveness-detection multiplier 5
Selecting the operational mode for your MNHA deployment is straightforward. Start with the question - What resources am I providing secure connectivity between? The VPN scenarios we're working with require connectivity with destinations protected by the SRX in the DMZ and INT zones. These destination resources use a VIP as their gateway. We want to keep symmetric flows (conditional route advertisements) between the VPN sources and the VIPs. The answer is hybrid-mode.
We can configure a single SRG to support both RA and S2S VPN connections, but we will be using two SRGs to further delve into potentials when supporting multiple SRGs; creating specific SRG based on VPN function/type (SRG1 for S2S and SRG2 for RA).
The next question then, is there a need for independent failover capability? Meaning if there were an event impacting either the RA-VPN connectivity or S2S VPN, do we trigger a holistic failover that shifts both groups of traffic over to the backup node as well or just the impacted group? Using multiple SRGs can create disparity between the active nodes - SRX-A active for SRG1 and SRX-B active for SRG2, or vice-versa - where traffic for a given session ingresses one node and egresses the other. Describing this cross-node forwarding pattern as a Z-mode (or Z-mode like) flow is distinct and entirely different from the Z-mode behavior in Chassis Cluster.
The testing in the following sections uses simple 5-tuple security policies without advanced inspection services (plugin inspections); under these conditions ICD will forward asymmetric packets and sessions will survive without impact. Where advanced inspection services are applied, sustained Z-mode flows from SRG activeness disparity are not a supported steady-state design - plugin inspection requires complete bidirectional flow visibility on a single node and session failures will result. During failover events ICD provides transient forwarding while routing converges; established long-lived sessions are typically tolerant of his window regardless of policy type. Traffic engineering should ensure complete flows traverse a single active node under steady-state conditions when advanced services are in policy.
We cannot have the same VIP configured in multiple SRGs. A simpler deployment using a single SRG to support both RA and S2S VPN is entirely valid; the two-SRG design here is used deliberately to explore independent failover capability and the behavioral differences between SRG configurations. SRG1 is configured in L3 mode for site-to-site VPNs. SRG2 is configured in hybrid mode - this describes how northbound ISP connectivity is handled, not where the RA tunnels terminate. In both cases, floating IPs on loopback interfaces anchor the tunnel endpoints; no VIP is used for tunnel termination. The distinction between L3 and hybrid mode determines how traffic is steered to the active node northbound, not where the tunnels terminate. MNHA accomplishes this steering through SRG-specific prefix lists and conditional route advertisements.
SRG-1 (L3 Mode) configuration
MNHA-VSRX-A & B
set policy-options prefix-list IKE-GW-VPN-1
10.165.251.200/32
set chassis high-availability services-redundancy-group 1 deployment-type routing
set chassis high-availability services-redundancy-group 1 activeness-probe dest-ip 192.168.251.2
set chassis high-availability services-redundancy-group 1 activeness-probe dest-ip src-ip 192.168.251.1
set chassis high-availability services-redundancy-group 1 monitor interface ge-0/0/4
set chassis high-availability services-redundancy-group 1 active-signal-route 169.254.200.1
set chassis high-availability services-redundancy-group 1 backup-signal-route 169.254.200.2
set chassis high-availability services-redundancy-group 1 prefix-list
IKE-GW-VPN-1
routing-instance PROD
set chassis high-availability services-redundancy-group 1
managed-services ipsec
set chassis high-availability services-redundancy-group 1 process-packet-on-backup
MNHA-VSRX-A
set chassis high-availability services-redundancy-group 1 peer-id 2
set chassis high-availability services-redundancy-group 1 activeness-priority 200
MNHA-VSRX-B
set chassis high-availability services-redundancy-group 1 peer-id 1
set chassis high-availability services-redundancy-group 1 activeness-priority 100
SRG-2 (Hybrid) configuration:
MNHA-VSRX-A & B
set policy-options prefix-list IKE-GW-RA-VPN
203.0.113.100/32
set chassis high-availability services-redundancy-group 2 deployment-type hybrid
set chassis high-availability services-redundancy-group 2 virtual-ip 1 ip 192.168.97.1/24
set chassis high-availability services-redundancy-group 2 virtual-ip 1 interface ge-0/0/3.0
set chassis high-availability services-redundancy-group 2 virtual-ip 2 ip 192.168.252.1/24
set chassis high-availability services-redundancy-group 2 virtual-ip 2 interface ge-0/0/0.0
set chassis high-availability services-redundancy-group 2 active-signal-route 169.254.200.3
set chassis high-availability services-redundancy-group 2 backup-signal-route 169.254.200.4
set chassis high-availability services-redundancy-group 2
prefix-list IKE-GW-RA-VPN
routing-instance PROD
set chassis high-availability services-redundancy-group 2
managed-services ipsec
set chassis high-availability services-redundancy-group 2 process-packet-on-backup
MNHA-VSRX-A
set chassis high-availability services-redundancy-group 2 monitor interface ge-0/0/1
set chassis high-availability services-redundancy-group 2 peer-id 2
set chassis high-availability services-redundancy-group 2 activeness-priority 200
MNHA-VSRX-B
set chassis high-availability services-redundancy-group 2 monitor interface ge-0/0/2
set chassis high-availability services-redundancy-group 2 peer-id 1
set chassis high-availability services-redundancy-group 2 activeness-priority 100
Asymmetric Flows with ICD
As of version 23.4R1, MNHA supports an ICD to additionally support asymmetric traffic flows. Not all packets associated with an asymmetric traffic flow are required to traverse the ICD. The ICD is engaged during initial TCP 3-Way handshake (Figure 8) and remains active until all content security plugins (advanced inspection services) have completed evaluation and detached from the session. Once plugins detach and no advanced services require continued full-flow visibility, the synchronized session can transition from warm to active on the receiving node, and subsequent packets are processed locally without ICD forwarding.
Examples presented walk through ingress flows, the same behavior is exhibited for egress flows.
The flows evaluated with either ICD or without ICD matched a traditional 5-tuple security policy without application ID or any other advanced security services applied:
set security policies from-zone XXX to-zone YYY policy POL-NAME match source-address any
set security policies from-zone XXX to-zone YYY policy POL-NAME match destination-address any
set security policies from-zone XXX to-zone YYY policy POL-NAME match application any
set security policies from-zone XXX to-zone YYY policy POL-NAME then permit
set security policies from-zone XXX to-zone YYY policy POL-NAME then log session-init
set security policies from-zone XXX to-zone YYY policy POL-NAME then count
When an ICD is configured, Application Tracking is one of those features where the SRX wants visibility for end-to-end flows.
ICD configuration:
MNHA-VSRX-A
set chassis high-availability local-id local-forwarding-ip 100.64.10.9
set chassis high-availability peer-id 2 peer-forwarding-ip 100.64.10.10
set chassis high-availability peer-id 2 peer-forwarding-ip interface ge-0/0/6.0
set chassis high-availability peer-id 2 peer-forwarding-ip liveness-detection minimum-interval 400
set chassis high-availability peer-id 2 peer-forwarding-ip liveness-detection multiplier 5
MNHA-VSRX-B
set chassis high-availability local-id local-forwarding-ip 100.64.10.10
set chassis high-availability peer-id 1 peer-forwarding-ip 100.64.10.9
set chassis high-availability peer-id 1 peer-forwarding-ip interface ge-0/0/6.0
set chassis high-availability peer-id 1 peer-forwarding-ip liveness-detection minimum-interval 400
set chassis high-availability peer-id 1 peer-forwarding-ip liveness-detection multiplier 5
Two basic asymmetrical flows are highlighted, neither of which use any NAT functionality. A ping test from a remote access VPN tunnel and an SSH connection. The ICMP test will demonstrate classic Z-mode connectivity, while the SSH connection is for connectivity not directly connected to the SRXs.
Ping, ICMP, isn't synchronized between the two nodes by default; most use cases don't require it. For testing purposes, we've enabled synchronization to more easily validate packets traversing the ICD.
set security flow allow-embedded-icmp
set security flow sync-icmp-session
With SRX-B active for the SRG, we explicitly configure the gateway on a target host (192.168.97.99) to SRX-A creating an asymmetrical (Z-Mode) flow. This same Z-Mode behavior is relative to other traffic flows, not just ICMP. ICMP was used to easily identify and track packets at relative points in the flow.
Figure 8. Asymmetrical Flow - Z-Mode with ICD
Initiating a 500-byte ping from source 192.168.41.100 across VPN tunnel (192.168.100.133 :: 203.0.113.100) to destination address of 192.168.97.99. An IP from the address pool, 192.168.4.1 was assigned to the client. Traffic was captured at the ingress interface (GE-0/0/2 - physical interface bound to the VPN tunnel interface ST0.100) on the active node, MNHA-SRX-B, and at the ICD interface (GE-0/0/6) shown below.
Figure 9. Z-Mode Packet capture across ICD
Notice the UDP encapsulation and additional 40 byte overhead.
The representative session tables identify the ingress traffic (ICMP Echo) at MNHA-VSRX-B on the tunnel and the return traffic (ICMP Echo Reply) on MNHA-VSRX-A. Wings show active, active on B, reachable via directly connected, with zero packets/bytes incrementing where we should see the return traffic incrementing by one. However, we see Warm/Active active on A. The warm flow is the synchronized Active flow for the ingress shown on MNHA-VSRX-B while the Active wing indicates incrementing packets/bytes processed on MNHA-VSRX-A.
MNHA-VSRX-B
# run show security flow session source-prefix 192.168.4.0/24 protocol 1
Session ID: 91585, Policy name: VPN-DMZ-ANY/33, HA State: Active, Timeout: 2, Session State: Valid
In: 192.168.4.1/29 --> 192.168.97.99/31830;icmp, Conn Tag: 0x0, If: st0.100, Pkts: 1, Bytes: 528, HA Wing State: Active,
Out: 192.168.97.99/31830 --> 192.168.4.3/29;icmp, Conn Tag: 0x0, If: ge-0/0/3.0,
Pkts: 0, Bytes: 0
, HA Wing State:
Active
,
MNHA-VSRX-A
# run show security flow session source-prefix 192.168.4.0/24 protocol 1
Session ID: 689980, Policy name: VPN-DMZ-ANY/34, HA State: Warm, Timeout: 54, Session State: Valid
In: 192.168.4.3/29 --> 192.168.97.99/31830;icmp, Conn Tag: 0x0, If: st0.100,
Pkts: 0, Bytes: 0
, HA Wing State:
Warm
,
Out: 192.168.97.99/31830 --> 192.168.4.1/29;icmp, Conn Tag: 0x0, If: ge-0/0/3.0, Pkts: 1, Bytes: 528, HA Wing State: Active,
Another example of asymmetry is with through traffic. Traffic that does not initiate or terminate with a source or destination that is "directly" connected to the SRX (providing gateway services). Figure 10 and subsequent flow information for an SSH connection originating from 192.168.100.133 to 10.177.177.77.
Figure 10. Asymmetric Flow Support - Non-Z-Mode with ICD
We can see the same Active/Warm sessions split between the B and A nodes as before. However, in this scenario, no session traffic is crossing the ICD.
MNHA-VSRX-B
> show security flow session source-prefix 192.168.100.33 destination-prefix 10.177.177.77
Session ID: 22363, Policy name: default-permit/9, HA State: Active, Timeout: 1714, Session State: Valid
In: 192.168.100.33/13623 --> 10.177.177.77/22;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 1560, Bytes: 106121, HA Wing State:
Active
,
Out: 10.177.177.77/22 --> 192.168.100.33/13623;tcp, Conn Tag: 0x0, If: ge-0/0/4.0, Pkts: 0, Bytes: 0, HA Wing State: Warm,
Total sessions: 1
MNHA-VSRX-A
> show security flow session source-prefix 192.168.100.33 destination-prefix 10.177.177.77
Session ID: 34509, Policy name: default-permit/9, HA State: Active, Timeout: 1762, Session State: Valid
In: 192.168.100.33/13623 --> 10.177.177.77/22;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, HA Wing State:
Warm
,
Out: 10.177.177.77/22 --> 192.168.100.33/13623;tcp, Conn Tag: 0x0, If: ge-0/0/4.0, Pkts: 1326, Bytes: 487153, HA Wing State: Active,
Total sessions: 1
In this environment, you can use the command, "show chassis high-availability data-plane statistics", to determine that packets are not using the ICD. This is a lot easier than implementing a packet capture.
MNHA-VSRX-B> show chassis high-availability data-plane statistics
...
Packet stats                              Pkts sent    Pkts received
ICD Data                                  0            0
With increasing traffic counters for sent and received packets for the synchronized flow (show security flow session), there is no incrementation of either sent or received packets in the data-plane statistics for ICD Data.
Let's take a deeper dive into this flow. The previous conversation was from a look at an active session, past the initial setup. During initial setup, the
SYN
will pass through SRX-B, the asymmetric
SYN-ACK
will ingress into SRX-A, cross the ICD, and egress SRX-B. Completing the 3-way handshake, the path of the final
ACK
is identical to the initial SYN (Figure 11). Once complete, the remainder of the asymmetric flow will not traverse the ICD and egress via SRX-B (Figure 10).
Figure 11. Asymmetrical TCP 3-Way Handshake with ICD
Validating the source and destination hardware addresses in the packet capture below, we can see that 00:0C:29:2F:E7:6F (SRX-B) sends and receives the three-way handshake packets, while frame 5 shows an egress packet via SRX-A (00:0C:29:CB:8B:D6).
MNHA-VSRX-A
> show interfaces ge-0/0/2 | grep hardware
Current address: 00:0c:29:c8:8b:d6, Hardware address:
00:0c:29:c8:8b:d6
MNHA-VSRX-B
> show interfaces ge-0/0/2 | grep hardware
Current address: 00:0c:29:2f:e7:6f, Hardware address:
00:0c:29:2f:e7:6f
Figure 12. Packet Capture - Asymmetric SSH connection with ICD
Just a little deeper and we'll round out this discussion about the ICD. What happens if we have this established asymmetric flow, no other changes to either North or South bound routing, and the link between SRX-A and ISP-2 fails (the active return path)? Will the flow drop? No. The SSH traffic will shift across the ICD. Similarly, when the failed link returns to service, the original flow characteristics will resume without traversing the ICD.
However, if the ICD is down, our SSH session fails.
From 192.168.100.33 - "ssh: connect to host 10.177.177.77 port 22: Operation timed out"
Figure 13. SYN ACK Failures with ICD DOWN
Respective flow information on SRX-B and SRX-A is correct but 192.168.100.33 is not getting a SYN-ACK returned.
MNHA-VSRX-A
Session ID: 102130, Policy name: PUB-ASYM-TEST/51, HA State: Warm, Timeout: 14386, Session State: Valid
In: 192.168.100.33/31801 --> 10.177.177.77/22;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, HA Wing State: Warm,
Out: 10.177.177.77/22 --> 192.168.100.33/31801;tcp, Conn Tag: 0x0, If: ge-0/0/4.0, Pkts: 7, Bytes: 448, HA Wing State: Active,
Total sessions: 1
MNHA-VSRX-B
show security flow session destination-prefix 10.177.177.77 destination-port 22
Session ID: 52136, Policy name: PUB-ASYM-TEST/50, HA State: Active, Timeout: 12, Session State: Valid
In: 192.168.100.33/31801 --> 10.177.177.77/22;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 3, Bytes: 192, HA Wing State: Active,
Out: 10.177.177.77/22 --> 192.168.100.33/31801;tcp, Conn Tag: 0x0, If: ge-0/0/4.0, Pkts: 0, Bytes: 0, HA Wing State: Warm,
Total sessions: 1
The SRX isn't forwarding the SYN-ACK at all. Further research indicates that SRX-A is attempting to forward the SYN-ACK across the down ICD link.
MNHA-VSRX-A
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_ha_fwd_check: MNHA forward for process
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_ha_fwd_check_vector:
MNHA forward for flow process
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_mnha_flow_forward: flags: 1
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_mnha_flow_forward: in_vrf_id: 0
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_mnha_flow_forward: ingress if: ge-0/0/4.0
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_mnha_flow_forward: rtt: PROD, rtt index 7
CID-0:THREAD_ID-02:LSYS_ID-00:RT:flow_fast_mnha_flow_forward: total_tlv_length: 28
CID-0:THREAD_ID-02:LSYS_ID-00:RT:Route-lookup for 100.64.10.10 yielded reject NH
CID-0:THREAD_ID-02:LSYS_ID-00:RT:
re-route failed
Similar to the ICD down scenario above, ICL latency can produce the same type of drop. If the latency between the nodes supporting the ICL connectivity is such that the RTO isn't processed on the peer node and return traffic arrives on the backup node (before session sync), that traffic will be dropped. If designing to support asymmetrical flows, factor the ICL latency accordingly.
Proxy ARP with ICD
With MNHA, NAT configurations should be identical between the two nodes to support stateful fail-overs. With NAT, if we're doing a translation for an address that the firewall doesn't "own" (configured locally on an interface) and is within the same subnet (broadcast domain), we typically use proxy ARP. This is not an issue with interface NAT as the IP and HW addresses will be unique between the nodes' interfaces.
Proxy ARP will only reply to ARP requests, not initiate an ARP request. The SRX will source the IP assigned to the interface for any ARP resolutions. Figure 14 frames the picture of an upstream device ‘ARPing' for the hardware address of an IP 192.168.99.232. The SRXs have SNAT and proxy ARP configurations to answer for 192.168.99.232. Both SRXs will reply to the request. The upstream device can only have 1 ARP entry to IP address in its table, usually the first received reply is honored. If SRX-A forwards a SNAT packet to the upstream device, all is well, until the upstream device returns the packet back to SRX-B with an ICD configured.
Figure 14. Proxy ARP and upstream ARP conflict
Each MNHA node maintains an independent control plane, which means both nodes will respond to proxy-ARP requests. Deployments that rely on proxy-ARP for upstream reachability to the virtual IP, such as those migrating from Chassis Clustering, will need to transition to a L3 routing solution where the upstream device routes directly to the VIP. Without this, a node receiving a packet for a session where NAT was performed on the other node will drop it - show security packet-drop records will report "Dropped by FLOW:error info in MNHA flow meta header". This message can be a useful indicator when troubleshooting asymmetric drop scenarios during migration.
Without the ICD configured, the MNHA pair will process traffic similarly as described in the next section.
Asymmetric Flows without ICD
Let's look at the same two session examples (no NAT function) used in the previous ICD section for comparison: the 500-byte ping Z-Mode test via the RA-VPN tunnel and the SSH asymmetric connection. Regarding the ICMP test, without an ICD configured, the return path is different. Instead of returning to the origination via ISP-2, the encrypted packet is forwarded towards ISP-1.
Figure 15. Asymmetrical Flow (Z-Mode Comparison) without ICD
Three merged packet captures show this behavior with better detail. Frame 56 is our encrypted ingress ICMP ECHO-REQUEST processed at SRX-B (destination MAC address for GE-0/0/2). Frames 57 and 58 show the host receiving and replying to the ping. Frame 59 is the egress encrypted ICMP ECHO-REPLY sent from SRX-A (source MAC address for GE-0/0/1) toward ISP-1.
Figure 16. ICMP Asymmetrical Flow without ICD
The SSH test performed the same with or without an ICD configured.
Figure 17. SSH Asymmetrical Flow without ICD
Again, we'll validate the ingress and egress interfaces by looking at the hardware addresses of the interfaces: Frame 1 = SRX-B, Frame 2 = SRX-A, Frame 3 = SRX-B.
Figure 18. Packet Capture, SSH Asymmetrical Flow no ICD
MNHA-VSRX-B
show security flow session source-prefix 192.168.100.33 destination-port 22 pretty
Session ID              : 57304
Forward Direction       : Interface:
ge-0/0/2.0
, 192.168.100.33/14790 --> 10.177.177.77/22;tcp, conn tag: 0x0, gateway: 192.168.98.1
Reverse Direction       : Interface:
ge-0/0/4.0
, 10.177.177.77/22 --> 192.168.100.33/14790;tcp, conn tag: 0x0, gateway: 192.168.251.130
Forwarding Type         : Route
Bandwidth               : 0.00 MB
From Zone               :
EXT
To Zone                 :
EXT
Layer4 Application      : junos-ssh
...
HA Session Status       :
Active
Policy                  : PUB-ASYM-TEST/50
...
MNHA-VSRX-A
show security flow session source-prefix 192.168.100.33 destination-port 22 pretty
Session ID              : 109699
Forward Direction       : Interface:
ge-0/0/2.0
, 192.168.100.33/14790 --> 10.177.177.77/22;tcp, conn tag: 0x0, gateway: 192.168.98.1
Reverse Direction       : Interface:
ge-0/0/4.0
, 10.177.177.77/22 --> 192.168.100.33/14790;tcp, conn tag: 0x0, gateway: 192.168.251.2
Forwarding Type         : Route
Bandwidth               : 0.00 MB
From Zone               :
EXT-2
To Zone                 :
EXT
Layer4 Application      : junos-ssh
...
HA Session Status       :
Warm
Policy                  : PUB-ASYM-TEST/51
...
Notice the "From Zone" in the output shows EXT-2 while the ingress interface aligns with GE-0/0/2.0 where the return packets are forwarded.
Session creation for the flow (active wing), on SRX-B, installed the forwarding direction, interface ge-0/0/2.0. Now what if that link goes down? Does the traffic fail? Yes.
MNHA-VSRX-A
LSYS-ID-00 10.177.177.77/22-->192.168.100.33/9976;tcp,ipid-39304,ge-0/0/4.0,Dropped by FLOW:fast path pkt reroute failed
Another critical point to factor into designing MNHA deployments. The scheme used for interface connectivity needs to be identical to support any asymmetric flows.
NAT Considerations
During
flow processing
, there is a route-lookup function to determine the security zone, subsequent interface and next-hop to forward traffic to. Before a session is created, the route-lookup function does more than just determine egress interface and zone. Reverse Path Forwarding (RPF) check as well as Reverse Route Lookups (RRL) are performed before certain NAT operations. RPF checks if the source IP is reachable via the same interface the packet arrived on, if the interface is different the packet is dropped (think IP Spoofing mitigation). The Reverse Route Lookup is a mechanism that ensures the return traffic for a session is sent back through the correct, symmetric path (think Zone-to-Zone consistency).
Source NAT (SNAT)
Regarding a single route table that has two route entries (default route) reachable via different destinations A or B, the forwarding decision will select one of the two next-hops, A or B. Now if we want to NAT that traffic, as with typical ISP connections, we need to consider the impacts of RPF and RRL.
Figure 19. ECMP with SNAT List
Source NAT (SNAT) functions occur after the L3 lookup. NAT configurations are processed linearly, from top to bottom (reading a list). If we first define an entry that translates an address (interface or range) that matches the forwarding path (A::A) then there shouldn't' be any issues with our egress traffic (matching forwarding path with SNAT configuration). If the next lookup selects the also valid path with the next-hop towards B, the SRX will perform the NAT operation, and the upstream device will drop the packet. This B:A pattern is problematic.
Figure 20. L3 forwarding potentials with sequential NAT list
A solution is to configure discrete routing instances, separating the tables and relative A/B interfaces (ISP-1/ISP-2) and mapping discrete lists for NAT processing. This results in a predictive L3 lookup and source NAT translation (Figure 21).
Another approach worth considering is with the source NAT rule-set to interface construct, ‘set security nat source rule-set X to interface'; binding a rule-set to a specific egress interface with a corresponding SNAT pool. Unique SNAT pools advertised exclusively to their respective ISPs, the return path is deterministic and ‘to interface' can work effectively. However, consider:
If a common or shared pool range is used, the same prefix is reachable via both ISPs and return traffic becomes non-deterministic and can cause end-to-end flows to fail.
Splitting the pool range, or using unique ranges, per ISP resolves the return path, but introduces additional operational dependencies regarding ECMP hash consistency, correct per-ISP prefix advertisements, and disciplined SNAT rule-set to pool mapping are dependencies that all need to align. A misalignment can cause traffic failures and increase the difficulty in diagnosing these types of faults.
The examples used and discussed in this post use a shared pool and separate routing instances. Again - mileage varies....
Figure 21. Separated L3 forwarding potentials with NAT lists
The bow-tie journey begins...
SNAT Pools without Proxy ARP
Continuing with the above SNAT pool example for 192.168.99.232 we can explicitly tell the upstream router to send return traffic to the IP address assigned to the physical interface (GE-0/0/1) of the SRX that initiated the flow. The upstream router would then only need an ARP entry for the physical interface of the SRX and not for 192.168.99.232.
Figure 22. ARP for SRX Interface
What about redundancy? We can solve the problem with routing, such that we weight the routes in so return traffic always prefers A, unless A is down, then use B as the next-hop.
Figure 23. ISP L3 Next-hop to SNAT Pool
Note: In Junos 25.4R, the limit of 32 VIPs per SRG is raised to 2,000.
This may be an issue if your ISP will only accept certain prefix lengths or provides a single static route back. Also, there is an increased potential for asymmetrical traffic patterns. Instead of pointing the next-hop to the SRX interfaces, you can point them to a VIP.
Adding an additional 2 VIPS, 1 for the ISP-1 (192.168.99.129) and 1 for ISP-2 (192.168.98.129):
MNHA-VSRX-A & MNHA-VSRX-B
set chassis high-availability services-redundancy-group 2 virtual-ip 2 interface ge-0/0/0.0
set chassis high-availability services-redundancy-group 2 virtual-ip 31 ip 192.168.99.129/24
set chassis high-availability services-redundancy-group 2 virtual-ip 31 interface ge-0/0/1.0
set chassis high-availability services-redundancy-group 2 virtual-ip 32 ip 192.168.98.129/24
set chassis high-availability services-redundancy-group 2 virtual-ip 32 interface ge-0/0/2.0
Different SNATs - Different ISPs
In cases where there will be different SNAT pools per ISP and a failover event occurs, requiring traffic to be SNAT'd into a different address range, expect active connections to fail and require reestablishing. If you have a common prefix that you can announce to both ISPs, then stateful failover is possible. The common prefix we'll use in our examples will be 203.0.113.0/24.
BGP and Routing Policies
Border Gateway Protocol (BGP) - tomes have been dedicated to this subject. BGP is not the only protocol you can use to influence traffic flows, but it is popular, highly configurable, and versatile for traffic engineering especially with MNHA designs. The examples illustrate a few methods to control traffic in and out of the MNHA pair:
AS Path Prepends - to influence ingress traffic by creating a less desirable path (shorter paths preferred) across Autonomous Systems (AS).
Multi Exit Discriminator (MED) - influence ingress traffic from adjacent AS with multiple exit points (lower metric preferred).
Local Preference - influence egress traffic within the AS (higher preferred).
Figure 24. BGP Autonomous Systems View
In the example below, we'll just be ingesting the default route via BGP from each of the ISPs. The SRXs (AS65020) are "directly" connected to the ISPs (AS65002 and AS65003), similarly the SRXs can be connected to an intermediary L3 pair of edge routers and then to the ISPs. AS65001 will be where the remote access VPN clients originate from while AS65300 will source S2S VPN connections.
With symmetry in mind, we want ingress and egress traffic to follow the same path regarding the active MNHA node for the SRG.
Figure 25. Symmetric Traffic Flows
Dual uplinks to different provides, multiple routing instances, MNHA, NAT scenarios and considerations for terminating VPN tunnels can be a challenge. Similarly, how we scratched the surface on how MNHA deployments support asymmetric flows with or without an ICD, we cover a few scenarios which underscore additional reasons to encourage symmetric traffic flows. The scenarios that we'll investigate are:
1) Gateway Lookup Failure (ISP Routing Policies)
2) IP Spoofing (ISP Routing Policies)
3) Non-MNHA Asymmetrical Flows (Internal/External)
ISP Routing Policies
Node/Status
ISP-1 (RI:PROD/SZ:EXT)
ISP-2 (RI:ISP-2/SZ:EXT-2)
SRX-A (SRG-2)
MNHA_ROUTE_POLICY_ISP
MNHA_ROUTE_POLICY_ISP_BACKUP
Active
Best Path
Backup Path
Backup
Backup Path
Backup Path
Node/Status
ISP-2 (RI:PROD/SZ:EXT)
ISP-1 (RI:ISP-1/SZ:EXT-1)
SRX-B (SRG-2)
MNHA_ROUTE_POLICY_ISP_BACKUP
MNHA_ROUTE_POLICY_ISP
Active
Backup Path
Best Path
Backup
Backup Path
Backup Path
Table 1. ISP route preferences
Starting with a high-level intent of how we want to influence traffic to and from our ISP connections. A single prefix 203.0.113.0/24 will be advertised northbound to both ISP-1 and ISP-2 to cover our SNAT pools. From that same /24, we'll advertise the /32 for the floating loopback for tunnel anchoring. A single prefix for the default route is received from the ISPs.
Signal routes for SRG-2 that will be the trigger or matching condition for the route treatment will be 169.254.200.3 and 169.254.200.4. If one of the SRXs sees 169.254.200.3 in its routing table, the role is active. Vice versa, if an SRX sees 169.254.200.4, the role will be that of backup. The SRX will only see one of these signal routes, not both. Creatively, we'll name the route policies MNHA_ROUTE_ISP and MNHA_ROUTE_POLICY_ISP_BACKUP (Table 1).
Figure 26. SRG2 - Active/Backup Conditional Route Advertising
When configuring the active/backup signal routes if you don't specify the routing instance, the SRX will modify inet0. Wherever the signal routes are added, based on active/backup role status, we'll need to match for investigating the existence of the signal route.
MNHA-VSRX-A & MNHA-VSRX-B
set chassis high-availability services-redundancy-group 2 active-signal-route
169.254.200.3
set chassis high-availability services-redundancy-group 2 backup-signal-route
169.254.200.4
set policy-options condition ACTIVE_ROUTE_EXISTS_SRG2 if-route-exists address-family inet 169.254.200.3/32
set policy-options condition ACTIVE_ROUTE_EXISTS_SRG2 if-route-exists address-family inet
table inet.0
set policy-options condition BACKUP_ROUTE_EXISTS_SRG2 if-route-exists address-family inet 169.254.200.4/32
set policy-options condition BACKUP_ROUTE_EXISTS_SRG2 if-route-exists address-family inet
table inet.0
Gateway Lookup Failures - Ingress Control (AS Path Prepend)
Avoid the dreaded "Gateway lookup failed" situation. If VPN tunnel initiation traffic is received at an external interface that is in a different routing-instance (RI:ISP-1 or RI:ISP-2) than the floating IP (RI:PROD), an IKE GW-LOOKUP-FAILURE event is created (Figure 27) resulting in a failed IKE Security Association (SA).
Figure 27. VPN GW-LOOKUP-FAILURE, Different Routing Instances
[TER] [PEER] [203.0.113.100 <-> 192.168.100.133] IKE: R:192.168.100.133:500 Role:R
Gateway lookup failed
This is an example for ingress control - advertising the 203.0.113.100/32 prefix ensuring that the preferred path is via ISP1 to the PROD instance on SRX-A and if SRX-B is active then we want the preferred path to be that from ISP-2.
Another bow-tie moment... If we didn't advertise any prefixes Northbound (SRX-A to ISP-2 or SRX-B to ISP-1) there isn't any potential for the ISP routers to forward traffic to the non-MNHA routing instance.
We only conditionally advertise the floating-ip our RA-VPN clients connect to. The shared SNAT prefix does not need to be pinned to a single node. Notice in the MNHA_ROUTE_POLICY_ISP below, the prepended advertisement if the backup signal route is present. Not required for functionality.
MNHA_ROUTE_POLICY_ISP (A side):
MNHA-VSRX-A
set policy-options prefix-list SNAT-POOL-COMMON-203 203.0.113.0/24
set policy-options prefix-list IKE-GW-RA-VPN 203.0.113.100/32
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 from prefix-list SNAT-POOL-COMMON-203
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 then next-hop 192.168.99.129
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 from prefix-list IKE-GW-RA-VPN
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 from condition
ACTIVE_ROUTE_EXISTS_SRG2
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 then next-hop 192.168.99.129
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 from prefix-list IKE-GW-RA-VPN
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 from condition
BACKUP_ROUTE_EXISTS_SRG2
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then as-path-prepend "65020 65020 65020 65020"
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then next-hop 192.168.99.129
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term default then reject
MNHA_ROUTE_POLICY_ISP (B side):
MNHA-VSRX-B
set policy-options prefix-list SNAT-POOL-COMMON-203 203.0.113.0/24
set policy-options prefix-list IKE-GW-RA-VPN 203.0.113.100/32
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 from prefix-list SNAT-POOL-COMMON-203
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 then next-hop 192.168.99.128
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 10 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 from prefix-list IKE-GW-RA-VPN
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 from condition
ACTIVE_ROUTE_EXISTS_SRG2
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 then next-hop 192.168.99.128
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 15 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 from prefix-list IKE-GW-RA-VPN
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 from condition
BACKUP_ROUTE_EXISTS_SRG2
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then as-path-prepend "65020 65020 65020 65020"
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then next-hop 192.168.99.129
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term 20 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY_ISP term default then reject
Traditionally, the BGP multihop feature is used to support eBGP peering between IP addresses that are not on the same local subnet, often between loopback interfaces.  To modify the next-hop to an address on the same subnet, not the self IP used for the peering, we will need to use multihop.  Without multihop, the next-hop for the advertised prefix will be the self IP used in the peering.
Without multihop:
MNHA-VSRX-A
show route advertising-protocol bgp 192.168.99.1
...
* 203.0.113.100/24        Self                                    I
With multihop:
MNHA-VSRX-A
show route advertising-protocol bgp 192.168.99.1
...
203.0.113.100/24       192.168.99.129                          I
Alternatively, the ISP routers would need a configured route for the advertised prefix to the VIP.
IP Spoofing - Egress Control (Local Preference)
Another potential issue is with return traffic. With default configurations, IP Spoofing (RPF) will drop traffic if the path back to the originator is different (Figure 28).
Figure 28. IP Spoofing Example
LSYS-ID-00 192.168.100.33/10502-->203.0.113.100/4139;icmp,ipid-19482,ge-0/0/2.0,Dropped by IDS:IP spoofing
For this example, we'll influence the egress direction by changing the local preference of the default route received from the non-PROD routing instance. Yes, if we didn't receive these default routes we wouldn't need to update (bow-tie...).
MNHA-VSRX-A
set policy-options prefix-list DEFAULT-ROUTE 0.0.0.0/0
set policy-options policy-statement ISP-2-DEFAULT-ROUTE term 10 from instance ISP-2
set policy-options policy-statement ISP-2-DEFAULT-ROUTE term 10 from protocol bgp
set policy-options policy-statement ISP-2-DEFAULT-ROUTE term 10 from prefix-list DEFAULT-ROUTE
set policy-options policy-statement ISP-2-DEFAULT-ROUTE term 10 then local-preference 50
set policy-options policy-statement ISP-2-DEFAULT-ROUTE term 10 then accept
set routing-instances PROD routing-options instance-import ISP-2-DEFAULT-ROUTE
MNHA-VSRX-B
set policy-options prefix-list DEFAULT-ROUTE 0.0.0.0/0
set policy-options policy-statement ISP-1-DEFAULT-ROUTE term 10 from instance ISP-1
set policy-options policy-statement ISP-1-DEFAULT-ROUTE term 10 from protocol bgp
set policy-options policy-statement ISP-1-DEFAULT-ROUTE term 10 from prefix-list DEFAULT-ROUTE
set policy-options policy-statement ISP-1-DEFAULT-ROUTE term 10 then local-preference 50
set policy-options policy-statement ISP-1-DEFAULT-ROUTE term 10 then accept
set routing-instances PROD routing-options instance-import ISP-1-DEFAULT-ROUTE
The SRXs have both default routes in the table. The preferred selection is the default with the local preference of 100 (default) over 50.
MNHA-VSRX-A
show route table PROD.inet.0 0.0.0.0/0 exact
PROD.inet.0: 49 destinations, 59 routes (49 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
0.0.0.0/0          *[BGP/170] 00:33:57, localpref 100
AS path: 65002 I, validation-state: unverified
>  to 192.168.99.1 via ge-0/0/1.0
[BGP/170] 00:33:31, localpref 50, from 10.0.0.3
AS path: 65003 I, validation-state: unverified
>  to 192.168.98.1 via ge-0/0/2.0
MNHA-VSRX-B
show route table PROD.inet.0 0.0.0.0/0 exact
PROD.inet.0: 45 destinations, 52 routes (45 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
0.0.0.0/0          *[BGP/170] 00:28:58, localpref 100, from 10.0.0.3
AS path: 65003 I, validation-state: unverified
>  to 192.168.98.1 via ge-0/0/2.0
[BGP/170] 00:25:26, localpref 50
AS path: 65002 I, validation-state: unverified
>  to 192.168.99.1 via ge-0/0/1.0
Non-MNHA Asymmetrical Flows - Ingress Control (Local Pref plus)
Flows that ingress the MNHA cluster via a routing-instance that isn't associated with MNHA (RI:PROD), that are asymmetrical, are subject to traditional processing and enforcements as if the flow was traversing two independent SRXs. The ICL in our discussions is in the PROD. Figure 29 shows traffic received on an interface in the ISP-1 RI - Routing Instance mismatch per say. There will not be any flow synchronization between the two SRXs.
Figure 29. TCP SYN Check and Drop
LSYS-ID-00 10.177.177.77/22-->192.168.100.33/12692;tcp,ipid-61105,ge-0/0/4.0,Dropped by FLOW:First path
Pkt not syn
SRX-A sees the SYN-ACK without first seeing the SYN and will drop the packet accordingly - TCP SYN Checking. The concepts of MNHA are not applicable to ingress flows from a Routing Instance that is not where the ICL is configured.
The complete solution is a combination of the ingress routing policies at both sides of the connection, ISP and Internal.
Internal Routing Policies
The Internal/Extranet example topology is purposefully different from the ISP examples (Figure 30). The ISP examples had a single peer point to different adjacent AS from each of the SRXs. Here, the SRXs will have a single peering each into the same adjacent AS. There isn't a potential RI mismatch, so we can advertise the default route without any treatment if we want downstream ECMP capabilities. We want to influence the following prefixes:
10.165.251.200/32 is the floating IP used with site-to-site tunnel.
192.168.97.0/24 and 192.168.252.0/24 are DMZ/INT subnets supported by our VIPs.
The 192.168.251.x/25 prefixes are to support troubleshooting efforts with tools like traceroute.
Figure 30. Internal BGP Connections
Beginning with the high-level intent of how we want to influence traffic towards our "internal" network (Table 2).
Node/Status
RTR-A (RI:PROD/SZ:EXT)
SRX-A (SRG-1)
MNHA_ROUTE_POLICY
Active
Best Path
Backup
Backup Path
Node/Status
RTR-B (RI:PROD/SZ:EXT)
SRX-B (SRG-1)
MNHA_ROUTE_POLICY
Active
Best Path
Backup
Backup Path
(Table 2. Routing Preferences for SRG-1)
Signal routes for SRG-1 that will be 169.254.200.1 and 169.254.200.2.
MNHA-SRX-A & B
set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet 169.254.200.1/32
set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0
Prefix lists configuration:
MNHA-SRX-A & B
set policy-options prefix-list INTERNAL-PREFIXES 10.165.251.200/32
set policy-options prefix-list INTERNAL-PREFIXES 192.168.97.0/24
set policy-options prefix-list INTERNAL-PREFIXES 192.168.252.0/24
MNHA-SRX-A
set policy-options prefix-list INTERNAL-PREFIXES 192.168.251.0/25
MNHA-SRX-B
set policy-options prefix-list INTERNAL-PREFIXES 192.168.251.128/25
Routing policy configuration:
MNHA-SRX-A & B
set policy-options prefix-list INTERNAL-PREFIXES 10.165.251.200/32
set policy-options policy-statement MNHA_ROUTE_POLICY term 10 from prefix-list INTERNAL-PREFIXES
set policy-options policy-statement MNHA_ROUTE_POLICY term 10 from condition ACTIVE_ROUTE_EXISTS_SRG1
set policy-options policy-statement MNHA_ROUTE_POLICY term 10 then metric 10
set policy-options policy-statement MNHA_ROUTE_POLICY term 10 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY term 20 from prefix-list INTERNAL-PREFIXES
set policy-options policy-statement MNHA_ROUTE_POLICY term 20 from condition BACKUP_ROUTE_EXISTS_SRG1
set policy-options policy-statement MNHA_ROUTE_POLICY term 20 then metric 20
set policy-options policy-statement MNHA_ROUTE_POLICY term 20 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY term 100 from prefix-list DEFAULT-ROUTE
set policy-options policy-statement MNHA_ROUTE_POLICY term 100 then accept
set policy-options policy-statement MNHA_ROUTE_POLICY term default then reject
While the MED will influence a decision towards our MNHA cluster as AS65200 has 2 exit points toward AS65020, additional configuration on the routers is needed due to the iBGP link between them. Production deployments should consider additional policy terms to account for transitional node states such as boot or ineligible; ensuring path selection remains deterministic regardless of SRG condition.
MNHA-RTR-A & MNHA-RTR-B
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-10_2_LP_200 from protocol bgp
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-10_2_LP_200 from metric 10
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-10_2_LP_200 then local-preference 200
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-10_2_LP_200 then accept
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-20_2_LP_50 from protocol bgp
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-20_2_LP_50 from metric 20
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-20_2_LP_50 then local-preference 50
set policy-options policy-statement MNHA-MED-LOCAL-PREF term MED-20_2_LP_50 then accept
set policy-options policy-statement MNHA-MED-LOCAL-PREF term OTHER-BGP-PREFIXES from protocol bgp
set policy-options policy-statement MNHA-MED-LOCAL-PREF term OTHER-BGP-PREFIXES then accept
set protocols bgp group EXT-AS65200-AS65020 import MNHA-MED-LOCAL-PREF
With MNHA-SRX-A (Active for SRG-1)
MNHA-RTR-A
show route 10.165.251.200
inet.0: 19 destinations, 24 routes (18 active, 0 holddown, 1 hidden)
+ = Active Route, - = Last Active, * = Both
10.165.251.200/32  *[BGP/170] 02:41:13, MED 10, localpref 200
AS path: 65020 I, validation-state: unverified
>  to 192.168.251.1 via ge-0/0/0.0
MNHA-RTR-B
show route 10.165.251.200
inet.0: 16 destinations, 23 routes (15 active, 0 holddown, 1 hidden)
+ = Active Route, - = Last Active, * = Both
10.165.251.200/32  *[BGP/170] 02:14:19, MED 10, localpref 200
AS path: 65020 I, validation-state: unverified
>  to 172.16.1.0 via ge-0/0/2.0
[BGP/170] 02:11:38, MED 20, localpref 50
AS path: 65020 I, validation-state: unverified
>  to 192.168.251.129 via ge-0/0/0.0
IPSEC VPNs
Internet Protocol Security (IPSec) can be used to securely tunnel encrypted traffic across less trusted (or not at all) networks. Two types we'll look are for remote access (aka user) and site to site. Before we dig into the configurations let's look at some common observations relative to IPSec tunnels and MNHA.
With MNHA IKE/IPSEC, Security Associations (SAs) status can be viewed on either node, further narrowed down by SRG. Below is shown IKE Security associations from both SRX-A and SRX-B.
MNHA-SRX-A
show security ike security-associations
Index   State  Initiator cookie  Responder cookie  Mode           Remote Address
33554467 UP
cb1efa14bb285afc
9d19988ca6ed7c15  IKEv2          192.168.100.33
16777257 UP    f80d6cf38e7e07f9  bc8441834c7ab148  IKEv2          10.177.177.77
show security ike security-associations
srg-id 2
Index   State  Initiator cookie  Responder cookie  Mode           Remote Address
33554467 UP
cb1efa14bb285afc
9d19988ca6ed7c15  IKEv2          192.168.100.33
MNHA-SRX-B
show security ike security-associations
Index   State  Initiator cookie  Responder cookie  Mode           Remote Address
33554467 UP
cb1efa14bb285afc
9d19988ca6ed7c15  IKEv2          192.168.100.33
16777257 UP    f80d6cf38e7e07f9  bc8441834c7ab148  IKEv2          10.177.177.77
show security ike security-associations
srg-id 1
Index   State  Initiator cookie  Responder cookie  Mode           Remote Address
16777257 UP
f80d6cf38e7e07f9
bc8441834c7ab148  IKEv2          10.177.177.77
While the information presented is the same, the tunnel is established to the active node for the SRG.
MNHA-SRX-B
show chassis high-availability information
...
Services Redundancy Group: 1
Deployment Type: ROUTING
Status: BACKUP
...
Services Redundancy Group: 2
Deployment Type: HYBRID
Status: ACTIVE
Additional validation of where the tunnels anchored can be evaluated in the session tables by looking at the HA State (Active or Backup). For a more focused view use "show security flow session tunnel".
MNHA-SRX-B
show security flow session protocol esp
Session ID: 19, Policy name: N/A,
HA State: Active
, Timeout: N/A, Session State: Valid
In: 100.64.0.9/0 --> 100.64.0.10/0;esp, Conn Tag: 0x0, If: ge-0/0/5.0, Pkts: 1, Bytes: 108, HA Wing State: Active,
Session ID: 51, Policy name: N/A,
HA State: Backup
, Timeout: N/A, Session State: Valid
In: 10.177.177.77/0 --> 10.165.251.200/0;esp, Conn Tag: 0x0, If: lo0.10, Pkts: 0, Bytes: 0, HA Wing State: Active,
Session ID: 23167, Policy name: N/A,
HA State: Active
, Timeout: N/A, Session State: Valid
In: 192.168.100.33/0 --> 203.0.113.100/0;esp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, HA Wing State: Active,
...
Total sessions: 11
MNHA-SRX-A
show security flow session protocol esp
Session ID: 789, Policy name: N/A,
HA State: Active
, Timeout: N/A, Session State: Valid
In: 10.177.177.77/0 --> 10.165.251.200/0;esp, Conn Tag: 0x0, If: lo0.10, Pkts: 0, Bytes: 0, HA Wing State: Active,
Session ID: 798, Policy name: N/A,
HA State: Active
, Timeout: N/A, Session State: Valid
In: 100.64.0.10/0 --> 100.64.0.9/0;esp, Conn Tag: 0x0, If: ge-0/0/5.0, Pkts: 0, Bytes: 0, HA Wing State: Active,
Session ID: 44168, Policy name: N/A,
HA State: Backup
, Timeout: N/A, Session State: Valid
In: 192.168.100.33/0 --> 203.0.113.100/0;esp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 0, Bytes: 0, HA Wing State: Active,
...
Total sessions: 11
Both nodes have identical tunnel configurations. To view traffic a specific node is forwarding on its tunnel interface, use the show interface st0.x command. Traffic statistics are specific to the node and not sync'd between the two. The following shows a symmetric traffic pattern as we increment both transmit and receive on a single node's tunnel interface.
MNHA-VSRX-B> show interfaces st0.100 | grep packets
Input packets :
197774
Output packets:
196171
MNHA-VSRX-A# run show interfaces st0.100 | grep packets
Input packets : 8058
Output packets: 8109
MNHA-VSRX-B> show interfaces st0.100 | grep packets
Input packets :
197780
Output packets:
196177
MNHA-VSRX-A# run show interfaces st0.100 | grep packets
Input packets : 8058
Output packets: 8109
Asymmetric patterns will show input packets (or output packets) on one node while output (or input) packets on the other node incrementing for the session.
Remote Access VPN
Observations:
IKEV1 aggressive mode sessions aren't synchronized across. IKEv1 requires the VPN client to re-authenticate and re-establish the tunnel with the new active node upon failover.
When adding certs, you only need to add the cert on 1 node. The certificate will be synchronized to the 2nd node as long as the ICL is up and in sync - "Cold Sync Status: COMPLETE"
We will explore a full tunnel example (no split tunnelling). All traffic from the client is sent to the SRX for inspection and forwarding.
Addresses will be assigned from pools based on group information provided from RADIUS server (Framed-Pool attribute) from 192.168.4-6.0/24. In an active-active scenario with multiple SRGs, then a different address pool (or split the /24s in half and assign 1 half to node A and the other to node B per SRG) is required. It is not necessary to do with a single SRG as in our setup.
Consider a tunnel active on SRX-A. The client is assigned an address of 192.168.4.4 from the pool.
MNHA-VSRX-A
show network-access address-assignment pool 192_168_4_0-24
IP address/prefix       Hardware address     Host/User      Type
192.168.4.4            FF:FF:C0:A8:04:04    james          xauth
show security ike security-associations 192.168.100.33 detail | grep "AAA assigned IP"
AAA assigned IP: 192.168.4.4
If a failover event is triggered, the assigned IP for the client from the pool moves to SRX-B.
MNHA-VSRX-B
show network-access address-assignment pool 192_168_4_0-24
IP address/prefix       Hardware address     Host/User      Type
192.168.4.4            FF:FF:C0:A8:04:04    james          xauth
show security ike security-associations 192.168.100.33 detail | grep "AAA assigned IP"
AAA assigned IP: 192.168.4.4
If while SRX-B is active, new connections will pull from the same pool. Similarly, if we failback, all the addresses used from the pool will follow - without collision. If a different range was used for the same SRG pool, then when failing back and forth the tunnel connections would drop as the pool is not common. With multiple SRGs, there is a possibility of address collisions, hence the requirement for separate (shared) ranges between the nodes.
Address pool configuration
MNHA-SRX-A & MNHA-SRX-B
set access address-assignment pool 192_168_4_0-24 family inet network 192.168.4.0/24
set access address-assignment pool 192_168_4_0-24 family inet xauth-attributes primary-dns 192.168.99.100/32
set access address-assignment pool 192_168_4_0-24 family inet xauth-attributes secondary-dns 8.8.8.8/32
IKE Proposal configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ike proposal IKE-PROP-CERT authentication-method rsa-signatures
set security ike proposal IKE-PROP-CERT dh-group group14
set security ike proposal IKE-PROP-CERT authentication-algorithm sha-256
set security ike proposal IKE-PROP-CERT encryption-algorithm aes-128-cbc
set security ike proposal IKE-PROP-CERT lifetime-seconds 28800
IKE Policy configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ike policy MNHA-RA-VPN proposals IKE-PROP-CERT
set security ike policy MNHA-RA-VPN certificate local-certificate MNHA-RA-VPN
set security ike policy MNHA-RA-VPN certificate trusted-ca ca-profile WINLAB-DC1_1
The external interface is the interface that is associated with the configuration the floating IP address (lo0.10). The local address, 203.0.113.100/32, is monitored with MNHA (prefix-list). 203.0.113.100 resolves to mnha-ra.winlab.local and is what the client will initiate its connection to.
IKE GW configuration:
MNHA-SRX-A & MNHA-SRX-B
set access address-assignment pool 192_168_4_0-24 family inet network 192.168.4.0/25
set security ike gateway MNHA-RA-VPN ike-policy MNHA-RA-VPN
set security ike gateway MNHA-RA-VPN dynamic hostname client.ra-vpn.winlab.local
set security ike gateway MNHA-RA-VPN dynamic connections-limit 25
set security ike gateway MNHA-RA-VPN dynamic ike-user-type group-ike-id
set security ike gateway MNHA-RA-VPN dead-peer-detection optimized
set security ike gateway MNHA-RA-VPN dead-peer-detection interval 10
set security ike gateway MNHA-RA-VPN dead-peer-detection threshold 5
set security ike gateway MNHA-RA-VPN nat-keepalive 10
set security ike gateway MNHA-RA-VPN local-identity inet 203.0.113.100
set security ike gateway MNHA-RA-VPN
external-interface lo0.10
set security ike gateway MNHA-RA-VPN
local-address 203.0.113.100
set security ike gateway MNHA-RA-VPN aaa access-profile USER-AUTH
set security ike gateway MNHA-RA-VPN version v2-only
set security ike gateway MNHA-RA-VPN tcp-encap-profile SSL-RA-VPN-PROF
IPSec proposal configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec proposal IPSEC-PROP protocol esp
set security ipsec proposal IPSEC-PROP encryption-algorithm aes-128-gcm
set security ipsec proposal IPSEC-PROP lifetime-seconds 3600
IPSec policy configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec policy IPSEC-POLICY proposals IPSEC-PROP
IPSec VPN configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec vpn MNHA-RA-VPN bind-interface st0.100
set security ipsec vpn MNHA-RA-VPN df-bit clear
set security ipsec vpn MNHA-RA-VPN copy-outer-dscp
set security ipsec vpn MNHA-RA-VPN ike gateway MNHA-RA-VPN
set security ipsec vpn MNHA-RA-VPN ike ipsec-policy IPSEC-POLICY
set security ipsec vpn MNHA-RA-VPN traffic-selector ts-1 local-ip 0.0.0.0/0
set security ipsec vpn MNHA-RA-VPN traffic-selector ts-1 remote-ip 0.0.0.0/0
In Junos OS Release 23.1R1 and later, the default-profile option is deprecated. The new profile names use FQDNs or IPs to identify the remote connections.
MNHA-SRX-A & MNHA-SRX-B
set security ipsec vpn MNHA-RA-VPN bind-interface st0.100
set security remote-access profile mnha-ra-vpn.winlab.local access-profile USER-AUTH
set security remote-access profile mnha-ra-vpn.winlab.local ipsec-vpn MNHA-RA-VPN
set security remote-access profile mnha-ra-vpn.winlab.local access-profile USER-AUTH
set security remote-access profile mnha-ra-vpn.winlab.local client-config JCS-RAS-VPN
set security remote-access client-config JCS-RAS-VPN connection-mode manual
set security remote-access client-config JCS-RAS-VPN dead-peer-detection interval 60
set security remote-access client-config JCS-RAS-VPN dead-peer-detection threshold 5
set security remote-access client-config JCS-RAS-VPN no-eap-tls
set security remote-access client-config JCS-RAS-VPN certificate no-pin-request-per-connection
set security remote-access client-config JCS-RAS-VPN certificate warn-before-expiry 60
set security remote-access client-config JCS-RAS-VPN credentials password
The profile entry matches that of what the client uses to connect with.
Figure 31. JSC Connection Profile
In MNHA, the control planes are independent. RADIUS configurations are specific to the node as well as connectivity from each node to the RADIUS server.
MNHA-SRX-A & MNHA-SRX-B
set access radius-server 192.168.99.100 port 1812
set access radius-server 192.168.99.100 accounting-port 1813
set access radius-server 192.168.99.100 secret "$9$<REDACTED>"
set access radius-server 192.168.99.100 timeout 2
set access radius-server 192.168.99.100 retry 3
set access radius-server 192.168.99.100 source-address X.X.X.X
Additional configurations:
MNHA-SRX-A & MNHA-SRX-B
set system services web-management https interface lo0.10
set services ssl termination profile SSL-RA-VPN-TERM-PROF server-certificate MNHA-RA-VPN
set security tcp-encap profile SSL-RA-VPN-PROF ssl-profile SSL-RA-VPN-TERM-PROF
set security tcp-encap profile SSL-RA-VPN-PROF log
set access profile USER-AUTH authentication-order radius
set access firewall-authentication web-authentication default-profile USER-AUTH
Site-to-Site VPN
The site-to-site VPN example is very basic. The only added twist is that the tunnel interface is in a different routing-instance.
Reference for IPSec configurations
: Active/Active, Dynamic Routing Protocols, and ADVPN.
IKE Proposal configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ike proposal IKE-PROP authentication-method pre-shared-keys
set security ike proposal IKE-PROP dh-group group14
set security ike proposal IKE-PROP authentication-algorithm sha-256
set security ike proposal IKE-PROP encryption-algorithm aes-128-cbc
set security ike proposal IKE-PROP lifetime-seconds 28800
IKE Policy configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ike policy IKE-POLICY pre-shared-key ascii-text "$9$<REDACTED>"
set security ike policy IKE-POLICY-2 proposals IKE-PROP
set security ike policy IKE-POLICY-2 pre-shared-key ascii-text "$9$<REDACTED>"
Again, the external interface is that of lo0.10 but the local address is 10.165.251.100, floating IP in SRG-1.
IKE GW configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ike gateway IKE-GW-VPN-1 ike-policy IKE-POLICY-2
set security ike gateway IKE-GW-VPN-1 address 10.177.177.77
set security ike gateway IKE-GW-VPN-1 dead-peer-detection optimized
set security ike gateway IKE-GW-VPN-1 dead-peer-detection interval 10
set security ike gateway IKE-GW-VPN-1 dead-peer-detection threshold 5
set security ike gateway IKE-GW-VPN-1
external-interface lo0.10
set security ike gateway IKE-GW-VPN-1
local-address 10.165.251.200
set security ike gateway IKE-GW-VPN-1 version v2-only
IPSec proposal configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec proposal IPSEC-PROP protocol esp
set security ipsec proposal IPSEC-PROP encryption-algorithm aes-128-gcm
set security ipsec proposal IPSEC-PROP lifetime-seconds 3600
IPSec policy configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec policy IPSEC-POLICY proposals IPSEC-PROP
IPSec VPN configuration:
MNHA-SRX-A & MNHA-SRX-B
set security ipsec vpn VPN-1 bind-interface st0.200
set security ipsec vpn VPN-1 ike gateway IKE-GW-VPN-1
set security ipsec vpn VPN-1 ike ipsec-policy IPSEC-POLICY
set security ipsec vpn VPN-1 traffic-selector 192.168.252.0_192.168.249.0 local-ip 192.168.252.0/24
set security ipsec vpn VPN-1 traffic-selector 192.168.252.0_192.168.249.0 remote-ip 192.168.249.0/24
set security ipsec vpn VPN-1 traffic-selector 192.168.97.0_192.168.249.0 local-ip 192.168.97.0/24
set security ipsec vpn VPN-1 traffic-selector 192.168.97.0_192.168.249.0 remote-ip 192.168.249.0/24
set security ipsec vpn VPN-1 establish-tunnels immediately
When the tunnel builds, Auto Route Insertion (ARI) will add the prefix for our traffic selector in the PROD RI, for 192.168.249.0/24, on both MNHA nodes.
MNHA-SRX-A & MNHA-SRX-B
show route table PROD.inet.0 192.168.249.0/24
PROD.inet.0: 54 destinations, 61 routes (54 active, 0 holddown, 0 hidden)
+ = Active Route, - = Last Active, * = Both
192.168.249.0/24   *[
ARI-TS/5
] 1d 05:10:02, metric 5
>  via st0.200
The tunnel interface st0.200 resides in the VPN RI. We're not beholden to the same restriction regarding the IKE-GW. There needs to be routing to and from the PROD RI and VPN RI for successful connectivity.
MNHA-SRX-A & MNHA-SRX-B
set policy-options prefix-list S2S-PROD-VPN-1_ST0-200 192.168.249.0/24
set policy-options policy-statement S2S-PROD-VPN-1 term 10 from instance VPN
set policy-options policy-statement S2S-PROD-VPN-1 term 10 from prefix-list S2S-PROD-VPN-1_ST0-200
set policy-options policy-statement S2S-PROD-VPN-1 term 10 then accept
set routing-instances PROD routing-options instance-import S2S-PROD-VPN-1
set policy-options policy-statement PROD-S2S-VPN term 10 from instance PROD
set policy-options policy-statement PROD-S2S-VPN term 10 from prefix-list PROD-S2S-PREFIXES
set policy-options policy-statement PROD-S2S-VPN term 10 then accept
set policy-options policy-statement PROD-S2S-VPN term 900 then reject
set routing-instances VPN routing-options instance-import PROD-S2S-VPN
Keeping it Simple
If you've made it this far without skipping ahead, you might think that MNHA is overly complex. The purpose of including the bow-tie design with dual ISPs was to enforce concepts and principles related to MNHA and how MNHA may be incorporated into network architectures. Mileage varies...
Initial questions to answer before you begin your MNHA journey:
Asymmetrical Flow Support?
Advanced Security Services = ICD
VPNs?
Need IKED
Encrypt ICL
SRG (other than SRG0)
Multiple Routing Instances?
ICL, Floating IP (Loopback) and Physical Interface in same RI
NAT/SNAT?
Use L3 over Proxy ARP
If the goal is to load-balance traffic through the MNHA pair, instead of making an ECMP decision on the firewalls, move that functionality outside of the firewalls. This type of ECMP flow-based load-balancing can be viewed with the screen capture from Security Director Cloud (SDC) below.
Figure 32. SDC showing ECMP through MNHA pair
Reduce complexity. Simplify the number of routing tables, e.g. use a single one. Keep in mind any asymmetric potentials, scope the ICL and ICDs for appropriate BW usage.
Appendix A: IP Connectivity Diagram
Appendix B - MNHA INT/SZ/RI
Appendix C - Full Configurations
Link to full configurations:
https://github.com/JNPRAutomate/mnha-ipsec-and-multiple-routing-instances
Summary
A colleague once told me, "If you're a network (router) guy you will have designs with multiple VRFs. If you're a security (firewall) guy, you'll just have one - inet0." Just because you can doesn't mean you should.... It's imperative to understand the requirements to design and implement a successful,
supportable
solution.
Don't add complexity for the sake of it. Reference organizational security policies and standards. Understand traffic flows, expectations and functionality - not only for efficient operations but for more efficient support and troubleshooting.
Useful links
Multi-Node High Availability: public documentation
https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html
Multi-Node High Availability Basics
https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics
Hybrid MNHA with eBGP
https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp
SRX clustering: from Chassis Cluster to MultiNode High Availability
https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha
Flow-Based and Packet-Based Processing User Guide for Security Devices
https://www.juniper.net/documentation/us/en/software/junos/flow-packet-processing/topics/topic-map/security-srx-devices-processing-overview.html
Chassis Cluster Fabric Interfaces
https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/topic-map/security-chassis-cluster-data-plane-interfaces.html
IPSec VPN Configuration Overview
https://www.juniper.net/documentation/us/en/software/junos/vpn-ipsec/topics/topic-map/security-ipsec-vpn-configuration-overview.html
Public Key Infrastructure Guide
https://www.juniper.net/documentation/us/en/software/junos/pki/topics/topic-map/enroll-certificates.html
Juniper Secure Connect User Guide
https://www.juniper.net/documentation/us/en/software/secure-connect/secure-connect-user-guide/topics/concept/juniper-secure-connect-for-windows.html
[SRX] Traffic loss when IPsec VPN is terminated on loopback interface
https://supportportal.juniper.net/s/article/SRX-Traffic-loss-when-IPsec-VPN-is-terminated-on-loopback-interface
[SRX] How to troubleshoot a VPN that is up, but is not passing traffic
https://supportportal.juniper.net/s/article/SRX-How-to-troubleshoot-a-VPN-that-is-up-but-is-not-passing-traffic
Issues with Juniper Secure Connect Configuration with rsa-signature proposals
https://supportportal.juniper.net/s/article/Issues-with-Juniper-Secure-Connect-Configuration-with-rsa-signatures-proposals
[SRX] VPN does not fail back to primary gateway
https://supportportal.juniper.net/s/article/SRX-VPN-does-not-fail-back-to-primary-gateway
[SRX] How to perform ISP failover on dual ISP scenario where ISPs push default route over DHCP...
https://supportportal.juniper.net/s/article/SRX-How-to-perform-ISP-failover-on-dual-ISP-scenario-where-ISPs-push-default-route-over-DHCP-access-internal-route-and-the-ISPs-use-dynamic-IP-addresses-as-well
Github with all config files:
https://github.com/JNPRAutomate/mnha-ipsec-and-multiple-routing-instances
Glossary
ARI - Auto Route Insertion
AS - Autonomous System
BFD - Bi-Directional Forwarding Detection
BGP - Border Gateway Protocol
ECMP - Equal Cost MultiPath
HA - High Availability
ICD - Inter Chassis Datapath Link
ICL - Inter-Chassis Link
L2 - Layer 2
L3 - Layer 3
MED - Multi-Exit Discriminator
MNHA - MultiNode High Availability
RI - Routing Instance
RPF - Reverse Path Forwarding
RRL - Reverse Route Lookup
SDC - Security Director Cloud
SRG - Services Redundancy Group
VIP - Virtual IP
VRF - Virtual Route Forwarding
Acknowledgements
The collective team that reviewed and provided valuable feedback, namely Karel Hendrych and Scott Astor. Plus... Nicolas Fevrier for overseeing the Tech Posts site and handling all the publishing tasks.
Comments
If you want to reach out for comments, feedback or questions, drop us a mail at:
Revision History
Version
Author(s)
Date
Comments
1
James Rathbun
April 2026
Initial Publication
