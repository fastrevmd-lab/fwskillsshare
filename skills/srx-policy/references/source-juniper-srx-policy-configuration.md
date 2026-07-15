# Juniper SRX Policy Configuration

Source URL: https://rayka-co.com/lesson/juniper-srx-policy-configuration/
Final URL: https://rayka-co.com/lesson/juniper-srx-policy-configuration/
HTTP status: 200
Extractor: htmlparser
Extracted characters: 13193

## Extracted text

7. Juniper SRX Policy Configuration - RAYKA (are you a network engineer?)

Skip to content

[email protected] 011 322 44 56 Monday – Friday 10 AM – 8 PM

cart: $ 0.00 0

View Cart Checkout

No products in the cart.

Subtotal: $ 0.00

View Cart Checkout

YouTube page opens in new window Linkedin page opens in new window X page opens in new window

RAYKA (are you a network engineer?)

are you a network engineer?

Courses
DEVOPS_AUTOMATION devops and automation courses like ansible, cisco devnet and bash scripting

CISCO NETWORKING cisco networking, security, cloud, devnet and service provider courses
SERVICE PROVIDER mpls, segment routing,mpls services like mpls vpn, vpls and mpls te

Cisco Security

Data Center

SDN-based NETWORK sd-access, sd-wan and sdn based data center

Juniper
Juniper Security

F5 BIG-IP

Free Courses

Shop
Service Provider

Security

DevOps / Automation

Data Center

SDN-based Networks

Juniper

F5

About
About Teachers

Privacy Policy

Contact Us

discount

Search:

My-Account
Login
Register

Courses
DEVOPS_AUTOMATION devops and automation courses like ansible, cisco devnet and bash scripting

CISCO NETWORKING cisco networking, security, cloud, devnet and service provider courses
SERVICE PROVIDER mpls, segment routing,mpls services like mpls vpn, vpls and mpls te

Cisco Security

Data Center

SDN-based NETWORK sd-access, sd-wan and sdn based data center

Juniper
Juniper Security

F5 BIG-IP

Free Courses

Shop
Service Provider

Security

DevOps / Automation

Data Center

SDN-based Networks

Juniper

F5

About
About Teachers

Privacy Policy

Contact Us

discount

7. Juniper SRX Policy Configuration

You are here:

Home

Lesson

7. Juniper SRX Policy Configuration

Juniper SRX security policy is the main task of the SRX device to control traffic between zones.

Unlike firewall filter it works stateful. That means you only have to permit from the initiator zone to the destination zone. Return traffic is automatically allowed based on the session table.

In this section we will learn how to configure security policy. security policy monitoring will be discussed in the next specific section because of its importance.

Configuring Security Policies in Juniper SRX

Juniper SRX security policy structure

as you know and we have discussed in the second lesson “ Juniper SRX Traffic Flow” , policy is the main target of a juniper SRX device. It control traffic between zones, stateful.

In this section, we will learn how to configure a security policy.

As you see in the figure, security policies have to be configured between zones.

Juniper Security Policy structure

Between each zone-pair, you can configure as many policy, you need. The order of policies are important and they are process in order until there is match with the traffic.

By default, there is implicit deny-all rule at the end of zone-pair policies. In other words, if the traffic is not matched with any of configured policies, then it will be discarded.

It is recommend that you write your explicit “deny-all” policy at the of each zone-pair policies in order to also log discarded traffics.

For each policy we have to match the traffic. matching source address, destination address and application is necessary for each security policy.

Address and application must be “any” or selected from address book and application list that we have already prepared. In the previous sections, we have discussed both of these topics.

For each policy, we have to also select an action which is normally to permit or reject the traffic. with reject, SRX send an icmp message to the source of traffic to inform that the traffic is discarded. But with discard, traffic is discarded silently.

It is recommended to also log and count important traffic. in addition to permit/reject/discard actions, you are allowed to choose log and count actions simultaneously.

The topology to configure security policy

This is the topology, on which we will configure our first security policy.

Juniper Security Policy Topology

Juniper SRX is connected to outside zone through interface Gigabit Ethernet 0 and with IP subnet 192.168.1.0/24. It is also connected to inside zone through interface Gigabit Ethernet 1 and with IP subnet 192.168.10.0/24.

Our target is to permit, log and count http, icmp and telnet traffic from inside zone to outside zone. We discard and log all other traffic through configuring explicit “deny-all” policy.

Juniper SRX security policy configuration example

This is the configuration that we will apply to the juniper SRX device. All policies are configured from inside-zone to the outside-zone.

[edit] rayka# show | compare [edit security policies] from-zone outside to-zone junos-host { ... } + from-zone inside to-zone outside { + policy PERMIT-WEB { + match { + source-address NET_192_168_10_0__24; + destination-address any; + application junos-http; + } + then { + permit; + log { + session-init; + session-close; + } + count; + } + } + policy PERMIT-TELNET { + match { + source-address NET_192_168_10_0__24; + destination-address any; + application junos-telnet; + } + then { + permit; + log { + session-init; + session-close; + } + count; + } + } + policy PERMIT-ICMP { + match { + source-address NET_192_168_10_0__24; + destination-address any; + application junos-icmp-all; + } + then { + permit; + log { + session-init; + } + count; + } + } + policy DENY-ALL { + match { + source-address any; + destination-address any; ! set security policies from-zone inside to-zone outside policy PERMIT-WEB match source-address NET_192_168_10_0__24 set security policies from-zone inside to-zone outside policy PERMIT-WEB match destination-address any set security policies from-zone inside to-zone outside policy PERMIT-WEB match application junos-http set security policies from-zone inside to-zone outside policy PERMIT-WEB then permit set security policies from-zone inside to-zone outside policy PERMIT-WEB then log session-init set security policies from-zone inside to-zone outside policy PERMIT-WEB then log session-close set security policies from-zone inside to-zone outside policy PERMIT-WEB then count ! set security policies from-zone inside to-zone outside policy PERMIT-TELNET match source-address NET_192_168_10_0__24 set security policies from-zone inside to-zone outside policy PERMIT-TELNET match destination-address any set security policies from-zone inside to-zone outside policy PERMIT-TELNET match application junos-telnet set security policies from-zone inside to-zone outside policy PERMIT-TELNET then permit set security policies from-zone inside to-zone outside policy PERMIT-TELNET then log session-init set security policies from-zone inside to-zone outside policy PERMIT-TELNET then log session-close set security policies from-zone inside to-zone outside policy PERMIT-TELNET then count ! set security policies from-zone inside to-zone outside policy PERMIT-ICMP match source-address NET_192_168_10_0__24 set security policies from-zone inside to-zone outside policy PERMIT-ICMP match destination-address any set security policies from-zone inside to-zone outside policy PERMIT-ICMP match application junos-icmp-all set security policies from-zone inside to-zone outside policy PERMIT-ICMP then permit set security policies from-zone inside to-zone outside policy PERMIT-ICMP then log session-init set security policies from-zone inside to-zone outside policy PERMIT-ICMP then count ! set security policies from-zone inside to-zone outside policy DENY-ALL match source-address any set security policies from-zone inside to-zone outside policy DENY-ALL match destination-address any set security policies from-zone inside to-zone outside policy DENY-ALL match application any set security policies from-zone inside to-zone outside policy DENY-ALL then reject set security policies from-zone inside to-zone outside policy DENY-ALL then log session-init set security policies from-zone inside to-zone outside policy DENY-ALL then count set security policies pre-id-default-policy then log session-close

We write four policies. In the first policy, with the name of “PERMIT-WEB”, we will permit, log and count any traffic from the source 192.168.10.0/24 to any destination with http as application.

The source address is selected from the address-book that we have configured in the previous sections.

We log matching traffic when the sessions are initiated and terminated wit “log session-init” and “log session-close” keywords.

In the same way, telnet traffic and icmp traffic are permitted in the second and third policies with the names of “PERMIT-TELNET” and “PERMIT-ICMP”.

In the last rule, we configure a policy to deny all other traffic. we do not use the default implicit “deny-all” traffic since we are going to log and count discarded traffic which is not activated in implicit deny rule.

test the result of Juniper SRX security policy

Just to test the result of our policy, I will ping , telnet and create an http connection from inside to outside zone. It is expected that all these sessions will be open.

We also create a ftp connection from inside to outside zone and it is expected that it does not work.

In the next section , we will discuss how to monitor and troubleshoot security policies but now just to make sure that the traffic is really transferred through juniper SRX, we can check traffic flow with “show security flow session” command.

<pre><code>[edit] rayka# run show security flow session Session ID: 144635, Policy name: PERMIT-WEB/ 6, State: Stand-alone, Timeout: 280, Valid   In: 192.168.10.121/61463 --> 192.168.1.88/80;tcp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 4, Bytes: 769,   Out: 192.168.1.88/80 --> 192.168.10.121/61463;tcp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 2, Bytes: 303, Session ID: 144636, Policy name: PERMIT-WEB/6, State: Stand-alone, Timeout: 280, Valid   In: 192.168.10.121/61464 --> 192.168.1.88/80;tcp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 2, Bytes: 98,   Out: 192.168.1.88/80 --> 192.168.10.121/61464;tcp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 1, Bytes: 52, Session ID: 144647, Policy name: PERMIT-TELNET /8, State: Stand-alone, Timeout: 1792, Valid   In: 192.168.10.121/61465 --> 192.168.1.88/23;tcp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 5, Bytes: 257,   Out: 192.168.1.88/23 --> 192.168.10.121/61465;tcp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 4, Bytes: 236, Session ID: 144676, Policy name: PERMIT-ICMP/ 9, State: Stand-alone, Timeout: 2, Valid   In: 192.168.10.121/1 --> 192.168.1.88/29;icmp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 1, Bytes: 60,   Out: 192.168.1.88/29 --> 192.168.10.121/1;icmp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 1, Bytes: 60, Session ID: 144678, Policy name: PERMIT-ICMP/9, State: Stand-alone, Timeout: 2, Valid   In: 192.168.10.121/1 --> 192.168.1.88/30;icmp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 1, Bytes: 60,   Out: 192.168.1.88/30 --> 192.168.10.121/1;icmp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 1, Bytes: 60, Session ID: 144680, Policy name: PERMIT-ICMP/9, State: Stand-alone, Timeout: 4, Valid   In: 192.168.10.121/1 --> 192.168.1.88/31;icmp, Conn Tag: 0x0, If: ge-0/0/1.0, Pkts: 1, Bytes: 60,   Out: 192.168.1.88/31 --> 192.168.10.121/1;icmp, Conn Tag: 0x0, If: ge-0/0/0.0, Pkts: 1, Bytes: 60, Total sessions: 6</code></pre>

You can see that all teh policies from inside zone to outside zone are matched with the traffic.

Back to: Juniper Security Associate (JNCIA-SEC) based on vSRX version 22.1R1.10 > Security Policies

Leave a Reply Cancel reply

Your email address will not be published. Required fields are marked *

Comment

Name * Email * Website

Save my name, email, and website in this browser for the next time I comment.

Post comment

discount until November 7, 2024, at 23:59 (UTC+1, CEST)



Get 85% discount

Coupon: halloween2024

until November 7, 2024, at 23:59 (UTC+1, CEST)

discount subscription

RAYKA

Cisco Networking

YouTube Video VVVUcmdvbF9fbllTclFCaF9qMlBjTjRRLldDMEJSRjVlcGtR

Load More... Subscribe

LATEST COURSES

Docker Container and GitLab CI/CD for Network Engineers (in Progress) 4 Lessons

MPLS & MPLS VPN Fundamental 22 Lessons

Network Automation with pyATS & Genie 22 Lessons

IPv6 35 Lessons

F5 BIG-IP AWAF (formerly ASM) 27 Lessons

LATEST LESSONS

4. Docker Commands in Practice Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress)

3. Docker Image vs Docker Container Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress)

2. Install Docker on Ubuntu Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress)

1. Containers and CI/CD in Network Automation : Definition and Applications Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress)

22. Carrier Supporting Carriers Part of: MPLS & MPLS VPN Fundamental

More Lessons

Go to Top

We noticed you're visiting from United States (US). We've updated our prices to United States (US) dollar for your shopping convenience. Use Euro instead. Dismiss
