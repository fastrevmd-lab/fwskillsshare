# `set system processes ntp enable` — live validation across Junos 24.2 / 24.4 / 25.4 / 26.2

**Date:** 2026-08-27
**Method:** read-only operational commands plus non-activating `commit check` over NETCONF, via `rust-junosmcp`.
**Devices:** 13 reachable of 41 in inventory (one physical SRX345, twelve vSRX). No configuration was activated on any device.

## Question

Does Junos 24 and later require the hidden `set system processes ntp enable`
statement before NTP will synchronize? The claim matters because
`srx-initial-setup` treats `mgmt.ntp-absent` as **blocking**, and because a
skewed SRX clock silently breaks log delivery to Security Director Cloud and
Security Director On-Prem — the transport succeeds, the logs never appear.

## Result

**The statement is valid and is a real enable/disable toggle on 24.2 through
26.2. It is not, on the devices tested, a precondition for synchronization.**

`commit check` (loaded to candidate, validated, discarded — never activated):

| Device | Model | Junos | Statement checked | Outcome |
|---|---|---|---|---|
| `srx345` | SRX345 (hardware) | 24.2R2-S5.3 | `set system processes ntp enable` | valid — diff creates `system { processes { ntp enable; } }` |
| `vsrx-ci` | vSRX | 24.4R1.9 | `set system processes ntp enable` | valid — same diff |
| `dc-fw` | vSRX | 26.2R1.7 | `set system processes ntp disable` | valid — diff replaces `ntp enable;` with `ntp disable;` |

The third check is the one that establishes the semantics: `enable` and
`disable` are opposing values of one statement, so a device carrying neither is
in a third state — unset — and unset is not disabled.

## Fleet observation

| Device | Junos | `processes ntp enable` | `ntpd` running | `show ntp associations` | Time source |
|---|---|:---:|:---:|---|---|
| `srx345` (hardware) | 24.2R2-S5.3 | **absent** | yes | `*<ntp-a>` reach 377, offset −0.496 ms | NTP |
| `vsrx-ci` | 24.4R1.9 | **absent** | yes | `*<ntp-a>` reach 377, offset +0.451 ms | NTP CLOCK |
| `vsrx-br01` | 24.4R1.9 | absent | yes | all peers `.INIT.`, reach 0 | LOCAL CLOCK |
| `vsrx-br02` | 24.4R1.9 | absent | yes | all peers `.INIT.`, reach 0 | LOCAL CLOCK |
| `vsrx-core-a` | 24.4R1.9 | absent | yes | all peers `.INIT.`, reach 0 | LOCAL CLOCK |
| `vsrx-prod` | 25.4R1.12 | present | yes | `*<ntp-a>` reach 377 | NTP |
| `infra-vsrx`, `dc-fw`, `core-fw`, `core-b`, `br1-fw`, `br2-fw`, `br3-fw`, `edge-fw`, `edge-b`, `dmz-fw`, `legacy-dc-n0`, `demo-campus` | 26.2R1.7 | present | yes | `*` peer, reach 377 | NTP CLOCK |

Two findings fall out of this table.

**1. Synchronization without the statement is observed, on hardware and on
vSRX.** `srx345` (24.2R2-S5.3) and `vsrx-ci` (24.4R1.9) carry no
`system processes` configuration at all, run `ntpd`, and hold a selected peer at
full reach with sub-millisecond offset. "Junos 24+ will not sync without it"
does not reproduce on either.

**2. The three non-synchronizing devices are a reachability failure, not a
daemon failure — and the confound was checked rather than assumed.** All three
sit on 24.4R1.9 without the statement, which looks like corroboration until the
path is tested:

```
vsrx-br01> show route <ntp-a>          -> (no route)
vsrx-br01> show route 0.0.0.0/0             -> (no default route)
vsrx-br01> ping <ntp-a> count 3 wait 2  -> ping: sendto: No route to host  (100% loss)
```

`vsrx-br02` and `vsrx-core-a` return the same three results. These devices have
no path to their configured NTP servers, so they cannot distinguish the
hypothesis; they are `mgmt.default-route-absent`, not an NTP fault. Reporting
them as evidence for the process statement would have been wrong.

## Limits of this run

- **No counterfactual on 25.4 or 26.2.** Every device on those releases already
  carries `ntp enable`, and no device on either release was available to test
  without it. The claim may hold on 25.4+ and simply be untestable here; a
  25.4-or-later device that will not synchronize with reachability already
  proven is where to add the statement first.
- **No behavioral toggle test.** Whether committing `ntp disable` actually stops
  `ntpd` was not tested — the MCP surface exposes `commit check` only, and no
  device was a candidate for an activating write. Schema validity is proven;
  runtime effect is inferred from the statement's semantics.
- 4 of 41 inventory devices were unreachable (`No route to host`) and
  `vsrx-isp-a` failed on a `known_hosts` key mismatch; none were sampled.

## Changes made

- `srx-initial-setup` 1.3.0 → 1.4.0. `mgmt.ntp-absent` now proposes
  `set system processes ntp enable` alongside the servers, documents the hidden
  hierarchy and its three configured states, adds a "configured but never
  synchronizes" path-first troubleshooting sequence, and rewrites Stage 2
  verification to gate on `show ntp associations` rather than on the status
  word or on the statement's presence.
- `sd-onprem-proxmox-deploy` 1.1.0 → 1.2.0. §4a described the statement as
  "required" and listed its presence as a **gate**, which would fail `srx345`
  and `vsrx-ci` — both genuinely synchronized. Reclassified to supporting
  evidence, with `ntp disable` present as the hard fail.
