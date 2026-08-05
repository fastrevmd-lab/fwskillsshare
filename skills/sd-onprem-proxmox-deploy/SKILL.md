---
name: sd-onprem-proxmox-deploy
description: Deploy and validate Juniper Security Director On-Prem 25/26 as a Proxmox VE KVM guest. Use when planning, installing, rebuilding, validating network connectivity or first-boot seed data, and onboarding SRX/Junos devices. Not for Junos Space Security Director or Security Director Cloud.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [security-director, sd-on-prem, juniper, proxmox, kvm, qcow2, vm-deploy, virtio, ntp, log-collector, device-onboarding]
    related_skills: [srx-policy, srx-mnha, parsing-srx-configs]
  sources:
    - title: "SDC-KVM-Proxmox-support (Juniper Proxmox deployment how-to)"
      author: Juniper Networks
      note: "Vendor PDF; authoritative Proxmox import steps (25.2.2-era; uses --no-launch, renamed --no-run in 26.2.1)."
      retrieved: "2026-07-21"
    - title: "Deploy Juniper Security Director Using KVM | SD On-Prem 25.2.2"
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/sd-on-prem25.2.2/sd-on-prem-install-upgrade/install-guide/topics/task/install-kvm-tool.html
      retrieved: "2026-07-21"
    - title: "Deploy Juniper Security Director Using VMware vSphere | SD On-Prem 25.4.1"
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/sd-on-prem25.4.1/sd-on-prem-install-upgrade/install-guide/topics/task/install.html
      note: "Documents the cliadmin SSH user and predeployment VM-network reachability requirements."
      retrieved: "2026-07-24"
    - title: "set ipaddress change | SD On-Prem 25.4.1"
      author: Juniper Networks
      url: https://www.juniper.net/documentation/us/en/software/sd-on-prem25.4.1/sd-on-prem-user-guide/user-guide/topics/reference/set-ipaddress.html
      note: "The documented management-IP workflow prompts for netmask and gateway; it does not document a gateway-only command."
      retrieved: "2026-07-24"
  verified_on:
    - release: "26.2.1-5348"
      host: "Proxmox VE 9.2 (dell-r6515-2)"
      date: "2026-07-21"
---

# Deploying Security Director On-Prem on Proxmox VE

> **STATUS: stable (v1.0.0).** Procedure below was executed end-to-end on
> **SD On-Prem 26.2.1-5348** on Proxmox VE 9.2, and has since been run to
> completion three times by the maintainer — the repeat runs the draft label was
> waiting on. Values in `<angle brackets>` are site-specific.

**Full step-by-step how-to:** `references/HOWTO-deploy-sd-onprem-proxmox.md`
(complete deployment + log-path + operations guide; this SKILL.md is the summary).

## Overview

> **This is Security Director On-Prem 25/26 — a NEW ATOM-based appliance on
> single-node RKE2 Kubernetes, NOT Junos Space Security Director.** Ignore
> Space-era guidance: there is **no device "schema install"**, no Space fabric.
> Version parity (device 26.x + SD 26.x) is not a schema concern. Log analytics
> ("All Security Events") is gated by an **assigned subscription**, not a schema.
> Ingest path = `secmgt/jingest` pod → `kafka-la` → `logging/opensearch`.

SD On-Prem ships as a **KVM appliance**: an OS boot disk (qcow2) + two data disks
+ a seed ISO carrying first-boot config. Juniper's supported flow targets a
**libvirt/virsh** host, but Proxmox VE does not run `libvirtd`. So we run the
vendor `.bin` in **extract-only mode (`--no-run`)** to generate the qcow2s + ISO
(no KVM needed), then **import them into a `qm`-native VM** and skip the vendor
`launch-vm.sh`. The VM stays fully Proxmox-managed (snapshots, HA, API).

## Artifacts (both files are needed for a fresh install)

| File | Role |
|---|---|
| `Juniper-Security-Director-<ver>-<build>-kvm.bin` (~6 GB) | Embeds **disk-0** (OS qcow2, sha256-verified). Run normally it deploys/upgrades via libvirt; run **`--no-run`** it ONLY extracts artifacts (disk-0 + builds disk-1/2 + seed ISO) — no KVM. This is the fresh-install extractor on Proxmox. |
| `Juniper-Security-Director-<ver>-<build>.tgz` (~8 GB) | The **encrypted** software bundle the appliance pulls + decrypts at first boot. It is `tgz → metadata.json + *-software.zip.psig + *-software.zip → sd_onprem_software.zip (ENCRYPTED)`. **You cannot hand-extract qcow2s from it** — it is not the disk source; the `.bin` is. |

> **Gotcha:** a common misread is "the `.bin` is only for upgrades, just use the
> `.tgz`." False for a fresh Proxmox install — the `.tgz` payload is an encrypted
> zip; the disks come from `.bin --no-run`. You need **both**.

## Requirements

- **4 IP addresses in the SAME subnet:** management (VM/CLI), UI VIP, device-
  connection VIP, log-collector VIP. Plan them contiguously.
- **Sizing is chosen at extract time** from a flavor table (`--no-run` prompt).
  26.2.1 flavors: `1)` 8 vCPU / 64 GB / 200+250+500 GB · `2)` 16 / 80 / 200+400+1536
  · `3)` 40 / 208 / 200+525+3584. Disk sizes come from the artifacts; you don't set them.
- **A REACHABLE NTP server** — SD requires NTP at first boot (cert/bootstrap). If the
  site blocks outbound UDP/123 (common), an internet NTP like NIST will hang the
  install; use an **internal** NTP the SD subnet can reach.
- A complete inventory of every managed firewall's management target, management
  service, reverse-channel source addresses, zones, transit hops, and return paths.
- **SD internal CIDR** default `10.42.0.0/21` (≥/21); must not overlap any lab net.
- `--no-run` host deps: `qemu-img`, `genisoimage`/`mkisofs`, `column`,
  `cracklib-check` (Debian: `cracklib-runtime`), `sha256sum`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.

## Mandatory predeployment connectivity STOP gate

> **STOP GATE — do not extract artifacts, create/import disks, or create/start an
> SD VM until every check below passes.** A test sourced by the Proxmox host is
> invalid when the host and proposed SD guest use different addresses, gateways,
> routes, policies, or NAT.

1. Confirm all 4 IPs are free (`arping`), outside any DHCP pool.
2. **Per-firewall connectivity matrix.** Fill one row per firewall and traffic
   direction. Do not leave an implicit "same as above" path:

   | Firewall/path | Exact source | Target + port | Source gateway | Hops | From/to zones + policy | NAT | Return route | Bidirectional proof |
   |---|---|---|---|---|---|---|---|---|
   | `<fw>-discovery` | `<SD-mgmt-IP>` | `<fw-mgmt-IP>:22` | `<SD-gateway>` | `<routers/FWs>` | `<zones/rule>` | `<none/SNAT>` | `<to translated/original source>` | `<session In/Out>` |
   | `<fw>-device` | `<device-source>` | `<device-VIP>:7804` | `<device-gateway>` | `<routers/FWs>` | `<zones/rule>` | `<none/SNAT>` | `<to translated/original source>` | `<listener + session>` |
   | `<fw>-logs` | `<revenue-source>` | `<log-VIP>:6514/TLS` | `<device-gateway>` | `<routers/FWs>` | `<zones/rule>` | `<none/SNAT>` | `<to translated/original source>` | `<TLS handshake + session>` |
   | `bundle` | `<SD-mgmt-IP>` | `<exact HTTP URL or SCP endpoint/path>` | `<SD-gateway>` | `<routers/FWs>` | `<zones/rule>` | `<none/approved translation>` | `<to observed source>` | `<full retrieval + identity>` |

3. Attach a disposable probe VM or network namespace to the **same Proxmox
   bridge** and configure the exact proposed SD management source IP/prefix and
   default gateway. From that source:
   - confirm the default route and first hop;
   - complete TCP/22 (or the selected management service) to **every** firewall;
   - query every DNS server with `dig @<server> <name>`;
   - obtain a valid NTP response with `chronyd -Q`, `ntpdate -q`, or `sntp`.
4. From that same exact source, fully retrieve the configured bundle path
   **before extraction**:
   - For the restricted HTTP pattern below, require a direct path with no SNAT
     and no HTTP proxy so the server observes `<SD-mgmt-IP>`. Prove intentionally
     unauthenticated HTTP, readability, expected filename and byte size/checksum,
     gateway/hops, `NAT=none`, return path, and bidirectional session counters.
   - If SCP is selected, retrieve the exact seeded host, port, username, and path.
     Prove noninteractive authentication, readability, expected filename and
     byte size/checksum, gateway/hops, policy, NAT, return path, and bidirectional
     session counters. Never record a password in commands or evidence.
   If direct HTTP or the exact configured SCP path cannot be proved, STOP.
   Separately design and approve any translated, proxied, or alternate method;
   record both original and server-observed sources and preflight that exact
   method before reopening the gate.
5. Bind temporary listeners to the proposed device and log VIPs. Test TCP/7804
   from each device-management source. For TCP/6514, complete and validate a TLS
   handshake from every selected revenue/log source; a TCP connect alone is a
   failure. Missing TLS tooling is `UNTESTED`, which keeps the gate closed.
6. While each probe is active, inspect every stateful transit firewall. Require
   request and reply packets (`In` and `Out` both non-zero), expected zones and
   policy, expected translation, and a return route to the translated or
   original source. Route/config inspection alone is not proof.
7. Record the results and obtain approval for any required firewall or routing
   changes. Re-run failed probes after the approved change. Advance only when
   the matrix, including the bundle and TLS rows, has no failed or untested row.
8. Confirm host CPU, RAM, and thin block storage headroom for the selected flavor.

**Regression guard (remote lab, 2026-07-24):** hypervisor-only DNS/NTP checks
passed while the seed used gateway `10.88.15.254`. The installed SD source
`10.88.15.19/21` then sent managed-device traffic to the wrong first hop and
could not reach the firewalls. The required gateway was the policy/routing
firewall `10.88.15.18`; the reverse paths terminate at device VIP
`10.88.15.21:7804` and log VIP `10.88.15.22:6514`. Exact-source testing would
have failed before deployment.

## Procedure

### 1. Stage artifacts + extract with `--no-run`

Stage the `.tgz` (served to the VM later) and the `.bin` on the host. Then run the
extractor. It is interactive; the **prompt order (26.2.1)** is:

1. Base folder for KVM artifacts  → `<staging-dir>` (must already exist; artifacts land in `<staging-dir>/<version>/`)
2. *(re-runs only)* `Overwrite existing contents? (y/N)` → `y`
3. Virtual Machine Name
4. Hostname
5. CLI Admin Password *(silent; 8–32, ≥3 of digit/upper/lower/special, must pass cracklib — systematic strings like `Test1234!` are rejected)*
6. Management IP (CIDR)
7. Default Gateway
8. DNS Servers (space-separated)
9. Search Domains *(optional — blank ok)*
10. UI Virtual IP
11. UI FQDN *(optional)*
12. Device Connection VIP
13. Device Connection FQDN *(optional)*
14. LOG Collector VIP
15. LOG Collector FQDN *(optional)*
16. Software Bundle Path — SCP `user@host:port/path` **or** HTTP `http://host:port/path` (see below)
17. *(if HTTP bundle)* HTTP Proxy URL *(blank for this direct restricted-server pattern)*
18. NTP Server *(single IP/host — must be reachable!)*
19. Security Director CIDR *(optional → default `10.42.0.0/21`)*
20. **Configuration ID / flavor** (`1`/`2`/`3` from the sizing table) — **easy to miss; not defaulted, loops on invalid**
21. Bridge interface name (e.g. `vmbr5`)
22. Disk provisioning (`1` Thin / `2` Thick-falloc / `3` Thick-full) — `1` for thin sparse qcow2s

Output: `<staging>/<version>/` with `Security-Director-OnPrem-disk-0/1/2.qcow2`,
`Security-Director-OnPrem-kvm.iso`, `kvm-env.ini`, `sd-onprem.xml`.

> **Bundle delivery.** Never serve `<staging-dir>` or an extraction directory:
> it contains `kvm-env.ini` (CLI/SCP credentials) plus XML, qcow2, and ISO files.
> File mode `0600` does not protect them from a web server running as their
> owner. Serve only the `.tgz` from a dedicated bundle-only webroot, bind the
> approved host IP, and restrict the host firewall to `<SD-mgmt-IP>/32` and the
> selected port. Stop the server and remove its temporary rule immediately after
> each preflight or appliance retrieval. Use bundled
> `scripts/serve_bundle.py`; it enforces the exact file/source and emits a
> `COMPLETE` byte count only after streaming finishes. See the HOWTO for evidence
> and fail-closed cleanup.
> Confirm management IP/prefix, gateway, bridge, DNS, NTP, bundle URL, and all
> VIPs in `kvm-env.ini` match the passed STOP-gate evidence before booting.

Driving it non-interactively: pipe the answers in order via stdin, but only after
verifying every value's format (a looping validator desyncs the pipe). All values
before the password must be valid so the silent password read stays aligned.

### 2. Build the Proxmox VM (mirror the generated `sd-onprem.xml`)

Read `<staging>/<version>/sd-onprem.xml` for the exact hardware. On 26.2.1:
**machine `q35`, CPU host-passthrough, 3 `virtio` disks (vda/vdb/vdc), ISO on a
virtio-scsi cdrom, virtio NIC.**

```bash
VM_DIR=<staging>/<version>
qm create <vmid> --name sd-onprem --machine q35 --cpu host --cores <N> --sockets 1 \
  --memory <MB> --numa 0 --ostype l26 --scsihw virtio-scsi-single \
  --net0 virtio,bridge=<bridge> --vga std --serial0 socket
cp "$VM_DIR"/Security-Director-OnPrem-kvm.iso /var/lib/vz/template/iso/sd-onprem-seed.iso
for i in 0 1 2; do qm importdisk <vmid> "$VM_DIR"/Security-Director-OnPrem-disk-$i.qcow2 local-lvm; done
qm set <vmid> --virtio0 local-lvm:vm-<vmid>-disk-0 --virtio1 local-lvm:vm-<vmid>-disk-1 \
  --virtio2 local-lvm:vm-<vmid>-disk-2 --ide2 local:iso/sd-onprem-seed.iso,media=cdrom
qm set <vmid> --boot order=virtio0     # SEPARATE command — see gotcha
```

> **Gotcha — boot order.** Setting `--boot order=virtio0` in the SAME `qm set` that
> attaches the disks does NOT stick (the disk isn't a valid boot target yet); it
> silently falls back to `order=net0;ide2`. Set boot order in its OWN `qm set`
> AFTER the disks are attached, then confirm `qm config <vmid> | grep ^boot`.

### 3. First boot

For HTTP, recreate the approved bundle-only webroot/firewall window and start
its bound server. For SCP, revalidate the approved exact account, endpoint, and
path restriction; do not substitute an HTTP service. Then `qm start <vmid>`.
The seed ISO applies network config and the VM pulls + decrypts the `.tgz`, then
installs its container stack (RKE/k8s + SD) — **long (tens of minutes)**.
Progress signals:
- mgmt IP answers ping within ~1–2 min (network seeded),
- the configured service records a completed transfer from the observed SD
  source (HTTP must emit a matching `COMPLETE` byte count),
- SD CLI (`ssh cliadmin@<mgmt-ip>` on 26.2.1) then UI VIP
  (`https://<ui-vip>`) come up last.
Close the temporary bundle-delivery window as soon as the successful transfer
completes: remove the HTTP server/rule/webroot or the temporary SCP access, as
applicable. Retain redacted transfer, session, and checksum evidence.
Snapshot the VM before onboarding.

### 4. Onboard Junos/SRX devices

#### 4a. NTP preflight — a hard gate, before any device is discovered

**Do not add, discover, or onboard an SRX until its clock is proven
synchronized.** Configured servers and a running `ntpd` are *not* the gate;
**proven synchronization is**. An SRX whose clock is skewed still completes the
mTLS handshake and still gets its payloads acknowledged by the collector, so
every transport-level check passes while the logs never surface in SD. Observed
in a live deployment: several SRXs ran ~375 s behind, the streams connected and
were acknowledged, and the traffic logs were simply absent from the GUI. They
appeared only after NTP was corrected and fresh traffic was generated.

Configure at least two reachable servers and an appropriate source address:

```junos
set system processes ntp enable
set system ntp server <primary-server>
set system ntp server <secondary-server>
set system ntp source-address <reachable-source-address>
```

**`set system processes ntp enable` is hidden from CLI completion but is valid
and required** — it will not tab-complete, which is why it gets skipped. Verified
present on production SRXs running Junos 26.2R1.

**Verify sync before onboarding — `show ntp associations` is authoritative:**

```text
show configuration system processes | display set | match "ntp enable"
show ntp associations no-resolve
show system uptime | match "Current time|Time Source"
show ntp status
show system processes extensive | match " ntpd"
```

Required state:

| Evidence | Role | Required |
|---|---|---|
| `show ntp associations` | **the gate** | at least one peer prefixed `*` (selected system peer), `reach` non-zero — `377` is fully reached — and `offset` within deployment tolerance |
| `show configuration system processes` | gate | `set system processes ntp enable` present |
| `show system processes extensive` | gate | `ntpd` running |
| `show system uptime` | corroborating | `Time Source: NTP CLOCK` |
| `show ntp status` | corroborating | `leap_none`, `sync_ntp`; `clock_sync` when settled |
| Fleet-wide | gate | all SRX clocks agree **before** SD configures certificates, device identity, or log streaming |

**Pass/fail on the associations table, not on the status word.** Two observations
from live devices explain why:

- **`sync_ntp` is not by itself proof of synchronization.** It appears alongside
  `no_sys_peer` — meaning no system peer is currently selected. So `sync_ntp` on
  its own must not be read as a pass.
- **But `clock_sync` must not be a hard fail either.** A device reporting
  `leap_none, sync_ntp, no_sys_peer` was, moments later, showing a `*` peer at
  `reach 377` with a sub-second offset — genuinely synchronized, with the status
  word simply lagging. Requiring `clock_sync` would have failed a healthy device.

So: read `show ntp associations`. A `*` peer with non-zero reach and an
acceptable offset is a pass even if the status word has not caught up; no `*`
peer, or `reach 0`, is a fail regardless of what `sync_ntp` says.
`Time Source: NTP CLOCK` appears in both states and cannot settle it.

**Through NAT or VPN, check UDP/123 both ways.** Verify routing, security
policy, and source NAT for UDP/123, and prove the return path — a request that
leaves and never comes back looks identical to an unreachable server.

- When remote SRXs source NTP from a **loopback management identity**, that
  loopback prefix must be included in the transit firewall's **source**-NAT
  match. This is the common miss: the device has a route and a policy, but its
  loopback source is not translated, so replies never return.
- **The NTP servers' own addresses do not belong in a source-address NAT
  match.** They are destinations. Putting them there is a frequent
  misconfiguration that silently breaks the return path.

If any device fails this gate, fix NTP and re-verify before continuing. Do not
proceed to 4b with a known-skewed clock and plan to fix it later — the
onboarding will appear to succeed.

#### 4b. Onboarding

- **Device MANAGEMENT** (add in SD → Inventory → Devices: mgmt IP, super-user,
  NETCONF/SSH) connects toward the **device-connection VIP** and may ride the
  management path (fxp0 / mgmt net).
- **LOG STREAMING must NOT source off fxp0 — SD cannot receive security logs
  from the management interface.** SRX stream-mode security logs are emitted by
  the PFE (data plane), which cannot egress fxp0. So each device must reach the
  **log-collector VIP from a production/revenue port**: set `security log
  source-address` to a revenue interface IP and give the device a data-plane
  route to the collector. Because the 4-VIP same-subnet rule pins the
  log-collector VIP onto the management subnet, that subnet must be made
  reachable from the data fabric — e.g. one SRX carries a revenue-port leg on the
  collector subnet and acts as the log gateway the rest of the fleet routes
  through. Logging via fxp0 silently never arrives.
- **All Security Events / log analytics is gated behind an assigned
  subscription/license** (Admin → Subscriptions) — separate from device
  management. If logs arrive (verify at the collector) but Security Events is
  empty, assign a subscription to the device before chasing anything else.

## Gotchas (all hit in a real 26.2.1 build)

- **No libvirt on Proxmox** → don't run `launch-vm.sh`; import qcow2s into `qm`.
- **`.bin --no-run` is the disk source**, not the `.tgz` (whose payload is encrypted).
- **Flavor/config-ID prompt** is easy to miss when scripting answers — it has no
  default and loops on invalid input; a short answer list desyncs here.
- **Boot order must be a separate `qm set`** after disks attach (else `net0;ide2`).
- **NTP must be reachable** — an internet NTP behind a site that blocks outbound 123
  hangs first boot; use an internal NTP. SD egresses via its default gateway, so a
  plain reachable internal server needs no extra routes.
- **There is no documented gateway-only CLI command.** The documented
  `set ipaddress change <IP>` workflow prompts for management IP, netmask, and
  gateway. For the verified 26.2.1 wrong-seed incident, preserving the failed
  guest and rebuilding from corrected seed data with fresh disks is the
  conservative recovery policy—not a claim about universal vendor behavior.
- **Every DNS server must actually answer DNS.** A non-resolving entry (ping/NTP-only
  host) loops first boot on `DNS address is not connectable` — the appliance boots,
  applies config, but never pulls the bundle (0 requests to the bundle server).
  Fix = correct the DNS in `kvm-env.ini` and rebuild the ISO (re-run `--no-run`),
  swap the cdrom, reboot; disks/imports stay. Diagnose via the VGA console
  (`qm monitor <vmid>` → `screendump`) — it names the unreachable server.
- **Log transport is TLS on TCP/6514** (not UDP/514). A plain TCP connect does
  not pass preflight; require a successful TLS handshake from every selected
  revenue source. Permit tcp/6514 through every transit FW, and **source-NAT on
  the FW that fronts SD** — TLS is
  bidirectional and SD's only route off its subnet is its default gateway, so it
  can't reply to a device's fabric IP. Verify: the FW session shows `In` AND `Out`
  packets both non-zero.
- **A skewed device clock looks exactly like a working log pipeline.** The mTLS
  stream connects, the collector acknowledges the payloads, the FW session shows
  `In` and `Out` non-zero — and the traffic logs still never appear in the SD
  GUI. Seen with SRXs ~375 s behind; the logs surfaced only after NTP was fixed
  and fresh traffic generated. Every transport check you would reach for passes,
  so gate on NTP **before** onboarding (§4a) rather than debugging the stream.
- **`lo0` is NOT a selectable log source** — SD's picker lists only physical
  revenue interfaces. For tunnel-managed branches pick the **LAN** port (subnet the
  gateway routes back over the tunnel), **not the WAN** (on the shared underlay the
  gateway reaches directly) — a WAN source is asymmetric (forward via tunnel, reply
  via underlay) so the branch drops the SYN-ACK (`Out:0`). Also keep the source IP
  in the gateway's source-NAT range.
- **Device-connection (VIP:7804) needs the same source-NAT** as logs for
  tunnel-managed branches — NAT both the device-connection VIP and the log VIP, or
  branch adoption hangs at `In:1 / Out:0` (no return path to the branch subnet).
- **MNHA:** each node has an independent config (configure the route on both);
  only the active node logs (backup is idle, streams on failover).
- **Disks are virtio (`virtio0/1/2`), machine q35** per the generated XML.
- The `--no-run` "not enough disk space (thick)" message is benign under thin.
- **Flavor is validated as a WHOLE SET on every boot — you cannot partially
  resize.** SD checks CPU + RAM + all three disk sizes against the supported
  flavor table (26.2.1: `8/64/200+250+500`, `16/80/200+400+1536`,
  `40/208/200+525+3584`). Bumping only CPU/RAM (e.g. 8/64 → 16/80 while leaving
  the flavor-1 disks) yields **"Unsupported CPU/Memory/Disk configured"** on the
  console and **RKE2 never starts** (`kubectl`/CLI: `connection to 127.0.0.1:6443
  refused`). To move flavors you must resize CPU, RAM, AND grow the data disks to
  the target row (a real storage migration, not just `qm resize`). Recovery:
  power off, set all resources back to the installed flavor, power on. So to
  relieve memory pressure on flavor 1, tune log volume/retention instead of
  adding RAM — or plan a full flavor-2 migration.

## Rollback

For the verified 26.2.1 wrong-seed case, protect/stop the failed guest and build
a fresh VM from corrected seed data and fresh disks; do not destroy the rollback
copy until the replacement passes the same connectivity matrix. `qm stop <vmid>
&& qm destroy <vmid>` removes an explicitly approved disposable VM (verify the
VMID; never destroy a protected guest). Stop the bundle server; remove its
temporary host-firewall rule, bundle-only webroot, and test certificates. No
libvirt state remains.
