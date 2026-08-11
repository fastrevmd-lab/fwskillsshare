# Failure modes and their hypervisor causes

Chassis-cluster failures on a hypervisor rarely announce themselves. This table maps what you see to what is actually wrong.

| Symptom | Cause |
|---|---|
| Reths report `Up`, no traffic passes | per-NIC firewall enabled: anti-spoof rule versus the reth virtual MAC |
| Fabric never forms, or wedges under load | fabric segment below MTU 9000 |
| Secondary stays `ineligible` or `disabled` | control-link segment not isolated, or leaking into a data segment |
| Intermittent, or works in one direction only | NIC index to bridge/VLAN mapping differs between the nodes |
| Traffic stops after failover, returns in about five minutes | `neigh_suppress` on or `learning` off: gratuitous ARP lost, forwarding entry ages out |
| Nodes cannot see each other despite correct VLANs | `isolated` on, or `locked` / `mab` set on the port |
| Duplicate MAC complaints on the segment | two clusters sharing a cluster-id |
| The internet-facing segment dies the moment clustering is enabled | standalone-shaped guest promoted in place: second NIC became the control link and every index shifted |

---

## Reths up, no traffic

**Check on the hypervisor:**

```
qm config VMID | grep firewall=1
bridge fdb show | grep -i '00:10:db'
```

A non-empty first result, or an empty second result while reths report `Up`, confirms it.

**Check on the device:** `show chassis cluster interfaces` shows every reth `Up`, and `show chassis cluster statistics` shows session-create counters advancing on the primary while nothing arrives at the secondary.

**Remedy:** remove `firewall=1` from every cluster NIC and delete any `/etc/pve/firewall/VMID.fw`. The option is enabled by default when a NIC is added through the web UI, so it recurs whenever someone edits the guest there.

## Fabric never forms or wedges under load

**Check on the hypervisor:** `ip -d link show BRIDGE | head -2` — the fabric segment must be MTU 9000.

**Check on the device:** `show interfaces fab0 | match MTU` should report 9014 layer 2 and 9000 inet. `show chassis cluster statistics` should show fabric probes both sent and received; probes sent with none received points at the segment.

**Remedy:** raise the fabric bridge to MTU 9000. The control segment does not need it — see `proxmox-network-invariants.md`. Note that taps inherit the bridge MTU, so raising the bridge is sufficient for new taps, while running guests need their taps raised too or a restart.

## Secondary ineligible or disabled

**Check:** confirm the control VLAN carries only the two control-link taps. A control segment shared with data traffic, or bridged to anything beyond the two nodes, disrupts the heartbeat.

**Check on the device:** `show chassis cluster statistics` — heartbeat errors greater than zero, or received counts far below sent.

**Remedy:** give control its own VLAN with exactly two member ports.

## Intermittent or one-way

**Check:** the node symmetry diff in `proxmox-network-invariants.md`. Expected output is nothing.

**Remedy:** correct the mismatched NIC so both guests agree at every index. This failure is worth ruling out early precisely because interface state looks healthy on both nodes.

## Traffic stops after failover, returns in about five minutes

**Check:** `bridge -d link show` for the cluster taps — `learning` must be on and `neigh_suppress` off.

Five minutes is the tell. It is the default `ageing_time` of 30000, which is how long the bridge keeps forwarding to the departed node's port when nothing tells it to relearn.

**Remedy:** re-enable learning, disable neighbour suppression. Do not compensate by lowering `ageing_time`; that hides the fault and slows convergence for everything else on the bridge.

## Nodes cannot see each other despite correct VLANs

**Check:** `bridge -d link show` for `isolated on`, `locked on`, or `mab on`.

**Remedy:** clear them on cluster ports. These usually arrive from a host-hardening template written for tenant isolation, where preventing guest-to-guest traffic is the entire point — which is exactly what a cluster needs to do.

## Duplicate MAC complaints

**Check:** enumerate cluster-ids already in use on the segment. The reth MAC is `00:10:db:ff:<cluster-id x 16>:<reth number>`, so two clusters sharing an id collide on every reth.

**Remedy:** rebuild one cluster with a different cluster-id. It cannot be changed without `set chassis cluster cluster-id ... reboot` on both nodes.

## Internet-facing segment dies when clustering is enabled

**Check:** `qm config VMID | grep '^net'` before enabling. If the second NIC carries data, this will happen.

**Remedy:** redraw the NIC plan — see `vsrx-nic-mapping.md`. There is no in-place fix.

---

## Worked post-mortem: three independent faults

A pair of vSRX guests intended to become a chassis cluster, abandoned before completion. Each fault below was sufficient on its own.

**1. The fabric bridge was 1500.** Dedicated control and fabric bridges had been created — the right instinct — but the fabric one was left at the default MTU while Junos provisions its fabric interface to 9014. The control bridge was also 1500, and that was *correct*: control never needed jumbo. A build can hold a right and a wrong 1500 at the same time.

**2. The guests were never attached to those bridges.** Both had zero ports. The bridges existed in the host's network configuration and carried nothing.

**3. The guests were standalone-shaped.** Four NICs each: management plus three data VLANs, no control segment and no fabric segment. Enabling cluster mode would have consumed the first data VLAN as the control link and shifted the remaining two, so even completing steps 1 and 2 would not have produced a working cluster.

The instinct to build dedicated control and fabric segments was correct. What was skipped was the fabric MTU and the NIC re-plan — and because nothing surfaced an error, the attempt simply stopped rather than failing visibly.
