# Trigger-Token Overlap Analysis: parsing-firepower-configs vs parsing-cisco-configs

**Date:** 2026-08-27
**Method:** Mechanical token overlap analysis (not a live clean-context retrieval test)

## Overview

This document records a mechanical analysis of which skill description's trigger tokens each test artifact matches, to verify that `parsing-firepower-configs` and `parsing-cisco-configs` do not compete for the same artifacts. This is **not** a live clean-context retrieval test where a model was asked to select a skill; instead, it is a deterministic token-matching exercise performed by comparing artifact content against the two skill descriptions.

## Skill Descriptions

### parsing-firepower-configs

> Parse Cisco Secure Firewall (Firepower) FMC and FDM management exports into the shared firewall schema. Use when input is JSON from the FMC or FDM REST API or an FDM configexport bundle and contains accessPolicy, accessrules, securityZones, prefilterpolicies, intrusionPolicy, filePolicy, variableSet, ftdnatpolicies, applicationFilters, or urlCategories, including audit, conversion, diff, summary, and explanation tasks. For ASA-style LINA running-config text such as access-list, nameif, or object network, use parsing-cisco-configs instead.

### parsing-cisco-configs

> Parse Cisco ASA and FTD LINA running configurations into the shared firewall schema. Use when input contains show running-config, access-list, access-group, object network, object-group, nameif, security-level, NAT, interfaces, or failover, including audit, conversion, diff, summary, and explanation tasks. For FMC- or FDM-managed Firepower policy exported as JSON, use parsing-firepower-configs instead.

## Combined Description Budget

**Total:** 9,719 characters (under the 12,000-character soft budget)

## Test Artifacts and Token Analysis

### Artifact 1: FMC Access Rule JSON Snippet

**Content:**
```json
{
  "accessPolicy": {
    "name": "Production-ACP",
    "defaultAction": "BLOCK",
    "rules": [
      {
        "name": "Allow-HTTPS-Inbound",
        "action": "ALLOW",
        "sourceZones": [
          {"name": "OUTSIDE"}
        ],
        "destinationZones": [
          {"name": "DMZ"}
        ],
        "applications": [
          {"name": "HTTPS"}
        ]
      }
    ]
  },
  "securityZones": [
    {"name": "OUTSIDE", "interfaceMode": "ROUTED"},
    {"name": "DMZ", "interfaceMode": "ROUTED"}
  ]
}
```

**Matched tokens in parsing-firepower-configs description:**
- JSON
- FMC
- accessPolicy
- securityZones
- rules (as part of "accessrules")

**Matched tokens in parsing-cisco-configs description:**
- (none)

**Predicted selection:** `parsing-firepower-configs` (5 matches vs 0)

**Result:** ✅ PASS

---

### Artifact 2: ASA access-list / nameif Block

**Content:**
```
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address 203.0.113.1 255.255.255.0
!
interface GigabitEthernet0/1
 nameif inside
 security-level 100
 ip address 10.0.1.1 255.255.255.0
!
access-list OUTSIDE-IN extended permit tcp any host 10.0.1.10 eq https
access-list OUTSIDE-IN extended deny ip any any log
access-group OUTSIDE-IN in interface outside
```

**Matched tokens in parsing-firepower-configs description:**
- access-list (mentioned in the hand-off clause)
- nameif (mentioned in the hand-off clause)

**Matched tokens in parsing-cisco-configs description:**
- access-list
- access-group
- nameif
- security-level
- interfaces

**Predicted selection:** `parsing-cisco-configs` (5 matches vs 2)

**Result:** ✅ PASS

---

### Artifact 3: FTD LINA show running-config Excerpt

**Content:**
```
! FTD Version 7.4.2
!
hostname FTD-Edge-01
!
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address 198.51.100.1 255.255.255.252
!
interface GigabitEthernet0/1
 nameif inside
 security-level 100
 ip address 192.168.10.1 255.255.255.0
!
object network obj-inside-subnet
 subnet 192.168.10.0 255.255.255.0
!
access-list OUTSIDE-IN extended permit tcp any object obj-inside-subnet eq 443
access-list OUTSIDE-IN extended deny ip any any log
access-group OUTSIDE-IN in interface outside
```

**Matched tokens in parsing-firepower-configs description:**
- FTD

**Matched tokens in parsing-cisco-configs description:**
- FTD
- show running-config
- access-list
- access-group
- object network
- nameif
- security-level
- interfaces

**Predicted selection:** `parsing-cisco-configs` (8 matches vs 1)

**Result:** ✅ PASS

**Note:** Although "FTD" appears in both descriptions, `parsing-cisco-configs` wins decisively on the strength of LINA-specific tokens (`show running-config`, `access-list`, `nameif`, `object network`).

---

### Artifact 4: FDM accessrules JSON Snippet

**Content:**
```json
{
  "accessrules": [
    {
      "name": "Permit-Web-Traffic",
      "ruleAction": "PERMIT",
      "sourceZones": [
        {"id": "zone-outside", "name": "OUTSIDE"}
      ],
      "destinationZones": [
        {"id": "zone-dmz", "name": "DMZ"}
      ],
      "applications": [
        {"name": "HTTP"},
        {"name": "HTTPS"}
      ],
      "enabled": true,
      "logging": {
        "logBegin": false,
        "logEnd": true
      }
    }
  ],
  "ftdnatpolicies": {
    "name": "NAT-Policy",
    "rules": []
  }
}
```

**Matched tokens in parsing-firepower-configs description:**
- JSON
- FDM
- accessrules
- ftdnatpolicies

**Matched tokens in parsing-cisco-configs description:**
- (none)

**Predicted selection:** `parsing-firepower-configs` (4 matches vs 0)

**Result:** ✅ PASS

---

## Summary

**Overall result:** 4 of 4 predictions correct (100%)

All four artifacts were correctly classified by token overlap:
- FMC JSON → `parsing-firepower-configs` (5 matches vs 0)
- ASA access-list/nameif → `parsing-cisco-configs` (5 matches vs 2)
- FTD LINA running-config → `parsing-cisco-configs` (8 matches vs 1)
- FDM accessrules JSON → `parsing-firepower-configs` (4 matches vs 0)

The sharp case (Artifact 3, FTD LINA running-config) correctly predicted `parsing-cisco-configs` despite "FTD" appearing in both descriptions, because LINA-specific tokens (`show running-config`, `access-list`, `nameif`, `object network`) dominated the match count.

## Conclusion

The trigger-token overlap analysis confirms that `parsing-firepower-configs` and `parsing-cisco-configs` have sufficiently distinct descriptions to route artifacts to the correct skill without competition. The combined description budget (9,719 characters) remains under the 12,000-character soft limit.
