# [SRX] Understanding and Using address-persistent in Source NAT on Juniper SRX

Source: https://supportportal.juniper.net/s/article/SRX-Understanding-and-Using-address-persistent-in-Source-NAT-on-Juniper-SRX
Article ID: KB101182
Created: 2025-07-25
Last Updated: 2025-07-25
Retrieved: 2026-05-15

---

## Description

This article explains the purpose, use case, and potential impact of the `address-persistent` knob in source NAT configuration on SRX. It describes scenarios where enabling or disabling this feature may help with application performance.

The `address-persistent` option in SRX source NAT configuration ensures that the same translated source IP address and port are consistently used for all sessions initiated by a specific source IP.

> Editor's note: `address-persistent` provides address affinity only — the same
> translated source IP for all sessions from a given source IP. Ports are still
> allocated per session (reusing one port across concurrent sessions would
> collide). Port preservation is a property of persistent NAT, a distinct feature.

While this behavior benefits certain protocols requiring stable NAT mappings, it may cause unintended issues with applications such as speedtest.net services that rely on varying NAT flows.

## Symptoms

When `address-persistent` is enabled:

- Unable to perform speed tests on websites like speedtest.net.
- Some users intermittently unable to load specific website elements, such as logos.
- VPN tunnels may fail to establish when using NAT with persistent address mapping.

## Solution

### Option 1: Disable address-persistent

If the environment does not require consistent source NAT mappings, remove the `address-persistent` configuration to allow dynamic port assignment.

```text
user@host# delete security nat source address-persistent
```

Note: `address-persistent` is global at `[edit security nat source]`, not under a rule.

### Option 2: Reduce TCP MSS to avoid fragmentation

In cases where traffic passes through a tunnel or WAN interface with smaller MTU, set TCP MSS to reduce fragmentation:

```text
user@host# set security flow tcp-mss all-tcp mss 1350
```
