#!/usr/bin/env python3
"""Verify the pinned SRX STIG ZIP and emit rule identity metadata only."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


PINNED_SHA256 = "9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f"
XCCDF_NAMESPACE = {"xccdf": "http://checklists.nist.gov/xccdf/1.1"}
SEVERITY_TO_CAT = {"high": "I", "medium": "II", "low": "III"}
COMPONENT_PATTERN = re.compile(r"_SG_(ALG|IDPS|NDM|VPN)_")
EXPECTED = {
    "ALG": {
        "release": "V3R3",
        "rules": 24,
        "cat_counts": {"I": 4, "II": 20, "III": 0},
        "accepted": "2024-12-19",
        "benchmark_date": "30 Jan 2025",
        "tuple_sha256": "7701a47e7baa3ad0e3649a28277ebad538bb753545902c6d8cbc1619f251cd12",
    },
    "IDPS": {
        "release": "V2R1",
        "rules": 28,
        "cat_counts": {"I": 1, "II": 27, "III": 0},
        "accepted": "2024-06-10",
        "benchmark_date": "24 Jul 2024",
        "tuple_sha256": "fdb172d016419c65854aabc646084c5fc0d4e8663e037b4e0659d9583370c6c1",
    },
    "NDM": {
        "release": "V3R3",
        "rules": 68,
        "cat_counts": {"I": 8, "II": 43, "III": 17},
        "accepted": "2024-12-20",
        "benchmark_date": "30 Jan 2025",
        "tuple_sha256": "3d8508a6909742904cecded5fd7608ff52d942da6754168d3f200e2caaf1f7d9",
    },
    "VPN": {
        "release": "V3R2",
        "rules": 28,
        "cat_counts": {"I": 8, "II": 20, "III": 0},
        "accepted": "2024-12-20",
        "benchmark_date": "30 Jan 2025",
        "tuple_sha256": "0c3b2f010690aeed833f80b68eeb1d40c7070267418f8f300ecebeba2679c10c",
    },
}


class SourceError(RuntimeError):
    """The supplied artifact does not match the pinned source contract."""


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tuple_digest(rows: list[dict[str, str]]) -> str:
    canonical = "".join(
        f"{row['v_id']}|{row['sv_id']}|{row['jusx_id']}|{row['cat']}\n"
        for row in rows
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def required_text(parent: ElementTree.Element, path: str, label: str) -> str:
    value = parent.findtext(path, namespaces=XCCDF_NAMESPACE)
    if not value or not value.strip():
        raise SourceError(f"missing {label}")
    return value.strip()


def parse_component(member: str, data: bytes) -> tuple[str, dict[str, object]]:
    component_match = COMPONENT_PATTERN.search(member)
    if component_match is None:
        raise SourceError(f"cannot identify component from {member}")
    component = component_match.group(1)
    expected = EXPECTED[component]

    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        raise SourceError(f"invalid XCCDF XML in {member}: {exc}") from exc

    status = root.find("xccdf:status", XCCDF_NAMESPACE)
    accepted = status.attrib.get("date", "") if status is not None else ""
    release_info = ""
    for text_node in root.findall("xccdf:plain-text", XCCDF_NAMESPACE):
        if text_node.attrib.get("id") == "release-info":
            release_info = (text_node.text or "").strip()
            break
    benchmark_match = re.search(r"Benchmark Date:\s*(.+)$", release_info)
    benchmark_date = benchmark_match.group(1).strip() if benchmark_match else ""
    release_match = re.search(rf"_{component}_(V\d+R\d+)_Manual", member)
    release = release_match.group(1) if release_match else ""

    rows: list[dict[str, str]] = []
    for group in root.findall("xccdf:Group", XCCDF_NAMESPACE):
        rule = group.find("xccdf:Rule", XCCDF_NAMESPACE)
        if rule is None:
            raise SourceError(f"{member}: group {group.attrib.get('id')} has no Rule")
        severity = rule.attrib.get("severity", "")
        if severity not in SEVERITY_TO_CAT:
            raise SourceError(f"{member}: unsupported severity {severity!r}")
        rows.append(
            {
                "v_id": group.attrib.get("id", ""),
                "sv_id": rule.attrib.get("id", ""),
                "jusx_id": required_text(rule, "xccdf:version", "JUSX identifier"),
                "cat": SEVERITY_TO_CAT[severity],
            }
        )

    for field in ("v_id", "sv_id", "jusx_id"):
        values = [row[field] for row in rows]
        if any(not value for value in values):
            raise SourceError(f"{member}: empty {field}")
        if len(values) != len(set(values)):
            raise SourceError(f"{member}: duplicate {field}")

    actual = {
        "release": release,
        "rules": len(rows),
        "cat_counts": {
            cat: Counter(row["cat"] for row in rows)[cat]
            for cat in ("I", "II", "III")
        },
        "accepted": accepted,
        "benchmark_date": benchmark_date,
        "tuple_sha256": tuple_digest(rows),
    }
    for field, expected_value in expected.items():
        if actual[field] != expected_value:
            raise SourceError(
                f"{component}: {field} mismatch: expected {expected_value!r}, "
                f"found {actual[field]!r}"
            )
    actual["tuples"] = rows
    return component, actual


def extract(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise SourceError(f"artifact does not exist: {path}")
    artifact_sha256 = file_sha256(path)
    if artifact_sha256 != PINNED_SHA256:
        raise SourceError(
            f"artifact SHA-256 mismatch: expected {PINNED_SHA256}, found {artifact_sha256}"
        )

    try:
        with ZipFile(path) as archive:
            members = sorted(
                name for name in archive.namelist() if name.endswith("Manual-xccdf.xml")
            )
            if len(members) != len(EXPECTED):
                raise SourceError(
                    f"expected {len(EXPECTED)} Manual XCCDF members, found {len(members)}"
                )
            components = dict(parse_component(name, archive.read(name)) for name in members)
    except BadZipFile as exc:
        raise SourceError(f"invalid ZIP artifact: {exc}") from exc

    if set(components) != set(EXPECTED):
        raise SourceError(
            f"component mismatch: expected {sorted(EXPECTED)}, found {sorted(components)}"
        )

    all_rows = [
        row
        for component in EXPECTED
        for row in components[component]["tuples"]  # type: ignore[index]
    ]
    for field in ("v_id", "sv_id", "jusx_id"):
        values = [row[field] for row in all_rows]
        if len(values) != len(set(values)):
            raise SourceError(f"duplicate cross-component {field}")
    totals = {
        "rules": len(all_rows),
        "cat_counts": {
            cat: Counter(row["cat"] for row in all_rows)[cat]
            for cat in ("I", "II", "III")
        },
    }
    if totals != {"rules": 148, "cat_counts": {"I": 21, "II": 110, "III": 17}}:
        raise SourceError(f"unexpected aggregate totals: {totals}")

    return {
        "artifact": path.name,
        "sha256": artifact_sha256,
        "checklist": "NIST NCP 657",
        "release": "Y25M01",
        "components": components,
        "totals": totals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the pinned Juniper SRX Y25M01 STIG ZIP and emit identity metadata."
    )
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    try:
        result = extract(args.zip_path)
    except (OSError, SourceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
