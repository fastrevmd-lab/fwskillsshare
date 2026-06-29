# firewall-best-practices-audit v1.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the shared intermediate schema + the SRX parser with generic management/control-plane/auth/security-service fields, and add 9 new checks to `firewall-best-practices-audit` so it sees the SRX security surface beyond the stateful policy rulebase.

**Architecture:** Documentation skills (Markdown). Schema-first: extend the shared `intermediate-schema.md` (canonical = parsing-srx-configs, propagated byte-identical to the other 3 parsers), then teach the SRX parser to populate the new fields, then add the checks that consume them, then a worked example from the real `vSRX-Production` parse, then a live re-audit regression. New fields are additive/optional — parsers that don't populate them leave the dependent checks to skip gracefully.

**Tech Stack:** Markdown + YAML frontmatter + JSON schema docs. Verification is structural (Python one-liners for schema sync, frontmatter, catalog-id coverage — same as v1.0) plus a controller-run live MCP re-audit. No pytest.

## Global Constraints

- Shared schema is duplicated byte-identical across all 4 `parsing-*` skills. Edit ONLY the canonical copy `skills/parsing-srx-configs/references/intermediate-schema.md`, copy verbatim to cisco/fortinet/palo, then `python3 scripts/check-shared-schema.py` MUST report all 4 identical. (Policy: `skills/SHARED-SCHEMA.md`.)
- New schema fields are additive/optional; absence → the dependent audit check is skipped and listed in the audit summary.
- Audit skill stays vendor-neutral and findings-only: a *missing* control is a finding; a *present* good control yields no finding. Never claim "secure"/"compliant"; never cite a compliance control ID.
- Every new check has: id, detected condition, schema fields, default severity, confidence (definitive vs heuristic), and a remediation family (SRX snippet authoritative).
- Versions after this work: `firewall-best-practices-audit` → 1.1.0; `parsing-srx-configs` → 1.2.0.
- Frontmatter `name` == dir; description starts "Use when", ≤1024 chars; `author: [fastrevmd-lab, Claude]`; audit-skill `license: MIT`.
- Re-sync changed skills into `~/.claude/skills/` as the final step. No real secrets in any example.

---

### Task 1: Extend the shared intermediate schema

**Files:**
- Modify: `skills/parsing-srx-configs/references/intermediate-schema.md` (canonical)
- Modify (verbatim copies): `skills/parsing-cisco-configs/references/intermediate-schema.md`, `skills/parsing-fortinet-configs/references/intermediate-schema.md`, `skills/parsing-palo-configs/references/intermediate-schema.md`

**Interfaces:**
- Produces: schema fields `zones[].screen`, `system.ssh`, `system.auth`, `system.control_plane_protection`, and a new top-level `security_services` object. Tasks 2–5 consume these exact names.

- [ ] **Step 1: In the canonical schema, add `screen` to the Zone object.** In the `## Zone` JSON block, after `"zone_type": "layer3",` add `"screen": "untrust-screen",` (a string naming the bound screen/DoS profile, or null if none). After the existing `host_inbound` bullets add a line:
  `- \`screen\`: name of the bound screen / DoS-protection profile for the zone (SRX \`screen <name>\`), or null. Populated where the vendor parser supports it; absent → SEC-NO-SCREEN skipped.`

- [ ] **Step 2: Extend the `## System` JSON block.** After the `mgmt_services` object (before the closing `}`), add:
```json
  "ssh": {
    "root_login": "deny-password",
    "rate_limit": 32,
    "ciphers": [],
    "protocol_version": null,
    "connection_limit": null
  },
  "auth": {
    "password_policy": {"min_length": 12, "complexity": "character-sets"},
    "login_lockout": {"tries": 3, "lockout_period": 5},
    "root_authentication_present": true
  },
  "control_plane_protection": {
    "re_filter_present": true,
    "applied_to": ["lo0.0"]
  }
```
  Then add prose under the System block:
  `- \`ssh.root_login\`: allow | deny | deny-password | null. \`ssh.rate_limit\`/\`connection_limit\`: ints or null. Generic across vendors (SRX \`system services ssh\`, Cisco \`ssh\`/\`http\` servers, Palo/Forti admin access).`
  `- \`auth\`: password policy + login lockout + whether a root credential is set. \`control_plane_protection.re_filter_present\`: a stateless device/control-plane protection filter is applied (SRX lo0 input filter; Cisco CoPP; Palo/Forti mgmt profile). All optional; absent → the dependent check skips.`

- [ ] **Step 3: Add a new `## Security Services` section** immediately after the `## System` section:
````markdown
## Security Services

```json
{
  "app_id": true,
  "idp": true,
  "secintel": true,
  "aamw": true,
  "utm": true
}
```

Presence flags for advanced security services configured on the device
(application identification, IDP/IPS, security intelligence, advanced anti-malware,
UTM). The audit's SEC-SERVICES-UNREFERENCED check compares these against
`security_policies[].security_profiles` to find configured-but-inert services.
Populated where the vendor parser supports it; absent → the check is skipped.
````

- [ ] **Step 4: Register `security_services` in the Top-Level Structure block.** In the `## Top-Level Structure` JSON (near `"system": {}`), add `"security_services": {},` so consumers know the key exists.

- [ ] **Step 5: Propagate canonical → other 3 copies and verify byte-identical.**

Run:
```bash
cd /home/mharman/fwskillsshare
for v in cisco fortinet palo; do
  cp skills/parsing-srx-configs/references/intermediate-schema.md skills/parsing-$v-configs/references/intermediate-schema.md
done
python3 scripts/check-shared-schema.py
```
Expected: `OK: all 4 intermediate-schema.md files match (<hash>)`.

- [ ] **Step 6: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/parsing-*/references/intermediate-schema.md
git commit -m "feat(schema): add ssh/auth/control-plane/screen/security-services fields"
```

---

### Task 2: Teach the SRX parser to populate the new fields

**Files:**
- Modify: `skills/parsing-srx-configs/SKILL.md` (extraction pipeline + version)

**Interfaces:**
- Consumes: the schema fields from Task 1.
- Produces: documented parser extraction rules that populate `system.ssh`, `system.auth`, `system.control_plane_protection`, `zones[].screen`, `security_services`.

- [ ] **Step 1: Bump the version.** In frontmatter change `version: 1.1.0` to `version: 1.2.0`.

- [ ] **Step 2: Extend the System extraction (section "### 10. System Configuration").** Add bullets:
```
- `system.services.ssh` { `root-login`, `rate-limit`, `ciphers`, `protocol-version`, `connection-limit` } → `system.ssh` (omit/null absent keys; root-login defaults to Junos `deny-password` when unset).
- `system.login.password` { `minimum-length`→min_length, `change-type`→complexity, `minimum-changes` } and `system.login.retry-options` { `tries-before-disconnect`→tries, `lockout-period` } → `system.auth.password_policy` / `system.auth.login_lockout`. Set `system.auth.root_authentication_present: true` when `system.root-authentication` exists.
```

- [ ] **Step 3: Add control-plane-protection extraction (under "### 11. Infrastructure").** Add:
```
- **Control-plane / RE protection:** when a stateless `firewall { family inet filter <name> }` is applied as an interface input filter on `lo0` (`interfaces lo0 unit N family inet filter input <name>`), set `system.control_plane_protection { re_filter_present: true, applied_to: ["lo0.<N>"] }`. The filter terms still go to `residual_raw`; this is a presence flag, not a full parse.
```

- [ ] **Step 4: Add screen-binding + security-services extraction.** Under the Screen extraction note add:
```
- **Screen zone binding:** for each `security.zones.security-zone.<z>.screen <name>`, set `zones[].screen = <name>`. The screen option detail continues to populate the Screen/IDS Config object.
- **Security services presence:** set `security_services` flags true when present: `services application-identification`→app_id, `security idp` / `services idp` (security-package)→idp, `services security-intelligence`→secintel, `services advanced-anti-malware`→aamw, `security utm`→utm.
```

- [ ] **Step 5: Verify frontmatter + that the new fields are documented.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
t=Path("skills/parsing-srx-configs/SKILL.md").read_text()
fm=yaml.safe_load(t[3:t.find("\n---",3)])
assert fm["version"]=="1.2.0", fm["version"]
for f in ["system.ssh","system.auth","control_plane_protection","zones[].screen","security_services"]:
    assert f in t, f"parser does not document {f}"
print("OK parser documents new fields; version", fm["version"])
EOF
```
Expected: `OK parser documents new fields; version 1.2.0`.

- [ ] **Step 6: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/parsing-srx-configs/SKILL.md
git commit -m "feat(parser): populate ssh/auth/control-plane/screen/security-services from SRX config"
```

---

### Task 3: Add the new checks to the audit catalog

**Files:**
- Modify: `skills/firewall-best-practices-audit/references/check-catalog.md`

**Interfaces:**
- Consumes: schema fields from Task 1.
- Produces: 9 new check IDs (the contract Tasks 4–5 reference): `SEC-SSH-ROOT-LOGIN`, `SEC-SERVICES-UNREFERENCED`, `SEC-ZONES-NAT-NO-POLICY`, `SEC-EMPTY-POLICYSET`, `SEC-HOST-INBOUND-EXPOSURE`, `SEC-NO-SCREEN`, `OPS-LOG-COMPLETENESS`, `SEC-AUTH-HARDENING`, `SEC-IPV6-POSTURE`.

- [ ] **Step 1: Append the 9 new checks** to the catalog, in the existing entry format (`- ID — detects — schema fields — SEVERITY — confidence`), grouped under their Security/Operational sections:
```
- SEC-SSH-ROOT-LOGIN — SSH permits root login or uses weak ciphers / no rate-limit — `system.ssh` (`root_login`, `ciphers`, `rate_limit`) — HIGH — definitive
- SEC-SERVICES-UNREFERENCED — a configured security service is attached to no policy (inert security stack) — `security_services` vs `security_policies[].security_profiles` — HIGH — heuristic (depends on profile capture)
- SEC-ZONES-NAT-NO-POLICY — zones/NAT exist but no security_policies reference them — `zones`, `nat_rules`, `security_policies` — HIGH — heuristic
- SEC-EMPTY-POLICYSET — security_policies is empty: emit a coverage warning rather than staying silent; distinguish default-deny-by-design from partial config / logical-system / tenant — `security_policies`, `_logical_system`/`_tenant` markers — MEDIUM — definitive
- SEC-HOST-INBOUND-EXPOSURE — management/sensitive host-inbound services on an untrusted/data zone — `zones[].host_inbound.system_services` — MEDIUM — heuristic
- SEC-NO-SCREEN — an external/untrust zone has no screen bound (binding absence is definitive; classifying a zone as external is heuristic — key off zone name and the default-route-facing interface) — `zones[].screen`, `zones[].interfaces`, `static_routes` — MEDIUM — heuristic
- OPS-LOG-COMPLETENESS — no remote security-log stream/host target configured — `system` syslog/security-log fields — MEDIUM — definitive
- SEC-AUTH-HARDENING — missing/weak password policy or login lockout — `system.auth` (`password_policy`, `login_lockout`) — MEDIUM — definitive
- SEC-IPV6-POSTURE — interfaces have inet6 addresses but no corresponding v6 controls/policies — `interfaces[].ipv6`, `security_policies` — LOW — heuristic
```

- [ ] **Step 2: Refine SEC-NO-DENY-ALL.** Edit its existing entry's description so it notes the SRX implicit-deny exists and the recommendation is an explicit *logged* deny-all for visibility (not just enforcement). Keep its id/severity/confidence.

- [ ] **Step 3: Verify catalog count + unique ids + new ids present.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re
from pathlib import Path
t=Path("skills/firewall-best-practices-audit/references/check-catalog.md").read_text()
ids=re.findall(r'^- ((?:SEC|OPS)-[A-Z0-9-]+) —', t, re.M)
new=["SEC-SSH-ROOT-LOGIN","SEC-SERVICES-UNREFERENCED","SEC-ZONES-NAT-NO-POLICY","SEC-EMPTY-POLICYSET","SEC-HOST-INBOUND-EXPOSURE","SEC-NO-SCREEN","OPS-LOG-COMPLETENESS","SEC-AUTH-HARDENING","SEC-IPV6-POSTURE"]
assert len(ids)==len(set(ids)), "dup ids"
for n in new: assert n in ids, f"missing {n}"
assert len(ids)>=39, f"expected >=39, got {len(ids)}"
print("OK catalog:",len(ids),"checks; all 9 new present")
EOF
```
Expected: `OK catalog: 39 checks; all 9 new present`.

- [ ] **Step 4: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/references/check-catalog.md
git commit -m "feat(audit): add 9 v1.1 checks for mgmt/control-plane/auth/security-service coverage"
```

---

### Task 4: Audit body + remediation for the new checks

**Files:**
- Modify: `skills/firewall-best-practices-audit/SKILL.md` (frontmatter version, Input Handling, Audit Workflow)
- Modify: `skills/firewall-best-practices-audit/references/remediation-patterns.md`

**Interfaces:**
- Consumes: the 9 check IDs from Task 3.

- [ ] **Step 1: Bump audit-skill version.** In frontmatter change `version: 1.0.0` to `version: 1.1.0`.

- [ ] **Step 2: Update Input Handling.** Add one sentence that the audit now also reads `system.ssh`, `system.auth`, `system.control_plane_protection`, `zones[].screen`, and `security_services`, and that any absent field skips its dependent check (the v1.1 coverage). Keep the section concise.

- [ ] **Step 3: Update the Audit Workflow** step 3 ("Run the security checks") to mention the new families: SSH/management hardening, security-services-unreferenced, zone/NAT-without-policy, host-inbound exposure, screen presence, auth hardening, and the empty-policyset coverage warning. One added clause, not a rewrite.

- [ ] **Step 4: Add remediation families** to `remediation-patterns.md` for the new checks, each with the SRX fix authoritative and a one-line cross-vendor note where the concept maps. Cover at minimum:
  - SSH root-login/hardening — SRX `set system services ssh root-login deny` (+ `no-passwords`/`connection-limit`/`rate-limit`); note Cisco `no ip http server`/SSH, Palo/Forti admin access.
  - Security-services-unreferenced — attach the service to a permit policy (SRX `then permit application-services { ... }`).
  - Zones/NAT-without-policy + empty-policyset — add explicit permit policies for intended flows + a logged global deny.
  - Host-inbound exposure — SRX remove mgmt services from `host-inbound-traffic` on untrust.
  - No-screen — SRX bind a screen to the external zone.
  - Auth hardening — SRX `set system login password` policy + `retry-options` lockout.
  Use placeholders; no real secrets.

- [ ] **Step 5: Verify version + new check coverage in body/remediation.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
t=Path("skills/firewall-best-practices-audit/SKILL.md").read_text()
fm=yaml.safe_load(t[3:t.find("\n---",3)])
assert fm["version"]=="1.1.0", fm["version"]
d=re.sub(r'\s+',' ',re.search(r'^description:\s*(.*?)(?=^\w[\w-]*:|\Z)',t[3:t.find(chr(10)+"---",3)],re.M|re.S).group(1)).strip()
assert len(d)<=1024, len(d)
rem=Path("skills/firewall-best-practices-audit/references/remediation-patterns.md").read_text().lower()
for kw in ["root-login","screen","application-services","retry-options"]:
    assert kw in rem, f"remediation missing {kw}"
print("OK body v1.1, desc",len(d),"chars; remediation families added")
EOF
```
Expected: `OK body v1.1, desc <N> chars; remediation families added`.

- [ ] **Step 6: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/SKILL.md skills/firewall-best-practices-audit/references/remediation-patterns.md
git commit -m "feat(audit): wire v1.1 checks into body + per-vendor remediation"
```

---

### Task 5: Rebuild the worked example from the real vSRX-Production parse

**Files:**
- Modify: `skills/firewall-best-practices-audit/references/example-audit.md`

**Interfaces:**
- Consumes: the 9 check IDs (Task 3); the Finding/Summary templates in the audit body.

**Ground-truth facts about `vSRX-Production` (Junos 25.4R1), to base the example on — do NOT fabricate beyond these:**
- `security_policies`: **empty** (only `policies { policy-rematch }`).
- `zones`: `trust` (ge-0/0/1.0, ge-0/0/3.0; host_inbound dhcp/ping/dns), `untrust` (ge-0/0/0.0; **screen `untrust-screen` bound**; host_inbound ping only), `IoT` (ge-0/0/2.0; host_inbound dhcp/ping/dns).
- `nat_rules`: source `trust→untrust` (0.0.0.0/0 → interface), source `IoT→untrust` (0.0.0.0/0 → interface).
- `system.ssh.root_login` = `allow`; rate_limit 32.
- `system.auth`: password_policy present (min_length 12, complexity character-sets), login_lockout present (tries 3, lockout 5), root_authentication_present true. → **good, so SEC-AUTH-HARDENING does NOT fire.**
- `system.control_plane_protection.re_filter_present` = true (PROTECT-RE on lo0.0). → good.
- `security_services`: app_id, idp, secintel, aamw, utm all true; no policy references any → SEC-SERVICES-UNREFERENCED fires.
- security log stream to 192.168.1.150:514 present → OPS-LOG-COMPLETENESS does NOT fire.
- ge-0/0/0 has an inet6 address; no v6 policy.

- [ ] **Step 1: Rewrite `example-audit.md`** as a worked audit of this vSRX-Production-shaped schema. Name the source (`vSRX-Production`, Junos 25.4R1, parsed via parsing-srx-configs). Emit findings using the exact Finding template for the checks that GENUINELY fire: `SEC-EMPTY-POLICYSET`, `SEC-ZONES-NAT-NO-POLICY`, `SEC-SERVICES-UNREFERENCED`, `SEC-SSH-ROOT-LOGIN`, `SEC-NO-DENY-ALL`, and `SEC-IPV6-POSTURE` (Low). Explicitly note in prose that SEC-NO-SCREEN, SEC-AUTH-HARDENING, and OPS-LOG-COMPLETENESS do **not** fire because those controls are present (demonstrates findings-only: present control → no finding). End with the Audit Summary template (posture line, severity tally, skipped checks like SEC-WEAK-IKE/OPS-ZERO-HIT, top fixes). Every id must exist in the catalog; SRX remediation snippets only; redact secrets.

- [ ] **Step 2: Verify the example uses only catalog ids, shows the v1.1 checks, and avoids the present-control false positives.**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re
from pathlib import Path
cat=set(re.findall(r'(?:SEC|OPS)-[A-Z0-9-]+', Path("skills/firewall-best-practices-audit/references/check-catalog.md").read_text()))
ex=Path("skills/firewall-best-practices-audit/references/example-audit.md").read_text()
used=set(re.findall(r'\[((?:SEC|OPS)-[A-Z0-9-]+)\]', ex))
assert used <= cat, f"unknown ids: {used-cat}"
for must in ["SEC-EMPTY-POLICYSET","SEC-SERVICES-UNREFERENCED","SEC-SSH-ROOT-LOGIN"]:
    assert must in used, f"example should fire {must}"
assert "vSRX-Production" in ex and "Posture:" in ex
# present controls must NOT be flagged as findings
assert "[SEC-NO-SCREEN]" not in ex, "SEC-NO-SCREEN must not fire (untrust screen present)"
assert "[SEC-AUTH-HARDENING]" not in ex, "auth is hardened; must not fire"
print("OK example fires", sorted(used))
EOF
```
Expected: `OK example fires [...]` including the three required ids, without SEC-NO-SCREEN/SEC-AUTH-HARDENING.

- [ ] **Step 3: Commit**

```bash
cd /home/mharman/fwskillsshare
git add skills/firewall-best-practices-audit/references/example-audit.md
git commit -m "feat(audit): rebuild worked example from real vSRX-Production parse (v1.1 checks)"
```

---

### Task 6: Validation, housekeeping, re-sync

**Files:**
- Modify: `TODO.md` (tick the 14 v1.1 items), `README.md` (note v1.1 / parser v1.2.0 where versions/schema are described)

- [ ] **Step 1: Full repo validation (frontmatter + reference pointers + schema sync).**

Run:
```bash
cd /home/mharman/fwskillsshare && python3 - <<'EOF'
import re,yaml
from pathlib import Path
fail=0
for p in sorted(Path("skills").glob("*/SKILL.md")):
    d=p.parent.name; t=p.read_text(); e=t.find("\n---",3); fm=t[3:e]; body=t[e+4:]
    yaml.safe_load(fm)
    for ref in set(re.findall(r'references/([A-Za-z0-9._-]+)', body)):
        if not (p.parent/"references"/ref).exists(): print("dangling",d,ref); fail+=1
print(("OK" if not fail else f"{fail} FAIL"),"—",len(list(Path('skills').glob('*/SKILL.md'))),"skills")
EOF
python3 scripts/check-shared-schema.py
```
Expected: `OK — 18 skills` and `OK: all 4 intermediate-schema.md files match`.

- [ ] **Step 2: Tick the v1.1 TODO items.** In `TODO.md` PRIORITY PROJECT section, change every `- [ ]` under the schema-extensions and new-checks lists to `- [x]`. Add a one-line "Completed 2026-06-29 — see plan docs/superpowers/plans/2026-06-29-firewall-best-practices-audit-v1.1.md" note under the section heading.

- [ ] **Step 3: Note versions in README.** Where the README lists the audit skill / schema, add that the audit skill is v1.1 (mgmt/control-plane/auth/security-service checks) and the SRX parser is v1.2.0. Keep it to the existing style.

- [ ] **Step 4: Re-sync changed skills into the user dir + parity.**

Run:
```bash
cd /home/mharman/fwskillsshare
for n in firewall-best-practices-audit parsing-srx-configs parsing-cisco-configs parsing-fortinet-configs parsing-palo-configs; do
  rm -rf "$HOME/.claude/skills/$n" && cp -r "skills/$n" "$HOME/.claude/skills/$n"
  diff -rq "skills/$n" "$HOME/.claude/skills/$n" >/dev/null && echo "PARITY OK $n" || echo "DIFF $n"
done
```
Expected: `PARITY OK` for all 5.

- [ ] **Step 5: Commit**

```bash
cd /home/mharman/fwskillsshare
git add TODO.md README.md
git commit -m "docs: tick v1.1 TODO items, note audit v1.1 / parser v1.2.0 in README"
```

---

## Controller-run final regression (not a subagent task)

After Task 6, the controller re-runs the live test through `rust-junosmcp`:
`get_junos_config(vSRX-Production)` → apply `parsing-srx-configs` (now v1.2.0) → apply `firewall-best-practices-audit` (now v1.1). Confirm the catalog now produces multiple findings (target: SEC-EMPTY-POLICYSET, SEC-ZONES-NAT-NO-POLICY, SEC-SERVICES-UNREFERENCED, SEC-SSH-ROOT-LOGIN, SEC-NO-DENY-ALL, SEC-IPV6-POSTURE) vs. the single finding in v1.0 — closing the regression the test write-up requires. Record the result (secrets redacted); optionally append to `docs/skill-tests/2026-06-29-vsrx-production-audit.md` as a v1.1 re-test note.

## Notes for the executor

- Author Markdown in full prose at execution time; the plan fixes structure, exact field names, the exact check list, ground-truth facts, and verification gates.
- Do NOT invent schema fields beyond those in Task 1. If a check needs data the schema does not carry, mark it data-dependent/skipped (graceful degradation), as v1.0 does.
- Keep the audit body lean; heavy detail lives in references/.
