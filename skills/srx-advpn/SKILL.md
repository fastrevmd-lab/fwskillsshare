---
name: srx-advpn
description: Use when designing, configuring, auditing, or troubleshooting Juniper SRX Auto Discovery VPN (ADVPN) — hub-and-spoke IPsec that dynamically builds direct spoke-to-spoke shortcut tunnels so branch-to-branch traffic bypasses the hub. Covers suggester and partner roles, the shortcut lifecycle, the multipoint st0 overlay, OSPF p2mp with dynamic-neighbors over the overlay, the certificate-authentication requirement (IKEv2 PSK with dynamic ike-user-type is rejected on modern Junos), PKI enrollment, the chassis-cluster certificate-load gotcha, verification, and troubleshooting including the vSRX 'No public key found' IKE_AUTH failure.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
license: source-derived-summary-local-use
metadata:
  hermes:
    tags: [srx, junos, advpn, auto-discovery-vpn, ipsec, vpn, spoke-to-spoke, shortcut, dynamic-mesh, suggester, partner, multipoint, st0, ospf, p2mp, dynamic-neighbors, pki, certificates, ikev2]
    related_skills: [srx-autovpn-full-tunnel, srx-ipsec-hub-spoke, srx-nat, srx-policy, parsing-srx-configs]
  sources:
    - title: Auto Discovery VPNs | Junos OS
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/junos/vpn-ipsec/topics/topic-map/security-auto-discovery-vpns.html
      retrieved: "2026-07-02"
    - title: IPsec VPN User Guide | Junos OS
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/junos/vpn-ipsec/index.html
      retrieved: "2026-07-02"
    - title: "Field report: 12-branch vSRX3 lab (6 AutoVPN + 6 ADVPN), Junos 24.4R1.9 / 25.4R1.12"
      author: community field report (fwskillsshare issue #4)
      url: https://github.com/fastrevmd-lab/fwskillsshare/issues/4
      retrieved: "2026-07-02"
---

# SRX Auto Discovery VPN (ADVPN)

## Overview

ADVPN is hub-and-spoke IPsec that **discovers spoke-to-spoke traffic and builds
direct shortcut tunnels at runtime**. The hub (the *suggester*) notices two
spokes (*partners*) exchanging traffic through it, introduces them to each
other over an IKEv2 extension, and the partners negotiate a direct IKE/IPsec
shortcut. A dynamic routing protocol running over the overlay (typically OSPF)
then reconverges so branch↔branch traffic takes the shortcut instead of
hairpinning through the hub. Idle shortcuts tear down and traffic falls back to
the hub path.

Core principle: **the hub brokers introductions; routing — not selectors —
steers traffic onto shortcuts.** That drives every design difference from
plain AutoVPN: a **multipoint numbered `st0`**, a **routing protocol over the
overlay**, and **certificate authentication**.

> **Certificates are effectively mandatory.** On current Junos (field-verified
> on vSRX3 24.4R1.9 and 25.4R1.12), IKEv2 with `authentication-method
> pre-shared-keys` **fails commit** whenever `dynamic ike-user-type`
> (group-ike-id or shared-ike-id) is configured:
> `When dynamic ike-user-type is configured, IKEv2 with authentication-method
> pre-shared-key is not allowed`. ADVPN's group model therefore requires
> RSA/ECDSA certificate auth. Plan PKI first — do not burn a day on a PSK
> ADVPN that cannot commit.

## When to Use

- Branch↔branch traffic is significant (VoIP, file transfer, replication) and
  hairpinning it through the hub adds latency or load — but a static full mesh
  is unmanageable.
- Many or churning spokes that still need direct any-to-any reachability.
- Auditing or troubleshooting an existing ADVPN: shortcuts not forming,
  shortcuts flapping, OSPF adjacencies missing, cert-auth failures.

When **not** to use:
- Spoke-to-spoke traffic is rare or policy requires central inspection of it —
  use `srx-autovpn-full-tunnel` (hub hairpin, zero-touch spokes, PSK possible
  with per-spoke gateways).
- A handful of stable sites — static per-spoke tunnels
  (`srx-ipsec-hub-spoke`) or a small static mesh is simpler.
- No PKI and no appetite to build one: ADVPN needs certificates (see above).

## Roles and the Shortcut Lifecycle

| Role | Where | Config |
|------|-------|--------|
| **Suggester** | Hub | `set security ike gateway <gw> advpn partner disable` (suggests only, never a shortcut endpoint) |
| **Partner** | Spokes | `set security ike gateway <gw> advpn suggester disable` (accepts suggestions, forms shortcuts) |

Lifecycle:
1. **Via hub.** Spoke A → hub → spoke B; OSPF routes over the overlay all point
   at the hub.
2. **Suggestion.** The suggester sees A↔B flows transiting and sends both
   partners a *shortcut suggestion* (IKEv2 notification) carrying each other's
   tunnel endpoint and identity.
3. **Shortcut establishment.** One partner initiates a direct IKEv2 SA to the
   other, authenticated with the same certificates as the hub tunnel. A
   shortcut IPsec SA comes up on the **same multipoint `st0` unit**.
4. **Reconvergence.** OSPF forms a direct adjacency over the shortcut; the
   partner's LAN routes now resolve via the shortcut next-hop, and traffic
   leaves the hub path.
5. **Teardown.** When the shortcut idles below the threshold for `idle-time`
   seconds, partners tear it down and routes fall back to the hub.

Partner-side tuning knobs (under `advpn partner`): `idle-time <seconds>`
(teardown timer), `idle-threshold <pps>` (rate below which the shortcut counts
as idle), `connection-limit <n>` (max concurrent shortcuts a partner will
hold).

## The Multipoint st0 Overlay

Unlike AutoVPN-with-traffic-selectors (point-to-point unnumbered `st0`), ADVPN
uses **one numbered, multipoint `st0` unit per node** on a shared overlay
subnet — shortcuts attach to the same unit at runtime:

```
set interfaces st0 unit 1 multipoint
set interfaces st0 unit 1 family inet address 10.255.0.11/24
```

- One overlay subnet (e.g. `10.255.0.0/24`), one address per node.
- Traffic selectors are **not** used — routing over the overlay decides what
  enters the tunnel. Do not configure `traffic-selector` on the ADVPN VPN.
- Put the `st0.1` unit in its own zone (e.g. `VPN`) with `host-inbound-traffic
  protocols ospf` so overlay adjacencies can form.

## Routing over the Overlay (OSPF p2mp)

Static routes cannot model tunnels that appear and disappear at runtime — a
dynamic protocol is required. The standard pattern is OSPF point-to-multipoint
with dynamic neighbors:

```
set protocols ospf area 0.0.0.0 interface st0.1 interface-type p2mp
set protocols ospf area 0.0.0.0 interface st0.1 dynamic-neighbors
set protocols ospf area 0.0.0.0 interface st0.1 flood-reduction
set protocols ospf area 0.0.0.0 interface <LAN-ifl> passive
```

- **`interface-type p2mp`** — the overlay is one subnet but not broadcast;
  p2mp advertises host routes to each neighbor rather than electing a DR.
- **`dynamic-neighbors`** — adjacencies form with peers discovered on the
  interface at runtime (shortcut partners) without listing neighbors.
- **`flood-reduction`** — suppresses periodic LSA refresh flooding over the
  overlay; worthwhile once shortcut count grows.
- Advertise each site's LAN into OSPF (passive interface or export policy).
- For full-tunnel-style centralized egress, originate the default from the hub
  with an OSPF export policy injecting `0.0.0.0/0` (area 0 cannot be a
  stub/NSSA, so `default-metric` does not apply here); keep the
  **anti-recursion host route** to the hub/partner WAN IPs more specific than
  any default that points into `st0` (same trap as
  `srx-autovpn-full-tunnel`).

When a shortcut forms, the two partners' OSPF cost to each other drops from
two overlay hops (via hub) to one, so the shortcut wins automatically — no
metric engineering needed for the basic case.

## PKI Enrollment

Minimum viable lab PKI (per node):

```
set security pki ca-profile LAB-CA ca-identity LAB-CA
# lab only — use CRL/OCSP revocation checking in production
set security pki ca-profile LAB-CA revocation-check disable

request security pki generate-key-pair certificate-id ADVPN-CERT size 2048 type rsa
request security pki generate-certificate-request certificate-id ADVPN-CERT subject CN=spoke11.homelab.local domain-name spoke11.homelab.local filename spoke11.csr
# sign the CSR on the CA, then:
request security pki ca-certificate load ca-profile LAB-CA filename ca.pem
request security pki local-certificate load certificate-id ADVPN-CERT filename spoke11.pem
request security pki local-certificate verify certificate-id ADVPN-CERT
```

> **Chassis-cluster gotcha (field-verified).** `request security pki
> local-certificate load` executes on the **RG0-primary node**. If the keypair
> was generated on the *other* node (e.g. after a failover), the load fails
> with `error load certid<...>` — and cross-node PKI HA-sync may not populate
> (`pkid_handle_hasync_files: no files` in pki-trace). Fix: `request chassis
> cluster failover redundancy-group 0 node <keypair-node>` so the keypair and
> the load land on the same RE, then load.

## Config Skeleton (`set` format)

Hub (suggester) — spokes differ only where noted:

```
# --- Multipoint tunnel interface, numbered overlay ---
set interfaces st0 unit 1 multipoint
set interfaces st0 unit 1 family inet address 10.255.0.1/24        # spoke: .11, .12, ...

# --- IKE Phase 1: certificates, IKEv2 ---
set security ike proposal ADVPN-IKE-PROP authentication-method rsa-signatures
set security ike proposal ADVPN-IKE-PROP dh-group group14
set security ike proposal ADVPN-IKE-PROP authentication-algorithm sha-256
set security ike proposal ADVPN-IKE-PROP encryption-algorithm aes-256-cbc
set security ike policy ADVPN-IKE-POL proposals ADVPN-IKE-PROP
set security ike policy ADVPN-IKE-POL certificate local-certificate ADVPN-CERT
set security ike policy ADVPN-IKE-POL certificate trusted-ca LAB-CA

# Hub gateway: dynamic, accepts any cert under the domain, suggester role
set security ike gateway ADVPN-HUB-GW ike-policy ADVPN-IKE-POL
set security ike gateway ADVPN-HUB-GW dynamic hostname homelab.local
set security ike gateway ADVPN-HUB-GW dynamic ike-user-type group-ike-id
set security ike gateway ADVPN-HUB-GW local-identity distinguished-name
set security ike gateway ADVPN-HUB-GW external-interface ge-0/0/0.0
set security ike gateway ADVPN-HUB-GW version v2-only
set security ike gateway ADVPN-HUB-GW advpn partner disable          # hub = suggester only

# Spoke gateway instead: address <HUB_WAN>, local-identity hostname spokeNN.homelab.local,
#   advpn suggester disable, and optionally:
# set security ike gateway ADVPN-SPOKE-GW advpn partner idle-time 300

# --- IPsec Phase 2: bound to the multipoint st0.1, NO traffic selectors ---
set security ipsec proposal ADVPN-IPSEC-PROP protocol esp
set security ipsec proposal ADVPN-IPSEC-PROP encryption-algorithm aes-256-gcm
set security ipsec policy ADVPN-IPSEC-POL perfect-forward-secrecy keys group14
set security ipsec policy ADVPN-IPSEC-POL proposals ADVPN-IPSEC-PROP
set security ipsec vpn ADVPN-VPN bind-interface st0.1
set security ipsec vpn ADVPN-VPN ike gateway ADVPN-HUB-GW
set security ipsec vpn ADVPN-VPN ike ipsec-policy ADVPN-IPSEC-POL
set security ipsec vpn ADVPN-VPN establish-tunnels immediately        # spoke side
set security flow tcp-mss ipsec-vpn mss 1350

# --- Zones ---
set security zones security-zone untrust host-inbound-traffic system-services ike
set security zones security-zone untrust interfaces ge-0/0/0.0
set security zones security-zone VPN host-inbound-traffic protocols ospf
set security zones security-zone VPN host-inbound-traffic system-services ping
set security zones security-zone VPN interfaces st0.1

# --- OSPF over the overlay ---
set protocols ospf area 0.0.0.0 interface st0.1 interface-type p2mp
set protocols ospf area 0.0.0.0 interface st0.1 dynamic-neighbors
set protocols ospf area 0.0.0.0 interface st0.1 flood-reduction
set protocols ospf area 0.0.0.0 interface ge-0/0/1.0 passive          # site LAN
```

Spoke prerequisites that are easy to miss (both field-verified on the AutoVPN
sibling and equally applicable here):
- **`untrust` needs `host-inbound-traffic system-services ike`** even on the
  initiator — without it the NAT-T port-4500 return is dropped at
  host-inbound and IKE_AUTH retransmits forever.
- The **anti-recursion host route** to the hub WAN (and, with shortcuts, the
  underlay path to partner WANs) must stay more specific than any default
  pointing into `st0`.

## Verification

```
show security ike security-associations              # hub tunnel + shortcut SAs
show security ike active-peer                        # all partners registered on the hub
show security ipsec security-associations            # shortcut SAs appear alongside the hub SA
show security ipsec security-associations detail     # look for the ADVPN/shortcut flag per SA
show ospf neighbor                                   # hub adjacency + per-shortcut adjacencies
show route <remote-branch-LAN>                       # next-hop moves from hub overlay IP to partner overlay IP
```

Prove the shortcut path end-to-end: start a spoke-A↔spoke-B flow, confirm a
new IKE SA between the two spoke WAN IPs, then `traceroute` (or compare
`show security flow session` on the hub — the A↔B session should disappear
from the hub once the shortcut carries it).

## Troubleshooting Matrix

| Stage | Symptom | Cause / fix |
|-------|---------|-------------|
| Commit | `IKEv2 with authentication-method pre-shared-key is not allowed` | PSK + `dynamic ike-user-type` is rejected (24.4R1/25.4R1) — use certificate auth; there is no PSK ADVPN on these images |
| IKE_AUTH | Hub logs `ikev2_reply_cb_public_key: Error: No public key found` → `N(AUTHENTICATION_FAILED)` to every spoke | **Open field blocker on vSRX3** — see below |
| NAT-T | IKE_SA_INIT (500) completes; 4500 IKE_AUTH retransmits forever, responder side shows UP | Double NAT in the underlay (carrier PAT + hub-behind-static-NAT) drops the 4500 return — collapse to a single NAT hop |
| NAT-T | Same 4500-retransmit symptom, single NAT | Initiator's `untrust` zone missing `host-inbound-traffic system-services ike` |
| Shortcut | Hub tunnel up, spokes reach each other only via hub, no shortcut SA | Roles wrong (`advpn suggester/partner disable` on the wrong end), partner `connection-limit` reached, or suggester never sees transit traffic (flows not crossing the hub st0) |
| Shortcut | Shortcut forms, traffic still via hub | OSPF not running over `st0.1` (`dynamic-neighbors` missing, zone blocks `protocols ospf`), or LAN routes not advertised |
| Shortcut | Shortcuts flap | `idle-time`/`idle-threshold` too aggressive for the traffic profile |
| PKI (cluster) | `error load certid<...>` loading a cert | Keypair on the non-RG0-primary node — fail RG0 over to that node, then load |
| Fragmentation | Small flows work, large fail | ESP overhead — keep `tcp-mss ipsec-vpn 1350`, lower on PMTU issues |

### Open blocker: `No public key found` at IKE_AUTH (vSRX3 24.4R1 / 25.4R1)

Field state as of 2026-07: a 6-spoke vSRX3 ADVPN lab is PKI-enrolled but
blocked — the hub (responder, chassis cluster) rejects **every** spoke cert at
`ikev2_state_auth_responder_in_verify_signature` with
`ikev2_reply_cb_public_key: Error: No public key found`, then sends
`N(AUTHENTICATION_FAILED)`. IKE_SA_INIT completes; the fragmented IKE_AUTH is
received.

Ruled out (all tested): Junos version (identical on 24.4R1.9 and 25.4R1.12);
cert chain (`openssl verify` and on-device `request security pki
local-certificate verify` pass on every node); clock skew (NTP-synced, certs
in validity — the classic cause, and it is *not* it here); EKU (re-issued
leaves with id-kp-ipsecIKE `1.3.6.1.5.5.7.3.17` + serverAuth + clientAuth —
same failure); `group-ike-id` vs per-spoke static cert gateways; `trusted-ca
use-all` vs explicit profile; `revocation-check disable`; `restart
pki-service` and `restart ipsec-key-management`.

Best diagnostic lead: `show log pki-trace` shows **pkid is never consulted at
IKE connect time** — iked fails internally before handing the peer CERT
payload to pkid, pointing at iked-internal peer-cert handling on vSRX3 or a
missing IKE-policy certificate knob.

Try next (untried at time of writing): `set security ike policy <pol>
certificate peer-certificate-type x509-signature`; check for an RFC 7427
digital-signature vs PKCS#1 `rsa-signatures` mismatch; build a minimal
non-ADVPN, non-cluster IKEv2 cert VPN on the same image to isolate whether
cert auth works at all; open a JTAC case with the iked/pki traces.

## Choose ADVPN vs AutoVPN vs Static

| | **ADVPN (this skill)** | AutoVPN full-tunnel | Static P2P hub-spoke |
|---|---|---|---|
| Spoke↔spoke path | Direct shortcut after introduction | Hairpin via hub | Hairpin via hub |
| Hub tunnel interface | Multipoint numbered `st0` | Single P2P unnumbered `st0.0` | One `st0` unit per spoke |
| Routing | OSPF (p2mp, dynamic-neighbors) over overlay | ARI + statics | Manual statics |
| Auth | **Certificates (required)** | PSK possible (per-spoke gateways) or certs | PSK or certs |
| Add a spoke | Zero hub change (enroll cert) | Zero hub change (cert) / one gateway (PSK) | Hub change per spoke |
| Best for | Meshy branch↔branch traffic at scale | Centralized egress/inspection | Few stable sites |

Centralized-egress backhaul and ADVPN compose: originate the default from the
hub into OSPF and shortcuts still form for branch↔branch flows.

## Source Notes

Mechanics summarized from Juniper's Auto Discovery VPN documentation. The
certificate-requirement commit error, chassis-cluster PKI gotcha, NAT-T
double-NAT and host-inbound findings, and the open `No public key found`
blocker are field data from a 12-branch vSRX3 lab build (Junos 24.4R1.9 /
25.4R1.12) contributed via
[fwskillsshare issue #4](https://github.com/fastrevmd-lab/fwskillsshare/issues/4).
See `references/field-notes-vsrx-advpn-lab.md`.
