# Field Notes — 12-branch vSRX3 lab: 6 AutoVPN + 6 ADVPN branches

Source: community field report, [fwskillsshare issue #4](https://github.com/fastrevmd-lab/fwskillsshare/issues/4) (2026-07-02).
Environment: vSRX3, Junos 24.4R1.9 and 25.4R1.12, hub as chassis cluster behind
1:1 static NAT, simulated dual-ISP underlay, IKEv2.

## Baseline that worked

The 6 hub-and-spoke branches (per `srx-autovpn-full-tunnel`, adapted) came up
cleanly with full-tunnel backhaul once two commit-blockers were worked around:

1. **`dynamic ike-user-type group-ike-id` + IKEv2 + PSK fails commit** on
   24.4R1.9 / 25.4R1.12:
   ```
   When dynamic ike-user-type is configured, IKEv2 with authentication-method pre-shared-key is not allowed
   ```
   This also blocks `shared-ike-id`. Working PSK alternative: per-spoke IKEv2
   gateways on the hub, each pinned by unique `remote-identity hostname
   <spokeN>`, no `ike-user-type`. Verified with 6 spokes. Consequence for
   ADVPN: the group model requires certificate auth.

2. **Traffic-selector `remote-ip 0.0.0.0/0` fails commit** when the spoke
   gateway has a static `address`:
   ```
   Remote-ip 0.0.0.0/0 in traffic-selector is not supported when address is configured under ike gateway
   ```
   Working split (both halves commit and bring up two child SAs):
   ```
   set security ipsec vpn <vpn> traffic-selector TS-LO local-ip <LAN>/24 remote-ip 0.0.0.0/1
   set security ipsec vpn <vpn> traffic-selector TS-HI local-ip <LAN>/24 remote-ip 128.0.0.0/1
   ```

## NAT-T findings (apply to ADVPN and AutoVPN alike)

- **Double NAT kills the 4500 float.** Spoke → carrier PAT → edge 1:1
  static-NAT → hub: IKE_SA_INIT (UDP 500) survives, but the fragmented
  IKE_AUTH **response** on UDP 4500 never returns through the stacked NATs.
  Hub completes as responder (shows UP); spoke retransmits forever. Fix:
  collapse to a single NAT hop (remove the underlay PAT; keep only the 1:1
  static NAT for the hub).
- **Initiator still needs `host-inbound-traffic system-services ike`** on its
  WAN/untrust zone, or the 4500 return is dropped at host-inbound. Proven by
  upstream session counters showing packets arriving at the spoke WAN and
  dying at the zone.

## ADVPN state: PKI-enrolled, blocked at IKE cert auth

**Blocker — `No public key found` at IKE_AUTH (unresolved):**
- Hub (responder) rejects every spoke cert: iked hits
  `ikev2_reply_cb_public_key: Error: No public key found` and sends
  `N(AUTHENTICATION_FAILED)`. IKE_SA_INIT completes; the fragmented IKE_AUTH
  is received; failure is at `ikev2_state_auth_responder_in_verify_signature`.
- Ruled out (all tested):
  - Junos version — hub cluster and spokes upgraded 24.4R1.9 → 25.4R1.12,
    identical failure.
  - Cert chain — `openssl verify -CAfile ca.pem <leaf>` OK; on-device
    `request security pki local-certificate verify` succeeds on both cluster
    nodes and every spoke.
  - Clock skew — NTP-synced, certs within validity (the classic cause; not it).
  - EKU — leaves re-issued with `extendedKeyUsage = 1.3.6.1.5.5.7.3.17`
    (id-kp-ipsecIKE) + serverAuth + clientAuth, loaded and verified; same
    failure.
  - `group-ike-id` vs per-spoke static cert gateways — identical.
  - `trusted-ca use-all` vs explicit `trusted-ca <PROFILE>`.
  - `revocation-check disable`.
  - `restart pki-service` + `restart ipsec-key-management`.
- Best diagnostic lead: `show log pki-trace` shows **pkid is never consulted
  at IKE connect time** — iked returns "No public key found" internally,
  before handing the received CERT payload to pkid for validation. Points at
  iked-internal peer-cert handling on vSRX3, or a missing
  `ike policy … certificate` knob.
- Untried hypotheses:
  - `set security ike policy <pol> certificate peer-certificate-type x509-signature`
  - RFC 7427 digital-signature vs PKCS#1 `rsa-signatures` mismatch
  - Minimal non-ADVPN, non-cluster IKEv2 cert VPN on the same image to
    isolate whether cert auth works at all
  - JTAC

**Chassis-cluster PKI gotcha (solved):** on a cluster,
`request security pki local-certificate load` runs on the **RG0-primary
node**. If the keypair was generated on the other node (e.g. after a
failover), load fails with `error load certid<...>`. Cross-node PKI HA-sync
appeared not to populate (`pkid_handle_hasync_files: no files`). Fix:
`request chassis cluster failover redundancy-group 0 node <keypair-node>` so
keypair and load land on the same RE, then load.
