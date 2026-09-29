---
name: srx-mnha-builder
description: Builds a new two-node Juniper SRX/vSRX Multi-Node High Availability (MNHA) pair end-to-end through the Junos MCP Server (junos-mcp-server). Selects the deployment mode (routing/L3 with eBGP, switching/default-gateway with VIPs, or hybrid) during setup, then does preflight discovery, a single pair sheet, rendered and linted per-node configs, staged commits with approval gates, the HA-activation reboot handoff, formation verification and failover testing. In L3 and hybrid modes it also builds the eBGP upstream and signal-route export. Use when the user wants to create, stand up, build, deploy, or bring up an MNHA pair, "turn these two SRXs into an HA pair", or configure chassis high-availability on devices reachable via MCP - even if they only name the two devices. For MNHA design theory or troubleshooting an already-running pair, use srx-mnha instead.
version: 0.1.0
author:
  - fastrevmd-lab
  - Claude
  - GPT
  - jgrizzuti
license: MIT
metadata:
  hermes:
    tags: [srx, vsrx, junos, mnha, high-availability, srg, icl, bfd, bgp, signal-route, vip, ha-link-encryption, jinja2, mcp, junos-mcp-server, approval-gate, failover-test]
    related_skills: [srx-mnha, srx-policy, srx-nat, parsing-srx-configs]
---

# SRX MNHA Pair Builder (via junos-mcp-server)

This skill turns two standalone SRX nodes into an MNHA pair. It uses the Junos MCP
Server's tools and never pushes anything without explicit approval. Design knowledge
(modes, SRGs, pitfalls) lives in the `srx-mnha` skill. This skill is about **choosing
the mode and building the pair in a safe order**.

**Scope:**
- A new pair, built from two nodes with no chassis cluster and no existing
  `chassis high-availability`. Existing interfaces, zones and an eBGP group may be
  reused if they match the pair sheet.
- SRG0 plus one SRG1.
- The ICL in the default routing instance, either on a dedicated link or as loopbacks
  over a shared data segment, encrypted or not.
- **Out of scope:** ICD, multiple SRG1+ groups, OSPF, security policies
  and NAT, and MNHA IPsec. MNHA IPsec will be its own skill.
- An existing IPsec setup on a node is left untouched. It stays tied to that node and
  will **not** fail over. Tell the user so, and never add `managed-services ipsec`.

**Naming:** Node0 maps to MNHA `local-id 1` and Node1 to `local-id 2`. Node0 gets the
higher `activeness-priority`, so it is the SRG1 ACTIVE node by default.

Read `references/mcp-transport-notes.md` before starting. Four facts from the server
source shape every step:
- there is no commit confirmed;
- `load_and_commit_config` commits without a commit check;
- the server blocks reboot commands;
- idle connections are dropped after 300 s.

## Runtime intake

Before starting the workflow, inspect the request, supplied artifacts, and available approved read-only evidence. If unresolved facts could materially change safety, scope, correctness, confidence, or the requested output, read `references/runtime-intake.md`. For each unresolved material fact whose catalog condition is true, invoke Claude `AskUserQuestion` or Codex `request_user_input` before continuing or issuing an open-ended request. Ask at most three single-select catalog questions per round. After each response, ask another round whenever any unresolved material catalog condition remains true; continue only when none remain. Do not repeat answered questions or show the full catalog. Without a native tool, present each selected catalog question with its 2-3 labeled choices and a free-text `Other` path in concise plain text; do not substitute a generic checklist. Never request secrets or unredacted customer data. Treat intake answers as task context, not approval for a live change; obtain separate explicit approval before configuration, commit, upgrade, reboot, delete, or failover actions.

## Step 0 - Targets and facts

1. Call `get_router_list` and confirm both device names exist exactly as the user gave
   them.
2. Run `gather_device_facts` on each node. **Stop** if the models or `version` differ.
3. Run `show chassis cluster status` on each node. **Stop** if either node is clustered.
4. Run `show chassis high-availability information` on each node. Expect *mode not
   configured*. If a node shows an MNHA configuration, it isn't a new node: stop and
   hand back to the user to clean it and reboot.
5. Ask the user to confirm they have **console / out-of-band access to both nodes**.
   This is a hard prerequisite, because nothing reverts a bad commit automatically.

## Step 1 - Baseline and safety net

1. Run `get_junos_config` on both nodes and save the output as `<router>.set`.
2. Run `request system configuration rescue save` on both nodes.
3. From the baselines, note:
   - free interfaces, and the interfaces that already exist with their addresses and
     zones
   - the `fxp0` addressing
   - any static default route
   - any existing autonomous-system number or BGP group

The baseline must be re-taken if anyone changes a node before Step 6. The undo files
are computed from it.

## Step 2 - Select the deployment mode

Ask this before anything else in the pair sheet, because the mode decides which
sections are required. If the client supports it, present the choice as tappable
options. Offer a recommendation based on what the user describes:

| Mode | `deployment-type` | Pick it when | Skill builds |
|---|---|---|---|
| **Routing (L3)** | `routing` | Neighbors are routers that can run BGP. No hosts use the SRX as their static gateway. | Signal routes, eBGP group, route-filtered export with MEDs. Activeness probe required. |
| **Switching (default-gateway / L2)** | `switching` | Hosts on a shared L2 segment use the SRX as their gateway, and there is no dynamic routing. | VIPs, uplink monitoring. No BGP. |
| **Hybrid** | `hybrid` | One side is an L2 host segment that needs a VIP; the other side is routed upstream. | VIPs, monitoring, signal routes and eBGP. |

To help the user choose, ask:
1. Do any directly attached hosts use the firewall's address as their static default
   gateway?
2. Can the upstream run eBGP with both nodes?

If the answers are yes / yes, the mode is hybrid. No / yes means routing. Yes / no means
switching.

Also point out the per-segment consequence (from `srx-mnha`): in routing mode, a host
whose static gateway is one node's own IP is stranded when that node fails. In switching
and hybrid modes, the vMAC moves on failover, so the adjacent switches must accept the
MAC move. Check MAC-move limits, Dynamic ARP Inspection (DAI) and storm-control.

### ICL questions (asked right after the mode)

**1. Dedicated or shared ICL?**

| ICL transport | What it is | Skill builds |
|---|---|---|
| **Dedicated** (recommended) | Its own back-to-back link, e.g. `ge-0/0/2` ↔ `ge-0/0/2`, /30 | Link addresses in a dedicated ICL zone |
| **Shared** | Loopback /32s reached over a data segment, used when no spare port or path exists | `lo0.<unit>` in the ICL zone, a static /32 route to the peer loopback, and HA/BFD (+IKE) host-inbound opened on the transport segment's zone |

**2. Encrypted or not?** Recommend encryption whenever the ICL is shared or crosses
anything the user doesn't control. It is optional on a dedicated back-to-back link.
Encryption uses Junos HA link encryption: an IPsec VPN with `ha-link-encryption`,
referenced by `peer-id … vpn-profile`. It has two prerequisites the skill cannot do
itself:
- **`junos-ike` package on both nodes.** Check the `show version` output for
  "JUNOS ike". If it's missing, the user installs it
  (`request system software add optional://junos-ike.tgz`); a reboot may be needed.
- **The pre-shared key, set by the user on both nodes via CLI**, before the baseline is
  taken:
  `set security ike policy MNHA-ICL-IKE-POL pre-shared-key ascii-text <key>`.
  The key never goes into the sheet, the chat or an MCP push. The lint fails until the
  line appears in both baselines. The skill then adds everything else: proposals,
  gateway, VPN, `vpn-profile`, and IKE host-inbound.

Field-confirmed 2026-09-25: the encrypted-ICL stanza (`ha-link-encryption` + `peer-id …
vpn-profile`) commit-checks on vSRX 24.4R2.21 (flat model). On the grid model (26.x) the
`vpn-profile` placement is not confirmed, so treat the device dry run as the authority there.

## Step 3 - Pair sheet

1. Copy `references/pair-sheet.example.yaml` and set `deployment_mode` first.
2. Fill the sheet from the facts and baseline. Ask the user only for what is still
   missing, at most three questions per round.
3. Never ask for secrets.

What each mode needs:
- **All modes:** `icl.transport` and `icl.encryption.enabled`, then ICL interface and IPs
  (dedicated) or segment, loopback unit and loopback IPs (shared), segments (the IFL name is shared; each node has
  its own address), activeness priorities.
- **Routing and hybrid:** `bgp` (local and peer AS, group, BFD, protected prefixes with
  a match type, transit subnets), per-node `bgp_neighbors`, and exactly one segment with
  `role: upstream`. Routing mode also needs a per-node `probe`.
- **Switching and hybrid:** `srg1.vips` (the VIP must sit inside that segment's subnet
  on both nodes) and `monitor_interfaces`.

If a BGP group, zone or interface already exists in the baseline, the sheet must match
it. The lint catches conflicts, such as a group that already exports another policy or a
different autonomous-system number.

## Step 4 - Render and lint (nothing touches devices)

**With code execution:**
```
python scripts/build_pair.py pair.yaml --out build \
  --baseline <NODE0>=<node0>.set --baseline <NODE1>=<node1>.set
```
Output per node:
- `stage1.set`: underlay, meaning the ICL transport, data segments, zones and host-inbound
  rules
- `stage2.set`: ICL crypto objects when encrypted, plus the HA stanza for the chosen mode
  and the flat or grid model
- `stage3.set`: eBGP and the export policy (routing and hybrid only)
- matching `undo-stageN.set` files
- a summary of how many lines each stage adds

Handling the report:
- **Any ERROR means stop.**
- WARNs need a one-line acknowledgment from the user.
- INFO lines are context for the user.

**Without code execution:**
1. Render the templates with `render_and_apply_j2_template` (`apply_config: false`) and
   per-node vars.
2. The tool takes a single template string, so paste the contents of
   `_srg1-common.set.j2` and `_icl-crypto.set.j2` in place of the `{% include %}` lines.
3. Walk the checks in `scripts/build_pair.py` by hand.
4. Write undo files manually. They must delete only what each stage adds.

## Step 5 - Dry run on devices

For every node, run `render_and_apply_j2_template` on stage 1 alone and on stages 1+2+3
concatenated (later stages reference earlier ones), with:
- `template_content` = the rendered stage text
- `vars_content: "skill: srx-mnha-builder"` (a dummy key; `{}` is rejected)
- `config_format: "set"`
- `apply_config: true, dry_run: true`

Also dry-run each `undo-stageN.set` against the current config. This shows exactly what
an undo would remove.

## Step 6 - Approval gate #1

1. Show the user the per-node diffs, the lint result and the undo files.
2. Get explicit approval to push Stage 1 and Stage 2. Approval of the design or the dry
   run is not approval to push.

## Step 7 - Stage 1: underlay

1. Push `stage1.set` with `render_and_apply_j2_template` (`dry_run: false`) on Node0,
   then on Node1.
2. Verify per `references/verification.md` → "After Stage 1":
   - ICL ping, including the 1400-byte DF ping
   - each segment's neighbor answers ping
3. If verification fails, run `undo-stage1` and diagnose before going on.

## Step 8 - Stage 2: HA stanza

1. Push `stage2.set` on Node0, then Node1.
2. Run `junos_config_diff` (version 1) on each node as evidence.

## Step 9 - Reboot handoff (approval gate #2)

The server blocks reboots, so the user does this step.

1. Ask the user to reboot **Node1 first**, then Node0 once Node1 is back.
   **Expected side effect:** while Node0 reboots, Node1 goes from HOLD to SRG1 ACTIVE and takes the
   VIP. With preemption off, it stays ACTIVE after Node0 returns, even though Node0 has the higher
   priority (field-confirmed 2026-09-25). Tell the user this before the reboot. If they want
   Node0 ACTIVE, a manual SRG1 failover (approval gate) restores it and doubles as the first
   failover test.
2. After each reboot, expect the first MCP call to time out. Retry once with a short
   `timeout`, then confirm the node with `gather_device_facts`.
3. On vSRX, if `show interfaces terse` lists no `ge-` interfaces, the user needs a full
   VM stop and start.
4. With an encrypted ICL, also check `show security ike security-associations` and
   `show security ipsec security-associations` for the ICL peer once both nodes are up.

## Step 10 - Verify formation

Run the "After Stage 2 + reboot" checks on both nodes with
`execute_junos_command_batch`. For switching and hybrid modes, also run the VIP checks.

- **Pass:** both ONLINE, Conn State UP, Cold Sync COMPLETE, and exactly one SRG1 ACTIVE,
  the higher-priority node.
- **Fail:** follow the diagnostic tree. The BFD permit comes first.

## Step 11 - Stage 3: eBGP (routing and hybrid; approval gate #3)

1. Get approval, then push `stage3.set` on both nodes.
2. The upstream router must have both nodes configured as neighbors. If the upstream is
   MCP-managed, read its config first. It often already has a group for Node0; the smallest
   change is to add Node1 as another neighbor in that group, after a dry run. Otherwise ask the
   user to configure it.
3. Verify:
   - BGP sessions established, with BFD up if configured
   - the **role-consistency invariant** in `references/verification.md`: the SRG1 ACTIVE node,
     the VIP holder, the node with the active signal route, and the upstream's selected BGP path
     are all the same node
4. Re-check the invariant after every failover or failback in Step 12. It is the pass criterion
   for "the failover worked".

## Step 12 - Failover test (approval gate #4, recommended)

Follow the failover section of `references/verification.md`. Confirm the
manual-failover syntax on the target release before running it. For switching and
hybrid modes, include the VIP move and the ARP refresh on a host in the checks.

## Step 13 - As-built report

Deliver:
- the pair sheet
- the per-node stage files
- key verification lines
- test results
- the rollback procedure: `undo-stage3` → `undo-stage2` → reboot (user) → `undo-stage1`,
  with the rescue config as the last resort from the console

## Guardrails

- Every push needs explicit, stage-specific approval.
- Push Node0 then Node1, and verify between stages.
- Never hand-edit staged files; change the sheet and re-render.
- Never touch `fxp0`, system services, logins or `mgmt_junos`.
- If a commit's result is unclear because the connection dropped, check
  `junos_config_diff` before retrying.
- Undo files are only valid against the baseline they were computed from.
