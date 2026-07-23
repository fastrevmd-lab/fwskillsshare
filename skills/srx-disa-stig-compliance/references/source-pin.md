# Y25M01 Source Pin

## Authoritative artifact

- Checklist: NIST NCP checklist 657
- NIST record: https://ncp.nist.gov/checklist/657
- NIST download resource: 12977
- Download record: https://ncp.nist.gov/checklist/657/download/12977
- Release/status: Y25M01, Final
- Artifact: `U_Juniper_SRX_SG_Y25M01_STIG.zip`
- Official package:
  https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_Juniper_SRX_SG_Y25M01_STIG.zip
- SHA-256:
  `9ffd17664efa307503f620434fec16501857196b091ea946f59284572f87690f`

The package is a Manual_STIG distribution with four XCCDF 1.1.4 benchmarks. It
contains no OVAL checks and provides no executable scanner. Configuration,
operational, and manual evidence must be evaluated explicitly.

## Component manifest

| Component | Release | Benchmark date | Accepted | Rules | CAT I | CAT II | CAT III | Ordered identity digest |
|---|---|---|---|---:|---:|---:|---:|---|
| NDM | NDM V3R3 | 30 Jan 2025 | 2024-12-20 | 68 | 8 | 43 | 17 | `3d8508a6909742904cecded5fd7608ff52d942da6754168d3f200e2caaf1f7d9` |
| ALG | ALG V3R3 | 30 Jan 2025 | 2024-12-19 | 24 | 4 | 20 | 0 | `7701a47e7baa3ad0e3649a28277ebad538bb753545902c6d8cbc1619f251cd12` |
| IDPS | IDPS V2R1 | 24 Jul 2024 | 2024-06-10 | 28 | 1 | 27 | 0 | `fdb172d016419c65854aabc646084c5fc0d4e8663e037b4e0659d9583370c6c1` |
| VPN | VPN V3R2 | 30 Jan 2025 | 2024-12-20 | 28 | 8 | 20 | 0 | `0c3b2f010690aeed833f80b68eeb1d40c7070267418f8f300ecebeba2679c10c` |
| **Total** |  |  |  | **148** | **21** | **110** | **17** |  |

The tuple digest is SHA-256 over source-ordered lines of
`V-ID|SV-ID|JUSX-ID|CAT`. It detects identifier, severity, omission, and order
drift without bundling source prose.

## XCCDF profiles

Each component contains the same nine profiles:

- `MAC-1_Classified`, `MAC-1_Public`, `MAC-1_Sensitive`
- `MAC-2_Classified`, `MAC-2_Public`, `MAC-2_Sensitive`
- `MAC-3_Classified`, `MAC-3_Public`, `MAC-3_Sensitive`

Every one selects all rules in its component. Treat these as source metadata,
not useful tailoring. Component role and rule applicability drive scope.

## Refresh procedure

1. Download only from the NIST-linked DISA source.
2. Compare the published and calculated SHA-256.
3. Run `scripts/extract-srx-stig-metadata.py <zip>`.
4. Review component/member changes, releases, dates, counts, identifiers,
   severities, rule order, N/A semantics, and revision history.
5. Reconcile every changed catalog row and compatibility note.
6. Update the source pin and tuple digests together.
7. Run the focused catalog validator and all repository gates.

If release, hash, members, counts, or tuple digests differ, fail closed. Do not
continue assessment by mixing the new artifact with the Y25M01 catalogs.
