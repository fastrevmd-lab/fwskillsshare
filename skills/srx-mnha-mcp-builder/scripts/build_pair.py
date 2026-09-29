#!/usr/bin/env python3
"""Render, lint and compute undo for a two-node MNHA pair from one pair sheet.

Usage:
  python build_pair.py pair.yaml --out build [--baseline NODE0=node0.set --baseline NODE1=node1.set]

Per node writes build/<router>/stageN.set, undo-stageN.set and vars.yaml, then prints the
lint report. Exit 1 on any ERROR - do not push. Baselines are get_junos_config output.
Undo files delete only what the stage ADDS relative to the baseline, so pre-existing
config that a stage merely re-states is never removed by an undo.
"""
import argparse, ipaddress, re, sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

TPL = Path(__file__).resolve().parent.parent / "templates"
MODES = {"routing", "switching", "hybrid"}
findings = []
def err(m): findings.append(("ERROR", m))
def warn(m): findings.append(("WARN", m))
def info(m): findings.append(("INFO", m))

def fills(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items(): yield from fills(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from fills(v, f"{path}[{i}]")
    elif isinstance(obj, str) and "<FILL>" in obj:
        yield path

def check_fills(sheet, mode):
    skip = []
    if mode == "switching":
        skip = [r"^pair\.bgp", r"^nodes\.node\d\.bgp_neighbors", r"^pair\.srg1\.(active|backup)_signal_route"]
    if sheet["pair"]["icl"].get("transport") == "shared": skip += [r"^pair\.icl\.(ifd|unit|prefix_len)"]
    else: skip += [r"^pair\.icl\.(segment|loopback_unit)"]
    missing = [p for p in fills(sheet) if not any(re.search(s, p) for s in skip)]
    if missing:
        print("ERROR: unfilled fields:\n  " + "\n  ".join(missing)); sys.exit(1)

def resolve_model(pair):
    m = re.match(r"(\d+)\.(\d+)", str(pair["junos_release"]))
    if not m: err(f"cannot parse junos_release {pair['junos_release']}"); return "grid"
    major = int(m.group(1)); model = pair.get("config_model", "auto")
    if model == "auto":
        if major >= 26: return "grid"
        if major <= 24: return "flat"
        err("25.x is ambiguous - set config_model explicitly"); return "grid"
    if model == "flat" and major >= 26: err("flat model on 26.x never activates - use grid")
    if model == "grid" and major <= 24: warn("grid model on <=24.x - verify release support")
    return model

def seg_objs(pair, node):
    out = []
    for s in pair.get("segments") or []:
        ifd, unit = s["ifl"].split(".")
        addr = (node.get("addresses") or {}).get(s["name"])
        if not addr: err(f"{node['router_name']}: no address for segment '{s['name']}'"); continue
        out.append({**s, "ifd": ifd, "unit": unit, "cidr": str(ipaddress.ip_interface(addr))})
    return out

def node_vars(pair, me, peer, lid, pid, model, mode):
    icl, srg = pair["icl"], pair["srg1"]; bgp = pair.get("bgp") if mode != "switching" else None
    segs = seg_objs(pair, me); peer_segs = seg_objs(pair, peer)
    transport = icl.get("transport", "dedicated"); enc = icl.get("encryption") or {}
    iv = {"icl_transport": transport, "icl_zone": icl["zone"], "icl_encrypted": bool(enc.get("enabled")),
          "icl_ike_policy": enc.get("ike_policy", "MNHA-ICL-IKE-POL")}
    if transport == "dedicated":
        iv.update({"icl_ifd": icl["ifd"], "icl_unit": icl["unit"], "icl_ifl": f"{icl['ifd']}.{icl['unit']}",
                   "icl_cidr": str(ipaddress.ip_interface(f"{me['icl_ip']}/{icl['prefix_len']}"))})
        iv["icl_ha_ifl"] = iv["icl_ifl"]
    else:
        t = next((x for x in segs if x["name"] == icl.get("segment")), None)
        pt = next((x for x in peer_segs if x["name"] == icl.get("segment")), None)
        if not t or not pt: err(f"icl.segment '{icl.get('segment')}' is not a declared segment"); t = pt = {"ifl": "?", "zone": "?", "cidr": "0.0.0.0/32"}
        iv.update({"icl_lo_unit": icl.get("loopback_unit", 1), "icl_ha_ifl": t["ifl"], "icl_transport_zone": t["zone"],
                   "icl_peer_nexthop": str(ipaddress.ip_interface(pt["cidr"]).ip), "icl_transport_net": t["cidr"],
                   "icl_ifd": "lo0", "icl_unit": icl.get("loopback_unit", 1), "icl_ifl": f"lo0.{icl.get('loopback_unit', 1)}",
                   "icl_cidr": f"{me['icl_ip']}/32"})
    up = next((s for s in segs if s.get("role") == "upstream"), None)
    probe = me.get("probe") or {}
    v = {
        "router_name": me["router_name"], "config_model": model, "grid_id": pair.get("grid_id", 1),
        "deployment_type": mode, "local_id": lid, "peer_id": pid,
        "local_icl_ip": me["icl_ip"], "peer_icl_ip": peer["icl_ip"],
        "liveness_min": pair["liveness"]["min_interval"], "liveness_mult": pair["liveness"]["multiplier"],
        "probe_dst": probe.get("dest_ip"), "probe_src": probe.get("src_ip"),
        "activeness_priority": me["activeness_priority"], "preemption": bool(srg.get("preemption")),
        "active_signal_route": srg.get("active_signal_route"), "backup_signal_route": srg.get("backup_signal_route"),
        "vips": srg.get("vips") or [], "monitor_interfaces": srg.get("monitor_interfaces") or [],
        "segments": segs, "bgp_enabled": bool(bgp),
        "bgp_bfd": (bgp or {}).get("bfd"), "cond_active": "MNHA-SRG1-ACTIVE", "cond_backup": "MNHA-SRG1-BACKUP",
    }
    v.update(iv)
    if bgp:
        v.update({"local_as": bgp["local_as"], "peer_as": bgp["peer_as"], "bgp_group": bgp["group"],
                  "export_policy": bgp["export_policy"], "protected_prefixes": bgp.get("protected_prefixes") or [],
                  "transit_subnets": bgp.get("transit_subnets") or [], "active_metric": bgp["active_metric"],
                  "backup_metric": bgp["backup_metric"], "bgp_neighbors": me.get("bgp_neighbors") or [],
                  "upstream_ip": str(ipaddress.ip_interface(up["cidr"]).ip) if up else None})
    return v

def lint_pair(pair, mode, v0, v1):
    a, b = ipaddress.ip_interface(v0["icl_cidr"]), ipaddress.ip_interface(v1["icl_cidr"])
    if a.ip == b.ip: err("ICL IPs identical")
    if v0["icl_transport"] == "dedicated":
        if a.network != b.network: err(f"ICL IPs not in one subnet: {a} vs {b}")
    else:
        tn = ipaddress.ip_interface(v0["icl_transport_net"]).network
        for v in (v0, v1):
            if ipaddress.ip_address(v["local_icl_ip"]) in tn: err(f"{v['router_name']}: shared-ICL loopback {v['local_icl_ip']} sits inside the transport subnet")
        info(f"shared ICL over {v0['icl_ha_ifl']} (zone {v0['icl_transport_zone']}): HA/BFD{'/IKE' if v0['icl_encrypted'] else ''} host-inbound opened on that zone")
        if not v0["icl_encrypted"]: warn("shared (non-dedicated) ICL without encryption - session state crosses a shared segment in clear text")
    if v0["icl_encrypted"]:
        info("encrypted ICL: both nodes need the junos-ike package (check 'show version') and the same PSK set by the user on "
             f"'security ike policy {v0['icl_ike_policy']}' before the baseline is taken")
    if v0["activeness_priority"] == v1["activeness_priority"]: err("activeness_priority equal on both nodes")
    ups = [s for s in pair.get("segments") or [] if s.get("role") == "upstream"]
    for v in (v0, v1):
        r = v["router_name"]
        if bool(v["probe_dst"]) != bool(v["probe_src"]): err(f"{r}: probe needs both dest_ip and src_ip")
        for ip in filter(None, (v["probe_dst"], v["probe_src"])):
            if ipaddress.ip_address(ip) in a.network: err(f"{r}: probe address {ip} is on the ICL - use a data segment")
    # mode rules
    if mode == "routing":
        if not v0["probe_dst"] or not v1["probe_dst"]: err("routing mode requires activeness-probe dest-ip/src-ip on both nodes (pitfall 20)")
        if v0["vips"]: err("routing mode has no VIPs - use hybrid or switching for a shared gateway")
    if mode in ("switching", "hybrid"):
        if not v0["vips"]: err(f"{mode} mode needs at least one VIP")
        if not v0["monitor_interfaces"]: warn(f"{mode}: no monitor_interfaces - VIP will not move on uplink loss")
        if not v0["probe_dst"]: warn(f"{mode}: no activeness-probe - consider one to avoid dual-active on ICL loss")
        segs = {s["ifl"]: s for s in pair.get("segments") or []}
        for vip in v0["vips"]:
            vi = ipaddress.ip_interface(vip["ip"])
            if vip["ifl"] not in segs: err(f"VIP {vip['ip']} on {vip['ifl']}, which is not a declared segment"); continue
            for v in (v0, v1):
                sc = next(ipaddress.ip_interface(s["cidr"]) for s in v["segments"] if s["ifl"] == vip["ifl"])
                if vi.network != sc.network: err(f"{v['router_name']}: VIP {vi} not in segment subnet {sc.network}")
                if vi.ip == sc.ip: err(f"{v['router_name']}: VIP equals the node's own address")
        print_l2 = "switching/hybrid: adjacent switches must accept the vMAC move (MAC-move limits, DAI, storm-control)"
        info(print_l2)
    if mode in ("routing", "hybrid"):
        if len(ups) != 1: err(f"{mode} mode needs exactly one segment with role: upstream")
        bgp = pair.get("bgp") or {}
        if not bgp.get("protected_prefixes"): err("bgp.protected_prefixes empty - export would advertise nothing")
        for p in bgp.get("protected_prefixes") or []:
            if len(p.split()) < 2: err(f"protected prefix '{p}' lacks a route-filter match type")
        if not bgp.get("transit_subnets"): warn("bgp.transit_subnets empty - return traffic to on-transit sources may black-hole (pitfall 21)")
        prot = {x.split()[0] for x in bgp.get("protected_prefixes") or []}
        for t in bgp.get("transit_subnets") or []:
            if t in prot: warn(f"{t} is in both protected_prefixes and transit_subnets - the transit term is redundant")
        if bgp.get("local_as") == bgp.get("peer_as"): err("local_as == peer_as - this builder does eBGP only")
        for v in (v0, v1):
            if not v["bgp_neighbors"]: err(f"{v['router_name']}: no bgp_neighbors")
            up = next(ipaddress.ip_interface(s["cidr"]) for s in v["segments"] if s.get("role") == "upstream")
            for n in v["bgp_neighbors"]:
                if ipaddress.ip_address(n) not in up.network: warn(f"{v['router_name']}: neighbor {n} not on upstream subnet {up.network} (multihop not built)")
        for s in (v0["active_signal_route"], v0["backup_signal_route"]):
            if ipaddress.ip_address(s) not in ipaddress.ip_network("169.254.0.0/16"): warn(f"signal route {s} outside 169.254/16")
        if v0["active_signal_route"] == v0["backup_signal_route"]: err("active and backup signal routes identical")
    if v0["preemption"]: warn("preemption on - test failback convergence (pitfall 8)")

MGMT = re.compile(r"^(set|delete) (interfaces fxp0|system (services|login|root-authentication)|routing-instances mgmt_junos)")
BROAD = re.compile(r"(host-inbound-traffic (system-services|protocols) all|default-policy permit-all)")

def lint_rendered(r, st):
    txt = "\n".join(st.values())
    for line in txt.splitlines():
        if MGMT.match(line): err(f"{r}: stage touches the management plane: '{line}'")
        if BROAD.search(line): err(f"{r}: broad permission: '{line}'")
    if "host-inbound-traffic protocols bfd" not in st["stage1"]: err(f"{r}: ICL zone lacks protocols bfd (pitfall 22)")
    if "vpn-profile" in st["stage2"] and "host-inbound-traffic system-services ike" not in st["stage1"]:
        err(f"{r}: encrypted ICL but no 'system-services ike' on the ICL zone")
    if "deployment-type routing" in st["stage2"] and "activeness-probe dest-ip" not in st["stage2"]:
        err(f"{r}: routing SRG without activeness-probe (pitfall 20)")
    s3 = st.get("stage3", "")
    for t in set(re.findall(r"term (\S+) then accept", s3)):
        if not re.search(rf"term {re.escape(t)} from route-filter", s3): err(f"{r}: export term '{t}' accepts without route-filter (pitfall 5)")

def lint_baseline(r, base, v):
    B = lambda pat: re.search(pat, base, re.M)
    if B(r"^set chassis cluster"): err(f"{r}: chassis cluster config present")
    if B(r"^set chassis high-availability"): err(f"{r}: existing chassis high-availability - remove it and reboot first")
    if B(r"^set interfaces fxp0 unit 0 family inet dhcp"): err(f"{r}: fxp0 on DHCP (pitfall 23)")
    if B(r"^set routing-options static route 0\.0\.0\.0/0"): warn(f"{r}: static default route present - check next hop is on a zoned interface (pitfall 18) and that it should win over BGP")
    if v["icl_transport"] == "dedicated":
        units = re.findall(rf"^set interfaces {re.escape(v['icl_ifd'])} unit (\S+) (.*)$", base, re.M)
        other = [u for u in units if not (u[0] == str(v["icl_unit"]) and u[1] == f"family inet address {v['icl_cidr']}")]
        if other: err(f"{r}: ICL interface {v['icl_ifd']} has other config: {[' '.join(o) for o in other]}")
        elif units: info(f"{r}: ICL {v['icl_ifl']} {v['icl_cidr']} already present - reused")
        zin = re.findall(rf"^set security zones security-zone (\S+) interfaces {re.escape(v['icl_ifl'])}$", base, re.M)
        if zin and v["icl_zone"] not in zin: err(f"{r}: ICL {v['icl_ifl']} is in zone {zin} - move it or reuse that zone name")
    else:
        lo = re.findall(rf"^set interfaces lo0 unit {v['icl_lo_unit']} family inet address (\S+)", base, re.M)
        if lo and f"{v['local_icl_ip']}/32" not in lo: err(f"{r}: lo0.{v['icl_lo_unit']} already has {lo} - pick another loopback_unit")
        zin = re.findall(rf"^set security zones security-zone (\S+) interfaces lo0\.{v['icl_lo_unit']}$", base, re.M)
        if zin and v["icl_zone"] not in zin: err(f"{r}: lo0.{v['icl_lo_unit']} is in zone {zin}")
    if B(rf"^set security zones security-zone {re.escape(v['icl_zone'])} "): err(f"{r}: zone {v['icl_zone']} already exists")
    if v["icl_encrypted"]:
        if not B(rf"^set security ike policy {re.escape(v['icl_ike_policy'])} pre-shared-key "):
            err(f"{r}: encrypted ICL needs the PSK on 'security ike policy {v['icl_ike_policy']}' - user sets it on the node via CLI, then re-take the baseline")
        rendered = set(v.get("_stage2_lines", []))
        for obj in ("ike proposal MNHA-ICL-IKE-PROP", "ike policy MNHA-ICL-IKE-POL", "ike gateway MNHA-ICL-IKE-GW",
                    "ipsec proposal MNHA-ICL-IPSEC-PROP", "ipsec policy MNHA-ICL-IPSEC-POL", "ipsec vpn MNHA-ICL-VPN"):
            clash = [l for l in re.findall(rf"^set security {obj} .*$", base, re.M)
                     if l not in rendered and " pre-shared-key " not in l]
            if clash: err(f"{r}: existing 'security {obj}' differs from the rendered one: {clash}")
    for s in v["segments"]:
        have = re.findall(rf"^set interfaces {re.escape(s['ifd'])} unit {s['unit']} family inet address (\S+)", base, re.M)
        if have and s["cidr"] not in have: err(f"{r}: {s['ifl']} has {have}, sheet says {s['cidr']}")
        elif have: info(f"{r}: {s['ifl']} {s['cidr']} already present - reused")
        z = re.findall(rf"^set security zones security-zone (\S+) interfaces {re.escape(s['ifl'])}$", base, re.M)
        if z and s["zone"] not in z: err(f"{r}: {s['ifl']} is in zone {z}, sheet says {s['zone']}")
    if v["bgp_enabled"]:
        asn = re.findall(r"^set routing-options autonomous-system (\S+)", base, re.M)
        if asn and str(v["local_as"]) not in asn: err(f"{r}: autonomous-system {asn} != sheet {v['local_as']}")
        g = re.escape(v["bgp_group"])
        pas = re.findall(rf"^set protocols bgp group {g} peer-as (\S+)", base, re.M)
        if pas and str(v["peer_as"]) not in pas: err(f"{r}: group {v['bgp_group']} peer-as {pas} != sheet {v['peer_as']}")
        exps = [e for e in re.findall(rf"^set protocols bgp group {g} export (\S+)", base, re.M) if e != v["export_policy"]]
        if exps: err(f"{r}: group {v['bgp_group']} already exports {exps} - remove or pick another group name")
        if B(rf"^set policy-options policy-statement {re.escape(v['export_policy'])} "): err(f"{r}: policy {v['export_policy']} already exists")
    if B(r"^set security (ike|ipsec) (?!\S+ MNHA-ICL-)"): warn(f"{r}: node-local IPsec present - untouched, will NOT fail over (out of scope)")
    if B(r"managed-services ipsec"): err(f"{r}: managed-services ipsec present - out of scope")
    if B(r"default-policy permit-all"): warn(f"{r}: baseline has default-policy permit-all")
    if B(r"host-inbound-traffic (system-services|protocols) all"): warn(f"{r}: baseline zone allows host-inbound 'all'")

def undo_for(stage_txt, base_lines):
    prefixes = set()
    for l in base_lines:
        w = l.split()[1:]
        for i in range(1, len(w) + 1): prefixes.add(" ".join(w[:i]))
    out, seen = [], set()
    for line in reversed(stage_txt.splitlines()):
        w = line.split()[1:]
        cut = next((i for i in range(1, len(w) + 1) if " ".join(w[:i]) not in prefixes), None)
        if cut is None: continue          # line already in baseline: never undo it
        d = "delete " + " ".join(w[:cut])
        if d not in seen and not any(d.startswith(s + " ") for s in seen): seen.add(d); out.append(d)
    return "\n".join(out) + ("\n" if out else "")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("sheet"); ap.add_argument("--out", default="build")
    ap.add_argument("--baseline", action="append", default=[])
    a = ap.parse_args()
    sheet = yaml.safe_load(Path(a.sheet).read_text()); pair = sheet["pair"]
    mode = pair.get("deployment_mode")
    if mode not in MODES: print(f"ERROR: deployment_mode must be one of {sorted(MODES)}"); sys.exit(1)
    check_fills(sheet, mode)
    model = resolve_model(pair); n0, n1 = sheet["nodes"]["node0"], sheet["nodes"]["node1"]
    v0 = node_vars(pair, n0, n1, 1, 2, model, mode); v1 = node_vars(pair, n1, n0, 2, 1, model, mode)
    lint_pair(pair, mode, v0, v1)
    env = Environment(loader=FileSystemLoader(str(TPL)), undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    stages = {"stage1": "stage1-underlay", "stage2": f"stage2-ha-{model}"}
    if mode != "switching": stages["stage3"] = "stage3-bgp"
    bases = dict(b.split("=", 1) for b in a.baseline); summary = []
    for v in (v0, v1):
        r = v["router_name"]; d = Path(a.out) / r; d.mkdir(parents=True, exist_ok=True)
        base = Path(bases[r]).read_text() if r in bases else ""
        base_lines = [l.strip() for l in base.splitlines() if l.startswith("set ")]
        bset = set(base_lines); st = {}
        for k, t in stages.items():
            txt = "\n".join(l for l in env.get_template(f"{t}.set.j2").render(**v).splitlines() if l.strip()) + "\n"
            st[k] = txt; (d / f"{k}.set").write_text(txt)
            (d / f"undo-{k}.set").write_text(undo_for(txt, base_lines))
            new = sum(1 for l in txt.splitlines() if l not in bset)
            summary.append(f"  {r} {k}: {len(txt.splitlines())} lines, {new} new")
        (d / "vars.yaml").write_text(yaml.safe_dump({k: x for k, x in v.items() if not k.startswith("_")}, sort_keys=False))
        lint_rendered(r, st)
        v["_stage2_lines"] = st["stage2"].splitlines()
        if base: lint_baseline(r, base, v)
        else: warn(f"{r}: no baseline - baseline checks skipped, undo deletes every staged line")
    print(f"Mode: {mode} | Model: {model} | Node0={v0['router_name']} (local-id 1, prio {v0['activeness_priority']}) "
          f"Node1={v1['router_name']} (local-id 2, prio {v1['activeness_priority']})")
    print("\n".join(summary)); print(f"Rendered to: {Path(a.out).resolve()}")
    for lvl in ("ERROR", "WARN", "INFO"):
        for l, m in findings:
            if l == lvl: print(f"{l}: {m}")
    if not any(l in ("ERROR", "WARN") for l, _ in findings): print("LINT: clean")
    sys.exit(1 if any(l == "ERROR" for l, _ in findings) else 0)

if __name__ == "__main__":
    main()
