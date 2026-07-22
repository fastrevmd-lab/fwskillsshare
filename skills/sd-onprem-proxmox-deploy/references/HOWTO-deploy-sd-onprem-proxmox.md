# How-To: Deploy Security Director On-Prem 26.x on Proxmox VE

> **Product note — read first.** This guide is for **Security Director On-Prem
> 25/26**, Juniper's **new ATOM-based appliance** that runs on single-node RKE2
> Kubernetes. It is **NOT Junos Space Security Director** and shares nothing with
> it. There is **no device "schema install"** step, no Space fabric. Version
> parity (device 26.x + SD 26.x) is not a schema concern. Ignore all Space-era
> Security Director documentation.

Proven end-to-end on **SD On-Prem 26.2.1-5348**, Proxmox VE 9.2, managing Junos
26.2R1.7 vSRX (incl. MNHA pairs). Values in `<angle brackets>` are site-specific;
the worked example uses the mechub remote lab (mgmt subnet `192.168.77.0/24`).

---

## 1. Architecture in one paragraph

SD On-Prem ships as a **KVM appliance**: an OS boot disk + two data disks (config,
logs) + a seed ISO that carries first-boot config. Inside, it's the Juniper
**ATOM microservices platform** on **RKE2 Kubernetes** — ~70 pods including
OpenSearch (log/event store), two Kafka buses, PostgreSQL/Patroni, Redis, and the
`jingest` log parser. Juniper's supported install targets a libvirt/virsh host,
but Proxmox has no `libvirtd`, so we **extract the qcow2 disks + ISO with the
software `.bin --no-run`** and **import them into a `qm`-native VM**.

---

## 2. Prerequisites

**Artifacts (both required for a fresh install):**

| File | Role |
|---|---|
| `Juniper-Security-Director-<ver>-<build>-kvm.bin` (~6 GB) | Embeds **disk-0** (OS, sha256-verified). `--no-run` extracts artifacts (disks + seed ISO) without KVM. This is the fresh-install extractor on Proxmox. |
| `Juniper-Security-Director-<ver>-<build>.tgz` (~8 GB) | The **encrypted** software bundle the VM pulls + decrypts at first boot. Triple-nested & encrypted — you **cannot** hand-extract qcow2s from it. It is not the disk source; the `.bin` is. |

> Common misread: "the `.bin` is only for upgrades, just use the `.tgz`." False for
> a fresh Proxmox install — you need **both**.

**Flavors (26.2.1) — pick one; the WHOLE ROW is enforced (see §9):**

| Flavor | vCPU | RAM | OS disk | Config disk | Log disk |
|---|---|---|---|---|---|
| 1 | 8 | 64 GB | 200 G | 250 G | 500 G |
| 2 | 16 | 80 GB | 200 G | 400 G | 1.5 T |
| 3 | 40 | 208 GB | 200 G | 525 G | 3.5 T |

**Four IP addresses in the SAME subnet:** management/CLI, UI VIP, device-connection
VIP, log-collector VIP. Plan them contiguously (e.g. `.20/.21/.22/.23`).

**Reachable NTP + DNS from the SD subnet** — and verify by *protocol*, not ping
(see §3). SD requires NTP at first boot.

**`--no-run` host dependencies:** `qemu-img`, `genisoimage`/`mkisofs`, `column`,
`cracklib-check` (Debian: `cracklib-runtime`), `sha256sum`. (Proxmox 9 has all but
`cracklib-runtime` — `apt install cracklib-runtime`.)

---

## 3. Pre-flight (read-only)

1. **Free IPs** — `arping -I <bridge> <ip>` for all four; must be outside any DHCP pool.
2. **NTP reachability** — if even the hypervisor host's `chronyc sources` shows
   Reach 0 to public NTP, the site blocks outbound UDP/123 (common). Use an
   **internal** NTP the SD subnet can reach.
3. **DNS reachability — test with a real query, `dig @<ip> example.com`.** A host
   that answers ping/NTP may NOT answer DNS. SD validates **every** configured DNS
   server at first boot and loops forever on a dead one
   (`DNS address is not connectable: <ip>`), never pulling the bundle. **Use a
   single verified-working resolver** rather than an unverified pair.
4. **Host headroom** — cores, RAM, and thin block storage (e.g. `local-lvm`).

---

## 4. Extract artifacts (`--no-run`)

Stage both files on the host (e.g. `/var/lib/vz/sd-onprem/`), then run the
extractor. It is interactive; the **26.2.1 prompt order is 22 prompts**:

| # | Prompt | Example |
|---|---|---|
| 1 | Base folder for KVM artifacts | `/var/lib/vz/sd-onprem` (must exist; output lands in `<base>/<version>/`) |
| 2 | *(re-runs only)* `Overwrite existing contents? (y/N)` | `y` |
| 3 | Virtual Machine Name | `sd-onprem` |
| 4 | Hostname | `sd-onprem` |
| 5 | CLI Admin Password | *(silent; 8–32, ≥3 of digit/upper/lower/special, must pass cracklib — systematic strings like `Test1234!` are rejected)* |
| 6 | Management IP (CIDR) | `192.168.77.20/24` |
| 7 | Default Gateway | `192.168.77.1` |
| 8 | DNS Servers (space-sep) | `10.88.25.1` *(one verified resolver)* |
| 9 | Search Domains (optional) | *(blank)* |
| 10 | UI Virtual IP | `192.168.77.21` |
| 11 | UI FQDN (optional) | *(blank — reached by IP)* |
| 12 | Device Connection VIP | `192.168.77.22` |
| 13 | Device Connection FQDN (optional) | *(blank)* |
| 14 | LOG Collector VIP | `192.168.77.23` |
| 15 | LOG Collector FQDN (optional) | *(blank)* |
| 16 | Software Bundle Path | `http://192.168.77.254:8085/<bundle>.tgz` *(HTTP; see note)* |
| 17 | HTTP Proxy URL (optional, http only) | *(blank)* |
| 18 | NTP Server | `10.88.25.1` *(must be reachable)* |
| 19 | Security Director CIDR (optional) | *(blank → default `10.42.0.0/21`)* |
| 20 | **Configuration ID / flavor** (1/2/3) | `1` — **easy to miss when scripting; no default, loops on invalid** |
| 21 | Bridge interface name | `vmbr5` |
| 22 | Disk provisioning (1 Thin / 2/3 Thick) | `1` — thin sparse qcow2s |

**Bundle delivery = HTTP no-auth** (SCP bakes a password into `kvm-env.ini`).
Serve it from the host at boot time:
`python3 -m http.server 8085 --bind <host-mgmt-ip> --directory <base>`
(the URL is only format-checked at extract time; the server must be up when the VM
boots and pulls). **Confirm `NTPServer=` and `DNS=` in the generated `kvm-env.ini`
are reachable before booting** — if wrong, re-run `--no-run` (the ISO is built
from it), swap the cdrom, reboot.

Output in `<base>/<version>/`: `Security-Director-OnPrem-disk-0/1/2.qcow2`,
`Security-Director-OnPrem-kvm.iso`, `kvm-env.ini`, `sd-onprem.xml`.

Driving `--no-run` non-interactively (pipe answers via stdin) works, but only if
every value's format is valid — a looping validator desyncs the stream.

---

## 5. Build the Proxmox VM

Mirror the generated `sd-onprem.xml`: **machine `q35`, CPU host-passthrough, 3
`virtio` disks (vda/vdb/vdc), ISO on cdrom, virtio NIC.**

```bash
VM_DIR=<base>/<version>
qm create <vmid> --name sd-onprem --machine q35 --cpu host --cores 8 --sockets 1 \
  --memory 65536 --numa 0 --ostype l26 --scsihw virtio-scsi-single \
  --net0 virtio,bridge=<bridge> --vga std --serial0 socket
cp "$VM_DIR"/Security-Director-OnPrem-kvm.iso /var/lib/vz/template/iso/sd-onprem-seed.iso
for i in 0 1 2; do qm importdisk <vmid> "$VM_DIR"/Security-Director-OnPrem-disk-$i.qcow2 local-lvm; done
qm set <vmid> --virtio0 local-lvm:vm-<vmid>-disk-0 --virtio1 local-lvm:vm-<vmid>-disk-1 \
  --virtio2 local-lvm:vm-<vmid>-disk-2 --ide2 local:iso/sd-onprem-seed.iso,media=cdrom
qm set <vmid> --boot order=virtio0     # SEPARATE command — see §9
```

---

## 6. First boot + verify

Start the HTTP bundle server, then `qm start <vmid>`. Sequence:
- mgmt IP answers ping within ~1–2 min (network seeded);
- the bundle server logs a `GET` from the mgmt IP (pull started);
- container-stack install runs (**tens of minutes** — OpenSearch, Kafka, etc.);
- ingress comes up (`https://<ui-vip>` serves the Juniper self-signed cert, may 404);
- app pods finish → `https://<ui-vip>/login` returns 200.

Snapshot the VM before onboarding. Assign the **subscription/license** (Admin →
Subscriptions) — **log analytics / "All Security Events" is gated behind it**,
separate from device management.

---

## 7. Onboard Junos/SRX devices

**Management** and **logging are two different planes:**

- **Management** — create the device in SD (Inventory → Devices), apply the
  generated adopt/onboard config to the device. It connects out to the
  **device-connection VIP** (`.22`); can ride the management path (fxp0/mgmt net).
  SD then pushes the `sd-logs` log stream to the device.
- **Logging — must NOT source off fxp0.** SD cannot receive security logs from the
  management interface. See §8.

---

## 8. The log path (the hard part)

**SD On-Prem collects structured syslog over TLS on TCP/6514** (not plain UDP/514).
When SD onboards a device it pushes:

```
set security log source-interface <revenue-port>.0
set security log stream sd-logs host <log-VIP> port 6514 transport protocol tls ...
```

For that stream to actually work, three network facts must hold:

1. **Source from a production/revenue port** (SD sets `source-interface`), never
   fxp0 — the PFE cannot egress the management interface.
2. **A data-plane route to the log-collector VIP.** The VIP sits on the management
   subnet (the 4-VIP same-subnet rule forces this), which the data fabric can't
   normally reach. Give **one SRX a revenue-port leg on the collector subnet** and
   make it the **log gateway** the rest of the fleet routes through. In the worked
   example, `dc-fw ge-0/0/3 = 192.168.77.50` is directly connected to the log
   subnet; every other device routes `<log-VIP>/32` toward it.
3. **Source-NAT on the log-gateway FW.** TLS/6514 is **bidirectional** (unlike
   one-way UDP syslog), so SD must be able to reply. SD's only route off its subnet
   is its default gateway — it has **no route back to the FW's fabric interface**.
   Source-NAT the log traffic to the gateway's on-subnet leg so SD replies
   on-subnet and the FW un-NATs back.

**Worked config (per hop):**

```junos
# every logging device: route the collector VIP toward the log-gateway FW
set routing-options static route <log-VIP>/32 next-hop <toward-gateway>

# the log-gateway FW (dc-fw): permit + source-NAT the log traffic
set applications application sd-syslog-tls protocol tcp destination-port 6514
set security policies global policy 600-syslog-to-sd match from-zone <fabric> to-zone <collector-leg-zone>
set security policies global policy 600-syslog-to-sd match application [ junos-syslog sd-syslog-tls ]
set security policies global policy 600-syslog-to-sd then permit
insert security policies global policy 600-syslog-to-sd before policy <deny-all>
set security nat source rule-set logs-to-sd from zone [ <fabric-zones> ] to zone <collector-leg-zone>
set security nat source rule-set logs-to-sd rule nat-logs match source-address <fabric-supernets>
set security nat source rule-set logs-to-sd rule nat-logs match destination-address <log-VIP>/32
set security nat source rule-set logs-to-sd rule nat-logs then source-nat interface

# transit FWs between device and gateway: permit tcp/6514 (their stateful session handles the return)
set applications application sd-syslog-tls protocol tcp destination-port 6514
set security policies global policy 600-syslog-to-sd match application [ junos-syslog sd-syslog-tls ]  # + route the VIP onward
```

**Verify** on the log-gateway FW:
`show security flow session destination-prefix <log-VIP> protocol tcp` — a healthy
stream is `Session State: Valid`, **`In` AND `Out` packets both non-zero** (TLS is
bidirectional; `Out: 0` means the return path is broken — check the source-NAT).

**Logging source interface per device** = the revenue port whose route reaches the
log gateway (the egress interface toward it). E.g. a device that reaches the
gateway via its dc-facing `ge-0/0/2` should log-source from `ge-0/0/2`.

> **SD's source-interface picker only lists PHYSICAL revenue interfaces — `lo0`
> is not selectable.** For a device managed over a tunnel (branches, whose only
> stable identity is `lo0`), you must pick a physical port — but **NOT just any
> one.** The log stream default-routes out the tunnel (st0), so the reply must
> come back over the tunnel too. Pick the interface whose subnet the gateway
> routes **via the tunnel** — the **LAN** (`ge-0/0/1`), reachable only over st0 —
> **not the WAN** (`ge-0/0/0`), which sits on the shared underlay the gateway
> reaches **directly**. Sourcing from the WAN → forward via tunnel, reply via
> underlay = **asymmetric**, and the branch drops the SYN-ACK (`Out: 0`, the TLS
> handshake never completes). Also ensure the chosen IP is inside the gateway's
> source-NAT range. Verify on the gateway: `show route <candidate-IP>` must
> resolve to the same st0 the traffic egresses, not a directly-connected underlay.

**Device-connection (`.22`) needs the same return-path fix as logs.** The device
management channel (outbound to the device-connection VIP, port 7804) is also
bidirectional and also breaks for tunnel-managed branches (SD has no route back to
`172.31.x`). Make the gateway FW's source-NAT match **both** the device-connection
VIP and the log-collector VIP (e.g. `destination-address [ <dev-VIP> <log-VIP> ]`),
or branch adoption hangs at `In: 1 / Out: 0`.

**MNHA pairs:** each node runs an INDEPENDENT config (different interface IPs) —
configure the route on **both** nodes. Only the **active** node processes transit
traffic, so only it generates security logs; the backup is idle and starts
streaming automatically on failover. Both nodes' streams land on the same
gateway-FW zone, so one transit permit + source-NAT covers the pair.

---

## 9. Gotchas (all hit in a real build)

- **No libvirt on Proxmox** → don't run the vendor `launch-vm.sh`; import qcow2s.
- **`.bin --no-run` is the disk source**, not the encrypted `.tgz`.
- **Config-ID / flavor prompt (#20) is easy to miss** when scripting — no default,
  loops on invalid.
- **Boot order must be a SEPARATE `qm set`** after the disks attach, else it
  silently falls back to `order=net0;ide2` and won't boot the OS disk.
- **NTP must be reachable** — an internet NTP behind a site that blocks outbound
  123 hangs first boot; use an internal one.
- **Every DNS server must actually answer DNS** — a non-resolving entry loops first
  boot on `DNS address is not connectable`; the VM never pulls the bundle
  (0 requests to the bundle server). Diagnose from the console
  (`qm monitor <vmid>` → `screendump`); it names the dead server.
- **Log analytics is subscription-gated** — logs can arrive at the collector while
  "All Security Events" stays empty until a subscription is assigned.
- **Logs are TLS/6514, not UDP/514** — permit tcp/6514 through transit and
  source-NAT for the return path (§8).
- **Flavor is validated as a WHOLE SET on every boot — you cannot partially
  resize.** CPU + RAM + all three disk sizes must match one flavor row (§2).
  Bumping only CPU/RAM (e.g. 8/64 → 16/80 while leaving flavor-1 disks) yields
  **"Unsupported CPU/Memory/Disk configured"** on the console and **RKE2 never
  starts** (CLI: `connection to 127.0.0.1:6443 refused`, RAM sits near 0). Recovery:
  power off, set resources back to the installed flavor, power on. To actually move
  flavors you must grow the data disks too — a real storage migration.

---

## 10. Operations

- **CLI:** `ssh <cli-user>@<mgmt-ip>` (restricted appliance CLI; `show node`,
  `show pod` work; `?`/`help` don't — use interactive `space?` completion). No
  shell/`kubectl`.
- **Memory:** the 8/64 floor is genuinely tight — OpenSearch + Kafka + Postgres +
  Redis + ~70 JVM microservices on one node. RAM climbs with log volume. **You
  cannot just add RAM** (flavor lock, §9). Relieve pressure by **cutting log load**:
  shorter retention, specific log categories instead of `category all`, fewer
  chatty devices. A true bump means a full flavor-2 migration.
- **Snapshots:** `qm snapshot <vmid> <name>` before any change. `protection: 1` +
  the `protected` tag block deletion, not stop/config/start.

---

## 11. Rollback

- Config-only issues (wrong DNS/NTP baked in the ISO): re-run `--no-run` with the
  fix, copy the new ISO over the cdrom, reboot — disks/imports stay.
- Full rollback: `qm rollback <vmid> <snapshot>` (restores disks **and** the VM
  config, e.g. CPU/RAM, from snapshot time).
- Remove: `qm stop <vmid> && qm destroy <vmid>` (clear `protection` first; never
  destroy a `protected` guest you didn't create). No libvirt state remains.
