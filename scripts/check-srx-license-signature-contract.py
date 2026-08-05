#!/usr/bin/env python3
"""Verify the srx-license-signature-maintenance behavioral contract.

Offline only. This encodes the decisions the skill mandates — two independent
approval gates, secret-safe license sourcing, condition-based terminal-state
polling, per-node cluster evidence, version-qualifier handling, and the
no-active-policy warning — as executable checks, then guards the wording that
documents them.

No device is contacted and no fixture contains license material.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "srx-license-signature-maintenance"
SKILL_PATH = SKILL_DIR / "SKILL.md"
LICENSING_PATH = SKILL_DIR / "references" / "licensing.md"
SIGNATURES_PATH = SKILL_DIR / "references" / "offline-signatures.md"
VERIFY_PATH = SKILL_DIR / "references" / "verification-troubleshooting.md"

GATE_LICENSE = "license"
GATE_SIGNATURE = "signature"

# Terminal states. Anything not listed is non-terminal and must keep polling.
TERMINAL_SUCCESS = frozenset({"success", "done"})
TERMINAL_FAILURE = frozenset({"failed", "error"})


def gate_satisfied(gate: str, approvals: frozenset[str]) -> bool:
    """Return whether `gate` is authorized.

    Each gate needs its own explicit approval. Neither implies the other, and
    read-only work (an empty approval set) authorizes neither.
    """
    return gate in approvals


def is_terminal(status: str) -> bool:
    """Return whether a polled status may end the wait."""
    normalized = status.strip().lower()
    return normalized in TERMINAL_SUCCESS or normalized in TERMINAL_FAILURE


def is_terminal_success(status: str) -> bool:
    return status.strip().lower() in TERMINAL_SUCCESS


def license_source_safe(*, exists: bool, regular_file: bool, symlink: bool,
                        empty: bool, inside_repository: bool) -> bool:
    """Return whether a supplied license file may be staged."""
    return exists and regular_file and not symlink and not empty and not inside_repository


def cluster_evidence_complete(node_reports: dict[str, bool], expected_nodes: tuple[str, ...],
                              aggregate_ok: bool) -> bool:
    """Return whether cluster state is proven.

    An aggregate/cluster-level response can reflect the primary alone, so it is
    never sufficient: every expected node must have answered for itself.
    """
    del aggregate_ok  # deliberately unused: an aggregate proves nothing per node
    return all(node_reports.get(node) is True for node in expected_nodes)


def normalize_version(token: str) -> tuple[str, str]:
    """Split a version token into (comparable, qualifier).

    Real device output is `3929(Minor, Thu Jul 23 13:53:38 2026 UTC)` — no
    space before the paren, and the qualifier carries a timestamp. It compares
    as `3929` but must still report the whole qualifier.

    The numeric pattern is strict on purpose: a malformed token such as `3929.`
    or `1..2` must not silently compare unequal to a well-formed one.
    """
    match = re.fullmatch(
        r"\s*([0-9]+(?:\.[0-9]+)*)\s*(?:\(([^)]*)\))?\s*", token or ""
    )
    if not match:
        return ("", "")
    return (match.group(1), match.group(2) or "")


def install_outcome(*, install_terminal_success: bool, active_idp_policy: bool) -> tuple[str, bool]:
    """Return (classification, claims_enforcement_active).

    A package install that lands with no active IDP policy is a success with an
    operational warning; it must never be reported as active enforcement.
    """
    if not install_terminal_success:
        return ("failed", False)
    if not active_idp_policy:
        return ("success-with-warning", False)
    return ("success", True)


# Built rather than written literally so this file does not trip its own
# key-block scan below.
KEY_BLOCK_MARKER = "-" * 5 + "BEGIN"
SECRET_MARKERS = ("JUNOS", KEY_BLOCK_MARKER)
# Substring matching on "license key" misses the forms secrets actually appear
# in — "license-key", "licensekey", "License_Key". Match the separator instead.
SECRET_PATTERNS = (
    re.compile(r"licen[cs]e[\s_\-]*key", re.I),
    re.compile(r"auth(?:orization)?[\s_\-]*code", re.I),
    re.compile(r"license[\s_\-]*identifier", re.I),
    re.compile(r"software[\s_\-]*serial[\s_\-]*number", re.I),
)


def report_is_sanitized(report: str) -> bool:
    """Return whether a report is free of license material markers."""
    lowered = report.lower()
    if any(marker.lower() in lowered for marker in SECRET_MARKERS):
        return False
    return not any(pattern.search(report) for pattern in SECRET_PATTERNS)


def behavior_errors() -> list[str]:
    errors: list[str] = []

    # --- Two independent approval gates -------------------------------------
    readonly = frozenset()
    license_only = frozenset({GATE_LICENSE})
    signature_only = frozenset({GATE_SIGNATURE})
    both = frozenset({GATE_LICENSE, GATE_SIGNATURE})

    if gate_satisfied(GATE_LICENSE, readonly) or gate_satisfied(GATE_SIGNATURE, readonly):
        errors.append("read-only baseline authorized a mutation gate")
    if gate_satisfied(GATE_SIGNATURE, license_only):
        errors.append("licensing approval leaked into the signature gate")
    if gate_satisfied(GATE_LICENSE, signature_only):
        errors.append("signature approval leaked into the licensing gate")
    if not gate_satisfied(GATE_LICENSE, license_only):
        errors.append("explicit licensing approval was not honored")
    if not (gate_satisfied(GATE_LICENSE, both) and gate_satisfied(GATE_SIGNATURE, both)):
        errors.append("both-gate approval did not authorize both phases")

    # --- License source safety ----------------------------------------------
    safe = dict(exists=True, regular_file=True, symlink=False, empty=False,
                inside_repository=False)
    if not license_source_safe(**safe):
        errors.append("a safe license source was rejected")
    for field in ("exists", "regular_file"):
        if license_source_safe(**{**safe, field: False}):
            errors.append(f"unsafe license source accepted with {field}=False")
    for field in ("symlink", "empty", "inside_repository"):
        if license_source_safe(**{**safe, field: True}):
            errors.append(f"unsafe license source accepted with {field}=True")

    # --- Condition-based polling --------------------------------------------
    for non_terminal in ("In progress", "in progress", "", "   ", "pending", "timeout"):
        if is_terminal(non_terminal):
            errors.append(f"non-terminal status {non_terminal!r} ended the poll")
        if is_terminal_success(non_terminal):
            errors.append(f"non-terminal status {non_terminal!r} was read as success")
    if not is_terminal_success("success"):
        errors.append("terminal success was not recognized")
    if not is_terminal("failed"):
        errors.append("terminal failure was not recognized")
    if is_terminal_success("failed"):
        errors.append("terminal failure was read as success")

    # --- Cluster evidence ----------------------------------------------------
    nodes = ("node0", "node1")
    if cluster_evidence_complete({"node0": True}, nodes, aggregate_ok=True):
        errors.append("cluster aggregate substituted for missing secondary evidence")
    if cluster_evidence_complete({"node0": True, "node1": False}, nodes, aggregate_ok=True):
        errors.append("failed secondary was treated as verified")
    if not cluster_evidence_complete({"node0": True, "node1": True}, nodes, aggregate_ok=False):
        errors.append("per-node evidence was not accepted without an aggregate")

    # --- Version qualifiers --------------------------------------------------
    if normalize_version("3929(Minor)") != ("3929", "Minor"):
        errors.append("version qualifier was not split from the comparable token")
    if normalize_version("3929") != ("3929", ""):
        errors.append("plain version token was not parsed")
    if normalize_version("3929(Minor)")[0] != normalize_version("3929")[0]:
        errors.append("qualifier changed the comparable version token")
    if normalize_version("3929(Minor)")[1] == "":
        errors.append("qualifier was discarded instead of retained for the report")
    # Real device output: no space before the paren, timestamp inside it.
    live = normalize_version("3929(Minor, Thu Jul 23 13:53:38 2026 UTC)")
    if live[0] != "3929":
        errors.append("live-format version token did not compare as 3929")
    if "Thu Jul 23" not in live[1]:
        errors.append("live-format qualifier lost its timestamp")
    if normalize_version("12.6.180260106") != ("12.6.180260106", ""):
        errors.append("dotted detector version was not parsed")
    # Malformed tokens must not masquerade as well-formed ones.
    for malformed in ("3929.", "1..2", ".3929", "39a29"):
        if normalize_version(malformed)[0] == malformed:
            errors.append(f"malformed version {malformed!r} was accepted verbatim")

    # --- No active IDP policy ------------------------------------------------
    classification, claims = install_outcome(install_terminal_success=True,
                                             active_idp_policy=False)
    if classification != "success-with-warning":
        errors.append("install without an active IDP policy was misclassified")
    if claims:
        errors.append("enforcement was claimed active with no active IDP policy")
    if install_outcome(install_terminal_success=False, active_idp_policy=True)[0] != "failed":
        errors.append("failed install was not classified as failed")
    if install_outcome(install_terminal_success=True, active_idp_policy=True) != ("success", True):
        errors.append("fully successful install was misclassified")

    # --- Output sanitization --------------------------------------------------
    if report_is_sanitized("Router A | AppID active | key JUNOS123ABC"):
        errors.append("a report carrying license material passed sanitization")
    if not report_is_sanitized("Router A | AppID active | expiry 2027-01-01 | updated"):
        errors.append("a clean sanitized report was rejected")
    # Separator variants must not slip past — plain substring matching missed these.
    for leaky in (
        "Router A | License-key: ABC123",
        "Router A | licensekey ABC123",
        "notes: License_Key rotated",
        "Router A | authorization-code XYZ",
        "License identifier: DemolabJUNOS338042937",
        "Software Serial Number: 44400201-CcRw7",
    ):
        if report_is_sanitized(leaky):
            errors.append(f"secret-bearing report passed sanitization: {leaky!r}")

    return errors


def documentation_errors() -> list[str]:
    errors: list[str] = []
    for path in (SKILL_PATH, LICENSING_PATH, SIGNATURES_PATH, VERIFY_PATH):
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing required file")
    if errors:
        return errors

    requirements = {
        SKILL_PATH: (
            "Two independent approval gates",
            "Gate A",
            "Gate B",
            "Never display, summarize, quote, hash",
            "license every cluster node independently".lower(),
            "condition",
            "(Minor)",
            "no active IDP policy",
            "audit only",
        ),
        LICENSING_PATH: (
            "request system license add",
            "subsystem request failed on channel 0",
            "scp -O",
            "regular file",
            "symlink",
            "node 1",
        ),
        SIGNATURES_PATH: (
            "request security idp security-package offline-download",
            "request security idp security-package install",
            "terminal",
            "pilot",
            "Stop conditions",
        ),
        VERIFY_PATH: (
            "show security idp security-package-version",
            "show services application-identification version",
            "normaliz",
            "operational warning",
            "separate",
        ),
    }
    for path, terms in requirements.items():
        text = path.read_text(encoding="utf-8").lower()
        for term in terms:
            if term.lower() not in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: missing required contract term {term!r}"
                )

    # The skill must never instruct printing license contents.
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    for forbidden in ("show system license output in full", "print the license key"):
        if forbidden in skill_text.lower():
            errors.append(f"SKILL.md instructs exposing license material: {forbidden!r}")

    # No fixture or doc may carry license-like material.
    for path in (SKILL_PATH, LICENSING_PATH, SIGNATURES_PATH, VERIFY_PATH,
                 Path(__file__)):
        text = path.read_text(encoding="utf-8")
        if KEY_BLOCK_MARKER in text:
            errors.append(f"{path.name}: contains a key block marker")

    return errors


def main() -> int:
    errors = behavior_errors() + documentation_errors()
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        "OK: srx-license-signature-maintenance separates both approval gates, "
        "rejects unsafe license sources, polls to terminal states, requires "
        "per-node cluster evidence, retains version qualifiers, and refuses to "
        "claim enforcement without an active IDP policy"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
