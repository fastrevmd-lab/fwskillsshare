# Security Policy Applications and Application Sets | Junos OS

Source URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/policy-application-sets-configuration.html
Final URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/policy-application-sets-configuration.html
HTTP status: 200
Extractor: htmlparser
Extracted characters: 9518

## Extracted text

Security Policy Applications and Application Sets | Junos OS | Juniper Networks

X

Help us improve your experience.

Let us know what you think.

Do you have time for a two-minute survey?

Yes

Maybe Later

ON THIS PAGE

Security Policy Applications Overview

Security Policy Application Sets Overview

Example: Configuring Security Policy Applications and Application Sets

Understanding Policy Application Timeout Configuration and Lookup

Understanding Policy Application Timeouts Contingencies

Example: Setting a Policy Application Timeout

Security Policy Applications and Application Sets

Policy applications are types of traffic for which protocol standards exist. The policy application set is a group of policy applications. Junos OS simplifies the process by allowing you to manage a small number of policy application sets, rather than a large number of individual policy application entries.

The policy application or application set is referred by security policies as match criteria for packets initiating sessions. Junos OS allows you to configure policy applications and application sets. You can create an application set that contains all the approved applications.

Security Policy Applications Overview

Applications are types of traffic for which protocol standards exist. Each application has a transport protocol and destination port number(s) associated with it, such as TCP/port 21 for FTP and TCP/port 23 for Telnet. When you create a policy, you must specify an application for it.

You can select one of the predefined applications from the application book, or a custom application or application set that you created. You can see which application you can use in a policy by using the
show applications CLI command.

Note:
Each predefined application has a source port range of
1–65535 , which includes the entire set of valid port numbers. This prevents potential attackers from gaining access by using a source port outside of the range. If you need to use a different source port range for any predefined application, create a custom application. For information, see Understanding Custom Policy Applications .

See Also

Understanding Security Policy Elements

Security Policy Application Sets Overview

When you create a policy, you must specify an application, or service, for it to indicate that the policy applies to traffic of that type. Sometimes the same applications or a subset of them can be present in multiple policies, making it difficult to manage. Junos OS allows you to create groups of applications called application sets. Application sets simplify the process by allowing you to manage a small number of application sets, rather than a large number of individual application entries.

The application (or application set) is referred to by security policies as match criteria for packets initiating sessions. If the packet matches the application type specified by the policy and all other criteria match, then the policy action is applied to the packet.

You can specify the name of an application set in a policy. In this case, if all of the other criteria match, any one of the applications in the application set serves as valid matching criteria;
any is the default application name that indicates all possible applications.

Applications are created in the
.../applications/application/ application-name directory. You do not need to configure an application for any of the services that are predefined by the system.

In addition to predefined services, you can configure a custom service. After you create a custom service, you can refer to it in a policy.

Example: Configuring Security Policy Applications and Application Sets

This example shows how to configure applications and application sets.

Requirements

Overview

Configuration

Verification

Requirements

Before you begin, configure the required applications. See Security Policy Application Sets Overview .

Overview

Rather than creating or adding multiple individual application names to a policy, you can create an application set and refer to the name of the set in a policy. For example, for a group of employees, you can create an application set that contains all the approved applications.

In this example, you create an application set that are used to log in to the servers in the ABC (intranet) zone, to access the database, and to transfer files.

Define the applications in the configured application set.

Managers in zone A and managers in zone B use these services. Therefore, give the application set a generic name, such as MgrAppSet.

Create an application set for the applications that are used for e-mail and Web-based applications that are delivered by the two servers in the external zone.

Topology

Configuration

Procedure

Step-by-Step Procedure
To configure an application and application set:

Create an application set for managers.

[edit applications] user@host# set application-set MgrAppSet application junos-ssh user@host# set application-set MgrAppSet application junos-telnet

Create another application set for e-mail and Web-based applications.

[edit applications] user@host# set application-set WebMailApps application junos-smtp user@host# set application-set WebMailApps application junos-pop3

If you are done configuring the device, commit the configuration.

[edit] user@host# commit

Verification

To verify the configuration is working properly, enter the
show applications command in configuration mode.

Understanding Policy Application Timeout Configuration and Lookup

The application timeout value you set for an application determines the session timeout. You can set the timeout threshold for a predefined or custom application; you can use the application default timeout, specify a custom timeout, or use no timeout at all.

Application timeout values are stored in the root TCP and UDP port-based timeout table and in the protocol-based default timeout table. When you set an application timeout value, Junos OS updates these tables with the new value. There are also default timeout values in the applications entry database, which are taken from predefined applications. You can set a timeout, but you cannot alter a default value.

Each custom application can be configured with its own custom application timeout. If multiple custom applications are configured with custom timeouts, then each application will have its own custom application timeout.

If the application that is matched for the traffic has a timeout value, that timeout value is used. Otherwise, the lookup proceeds in the following order until an application timeout value is found:

The root TCP and UDP port-based timeout table is searched for a timeout value.

The protocol-based default timeout table is searched for a timeout value. See Table 1 .

Table 1: Protocol-Based Default Timeout

Protocol

Default Timeout (seconds)

TCP

1800

UDP

60

ICMP

60

OSPF

60

Other

1800

Understanding Policy Application Timeouts Contingencies

When setting timeouts, be aware of the following contingencies:

If an application contains several application rule entries, all rule entries share the same timeout. You need to define the application timeout only once. For example, if you create an application with two rules, the following commands will set the timeout to 20 seconds for both rules:

user@host# set applications application test term test protocol tcp destination-port 1035-1035 inactivity-timeout 20 user@host# set applications application test term test protocol udp user@host# set applications application test term test source-port 1-65535 user@host# set applications application test term test destination-port 1111-1111

If multiple custom applications are configured with custom timeouts, then each application will have its own custom application timeout. For example:

user@host# set applications application ftp-1 protocol tcp source-port 0-65535 destination-port 2121-2121 inactivity-timeout 10 user@host# set applications application telnet-1 protocol tcp source-port 0-65535 destination-port 2300-2348 inactivity-timeout 20

With this configuration, Junos OS applies a 10-second timeout for destination port 2121 and a 20-second timeout for destination port 2300 in an application group.

Example: Setting a Policy Application Timeout

This example shows how to set a policy application timeout value.

Requirements

Overview

Configuration

Verification

Requirements

Before you begin, understand policy application timeouts. See Understanding Policy Application Timeout Configuration and Lookup .

Overview

Application timeout values are stored in the application entry database and in the corresponding vsys TCP and UDP port-based timeout tables. In this example, you set the device for a policy application timeout to 75 minutes (4500 seconds) for the FTP predefined application.

When you set an application timeout value, Junos OS updates these tables with the new value.

Configuration

Procedure

Step-by-Step Procedure
To set a policy application timeout:

Set the inactivity timeout value.

[edit applications application ftp] user@host# set inactivity-timeout 4500

Commit the configuration if you are done configuring the device.

[edit] user@host# commit

Verification

To verify the configuration is working properly, enter the
show applications command.

Related Documentation

Custom Policy Applications
