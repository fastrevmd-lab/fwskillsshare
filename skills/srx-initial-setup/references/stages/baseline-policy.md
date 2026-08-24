# Stage 5 — Baseline Policy

This stage establishes the **minimum** security policy required to make the device usable: explicit outbound access for essential services, default-deny behavior, and logging. This is not a complete policy design — it is the foundational structure that later policy work builds upon.

## The minimum, and why it is the minimum

A usable Branch SRX requires:

1. **Outbound internet access** for DNS, NTP, and basic web browsing from the LAN. Without this, time synchronization fails, name resolution fails, and users cannot reach the internet.
2. **Default-deny behavior** as the backstop. If no explicit rule matches, traffic is denied. This is a security fundamental.
3. **Session logging** on key policies to provide visibility into what traffic is permitted or denied.

**This stage provides only these three elements.** It does not design application-aware policies, URL filtering, intrusion prevention, or advanced security services. Those belong to `srx-policy`.

**Why this is the minimum:**

- **Outbound access is required for device operation:** The device itself needs DNS and NTP (configured in Stage 2). LAN clients need DNS and web access to be useful. An SRX with no outbound permit policy is a device that cannot resolve names or reach the internet.
- **Default-deny is required for security:** Without an explicit deny-all policy at the bottom of the table, traffic not matching any permit rule may be silently dropped (Junos default behavior) but the operator has no log visibility into what is being blocked. An explicit default-deny with logging makes the security posture clear and measurable.
- **Logging is required for operations:** Without session logs, the operator cannot troubleshoot connectivity issues, verify policy is working as intended, or detect attacks. Logging at session-close provides a record of permitted flows without flooding logs with every packet.

**What this is not:**

- This is not a complete security policy. It is a baseline that makes the device functional.
- This is not application-aware. The baseline uses port-based applications (HTTP, HTTPS, DNS) because AppID signatures, dynamic applications, and deep inspection are out of scope for initial setup.
- This is not segmented. The baseline assumes a simple trust-to-untrust flow. Multi-zone policies, DMZ isolation, and cross-zone LAN segmentation are later work.

**All gaps in this stage have `lockout_risk: false`.** Adding permit policies and default-deny does not affect management reachability. The gate protocol in `references/write-safety.md` applies to this skill's lockout-risk changes in other stages.

## Default deny and logging

Junos SRX implements implicit deny: if no policy matches, traffic is dropped. However, relying on implicit behavior provides no log visibility.

**Best practice:** Add an explicit default-deny policy as the **last** rule in the global policy table. Configure it with `session-init` logging so that denied flows generate log entries, making it clear what traffic is being blocked.

**Syntax:**

```text
set security policies global policy 999-DEFAULT-DENY match source-address any
set security policies global policy 999-DEFAULT-DENY match destination-address any
set security policies global policy 999-DEFAULT-DENY match application any
set security policies global policy 999-DEFAULT-DENY then deny
set security policies global policy 999-DEFAULT-DENY then log session-init
```

**Source:** Juniper Networks, "Configuring Security Policies" (Junos OS Security Policies), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html

The documentation states: "If there is no matching policy, the packet is dropped." It also documents logging options: "Enable logging at the end of a session with the `session-close` command" or "Enable at the beginning using `session-init`."

**Why `session-init` for the default-deny:** Denied flows never complete a session, so `session-close` logging would not capture them. Using `session-init` logs the denial attempt when the first packet arrives, providing visibility into blocked traffic.

**Why `session-close` for permit policies:** Permitted flows complete sessions. Logging at `session-close` records the full session (duration, bytes transferred, applications) without generating a log entry for every packet. This balances visibility with log volume.

## Global policy structure

This skill enforces the use of **global policies** for greenfield and day-one onboarding work, consistent with the `srx-policy` skill's documented position.

**Source:** `skills/srx-policy/SKILL.md` (this repository), section "Enforced Global-Policy Output Contract."

The `srx-policy` skill states: "For greenfield, migration, and onboarding work, generated policy MUST use `security policies global`; express zones only as `match from-zone` and `match to-zone` fields inside each global policy. Do not preserve zone-pair structure merely because it appears in the input."

**Why global policy:**

- Most vendor firewalls already use a single ordered policy table with source zone, destination zone, source, destination, service/application, action, and logging as fields.
- Global policy matches this model naturally: one table, ordered rules, zone matching inside each policy.
- It avoids duplicating the same logical rule across every zone pair.
- It pairs naturally with the global address book and application objects.
- It is easier to review, diff, reorder, and migrate than separate zone-pair contexts.

**Syntax for global policy:**

```text
set security policies global policy <policy-name> match from-zone <source-zone>
set security policies global policy <policy-name> match to-zone <destination-zone>
set security policies global policy <policy-name> match source-address <address-or-any>
set security policies global policy <policy-name> match destination-address <address-or-any>
set security policies global policy <policy-name> match application <application-or-any>
set security policies global policy <policy-name> then permit
set security policies global policy <policy-name> then log session-close
```

**Source for global policy syntax:** Juniper Networks, "Global Security Policies" (Junos OS Security Policies), retrieved 2026-08-20.
URL: https://juniper.net/documentation/en_US/junos/topics/topic-map/security-global-policies.html#id-global-policy-overview

The documentation confirms: "Unlike other security policies in Junos OS, global policies do not reference specific source and destination zones, but instead reference the predefined address 'any' or user-defined addresses that can span multiple security zones." It also documents the `match from-zone` and `match to-zone` statements for zone-specific matching within global policies.

**Policy ordering:**

Global policies are evaluated in the order they appear in the configuration. The first matching policy is applied. **Critical:** Place specific permit rules before broad deny rules, and place the default-deny as the last rule.

**Example order:**

1. `100-TRUST-TO-UNTRUST-DNS` — Permit DNS from trust to untrust
2. `110-TRUST-TO-UNTRUST-WEB` — Permit HTTP/HTTPS from trust to untrust
3. `120-TRUST-TO-UNTRUST-NTP` — Permit NTP from trust to untrust
4. `999-DEFAULT-DENY` — Deny all other traffic

## Explicit zone-to-zone opt-out

**Default:** This skill generates Day-1 baseline policy under `security policies global` only. Global policy is the only policy model this skill produces.

**Zone-pair exceptions route by platform.** When the caller opts into one of the three exceptions documented in `skills/srx-policy/SKILL.md`, section "Enforced Global-Policy Output Contract", this skill does not generate policy at all — the baseline-policy stage routes policy design as follows:

- **Non-Branch platforms** (SRX1600, SRX4120, SRX4300, SRX4700, SRX5000, vSRX): route to `skills/srx-policy/`, which owns zone-pair design for non-Branch platforms and already has a working zone-pair generation path.
- **Branch platforms** (SRX300 series, SRX400 series): `skills/srx-policy/` scopes itself to "non-Branch SRX platforms" (see its description and scope statement). **No skill in this repository currently owns Branch zone-pair policy design.** The operator designs it manually, or extends and validates `srx-policy` for Branch platforms first.

The three named exceptions are:

1. **Existing-estate compatibility** where structural change is outside scope;
2. **An isolated exception** that is clearer and safer as a zone-pair policy;
3. **A customer standard or toolchain** that requires zone-pair contexts.

**What still applies under an opt-out:** Stages 1 through 4 (access and recovery, management plane, interfaces and zones, screens) apply unchanged. Only the baseline-policy stage hands off.

**Caller responsibility:** When an exception applies, the caller must:

- State which exception applies and why global policy is unsuitable for this specific baseline;
- Constrain the zone-pair scope to only the zones where the exception is necessary;
- Keep all other generated rules global.

**Not implicit opt-outs:** A small initial rulebase, the presence of zone-pair syntax in prior configurations, or a staged migration plan do not constitute implicit opt-outs. Repeated rules across zone pairs require a global rewrite unless the caller explicitly selects an exception and provides the rationale.

**Rationale:** See `skills/srx-policy/SKILL.md`, section "Enforced Global-Policy Output Contract" and "Explicit Zone-to-Zone Opt-Out" for the complete reasoning behind this position.

**Verification:** Without an opt-out, the proposed set-format configuration must contain no matches for `set security policies from-zone` and every baseline rule must start with `set security policies global policy` with `match from-zone` and `match to-zone` fields. With an opt-out, this skill proposes no policy configuration at all and the verification check does not apply here — verification belongs to `srx-policy` for non-Branch platforms or to the operator for Branch platforms.


## Gaps

### `policy.global-policy-absent`

- **Stage:** baseline-policy
- **Severity:** `blocking`
- **Depends on:** `zone.trust-absent`, `zone.untrust-absent`
- **Lockout risk:** `false` (creating a policy table does not change traffic flow; policies must be committed and activated)
- **Zone-pair opt-out handoff:** When a zone-pair exception is selected, this gap is transferred to `srx-policy` (non-Branch platforms) or to the operator (Branch platforms). The gap is satisfied when a policy configuration exists and is verified by that party, whatever its structure.
- **Evidence:** `show configuration security policies global` returns no configuration
- **Proposal:**

  Initialize the global policy hierarchy:

  ```text
  set security policies global
  ```

  This creates the configuration hierarchy for global policies. No policies are defined yet.

  **Source:** Same as "Global policy structure" section above.

### `policy.explicit-outbound`

- **Stage:** baseline-policy
- **Severity:** `blocking`
- **Depends on:** `policy.global-policy-absent`, all `zone.*` gaps closed
- **Lockout risk:** `false` (adding permit policies does not break existing flows; removing or changing them can)
- **Zone-pair opt-out handoff:** When a zone-pair exception is selected, this gap is transferred to `srx-policy` (non-Branch platforms) or to the operator (Branch platforms). The gap is satisfied when a policy configuration exists and is verified by that party, whatever its structure.
- **Evidence:** `show configuration security policies global` returns no policies, or existing policies do not permit trust-to-untrust outbound traffic for essential services (DNS, HTTP, HTTPS, NTP)
- **Proposal:**

  ```text
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS match from-zone trust
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS match to-zone untrust
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS match source-address any
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS match destination-address any
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS match application junos-dns-udp
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS then permit
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS then log session-close

  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match from-zone trust
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match to-zone untrust
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match source-address any
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match destination-address any
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match application junos-http
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match application junos-https
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB then permit
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB then log session-close

  set security policies global policy 120-TRUST-TO-UNTRUST-NTP match from-zone trust
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP match to-zone untrust
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP match source-address any
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP match destination-address any
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP match application junos-ntp
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP then permit
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP then log session-close
  ```

  **Reasoning:** These three policies permit the minimum outbound traffic required for a functional Branch deployment:

  - **DNS (junos-dns-udp):** Required for name resolution by the device and LAN clients.
  - **HTTP and HTTPS (junos-http, junos-https):** Required for web browsing by LAN clients and for the device to reach external services (software updates, cloud management, license activation).
  - **NTP (junos-ntp):** Required for time synchronization by the device and optionally by LAN clients.

  **Why these applications:** The `junos-dns-udp`, `junos-http`, `junos-https`, and `junos-ntp` applications are predefined in Junos and match the standard port/protocol combinations for these services. Using predefined applications avoids custom application definitions for basic services.

  **Why `session-close` logging:** These are permit policies. Logging at session-close records completed sessions without flooding logs with session-init entries for every connection.

  **Why `source-address any` and `destination-address any`:** This baseline does not implement source-based restrictions (e.g., only certain LAN subnets can browse the web) or destination-based restrictions (e.g., only certain DNS servers are allowed). Those refinements belong to later policy work in `srx-policy`.

  **Status:** UNVERIFIED. The multiple `match application` statements on a single policy (as shown in `110-TRUST-TO-UNTRUST-WEB`) assume Junos treats multiple `match application` lines as OR logic (match HTTP OR HTTPS). This is the expected behavior for global policies, but the exact CLI syntax and matching logic should be verified against current Junos OS documentation for the SRX300/400 Branch platforms.

  If multiple `match application` statements are not supported in a single policy, the alternative is to create separate policies for HTTP and HTTPS, or to define an application-set:

  ```text
  set applications application-set WEB-SERVICES application junos-http
  set applications application-set WEB-SERVICES application junos-https
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB match application WEB-SERVICES
  ```

  **Source for predefined applications:** Juniper Networks, "Security Policy Applications and Application Sets" (Junos OS Security Policies), documented in `skills/srx-policy/SKILL.md` metadata sources, retrieved 2026-05-15 (as cited in srx-policy).
  URL: https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/policy-application-sets-configuration.html

  **Cross-reference to factory.permissive-policy:** This gap is the replacement for the factory-default trust-to-untrust permit-any policy documented in `skills/srx-initial-setup/references/factory-default-branch.md`. The factory policy allows all applications; this baseline allows only DNS, HTTP, HTTPS, and NTP. Closing `factory.permissive-policy` depends on this gap being closed first.

### `policy.default-deny-absent`

- **Stage:** baseline-policy
- **Severity:** `blocking`
- **Depends on:** `policy.explicit-outbound`
- **Lockout risk:** `false` (adding a default-deny at the bottom of the table does not block traffic already permitted by earlier rules; it only makes the implicit deny explicit and logged)
- **Zone-pair opt-out handoff:** When a zone-pair exception is selected, this gap is transferred to `srx-policy` (non-Branch platforms) or to the operator (Branch platforms). The gap is satisfied when a policy configuration exists and is verified by that party, whatever its structure.
- **Evidence:** `show configuration security policies global` returns policies, but no final deny-all rule with logging exists
- **Proposal:**

  ```text
  set security policies global policy 999-DEFAULT-DENY match source-address any
  set security policies global policy 999-DEFAULT-DENY match destination-address any
  set security policies global policy 999-DEFAULT-DENY match application any
  set security policies global policy 999-DEFAULT-DENY then deny
  set security policies global policy 999-DEFAULT-DENY then log session-init
  ```

  **Reasoning:** This policy matches all traffic that was not matched by earlier rules and explicitly denies it. The `session-init` logging generates log entries for denied flows, providing visibility into what traffic is being blocked.

  **Why policy name `999-DEFAULT-DENY`:** The numeric prefix ensures this policy sorts to the bottom of the table. Junos evaluates policies in configuration order, so the default-deny must be last.

  **Why `match source-address any`, `match destination-address any`, `match application any`:** This policy is a catch-all. It matches everything.

  **Critical ordering requirement:** If policies are added after the default-deny using `set` commands, they may be inserted **after** the default-deny in the configuration order, rendering them unreachable (shadowed). Use `insert` commands to place new policies before the default-deny, or re-verify the final order before commit:

  ```text
  show configuration security policies global | display set
  ```

  Expect the default-deny to appear as the **last** policy in the output.

  **Source:** Same as "Default deny and logging" section above.

### `policy.logging-unconfigured`

- **Stage:** baseline-policy
- **Severity:** `advisory` (logging is operationally important but not a blocker for connectivity)
- **Depends on:** `policy.explicit-outbound`, `policy.default-deny-absent`
- **Lockout risk:** `false`
- **Zone-pair opt-out handoff:** When a zone-pair exception is selected, this gap is transferred to `srx-policy` (non-Branch platforms) or to the operator (Branch platforms). The gap is satisfied when a policy configuration exists and is verified by that party, whatever its structure.
- **Evidence:** Policies exist but `show configuration security policies global | match log` returns no logging configuration on permit policies
- **Proposal:**

  If permit policies were created without logging, add it:

  ```text
  set security policies global policy 100-TRUST-TO-UNTRUST-DNS then log session-close
  set security policies global policy 110-TRUST-TO-UNTRUST-WEB then log session-close
  set security policies global policy 120-TRUST-TO-UNTRUST-NTP then log session-close
  ```

  If the default-deny was created without logging, add it:

  ```text
  set security policies global policy 999-DEFAULT-DENY then log session-init
  ```

  **Reasoning:** Without logging, the operator has no visibility into which policies are matching, what traffic is being permitted or denied, or whether the baseline is working as intended.

  **Source:** Same as "Default deny and logging" section above.

## Where this stage stops

This stage establishes the **minimum** policy structure. The following policy design and security service topics are explicitly **out of scope** for this skill and belong to `srx-policy`:

- **Application Firewall (AppFW):** Dynamic application identification and blocking (e.g., blocking YouTube streaming while permitting general HTTPS). Requires AppID signatures and AppFW rule-sets. See `srx-policy` references for AppFW configuration.

- **NextGen Web Filtering (NGWF):** URL category filtering, reputation-based blocking, and cloud-based web filtering. Preferred for Junos 23.4R1+ greenfield designs. See `srx-policy` references for NGWF vs EWF decision framework and configuration.

- **Enhanced Web Filtering (EWF):** On-box or redirected URL filtering. Treat as existing-estate or compatibility path when NGWF is unavailable. See `srx-policy` references for EWF configuration and migration to NGWF.

- **Security Intelligence (SecIntel):** Dynamic threat feeds for malicious IP addresses, domains, and URLs. Requires subscriptions and feed connectivity. See `srx-policy` references for SecIntel integration.

- **Advanced Threat Prevention (ATP):** Malware analysis, sandboxing, and verdict-based enforcement. Requires ATP Cloud or ATP Appliance integration. See `srx-policy` references for ATP placement and workflow.

- **Policy design beyond the baseline:** Source-based restrictions (e.g., only certain LAN subnets can access the internet), destination-based restrictions (e.g., block social media sites), application-specific rules (e.g., permit Zoom but block gaming), time-based policies, user-based policies (requires authentication), and multi-zone policies (DMZ, guest, IoT segmentation). All of these are policy **design** work, not initial setup. See `srx-policy` for greenfield policy design workflows.

- **Intrusion Prevention (IDP):** Signature-based attack detection and blocking. Requires IDP-SIG license and signature updates. Out of scope for this skill; consult Juniper IDP documentation or `srx-license-signature-maintenance` for signature management.

**Handoff to srx-policy:**

Once this stage closes, the device has a working baseline policy:

- Outbound internet access for essential services (DNS, HTTP, HTTPS, NTP)
- Default-deny with logging
- Global policy structure ready for expansion

**The next step is policy design**, not configuration. The operator should:

1. Identify business requirements: What applications and services must be permitted? What should be blocked?
2. Design segmentation: Should the LAN be divided into multiple zones (users, servers, IoT, guest)?
3. Choose security services: Is URL filtering required? Application control? Threat intelligence?
4. Use `srx-policy` to design, migrate, and configure the production policy that meets these requirements.

**Do not expand the baseline policy in this skill.** The baseline is intentionally minimal. Feature-rich policies belong in `srx-policy`.

## Verification

After this stage closes, verify:

1. **Global policy table exists:**

   ```text
   show security policies global
   ```

   Expect at least three permit policies (DNS, web, NTP) and one default-deny policy.

2. **Policy order is correct:**

   ```text
   show configuration security policies global | display set
   ```

   Expect permit policies to appear before the default-deny. The default-deny should be the **last** policy in the output.

3. **Policy hit counts (after traffic flows):**

   ```text
   show security policies hit-count
   ```

   Expect non-zero hit counts on the permit policies if LAN clients are generating traffic. Expect hit counts on the default-deny only if traffic is being blocked (which is expected for unsolicited inbound traffic from untrust, and for any LAN traffic not matching the permit policies).

4. **Session logging is working:**

   ```text
   show log messages | match RT_FLOW
   ```

   Expect `RT_FLOW_SESSION_CLOSE` log entries for permitted sessions, and `RT_FLOW_SESSION_DENY` entries for denied sessions.

   **Source for log message format:** Junos generates session log entries with `RT_FLOW` tags. This is common Junos logging behavior, but the exact log format and message structure are platform and release-specific. Verify log output on the target device.

5. **Traffic is flowing:**

   External connectivity tests (`nslookup example.com`, `curl http://example.com`, `curl https://example.com`) require source NAT, which this skill does not configure — see `srx-nat` for NAT configuration. Without NAT, these tests fail even when the baseline policy is correct. Test policy effectiveness via hit counts and log entries, not external reachability. See `references/verification.md` for the complete verification protocol.

All `policy.*` gaps are now closed. The device has a minimal working policy. Further policy design and security service configuration are handled by `srx-policy`.
