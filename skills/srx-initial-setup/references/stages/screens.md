# Stage 4 — Starter Screens

This stage applies a conservative set of IDS screen options to detect and block common network attacks. Screens provide defense-in-depth by inspecting traffic at the zone interface before security policy processing.

## What screens are and are not

Screens are **not** a substitute for security policy. They are a complementary layer that detects protocol anomalies, malformed packets, and known attack patterns. Screens operate before policy lookup, providing early filtering of malicious traffic.

**What screens do:**

- Detect and block known attack signatures (TCP flag anomalies, IP option abuse, ICMP attacks)
- Detect excessive traffic patterns (floods, sweeps, scans) based on thresholds
- Validate packet sanity (malformed headers, illegal combinations)
- Operate at the security zone level, before policy processing

**Source:** Juniper Networks, "Screens Options for Attack Detection and Prevention" (Junos OS Denial of Service Protection), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/topics/topic-map/security-introduction-to-adp.html

The documentation states that screens inspect traffic "prior to the security policy processing, resulting in less resource utilization" and provide protection "against different internal and external attacks."

**What screens are not:**

- **Not a firewall:** Screens do not replace security policies. A permit policy is still required for legitimate traffic to flow between zones.
- **Not application-aware:** Screens operate at the network and transport layers (IP, ICMP, TCP, UDP). They do not inspect application payloads or perform deep packet inspection. Application-level filtering requires AppFW, UTM, or other security services.
- **Not a substitute for proper segmentation:** Screens can block attacks, but they do not establish trust boundaries. Security zones and policies define segmentation.
- **Not stateful at the application layer:** Screens perform stateful inspection at the protocol level (tracking SYN/ACK sequences, fragment reassembly) but do not understand application state.

**Critical limitation:** Screens can produce false positives. An overly aggressive screen configuration can drop legitimate traffic, especially in environments with high connection rates, legitimate network scanning tools, or fragmented traffic. The starter profile below is deliberately conservative to minimize false positives in a normal Branch deployment.

**All gaps in this stage have `lockout_risk: false`.** Changes proposed here do not affect management reachability. The gate protocol in `references/write-safety.md` applies to this skill's lockout-risk changes in other stages.

## The starter profile

This table documents the screen options proposed for a conservative starter profile. Only options with **low or documented false-positive risk** are enabled by default. Options that can interfere with legitimate traffic in a normal Branch deployment are marked as advisory and not included in the applied configuration.

| Screen Option | What It Blocks | False-Positive Risk | In Starter Profile? | Why |
|---|---|---|---|---|
| **IP Screens** |
| `source-route-option` | IP packets with loose or strict source routing options | **Low** — Source routing is rarely used in legitimate traffic and is a known attack vector | **Yes** | Source routing can bypass firewall policies and is not needed in Branch deployments |
| `record-route-option` | IP packets with record-route option set | **Low** — Rarely used in production traffic; primarily a diagnostic tool | **Yes** | Not required for normal operations; can be exploited |
| `timestamp-option` | IP packets with timestamp option set | **Low** — Rarely used in production traffic | **Yes** | Not required for normal operations |
| `bad-option` | IP packets with unrecognized or malformed IP options | **Very Low** — Malformed options are not legitimate | **Yes** | Protects against option-based attacks |
| `ip-spoofing` | IP packets with source addresses from a protected network arriving on an external interface | **Low to Medium** — Requires correct interface trust direction configuration; false positives occur if interface directionality is misconfigured | **Advisory** | Effective when properly configured, but requires validation of internal address ranges and interface directionality |
| **ICMP Screens** |
| `ping-death` | Oversized ICMP echo request packets (ping of death attack) | **Very Low** — Legitimate ping packets are not oversized | **Yes** | Classic attack; no legitimate reason for oversized ICMP packets |
| `icmp-flood` (threshold-based) | ICMP packets exceeding configured threshold | **Medium to High** — Legitimate network monitoring, troubleshooting, and availability checks can trigger threshold | **Advisory** | Useful in environments with known baseline; requires tuning to avoid blocking legitimate monitoring |
| `icmp-fragment` | ICMP packets with IP fragmentation | **Low** — Fragmented ICMP is unusual and can indicate evasion attempts | **Yes** | Fragmented ICMP is not required for normal ping or traceroute |
| **TCP Screens** |
| `syn-fin` | TCP packets with both SYN and FIN flags set | **Very Low** — This combination is illegal per RFC 793 | **Yes** | Never occurs in legitimate TCP; clear attack signature |
| `fin-no-ack` | TCP packets with FIN flag set but no ACK flag | **Very Low** — Violates TCP state machine | **Yes** | Not a valid TCP flag combination |
| `tcp-no-flag` | TCP packets with no flags set (null scan) | **Very Low** — Never legitimate | **Yes** | Clear scanning or evasion technique |
| `syn-frag` | TCP SYN packets with IP fragmentation | **Very Low** — SYN packets should fit in a single packet | **Yes** | Fragmented SYN is an evasion technique |
| `tcp-sweep` (threshold-based) | Multiple TCP connection attempts to different ports from a single source | **High** — Legitimate network inventory tools, vulnerability scanners, and even some monitoring systems perform port enumeration | **Advisory** | Effective against reconnaissance, but legitimate scanning tools and administrative tasks trigger it |
| `syn-flood` (threshold-based) | Excessive TCP SYN packets from a source or to a destination | **Medium to High** — High-traffic web servers, load balancers, and connection-heavy applications can exceed thresholds during normal operation | **Advisory** | Useful with proper baseline tuning; default thresholds may cause false positives on busy servers |
| `land-attack` | TCP packets with identical source and destination IP and port | **Very Low** — Never occurs in legitimate traffic | **Yes** | Classic denial-of-service attack |
| `winnuke` | TCP packets targeting known WinNuke vulnerabilities (port 139 with out-of-band data) | **Very Low** — Attack-specific signature; not legitimate traffic | **Yes** | Targets obsolete Windows vulnerability; safe to block |
| **UDP Screens** |
| `udp-flood` (threshold-based) | Excessive UDP packets exceeding threshold | **Medium to High** — Legitimate high-volume UDP applications (VoIP, video streaming, gaming, DNS under load) can exceed thresholds | **Advisory** | Requires tuning per deployment; default thresholds risk blocking legitimate UDP-heavy applications |
| `udp-sweep` (threshold-based) | Multiple UDP packets to different ports from a single source | **Medium to High** — Legitimate service discovery (mDNS, SSDP), network monitoring, and diagnostics trigger this | **Advisory** | Effective against reconnaissance, but normal IoT discovery and troubleshooting produce sweeps |
| **Fragment Screens** |
| `tear-drop` | Overlapping IP fragment offsets | **Very Low** — Legitimate fragmentation does not produce overlapping fragments | **Yes** | Fragment overlap is a known evasion and DoS technique |
| **IPv6 Screens** |
| `ipv6-malformed-header` | IPv6 packets with malformed headers | **Very Low** — Malformed headers are not legitimate | **Yes** (if IPv6 is deployed) | Protects against IPv6-specific attacks |
| `ipv6-extension-header-limit` | IPv6 packets exceeding recommended extension header count | **Low** — RFC 2460 recommends up to 7 extension headers; legitimate traffic rarely exceeds this | **Yes** (if IPv6 is deployed) | Prevents excessive header chaining used in evasion |

**Source for screen options and behaviors:** Juniper Networks, "Screens Options for Attack Detection and Prevention" (Junos OS Denial of Service Protection), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/topics/topic-map/security-introduction-to-adp.html

**Source for false-positive risk assessment:** Based on the Juniper documentation above, which states that signature-based screens (IP options, TCP flag anomalies, known attacks) operate on "clear attack signatures" with low false-positive risk, while threshold-based screens (floods, sweeps, session limits) require tuning and can affect "legitimate high-volume applications."

The documentation notes: "Only the first offending packet per screen per second generates a log message" (post-15.1X49-D20 release), indicating that high-volume legitimate traffic triggering a screen would generate repeated log entries — a sign that threshold tuning is needed.

## Binding to zones

Screens are applied at the security zone level, not per-interface. Create a screen profile (also called an `ids-option`), configure the desired screen options, then bind the profile to one or more security zones.

**Syntax:**

```text
set security screen ids-option <profile-name> <screen-category> <specific-screen>
set security zones security-zone <zone-name> screen <profile-name>
```

**Example:**

```text
set security screen ids-option STARTER-SCREENS ip source-route-option
set security screen ids-option STARTER-SCREENS ip record-route-option
set security screen ids-option STARTER-SCREENS ip bad-option
set security screen ids-option STARTER-SCREENS icmp ping-death
set security screen ids-option STARTER-SCREENS icmp icmp-fragment
set security screen ids-option STARTER-SCREENS tcp syn-fin
set security screen ids-option STARTER-SCREENS tcp fin-no-ack
set security screen ids-option STARTER-SCREENS tcp tcp-no-flag
set security screen ids-option STARTER-SCREENS tcp syn-frag
set security screen ids-option STARTER-SCREENS tcp land
set security screen ids-option STARTER-SCREENS tcp winnuke
set security screen ids-option STARTER-SCREENS ip tear-drop

set security zones security-zone untrust screen STARTER-SCREENS
set security zones security-zone trust screen STARTER-SCREENS
```

**Recommended binding:**

- **untrust zone:** Apply the starter profile to detect attacks from the internet.
- **trust zone:** Apply the starter profile to detect compromised internal hosts or rogue devices.
- **mgmt zone (if applicable):** Apply only if the mgmt zone accepts connections from untrusted sources. If mgmt zone is restricted to a known management network, screens may be omitted or use a lighter profile.

**Source:** Juniper Networks, "Screens Options for Attack Detection and Prevention" (Junos OS Denial of Service Protection), retrieved 2026-08-20.
URL: https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/topics/topic-map/security-introduction-to-adp.html

The documentation provides configuration examples showing screens created under `security screen ids-option` and then attached to zones via `set security zones security-zone [zone-name] screen [profile-name]`.

## Gaps

### `screen.starter-profile-absent`

- **Stage:** screens
- **Severity:** `advisory` (screens are defense-in-depth, not a blocker for basic connectivity)
- **Depends on:** `zone.trust-absent`, `zone.untrust-absent`
- **Lockout risk:** `false` (the starter profile contains only low-false-positive signature-based screens; it does not include aggressive threshold-based screens that might block legitimate traffic)
- **Evidence:** `show configuration security screen` returns no `ids-option` configuration, or the starter profile does not exist
- **Proposal:**

  ```text
  set security screen ids-option STARTER-SCREENS ip source-route-option
  set security screen ids-option STARTER-SCREENS ip record-route-option
  set security screen ids-option STARTER-SCREENS ip timestamp-option
  set security screen ids-option STARTER-SCREENS ip bad-option
  set security screen ids-option STARTER-SCREENS icmp ping-death
  set security screen ids-option STARTER-SCREENS icmp icmp-fragment
  set security screen ids-option STARTER-SCREENS tcp syn-fin
  set security screen ids-option STARTER-SCREENS tcp fin-no-ack
  set security screen ids-option STARTER-SCREENS tcp tcp-no-flag
  set security screen ids-option STARTER-SCREENS tcp syn-frag
  set security screen ids-option STARTER-SCREENS tcp land
  set security screen ids-option STARTER-SCREENS tcp winnuke
  set security screen ids-option STARTER-SCREENS ip tear-drop
  ```

  If IPv6 is deployed:

  ```text
  set security screen ids-option STARTER-SCREENS ipv6 ipv6-malformed-header
  set security screen ids-option STARTER-SCREENS ipv6 ipv6-extension-header-limit 7
  ```

  **Reasoning:** This profile includes only screens with very low or low false-positive risk. All are signature-based (detecting illegal flag combinations, malformed packets, or known attack patterns) rather than threshold-based.

  **Source:** Same as "Binding to zones" section above.

### `screen.untrust-binding-absent`

- **Stage:** screens
- **Severity:** `advisory`
- **Depends on:** `screen.starter-profile-absent`, `zone.untrust-absent`
- **Lockout risk:** `false`
- **Evidence:** The starter profile exists, but `show configuration security zones security-zone untrust` does not show `screen STARTER-SCREENS`
- **Proposal:**

  ```text
  set security zones security-zone untrust screen STARTER-SCREENS
  ```

  **Reasoning:** The untrust zone faces the internet and is the most likely source of attacks. Applying screens here provides early filtering before policy lookup.

  **Source:** Same as "Binding to zones" section above.

### `screen.trust-binding-absent`

- **Stage:** screens
- **Severity:** `advisory`
- **Depends on:** `screen.starter-profile-absent`, `zone.trust-absent`
- **Lockout risk:** `false`
- **Evidence:** The starter profile exists, but `show configuration security zones security-zone trust` does not show `screen STARTER-SCREENS`
- **Proposal:**

  ```text
  set security zones security-zone trust screen STARTER-SCREENS
  ```

  **Reasoning:** Applying screens to the trust zone detects compromised internal hosts or rogue devices. The starter profile's low false-positive risk makes it safe to apply to internal zones.

  **Source:** Same as "Binding to zones" section above.

### `screen.threshold-screens-advisory`

- **Stage:** screens
- **Severity:** `advisory`
- **Depends on:** `screen.starter-profile-absent`
- **Lockout risk:** `false` (this gap is informational; it does not propose a configuration change)
- **Evidence:** The starter profile is applied, but no threshold-based screens (SYN flood, ICMP flood, UDP flood, port scan, IP sweep) are configured
- **Proposal:**

  **This gap is advisory only.** Threshold-based screens require tuning to avoid false positives. The operator should:

  1. Establish a traffic baseline by monitoring logs and flow statistics for at least one week.
  2. Determine acceptable thresholds for SYN connections per second, ICMP packets per second, UDP packets per second, and scan attempt rates.
  3. Configure threshold-based screens with values above the observed baseline but below attack traffic levels.
  4. Test in `alarm-without-drop` mode first to verify no false positives before enabling drop mode.

  **Example configuration (not applied by default):**

  ```text
  set security screen ids-option THRESHOLD-SCREENS tcp syn-flood alarm-threshold 500
  set security screen ids-option THRESHOLD-SCREENS tcp syn-flood attack-threshold 1000
  set security screen ids-option THRESHOLD-SCREENS tcp syn-flood source-threshold 100
  set security screen ids-option THRESHOLD-SCREENS tcp syn-flood destination-threshold 500
  set security screen ids-option THRESHOLD-SCREENS tcp syn-flood timeout 20
  ```

  **Status:** UNVERIFIED. The exact threshold values and syntax for per-source and per-destination SYN flood limits have not been verified against current Junos OS SRX300/400 Branch documentation. The syntax above is a common pattern observed in screen configuration examples, but platform-specific behavior, supported threshold ranges, and CLI syntax should be confirmed before applying.

  **Reasoning:** Threshold-based screens are effective against DoS attacks, but incorrect thresholds cause false positives. The starter profile intentionally omits them to avoid disrupting legitimate traffic. Operators with specific DoS protection requirements should configure these screens separately after baselining.

  **Source for threshold concept and alarm-without-drop mode:** Juniper Networks, "Screens Options for Attack Detection and Prevention" (Junos OS Denial of Service Protection), retrieved 2026-08-20.
  URL: https://www.juniper.net/documentation/us/en/software/junos/denial-of-service/topics/topic-map/security-introduction-to-adp.html

  The documentation states: "`alarm-without-drop`—Direct the device to generate an alarm when detecting an attack but not block the attack." This mode is useful for validating that a threshold-based screen does not trigger on legitimate traffic before enabling drop mode.

## Verification

After this stage closes, verify:

1. **Starter profile exists:**

   ```text
   show security screen ids-option STARTER-SCREENS
   ```

   Expect the configured screen options to appear.

2. **Screens bound to zones:**

   ```text
   show security zones
   ```

   Expect `Screen: STARTER-SCREENS` to appear under the untrust and trust zones.

3. **Screen statistics (after traffic flows):**

   ```text
   show security screen statistics
   ```

   Expect zero or very low drop counts unless an actual attack is occurring. High drop counts on signature-based screens indicate either an attack or a misconfiguration. High drop counts on screens that are **not** in the starter profile (e.g., SYN flood, if manually added) may indicate false positives or a real attack.

4. **Logs for screen hits:**

   ```text
   show log messages | match "screen"
   ```

   Expect log entries only when attacks are detected. Continuous log entries for the same screen from legitimate sources indicate a false positive and the screen should be reviewed.

All `screen.*` gaps are now closed. Stage 5 (baseline policy) may proceed.
