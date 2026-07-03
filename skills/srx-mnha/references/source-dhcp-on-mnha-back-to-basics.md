# Source: DHCP on MNHA:  Back to Basics

Extracted from: dhcp-on-mnha-back-to-basics.html

Selected selector: after-title row.margin-top-large .col-md-12

---

[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)

![DHCP on MNHA:  Back to Basics](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/XuCKvkePSoK0lbSq5q0A_Banners TechPost-16.png)

Multi-Node High Availability (MNHA) is increasingly common as an alternative to chassis cluster. One operational question that surfaces quickly in MNHA deployments is Dynamic Host Configuration Protocol (DHCP). As of Junos 25.4R1, each node runs an independent DHCP process with no lease database synchronization between them. Unlike chassis cluster, DHCP state is not replicated across nodes. Left unaddressed, both nodes will respond to client Discovers, may offer addresses from overlapping ranges, and will produce a split lease database. This post covers the observed behavior and provides practical configurations.  

# Introduction  

We're not going to take a deep dive into MNHA or RFC 2131. The focus is on hybrid and default gateway mode MNHA deployments that leverage a Virtual IP (VIP) floating between nodes and IPv4 DHCP interactions. Two solutions exist for providing DHCP on an MNHA subnet. The first is to relay to a remote DHCP server, which is straightforward and included here for completeness. The second is to use the SRX nodes as local DHCP servers.

This post assumes familiarity with MNHA fundamentals. If you need a refresher before diving in:  

  * [Multi-Node High Availability Basics](https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3 "https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3") — Steven Jacques covers ICL mechanics, SRG0, session synchronization, and config sync.  

  * [Hybrid MNHA with eBGP](https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3 "https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3") — hybrid deployment mode, BFD-driven failover, signal routes, and VIP behavior. The VIP mechanics in this post build directly on that content.  

  * [SRX clustering: from Chassis Cluster to MultiNode High Availability](https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha "https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha") — Laurent Paumelle's architectural overview of MNHA modes, SRG taxonomy, VIP/vMAC behavior, and platform support. Good context for the Default Gateway and Hybrid mode VIP mechanics that underpin the DHCP behavior discussed here.  

# DHCP Quick Reference  

DORA describes the four-message exchange a client uses to obtain a DHCP address for the first time: Discover, Offer, Request and Acknowledgement. Two options are particularly relevant with MNHA behavior, Option 50 and Option 54 (Table 1).  

**Message** | **Direction** | **Key Options** | **Purpose**  
---|---|---|---  
Discover | Client → Broadcast | Option 50  
Requested IP (if client has prior lease)  
| Client solicits any available DHCP server  
Offer | Server → Client | Option 54  
Server Identifier (server's IP) | Server proposes address   
and lease terms  
Request | Client → Broadcast | Option 54  
identifies accepted server  
Option 50  
requested address | Client accepts one offer, broadcasts choice to all servers  
Acknowledge | Server → Client  | Option 54  
confirming server identity | Server confirms,  
lease is now bound  
  
_Table 1. DORA and Options 50 and 54_  

Once a client has an IP bound, two timers govern the lease lifecycle:  

**T1 - Renewal (default 50% of lease time)** : The client unicasts a DHCPREQUEST to the server identified in Option 54 of its lease. A server ACK renews the lease. A server NAK causes the client to immediately drop the lease and restart DORA. No response at T1 means the client holds the address and waits for T2.  

**T2 - Rebind (default 87.5% of lease time)** : The client broadcasts a DHCPREQUEST to any available server. Any server recognizing the lease can ACK it. If no server responds before the lease expires, the client drops the address and restarts DORA from scratch.  

Option 54 requires particular attention in MNHA deployments. It determines which IP the client unicasts to at T1. In deployments where two independent nodes can both issue leases, that single value drives the behavior documented in this post.  

# MNHA: Two Nodes – One Subnet  

With both nodes serving DHCP on the same subnet, both nodes receive every client Discover and both can respond with an Offer. The client accepts one, broadcasts a Request citing its chosen server via Option 54, and expects a single ACK. What ends up in the client's lease file depends entirely on how pool ranges and the server-identifier are configured on each node.   

Configuration options are covered in detail later. The lab environment and observed behavior below use Option 2, split pools with a shared VIP server-identifier, as the baseline.  

## Lab Environment

_![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/953dc33556914c7bb4947c5e565b1625.png)_

_Figure 1. Lab Topology_

The lab topology (Figure 1) consists of two vSRX configured in MNHA hybrid mode. Service Redundancy Group 2 (SRG2) supports a Virtual IP (VIP) of 192.168.252.1 via their respective client facing interfaces, GE-0/0/0.0. The VIP will only be installed on the active node for the MNHA pair. Physical interface IP addresses are 192.168.252.9 (VSRX-A) and 192.168.252.10 (VSRX-B). Four DHCP clients are connected on the shared LAN segment   
for 192.168.252.0/24.   

## Baseline DHCP Configurations  

The configurations begin with assigning an IP address to the physical interfaces (GE-0/0/0.0). In the lab environment, we’ll be using a routing-instance called PROD where the client facing interfaces are associated. GE-0/0/0.0 belongs to the INT security zone. The security zone needs to allow DHCP requests inbound or they will be silently dropped. The following shows these, as well as the DHCP, configurations per node:

MNHA-VSRX-A
    
    
    set interfaces ge-0/0/0 unit 0 family inet address 192.168.252.9/24  
    set routing-instances PROD interface ge-0/0/0.0  
    set security zones security-zone INT host-inbound-traffic system-services dhcp  
    
    set routing-instances PROD system services dhcp-local-server group MNHA-252 interface ge-0/0/0.0  
    
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet network 192.168.252.0/24  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet range DHCP-POOL-1 low 192.168.252.211  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet range DHCP-POOL-1 high 192.168.252.222  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes maximum-lease-time 3600  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes server-identifier 192.168.252.1  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes domain-name winlab.local  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes name-server 192.168.99.100  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes name-server 8.8.8.8  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes router 192.168.252.1

MNHA-VSRX-B
    
    
    set interfaces ge-0/0/0 unit 0 family inet address 192.168.252.10/24  
    set routing-instances PROD interface ge-0/0/0.0  
    set security zones security-zone INT host-inbound-traffic system-services dhcp  
    
    set routing-instances PROD system services dhcp-local-server group MNHA-252 interface ge-0/0/0.0  
    
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet network 192.168.252.0/24  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet range DHCP-POOL-1 low 192.168.252.201  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet range DHCP-POOL-1 high 192.168.252.210  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes maximum-lease-time 3600  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes server-identifier 192.168.252.1  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes domain-name winlab.local  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes name-server 192.168.99.100  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes name-server 8.8.8.8  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes router 192.168.252.1

_Note: the lease time of 1 hour is intentional for lab testing._  

# Observations  

MNHA-VSRX-B is the active node for SRG2 and holds the VIP (192.168.252.1). Both nodes configure the VIP as their DHCP server-identifier (Option 54). From a client's perspective there is a single DHCP server on the subnet regardless of which node responds.
    
    
    MNHA-VSRX-A  
    show chassis high-availability services-redundancy-group 2   
    …  
    Services Redundancy Group: 2  
            Deployment Type: HYBRID  
            Status: BACKUP  
            Activeness Priority: 200  
    …  
              Index: 2         
              IP: 192.168.252.1/24  
              VMAC: N/A          
              Interface: ge-0/0/0.0        
              Status: NOT INSTALLED  
    …  
    
    MNHA-VSRX-B  
    show chassis high-availability services-redundancy-group 2   
    …  
    
    Services Redundancy Group: 2  
            Deployment Type: HYBRID  
            Status: ACTIVE  
            Activeness Priority: 100  
    …  
    
              Index: 2         
              IP: 192.168.252.1/24  
              VMAC: N/A          
              Interface: ge-0/0/0.0        
              Status: INSTALLED

_Note: In this scenario, MNHA-VSRX-B is showing active with a lower Activeness priority is intentional. Preemption isn’t configured to promote MNHA-VSRX-A to active status despite the higher priority._  

One familiar with MNHA configurations may point to the ‘process-packet-on-backup’ knob as a prerequisite for the backup node to participate in DHCP. However, the ‘process-packet-on-backup' is specific to IPSec configurations. The backup node participates in DORA regardless of that setting (a function of jdhcpd running independently on each node).  

In testing, MNHA-VSRX-A (the backup node) won the offer race consistently for certain clients, while MNHA-VSRX-B was quickest for other clients. In production environments this is timing-dependent and either node may respond first on any given DORA cycle. The specific node that wins the offer race on any given transaction is less important than understanding that both nodes will participate and the resulting behavior related to cross-node NAK traffic, split lease databases, and T1 renewal interactions. Figure 2 highlights the backup node winning the race. 

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/00db091adad34d3495f26eaf8b8b40e4.png)

Figure 2. 000C:29DD:855E – DORA Sequence  

A client at 00:0c:29:dd:85:5e broadcasts a Discover. MNHA-VSRX-A (192.168.252.9), the backup node, replies first with an Offer at 05:53:51.252 — 2ms after the Discover. The client accepts the first Offer received and commits to that server for the transaction, broadcasting a Request that cites VSRX-A via Option 54. MNHA-VSRX-A ACKs at 05:53:51.273 and the client binds to 192.168.252.216. The active node's Offer arrives at 05:53:51.384 — 130ms after the Discover and well after the transaction is complete. It is silently discarded. The binding is recorded in VSRX-A's lease database only.  

## Split Lease Database  

With both nodes advertising the VIP (192.168.252.1) as their server-identifier, from the client's perspective there is a single DHCP server on the subnet. As previously mentioned, both nodes participate in the DHCP process. The results are evident when viewing the bindings from each of the nodes creating a split lease database. 
    
    
    MNHA-VSRX-A  
    show dhcp server binding routing-instance PROD  
    IP address        Session Id  Hardware address   Expires  State      Interface  
    192.168.252.201   92          ca:fe:c0:ff:ee:10  2906     BOUND      ge-0/0/0.0  
    192.168.252.204   32          ca:fe:c0:ff:ee:11  3094     BOUND      ge-0/0/0.0  
    
    MNHA-VSRX-B  
    show dhcp server binding routing-instance PROD  
    IP address        Session Id  Hardware address   Expires  State      Interface  
    192.168.252.211   1           00:0c:29:bb:5f:a9  2961     BOUND      ge-0/0/0.0  
    192.168.252.216   21          00:0c:29:dd:85:5e  3144     BOUND      ge-0/0/0.0

Neither node has any visibility into the other's bindings. From VSRX-B's perspective, .211 and .216 are unassigned addresses. From VSRX-A's perspective, .201 and .204 are unassigned. Four clients on the same /24 subnet, two independent lease databases, no coordination between the nodes.  

## Cross-Node NAK and T1 Renewals  

T1 renewal behavior with a shared VIP server-identifier depends entirely on which node issued the original lease. The two captures below show the same subnet, the same configuration, and two clients with different outcomes. Figure 3 shows a client receiving its lease from the active node (MNHA-VSRX-B). At T1 it unicasts a DHCPREQUEST to 192.168.252.1, the VIP installed on VSRX-B. VSRX-B has the binding and ACKs cleanly. The pattern repeats every 30 minutes without interruption across 7+ hours of captures. No NAKs, no DORA restarts, no disruption.  

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/053a1e6eb6a2463cb0e58f9504f22d1d.png)

_Figure 3. T1 Renewal Sequence, Active Node Issued Lease_  

Figure 4 further highlights the behavior of when the backup node wins the race and subsequent NAKs from the active node. When the client at 192.168.252.216 unicasts a DHCPREQUEST to the active node for an address outside its pool range, MNHA-VSRX-B NAKs, triggering a full DORA cycle. The subsequent DORA resolves back to MNHA-VSRX-A, which re-offers the same address. The client maintains the same IP address throughout with no connectivity impact. The cross-node NAK traffic produces measurable protocol overhead visible in the statistics and on the wire, but no client impact. 

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/552733e8b90c416491a46792b4d096ba.png)

_Figure 4. T1 Renewal Failures, Backup Node Issued Lease_  

The DHCP server statistics holistically confirm the cross-node NAK traffic the shared VIP server-identifier produces.
    
    
    MNHA-VSRX-A  
    show dhcp server statistics routing-instance PROD  
    DHCPDISCOVER     51    received  
    DHCPOFFER        51    sent  
    DHCPREQUEST      73    received  
    DHCPACK          49    sent  
    DHCPNAK           3    sent  
    DHCPINFORM        1    received  
    Packets dropped:  0  
    
    MNHA-VSRX-B  
    show dhcp server statistics routing-instance PROD  
    DHCPDISCOVER     53    received  
    DHCPOFFER        53    sent  
    DHCPREQUEST     131    received  
    DHCPACK          32    sent  
    DHCPNAK          49    sent  
    DHCPINFORM        1    received  
    No binding found  31   dropped

The 31 "no binding found" drops are unicast T1 renewal attempts from clients whose leases were issued by the backup node. The active node has no binding record and drops them silently.  

## Lease Behavior on Node Loss  

With both nodes operational the client always rebounds to the same address. No IP change, no session disruption. 

If either node becomes unavailable due to a hard failure, client-facing interface failure, routing loss, or split-brain, its lease database is gone or inaccessible. Outcomes depend on which node issued the lease. For leases issued by the active node, T1 unicasts hit the VIP and are ACKed. The active node holds the binding. For leases issued by the backup node, T1 unicasts hit the VIP on the surviving node which has no binding and NAKs. The client restarts DORA and receives a new address from the surviving node's pool. Clients holding leases from the failed node's pool range get re-addressed. That IP change is what disrupts established sessions.

The same applies to backup node loss. A backup node failure produces no VIP movement. The active node stays active and traffic continues normally. Clients in the backup's pool range are silently orphaned. When their T1 or T2 renewal attempts go unanswered they eventually broadcast a fresh Discover and are re-addressed by the active node.

The disruption window is bounded by the lease lifecycle. A client is only re-addressed when a renewal or rebind attempt falls within a period where the issuing node is unreachable. Outside those windows the client holds its address unaffected. This is why lease time is a risk management decision in MNHA deployments. 

Lease time determines how long a client can ride out a loss of reachability to the issuing node before a renewal attempt forces re-addressing. With a 24-hour lease a client that just renewed has up to 12 hours before T1 fires. If the failed node recovers within that window the client renews successfully without disruption. If the node remains unavailable through T1 and T2 the client broadcasts a fresh Discover and gets re-addressed. Shorter leases shorten that tolerance window. Longer leases extend it at the cost of slower recovery when re-addressing is warranted.  

# MNHA DHCP Configuration Options  

Four DHCP configurations are possible in conjunction with MNHA, summarized in Table 2. Three host local DHCP services while the fourth leverages remote DHCP servers via DHCP relay. Remote DHCP servers eliminate the split database and potential NAK behavior inherent to local DHCP on MNHA nodes.

The server-identifier (Option 54) is the variable that distinguishes Options 2 and 3. It controls which IP appears in the client's lease file as the T1 renewal target, therefore which node receives that client's unicast at renewal time. Options 2 and 3 both use split pools. Option 1 does not use split pools and is not recommended.

| **Option 1: Overlapping or Duplicate Pools** | **Option 2: Split Pools  
(SID = VIP)** | **Option 3: Split Pools  
(SID = Node)** | **Option 4: DHCP Relay**  
---|---|---|---|---  
Duplicate addresses | Yes | No | No | No  
Cross-Node NAK | Yes | Yes | No | No  
IP change -  
both nodes up | Possible | No — rebinds same IP | No — rebinds same IP | No  
IP change - node down/unreachable | Yes | Yes (T1 window) | Yes (lease expiry window) | No  
Post-failure disruption window | Severe | Up to ½ lease time | Up to full lease time | None  
Soft/planned failover impact | None | None | None | None  
Lease database split | Yes | Yes | Yes (by design) | No  
External dependency | No | No | No | Yes  
Recommended | **Never** | No | Yes | Yes (if available)  
  
_Table 2. MNHA DHCP Configurations_

## Option 1 – Overlapping Pools  

Overlapping or identical pool ranges on both nodes result in duplicate IP assignments. Two clients can hold the same address, both believing their lease is valid. This typically surfaces as intermittent connectivity failures and ARP conflicts that are difficult to diagnose. The most common cause is copying pool configuration from one node to the other without adjusting the range. With overlapping pools, the server-identifier is irrelevant. The address collision occurs regardless of what Option 54 contains.

Duplicate assignments from overlapping pools are not a theoretical risk. They are an expected outcome at scale. Avoid this configuration entirely.

## Option 2 – Split Pools, Shared VIP Server Identifier  

Each node serves a non-overlapping range. Both nodes advertise the VIP as server-identifier. This is the configuration detailed in the Observations section above.

**Normal Operation** : Pools are non-overlapping so duplicate address assignment is not a concern. Both nodes independently serve their ranges. Cross-node NAK traffic is generated when clients broadcast Requests for addresses in the other node's range. Clients complete DORA through retry cycles. This is overhead, not a blocking condition.

**Soft Failover** : Both nodes remain operational with lease databases intact. At T1, clients unicast to the VIP and whichever node holds the binding ACKs cleanly. Clients in either pool range rebind to the same address without disruption.

**Node Down or Unreachable** : The node that issued the lease is gone or inaccessible. At T1 the client unicasts to the VIP on the surviving node. The surviving node NAKs because the requested address is in the failed node's pool range. The client restarts DORA and receives a new address from the surviving node's pool. The IP change disrupts established sessions.

**Verdict** : Produces measurable cross-node NAK traffic during normal operation. Re-addressing on node loss is faster than Option 3 because the T1 NAK forces a fresh DORA within minutes of the event. Not recommended for production due to NAK overhead.

## Option 3 – Split Pools, Per-Node Server Identifier  

Each node serves a non-overlapping range and uses its own physical IP as server-identifier. The router option still points to the VIP so clients use the VIP as their default gateway regardless of which node issued the lease.
    
    
    MNHA-VSRX-A  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes server-identifier 192.168.252.9  
    
    MNHA-SRX-B  
    set routing-instances PROD access address-assignment pool DHCP-MNHA-252 family inet dhcp-attributes server-identifier 192.168.252.10

**Normal Operation** : No duplicate address assignment. No cross-node NAK traffic. Each node only processes Requests that cite its own physical IP in Option 54. T1 renewals unicast directly to the issuing node and are ACKed. Lease databases remain authoritative per node.

Figures 5 and 6 show T1 renewal behavior for clients issued by each node respectively. T1 unicasts go directly to the issuing node's physical IP. Both renew without NAKs or DORA restarts. The cross-node NAK traffic observed in Option 2 is absent entirely.

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/2a30076b896e44f6b5ffff6a21828f86.png)

_Figure 5. MNHA Active Node, per-node sever-identifier_

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/MessageImages/a590d09f626344b1a8e05a43fc107e3e.png)

_Figure 6. MNHA Backup Node, per-node sever-identifier_

**Soft Failover** : Both nodes remain operational with lease databases intact. T1 unicasts reach the issuing node directly for a clean renewal. Soft and monitoring-triggered failovers are completely transparent to DHCP regardless of which node is active.

**Node Down or Unreachable** : The issuing node's lease database is gone or inaccessible. Clients attempt T1 renewal to that node's physical IP with no response at T1 or T2. The client waits until lease expiry, broadcasts a fresh Discover, and receives a new address from the surviving node's pool. The IP change disrupts established sessions. This applies equally to active or backup node loss. Backup node loss produces no VIP movement to signal the event. Clients in that pool range are silently orphaned until their lease expires.

_Note: Per-node server-identifier produces a longer post-failure re-addressing window than Option 2. With a shared VIP, the T1 NAK fires quickly and forces re-addressing within minutes. With per-node identifiers, the client waits silently through T1 and T2 before restarting DORA. Shorter lease times directly correlate to how long clients remain orphaned after a node failure. Tune accordingly._

**Verdict** : Correct architecture for local DHCP on MNHA. Clean normal operation with no cross-node NAK traffic. Recommended for production deployments.

## Option 4 – DHCP Relay  

Both nodes relay DHCP traffic to an external server. Single authoritative lease database. No split pools required.
    
    
    MNHA-VSRX-A & MNHA-SRX-B  
    set routing-instances <RI> forwarding-options dhcp-relay group RELAY-GROUP active-server-group DHCP-SERVERS  
    set routing-instances <RI> forwarding-options dhcp-relay server-group DHCP-SERVERS <IP_ADDR>  
    set routing-instances PROD forwarding-options dhcp-relay group RELAY-GROUP interface <INT>

Eliminates the MNHA DHCP problem entirely. A single lease database means no NAK traffic, no split pools, and no post-failover re-addressing. Failover is transparent to DHCP. Both nodes relay to the same server and the server's bindings are unaffected by which SRX is active.

Adds a dependency on external server availability and relay path reachability. If either fails, DHCP stops working for the subnet.   

# MNHA Local DHCP Server Recommendations  

The following recommendations apply to MNHA deployments using local DHCP servers on the nodes. If off-node relay is available and continuity is a hard requirement, use it. For local DHCP the recommendations below produce stable normal operation with predictable failover behavior.

  * Split the pool — always  

  * Use per-node physical IP as server-identifier  

  * Exclude peer physical IPs from the pool  

  * Mirror static reservations on both nodes  

  * Monitor pool utilization by binding count  

  * Include DHCP binding cleanup in planned failover Method of Procedures (MOPs)

## Split the Pool - Always  

Even with per-node server-identifiers, overlapping pools risk duplicate address assignment. Non-overlapping ranges per node are the only safe configuration for local DHCP on MNHA. A /24 split between two nodes yields approximately 126 usable addresses per node, which is sufficient for most branch deployments.

## Per-Node Physical IP as Server-Identifier  

Set the server-identifier on each node to its own physical interface IP, not the VIP. Set the router option to the VIP on both nodes. Clients get the correct default gateway while each node's DHCP transactions remain self-contained. No cross-node NAK traffic during normal operation and T1 renewals unicast directly to the issuing node.

## Exclude Peer Physical IPs from the Pool  

Explicitly exclude each node's peer physical IP from the pool to prevent accidental assignment:
    
    
    MNHA-VSRX-A & MNHA-SRX-B  
    set routing-instances <RI> access address-assignment pool <POOL> family inet excluded-address <IP_ADDR>

## Mirror Static Reservations on Both Nodes  

Static host reservations must be configured identically on both nodes. A device with a reservation on one node only will receive a dynamic address from the pool if the other node handles its next DORA. For devices requiring address stability, identical static reservations on both nodes are more reliable than relying on short lease times.
    
    
    MNHA-VSRX-A & MNHA-SRX-B  
    set routing-instances <RI> access address-assignment pool <POOL> family inet host <NAME> hardware-address <MAC_ADDR>  
    set routing-instances <RI> access address-assignment pool <POOL> family inet host PRINTER-01 ip-address <IP_ADDR>

## Monitor Pool Utilization by Binding Count  

jdhcp does not provide a native pool utilization command. The show dhcp server pool command does not exist. Derive utilization by counting bindings against the configured range:
    
    
    show dhcp server binding routing-instance <RI> | count  
    # Compare result against pool range size to determine available addresses

## Include DHCP Binding Cleanup in Planned Failover MOPs  

For planned maintenance, always clear bindings on the surviving node before triggering failover. This is the single most impactful operational procedure for minimizing post-failover DHCP disruption. With bindings cleared, clients get re-addressed on their next DORA cycle. The re-addressing window collapses to seconds rather than the remaining lease duration.
    
    
    # Run on the node that will survive the failover  
    clear dhcp server binding routing-instance <RI> all  
    
    # Then trigger failover  
    request chassis high-availability failover peer-id <ID> services-redundancy-group <SRG>

## A Note on IPv6  

MNHA currently supports a single IPv4 or IPv6 VIP per logical interface per SRG — dual-stack VIPs are not supported. Junos OS 25.4R1 extended IPv6 support to MNHA control plane signaling (signal routes, activeness probes, install-on-failure routes) but this does not extend to data-plane VIPs. The VIP mechanism that provides default gateway and DHCP server-identifier anchoring remains constrained to a single address family per interface. DHCPv6 as a client addressing mechanism under MNHA is architecturally limited by this. Dual-stack VIP support is noted as planned in Juniper's documentation but has no published release timeline. For now, MNHA DHCP is an IPv4 conversation.  

# Summary  

MNHA's independent control planes are a feature, not a limitation. For DHCP, that independence has consequences worth understanding before deployment. Leverage an external DHCP server when available. It sidesteps the split database, the NAK traffic, and the T1 renewal complexity entirely. When local DHCP is the only option, split the pools and use per-node server-identifiers. The captures don't lie.

Embrace the ACKs. Avoid the NAKs.  

## Useful links

  * Multi-Node High Availability Basics: <https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics>  

  * Hybrid MNHA with eBGP: <https://community.juniper.net/blogs/james-rathbun/2025/06/12/hybrid-mnha-with-ebgp>  

  * SRX clustering: from Chassis Cluster to MultiNode High Availability: https://community.juniper.net/blogs/laurentp/2026/02/15/srx-from-chassis-cluster-to-mnha  

  * Juniper MNHA Documentation: <https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html>  

  * Junos DHCP User Guide: <https://www.juniper.net/documentation/us/en/software/junos/dhcp/dhcp.pdf>  

  * MNHA Preparation (VIP limitations): <https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/concept/mnha-preparation.html>  

## Glossary  

  * ACK - Acknowledgment  

  * DHCP – Dynamic Host Configuration Protocol  

  * jdhcpd – Extended DHCP daemon  

  * MNHA – Multi-Node High Availability  

  * NAK/DHCPNAK – DHCP Negative Acknowledgement  

  * RTO – Real Time Object  

  * SRG – Service Redundancy Group  

  * VIP – Virtual IP  

## Acknowledgements  

The collective team that reviewed and provided valuable feedback, namely Scott Astor and Karel Hendrych. Plus... Nicolas Fevrier for overseeing the Tech Posts site and handling all the publishing tasks.

### Comments

If you want to reach out for comments, feedback or questions, drop us a mail at:

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/rAX6IO6zReO0h0BuHqZH_mail.png)

### Revision History

**Version** | **Author(s)** | **Date** | **Comments**  
---|---|---|---  
1 | James Rathbun | April 2026 | Initial Publication  
  
[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)
