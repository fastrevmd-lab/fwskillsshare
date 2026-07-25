# SRX Cross-Zone Service Discovery

Use this reference for mDNS, SSDP, casting, AirPlay, Sonos, Plex, and similar discovery failures across VLANs or zones.

## Discovery mechanics

- **Link-local discovery is not routable.** mDNS (`224.0.0.251:5353`) and SSDP (`239.255.255.250:1900`) use IP TTL 1. A flow-mode SRX will not forward them across an L3 boundary regardless of policy.
- **Routable multicast requires multicast routing.** Real multicast forwarding needs IGMP, PIM or forwarding-options configuration plus security policy. A permit rule alone is insufficient.
- **Cross-VLAN discovery normally needs an off-box reflector.** Use Avahi or a controller-based reflector with reach into every routed subnet. If the SRX owns inter-VLAN routing, a reflector limited to one controller L2 domain cannot cross it.

## Firewall role

1. Let the reflector handle discovery.
2. Permit the post-discovery unicast control and stream traffic between source and device subnets, scoped to a media application set rather than `application any`.
3. Verify policy hits and inspect default-deny logs for missing media ports:

```text
show security policies hit-count
show security match-policies from-zone <SRC> to-zone <DST> source-ip <client> destination-ip <device> protocol tcp destination-port <port>
show log messages | match "RT_FLOW_SESSION_DENY|DEFAULT-DENY"
```

Do not promise cross-VLAN casting from a permit rule alone. Policy enables the unicast stream after discovery; without a reflector or multicast routing, the endpoints never discover each other. Use `parsing-srx-configs` to identify existing multicast-routing configuration.
