---
name: sd-onprem-proxmox-deploy
description: Deploy Juniper Security Director On-Prem as a Proxmox VE guest from the vendor KVM artifacts. Use when installing SD On-Prem on Proxmox (no libvirt) by extracting the shipped qcow2 disks + seed ISO with the software .bin `--no-run` and importing them into a qm-native VM, planning the 4 same-subnet IPs (management + UI/device/log VIPs), choosing the sizing flavor, seeding first-boot config, ensuring a REACHABLE NTP server, and onboarding SRX/Junos devices. Not for Junos Space Security Director or Security Director Cloud (SaaS).
version: 0.2.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  status: draft
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
  verified_on:
    - release: "26.2.1-5348"
      host: "Proxmox VE 9.2 (dell-r6515-2)"
      date: "2026-07-21"
---

# Deploying Security Director On-Prem on Proxmox VE

> **STATUS: draft (v0.2.0).** Procedure below was executed end-to-end on
> **SD On-Prem 26.2.1-5348** on Proxmox VE 9.2. Values in `<angle brackets>` are
> site-specific. Finalize/promote via `writing-skills` after a second clean run.

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
- **SD internal CIDR** default `10.42.0.0/21` (≥/21); must not overlap any lab net.
- `--no-run` host deps: `qemu-img`, `genisoimage`/`mkisofs`, `column`,
  `cracklib-check` (Debian: `cracklib-runtime`), `sha256sum`.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

Invoke Claude `AskUserQuestion` or Codex `request_user_input` only for those
unresolved facts. Do not repeat answered questions or present the full catalog
automatically. Ask at most three single-select questions per round, then
re-evaluate. If no native interaction tool is available, ask the same questions
in concise plain text and preserve a free-text `Other` path.

Never request secrets or unredacted customer data. Treat intake answers as task
context, not approval for a live change; obtain separate explicit approval
before configuration, commit, upgrade, reboot, delete, or failover actions.

## Pre-flight (read-only)

1. Confirm all 4 IPs are free (`arping`), outside any DHCP pool.
2. **Verify the SD subnet can reach the chosen NTP + DNS — by PROTOCOL, not ping.**
   - NTP: if even the hypervisor host's `chronyc sources` shows Reach 0 to public
     NTP, the site blocks outbound 123 — find an internal NTP (often the site DNS
     servers also serve NTP).
   - DNS: send an actual DNS query to each candidate (`dig @<ip> example.com` or a
     UDP/53 probe). **A server that answers ping/NTP may NOT answer DNS.** SD
     validates EVERY configured DNS server at first boot and loops forever on a
     dead one (`DNS address is not connectable: <ip>`), never reaching the bundle
     pull. Prefer a single verified-working resolver over an unverified pair.
   - If egress is via a NAT firewall, confirm its source-NAT + permit policy cover
     the subnet, then test that replies actually return.
3. Host headroom: cores, RAM, and thin block storage (e.g. `local-lvm`) for the disks.

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
17. *(if HTTP bundle)* HTTP Proxy URL *(optional — blank)*
18. NTP Server *(single IP/host — must be reachable!)*
19. Security Director CIDR *(optional → default `10.42.0.0/21`)*
20. **Configuration ID / flavor** (`1`/`2`/`3` from the sizing table) — **easy to miss; not defaulted, loops on invalid**
21. Bridge interface name (e.g. `vmbr5`)
22. Disk provisioning (`1` Thin / `2` Thick-falloc / `3` Thick-full) — `1` for thin sparse qcow2s

Output: `<staging>/<version>/` with `Security-Director-OnPrem-disk-0/1/2.qcow2`,
`Security-Director-OnPrem-kvm.iso`, `kvm-env.ini`, `sd-onprem.xml`.

> **Bundle delivery.** SCP bakes a password into `kvm-env.ini`; prefer **HTTP no-auth**
> served from the host at boot time (the URL is only format-checked at extract time):
> `python3 -m http.server <port> --bind <host-mgmt-ip> --directory <staging-dir>`.
> Confirm `NTPServer=` in the generated `kvm-env.ini` is your **reachable** server
> before booting — if it's wrong, re-run `--no-run` (the ISO is built from it).

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

Start the HTTP bundle server (if used), then `qm start <vmid>`. The seed ISO applies
network config and the VM pulls + decrypts the `.tgz`, then installs its container
stack (RKE/k8s + SD) — **long (tens of minutes)**. Progress signals:
- mgmt IP answers ping within ~1–2 min (network seeded),
- the bundle server logs a `GET` from the mgmt IP (pull started),
- SD CLI (`ssh admin@<mgmt-ip>`) then UI VIP (`https://<ui-vip>`) come up last.
Snapshot the VM before onboarding.

### 4. Onboard Junos/SRX devices

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
- **Every DNS server must actually answer DNS.** A non-resolving entry (ping/NTP-only
  host) loops first boot on `DNS address is not connectable` — the appliance boots,
  applies config, but never pulls the bundle (0 requests to the bundle server).
  Fix = correct the DNS in `kvm-env.ini` and rebuild the ISO (re-run `--no-run`),
  swap the cdrom, reboot; disks/imports stay. Diagnose via the VGA console
  (`qm monitor <vmid>` → `screendump`) — it names the unreachable server.
- **Log transport is TLS on TCP/6514** (not UDP/514). Permit tcp/6514 through
  every transit FW, and **source-NAT on the FW that fronts SD** — TLS is
  bidirectional and SD's only route off its subnet is its default gateway, so it
  can't reply to a device's fabric IP. Verify: the FW session shows `In` AND `Out`
  packets both non-zero.
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

`qm stop <vmid> && qm destroy <vmid>` removes it cleanly (verify the VMID; never
destroy a `protected` guest). Stop the HTTP bundle server. No libvirt state remains.
