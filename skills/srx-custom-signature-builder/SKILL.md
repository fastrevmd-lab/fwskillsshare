---
name: junos-custom-signature-builder
description: Designs, validates, and safely deploys a new custom Junos IDP signature for a specific vulnerability or attack pattern via the Junos MCP Server — covering the check-existing-coverage-first step, context/pattern/action selection, and the monitor-mode-before-enforcement workflow. Use whenever the user wants to detect something a scanner (Nuclei, nikto, a pentest) found that isn't already covered, wants to write a custom-attack signature, or asks to extend IDP coverage for a new finding. Complements junos-idp-triage, which analyzes logs against signatures that already exist — this skill is for when the signature doesn't exist yet.
---

# Building a Custom Junos IDP Signature

Turns a specific finding (an exposed path, an injection technique, an
auth-bypass pattern) into a working, validated custom IDP signature —
built on a project that spent real time on false starts here, so the
steps below encode what actually failed and why, not just what worked.

## Step 0 — Is this even worth a custom signature?

**Check whether Juniper already covers it first.** Writing a duplicate
signature is wasted effort, and the predefined database is larger than
intuition suggests (tens of thousands of entries).

- Get a current export from HPE's Threat Labs portal (Juniper's IPS
  signature database, now hosted under the HPE brand):
  `https://www.hpe.com/h41379/threatlabs/ips-signatures` — this is a
  paginated web page, not a direct download link, so the CSV must be
  exported/downloaded through the page itself. Confirm the column
  headers still match (`signature_name`, `signature_type`,
  `signature_category`, `signature_description`, `signature_severity`,
  `signature_keywords`, etc.) before reusing the parsing approach below,
  in case the export format changes in a future refresh.
- If a full signature-database export (CSV) is available, search it
  directly with a script (Python's `csv` module handles the nested
  quoting correctly; naive `grep` misses fields). Search `name`,
  `display_name`, `description`, and `keywords` for the finding's
  keywords and close synonyms — a single keyword pass misses real
  matches (e.g. "gitignore" alone won't find a signature keyed on
  "git-config-disclosure").
- If no export is available, do **not** trust interactive
  "browse the database" commands — `show security idp attack
  attack-list ...`, `show security idp security-package
  predefined-attacks filters ...`, and `show security idp
  attack-group predefined` all failed identically (`syntax error,
  expecting <command>`) through this MCP relay across multiple
  attempted syntaxes, despite being documented Junos commands. This
  looks like a limitation of the relay's command parsing for this
  sub-hierarchy, not a real syntax error — don't keep trying variants
  of it.
- The reliable alternative: **propose a candidate predefined-attack
  name directly in a rule and see if the commit accepts it.** Junos
  validates attack names against the loaded database at commit time —
  an invalid name is rejected outright, a valid one commits cleanly.
  Use `dry_run` (via a template-apply tool that supports it, or a
  throwaway commit you're prepared to revert) to check without
  committing for real. This only tells you a *guessed* name exists or
  doesn't — it's not a search, so don't lean on it to explore broadly.
- Test whatever you find against real traffic before trusting it —
  a name matching by convention doesn't guarantee it matches your
  specific payload shape. (One pass at this project tested the full
  `HTTP - All` predefined group live against real traffic specifically
  to get an exhaustive negative result, not just a documentation-based
  guess.)

**Is the finding even detectable this way at all?** Signature matching
works on byte patterns present in traffic. Three categories don't fit:

- **Absences** — missing security headers, missing cookie flags. There's
  no pattern to match against something that isn't there. This is a
  WAF/header-injection or app-config fix, not an IDP signature.
- **Business-logic/authorization flaws** — e.g. viewing another user's
  data by changing an ID. The request is byte-for-byte identical to a
  legitimate one; only *which resource* it asks for is wrong. No network
  signature can distinguish that.
- **Fingerprinting/tech-detection** — identifying what a server runs
  isn't itself malicious traffic.

If the finding falls in one of these, say so plainly rather than forcing
a signature that will never fire meaningfully.

## Step 1 — One signature, or two?

If the finding has a **recon step and a separate exploitation step**
(a directory listing that *reveals* a sensitive file, vs. actually
*fetching* that file), consider two signatures rather than one:

- The recon/disclosure step → `severity info`, permanent `no-action`.
  Worth logging, not worth blocking — browsing a listing isn't itself
  damage, and blocking it has no real security benefit.
- The exploitation step → `severity major` (or higher), moves to
  enforcement once validated. This is the step with real impact.

This split makes the eventual policy more defensible to explain (why
one thing is monitored forever and another gets blocked) than lumping
both into one rule.

## Step 2 — Choose context and direction

Junos IDP contexts are more specific than they first appear, and guessing
wrong doesn't fail loudly — it just silently never matches.

- **HTTP contexts are method-specific.** `http-get-url-parsed`,
  `http-post-url-parsed`, `http-head-url-parsed` are real; a generic
  `http-url-parsed` (no method prefix) is accepted at commit but does
  not behave as a catch-all — don't assume it covers what the
  method-specific ones do.
- **`http-post-variable-parsed`** matches individual POST form field
  values specifically — reliable and fast for form-based payloads
  (command injection in a POST body, for example).
- **Generic, protocol-agnostic contexts exist and are useful when HTTP
  taxonomy is uncertain or the traffic isn't cleanly HTTP**: `stream`
  (matches anywhere in the reassembled TCP payload), plus `packet` and
  `line`. These bypass HTTP-parsing ambiguity entirely at the cost of
  being less targeted.
- **Direction matters and is easy to get backwards.** A signature
  matching a server's *response* (e.g. a directory-listing page's
  "Index of /" HTML) needs `direction server-to-client`, not the
  default assumption of client-to-server.
- Set `protocol-binding tcp` explicitly on generic contexts rather than
  leaving it implicit.

## Step 3 — Write the pattern defensively

- **Assume case matters.** Don't rely on the engine being
  case-insensitive. For a keyword that could appear either way, use
  character classes: `[Uu][Nn][Ii][Oo][Nn]` rather than `union`.
- **Match on substrings that survive encoding, not ones that don't.**
  Special characters (`<`, `>`, `=`) get percent-encoded in some
  transports; plain ASCII letters never do. A pattern matching `script`
  (bare word) survives whether the surrounding `<script>` tag is
  encoded or not; a pattern requiring the literal `<script` does not.
  When in doubt, drop the special characters from the match and keep
  the letters.
- **Keep patterns broad enough to catch variants, scoped by
  `destination-address` to limit blast radius** rather than trying to
  make the pattern itself narrow. A broad pattern scoped to one lab host
  is safe; the same pattern devicewide in production would need much
  more care about false positives — say so if this signature is heading
  anywhere near production traffic.

## Step 4 — Build in monitor mode first, always

```
set security idp custom-attack CUSTOM-<NAME> severity <info|major|...>
set security idp custom-attack CUSTOM-<NAME> attack-type signature context <context>
set security idp custom-attack CUSTOM-<NAME> attack-type signature protocol-binding tcp
set security idp custom-attack CUSTOM-<NAME> attack-type signature pattern "<pattern>"
set security idp custom-attack CUSTOM-<NAME> attack-type signature direction <direction>

set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match from-zone <zone>
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match source-address any
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match to-zone <zone>
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match destination-address <host>
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match application default
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> match attacks custom-attacks [ CUSTOM-<NAME> ]
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> then action no-action
set security idp idp-policy <policy> rulebase-ips rule BLOCK-<NAME> then notification log-attacks
```

Commit, then **wait ~20-30 seconds and verify compile** with
`show security idp status` — `Policy Name` populated and `Running
Detector Version` set. A successful commit message is not the same as
the policy being live on the data plane; this project hit that gap
repeatedly.

## Step 5 — Prove it matches, with real evidence

Generate the actual traffic this signature should catch, then check
`idp-log`:

- Check file size first (`file list detail`). Large files don't filter
  reliably through pipe modifiers on this relay (`| match`, `| last N`
  often return the whole file regardless) — either clear the log for a
  clean small pull, or fetch the whole thing and filter locally.
- **If the test creates state that could persist across runs** (a
  database record, a stored file, anything server-side that survives
  after this test ends), give your test payload a run-unique marker
  (a PID, a timestamp) rather than a fixed string. A fixed marker used
  across multiple runs will match an *old* success from a previous run
  and produce a false "it worked" even when the current attempt was
  genuinely blocked — this cost real debugging time on a persisted-XSS
  test where an earlier successful write stayed in the target
  application's database indefinitely.
- If nothing fires and you're confident the pattern is right, verify
  the surrounding plumbing before doubting the signature: **confirm the
  security policy's `application-services` binding to the idp-policy is
  actually still attached.** A missing binding produces total, silent
  detection failure — every signature, not just the new one — and looks
  identical to "my new signature doesn't match" until you check.

## Step 6 — Move to enforcement, then re-verify

Once monitor-mode matching is confirmed, flip the action. In this
project, `close-client-and-server` was the most consistently effective
choice across every signature tested; `drop-packet` and
`drop-connection` did not reliably outperform it for the same traffic
and are more indirect. Re-run the exact same test traffic and confirm
the client sees the connection actually fail (reset/refused), then
cross-check `idp-log` one more time for `action=CLOSE` on the fresh
attempt.

## Quick-reference: signatures built this way, this project

| Name | Context | Pattern idea | Direction | Action |
|---|---|---|---|---|
| `CUSTOM-HTTP-BRUTEFORCE` | `http-post-url-parsed` + time-binding | 5+ requests to a login path | client-to-server | close-client-and-server |
| `CUSTOM-SQL-INJECTION` | `stream` | `UNION`...`SELECT` | client-to-server | close-client-and-server |
| `CUSTOM-XSS-INJECTION` | `stream` | `script` / `onerror` / `onload` (bare words) | client-to-server | close-client-and-server |
| `CUSTOM-CMD-INJECTION` | `http-post-variable-parsed` | `&&`, `;`, `\|` | client-to-server | close-client-and-server |
| `CUSTOM-SQL-TAUTOLOGY` | `stream` | quote + SQL comment sequence | client-to-server | close-client-and-server |
| `CUSTOM-DIR-LISTING` | `stream` | `Index of /` | **server-to-client** | permanent `no-action` (info only) |
| `CUSTOM-SENSITIVE-FILE-ACCESS` | `stream` | `.bak`/`.old`/`.swp`/`.sql`/`.env` | client-to-server | close-client-and-server |
