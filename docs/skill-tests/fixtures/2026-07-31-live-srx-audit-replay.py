#!/usr/bin/env python3
"""Deterministic replay of the parsing-srx-configs extraction contract plus the
firewall-best-practices-audit v1.1 check catalog over a live SRX policy set.

Companion to `../2026-07-31-firewall-best-practices-audit-live-srx.md`.

Input: one or more files of `show configuration ... | display set` output. The
three arguments select where policies, address objects, and applications are
read from; pass the same whole-config file three times when it contains all of
them.

    python3 2026-07-31-live-srx-audit-replay.py config.set config.set config.set

Output: object counts followed by per-check finding rows. This script contains
no device data — supply your own capture.
"""
import ipaddress
import re
import sys
from collections import OrderedDict, defaultdict

POLICY_RE = re.compile(r"^set security policies global policy (\S+) (.*)$")


def parse_policies(path):
    """Parse global policies preserving configured order as _rule_index."""
    policies = OrderedDict()
    for raw in open(path):
        line = raw.strip()
        m = POLICY_RE.match(line)
        if not m:
            continue
        name, rest = m.group(1), m.group(2)
        pol = policies.setdefault(
            name,
            {
                "name": name,
                "_rule_index": len(policies),
                "src_addresses": [],
                "dst_addresses": [],
                "applications": [],
                "dynamic_applications": [],
                "src_zones": [],
                "dst_zones": [],
                "action": None,
                "log_start": False,
                "log_end": False,
                "description": None,
                "security_profiles": [],
                "disabled": False,
                "count": False,
            },
        )
        toks = rest.split()
        if toks[0] == "match":
            key, val = toks[1], " ".join(toks[2:])
            mapping = {
                "source-address": "src_addresses",
                "destination-address": "dst_addresses",
                "application": "applications",
                "dynamic-application": "dynamic_applications",
                "from-zone": "src_zones",
                "to-zone": "dst_zones",
            }
            if key in mapping:
                pol[mapping[key]].append(val)
        elif toks[0] == "then":
            if toks[1] in ("permit", "deny", "reject"):
                pol["action"] = {"permit": "allow", "deny": "deny", "reject": "reset-both"}[toks[1]]
                if len(toks) > 2 and toks[2] == "application-services":
                    pol["security_profiles"].append(" ".join(toks[3:]))
            elif toks[1] == "log":
                if "session-init" in toks:
                    pol["log_start"] = True
                if "session-close" in toks:
                    pol["log_end"] = True
            elif toks[1] == "count":
                pol["count"] = True
        elif toks[0] == "description":
            pol["description"] = " ".join(toks[1:]).strip('"')
    return list(policies.values())


def parse_addresses(path):
    """Parse address-book objects, address-sets, and dynamic-address objects.

    `security dynamic-address` entries are defined objects that policies
    reference exactly like address-book entries. Omitting them makes every
    referencing rule look like a dangling reference (SEC-ORPHAN-REF).
    """
    addrs, sets, dynamic = {}, defaultdict(list), {}
    for raw in open(path):
        t = raw.strip().split()
        if len(t) >= 6 and t[:5] == ["set", "security", "address-book", "global", "address"]:
            addrs[t[5]] = " ".join(t[6:])
        elif len(t) >= 8 and t[:5] == ["set", "security", "address-book", "global", "address-set"]:
            sets[t[5]].append(t[7])
        elif len(t) >= 5 and t[:4] == ["set", "security", "dynamic-address", "address-name"]:
            dynamic.setdefault(t[4], "dynamic")
    addrs.update(dynamic)
    return addrs, dict(sets), dynamic


def parse_apps(path):
    apps, appsets = defaultdict(dict), defaultdict(list)
    for raw in open(path):
        t = raw.strip().split()
        if len(t) >= 6 and t[1] == "applications" and t[2] == "application":
            apps[t[3]][t[4]] = t[5]
        elif len(t) >= 6 and t[1] == "applications" and t[2] == "application-set":
            appsets[t[3]].append(t[5])
    return dict(apps), dict(appsets)


def expand(name, groups, seen=None):
    """Flatten an address-set to leaf member names."""
    seen = seen or set()
    if name in seen:
        return []
    seen.add(name)
    if name not in groups:
        return [name]
    out = []
    for m in groups[name]:
        out.extend(expand(m, groups, seen))
    return out


def is_broad(value):
    """True when an address value is 0.0.0.0/0 or a supernet at or above /8."""
    try:
        net = ipaddress.ip_network(value, strict=False)
    except ValueError:
        return False
    return net.prefixlen <= 8


def main(pol_path, addr_path, app_path):
    policies = parse_policies(pol_path)
    addrs, groups, dynamic = parse_addresses(addr_path)
    apps, appsets = parse_apps(app_path)

    print(f"policies={len(policies)} addresses={len(addrs)} (of which dynamic={len(dynamic)}) address_sets={len(groups)} "
          f"applications={len(apps)} application_sets={len(appsets)}")

    findings = defaultdict(list)
    # Zones treated as untrusted for SEC-INBOUND-ANY.
    UNTRUSTED = {"UNTRUST"}
    # Words in a rule name that assert an action, for the name-vs-action check.
    DENY_WORDS = re.compile(r"deny|block|drop|reject", re.I)

    for p in policies:
        src_any = p["src_addresses"] == ["any"]
        dst_any = p["dst_addresses"] == ["any"]
        dynapp_any = p["dynamic_applications"] in ([], ["any"])
        # A rule scoped by dynamic-application is NOT an any-service rule.
        app_any = (p["applications"] == ["any"] or not p["applications"]) and dynapp_any
        logged = p["log_start"] or p["log_end"]

        if p["action"] == "allow":
            # SEC-ANY-ANY: any source AND any destination AND any service
            if src_any and dst_any and app_any:
                findings["SEC-ANY-ANY"].append((p["name"], "logged" if logged else "UNLOGGED"))
            # SEC-ANY-SVC: any service but specific src+dst
            elif app_any and not (src_any and dst_any):
                findings["SEC-ANY-SVC"].append((p["name"], f"{p['src_addresses']}->{p['dst_addresses']}"))
            # SEC-BROAD-SRC / SEC-BROAD-DST
            for a in p["src_addresses"]:
                if a == "any" or is_broad(addrs.get(a, "")):
                    findings["SEC-BROAD-SRC"].append((p["name"], a, addrs.get(a, "any")))
                    break
            for a in p["dst_addresses"]:
                if a == "any" or is_broad(addrs.get(a, "")):
                    findings["SEC-BROAD-DST"].append((p["name"], a, addrs.get(a, "any")))
                    break
            # SEC-NO-LOG
            if not logged:
                findings["SEC-NO-LOG"].append((p["name"],))
            # SEC-INBOUND-ANY: permit sourced from an untrusted zone with any source
            if src_any and UNTRUSTED.intersection(p["src_zones"]) and not UNTRUSTED.intersection(p["dst_zones"]):
                findings["SEC-INBOUND-ANY"].append(
                    (p["name"], "/".join(p["src_zones"]) + "->" + "/".join(p["dst_zones"]),
                     "any/any/any" if (dst_any and app_any) else "scoped dst/app"))

        # Name asserts deny/block but the configured action permits (no catalog check covers this).
        if p["action"] == "allow" and DENY_WORDS.search(p["name"]):
            findings["NAME-ACTION-MISMATCH"].append(
                (p["name"], "/".join(p["src_zones"]) + "->" + "/".join(p["dst_zones"]), "then permit"))
        # SEC-NO-DESC
        if not p["description"]:
            findings["SEC-NO-DESC"].append((p["name"],))
        # SEC-ORPHAN-REF
        for a in p["src_addresses"] + p["dst_addresses"]:
            if a != "any" and a not in addrs and a not in groups:
                findings["SEC-ORPHAN-REF"].append((p["name"], "address", a))
        for a in p["applications"]:
            if a not in ("any",) and not a.startswith("junos-") and a not in apps and a not in appsets:
                findings["SEC-ORPHAN-REF"].append((p["name"], "application", a))

    # SEC-NO-DENY-ALL: is the tail rule an any/any deny?
    tail = policies[-1] if policies else None
    if tail:
        tail_is_deny_all = (
            tail["action"] == "deny"
            and tail["src_addresses"] == ["any"]
            and tail["dst_addresses"] == ["any"]
            and (tail["applications"] == ["any"] or not tail["applications"])
            and tail["dynamic_applications"] in ([], ["any"])
        )
        if not tail_is_deny_all:
            findings["SEC-NO-DENY-ALL"].append((tail["name"], tail["action"], "tail is not an any/any deny"))
        elif not (tail["log_start"] or tail["log_end"]):
            findings["SEC-NO-DENY-ALL"].append((tail["name"], "deny-all present but UNLOGGED"))

    # SEC-REDUNDANT: identical match tuple + action
    seen = {}
    for p in policies:
        key = (
            tuple(sorted(p["src_zones"])), tuple(sorted(p["dst_zones"])),
            tuple(sorted(p["src_addresses"])), tuple(sorted(p["dst_addresses"])),
            tuple(sorted(p["applications"])),
            tuple(sorted(p["dynamic_applications"])), p["action"],
        )
        if key in seen:
            findings["SEC-REDUNDANT"].append((seen[key], p["name"]))
        else:
            seen[key] = p["name"]

    # SEC-SHADOW: an earlier same-zone-pair allow with any/any/any covers everything after it
    by_pair = defaultdict(list)
    for p in policies:
        by_pair[(tuple(sorted(p["src_zones"])), tuple(sorted(p["dst_zones"])))].append(p)
    for pair, group in by_pair.items():
        for i, earlier in enumerate(group):
            if earlier["action"] != "allow":
                continue
            if not (earlier["src_addresses"] == ["any"] and earlier["dst_addresses"] == ["any"]
                    and (earlier["applications"] == ["any"] or not earlier["applications"])):
                continue
            for later in group[i + 1:]:
                findings["SEC-SHADOW"].append((earlier["name"], later["name"], "/".join(pair[0]) + "->" + "/".join(pair[1])))

    # OPS-DUP-OBJ: same value, different name
    byval = defaultdict(list)
    for n, v in addrs.items():
        byval[v].append(n)
    for v, names in byval.items():
        if len(names) > 1:
            findings["OPS-DUP-OBJ"].append((v, names))

    # OPS-UNUSED-OBJ: defined but referenced by no policy, group, or NAT
    referenced = set()
    for p in policies:
        for a in p["src_addresses"] + p["dst_addresses"]:
            referenced.add(a)
            for leaf in expand(a, groups):
                referenced.add(leaf)
    for g, members in groups.items():
        if g in referenced:
            for leaf in expand(g, groups):
                referenced.add(leaf)
    unused = sorted(set(addrs) - referenced)
    unused_groups = sorted(set(groups) - referenced)

    # OPS-LARGE-GROUP / OPS-NESTED-GROUP
    for g in groups:
        n = len(expand(g, groups))
        if n >= 50:
            findings["OPS-LARGE-GROUP"].append((g, n))

    def depth(name, seen=None):
        seen = seen or set()
        if name in seen or name not in groups:
            return 0
        seen.add(name)
        return 1 + max([depth(m, seen) for m in groups[name]] or [0])

    for g in groups:
        d = depth(g)
        if d >= 3:
            findings["OPS-NESTED-GROUP"].append((g, d))

    # SEC-LARGE-PORTRANGE
    for name, fields in apps.items():
        port = fields.get("destination-port", "")
        if "-" in port:
            lo, hi = port.split("-", 1)
            try:
                if int(hi) - int(lo) + 1 >= 1024:
                    findings["SEC-LARGE-PORTRANGE"].append((name, port, int(hi) - int(lo) + 1))
            except ValueError:
                pass

    for check in sorted(findings):
        rows = findings[check]
        print(f"\n== {check} ({len(rows)}) ==")
        for r in rows[:25]:
            print("   ", r)
        if len(rows) > 25:
            print(f"    ... and {len(rows)-25} more")

    print(f"\n== OPS-UNUSED-OBJ ({len(unused)} addresses, {len(unused_groups)} groups) ==")
    print("    addresses:", unused[:30], "..." if len(unused) > 30 else "")
    print("    groups:", unused_groups)


if __name__ == "__main__":
    main(*sys.argv[1:4])
