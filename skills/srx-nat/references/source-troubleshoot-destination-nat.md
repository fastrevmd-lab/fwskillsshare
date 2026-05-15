# Resolution Guide - SRX - Troubleshoot Destination NAT

Source: https://supportportal.juniper.net/s/article/Resolution-Guide-SRX-Troubleshoot-Destination-NAT
Article ID: KB21839
Created: 2011-09-13
Last Updated: 2020-08-14
Retrieved: 2026-05-15

---

## Description

This article assists with Destination NAT troubleshooting in a step-by-step approach.

Symptoms:

- Users on the Internet cannot access web servers hosted behind the SRX because there is an issue with Destination NAT.
- Destination NAT is not working.

## Troubleshooting Steps

1. Confirm the configuration:

```text
show security nat destination
```

If the configuration is wrong, correct it, generate traffic again, and retest.

2. Determine whether Destination NAT uses the external interface IP address.

- If yes, jump to rule-hit and flow troubleshooting.
- If no, continue to proxy ARP checks when the destination NAT address is on the same subnet as the external interface.

3. If the destination NAT IP address is in the same subnet as the external interface, verify proxy ARP:

```text
show security nat proxy-arp
```

If proxy ARP is missing, configure proxy ARP for the Destination NAT IP on the external interface and retest.

4. Check whether the NAT rule is being hit by viewing translation hits:

```text
show security nat destination rule <rulename>
show security nat destination rule all
```

If translation hits do not increase, verify that packets are reaching the SRX.

5. Use firewall filters to confirm ingress traffic reaches the external interface. If ingress counters do not increase, troubleshoot upstream network or ISP forwarding toward the SRX.

6. Configure flow traceoptions with packet filters for the client source IP and Destination NAT public IP. Use the trace to find where the packet is dropped.

7. If the drop location cannot be determined, collect SRX NAT/flow logs and open a case with Juniper support.
