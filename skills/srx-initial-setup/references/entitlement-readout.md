# Entitlement Readout

Read-only assessment of feature entitlement, configuration, and operational state. This skill never installs, modifies, or removes a license. All mutating license work routes to `srx-license-signature-maintenance`.

## The three axes

Feature readiness is evaluated across three independent dimensions:

| Axis | Source | What It Proves |
|---|---|---|
| **Entitled** | `show system license` output | The device holds a valid license grant for the feature |
| **Configured** | `show configuration` hierarchy for the feature | The feature is configured in the running configuration |
| **Active** | Feature-specific operational commands | The feature is operationally enforcing |

**Critical:** A license counter alone is never treated as proof a feature is active.

### Entitlement commands and findings

The baseline entitlement assessment uses the commands documented in `skills/srx-license-signature-maintenance/references/licensing.md`, section "Baseline (read-only, every mode)". That reference is the authority for:

- `show system license` output format and field interpretation
- Feature-specific operational status commands (`show services application-identification status`, `show security idp status`)
- Cluster-aware entitlement checking via `request routing-engine login node <n>`

**Two hard-won findings from that reference must be preserved here:**

1. **A license counter reporting "used" does NOT mean the feature is enforcing.** A live device reported `IDP-SIG` with `used 1` while `show security idp status` reported `Policy Name : none`. Never infer enforcement from a license counter alone. To know whether IDP is actually enforcing, read the operational policy status.

2. **The `show system license` command takes NO `node` argument.** Per-node entitlement state on a cluster requires reaching each routing engine directly via `request routing-engine login node <n>`, then issuing the plain `show system license` command from that node's context.

**Source for these findings:** `skills/srx-license-signature-maintenance/references/licensing.md` (this repository), sections "Baseline (read-only, every mode)" and "Cluster baseline."

## Result states

Entitlement readout produces exactly one of these five states per feature:

| State | Entitled | Configured | Active | Meaning |
|---|---|---|---|---|
| **`active`** | Yes | Yes | Yes | Feature is licensed, configured, and operationally enforcing |
| **`licensed but not configured`** | Yes | No | No | License is present but feature is not configured; no operational effect |
| **`configured but not licensed`** | No | Yes | No | Feature is configured but lacks entitlement; feature may refuse to activate or may operate in a degraded/unlicensed mode |
| **`neither`** | No | No | No | Feature is neither licensed nor configured; no operational effect and no entitlement |
| **`indeterminate`** | (any axis unreadable) | | | At least one axis could not be read; the true state is unknown |

**`indeterminate` is a first-class result.** When any axis cannot be read — due to device unreachability, command failure, privilege restrictions, cluster node unavailability, or parsing errors — the result IS `indeterminate` and is reported as such. Never round an `indeterminate` result to a cleaner state.

### When indeterminate occurs

Common causes of `indeterminate`:

- Device is unreachable or authentication fails (all axes unreadable)
- A cluster secondary node cannot be reached (entitlement axis unverifiable for that node)
- Operational status command returns unexpected output or an error (active axis unreadable)
- Configuration retrieval fails or times out (configured axis unreadable)

**Report the cause of indeterminacy** along with the state. Example: "`indeterminate` (cluster node 1 unreachable; entitlement state unverified)".

## Routing to owning skills

When a gap is identified in a feature area that this skill does not configure, route the operator to the skill that owns that feature:

| Feature area | Routes to |
|---|---|
| AppID, IDP/IPS entitlement and signature content | `srx-license-signature-maintenance` |
| Security policy, AppFW, NGWF, EWF, SecIntel placement | `srx-policy` |
| ATP Cloud | `srx-atp-cloud` |
| NAT | `srx-nat` |
| Logging to a collector or SIEM | `srx-syslog-logging` |
| Chassis cluster / MNHA | `srx-chassis-cluster-proxmox`, `srx-mnha` |
| IPsec VPN | `srx-ipsec-hub-spoke`, `srx-autovpn-full-tunnel`, `srx-advpn` |

**Note:** `srx-atp-cloud` is a planned second package and does not exist yet. Reference it in the routing table as the planned owner, but do not add it to `related_skills` in `SKILL.md` frontmatter until it ships.

## Secret handling

Report entitlement **fields** only. The following must never appear in skill output, logs, or reports:

- License keys (the activation string supplied to `request system license add`)
- License identifiers (UUID or other unique identifiers from the entitlement blob)
- Software serial numbers (device or entitlement serial)
- Customer identifiers (customer ID, contract ID, or other account identifiers)
- Raw entitlement blobs or their hashes

**What may be reported:**

- Feature name (e.g., `IDP-SIG`, `APPID Signature`)
- License count installed vs. needed (numeric values only)
- Expiry date or "permanent"
- Whether a license is active, inactive, or expired
- Entitlement state (entitled, not entitled, indeterminate)

This restriction applies even in error paths. A failed `request system license add` often echoes the offending line; suppress or sanitize such output before reporting it.

## Gate protocol reference

Entitlement readout is assessment only. When this skill's later stages apply configuration changes based on the assessment, those changes follow the gate protocol documented in `references/write-safety.md`. That file is the authority for commit-confirmed mechanics, rollback behavior, and lockout-risk handling.
