# junos-mcp-server behaviour that shapes this workflow

Verified against the Juniper/junos-mcp-server source (jmcp.py). Re-check if the
server version changes.

## Tools used and what they really do

| Tool | Behaviour that matters |
|---|---|
| `get_router_list` | Names returned here are the only valid `router_name` values. |
| `gather_device_facts` | PyEZ facts: hostname, model, version, serial. Use for Step 0. |
| `get_junos_config` | Runs `show configuration \| display inheritance no-comments \| display set \| no-more`. This is the baseline format `build_pair.py --baseline` expects. |
| `execute_junos_command` | Op-mode CLI only (PyEZ `dev.cli`). Config-mode commands such as `commit confirmed` or `rollback` cannot be run through it. |
| `execute_junos_command_batch` | Same command on several routers in parallel, JSON per-router results. Use it for side-by-side verification of both nodes. |
| `junos_config_diff` | Diff vs. rollback N (1-49). Use it after each commit as evidence. |
| `render_and_apply_j2_template` | Exclusive config lock. `apply_config=true, dry_run=true` = load + commit check + diff + automatic rollback. `dry_run=false` still runs commit check before committing. **Preferred push tool.** |
| `load_and_commit_config` | Loads and commits **immediately**. No commit check, no commit confirmed. Use it only for undo files, where speed matters more than the check. |

## Consequences

- **No commit confirmed.** Nothing auto-reverts if a commit cuts off management.
  The staged blocks therefore never touch `fxp0`, `system services`, `system login`
  or `mgmt_junos` (the lint enforces this). Every stage has a pre-rendered undo file.
  Out-of-band access to both nodes is a hard prerequisite.
- **Reboot is blocked by the server** (`block.cmd` blocks `request system reboot`,
  `halt`, `power-cycle`, `power-off`, `zeroize`). The user performs the reboot. Do
  not suggest editing the blocklist to get around this.
- **Config blocklist:** `set system root-authentication` and
  `set system login user … authentication` are rejected, so no stage may contain them.
- **Observed 2026-09-24 (a node after an upgrade reboot):** the first `gather_device_facts`
  hung for the full 4-minute client wait; an immediate retry with `timeout: 60` answered
  in about 1 s. Always pass a short `timeout` on the retry.
- **Idle pool timeout: 300 s by default** (`JMCP_POOL_IDLE_TIMEOUT`). After a reboot or
  any pause longer than ~5 min, the first call may fail. Retry once. If it fails again,
  ask the user to restart or re-engage the MCP server, then confirm with one
  `gather_device_facts` call before resuming.
- **Output handling:** `| display set` works (the server uses it itself). `| match`,
  `| last`, `| count` are not reliable through this path. Pull the whole output and
  read it. Results over ~1 MB get truncated, so query specific hierarchies
  (e.g. `show configuration chassis high-availability | display set`), not the full
  config, after the baseline is taken.
- **Pushing linted text through the J2 tool:** pass the rendered `stageN.set` file as
  `template_content`, `config_format: "set"`, and a one-key dummy mapping as
  `vars_content` (e.g. `skill: srx-mnha-mcp-builder`). **`{}` is rejected** with
  "Variables content is empty or invalid" (observed 2026-09-25). The files contain no Jinja
  syntax, so what the device receives is byte-for-byte what was linted.
- **Dry-run cumulatively.** A stage-2 dry run on a fresh node fails when it is run on its
  own, because it references stage-1 interfaces and zones. Dry-run stage 1 alone, and then
  1+2+3 concatenated. The tool rolls everything back after the check.
