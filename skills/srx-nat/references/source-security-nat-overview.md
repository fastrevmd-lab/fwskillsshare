# NAT Overview

Source: https://www.juniper.net/documentation/us/en/software/junos/nat/topics/topic-map/security-nat-overview.html
HTTP: 200 OK
Extractor: body
Retrieved: 2026-05-15

---

X

Help us improve your experience.

Let us know what you think.

Do you have time for a two-minute survey?

Yes

Maybe Later

##### ON THIS PAGE

  * Introduction to NAT

  * Understanding NAT Rule Sets and Rules

  * Additional Platform Information

# NAT Overview

Network Address Translation (NAT) is a mechanism to translate the IP address of a computer or group of computers into a single public address when the packets are sent out to the Internet. By translating the IP address, only one IP address is publicized to the outside network. Since only one IP address is visible to the outside world, NAT provides additional security and it can have only one public address for the entire network instead of having multiple IP addresses.

Use [Feature Explorer](https://apps.juniper.net/feature-explorer/) to confirm platform and release support for specific features. Additional platforms might be supported.

## Introduction to NAT

Network Address Translation (NAT) is a method for modifying or translating network address information in packet headers. Either or both source and destination addresses in a packet may be translated. NAT can include the translation of port numbers as well as IP addresses.

NAT is described in RFC 1631 to solve IP (version 4) address depletion problems. Since then, NAT has been found to be a useful tool for firewalls, traffic redirect, load sharing, network migrations, and so on.

The following types of NAT are supported on Juniper Networks devices:

  * Static NAT

  * Destination NAT

  * Source NAT

SRX Series Firewalls perform both policy lookup and service lookup based on the translated destination port.

You can use the NAT Wizard to perform basic NAT configuration. To perform more advanced configuration, use the J-Web interface or the CLI.

### See Also

  * [Source NAT](../concept/../topic-map/nat-security-source-and-source-pool.html)

  * [Destination NAT](../concept/../topic-map/security-nat-destination.html)

  * [Static NAT](../concept/../topic-map/security-nat-static.html)

## Understanding NAT Rule Sets and Rules

NAT processing centers on the evaluation of NAT rule sets and rules. A rule set determines the overall direction of the traffic to be processed. For example, a rule set can select traffic from a particular interface or to a specific zone. A rule set can contain multiple rules. Once a rule set is found that matches specific traffic, each rule in the rule set is evaluated for a match. Each rule in the rule set further specifies the traffic to be matched and the action to be taken when traffic matches the rule.

This topic includes the following sections:

  * NAT Rule Sets
  * NAT Rules
  * Rule Processing
  * NAT Rule Capacity

### NAT Rule Sets

A rule set specifies a general set of matching conditions for traffic. For static NAT and destination NAT, a rule set specifies one of the following:

  * Source interface

  * Source zone

  * Source routing instance

For source NAT rule sets, you configure both source and destination conditions:

  * Source interface, zone, or routing instance

  * Destination interface, zone, or routing instance

It is possible for a packet to match more than one rule set; in this case, the rule set with the more specific match is used. An interface match is considered more specific than a zone match, which is more specific than a routing instance match. If a packet matches both a destination NAT rule set that specifies a source zone and a destination NAT rule set that specifies a source interface, the rule set that specifies the source interface is the more specific match.

Source NAT rule set matching is more complex because you specify both source and destination conditions in a source NAT rule set. In the case where a packet matches more than one source NAT rule set, the rule set chosen is based on the following source/destination conditions (in order of priority):

  1. Source interface/destination interface

  2. Source zone/destination interface

  3. Source routing instance/destination interface

  4. Source interface/destination zone

  5. Source zone/destination zone

  6. Source routing instance/destination zone

  7. Source interface/destination routing instance

  8. Source zone/destination routing instance

  9. Source routing instance/destination routing instance

For example, you can configure rule set A, which specifies a source interface and a destination zone, and rule set B, which specifies a source zone and a destination interface. If a packet matches both rule sets, rule set B is the more specific match.

You cannot specify the same source and destination conditions for source NAT rule sets.

### NAT Rules

Once a rule set that matches the traffic has been found, each rule in the rule set is evaluated in order for a match. NAT rules can match on the following packet information:

  * Source and destination address

  * Source port (for source and static NAT only)

  * Destination port

The first rule in the rule set that matches the traffic is used. If a packet matches a rule in a rule set during session establishment, traffic is processed according to the action specified by that rule.

You can use the show security nat source rule and show security nat destination rule and the show security nat static rule commands to view the number of sessions for a specific rule.

### Rule Processing

The NAT type determines the order in which NAT rules are processed. During the first packet processing for a flow, NAT rules are applied in the following order:

  1. Static NAT rules

  2. Destination NAT rules

  3. Route lookup

  4. Security policy lookup

  5. Reverse mapping of static NAT rules

  6. Source NAT rules

Figure 1 illustrates the order for NAT rule processing.

Figure 1:  NAT Rule Processing

Static NAT and destination NAT rules are processed before route and security policy lookup. Static NAT rules take precedence over destination NAT rules. Reverse mapping of static NAT rules takes place after route and security policy lookup and takes precedence over source NAT rules. Source NAT rules are processed after route and security policy lookup and after reverse mapping of static NAT rules.

The configuration of rules and rule sets is basically the same for each type of NAT—source, destination, or static. But because both destination and static NAT are processed before route lookup, you cannot specify the destination zone, interface or routing instance in the rule set.

### NAT Rule Capacity

The NAT rule capacity requirement depends on the SRX Series Firewall and the Junos OS release.

The restriction on the number of rules per rule set is a device-wide limitation on how many rules a device can support. This restriction is provided to help you better plan and configure the NAT rules for the device.

For memory consumption, there is no guarantee to support these numbers (maximum source rule or rule set + maximum destination rule or rule set + maximum static rule or rule-set).

The NAT rule capacity requirement depends on the SRX Series Firewall and the Junos OS release.

Use [Feature Explorer](https://apps.juniper.net/feature-explorer/) to confirm platform and release support for specific features. Additional platforms may be supported.

See the [Additional Platform Information](../concept/../topic-map/security-nat-overview.html#concept_mrn_m2c_n2c) section for more information.

## Additional Platform Information

Use [Feature Explorer](https://apps.juniper.net/feature-explorer/) to confirm platform and release support for specific features. Additional platforms may be supported.

NAT Rule Type |  SRX300SRX320 |  SRX340SRX345 |  SRX1500SRX1600 |  SRX2300, SRX4120SRX4100SRX4200 |  SRX4600SRX5400SRX5600SRX5800 |  SRX4700
---|---|---|---|---|---|---
Source NAT rule |  1024 |  2048 |  8192 |  20,480 |  30,720 |  51200
Destination NAT rule |  1024 |  2048 |  8192 |  20,480 |  30,720 |  51200
Static NAT rule |  1024 |  2048 |  8192 |  20,480 |  30,720 |  51200

Objects |  SRX1600SRX2300, SRX4120 |  SRX4600SRX5400SRX5600SRX5800 |  SRX4700
---|---|---|---
Total NAT rule sets per system |  10,000  |  30,720 |  51200
Total NAT rules per rule set |  10,000  |  30,720 |  51200

Platform | Number of IPs supported with OL
---|---
vSRX small VSRX-2CPU-4G | 1
SRX1600 | 2
SRX2300, SRX4120 | 16
SRX4300 | 16
vSRX XL VSRX-17CPU-32G | 64
SRX4700 | 128
SRX5000 line of devices | 128

## Change History Table

Feature support is determined by the platform and release you are using. Use [Feature Explorer](https://apps.juniper.net/feature-explorer/) to determine if a feature is supported on your platform.

Release

Description

19.3R1

Starting from Junos OS Release 19.3R1, SRX5000 line devices with SRX5K-SPC3 card, SRX4100, SRX4200, and vSRX Virtual Firewall instances support NAT features such as source NAT, destination NAT, and static NAT for both IPv4 and IPv6 traffic in PowerMode IPsec (PMI) mode. NAT64 is not supported in PMI mode. However, NAT64 works properly in normal mode, when PMI is enabled.
