# Cisco Firepower Parsing Patterns and Behavioral Rules

## Action mapping

| Firepower action | Schema `action` | Note |
|---|---|---|
| `ALLOW` | `allow` | |
| `TRUST` | `allow` | bypasses deep inspection — record in `metadata` |
| `BLOCK` | `deny` | |
| `BLOCK_RESET` | `reset-both` | |
| `BLOCK_INTERACTIVE` | `deny` | interactive-block prompt not representable |
| `BLOCK_RESET_INTERACTIVE` | `reset-both` | interactive-block prompt not representable |
| `MONITOR` | `allow` + mandatory warning | **non-terminal — see below** |
| Prefilter `FASTPATH` | `allow` + mandatory warning | bypasses Snort entirely |
| Prefilter `ANALYZE` | not emitted as a policy | hands off to the ACP; record in `metadata` |

FDM uses `ruleAction` with values `PERMIT`, `TRUST`, and `DENY`, mapping to
`allow`, `allow`, and `deny` respectively. FDM has no `MONITOR`.

## MONITOR is non-terminal

A `MONITOR` rule logs and **continues** to the next rule. It does not terminate
evaluation. The shared schema has no non-terminal action, so mapping MONITOR to
`allow` tells a downstream consumer that the rule matches and stops — which it
does not.

This is the same defect class the 2026-07-31 live-SRX round found with
`match dynamic-application`: dropped narrowing collapsed distinct rules into
false duplicates and made a scoped deny read as a terminal deny-all.

Required behavior:

- Emit one `metadata.warnings` entry per MONITOR rule, naming the rule.
- State in the parse output that shadowing and terminal-deny conclusions are
  unreliable across a MONITOR rule.
- Never silently map MONITOR to a plain `allow` with no warning.

## Merged evaluation order

Firepower evaluates: Prefilter policy, then the ACP Mandatory section, then the
ACP Default section, then the ACP default action. Ancestor policies contribute
rules to both sections when the ACP inherits.

Flatten all of it into one continuous `_rule_index` starting at 1. Record
provenance — policy name, section, category, and inheriting ancestor — in
`metadata`, not in a new schema field. This follows the Panorama precedent:
`parsing-palo-configs/SKILL.md` records device-group and pre-versus-post origin
in `metadata` rather than inventing a context field, because the schema defines
no such field and downstream consumers ignore unknown `_`-prefixed keys.

The ACP default action becomes the single trailing policy with `_implicit: true`.

**Unresolved at authoring time:** the exact nesting direction of inherited
Default-section rules across a multi-level hierarchy. The general shape —
ancestor Mandatory before the child's rules, ancestor Default after them — is
established. Confirm the multi-level interleaving against current Cisco
documentation and record the version consulted before relying on it.

## Reference resolution

Rules reference objects as
`{"objects": [{type, id, name}], "literals": [{type, value}]}`.

- **objects** — resolve by `id` against the parsed object sets and prefer the
  parsed object's name. An `id` that resolves to nothing produces a
  `metadata.warnings` entry naming the unresolved reference and its rule. Never
  drop it.
- **literals** — mint anonymous objects using `anon-N-host` and `anon-N-net`,
  the same convention `parsing-cisco-configs` uses, so both Cisco parsers behave
  identically downstream.

## Interface modes

Record `mode` on every interface: `ROUTED`, `SWITCHPORT`, `PASSIVE`, or
`INLINE`. Passive and inline-set interfaces do not carry policy the way routed
interfaces do; an audit that assumes otherwise is wrong. `ifname` is the
`nameif` equivalent, and `securityZone` gives the zone binding directly — no
inference is needed, unlike the ASA path.
