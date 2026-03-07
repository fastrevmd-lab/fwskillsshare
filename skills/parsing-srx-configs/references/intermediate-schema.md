# Intermediate Schema Reference

This is the vendor-neutral intermediate JSON schema that all firewall config parsers produce.
All extracted data should be normalized to this format regardless of source vendor.

## Top-Level Structure

```json
{
  "zones": [],
  "address_objects": [],
  "address_groups": [],
  "service_objects": [],
  "service_groups": [],
  "security_policies": [],
  "nat_rules": [],
  "applications": [],
  "application_groups": [],
  "schedules": [],
  "security_profile_objects": [],
  "interfaces": [],
  "static_routes": [],
  "bgp_config": [],
  "ospf_config": [],
  "ha_config": {},
  "screen_config": [],
  "vpn_tunnels": [],
  "syslog_config": [],
  "dhcp_config": [],
  "routing_contexts": [],
  "metadata": {}
}
```

## Zone

```json
{
  "name": "trust",
  "description": "Internal network zone",
  "interfaces": ["ge-0/0/0.0", "ge-0/0/1.0"],
  "zone_type": "layer3"
}
```

## Address Object

```json
{
  "name": "web-server",
  "type": "host",
  "value": "10.0.1.10/32",
  "description": "Production web server",
  "tags": ["production"],
  "ip_version": "v4"
}
```

Valid `type` values: `"host"`, `"subnet"`, `"range"`, `"fqdn"`, `"wildcard"`, `"geo"`

- **host**: Single IP — value is `"x.x.x.x/32"` or `"::1/128"`
- **subnet**: Network — value is `"10.0.0.0/24"`
- **range**: IP range — value is `"10.0.1.1-10.0.1.254"`
- **fqdn**: Domain name — value is `"example.com"`
- **wildcard**: Wildcard mask — value is `"10.0.0.0/0.0.255.255"`
- **geo**: Geographic — value is country code `"US"`

## Address Group

```json
{
  "name": "web-servers",
  "members": ["web-server-1", "web-server-2"],
  "description": "All web servers",
  "tags": []
}
```

## Service Object

```json
{
  "name": "custom-https",
  "protocol": "tcp",
  "port_range": "8443",
  "source_port": "",
  "description": "Custom HTTPS port"
}
```

Port range formats: `"80"`, `"80-443"`, `"1024-65535"`
Protocol values: `"tcp"`, `"udp"`, `"icmp"`, `"sctp"`, `"ip"`

## Service Group

```json
{
  "name": "web-services",
  "members": ["HTTP", "HTTPS", "custom-https"],
  "description": ""
}
```

## Security Policy

```json
{
  "name": "allow-web-traffic",
  "src_zones": ["trust"],
  "dst_zones": ["untrust"],
  "src_addresses": ["internal-nets"],
  "dst_addresses": ["any"],
  "negate_source": false,
  "negate_destination": false,
  "applications": ["junos-http", "junos-https"],
  "services": ["application-default"],
  "action": "allow",
  "log_start": false,
  "log_end": true,
  "profile_group": "",
  "security_profiles": {
    "virus": "default",
    "url-filtering": "strict-filtering"
  },
  "description": "Allow outbound web access",
  "tags": ["outbound"],
  "disabled": false,
  "schedule": "",
  "source_users": [],
  "_rule_index": 1,
  "_implicit": false
}
```

### Action Values
- `"allow"` — permit traffic
- `"deny"` — silently drop traffic
- `"drop"` — silently drop (alias for deny on some platforms)
- `"reset-both"` — send TCP RST to both sides (reject)

### Security Profile Keys
- `"virus"` — antivirus profile
- `"url-filtering"` — URL/web filtering
- `"idp"` — IPS/IDP profile
- `"anti-spyware"` — anti-spyware (PAN-OS specific)
- `"file-blocking"` — file blocking profile
- `"wildfire"` — WildFire analysis
- `"dlp"` — data loss prevention
- `"ssl-proxy"` — SSL decryption/proxy profile

### Internal Fields (prefixed with `_`)
- `_rule_index` — sequential position in the rulebase (1-based)
- `_implicit` — true for vendor-implicit rules (appended by parser)
- `_logical_system` — SRX logical-system context name
- `_tenant` — SRX tenant context name
- `_vsys` — PAN-OS vsys name
- `_vdom` — FortiGate VDOM name
- `added_by_fpic` — marker that this rule was auto-generated

## NAT Rule

```json
{
  "name": "source-nat-outbound",
  "type": "source",
  "src_zones": ["trust"],
  "dst_zones": ["untrust"],
  "src_addresses": ["internal-nets"],
  "dst_addresses": ["any"],
  "translated_src": {
    "type": "interface",
    "addresses": []
  },
  "translated_dst": null,
  "translated_port": null,
  "description": "PAT to outside interface",
  "_rule_index": 1
}
```

### NAT Type Values
- `"source"` — source NAT only
- `"destination"` — destination NAT only
- `"static"` — bidirectional static NAT
- `"source-and-destination"` — both source and destination translated

### translated_src Object
```json
{
  "type": "interface",
  "addresses": []
}
```
Type values: `"interface"`, `"dynamic-ip-pool"`, `"static"`, `"no-nat"`

## Schedule

```json
{
  "name": "business-hours",
  "type": "recurring",
  "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
  "start": "08:00",
  "end": "18:00"
}
```

## Interface

```json
{
  "name": "ge-0/0/0.0",
  "ip": "10.0.1.1/24",
  "zone": "trust",
  "vlan": null,
  "type": "physical",
  "description": "LAN interface",
  "status": "up",
  "speed": "1g"
}
```

## Static Route

```json
{
  "name": "default-route",
  "destination": "0.0.0.0/0",
  "next_hop": "203.0.113.1",
  "next_hop_type": "ip",
  "interface": "",
  "metric": 10,
  "vrf": ""
}
```

## HA Config

```json
{
  "enabled": true,
  "mode": "active-passive",
  "group_id": 1,
  "priority": 200,
  "preempt": true,
  "peer_ip": "10.0.0.2",
  "ha_interfaces": [
    {"name": "fab0", "role": "fabric", "ip": "10.255.0.1/24"}
  ],
  "monitoring": {
    "interfaces": ["ge-0/0/0", "ge-0/0/1"],
    "failure_threshold": 255
  }
}
```

## Screen/IDS Config

```json
{
  "name": "outside-screen",
  "zone": "untrust",
  "icmp": {"ping-death": true, "flood": {"threshold": 1000}},
  "tcp": {"syn-flood": {"alarm-threshold": 1024, "attack-threshold": 2048}, "land": true},
  "udp": {"flood": {"threshold": 1000}},
  "ip": {"spoofing": true, "source-route-option": true},
  "limit_session": {"source-ip-based": 128, "destination-ip-based": 128}
}
```

## Metadata

```json
{
  "source_vendor": "srx",
  "source_version": "",
  "export_date": "",
  "rule_count": 42,
  "nat_rule_count": 5,
  "object_count": 120,
  "zone_count": 4,
  "interface_count": 8,
  "ha_enabled": true
}
```

Valid `source_vendor` values: `"srx"`, `"panos"`, `"fortigate"`, `"cisco_asa"`, `"checkpoint"`, `"sonicwall"`, `"huawei_usg"`
