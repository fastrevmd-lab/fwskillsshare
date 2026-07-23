#!/usr/bin/env python3
"""Validate the SRX DISA STIG skill's pinned catalog and safety contract."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "srx-disa-stig-compliance"
SKILL_PATH = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
ROW_HEADER = (
    "| V-ID | SV-ID | JUSX-ID | CAT | Summary | Applicability | Evidence | "
    "Normalized evidence | Additional evidence | Decision | Compatibility | Source |"
)
PROFILE_EXPECTED = {
    "ALG": {
        "file": "alg.md",
        "release": "V3R3",
        "rules": 24,
        "cats": {"I": 4, "II": 20, "III": 0},
        "digest": "7701a47e7baa3ad0e3649a28277ebad538bb753545902c6d8cbc1619f251cd12",
    },
    "IDPS": {
        "file": "idps.md",
        "release": "V2R1",
        "rules": 28,
        "cats": {"I": 1, "II": 27, "III": 0},
        "digest": "fdb172d016419c65854aabc646084c5fc0d4e8663e037b4e0659d9583370c6c1",
    },
    "NDM": {
        "file": "ndm.md",
        "release": "V3R3",
        "rules": 68,
        "cats": {"I": 8, "II": 43, "III": 17},
        "digest": "3d8508a6909742904cecded5fd7608ff52d942da6754168d3f200e2caaf1f7d9",
    },
    "VPN": {
        "file": "vpn.md",
        "release": "V3R2",
        "rules": 28,
        "cats": {"I": 8, "II": 20, "III": 0},
        "digest": "0c3b2f010690aeed833f80b68eeb1d40c7070267418f8f300ecebeba2679c10c",
    },
}
REQUIRED_REFERENCES = (
    "source-pin.md",
    "profile-router.md",
    "status-evidence-model.md",
    "junos-compatibility.md",
    "reporting.md",
)
KNOWN_CONFLICTS = {
    "JUSX-DM-000136",
    "JUSX-DM-000146",
    "JUSX-VN-000002",
    "JUSX-VN-000003",
    "JUSX-VN-000005",
    "JUSX-VN-000023",
    "JUSX-VN-000025",
    "JUSX-VN-000026",
    "JUSX-VN-000027",
    "JUSX-VN-000028",
}
ALLOWED_COMPATIBILITY = {"verified", "verification_required", "unsupported"}
ALLOWED_EVIDENCE = {"N", "R", "O", "M"}


def tuple_digest(rows: list[list[str]]) -> str:
    canonical = "".join(
        f"{row[0]}|{row[1]}|{row[2]}|{row[3]}\n" for row in rows
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def read_required(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def parse_profile(component: str, path: Path, errors: list[str]) -> list[list[str]]:
    text = read_required(path, errors)
    if not text:
        return []
    expected = PROFILE_EXPECTED[component]
    for marker in (
        f"Component: {component}",
        f"Release: {expected['release']}",
        f"Rule count: {expected['rules']}",
        ROW_HEADER,
    ):
        if marker not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing {marker!r}")

    lines = text.splitlines()
    try:
        header_index = lines.index(ROW_HEADER)
    except ValueError:
        return []
    if header_index + 1 >= len(lines) or not lines[header_index + 1].startswith("|---|"):
        errors.append(f"{path.relative_to(ROOT)}: missing table separator")
        return []

    rows: list[list[str]] = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 12:
            errors.append(
                f"{path.relative_to(ROOT)}: expected 12 cells, found {len(cells)} in {line[:80]!r}"
            )
            continue
        rows.append(cells)

    if len(rows) != expected["rules"]:
        errors.append(
            f"{path.relative_to(ROOT)}: expected {expected['rules']} rules, found {len(rows)}"
        )
    for index, row in enumerate(rows, start=1):
        label = f"{path.relative_to(ROOT)} row {index}"
        if any(not cell for cell in row):
            errors.append(f"{label}: every catalog field is required")
        if not re.fullmatch(r"V-\d+", row[0]):
            errors.append(f"{label}: invalid V-ID {row[0]!r}")
        if not re.fullmatch(r"SV-\d+r\d+_rule", row[1]):
            errors.append(f"{label}: invalid SV-ID {row[1]!r}")
        if not re.fullmatch(r"JUSX-[A-Z]{2}-\d{6}", row[2]):
            errors.append(f"{label}: invalid JUSX-ID {row[2]!r}")
        if row[3] not in {"I", "II", "III"}:
            errors.append(f"{label}: invalid CAT {row[3]!r}")
        evidence = {item.strip() for item in row[6].split(",") if item.strip()}
        if not evidence or not evidence <= ALLOWED_EVIDENCE:
            errors.append(f"{label}: invalid evidence codes {row[6]!r}")
        if row[10] not in ALLOWED_COMPATIBILITY:
            errors.append(f"{label}: invalid compatibility {row[10]!r}")
        if row[11] != f"{component}/{row[0]}":
            errors.append(f"{label}: invalid source pointer {row[11]!r}")

    cats = Counter(row[3] for row in rows)
    actual_cats = {cat: cats[cat] for cat in ("I", "II", "III")}
    if actual_cats != expected["cats"]:
        errors.append(
            f"{path.relative_to(ROOT)}: CAT mismatch: expected {expected['cats']}, "
            f"found {actual_cats}"
        )
    digest = tuple_digest(rows)
    if rows and digest != expected["digest"]:
        errors.append(
            f"{path.relative_to(ROOT)}: identity/order digest mismatch: "
            f"expected {expected['digest']}, found {digest}"
        )
    return rows


def require_terms(path: Path, terms: tuple[str, ...], errors: list[str]) -> str:
    text = read_required(path, errors)
    for term in terms:
        if term.casefold() not in text.casefold():
            errors.append(f"{path.relative_to(ROOT)}: missing required term {term!r}")
    return text


def validate_core(errors: list[str]) -> None:
    skill = require_terms(
        SKILL_PATH,
        (
            "references/source-pin.md",
            "references/profile-router.md",
            "references/status-evidence-model.md",
            "references/junos-compatibility.md",
            "references/reporting.md",
            "references/profiles/ndm.md",
            "references/profiles/alg.md",
            "references/profiles/idps.md",
            "references/profiles/vpn.md",
            "Pre-Return Self-Check",
            "Not Reviewed",
            "read-only",
        ),
        errors,
    )
    if skill and skill.count("\n") + 1 > 500:
        errors.append(f"{SKILL_PATH.relative_to(ROOT)}: exceeds 500 lines")
    if re.search(r"(?:device|SRX|environment) is DISA compliant", skill, re.IGNORECASE):
        errors.append(f"{SKILL_PATH.relative_to(ROOT)}: contains prohibited compliance verdict")

    source_pin = require_terms(
        REFERENCES / "source-pin.md",
        (
            "NIST NCP checklist 657",
            "Y25M01",
            "12977",
            "9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f",
            "U_Juniper_SRX_SG_Y25M01_STIG.zip",
            "NDM V3R3",
            "ALG V3R3",
            "IDPS V2R1",
            "VPN V3R2",
            "148",
            "21",
            "110",
            "17",
            "Manual_STIG",
            "no OVAL",
            "fail closed",
        ),
        errors,
    )
    if source_pin and "https://ncp.nist.gov/checklist/657" not in source_pin:
        errors.append("source-pin.md: missing official NIST checklist URL")

    require_terms(
        REFERENCES / "profile-router.md",
        (
            "| firewall only | NDM,ALG | none |",
            "| firewall + IDPS | NDM,ALG,IDPS | none |",
            "| firewall + VPN | NDM,ALG,VPN | none |",
            "| firewall + IDPS + VPN | NDM,ALG,IDPS,VPN | none |",
            "| role evidence unknown | NDM,ALG | IDPS/VPN scope unresolved |",
            "router",
            "switch",
        ),
        errors,
    )
    require_terms(
        REFERENCES / "status-evidence-model.md",
        (
            "| missing, partial, stale, ambiguous, unsupported | Not Reviewed |",
            "| complete evidence proves failure | Open |",
            "| complete evidence proves satisfaction | Not a Finding |",
            "| explicit applicability proven false and rule permits N/A | Not Applicable |",
            "_implicit: true",
            "mitigation does not change",
            "unknown applicability",
        ),
        errors,
    )
    compatibility = require_terms(
        REFERENCES / "junos-compatibility.md",
        tuple(sorted(KNOWN_CONFLICTS)) + ("formal STIG status", "verification_required"),
        errors,
    )
    require_terms(
        REFERENCES / "reporting.md",
        (
            "benchmark",
            "checksum",
            "evidence inventory",
            "CAT",
            "Not Reviewed",
            "does not by itself establish",
            "POA&M-style",
        ),
        errors,
    )
    if compatibility and re.search(
        r"(?:automatically|silently) (?:fix|remediate|modernize)",
        compatibility,
        re.IGNORECASE,
    ):
        errors.append("junos-compatibility.md: contains unsafe automatic remediation language")


def main() -> int:
    errors: list[str] = []
    if not SKILL_DIR.is_dir():
        print(
            "ERROR: missing required skill package: skills/srx-disa-stig-compliance",
            file=sys.stderr,
        )
        return 1

    validate_core(errors)
    rows_by_component: dict[str, list[list[str]]] = {}
    for component, expected in PROFILE_EXPECTED.items():
        rows_by_component[component] = parse_profile(
            component, REFERENCES / "profiles" / expected["file"], errors
        )

    catalogs_complete = all(
        len(rows_by_component[component]) == expected["rules"]
        for component, expected in PROFILE_EXPECTED.items()
    )
    if catalogs_complete:
        all_rows = [
            row
            for component in PROFILE_EXPECTED
            for row in rows_by_component[component]
        ]
        if len(all_rows) != 148:
            errors.append(f"expected 148 total catalog rows, found {len(all_rows)}")
        cats = Counter(row[3] for row in all_rows)
        if {cat: cats[cat] for cat in ("I", "II", "III")} != {
            "I": 21,
            "II": 110,
            "III": 17,
        }:
            errors.append("aggregate CAT counts do not equal I/II/III 21/110/17")
        for column, label in ((0, "V-ID"), (1, "SV-ID"), (2, "JUSX-ID")):
            values = [row[column] for row in all_rows]
            if len(values) != len(set(values)):
                errors.append(f"duplicate cross-component {label}")
        row_by_jusx = {row[2]: row for row in all_rows}
        for conflict in KNOWN_CONFLICTS:
            row = row_by_jusx.get(conflict)
            if row is not None and row[10] != "verification_required":
                errors.append(f"{conflict}: known conflict must be verification_required")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        "OK: SRX DISA STIG Y25M01 catalog has 148 source-pinned rules, "
        "conservative status routing, and compatibility guards"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
