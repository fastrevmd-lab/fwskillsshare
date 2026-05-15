# Resolution Guide - SRX - Troubleshoot Source NAT

Source: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Source-NAT
Article ID: KB21611
Created: 2011-08-11
Last Updated: 2017-03-04
Retrieved: 2026-05-15

---

## Description

This article assists with Source NAT troubleshooting in a step-by-step approach.

Symptoms:

- Clients on a private network cannot get to the Internet because there is an issue with Source NAT.
- Source NAT is not working.

## Troubleshooting Steps

1. Confirm the configuration:

```text
show security nat source
```

If the configuration is wrong, correct it, generate traffic again, and retest.

2. Determine whether the source NAT configuration uses interface NAT or a source NAT pool.

- Interface NAT: proceed to rule-hit and flow troubleshooting.
- Source NAT pool: continue to pool/proxy-ARP checks when applicable.

3. If the NAT pool is from the same subnet as the SRX external interface, verify proxy ARP.

Example condition: NAT pool `1.1.1.2` through `1.1.1.4`, SRX external interface `1.1.1.1/24`.

```text
show security nat proxy-arp
```

If proxy ARP is missing for pool addresses that must be L2 reachable, configure it and retest.

4. Check source NAT rule translation hits:

```text
show security nat source rule <name>
show security nat source rule all
```

If translation hits increment but traffic still fails, inspect sessions. If hits do not increment, check NAT rule order and matching conditions.

5. Check for a flow session for the source IP and destination IP:

```text
show security flow session source-prefix <source-ip> destination-prefix <destination-ip> extensive
```

If a session exists, inspect both wings and confirm the correct translated source IP/port appears.

6. If session wings show correct translated IPs, NAT is likely working and another feature may be dropping or filtering packets, such as an egress firewall filter, routing issue, upstream filtering, or return-path issue.

7. If NAT rule order is wrong, reorder specific source NAT rules above broader catch-all rules and retest.

8. Configure traceoptions with packet filters for the source IP and destination IP. Use the trace to identify packet drops.

9. If the issue cannot be isolated, collect SRX NAT/flow logs and data collection outputs for support.
