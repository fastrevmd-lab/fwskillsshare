# Firewall Best-Practices Audit — Remediation Patterns

> Reference material for the `firewall-best-practices-audit` skill; loaded on
> demand. The body's Finding template draws the `Fix (<source-vendor>)` line
> from the matching family below. Snippets are **illustrative templates** — use
> the placeholders (`<src-obj>`, `<dst-obj>`, `<port>`, `<zone>`, `<mgmt-subnet>`,
> `<name>`, `<id>`) and adapt to the real config. **Never paste real PSKs, keys,
> or secrets.** Always validate in a change window and confirm with the verify
> commands noted per family.

Each subsection covers the same fix for all four vendors: Cisco ASA/FTD,
Palo PAN-OS, FortiGate, and Juniper SRX. Vendor syntax is drawn from the repo's
parsing/`srx-*` skills so it stays idiomatic.

> **Cisco ASA/FTD note:** the "Cisco ASA/FTD" snippets below are ASA-style CLI
> (also applicable to FTD via FlexConfig/LINA). FMC-managed FTD applies the
> equivalent change through its access-control policy (and platform settings),
> not through persistent `access-list`/`http`/`ssh` CLI — translate accordingly.

---

## Overly permissive / any-any (SEC-ANY-ANY, SEC-ANY-SVC, SEC-BROAD-SRC, SEC-BROAD-DST)

Vendor-neutral: replace `any` with the specific source zones/subnets, destination
hosts, and named services the business actually needs; add per-rule logging; and
record an owner/description. Collapse broad supernets (≤ /8 or 0.0.0.0/0) into the
narrowest prefix that still satisfies intent.

- **Cisco ASA/FTD:** define objects, then a scoped ACE, and remove the any/any line:
  ```
  object network SRC-OBJ
   subnet <src-net> <mask>
  object network DST-OBJ
   host <dst-ip>
  access-list OUTSIDE_IN extended permit tcp object SRC-OBJ object DST-OBJ eq <port> log
  no access-list OUTSIDE_IN extended permit ip any any
  access-group OUTSIDE_IN in interface outside
  ```
- **Palo PAN-OS:** narrow the security rule's `source`, `destination`, and `service`
  to specific objects; keep `action allow` with `log-end yes`; drop the `any` members:
  ```
  set rulebase security rules <name> source <src-obj> destination <dst-obj>
  set rulebase security rules <name> service <svc-obj> application <app>
  set rulebase security rules <name> action allow log-end yes
  set rulebase security rules <name> description "<owner/ticket>"
  ```
- **FortiGate:** scope the policy to named address/service objects and enable logging:
  ```
  config firewall policy
      edit <id>
          set srcaddr "<src-obj>"
          set dstaddr "<dst-obj>"
          set service "<svc>"
          set logtraffic all
          set comments "<owner/ticket>"
      next
  end
  ```
- **Juniper SRX:** match specific address/application objects, permit with logging:
  ```
  set security policies global policy <name> match from-zone <zone>
  set security policies global policy <name> match to-zone <zone>
  set security policies global policy <name> match source-address <src-obj>
  set security policies global policy <name> match destination-address <dst-obj>
  set security policies global policy <name> match application <app>
  set security policies global policy <name> then permit
  set security policies global policy <name> then log session-close
  ```

---

## Missing logging / no owner (SEC-NO-LOG, SEC-NO-DESC)

Vendor-neutral: every permit (and every important deny) should log on session
close so flows are auditable; broad rules should also log session start. Add a
description tying the rule to an owner or change ticket.

- **Cisco ASA/FTD:** append `log` to the ACE (optionally `log <level> interval <n>`):
  ```
  access-list OUTSIDE_IN extended permit tcp object SRC-OBJ object DST-OBJ eq <port> log
  ```
  Cisco FTD additionally sets per-rule logging (log at end of connection) in the
  access-control policy and points it at the syslog/SIEM alarm config.
- **Palo PAN-OS:** turn on end-of-session logging and forward to the log profile:
  ```
  set rulebase security rules <name> log-end yes
  set rulebase security rules <name> log-setting <log-forwarding-profile>
  set rulebase security rules <name> description "<owner/ticket>"
  ```
- **FortiGate:** set `logtraffic all` (start+end); add `logtraffic-start enable` on
  high-value rules; record a comment:
  ```
  config firewall policy
      edit <id>
          set logtraffic all
          set logtraffic-start enable
          set comments "<owner/ticket>"
      next
  end
  ```
- **Juniper SRX:** log on session close (and `session-init` for denies); add a count:
  ```
  set security policies global policy <name> then log session-close
  set security policies global policy <name> then count
  set security policies global policy <name> then permit
  ```
  Send to a stream: `set security log mode stream` / `set security log stream <name> host <syslog-ip>`.

---

## Plaintext management (SEC-PLAINTEXT-MGMT)

Vendor-neutral: disable telnet, plaintext HTTP admin, and SNMP v1/v2c community
strings; enable SSHv2, HTTPS, and SNMPv3 (authPriv) instead.

- **Cisco ASA/FTD:** kill telnet, force SSHv2, move ASDM/HTTPS to the mgmt subnet,
  replace SNMP community with v3:
  ```
  no telnet 0.0.0.0 0.0.0.0 management
  crypto key generate rsa modulus 2048
  ssh version 2
  ssh <mgmt-subnet> <mask> management
  http server enable
  no http 0.0.0.0 0.0.0.0 outside
  http <mgmt-subnet> <mask> management
  no snmp-server community <community>
  snmp-server group MGMT-GRP v3 priv
  snmp-server user <user> MGMT-GRP v3 auth sha <auth-ph> priv aes 256 <priv-ph>
  snmp-server host management <nms-ip> version 3 <user>
  ```
- **Palo PAN-OS:** disable telnet/HTTP on the mgmt service, keep SSH/HTTPS, set SNMPv3:
  ```
  set deviceconfig system service disable-telnet yes
  set deviceconfig system service disable-http yes
  set deviceconfig system service disable-ssh no
  set deviceconfig system service disable-https no
  set deviceconfig system snmp-setting access-setting version v3
  ```
- **FortiGate:** remove telnet/http from interface access and disable v1/v2c SNMP,
  using an SNMPv3 user instead of a community:
  ```
  config system interface
      edit "<mgmt-intf>"
          set allowaccess ping ssh https
      next
  end
  config system global
      set admin-telnet disable
  end
  config system snmp user
      edit "<user>"
          set security-level auth-priv
          set auth-proto sha256
          set priv-proto aes256
      next
  end
  ```
- **Juniper SRX:** delete telnet and HTTP web-management, enable SSH + HTTPS, use SNMPv3:
  ```
  delete system services telnet
  delete system services web-management http
  set system services ssh protocol-version v2
  set system services web-management https system-generated-certificate
  delete snmp community <community>
  set snmp v3 usm local-engine user <user> authentication-sha authentication-key "<auth-ph>"
  set snmp v3 usm local-engine user <user> privacy-aes128 privacy-key "<priv-ph>"
  ```

---

## Exposed risky / management services (SEC-EXPOSED-MGMT, SEC-EXPOSED-RISKY, SEC-INBOUND-ANY, SEC-MGMT-DATAZONE)

Vendor-neutral: device management (SSH/HTTPS/SNMP) must not be reachable from
untrusted/data zones — restrict it to a dedicated management subnet/zone. Risky
services (RDP/SMB/DB/telnet) and any inbound-from-internet permits must be scoped
to specific sources and destinations, never `any`.

- **Cisco ASA/FTD:** confine SSH/HTTPS to the mgmt interface + subnet, and scope any
  inbound RDP/DB ACE to known sources:
  ```
  no ssh 0.0.0.0 0.0.0.0 outside
  ssh <mgmt-subnet> <mask> management
  no access-list OUTSIDE_IN extended permit tcp any any eq 3389
  access-list OUTSIDE_IN extended permit tcp object PARTNER-SRC object RDP-HOST eq 3389 log
  access-group OUTSIDE_IN in interface outside
  ```
- **Palo PAN-OS:** remove management services from data interfaces via an interface
  management profile with a permitted-ip allowlist; scope risky rules:
  ```
  set network profiles interface-management-profile MGMT-ALLOW permitted-ip <mgmt-subnet>
  set network profiles interface-management-profile MGMT-ALLOW ssh yes https yes ping yes
  set network interface ethernet ethernet1/3 layer3 interface-management-profile MGMT-ALLOW
  set rulebase security rules allow-rdp source <partner-src> destination <rdp-host> service <rdp-svc> action allow log-end yes
  ```
- **FortiGate:** strip mgmt protocols from the WAN interface and pin admin access to a
  trusthost; scope risky inbound to a VIP + source:
  ```
  config system interface
      edit "<wan-intf>"
          set allowaccess ping
      next
  end
  config system admin
      edit "admin"
          set trusthost1 <mgmt-subnet> <mask>
      next
  end
  config firewall policy
      edit <id>
          set srcintf "untrust"
          set dstintf "dmz"
          set srcaddr "<partner-src>"
          set dstaddr "<rdp-vip>"
          set service "RDP"
          set logtraffic all
      next
  end
  ```
- **Juniper SRX:** remove host-inbound management from the untrust zone (keep it on a
  dedicated mgmt zone / fxp0), and scope risky inbound policies:
  ```
  delete security zones security-zone untrust host-inbound-traffic system-services ssh
  delete security zones security-zone untrust host-inbound-traffic system-services https
  set security zones security-zone mgmt host-inbound-traffic system-services ssh
  set security policies global policy allow-rdp match from-zone untrust
  set security policies global policy allow-rdp match to-zone dmz
  set security policies global policy allow-rdp match source-address <partner-src>
  set security policies global policy allow-rdp match destination-address <rdp-host>
  set security policies global policy allow-rdp match application junos-ms-rdp
  set security policies global policy allow-rdp then permit
  set security policies global policy allow-rdp then log session-close
  ```

---

## Weak IKE / IPsec (SEC-WEAK-IKE, SEC-WEAK-IPSEC, SEC-PSK-WEAK)

Vendor-neutral: raise DH to group 14 or higher, use AES-256 (prefer AES-GCM), SHA-256+
integrity, enable PFS on Phase 2, force IKEv2 (disable IKEv1 aggressive mode), and
rotate any weak/shared pre-shared key to a long unique secret stored out of band.

- **Cisco ASA/FTD:** IKEv2 proposal + AES-GCM IPsec proposal, PFS on the crypto map,
  and disable IKEv1 aggressive mode:
  ```
  crypto ikev2 policy 10
   encryption aes-256
   integrity sha256
   group 14
   prf sha256
  crypto ipsec ikev2 ipsec-proposal AES-GCM
   protocol esp encryption aes-gcm-256
   protocol esp integrity null
  crypto map MAP 10 set ikev2 ipsec-proposal AES-GCM
  crypto map MAP 10 set pfs group14
  crypto ikev1 am-disable
  ```
- **Palo PAN-OS:** strong IKE and IPsec crypto profiles, IKEv2 only on the gateway:
  ```
  set network ike crypto-profiles ike-crypto-profiles STRONG-IKE dh-group group14 encryption aes-256-cbc hash sha256
  set network ike crypto-profiles ipsec-crypto-profiles STRONG-IPSEC esp encryption aes-256-gcm authentication none
  set network ike crypto-profiles ipsec-crypto-profiles STRONG-IPSEC dh-group group14
  set network ike gateway <gw> protocol version ikev2
  set network ike gateway <gw> protocol ikev2 dpd enable yes
  ```
- **FortiGate:** strong phase1/phase2 proposals, IKEv2, PFS enabled, main mode:
  ```
  config vpn ipsec phase1-interface
      edit "<name>"
          set ike-version 2
          set proposal aes256gcm-prfsha256
          set dhgrp 14
      next
  end
  config vpn ipsec phase2-interface
      edit "<name>"
          set proposal aes256gcm
          set pfs enable
          set dhgrp 14
      next
  end
  ```
- **Juniper SRX:** group14, AES-256-GCM, SHA-256, IKEv2 only, PFS group14:
  ```
  set security ike proposal IKE-PROP authentication-method pre-shared-keys
  set security ike proposal IKE-PROP dh-group group14
  set security ike proposal IKE-PROP authentication-algorithm sha-256
  set security ike proposal IKE-PROP encryption-algorithm aes-256-cbc
  set security ike policy IKE-POL mode main
  set security ike policy IKE-POL proposals IKE-PROP
  set security ike gateway <gw> version v2-only
  set security ipsec proposal IPSEC-PROP protocol esp
  set security ipsec proposal IPSEC-PROP encryption-algorithm aes-256-gcm
  set security ipsec policy IPSEC-POL perfect-forward-secrecy keys group14
  set security ipsec policy IPSEC-POL proposals IPSEC-PROP
  ```

---

## Shadowed / redundant / ordering (SEC-SHADOW, SEC-REDUNDANT, SEC-OVERLAP, SEC-NO-DENY-ALL, SEC-DISABLED, SEC-ORPHAN-REF)

Vendor-neutral: move specific rules above the broader rule that shadows them, delete
exact-duplicate and dead/disabled rules, fix references to missing objects, and make
sure the rulebase ends with an explicit logged deny-all.

- **Cisco ASA/FTD:** insert the specific ACE at a line number ahead of the broad one,
  remove the duplicate, and add a terminal logged deny:
  ```
  access-list OUTSIDE_IN line 5 extended permit tcp object SRC-OBJ object DST-OBJ eq <port> log
  no access-list OUTSIDE_IN extended permit ip any object DST-OBJ
  access-list OUTSIDE_IN extended deny ip any any log
  ```
- **Palo PAN-OS:** reorder the rule above the shadowing rule, delete the redundant
  entry, and keep an explicit logged deny-all (PAN-OS implicit deny is unlogged):
  ```
  move rulebase security rules <specific-rule> before <broad-rule>
  delete rulebase security rules <redundant-rule>
  set rulebase security rules deny-all from any to any source any destination any application any service any action deny log-end yes
  ```
- **FortiGate:** FortiGate matches top-down, so move the specific policy up, delete the
  duplicate, and add an explicit logged deny (implicit deny is unlogged):
  ```
  config firewall policy
      move <specific-id> before <broad-id>
      delete <redundant-id>
      edit <deny-id>
          set srcintf "any"
          set dstintf "any"
          set srcaddr "all"
          set dstaddr "all"
          set action deny
          set logtraffic all
      next
  end
  ```
- **Juniper SRX:** reorder with `insert`, delete the duplicate/disabled policy, and keep
  a final logged default-deny:
  ```
  insert security policies global policy <specific-name> before policy <broad-name>
  delete security policies global policy <redundant-name>
  set security policies global policy 999-DENY-REST match from-zone any
  set security policies global policy 999-DENY-REST match to-zone any
  set security policies global policy 999-DENY-REST match source-address any
  set security policies global policy 999-DENY-REST match destination-address any
  set security policies global policy 999-DENY-REST match application any
  set security policies global policy 999-DENY-REST then deny
  set security policies global policy 999-DENY-REST then log session-init
  ```

---

## Object & group cleanup (OPS-UNUSED-OBJ, OPS-DUP-OBJ, OPS-REDUNDANT-OBJ, OPS-LARGE-GROUP, OPS-NESTED-GROUP, OPS-NO-DESC-OBJ, OPS-NAMING, OPS-CONSOLIDATE)

Vendor-neutral: delete unreferenced and exact-duplicate objects, merge subset/superset
duplicates onto one canonical name, flatten oversized or deeply nested groups, add
descriptions, and standardize naming. Collapse many /32 hosts into a prefix when intent
is identical.

- **Cisco ASA/FTD:** remove unused/duplicate objects and split an oversized group:
  ```
  no object network <unused-obj>
  no object-group network <dup-group>
  object-group network WEB-SERVERS-A
   description Web tier subset A (owner: netops)
   network-object 10.0.1.0 255.255.255.0
  ```
  (Replace many `network-object host` lines with the summarizing subnet where equivalent.)
- **Palo PAN-OS:** delete the unused object, repoint references to the canonical one, and
  split the large group:
  ```
  delete address <unused-obj>
  set address <canonical-obj> ip-netmask <net>/<cidr> description "<owner>"
  set address-group <large-group> static [ <obj-1> <obj-2> ]
  ```
- **FortiGate:** delete unreferenced/duplicate addresses and tighten group membership:
  ```
  config firewall address
      delete "<unused-obj>"
      edit "<canonical-obj>"
          set subnet <net> <mask>
          set comment "<owner>"
      next
  end
  config firewall addrgrp
      edit "<large-group>"
          set member "<obj-1>" "<obj-2>"
      next
  end
  ```
- **Juniper SRX:** delete unused address-book/application objects, collapse /32s into a
  prefix, and add descriptions:
  ```
  delete security address-book global address <unused-obj>
  delete applications application <dup-app>
  set security address-book global address NET-WEB 10.0.1.0/24 description "<owner>"
  set security address-book global address-set WEB-SERVERS address NET-WEB
  ```

---

## SSH / management hardening (SEC-SSH-ROOT-LOGIN)

Vendor-neutral: never allow direct root/admin SSH login; force key-based auth where
possible, cap concurrent sessions, and rate-limit new connections so the management
plane resists brute-force and exhaustion. SRX is authoritative below.

- **Juniper SRX:** deny root SSH, drop password auth, and add connection/rate limits:
  ```
  set system services ssh root-login deny
  set system services ssh no-passwords
  set system services ssh connection-limit 5
  set system services ssh rate-limit 4
  set system services ssh protocol-version v2
  ```
- **Cross-vendor:** Cisco `no ip http server` + `ip ssh version 2` / `ip ssh
  authentication-retries <n>` and an ACL on the vty/SSH lines; Palo PAN-OS / FortiGate
  restrict admin SSH/HTTPS to a permitted-IP / trusthost management allowlist and
  disable plaintext admin (see Plaintext-management family).

Verify (SRX): `show configuration system services ssh | display set`.

---

## Unreferenced security services (SEC-SERVICES-UNREFERENCED)

Vendor-neutral: a configured inspection profile (UTM/web-filter/IPS/AppFW/AV) that is
attached to no permit rule inspects nothing — bind it to the intended allow policy or
delete it. SRX is authoritative below.

- **Juniper SRX:** attach the service to a permit policy under `then permit
  application-services`:
  ```
  set security policies global policy <name> then permit application-services utm-policy <utm-name>
  set security policies global policy <name> then permit application-services application-firewall rule-set <appfw-rs>
  ```
- **Cross-vendor:** Palo PAN-OS attach a `profile-setting profiles`/`group <name>` to
  the security rule; FortiGate set `utm-status enable` plus the relevant
  `av-profile`/`ips-sensor`/`webfilter-profile` on the policy; Cisco FTD reference the
  intrusion/file policy in the access-control rule.

Verify (SRX): `show security policies policy-name <name> detail`.

---

## Zones/NAT without policy + empty policy set (SEC-ZONES-NAT-NO-POLICY, SEC-EMPTY-POLICYSET)

Vendor-neutral: zones and NAT rules with no security policies referencing them pass no
traffic (or, on default-permit platforms, pass it unfiltered) — add explicit permit
policies for each intended flow and close the set with a logged global deny. An empty
policy set is a coverage warning: confirm whether it is default-deny-by-design,
partial config, or a logical-system/tenant whose policies live elsewhere. SRX is
authoritative below.

- **Juniper SRX:** add explicit permit policies for intended flows, then a final logged
  global deny:
  ```
  set security policies global policy 100-USERS-WEB match from-zone <src-zone>
  set security policies global policy 100-USERS-WEB match to-zone <dst-zone>
  set security policies global policy 100-USERS-WEB match source-address <src-obj>
  set security policies global policy 100-USERS-WEB match destination-address <dst-obj>
  set security policies global policy 100-USERS-WEB match application <app>
  set security policies global policy 100-USERS-WEB then permit
  set security policies global policy 100-USERS-WEB then log session-close
  set security policies global policy 999-DENY-REST match from-zone any
  set security policies global policy 999-DENY-REST match to-zone any
  set security policies global policy 999-DENY-REST match source-address any
  set security policies global policy 999-DENY-REST match destination-address any
  set security policies global policy 999-DENY-REST match application any
  set security policies global policy 999-DENY-REST then deny
  set security policies global policy 999-DENY-REST then log session-init
  ```
- **Cross-vendor:** Cisco bind an `access-group` to the interface and end the ACL with
  `deny ip any any log`; Palo PAN-OS / FortiGate add the intended allow rules plus an
  explicit logged deny-all (both implicit denies are unlogged — see the Shadowed family).

Verify (SRX): `show security policies` / `show security match-policies`.

---

## Host-inbound exposure (SEC-HOST-INBOUND-EXPOSURE)

Vendor-neutral: management and sensitive services must not be reachable on an
untrusted/data zone's host-inbound surface — strip them from the untrust zone and keep
them only on a dedicated management zone/interface. SRX is authoritative below.

- **Juniper SRX:** remove mgmt system-services from the untrust zone host-inbound
  traffic (keep them on the mgmt zone / fxp0):
  ```
  delete security zones security-zone untrust host-inbound-traffic system-services ssh
  delete security zones security-zone untrust host-inbound-traffic system-services https
  delete security zones security-zone untrust host-inbound-traffic system-services snmp
  set security zones security-zone mgmt host-inbound-traffic system-services ssh
  ```
- **Cross-vendor:** Cisco confine `ssh`/`http`/`snmp-server host` to the management
  interface + subnet; Palo PAN-OS detach the interface-management-profile (or strip
  ssh/https/snmp from it) on data interfaces; FortiGate set the WAN interface
  `allowaccess` to `ping` only.

Verify (SRX): `show configuration security zones security-zone untrust | display set`.

---

## No screen on external zone (SEC-NO-SCREEN)

Vendor-neutral: the internet-facing/untrust zone should have a screen (IDS) profile
bound so flood, scan, and malformed-packet protections apply at the edge. SRX is
authoritative below.

- **Juniper SRX:** define a screen profile and bind it to the external zone:
  ```
  set security screen ids-option UNTRUST-SCREEN tcp syn-flood alarm-threshold 1024
  set security screen ids-option UNTRUST-SCREEN icmp flood threshold 1000
  set security screen ids-option UNTRUST-SCREEN ip spoofing
  set security zones security-zone untrust screen UNTRUST-SCREEN
  ```
- **Cross-vendor:** Cisco rely on `threat-detection`/`ip verify reverse-path` and
  embryonic-connection limits in NAT/policy; Palo PAN-OS attach a Zone Protection
  profile to the untrust zone; FortiGate enable DoS policies on the WAN interface.

Verify (SRX): `show security screen status` / `show configuration security zones security-zone untrust | display set`.

---

## Auth hardening (SEC-AUTH-HARDENING)

Vendor-neutral: enforce a password-complexity/length policy and a login lockout (retry
limit + backoff) so local accounts resist guessing. Use placeholders; never commit a
real password. SRX is authoritative below.

- **Juniper SRX:** set a login password policy and retry-options lockout:
  ```
  set system login password minimum-length 12
  set system login password change-type character-sets
  set system login password minimum-changes 3
  set system login retry-options tries-before-disconnect 3
  set system login retry-options backoff-threshold 2
  set system login retry-options lockout-period 5
  ```
- **Cross-vendor:** Cisco `aaa local authentication attempts max-fail <n>` plus
  `password-policy` (minimum-length/complexity); Palo PAN-OS set a password-complexity
  profile and an authentication-profile lockout; FortiGate `config system
  password-policy` plus `config system global` `admin-lockout-threshold`/`-duration`.

Verify (SRX): `show configuration system login | display set`.

---

## Notes

- These are change templates, not turnkey configs — confirm interface names, zone
  names, object names, and platform/version syntax against the live device.
- After any change, verify: Cisco `show running-config access-list` / `show crypto`;
  Palo `show running security-policy` / `test security-policy-match`; FortiGate
  `show firewall policy` / `diagnose vpn ike gateway`; SRX `show security policies`,
  `show security ike security-associations`, `show configuration | display set`.
- Log forwarding (syslog/SIEM) and a final logged deny-all are prerequisites for the
  logging and shadowed-rule families to be effective.
