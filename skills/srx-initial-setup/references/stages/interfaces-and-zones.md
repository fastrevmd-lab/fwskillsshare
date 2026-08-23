# Stage 3 — Interfaces and Zones

This stage establishes network segmentation boundaries, interface addressing, and host-inbound-traffic rules that control which services can reach the device itself. Of all stages in this skill, this one carries the highest lockout risk because changing the interface currently carrying management traffic or its zone membership can sever the active session.

## What this stage establishes

- **Security zones:** Logical groupings of interfaces with common security requirements. Zones define trust boundaries and are prerequisites for security policies.
- **Interface addressing:** Layer 3 addresses on physical and logical interfaces, enabling routing and reachability.
- **Zone-to-interface assignment:** Binding interfaces to zones, which moves interfaces out of the null zone where they cannot pass traffic.
- **Host-inbound-traffic rules:** Explicit permission for system services (SSH, HTTPS, ping, NTP) and routing protocols (OSPF, BGP) to reach the device from interfaces in each zone.

All `zone.*` gaps are `blocking` for later stages. Security policies (Stage 5) require zones to exist before rules can reference them. Screens (Stage 4) bind to zones, not interfaces directly.

## Why this stage is the lockout stage

Changing zone membership or host-inbound-traffic settings for the interface currently carrying management traffic is the most common way a correctly-addressed interface becomes unreachable.

**All lockout-risk gaps in this stage follow the gate protocol in `references/write-safety.md`.** That file is the authority for commit-confirmed mechanics, timer selection, rollback points, and the requirement to state the operator's recovery path before proposing a lockout-risk change. Gap entries below specify only the verification commands and success criteria unique to each gap.

### What host-inbound-traffic controls

Host-inbound-traffic regulates traffic destined **to the device itself** from directly connected systems. This includes SSH, HTTPS, ping, SNMP, routing protocols, and other services that terminate on the Routing Engine.

**Source:** Juniper Networks, "Security Zones" (Junos OS Security Policies), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-zone-configuration.html

The documentation states: "You must enable all expected host-inbound traffic. Inbound traffic destined to this device is dropped by default."

**Additional source:** Juniper Networks, "system-services (Security Zones Host Inbound Traffic)" (Junos OS CLI Reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-system-service-zone-host-inbound-traffic.html

The CLI reference confirms: "All system services disabled" by default.

### Why omitting it causes unreachability

An interface can have a correct IP address, be assigned to a security zone, and have routing working — but if `host-inbound-traffic system-services ssh` is not configured for that zone or interface, SSH connections to the device **through that interface** will be dropped. The SSH daemon is running, the routing is correct, but the security zone blocks the traffic before it reaches the service.

**Common scenario:** An operator configures a new management zone, moves the management interface into it, and commits without adding `host-inbound-traffic system-services ssh` to the new zone. The commit succeeds, the interface is reachable via ping (if ICMP was enabled separately), but SSH is refused. If the operator was connected via that interface and did not use `commit confirmed`, they are locked out.

## Ordering within the stage

**Critical rule:** Establish and verify the replacement management path **before** removing or changing the old one.

If the current management access is through a factory-default zone (e.g., trust zone on Branch platforms) and the target configuration uses a different zone (e.g., a dedicated mgmt zone), the safe sequence is:

1. Create the new zone with `host-inbound-traffic system-services ssh` (and any other required services).
2. If using a different interface, configure its addressing and assign it to the new zone.
3. Apply the change per the gate protocol in `write-safety.md`.
4. **Verify** SSH reachability through the new interface/zone by establishing a **new** SSH session from the management network. Do not assume the existing session proves anything — it may survive because it is already established.
5. Only after the new path is confirmed working: remove the old zone's `host-inbound-traffic` settings or deactivate the old interface (as a separate, later change).

If the new and old management paths use the same physical interface but different zones, the same principle applies: add `host-inbound-traffic` to the new zone, move the interface, verify, confirm, then clean up the old zone in a separate change.

**Never remove the active management path in the same commit that establishes the replacement** unless both paths are in the same zone and only the interface addressing is changing.

## Gaps

### `zone.trust-absent`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking`
- **Depends on:** All `mgmt.*` gaps closed
- **Lockout risk:** `false` (creating a zone does not change existing traffic flow; assigning interfaces to it is the lockout-risk step)
- **Evidence:** `show configuration security zones security-zone trust` returns no configuration
- **Proposal:**

  ```text
  set security zones security-zone trust
  ```

  The trust zone is a standard naming convention for the internal/LAN side of a Branch deployment. On Branch platforms, this zone name ships as factory default; on bare devices, it does not exist and must be created.

  Creating the zone itself carries no lockout risk. The risk arises when interfaces are assigned to it or when `host-inbound-traffic` is configured (or omitted).

  **Source:** Juniper Networks, "Security Zones" (Junos OS Security Policies), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-zone-configuration.html

### `zone.untrust-absent`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking`
- **Depends on:** All `mgmt.*` gaps closed
- **Lockout risk:** `false`
- **Evidence:** `show configuration security zones security-zone untrust` returns no configuration
- **Proposal:**

  ```text
  set security zones security-zone untrust
  ```

  The untrust zone is a standard naming convention for the external/internet-facing side of a Branch deployment. On Branch platforms, this zone name ships as factory default; on bare devices, it does not exist and must be created.

  **Source:** Same as `zone.trust-absent`.

### `zone.mgmt-absent`

- **Stage:** interfaces-and-zones
- **Severity:** `advisory` (required only if out-of-band management is separated from trust)
- **Depends on:** All `mgmt.*` gaps closed
- **Lockout risk:** `false` (creating the zone does not change traffic flow)
- **Evidence:** `show configuration security zones security-zone mgmt` returns no configuration, and the deployment requires a dedicated management zone separate from trust
- **Proposal:**

  ```text
  set security zones security-zone mgmt
  ```

  A dedicated management zone is common when fxp0 (if present) or a dedicated revenue port is used exclusively for device management, isolated from user and server traffic.

  If management traffic shares the trust zone (as in the Branch factory default), this gap is not applicable.

  **Source:** Same as `zone.trust-absent`.

### `zone.trust-host-inbound-missing`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking`
- **Depends on:** `zone.trust-absent`
- **Lockout risk:** `true` (if trust carries current management traffic and this is removed or omitted, SSH access is lost)
- **Evidence:** `show configuration security zones security-zone trust interfaces` reports one or more interfaces, but `show configuration security zones security-zone trust host-inbound-traffic` does not list required services
- **Proposal:**

  ```text
  set security zones security-zone trust host-inbound-traffic system-services ssh
  set security zones security-zone trust host-inbound-traffic system-services https
  set security zones security-zone trust host-inbound-traffic system-services ping
  set security zones security-zone trust host-inbound-traffic protocols all
  ```

  This example enables SSH, HTTPS, and ping for management, plus all routing protocols. Adjust based on deployment requirements.

  **Reasoning:** The trust zone typically contains the LAN and may be the path the operator uses to reach the device. If SSH is not explicitly enabled here, the interface may be reachable via ping but SSH will be refused.

  **Verification:** If the operator is currently connected via an interface in the trust zone, verify SSH still works by establishing a new session after applying the change. If the operator is connected via another zone (e.g., fxp0 in a separate mgmt zone), this change carries no lockout risk for them.

  **Source:** Juniper Networks, "system-services (Security Zones Host Inbound Traffic)" (Junos OS CLI Reference), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/statement/security-edit-system-service-zone-host-inbound-traffic.html

### `zone.untrust-host-inbound-excessive`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking` (security risk; must resolve before production)
- **Depends on:** `zone.untrust-absent`, `factory.untrust-system-services` (if applicable)
- **Lockout risk:** `false` (removing permissive inbound rules does not break outbound connectivity or established sessions)
- **Evidence:** `show configuration security zones security-zone untrust host-inbound-traffic` reports system-services such as SSH, HTTPS, DHCP, or TFTP enabled from untrust
- **Proposal:**

  ```text
  delete security zones security-zone untrust host-inbound-traffic system-services ssh
  delete security zones security-zone untrust host-inbound-traffic system-services https
  delete security zones security-zone untrust host-inbound-traffic system-services dhcp
  delete security zones security-zone untrust host-inbound-traffic system-services tftp
  ```

  **Reasoning:** Allowing SSH and HTTPS from the internet-facing untrust zone exposes management interfaces to external attackers. Management access should be restricted to trusted networks (trust or mgmt zones).

  If remote management from the internet is required, use a VPN tunnel with the management interface in a VPN zone, not unrestricted access from untrust.

  **Source:** This is a security hardening principle documented in Branch factory-default references. The syntax for deletion is the inverse of the creation syntax from the CLI reference above.

### `zone.mgmt-host-inbound-missing`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking` (if mgmt zone exists and carries management traffic)
- **Depends on:** `zone.mgmt-absent`
- **Lockout risk:** `true` (if the operator is connected via the mgmt zone or will be after interface reassignment)
- **Evidence:** `zone.mgmt-absent` is closed, and interfaces are assigned to mgmt zone, but `show configuration security zones security-zone mgmt host-inbound-traffic` does not list required services
- **Proposal:**

  ```text
  set security zones security-zone mgmt host-inbound-traffic system-services ssh
  set security zones security-zone mgmt host-inbound-traffic system-services https
  set security zones security-zone mgmt host-inbound-traffic system-services ping
  set security zones security-zone mgmt host-inbound-traffic system-services netconf
  ```

  **Reasoning:** The mgmt zone exists specifically for device management. SSH, HTTPS, and optionally NETCONF (for API-based management) must be enabled.

  **Verification:** If the operator is currently connected via another zone and this gap is being closed in preparation for moving the management interface to the mgmt zone, apply this configuration **before** moving the interface. Establish a **new** SSH session through the mgmt zone (if the interface is already there or routable) to verify it works.

  **Source:** Same as `zone.trust-host-inbound-missing`.

### `zone.trust-interface-unassigned`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking`
- **Depends on:** `zone.trust-absent`, `zone.trust-host-inbound-missing`
- **Lockout risk:** `true` (if the interface currently carrying management traffic is being moved to trust zone from another zone, and the dependencies are not correctly satisfied first)
- **Evidence:** LAN-facing interfaces exist and are configured with addresses, but `show configuration security zones security-zone trust interfaces` reports no interfaces assigned
- **Proposal:**

  For a Branch deployment where ge-0/0/1 through ge-0/0/7 are LAN ports:

  ```text
  set security zones security-zone trust interfaces ge-0/0/1.0
  set security zones security-zone trust interfaces ge-0/0/2.0
  set security zones security-zone trust interfaces ge-0/0/3.0
  set security zones security-zone trust interfaces ge-0/0/4.0
  set security zones security-zone trust interfaces ge-0/0/5.0
  set security zones security-zone trust interfaces ge-0/0/6.0
  set security zones security-zone trust interfaces ge-0/0/7.0
  ```

  Or, if using an IRB interface for a VLAN:

  ```text
  set security zones security-zone trust interfaces irb.0
  ```

  Replace interface names with the actual LAN-facing interfaces for the platform.

  **Prerequisites and verification:** If the operator is currently connected via one of these interfaces **and** that interface is currently in a different zone (e.g., a factory-default trust zone being replaced with a new trust zone, or moving from mgmt to trust):

  1. Ensure `zone.trust-host-inbound-missing` is closed (SSH is enabled in the destination zone) before applying this gap.
  2. After applying, verify SSH reachability through the interface in its new zone by establishing a **new** session.

  If the operator is connected via a different interface (e.g., fxp0 in mgmt zone), this change carries no lockout risk for their current session.

  **Source:** Juniper Networks, "Security Zones" (Junos OS Security Policies), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-zone-configuration.html

  The documentation states: "By default, interfaces are in the null zone. The interfaces will not pass traffic until they have been assigned to a zone."

### `zone.untrust-interface-unassigned`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking`
- **Depends on:** `zone.untrust-absent`, `zone.untrust-host-inbound-excessive` (if applicable)
- **Lockout risk:** `false` (the WAN/untrust interface typically does not carry management traffic; if it does, the operator is violating the security model documented in `factory.untrust-system-services`)
- **Evidence:** The WAN interface (typically ge-0/0/0 on Branch platforms) is configured with an address, but `show configuration security zones security-zone untrust interfaces` reports no interfaces assigned
- **Proposal:**

  ```text
  set security zones security-zone untrust interfaces ge-0/0/0.0
  ```

  Replace `ge-0/0/0` with the actual WAN interface for the platform.

  **Reasoning:** The untrust zone typically contains the internet-facing WAN interface. On Branch platforms, this is ge-0/0/0 by default. Assigning it to the untrust zone is required for security policies to apply to traffic crossing the trust-to-untrust boundary.

  **Source:** Same as `zone.trust-interface-unassigned`.

### `zone.mgmt-interface-unassigned`

- **Stage:** interfaces-and-zones
- **Severity:** `blocking` (if mgmt zone exists and is intended to carry management traffic)
- **Depends on:** `zone.mgmt-absent`, `zone.mgmt-host-inbound-missing`
- **Lockout risk:** `true` (if the interface currently carrying management traffic is being moved to the mgmt zone)
- **Evidence:** The mgmt zone exists, and a dedicated management interface (fxp0 or a revenue port) is configured but not assigned to the zone
- **Proposal:**

  For fxp0 (if present and used for management):

  ```text
  set security zones security-zone mgmt interfaces fxp0.0
  ```

  Or, for a revenue port dedicated to management:

  ```text
  set security zones security-zone mgmt interfaces ge-0/0/1.0
  ```

  **Prerequisites and verification:** This is the highest-risk gap in the entire skill if the operator is currently connected via the interface being reassigned.

  Before applying:
  1. Verify `zone.mgmt-host-inbound-missing` is closed (SSH is enabled in mgmt zone).
  2. Verify the interface has a configured address and is reachable via ping from the management network.
  3. Confirm out-of-band recovery access (console or alternate management interface) is available.

  After applying: **Immediately** establish a **new** SSH session to the device through the management interface's address. Do not rely on the existing session.

  **Source:** Same as `zone.trust-interface-unassigned`.

## Verification

After this stage closes, verify:

1. **All zones exist:**

   ```text
   show security zones
   ```

   Expect trust, untrust, and mgmt (if applicable) zones to appear.

2. **Interfaces assigned to zones:**

   ```text
   show security zones
   ```

   Expect each configured interface to appear under its intended zone. No production interfaces should remain in the null zone.

3. **Host-inbound-traffic configured correctly:**

   ```text
   show configuration security zones | display set | match host-inbound-traffic
   ```

   Expect SSH, HTTPS, and ping (at minimum) enabled for trust and mgmt zones. Expect untrust to have no management services enabled (or only those explicitly required and secured, such as IKE for VPN).

4. **Management access still works:**

   From the operator's management network:

   ```text
   ssh admin@<management-interface-address>
   ```

   Expect successful connection. If using fxp0 or a dedicated management interface, verify the address is reachable and SSH works.

5. **Zone-to-zone traffic flow prerequisites met:**

   Security policies (Stage 5) will reference these zones. Verify with:

   ```text
   show security zones
   ```

   Confirm the zones exist and have the expected interfaces.

All `zone.*` gaps are now closed. Stages 4 (screens) and 5 (baseline policy) may proceed.
