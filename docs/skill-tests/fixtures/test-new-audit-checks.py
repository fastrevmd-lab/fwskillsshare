#!/usr/bin/env python3
"""Test fixture demonstrating SEC-NAME-ACTION-MISMATCH and SEC-PLAINTEXT-FEED-TRANSPORT.

This script validates the two new checks added to firewall-best-practices-audit:
1. SEC-NAME-ACTION-MISMATCH — rule names contradicting their configured action
2. SEC-PLAINTEXT-FEED-TRANSPORT — threat feeds fetched over plaintext HTTP

Usage: python3 test-new-audit-checks.py
"""
import re
from typing import Any

# Test data: policies with name-action mismatches
policies_with_mismatch = [
    {
        "name": "185-Explicit_deny_WAN_to_LAN",
        "action": "allow",
        "src_zones": ["untrust"],
        "dst_zones": ["trust"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": False,
        "log_end": False,
    },
    {
        "name": "DENY-GUEST-TO-CORP",
        "action": "allow",
        "src_zones": ["guest"],
        "dst_zones": ["corporate"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": False,
        "log_end": False,
    },
    {
        "name": "ALLOW-USERS-WEB",
        "action": "deny",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "src_addresses": ["users-net"],
        "dst_addresses": ["any"],
        "applications": ["junos-http", "junos-https"],
        "log_start": True,
        "log_end": False,
    },
]

# Test data: clean policies (no mismatch)
policies_clean = [
    {
        "name": "ALLOW-WEB-ACCESS",
        "action": "allow",
        "src_zones": ["trust"],
        "dst_zones": ["untrust"],
        "src_addresses": ["internal-nets"],
        "dst_addresses": ["any"],
        "applications": ["junos-http", "junos-https"],
        "log_start": False,
        "log_end": True,
    },
    {
        "name": "DENY-REST",
        "action": "deny",
        "src_zones": ["any"],
        "dst_zones": ["any"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "log_end": False,
    },
    {
        "name": "100-users-to-web",  # No action word in name
        "action": "allow",
        "src_zones": ["trust"],
        "dst_zones": ["dmz"],
        "src_addresses": ["users"],
        "dst_addresses": ["web-servers"],
        "applications": ["junos-https"],
        "log_start": False,
        "log_end": True,
    },
]

# Test data: edge cases that should NOT fire
policies_edge_cases = [
    {
        "name": "do-not-deny-guest",  # Negation, should not match
        "action": "allow",
        "src_zones": ["guest"],
        "dst_zones": ["dmz"],
        "src_addresses": ["guest-net"],
        "dst_addresses": ["any"],
        "applications": ["junos-http"],
        "log_start": False,
        "log_end": True,
    },
    {
        "name": "deny-or-allow-based-on-context",  # Both words, ambiguous
        "action": "allow",
        "src_zones": ["trust"],
        "dst_zones": ["dmz"],
        "src_addresses": ["any"],
        "dst_addresses": ["any"],
        "applications": ["any"],
        "log_start": True,
        "log_end": False,
    },
]

# Test data: address objects with feed transport
address_objects_with_feeds = [
    # Plaintext HTTP - should fire
    {
        "name": "blocklist-http",
        "type": "dynamic",
        "value": "feed:blocklist",
        "dynamic_source": {
            "kind": "feed",
            "selector": ["blocklist"],
            "feed_name": "blocklist",
            "feed_url": "http://threats.example.com/blocklist.txt",
            "feed_transport": "http",
        },
    },
    # HTTPS - should not fire
    {
        "name": "blocklist-https",
        "type": "dynamic",
        "value": "feed:blocklist",
        "dynamic_source": {
            "kind": "feed",
            "selector": ["blocklist"],
            "feed_name": "blocklist",
            "feed_url": "https://threats.example.com/blocklist.txt",
            "feed_transport": "https",
        },
    },
    # GeoIP - should not fire (not a feed)
    {
        "name": "Banned_countries",
        "type": "dynamic",
        "value": "geoip:RU,KP,IR",
        "dynamic_source": {
            "kind": "geoip",
            "selector": ["RU", "KP", "IR"],
            "feed_name": "",
            "feed_url": "",
            "feed_transport": "",
        },
    },
    # Regular static object - should not fire
    {
        "name": "web-server",
        "type": "host",
        "value": "10.0.1.10/32",
        "description": "Production web server",
    },
]


def check_name_action_mismatch(policy: dict[str, Any]) -> bool:
    """Return True if the policy name contradicts its configured action.

    Conservative matching to avoid false positives:
    - Whole-word boundaries treating hyphens and underscores as separators
    - Exclude negations (do-not-deny, no-allow, not-deny)
    - Skip rules whose names mention both actions (deny-or-allow)
    """
    name = policy.get("name", "")
    action = policy.get("action", "")

    # Patterns for action words. Use word boundaries that treat - and _ as separators.
    # (?<![a-zA-Z0-9]) = not preceded by alphanumeric
    # (?![a-zA-Z0-9]) = not followed by alphanumeric
    # This allows matching "deny" in "foo-deny-bar" or "foo_deny_bar" but not "foodenyphobia"
    deny_pattern = r'(?<![a-zA-Z0-9])(?:deny|block|drop|reject)(?![a-zA-Z0-9])'
    allow_pattern = r'(?<![a-zA-Z0-9])(?:allow|permit)(?![a-zA-Z0-9])'

    # Check for negations that would reverse the meaning
    # Match patterns like "do-not-deny", "no_allow", "not-permit"
    negation_pattern = r'(?<![a-zA-Z0-9])(?:do[-_]?not|no|not)[-_]?(?:deny|block|drop|reject|allow|permit)(?![a-zA-Z0-9])'

    if re.search(negation_pattern, name, re.IGNORECASE):
        return False  # Negations are excluded

    has_deny_word = bool(re.search(deny_pattern, name, re.IGNORECASE))
    has_allow_word = bool(re.search(allow_pattern, name, re.IGNORECASE))

    # Skip if both action words appear (ambiguous)
    if has_deny_word and has_allow_word:
        return False

    # Mismatch: name says deny but action is allow
    if has_deny_word and action == "allow":
        return True

    # Mismatch: name says allow but action is deny/drop/reset-both
    if has_allow_word and action in ("deny", "drop", "reset-both"):
        return True

    return False


def check_plaintext_feed(addr_obj: dict[str, Any]) -> bool:
    """Return True if the address object is a feed fetched over plaintext HTTP."""
    if addr_obj.get("type") != "dynamic":
        return False

    dynamic_source = addr_obj.get("dynamic_source", {})
    if dynamic_source.get("kind") != "feed":
        return False

    # Check feed_transport first (definitive)
    feed_transport = dynamic_source.get("feed_transport", "")
    if feed_transport == "http":
        return True

    # Also check feed_url as fallback
    feed_url = dynamic_source.get("feed_url", "")
    if feed_url.startswith("http://"):
        return True

    return False


def main() -> None:
    """Run all test cases and report results."""
    failures: list[str] = []
    print("Testing SEC-NAME-ACTION-MISMATCH")
    print("=" * 60)

    print("\n## Expected to fire (name contradicts action):")
    for policy in policies_with_mismatch:
        if check_name_action_mismatch(policy):
            print(f"  ✓ FIRED: {policy['name']!r} (name suggests deny/block but action={policy['action']})")
        else:
            print(f"  ✗ MISSED: {policy['name']!r} should have fired but didn't")
            failures.append(f"missed: {policy['name']!r}")

    print("\n## Expected to stay silent (name matches action):")
    for policy in policies_clean:
        if check_name_action_mismatch(policy):
            print(f"  ✗ FALSE POSITIVE: {policy['name']!r} fired but shouldn't have")
            failures.append(f"false positive: {policy['name']!r}")
        else:
            print(f"  ✓ SILENT: {policy['name']!r} (correct)")

    print("\n## Edge cases (should stay silent):")
    for policy in policies_edge_cases:
        if check_name_action_mismatch(policy):
            print(f"  ✗ FALSE POSITIVE: {policy['name']!r} (has negation/ambiguity)")
            failures.append(f"false positive (negation/ambiguity): {policy['name']!r}")
        else:
            print(f"  ✓ SILENT: {policy['name']!r} (negation/ambiguity correctly excluded)")

    print("\n" + "=" * 60)
    print("Testing SEC-PLAINTEXT-FEED-TRANSPORT")
    print("=" * 60)

    print("\n## Expected to fire (HTTP feed):")
    for obj in address_objects_with_feeds:
        if check_plaintext_feed(obj):
            url = obj.get("dynamic_source", {}).get("feed_url", "")
            print(f"  ✓ FIRED: {obj['name']!r} (feed over HTTP: {url})")
        else:
            # Only report missed if it's the HTTP one
            if obj["name"] == "blocklist-http":
                print(f"  ✗ MISSED: {obj['name']!r} should have fired but didn't")
                failures.append(f"missed: {obj['name']!r}")

    print("\n## Expected to stay silent (HTTPS or non-feed):")
    for obj in address_objects_with_feeds:
        if not check_plaintext_feed(obj):
            kind = obj.get("dynamic_source", {}).get("kind", obj.get("type"))
            print(f"  ✓ SILENT: {obj['name']!r} ({kind}, not plaintext feed)")
        else:
            # Only report false positive if it's not the HTTP one
            if obj["name"] != "blocklist-http":
                print(f"  ✗ FALSE POSITIVE: {obj['name']!r} fired but shouldn't have")
                failures.append(f"false positive: {obj['name']}")

    print("\n" + "=" * 60)
    if failures:
        print(f"FAILED — {len(failures)} incorrect result(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("All tests completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
