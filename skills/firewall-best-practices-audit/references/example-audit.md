# Firewall Best-Practices Audit — Worked Example

> Reference material for the `firewall-best-practices-audit` skill; loaded on
> demand. A single end-to-end audit over a real parsing fixture, demonstrating
> the workflow, the Finding template, and the Audit Summary. All findings below
> are grounded in the fixture's actual content — no invented rules or objects.

## Input

- **Fixture:** `skills/parsing-cisco-configs/references/fixture-expected-output.json`
- **Source vendor:** `metadata.vendor: cisco-asa` → remediation snippets use **Cisco ASA/FTD** syntax.

This is the parsed intermediate schema produced by the `parsing-cisco-configs`
skill, so the audit runs directly against it (no re-parsing).

## Workflow walk-through

**1. Establish input + vendor.** The schema is the parsed form of a Cisco ASA
config (`metadata.vendor: cisco-asa`). It carries 2 zones (`outside`, `inside`),
2 address objects (`WEB`, `INSIDE-NET`), 1 service object (`HTTPS-ALT`),
1 security policy (`OUTSIDE-IN-1`), and 1 source-NAT rule (`INSIDE-NET-auto-nat`).

**2. Resolve objects and zones.** `outside` binds `GigabitEthernet0/0`
(203.0.113.2/24, the internet edge); `inside` binds `GigabitEthernet0/1`
(10.0.0.1/24). `WEB` = host `10.0.1.10/32`; `INSIDE-NET` = subnet `10.0.0.0/16`;
`HTTPS-ALT` = `tcp/8443`. `INSIDE-NET-auto-nat` source-NATs `INSIDE-NET` to the
outside interface address (outbound hide-NAT). `metadata.warnings` flags that the
ACL destination zone may need route/interface resolution beyond the access-group
binding — so any zone-direction reasoning is treated as **heuristic**.

**3–4. Run security + operational checks.** Findings below.

**5–6. Severity, confidence, remediation.** Per the rubric; Cisco snippets drawn
from `references/remediation-patterns.md`.

**7. Output.** Findings, then the Audit Summary.

## Findings

```text
[SEC-INBOUND-ANY] HIGH (definitive) — Inbound permit from any internet source to internal host
Category: security / inbound-exposure
Affected: security_policies OUTSIDE-IN-1 (src_addresses: any, dst_addresses: WEB=10.0.1.10/32, services: tcp/443), ingress zone outside (GigabitEthernet0/0, 203.0.113.2/24)
Why it matters: OUTSIDE-IN-1 permits any source on the internet to reach the internal host WEB on tcp/443. An unrestricted internet-facing source means the entire IPv4 space can probe and attack the exposed service; a sourced allowlist shrinks that attack surface dramatically. Destination and service are already scoped, so the source is the gap.
Remediation: Replace the any source with the specific partner/customer prefixes (or a published-source allowlist) that actually need the service; keep the destination and port tight and retain logging.
Fix (Cisco ASA/FTD):
  object network PARTNER-SRC
   subnet <partner-net> <mask>
  no access-list OUTSIDE_IN extended permit tcp any object WEB eq 443
  access-list OUTSIDE_IN extended permit tcp object PARTNER-SRC object WEB eq 443 log
  access-group OUTSIDE_IN in interface outside
```

```text
[SEC-NO-DENY-ALL] MEDIUM (heuristic) — No explicit logged terminal deny-all
Category: security / deny-all
Affected: security_policies tail — OUTSIDE-IN-1 is the only/last rule (_rule_index: 1); no terminal deny-all present
Why it matters: The ASA enforces an implicit deny at the end of an ACL, but that implicit drop is not logged. Without an explicit logged deny-all, denied/attempted flows leave no audit trail, blinding incident response and tuning. Confidence is heuristic because the schema may not capture an implicit terminal rule.
Remediation: Append an explicit deny-all that logs, as the final ACE, so dropped traffic is visible to the SIEM.
Fix (Cisco ASA/FTD):
  access-list OUTSIDE_IN extended deny ip any any log
  access-group OUTSIDE_IN in interface outside
```

```text
[OPS-UNUSED-OBJ] LOW (heuristic) — Service object defined but never referenced
Category: operational / object-cleanup
Affected: service_objects HTTPS-ALT (tcp/8443) — not referenced by any security_policies or nat_rules (OUTSIDE-IN-1 uses tcp/443)
Why it matters: HTTPS-ALT (tcp/8443) is defined but unused — the only policy matches tcp/443. Dead objects accumulate, obscure intent, and risk being wired into a future rule by mistake. Confidence is heuristic because it depends on the parser capturing every reference site.
Remediation: Confirm no out-of-band reference, then delete the unused service object (or attach it to the rule it was intended for).
Fix (Cisco ASA/FTD):
  no object service HTTPS-ALT
```

```text
[SEC-NO-DESC] INFO (definitive) — Rule missing description/owner
Category: security / hygiene
Affected: security_policies OUTSIDE-IN-1 (no description field)
Why it matters: OUTSIDE-IN-1 carries no description tying it to an owner or change ticket. Undocumented rules become un-reviewable over time — nobody knows who owns the exposure or why it exists, which stalls rule recertification.
Remediation: Add a description/remark naming the owner and the change ticket or business justification.
Fix (Cisco ASA/FTD):
  access-list OUTSIDE_IN remark OWNER netops TICKET CHG-1234 inbound https to WEB
```

```text
[OPS-NO-DESC-OBJ] INFO (definitive) — Objects missing descriptions
Category: operational / object-cleanup
Affected: address_objects WEB, INSIDE-NET; service_objects HTTPS-ALT — none carry a description
Why it matters: None of the address or service objects document their purpose. Description-less objects make audits slower and increase the chance a reused name is misinterpreted during a change.
Remediation: Add an owner/purpose description to each object as part of routine cleanup.
Fix (Cisco ASA/FTD):
  object network WEB
   description Public web host (owner: netops)
  object network INSIDE-NET
   description Inside summary 10.0.0.0/16 (owner: netops)
  object service HTTPS-ALT
   description Alt HTTPS tcp/8443 (owner: netops)
```

## Audit Summary

```text
Posture: Not hardened — 1 high inbound-exposure finding (any-source internet permit to an internal host) plus a missing logged deny-all and object-hygiene gaps; this is a hygiene report, not a "secure"/"compliant" verdict.
Findings: Critical 0  High 1  Medium 1  Low 1  Info 2
Checks skipped (no data): OPS-ZERO-HIT (schema has no hit_count/last-used data); SEC-PLAINTEXT-MGMT and SEC-MGMT-DATAZONE (no system.mgmt_services / host-inbound data); SEC-WEAK-IKE, SEC-WEAK-IPSEC, SEC-PSK-WEAK (no vpn_tunnels in fixture).
Top fixes (prioritized):
  1. SEC-INBOUND-ANY — scope OUTSIDE-IN-1's any source to a partner/customer allowlist.
  2. SEC-NO-DENY-ALL — add an explicit logged deny-all as the final ACE.
  3. OPS-UNUSED-OBJ — remove the unused HTTPS-ALT (tcp/8443) service object.
  4. SEC-NO-DESC / OPS-NO-DESC-OBJ — add owner/ticket descriptions to the rule and objects.
```
