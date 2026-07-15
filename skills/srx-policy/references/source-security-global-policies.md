# Global Policy Overview | Junos OS

Source URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-global-policies.html
HTTP status: 200
Extracted characters: 14657

## Extracted text


Global Security Policies | Junos OS | Juniper Networks
X
Help us improve your experience.

Let us know what you think.

Do you have time for a two-minute survey?
Yes Maybe Later ON THIS PAGE

Global Policy Overview

Example: Configuring a Global Policy with No Zone Restrictions

Example: Configuring a Global Policy with Multiple Zones

Global Security Policies

A security policy is a stateful firewall policy and controls the traffic flow from one zone to another zone by defining the kind(s) of traffic permitted from specific IP sources to specific IP destinations at scheduled times. To avoid creating multiple policies across every possible context, you can create a global policy that encompasses all zones, or a multizone policy that encompasses several zones. Using a global policy, you can regulate traffic with addresses and applications, regardless of their security zones, by referencing user-defined addresses or the predefined address and also provides access to multiple source zones and multiple destination zones in one policy.

Global Policy Overview

In a Junos OS stateful firewall, security policies enforce rules for transit traffic, in terms of what traffic can pass through the firewall, and the actions that need to take place on traffic as it passes through the firewall. Security policies require traffic to enter one security zone and exit another security zone. This combination of a from-zone and to-zone is called a context . Each context contains an ordered list of policies. Each policy is processed in the order that it is defined within a context. Traffic is classified by matching the policy’s from-zone, to-zone, source address, destination address, and the application that the traffic carries in its protocol header. Each global policy, as with any other security policy, has the following actions: permit, deny, reject, log, count.

You can configure a security policy from the user interface. Security policies control traffic flow from one zone to another zone by defining the kind(s) of traffic permitted from specific IP sources to specific IP destinations at scheduled times. This works well in most cases, but it is not flexible enough. For example, if you want to perform actions on traffic you have to configure policies for each possible context. To avoid creating multiple policies across every possible context, you can create a global policy that encompasses all zones, or a multizone policy that encompasses several zones.

Using a global policy, you can regulate traffic with addresses and applications, regardless of their security zones, by referencing user-defined addresses or the predefined address “any.” These addresses can span multiple security zones. For example, if you want to provide access to or from multiple zones, you can create a global policy with the address “any,” which encompasses all addresses in all zones. Selecting the “any” address matches any IP address, and when “any” is used as a source/destination address in any global policy configuration, it matches the source/destination address of any packet.

Using a global policy you can also provide access to multiple source zones and multiple destination zones in one policy. However, we recommend that, for security reasons and to avoid spoofing traffic, when you create a multizone policy you use identical matching criteria (source address, destination address, application) and an identical action. In Figure 1 , for example, if you create a multizone policy that includes DMZ and Untrust from-zones, spoofing traffic from 203.0.113.0/24 from the DMZ zone could match the policy successfully and reach the protected host in the Trust to-zone.
Figure 1: Multizone Global Policy Security Consideration Note:
Global policies without from-zone and to-zone information do not support VPN tunnels because VPN tunnels require specific zone information.

When policy lookup is performed, policies are checked in the following order: intra-zone (trust-to-trust), inter-zone (trust-to-untrust), then global. Similar to regular policies, global policies in a context are ordered, such that the first matched policy is applied to the traffic.
Note:
If you have a global policy, make sure you have not defined a “catch-all” rule such as, match source any, match destination any, or match application any in the intra-zone or inter-zone policies because the global policies will not be checked. If you do not have a global policy, then it is recommended that you include a “deny all” action in your intra-zone or inter-zone policies. If you do have a global policy, then you should include a “deny all” action in the global policy.

In logical systems, you can define global policies for each logical system. Global policies in one logical system are in a separate context than other security policies, and have a lower priority than regular security policies in a policy lookup. For example, if a policy lookup is performed, regular security policies have priority over global policies. Therefore, in a policy lookup, regular security policies are searched first and if there is no match, global policy lookup is performed.

See Also

Security Policies Overview

Understanding Security Policy Rules

Understanding Security Policy Elements

Example: Configuring a Global Policy with No Zone Restrictions

Unlike other security policies in Junos OS, global policies do not reference specific source and destination zones. Global policies reference the predefined address “any” or user-defined addresses that can span multiple security zones. Global policies give you the flexibility of performing actions on traffic without any zone restrictions. For example, you can create a global policy so that every host in every zone can access the company website, for example, www.example.com. Using a global policy is a convenient shortcut when there are many security zones. Traffic is classified by matching its source address, destination address, and the application that the traffic carries in its protocol header.

This example shows how to configure a global policy to deny or permit traffic.

Requirements

Overview

Configuration

Verification

Requirements

Before you begin:

Review the firewall security policies.

See Security Policies Overview , Global Policy Overview , Understanding Security Policy Rules , and Understanding Security Policy Elements .

Configure an address book and create addresses for use in the policy.

See Example: Configuring Address Books and Address Sets .

Create an application (or application set) that indicates that the policy applies to traffic of that type.

See Example: Configuring Security Policy Applications and Application Sets .

Overview

This configuration example shows how to configure a global policy that accomplishes what multiple security policies (using zones) would have accomplished. Global policy gp1 permits all traffic while policy gp2 denies all traffic.

Topology

Configuration

CLI Quick Configuration

Procedure

CLI Quick Configuration

To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the
[edit] hierarchy level, and then enter
commit from configuration mode.

set security address-book global address server1 dns-name www.example.com set security address-book global address server2 dns-name www.mail.example.com set security policies global policy gp1 match source-address server1 set security policies global policy gp1 match destination-address server2 set security policies global policy gp1 match application any set security policies global policy gp1 then permit set security policies global policy gp2 match source-address server2 set security policies global policy gp2 match destination-address server1 set security policies global policy gp2 match application junos-ftp set security policies global policy gp2 then deny

Procedure

Step-by-Step Procedure

Results
Step-by-Step Procedure
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode in the CLI User guide.

To configure a global policy to permit or deny all traffic:

Create addresses.

[edit security] user@host# set security address-book global address server1 dns-name www.example.com user@host# set security address-book global address server2 dns-name www.mail.example.com

Create the global policy to permit all traffic.

[edit security] user@host# set policy global policy gp1 match source-address server1 user@host# set policy global policy gp1 match destination-address server2 user@host# set policy global policy gp1 match application any user@host# set policy global policy gp1 then permit

Create the global policy to deny all traffic.

[edit security] user@host# set policy global policy gp2 match source-address server2 user@host# set policy global policy gp2 match destination-address server1 user@host# set policy global policy gp2 match application junos-ftp user@host# set policy global policy gp2 then deny

Results
From configuration mode, confirm your configuration by entering the
show security policies and
show security policies global commands. If the output does not display the intended configuration, repeat the instructions in this example to correct the configuration.

user@host#
show security policies global { policy gp1 { match { source-address server1; destination-address server2; application any; } then { permit; } } policy gp2 { match { source-address server2; destination-address server1; application junos-ftp; } then { deny; } } }

user@host#
show security policies global policy gp1 { match { source-address server1; destination-address server2; application any; } then { permit; } } policy gp2 { match { source-address server2; destination-address server1; application junos-ftp; } then { deny; } }

If you are done configuring the device, enter
commit from configuration mode.

Verification

Verifying Global Policy Configuration

Purpose

Action

Meaning
Purpose
Verify that global policies gp1 and gp2 are configured as required.
Action
From operational mode, enter the
show security policies global command.

user@host>
show security policies global Global policies: Policy: gp1, State: enabled, Index: 6, Scope Policy: 0, Sequence number: 1 From zones: any To zones: any Source addresses: server1 Destination addresses: server2 Applications: any Action: permit Policy: gp2, State: enabled, Index: 7, Scope Policy: 0, Sequence number: 2 From zones: any To zones: any Source addresses: server2 Destination addresses: server1 Applications: junos-ftp Action: deny
Meaning
The output displays information about all the global policies configured on the device.

Example: Configuring a Global Policy with Multiple Zones

Unlike other security policies in Junos OS, global policies allow you to create multizone policies. A global policy is a convenient shortcut when there are many security zones, because it enables you to configure multiple source zones and multiple destination zones in one global policy instead of having to create a separate policy for each from-zone/to-zone pair, even when other attributes, such as source-address or destination-address, are identical.

Requirements

Overview

Configuration

Verification

Requirements

Before you begin:

Review the firewall security policies.

See Security Policies Overview , Global Policy Overview , Understanding Security Policy Rules , and Understanding Security Policy Elements .

Create security zones.

See Example: Creating Security Zones

Overview

This configuration example shows how to configure a global policy that accomplishes what multiple security policies would have accomplished. Global policy Pa permits all traffic from zones 1 and 2 to zones 3 and 4.

Topology

Configuration

CLI Quick Configuration

Procedure

CLI Quick Configuration

To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the
[edit] hierarchy level, and then enter
commit from configuration mode.

set security policies global policy Pa match source-address any set security policies global policy Pa match destination-address any set security policies global policy Pa match application any set security policies global policy Pa match from-zone zone1 set security policies global policy Pa match from-zone zone2 set security policies global policy Pa match to-zone zone3 set security policies global policy Pa match to-zone zone4 set security policies global policy Pa then permit

Procedure

Step-by-Step Procedure

Results
Step-by-Step Procedure
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode .

To configure a global policy with multiple zones:

Create a global policy to allow any traffic from zones 1 and 2 to zones 3 and 4.

[edit security] set security policies global policy Pa match source-address any set security policies global policy Pa match destination-address any set security policies global policy Pa match application any set security policies global policy Pa match from-zone zone1 set security policies global policy Pa match from-zone zone2 set security policies global policy Pa match to-zone zone3 set security policies global policy Pa match to-zone zone4 set security policies global policy Pa then permit

Results
From configuration mode, confirm your configuration by entering the
show security policies global command. If the output does not display the intended configuration, repeat the instructions in this example to correct the configuration.

[edit] user@host# show security policies global policy Pa { match { source-address any; destination-address any; application any; from-zone [ zone1 zone2 ]; to-zone [ zone3 zone4 ]; } then { permit; } }

If you are done configuring the device, enter
commit from configuration mode.

Verification

Verifying Global Policy Configuration

Purpose

Action
Purpose
Verify that the global policy is configured as required.
Action
From operational mode, enter the
show security policies global command.

Related Documentation

Security Policies Overview

Configuring Security Policies
