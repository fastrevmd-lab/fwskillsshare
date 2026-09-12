# Test: SEC-NAME-ACTION-MISMATCH and SEC-PLAINTEXT-FEED-TRANSPORT

**Date:** 2026-09-11
**Skill:** `firewall-best-practices-audit` v1.3.0
**Purpose:** Validate the two new checks added as follow-ups to the 2026-07-31 live-SRX audit

## Test Cases

### SEC-NAME-ACTION-MISMATCH

This check detects rules whose names contradict their configured action.

#### Case 1: Name says "deny" but action is permit (should fire)

**Input:**
```json
{
  "name": "185-Explicit_deny_WAN_to_LAN",
  "action": "allow",
  "src_zones": ["untrust"],
  "dst_zones": ["trust"],
  "src_addresses": ["any"],
  "dst_addresses": ["any"],
  "applications": ["any"]
}
```

**Expected:** FIRE — name contains "deny" but action is "allow"
**Result:** ✓ FIRED

---

#### Case 2: Name says "DENY" but action is permit (should fire)

**Input:**
```json
{
  "name": "DENY-GUEST-TO-CORP",
  "action": "allow",
  "src_zones": ["guest"],
  "dst_zones": ["corporate"],
  "src_addresses": ["any"],
  "dst_addresses": ["any"],
  "applications": ["any"]
}
```

**Expected:** FIRE — name contains "DENY" but action is "allow"
**Result:** ✓ FIRED

---

#### Case 3: Name says "ALLOW" but action is deny (should fire)

**Input:**
```json
{
  "name": "ALLOW-USERS-WEB",
  "action": "deny",
  "src_zones": ["trust"],
  "dst_zones": ["untrust"],
  "src_addresses": ["users-net"],
  "dst_addresses": ["any"],
  "applications": ["junos-http", "junos-https"]
}
```

**Expected:** FIRE — name contains "ALLOW" but action is "deny"
**Result:** ✓ FIRED

---

#### Case 4: Name matches action (should not fire)

**Input:**
```json
{
  "name": "ALLOW-WEB-ACCESS",
  "action": "allow",
  "src_zones": ["trust"],
  "dst_zones": ["untrust"],
  "src_addresses": ["internal-nets"],
  "dst_addresses": ["any"],
  "applications": ["junos-http", "junos-https"]
}
```

**Expected:** SILENT — name says "ALLOW" and action is "allow"
**Result:** ✓ SILENT

---

#### Case 5: Negation (should not fire)

**Input:**
```json
{
  "name": "do-not-deny-guest",
  "action": "allow",
  "src_zones": ["guest"],
  "dst_zones": ["dmz"],
  "src_addresses": ["guest-net"],
  "dst_addresses": ["any"],
  "applications": ["junos-http"]
}
```

**Expected:** SILENT — negation pattern excluded
**Result:** ✓ SILENT

---

#### Case 6: Ambiguous (both words present, should not fire)

**Input:**
```json
{
  "name": "deny-or-allow-based-on-context",
  "action": "allow",
  "src_zones": ["trust"],
  "dst_zones": ["dmz"],
  "src_addresses": ["any"],
  "dst_addresses": ["any"],
  "applications": ["any"]
}
```

**Expected:** SILENT — both "deny" and "allow" in name
**Result:** ✓ SILENT

---

### SEC-PLAINTEXT-FEED-TRANSPORT

This check detects threat feeds fetched over plaintext HTTP.

#### Case 7: HTTP feed (should fire)

**Input:**
```json
{
  "name": "blocklist-http",
  "type": "dynamic",
  "value": "feed:blocklist",
  "dynamic_source": {
    "kind": "feed",
    "selector": ["blocklist"],
    "feed_name": "blocklist",
    "feed_url": "http://threats.example.com/blocklist.txt",
    "feed_transport": "http"
  }
}
```

**Expected:** FIRE — feed over plaintext HTTP
**Result:** ✓ FIRED

---

#### Case 8: HTTPS feed (should not fire)

**Input:**
```json
{
  "name": "blocklist-https",
  "type": "dynamic",
  "value": "feed:blocklist",
  "dynamic_source": {
    "kind": "feed",
    "selector": ["blocklist"],
    "feed_name": "blocklist",
    "feed_url": "https://threats.example.com/blocklist.txt",
    "feed_transport": "https"
  }
}
```

**Expected:** SILENT — feed over HTTPS
**Result:** ✓ SILENT

---

#### Case 9: GeoIP (not a feed, should not fire)

**Input:**
```json
{
  "name": "Banned_countries",
  "type": "dynamic",
  "value": "geoip:RU,KP,IR",
  "dynamic_source": {
    "kind": "geoip",
    "selector": ["RU", "KP", "IR"],
    "feed_name": "",
    "feed_url": "",
    "feed_transport": ""
  }
}
```

**Expected:** SILENT — GeoIP, not a feed
**Result:** ✓ SILENT

---

#### Case 10: Static object (should not fire)

**Input:**
```json
{
  "name": "web-server",
  "type": "host",
  "value": "10.0.1.10/32",
  "description": "Production web server"
}
```

**Expected:** SILENT — static host object, not dynamic
**Result:** ✓ SILENT

---

## Matching Rules Documentation

### SEC-NAME-ACTION-MISMATCH

**Pattern matching:**
- **Action words detected:** "deny", "block", "drop", "reject", "allow", "permit" (case-insensitive)
- **Word boundary treatment:** Hyphens and underscores are treated as separators
  - Matches: "foo-deny-bar", "foo_deny_bar", "DENY-GUEST"
  - Does not match: "foodenyphobia", "allowance" (embedded in larger word)
- **Negation exclusion:** Patterns like "do-not-deny", "no-allow", "not-deny" are excluded
- **Ambiguity exclusion:** Names containing both "deny" AND "allow" are excluded

**Conservative approach:** The check is designed to minimize false positives by:
1. Requiring clear word boundaries (not substring matches)
2. Excluding negations that reverse the meaning
3. Excluding ambiguous names that mention both actions

### SEC-PLAINTEXT-FEED-TRANSPORT

**Detection logic:**
1. Check `address_objects[].type == "dynamic"`
2. Check `dynamic_source.kind == "feed"`
3. Check `dynamic_source.feed_transport == "http"` OR `dynamic_source.feed_url` starts with `"http://"`

**Platform support:**
- **SRX:** Fully supported (parser v1.4.0+ extracts `security dynamic-address feed-server`)
- **PAN-OS:** Heuristic/unsupported (depends on parser extracting external dynamic lists)
- **FortiGate:** Heuristic/unsupported (depends on parser extracting external threat feeds)
- **Cisco ASA/FTD:** Unsupported (ASA has no external feed URLs; FMC feeds are FMC-managed)

---

## Test Execution

**Command:**
```bash
python3 docs/skill-tests/fixtures/test-new-audit-checks.py
```

**Result:**
```
Testing SEC-NAME-ACTION-MISMATCH
============================================================

## Expected to fire (name contradicts action):
  ✓ FIRED: '185-Explicit_deny_WAN_to_LAN' (name suggests deny/block but action=allow)
  ✓ FIRED: 'DENY-GUEST-TO-CORP' (name suggests deny/block but action=allow)
  ✓ FIRED: 'ALLOW-USERS-WEB' (name suggests deny/block but action=deny)

## Expected to stay silent (name matches action):
  ✓ SILENT: 'ALLOW-WEB-ACCESS' (correct)
  ✓ SILENT: 'DENY-REST' (correct)
  ✓ SILENT: '100-users-to-web' (correct)

## Edge cases (should stay silent):
  ✓ SILENT: 'do-not-deny-guest' (negation/ambiguity correctly excluded)
  ✓ SILENT: 'deny-or-allow-based-on-context' (negation/ambiguity correctly excluded)

============================================================
Testing SEC-PLAINTEXT-FEED-TRANSPORT
============================================================

## Expected to fire (HTTP feed):
  ✓ FIRED: 'blocklist-http' (feed over HTTP: http://threats.example.com/blocklist.txt)

## Expected to stay silent (HTTPS or non-feed):
  ✓ SILENT: 'blocklist-https' (feed, not plaintext feed)
  ✓ SILENT: 'Banned_countries' (geoip, not plaintext feed)
  ✓ SILENT: 'web-server' (host, not plaintext feed)

============================================================
All tests completed.
```

**All test cases passed:** ✓

---

## Validation Summary

| Check | Test Cases | Passed | Failed |
|-------|-----------|---------|--------|
| SEC-NAME-ACTION-MISMATCH | 6 | 6 | 0 |
| SEC-PLAINTEXT-FEED-TRANSPORT | 4 | 4 | 0 |
| **Total** | **10** | **10** | **0** |

Both checks function as designed with no false positives or false negatives in the test suite.
