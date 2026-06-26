# Minimal SRX fixture input

```junos
set security zones security-zone trust interfaces ge-0/0/0.0
set security zones security-zone untrust interfaces ge-0/0/1.0
set security address-book global address WEB 10.0.1.10/32
set applications application APP-HTTPS protocol tcp
set applications application APP-HTTPS destination-port 443
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match source-address any
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match destination-address WEB
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match application APP-HTTPS
set security policies from-zone trust to-zone untrust policy ALLOW-WEB then permit
set security policies from-zone trust to-zone untrust policy ALLOW-WEB then log session-close
set security nat source rule-set TRUST-OUT from zone trust
set security nat source rule-set TRUST-OUT to zone untrust
set security nat source rule-set TRUST-OUT rule PAT match source-address 10.0.0.0/16
set security nat source rule-set TRUST-OUT rule PAT then source-nat interface
set routing-options static route 0.0.0.0/0 next-hop 203.0.113.1
```
