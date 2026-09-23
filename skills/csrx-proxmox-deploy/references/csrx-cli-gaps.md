# cSRX Operational CLI Gaps (vs vSRX)

Seven confirmed operational commands missing or silently non-functional in
**cSRX 26.2R1.7**, none producing a self-explanatory "command not found" error.

## Root causes

The missing `rpd` explains the `show route` and `show arp` gaps specifically;
the remainder reflect that cSRX has no chassis/RE object and a thinner
operational surface generally.

**Confirmed by reading the container's process table:** `srxpfe`, `mgd`,
`nsd`, `idpd`, `iked`/`ikemd`, `appidd`, `utmd`, `aamwd`, `casbd`, `pkid`,
`authd`, `useridd`, `rtlogd` and `ipfd` are present, but **no routing
daemon**. The security stack is whole; the routing stack is absent. Logging
is Linux `rsyslogd`, not Junos `syslogd`.

## The seven gaps

1. **`show interfaces terse`** — completely empty output: no rows, no header,
   no error, exit 0, even with interfaces up and actively passing traffic in
   both forwarding modes.
   **Substitute:** the full `show interfaces <ifname>` form.

2. **`show route`** — hard syntax error
   (`syntax error, expecting <command>: route`), not merely empty; a vSRX
   accepts it.
   **Substitute:** `show route forwarding-table`, which returns real
   connected/host entries.

3. **`show arp`** — hard syntax error
   (`syntax error, expecting <command>: arp`), not merely empty; a vSRX
   accepts it.
   **No working substitute was found.**

4. **`show interfaces <ifname> extensive`** — output **identical** to the
   plain form: no packet counts, no error/discard/collision counters.
   **No CLI substitute exists**; pull packet-level evidence from
   `/proc/net/snmp` or `tcpdump` on the endpoints instead.

5. **`show chassis routing-engine`** — hard syntax error
   (`syntax error, expecting <command>: routing-engine`). There is no RE
   object.
   **Substitute:** `show chassis hardware`, which *does* answer, reporting
   the container ID as the chassis serial and the `CSRX_SIZE` value as the
   Routing Engine description (e.g. `large memory`) — which makes it the one
   CLI command that reads back a `CSRX_*` runtime setting.

6. **`show system alarms`** — hard syntax error
   (`syntax error, expecting <command>: alarms`). No chassis, no alarm
   subsystem.
   **No substitute.**

7. **`show system uptime`** — rejected as
   `error: command is not valid on the csrx`.
   **Note:** this is the *only* gap that names the platform in its error,
   rather than failing as a generic parse error or silently; do not expect
   that message shape elsewhere.

## Commands verified working

The following commands **do** work and are worth relying on for a verification
plan:

- `show security flow session` / `status` / `statistics`
- `show security policies` (and `detail`)
- `show security zones`
- `show security nat source summary`
- `show chassis hardware`
- `show system storage`
- `show system license`
- `show log messages`
- `show route forwarding-table`
- The full `configure` / `commit` model

## Recommendation

Test the exact commands a verification plan depends on against the specific
cSRX build in hand before relying on them, and default to the Linux-side
fallback (`/proc/net/snmp`, `tcpdump`) rather than treating it as a last
resort.
