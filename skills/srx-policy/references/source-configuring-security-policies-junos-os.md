# Configuring Security Policies | Junos OS

Source URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html
Final URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html
HTTP status: 200
Extractor: htmlparser
Extracted characters: 68192

## Extracted text

Configuring Security Policies | Junos OS | Juniper Networks 

X 

Help us improve your experience. 

Let us know what you think. 

Do you have time for a two-minute survey? 

Yes 

Maybe Later 

ON THIS PAGE 

Understanding Security Policy Elements 

Understanding Security Policy Rules 

Policy Configuration Synchronization Enhancements 

Understanding Security Policies for Self Traffic 

Security Policies Configuration Overview 

Best Practices for Defining Policies 

Configuring Policies Using the Firewall Wizard 

Example: Configuring a Security Policy to Permit or Deny All Traffic 

Example: Configuring a Security Policy to Permit or Deny Selected Traffic 

Example: Configuring a Security Policy to Permit or Deny Wildcard Address Traffic 

Example: Configuring a Security Policy to Redirect Traffic Logs to an External System Log Server 

TAP Mode for Security Zones and Policies 

Dynamic Address Groups in Security Policies 

Platform-Specific Security Policy Behavior 

Additional Platform Information 

Configuring Security Policies 

To secure a network, a network administrator must create a security policy that outlines all of the network resources within that business and the required security level for those resources. Junos OS allows you to configure security policies. Security policies enforce rules for transit traffic, in terms of what traffic can pass through the firewall, and the actions that need to take place on traffic as it passes through the firewall. 

Understanding Security Policy Elements 

A security policy is a set of statements that controls traffic from a specified source to a specified destination using a specified service. A policy permits, denies, or tunnels specified types of traffic unidirectionally between two points. 

Each policy consists of: 

A unique name for the policy. 

A 
from-zone and a 
to-zone , for example: user@host# 
set security policies from-zone untrust to-zone untrust 

A set of match criteria defining the conditions that must be satisfied to apply the policy rule. The match criteria are based on a source IP address, destination IP address, and applications. The user identity firewall provides greater granularity by including an additional tuple, source-identity, as part of the policy statement. 

A set of actions to be performed in case of a match—permit, deny, or reject. 

Accounting and auditing elements—counting, logging, or structured system logging. 

If the device receives a packet that matches those specifications, it performs the action specified in the policy. 

Security policies enforce a set of rules for transit traffic, identifying which traffic can pass through the firewall and the actions taken on the traffic as it passes through the firewall. Actions for traffic matching the specified criteria include permit, deny, reject, log, or count. 

Understanding Security Policy Rules 

The security policy applies the security rules to the transit traffic within a context ( 
from-zone to 
to-zone ). Each policy is uniquely identified by its name. The traffic is classified by matching its source and destination zones, the source and destination addresses, and the application that the traffic carries in its protocol headers with the policy database in the data plane. 

Each policy is associated with the following characteristics: 

A source zone 

A destination zone 

One or many source address names or address set names 

One or many destination address names or address set names 

One or many application names or application set names 

These characteristics are called the match criteria . Each policy also has actions associated with it: permit, deny, reject, count, log, and VPN tunnel. You have to specify the match condition arguments when you configure a policy, source address, destination address, and application name. 

You can specify to configure a policy with IPv4 or IPv6 addresses using the wildcard entry 
any . When flow support is not enabled for IPv6 traffic, 
any matches IPv4 addresses. When flow support is enabled for IPv6 traffic, 
any matches both IPv4 and IPv6 addresses. To enable flow-based forwarding for IPv6 traffic, use the 
set security forwarding-options family inet6 mode flow-based command. You can also specify the wildcard 
any-ipv4 or 
any-ipv6 for the source and destination address match criteria to include only IPv4 or only IPv6 addresses, respectively. 

When flow support for IPv6 traffic is enabled, the maximum number of IPv4 or IPv6 addresses that you can configure in a security policy is based on the following match criteria: 

Number_of_src_IPv4_addresses + number_of_src_IPv6_addresses * 4 <= 1024 

Number_of_dst_IPv4_addresses + number_of_dst_IPv6_addresses * 4 <= 1024 

Thr reason for the match criteria is that an IPv6 address uses four times the memory space that an IPv4 address uses. 

Note: 
You can configure a security policy with IPv6 addresses only if flow support for IPv6 traffic is enabled on the device. 

If you do not want to specify a specific application, enter 
any as the default application. To look up the default applications, from configuration mode, enter 
show groups junos-defaults | find applications (predefined applications) . For example, if you do not supply an application name, the policy is installed with the application as a wildcard (default). Therefore, any data traffic that matches the rest of the parameters in a given policy would match the policy regardless of the application type of the data traffic. 

Note: 
If a policy is configured with multiple applications, and more than one of the applications match the traffic, then the application that best meets the match criteria is selected. 

The action of the first policy that the traffic matches is applied to the packet. If there is no matching policy, the packet is dropped. Policies are searched from top to bottom, so it is a good idea to place more specific policies near the top of the list. You should also place IPsec VPN tunnel policies near the top. Place the more general policies, such as one that would allow certain users access to all Internet applications, at the bottom of the list. For example, place deny-all or reject-all policies at the bottom after all of the specific policies have been parsed before and legitimate traffic has been allowed/count/logged. 

Note: 
Support for IPv6 addresses is added in Junos OS Release 10.2. Support for IPv6 addresses in active/active chassis cluster configurations (in addition to the existing support of active/passive chassis cluster configurations) is added in Junos OS Release 10.4. 

Policy look up determines the destination zone, destination address, and egress interface. 

When you are creating a policy, the following policy rules apply: 

Security policies are configured in a 
from-zone to 
to-zone direction. Under a specific zone direction, each security policy contains a name, match criteria, an action, and miscellaneous options. 

The policy name, match criteria, and action are required. 

The policy name is a keyword. 

The source address in the match criteria is composed of one or more address names or address set names in the 
from-zone . 

The destination address of the match criteria is composed of one or more address names or address set names in the 
to-zone . 

The application name in the match criteria is composed of the name of one or more applications or application sets. 

One of the following actions is required: permit, deny, or reject. 

Accounting and auditing elements can be specified: count and log. 

You can enable logging at the end of a session with the 
session-close command, or at the beginning of the session with the 
session-init command. 

When the count alarm is turned on, specify alarm thresholds in bytes per second or kilobytes per minute. 

You cannot specify 
global as either the 
from-zone or the 
to-zone except under following condition: 

Any policy configured with the 
to-zone as a global zone must have a single destination address to indicate that either static NAT or incoming NAT has been configured in the policy. 

The policy permit option with NAT is simplified. Each policy will optionally indicate whether it allows NAT translation, does not allow NAT translation, or does not care. 

Address names cannot begin with the following reserved prefixes. These are used only for address NAT configuration: 

static_nat_ 

incoming_nat_ 

junos_ 

Application names cannot begin with the 
junos_ reserved prefix. 

Understanding Wildcard Addresses 

Source and destination addresses are two of the five match criteria that should be configured in a security policy. You can now configure wildcard addresses for the source and destination address match criteria in a security policy. A wildcard address is represented as A.B.C.D/wildcard-mask. The wildcard mask determines which of the bits in the IP address A.B.C.D should be ignored by the security policy match criteria. For example, the source IP address 192.168.0.11/255.255.0.255 in a security policy implies that the security policy match criteria can discard the third octet in the IP address (symbolically represented as 192.168.*.11). Therefore, packets with source IP addresses such as 192.168.1.11 and 192.168.22.11 conform to the match criteria. However, packets with source IP addresses such as 192.168.0.1 and 192.168.1.21 do not satisfy the match criteria. 

The wildcard address usage is not restricted to full octets only. You can configure any wildcard address. For example, the wildcard address 192.168. 7.1/255.255.7.255 implies that you need to ignore only the first 5 bits of the third octet of the wildcard address while making the policy match. If the wildcard address usage is restricted to full octets only, then wildcard masks with either 0 or 255 in each of the four octets only will be permitted. 

Note: 
The first octet of the wildcard mask should be greater than 128. For example, a wildcard mask represented as 0.255.0.255 or 1.255.0.255 is invalid. 

A wildcard security policy is a simple firewall policy that allows you to permit, deny, and reject the traffic trying to cross from one security zone to another. You should not configure security policy rules using wildcard addresses for services such as Content Security . 

Note: 
Content Security for IPv6 sessions is not supported. If your current security policy uses rules with the IP address wildcard any, and Content Security features are enabled, you will encounter configuration commit errors because Content Security features do not yet support IPv6 addresses. To resolve the errors, modify the rule returning the error so that the any-ipv4 wildcard is used; and create separate rules for IPv6 traffic that do not include Content Security features. 

Configuring wildcard security policies on a device affects performance and memory usage based on the number of wildcard policies configured per from-zone and to-zone context. Therefore, you can only configure a maximum of 480 wildcard policies for a specific from-zone and to-zone context. 

See Also 

Understanding Security Policy Ordering 

Policy Configuration Synchronization Enhancements 

Enhanced policy configuration synchronization mechanism improves how policy configurations are synchronized between the Routing Engine (RE) and the Packet Forwarding Engine (PFE), enhancing system reliability and security. This mechanism ensures policies are automatically and accurately synchronized. In addition, the system effectively prevents any flow-drops during the security policy configuration change process. 

File-Serialization 

Prevent Flow Session Disruption During Policy Configuration Changes 

File-Serialization 

Perform policy changes propagation to the dataplane using file-serialization. By serializing policy configurations into files, the system ensure that they are read and applied by the PFE in a controlled and reliable manner. These serialized files are stored in designated directories and are automatically deleted after successful application, providing a more efficient and bandwidth-friendly method of synchronization. This file-based approach reduces the risk of security policy mismatches and enhances system reliability. 

By default, the file-based serialization is enabled. You can disable the file-serialization by using the following statement: 

[edit] user@host# set security policies no-file-serialization 

To re-enable the file-serialization feature, use the following statement: 

[edit] user@host# delete security policies no-file-serialization 

Or use the following statement: 

[edit] user@host# set security policies file-serialization 

Prevent Flow Session Disruption During Policy Configuration Changes 

You can avoid flow session disruption during security policy configuration changes commit. Configuration changes, such as policy match condition or action changes, addition or deletion of a policy, policy swap or change in policy order disrupts flow sessions. These changes affect PFE configuration data, potentially impacting ongoing policy searches and possibly leading to incorrect or default policy selection. That is, during the brief transition from old to new policy, sessions might match partially created data structures, causing incorrect policy matches. 

To avoid the disruption caused by security policy change, you can use the following statement: 

[edit] user@host# set security policies lookup-intact-on-commit 

When you configure the 
lookup-intact-on-commit option, restart the forwarding plane on the device or in a chassis cluster setup. 

Use the following command to check the status and eligibility of the device before enabling the 
lookup-intact-on-commit option. 

[edit] user@host> show security policies lookup-intact-on-commit 

The command output displays if the 
lookup-intact-on-commit option is already configured on the device and displays eligibility of the device in terms of available memory storage for activating 
lookup-intact-on-commit option. 

Memory and Error Handling 

Support for Logical System and Tenant System 

Memory and Error Handling 

Implementing these new synchronization mechanisms requires your system to meet specific memory requirements. Specifically, you need at least 5 percent free kernel heap and 1 percent free user heap to enable the lookup-intact-on-commit feature. This ensures that there is sufficient memory available for the file-based synchronization and dual-memory operations. In case of synchronization failures, the system is designed to automatically revert to the traditional method. 

You can use the 
show security policies lookup-intact-on-commit eligibility command to check the memory availability of the system per FPC. This output indicates if the particular FPC is eligible for configuring the 
set security policies lookup-intact-on-commit configuration. 

Support for Logical System and Tenant System 

You can configure 
lookup-intact-on-commit and 
file-serialization at the root logical system (system-level) only. Configuration at the logical-system and tenant-system levels is not supported. However, if you configure these settings at the root level, the configuration will also optimize policies configured at logical-system and tenant-system levels. 

Understanding Security Policies for Self Traffic 

Security policies are configured on the devices to apply services to the traffic flowing through the device. For example UAC and Content Security policies are configured to apply services to the transient traffic. 

Self-traffic or host traffic, is the host-inbound traffic; that is, the traffic terminating on the device or the host-outbound traffic that is the traffic originating from the device. You can now configure policies to apply services on self traffic. Services like the SSL stack service that must terminate the SSL connection from a remote device and perform some processing on that traffic, IDP services on host-inbound traffic, or IPsec encryption on host-outbound traffic must be applied through the security policies configured on self-traffic. 

When you configure a security policy for self-traffic, the traffic flowing through the device is first checked against the policy, then against the 
host-inbound-traffic option configured for the interfaces bound to the zone. 

You can configure the security policy for self-traffic to apply services to self-traffic. The host-outbound policies will work only in cases where the packet that originated in the host device goes through the flow and the incoming interface of this packet is set to local. 

The advantages of using the self-traffic are: 

You can leverage most of the existing policy or flow infrastructure used for the transit traffic. 

You do not need a separate IP address to enable any service. 

You can apply services or policies to any host-inbound traffic with the destination IP address of any interface on the device. 

Note: 
The default security policy rules do not affect self-traffic. 

Note: 
You can configure the security policy for self-traffic with relevant services only. For example, it is not relevant to configure the fwauth service on host-outbound traffic, and gprs-gtp services are not relevant to the security policies for self-traffic. 

The security policies for the self traffic are configured under the new default security zone called the junos-host zone. The junos-host zone will be part of the junos-defaults configuration, so users cannot delete it. The existing zone configurations such as interfaces, screen, tcp-rst, and host-inbound-traffic options are not meaningful to the junos-host zone. Therefore there is no dedicated configuration for the junos-host zone. 

Note: 
You can use host-inbound-traffic to control incoming connections to a device; however it does not restrict traffic going out of the device. Whereas, junos-host-zone allows you to select the application of your choice and also restrict outgoing traffic. For example, services like NAT, IDP, Content Security, and so forth can now be enabled for traffic going in or out of the device using junos-host-zone. 

Security Policies Configuration Overview 

You must complete the following tasks to create a security policy: 

Create zones. See Example: Creating Security Zones . 

Configure an address book with addresses for the policy. See Example: Configuring Address Books and Address Sets . 

Create an application (or application set) that indicates that the policy applies to traffic of that type. See Example: Configuring Security Policy Applications and Application Sets . 

Create the policy. See Example: Configuring a Security Policy to Permit or Deny All Traffic , Example: Configuring a Security Policy to Permit or Deny Selected Traffic , and Example: Configuring a Security Policy to Permit or Deny Wildcard Address Traffic . 

Create schedulers if you plan to use them for your policies. See Example: Configuring Schedulers for a Daily Schedule Excluding One Day . 

The Firewall Policy Wizard enables you to perform basic security policy configuration. For more advanced configuration, use the J-Web interface or the CLI. 

See Also 

Troubleshooting Security Policies 

Best Practices for Defining Policies 

A secure network is vital to a business. To secure a network, a network administrator must create a security policy that outlines all of the network resources within that business and the required security level for those resources. The security policy applies the security rules to the transit traffic within a context (from-zone to to-zone) and each policy is uniquely identified by its name. The traffic is classified by matching the source and destination zones, the source and destination addresses, and the application that the traffic carries in its protocol headers with the policy database in the data plane. 

Platform support depends on the Junos OS release in your installation. 

Note that as you increase the number of addresses and applications in each rule, the amount of memory that is used by the policy definition increases, and sometimes the system runs out of memory with fewer than 80,000 policies. 

To get the actual memory utilization of a policy on the Packet Forwarding Engine (PFE) and the Routing Engine (RE), you need to take various components of the memory tree into consideration. The memory tree includes the following two components: 

Policy context–Used to organize all policies in this context. Policy context includes variables such as source and destination zones. 

Policy entity–Used to hold the policy data. Policy entity calculates memory using parameters such as policy name, IP addresses, address count, applications, firewall authentication, WebAuth, IPsec, count, application services, and Junos Services Framework (JSF). 

Additionally, the data structures used to store policies, rule sets, and other components use different memory on the Packet Forwarding Engine and on the Routing Engine. For example, address names for each address in the policy are stored on the Routing Engine, but no memory is allocated at the Packet Forwarding Engine level. Similarly, port ranges are expanded to prefix and mask pairs and are stored on the Packet Forwarding Engine, but no such memory is allocated on the Routing Engine. 

Accordingly, depending on the policy configuration, the policy contributors to the Routing Engine are different from those to the Packet Forwarding Engine, and memory is allocated dynamically. 

Memory is also consumed by the “deferred delete” state. In the deferred delete state, when a device applies a policy change, there is transitory peak usage whereby both the old and new policies are present. So for a brief period, both old and new policies exist on the Packet Forwarding Engine, taking up twice the memory requirements. 

Therefore, there is no definitive way to infer clearly how much memory is used by either component (Packet Forwarding Engine or Routing Engine) at any given point in time, because memory requirements are dependent on specific configurations of policies, and memory is allocated dynamically. 

The following best practices for policy implementation enable you to better use system memory and to optimize policy configuration: 

Use single prefixes for source and destination addresses. For example, instead of using /32 addresses and adding each address separately, use a large subnet that covers most of the IP addresses you require. 

Use application “any” whenever possible. Each time you define an individual application in the policy, you can use an additional 52 bytes. 

Use fewer IPv6 addresses because IPv6 addresses consume more memory. 

Use fewer zone pairs in policy configurations. Each source or destination zone uses about 16,048 bytes of memory. 

The following parameters can change how memory is consumed by the bytes as specified: 

Firewall authentication–About 16 bytes or more (unfixed) 

Web authentication–About 16 bytes or more (unfixed) 

IPsec–12 bytes 

Application services–28 bytes 

Count–64 bytes 

Check memory utilization before and after compiling policies. 

Note: 
The memory requirement for each device is different. Some devices support 512,000 sessions by default, and the bootup memory is usually at 72 to 73 percent. Other devices can have up to 1 million sessions and the bootup memory can be up to 83 to 84 percent. In the worst-case scenario, to support about 80,000 policies in the SPU, the SPU should boot with a flowd kernel memory consumption of up to 82 percent, and with at least 170 megabytes of memory available. 

See Also 

Understanding Global Address Books 

Global Policy Overview 

Checking Memory Usage on SRX Series Devices 

Configuring Policies Using the Firewall Wizard 

The Firewall Policy Wizard enables you to perform basic security policy configuration. For more advanced configuration, use the J-Web interface or the CLI. 

To configure policies using the Firewall Policy Wizard: 

Select 
Configure>Tasks>Configure FW Policy in the J-Web interface. 

Click the Launch Firewall Policy Wizard button to launch the wizard. 

Follow the prompts in the wizard. 

The upper-left area of the wizard page shows where you are in the configuration process. The lower-left area of the page shows field-sensitive help. When you click a link under the Resources heading, the document opens in your browser. If the document opens in a new tab, be sure to close only the tab (not the browser window) when you close the document. 

Example: Configuring a Security Policy to Permit or Deny All Traffic 

This example shows how to configure a security policy to permit or deny all traffic. 

Requirements 

Overview 

Configuration 

Verification 

Requirements 

Before you begin: 

Create zones. See Example: Creating Security Zones . 

Configure an address book and create addresses for use in the policy. See Example: Configuring Address Books and Address Sets . 

Create an application (or application set) that indicates that the policy applies to traffic of that type. See Example: Configuring Security Policy Applications and Application Sets . 

Overview 

In the Junos OS, security policies enforce rules for transit traffic, in terms of what traffic can pass through the device, and the actions that need to take place on traffic as it passes through the device. From the perspective of security policies, the traffic enters one security zone and exits another security zone. In this example, you configure the trust and untrust interfaces, ge-0/0/2 and ge-0/0/1. See Figure 1 . 

Figure 1: Permitting All Traffic 

This configuration example shows how to: 

Permit or deny all traffic from the trust zone to the untrust zone but block everything from the untrust zone to the trust zone. 

Permit or deny selected traffic from a host in the trust zone to a server in the untrust zone at a particular time. 

Topology 

Configuration 

Procedure 

CLI Quick Configuration 

Step-by-Step Procedure 

Results 

CLI Quick Configuration 
To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the 
[edit] hierarchy level, and then enter 
commit from configuration mode. 

set security zones security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all set security zones security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all set security policies from-zone trust to-zone untrust policy permit-all match source-address any set security policies from-zone trust to-zone untrust policy permit-all match destination-address any set security policies from-zone trust to-zone untrust policy permit-all match application any set security policies from-zone trust to-zone untrust policy permit-all then permit set security policies from-zone untrust to-zone trust policy deny-all match source-address any set security policies from-zone untrust to-zone trust policy deny-all match destination-address any set security policies from-zone untrust to-zone trust policy deny-all match application any set security policies from-zone untrust to-zone trust policy deny-all then deny 

Step-by-Step Procedure 
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode in the CLI User guide. 

To configure a security policy to permit or deny all traffic: 

Configure the interfaces and security zones. 

[edit security zones] user@host# set security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all user@host# set security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all 

Create the security policy to permit traffic from the trust zone to the untrust zone. 

[edit security policies from-zone trust to-zone untrust] user@host# set policy permit-all match source-address any user@host# set policy permit-all match destination-address any user@host# set policy permit-all match application any user@host# set policy permit-all then permit 

Create the security policy to deny traffic from the untrust zone to the trust zone. 

[edit security policies from-zone untrust to-zone trust] user@host# set policy deny-all match source-address any user@host# set policy deny-all match destination-address any user@host# set policy deny-all match application any user@host# set policy deny-all then deny 

Results 
From configuration mode, confirm your configuration by entering the 
show security policies and 
show security zones commands. If the output does not display the intended configuration, repeat the configuration instructions in this example to correct it. 

Note: 
The configuration example is a default permit-all from the trust zone to the untrust zone. 

[edit] user@host# 
show security policies from-zone trust to-zone untrust { policy permit-all { match { source-address any; destination-address any; application any; } then { permit; } } } from-zone untrust to-zone trust { policy deny-all { match { source-address any; destination-address any; application any; } then { deny; } } } 

user@host# 
show security zones security-zone trust { interfaces { ge-0/0/2.0 { host-inbound-traffic { system-services { all; } } } } } security-zone untrust { interfaces { ge-0/0/1.0 { host-inbound-traffic { system-services { all; } } } } } 

If you are done configuring the device, enter 
commit from configuration mode. 

Verification 

Verifying Policy Configuration 

Purpose 

Action 

Meaning 

Purpose 
Verify information about security policies. 

Action 
From operational mode, enter the 
show security policies detail command to display a summary of all security policies configured on the device. 

Meaning 
The output displays information about policies configured on the system. Verify the following information: 

From and to zones 

Source and destination addresses 

Match criteria 

Example: Configuring a Security Policy to Permit or Deny Selected Traffic 

This example shows how to configure a security policy to permit or deny selected traffic. 

Requirements 

Overview 

Configuration 

Verification 

Requirements 

Before you begin: 

Create zones. See Example: Creating Security Zones . 

Configure an address book and create addresses for use in the policy. See Example: Configuring Address Books and Address Sets . 

Create an application (or application set) that indicates that the policy applies to traffic of that type. See Example: Configuring Security Policy Applications and Application Sets . 

Permit traffic to and from trust and untrust zones. See Example: Configuring a Security Policy to Permit or Deny All Traffic . 

Overview 

In Junos OS, security policies enforce rules for the transit traffic, in terms of what traffic can pass through the device, and the actions that need to take place on the traffic as it passes through the device. From the perspective of security policies, the traffic enters one security zone and exits another security zone. In this example, you configure a specific security policy to allow only e-mail traffic from a host in the trust zone to a server in the untrust zone. No other traffic is allowed. See Figure 2 . 

Figure 2: Permitting Selected Traffic 

Configuration 

Procedure 

CLI Quick Configuration 

Step-by-Step Procedure 

Results 

CLI Quick Configuration 
To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the 
[edit] hierarchy level, and then enter 
commit from configuration mode. 

set security zones security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all set security zones security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all set security address-book book1 address mail-untrust 203.0.113.14/24 set security address-book book1 attach zone untrust set security address-book book2 address mail-trust 192.168.1.1/32 set security address-book book2 attach zone trust set security policies from-zone trust to-zone untrust policy permit-mail match source-address mail-trust set security policies from-zone trust to-zone untrust policy permit-mail match destination-address mail-untrust set security policies from-zone trust to-zone untrust policy permit-mail match application junos-mail set security policies from-zone trust to-zone untrust policy permit-mail then permit 

Step-by-Step Procedure 
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode in the CLI User guide. 

To configure a security policy to allow selected traffic: 

Configure the interfaces and security zones. 

[edit security zones] user@host# set security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all user@host# set security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all 

Create address book entries for both the client and the server. Also, attach security zones to the address books. 

[edit security address-book book1] user@host# set address mail-untrust 203.0.113.14/24 user@host# set attach zone untrust 

[edit security address-book book2] user@host# set address mail-trust 192.168.1.1/32 user@host# set attach zone trust 

Define the policy to permit mail traffic. 

[edit security policies from-zone trust to-zone untrust] user@host# set policy permit-mail match source-address mail-trust user@host# set policy permit-mail match destination-address mail-untrust user@host# set policy permit-mail match application junos-mail user@host# set policy permit-mail then permit 

Results 
From configuration mode, confirm your configuration by entering the 
show security policies and 
show security zones commands. If the output does not display the intended configuration, repeat the configuration instructions in this example to correct it. 

[edit] user@host# 
show security policies from-zone trust to-zone untrust { policy permit-mail { match { source-address mail-trust; destination-address mail-untrust; application junos-mail; } then { permit; } } } 

user@host# 
show security zones security-zone trust { host-inbound-traffic { system-services { all; } interfaces { ge-0/0/2 { host-inbound-traffic { system-services { all; } } } } } security-zone untrust { interfaces { ge-0/0/1 { host-inbound-traffic { system-services { all; } } } } } 

user@host# 
show security address-book book1 { address mail-untrust 203.0.113.14/24; attach { zone untrust; } } book2 { address mail-trust 192.168.1.1/32; attach { zone trust; } } 

If you are done configuring the device, enter 
commit from configuration mode. 

Verification 

Verifying Policy Configuration 

Purpose 

Action 

Meaning 

Purpose 
Verify information about security policies. 

Action 
From operational mode, enter the 
show security policies detail command to display a summary of all security policies configured on the device. 

Meaning 
The output displays information about policies configured on the system. Verify the following information: 

From and to zones 

Source and destination addresses 

Match criteria 

Example: Configuring a Security Policy to Permit or Deny Wildcard Address Traffic 

This example shows how to configure a security policy to permit or deny wildcard address traffic. 

Requirements 

Overview 

Configuration 

Verification 

Requirements 

Before you begin: 

Understand wildcard addresses. See Understanding Security Policy Rules . 

Create zones. See Example: Creating Security Zones . 

Configure an address book and create addresses for use in the policy. See Example: Configuring Address Books and Address Sets . 

Create an application (or application set) that indicates that the policy applies to traffic of that type. See Example: Configuring Security Policy Applications and Application Sets . 

Permit traffic to and from trust and untrust zones. See Example: Configuring a Security Policy to Permit or Deny All Traffic . 

Permit e-mail traffic to and from trust and untrust zones. See Example: Configuring a Security Policy to Permit or Deny Selected Traffic 

Overview 

In the Junos operating system (Junos OS), security policies enforce rules for the transit traffic, in terms of what traffic can pass through the device, and the actions that need to take place on the traffic as it passes through the device. From the perspective of security policies, the traffic enters one security zone and exits another security zone. In this example, you configure a specific security to allow only wildcard address traffic from a host in the trust zone to the untrust zone. No other traffic is allowed. 

Configuration 

Procedure 

CLI Quick Configuration 

Step-by-Step Procedure 

Results 

CLI Quick Configuration 
To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the 
[edit] hierarchy level, and then enter 
commit in configuration mode. 

set security zones security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all set security zones security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all set security address-book book1 address wildcard-trust wildcard-address 192.168.0.11/255.255.0.255 set security address-book book1 attach zone trust set security policies from-zone trust to-zone untrust policy permit-wildcard match source-address wildcard-trust set security policies from-zone trust to-zone untrust policy permit-wildcard match destination-address any set security policies from-zone trust to-zone untrust policy permit-wildcard match application any set security policies from-zone trust to-zone untrust policy permit-wildcard then permit 

Step-by-Step Procedure 
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode in the CLI User guide. 

To configure a security policy to allow selected traffic: 

Configure the interfaces and security zones. 

[edit security zones] user@host# set security-zone trust interfaces ge-0/0/2 host-inbound-traffic system-services all user@host# set security-zone untrust interfaces ge-0/0/1 host-inbound-traffic system-services all 

Create an address book entry for the host and attach the address book to a zone. 

[edit security address-book book1] user@host# set address wildcard-trust wildcard-address 192.168.0.11/255.255.0.255 user@host# set attach zone trust 

Define the policy to permit wildcard address traffic. 

[edit security policies from-zone trust to-zone untrust] user@host# set policy permit-wildcard match source-address wildcard-trust user@host# set policy permit-wildcard match destination-address any user@host# set policy permit-wildcard match application any user@host# set policy permit-wildcard then permit 

Results 
From configuration mode, confirm your configuration by entering the 
show security policies and 
show security zones commands. If the output does not display the intended configuration, repeat the configuration instructions in this example to correct it. 

[edit] user@host# 
show security policies from-zone trust to-zone untrust { policy permit-wildcard { match { source-address wildcard-trust; destination-address any; application any; } then { permit; } } } 

user@host# 
show security zones security-zone trust { host-inbound-traffic { system-services { all; } interfaces { ge-0/0/2 { host-inbound-traffic { system-services { all; } } } } } } security-zone untrust { interfaces { ge-0/0/1 { host-inbound-traffic { system-services { all; } } } } } user@host# 
show security address-book book1 { address wildcard-trust { wildcard-address 192.168.0.11/255.255.0.255; } attach { zone trust; } } 

If you are done configuring the device, enter 
commit from configuration mode. 

Verification 

Verifying Policy Configuration 

Purpose 

Action 

Meaning 

Purpose 
Verify information about security policies. 

Action 
From operational mode, enter the 
show security policies policy-name permit-wildcard detail command to display details about the permit-wildcard security policy configured on the device. 

Meaning 
The output displays information about the permit-wildcard policy configured on the system. Verify the following information: 

From and To zones 

Source and destination addresses 

Match criteria 

Example: Configuring a Security Policy to Redirect Traffic Logs to an External System Log Server 

This example shows how to configure a security policy to send traffic logs generated on the device to an external system log server. 

Requirements 

Overview 

Configuration 

Verification 

Requirements 

This example uses the following hardware and software components: 

A client connected to an SRX5600 device at the interface ge-4/0/5 

A server connected to the SRX5600 device at the interface ge-4/0/1 

The logs generated on the SRX5600 device are stored in a Linux-based system log server. 

An SRX5600 device connected to the Linux-based server at interface ge-4/0/4 

No special configuration beyond device initialization is required before configuring this feature. 

Overview 

In this example, you configure a security policy on the SRX5600 device to send traffic logs, generated by the device during data transmission, to a Linux-based server. Traffic logs record details of every session. The logs are generated during session establishment and termination between the source and the destination device that are connected to the SRX5600 device. 

Configuration 

Procedure 

CLI Quick Configuration 

Step-by-Step Procedure 

Results 

CLI Quick Configuration 
To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the 
[edit] hierarchy level, and then enter 
commit in configuration mode. 

set security log source-address 127.0.0.1 set security log stream trafficlogs severity debug set security log stream trafficlogs host 203.0.113.2 set security zones security-zone client host-inbound-traffic system-services all set security zones security-zone client host-inbound-traffic protocols all set security zones security-zone client interfaces ge-4/0/5.0 set security zones security-zone server host-inbound-traffic system-services all set security zones security-zone server interfaces ge-4/0/4.0 set security zones security-zone server interfaces ge-4/0/1.0 set security policies from-zone client to-zone server policy policy-1 match source-address any set security policies from-zone client to-zone server policy policy-1 match destination-address any set security policies from-zone client to-zone server policy policy-1 match application any set security policies from-zone client to-zone server policy policy-1 then permit set security policies from-zone client to-zone server policy policy-1 then log session-init set security policies from-zone client to-zone server policy policy-1 then log session-close 

Step-by-Step Procedure 
The following example requires you to navigate various levels in the configuration hierarchy. For instructions on how to do that, see Using the CLI Editor in Configuration Mode in the CLI User guide. 

To configure a security policy to send traffic logs to an external system log server: 

Configure security logs to transfer traffic logs generated at the SRX5600 device to an external system log server with the IP address 203.0.113.2. The IP address 127.0.0.1 is the loopback address of the SRX5600 device. 

[edit security log] user@host# set source-address 127.0.0.1 user@host# set stream trafficlogs severity debug user@host# set stream trafficlogs host 203.0.113.2 

Configure a security zone and specify the types of traffic and protocols that are allowed on interface ge-4/0/5.0 of the SRX5600 device. 

[edit security zones] user@host# set security-zone client host-inbound-traffic system-services all user@host# set security-zone client host-inbound-traffic protocols all user@host# set security-zone client interfaces ge-4/0/5.0 

Configure another security zone and specify the types of traffic that are allowed on the interfaces ge-4/0/4.0 and ge-4/0/1.0 of the SRX5600 device. 

[edit security zones] user@host# set security-zone server host-inbound-traffic system-services all user@host# set security-zone server interfaces ge-4/0/4.0 user@host# set security-zone server interfaces ge-4/0/1.0 

Create a policy and specify the match criteria for that policy. The match criteria specifies that the device can allow traffic from any source, to any destination, and on any application. 

[edit security policies from-zone client to-zone server] user@host# set policy policy-1 match source-address any user@host# set policy policy-1 match destination-address any user@host# set policy policy-1 match application any user@host# set policy policy-1 then permit 

Enable the policy to log traffic details at the beginning and at the end of the session. 

[edit security policies from-zone client to-zone server] user@host# set policy policy-1 then log session-init user@host# set policy policy-1 then log session-close 

Results 
From configuration mode, confirm your configuration by entering the 
show security log command. If the output does not display the intended configuration, repeat the configuration instructions in this example to correct it. 

[edit] user@host# show security log format syslog; source-address 127.0.0.1; stream trafficlogs { severity debug; host { 203.0.113.2; } } 

If you are done configuring the device, enter 
commit from the configuration mode. 

Verification 

Confirm that the configuration is working properly. 

Verifying Zones 

Verifying Policies 

Verifying Zones 

Purpose 

Action 

Purpose 
Verify that the security zone is enabled or not. 

Action 
From operational mode, enter the 
show security zones command. 

Verifying Policies 

Purpose 

Action 

Purpose 
Verify that the policy is working. 

Action 
From operational mode, enter the 
show security policies command on all the devices. 

TAP Mode for Security Zones and Policies 

The Terminal Access Point (TAP) mode for security zones and policy allows you to passively monitor traffic flows across a network by way of a switch SPAN or mirror port. 

Understanding TAP Mode Support for Security Zones and Policies 

Example: Configuring Security Zones and Policies in TAP mode 

Understanding TAP Mode Support for Security Zones and Policies 

The Terminal Access Point (TAP) mode is a standby device, which checks the mirrored traffic through switch. If security zones and policies are configured, then the TAP mode inspects the incoming and outgoing traffic by configuring the TAP interface and generating a security log report to display the number of threats detected and the user usage. If some packet gets lost in the tap interface, the security zones and policies terminates the connection, as a result no report generates for this connection. The security zone and policy configuration remains the same as non-TAP mode. 

When you configure a device to operate in TAP mode, the device generates security log information to display the information on threats detected, application usage, and user details. When the device is configured to operate in TAP mode, the device receives packets only from the configured TAP interface. Except the configured TAP interface, other interface are configured to normal interface that is used as management interface or connected to the outside server. The device generates security report or log according to the incoming traffic. 

The security zone and default security policy will be configured after TAP interface is configured. You can configure other zones or policies if required. If one interface is used to connect a server then the IP address, routing-interface, and security configuration also need be configured. 

Note: 
You can configure only one TAP interface when you operate the device in TAP mode. 

Example: Configuring Security Zones and Policies in TAP mode 

This example shows how to configure security zones, and policies when the SRX Firewall is configured in TAP (Terminal Access Point) mode. 

Requirements 

Overview 

Configuration 

Verification 

Requirements 

This example uses the following hardware and software components: 

An SRX Firewall 

Junos OS Release 19.1R1 

Overview 

In this example, you configure the SRX Firewall to operate in TAP mode. When you configure the SRX Firewall to operate in TAP mode, the device generates security log information to display the information on threats detected, application usage, and user details. 

Configuration 

CLI Quick Configuration 

Procedure 

Results 

CLI Quick Configuration 
To quickly configure this example, copy the following commands, paste them into a text file, remove any line breaks, change any details necessary to match your network configuration, copy and paste the commands into the CLI at the 
[edit] hierarchy level, and then enter commit from configuration mode. 

set security zones security-zone tap-zone interfaces ge-0/0/0.0 set security zones security-zone tap-zone application-tracking set security policies from-zone tap-zone to-zone tap-zone policy tap-policy match source-address any set security policies from-zone tap-zone to-zone tap-zone policy tap-policy match destination-address any set security policies from-zone tap-zone to-

[TRUNCATED]

