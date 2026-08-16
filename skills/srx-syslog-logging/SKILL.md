---
name: srx-syslog-logging
description: Configure and troubleshoot Juniper SRX/vSRX logging to an external collector or SIEM. Use when system syslog or security logs are not arriving, when choosing between fxp0 and a revenue interface as the log source, when working with mgmt_junos, or when onboarding to Security Director Cloud. Covers the RE vs PFE logging split and why a non-default syslog port can silently fail.
version: 1.0.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, syslog, logging, siem, fxp0, mgmt_junos, management-vrf, security-log, stream-mode, security-director-cloud, troubleshooting]
    related_skills: [parsing-srx-configs, srx-policy, srx-chassis-cluster-proxmox]
  sources:
    - title: "fxp0, management VRF, and syslog — background notes"
      local: references/fxp0-and-management-vrf.md
    - title: "Field notes: system syslog silently dropped on a non-default port"
      local: references/field-notes-non-default-port.md
      note: "Empirical, observed on vSRX 25.4R1.12; verify against your platform and release"
---

# SRX / vSRX logging to an external collector

## Overview

Getting logs off an SRX fails in confusing ways because **two independent
subsystems** produce them, over **two different data paths**, with different
rules. Most "my logs aren't arriving" problems are a mismatch between which
subsystem produces the log and which path it is being asked to take.

See [`references/fxp0-and-management-vrf.md`](references/fxp0-and-management-vrf.md)
for background on fxp0 and management routing instances.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and
available approved read-only evidence. If unresolved facts could materially
change safety, scope, correctness, confidence, or the requested output, read
`references/runtime-intake.md`.

For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request.
Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog.
Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist.
Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.

## The split that explains most failures

| | System syslog | Security log |
|---|---|---|
| Config | `set system syslog` | `set security log` |
| Produced by | **Routing Engine** | **PFE** (in `mode stream`) |
| Content | commits, logins, kernel, daemons (`UI_*`, `mgd`, `kernel`) | traffic and threat events (`RT_FLOW`, `RT_SCREEN`, `RT_IDS`) |
| Can use fxp0? | yes — the RE is wired to fxp0 | **no** — fxp0 is not part of the PFE |
| Typical volume | low | high |

Two consequences follow:

- **Stream-mode security logs cannot originate from fxp0.** This is structural,
  not a policy choice. Security Director Cloud will not configure security
  logging when the source is fxp0.
- **The two subsystems can behave differently on the same device at the same
  time.** A device streaming `RT_SCREEN` to a collector while its system syslog
  sends nothing is a normal and highly useful diagnostic signal — see below.

## The non-default port trap

**A non-default syslog port may be silently discarded when system syslog
egresses a revenue interface.** No error, no log message, no counter.

Observed on vSRX 25.4R1.12 and confirmed by single-variable test:

| Host entry | Packets on the wire |
|---|---|
| `host 198.51.100.10` (default port 514) | flows |
| same host, `+ port 5140` | **zero** |

Same device, same source address, same interface, and no security policy
involved either way. Only the port changed.

The same non-default port worked on a comparable device whose syslog egressed
**fxp0**, because fxp0 bypasses flow processing. So the rule is not "that port is
broken":

> Non-default syslog port + revenue-interface egress → may be silently dropped.
> Non-default port + fxp0 egress → works.

**If your collector listens on a non-default port and the device must log from a
revenue interface, the device may be unable to reach it.** Prefer 514 and
demultiplex at the receiver — by `msgid`, `appname`, or source address — rather
than by port.

Treat this as platform- and release-specific. Verify with the two-host test below
before designing around it.

## Choosing the source interface

Decide per log type, not per device:

- **System syslog** → fxp0 suits it well: low volume, RE-generated, bypasses flow
  processing. If fxp0 is in `mgmt_junos`, every reference needs
  `routing-instance mgmt_junos` or it silently fails to route.
- **Security logs** → a revenue interface, always. Required by the architecture,
  and by Security Director Cloud.

**Keep fxp0 on its own logical network.** Do not address it into a subnet a
revenue interface already owns. Junos does not install cross-routes between the
management and dataplane tables; the revenue interface keeps the active route and
the fxp0 address simply does nothing. The change appears ignored rather than
failed, which is easy to misread as "that wasn't the problem".

That constraint has a hard consequence: **if the collector sits on a subnet a
revenue interface already owns, fxp0 cannot reach it**, so system syslog must use
the revenue path — which brings the non-default-port rule into play.

## Diagnosing "logs are not arriving"

Work outward from the device; each step eliminates a class of cause.

**1. Is the device generating the event at all?**

```
show log messages | match "UI_COMMIT_COMPLETED|UI_LOGIN_EVENT" | last 5
```

Local file logging and remote host logging are independent. Local entries with no
remote delivery means generation is fine and transport is not.

**2. Is anything leaving the interface?**

Capture as close to the device as possible — on the hypervisor port, switch SPAN,
or upstream hop — rather than at the collector. That distinguishes "the device
never sent" from "something dropped it in transit":

```bash
tcpdump -nn -i <interface> "udp port 514" -c 5 -w /tmp/capture.pcap
```

Two traps produce false negatives here:

- **Filter narrowly.** An unfiltered capture on a busy segment fills its packet
  limit with mDNS and multicast noise in milliseconds and never sees syslog.
- **Ensure an event actually occurs inside the window.** Automation and MCP
  tooling commonly pool NETCONF sessions, so read-only commands generate no
  syslog at all. Force a real event — a commit, or a failed SSH attempt.

**3. Compare the two subsystems on the same device.**

If `RT_*` events arrive but `UI_*` events do not, the PFE path works and the RE
path does not. That single observation eliminates routing, the collector, the
network and the subnet, and points straight at the RE-specific rules: port,
routing instance, source interface.

**4. Isolate with a second host entry.**

The decisive test. Add a second syslog host on an unused address with **default**
settings, then capture:

```
set system syslog host 198.51.100.11 any info
```

If that entry delivers and the original does not, diff the two — the difference
is the cause. Add back one attribute at a time.

## Red herrings

Each of these was tested and eliminated during a real outage. They look
plausible and cost hours:

| Suspected | Why it was wrong |
|---|---|
| `system syslog source-address` | A working reference device had none; a failing device had it set correctly. Neither presence nor absence changed delivery. |
| Missing `junos-host` → zone policy | Adding a scoped permit, then broadening it to `application any`, changed nothing. RE traffic left the same zoned interface fine on port 514 with no policy at all. |
| Routing or reachability | `ping` and `traceroute` (which is UDP) both succeeded from the intended source address. |
| Stale `eventd` | `restart event-processing` produced a fresh pid and no change. |
| A loopback filter such as `PROTECT-RE` | Those are **input** filters; they cannot affect egress. |
| fxp0 left unaddressed | Addressing it into the revenue subnet had no effect at all — see the own-logical-network rule. |

The common thread: every one concerned *reaching* the collector. The actual fault
was that the RE never generated a packet.

**Confirm emission before debugging delivery.**

## Attribution: the hostname trap

Collectors key events on the syslog hostname. If a device still carries a golden
image placeholder:

```
set system host-name source-device
```

events arrive but cannot be attributed, and a strict ingest pipeline may reject
the hostname and store an empty observer field — the rows exist but trace to
nothing. Set a real hostname before declaring logging fixed:

```
set system host-name <device-name>
```

Verify at the collector, not on the device. "Packets are leaving" and "rows are
attributed to the right device" are different claims.

## Working configuration

System syslog, revenue-interface egress, collector reachable on the dataplane:

```
set system host-name <device-name>
set system syslog host 198.51.100.10 any info
set system syslog host 198.51.100.10 structured-data
set system syslog source-address 192.0.2.1
```

Note the deliberate absence of a `port` statement.

Security logs in stream mode from a revenue port — also what Security Director
Cloud requires:

```
set security log mode stream
set security log format sd-syslog
set security log source-address 192.0.2.1
set security log stream SIEM severity info
set security log stream SIEM format sd-syslog
set security log stream SIEM category all
set security log stream SIEM host 198.51.100.10
set security log stream SIEM host port 514
```

With `mgmt_junos` and system syslog via fxp0, add the routing instance to **every**
fxp0-dependent service — syslog, NTP, DNS, RADIUS, JIMS:

```
set system syslog host 198.51.100.10 routing-instance mgmt_junos
```

Verify platform support first. fxp0-in-VRF support has varied across SRX models
and releases; on some the statement is rejected with *"Referenced routing
instance must be defined under [edit routing-instances]"*.

## Device-write safety

Every change here is a config commit. Follow the repo's write policy:

1. Show the intended `set`/`delete` lines and get approval.
2. Use `show | compare` to review the diff before committing.
3. Prefer `commit confirmed <minutes>` when a change could affect the management
   path — an interface address, a routing instance, or a policy on the interface
   you are connected through. Confirm with a second commit once verified.
4. Verify against the collector afterwards, not just the device.

Adding an address to an interface, changing a routing instance, or altering a
policy on the management path can remove your own access. `commit confirmed`
converts that from an on-site visit into a wait.

## Verification checklist

Do not call it fixed until all four hold:

1. Packets observed leaving the device on the expected interface and port.
2. Rows present at the collector.
3. Rows attributed to the correct hostname — not empty, not a placeholder.
4. **Both** classes checked: an `RT_*` event and a `UI_*` event. One arriving
   says nothing about the other; they travel different paths.

A device with no transit traffic produces no `RT_FLOW`/`RT_SCREEN` at all. Absence
there is expected rather than a fault — generate traffic before concluding the
security log path is broken.
