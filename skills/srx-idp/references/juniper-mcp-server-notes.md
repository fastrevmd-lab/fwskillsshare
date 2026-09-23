# Juniper junos-mcp-server field notes

These notes apply to **Juniper's** MCP server,
[`Juniper/junos-mcp-server`](https://github.com/Juniper/junos-mcp-server),
checked against tag **v1.1.1**. Other Junos MCP servers behave differently —
confirm each item against the server and version you are actually using before
relying on it. Items marked **[unverified]** come from one contributor's lab
sessions and have not yet been reproduced.

## Tools

v1.1.1 exposes nine tools: `get_router_list`, `gather_device_facts`,
`execute_junos_command`, `execute_junos_command_batch`,
`execute_junos_pfe_command`, `get_junos_config`, `junos_config_diff`,
`render_and_apply_j2_template`, and `load_and_commit_config`.

## Commits have no rollback window

`load_and_commit_config` takes `router_name`, `config_text`, `config_format`
(`set`, `text`, or `xml`) and `commit_comment`. It locks, loads, diffs, and runs
a **plain `commit`**, rolling back only if the load or commit itself fails.
There is no `commit confirmed` and no dry run.

The repository's own article (`docs/junos-mcp-server-article.html`) describes
`commit(confirm=1)`; the handler in `jmcp.py` does not do that. Trust the code.

The only dry run is in `render_and_apply_j2_template`: with `apply_config=true`
and `dry_run=true` it runs a commit check, shows the diff, and rolls back.

Consequence for the skills: when the only write path is
`load_and_commit_config`, state that no automatic rollback exists and get
approval for a manual rollback plan before pushing.

## Idle connections are closed after about five minutes

The server pools one NETCONF connection per router and closes idle ones.
The timeout is configurable with `JMCP_POOL_IDLE_TIMEOUT` (default **300
seconds**), and a cleanup thread runs about once a minute — which matches the
observed log line `Pool: closed idle connection to <router> (idle 305s)`.

**[unverified]** After such a close, the contributor saw calls either hang for
about four minutes or fail immediately, including trivial ones, and quick
retries did not recover. If a previously working call such as `get_router_list`
suddenly fails:

- retry once or twice at most, then stop;
- tell the user the server likely needs restarting or re-engaging;
- confirm with one simple call before resuming real work.

Expect this after any gap longer than about five minutes — a compile wait, the
user running a traffic script, a long discussion — and budget for one
reconnect rather than treating it as a new fault. Raising
`JMCP_POOL_IDLE_TIMEOUT` on the server is the operator's call.

## Pipe modifiers are not reliable

**[unverified]** Through `execute_junos_command`, `| match`, `| last N`, and
`| count` were observed returning the same unfiltered output, so appending them
does not keep a large log under the tool's result size limit. Filter off-box, or
archive and read a copy (see the triage skill, Step 2).

## Binary output does not survive the transport

**[unverified]** Output that is not guaranteed printable text — `monitor
traffic read-file`, `file show` of a pcap — failed with XML/PCDATA parsing
errors. Keep to plain-text operational and configuration commands, and review
packet captures off-box.

## Asynchronous operations return immediately

Signature package download and install return "processing in async mode". Poll
the matching `... status` command until it reaches a terminal state; see
`srx-license-signature-maintenance`.

## Some values reject characters Junos accepts elsewhere

**[unverified]** Packet-capture filenames rejected `.`, `/`, `%`, and spaces. If
a commit fails with a specific "must not contain" error, that message is
usually the whole story — adjust the value and retry.
