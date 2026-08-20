# Entry-State Assessment

Read-only. Runs before any question about intent and before any write is proposed.

## Entry states

| Entry state | Signature | Consequence |
|---|---|---|
| `factory-default` | Vendor-shipped configuration still present | Load `factory-default-branch.md`; removal steps become gap entries |
| `bare` | Minimal or zeroized configuration, no zones or policy | Build every stage from zero |
| `partial` | Some stages complete, others absent | Close only the open gaps |
| `configured` | All stages satisfied | Report the verification matrix; propose no writes |
| `unreachable` | No usable management channel | Emit the console recovery path; propose no writes |

## Evidence to collect

### Platform and software version

```text
show version
```

**Source:** Juniper Networks, "show version (Junos OS)" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/junos-overview/topics/ref/command/show-version.html

Displays hostname, device model, and Junos OS version. Required privilege: `view`.

```text
show chassis hardware
```

**Source:** Juniper Networks, "show chassis hardware" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-chassis-hardware.html

Displays chassis inventory including hardware version, part numbers, and serial numbers. Useful for identifying platform series (SRX300, SRX400, SRX1600, etc.). Required privilege: `view`.

### Chassis cluster membership

```text
show chassis cluster status
```

**Source:** Verified live in `skills/srx-license-signature-maintenance/references/licensing.md` (this repository).

Establishes whether the device is part of a cluster. If cluster membership is found, this skill stops and routes to `srx-chassis-cluster-proxmox` or `srx-mnha`.

### Configured interfaces and units

```text
show interfaces terse
```

**Status:** UNVERIFIED. Juniper documentation confirms `show interfaces` exists with multiple options including `terse`, but the exact output format and field names for this assessment have not been verified against current Junos releases.

Lists all physical and logical interfaces with their operational states. The `terse` option provides a compact view suitable for identifying configured units.

### Security zones and host-inbound-traffic

```text
show security zones
```

**Source:** Juniper Networks, "show security zones" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/ref/command/show-security-zones.html

Displays configured security zones, their interface bindings, and host-inbound-traffic settings. Use `show security zones detail` for comprehensive zone information including host-inbound-traffic services. Required privilege: `view`.

### Screen profiles and zone bindings

```text
show security screen ids-option
```

**Source:** Juniper Networks, "show security screen ids-option" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/flow-packet-processing/topics/ref/command/show-security-screen-ids-option.html

Displays IDS screen profiles including TCP/UDP attack thresholds, SYN flood parameters, ICMP protections, and IPv6 extension header screening options. Introduced in Junos OS 8.5. Required privilege: `view`.

To determine which zones use which screen profiles, cross-reference the output with zone configurations.

### Security policies

```text
show security policies
```

**Source:** Juniper Networks, "show security policies" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/show-security-policies.html

Displays all configured security policies including source/destination zones, addresses, applications, and actions. Use `show security policies detail` for expanded information including hit counts and session statistics. Required privilege: `view`.

### Management plane configuration

```text
show configuration system
```

**Status:** UNVERIFIED. This command syntax is commonly used to display system-level configuration including root-authentication, name-server, ntp, services, and host-name, but the exact hierarchy and output format have not been verified against a specific Junos release for this assessment.

Read root authentication status (whether encrypted-password or ssh-key is configured), name servers, NTP servers, and enabled system services.

Alternative approach (also UNVERIFIED):
```text
show configuration system root-authentication
show configuration system name-server
show configuration system ntp
show configuration system services
```

These per-hierarchy commands may provide more focused output for specific management-plane elements.

### Entitlement state

```text
show system license
```

**Source:** Verified live in `skills/srx-license-signature-maintenance/references/licensing.md` (this repository).

Displays licensed features including AppID Signature and IDP-SIG. Note: `used` count does NOT mean the feature is actively enforcing. This command takes **no `node` argument** (verified live on 2-node vSRX cluster). For cluster environments, reach each node's routing engine separately:

```text
request routing-engine login node 1
show system license
exit
```

For IDP and AppID package versions:
```text
show services application-identification version
show services application-identification status
show security idp security-package-version
```

**Source:** Verified live in `skills/srx-license-signature-maintenance/references/licensing.md` (this repository).

## Classification rules

Assessment reads current state and produces exactly one entry state classification:

### `unreachable`

No SSH, console, or NETCONF session can be established. Emit the console recovery procedure and propose no writes. This state is detected before assessment commands run.

### `factory-default`

Presence of vendor-shipped configuration elements. For **Branch platforms only** (SRX300 and SRX400 series), these signatures indicate factory-default:

- Security zone named `trust` containing `vlan-trust` with subnet 192.168.2.0/24
- Security zone named `untrust` containing ge-0/0/0 configured as DHCP client
- Default security policies permitting trust-to-untrust with source NAT
- System services (HTTPS, DHCP, TFTP, SSH) permitted from untrust to local host

**Campus and datacenter platforms** (SRX1600, SRX4120, SRX4300, SRX4700, SRX5000 series) do **not** ship this configuration. On those platforms, `factory-default` means a different shipped state; consult platform-specific documentation or classify as `bare` if zeroized.

If factory-default elements are detected alongside operator-added configuration, classify as **`partial`** and enumerate the factory-default remnants as gaps. A half-removed factory default is more dangerous than either clean state.

**Source for Branch factory-default signatures:** Juniper Networks, "Verify Default Branch Connectivity" (Guided Setup: SRX300 Line Firewalls), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/guided-setup/branch-srx-gs/step-1-p1-verify_defaults.html

### `configured`

All required stages are satisfied:
- Management plane: root authentication set, reachable management interface, DNS and NTP configured
- Access control: at least two zones exist (one for management, one for services)
- Screening: at least one screen profile applied to a zone
- Policy: at least one explicit security policy (excluding factory defaults)

Emit the verification matrix and propose no writes.

### `bare`

Minimal configuration with no zones, no policies, no management services. Typically the result of `request system zeroize` or a manual delete of all configuration stanzas. Build every stage from zero.

**Note on `request system zeroize`:** This command removes all configuration, reboots to factory defaults, and eliminates all user-created files including credentials. After reboot, console access as root is required. The command affects all Routing Engines on dual-RE devices.

**Source:** Juniper Networks, "request system zeroize (Junos OS)" (CLI reference), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/request-system-zeroize.html

### `partial`

Configuration exists but gaps remain. Examples:
- Zones configured but no policies
- Management interface configured but no NTP or DNS
- Factory-default trust/untrust zones present alongside custom zones
- No screen profiles applied

Close only the open gaps; preserve existing configuration that satisfies a stage.

### Tie-breaking rule

When a device shows **both** factory-default remnants **and** operator configuration, classify as `partial`. List the remnants as gaps in the `factory.*` namespace. Removing or adopting factory-default elements is a lockout-risk change and must follow the protocol in `write-safety.md`.

## Chassis cluster

If `show chassis cluster status` reports cluster membership, **stop**. Cluster formation is out of scope for this skill.

Route to:
- `srx-chassis-cluster-proxmox` for Proxmox-hosted lab clusters
- `srx-mnha` for Multi-Node High Availability in production environments

This skill covers the **single-node case** and the **pre-cluster baseline only**. A device already in a cluster requires cluster-aware configuration workflows that this skill does not provide.
