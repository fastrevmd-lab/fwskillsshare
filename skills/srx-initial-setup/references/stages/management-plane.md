# Stage 2 — Management Plane

This stage establishes system identity, time synchronization, name resolution, and management network addressing. These are prerequisites for later stages that depend on accurate timestamps, reachable logging destinations, and stable management connectivity.

## What this stage establishes

- **System identity:** Hostname and domain name configured for identification in logs, prompts, and DNS.
- **Time synchronization:** NTP configured and operational, providing accurate timestamps for logs, security event correlation, and troubleshooting.
- **Name resolution:** DNS name servers configured, enabling the device to resolve hostnames for logging, NTP (if using domain names), and external services.
- **Management addressing:** The management interface has a routable address, either static or via DHCP with a confirmed lease, and is reachable from the operator's management network.

All `mgmt.*` gaps are `blocking` for the `factory.*` stage, **except for `factory.auto-image-upgrade`, which is offered before this stage runs.** Phone-home ZTP resets DHCP client state on the WAN units and can install an image and reboot unattended, either of which can disrupt establishing the management plane; it must therefore close first. Every other factory-default removal is a lockout-risk change and waits for the replacement management path to be established and verified.

**Lockout-risk gaps in this stage follow the gate protocol in `references/write-safety.md`.** That file is the authority for commit-confirmed mechanics, timer selection, rollback points, and recovery-path requirements.

## Choosing the management interface

The decision between fxp0 (dedicated out-of-band management interface) and a revenue port (data-plane interface subject to security zones and policies) depends on platform capabilities, network topology, and deployment requirements.

**This skill does not re-derive that analysis.** The reasoning is owned by `skills/srx-syslog-logging/references/fxp0-and-management-vrf.md`, which documents:

- What fxp0 is and how it differs from revenue interfaces
- Whether to place fxp0 in a management routing instance (`mgmt_junos`)
- When to use a revenue port instead (e.g., Security Director Cloud onboarding, which requires a revenue port for stream-mode security logs)
- Platform and release support considerations

**This stage requires choosing which interface will carry management traffic** — either fxp0 (the dedicated out-of-band management interface, if present) or a revenue port (a data-plane interface that participates in security policy processing). The choice depends on platform capabilities, deployment topology, and whether features like Security Director Cloud onboarding are required.

**Route to `skills/srx-syslog-logging/references/fxp0-and-management-vrf.md` for the complete decision framework.** This stage assumes the operator has chosen the management interface based on that analysis.

## Gaps

### `mgmt.hostname-absent`

- **Stage:** management-plane
- **Severity:** `blocking`
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `false`
- **Evidence:** `show configuration system host-name` returns no configured hostname, or returns a default/placeholder value
- **Proposal:**

  ```text
  set system host-name <device-hostname>
  ```

  Replace `<device-hostname>` with the desired hostname. The hostname should be unique within the management domain and less than 256 characters.

  **Source:** Juniper Networks, "Hostnames" (Junos OS System Management and Monitoring), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/system-mgmt-monitoring/topics/topic-map/hostnames.html

### `mgmt.domain-absent`

- **Stage:** management-plane
- **Severity:** `advisory` (recommended for fully-qualified domain name construction; not blocking if DNS is unused)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `false`
- **Evidence:** `show configuration system domain-name` returns no configured domain name
- **Proposal:**

  ```text
  set system domain-name example.com
  ```

  Replace `example.com` with the organization's domain. Junos uses this as the default domain to append to hostnames that are not fully qualified.

  **Source:** Juniper Networks, "Understanding and Configuring DNS" (Junos OS System Management and Monitoring), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/junos-getting-started/topics/topic-map/dns-system-management.html

### `mgmt.dns-absent`

- **Stage:** management-plane
- **Severity:** `blocking` (name resolution is required for NTP if using domain names, and for logging to named destinations)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `false`
- **Evidence:** `show configuration system name-server` returns no configured DNS servers
- **Proposal:**

  ```text
  set system name-server 8.8.8.8
  set system name-server 8.8.4.4
  ```

  As a best practice, configure access to multiple name servers, up to a maximum of three. The system uses only the first three configured name servers even if additional servers are configured.

  **Source:** Juniper Networks, "name-server (System Services)" (Junos OS CLI Reference), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/name-server-edit-system.html

  Replace `8.8.8.8` and `8.8.4.4` with the organization's preferred DNS servers. Public DNS (Google, Cloudflare, Quad9) is shown here as an example; enterprise deployments should use internal DNS servers when available.

### `mgmt.ntp-absent`

- **Stage:** management-plane
- **Severity:** `blocking` (accurate time is required for log correlation, security event analysis, and certificate validation)
- **Depends on:** `mgmt.dns-absent` (if using domain names for NTP servers), `mgmt.default-route-absent` (the device must be able to reach the servers)
- **Lockout risk:** `false`
- **Evidence:** `show configuration system ntp` returns no configured NTP servers
- **Proposal:**

  ```text
  set system processes ntp enable
  set system ntp server 0.pool.ntp.org
  set system ntp server 1.pool.ntp.org
  ```

  Or, using IP addresses:

  ```text
  set system processes ntp enable
  set system ntp server 216.239.35.0
  set system ntp server 216.239.35.4
  ```

  Configure at least two NTP servers for redundancy. If DNS is configured, domain names can be used instead of IP addresses.

  **This gap is absent configuration only.** A device that already has servers configured but is not synchronizing is **not** `mgmt.ntp-absent`, and must not be "fixed" by adding public pool servers on top of an enterprise NTP configuration — that changes the time source instead of repairing the path to it. Synchronization failure on a configured device is a Stage 2 verification failure; work it through "NTP configured but never synchronizes" below.

  When the device sources NTP from a specific management identity — a loopback, or a revenue interface rather than `fxp0` — add `set system ntp source-address <address>` so the servers reply to an address the device can actually receive on.

  **Source:** Juniper Networks, "NTP Configuration" (Junos OS Time Management), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/time-mgmt/topics/example/ntp-configuration.html

  **Additional source:** Juniper Networks, "server (NTP)" (Junos OS CLI Reference), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/server-edit-system-ntp.html

  The documentation states: "To configure NTP, use the `set server` command with either a name or IP-address at the [edit system ntp] hierarchy level."

#### `set system processes ntp enable` — the hidden statement

`[edit system processes]` is hidden from CLI completion. `set system processes ntp enable` does not tab-complete and does not appear in `?` output, which is exactly why it gets omitted — but it is a valid, committable statement, and it is what makes the NTP daemon's enabled state explicit and auditable in the configuration rather than implicit.

**Validated on hardware and on vSRX, 2026-08-27** (`docs/skill-tests/2026-08-27-srx-ntp-process-enable-live-validation.md`): commit-check accepted `set system processes ntp enable` on SRX345 hardware running Junos 24.2R2-S5.3 and on vSRX 24.4R1.9, and accepted the opposing `set system processes ntp disable` on vSRX 26.2R1.7, whose diff replaced `ntp enable;` with `ntp disable;`. So the schema carries both values across 24.2 through 26.2, and `disable` is a real configured state rather than unrecognized syntax.

**What that run does not establish [inferred]:** no activating write was performed on any device, so the *runtime* effect — that `disable` actually suppresses `ntpd` — is inferred from the statement's semantics, not measured. Treat `disable` as a fault to correct, but confirm on the device with `show system processes extensive | match " ntpd"` rather than reporting the daemon down from the configuration alone.

Read the configured state as follows:

| Configured state | Meaning | Action |
|---|---|---|
| `set system processes ntp enable` present | Daemon explicitly enabled | Correct state — leave it |
| Statement absent | **Not** the same as disabled | Add it for explicitness, but do not report NTP broken on this basis alone |
| `set system processes ntp disable` present | Daemon explicitly suppressed (runtime effect inferred, not measured) | Replace with `enable`, and confirm `ntpd` state on the device |

**Absence is not a failed check.** On Junos 24.2R2-S5.3 (SRX345 hardware) and 24.4R1.9 (vSRX), devices carrying no `system processes` configuration at all were running `ntpd` and were synchronized to a `*` peer at `reach 377` with sub-millisecond offset. A blanket "Junos 24 and later will not synchronize without this statement" did not reproduce on the tested devices, so this skill does not gate on the statement's presence — it gates on `show ntp associations`. Every 25.4R1.12 and 26.2R1.7 device in the surveyed fleet already carried the statement, so the counterfactual could not be tested on those releases; on a 25.4-or-later device that will not synchronize with reachability already proven, adding this statement is the first thing to try.

**Enable NTP in its own commit.** First synchronization can step the clock, and a `commit confirmed` rollback deadline is wall-clock. See `references/write-safety.md` — the hazard is documented there and observed on hardware.

#### NTP configured but never synchronizes

`show ntp associations` showing every peer at `.INIT.` with `reach 0`, alongside `show system uptime` reporting `Time Source: LOCAL CLOCK`, means no NTP packet has ever completed a round trip. Work the path before suspecting the daemon — in every observed case in the 2026-08-27 survey the cause was reachability, not configuration:

1. **Route.** `show route <ntp-server>`. Three lab devices returned no route at all to their configured servers, having no default route present. That is `mgmt.default-route-absent`, not an NTP fault, and it must be closed first.
2. **Reachability.** `ping <ntp-server>`. `ping: sendto: No route to host` confirms the same condition.
3. **Return path.** UDP/123 must survive in both directions. When the device sources NTP from a loopback behind a transit firewall performing source NAT, that loopback prefix must appear in the NAT **source** match. The NTP servers' own addresses are destinations and do not belong in a source-address match — a frequent misconfiguration that silently breaks only the return path.
4. **Host-inbound-traffic.** The zone carrying the NTP path must accept the traffic; see `references/stages/interfaces-and-zones.md`.
5. **Daemon.** `show system processes extensive | match " ntpd"`. Only when `ntpd` is genuinely absent, or `set system processes ntp disable` is present in the configuration, is the process statement itself the fault.

#### Why this gap is `blocking` for downstream log management

A device whose clock is skewed still completes mTLS to a log collector and still has its payloads acknowledged, so every transport-level check passes while the logs never surface in the GUI. This has been observed in a live Security Director On-Prem deployment: several SRXs ran roughly 375 s behind, their streams connected and were acknowledged, and their traffic logs were simply absent until NTP was corrected and fresh traffic was generated. Prove synchronization here, in Stage 2, before any device is onboarded to Security Director Cloud or Security Director On-Prem — see `sd-onprem-proxmox-deploy` §4a and `srx-syslog-logging`.

### `mgmt.timezone-unset`

- **Stage:** management-plane
- **Severity:** `advisory` (NTP provides UTC; local timezone is a display preference)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `false`
- **Evidence:** `show configuration system time-zone` returns no configured time zone, or returns a default (often UTC)
- **Proposal:**

  ```text
  set system time-zone America/New_York
  ```

  Replace `America/New_York` with the appropriate IANA time zone identifier for the device's location. Common examples: `America/Los_Angeles`, `Europe/London`, `Asia/Tokyo`.

  **Status:** UNVERIFIED. The exact configuration hierarchy and accepted time zone identifiers have not been verified against current Junos OS documentation. This is a common configuration pattern, but platform-specific behavior should be confirmed.

### `mgmt.ssh-reachable`

- **Stage:** management-plane
- **Severity:** `blocking` (confirms the management path is working before factory-default removal)
- **Depends on:** `access.ssh-disabled`, `mgmt.mgmt-interface-unconfigured` (or equivalent gap establishing the management address)
- **Lockout risk:** `false` (this gap represents successful verification, not a configuration change)
- **Evidence:** SSH session to the management interface address succeeds
- **Proposal:**

  This is a verification-only gap. No configuration change is proposed. The operator or skill verifies SSH reachability by connecting to the management interface:

  ```text
  ssh admin@<mgmt-interface-address>
  ```

  If the connection succeeds and authentication works, this gap is closed. If the connection fails, diagnose and resolve before proceeding with lockout-risk stages.

  Possible causes of failure:
  - Management interface is not configured or has no IP address
  - No route from the operator's network to the management address
  - Firewall or host-inbound-traffic rules block SSH
  - SSH service is disabled

### `mgmt.mgmt-interface-unconfigured`

- **Stage:** management-plane
- **Severity:** `blocking`
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `true` (changing interface addressing can sever the current session)
- **Evidence:** The chosen management interface (fxp0 or a revenue port) has no configured IP address, or the address is unreachable
- **Proposal:**

  For **fxp0** (if present and chosen as the management interface):

  ```text
  set interfaces fxp0 unit 0 family inet address <management-ip>/<prefix-length>
  ```

  Example:

  ```text
  set interfaces fxp0 unit 0 family inet address 192.168.1.10/24
  ```

  For a **revenue port** (if fxp0 is not present or a revenue port is chosen):

  ```text
  set interfaces <interface-name> unit 0 family inet address <management-ip>/<prefix-length>
  set security zones security-zone mgmt interfaces <interface-name>.0 host-inbound-traffic system-services ssh
  set security zones security-zone mgmt interfaces <interface-name>.0 host-inbound-traffic system-services https
  set security zones security-zone mgmt interfaces <interface-name>.0 host-inbound-traffic system-services netconf
  ```

  Example for ge-0/0/0 as management interface:

  ```text
  set interfaces ge-0/0/0 unit 0 family inet address 10.1.1.10/24
  set security zones security-zone mgmt interfaces ge-0/0/0.0 host-inbound-traffic system-services ssh
  set security zones security-zone mgmt interfaces ge-0/0/0.0 host-inbound-traffic system-services https
  set security zones security-zone mgmt interfaces ge-0/0/0.0 host-inbound-traffic system-services netconf
  ```

  **Lockout-risk mitigation:** Apply via `commit confirmed 3`, verify SSH reachability from the new address before the timer expires, then issue the confirming commit. If verification fails, the automatic rollback restores the previous configuration.

  **Status:** UNVERIFIED. The exact interface naming conventions and zone configuration hierarchy are commonly used patterns, but platform-specific syntax and options should be verified against current Junos OS documentation for the target platform (SRX300/400 Branch series).

### `mgmt.wan-static`

- **Stage:** management-plane
- **Severity:** `advisory` (WAN addressing may be DHCP, static, or PPPoE depending on ISP requirements)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `true` (changing WAN addressing can break internet connectivity and remote management)
- **Evidence:** The WAN interface (typically ge-0/0/0 on Branch platforms) is configured as a DHCP client, but the deployment requires static addressing
- **Proposal:**

  ```text
  delete interfaces ge-0/0/0 unit 0 family inet dhcp
  set interfaces ge-0/0/0 unit 0 family inet address <ISP-assigned-IP>/<prefix-length>
  set routing-options static route 0.0.0.0/0 next-hop <ISP-gateway-IP>
  ```

  Example:

  ```text
  delete interfaces ge-0/0/0 unit 0 family inet dhcp
  set interfaces ge-0/0/0 unit 0 family inet address 203.0.113.10/30
  set routing-options static route 0.0.0.0/0 next-hop 203.0.113.9
  ```

  Replace `<ISP-assigned-IP>`, `<prefix-length>`, and `<ISP-gateway-IP>` with values provided by the ISP.

  **Lockout-risk mitigation:** If the operator is currently connected via a path that uses the WAN interface, changing its addressing can break that path. Apply via `commit confirmed 5`, verify reachability (ping the gateway, establish a new SSH session from the internet if that is the intended path), then confirm. If the ISP requires DHCP, mark this gap as `adopted` and leave the DHCP client configuration as-is.

  **Status:** UNVERIFIED. The interface name `ge-0/0/0` and the DHCP/static configuration syntax are common patterns for SRX Branch platforms, but exact syntax and behavior should be verified against current Junos OS documentation.

### `mgmt.default-route-absent`

- **Stage:** management-plane
- **Severity:** `blocking` (without a default route, the device cannot reach external services like NTP or logging destinations)
- **Depends on:** `mgmt.mgmt-interface-unconfigured`, `mgmt.wan-static` (if applicable)
- **Lockout risk:** `false` (adding a default route does not remove an existing path; changing or removing one is lockout-risk)
- **Evidence:** `show route 0.0.0.0/0` returns no default route, or returns a route that is inactive
- **Proposal:**

  ```text
  set routing-options static route 0.0.0.0/0 next-hop <gateway-ip>
  ```

  Replace `<gateway-ip>` with the IP address of the next-hop gateway (typically the ISP gateway on the WAN interface, or the management network gateway if using fxp0).

  Example for WAN gateway:

  ```text
  set routing-options static route 0.0.0.0/0 next-hop 203.0.113.1
  ```

  Example for management network gateway (if fxp0 is in use and needs a dedicated route):

  ```text
  set routing-options static route 0.0.0.0/0 next-hop 192.168.1.1
  ```

  If the WAN interface is a DHCP client, the DHCP server typically provides a default route automatically. Verify with `show route 0.0.0.0/0` before proposing a static default route.

  **Status:** UNVERIFIED. The static route syntax is a common pattern, but platform-specific behavior (e.g., how DHCP-learned routes interact with static routes, routing-instance requirements for fxp0) should be verified.

### `mgmt.external-dhcp-configured`

- **Stage:** management-plane
- **Severity:** `advisory` (required only if replacing factory-default IRB DHCP server with external DHCP)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `true` (removing the device's DHCP server before the external one is operational disconnects all LAN clients)
- **Evidence:** The deployment requires an external DHCP server instead of the device's built-in DHCP service, but the external server is not yet configured or reachable
- **Proposal:**

  **This gap performs the atomic cutover from the local DHCP server to external DHCP relay.** Both the relay configuration and the removal of the local DHCP server must occur in the same confirmed commit. Configuring the relay without removing the local server allows clients to continue using the local server, giving a false positive on lease tests; removing the server without the relay being functional disconnects all clients.

  Configure DHCP relay and remove the local DHCP server in one commit:

  ```text
  set forwarding-options dhcp-relay server-group external-dhcp <external-dhcp-server-ip>
  set forwarding-options dhcp-relay group dhcp-relay-group active-server-group external-dhcp
  set forwarding-options dhcp-relay group dhcp-relay-group interface <client-facing-interface>
  delete system services dhcp-local-server group <group-name> interface <client-facing-interface>
  delete access address-assignment pool <pool-name>
  ```

  Example for external DHCP server at 10.1.1.100 serving clients on irb.0, removing the factory-default 192.168.2.0/24 pool:

  ```text
  set forwarding-options dhcp-relay server-group external-dhcp 10.1.1.100
  set forwarding-options dhcp-relay group dhcp-relay-group active-server-group external-dhcp
  set forwarding-options dhcp-relay group dhcp-relay-group interface irb.0
  delete system services dhcp-local-server group jdhcp-group interface irb.0
  delete access address-assignment pool junosDHCPPool2
  ```

  **Verification before confirming the commit:** After applying via `commit confirmed <minutes>` (see `references/write-safety.md` for timer default), test that a client can obtain a lease from the external server through the relay. If the lease test succeeds, confirm the commit. If it fails, do not confirm — the automatic rollback will restore the local DHCP server configuration.

  **What rollback restores:** This commit removes the local DHCP server and adds DHCP relay. If the confirming commit does not arrive before the timer expires, rollback deletes the relay configuration and restores the local DHCP server pool, returning clients to local DHCP service.

  **Cross-reference to `factory.irb-dhcp-server`:** The `factory.irb-dhcp-server` gap in `references/factory-default-branch.md` documents the factory-default DHCP server as an element that can be adopted or removed. Assessment should record one of three outcomes for `factory.irb-dhcp-server`: (1) if the operator closes `mgmt.external-dhcp-configured` (adopts DHCP relay), record `factory.irb-dhcp-server` as handled by removal; (2) if the operator closes `mgmt.static-assignments` (moves to static addressing), record `factory.irb-dhcp-server` as handled by removal; (3) if the operator keeps the local DHCP server (adopts the factory default), record `factory.irb-dhcp-server` as adopted and leave both `mgmt.external-dhcp-configured` and `mgmt.static-assignments` open.

  **Status:** PARTIALLY VERIFIED. The *local DHCP server* hierarchy is hardware-verified on SRX345 (Junos 21.2R3-S6.11, 2026-08-25): the factory default uses `access address-assignment pool junosDHCPPool1|junosDHCPPool2` together with `system services dhcp-local-server group jdhcp-group { interface fxp0.0; interface irb.0; }`. The legacy `system services dhcp pool <subnet>` hierarchy **does not exist** on this platform, and a `delete` against it is a silent no-op — it does not error loudly, so a gap written against it would report closed while the DHCP server kept running. Note also that `jdhcp-group` serves **two** interfaces; removing only `irb.0` deliberately leaves the `fxp0.0` server intact.

  The *DHCP relay* half remains UNVERIFIED: relay syntax, server-group options, and interface reference format should still be checked against current Junos OS documentation for the target platform.

### `mgmt.static-assignments`

- **Stage:** management-plane
- **Severity:** `advisory` (required only if replacing factory-default IRB DHCP server with static addressing for LAN clients)
- **Depends on:** All `access.*` gaps closed
- **Lockout risk:** `true` (removing the DHCP server before clients are reconfigured with static addresses disconnects all LAN clients)
- **Evidence:** The deployment requires static IP assignments for LAN clients instead of DHCP, but clients are not yet reconfigured
- **Proposal:**

  This gap is a **coordination point**, not a device configuration change. The proposal is:

  1. Document the static IP assignment plan for all LAN clients (addresses, subnet mask, gateway, DNS servers).
  2. Reconfigure each client with its assigned static address **before** removing the device's DHCP service.
  3. Verify each client can reach the gateway and resolve DNS.
  4. Only after all clients are verified on static addressing, proceed with closing `factory.irb-dhcp-server` to remove the device's DHCP service.

  **Example static assignment plan:**

  | Client Hostname | MAC Address       | Static IP     | Gateway     | DNS             |
  |-----------------|-------------------|---------------|-------------|-----------------|
  | workstation-1   | 00:11:22:33:44:55 | 192.168.2.10  | 192.168.2.1 | 8.8.8.8, 8.8.4.4 |
  | workstation-2   | 00:11:22:33:44:66 | 192.168.2.11  | 192.168.2.1 | 8.8.8.8, 8.8.4.4 |
  | server-1        | 00:11:22:33:44:77 | 192.168.2.100 | 192.168.2.1 | 8.8.8.8, 8.8.4.4 |

  This gap closes when the operator confirms all clients are reconfigured and verified.

  **Lockout-risk mitigation:** This gap itself carries no device configuration change, so its lockout risk is indirect — it gates the `factory.irb-dhcp-server` removal, which is the actual lockout-risk change. Closing this gap is a confirmation that the precondition (clients reconfigured) is met.

## Verification

After this stage closes, verify:

1. **Hostname and domain configured:**

   ```text
   show configuration system host-name
   show configuration system domain-name
   ```

   Expect the configured values.

2. **DNS resolution works:**

   ```text
   show configuration system name-server
   ping pool.ntp.org
   ```

   Expect the configured DNS servers in the configuration, and successful DNS resolution of `pool.ntp.org` (or another known domain).

3. **NTP synchronized — `show ntp associations` is authoritative:**

   ```text
   show configuration system processes | display set | match ntp
   show ntp associations no-resolve
   show system processes extensive | match " ntpd"
   show system uptime | match "Current time|Time Source"
   show ntp status
   ```

   | Evidence | Role | Expected |
   |---|---|---|
   | `show ntp associations` | **the gate** | at least one peer prefixed `*`, `reach` non-zero (`377` is fully reached), `offset` within tolerance (typically < 1000 ms) |
   | `show system processes extensive` | supporting | `ntpd` running |
   | `show configuration system processes` | supporting | `ntp enable` present, and `ntp disable` **not** present |
   | `show system uptime` | corroborating | `Time Source: NTP CLOCK` |
   | `show ntp status` | corroborating | `leap_none`, `sync_ntp`; `clock_sync` once settled |

   **Pass or fail on the associations table, not on the status word.** `sync_ntp` appears alongside `no_sys_peer` — no peer currently selected — so it is not by itself proof of synchronization; and a device reporting `no_sys_peer` may show a `*` peer at `reach 377` moments later, so requiring `clock_sync` would fail a healthy device. `Time Source: NTP CLOCK` appears in both states and cannot settle it. A `*` peer with non-zero reach and an acceptable offset is a pass; no `*` peer, or `reach 0`, is a fail.

4. **Management interface reachable:**

   From the operator's management network:

   ```text
   ping <mgmt-interface-address>
   ssh admin@<mgmt-interface-address>
   ```

   Expect successful ping and SSH connection.

5. **Default route present and active:**

   ```text
   show route 0.0.0.0/0
   ```

   Expect at least one active default route.

All `mgmt.*` gaps are now closed. The factory-default removal stage (if applicable) may proceed.
