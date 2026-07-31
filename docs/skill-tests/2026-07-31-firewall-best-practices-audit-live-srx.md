# Skill Test: firewall-best-practices-audit v1.1 on live SRX devices

- **Validation date:** 2026-07-31
- **Issue:** [#15 — re-run policy-light and policy-heavy SRX audits](https://github.com/fastrevmd-lab/fwskillsshare/issues/15)
- **Skill under test:** `firewall-best-practices-audit` **v1.1.4**
- **Parser instructions:** `parsing-srx-configs` **v1.3.4**
- **Collection:** live devices over NETCONF via `rust-junosmcp` (34-device lab inventory)
- **Mode:** read, parse, and analyze only — every device call was a `show`
  command or a config read; no `configure`, `commit`, `request`, or `set`
  operation was issued
- **Outcome:** closes the live-device gap left open by the
  [2026-07-22 follow-up](2026-07-22-firewall-best-practices-audit-v1.1-follow-up.md),
  which could not contact a device. Both cases ran against current configs.
  Two reproducible parser/catalog defects were found.

All device names below are lab aliases. Public addresses, organization names,
site and building names, hostnames, and credential material from the source
configs are redacted or replaced with generic placeholders.

## Acceptance summary

| Acceptance item | Result | Evidence |
|---|---|---|
| Policy-light case emits explicit coverage findings rather than a near-empty report | **Superseded — device drifted** | The historical policy-light target now defines 8 policies. Its former single finding (`SEC-NO-DENY-ALL`) is **remediated**. It was audited as-is; a separate genuinely empty device confirms the coverage-warning path. See [Case 1](#case-1-the-historical-policy-light-device-has-drifted). |
| Policy-heavy case exercises stateful rulebase checks and documents counts | **Pass** | 101 policies / 238 addresses / 25 address-sets / 42 applications on a 2-node chassis cluster; 15 check families fired. See [Case 2](#case-2-policy-heavy-chassis-cluster). |
| Model, release, date, completeness, findings, false positives, unsupported cases, residuals recorded | **Pass** | Per-case provenance tables below; [false positives](#false-positives-and-coverage-gaps) called out separately. |
| Collection remains read-only | **Pass** | Read-only command set listed per case. |
| Results identify regressions, false positives, coverage gaps, follow-up issues | **Pass** | Two defects with reproductions; [follow-ups](#recommended-follow-ups) proposed. |

## Method

Device inventory was resolved first (`get_router_list`), then policy and zone
volume was probed across all 34 devices with `| display set | count` to select
targets by rulebase size rather than by name. Configuration was pulled with
`show configuration ... | display set`.

Extraction follows the `parsing-srx-configs` §6/§2/§3/§5b contract (global
policy path, global address book, address-sets, applications and
application-sets), preserving configured order as `_rule_index`. The catalog in
`firewall-best-practices-audit/references/check-catalog.md` was then applied.
The extraction and checks are implemented as a script so the counts below are
reproducible rather than prose assertions; it is retained at
[`fixtures/2026-07-31-live-srx-audit-replay.py`](fixtures/2026-07-31-live-srx-audit-replay.py).

Findings that the script cannot reach — device-plane facts such as
`system services ssh`, `system login`, `security log`, zone `host-inbound-traffic`,
screen bindings, and `lo0` filters — were read directly from the pulled configs
and are marked as such.

## Case 1: the historical policy-light device has drifted

### Provenance

| Field | Value |
|---|---|
| Device | `vsrx-prod` (the target the 2026-06-29 audit called `vSRX-Production`) |
| Model / release | vSRX, Junos **25.4R1.12** — same release as the 2026-06-29 baseline |
| Topology | standalone (no chassis cluster) |
| Last config commit on device | 2026-07-22 |
| Input completeness | complete running config |
| Policies / zones / NAT rules / address objects | 8 / 3 / 1 / 3 |

The 2026-06-29 baseline recorded **zero** security policies. The device now has
8 global policies. **It is no longer a policy-light device**, so the original
acceptance item cannot be re-run against it as written.

### Regression check: the 2026-06-29 finding is fixed

The single v1.0 finding was `SEC-NO-DENY-ALL`, with a recommended terminal
logged deny. That exact remediation is now on the device as the tail rule:

```text
set security policies global policy 999-DEFAULT-DENY match source-address any
set security policies global policy 999-DEFAULT-DENY match destination-address any
set security policies global policy 999-DEFAULT-DENY match application any
set security policies global policy 999-DEFAULT-DENY then deny
set security policies global policy 999-DEFAULT-DENY then log session-init
```

`SEC-NO-DENY-ALL` no longer fires. No regression.

### Findings

```text
[SEC-ANY-ANY] HIGH (definitive) — any/any/any permit from the IoT zone to untrust
Category: security / permissiveness
Affected: policy "Allow_set_for_IoT-1" (IoT -> untrust), _rule_index 5
Why it matters: source any, destination any, application any, action permit. Every
  IoT-zone host may reach any internet destination on any port. Severity is HIGH
  rather than CRITICAL because the rule logs session-close and attaches IDP,
  SecIntel, and anti-malware inspection — inspection narrows the blast radius but
  does not constrain what the rule permits.
Remediation: scope the destination or application, or split into per-service rules.
```

```text
[SEC-HOST-INBOUND-EXPOSURE] HIGH (heuristic) — SSH and NETCONF reachable on the untrust zone
Category: security / device-plane
Affected: zone "untrust" (internet-facing interface), host-inbound-traffic system-services
  = ping, ssh, netconf
Why it matters: the device's own management plane accepts SSH and NETCONF from the
  untrusted zone. This is a change from the 2026-06-29 baseline, which recorded
  untrust as ping-only and credited it as good practice. Severity is raised above
  the catalog default of MEDIUM because the exposed zone is internet-facing.
Remediation: remove ssh/netconf from the untrust zone's host-inbound-traffic and
  reach the device over the management path or a VPN.
Fix (SRX):
  delete security zones security-zone untrust host-inbound-traffic system-services ssh
  delete security zones security-zone untrust host-inbound-traffic system-services netconf
```

```text
[SEC-ZONES-NAT-NO-POLICY] MEDIUM (heuristic) — trust zone carries interfaces but no permit rule
Category: security / coverage
Affected: zone "trust" (2 interfaces), no permitting policy in any context
Why it matters: the only policy naming the trust zone is a deny. All trust-sourced
  traffic falls through to 999-DEFAULT-DENY. Either the zone is unused and should be
  removed, or intended permits are missing. The audit cannot tell which.
```

```text
[SEC-SERVICES-UNREFERENCED] HIGH (heuristic) — UTM configured but attached to no policy
Category: security / inert-security-stack
Affected: security utm custom-objects (base-filter, custom-url-ng-category set);
  no utm-policy defined and no policy references one
Why it matters: UTM objects are configured but no policy invokes UTM, so the web
  filtering they describe inspects nothing. IDP, SecIntel, and AAMW by contrast are
  correctly referenced by "Allow_set_for_IoT-1".
```

```text
[OPS-DUP-OBJ] LOW (definitive) — two address objects with the same value
Category: operational / object hygiene
Affected: CAST-CONTROLLERS and LAN-LOCAL, both <LAN-PREFIX>/24
Why it matters: divergent edits to one will silently not apply to rules using the other.
```

### Checks that passed on this device

`SEC-NO-DENY-ALL` (logged terminal deny present), `SEC-SSH-ROOT-LOGIN`
(`root-login deny-password`, `rate-limit 32`), `SEC-AUTH-HARDENING`
(password minimum-length 12 with `change-type character-sets`, retry-options
with 3 tries and a lockout period), `SEC-NO-CONTROL-PLANE-PROTECTION`
(`PROTECT-RE` on `lo0.0` inet and `PROTECT-RE6` on inet6),
`OPS-LOG-COMPLETENESS` (`security log mode stream` to a defined
`stream ... host`), `SEC-NO-SCREEN` (screen bound on the untrust zone),
`SEC-PLAINTEXT-MGMT` (no telnet, no HTTP management).

Every one of these except the deny-all was an uncredited control in the
2026-06-29 shortcomings table. The v1.1 device-plane families now evaluate them.

### Case 1b: a genuinely empty device

Five devices in the inventory (`vsrx-br07`, `-br09`, `-br10`, `-br11`, `-br12`)
have zero `security policies` **and** zero `security zones`. Auditing one of
these does exercise `SEC-EMPTY-POLICYSET` and produces the intended explicit
coverage warning rather than silence. It is a weaker test than the 2026-06-29
device, which was interesting precisely because it had zones, NAT, and a full
inspection stack wired to an empty policy set. **No device in the current
inventory reproduces that combination**, so the original policy-light scenario
is no longer available live.

## Case 2: policy-heavy chassis cluster

### Provenance

| Field | Value |
|---|---|
| Device | `vsrx-fw01` |
| Model / release | vSRX, Junos **24.4R1.9**, both nodes |
| Topology | chassis cluster ID 2 — node0 primary (priority 100), node1 secondary |
| Zone interfaces | `reth0.0`–`reth4.0` across 5 zones |
| Input completeness | complete running config (1,583 set lines) |
| Policies | **101** (all in the `global` context) |
| Address objects / address-sets | 238 / 25 |
| Applications / application-sets | 42 / 12 |
| NAT | 4 source rule-sets, 2 destination rule-sets, 7 source pools, 6 destination pools |

`reth*` interfaces parsed correctly as ordinary zone interfaces, per the
`parsing-srx-configs` cluster-interface rule. No zone interface was wrongly
excluded.

### Finding counts

| Check | Count | Severity |
|---|---|---|
| `SEC-ANY-ANY` | 8 | CRITICAL (all unlogged) |
| `SEC-INBOUND-ANY` | 12 | HIGH |
| `SEC-BROAD-DST` | 34 | MEDIUM |
| `SEC-BROAD-SRC` | 33 | HIGH |
| `SEC-ANY-SVC` | 37 | MEDIUM |
| `SEC-NO-LOG` | 70 | LOW–MEDIUM |
| `SEC-NO-DESC` | 101 | INFO |
| `SEC-SHADOW` | 1 | HIGH (heuristic) |
| `SEC-REDUNDANT` | 2 | LOW — **1 is a false positive** |
| `SEC-ORPHAN-REF` | 1 | MEDIUM — **false positive** |
| `SEC-LARGE-PORTRANGE` | 3 | LOW |
| `OPS-DUP-OBJ` | 12 | LOW |
| `OPS-LARGE-GROUP` | 1 | INFO |
| `OPS-UNUSED-OBJ` | 78 addresses, 6 groups | LOW (heuristic) |
| `SEC-NO-DENY-ALL` | **missed** | see [defects](#false-positives-and-coverage-gaps) |

### The finding that matters most

Five rules whose names assert a deny are configured `then permit`, with
`source-address any`, `destination-address any`, `application any`, and **no
logging**, across trust boundaries:

| Policy name (verbatim, non-identifying) | Zone pair | Configured action |
|---|---|---|
| `185-Explicit_deny_WAN_to_LAN__LAG` | UNTRUST → LAN | `then permit` |
| `182-explicit_deny_DMZ__LAG` | UNTRUST → DMZ | `then permit` |
| `048-explicit_dmz_lan_deny` | DMZ → INTERNAL | `then permit` |
| `135-explicit_dmz_lan_deny__LAG` | DMZ → LAN | `then permit` |
| `049-lan_dmz_deny` | INTERNAL → DMZ | `then permit` |

```text
[SEC-ANY-ANY] CRITICAL (definitive) — unrestricted internet-to-LAN permit named as a deny
Category: security / permissiveness
Affected: policy "185-Explicit_deny_WAN_to_LAN__LAG", zone pair UNTRUST -> LAN
Why it matters: source any, destination any, application any, then permit, unlogged.
  Every internet host can reach every LAN host on every port, and nothing is recorded.
  The rule name states the opposite of its configured action, so a reviewer scanning
  names — or an auditor reading a rulebase export — sees a deny where a full permit
  is programmed. Three further any/any/any permits carry the same contradiction on
  DMZ boundaries.
Remediation: confirm intent, then change the action and add logging.
Fix (SRX):
  set security policies global policy 185-Explicit_deny_WAN_to_LAN__LAG then deny
  set security policies global policy 185-Explicit_deny_WAN_to_LAN__LAG then log session-init
```

`SEC-SHADOW` fires once as a direct consequence: `049-lan_dmz_deny` permits all
INTERNAL → DMZ traffic and precedes a narrower INTERNAL → DMZ rule, which can
therefore never match.

### Device-plane findings (read directly from config)

```text
[SEC-SSH-ROOT-LOGIN] HIGH (definitive) — SSH permits direct root login
Affected: set system services ssh root-login allow
Fix (SRX): set system services ssh root-login deny

[SEC-PLAINTEXT-MGMT] HIGH (definitive) — plaintext HTTP management enabled
Affected: set system services web-management http interface fxp0.0
Note: HTTPS is also enabled; the HTTP listener is redundant and should be removed.
Fix (SRX): delete system services web-management http

[SEC-AUTH-HARDENING] MEDIUM (definitive) — no login lockout policy
Affected: system login password sets minimum-length 20 and change-type
  character-sets (strong), but no `login retry-options` — no tries-before-disconnect
  and no lockout-period, so password guessing is unthrottled.
Fix (SRX):
  set system login retry-options tries-before-disconnect 3
  set system login retry-options lockout-period 5

[SEC-NO-CONTROL-PLANE-PROTECTION] MEDIUM (heuristic) — no RE-protection filter
Affected: no `firewall family inet filter` exists and no input filter is applied
  to lo0, on a device with an internet-facing zone.

[SEC-MGMT-DATAZONE] MEDIUM (definitive) — management services on data zones
Affected: zones LAN, INTERNAL, NET-MGMT all permit host-inbound https and ssh.
  UNTRUST is correctly ping-only.

[OPS-LOG-COMPLETENESS] MEDIUM (definitive) — stream logging configured with no destination
Affected: `security log mode stream` and `security log source-interface reth1.0` are
  set, but no `security log stream <name> host <ip>` exists. Security logs are
  generated in stream mode and sent nowhere. Combined with 70 unlogged permits,
  this device has effectively no security-event record.
Fix (SRX):
  set security log stream <NAME> host <COLLECTOR-IP>
  set security log stream <NAME> host port <PORT>
```

`SEC-NO-SCREEN` passes for the external zone (`SCREEN-UNTRUST` is bound to
UNTRUST; `SCREEN-INTERNAL` to INTERNAL). DMZ, LAN, and NET-MGMT have no screen,
which is worth noting but is outside the check's external-zone scope.
`SEC-IPV6-POSTURE` is skipped: the device has no `family inet6` anywhere.

## False positives and coverage gaps

Two defects reproduced on live configs. Both trace to the same root cause: the
`parsing-srx-configs` §6 policy contract does not extract
`match dynamic-application`, and §2/§3 address extraction does not model
`security dynamic-address`.

### Defect 1 — `security dynamic-address` objects read as undefined references

`parsing-srx-configs` §2 and §3 extract only `security address-book` entries.
Addresses defined under `security dynamic-address address-name <name>` (GeoIP
categories and threat-feed-backed objects) are therefore absent from
`address_objects`, and any policy referencing one produces a spurious
`SEC-ORPHAN-REF`.

Reproduced on both devices:

| Device | Policy | Reference | Actually defined at |
|---|---|---|---|
| `vsrx-fw01` | `Block_Countries_inbound` | `Bad_Countries` | `security dynamic-address address-name Bad_Countries profile category GeoIP` |
| `vsrx-prod` | `Block_Country_dst` / `Block_Country_src` | `Banned_countries` | `security dynamic-address address-name Banned_countries profile category GeoIP` |
| `vsrx-prod` | `deny-feed-blocklist` | `wilddns-blocklist` | `security dynamic-address address-name wilddns-blocklist profile feed-name blocklist` |

Impact: **false-positive `SEC-ORPHAN-REF` findings**, and — more damaging —
these objects are invisible to `OPS-UNUSED-OBJ` and to any reasoning about what
a rule actually matches. The repository already ships an `srx-dynamic-ip-feed`
skill covering this feature, so the gap is in the parser's schema coverage, not
in product knowledge.

### Defect 2 — `match dynamic-application` is dropped, collapsing distinct rules

§6 extracts `match application` but not `match dynamic-application`. Two
consequences appeared on `vsrx-fw01`, which uses AppID-scoped policies:

**False-positive `SEC-REDUNDANT`.** These two rules are reported as duplicates
because the only field distinguishing them is discarded:

```text
policy Block_Bad_Applications_Everywhere  ... match application any
                                          ... match dynamic-application Apps_blocked_globally
policy Unsactioned_DNS                    ... match application any
                                          ... match dynamic-application junos:DNS
                                          ... match dynamic-application junos:DNS-ENCRYPTED
```

**False-negative `SEC-NO-DENY-ALL`.** The tail rule of the 101-policy set is
`Unsactioned_DNS`, which the audit reads as an any/any/any logged deny and
therefore accepts as a terminal deny-all. It is not — it is an AppID-scoped DNS
deny. `vsrx-fw01` has **no** explicit terminal deny-all, and the check that
exists to catch that stayed silent.

The mirror risk also exists: a rule narrowed only by `dynamic-application` will
present as any/any/any and can produce a false-positive `SEC-ANY-ANY`. On
`vsrx-prod` this did not change any verdict, because the three rules using
`dynamic-application` there all specify `any`.

### Gap 3 — no check for a rule name that contradicts its action

Eleven `vsrx-fw01` rules whose names contain deny/block are configured
`then permit`; five of those are unlogged any/any/any permits across trust
boundaries. The catalog has no check for this. The nearest, `OPS-NAMING`, is
INFO severity and framed as naming-convention hygiene, which badly understates
a rule that reads as a deny and functions as a full permit. This pattern is
cheap to detect and high signal.

### Gap 4 — no check for plaintext threat-feed transport

`vsrx-prod` fetches its dynamic-address feed bundle over plaintext HTTP
(`security dynamic-address feed-server ... url http://<host>/bundle.tgz`). A
feed that drives deny decisions, retrieved without TLS or authentication, is
tamperable on the wire. No catalog check covers feed transport.

## Recommended follow-ups

1. ~~**Parser — model `security dynamic-address`.**~~ **Fixed 2026-07-31** in
   `parsing-srx-configs` v1.4.0 (§2b) and `firewall-best-practices-audit` v1.2.0.
   `address-name` entries now parse into `address_objects` as `type: "dynamic"`
   with a `dynamic_source` selector, and `SEC-ORPHAN-REF` counts them resolved.
2. ~~**Parser — extract `match dynamic-application`.**~~ **Fixed 2026-07-31** in
   the same releases. It is now a documented narrowing field, included in the
   `SEC-REDUNDANT` match tuple and the catch-all test behind `SEC-ANY-ANY` and
   `SEC-NO-DENY-ALL`.
3. **Catalog — add a name-versus-action contradiction check** at HIGH severity,
   definitive when the configured action is the opposite of what the rule name
   asserts. Addresses Gap 3.
4. **Catalog — add a feed-transport check** for `dynamic-address feed-server`
   URLs that are not HTTPS. Addresses Gap 4.
5. **Test corpus.** The 2026-06-29 policy-light scenario (zones + NAT + full
   inspection stack, empty policy set) no longer exists on any live device. If
   that case is to stay covered, it should become a retained synthetic fixture
   rather than a device reference.

Items 3–5 remain open and warrant their own issues.

### Verification of the Defect 1 and 2 fixes

Re-running the replay script against the same unmodified `vsrx-fw01` capture,
before and after the parser and catalog changes:

| Check | Before | After | Why |
|---|---|---|---|
| `SEC-ORPHAN-REF` | 1 | **0** | the GeoIP object now parses as a defined dynamic address |
| `SEC-REDUNDANT` | 2 | **1** | the AppID-differentiated pair is no longer a duplicate |
| `SEC-NO-DENY-ALL` | not raised | **raised** | the tail rule is correctly rejected as AppID-scoped |
| `SEC-ANY-ANY` | 8 | 8 | unchanged — none of those rules is AppID-scoped |
| `SEC-ANY-SVC` | 37 | 37 | unchanged |

Two false positives eliminated and one false negative corrected, with no
collateral change to the other checks. The behavior is pinned by regressions in
`scripts/check-audit-rule-contract.py`
(`_dynamic_application_errors`, `_dynamic_address_errors`), which fail against
the pre-fix logic.

## Safety statement

Every device interaction was read-only. Commands issued: `get_router_list`,
`gather`-class reads, `show version`, `show chassis cluster status`,
`show configuration ... | display set`, and `| count` variants of the same. No
configuration was loaded, committed, rolled back, or discarded; no
`request`-class operation ran; no failover was triggered. The chassis cluster's
primary/secondary state was read but not altered.
