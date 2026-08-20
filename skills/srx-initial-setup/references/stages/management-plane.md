# Stage 2 — Management Plane

This stage establishes system identity, time synchronization, name resolution, and management network addressing. These are prerequisites for later stages that depend on accurate timestamps, reachable logging destinations, and stable management connectivity.

## What this stage establishes

- **System identity:** Hostname and domain name configured for identification in logs, prompts, and DNS.
- **Time synchronization:** NTP configured and operational, providing accurate timestamps for logs, security event correlation, and troubleshooting.
- **Name resolution:** DNS name servers configured, enabling the device to resolve hostnames for logging, NTP (if using domain names), and external services.
- **Management addressing:** The management interface has a routable address, either static or via DHCP with a confirmed lease, and is reachable from the operator's management network.

All `mgmt.*` gaps are `blocking` for the `factory.*` stage. Factory-default removal is a lockout-risk change; the replacement management path must be established and verified before factory elements are removed.

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
- **Depends on:** `mgmt.dns-absent` (if using domain names for NTP servers)
- **Lockout risk:** `false`
- **Evidence:** `show configuration system ntp` returns no configured NTP servers
- **Proposal:**

  ```text
  set system ntp server 0.pool.ntp.org
  set system ntp server 1.pool.ntp.org
  ```

  Or, using IP addresses:

  ```text
  set system ntp server 216.239.35.0
  set system ntp server 216.239.35.4
  ```

  Configure at least two NTP servers for redundancy. If DNS is configured, domain names can be used instead of IP addresses.

  **Source:** Juniper Networks, "NTP Configuration" (Junos OS Time Management), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/time-mgmt/topics/example/ntp-configuration.html

  **Additional source:** Juniper Networks, "server (NTP)" (Junos OS CLI Reference), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/server-edit-system-ntp.html

  The documentation states: "To configure NTP, use the `set server` command with either a name or IP-address at the [edit system ntp] hierarchy level."

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
  delete system services dhcp pool <subnet>
  ```

  Example for external DHCP server at 10.1.1.100 serving clients on irb.0, removing the factory-default 192.168.2.0/24 pool:

  ```text
  set forwarding-options dhcp-relay server-group external-dhcp 10.1.1.100
  set forwarding-options dhcp-relay group dhcp-relay-group active-server-group external-dhcp
  set forwarding-options dhcp-relay group dhcp-relay-group interface irb.0
  delete system services dhcp pool 192.168.2.0/24
  ```

  **Verification before confirming the commit:** After applying via `commit confirmed <minutes>` (see `references/write-safety.md` for timer default), test that a client can obtain a lease from the external server through the relay. If the lease test succeeds, confirm the commit. If it fails, do not confirm — the automatic rollback will restore the local DHCP server configuration.

  **What rollback restores:** This commit removes the local DHCP server and adds DHCP relay. If the confirming commit does not arrive before the timer expires, rollback deletes the relay configuration and restores the local DHCP server pool, returning clients to local DHCP service.

  **Cross-reference to `factory.irb-dhcp-server`:** The `factory.irb-dhcp-server` gap in `references/factory-default-branch.md` documents the factory-default DHCP server as an element that can be adopted or removed. If this gap (`mgmt.external-dhcp-configured`) is closed — meaning the local server has been replaced with external DHCP relay — then `factory.irb-dhcp-server` is already handled and should be marked as such during assessment. Conversely, if the operator chooses to keep the local DHCP server (adopt the factory default), this gap remains open and `factory.irb-dhcp-server` documents that adoption decision.

  **Status:** UNVERIFIED. The DHCP relay syntax and configuration hierarchy are common patterns for Junos platforms, but exact syntax, server-group configuration options, and interface reference format should be verified against current Junos OS documentation for the target platform.

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

3. **NTP synchronized:**

   ```text
   show ntp associations
   show ntp status
   ```

   Expect at least one NTP server showing `*` (synchronized) and the system clock offset within acceptable range (typically < 1000ms).

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
