# Policy-heavy synthetic SRX fixture for issue #15

- **Authored:** 2026-07-22
- **Provenance:** fully synthetic; no device or customer configuration was used
- **Intended profile:** vSRX Virtual Firewall, Junos 25.4R1-compatible display-set syntax
- **Purpose:** offline, read-only parsing and `firewall-best-practices-audit` validation
- **Completeness:** complete for the declared zones, objects, policies, source NAT,
  system hardening, screen, logging, and RE-filter surface; intentionally omits
  VPN, HA, IPv6, dynamic telemetry, and hit/last-used counters

## Safety

Prerequisites: none for reading or parsing this file. Reading, parsing, and
analyzing the fenced text has no side effects. **Do not load these commands on a
device:** applying them would change configuration, is outside issue #15, and
has no approved target or rollback plan. Rollback is therefore not applicable
to this offline fixture.

All addresses use [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) or private
documentation space. Names, descriptions, policy defects, and findings are
deliberately invented to exercise the audit catalog.

## Fixture input

```junos
set version 25.4R1
set system host-name SYNTHETIC-POLICY-HEAVY
set system services ssh root-login deny
set system services ssh connection-limit 5
set system services ssh rate-limit 4
set system login password minimum-length 12
set system login password change-type character-sets
set system login retry-options tries-before-disconnect 3
set system login retry-options lockout-period 5
set system syslog host 192.0.2.200 any notice

set interfaces ge-0/0/0 unit 0 family inet address 198.51.100.2/30
set interfaces ge-0/0/1 unit 0 family inet address 10.10.0.1/16
set interfaces ge-0/0/2 unit 0 family inet address 10.20.0.1/16
set interfaces lo0 unit 0 family inet address 192.0.2.1/32
set interfaces lo0 unit 0 family inet filter input PROTECT-RE

set firewall family inet filter PROTECT-RE term ALLOW-SSH from protocol tcp
set firewall family inet filter PROTECT-RE term ALLOW-SSH from destination-port ssh
set firewall family inet filter PROTECT-RE term ALLOW-SSH then accept
set firewall family inet filter PROTECT-RE term DENY-REST then discard

set security screen ids-option EDGE-SCREEN tcp syn-flood alarm-threshold 1000
set security zones security-zone untrust interfaces ge-0/0/0.0
set security zones security-zone untrust screen EDGE-SCREEN
set security zones security-zone untrust host-inbound-traffic system-services ping
set security zones security-zone trust interfaces ge-0/0/1.0
set security zones security-zone dmz interfaces ge-0/0/2.0

set security address-book global address CorpNet 10.10.0.0/16
set security address-book global address CorpNet description "Synthetic corporate network"
set security address-book global address WebServer 10.20.10.10/32
set security address-book global address WebServer description "Synthetic web service"
set security address-book global address WebServerCopy 10.20.10.10/32
set security address-book global address WebServerCopy description "Intentional duplicate"
set security address-book global address DnsServer 10.20.53.53/32
set security address-book global address DnsServer description "Synthetic DNS service"
set security address-book global address JumpHost 10.20.30.10/32
set security address-book global address JumpHost description "Synthetic jump host"
set security address-book global address LegacyFtp 10.20.21.10/32
set security address-book global address UnusedHost 10.99.99.99/32

set applications application APP-WIDE protocol tcp
set applications application APP-WIDE destination-port 1024-65535

set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE description "Intentional logged any-any audit seed"
set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE match source-address any
set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE match destination-address any
set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE match application any
set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE then permit
set security policies from-zone trust to-zone untrust policy ALLOW-ALL-EDGE then log session-close

set security policies from-zone trust to-zone untrust policy ALLOW-WEB description "Specific rule intentionally shadowed by ALLOW-ALL-EDGE"
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match source-address CorpNet
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match destination-address WebServer
set security policies from-zone trust to-zone untrust policy ALLOW-WEB match application junos-https
set security policies from-zone trust to-zone untrust policy ALLOW-WEB then permit
set security policies from-zone trust to-zone untrust policy ALLOW-WEB then log session-close

set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY description "Intentional redundant rule"
set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY match source-address CorpNet
set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY match destination-address WebServer
set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY match application junos-https
set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY then permit
set security policies from-zone trust to-zone untrust policy ALLOW-WEB-COPY then log session-close

set security policies from-zone trust to-zone untrust policy ALLOW-DNS-NOLOG match source-address CorpNet
set security policies from-zone trust to-zone untrust policy ALLOW-DNS-NOLOG match destination-address DnsServer
set security policies from-zone trust to-zone untrust policy ALLOW-DNS-NOLOG match application junos-dns-udp
set security policies from-zone trust to-zone untrust policy ALLOW-DNS-NOLOG then permit

set security policies from-zone trust to-zone untrust policy OLD-FTP match source-address CorpNet
set security policies from-zone trust to-zone untrust policy OLD-FTP match destination-address LegacyFtp
set security policies from-zone trust to-zone untrust policy OLD-FTP match application junos-ftp
set security policies from-zone trust to-zone untrust policy OLD-FTP then permit
set security policies from-zone trust to-zone untrust policy OLD-FTP then log session-close
deactivate security policies from-zone trust to-zone untrust policy OLD-FTP

set security policies from-zone untrust to-zone dmz policy ALLOW-RDP-IN description "Intentional risky inbound audit seed"
set security policies from-zone untrust to-zone dmz policy ALLOW-RDP-IN match source-address any
set security policies from-zone untrust to-zone dmz policy ALLOW-RDP-IN match destination-address JumpHost
set security policies from-zone untrust to-zone dmz policy ALLOW-RDP-IN match application junos-rdp
set security policies from-zone untrust to-zone dmz policy ALLOW-RDP-IN then permit

set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN description "Intentional conflict shadowed by earlier permit"
set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN match source-address any
set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN match destination-address JumpHost
set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN match application junos-rdp
set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN then deny
set security policies from-zone untrust to-zone dmz policy DENY-RDP-IN then log session-init

set security policies from-zone trust to-zone dmz policy ALLOW-MISSING description "Intentional unresolved destination reference"
set security policies from-zone trust to-zone dmz policy ALLOW-MISSING match source-address CorpNet
set security policies from-zone trust to-zone dmz policy ALLOW-MISSING match destination-address MissingBackend
set security policies from-zone trust to-zone dmz policy ALLOW-MISSING match application junos-https
set security policies from-zone trust to-zone dmz policy ALLOW-MISSING then permit
set security policies from-zone trust to-zone dmz policy ALLOW-MISSING then log session-close

set security policies global policy DENY-REST description "Synthetic terminal logged deny"
set security policies global policy DENY-REST match source-address any
set security policies global policy DENY-REST match destination-address any
set security policies global policy DENY-REST match application any
set security policies global policy DENY-REST then deny
set security policies global policy DENY-REST then log session-init

set security nat source rule-set TRUST-OUT from zone trust
set security nat source rule-set TRUST-OUT to zone untrust
set security nat source rule-set TRUST-OUT rule PAT match source-address 10.10.0.0/16
set security nat source rule-set TRUST-OUT rule PAT then source-nat interface

set routing-options static route 0.0.0.0/0 next-hop 198.51.100.1
```

## Deliberate audit seeds

The fixture intentionally contains a logged any-any permit, broader rules before
specific rules, a duplicate policy, an allow/deny ordering conflict, missing
policy logging, untrusted RDP exposure, an unresolved address reference, a
disabled policy, a large unused application, duplicate/unused objects, and
missing descriptions. The terminal global deny, screen, SSH/auth hardening,
remote syslog host, and lo0 input filter are deliberate negative controls that
must suppress their corresponding absence findings.
