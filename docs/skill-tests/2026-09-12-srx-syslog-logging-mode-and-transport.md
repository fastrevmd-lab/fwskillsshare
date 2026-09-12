# srx-syslog-logging — mode, transport and delivery-check validation

**Date:** 2026-09-12
**Skill:** `srx-syslog-logging` (1.0.0 → 1.1.0)
**Scope:** read-only operational commands plus non-activating `commit check`.
No configuration was activated on any device. No test events were generated.
**Authorization:** read-only + `commit check`, explicitly granted for this task.

This record closes the P0 item in `TODO.md`. It also **corrects that item's
premise**, which asserted something the devices do not do.

## Devices

| Device | Model | Junos | Security log config |
|---|---|---|---|
| `srx345` | SRX345-dual-ac (physical Branch) | 26.2R1.7 | none |
| `vsrx-ci` | vSRX | 24.4R1.9 | `mode stream`, `source-interface ge-0/0/0.0`, UDP + TLS streams |
| `vsrx-prod` | vSRX | 25.4R1.12 | `mode stream`, `source-address 192.168.1.240`, UDP 514 |
| `vsrx-br01` | vSRX | 24.4R1.9 | `mode stream`, `source-address 192.168.1.228` |
| `core-fw` | vSRX | 26.2R1.7 | `mode stream`, `source-interface ge-0/0/2.0`, TLS 6514 |
| `vsrx-dc` | vSRX | — | unreachable, `No route to host` |

Branch coverage is `srx345`, which is the lab's only physical SRX.

## What the TODO expected, and what the devices show

`TODO.md` stated:

> The current blanket statement that security logs always require a revenue
> interface is documented only for `mode stream`; `event` uses the control
> plane and `stream-event` uses both planes.

The implication — that the skill's "a revenue interface, always" was an
overclaim to be relaxed — **is not supported**. Junos rejects fxp0 for
`security log source-interface` irrespective of the configured mode:

```
set security log mode event
set security log source-interface fxp0.0
→ source-interface: 'fxp0.0': This interface cannot be configured for log,
  only revenue port is allowed
```

Measured on `srx345` (26.2R1.7) and `vsrx-ci` (24.4R1.9). The `mode event`
statement was present in the same candidate in both cases and made no
difference to the rejection.

Juniper's own CLI reference scopes the prohibition more narrowly — "You cannot
use fxp0 interface for stream mode irrespective of whether the fxp0 interface
is part of the default routing instance or mgmt_junos routing instance" — so
the CLI is **stricter than the documentation**.

Both statements are true of different things, and that is the correction the
skill now carries: `security log source-interface` is a forwarding-plane
statement that never accepts fxp0, while in `mode event` the Routing Engine
delivers over the **system syslog** path, where `system syslog source-address`
applies instead. The mode-awareness the TODO asked for is real; it is about
*which statement governs delivery*, not about relaxing the fxp0 rule.

Had the TODO been implemented as written, the skill would have told operators
they could source `mode event` security logs from fxp0. The CLI refuses that.

## Mode validity — `commit check`, non-activating

| Configuration | Device | Result |
|---|---|---|
| `mode event` | `srx345` | valid |
| `mode event` + `source-interface fxp0.0` | `srx345` | rejected, revenue port only |
| `mode event` + `source-interface fxp0.0` | `vsrx-ci` | rejected, revenue port only |
| `mode stream-event` + `source-interface ge-0/0/1.0` | `srx345` | valid |

Junos documents the three modes as: `event` — "Process security logs in the
control plane."; `stream` — "Process security logs directly in the forwarding
plane."; `stream-event` — "Process security logs in the control and forwarding
plane."

## Stream transport

| Configuration | Device | Result |
|---|---|---|
| `transport protocol udp` | `vsrx-ci` | valid |
| `transport protocol tcp` | `vsrx-ci` | valid |
| `transport protocol tls` + undefined `tls-profile` | `vsrx-ci` | rejected: `SSL profile must be defined under [services ssl initiation profile]` |

The TLS profile is an **SSL initiation** profile — the device is the client
connecting outward. Live TLS streams in the set use `transport protocol tls`,
`transport tls-profile`, `transport division line-based`, and port 6514 against
Security Director Cloud.

A combined UDP/TCP/TLS candidate on `srx345` returned **no verdict** — the
NETCONF reply could not be parsed (`unknown element directly inside rpc-error`).
That is recorded as neither pass nor fail. The individual protocol results above
are from `vsrx-ci`, where verdicts were returned cleanly.

## `show security log transport` — version gate and a caveat

| Device | Junos | Result |
|---|---|---|
| `vsrx-ci` | 24.4R1.9 | `syntax error, expecting <command>` |
| `vsrx-prod` | 25.4R1.12 | accepted |
| `core-fw` | 26.2R1.7 | accepted |
| `srx345` | 26.2R1.7 | accepted |

The 25.4R1 gate the TODO describes is confirmed, on both vSRX and Branch
hardware.

**But the command returned empty on every device that accepted it**, including
the `statistics` and `status` forms, while those devices were in `mode stream`
and generating logs. `show security log statistics` on the same devices did
return data — `vsrx-prod` reported `SCREEN 111913` generated, `FLOW 3275`,
zero discarded.

So the skill recommends `show security log statistics` to establish generation,
proof on the wire or at the collector for delivery, and treats
`show security log transport` as supplementary until seen to populate on the
operator's own platform and release. Why it is empty under `mode stream` on
these releases was not determined; establishing that would need either
documentation that explains the counter's scope or an activated `mode event`
configuration, which was outside this task's authorization.

`show security log report` is a syntax error on 24.4R1.9, 25.4R1.12 and
26.2R1.7 — including on `vsrx-prod`, which has `set security log report`
configured. The configuration statement and the operational command are not a
pair.

## Not covered

- **No test event was generated.** Delivery was not proven end to end to a
  collector in this run; the skill now requires explicit approval before
  generating one and prefers an already-occurring event.
- **`mode event` and `stream-event` runtime behaviour is unverified.** Every
  device in the set runs `mode stream`. Mode semantics are documentation-sourced;
  only their syntactic validity is measured.
- **Why `show security log transport` is empty under `mode stream`** is
  unexplained, as above.
- `vsrx-dc` was unreachable and contributed nothing.
