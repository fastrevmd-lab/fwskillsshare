---
name: junos-idp-triage
description: Analyzes Junos SRX IDP/screen logs via the Junos MCP Server to identify what's actually being detected, then recommends — and, after explicit approval, pushes — a policy change to move currently monitor-mode (no-action) IDP rules to enforcement. Use this whenever the user asks Claude to review logs on a Junos SRX, check for attacks, evaluate threats, investigate suspicious traffic, or recommend/apply a remediation policy on a device reachable via the Junos MCP Server — even for casual phrasing like "check the logs," "what's happening on the firewall," or "can we block this." Always consult this skill for Junos IDP log-analysis-and-remediation requests rather than improvising the log-pull sequence from scratch, since the MCP transport has several non-obvious limitations documented here that are easy to rediscover the hard way.
---

# Junos IDP Log Triage & Remediation

Reads what a Junos SRX's IDP/screen logs actually show, turns that into a
plain-language finding, and proposes a specific, reviewable config change —
never pushes anything without explicit human approval first.

## Scope: analyze and recommend, don't invent signatures live

This skill covers **triage of already-configured detection** (rules that
exist, most likely in monitor/no-action mode) and recommending a move to
enforcement. It does **not** cover writing new custom IDP signatures from
scratch in front of a live audience — that's an iterative, packet-level R&D
task (getting the right `context`, escaping patterns correctly, picking an
action that actually wins the race for the traffic shape in question) that
took many rounds of trial, error, and log cross-checking to get right even
with full tool access. If the logs show attack traffic that doesn't match
any existing rule, say so plainly and offer to scope that as separate work —
don't improvise a signature on the spot.

## Step 0 — Confirm connectivity and identify the target

```
get_router_list          (or equivalent MCP tool listing)
```

Confirm the target device is registered before doing anything else. If a
basic call like this fails or times out, don't retry blindly — see
"MCP connection gotchas" below.

## Step 1 — Establish current state before touching anything

Don't assume you know what's configured. Pull it fresh:

```
show security idp status
show configuration security idp idp-policy <policy-name>
```

From this, build a table of every `rulebase-ips` rule: its name, which
attack object(s)/dynamic-attack-group it matches, and its **current
action**. This tells you which rules are already enforcing vs. which are
in monitor mode (`no-action`) and are candidates for a recommendation.

## Step 2 — Pull logs, small and attributable

Prefer a dedicated, purpose-built log file over the generic `messages` log
— `messages` accumulates unrelated noise (management-plane SSH, routine
traffic) fast enough to bury the signal. If the environment has a
dedicated IDP or screen log file (check `show configuration system
syslog`), use that.

**Before pulling, always check size first:**
```
file list detail /var/log/<logfile>
```
If it's small (roughly under a few hundred KB), pull it directly:
```
show log <logfile>
```
If it's large (multi-hundred-KB to MB range), **don't try to filter it with
a pipe** — `| match`, `| last N`, and `| count` are not reliably honored
through this MCP command-execution path; they often just return the same
unfiltered content and you'll hit the tool's ~1MB result cap regardless of
what you append. Instead:
```
clear log <logfile>
```
...then ask the user to regenerate a small, fresh, attributable slice of
traffic (re-run whatever script/tool produces it), and pull the now-small
file. **Always read a log's content before clearing it if you actually
want to know what's in it** — clearing first destroys the evidence you're
about to go looking for. This is an easy, costly mistake to make twice.

## Step 3 — Parse and cross-reference

For each log entry, note: source IP, destination, matched rule name,
signature name, action taken, and the `repeat=` field. **`repeat=N` means
N+1 total coalesced matches were logged as one line, not N** — don't
undercount.

Cross-reference matched signature names against the table from Step 1 to
confirm which ones are currently in monitor mode. If working against a
known environment, use the reference table below rather than rediscovering
rule names.

## Step 4 — Synthesize the finding (plain language first)

Before any config, state in plain English: which source IP, what it did,
which signatures fired, over what time window, and how many times. Example
shape:

> Source `<source-ip>` triggered `<signature-A>` 3 times and
> `<signature-B>` 3 times against `<destination-ip>:<port>` between
> `<start-time>`–`<end-time>`. Both rules are currently in monitor mode
> (`action=NONE`) — nothing was blocked.

## Step 5 — One combined recommendation, not several sequential ones

Propose flipping **all** currently-monitor-mode rules relevant to the
observed traffic to enforcement in a single reviewed block, rather than a
rule-by-rule back-and-forth. For each rule needing a change:

```
delete security idp idp-policy <policy> rulebase-ips rule <rule> then action no-action
set security idp idp-policy <policy> rulebase-ips rule <rule> then action close-client-and-server
```

State clearly this is the exact command set you'd push, and **stop — do
not commit** until the user explicitly approves. Never treat "yes" to an
analysis request as approval to also push config.

## Step 6 — After approval: push, then verify the data plane actually caught up

```
load_and_commit_config   (with the exact commands from Step 5)
```

A successful commit message does **not** mean the change is live for
traffic yet — IDP policy changes need to recompile onto the data plane,
which commonly takes ~20–30 seconds. Wait, then verify before telling
the user it's ready:

```
show security idp status
```

Look for `Policy Name` and `Running Detector Version` populated — that's
the signal the new policy actually compiled, not just that config was
accepted. Don't skip this; a config that looks committed can still be
running the old compiled policy for a short window.

## Step 7 — Offer to demonstrate

Suggest re-running whatever attack-generating script/tool produced the
original evidence, so the before/after is visible, and offer to pull the
log again afterward to confirm the new action (e.g. `CLOSE` or `DROP`
instead of `NONE`) actually appears.

---

## MCP connection gotchas (learned the hard way)

- **Async commands** (e.g. signature package download/install) return
  immediately with "processing in async mode" — poll with a `... status`
  follow-up command rather than assuming completion.
- **Binary content does not survive this transport.** `monitor traffic
  read-file`, raw `file show` of a pcap, or anything else that isn't
  guaranteed printable text will fail with XML/PCDATA parsing errors. Stick
  to `show log`, `show configuration`, and other plain-text operational
  commands.
- **Some config values reject special characters** that would be fine
  elsewhere in Junos — e.g. packet-capture filenames can't contain `.`,
  `/`, `%`, or spaces. If a commit fails with a specific "must not contain"
  error, that's usually the actual constraint, not a deeper problem — just
  adjust the value and retry.
- **The connection can go unresponsive mid-session** without warning —
  sometimes as a slow timeout (~4 minutes) on a specific call, sometimes as
  an immediate failure on *every* call including trivial ones. Known root
  cause in at least one deployment: the local MCP server pools connections
  per-router and closes them after ~305 seconds idle (visible in that
  server's own logs as `Pool: closed idle connection to <router> (idle
  305s)`). Any gap longer than ~5 minutes — a long recompile wait, the user
  running a script, an extended discussion — can trigger this. A couple of
  quick retries from the assistant side do NOT reliably self-heal it; if a
  basic, previously-working call (like `show security idp status` or a
  router list) suddenly fails, don't keep retrying more than once or
  twice — tell the user the connection likely needs a nudge on their end
  (restarting the local MCP server, or simply re-engaging the app), and
  verify with one simple call once they confirm before resuming real work.
  Practical mitigation: if a step is known to involve a long wait (e.g.
  asking the user to run an attack script), expect the next call to
  possibly need a retry-after-reconnect rather than treating it as a
  fresh failure requiring investigation.

---

## Reference: keep a known-environment cheat sheet, filled in per deployment

If you're running this skill repeatedly against the same device/policy,
maintain a short reference block like the one below with that
environment's real values, so you're not rediscovering rule names and
signature bindings on every run. Fill in your own policy name, rule
table, validated enforcement action, log file names, and attack source —
this is a template, not data:

**Policy**: `<idp-policy-name>`, active on `<device-name>`.

| Rule | Signature | Detects |
|---|---|---|
| `<rule-name>` | `<signature-name>` (context `<context>`) | `<what it matches>` |

**Validated action**: note here whichever action (`close-client-and-server`,
`drop-connection`, `drop-packet`) has actually been confirmed via
before/after log cross-checks to work reliably for this traffic shape —
don't assume one action generalizes from a different environment without
re-testing.

**Logs**: list the dedicated log files in use (not the general `messages`
log) and what each captures.

**Attack source**: the tool/script and target used to generate the
traffic this policy is meant to catch, if one exists.
