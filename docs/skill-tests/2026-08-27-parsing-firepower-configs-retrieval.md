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

## Counting Standard

To ensure consistent and defensible token matching across all artifacts, the following rules are applied:

1. **Substring matches do not count.** A token must appear as a complete word or term, not as part of a longer word. Example: the endpoint name `ftdnatpolicies` in a description does not make "FTD" a match; "FTD" must appear standalone.

2. **Plural and singular forms are distinct tokens.** For strict token matching, "interface" and "interfaces" are different tokens. A description listing "interfaces" (plural) does not match an artifact containing only "interface" (singular).

3. **Only artifact content counts.** Tokens appearing only in an artifact's section heading or editorial label do not count as matches. The content is what a user would paste; headings are reader context.

4. **Hand-off clause tokens count but are labeled.** Tokens mentioned in a description's negative hand-off clause (e.g., "For ASA-style LINA running-config text such as access-list, nameif, or object network, use parsing-cisco-configs instead") are counted because they appear in the description text, even though they direct users elsewhere. These are explicitly labeled as "(hand-off)" to distinguish them from positive trigger tokens.

All token matches below were verified by grepping the actual description text before counting.

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
- accessPolicy (field name in artifact content)
- securityZones (field name in artifact content)

**Matched tokens in parsing-cisco-configs description:**
- (none)

**Predicted selection:** `parsing-firepower-configs` (2 matches vs 0)

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

**Predicted selection:** `parsing-cisco-configs` (4 matches vs 2)

**Note:** The artifact contains "interface" (singular) but the description specifies "interfaces" (plural), which are distinct tokens under the counting standard.

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
- access-list (mentioned in hand-off clause: "For ASA-style LINA running-config text such as access-list...")
- nameif (mentioned in hand-off clause)
- object network (mentioned in hand-off clause)

**Matched tokens in parsing-cisco-configs description:**
- FTD (appears in artifact header; appears in description as "Cisco ASA and FTD LINA")
- access-list (appears multiple times in artifact)
- access-group (appears in artifact)
- object network (appears in artifact)
- nameif (appears multiple times in artifact)
- security-level (appears multiple times in artifact)

**Predicted selection:** `parsing-cisco-configs` (6 matches vs 3)

**Result:** ✅ PASS

**Note:** This is the sharp case. The artifact is an FTD device's LINA-format running configuration. Although the Firepower description mentions `access-list`, `nameif`, and `object network` in its hand-off clause (directing such configs to parsing-cisco-configs), the Cisco description dominates with its FTD product token and full set of LINA syntax tokens. The standalone token "FTD" does NOT appear in the Firepower description (which lists "FMC and FDM", not "FTD"); the Firepower description contains only the compound endpoint name `ftdnatpolicies`, which is unrelated to the product token.

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
- accessrules (field name in artifact content)
- ftdnatpolicies (field name in artifact content)

**Matched tokens in parsing-cisco-configs description:**
- (none)

**Predicted selection:** `parsing-firepower-configs` (2 matches vs 0)

**Note:** "FDM" appears in the artifact's section heading but not in the JSON content itself, so it does not count under the content-only rule.

**Result:** ✅ PASS

---

## Summary

**Overall result:** 4 of 4 predictions correct (100%)

All four artifacts were correctly classified by token overlap:
- FMC JSON → `parsing-firepower-configs` (2 matches vs 0)
- ASA access-list/nameif → `parsing-cisco-configs` (4 matches vs 2)
- FTD LINA running-config → `parsing-cisco-configs` (6 matches vs 3)
- FDM accessrules JSON → `parsing-firepower-configs` (2 matches vs 0)

The sharp case (Artifact 3, FTD LINA running-config) correctly predicted `parsing-cisco-configs` because the artifact's ASA-style LINA syntax (`access-list`, `access-group`, `object network`, `nameif`, `security-level`) matches the Cisco description's trigger tokens, while the Firepower description only mentions these same tokens in its negative hand-off clause directing such configs elsewhere. The Firepower description does not claim the standalone product token "FTD" (it lists "FMC and FDM" instead, with `ftdnatpolicies` being an unrelated JSON endpoint name).

## Conclusion

The trigger-token overlap analysis confirms that `parsing-firepower-configs` and `parsing-cisco-configs` have sufficiently distinct descriptions to route artifacts to the correct skill without competition. The combined description budget (9,719 characters) remains under the 12,000-character soft limit.
