# Cisco FMC and FDM REST API JSON Format Reference

## Documentation Sources

### Attempted Sources (Inaccessible — HTTP 403)

The following official Cisco documentation pages were identified but returned 403 Forbidden errors during automated access attempts:

- [FMC REST API Quick Start Guide v10.0](https://www.cisco.com/c/en/us/td/docs/security/firepower/10-0/API/REST/firepower_management_center_rest_api_quick_start_guide_10_0/About_The_Firewall_Management_Center_REST_API.html)
- [FTD REST API Guide](https://www.cisco.com/c/en/us/td/docs/security/firepower/ftd-api/guide/ftd-rest-api.html)
- Multiple FMC Quick Start Guides (v7.0, v7.2, v7.3, v7.4, v7.6, v7.7)

### Sources Actually Consulted

Information in this reference was gathered from:

- **Cisco DevNet Resources**:
  - [Firepower Management Center API](https://developer.cisco.com/secure-firewall/management-center/) — landing page with general API structure
  - [FTD API Reference v6.2 (FTD v7.2)](https://developer.cisco.com/docs/ftd-api-reference/latest/) — base URL and JSON format information
- **Community Documentation**: GitHub repositories (PowerFMC, Net::Cisco::FMC, fmc-rest-client) with endpoint path examples
- **Search Result Excerpts**: Partial content from cisco.com pages accessible via search engine result previews

**Verification Limitation**: Without access to complete official API documentation, sections marked `[unverified]` could not be confirmed and require validation against a live API Explorer (`https://{fmc-or-ftd}/api/api-explorer`) or official documentation.

## Input Packaging

This skill accepts three input forms:

### 1. Keyed Envelope (Preferred)

```json
{
  "fmc_exports": {
    "domain_uuid": "e276abec-e0f2-11e3-8169-6d9ed49b625f",
    "responses": {
      "accesspolicies": { "items": [...], "paging": {...} },
      "networks": { "items": [...], "paging": {...} },
      "networkgroups": { "items": [...], "paging": {...} }
    }
  }
}
```

The `responses` object keys match FMC endpoint suffixes (e.g., `accesspolicies`, `networks`, `portobjectgroups`). Each value is a complete API response including `items` and `paging` metadata.

### 2. Bundle Format

```json
{
  "responses": [
    {
      "endpoint": "/api/fmc_config/v1/domain/{uuid}/policy/accesspolicies",
      "response": { "items": [...], "paging": {...} }
    },
    {
      "endpoint": "/api/fmc_config/v1/domain/{uuid}/object/networks",
      "response": { "items": [...], "paging": {...} }
    }
  ]
}
```

Each entry carries the full endpoint path and the JSON response body.

### 3. Single Response

A bare FMC API response object (detected by presence of `items` or `paging` top-level keys):

```json
{
  "items": [
    { "type": "AccessPolicy", "id": "...", "name": "..." }
  ],
  "paging": { "count": 1, "limit": 25, "offset": 0, "pages": 1 }
}
```

**Warning**: A single-response input yields a **partial parse**. The parser records a warning in `metadata.warnings` stating that only one endpoint was provided and cross-references cannot be fully resolved.

## Paging and Truncation

FMC API responses include a `paging` metadata block:

```json
{
  "items": [ ... ],
  "paging": {
    "count": 150,
    "limit": 25,
    "offset": 0,
    "pages": 6
  }
}
```

- `count`: Total number of items in the collection on the server
- `limit`: Maximum items returned in this response (default 25)
- `offset`: Starting position for this page
- `pages`: Total number of pages

**Critical Rule**: If `paging.count` exceeds the number of items actually present in the `items` array, the collection is **TRUNCATED**. This is recorded in `metadata.warnings` as:

```
Truncated collection detected: {endpoint} reports {count} total items but only {actual} provided (offset {offset}). Policy parse is INCOMPLETE.
```

A truncated collection is **never** treated as a complete object set. All downstream audit findings must be qualified with the incomplete-data warning.

To retrieve complete collections, callers must page through results by adjusting `offset` and `limit` query parameters until all items are retrieved, then merge the `items` arrays before passing to the parser.

## Reference Shape

Network objects, zones, services, and other reusable entities are represented in two forms:

### Object References

Named objects carry `type`, `id`, and usually `name`:

```json
{
  "type": "Network",
  "id": "00505694-9ff4-11ec-ba6c-c58e9427c3b9",
  "name": "internal-net"
}
```

Some references include a `links.self` URL for retrieval:

```json
{
  "type": "NetworkGroup",
  "id": "00505694-a001-11ec-ba6c-c58e9427c3b9",
  "name": "RFC1918-Networks",
  "links": {
    "self": "https://fmc/api/fmc_config/v1/domain/{uuid}/object/networkgroups/00505694-a001-11ec-ba6c-c58e9427c3b9"
  }
}
```

### Literal Values `[unverified]`

Protocol numbers, port numbers, and ICMP types appear as inline literals in some contexts. The exact structure varies by endpoint and object type. Example from access rule source ports:

```json
{
  "protocol": "6",
  "port": "443"
}
```

The parser normalizes these into a reference container:

```json
{
  "objects": [
    { "type": "Network", "id": "...", "name": "internal-net" }
  ],
  "literals": [
    { "type": "Protocol", "value": "6" },
    { "type": "Port", "value": "443" }
  ]
}
```

**Note**: The `literals` normalization schema is marked `[unverified]` because Cisco's accessible documentation did not provide complete examples of all literal value formats. Validation against live API responses is required.

## FMC Endpoint Families

FMC REST API endpoints follow the pattern:

```
/api/fmc_config/v1/domain/{domainUUID}/{family}/{resource}
```

Common endpoint families verified from documentation and community examples:

| Family | Resource Examples | Status |
|--------|------------------|--------|
| `policy` | `accesspolicies`, `accesspolicies/{id}/accessrules`, `prefilterpolicies`, `prefilterpolicies/{id}/prefilterrules`, `accesspolicies/{id}/defaultactions`, `intrusionpolicies` | Verified |
| `object` | `networks`, `networkgroups`, `hosts`, `ranges`, `fqdns`, `portobjectgroups`, `protocolportobjects`, `icmpv4objects`, `icmpv6objects` | Partially verified |
| `devices` | `devicerecords` | Verified |
| `audit` | `auditrecords` | Verified |

**Unverified endpoint families** (mentioned in community code but not confirmed in accessible official docs):

| Family | Resource Examples | Status |
|--------|------------------|--------|
| `object` | `applicationgroups`, `urlgroups`, `vlangroups`, `securityzones` | `[unverified]` |
| `policy` | `natrules`, `filepolicies`, `malwarepolicies` | `[unverified]` |

To verify additional endpoints, consult the API Explorer built into your FMC instance at:

```
https://{fmc-hostname}/api/api-explorer
```

## FDM (Firepower Threat Defense) Differences

FDM-managed FTD devices use a different API with distinct structural differences from FMC:

### 1. Base URL

FMC: `/api/fmc_config/v1/domain/{domainUUID}/...`

FDM: `/api/fdm/v6/...` (version varies; v6 is representative)

### 2. Flatter Object Model `[unverified]`

FDM responses appear to use a flatter JSON structure without the deep policy hierarchy found in FMC (based on migration discussions in community forums, not confirmed in official docs).

### 3. Field Name Differences

Verified from DevNet examples and community posts:

- **Action field**: FDM uses `ruleAction` (e.g., `"ruleAction": "PERMIT"`), while FMC uses `action`
- **Logging**: FDM uses `eventLogAction` (e.g., `"eventLogAction": "LOG_FLOW_END"`), while FMC uses `logBegin`/`logEnd` boolean fields

### 4. No Policy Sections `[unverified]`

FMC access policies have Mandatory, Standard, and Default sections. FDM does not appear to use this three-tier structure (based on community migration discussions).

### 5. No Policy Inheritance `[unverified]`

FMC supports parent/child policy relationships. FDM does not appear to support policy inheritance.

**Validation Note**: FDM differences marked `[unverified]` are based on community forum posts and migration tool discussions, not official API documentation. Confirm these differences against the FDM API Explorer before relying on them:

```
https://{ftd-hostname}/api/api-explorer
```

## Out of Scope

The following formats are **explicitly excluded** from this skill's scope:

### 1. `.sfo` Policy Bundles

FMC policy bundles (`.sfo` files) are binary or proprietary-format exports used for backup and policy migration between FMC instances. These files are:

- Not documented for third-party parsing in Cisco's public API documentation
- Not accessible via the REST API as structured JSON
- Reverse-engineering would violate the repository's evidence rule requiring "authoritative evidence or an explicit unsupported/uncertain classification"

**Reason for exclusion**: No published specification exists for parsing `.sfo` internals.

### 2. PDF Policy Reports

FMC can export policy reports as PDF files. These are presentation documents, not structured data exports, and parsing them would require OCR or PDF text extraction, which:

- Is fragile and error-prone
- Does not provide UUIDs or full object metadata
- Cannot reliably distinguish object references from inline literals

**Reason for exclusion**: PDF reports are intended for human review, not programmatic parsing. The REST API JSON exports provide the authoritative structured representation.

### 3. Configuration Backups via HTTPS Export

FMC supports HTTPS-based configuration exports (not the REST API). The format of these exports is not documented in the REST API guides and appears to be a different serialization than the REST JSON responses.

**Reason for exclusion**: Not documented as a supported third-party parsing target.

---

**Verification Status Summary**:

- **FMC endpoint paths and paging structure**: Verified from DevNet resources and community examples
- **Object reference format** (`type`, `id`, `name`): Verified
- **FDM field differences** (`ruleAction`, `eventLogAction`): Verified from DevNet examples
- **Complete endpoint family table**: Partially verified; marked unverified entries require live API Explorer validation
- **Literal value normalization schema**: Unverified; requires validation against live responses
- **FDM structural differences** (sections, inheritance): Unverified; based on community discussions, not official docs

For production use, validate all `[unverified]` sections against the API Explorer in your FMC or FDM instance.
