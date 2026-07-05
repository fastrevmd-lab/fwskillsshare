# MNHA Configuration Patterns (srx-mnha reference)

Moved out of SKILL.md for token-efficient progressive disclosure; content unchanged and previously reviewed.

## Commit Peer Synchronization Pattern

```junos
set groups MNHA-SYNC when peers [ <NODE_A> <NODE_B> ]
set groups MNHA-SYNC security policies ...
set groups MNHA-SYNC security nat ...
set apply-groups MNHA-SYNC
set system commit peers-synchronize
set system commit peers <PEER_HOSTNAME> user <USERNAME>
set system commit peers <PEER_HOSTNAME> authentication "<SECRET>"
set system static-host-mapping <PEER_HOSTNAME> inet <PEER_MANAGEMENT_OR_ICL_IP>
set security ssh-known-hosts fetch-from-server <PEER_HOSTNAME>
```

## BGP Export Policy from Signal Routes (Full Example)

```junos
set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet 169.254.200.1/32
set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet table inet.0
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet 169.254.200.2/32
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet table inet.0

set policy-options policy-statement MNHA-SRG1-EXPORT term active from protocol direct
set policy-options policy-statement MNHA-SRG1-EXPORT term active from route-filter <PROTECTED_PREFIX> exact
set policy-options policy-statement MNHA-SRG1-EXPORT term active from condition ACTIVE_SRG1
set policy-options policy-statement MNHA-SRG1-EXPORT term active then metric 10
set policy-options policy-statement MNHA-SRG1-EXPORT term active then accept

set policy-options policy-statement MNHA-SRG1-EXPORT term backup from protocol direct
set policy-options policy-statement MNHA-SRG1-EXPORT term backup from route-filter <PROTECTED_PREFIX> exact
set policy-options policy-statement MNHA-SRG1-EXPORT term backup from condition BACKUP_SRG1
set policy-options policy-statement MNHA-SRG1-EXPORT term backup then metric 20
set policy-options policy-statement MNHA-SRG1-EXPORT term backup then accept

set policy-options policy-statement MNHA-SRG1-EXPORT term default then reject
set protocols bgp group <GROUP> export MNHA-SRG1-EXPORT
```

## OSPF Variant of Signal-Route Steering (Full Example)

```junos
set protocols ospf area 0 interface lo0.0 passive   # lo0.0 carries <PROTECTED_PREFIX> — the /32 the route-filter terms below match
set protocols ospf area 0 interface <UPLINK_IFL> metric <NODE_METRIC>   # higher on the backup node

set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet 169.254.200.1/32
set policy-options condition ACTIVE_SRG1 if-route-exists address-family inet table inet.0
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet 169.254.200.2/32
set policy-options condition BACKUP_SRG1 if-route-exists address-family inet table inet.0

set policy-options policy-statement MNHA-SRG1-OSPF term active from route-filter <PROTECTED_PREFIX> exact
set policy-options policy-statement MNHA-SRG1-OSPF term active from condition ACTIVE_SRG1
set policy-options policy-statement MNHA-SRG1-OSPF term active then metric <LOW_METRIC>
set policy-options policy-statement MNHA-SRG1-OSPF term active then accept
set policy-options policy-statement MNHA-SRG1-OSPF term backup from route-filter <PROTECTED_PREFIX> exact
set policy-options policy-statement MNHA-SRG1-OSPF term backup from condition BACKUP_SRG1
set policy-options policy-statement MNHA-SRG1-OSPF term backup then metric <HIGH_METRIC>
set policy-options policy-statement MNHA-SRG1-OSPF term backup then accept
set policy-options policy-statement MNHA-SRG1-OSPF term default then reject
set protocols ospf export MNHA-SRG1-OSPF
```

## Local DHCP Pattern, Node A

```junos
set routing-instances <RI> interface <CLIENT_INTERFACE>
set security zones security-zone <ZONE> host-inbound-traffic system-services dhcp
set routing-instances <RI> system services dhcp-local-server group <GROUP> interface <CLIENT_INTERFACE>
set routing-instances <RI> access address-assignment pool <POOL> family inet network <SUBNET>
set routing-instances <RI> access address-assignment pool <POOL> family inet range NODE-A low <NODE_A_POOL_LOW>
set routing-instances <RI> access address-assignment pool <POOL> family inet range NODE-A high <NODE_A_POOL_HIGH>
set routing-instances <RI> access address-assignment pool <POOL> family inet dhcp-attributes router <VIP_GATEWAY>
set routing-instances <RI> access address-assignment pool <POOL> family inet dhcp-attributes server-identifier <NODE_A_INTERFACE_IP>
```

Node B uses the same pool name/network if desired, but a different non-overlapping range and its own physical interface IP as `server-identifier`.
