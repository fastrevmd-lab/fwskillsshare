---
name: csrx-proxmox-deploy
description: Deploy a Juniper cSRX container firewall as a Docker workload on a Proxmox VE KVM guest, in both secure-wire (L2 bump-in-the-wire) and routing (L3) forwarding modes, drawn from an end-to-end build rather than vendor documentation. Use when sizing the Docker host guest, setting the mandatory host CPU model, wiring cSRX data-plane interfaces through Docker macvlan networks, diagnosing a container that reports healthy with no forwarding plane at all, TCP that hangs or corrupts while ICMP passes cleanly, a deny policy that blocks traffic but logs nothing, a routing-mode rebuild with no addressable interface, rediscovering the CSRX_* environment-variable surface for a different image release, judging a throughput number against a known baseline, or verifying isolation and enforcement with a test that can actually fail.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [csrx, juniper, container-firewall, docker, macvlan, proxmox, kvm, dpdk, vsrx, crpd, secure-wire]
    related_skills: [srx-chassis-cluster-proxmox, srx-policy, parsing-srx-configs]
  verified_on:
    - release: "26.2R1.7 (cSRX)"
      host: "Proxmox VE 9.2.20, Docker CE on a KVM guest"
      date: "2026-09-22"
      note: "Verified in both CSRX_FORWARD_MODE=wire (secure-wire) and CSRX_FORWARD_MODE=routing. Not validated on any other cSRX release, nor on a second Proxmox estate."
---

# Deploying a Juniper cSRX Container Firewall on Proxmox VE

> **STATUS: draft (v0.1.0).** Every claim below comes from one end-to-end build
> on **Proxmox VE 9.2.20** running **cSRX 26.2R1.7** as a Docker container,
> exercised in both secure-wire and routing forwarding modes. It has **not**
> been repeated on a different cSRX release or a second Proxmox estate. No
> vendor release notes existed for the build this content is drawn from — the
> image's own init scripts were the source of truth throughout, and that
> method is preserved here (§ "Rediscovering the CSRX_* surface") so it
> transfers to a release this skill has not seen. Values in `<angle
> brackets>` are site-specific.

## Overview

> **The two findings that cost the most time, first in Gotchas below:** (1)
> Proxmox's default CPU model does not expose SSSE3, and cSRX's forwarding
> process hard-requires it even when its DPDK fast-path driver is not
> selected — the container comes up `Up` and healthy with **zero** forwarding
> plane underneath it. (2) Docker's default macvlan `bridge` mode structurally
> cannot deliver a frame addressed to a foreign MAC — exactly what a
> bump-in-the-wire firewall needs — regardless of promiscuous-mode settings on
> either end. The pre-power-on gate exists specifically to catch both before a
> live build re-discovers them the hard way.

cSRX ships as a Docker image, not a VM appliance — there is no qcow2, no raw
disk, no ISO. Deployment is therefore: build a **KVM guest** (not an LXC —
cSRX runs `--privileged` and manipulates its own network namespace, which an
LXC's nesting makes unworkable to debug) running Docker CE, with one
management NIC and at least two data-plane NICs; wire the data-plane NICs to
Docker **macvlan** networks in `passthru` mode; and run the cSRX container
against that image with the `CSRX_*` environment-variable surface set for
the chosen forwarding mode. Junos configuration then proceeds through the
container's own CLI exactly as on a vSRX, with the CLI-surface gaps noted
below.

Two forwarding modes exist, selected once at container-run time and not
convertible in place:

- **`CSRX_FORWARD_MODE=wire`** — secure-wire: a true Layer-2 splice between
  two interfaces. No `family inet`, no routing; the two segments it bridges
  must already share one IP subnet.
- **`CSRX_FORWARD_MODE=routing`** (the default) — Layer-3, with the same
  interface/zone/policy model as a vSRX, but **no auto-created logical
  unit** — addressing is mandatory, not a fallback.

## Artifacts

| Artifact | Role |
|---|---|
| cSRX Docker image (e.g. `csrx:<version>`) | The entitled image tarball, loaded with `docker load`. Distributed behind a signed, time-limited download URL — do not reproduce that URL, and do not commit the tarball. |
| Licence file | Referenced by path via `CSRX_LICENSE_FILE`, typically bind-mounted into the container. Reference it by path/environment variable only — never reproduce its contents or any embedded identifier. |

## Requirements

- A KVM guest (not an LXC) running Docker CE, with **CPU model set to pass
  through the host's real features** — mandatory, not an optimization; see
  the pre-power-on gate.
- At least **one management vNIC** and **two data-plane vNICs**, one per
  side of the firewall. `CSRX_PORT_NUM` forces a minimum of 3 data-plane
  ports when `CSRX_FORWARD_MODE=wire`.
- Each data-plane vNIC's Proxmox-side parent interface **administratively
  up** with no IP address of its own — see Gotcha 9.
- Docker CE installed non-interactively (`DEBIAN_FRONTEND=noninteractive` for
  every install that might carry an interactive postinst — see Gotcha 13).
- The entitled image tarball and, if licensing is required, a licence file
  reachable by path inside the guest.
- A rough idea of the expected throughput envelope before testing — see
  "The performance envelope" — so a slow-but-correct result is not mistaken
  for a bug.

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

## Mandatory pre-power-on gate

> **STOP — verify all five before the container's first `docker run`.**
> Items 1 and 2 are the two findings above; getting either wrong produces a
> container that looks healthy and passes no traffic, with no error that
> names the real cause.

1. **The Docker host guest's CPU model passes through the host's real
   features** (on Proxmox: `qm set <vmid> --cpu host`), and the guest has
   been **cold-restarted** (`qm stop` / `qm start` — not a soft reboot; a CPU
   model change never applies to a running VM). Confirm `ssse3` is present
   in the guest's `/proc/cpuinfo` after the restart.
2. **The macvlan networks that will carry cSRX's data-plane interfaces are
   planned as `-o macvlan_mode=passthru`**, one network per parent NIC — not
   the Docker default `bridge` mode. Decide this before the first `docker
   network create`, because switching an already-running container from
   `bridge` to `passthru` networks is **not** sufficient by itself (Gotcha
   2) — plan for a `docker restart` of the container as part of that change,
   not as an afterthought.
3. **Checksum/segmentation offload will be disabled at every hop** between
   the two endpoints and cSRX's data-plane interfaces — the container-side
   veth peers and the hypervisor's own tap devices — before any TCP test is
   trusted. Confirming this is planned, not deferring it until a TCP test
   hangs.
4. **The forwarding mode is decided** (`wire` vs `routing`) before interface
   configuration begins — secure-wire forces a same-subnet, non-routed
   topology and rejects `family inet` outright; routing mode requires
   explicit `unit`/`family`/`address` on every data interface with no
   auto-creation. Changing the mode later is a rebuild of the interface
   configuration, not a toggle.
5. **The licence file, if used, is referenced by path/environment variable
   only.** Confirm nothing that will be typed, committed, or logged during
   this deployment reproduces its contents or the image's signed download
   URL.

## Procedure

### 1. Rediscover the CSRX_* surface for the release in hand

Do this before writing any `docker run` line — do not assume the table in
`references/csrx-environment-variables.md` (drawn from 26.2R1.7) carries
forward unchanged. Method, in full there: read `/etc/rc.local`, then read
every script it sources **in full, not a grep** — at least one
release-critical variable (`CSRX_FORWARD_MODE`) lives inside a sourced helper
function, not as a literal string in `rc.local` itself.

### 2. Build the Docker host guest

```bash
qm create <vmid> --name <name> --ostype l26 --cpu host \
  --sockets 1 --cores <n> --memory <mb> \
  --net0 virtio,bridge=<mgmt-bridge> \
  --net1 virtio,bridge=<data-bridge-left> \
  --net2 virtio,bridge=<data-bridge-right>
# then a normal OS install/provision, Docker CE installed with
# DEBIAN_FRONTEND=noninteractive for every package (Gotcha 13)
```

Confirm each in-guest interface name against its MAC address
(`cat /sys/class/net/<if>/address`), not by position (Gotcha 10). Bring the
data-plane parent interfaces up with no address (Gotcha 9):

```bash
ip link set <data-if-left> up
ip link set <data-if-right> up
```

Apply the CPU-model change and cold restart per the pre-power-on gate before
proceeding.

### 3. Create the macvlan networks (passthru, not bridge)

```bash
docker network create -d macvlan \
  --subnet <left-subnet-cidr> --gateway <left-gateway> \
  -o parent=<data-if-left> -o macvlan_mode=passthru <left-network-name>

docker network create -d macvlan \
  --subnet <right-subnet-cidr> --gateway <right-gateway> \
  -o parent=<data-if-right> -o macvlan_mode=passthru <right-network-name>
```

One network per parent NIC — `passthru` gives a single child the entire
parent, which is why only one network per parent is valid.

### 4. Disable offload on every hop before any TCP test

```bash
ethtool -K <iface> tx-checksum-ip-generic off tso off gso off
```

Apply to the container-side veth peers of both endpoints **and** the
hypervisor's tap devices for the data-plane vNICs — all hops need it, or the
handshake completes while data segments still fail. **Does not survive a
reboot of either endpoint or the Docker host guest** — re-verify after any
reboot (Gotcha 3).

### 5. Run the cSRX container

```bash
docker run -d --name <container-name> --privileged \
  -e CSRX_FORWARD_MODE=<wire|routing> \
  -e CSRX_SIZE=<size> \
  -e CSRX_PACKET_DRIVER=<interrupt|dpdk|poll|virtio> \
  -e CSRX_LICENSE_FILE=/config/license.lic \
  -v <host-licence-path>:/config/license.lic:ro \
  <image>:<tag>

docker network connect <left-network-name> <container-name>
docker network connect <right-network-name> <container-name>
docker restart <container-name>   # mandatory — see Gotcha 2
```

To load a startup configuration, bind-mount it at `/config/juniper.conf`
directly, or set `CSRX_JUNOS_CONFIG` to a path the image loads with `load
merge` — **not** `CSRX_JUNIPER_CONFIG`, which is silently discarded (Gotcha
5).

### 6. Configure interfaces, zones, and logging

Routing mode requires explicit addressing on every data interface — nothing
is auto-created:

```junos
set interfaces ge-0/0/0 unit 0 family inet address <left-addr>/<prefix>
set interfaces ge-0/0/1 unit 0 family inet address <right-addr>/<prefix>
set security zones security-zone <left-zone> interfaces ge-0/0/0.0
set security zones security-zone <right-zone> interfaces ge-0/0/1.0
set security zones security-zone <left-zone> host-inbound-traffic system-services ping
```

Secure-wire mode never takes `family inet` — configure it as a Layer-2
splice between two interfaces on the same subnet instead.

Commit local logging explicitly before relying on any log-based check — this
image ships with **none** by default (Gotcha 4):

```junos
set system syslog file messages any any
set security log mode event
```

### 7. Verify

Follow "Verification methodology" below — do not stop at "traffic passes."

## Gotchas (all hit in a real build)

1. **Container reports `Up`, every control-plane daemon looks healthy, but
   there is no data plane at all.** `docker ps` shows `Up`; `mgd`, `idpd`,
   `authd` are all running; the CLI answers normally — but `show security
   flow session` errors with `usp_ipc_client_open: failed to connect to the
   server`, and no traffic, not even ICMP under a permit-all policy, crosses.
   This reads exactly like a policy or IPC fault. **Cause:** the
   packet-forwarding process (`srxpfe`) initializes DPDK's EAL at startup
   **even when `CSRX_PACKET_DRIVER=interrupt`** — DPDK's EAL hard-requires
   SSSE3 unconditionally. If the hypervisor's default CPU model doesn't
   expose it, `srxpfe` fails at `EAL: unsupported cpu type` and never
   starts, while every control-plane daemon comes up fine. **Fix:** `qm set
   <vmid> --cpu host`, then a **cold** `qm stop`/`qm start` (a soft reboot
   does not renegotiate the CPU model). Confirm `ssse3` in
   `/proc/cpuinfo` and `srxpfe` actually running (`ps aux | grep srxpfe`)
   before trusting any subsequent ping test — **`Up` proves nothing about
   the data plane.** The only real proof is `show security flow session`
   succeeding, or `srxpfe` visibly in the process list.

2. **Traffic passes cleanly on plain Docker networks, then goes
   unidirectional or silent the moment interfaces move onto macvlan
   networks parented on real NICs.** ARP requests (broadcast) cross fine;
   ARP replies and all real unicast transit traffic vanish — with or
   without promiscuous mode set on either end. **Cause:** Docker's default
   macvlan mode is `bridge`. At the kernel level, `macvlan_handle_frame()`
   looks up the destination MAC in the macvlan port's per-child hash table;
   a frame addressed to a MAC that isn't a known child is dropped
   unconditionally, regardless of promiscuous mode. That is exactly the
   situation a bump-in-the-wire firewall creates: it needs to receive
   frames addressed to MACs that are not its own. **Fix:** create the
   macvlan network with `-o macvlan_mode=passthru`, which gives one child
   the whole parent NIC with no MAC filtering — one macvlan network per
   parent. **A live `docker network connect` from `bridge` to `passthru`
   networks on an already-running container is not sufficient by itself**
   — cSRX's boot-time tap↔interface MAC-pairing logic has already latched
   onto the old MACs, leaving traffic dead in both directions until a full
   `docker restart` of the container.

3. **TCP hangs or loses most of its data on a path ICMP crosses cleanly.**
   `ping` shows 0% loss; `iperf3` on the same path hangs indefinitely or
   transfers at a fraction of expected throughput with heavy retransmission.
   **Cause:** GSO/TSO and TX checksum offload left enabled on host-side
   virtual interfaces — the endpoints' veth peers and the hypervisor's tap
   devices. These offloads leave a placeholder checksum on the wire,
   expecting a NIC further down the chain to finish the calculation; through
   several layers of software bridging and cSRX's raw-copy forwarding path,
   nothing ever finishes it, and the segment arrives provably corrupt
   (confirm with `tcpdump -vv`: an identical placeholder checksum across
   packets with different sequence numbers). The receiving kernel silently
   drops these (`InCsumErrors` in `/proc/net/snmp`'s `Tcp:` line increments
   by exactly the SYN-retransmit count). ICMP carries its own checksum with
   no offload involved, so it's unaffected. **Fix:** `ethtool -K <iface>
   tx-checksum-ip-generic off tso off gso off` at **every** hop — one end is
   not sufficient. Confirm by watching `InCsumErrors` stop incrementing
   across a full transfer, not just by improved throughput. **Does not
   survive a reboot** of either endpoint — re-check, don't assume, before
   trusting any future throughput measurement on the same path.

4. **A deny policy is committed, traffic is genuinely blocked, but nothing
   shows in the log.** `then deny` + `then log session-init` commits
   cleanly; the matching traffic is confirmed blocked (100% loss, non-zero
   policy hit-counter) — but `show log messages | match RT_FLOW` returns
   nothing. **Cause:** this image ships with **no default local-logging
   configuration** — no `messages` file under `/var/log/`, and both `show
   configuration system syslog` and `show configuration security log` are
   empty by default on every freshly recreated container, not just first
   boot. `then log session-init` alone is not sufficient without a syslog
   destination and a security-log mode. **Fix:** commit `set system syslog
   file messages any any` **and** `set security log mode event` together, as
   part of the same commit as the interface/zone/policy config — not as a
   reaction to "the log is empty."

5. **`CSRX_JUNIPER_CONFIG` is silently discarded.** Its name looks exactly
   like the "supply startup config" knob; it is not. The init script
   unconditionally hardcodes it to `/config/juniper.conf` after sourcing the
   environment and before first use — anything supplied at `docker run`
   time is thrown away with no warning. **Fix:** use `CSRX_JUNOS_CONFIG`
   (loaded with `load merge` if the path exists) instead, or bind-mount a
   file directly at `/config/juniper.conf`.

6. **Secure-wire mode rejects `family inet` outright.** Committing an IP
   address on a secure-wire data interface is a commit error, not a warning.
   **Cause:** `CSRX_FORWARD_MODE=wire` is a true Layer-2 splice, never an
   IP-aware bump-in-the-wire — it forces the two segments it bridges to
   already share one IP subnet. Plan the topology around this before
   choosing wire mode, not after a commit fails.

7. **A routing-mode rebuild has no addressable logical unit at all.** After
   rebuilding into `CSRX_FORWARD_MODE=routing`, `show interfaces terse |
   match ge-` returns nothing, and the full `show interfaces ge-0/0/0` form
   shows the link physically Up with **no logical unit beneath it** — no
   `unit 0`, no `family`, nothing to address. **Cause:** cSRX does not
   auto-create a logical unit on its data interfaces when the forward mode
   changes; there is no auto-addressing fallback to fall back to. **Fix:**
   explicit interface configuration is mandatory — `set interfaces ge-0/0/0
   unit 0 family inet address ...` on every data interface, plus zone
   binding and whatever `host-inbound-traffic system-services` entries the
   interface itself needs to answer (at minimum `ping`, if the verification
   plan pings the interface's own address).

8. **cSRX's operational CLI is measurably thinner than a vSRX's — plan
   verification around this, don't assume parity.** Four confirmed gaps,
   none producing a self-explanatory "command not found" error:
   - `show interfaces terse` — completely empty output: no rows, no header,
     no error, exit 0, even with interfaces up and actively passing traffic
     in both forwarding modes. **Substitute:** the full `show interfaces
     <ifname>` form.
   - `show route` / `show arp` — hard syntax errors
     (`syntax error, expecting <command>: route` / `: arp`), not merely
     empty; a vSRX accepts both. **Substitute for routes:** `show route
     forwarding-table`, which returns real connected/host entries. No
     working substitute was found for `show arp`.
   - `show interfaces <ifname> extensive` — output **identical** to the
     plain form: no packet counts, no error/discard/collision counters.
     No CLI substitute exists; pull packet-level evidence from
     `/proc/net/snmp` or `tcpdump` on the endpoints instead.
   Test the exact commands a verification plan depends on against the
   specific cSRX build in hand before relying on them, and default to the
   Linux-side fallback rather than treating it as a last resort.

9. **A macvlan parent interface is administratively down, and nothing about
   the guest build brought it up.** A NIC meant to parent a Docker macvlan
   network shows `DOWN` in the guest, with no network-config stanza
   referencing it, even though the hypervisor reports the link connected.
   **Cause:** a provisioned guest typically only configures the
   interface(s) it was told to bring up (usually just management via DHCP);
   interfaces with no addressing intent are left exactly as the kernel
   presents them. **Fix:** a macvlan parent needs no IP address but must be
   administratively **up** — add a minimal, address-free stanza for it as
   part of the guest build itself, not the first time a macvlan network
   needs it, which conflates "did the interface come up" with "does the
   traffic work."

10. **The first virtual NIC does not get the interface name you'd expect
    from the others.** A guest with several vNICs on the same virtual bus
    does not necessarily name them with one consistent scheme — in this
    build the first (management) NIC came up as a plain `eth0` while the
    data-plane NICs came up as `ensNN` as expected. A udev/systemd
    naming-scheme quirk, not a hypervisor guarantee. **Fix:** never assume a
    naming pattern from NIC ordering — confirm each in-guest interface name
    against its MAC address (`cat /sys/class/net/<if>/address`), matched to
    the hypervisor's own record of which MAC was assigned to which vNIC
    slot, not by position.

11. **`qm guest cmd` (or the equivalent host-agent call) never answers, no
    matter how long you wait.** The guest has the guest-agent channel
    enabled (`--agent 1`), but every call fails permanently with `QEMU guest
    agent is not running` — not a timing issue; it never resolves.
    **Cause:** `--agent 1` only enables the **hypervisor-side** channel — it
    does not install the in-guest agent package, and common minimal cloud
    images don't ship it. **Fix:** add the package to first-boot
    provisioning, or resolve the guest's address from the hypervisor's own
    ARP/neighbor table by its known MAC (`ip neigh show <addr>`) instead.

12. **A NIC hot-added to an already-running container never actually comes
    up.** Its network config correctly shows the new interface with DHCP
    configured, but it never acquires an IPv4 address — only IPv6 SLAAC, if
    anything — and DNS/HTTP through it fails with errors that look like a
    DNS problem. **Cause:** hotplugging a NIC does not automatically trigger
    interface bringup (`ifup`) in every container OS/init combination, even
    with a correct static config present. **Fix:** explicitly `ifup <iface>`
    after adding it; verify with `ip -4 addr show <iface>` before
    proceeding.

13. **A package install appears to hang forever with `-y -qq` set.**
    `apt-get install -y -qq <package>` run non-interactively simply never
    completes — no error, no output, no timeout. **Cause:** `-y`/`-qq`
    silence apt's own prompts but not an interactive `debconf` dialog raised
    by a postinst script (e.g. "start this service as a daemon
    automatically?"). The install is genuinely blocked on a TTY prompt that
    will never be answered. **Fix:** always set
    `DEBIAN_FRONTEND=noninteractive` for any install that might ship an
    interactive postinst. If already stuck: kill the blocked process tree,
    run `DEBIAN_FRONTEND=noninteractive dpkg --configure -a` to finish the
    half-configured package, then retry with the frontend variable set for
    the whole invocation.

## The performance envelope

None of the gotchas above is "cSRX is slow" — deliberately. Single-digit-
Mbit/s TCP throughput on this stack is a **baseline, not a fault**. A reader
who measures a few Mbit/s and works through the gotchas looking for a cause
will most likely land on Gotcha 3 (`InCsumErrors`), find it already zero,
and have nowhere left to go.

> **Sample size: one run per mode, on one build.** These figures come from a
> single `iperf3` run in each forwarding mode on a single cSRX release and host.
> Run-to-run variance was never measured, so treat them as an order-of-magnitude
> expectation — "single-digit Mbit/s, not Gbit/s" — rather than a number to
> compare against precisely. The *relative* finding (routing roughly two orders
> faster than secure-wire, with `CSRX_SIZE` and `CSRX_PACKET_DRIVER` held
> constant) is the durable part; the absolute figures are one data point each.
> `CSRX_PACKET_DRIVER=poll` and `dpdk` were never benchmarked, so the driver
> hypothesis for the residual gap remains untested.

**Observed** (`CSRX_SIZE=large`, `CSRX_PACKET_DRIVER=interrupt`, identical
across both runs):

| Forwarding mode | Sender bitrate | Retransmits | `InCsumErrors` |
|---|---|---|---|
| Secure-wire (L2 bump-in-the-wire) | 210 Kbit/s | 166 | 0 |
| Routing (L3, static routes) | 8.81 Mbit/s | 3192 | 0 |

Both are roughly three orders of magnitude below line rate on what is
otherwise a local veth-chain path with no physical link in it — and neither
is a checksum-corruption symptom (`InCsumErrors` is 0 in both).

**What the ~42x mode gap does and does not establish.** Holding `CSRX_SIZE`
and `CSRX_PACKET_DRIVER` constant isolates the forwarding path as the only
variable between the two runs: if sizing or the interrupt-mode packet driver
were the dominant bottleneck, both modes would be roughly equally slow, and
they are not — routing mode's flow-based L3 path (route lookup, TTL
decrement, a real policy/session lookup) outperforms secure-wire's raw
byte-splice forwarding by roughly 42x under otherwise identical settings.

**What is still unexplained — do not present this as solved.** Routing
mode's own 8.81 Mbit/s is itself far below what a local veth path should
sustain, with zero checksum errors and a congestion window pinned near its
floor for the full transfer. The leading hypothesis is
`CSRX_PACKET_DRIVER=interrupt` — a non-DPDK, userspace, per-packet driver
crossing several virtualization hops — but this is **partly explained, not
settled**: the packet driver was never varied against a DPDK/poll-mode
alternative here, so that theory was never isolated the way the mode
comparison was.

**Practical takeaway.** Single-digit Mbit/s in routing mode, or low hundreds
of Kbit/s in secure-wire, with `InCsumErrors` at 0, matches this baseline —
not a new bug. A number *below* this envelope, or a nonzero `InCsumErrors`,
is the actual signal worth investigating.

## The cRPD finding — read from the image, never executed

**Explicitly unverified — do not treat this as a working configuration.**
Included because it changes what "cSRX and cRPD are unrelated products"
means, and is the strongest lead toward a future Kubernetes/CNF-style
deployment — not because it was tested.

Evidence, found while inspecting the image for the `CSRX_*` table: the
data-plane process (`srxpfe`) reads a `CSRX_CRPD` environment variable
(`enable`/`disable`, default `disable`), validated the same way as every
other genuinely env-driven variable. The same binary carries this
log-format string: `CSRX_CRPD %s: action:%s proto:%d gw_ip: %s
linux_ifd:%d junos_ifd:%d dest:%s/%d` — route-programming instrumentation
with a `linux_ifd` → `junos_ifd` mapping, the signature of importing Linux
kernel FIB entries into the Junos-side forwarding table. That is exactly how
cRPD operates: it runs the actual routing protocol daemons and programs
routes into the **Linux** kernel routing table of whatever namespace it
shares, rather than a Junos RIB directly. With `CSRX_CRPD=enable`, cSRX's
dataplane appears built to consume routes from that shared table.

**What this does and does not establish.** It does not mean cSRX itself runs
any routing protocol — there is no `rpd`/cRPD binary in the cSRX image;
cRPD remains a separate container with its own entitlement. It does
establish that cSRX has a first-class mode for acting as the enforcement
dataplane behind a cRPD control plane in the same host/namespace, rather
than the two products being merely chained as independent boxes.

**Unverified:** the required deployment topology (shared namespace? sidecar
containers? a Kubernetes pod shape via Multus?); whether `CSRX_CRPD=enable`
needs a separate licence entitlement; and whether it works at all, in any
topology. This is a reading of a log-format string and an environment
default, not an observed behavior.

## Verification methodology

The reasoning for why a check is trustworthy matters as much as the command
— a test that cannot produce the opposite result proves nothing, and this
build hit that trap more than once.

**Every pass/fail check must be shown capable of the opposite result.** The
load-bearing pattern is a two-step gate: confirm traffic is **blocked** with
no policy in place, then confirm the identical traffic **passes** once a
permissive policy is committed, in that order. Proving pass without first
proving fail leaves open that the traffic was never actually being inspected
— it could be bypassing the device entirely, or the device might never have
been in the path. A permit-everything policy that passes traffic proves
only that packets flow, not that anything is enforcing on them. The same
discipline applies to a deny test: enforcement is not proven by "traffic
stopped" alone — it must be shown **blocked and logged, both** (Gotcha 4). A
policy that blocks traffic but produces no matching log line is ambiguous
between "nothing was denied" and "logging is silently off" until the
logging pipeline itself is confirmed configured.

**Why a plain cross-subnet `ping` is not an isolation test.** Before
trusting a later "traffic now crosses via the firewall" result, isolation
between the two segments has to be proven first — if they weren't really
isolated, that later result would be meaningless. The naive test — `ping`
from one subnet directly to an address on the other, with no gateway
configured — cannot prove isolation either way: if the addresses are in
different subnets and no route exists, the kernel's routing-table lookup
fails immediately with `Network is unreachable` **before a single frame is
put on the wire** — the identical result whether the segments are genuinely
isolated or fully bridged together. **The fix:** force the kernel to
actually try, by adding a temporary on-link route for the far address out
the near interface, then removing it immediately after. With a forced
route, the kernel ARPs for the far address onto the (allegedly isolated)
segment. If the segments are genuinely isolated, the ARP goes unanswered — a
real timeout, not an instant rejection. If they're secretly bridged, the ARP
gets answered and the ping succeeds. This is the first result in the whole
test that actually depends on the state of the thing being tested.

**Sampling timing matters for flow-session checks.** Flow-table entries can
expire within single-digit seconds for ICMP. A "show me the session" check
run immediately *after* a ping completes, rather than *during* it, can
legitimately read zero active sessions even though forwarding worked
correctly moments earlier — sample mid-test, not after.

## Day-2 operations

- **A forwarding-mode change is a rebuild, not a toggle.** Interface
  addressing, zone bindings, and policy all have to be redone; there is no
  live migration path from `wire` to `routing` or back.
- **The offload fix does not survive a reboot of any host in the path.**
  After any reboot of an endpoint or the Docker host guest, re-check
  `InCsumErrors` before trusting a throughput measurement — don't assume
  the earlier `ethtool -K` settings carried forward.
- **A container reporting `Up` is not a health check.** The routine health
  signal is `srxpfe` visibly running and `show security flow session`
  succeeding rather than erroring with `usp_ipc_client_open` — check this
  after any container restart, host reboot, or CPU-model change.
- **Before moving to a different cSRX release**, re-derive the `CSRX_*`
  surface for that image rather than assuming this build's table still
  applies — see `references/csrx-environment-variables.md`.
- **Keep the licence outside the image and out of version control.**
  Reference it only via `CSRX_LICENSE_FILE` and a bind mount.

## Rollback

Nothing outside the Docker host guest is modified by cSRX itself — its state
lives in the container's writable layer plus whatever config/licence paths
are bind-mounted in. Rollback is bounded:

- **Container-level:** `docker stop <name> && docker rm <name>` plus
  `docker network rm` for the macvlan networks it used. Recreate from the
  same image tag and the same `CSRX_*` values.
- **Host-guest-level:** if the CPU model or NIC configuration was changed,
  revert with `qm set` and a **cold** restart — a live reboot will not
  undo a CPU-model change either.
- **Image-level:** the entitled image was obtained behind a signed,
  time-limited URL. If it's removed (`docker rmi`) without keeping a local
  copy, it cannot be re-derived without going back through that
  entitlement flow — keep a local copy of the loaded tarball for the
  duration of any build that might need a clean re-run.

Take a Proxmox snapshot of the Docker host guest before changing its CPU
model or before loading a different cSRX release, since there is no
separate rehearsal rig documented here to fall back to.
