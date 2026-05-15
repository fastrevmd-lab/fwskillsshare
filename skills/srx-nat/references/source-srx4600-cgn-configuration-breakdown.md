# TechPost

Source: https://community.juniper.net/blogs/karel-hendrych/2024/11/15/srx4600-cgn-configuration-breakdown
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

##  SRX4600 CGN Configuration Breakdown 

#### 

[](https://community.juniper.net/people/karel-hendrych) By [Karel Hendrych](https://community.juniper.net/people/karel-hendrych) posted 11-15-2024 08:28 

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl05$ucPermission$BlogItemRating$lbLike',''\) "Recommend this item.")

[](https://community.juniper.net/home/techpost)

_Junos configuration details and KPIs of a real-life SRX4600 CGN deployment for an operator serving fixed customers._

The SRX has been used as a Carrier Grade NAT (CGN) or mobile Gi/SGi firewall since the early days. Due to popular demand, this TechPost aims to describe the Junos configuration details and KPIs of a real-life SRX4600 CGN deployment for an operator serving fixed customers. In addition, the article describes optional settings and features introduced by newer Junos releases that may be relevant to the CGN use case, as well as some tweaks pertinent to Gi/SGi firewalls.

# Introduction  

Since the early days, the SRX has been widely used by fixed and mobile operators as a CGN device, among other use cases. There is usually a minor difference between the SRX CGN (typically referred to in the fixed world) and the Gi/SGi firewall configuration for mobile operators, which also typically covers CGN.  

Historically, these were typically operators using the SRX3k series and older SRX5k generations, both of which are known for their scalability and real-world performance. To this day, some of these devices are still in production; however, in most cases, they are being upgraded to the latest generation of SRX5k, SRX4600, and, more recently, to scaled-out vSRX swarms and the new mid-range SRX series.  

Over time, the SRX platforms have received numerous hardware and software updates, making them the industry's security and networking platform Swiss Army knife at capacity and scale. A very popular option among those who do not need the scalability of the SRX5k, or who are not yet considering software options, is the 1U powerhouse SRX4600.  

The following paragraphs will break down a rather simplistic configuration and KPIs of a real-life SRX4600 CGN Junos configuration, with appropriate comments used during the pilot for about 10,000 subscribers before being transferred to a full production setup. The focus is not on the specifics of connectivity to adjacent networking equipment, as every deployment may use a different approach to routing and redundancy: static vs. dynamic routing, VRRP, L3-based redundancy of standalone boxes, classical SRX chassis clustering, or multi-node HA as part of a scale-out swarm, etc. Additionally, tuning of system services, the IP stack, and other related topics will not be discussed here.  

Instead, the focus will primarily be on the Junos configuration relevant to the pilot and agnostic to the underlying networking. In the customer’s production use case, the SRX4600s are effectively stand-alone firewalls on a stick, attached to MX480 routers, with PFE enabled for 4x100GE interface operation. The software chosen conservatively for the pilot and initial deployment was the Junos 22.2 release train.

# The Configuration Breakdown

The configuration breakdown section describes the customer’s choices for the SRX4600 CGN configuration. The entire configuration is presented in Appendix 1. For detailed information about the discussed features see the Useful links section.

_Figure 1 - simplified SRX4600 setup layout_

### System Settings  

In addition to the usual hostname, login classes, NTP, DNS, SNMP, various APIs, remote SYSLOG, SSH tuning, inet options, and similar configurations, a good starting point for new deployments is to ensure that on-box control plane logging is enabled for a quick assessment of issues while keeping the rotation reasonable.
    
    
    set system syslog file messages any any  
    set system syslog file messages archive size 5m  
    set system syslog file messages archive files 5

Sidenote: In the case of unwanted logging, the following can be used to exclude certain log patterns:
    
    
    set system syslog file messages match "!(stanza1|stanza2)"

A very useful and broadly applicable Junos configuration is the remote archival of settings, typically upon commit. This feature is handy for configuration rollback beyond on-box capabilities, as well as for backup and audit purposes. 
    
    
    set system archival configuration transfer-on-commit  
    set system archival configuration archive-sites "sftp://username:password@host:folder/"

Archival to remove SFTP sites require saving the fingerprint of remote SSH service public key:
    
    
    set security ssh-known-hosts fetch-from-server [host]

Sample configuration for the SFTP site is covered in Appendix 4.

### Chassis  

Typically, the SRX4600 is configured at boot time to 4x100Gbps interface mode and acts as a firewall-on-a-stick with an aggregate interface. Please note that this implies there are no additional interfaces available. However, PFE logging can be sourced from a separate logical unit on the aggregate interfaces when separation is desired. The only exception is in a classical chassis cluster mode, where dedicated control and fabric links can be used. The [port checker tool](https://apps.juniper.net/port-checker/mx204/ "https://apps.juniper.net/port-checker/mx204/") for the sibling product MX204 is a good starting point to validate the desired interface combinations.
    
    
    set chassis aggregated-devices ethernet device-count 4  
    set chassis fpc 1 pic 0 port 0 speed 100g  
    set chassis fpc 1 pic 0 port 1 speed 100g  
    set chassis fpc 1 pic 0 port 2 speed 100g  
    set chassis fpc 1 pic 0 port 3 speed 100g  
    set chassis fpc 1 pic 1 number-of-ports 0

Sidenote: regarding Services Offload (also known as SOF or Express Path), which is the technology for processing traffic using hardware acceleration discussed later: unlike the SRX5k, the np-cache mode of the PIC has been enabled on the SRX4600 by default, even before the Junos 21.2 release, which also made it the default for SRX5k IOC3/IOC4. 

### Routing Instance  

A good practice is to place revenue (PFE traffic) interfaces into separate routing instances. Another approach is to use a management instance to separate the out-of-band management interface, fxp0. The traditional method chosen is to place everything into instances, except for fxp0:
    
    
    set routing-instances VR_1 instance-type virtual-router  
    set routing-instances VR_1 routing-options static route 0.0.0.0/0 next-hop [NH]  
    set routing-instances VR_1 routing-options static route 100.64.0.0/10 next-hop [NH]  
    set routing-instances VR_1 interface ae0.80  
    set routing-instances VR_1 interface ae0.81

### Screening  

Screening is the fundamental network-level protection against DoS/DDoS attacks and anomalies. On the subscriber/LAN side, the customer decided not to enforce screening by configuring "alarm-without-drop." The idea behind this setting is to receive session limit screen logs for instant identification when a subscriber is approaching the limit of ports defined by the block size and the maximum number of blocks. The topic of Port Block Allocation (PBA) will be discussed in one of the following sections. Additionally, for visibility purposes, UDP and ICMP flood thresholds are configured.
    
    
    set security screen ids-option LAN_SCREEN alarm-without-drop  
    set security screen ids-option LAN_SCREEN icmp flood threshold 10000  
    set security screen ids-option LAN_SCREEN udp flood threshold 50000  
    set security screen ids-option LAN_SCREEN limit-session source-ip-based 3800  
    set security screen ids-option LAN_SCREEN limit-session destination-ip-based 100000

Sidenote: unless RPF is implemented elsewhere, as in the customer’s case, enforcing an IP spoofing screen would be appropriate for the common good. 

As a starting point, the customer has been using the following configuration for the Internet/WAN side, primarily focusing on dropping packets with IP options and addressing floods. The TCP attack threshold is set above the destination threshold; therefore, SYN cookies will never engage. There is a rather niche use case for SYN cookies on devices that primarily permit traffic from inside to outside, except when Persistent NAT (also known as Cone NAT, discussed in NAT sections) protections are considered. True tuning is typically done during the first significant DoS/DDoS event.
    
    
    set security screen ids-option WAN_SCREEN icmp flood threshold 10000  
    set security screen ids-option WAN_SCREEN ip record-route-option  
    set security screen ids-option WAN_SCREEN ip timestamp-option  
    set security screen ids-option WAN_SCREEN ip security-option  
    set security screen ids-option WAN_SCREEN ip stream-option  
    set security screen ids-option WAN_SCREEN ip spoofing  
    set security screen ids-option WAN_SCREEN ip source-route-option  
    set security screen ids-option WAN_SCREEN ip loose-source-route-option  
    set security screen ids-option WAN_SCREEN ip strict-source-route-option  
    set security screen ids-option WAN_SCREEN tcp syn-flood alarm-threshold 10000  
    set security screen ids-option WAN_SCREEN tcp syn-flood attack-threshold 100000  
    set security screen ids-option WAN_SCREEN tcp syn-flood source-threshold 10000  
    set security screen ids-option WAN_SCREEN tcp syn-flood destination-threshold 50000  
    set security screen ids-option WAN_SCREEN tcp land  
    set security screen ids-option WAN_SCREEN udp flood threshold 200000

Sidenote: recently, higher UDP figures have become appropriate due to major services utilizing UDP-based QUIC/HTTP3 transport.

### Zone Settings  

Zones bind interfaces, screening profiles, and permit host-inbound services for in-band management and testing purposes. The internal LAN zone is configured to send TCP resets for out-of-state TCP traffic, allowing for more interactive application behaviour than what is provided by a timeout. Such conditions can occur when an application does not send any data within the session timeout or during failover conditions between non-synchronized systems (in the customer’s scenario, there are two independent SRX4600s). SSH is permitted for in-band management, as covered in the Firewall Rules section.
    
    
    set security zones security-zone LAN tcp-rst  
    set security zones security-zone LAN screen LAN_SCREEN  
    set security zones security-zone LAN host-inbound-traffic system-services ping  
    set security zones security-zone LAN interfaces ae0.80  
    
    set security zones security-zone WAN screen WAN_SCREEN  
    set security zones security-zone WAN host-inbound-traffic system-services ssh  
    set security zones security-zone WAN host-inbound-traffic system-services ping  
    set security zones security-zone WAN interfaces ae0.81

### NAT Pool  

The specific customer has a generous policy regarding PBA resources, allocating up to three 1280-port blocks to every subscriber. The configuration below assigns blocks from a 4x /24 prefix with address-pooling paired persistence. This ensures that sessions from the same subscriber will always use the same NAT pool IP address. Unlike the hash-based address-persistent setting, which is global for source NAT, pool-level address-pooling operates on a round-robin basis and overrides the global address-persistent setting. An important configuration parameter is the last-block-recycle-timeout, which releases the last block after 300 seconds if there are no sessions. Otherwise, the block would remain allocated indefinitely, potentially depleting NAT resources in the case of a large subscriber pool with random client allocation.
    
    
    set security nat source pool POOL_1 address 1.2.84.0/24  
    set security nat source pool POOL_1 address 1.2.85.0/24  
    set security nat source pool POOL_1 address 1.2.86.0/24  
    set security nat source pool POOL_1 address 1.2.87.0/24  
    set security nat source pool POOL_1 port block-allocation block-size 1280  
    set security nat source pool POOL_1 port block-allocation maximum-blocks-per-host 3  
    set security nat source pool POOL_1 port block-allocation last-block-recycle-timeout 300  
    set security nat source pool POOL_1 address-pooling paired

Tuning block sizes is a complex issue that requires careful analysis of the specific scenario. Usual mobile patterns in Europe indicate an average of 10 sessions (or ports) per subscriber, while fixed scenarios typically require fewer than 50 sessions. However, it is important to account for spikes (e.g., complex web pages, mobile tethering), which can demand hundreds or even thousands of ports. Generally, a good starting point is 4x256 blocks, which may be overly conservative for mobile but might not be sufficient for fixed scenarios.

For the purposes of PBA tuning, the [pba-stat tool](https://github.com/JNPRAutomate/srx-pba-stat/ "https://github.com/JNPRAutomate/srx-pba-stat/") has been created to reveal important statistics, even in large-scale deployments. The idea is to check whether the NAT settings are appropriate for the use case—inefficient use of public IP addresses on one side and too few resources on the other, which could potentially lead to service impact. By creating NAT rule(s) with a separate NAT pool for a specific set of representative clients, the pba-stat analysis can handle tens of thousands of allocated blocks, depending on the platform. Appendix 3 covers a sample of real-world pba-stat output.

Sidenote: in the case of an SRX chassis cluster, unless in explicit Active/Passive mode, the NAT IP has half of the port range (31k instead of 62k due to reservations for Active/Active operation). For details, see [KB82919](https://supportportal.juniper.net/s/article/SRX-My-cluster-is-set-as-activepassive-then-why-the-operational-mode-says-activeactive "https://supportportal.juniper.net/s/article/SRX-My-cluster-is-set-as-activepassive-then-why-the-operational-mode-says-activeactive") and the linked resources.

### NAT Rules  

CGN scenarios typically require [Persistent NAT](https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/security-persistent-nat-and-nat64.html "https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/security-persistent-nat-and-nat64.html"), also known as Cone NAT, primarily to support gaming consoles, allowing endpoints to be directly reachable from the Internet for P2P communication without the need for interim proxies. Endpoints communicating with the outside world establish a Persistent NAT binding while creating a firewall/NAT connection. With the assistance of a STUN service, they can retrieve the translated IP address and port. This is typically used in signaling to determine where the host is reachable for P2P communication.  

The catch is that the SRX4600 does not scale Persistent NAT bindings (2 million) to match the entire session table capacity (62 million). Therefore, resources must be managed accordingly. As a good starting point, the following approach enables Endpoint Independent Mapping (where any remote host can reach the endpoint) for Persistent NAT, but only for selected destination ports defined by the application group GAMING_CONSOLES_TUNED. This group essentially includes STUN, STUN-TLS, and one Xbox-specific port. The rest of the traffic is then translated without the creation of Persistent NAT bindings. This approach has been proven to be effective in a specific region; however, other regions using different applications may require fine-tuning. The effectiveness of Persistent NAT tuning is covered in the Sample KPIs section.
    
    
    set security nat source rule-set LAN_TO_WAN from zone LAN  
    set security nat source rule-set LAN_TO_WAN to zone LAN  
    set security nat source rule-set LAN_TO_WAN to zone WAN  
    
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match source-address 100.64.0.0/10  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match destination-address 0.0.0.0/0  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match application GAMING_CONSOLES_TUNED  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool POOL_1  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool persistent-nat permit any-remote-host  
    
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match source-address 100.64.0.0/10  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match destination-address 0.0.0.0/0  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 then source-nat pool POOL_1  
    
    set applications application STUN-TLS term 1 protocol tcp  
    set applications application STUN-TLS term 1 destination-port 5349  
    set applications application STUN-TLS term 2 protocol udp  
    set applications application STUN-TLS term 2 destination-port 5349  
    set applications application XBOX-UDP-3544 protocol udp  
    set applications application XBOX-UDP-3544 destination-port 3544  
    set applications application-set GAMING_CONSOLES_TUNED application STUN-TLS  
    set applications application-set GAMING_CONSOLES_TUNED application junos-stun  
    set applications application-set GAMING_CONSOLES_TUNED application XBOX-UDP-3544

Sidenote: port blocks that had sessions creating Persistent NAT bindings, which no longer have sessions and should have already expired, remain in the QUERY state if the bindings have not expired yet.

### Firewall Rules  

The SRX is a stateful firewall by default, offering various options to tune its behavior. Here is a breakdown of the ruleset:

The PERMIT_HAIRPIN rule allows traffic between two internal endpoints via a NAT IP, while non-translated traffic is prohibited and dropped (this applies in the context of Persistent NAT, e.g., two gaming consoles on the same network). Logging is at session close and interim which contains accounting information every 30 minutes (session-update). Technically, interim logs are generated if traffic is passing through the session. 

The DEFAULT_PERMIT rule permits anything from inside to outside with close and interim log.

The FINAL_TOUCH rule is primarily in place for clarity, indicating that the final action is to drop traffic and to collect rule hit counter data for dropped traffic as well.
    
    
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match source-address any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match destination-address any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match application any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then permit destination-address drop-untranslated  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then log session-close  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then log session-update 30  
    
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match source-address any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match destination-address any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match application any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then permit  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then log session-close  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then log session-update 30  
    
    set security policies global policy FINAL_TOUCH match source-address any  
    set security policies global policy FINAL_TOUCH match destination-address any  
    set security policies global policy FINAL_TOUCH match application any  
    set security policies global policy FINAL_TOUCH then deny

Sidenote: some customers may drop certain traffic, except for that destined for local services (typically SMTP, with only the ISP's local relay host permitted to mitigate spamming).

The next policy section covers in-band management using the junos-host zone (out-of-band security is not covered here). Although the preferred method of management is through an out-of-band interface, in-band management is prevalent in real-life scenarios. The traditional method involves using stateless filters either on the ingress or loopback interface. However, the SRX native approach uses policies in the zone->junos-host context, which also prevents potential offloading disqualification discussed in the Offloading section.
    
    
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match source-address MGMT_ENDPOINT_1  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match source-address MGMT_ENDPOINT_2  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match application junos-ssh  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH then permit  
    
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match source-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match application junos-icmp-ping  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING then permit  
    
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match source-address any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match application any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST then deny  
    
    set security address-book global address MGMT_ENDPOINT_1 3.4.0.1/32  
    set security address-book global address MGMT_ENDPOINT_2 3.4.0.2/32

Sidenote: the order of processing in-band traffic is as follows  

  * Interface firewall filter  

  * Zone level allowed services  

  * Zone->junos-host context  

  * If there is no explicit drop at the end of Zone->junos-host context, then the loopback filter is applied if configured

### Logging  

Although the SRX4600 features a full-fledged on-box logging capability that can store millions of logs with the option to dedicate CPU resources, the highly recommended approach is to use stream mode and send the logs to remote destination(s). Besides the on-box logging being impractical when there are multiple logging devices, SSD write endurance also has to be taken into account. In practice, stream mode is the only viable option for CGN scenarios when it comes to historical log storage. In the example below, the destination .36 is receiving only NAT logging (PBA logs) and .35 session logging. A sample log format is available in the second appendix.  

With Junos 21.2 and above, logging templates that select particular columns can be configured and applied to the selected log stream to reduce log size.
    
    
    set security log mode stream  
    set security log stream STREAM_1 host 172.30.16.35  
    set security log stream STREAM_1 host routing-instance VR_1  
    set security log stream STREAM_1 source-address 172.30.0.1  
    set security log stream STREAM_2 category nat  
    set security log stream STREAM_2 host 172.30.16.36  
    set security log stream STREAM_2 host routing-instance VR_1  
    set security log stream STREAM_2 source-address 172.30.0.1  
    set security log profile PROFILE_1 stream-name STREAM_1  
    set security log profile PROFILE_1 category session field-name source-address  
    set security log profile PROFILE_1 category session field-name source-port  
    set security log profile PROFILE_1 category session field-name destination-address  
    set security log profile PROFILE_1 category session field-name destination-port  
    set security log profile PROFILE_1 category session field-name protocol-id  
    set security log profile PROFILE_1 category session field-name nat-source-address  
    set security log profile PROFILE_1 category session field-name nat-source-port  
    set security log profile PROFILE_1 category session field-name reason  
    set security log profile PROFILE_1 category session field-name elapsed-time  
    set security log profile PROFILE_1 default-profile

Sidenote: notice the routing-instance configuration beneath the specific stream host; this is the solution for Day 1 design when logs originated in inet.0 and a next-table or similar route had to be used.

### Application Layer Gateways  

In terms of configuring ALGs, a typical good starting point is to keep FTP, DNS, SIP, and PPTP enabled, with optional tuning for permissive behavior for the SIP ALG. The DNS ALG is designed to expedite UDP flow closure upon receiving a DNS response.
    
    
    set security alg msrpc disable  
    set security alg sunrpc disable  
    set security alg sip application-screen unknown-message permit-nat-applied  
    set security alg sip application-screen unknown-message permit-routed  
    set security alg talk disable  
    set security alg tftp disable

Sidenote: in the case of overwhelming DNS traffic, the DNS ALG can either be disabled globally or substituted with a custom UDP port 53 L4 application, using the application protocol set to 'none.' The latter is done through exception rules that have the custom application configured before the rules permit traffic.

### Offloading  

Generally, after Junos 21.2, the device offloads to hardware (also referred to as Express Path, Services Offload, SOF) all TCP/UDP traffic by default, with no configuration required, except for notoriously short-lived NTP and DNS transactions (UDP ports 123 and 53, respectively). The default logic has changed from explicitly enabling services offload at the firewall rule level to a no-services-offload setting. To revert this logic, it is possible to disable offloading globally and enable services offload at the rule level, similar to how it was done in Junos releases prior to 21.2. The choice of Junos 22.2 was not accidental, as it is the first release for the SRX4600 that increases offloading capacity from 2.5 million sessions to 10 million sessions (10.485.760 exactly).

In the customer’s deployment, deactivation of offloading per rule would be as follows:
    
    
    [firewall rule] then permit no-services-offload

Sidenote: to revert to the pre-21.2 logic, which may be more suitable for enabling offloading only to certain destinations:
    
    
    set security forwarding-options services-offload disable  
    [firewall rule] then permit services-offload

However, selective offloading from the perspective of capacity planning requires thorough and continuous analysis of traffic to determine whether offloading to certain destinations is effective, particularly where small session counts result in large traffic volumes (high-bandwidth sessions).  

IMPORTANT NOTE: it is strongly recommended to avoid settings that disqualify offloading, such as when the traffic is subjected to the following features in addition to those listed here:

  * Firewall filters attached to interfaces in Pre-Junos 23.2 software  

  * NetFlow/J-Flow sampling

The chapter "Applicable Junos Features Post 22.2" describes enhancements to firewall filters in Junos 23.2.

### Monitoring  

As the deployment is based on Junos prior to 23.4, where PBA SNMP resource monitoring was introduced, [a custom utility MIB script](https://github.com/JNPRAutomate/srx-pba-utility-mib/tree/main "https://github.com/JNPRAutomate/srx-pba-utility-mib/tree/main") had to be used. The generic concept of the Junos SNMP utility MIB is [described here](https://community.juniper.net/blogs/karel-hendrych/2024/02/07/using-junos-snmp-utility-mib-on-juniper-srx "https://community.juniper.net/blogs/karel-hendrych/2024/02/07/using-junos-snmp-utility-mib-on-juniper-srx").  

Otherwise, nearly all system KPIs can be monitored using the comprehensive Junos SNMP MIB, with some having an option for telemetry (emerging sensors over Junos releases).

# Sample KPIs

### Logs  

The first KPI is to examine the ratios between various types of logs, which essentially indicates how PBA can save resources (statistics is a hidden syntax).
    
    
    > show security log statistics   
    Log Module Statistics  
    Name               Generated       Discarded  
    --------------------------------------------  
    UTM                0               0  
    FW_AUTH            0               0  
    SCREEN             36461           0  
    ALG                197578          0  
    NAT                8074056         0  
    FLOW               3447959191      0

### CPU and Session Load  

For 20 Gbps with 2.5 MPPS from approximately 9,000 active endpoints, the following observations can be made regarding CPU load, Connections Per Second (CPS), and Concurrent Connections (CC):
    
    
    > show security monitoring fpc 0   
    FPC 0   
      PIC 0   
        CPU utilization          : 4 %   
        Memory utilization       : 44 %   
        Current flow session     : 689188   
        Current flow session IPv4: 689188   
        Current flow session IPv6: 0   
        Max flow session         : 62914560   
    Total Session Creation Per Second (for last 96 seconds on average): 12146   
    IPv4  Session Creation Per Second (for last 96 seconds on average): 12146   
    IPv6  Session Creation Per Second (for last 96 seconds on average): 0

### Offloading  

In terms of offloading capacity, the customer’s traffic pattern utilized 5% of the overall 20 million session wing offloading capacity. A "wing" represents one direction of a session; a bi-directional TCP session consists of two wings, while a unidirectional UDP session accounts for one wing. Based on the current flow sessions and offloaded sessions, approximately 78% of sessions are offloaded. This figure can be affected by some sessions being in an invalidated state shortly before closure, as well as traffic that is not being offloaded (such as UDP DNS and NTP).
    
    
    > show security np-cache summary   
      NP-cache/services-offload Wings: 1083800   
      NP-cache Capacity: 20971520   
      NP-cache Usage: 5%

### IP Proto Breakdown  

Using the utility MIB described in the Monitoring section, the following is a breakdown of typical IP protocols in the session table. The summary does not align with the overall session count mentioned above due to the time delta between data collection.
    
    
    > show snmp mib walk jnxUtil ascii| match session | match value   
    jnxUtilCounter64Value."session_count_esp" = 7   
    jnxUtilCounter64Value."session_count_gre" = 33   
    jnxUtilCounter64Value."session_count_icmp" = 1884   
    jnxUtilCounter64Value."session_count_tcp" = 536961   
    jnxUtilCounter64Value."session_count_udp" = 136829 

### PBA  

Similar to the previous section, [the utility MIB](https://github.com/JNPRAutomate/srx-pba-utility-mib "https://github.com/JNPRAutomate/srx-pba-utility-mib") is used on Junos 22.2 to retrieve details for PBA.
    
    
    > show snmp mib walk jnxUtil ascii | match block | match value   
    jnxUtilCounter64Value."pba_blocks_POOL_1_total" = 51200   
    jnxUtilCounter64Value."pba_blocks_POOL_1_used" = 9355   
    jnxUtilCounter64Value."pba_blocks_POOL_1_used_perc" = 19   
    jnxUtilCounter64Value."pba_blocks_total" = 51200   
    jnxUtilCounter64Value."pba_blocks_used" = 9355   
    jnxUtilCounter64Value."pba_blocks_used_perc" = 19 

### Flow Stats  

Besides other metrics, flow statistics reveal interesting data about fragmentation and offloading. By utilizing the interface counter values, it can be determined that approximately 93% of packets are being offloaded to the Trio chipset. Fragmented packets account for around 0.03% of the total packets. In non-accelerated path statistics, the packets received statistics correspond to a summary of packets that are internally forwarded/queued, copied (L7 processing and ALGs), dropped (first and fast-path), and transmitted (forwarded immediately).
    
    
    > show security flow statistics   
      Current sessions: 644383   
      Packets received: 2571372129   
      Packets transmitted: 1536329509   
      Packets forwarded/queued: 40013   
      Packets copied: 945319252   
      Packets dropped: 89683379   
      Services-offload packets processed: 61341780228   
      Fragment packets: 19782641   
      Pre fragments generated: 0   
      Post fragments generated: 0 

### Persistent NAT  

Finally, in terms of Persistent NAT usage, optimizing its use for specific destination ports resulted in fewer than 3,000 active bindings with approximately 650,000 session table records.
    
    
    > show security nat source persistent-nat-table summary   
      binding total    : 2097152    
      binding in use   : 2983   
      enode total      : 67108864  
      enode in use     : 0

# Mobile Use-case Tuning  

For the mobile Gi/SGi firewall use case, some additional settings on top of the discussed fixed CGN setup may be appropriate in the following areas.

### NAT Tuning  

The mobile use case would likely have many more subscribers, requiring much larger NAT pools in the case of PBA to accommodate generous blocks, similar to those in the discussed fixed scenario. The [pba-stat utility](https://github.com/JNPRAutomate/srx-pba-stat/tree/main "https://github.com/JNPRAutomate/srx-pba-stat/tree/main") mentioned earlier could provide valuable information for adjusting the block sizes, likely resulting in the possibility of reducing both the number of blocks and their sizes (appendix 3 contains sample pba-stat outputs).

### Flow Tuning  

The prevalent setting for mobile use cases is TCP MSS adjustment. This can be done on the SRX globally or per firewall rule. A sample global setting usually safe for multiple encapsulations enroute (e.g., roaming coverage):
    
    
    set security flow tcp-mss all-tcp mss 1350

[Strict SYN checking](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-strict-syn.html "https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-strict-syn.html") increases TCP handling security:
    
    
    set security flow tcp-session strict-syn-check

### Unidirectional Session Refresh  

The next item could be [uni-directional session refreshing](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/unidirectional-session-refreshing.html "https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/unidirectional-session-refreshing.html"), where the session is refreshed only with traffic from LAN to WAN in the context of the discussed example. This is an essential measure against overbilling, as a new subscriber reusing an IP address may receive unsolicited traffic from outside, initiated by the previous subscriber. This setting is enabled on the ingress zone.
    
    
    set security zones security-zone LAN unidirectional-session-refreshing

This problem may be self-remediated if the endpoint sends a TCP reset or ICMP port unreachable message; in that case, the session is removed from the SRX as well.

Regarding Persistent NAT, with the following setting, if there are no packets from the endpoint within the persistent NAT inactivity timeout, then no packets are accepted from outside towards the Persistent NAT binding. Otherwise, the binding could be refreshed by traffic from outside indefinitely.
    
    
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool persistent-nat block-ext-session

Sidenote: in conjunction with PPTP ALG, uni-directional session refreshing is applicable only with the latest Junos 22.4 and above, due to the fix for the removal of the ALG gate for GRE traffic from outside.

### Advanced Connection Tracking  

Another feature applicable to mobile use cases, which may not necessarily perform NAT, is [Advanced Connection Tracking (ACT)](https://www.juniper.net/documentation/en_US/junos/topics/reference/configuration-statement/advanced-connection-tracking.html "https://www.juniper.net/documentation/en_US/junos/topics/reference/configuration-statement/advanced-connection-tracking.html"), a policy-level construct [documented here](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-permit-security-policy.html "https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-permit-security-policy.html"). In simplified terms, this can be described as Persistent NAT without the NAT component. ACT has been designed to allow connections from outside to inside only if the inside endpoint is active. It was created for IPv6 scenarios to prevent unsolicited traffic from horizontal scans of vast IPv6 prefixes when some ports are permitted. Additionally, it is perfectly applicable to IPv4. ACT increases load due to the setup of a separate tracking table. The recommended approach is to have a separate zone that enables ACT for hosts needing this service.

The following sample configuration would permit SSH access from any external host to the internal network if the internal endpoint is active and has ACT table records (timeout of 10 minutes).
    
    
    set security zones security-zone LAN advanced-connection-tracking mode allow-any-host  
    set security advanced-connection-tracking-timeout 600  
    set security policies from-zone WAN to-zone LAN policy ACT match source-address any  
    set security policies from-zone WAN to-zone LAN policy ACT match destination-address any  
    set security policies from-zone WAN to-zone LAN policy ACT match application junos-ssh  
    set security policies from-zone WAN to-zone LAN policy ACT then permit advanced-connection-tracking

Sidenotes:  

  * In the above example, ACT is still subject to L4 firewall processing, where sources, destinations, and services can be narrowed down.  

  * The above ACT rule is terminal for the SSH application from any source to any destination; no sub-sequent ACT rule for TCP port 22 would be evaluated.  

# Applicable Junos Features Post 22.2

### Junos 22.4   

  * for non-PBA source NAT, the ability to preserve the port range is similar to the existing MX services capability. This is intended to support niche use cases like NFS, where extra flags need to be added on the server side to accept connections from ports above 1024.

### Junos 23.2   

  * The SRX5k IOC3/IOC4 and SRX4600 hardware process stateless filters and policers, including packet rate policing. This is especially useful for high-performance protections and for setting overall limits on screening, which operates in a token-bucket style when limits apply per destination IP address. This setting is activated by adding the enhanced-mode knob to the firewall filters.

### Junos 23.4  

  * Services offload fragmentation support of unequal in/out interface MTU (no reassembly)  

  * drop-flow for accelerated traffic drops, which would otherwise be repeatedly evaluated in the slow path. Practically, this setting can cause a side effect in the Junos versions available at the time of writing, resulting in logging of all dropped packets.  

  * Increased Persistent NAT capacity for SRX4100/4200 and vSRX.  

  * Enhancement of the jnxJsNatPbaStatsTable SNMP MIB for monitoring the PBA NAT pool.  

  * Aggressive session aging per protocol and application.  

  * Zone-attached screening white-list.

### Junos 24.2  

  * asymmetric traffic in MN-HA resiliency formation with CGNAT.  

  * RADIUS accounting PBA logging, with an option to avoid allocating a block in the case of a missing RADIUS accounting acknowledgment.  

  * DS-Lite with enhanced PBA logging.

### Junos 24.4  

  * Subscriber level trap/SYSLOG for PBA port utilization  

  * DS-Lite performance and fragmentation control enhancements 

# Appendixes

### Appendix 1: Complete Configuration
    
    
    set system syslog file messages any any  
    set system syslog file messages archive size 5m  
    set system syslog file messages archive files 5  
    
    set system archival configuration transfer-on-commit  
    set system archival configuration archive-sites "sftp://user:password@host:path"  
    
    set chassis aggregated-devices ethernet device-count 4  
    set chassis fpc 1 pic 0 port 0 speed 100g  
    set chassis fpc 1 pic 0 port 1 speed 100g  
    set chassis fpc 1 pic 0 port 2 speed 100g  
    set chassis fpc 1 pic 0 port 3 speed 100g  
    set chassis fpc 1 pic 1 number-of-ports 0  
    
    set security log mode stream  
    set security log stream STREAM_1 host 172.30.16.35  
    set security log stream STREAM_1 host routing-instance VR_1  
    set security log stream STREAM_1 source-address 172.30.0.1  
    set security log stream STREAM_2 category nat  
    set security log stream STREAM_2 host 172.30.16.36  
    set security log stream STREAM_2 host routing-instance VR_1  
    set security log stream STREAM_2 source-address 172.30.0.1  
    set security log profile PROFILE_1 stream-name STREAM_1  
    set security log profile PROFILE_1 category session field-name source-address  
    set security log profile PROFILE_1 category session field-name source-port  
    set security log profile PROFILE_1 category session field-name destination-address  
    set security log profile PROFILE_1 category session field-name destination-port  
    set security log profile PROFILE_1 category session field-name protocol-id  
    set security log profile PROFILE_1 category session field-name nat-source-address  
    set security log profile PROFILE_1 category session field-name nat-source-port  
    set security log profile PROFILE_1 category session field-name reason  
    set security log profile PROFILE_1 category session field-name elapsed-time  
    set security log profile PROFILE_1 default-profile  
    
    set security ssh-known-hosts host [ set security ssh-known-hosts fetch-from-server [host] ]  
    
    set security address-book global address MGMT_ENDPOINT_1 3.4.0.1/32  
    set security address-book global address MGMT_ENDPOINT_2 3.4.0.2/32  
    
    set security alg msrpc disable  
    set security alg sunrpc disable  
    set security alg sip application-screen unknown-message permit-nat-applied  
    set security alg sip application-screen unknown-message permit-routed  
    set security alg talk disable  
    set security alg tftp disable  
    
    set security screen ids-option LAN_SCREEN alarm-without-drop  
    set security screen ids-option LAN_SCREEN icmp flood threshold 10000  
    set security screen ids-option LAN_SCREEN udp flood threshold 50000  
    set security screen ids-option LAN_SCREEN limit-session source-ip-based 3800  
    set security screen ids-option LAN_SCREEN limit-session destination-ip-based 100000  
    set security screen ids-option WAN_SCREEN icmp flood threshold 10000  
    set security screen ids-option WAN_SCREEN ip record-route-option  
    set security screen ids-option WAN_SCREEN ip timestamp-option  
    set security screen ids-option WAN_SCREEN ip security-option  
    set security screen ids-option WAN_SCREEN ip stream-option  
    set security screen ids-option WAN_SCREEN ip spoofing  
    set security screen ids-option WAN_SCREEN ip source-route-option  
    set security screen ids-option WAN_SCREEN ip loose-source-route-option  
    set security screen ids-option WAN_SCREEN ip strict-source-route-option  
    set security screen ids-option WAN_SCREEN tcp syn-flood alarm-threshold 10000  
    set security screen ids-option WAN_SCREEN tcp syn-flood attack-threshold 100000  
    set security screen ids-option WAN_SCREEN tcp syn-flood source-threshold 10000  
    set security screen ids-option WAN_SCREEN tcp syn-flood destination-threshold 50000  
    set security screen ids-option WAN_SCREEN tcp land  
    set security screen ids-option WAN_SCREEN udp flood threshold 200000  
    
    set security nat source pool POOL_1 address 1.2.84.0/24  
    set security nat source pool POOL_1 address 1.2.85.0/24  
    set security nat source pool POOL_1 address 1.2.86.0/24  
    set security nat source pool POOL_1 address 1.2.87.0/24  
    set security nat source pool POOL_1 port block-allocation block-size 1280  
    set security nat source pool POOL_1 port block-allocation maximum-blocks-per-host 3  
    set security nat source pool POOL_1 port block-allocation last-block-recycle-timeout 300  
    set security nat source pool POOL_1 address-pooling paired  
    set security nat source rule-set LAN_TO_WAN from zone LAN  
    set security nat source rule-set LAN_TO_WAN to zone LAN  
    set security nat source rule-set LAN_TO_WAN to zone WAN  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match source-address 100.64.0.0/10  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match destination-address 0.0.0.0/0  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 match application GAMING_CONSOLES_TUNED  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool POOL_1  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_PNAT_1 then source-nat pool persistent-nat permit any-remote-host  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match source-address 100.64.0.0/10  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 match destination-address 0.0.0.0/0  
    set security nat source rule-set LAN_TO_WAN rule LAN_WAN_NAT_1 then source-nat pool POOL_1  
    
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match source-address any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match destination-address any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN match application any  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then permit destination-address drop-untranslated  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then log session-close  
    set security policies from-zone LAN to-zone LAN policy PERMIT_HAIRPIN then log session-update 30  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match source-address any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match destination-address any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT match application any  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then permit  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then log session-close  
    set security policies from-zone LAN to-zone WAN policy DEFAULT_PERMIT then log session-update 30  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match source-address MGMT_ENDPOINT_1  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match source-address MGMT_ENDPOINT_2  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH match application junos-ssh  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_SSH then permit  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match source-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING match application junos-icmp-ping  
    set security policies from-zone WAN to-zone junos-host policy PERMIT_PING then permit  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match source-address any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match destination-address any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST match application any  
    set security policies from-zone WAN to-zone junos-host policy DENY_JUNOS_HOST then deny  
    set security policies global policy FINAL_TOUCH match source-address any  
    set security policies global policy FINAL_TOUCH match destination-address any  
    set security policies global policy FINAL_TOUCH match application any  
    set security policies global policy FINAL_TOUCH then deny  
    
    set security zones security-zone LAN tcp-rst  
    set security zones security-zone LAN screen LAN_SCREEN  
    set security zones security-zone LAN host-inbound-traffic system-services ping  
    set security zones security-zone LAN interfaces ae0.80  
    set security zones security-zone WAN screen WAN_SCREEN  
    set security zones security-zone WAN host-inbound-traffic system-services ssh  
    set security zones security-zone WAN host-inbound-traffic system-services ping  
    set security zones security-zone WAN interfaces ae0.81  
    
    set routing-instances VR_1 instance-type virtual-router  
    set routing-instances VR_1 routing-options static route 0.0.0.0/0 next-hop [nh]  
    set routing-instances VR_1 routing-options static route 100.64.0.0/10 next-hop [nh]  
    set routing-instances VR_1 interface ae0.80  
    set routing-instances VR_1 interface ae0.81  
    
    set applications application STUN-TLS term 1 protocol tcp  
    set applications application STUN-TLS term 1 destination-port 5349  
    set applications application STUN-TLS term 2 protocol udp  
    set applications application STUN-TLS term 2 destination-port 5349  
    set applications application XBOX-UDP-3544 protocol udp  
    set applications application XBOX-UDP-3544 destination-port 3544  
    set applications application-set GAMING_CONSOLES_TUNED application STUN-TLS  
    set applications application-set GAMING_CONSOLES_TUNED application junos-stun  
    set applications application-set GAMING_CONSOLES_TUNED application XBOX-UDP-3544

### Appendix 2: Sample Session and PBA Logs

Sample session-init and session-close logs with all columns:
    
    
    RT_FLOW - RT_FLOW_SESSION_CREATE [source-address="10.0.10.10" source-port="46776" destination-address="1.2.84.162" destination-port="80" connection-tag="0" service-name="junos-http" nat-source-address="1.2.84.172" nat-source-port="53328" nat-destination-address="1.2.84.162" nat-destination-port="80" nat-connection-tag="0" src-nat-rule-type="source rule" src-nat-rule-name="untrust" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="permit" source-zone-name="trust" destination-zone-name="untrust" session-id="92317" username="N/A" roles="N/A" packet-incoming-interface="ge-0/0/0.0" application="UNKNOWN" nested-application="UNKNOWN" encrypted="UNKNOWN" application-category="N/A" application-sub-category="N/A" application-risk="-1" application-characteristics="N/A" src-vrf-grp="N/A" dst-vrf-grp="N/A" tunnel-inspection="Off" tunnel-inspection-policy-set="root"]   
    
    RT_FLOW - RT_FLOW_SESSION_CLOSE [reason="TCP FIN" source-address="10.0.10.2" source-port="63996" destination-address="1.2.84.162" destination-port="80" connection-tag="0" service-name="junos-http" nat-source-address="1.2.84.169" nat-source-port="4986" nat-destination-address="1.2.84.162" nat-destination-port="80" nat-connection-tag="0" src-nat-rule-type="source rule" src-nat-rule-name="untrust" dst-nat-rule-type="N/A" dst-nat-rule-name="N/A" protocol-id="6" policy-name="permit" source-zone-name="trust" destination-zone-name="untrust" session-id="178" packets-from-client="663496" bytes-from-client="34501936" packets-from-server="719792" bytes-from-server="1079262436" elapsed-time="249" application="UNKNOWN" nested-application="UNKNOWN" username="N/A" roles="N/A" packet-incoming-interface="ge-0/0/0.0" encrypted="UNKNOWN" application-category="N/A" application-sub-category="N/A" application-risk="-1" application-characteristics="N/A" secure-web-proxy-session-type="NA" peer-session-id="0" peer-source-address="0.0.0.0" peer-source-port="0" peer-destination-address="0.0.0.0" peer-destination-port="0" hostname="NA NA" src-vrf-grp="N/A" dst-vrf-grp="N/A" tunnel-inspection="Off" tunnel-inspection-policy-set="root" session-flag="0"] 

Port Block Allocation logs – block allocation, interim log and block release.
    
    
    RT_NAT - RT_SRC_NAT_PBA_ALLOC [internal-ip="10.0.10.10" block-used="1" block-max-per-host="4" block-port-low="48640" block-port-high="48895" reflexive-ip="1.2.84.172" nat-pool-name="guest" logical-system-id="0" epoch-time-64="624b0492"]   
    
    RT_NAT - RT_SRC_NAT_PBA_INTERIM [internal-ip="10.0.10.10" block-used="1" block-max-per-host="4" block-port-low="48640" block-port-high="48895" reflexive-ip="1.2.84.172" nat-pool-name="guest" logical-system-id="0" epoch-time-64="624b0492"]   
    
    RT_NAT - RT_SRC_NAT_PBA_RELEASE [internal-ip="10.0.10.10" block-used="0" block-max-per-host="4" block-port-low="48640" block-port-high="48895" reflexive-ip="1.2.84.172" nat-pool-name="guest" logical-system-id="0" epoch-time-64="624b0cc7"] 

### Appendix 3: Sample pba-stat Tool Output

The output below, along with extra comments explaining its meaning, indicates:

  * The max/min/avg usage of NAT pool IPs by internal hosts is balanced and does not approach the maximum number of available blocks.  

  * Most hosts are using one block; based on the averages, there may be an option to reduce the block size.  

  * There is already one or more hosts using almost all the available port resources; these hosts can be listed using the port-threshold parameter for further analysis (a typical case is malware infection).

    
    
    ------------------------------      
    NAT-IP : #int-hosts/alloc blk       
    --------------->                    
    1.2.84.0        : 10/11            // specific NAT pool IP serves 10 endpoints with 11 allocated blocks  
    1.2.84.1        : 11/13             
    <SNIP>                              
    1.2.87.254      : 11/11             
    1.2.87.255      : 11/11             
    ------------------------------      
    Int-hosts per NAT-IP stats         // stats of maximum/minimum/avg number of hosts using one NAT pool IP  
    --------------->                    
    max             : 25                 
    min             : 5                 
    avg             : 13.86             
    ------------------------------      
    Blk per NAT-IP                      
    --------------->                    
    capacity        : 50               // maximum blocks per NAT IP  
    max used        : 28               // current maximum used  
    min used        : 5                 
    avg used        : 14.93             
    ------------------------------      
    PBA pool stats                      
    --------------->                    
    blk size        : 1280              
    maximum blk     : 3                 
    total blk       : 51200             
    allocated blk   : 15284             
    utilization     : 29.9%             
    ------------------------------      
    Int-host stats                      
    --------------->                    
    unique hosts    : 14189              
    avg blk         : 1.08              
    total sess      : 539725           // session terminology instead of ports (e.g., GRE doesn't have port)  
    max sess        : 3834             // maximum number of sessions per endpoint (port-threshold to list those)  
    avg sess        : 38.0             // average sessions per endpoint  
    ------------------------------      
    Stats per alloc blk cohort          
    --------------->                    
    blk/hosts       : 1/13275          // 13275 endpoints have 1 block  
    blk/hosts       : 2/733            // 733 endpoints 2 blocks  
    blk/hosts       : 3/181            // 181 endpoints 3 blocks  
    ----------------                    
    blk/percent     : 1/93.6%          // percentual representation of above  
    blk/percent     : 2/5.2%            
    blk/percent     : 3/1.3%            
    ----------------                    
    blk/max sess    : 1/630            // endpoints with 1 block have max of 630 sessions  
    blk/max sess    : 2/1137           // endpoints with 2 blocks have max of 1137 sessions  
    blk/max sess    : 3/3834           // endpoints with 3 blocks have max of 3834 sessions  
    ----------------                    
    blk/avg sess    : 1/33             // endpoints with 1 block have on avg 33 sessions  
    blk/avg sess    : 2/69             // endpoints with 2 blocks have on avg 69 sessions  
    blk/avg sess    : 3/283            // endpoints with 3 blocks have on avg 283 sessions  
    ------------------------------    

### Appendix 4: SFTP Site for Junos Archival

For remote SFTP archival, OpenSSH allows to configure an SFTP-only user with a chroot to a specific folder by using the "Match" stanza in the sshd_config file. The directory with write permissions for the archival user would be the upload directory specified in the SFTP URL above. The chroot directory itself must not be writable by the user.
    
    
    Match User archival  
            ForceCommand internal-sftp  
            PasswordAuthentication yes  
            ChrootDirectory /mnt/storage/archival  
            PermitTunnel no  
            AllowAgentForwarding no  
            AllowTcpForwarding no  
            X11Forwarding no  
            AllowStreamLocalForwarding no

### Useful links

  * [https://www.juniper.net/content/dam/www/assets/datasheets/fr/fr/security/srx4600-services-gateway.pdf](https://www.juniper.net/content/dam/www/assets/datasheets/fr/fr/security/srx4600-services-gateway.pdf "https://www.juniper.net/content/dam/www/assets/datasheets/fr/fr/security/srx4600-services-gateway.pdf")  

  * [https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/denial-of-service.pdf](https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/denial-of-service.pdf "https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/denial-of-service.pdf")  

  * [https://www.juniper.net/documentation/us/en/software/junos/nat/nat.pdf](https://www.juniper.net/documentation/us/en/software/junos/nat/nat.pdf "https://www.juniper.net/documentation/us/en/software/junos/nat/nat.pdf")  

  * [https://www.juniper.net/documentation/us/en/software/junos/alg/alg.pdf](https://www.juniper.net/documentation/us/en/software/junos/alg/alg.pdf "https://www.juniper.net/documentation/us/en/software/junos/alg/alg.pdf")  

  * [https://www.juniper.net/documentation/us/en/software/junos/security-policies/security-policies.pdf](https://www.juniper.net/documentation/us/en/software/junos/security-policies/security-policies.pdf "https://www.juniper.net/documentation/us/en/software/junos/security-policies/security-policies.pdf")  

  * [https://www.juniper.net/documentation/us/en/software/junos/flow-packet-processing/flow-packet-processing.pdf](https://www.juniper.net/documentation/us/en/software/junos/flow-packet-processing/flow-packet-processing.pdf "https://www.juniper.net/documentation/us/en/software/junos/flow-packet-processing/flow-packet-processing.pdf")  

  * [https://apps.juniper.net/port-checker/mx204/](https://apps.juniper.net/port-checker/mx204/ "https://apps.juniper.net/port-checker/mx204/")  

  * [https://community.juniper.net/blogs/karel-hendrych/2024/02/07/using-junos-snmp-utility-mib-on-juniper-srx](https://community.juniper.net/blogs/karel-hendrych/2024/02/07/using-junos-snmp-utility-mib-on-juniper-srx "https://community.juniper.net/blogs/karel-hendrych/2024/02/07/using-junos-snmp-utility-mib-on-juniper-srx")  

  * [https://github.com/JNPRAutomate/srx-pba-stat](https://github.com/JNPRAutomate/srx-pba-stat "https://github.com/JNPRAutomate/srx-pba-stat")  

  * [https://github.com/JNPRAutomate/srx-pba-utility-mib](https://github.com/JNPRAutomate/srx-pba-utility-mib "https://github.com/JNPRAutomate/srx-pba-utility-mib")

### Glossary

  * ACT Advanced Connection Tracking  

  * ALG Application Layer Gateway  

  * API Application Programming Interface  

  * CGN Carrier Grade NAT  

  * DDoS Distributed Denial of Service  

  * DNS Domain Name System  

  * DoS Denial of Service  

  * FTP File Transfer Protocol  

  * Gbps Gigabits Per Second  

  * HA High Availability  

  * HTTP Hyper Text Transfer Protocol  

  * IOC Input Output Card  

  * KPI Key Performance Indicator  

  * MIB Management Information Base  

  * MPPS Million Packets Per Second  

  * MSS Maximum Segment Size  

  * NAT Network Address Translation  

  * NTP Network Time Protocol  

  * P2P Peer to Peer  

  * PBA Port Block Allocation  

  * PFE Packet Forwarding Engine  

  * PIC Physical Interface Card  

  * PPTP Point to Point Tunneling Protocol  

  * RADIUS Remote Authentication Dial-In User Service)  

  * RPF Reverse Path Filtering  

  * SFTP Secure File Transfer Protocol  

  * SIP Session Initiation Protocol  

  * SNMP Small Network Monitoring Protocol  

  * SSH Secure Shell   

  * STUN Session Traversal Utilities for NAT  

  * TCP Transmission Control Protocol  

  * TLS Transport Layer Security  

  * UDP User Datagram Protocol  

  * URL Uniform Resource Locator  

  * VRRP Virtual Router Redundancy Protocol  

### Acknowledgments

I would like to acknowledge all the brilliant people I have the pleasure of working closely with— Mark Barrett, Kelly Brazil, Tim Carlens, Steven Jacques, David Kuncar, Matthijs Nagel, Pawel Rabiej and others from the JNPR team! Finally, I extend my gratitude to the vSRX/SRX development and product teams for delivering the Swiss Army knife of security and networking.

### Comments

If you want to reach out for comments, feedback or questions, drop us a mail at:

### Revision History

**Version** | **Author(s)** | **Date** | **Comments**  
---|---|---|---  
1 | Karel Hendrych | November 2024 | Initial Publication  
2 | Karel Hendrych | March 2025 | Typos fixed  
  
[](https://community.juniper.net/home/techpost)

  
[#SolutionsandTechnology](https://community.juniper.net/search?s=tags%3A%22Solutions and Technology%22&executesearch=true)

  
[#SRXSeries](https://community.juniper.net/search?s=tags%3A%22SRX Series%22&executesearch=true)

0 comments 

101 views 

##  Permalink

https://community.juniper.net/blogs/karel-hendrych/2024/11/15/srx4600-cgn-configuration-breakdown

© 2025 Hewlett Packard Enterprise Development LP 

[Powered by Higher Logic](http://www.higherlogic.com)
