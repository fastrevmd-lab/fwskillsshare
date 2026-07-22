# Skill Test Follow-up: firewall-best-practices-audit v1.1

- **Validation date:** 2026-07-22
- **Issue:** [#15 — re-run policy-light and policy-heavy SRX audits](https://github.com/fastrevmd-lab/fwskillsshare/issues/15)
- **Skill under test:** `firewall-best-practices-audit` **v1.1.3**
- **Parser instructions:** `parsing-srx-configs` **v1.3.4**
- **Mode:** read, parse, and analyze only; no device-side operation was called
- **Outcome:** offline policy-light replay and synthetic policy-heavy validation
  exercised the intended v1.1 coverage; a current live-device rerun remains open
  because no Junos/SRX/NETCONF connector was available in this session

## Acceptance summary

| Acceptance item | Result | Evidence and limitation |
|---|---|---|
| Same policy-light case emits explicit v1.1 coverage findings | **Offline pass** | The repository-preserved worked-example projection emits 6 findings, including `SEC-EMPTY-POLICYSET`; this was not a new live collection. |
| Policy-heavy case exercises stateful rulebase checks | **Synthetic pass** | A secret-free 9-explicit-policy fixture emits 16 finding IDs across permissiveness, shadow/redundancy/overlap, exposure, logging, reference, cleanup, and object checks. |
| Model, release, date, completeness, findings, false positives, unsupported cases, and residuals recorded | **Pass with stated gaps** | Exact current device model/release/config and the historical policy-light residual count cannot be recovered without a live pull or retained raw artifact. |
| Collection remains read-only | **Pass** | No device connector was callable; all work used repository artifacts and a synthetic local fixture. |

This follow-up does **not** claim that `vSRX-Production` was contacted or that its
2026-07-22 state matches the historical projection.

## Method and evidence

The repository is Markdown-first and does not contain an executable parser or
audit engine. The results below are a deterministic, line-by-line application of
the current `parsing-srx-configs` extraction contract and
`firewall-best-practices-audit` catalog to the declared inputs. The synthetic
input is retained at
[`fixtures/2026-07-22-policy-heavy-synthetic-srx.md`](fixtures/2026-07-22-policy-heavy-synthetic-srx.md)
so the reasoning can be repeated.

The Junos policy-order and syntax interpretation was cross-checked against
Juniper's current primary documentation:

- [Configuring Security Policies](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html)
  documents top-to-bottom, first-match evaluation and the source/destination/
  application/action tuple.
- [Global Security Policies](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-global-policies.html)
  documents inter-zone-before-global lookup and a terminal global deny when a
  global context is used.
- [Security Zones](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-zone-configuration.html)
  documents zone bindings, host-inbound traffic, and screen attachment.

## Case 1: policy-light vSRX-Production projection

### Provenance and completeness

This input is an **offline replay of the worked-example projection** in
`skills/firewall-best-practices-audit/references/example-audit.md`, not a
preserved machine-readable normalized snapshot and not a live rerun. That file
labels its source as a `vSRX-Production` point-in-time state captured
**2026-06-26**, Junos **25.4R1**, parsed through `parsing-srx-configs`. The earlier
test note records a later `vSRX-Production` pull on 2026-06-29 as Junos
**25.4R1.12**, but also records that the device gained policies that day and was
no longer policy-light.

- **Model:** vSRX Virtual Firewall by repository provenance; exact live model
  string was not retained.
- **Release:** 25.4R1 in the policy-light worked example; the exact maintenance
  release for that 2026-06-26 projection was not retained.
- **Collection date:** 2026-06-26 according to the worked example.
- **Replay date:** 2026-07-22.
- **Input completeness:** sufficient for the six recorded findings and five
  negative controls, but incomplete for a fresh full parse: raw config, a
  machine-readable schema, exact object/interface counts, warnings, and the
  complete residual array are not stored.

The projection contains 3 zones (`trust`, `untrust`, `IoT`), 2 outbound source
NAT rules, 0 explicit policies, 5 configured security-service families, an
untrust screen, hardened login policy/lockout, a lo0 RE filter, remote logging,
and an IPv6 address on the untrust interface.

### Explicit-versus-implicit policy contract

`parsing-srx-configs` appends one `_implicit: true` default-deny rule after
parsing. For this test, **explicit policy count** means
`security_policies` filtered to `_implicit != true`. This yields 0 explicit
policies and allows `SEC-EMPTY-POLICYSET` to fire. A consumer that tests the raw
array length instead would see the appended implicit rule and incorrectly
suppress the finding. The v1.1.3 policy-population contract now requires this
partition and `scripts/check-audit-rule-contract.py` guards it.

### Findings

| ID | Severity | Confidence | Grounded evidence |
|---|---|---|---|
| SEC-ZONES-NAT-NO-POLICY | High | heuristic | Three zones and two source-NAT rules exist, but 0 explicit policies reference their flows. |
| SEC-SERVICES-UNREFERENCED | High | heuristic | AppID, IDP, SecIntel, AAMW, and UTM are present with no explicit permit policy/profile attachment. |
| SEC-SSH-ROOT-LOGIN | High | definitive | The projection records `system.ssh.root_login: allow`. |
| SEC-EMPTY-POLICYSET | Medium | definitive | Explicit-policy count is 0 after excluding the parser-appended implicit rule. |
| SEC-NO-DENY-ALL | Medium | heuristic | No explicit logged terminal deny exists; the SRX implicit drop is enforcement without the desired policy log. |
| SEC-IPV6-POSTURE | Low | heuristic | The untrust interface has inet6 addressing and no explicit v6-aware policy intent is present. |

**Tally:** Critical 0, High 3, Medium 2, Low 1, Info 0 — **6 finding
IDs**.

### Negative controls and false-positive review

The preserved projection correctly suppresses these findings:

- `SEC-NO-SCREEN`: untrust has `untrust-screen` bound.
- `SEC-AUTH-HARDENING`: minimum length/complexity and login lockout are present.
- `SEC-NO-CONTROL-PLANE-PROTECTION`: a lo0 input RE filter is present.
- `OPS-LOG-COMPLETENESS`: an off-box log destination is present.
- `SEC-HOST-INBOUND-EXPOSURE`: untrust host-inbound permits ping only.

**Confirmed false positives:** 0 in the evidence that remains available.

**Review-required potential overstatement:** `SEC-IPV6-POSTURE` is useful as a
low-confidence intent warning, but an empty explicit SRX policy set still
default-denies transit traffic for both address families. It must not be read as
proof that IPv6 transit is permitted. If the check is intended to mean missing
documented dual-stack intent rather than exposure, its title/rationale should
say so explicitly.

### Parser residuals and unsupported data

The historical residual count is **unavailable** because neither raw input nor
the normalized residual array was retained. The prior report identifies these
known residual/partial-model areas:

- detailed `PROTECT-RE` stateless filter terms (the v1.1+ parser promotes only
  the `re_filter_present`/`applied_to` presence signal);
- detailed security-service configuration beyond presence flags/profile
  attachments;
- SDcloud `outbound-ssh` phone-home configuration;
- potentially the detailed security-log stream if not promoted to
  `syslog_config` by the parse used for the projection.

VPN crypto checks and `OPS-ZERO-HIT` are unsupported for this replay because no
VPN chain or hit/last-used telemetry is present. Current device drift, logical
systems/tenants, current screen/filter contents, and current remote-log health
cannot be assessed from the preserved projection.

## Case 2: policy-heavy synthetic SRX fixture

### Provenance and completeness

- **Model:** synthetic vSRX Virtual Firewall profile; no real device.
- **Release:** synthetic `set version 25.4R1`; syntax profile only, not a live
  software fact and not commit-validated.
- **Collection/authorship date:** 2026-07-22.
- **Input completeness:** complete for the declared policy/NAT/object/system
  surface. VPN, HA, IPv6, dynamic telemetry, and hit/last-used data are
  intentionally absent.
- **Secrets/identifiers:** none; all names are synthetic and all public addresses
  use documentation prefixes.

### Parsed projection and quality gates

| Section | Parsed result |
|---|---|
| Format/scope | Juniper SRX, display-set, single root context, version clue 25.4R1 |
| Zones/interfaces | 3 zones; 4 interfaces including lo0 |
| Objects/groups | 7 address objects; 0 address groups; 1 service/application object; 0 groups |
| Policies | 9 explicit policies (8 enabled, 1 disabled) plus 1 parser-appended `_implicit: true` default deny |
| NAT/routes | 1 source-NAT rule; 1 IPv4 default route |
| System/device plane | SSH root denied with rate/connection limits; password policy and lockout present; 1 remote syslog target; screen bound to untrust; lo0 RE filter present |
| VPN/HA/admin | 0 VPNs; no HA; 0 admin users |
| Reference resolution | 1 deliberate unresolved reference: `ALLOW-MISSING` → `MissingBackend` |
| Ordering/state | Order preserved within each zone context; `OLD-FTP` preserved disabled; global `DENY-REST` retained as the terminal fallback |

### Findings

| ID | Severity | Confidence | Affected synthetic evidence |
|---|---|---|---|
| SEC-ANY-ANY | High | definitive | Logged `ALLOW-ALL-EDGE` permits any source, destination, and application trust→untrust. |
| SEC-BROAD-SRC | High | definitive | Active permits `ALLOW-ALL-EDGE` and `ALLOW-RDP-IN` use `any` source. |
| SEC-SHADOW | High | heuristic | `ALLOW-ALL-EDGE` precedes and covers `ALLOW-WEB`, `ALLOW-WEB-COPY`, and `ALLOW-DNS-NOLOG`; `ALLOW-RDP-IN` precedes the matching deny. |
| SEC-EXPOSED-RISKY | High | definitive | `ALLOW-RDP-IN` permits RDP from untrust to `JumpHost`. |
| SEC-INBOUND-ANY | High | definitive | `ALLOW-RDP-IN` accepts any untrust source. |
| SEC-BROAD-DST | Medium | definitive | `ALLOW-ALL-EDGE` permits any destination. |
| SEC-OVERLAP | Medium | heuristic | `ALLOW-RDP-IN` and `DENY-RDP-IN` have the same match but opposite actions; first match wins. |
| SEC-ORPHAN-REF | Medium | definitive | `ALLOW-MISSING` references undefined `MissingBackend`. |
| SEC-NO-LOG | Medium | definitive | `ALLOW-DNS-NOLOG` and broad inbound `ALLOW-RDP-IN` permit without session logging; broad inbound context raises the grouped finding to Medium. |
| SEC-REDUNDANT | Low | definitive | `ALLOW-WEB-COPY` duplicates `ALLOW-WEB` match and action. |
| SEC-LARGE-PORTRANGE | Low | definitive | Unused `APP-WIDE` spans TCP/1024-65535. |
| OPS-UNUSED-OBJ | Low | heuristic | `WebServerCopy`, `UnusedHost`, and `APP-WIDE` are unreferenced in the complete fixture. |
| OPS-DUP-OBJ | Low | definitive | `WebServer` and `WebServerCopy` both equal 10.20.10.10/32. |
| SEC-DISABLED | Info | definitive | `OLD-FTP` is present but deactivated and is reported as cleanup, not active exposure. |
| SEC-NO-DESC | Info | definitive | `ALLOW-DNS-NOLOG` and `OLD-FTP` have no policy description. |
| OPS-NO-DESC-OBJ | Info | definitive | `LegacyFtp`, `UnusedHost`, and `APP-WIDE` have no description. |

**Tally:** Critical 0, High 5, Medium 4, Low 4, Info 3 — **16 finding
IDs**.

All 16 are deliberately seeded, so **confirmed false positives are 0**. The
catalog-mandated heuristic confidence remains appropriate for shadow/overlap and
unused-object results even though the synthetic input is complete.

### Negative controls, skipped checks, and residuals

Correctly not fired:

- `SEC-NO-DENY-ALL`: `DENY-REST` is an explicit logged terminal global deny.
- `SEC-SSH-ROOT-LOGIN`: root login is denied and limits are present.
- `SEC-AUTH-HARDENING`: password policy and lockout are present.
- `SEC-NO-SCREEN`: `EDGE-SCREEN` is bound to untrust.
- `SEC-NO-CONTROL-PLANE-PROTECTION`: `PROTECT-RE` is applied to lo0 input.
- `OPS-LOG-COMPLETENESS`: a remote `system syslog host` target is present.
- `SEC-HOST-INBOUND-EXPOSURE`: untrust host-inbound permits ping only.
- `SEC-ZONES-NAT-NO-POLICY` / `SEC-EMPTY-POLICYSET`: all NAT zones are used by
  explicit policies and the explicit set is nonempty.

Skipped/no data: `SEC-WEAK-IKE`, `SEC-WEAK-IPSEC`, and `SEC-PSK-WEAK` (no VPN
chain); `SEC-IPV6-POSTURE` (no IPv6); `OPS-ZERO-HIT` (no counters);
`SEC-SERVICES-UNREFERENCED` (no advanced security service configured);
group-size/depth checks (no groups); `OPS-NAMING` (no engagement naming standard
was supplied). The SSH cipher-strength subcheck also skips because the fixture
does not configure an explicit cipher list; root-login and rate-limit evidence
remain sufficient to suppress the conditions they directly test.

Parser residuals are **4 source lines**, all the detailed `PROTECT-RE` filter
terms under the `Firewall Filters` category. The structured projection still
records `system.control_plane_protection.re_filter_present: true` and
`applied_to: ["lo0.0"]`; the terms remain residual by design. No other fixture
line is silently dropped under the current parser instructions.

## Coverage and root-cause findings

1. **The original root cause is covered offline.** v1.0's policy-centric model
   produced one finding on the empty-policy projection. v1.1 emits six grounded
   IDs by reading explicit-policy emptiness, zones/NAT, security-service
   attachment, SSH, control-plane/device-plane data, logging, and IPv6 posture.
2. **Stateful catalog coverage is exercised.** The policy-heavy fixture produces
   16 IDs across ordered policy and object families, not merely device-plane
   absence checks.
3. **Negative controls did not over-fire.** Screen, auth hardening, RE filter,
   remote logging, safe host-inbound, and terminal deny controls suppress their
   corresponding findings in both cases where the needed data is present.
4. **The implicit-rule contract gap is guarded.** Audit implementations must
   exclude `_implicit: true` from explicit-rule families. The v1.1.3 contract
   and regression check pin empty-policy, enabled explicit tail,
   shadow/redundancy/overlap, and disabled-cleanup behavior.
5. **Control-plane quality remains residual.** The audit models only that an RE
   filter is applied, not whether its terms enforce least privilege. The
   synthetic `PROTECT-RE` terms permit SSH without a source restriction and
   therefore demonstrate a possible false-negative area even though the
   absence-only `SEC-NO-CONTROL-PLANE-PROTECTION` check correctly stays quiet.
6. **Live acceptance remains incomplete.** The exact current
   `vSRX-Production` model, release, config drift, parser warnings/residuals, and
   live v1.1 finding set were not recollected because this session exposed no
   read-only Junos connector. Re-running `get_junos_config` (read-only) through
   the parser/audit remains necessary when an authorized connector is available.

No device configuration, commit, failover, clear, upgrade, reboot, candidate
operation, or other mutation was attempted. No follow-up issue was created as
part of this validation.
