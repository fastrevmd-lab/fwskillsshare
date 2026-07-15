# Source: Hybrid MNHA with eBGP

Extracted from: hybrid-mnha-with-ebgp.html

Selected selector: after-title row.margin-top-large .col-md-12

---

[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)

![Hybrid MNHA with eBGP](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/dbXft6kPReeQX8ChUI7C_Banners TechPost-3.png)

Let's highlight the flexibility of Multi-Node High Availability (MNHA) and JUNOS while providing design considerations when implementing MNHA in a hybrid deployment model.

# Introduction

Every network environment is unique and has different requirements and caveats. The focus will be on:

  * Implementation considerations

  * Monitoring/Failover scenarios

  * MNHA functionality and traffic flows (with hybrid deployments)

Steven Jacques’ post, [Multi-Node High Availability](https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3 "https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics?CommunityKey=44efd17a-81a6-4306-b5f3-e5f82402d8d3") is an excellent post covering the basics and MNHA and Layer 3 (L3) implementations.

### Objectives

High level topology (Figure 1) represents a topology having a Layer 2 (L2) hand-off to an external network, a Layer 3 (L3) internal hand-off demarcated by a pair of SRXs. MNHA hybrid designs provide flexibility of L2 hand-offs (internal/external). Objectives validated:

  * RTRs (RTR-1 and RTR-2) send L3 untagged packets (routed) to the SRXs (SRX-1 and SRX-2)

  * RTRs also send L2 tagged packet to the SRXs (SRXs will provide default gateway functionality)

  * RTRs have redundant connections, crossed (bowtie) with the SRXs

  * Northbound connections from the SRXs provide default gateway functionality with the external network.
  * High availability (HA) implementation with fast stateful failover.

__

![Figure 1.  High Level Topology](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/HnW87jaiRO2tAxfKtUJN_Hybrid MNHA-01.png)

_Figure 1. High Level Topology_

![Figure 2.  Reference Layer 2/3 Topology](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/dVmpT38DQa6lm4qylz7r_Hybrid MNHA-02.png)

_Figure 2. Reference Layer 2/3 Topology_

L2 gateways (floating) on the SRXs are 192.168.252.254 (UNTRUST) and 192.168.253.1 (TRUST).

Note: ICL traffic can be encrypted, however, this example does not use an encrypted ICL. If terminating IPSec VPNs ICL encryption is a requirement. Configuring encryption on the ICL later may be disruptive to a production environment. Also, configuring ICL in its own routing instance is a good practice to isolate the ICL forwarding instance from other data path forwarding information.

# Border Gateway Protocol (BGP)

Figure 3 shows the BGP Autonomous System (AS) configuration used during testing. RTR-1 and RTR-2 iBGP peer each other (AS65012) and eBGP peer to both SRX-1 and SRX-2 in AS65022. With a “bow-tie” design, both routers (RTR-1 and RTR-2) can forward traffic to the active SRX. An external BGP speaker, RTR-X (AS65002), allows for ECMP traffic flows to RTR-1 and RTR-2.

![Figure 3.  BGP AS Topology](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/7j0wHvIqTdi7aH2iiON7_Hybrid MNHA-03.png)

_Figure 3. BGP AS Topology_

Any BGP traffic engineering method can be used to influence active/backup paths (e.g. path prepend, local pref, etc.), however, this example modifies the Multi-Exit Discriminator (MED) for active/back-up advertisements from the SRXs to the RTRs for 192.168.252.0/24 based on the Service Redundancy Group (SRG) activeness and presence of signal routes.


    MNHA-RTR-1> show bgp summary 

    Threading mode: BGP I/O
    Default eBGP mode: advertise - accept, receive - accept
    Groups: 4 Peers: 5 Down peers: 0
    Table          Tot Paths  Act Paths Suppressed    History Damp State    Pending
    inet.0               
                          72         33          0          0          0          0
    Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
    10.10.99.5            65022       2155       2124       0       0    16:06:17 Establ
      inet.0: 6/8/8/0
    10.10.99.131          65022       2146       2122       0       0    16:05:46 Establ
      inet.0: 2/8/8/0
    10.10.101.2           65012       2138       2128       0       0    16:06:59 Establ
      inet.0: 0/30/30/0
    192.168.99.1          65002       2221       2126       0       0    16:06:54 Establ
      inet.0: 25/26/26/0

(RTR-1 BGP Peers)


    MNHA-RTR-2> show bgp summary    

    Threading mode: BGP I/O
    Default eBGP mode: advertise - accept, receive - accept
    Groups: 4 Peers: 5 Down peers: 0
    Table          Tot Paths  Act Paths Suppressed    History Damp State    Pending
    inet.0               
                          75         33          0          0          0          0
    Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
    10.10.99.69           65022          5          4       0       0           9 Establ
      inet.0: 3/8/8/0
    10.10.99.195          65022       1967       1950       0       1    14:44:51 Establ
      inet.0: 5/8/8/0
    10.10.101.1           65012       2149       2159       0       0    16:15:59 Establ
      inet.0: 0/33/33/0
    10.10.201.1           65100       2145       2150       0       0    16:16:04 Establ
      VR_ALT.inet.0: 1/1/1/0
    192.168.99.1          65002       1541       1479       0       1    11:10:34 Establ
      inet.0: 25/26/26/0

(RTR-2 BGP Peers)


    MNHA-SRX-1> show bgp summary 

    Threading mode: BGP I/O
    Default eBGP mode: advertise - accept, receive - accept
    Groups: 1 Peers: 2 Down peers: 0
    Table          Tot Paths  Act Paths Suppressed    History Damp State    Pending
    inet.0               
                          50         50          0          0          0          0
    Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
    10.10.99.1            65012       2146       2174       0       0    16:15:54 Establ
      inet.0: 25/25/25/0
    10.10.99.65           65012          6          5       0       0          46 Establ
      inet.0: 25/25/25/0

(SRX-1 BGP Peers)


    MNHA-SRX-2> show bgp summary

    Threading mode: BGP I/O
    Default eBGP mode: advertise - accept, receive - accept
    Groups: 1 Peers: 2 Down peers: 0
    Table          Tot Paths  Act Paths Suppressed    History Damp State    Pending
    inet.0               
                          50         50          0          0          0          0
    Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
    10.10.99.129          65012          8          6       0       0        1:22 Establ
      inet.0: 25/25/25/0
    10.10.99.193          65012          7          5       0       0        1:11 Establ
      inet.0: 25/25/25/0

(SRX-2 BGP Peers)


    MNHA-RTR-1> show configuration protocols bgp | display set 
    set protocols bgp group EXT type external
    set protocols bgp group EXT multihop ttl 4
    set protocols bgp group EXT local-address 192.168.99.178
    set protocols bgp group EXT local-as 65012
    set protocols bgp group EXT multipath multiple-as
    set protocols bgp group EXT bfd-liveness-detection minimum-interval 500
    set protocols bgp group EXT bfd-liveness-detection multiplier 3
    set protocols bgp group EXT neighbor 192.168.99.1 peer-as 65002
    set protocols bgp group INT type internal
    set protocols bgp group INT export NHS
    set protocols bgp group INT local-as 65012
    set protocols bgp group INT bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group INT bfd-liveness-detection multiplier 3
    set protocols bgp group INT neighbor 10.10.101.2
    set protocols bgp group INT-ebgp type external
    set protocols bgp group INT-ebgp local-as 65012
    set protocols bgp group INT-ebgp bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT-ebgp bfd-liveness-detection multiplier 3
    set protocols bgp group INT-ebgp bfd-liveness-detection holddown-interval 10000
    set protocols bgp group INT-ebgp neighbor 10.10.99.131 peer-as 65022
    set protocols bgp group INT-ebgp neighbor 10.10.99.5 peer-as 65022

_(RTR-1 BGP Configuration)_


    MNHA-RTR-2> show configuration protocols bgp | display set 
    set protocols bgp group unINT type external
    set protocols bgp group unINT local-address 192.168.99.179
    set protocols bgp group unINT local-as 65012
    set protocols bgp group unINT multipath multiple-as
    set protocols bgp group unINT bfd-liveness-detection minimum-interval 500
    set protocols bgp group unINT bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group unINT bfd-liveness-detection multiplier 3
    set protocols bgp group unINT neighbor 192.168.99.1 peer-as 65002
    set protocols bgp group INT type internal
    set protocols bgp group INT export NHS
    set protocols bgp group INT local-as 65012
    set protocols bgp group INT bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT bfd-liveness-detection multiplier 3
    set protocols bgp group INT neighbor 10.10.101.1
    set protocols bgp group INT-ebgp local-as 65012
    set protocols bgp group INT-ebgp bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT-ebgp bfd-liveness-detection multiplier 3
    set protocols bgp group INT-ebgp bfd-liveness-detection holddown-interval 10000
    set protocols bgp group INT-ebgp neighbor 10.10.99.69 peer-as 65022
    set protocols bgp group INT-ebgp neighbor 10.10.99.195 peer-as 65022

(RTR-2 BGP Configuration)


    MNHA-SRX-1> show configuration protocols bgp | display set 
    set protocols bgp group trust type external
    set protocols bgp group trust export MNHA_ROUTE_POLICY
    set protocols bgp group trust local-as 65022
    set protocols bgp group trust multipath
    set protocols bgp group trust bfd-liveness-detection minimum-interval 500
    set protocols bgp group trust bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group trust bfd-liveness-detection multiplier 3
    set protocols bgp group trust bfd-liveness-detection holddown-interval 10000
    set protocols bgp group trust neighbor 10.10.99.1 peer-as 65012
    set protocols bgp group trust neighbor 10.10.99.65 peer-as 65012

(SRX-1 BGP Configuration)


    MNHA-SRX-2> show configuration protocols bgp | display set 
    set protocols bgp group trust type external
    set protocols bgp group trust export MNHA_ROUTE_POLICY
    set protocols bgp group trust local-as 65022
    set protocols bgp group trust multipath multiple-as
    set protocols bgp group trust bfd-liveness-detection minimum-interval 500
    set protocols bgp group trust bfd-liveness-detection multiplier 3
    set protocols bgp group trust bfd-liveness-detection holddown-interval 10000
    set protocols bgp group trust neighbor 10.10.99.129 peer-as 65012
    set protocols bgp group trust neighbor 10.10.99.193 peer-as 65012

(SRX-2 BGP Configuration)

### BGP Bi-Directional Liveliness Detection

Bidirectional Forwarding Detection (BFD) is not effective until there is an initial session established between the peers (transitioned from INIT to UP). Once a session is established, BFD assists in detecting peer connectivity issues, as well as physical layer issues such as downed links (directly connected), one-way links (not registered as down, but only receiving or transmitting), additional non-functioning or “stuck” interface scenarios, etc.

There is no need to adjust the default BGP timers. Testing BFD liveliness to determine neighbor failures in 1.5 seconds (Figure 4) versus default BGP neighbor failures of 180 seconds. 1.5 second failure detection is achieved with 500ms intervals with a multiplier of 3 (500ms x 3 missed = 1500ms). Sub second failure detection is just a matter of tuning your BFD intervals. BFD does add overhead – so it’s important to understand your hardware/software/network capabilities. Tuning BFD timers too tightly can cause instability.

BFD is used for both BGP neighbor detection as well as high availability peer detection.


    MNHA-SRX-1> show bfd session 
                                                      Detect   Transmit
    Address                  State     Interface      Time     Interval  Multiplier
    10.10.99.1      ** _(BGP)_**    Up        ge-0/0/0.10    1.500     0.500        3   
    10.10.99.65     **_(BGP)_**    Up        ge-0/0/1.0     1.500     0.500        3   
    100.0.0.1       **_(HA)_**     Up                       2.000     0.400        5   

    3 sessions, 5 clients
    Cumulative transmit rate 6.5 pps, cumulative receive rate 6.5 pps

(BFD Sessions)

### BFD BGP Hold-down

The hold-down is the length of time a stable BFD session is up before bringing up the BGP neighbor. The graph below (Figure 4), shows BFD must be up for 10 seconds before bringing up the BGP session. The hold-down interval is used during testing to highlight a potential convergence event external to the MNHA failover process – discussed further in the Preemption section.

![Figure 4.  Packet Capture at SRX-1, BFD Failure Detection](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/DjU3tyMQMeqso8PXoEv1_Hybrid MNHA-04.png)

_Figure 4. Packet Capture at SRX-1, BFD Failure Detection_

During session flaps, BFD timers (by default) adapt. If a BFD session flap occurs more than three times in a span of 15 seconds a back-off algorithm increases the receive interval. This feature can be disabled if required.

[Additional BFD information](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/bfd.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/bfd.html") (distributed, centralized, additional considerations).

### MNHA - Activeness

The highest priority determines the active node in the MNHA pair. On SRX-1 and SRX-2:


    set chassis high-availability services-redundancy-group 1 activeness-priority 200

(Activeness configurations)


    MNHA-SRX-1> show chassis high-availability services-redundancy-group 1 
    SRG failure event codes:
        BF  BFD monitoring
        IP  IP monitoring
        IF  Interface monitoring
        CP  Control Plane monitoring

    Services Redundancy Group: 1
            Deployment Type: HYBRID
            **Status: ACTIVE**
            **Activeness Priority: 200**
            Preemption: DISABLED
            Process Packet In Backup State: NO
            Control Plane State: READY
            System Integrity Check: N/A
            Failure Events: NONE
            Peer Information:
              Peer Id: 2
              Status : BACKUP
              Health Status: HEALTHY
              Failover Readiness: READY

(SRX-1 Active status for SRG-1)


    MNHA-SRX-2> show chassis high-availability services-redundancy-group 1 
    SRG failure event codes:
        BF  BFD monitoring
        IP  IP monitoring
        IF  Interface monitoring
        CP  Control Plane monitoring

    Services Redundancy Group: 1
            Deployment Type: HYBRID
            **Status: BACKUP**
            **Activeness Priority: 100**
            Preemption: DISABLED
            Process Packet In Backup State: NO
            Control Plane State: READY
            System Integrity Check: COMPLETE
            Failure Events: NONE
            Peer Information:
              Peer Id: 1
              Status : ACTIVE
              Health Status: HEALTHY
              Failover Readiness: N/A

(SRX-2 Backup status for SRG-1)

### MNHA - Signal Routes

The signal routes are arbitrary and installed locally to the SRXs. However, do not use active prefixes in your environment as this may cause unwanted connectivity issues with those production prefixes. The signal routes used are 169.254.200.1/32 (active) and 169.254.200.2/32 (backup).


    set chassis high-availability services-redundancy-group 1 **active-signal-route** 169.254.200.1
    set chassis high-availability services-redundancy-group 1 **backup-signal-route** 169.254.200.2

(Signal route configuration)

The active (highest activeness priority) will install the “active” signal route while the backup (lowest activeness priority) will install the “backup” signal route in the respective local routing tables.

The active SRX (SRX-1) installs the active signal route 169.254.200.1 and does not have an entry for the backup signal route 169.254.200.2.


    MNHA-SRX-1> show route 169.254.200.0/30

    inet.0: 43 destinations, 70 routes (43 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    169.254.200.1/32   *[Static/12] 16:24:08
                           Receive

    MNHA-SRX-1>

(SRX-1 active signal route)

The backup SRX (SRX-2) installs the backup signal route 169.254.200.2 and does not have an entry for the active signal route 169.254.200.1.


    MNHA-SRX-2> show route 169.254.200.0/30 

    inet.0: 41 destinations, 66 routes (41 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    169.254.200.2/32   *[Static/12] 16:24:47
                           Receive

    MNHA-SRX-2>

(SRX-2 backup signal route)

### BGP Export Policy

The export policy will advertise the 192.168.252.0/24 prefix to respective BGP peers with specified MED if the active route (10) or backup route (20) are present in the routing table.

The policy options and conditions are configured identically on the SRXs.


    MNHA-SRX-1> show configuration policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 | display set 
    set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 **if-route-exists** address-family inet **169.254.200.1/32**
     set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0

    MNHA-SRX-1> show configuration policy-options condition BACKUP_ROUTE_EXISTS_SRG1 | display set    
    set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 **if-route-exists** address-family inet **169.254.200.2/32**
     set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0

(Policy Options)


    MNHA-SRX-1> show configuration | display set | grep MNHA_ 
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from route-filter 192.168.252.0/24 exact
    **set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from condition ACTIVE_ROUTE_EXISTS_SRG1**
     set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then metric 10
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from route-filter 192.168.252.0/24 exact
    **set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from condition BACKUP_ROUTE_EXISTS_SRG1**
     set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then metric 20
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then metric 30
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term default then reject
    set protocols bgp group trust export MNHA_ROUTE_POLICY

(Export Policy)

RTR-1 preferred route to 192.168.252.0/24 is to SRX-1 (active – best metric) and RTR-2 preferred route to 192.168.252.0/24 is also to SRX-1 (active – best metric). If the link (BGP peers) from either RTR-1 or RTR-2 to SRX-1 fails, traffic will be routed across the cross connection between RTR-1 and RTR-2 to reach SRX-1.


    MNHA-RTR-1> show route 192.168.252.0/24 receive-protocol bgp 10.10.99.5  

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
      Prefix                  Nexthop              MED     Lclpref    AS path
    * 192.168.252.0/24        **10.10.99.5**           **10**                 65022 I

    MNHA-RTR-1> show route 192.168.252.0/24 receive-protocol bgp 10.10.99.131  

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
      Prefix                  Nexthop              MED     Lclpref    AS path
      192.168.252.0/24        **10.10.99.131**         **20**                 65022 I

    MNHA-RTR-1> show route 192.168.252.0/24 

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    192.168.252.0/24   *[BGP/170] 16:31:53, **MED 10** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.99.5 via ge-0/0/0.0
                        [BGP/170] 00:17:46, **MED 10** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.101.2 via ge-0/0/3.101
                        [BGP/170] 16:31:22, **MED 20** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.99.131 via ge-0/0/2.0

(RTR-1 route to 192.168.252.0/24)


    MNHA-RTR-2> show route 192.168.252.0/24 receive-protocol bgp 10.10.99.69 

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
      Prefix                  Nexthop              MED     Lclpref    AS path
    * 192.168.252.0/24        **10.10.99.69**          **10**                 65022 I

    MNHA-RTR-2> show route 192.168.252.0/24 receive-protocol bgp 10.10.99.195   

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
      Prefix                  Nexthop              MED     Lclpref    AS path
      192.168.252.0/24        **10.10.99.195**         **20**                 65022 I

    MNHA-RTR-2> show route 192.168.252.0/24                                      

    inet.0: 45 destinations, 87 routes (45 active, 0 holddown, 0 hidden)
    + = Active Route, - = Last Active, * = Both

    192.168.252.0/24   *[BGP/170] 00:19:32, **MED 10** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.99.69 via ge-0/0/2.0
                        [BGP/170] 16:33:38, **MED 10** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.101.1 via ge-0/0/3.101
                        [BGP/170] 15:04:14, **MED 20** , localpref 100
                          AS path: 65022 I, validation-state: unverified
                        >  to 10.10.99.195 via ge-0/0/0.0

(RTR-2 route to 192.168.252.0/24)

# MNHA – L2 Default Gateways

The active SRX will use 192.168.253.1 for VLAN 500 and will use 192.168.252.254 for the north bound L2 hand-off. A failover event will trigger a GARP advertisement to update the connected switching tables when the IP moves from the previously active SRX to the newly active SRX.


    set chassis high-availability services-redundancy-group 1 **virtual-ip 1** ip **192.168.252.254/24**
     set chassis high-availability services-redundancy-group 1 virtual-ip 1 interface **ge-0/0/2.0**
     set chassis high-availability services-redundancy-group 1 **virtual-ip 2** ip **192.168.253.1/24**
     set chassis high-availability services-redundancy-group 1 virtual-ip 2 interface **ge-0/0/0.500**

(VIP configuration)

The active SRX (SRX-1) will install the VIP while the backup SRX will show that the VIP is not installed.


            Virtual IP Info:
              Index: 2       
              **IP: 192.168.253.1/24**
              VMAC: N/A        
              Interface: ge-0/0/0.500    
              **Status: INSTALLED**   

              Index: 1       
              **IP: 192.168.252.254/24**
              VMAC: N/A        
              Interface: ge-0/0/2.0      
              **Status: INSTALLED**

(SRX-1 – Active)


            Virtual IP Info:
              Index: 2       
              **IP: 192.168.253.1/24**
              VMAC: N/A        
              Interface: ge-0/0/0.500    
              **Status: NOT INSTALLED**  

              Index: 1       
              **IP: 192.168.252.254/24**
              VMAC: N/A        
              Interface: ge-0/0/2.0      
              **Status: NOT INSTALLED**

(SRX-2 – Backup)

You can use a virtual-mac that will float with the active IP address, otherwise, the physical MAC of the interface will be used.


    MNHA-SRX-1> show interfaces ge-0/0/0 | grep address: 
      Current address: 00:0c:29:3d:90:62, Hardware address: 00:0c:29:3d:90:62

    MNHA-SRX-1> show interfaces ge-0/0/2 | grep address:    
      Current address: 00:0c:29:3d:90:76, Hardware address: 00:0c:29:3d:90:76

    MNHA-SRX-2> show interfaces ge-0/0/0 | grep address: 
      Current address: 00:0c:29:ed:4b:42, Hardware address: 00:0c:29:ed:4b:42

    MNHA-SRX-2> show interfaces ge-0/0/2 | grep address:    
      Current address: 00:0c:29:ed:4b:56, Hardware address: 00:0c:29:ed:4b:56

(SRX-1 and SRX-2 Hardware Addresses)

Hosts within the L2 domains respective gateways pointing to the VIP addresses on the SRXs shown in Figure 5.

![Figure 5.  Hosts’ Default Gateways](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/tPO15vjdQPCju1ohXkZC_Hybrid MNHA-05.png)

_Figure 5. Hosts’ Default Gateways_

# Monitoring and Failover Criteria

There are several combinations of monitoring thresholds and weights. For this example, BFD and interface monitoring is configured such that:

  * If a single L3 BFD monitored interface fails, SRG failover will not occur (weight 50)

  * If both L3 BFD monitored interfaces fails, SRG failover will occur (weight 100)

  * If a single L2 interface fails, SRG failover will occur (weight 100)



    [edit chassis high-availability services-redundancy-group 1]
    MNHA-SRX-2# show | display set | grep monitor 
    …monitor-object BFD_UPLINKS object-threshold 100
    …monitor-object BFD_UPLINKS bfd-liveliness threshold 100
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 src-ip 10.10.99.195
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 session-type singlehop
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 interface ge-0/0/0.10
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 weight 50
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 src-ip 10.10.99.131
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 session-type singlehop
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 interface ge-0/0/1.0
    …monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 weight 50
    …monitor-object L2-GWS object-threshold 100
    …monitor-object L2-GWS interface threshold 100
    …monitor-object L2-GWS interface interface-name ge-0/0/2 weight 100
    …monitor-object L2-GWS interface interface-name ge-0/0/1 weight 100
    …monitor srg-threshold 100

(SRG Monitored Objects)

# Traffic Flows

Traffic flows during a normalized state, with SRX-1 as the active node, traffic will first hit the hosts’ respective default gateways. For the MNHA-L3 flow (Figure 6), the SRX-1 has an ECMP route to the destination and flows will be routed accordingly.

![Figure 6. MNHA-L3 Traffic Flow](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/7YZocilfS28FwHs4n85B_Hybrid MNHA-06.png)

_Figure 6. MNHA-L3 Traffic Flow_

With the MNHA-DFG (Figure 7) scenario, return traffic (or originating traffic) from 192.168.253.244 will be sent to its default gateway on the active SRX.

![Figure 7.  MNHA-DFG Traffic Flow](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/e4CPZ02cSMWPSbl7zngO_Hybrid MNHA-07.png)

_Figure 7. MNHA-DFG Traffic Flow_

During failover testing, a **L3 flow** is represented as a long-lived (TCP 5202) session from 192.168.99.100, internal - behind RTR-X, to 192.168.252.99, external. An**L2 flow** is represented as a long-lived (TCP 5201) session from 192.168.253.244, internal, to 192.168.252.99, external.

Sessions on the active SRX will be installed in the table with an HA Wing state of Active. Session information, under normalized conditions:


    MNHA-SRX-1> show security flow session destination-prefix 192.168.252.99/32 protocol tcp    

    Session ID: 118631, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1800, Session State: Valid
      In: **192.168.253.244/55293 -- > 192.168.252.99/5202;tcp**, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 565563, Bytes: 846279017, **HA Wing State: Active** ,
      Out: 192.168.252.99/5202 --> 192.168.253.244/55293;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 93439, Bytes: 3737596, HA Wing State: Active, 

    Session ID: 119130, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1800, Session State: Valid
      In: **192.168.99.100/52650 -- > 192.168.252.99/5201;tcp**, Conn Tag: 0x0, If: ge-0/0/0.10, Pkts: 244665, Bytes: 366100861, **HA Wing State: Active** , 
      Out: 192.168.252.99/5201 --> 192.168.99.100/52650;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 23385, Bytes: 938184, HA Wing State: Active, 
    Total sessions: 2

****

(Active SRX Security Flows)

Sessions on the backup SRX will be installed in the table with an HA Wing state of Warm.


    MNHA-SRX-2> show security flow session destination-prefix 192.168.252.99/32 protocol tcp 
    Session ID: 114931, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 13604, Session State: Valid
      In: **192.168.253.244/55293 -- > 192.168.252.99/5202;tcp**, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 0, Bytes: 0, **HA Wing State: Warm** , 
      Out: **192.168.252.99/5202 -- > 192.168.253.244/55293;tcp**, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, **HA Wing State: Warm** , 

    Session ID: 115414, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 13942, Session State: Valid
      In: **192.168.99.100/52650 -- > 192.168.252.99/5201;tcp**, Conn Tag: 0x0, If: ge-0/0/0.10, Pkts: 0, Bytes: 0, **HA Wing State: Warm** , 
      Out: **192.168.252.99/5201 -- > 192.168.99.100/52650;tcp**, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, **HA Wing State: Warm** , 
    Total sessions: 2

****

(Backup SRX Security Flows)

### Active Forwarding Path – BFD Detection

If there is failure on the active forwarding path in the bow-tie design, traffic will be instantly routed across the cross connect between RTR-1 and RTR-2 (MED 10) and a failover event will not occur as shown below with the change of interface on session (ID 119130) from 0/0/0.10 to 0/0/1.0. The L2 forwarding paths were not changed (0/0/0.500).


    MNHA-SRX-1> show bfd session 
                                                      Detect   Transmit
    Address                  State     Interface      Time     Interval  Multiplier
    10.10.99.1               **Down**      ge-0/0/0.10    1.500     2.000        3   
    10.10.99.65              Up        ge-0/0/1.0     1.500     0.500        3   
    100.0.0.1                Up                       2.000     0.400        5   

    3 sessions, 5 clients
    Cumulative transmit rate 5.0 pps, cumulative receive rate 6.5 pps

    jadmin@MNHA-SRX-1> **show security flow session destination-prefix 192.168.252.99/32 protocol tcp**    
    Session ID: 118631, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1800, Session State: Valid
      In: 192.168.253.244/55293 --> 192.168.252.99/5202;tcp, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 1166223, Bytes: 1745079945, HA Wing State: Active, 
      Out: 192.168.252.99/5202 --> 192.168.253.244/55293;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 186388, Bytes: 7455580, HA Wing State: Active, 

    Session ID: 119130, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1800, Session State: Valid
      In: 192.168.99.100/52650 --> 192.168.252.99/5201;tcp, Conn Tag: 0x0, If: **ge-0/0/1.0** , Pkts: 854061, Bytes: 1277977581, HA Wing State: Active, 
      Out: 192.168.252.99/5201 --> 192.168.99.100/52650;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 79932, Bytes: 3212636, HA Wing State: Active, 
    Total sessions: 2

****

(Active forwarding path failure, SRX-1)

With an active fault condition, single BFD session down between SRX-1 and RTR-1, the backup SRX session table remains unchanged; no failover event triggered.


    MNHA-SRX-2> show security flow session destination-prefix 192.168.252.99/32 protocol tcp    
    Session ID: 114931, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 13070, Session State: Valid
      In: 192.168.253.244/55293 --> 192.168.252.99/5202;tcp, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 0, Bytes: 0, HA Wing State: Warm, 
      Out: 192.168.252.99/5202 --> 192.168.253.244/55293;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, HA Wing State: Warm, 

    Session ID: 115414, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 13408, Session State: Valid
      In: 192.168.99.100/52650 --> 192.168.252.99/5201;tcp, Conn Tag: 0x0, If: ge-0/0/0.10, Pkts: 0, Bytes: 0, HA Wing State: Warm, 
      Out: 192.168.252.99/5201 --> 192.168.99.100/52650;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 0, Bytes: 0, HA Wing State: Warm,

(Active forwarding path failure, SRX-2)

### Failover Event – BFD Detection

If both redundant BFD sessions fail, a failover event is triggered (Figure 8). The initially active SRX (SRX-1) transitions into an Ineligible state while the previously backup SRX (SRX-2) moves into the active state. The sessions transition from Warm to Active on the newly active SRX-2 and vice versa for SRX-1.


    MNHA-SRX-1> show bfd session    
                                                      Detect   Transmit
    Address                  State     Interface      Time     Interval  Multiplier
    10.10.99.1               **Down**      ge-0/0/0.10    1.500     2.000        3   
    10.10.99.65              **Down**      ge-0/0/1.0     1.500     2.000        3   
    100.0.0.1                Up                       2.000     0.400        5   

    3 sessions, 5 clients
    Cumulative transmit rate 3.5 pps, cumulative receive rate 6.5 pps

    jadmin@MNHA-SRX-1> **show security flow session destination-prefix 192.168.252.99/32 protocol tcp**    
    Session ID: 118631, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 1808, Session State: Valid
      In: 192.168.253.244/55293 --> 192.168.252.99/5202;tcp, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 1507953, Bytes: 2256429529, HA Wing State: Warm, 
      Out: 192.168.252.99/5202 --> 192.168.253.244/55293;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 240892, Bytes: 9635740, HA Wing State: Warm, 

    Session ID: 119130, Policy name: default-policy-logical-system-00/2, HA State: Warm, Timeout: 1806, Session State: Valid
      In: 192.168.99.100/52650 --> 192.168.252.99/5201;tcp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 1202249, Bytes: 1798992517, HA Wing State: Warm, 
      Out: 192.168.252.99/5201 --> 192.168.99.100/52650;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 111920, Bytes: 4496748, HA Wing State: Warm, 
    Total sessions: 2

(BFD Triggered Failover – SRX-1)


    MNHA-SRX-2> show bfd session                                                                
                                                      Detect   Transmit
    Address                  State     Interface      Time     Interval  Multiplier
    10.10.99.129             Up        ge-0/0/1.0     1.500     0.500        3   
    10.10.99.193             Up        ge-0/0/0.10    1.500     0.500        3   
    100.0.0.0                Up                       2.000     0.400        5   

    3 sessions, 5 clients
    Cumulative transmit rate 6.5 pps, cumulative receive rate 6.5 pps

    jadmin@MNHA-SRX-2> show security flow session destination-prefix 192.168.252.99/32 protocol tcp    
    Session ID: 114931, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1798, Session State: Valid
      In: 192.168.253.244/55293 --> 192.168.252.99/5202;tcp, Conn Tag: 0x0, If: ge-0/0/0.500, Pkts: 26550, Bytes: 39728240, HA Wing State: Active, 
      Out: 192.168.252.99/5202 --> 192.168.253.244/55293;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 4299, Bytes: 171960, HA Wing State: Active, 

    Session ID: 115414, Policy name: default-policy-logical-system-00/2, HA State: Active, Timeout: 1798, Session State: Valid
      In: 192.168.99.100/52650 --> 192.168.252.99/5201;tcp, Conn Tag: 0x0, If: ge-0/0/0.10, Pkts: 26291, Bytes: 39337804, HA Wing State: Active, 
      Out: 192.168.252.99/5201 --> 192.168.99.100/52650;tcp, Conn Tag: 0x0, If: ge-0/0/2.0, Pkts: 2998, Bytes: 123396, HA Wing State: Active, 
    Total sessions: 2

(BFD Triggered Failover – SRX-2)

Figure 8 visualizes the BFD detection time, impacting L3 traffic for 1.5 seconds.

![Figure 8.  BFD triggered Failover](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/nzbiNsJOSuqjCR34bKuG_Hybrid MNHA-08.png)

_Figure 8. BFD triggered Failover_

### Failover Event – Reboot Active Node and Split-Brain Detection

With hybrid deployments, when there is impact to the ICL connectivity, for example losing power to the active node, the mechanism to tell the backup SRX for an SRG group to transition to active is gone. Once the configurable detection time expires, 2 seconds in these scenarios, either an ICMP or BFD based split-brain detection initializes. Split-brain detection is leveraged to ensure that there is not an opportunity for the VIP to be active on both SRXs (duplicate IP address) and negatively impacting traffic flows.

ICMP activeness is the default method for split-brain detection. The following example uses a 1 second probe, requiring 3 failed responses to declare the SRX as active for the VIP – triggering the GARP process (if previously backup for the SRG). The default gateway, VIP, move can have an impact to traffic between 3-8 seconds with ICMP detection.


    set chassis high-availability services-redundancy-group 1 activeness-probe minimum-interval 1000
    set chassis high-availability services-redundancy-group 1 activeness-probe multiplier 3

(ICMP Activeness Configuration)

![Figure 9.  Reboot Active SRG SRX ICMP Based](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/IqO75lhFQLO96LrWNXom_Hybrid MNHA-09.png)

_Figure 9. Reboot Active SRG SRX ICMP Based_

Notice that L3 traffic, traffic routed towards the destination versus switched, was not impacted. The interfaces were hard down during the reboot, traffic routed from SRX-1 (00:0C:29:3D:90:76) to 192.168.252.99 via SRX-2 (00:0C:29:ED:4B:56) (Figure 10).

![Figure10.  Reboot Active SRG SRX - L3 flow](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/fByGGWvgSXKXwxBp8hYi_Hybrid MNHA-10.png)

_Figure10. Reboot Active SRG SRX - L3 flow_

Single-hop BFD is an alternative to ICMP based split-brain detection. While ICMP based split-brain detection initiates after an ICL failure is detected, BFD is constantly running on the SRG and can achieve quicker default gateway failovers. Be aware that you can not configure both ICMP and BFD split-brain detections simultaneously.

Additional details about [Split-Brain Detection](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html#concept_fdg_tlp_31c__section_z4p_dnp_31c "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html#concept_fdg_tlp_31c__section_z4p_dnp_31c").

### Preemption

With preemption, there is an automatic fail-back once the monitoring criteria is met. The BFD BGP hold-down timer mentioned previously is simply used to illustrate potential convergence/instability issues along the active SRXs forwarding path(s). In the following example (Figure 11), SRX-1 preempts becoming active. L2 traffic is not impacted (with interface failover). However, the L3 traffic is impacted by the duration of the hold-down timer (10s); the BGP peers are not up while SRX-1 is active.

Failover event graphs were from packet captures taken on 192.168.252.99 (L2 external host).

![Figure 11.  Preempt Failover/Failback with hold-down](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/oueCFIRVQn2q7UOKetc4_Hybrid MNHA-11.png)

_Figure 11. Preempt Failover/Failback with hold-down_

Figure 12 shows the same traffic flows during failover and a preempted failback, without the BGP BFD hold-down timer configured.

![Figure 12. Preempt Failover/Failback without hold-down](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/ywir8TIEThih23MKzg20_Hybrid MNHA-12.png)

_Figure 12. Preempt Failover/Failback without hold-down_


    request chassis high-availability failover peer-id 1 services-redundancy-group 1

Figure 13 shows the same failover, with BGP BFD hold down (10s) configured, without preemption and a manual fail back to SRX-1 from SRX-2.

![Figure 13.  Failover/Manual Failback withhold-down](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/hNu1FBX8R6CEk4q2COWA_Hybrid MNHA-13.png)

_Figure 13. Failover/Manual Failback withhold-down_

# Alternative Designs

### iBGP Considerations

Under normalized operations, no failed links, a bow-tie design with iBGP and MNHA operates as expected – symmetrical traffic to the active SRX. However, there may be an issue during an active failed link event without any additional design considerations. For example, if there was a BGP peer failure on the active forwarding path, let’s say RTR-1 to SRX-1, traffic will not flow across the inter-connect between RTR-1 and RTR-2 to reach SRX-1. Instead, traffic will flow from the link between RTR-1 to SRX-2 (backup SRX) creating an asymmetric flow and causing stateful flows to break. This is due to BGP’s loop prevention, preventing iBGP peers from forwarding iBGP learned prefixes (SRX-1/2) to other iBGP neighbors (RTR-1/2).

![Figure 14.  Asymmetrical Traffic Flow](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/8ITmxxoLSBqDiIeL6yRs_Hybrid MNHA-14.png)

_Figure 14. Asymmetrical Traffic Flow_

To mitigate stateful traffic disruptions during an active failed path, with an iBGP bowtie configuration, implement an IGP with appropriate redistribution or a “floating static route” between RTR-1 and RTR-2. Another mitigation method is to use [ICD (Inter Chassis Datapath)](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-asymmetric-route-support.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-asymmetric-route-support.html") link(s).

### LAG/No Bow-tie

The same level of physical redundancy can be achieved by deploying 802.11ad (LACP) aggregate interfaces (Figure 15) between the routers and SRXs without “crossing” the links. Instead of ECMP load-balancing, the load-balancing would be with the LAG’s hashing algorithm.

![Figure 15.  LAG Uplinks](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/roN2f5d2RL2O65vlyoNH_Hybrid MNHA-15.png)

Figure 15. LAG Uplinks

### Active/Active Service Redundancy Groups

Another alternative would be to use 2 SRGs (Service Redundancy Groups) in an active/active (Figure 16) scenario such that the redundant L3 links from the routers are split between the 2 groups. This would also require an additional VIP.

![Figure 16.  Active-Active Multiple SRG](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/HkvEjXn6TbaAdJodNdoC_Hybrid MNHA-16.png)

_Figure 16. Active-Active Multiple SRG_

# Configurations

### RTR-1


    set system host-name MNHA-RTR-1
    set system no-redirects
    set security forwarding-options family inet mode packet-based
    set interfaces ge-0/0/0 unit 0 family inet address 10.10.99.1/26
    set interfaces ge-0/0/1 unit 0 family inet address 192.168.99.178/24
    set interfaces ge-0/0/2 unit 0 family inet address 10.10.99.129/26
    set interfaces ge-0/0/3 flexible-vlan-tagging
    set interfaces ge-0/0/3 unit 101 vlan-id 101
    set interfaces ge-0/0/3 unit 101 family inet address 10.10.101.1/24
    set interfaces ge-0/0/3 unit 201 vlan-id 201
    set interfaces ge-0/0/3 unit 201 family inet address 10.10.201.1/24
    set interfaces ge-0/0/4 flexible-vlan-tagging
    set interfaces ge-0/0/4 native-vlan-id 500
    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members V500
    set interfaces ge-0/0/5 flexible-vlan-tagging
    set interfaces ge-0/0/5 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/5 unit 0 family ethernet-switching vlan members V500
    set interfaces fxp0 unit 0 family inet address 192.168.100.178/24
    set interfaces lo0 unit 101 family inet address 10.11.11.12/32
    set interfaces lo0 unit 201 family inet address 10.11.201.1/32
    set policy-options policy-statement NHS term 1 from protocol bgp
    set policy-options policy-statement NHS term 1 from route-type external
    set policy-options policy-statement NHS term 1 then next-hop self
    set policy-options policy-statement load-balancing-policy then load-balance per-flow
    set protocols bgp group EXT type external
    set protocols bgp group EXT multihop ttl 4
    set protocols bgp group EXT local-address 192.168.99.178
    set protocols bgp group EXT local-as 65012
    set protocols bgp group EXT multipath multiple-as
    set protocols bgp group EXT bfd-liveness-detection minimum-interval 500
    set protocols bgp group EXT bfd-liveness-detection multiplier 3
    set protocols bgp group EXT neighbor 192.168.99.1 peer-as 65002
    set protocols bgp group INT type internal
    set protocols bgp group INT export NHS
    set protocols bgp group INT local-as 65012
    set protocols bgp group INT bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group INT bfd-liveness-detection multiplier 3
    set protocols bgp group INT neighbor 10.10.101.2
    set protocols bgp group INT-ebgp type external
    set protocols bgp group INT-ebgp local-as 65012
    set protocols bgp group INT-ebgp bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT-ebgp bfd-liveness-detection multiplier 3
    set protocols bgp group INT-ebgp bfd-liveness-detection holddown-interval 10000
    set protocols bgp group INT-ebgp neighbor 10.10.99.131 peer-as 65022
    set protocols bgp group INT-ebgp neighbor 10.10.99.5 peer-as 65022
    set routing-options static route 192.168.99.100/32 next-hop 192.168.99.1
    set routing-options forwarding-table export load-balancing-policy
    set vlans V500 vlan-id 500
    set vlans VLAN101 vlan-id 101

### RTR-2


    set system host-name MNHA-RTR-2
    set system no-redirects
    set security forwarding-options family inet mode packet-based
    set interfaces ge-0/0/0 unit 0 family inet address 10.10.99.193/26
    set interfaces ge-0/0/1 unit 0 family inet address 192.168.99.179/24
    set interfaces ge-0/0/2 unit 0 family inet address 10.10.99.65/26
    set interfaces ge-0/0/3 flexible-vlan-tagging
    set interfaces ge-0/0/3 unit 101 vlan-id 101
    set interfaces ge-0/0/3 unit 101 family inet address 10.10.101.2/24
    set interfaces ge-0/0/3 unit 201 vlan-id 201
    set interfaces ge-0/0/3 unit 201 family inet address 10.10.201.2/24
    set interfaces ge-0/0/4 flexible-vlan-tagging
    set interfaces ge-0/0/4 native-vlan-id 500
    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members V500
    set interfaces ge-0/0/5 flexible-vlan-tagging
    set interfaces ge-0/0/5 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/5 unit 0 family ethernet-switching vlan members V500
    set interfaces fxp0 unit 0 family inet address 192.168.100.179/24
    set interfaces lo0 unit 101 family inet address 10.11.11.11/32
    set policy-options policy-statement NHS term 1 from protocol bgp
    set policy-options policy-statement NHS term 1 from route-type external
    set policy-options policy-statement NHS term 1 then next-hop self
    set policy-options policy-statement load-balancing-policy then load-balance per-flow
    set protocols bgp group EXT type external
    set protocols bgp group EXT local-address 192.168.99.179
    set protocols bgp group EXT local-as 65012
    set protocols bgp group EXT multipath multiple-as
    set protocols bgp group EXT bfd-liveness-detection minimum-interval 500
    set protocols bgp group EXT bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group EXT bfd-liveness-detection multiplier 3
    set protocols bgp group EXT neighbor 192.168.99.1 peer-as 65002
    set protocols bgp group INT type internal
    set protocols bgp group INT export NHS
    set protocols bgp group INT local-as 65012
    set protocols bgp group INT bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT bfd-liveness-detection multiplier 3
    set protocols bgp group INT neighbor 10.10.101.1
    set protocols bgp group INT-ebgp local-as 65012
    set protocols bgp group INT-ebgp bfd-liveness-detection minimum-interval 500
    set protocols bgp group INT-ebgp bfd-liveness-detection multiplier 3
    set protocols bgp group INT-ebgp bfd-liveness-detection holddown-interval 10000
    set protocols bgp group INT-ebgp neighbor 10.10.99.69 peer-as 65022
    set protocols bgp group INT-ebgp neighbor 10.10.99.195 peer-as 65022
    set routing-options static route 192.168.99.100/32 next-hop 192.168.99.1
    set routing-options forwarding-table export load-balancing-policy
    set vlans V500 vlan-id 500
    set vlans VLAN101 vlan-id 101

### SRX-1


    set system host-name MNHA-SRX-1
    set chassis high-availability local-id 1
    set chassis high-availability services-redundancy-group 1 activeness-probe minimum-interval 1000
    set chassis high-availability services-redundancy-group 1 activeness-probe multiplier 3
    set chassis high-availability local-id local-ip 100.0.0.0
    set chassis high-availability peer-id 2 peer-ip 100.0.0.1
    set chassis high-availability peer-id 2 interface ge-0/0/3.0
    set chassis high-availability peer-id 2 liveness-detection minimum-interval 400
    set chassis high-availability peer-id 2 liveness-detection multiplier 5
    set chassis high-availability services-redundancy-group 0 peer-id 2
    set chassis high-availability services-redundancy-group 1 deployment-type hybrid
    set chassis high-availability services-redundancy-group 1 peer-id 2
    set chassis high-availability services-redundancy-group 1 virtual-ip 1 ip 192.168.252.254/24
    set chassis high-availability services-redundancy-group 1 virtual-ip 1 interface ge-0/0/2.0
    set chassis high-availability services-redundancy-group 1 virtual-ip 2 ip 192.168.253.1/24
    set chassis high-availability services-redundancy-group 1 virtual-ip 2 interface ge-0/0/0.500
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS object-threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.1 src-ip 10.10.99.5
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.1 session-type singlehop
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.1 interface ge-0/0/0.10
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.1 weight 50
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.65 src-ip 10.10.99.69
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.65 session-type singlehop
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.65 interface ge-0/0/1.0
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.65 weight 50
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS object-threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface interface-name ge-0/0/2 weight 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface interface-name ge-0/0/0 weight 100
    set chassis high-availability services-redundancy-group 1 monitor srg-threshold 100
    set chassis high-availability services-redundancy-group 1 active-signal-route 169.254.200.1
    set chassis high-availability services-redundancy-group 1 backup-signal-route 169.254.200.2
    set chassis high-availability services-redundancy-group 1 activeness-priority 200
    set security policies default-policy permit-all
    set security zones security-zone HA-ICL host-inbound-traffic system-services all
    set security zones security-zone HA-ICL host-inbound-traffic protocols all
    set security zones security-zone HA-ICL interfaces ge-0/0/3.0
    set security zones security-zone trust host-inbound-traffic system-services all
    set security zones security-zone trust host-inbound-traffic protocols all
    set security zones security-zone trust interfaces ge-0/0/1.0
    set security zones security-zone trust interfaces ge-0/0/0.500
    set security zones security-zone trust interfaces ge-0/0/0.10
    set security zones security-zone untrust host-inbound-traffic system-services ping
    set security zones security-zone untrust interfaces ge-0/0/2.0
    set interfaces ge-0/0/0 flexible-vlan-tagging
    set interfaces ge-0/0/0 native-vlan-id 10
    set interfaces ge-0/0/0 unit 10 vlan-id 10
    set interfaces ge-0/0/0 unit 10 family inet address 10.10.99.5/26
    set interfaces ge-0/0/0 unit 500 vlan-id 500
    set interfaces ge-0/0/0 unit 500 family inet address 192.168.253.2/24
    set interfaces ge-0/0/1 unit 0 family inet address 10.10.99.69/26
    set interfaces ge-0/0/2 unit 0 family inet address 192.168.252.252/24
    set interfaces ge-0/0/3 mtu 1514
    set interfaces ge-0/0/3 unit 0 family inet address 100.0.0.0/31
    set interfaces fxp0 unit 0 family inet address 192.168.100.180/24
    set interfaces lo0 unit 0 family inet address 172.16.0.1/32
    set forwarding-options hash-key family inet layer-3
    set forwarding-options hash-key family inet layer-4
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from route-filter 192.168.252.0/24 exact
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from condition ACTIVE_ROUTE_EXISTS_SRG1
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then metric 10
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from route-filter 192.168.252.0/24 exact
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from condition BACKUP_ROUTE_EXISTS_SRG1
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then metric 20
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then metric 30
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term default then reject
    set policy-options policy-statement load-balancing-policy then load-balance per-flow
    set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet 169.254.200.1/32
    set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0
    set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 if-route-exists address-family inet 169.254.200.2/32
    set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0
    set protocols bgp group trust type external
    set protocols bgp group trust export MNHA_ROUTE_POLICY
    set protocols bgp group trust local-as 65022
    set protocols bgp group trust multipath
    set protocols bgp group trust bfd-liveness-detection minimum-interval 500
    set protocols bgp group trust bfd-liveness-detection minimum-receive-interval 500
    set protocols bgp group trust bfd-liveness-detection multiplier 3
    set protocols bgp group trust bfd-liveness-detection holddown-interval 10000
    set protocols bgp group trust neighbor 10.10.99.1 peer-as 65012
    set protocols bgp group trust neighbor 10.10.99.65 peer-as 65012
    set routing-options forwarding-table export load-balancing-policy

SRX-2


    set system host-name MNHA-SRX-2
    set chassis high-availability local-id 2
    set chassis high-availability services-redundancy-group 1 activeness-probe minimum-interval 1000
    set chassis high-availability services-redundancy-group 1 activeness-probe multiplier 3
    set chassis high-availability local-id local-ip 100.0.0.1
    set chassis high-availability peer-id 1 peer-ip 100.0.0.0
    set chassis high-availability peer-id 1 interface ge-0/0/3.0
    set chassis high-availability peer-id 1 liveness-detection minimum-interval 400
    set chassis high-availability peer-id 1 liveness-detection multiplier 5
    set chassis high-availability services-redundancy-group 0 peer-id 1
    set chassis high-availability services-redundancy-group 1 deployment-type hybrid
    set chassis high-availability services-redundancy-group 1 peer-id 1
    set chassis high-availability services-redundancy-group 1 virtual-ip 1 ip 192.168.252.254/24
    set chassis high-availability services-redundancy-group 1 virtual-ip 1 interface ge-0/0/2.0
    set chassis high-availability services-redundancy-group 1 virtual-ip 2 ip 192.168.253.1/24
    set chassis high-availability services-redundancy-group 1 virtual-ip 2 interface ge-0/0/0.500
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS object-threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 src-ip 10.10.99.195
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 session-type singlehop
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 interface ge-0/0/0.10
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.193 weight 50
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 src-ip 10.10.99.131
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 session-type singlehop
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 interface ge-0/0/1.0
    set chassis high-availability services-redundancy-group 1 monitor monitor-object BFD_UPLINKS bfd-liveliness destination-ip 10.10.99.129 weight 50
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS object-threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface threshold 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface interface-name ge-0/0/2 weight 100
    set chassis high-availability services-redundancy-group 1 monitor monitor-object L2-GWS interface interface-name ge-0/0/1 weight 100
    set chassis high-availability services-redundancy-group 1 monitor srg-threshold 100
    set chassis high-availability services-redundancy-group 1 active-signal-route 169.254.200.1
    set chassis high-availability services-redundancy-group 1 backup-signal-route 169.254.200.2
    set chassis high-availability services-redundancy-group 1 activeness-priority 100
    set security policies default-policy permit-all
    set security zones security-zone HA-ICL host-inbound-traffic system-services all
    set security zones security-zone HA-ICL host-inbound-traffic protocols all
    set security zones security-zone HA-ICL interfaces ge-0/0/3.0
    set security zones security-zone trust host-inbound-traffic system-services all
    set security zones security-zone trust host-inbound-traffic protocols all
    set security zones security-zone trust interfaces ge-0/0/1.0
    set security zones security-zone trust interfaces ge-0/0/0.500
    set security zones security-zone trust interfaces ge-0/0/0.10
    set security zones security-zone untrust host-inbound-traffic system-services ping
    set security zones security-zone untrust interfaces ge-0/0/2.0
    set interfaces ge-0/0/0 flexible-vlan-tagging
    set interfaces ge-0/0/0 native-vlan-id 10
    set interfaces ge-0/0/0 unit 10 vlan-id 10
    set interfaces ge-0/0/0 unit 10 family inet address 10.10.99.195/26
    set interfaces ge-0/0/0 unit 500 vlan-id 500
    set interfaces ge-0/0/0 unit 500 family inet address 192.168.253.3/24
    set interfaces ge-0/0/1 unit 0 family inet address 10.10.99.131/26
    set interfaces ge-0/0/2 unit 0 family inet address 192.168.252.253/24
    set interfaces ge-0/0/3 mtu 1514
    set interfaces ge-0/0/3 unit 0 family inet address 100.0.0.1/31
    set interfaces fxp0 unit 0 family inet address 192.168.100.181/24
    set interfaces lo0 unit 0 family inet address 172.16.0.2/32
    set forwarding-options hash-key family inet layer-3
    set forwarding-options hash-key family inet layer-4
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from route-filter 192.168.252.0/24 exact
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 from condition ACTIVE_ROUTE_EXISTS_SRG1
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then metric 10
    set policy-options policy-statement MNHA_ROUTE_POLICY term 1 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from route-filter 192.168.252.0/24 exact
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 from condition BACKUP_ROUTE_EXISTS_SRG1
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then metric 20
    set policy-options policy-statement MNHA_ROUTE_POLICY term 2 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 from protocol direct
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then metric 30
    set policy-options policy-statement MNHA_ROUTE_POLICY term 99 then accept
    set policy-options policy-statement MNHA_ROUTE_POLICY term default then reject
    set policy-options policy-statement load-balancing-policy then load-balance per-flow
    set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet 169.254.200.1/32
    set policy-options condition ACTIVE_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0
    set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 if-route-exists address-family inet 169.254.200.2/32
    set policy-options condition BACKUP_ROUTE_EXISTS_SRG1 if-route-exists address-family inet table inet.0
    set protocols bgp group trust type external
    set protocols bgp group trust export MNHA_ROUTE_POLICY
    set protocols bgp group trust local-as 65022
    set protocols bgp group trust multipath multiple-as
    set protocols bgp group trust bfd-liveness-detection minimum-interval 500
    set protocols bgp group trust bfd-liveness-detection multiplier 3
    set protocols bgp group trust bfd-liveness-detection holddown-interval 10000
    set protocols bgp group trust neighbor 10.10.99.129 peer-as 65012
    set protocols bgp group trust neighbor 10.10.99.193 peer-as 65012
    set routing-options static route 0.0.0.0/0 next-hop 192.168.99.1
    set routing-options forwarding-table export load-balancing-policy

# Summary

With any high-availability design prudent planning is imperative. Understanding the requirements, goals, capabilities and integration with the network provides for a successful MNHA deployment:

  * Which MNHA model to deploy Layer 3, Layer 2 (Default Gateway) or Hybrid?

  * Active/Active or Active/Backup?

  * If L3, what protocols will be used to integrate with the network (eBGP, iBGP, OSPF)?

  * If L2, what type of fabric to integrate? Spanning Tree concerns?

  * Any convergence issues?

  * How quick to failover? Automatic Failback?

  * What mechanism to track for failover (BFD, IP, Interface, or combination of the 3)?

Once decided, it’s just a matter of testing and configuring your deployment.

### Useful links

  * Multi-Node High Availability Basics
[https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics](https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics "https://community.juniper.net/blogs/steven-jacques/2024/12/20/multi-node-high-availability-basics")

  * Multi-Node High Availability: public documentation
[https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html ](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/mnha-introduction.html ")

  * BFD Liveliness Detection (BGP)
[https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/bfd-liveness-detection-edit-protocols-bgp.html](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/bfd-liveness-detection-edit-protocols-bgp.html "https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/bfd-liveness-detection-edit-protocols-bgp.html")

  * Understanding How BFD Detects Network Failures
[https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/bfd.html](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/bfd.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/bfd.html")

  * Load Balancing on Aggregated Ethernet Interfaces
[https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/load-balancing-aggregated-ethernet-interfaces.html](https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/load-balancing-aggregated-ethernet-interfaces.html "https://www.juniper.net/documentation/us/en/software/junos/high-availability/topics/topic-map/load-balancing-aggregated-ethernet-interfaces.html")

### Glossary

  * AS – Autonomous System

  * BFD – Bi-Directional Forwarding Detection

  * BGP – Border Gateway Protocol

  * HA – High Availability

  * ICD – Inter Chassis Datapath Link

  * ICL – Inter-Chassis Link

  * L2 – Layer 2

  * L3 – Layer 3

  * MED – Multi-Exit Discriminator

  * SRG – Services Redundancy Group

  * VIP – Virtual IP

### Acknowledgements

Karel Hendrych reviewing and sanity checking. Steven Jacques providing excellent foundation MNHA post to build on.

### Comments

If you want to reach out for comments, feedback or questions, drop us a mail at:

![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/rAX6IO6zReO0h0BuHqZH_mail.png)

### Revision History

**Version** | **Author(s)** | **Date** | **Comments**
---|---|---|---
1 | James Rathbun | June 2025 | Initial Publication

[![](https://higherlogicdownload.s3.amazonaws.com/JUNIPER/UploadedImages/twV0cjAeQE2r7m3DBv4A_new-back-button4.png)](https://community.juniper.net/home/techpost)


[#SolutionsandTechnology](https://community.juniper.net/search?s=tags%3A%22Solutions and Technology%22&executesearch=true)


[#SRXSeries](https://community.juniper.net/search?s=tags%3A%22SRX Series%22&executesearch=true)
