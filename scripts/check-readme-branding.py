#!/usr/bin/env python3
"""Verify the README uses the theme-aware fw[skills]share wordmark."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ASSETS = {
    "docs/assets/fwskillsshare-wordmark.svg": ("#F8F9FA", "#C4B5FD"),
    "docs/assets/fwskillsshare-wordmark-light.svg": ("#171A22", "#7C3AED"),
}


def main() -> int:
    errors: list[str] = []
    readme = README.read_text(encoding="utf-8")

    for relative_path, (base_color, skills_color) in ASSETS.items():
        if relative_path not in readme:
            errors.append(f"README.md does not reference {relative_path}")

        asset = ROOT / relative_path
        if not asset.is_file():
            errors.append(f"missing wordmark asset: {relative_path}")
            continue

        svg = asset.read_text(encoding="utf-8")
        if f'fill="{base_color}"' not in svg:
            errors.append(f"{relative_path} does not use base color {base_color}")
        if f'<tspan fill="{skills_color}">skills</tspan>' not in svg:
            errors.append(f"{relative_path} does not color the skills fragment {skills_color}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1

    print("OK: README renders fw[skills]share with theme-aware violet branding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
