# Branch Factory-Default Configuration

Applies to **SRX300 and SRX400 Branch platforms only**. Campus and datacenter platforms (SRX1600, SRX4120, SRX4300, SRX4700, SRX5000 series) do **not** ship this configuration; on those, an entry state of `factory-default` means a different shipped state and this file does not apply.

## What ships on the device

**Source:** Juniper Networks, "Verify Default Branch Connectivity" and "Step 1: Verify and Secure Local Branch Connectivity" (Guided Setup: How to Configure and Operate Juniper SRX300 Line Firewalls), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/guided-setup/branch-srx-gs/step-1-p1-verify_defaults.html
URL: https://www.juniper.net/documentation/us/en/software/guided-setup/branch-srx-gs/topics/topic-map/step-1-verify_secure_local.html

Branch SRX devices ship with a plug-and-play configuration designed for immediate internet connectivity. The following elements are preconfigured:

### Security zones

Two security zones exist:

| Zone | Interfaces | Configuration |
|---|---|---|
| `untrust` | ge-0/0/0 (WAN interface) | DHCP client to obtain IP address from ISP |
| `trust` | All LAN ports | Full Layer 2 connectivity within VLAN `vlan-trust` |

### VLAN configuration

Two VLANs are preconfigured:

- **default VLAN** (ID 1) — Unassigned in factory configuration
- **vlan-trust** (ID 3) — Contains all LAN ports, sharing the 192.168.2.0/24 IP subnet

### DHCP service

An **Integrated Routing and Bridging (IRB)** interface functions as the DHCP server, automatically assigning addresses from the 192.168.2.0/24 pool to all LAN clients.

### Management interface (if present)

If the platform includes a dedicated out-of-band management interface (`fxp0`), it is configured as a DHCP server with IP address 192.168.1.1/24.

**Source:** Juniper Networks, "Configuring Junos OS on the SRX1500" (mentions fxp0 management interface configuration for platforms that have it), retrieved 2026-08-20.
URL: https://juniper.net/documentation/en_US/release-independent/junos/topics/topic-map/srx1500-configuring-junos.html

**Note:** Not all Branch platforms include fxp0. SRX300 series models vary by SKU; consult platform-specific hardware documentation.

### Security policies

The factory-default policies establish asymmetrical traffic flow:

- Traffic sent from any LAN port (trust zone) is **allowed** to the untrust zone
- Return traffic from untrust to trust is **permitted**
- Traffic that originates in the untrust zone is **blocked** from the trust zone
- **Source NAT** is applied to outbound trust-to-untrust traffic using the WAN interface IP

### System services

System services (HTTPS, DHCP, TFTP, SSH) are permitted from the untrust zone to the local host, allowing remote management from the WAN.

**Security concern:** This exposes management interfaces to the internet. In production deployments, these should be restricted to trusted management networks only.

### MAC address learning

The device automatically learns MAC addresses through DHCP discovery and populates its Ethernet switching table for Layer 2 forwarding decisions.

## Why removal is a lockout-risk change

The shipped configuration may be what is currently providing the operator's address. Removing it before the replacement management path is established and verified costs reachability.

**Lockout scenarios:**

1. **Operator connected via trust-zone LAN port**: Removing `vlan-trust` or the IRB DHCP server severs the operator's IP address. If the replacement management interface is not yet configured and reachable, access is lost.

2. **Operator connected via WAN (untrust)**: Removing the system-services allow-list from untrust blocks SSH before the replacement management access is confirmed working.

3. **Console-only access after premature removal**: If the factory defaults are removed without a tested replacement, the only recovery path is console access with manual configuration rebuild.

**Mitigation:** Every gap in this file carries `lockout_risk: true`. The protocol in `write-safety.md` mandates:

- Pre-commit reachability test of the replacement management path
- Commit with `commit confirmed <minutes>` — rollback is automatic if the operator loses connectivity
- Post-commit re-verification that management access still works
- Explicit confirmation to make the commit permanent

## Adopt or remove

Not all factory-default elements are harmful. The decision framework:

### Elements to **remove** in production

| Element | Reasoning | Gap id |
|---|---|---|
| System services allowed from untrust | Exposes SSH, HTTPS, DHCP, TFTP to the internet | `factory.untrust-system-services` |
| ge-0/0/0 as DHCP client | ISP-assigned address is unpredictable; static or PPPoE is preferred for routing and policy | `factory.wan-dhcp` |
| Default trust-to-untrust allow-any policy | Too permissive; replace with explicit application-aware policies | `factory.permissive-policy` |

### Elements to **adopt** or keep

| Element | Reasoning | Decision |
|---|---|---|
| `trust` and `untrust` zones | Standard naming; widely understood | Keep and build on them |
| Source NAT on trust-to-untrust | Required for internet access with private LAN addressing | Keep; it is correct as-is |
| IRB DHCP server on trust | Provides client addressing; only replace if static DHCP reservations or an external DHCP server is preferred | Adopt or replace based on deployment |
| vlan-trust Layer 2 domain | Puts all LAN ports in one broadcast domain; acceptable for small sites | Adopt for small sites; segment into multiple VLANs for larger deployments |

### Elements that are **deployment-specific**

| Element | Keep if… | Remove if… | Gap id |
|---|---|---|---|
| fxp0 management interface (if present) | Dedicated out-of-band management network exists | WAN is the only connectivity and fxp0 is unused | `factory.fxp0-unused` |
| IRB 192.168.2.0/24 subnet | No conflict with other site subnets | Subnet overlaps with another network in the enterprise | `factory.irb-subnet-conflict` |

The skill does not make this decision. It presents the elements, their purposes, and their risks. The operator chooses adopt or remove per element based on their deployment requirements.

## Gap entries

These gaps populate the `factory.*` namespace. All have `lockout_risk: true` and depend on the management-plane stage completing first.

### `factory.untrust-system-services`

- **Stage:** factory-default-removal
- **Severity:** `blocking` (security risk; must resolve before production)
- **Depends on:** `mgmt.ssh-reachable` (or equivalent management-plane gap confirming trusted access is established)
- **Lockout risk:** `true`
- **Evidence:** `show security zones untrust detail` reports `system-services` including SSH, HTTPS, DHCP, TFTP from untrust
- **Proposal:**
  ```text
  delete security zones security-zone untrust host-inbound-traffic system-services ssh
  delete security zones security-zone untrust host-inbound-traffic system-services https
  delete security zones security-zone untrust host-inbound-traffic system-services dhcp
  delete security zones security-zone untrust host-inbound-traffic system-services tftp
  ```
  Apply via `commit confirmed 3` after verifying trusted-network SSH access works.

### `factory.wan-dhcp`

- **Stage:** factory-default-removal
- **Severity:** `advisory` (functional, but unpredictable addressing complicates routing and policy)
- **Depends on:** `mgmt.wan-static` (a gap proposing static WAN configuration, if desired) or ISP's requirement for DHCP
- **Lockout risk:** `true` (if DHCP is replaced with static but the static config is wrong, WAN connectivity is lost)
- **Evidence:** `show configuration interfaces ge-0/0/0 unit 0 family inet` reports `dhcp`
- **Proposal:** Depends on ISP requirements. If static IP is available:
  ```text
  delete interfaces ge-0/0/0 unit 0 family inet dhcp
  set interfaces ge-0/0/0 unit 0 family inet address <ISP-assigned-IP>/<prefix>
  ```
  If ISP requires DHCP, mark this gap as `adopted` and leave the configuration as-is.

### `factory.permissive-policy`

- **Stage:** factory-default-removal
- **Severity:** `blocking` (too permissive; violates least-privilege)
- **Depends on:** `policy.explicit-outbound` (a gap proposing explicit application-aware policies)
- **Lockout risk:** `false` (policy change does not affect management-plane reachability if management access is in a separate zone)
- **Evidence:** `show security policies from-zone trust to-zone untrust` reports a default-permit or broad junos-defaults policy
- **Proposal:** Replace with explicit policies per required application. Example:
  ```text
  delete security policies from-zone trust to-zone untrust policy <factory-policy-name>
  set security policies from-zone trust to-zone untrust policy allow-http match source-address any destination-address any application junos-http
  set security policies from-zone trust to-zone untrust policy allow-http then permit
  set security policies from-zone trust to-zone untrust policy allow-https match source-address any destination-address any application junos-https
  set security policies from-zone trust to-zone untrust policy allow-https then permit
  set security policies from-zone trust to-zone untrust policy allow-dns match source-address any destination-address any application junos-dns-udp
  set security policies from-zone trust to-zone untrust policy allow-dns then permit
  ```
  Expand per deployment needs (NTP, ICMP, etc.). Use address objects instead of `any` for tighter control.

### `factory.irb-dhcp-server`

- **Stage:** factory-default-removal
- **Severity:** `advisory` (functional; replace only if external DHCP or static assignments are required)
- **Depends on:** `mgmt.external-dhcp-configured` or `mgmt.static-assignments` (if replacing)
- **Lockout risk:** `true` (removing DHCP before replacement addressing is active disconnects all LAN clients)
- **Evidence:** `show configuration interfaces irb` and `show configuration system services dhcp` report IRB as DHCP server for 192.168.2.0/24
- **Proposal:** If keeping DHCP but want reservations:
  ```text
  set system services dhcp pool 192.168.2.0/24 address-range low 192.168.2.10 high 192.168.2.200
  set system services dhcp pool 192.168.2.0/24 static-binding <MAC-address> fixed-address 192.168.2.50
  ```
  If moving to external DHCP server, configure DHCP relay:
  ```text
  delete system services dhcp pool 192.168.2.0/24
  set forwarding-options dhcp-relay server-group dhcp-servers <external-dhcp-ip>
  set forwarding-options dhcp-relay group dhcp-relay-group active-server-group dhcp-servers
  set forwarding-options dhcp-relay group dhcp-relay-group interface irb.0
  ```

### `factory.vlan-trust-single-broadcast-domain`

- **Stage:** factory-default-removal
- **Severity:** `advisory` (acceptable for small sites; segment for larger deployments)
- **Depends on:** Network segmentation requirements
- **Lockout risk:** `true` (VLAN restructuring can orphan the operator's management address)
- **Evidence:** `show vlans` reports `vlan-trust` with all LAN ports as members
- **Proposal:** For small sites, adopt as-is. For segmentation into multiple VLANs (e.g., users, servers, IoT):
  ```text
  set vlans vlan-users vlan-id 10
  set vlans vlan-servers vlan-id 20
  set vlans vlan-iot vlan-id 30
  set interfaces ge-0/0/1 unit 0 family ethernet-switching vlan members vlan-users
  set interfaces ge-0/0/2 unit 0 family ethernet-switching vlan members vlan-servers
  set interfaces ge-0/0/3 unit 0 family ethernet-switching vlan members vlan-iot
  ```
  Corresponding IRB units and zones required. Plan and test before removing `vlan-trust`.

### `factory.fxp0-unused`

- **Stage:** factory-default-removal
- **Severity:** `advisory` (no harm if unused, but clarifies intent)
- **Depends on:** Whether out-of-band management network exists
- **Lockout risk:** `false` (if fxp0 is unused, removing its config has no reachability impact)
- **Evidence:** Platform has fxp0; `show configuration interfaces fxp0` reports 192.168.1.1/24 DHCP server; no devices are connected to it
- **Proposal:** If truly unused:
  ```text
  delete interfaces fxp0
  delete system services dhcp pool 192.168.1.0/24
  ```
  If out-of-band management is planned, keep and connect it.

## Platform applicability

This file documents factory-default configuration observed and documented for **SRX300 and SRX400 series** Branch platforms. The Juniper guided setup documentation specifically covers SRX300 Line models (SRX320, SRX340, SRX345, SRX380).

**SRX345 validation target:** The repository owner has an SRX345 available for hardware validation. Claims applicable to SRX345 are especially valuable and should be verified against live device output when possible.

**Campus and datacenter platforms do not ship this configuration.** On SRX1600, SRX4120, SRX4300, SRX4700, and SRX5000 series, `factory-default` entry state means something different. Consult platform-specific documentation or classify as `bare` if the device was zeroized.
