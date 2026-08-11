---
name: srx-chassis-cluster-proxmox
description: Build and validate a Juniper SRX or vSRX chassis cluster whose two nodes are Proxmox VE guests. Use when planning bridges and VLANs for the control and fabric links, mapping virtual NICs to Junos interface names, bootstrapping cluster-id, configuring fab interfaces, reth interfaces and redundancy groups, or diagnosing a cluster that forms but passes no traffic. Not for Multi-Node High Availability.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, chassis-cluster, proxmox, kvm, linux-bridge, reth, fabric-link, control-link, mtu, high-availability, virtualization]
    related_skills: [srx-mnha, srx-policy, srx-nat, parsing-srx-configs, sd-onprem-proxmox-deploy]
  sources:
    - title: "Reference implementation: vsrx-fw01 chassis cluster on Proxmox VE"
      author: fastrevmd-lab
      note: "Original lab work. Every hypervisor and Junos value in this skill was measured on a healthy two-node vSRX cluster (cluster-id 2, Junos 24.4R1.9) running as Proxmox guests."
      retrieved: "2026-08-11"
---

# SRX Chassis Cluster on Proxmox VE

## Overview

Chassis cluster joins two SRX nodes into one logical chassis: a shared configuration, active/backup control plane, redundancy groups that move ownership on failure, and reth interfaces carrying a virtual MAC. Juniper documents it for two physical appliances joined by real cables.

On Proxmox VE the control link, the fabric link, and every reth leg are Linux bridge ports instead. That substitution is where clusters fail, and it fails quietly. Nothing logs "your bridge dropped this frame." The observable result is a cluster that forms and reports healthy while passing no traffic, or a fabric that comes up and then wedges under load.

This skill owns that hypervisor-to-Junos seam: bridge and VLAN design, virtual NIC to Junos interface mapping, the bridge settings that must hold, cluster bootstrap, and a validation sequence that catches silent filtering instead of trusting a green status line.

Use `srx-mnha` for Multi-Node High Availability, which is a different HA model with different failure modes. Use `srx-policy` and `srx-nat` for the security configuration riding on the reth interfaces, and `parsing-srx-configs` for full-configuration extraction.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`. For each unresolved material fact whose catalog
condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input`
before continuing or issuing an open-ended request. Ask at most three
single-select catalog questions per round. After each response, ask another
round whenever any unresolved material catalog condition remains true; continue
only when none remain. Do not repeat answered questions or show the full
catalog. Without a native tool, present each selected catalog question with its
2-3 labeled choices and a free-text `Other` path in concise plain text; do not
substitute a generic checklist. Never request secrets or unredacted customer
data. Treat intake answers as task context, not approval for a live change;
obtain separate explicit approval before configuration, commit, upgrade,
reboot, delete, or failover actions.

## Before you start

Three questions decide whether a build can succeed. Answer all three before touching a guest.

**1. Is there a jumbo-capable segment for the fabric?**

```
ip -d link show BRIDGE | head -2
```

The fabric segment needs MTU 9000. The control segment does not. If no jumbo bridge exists, creating one is step zero — see `references/proxmox-network-invariants.md`.

**2. Are the guests purpose-built for clustering, or standalone-shaped?**

```
qm config VMID | grep '^net'
```

If the second NIC carries data today, this VM cannot be promoted in place. In cluster mode the second NIC becomes the control link and every remaining interface index shifts. The NIC plan has to be redrawn. See `references/vsrx-nic-mapping.md`.

**3. Is the cluster-id free on this L2 domain?**

The cluster-id determines the reth virtual MAC. Two clusters sharing a cluster-id on one bridged domain produce duplicate MAC addresses.

## Procedure

### Phase 1 — hypervisor network

Build one portless, VLAN-aware bridge at MTU 9000 and give each function its own VLAN: one for control, one for fabric, one per reth. Verify each chosen VLAN ID is unused on that host before committing to it.

Bridge settings that must hold, and why each is load-bearing, are in `references/proxmox-network-invariants.md`. The short version: VLAN-aware, MTU 9000, STP off, forward delay 0, MAC learning on, flooding on, port isolation off, MAC locking off, neighbour suppression off.

### Phase 2 — guests

Clone from a template, then size the NIC list to the plan: management, control, fabric, and one per reth. Wire every NIC to its bridge and tag.

Two checks close this phase.

**No per-NIC firewall on any cluster NIC.** This is the single easiest way to break a cluster, because the option is enabled by default when a NIC is added through the web UI.

```
qm config VMID | grep -c 'firewall=1'
ls /etc/pve/firewall/VMID.fw
```

Expected: `0`, and no such file.

**The two nodes are identical apart from MAC addresses.**

```
diff <(qm config VMID_A | grep -E '^net[0-9]:' | sed 's/=[A-Fa-f0-9:]\{17\}//') \
     <(qm config VMID_B | grep -E '^net[0-9]:' | sed 's/=[A-Fa-f0-9:]\{17\}//')
```

Expected: no output. Any asymmetry produces a one-way blackhole that presents as an intermittent cluster.

### Phase 3 — cluster bootstrap

Boot both nodes standalone, reach each over its management interface, then set the cluster identity per node:

```
set chassis cluster cluster-id ID node 0 reboot
set chassis cluster cluster-id ID node 1 reboot
```

This is not configuration. It does not appear in `show configuration`, it does not roll back, and it determines the reth virtual MAC. Both nodes reboot into cluster mode.

After the reboot, confirm the interface mapping on this image before configuring anything — releases and images differ, and the mapping is the foundation everything else rests on:

```
show interfaces terse | match "^ge-|^em0|^fxp0"
```

### Phase 4 — cluster configuration

Node-specific identity comes from groups, because the two nodes share one configuration:

```
set groups node0 system host-name NAME-n0
set groups node1 system host-name NAME-n1
set apply-groups "${node}"
```

Then the cluster itself:

```
set chassis cluster reth-count N
set chassis cluster redundancy-group 0 node 0 priority 200
set chassis cluster redundancy-group 0 node 1 priority 100
set chassis cluster redundancy-group 1 node 0 priority 200
set chassis cluster redundancy-group 1 node 1 priority 100
set chassis cluster redundancy-group 1 preempt
set chassis cluster redundancy-group 1 interface-monitor INTERFACE weight 255
set interfaces fab0 fabric-options member-interfaces ge-0/0/X
set interfaces fab1 fabric-options member-interfaces ge-7/0/X
set interfaces ge-0/0/Y gigether-options redundant-parent rethN
set interfaces ge-7/0/Y gigether-options redundant-parent rethN
set interfaces rethN redundant-ether-options redundancy-group 1
```

Redundancy group 0 owns control-plane mastership; group 1 and above own data. Interface monitoring belongs on the data group only.

Use symmetric priorities such as 200/100. A wide split like 100/1 works but leaves the secondary with almost no margin and unable to preempt; `references/worked-example.md` documents a real cluster running that way and why not to copy it.

### Phase 5 — validate

Run the full sequence below. Do not stop at the first green line.

## Validation

| Check | Pass condition |
|---|---|
| `show chassis cluster status` | one primary, one secondary, no monitor failures |
| `show chassis cluster interfaces` | control link Up; `fab0` and `fab1` both Up/Up; every reth Up |
| `show chassis cluster statistics` | heartbeats incrementing, zero errors; fabric probes moving in both directions |
| `show interfaces fab0` | MTU 9014 / 9000, confirming the underlay accepted jumbo frames |
| `show system alarms` | no major alarms |
| `show version invoke-on all-routing-engines` | no version skew between routing engines |
| `bridge fdb show` on the hypervisor | reth virtual MACs present on the primary node's tap interfaces |
| `validate_chassis_cluster_health` | verdict `pass`, or `warn` only for a missing rescue configuration |

**A passing cluster status is not sufficient.** Reth interfaces report `Up` whenever their underlying links are up, including when the hypervisor is silently discarding every frame they send. Two checks catch that case and nothing else does: fabric probe counters moving in *both* directions, and the reth virtual MAC appearing in the bridge forwarding table.

```
bridge fdb show | grep -i '00:10:db'
```

An empty result while reth interfaces report `Up` is the anti-spoof signature. See `references/failure-modes.md`.

## Common pitfalls

Full symptom-to-cause mapping with per-row checks and remedies is in `references/failure-modes.md`. The two that account for most lost time:

- **Per-NIC firewall left enabled.** The reth virtual MAC never matches the assigned MAC, so the anti-spoof rule discards every reth frame. Reths report `Up`, no traffic passes, nothing is logged. Enabled by default in the web UI.
- **Fabric segment below MTU 9000.** Junos provisions the fabric interface to a jumbo MTU on its own. A 1500-byte segment cannot carry those frames. The control link genuinely does not need jumbo, so "set everything to 9000" is the wrong lesson — the asymmetry is the lesson.

A third deserves naming because it destroys working service: **promoting a standalone-shaped VM in place.** The second NIC becomes the control link, taking whatever data segment it used to carry, and every remaining interface index shifts by one.

## Reference material

- `references/proxmox-network-invariants.md` — bridge and VLAN design, the fabric/control MTU asymmetry and its mechanism, the anti-spoof trap, load-bearing port flags, node symmetry.
- `references/vsrx-nic-mapping.md` — virtual NIC to Junos interface mapping, the secondary node's slot model, and how to verify the mapping rather than assume it.
- `references/failure-modes.md` — symptom-to-cause table with checks and remedies, plus a worked three-fault post-mortem.
- `references/worked-example.md` — a complete healthy build to diff your own against, including its two known deviations.
- `references/runtime-intake.md` — intake question catalog.

## Source notes

This skill is original operational work, not a vendor-derived summary. Every hypervisor value, Junos MTU, interface mapping, and bridge flag recorded here was measured on a healthy two-node vSRX chassis cluster running as Proxmox VE guests: cluster-id 2, Junos 24.4R1.9, five reth interfaces, control and fabric on dedicated VLANs of a single portless VLAN-aware bridge.

Values that were measured are stated as measurements. Where behaviour is inferred from a mechanism rather than directly observed, the text says so. Vendor documentation covers chassis cluster on physical appliances; the hypervisor-side requirements collected here are not documented by the vendor and were established empirically.
