# Source: SRX clustering: from Chassis Cluster to MultiNode High Availability

Extracted from: srx-from-chassis-cluster-to-mnha.html

Selected selector: after-title row.margin-top-large .col-md-12

---

[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)

![SRX clustering: from Chassis Cluster to MultiNode High Availability](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/85J06gBRdycm8kOQaaFM_Banners TechPost-4.png)

A simple guide for understanding the differences between Chassis Cluster (original CC) and MultiNode High Availability (MNHA) used on Juniper SRX. 

Existing Techpost articles cover the method to understand MNHA:

  * [Multi-Node High Availability Basics](https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics "https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics") (techpost from Steven Jacques)
  * [Hybrid MNHA with eBGP](https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp "https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp") (techpost from James Rathburn)

# Introduction

Historically in Junos, SRX have supported **Chassis Cluster** since day one (i.e. when this feature was introduced around 2008).

This Chassis Cluster technology was inherited from other Junos platform that had the same need to see a pair of devices acting as a single one.  

This evolved over time to incorporate multiple health check mechanisms and support all SRX platforms. But it came with some limitations.

Later (around 2020) **Multi-Node High Availability** (MNHA) was introduced to help redesign the Chassis Cluster and eliminate those limitations. This was introduced in Junos 20.4 on some highend platforms initially.  

It expanded to all SRX midrange platforms later (including vSRX, but not the SRX Branches).

The term “multi-node” also aimed at adding more devices in the same cluster. The feature was released supporting two nodes. Release 25.4 supports up to 3 and 4 nodes.

# Why High Availability?  

This mechanism is utilized for a 2-chassis back-up deployment, preferably seamless, to ensure service availability (here, service is defined as a security service utilizing SRX).  

This includes:  

  * The config level (same shared configuration or partial configuration, for example, shared security policies)  

  * The network level (same IP on same L2 network domain, similar to VRRP, or same loopback if L3 routed),   

  * The session synchronization (not needed for a router but needed for a statefull device like SRX)  

  * The IPsec SA (Security Associations) need also to be synchronized  

  * Common IP Pool for NAT scenarios (single pool split between nodes, or same IP range sync’ed with other node)

Dependencies:  

  * SRX have (dedicated) HA ports for Control Plane and Data Plane  

  * Legacy Chassis Cluster needs L2 between SRX  

  * Security Policies need to be the same

Exceptions:  

  * Some customers may want “HA without State Sync” (some SP/Gi use cases in US/EU)

# What is Chassis Cluster?  

  * Historically, SRX High Availability is using **2 identical chassis** running the **same Junos version** and is seen as a single chassis on the control plane (therefore, named “Chassis Cluster”).  

  * It also shares a single control plane which was running a **single configuration on a single RE**.  

  * Interface numbering is an extension from the first chassis to the second chassis (e.g. slot 0 to slot 7)  

![Figure 01: Interface Numbering](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/pC2T9kSS5GNEHqAjlzC7_SRX-Clustering-01.png)

_Figure 01: Interface Numbering_

  * SRX Chassis Cluster is **available on all SRX models** from Branch to Mid-Range to High-End (including new models, except few initially)  

  * It is also available on the vSRX platform (for private clouds only: ESXi and KVM)  

  * Chassis Cluster has been present for a long time (2008) and has maturated over time, but it is not perfect…

Chassis Cluster supports all SRX but also holds some limitations:  

  * A links) increases cost and complexity  

  * Interface renumbering complicates the configuration and understanding of the utilized ports   

  * Public Cloud environments do not support L2 domain (for HA links)  

  * Chassis cluster requires a dedicated L2 stretch between nodes to offer geo/redundancy  

  * Chassis cluster does not support NSR which results in slow switchovers during control plane failure, causing traffic disruption in certain cases  

  * Chassis upgrades can use a single command, but it takes time, and rollback is more complex  

  * RE switchover needs processes to restart on the new master (such as BGP, losing peerings)

# What is Multi-Node High Availability?  

  * **MNHA** stands for **Multi-Node High Availability** , where the redesign goals for HA include:  

    * having more network flexibility,   

    * eliminating some of the Chassis Cluster limitations (L2 needs…)   

    * allowing more than 2 nodes
  * MNHA uses 2 SRX devices with their own networking:  

    * they are then independent and associated in a way that sessions get synchronized  

    * no more extended chassis notion (then no interface renumbering)
  * Some network design needs some common IP:  

    * Uses a common VIP/vMac for Default Gateway or Hybrid modes  

    * both devices can have their own local services (e.g. BGP, OSPF) 
  * MNHA does not synchronize full configurations:  

    * Each node has its own configuration, only common element (VIP/vMac) needs to be the same   

    * ”commit sync” can help synchronize parts of the configuration (using junos groups)

Other important elements that MNHA solves:  

  * Modern networks and deployments require dual-homing support  

  * Geo-resilience is no longer limited to dark fiber/L2 connectivity (L2 over any link or L3 over routed networks)  

  * Support for Public Cloud deployment with resiliency (AWS, Azure and GCP support)  

  * Allows different version of Junos per node during upgrade phases (requires same feature set across nodes and should be upgraded to same version when all looks stable and sessions are all synchronized)  

  * Improved software lifecycle management (replaces LICU/ISSU)  

  * Built to meet Common Criteria and FIPS certification requirement

# MNHA Control and Data links  

Like Chassis Cluster, MNHA uses a link to exchange information, this is the ICL (like Fab link for session sync).

## Inter Chassis Link (ICL) – Control Plane  

  * In MNHA the ICL link is responsible for the data plane object synchronization (RTO). This link synchronizes all the states in the data plane between the 2 units. An example for an RTO is a NAT table entry and all stateful sessions. The information is synchronized between the nodes in the cluster to make sure during a failure that the session is persistent and continues to work on the other firewall.   

  * The ICL is a layer 3 connected link between the two nodes. The links do not have to be directly connected between both units, and multiple links can be used. The source of the ICL can also be a loopback.  

  * If required, the traffic on the ICL can be encrypted (using IPsec). This encryption may be needed, like when exchanging some confidential material (certificates…). 

## Inter Chassis Datalink (ICD) – Data Plane  

  * The ICD link is used in scenarios when traffic is coming into the firewall via an asymmetric network path (like ECMP) - meaning the traffic is arriving on first node and coming back on second node.   

  * In that case the ICD is used to forward traffic being inspected by plugin services (L7 features like IPS and AppID) to make sure one processing service is seeing the complete session.  

  * Traffic is temporarily forwarded to the node that has started the session until the sessions is fully determined or analyzed depending on the policy. For example, if just TCP sequence is checked (no L7 inspection), then the traffic is then processed on the other node. If more L7 inspection is required, the traffic will continue to be forwarded across ICD.  

  * The ICD is recommended for asymmetric use cases where switches or routers have unpredictive targets as next hop (between the 2 SRX).

Next diagrams represents the MNHA architecture of 2 nodes where both Control Planes are active and both Data Planes also, depending on the status of the local groups (SRG). The networks on each side represent either 2 switches or 2 routers depending on the network mode used. ICL and ICD looks like connected directly to the dataplane, which is accurate, but can also be in different routing-instances (no detail shown here).

![Figure 02: MNHA architecture of 2 nodes](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/YeIcyD8bTuKQarCrZwx0_SRX-Clustering-02.png)

_Figure 02: MNHA architecture of 2 nodes_

Control plane:   

  * All the management functions on SRX (ssh, syslog, users, configurations…)  

  * Active on each node (can runs BGP, OSPF…)

Data Plane:  

  * **SRG0** always acts in Active / Active mode   

    * Handles the L3-L7 Security Services. Inspects symmetric security flows on all nodes.  

    * With ICD: traffics can be forwarded to other node to where session was started and needs to complete inspection (session setup phase, like TCP-SYN/SEQ checks and L7 level inspection)  

    * Uses its own monitored objects to prevent “split brain”
  * **SRG1** always acts in Active / Backup mode:  

    * Handles VIP/vMAC for L2 / Hybrid modes  

    * Terminates IKE/IPsec and syncs IPsec SAs   

    * Allows traffics to be handled by backup node (when sessions in established)  

    * Uses its own monitored objects to detect failover needs
  * **SRG2** or more:   

    * Each group can be Active or Backup state  

    * Each group can use different VIP for L2/Hybrid  

    * Each group can use different IPsec termination  

    * Announce of specific route prefix for each state  

    * Uses its own monitored objects to detect failover needs
  * **Node local** : IPsec termination, independent tunnel for a node that does not need tunnel synchronization (IPsec SA)
  * Node communication:  

    * ICL is a L3 traffic that can be routed  

    * ICL can use a dedicated revenue link and/or a shared link  

    * ICL can use multiple links (using its own loopback and/or aggregate)  

    * ICL can use its own routing-instance (VRx)  

    * ICL can be encrypted with IPsec (recommended)  

    * ICD (optional) routes asymmetric traffics between nodes

# Legacy Chassis Cluster to MNHA Architecture

![Figure 03: Chassis Cluster and MNHA internal structure](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/Ij6kWHrlQMGRqjyT4QA7_SRX-Clustering-03.png)

_Figure 03: Chassis Cluster and MNHA internal structure_

Note: node0/1 numbering used for CC and node1/2 for MNHA

The main difference in the CC vs MNHA architecture starts with the Control Plane (i.e. what controls the cluster).   
CC is by design an Active/Backup method as it runs on a single active RE for the full extended chassis while the other RE is waiting (plus doing some local checks and restarts only when needed). All Routing will be active on one node at a time, configuration is global.

MNHA starts with 2 active RE that are both active and independent. Then all configurations are independent by design and routing also. This allows the use of mulitple networking designs and allows both nodes to have some independence and differences (different ports used for example).

For the dataplane, it also looks similar as CC uses Redundancy Groups (RG) and also does MNHA with Security Redundancy Groups (SRG). But the naming does not it all. By design on MNHA, SRG0 is Active on both nodes, so independently of the networking, whatever interfaces the traffics use, it will always be active.  

SRG1+ groups will be used to associate interfaces and/or IPsec termination points.

Main features for CC and MNHA main features (at a glance)

**Function** | **Chassis Cluster** | **MNHA**  
---|---|---  
Active/Backup Control Plane | YES | YES  
Active/Active Control Plane | NO | YES  
Active/Active Data Plane | YES | YES  
Fabric and Control Link (Dedicated Ports) | YES | NO  
Routed Inter Chassis Link (Any Revenue Interface) | NO | YES  
Encrypted cluster communication (IPsec)  | SRX5000 only | YES  
Distributed BFD = Switchover Time < 1 sec | NO | YES  
Interfaces Types | RETH (L2) | L3  
L3 Geo Cluster | NO | YES  
Interfaces renumbering | YES | NO  
In Service Software Update (ISSU) | YES | Not Needed  
  
  
SRX platforms support for CC and MNHA

**Function** | **Chassis Cluster** | **MNHA**  
---|---|---  
cSRX | NO | NO  
vSRX on private clouds (ESXi, KVM) | YES | YES  
vSRX on public clouds (AWS, Azure, GCP) | NO | YES  
SRX300 Series | YES | NO  
SRX400 Series | NO | YES  
SRX1500 | YES | YES  
SRX4100 | YES | YES  
SRX4200 | YES | YES  
SRX1600 | YES | YES  
SRX4120 | YES | YES  
SRX4300 | YES | YES  
SRX4600 | YES | YES  
SRX4700 | NO | YES  
SRX5000 Series | YES | YES  
  
But the official support is of course defined by JTAC and is summarized [in this KB100225](https://supportportal.juniper.net/s/article/Supported-hardware-and-software-version-of-MNHA-on-SRX-platforms "https://supportportal.juniper.net/s/article/Supported-hardware-and-software-version-of-MNHA-on-SRX-platforms") that gives clear Junos version indication.

# MNHA Network Modes

MNHA can work in multiple ways, the simple being the usual Default Gateway that most users will probably adopt as it looks similar to any default cluster on most routers/firewalls. But it can also use multiple independent links (to 2 ISPs for example) or totally routed links in a bigger routed network (Service Provider or large Enterprise type). 

## MNHA Default Gateway Mode (or L2)

This is probably the most used method that admins will select as it uses a common Virtual IP (VIP) / Virtual Mac (vMAC) pair on each network (left and right on the diagram below). When a failover happens, the new active node on the SRG1 group simply sends a Gratuitous ARP for the switches to update their table (here on each network segments).

![Figure 04: MNHA Default Gateway Mode \(or L2\)](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/DnUGnEJ4Q6y7roTxuYMp_SRX-Clustering-04.png)

_Figure 04: MNHA Default Gateway Mode (or L2)_

**Features** | **Pros** | **Cons**  
---|---|---  
Default Gateway | Simple next hop for the network  
(the most common use case) | Broadcast domain used  
Needs a switch on both sides  
L2 integration | Uses VIP/vMac on each   
segment for each SRG | Limited to 32 VIP per interface  
(fixed to 2K VIP in 24.4R2, 25.4R1)  
Dual stack (IPv4, IPv6) | Can work with dual stack | Single IPv4 OR IPv6 per interface in each SRG (fixed planned)  
MNHA monitoring | Many monitoring features:  
Interfaces, peer router, BFD | BFD needs BFD peer  
SRG1+ | Active / Backup mode  
Terminate/sync IPsec on SRG | Creates other gateways on the segment  
  
MNHA Hybrid Mode (L2-L3)  

Similar to Default Gateway mode but with a different interface to 2 other networks on the other side (typical for a branch device connected to 2 ISP). No change in the way the L2 side works, on the other right side, each SRX may have a different gateway, and then have different IP and routes toward the next hops (toward Internet in general). They may announce a different pool or same pool in case this site owns a public IP (announced via BGP for example).

Note: ICD was represented here (and not before) as it may be more likely to receive some asymmetric traffics from the 2 different routers depending their on routing decision.

![Figure 05: MNHA Hybrid Mode \(L2-L3\)](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/KV8QNz55TNWK5vN0klby_SRX-Clustering-05.png)

_Figure 05: MNHA Hybrid Mode (L2-L3)_

**Features** | **Pros** | **Cons**  
---|---|---  
Default L2 Gateway (left) | Simple next hop for the network | Broadcast/VIP  
Needs a switch on left  
Routed L3 setup (right) | Very powerful routing design   
(BGP, OSPF…) | More routing setup  
Dual homing (right) | Can use 2 upstream routers / ISP | May need to announce a common prefix for NAT (e.g. use BGP)  
Path/session redundancy for traffic inside the VPN | 2 tunnels from each ISP using   
2 node-local tunnels  |   
Bidirectional Forward Detection (BFD) | BFD to quickly detect issues | Needs BFD on monitored objects  
  
MNHA Routing mode (L3)  

This fully routed design would match an environment where no L2/Hybrid works, like in a Service Provider or large Enterprise network, or for a virtual environment where a vSRX may not use any L2 traffics (like Public Cloud environments). This needs each SRX to have only a routed IP on each interface, they do not need to be on same networks, but it is wise to use a dynamic routing where they can announce which pass is available through each of them to the border routers. This announce can be linked to the state of the SRG group they are Active or Backup, like with a different metric in each case.

![Figure 05: MNHA Routing mode \(L3\)](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/e8oVG4IJRaO5Jrgfm237_SRX-Clustering-06.png)

_Figure 06: MNHA Routing mode (L3)_

**Features** | **Pros** | **Cons**  
---|---|---  
Routed L3 setup (right/left) | Very powerful routing design   
(BGP, OSPF…) | More routing setup  
SRG state influenced routing | Each SRG can trigger a condition, used to announce specific prefix (e.g. lo0) | Needs complex policy conditions for each SRG (very powerful)  
BFD to quickly detect issues | BFD influences each SRG state   
change and recovery | Needs BFD on monitored objects  
Active/Passive or Active/Active | Each SRG can be active on its own node | Doubles the SRG and policy conditions  
Additional | Used with CSDS/ScaleOut architecture |   
  
## MNHA Management

In Junos, everything can be configured using CLI with standard Junos configs (or config set). It can also use the API for any external automation tool using Netconf over SSH (e.g. PyEZ with python).  

In opposition to Chassis Cluster that uses a single active RE for both nodes (and copies to the second RE when committed), MNHA nodes have their own independent config, including IP addresses, which is not synchronized automatically. ICL is here for sessions sync, not configuration sync.

Except L2 and L2L3 modes that have a common IP (per SRG on L2 sides), there is no explicit need to synchronize a configuration between nodes for MNHA to be functional, but they need to communicate via Inter Chassis Link (ICL).

There are different methods proposed to get the same config for the common parts:  

  * **Manual copy/paste** from a node to the other (CLI)  good only for labs  

  * **Automatic “system commit sync” of junos-groups** with node names  easier for admins using CLI  

  * Using external **Automation tools with Junos API** (ansible, python, etc…)  DevSecOp teams  

  * Using **Security Director Cloud** (for the security portion only)  use templates in SDC  

  * **Apstra with “ConnectorOps”** (DC tool) can configure more complex routing using templates (MNHA/BGP/BFD…)

We’ll review only the 2 most practical methods below.

### Automatic commit sync with junos-groups

This part is already documented online at [Configuring MNHA with Junos Groups](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/multinode-high-availability-config-groups.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/multinode-high-availability-config-groups.html").

But the principle is declaring a group in Junos config that will be applied to both nodes (by name) and the one having this config will “commit sync” this group to all members (both MNHA nodes here). This requires the “commit sync” and IP/host mapping to be defined on the first node. Note this can be done in both directions.

Example of configuration for “commit sync” (on node1): 
    
    
    set system host-name slab-srx4200-03  
    set system static-host-mapping slab-srx4200-03 inet 10.100.142.3  
    set system static-host-mapping slab-srx4200-04 inet 10.100.142.4  
    
    set system commit peers-synchronize  
    set system commit peers slab-srx4200-04 user labuser  
    set system commit peers slab-srx4200-04 authentication "$9$A.somepassword"  
    set system commit peers slab-srx4200-04 routing-instance MNHA-ICL

Example of configuration for common IPsec for ICL:
    
    
    set groups mnha-sync-group when peers slab-srx4200-03  
    set groups mnha-sync-group when peers slab-srx4200-04  
    set groups mnha-sync-group security ike proposal MNHA-prop description MNHA-ICL  
    set groups mnha-sync-group security ike proposal MNHA-prop authentication-method pre-shared-keys  
    set groups mnha-sync-group security ike proposal MNHA-prop dh-group group14  
    set groups mnha-sync-group security ike proposal MNHA-prop authentication-algorithm sha-256  
    set groups mnha-sync-group security ike proposal MNHA-prop encryption-algorithm aes-256-cbc  
    set groups mnha-sync-group security ike proposal MNHA-prop lifetime-seconds 300  
    set groups mnha-sync-group security ike policy MNHA-pol description iclpolicy  
    set groups mnha-sync-group security ike policy MNHA-pol proposals MNHA-prop  
    set groups mnha-sync-group security ike policy MNHA-pol pre-shared-key ascii-text "$9$.preshared.key.for.icl"  
    set groups mnha-sync-group security ike gateway MNHA-gw ike-policy MNHA-pol  
    set groups mnha-sync-group security ike gateway MNHA-gw version v2-only  
    set groups mnha-sync-group security ipsec proposal MNHA-prop description ICL-esp  
    set groups mnha-sync-group security ipsec proposal MNHA-prop protocol esp  
    set groups mnha-sync-group security ipsec proposal MNHA-prop encryption-algorithm aes-256-gcm  
    set groups mnha-sync-group security ipsec proposal MNHA-prop lifetime-seconds 300  
    set groups mnha-sync-group security ipsec policy MNHA-pol description icl-ph2-pol  
    set groups mnha-sync-group security ipsec policy MNHA-pol proposals MNHA-prop  
    set groups mnha-sync-group security ipsec vpn MNHA-vpn ha-link-encryption  
    set groups mnha-sync-group security ipsec vpn MNHA-vpn ike gateway MNHA-gw  
    set groups mnha-sync-group security ipsec vpn MNHA-vpn ike ipsec-policy MNHA-pol   
    set apply-groups mnha-sync-group

This can be reproduced for almost any part of the configuration, including security addresses and policies.

### Management with Security Director Cloud/Onprem

  * SDC allows the onboarding of existing MNHA SRX/vSRX pair in either L2, Hybrid or L3 mode  

  * SDC allows the visibility of the MNHA status (not the MNHA configuration yet)  

  * SDC supports templates that can be used for specific MNHA configuration  

  * SDC provides for the management of all the security settings on both nodes (like it does for standalone SRX): security policies, NAT, IPsec VPN, L7 inspection, etc…

![Figure 06: Management with Security Director Cloud/Onprem](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/FkARqlKeQTuI5zzC63Iw_SRX-Clustering-07.png)

_Figure 07: Management with Security Director Cloud/Onprem_

## Other MNHA Network Designs

### Asymmetric Traffic Flow Support in MNHA

The need to handle asymmetric traffics comes when the switches or routers surrounding the 2 SRX may send packets to the other Backup node, and not the Active node. This creates an asymmetric data flow that may not work with the stateful nature of the SRX. Remember, to accept a flow, it needs to match a security policy and also match the security criteria to allow it, specifically during the sequence initialization like TCP SYN/SYN-ACK/ACK sequence (and sequence numbers), and any upper layer analysis if any to be performed (IDP, Content Analysis…).  

But in an asymmetric traffic, taking the TCP example, the SYN crosses the Active node, and SYN-ACK may come back on the Backup node instead. Since the session was not yet accepted by Active node (it’s waiting for the SYN-ACK and so on), it would fail here.   

The Inter Chassis Datalink (ICD) is solving this, allowing the asymmetric traffics to come back to the Active node (here the SYN-ACK and other packets) and then allowing the rest of the session establishment to be processed correctly. Active node adds a new session to the sessions table, which is synced to the Backup node.

![Figure 08: Asymmetric Traffic Flow](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/l9P8CH5iRbelKr3tkexG_SRX-Clustering-08.png)

_Figure 08: Asymmetric Traffic Flow_

If all the rest of the packets belonging to the session establishment are sent over ICD in this Z mode, it stops as far as the session is synchronized with the Backup node (this one recognising a known traffic to allow). At that time the traffics stays asymmetric but both nodes continue processing packets on their own side (and not using ICD anymore for this one). Then when inspection is done, ICD disengages and traffic continues asymmetric. Exception comes when more analysis is needed like any Layer 7 deep packet inspection (IDP, UTM, EWF, ATP, …) for the rest of the session.

Technical elements:  

  * 3-way handshake is sent over ICD  

  * ICD is not encrypted (like ICL) but can be routed (UDP encapsulated packets)  

  * ICD needs to support MTU that is large enough to forward and deliver encapsulated packets. Just the size of added IP/UDP header is enough (like MTU 1,600 bytes, or 2,000 bytes for IPv6 packets); in comparison with Chassis Cluster using Jumbo frames (9,000 bytes).

A more specific case comes with IPsec where return traffics should come from the tunnel. It may however fails after a failover (documented in KB90491) and another option has been added to solve, forcing the Backup unit to handle locally the return ESP packets (not the session setup part):
    
    
    set chassis high-availability services-redundancy-group 1 process-packet-on-backup

### MNHA Active/Backup or Active/Active

When it comes to optimizing traffics, or expanding the capacity of the cluster, we can use the Active/Backup model or also expand to an Active/Active model, where both devices will handle their share of traffics. This is different from asymmetric traffics since both will have their own traffics synced to the other node.  

However, this can only augment the network capacity in bandwidth term, not in sessions terms (if they synchronize all sessions). The reason being that each SRX can be used at its maximum, then doubling this capacity when both are used, but any failure will revert to a single SRX capacity. So, this single device capacity needs to be what was first selected as a sizing bandwidth criteria.

Taking 2 A/B models means using 2 gateways to be used at the same time. This may work in Default Gateway (L2), Hybrid (L2L3) or Routed (L3) modes. The idea is to simply use 2 SRG groups with each one its own network path where one node 1 is Active on SRG1 and node 2 is Active on SRG2. The diagrams below show how SRGs are used with a preference in routing that is mirrored.

![Figure 09: SRG1/SRG2 Active/Backup Options](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/a2sXqHJRTPW5elB15XJ9_SRX-Clustering-09.png)

![Figure 10: SRG1/SRG2 Active/Backup Options](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/VQqZTwESXSPeWQYT5XaU_SRX-Clustering-10.png)

_Figure 09 and 10: SRG1/SRG2 Active/Backup Options_

In Default Gateway (L2) and Hybrid (on L2 side) modes:  

  * node1 will have a VIP1 in SRG1 as gateway for the network1. Node2 will be backup of that group for the same network.  

  * Node2 will have a VIP2 in SRG2 as gateway for the network2. Node1 as backup for the same. 

In Hybrid (on L3 side) and Routed (L3) modes:  

  * node1 will have a **higher** route preference in **SRG1** as gateway from/to network1. Node2 will have a lower route preference group for the same network.   

  * Node2 will have a **higher** route preference in **SRG2** as gateway for from/to network2. Node1 will have a lower route preference group for the same network.   

  * Both may announce those route preferences to their router peers (BGP, OSPF…) that will make network1 preferably available via node1 and similarly for network2 and node2.

### Geo Redundancy with MNHA (L3)

![Figure 11: Distributed/Geo redundancy scenario](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/gfRCCN6PTOaABTn6brmb_SRX-Clustering-11.png)

_Figure 11: Distributed/Geo redundancy scenario_

  * Each cluster node has its own network configuration – no virtual IP/MAC, member nodes can be in entirely different networks  

  * Run-time objects (sessions, IPSec tunnels, etc) synched over Inter-Chassis Link (ICL) for stateful failover  

  * ICL is **logical** so can run across dedicated interfaces or in-band traffic interfaces  

  * Both devices ready to always forward traffic; no concept of ‘backup’ mode  

  * Routing policy determines preferred path  

  * BFD over DRP used for very fast failover (3 x 100ms)  

  * Facilitates geo redundant cluster – only requirement is <100ms RTT  

  * Both control planes active

### 4 Nodes MNHA across 2 domains (Junos 25.4R1)

Junos 25.4R1 brings a new capacity to add more nodes to the MNHA cluster, precisely up to 3 or 4 nodes. This is possible in a Routed/L3 environment where adding more nodes is just adding more next hop for the same networks. However, this also means synchronizing more sessions across nodes possibly.

In this 4 nodes model, this is kind of geo redundancy using Routed/L3 mode but split across 2 main sites called Domains. Domain1 will have 2 nodes (like a local MNHA pair) and same for Domain2. Since this is routed, it could also be split on 4 sites (but still considered 2 domains).

A new link is created between domains to synchronize sessions, like Inter Chassis Link (ICL) but named Inter Domain Link (IDL). This traffic can be routed and encrypted using IPsec. 

_![Figure 13: 3 Nodes MNHA across 2 domains](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/ckGUs9ZjTFuDCia8PvHt_SRX-Clustering-13.png)_

_Figure 12: 4 Nodes MNHA across 2 domains_

4-Node MNHA features:  

  * Initially for SRX4600 and SRX4700  

  * L3 Routed Nodes in each domain can be A/B or A/A  

  * An ICL link between nodes in same domain  

  * An IDL link between main nodes between domains  

  * ICL and IDL are logical links so can run across dedicated interfaces or in-band traffic interfaces  

  * Both ICL and IDL can be routed and use IPsec encryption  

  * Dynamic routing is used to attract traffics to active nodes (in each domain)  

  * Asymmetric traffics not supported (intra/inter domain)  

  * Syncing only SRG0 traffics for SFW and NAT (not IPsec that is tied to SRG1)  

  * Received RTO via ICL are synched via IDL to its remote domain peer  

  * Received RTO via IDL are synched via ICL to its local peer

Additional feature in 25.4R1:  

  * MNHA Session Sync Optimization on ICL and IDL is added in the same release, allowing to create policy profiles (“session-sync disabled” or “session-min-age” for selected policies). This allows reducing the amount of traffics to synchronize over ICL and IDL.

### 3 Nodes MNHA across 2 domains (Junos 25.4R1)

The use of 3 nodes might be interesting also for customer wanting a backup site. This is slightly more simple than 4 nodes, but the IDL is still used here to synchronize RTOs. And this time, both nodes from domain 1 do actively communicate with the 3rd node in domain 2. 

![Figure 12: 4 Nodes MNHA across 2 domains](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/QSEhX9SSiuagpb8R2BZy_SRX-Clustering-12.png)

_Figure 13: 3 Nodes MNHA across 2 domains_

3-Node MNHA features:  

  * L3 Routed Nodes in each domain can be A/P or A/A  

  * An ICL link between nodes in same domain  

  * 2 IDL links between nodes to single node in 2nd domain  

  * State sync happens from both nodes in domain1 to single node in domain2 (and reversely)  

  * Use case: second site as backup

And  

  * MNHA Session Sync Optimization on ICL and IDL with policy profiles (“session-sync disabled” or “session-min-age” for certain policies)

### More Nodes in a cluster? Look at CSDS architecture 

Adding more nodes in a cluster would mean some form of load balancing. It means also adding more traffics just for synchronization toward multiple nodes, potentially syncing back and forth in all directions. Our method is using existing (or dedicated) MX with Hardware acceleration (Trio ASIC) to maintain a connection with many SRXs and load balancing the traffics to them. Since we heavily use routing BGP and BFD, and leverage MNHA for SRX cluster pairs, this is scaling, fast and resilient.  

\--> This is what we propose [in ScaleOut / CSDS architecture](https://www.juniper.net/documentation/us/en/software/connected-security-distributed-services/csds-deploy/index.html "https://www.juniper.net/documentation/us/en/software/connected-security-distributed-services/csds-deploy/index.html").

Connected Security Distributed Services architecture (CSDS) allows to grow the scalability to a great number of SRX, either standalone or in MNHA pairs. Four Juniper Validated Designs (JVD) have been created to follow 4 different use cases with this same architecture:  

  * Juniper Scale-Out Stateful Firewall and CGNAT for SP Edge   

  * Juniper Scale-Out IPsec for Mobile Service Providers   

  * Juniper Scale-Out Stateful Firewall and Source NAT for Enterprise   

  * Juniper Scale-Out IPsec Solution for Enterprises 

# Conclusion

After showing all those options, I hope this will make you install your SRX in MultiNode High-Availability or migrate existing ones from Chassis Cluster to MNHA. It’s fairly easy to test it, even with vSRX in different clouds (on prem and public clouds).

As indicated above, there are many interests in using MNHA, and some of them are:  

  * Multiple network designs supported  

  * Going to more than 2 nodes (Junos 25.4)  

  * Geo-redundancy support  

  * Better integration with routed environment (especially BGP and OSPF)  

  * No more interface renumbering  

  * No more L2 criteria between nodes  

  * Easy upgrade of each node independently 

If you want to see the processus, just follow one of those other Tech Posts from our colleagues (links above) that will give you the directions for this.

## Useful Links  

Other Juniper Techposts on this topic:  

  * [Multi-Node High Availability Basics](https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics "https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics") (techpost from Steven Jacques)  

  * [Hybrid MNHA with eBGP](https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp "https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp") (techpost from James Rathburn)

High Availability = Chassis Cluster  

  * [Chassis Cluster Overview](https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/topic-map/security-chassis-cluster-overview.html "https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/topic-map/security-chassis-cluster-overview.html")  

  * [SRX Series Chassis Cluster Configuration Overview](https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/concept/chassis-cluster-srx-series-node-interface-understanding.html "https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/concept/chassis-cluster-srx-series-node-interface-understanding.html")  

  * [SRX Chassis Cluster Slot Numbering](https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/concept/chassis-cluster-srx-series-node-interface-understanding.html "https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/concept/chassis-cluster-srx-series-node-interface-understanding.html") (all SRX models)  

  * [SRX Getting Started - Configure Chassis Cluster (High Availability)](https://supportportal.juniper.net/s/article/SRX-Getting-Started-Configure-Chassis-Cluster-High-Availability?language=en_US "https://supportportal.juniper.net/s/article/SRX-Getting-Started-Configure-Chassis-Cluster-High-Availability?language=en_US") \- KB15650  

  * [SRX HA Configuration Generator](http://www.juniper.net/support/tools/srxha/ "http://www.juniper.net/support/tools/srxha/") (SRX Branch, vSRX, SRX1500, SRX4100, SRX4200)

Multi-Node High Availability  

  * [Multinode High Availability](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html")  

  * [Example: Configure Multinode High Availability in a Default Gateway Deployment](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example-default-gateway-deployment.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example-default-gateway-deployment.html")  

  * [Example: Configure Multinode High Availability in a Hybrid Deployment](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example-hybrid-deployment.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example-hybrid-deployment.html")  

  * [Example: Configure Multinode High Availability in a Layer 3 Network](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-configuration-example.html")  

  * [Example: Configure IPSec VPN in Active-Active Multinode High Availability in a Layer 3 Network](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-active-active-configuration-example.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/example/mnha-active-active-configuration-example.html")  

  * [Asymmetric Traffic Flow Support in Multinode High Availability](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-asymmetric-route-support.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-asymmetric-route-support.html")

## Glossary

Terminology used for Cluster:   

  * CC = “Chassis Cluster”   

  * L2HA = Layer 2 High Availability = Chassis Cluster   

  * CTRL = Control Link (dedicated interface)  

  * FAB = Fabric Link (dedicated interface)  

  * RG = Redundancy Group  

  * RTO = Real Time Objects (states to synchronize: sessions, NAT, ALG, IPsec…)

Terminology used for MNHA:  

  * MNHA = MultiNode High Availability  

  * ICL = Inter Chassis Link (similar to CTRL link)  

  * ICD = Inter Chassis Datapath (similar to FAB link)  

  * IDL = Inter Domain Link (more than 2 nodes scenario)  

  * SRG = Service Redundancy Group (similar to RG)  

  * RTO = Real Time Objects 

Junos Terminology:  

  * RE = Routing Engine on Junos  

  * NSR = Non Stop Routing (allowing protocols such as BGP to hold its route states when RE restarts)  

  * ISSU = In Service Software Update (updating the 2 nodes of a cluster, one at a time, without disturbing traffics)

Network Layers:  

  * L2 = simple Layer 2 network, i.e. same IP broadcast domain  

  * L2NG = Layer 2 with extended L2/switching features  

  * L3 = Layer 3, refers to routed networks  

  * L2-L3 = mix of Layer 2 and Layer 3, also named Hybrid  

  * L3-L7 = L3 + Layer 4 (TCP/UDP/ICMP/…) to Layer 7 (applications such as HTTP/S, FTP, DNS, etc…)

### Comments

If you want to reach out for comments, feedback or questions, drop us a mail at:

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/rAX6IO6zReO0h0BuHqZH_mail.png)

### Revision History

**Version** | **Author(s)** | **Date** | **Comments**  
---|---|---|---  
1 | Laurent Paumelle | February 2026 | Initial Publication  
  
[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)

  
[#SRXSeries](https://community.juniper.net/search?s=tags%3A%22SRX Series%22&executesearch=true)
