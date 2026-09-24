# Platform scope and service licensing

Read this before telling an operator that a policy-attached security service is
available on their platform. The policy layer and the services attached to it
have different platform stories, and conflating them is how a skill ends up
promising a feature the device cannot run.

## The policy layer is the same on Branch

Validated on SRX345 hardware (Junos 26.2R1.7) by `commit check`, 2026-09-12.
Full record: `docs/skill-tests/2026-09-12-srx-policy-branch-srx345-validation.md`.

| Construct | Branch |
|---|---|
| Zone-pair policy (`from-zone` / `to-zone`) | validated |
| Global policy (`security policies global`) | validated |
| Unified policy (`match dynamic-application`) | validated |
| `default-policy deny-all` | validated |
| Address book: `attach zone`, `address`, `address-set` | validated |
| `applications application` / `application-set` | validated |
| `then log session-close`, `then count` | validated |

Design policy for Branch exactly as for any other SRX. Rule order, default
deny, object modelling, the global-policy output contract and the zone-pair
rewrite all apply unchanged.

Prior to 2026-09-12 this skill excluded Branch platforms outright. That
exclusion had **no recorded rationale** anywhere in the repository — no design
document, no reference file, no commit message — and no Branch hardware had
ever been tested against it. It was removed on measurement, not on argument.

## The services attached to policy are licence-gated

`then permit application-services ...` hangs AppID/AppFW, NGWF, EWF, SecIntel,
ATP and IDP/IPS off a policy. These are **entitlements**, not platform
capabilities, and the same gates apply on Branch as on higher-end SRX.

**The configuration schema accepting a statement proves nothing about
entitlement.** On the unlicensed SRX345 used for validation, the
`application-services` hierarchy was accepted into the candidate for
`security-intelligence-policy`, `application-firewall` and `idp-policy` — while
`show system license` reported no features installed at all. A schema that
accepts a statement is not a device that can run it.

Those three checks additionally returned **no commit-check verdict** on that
device, so this repository has no measured result for service attachment on
Branch in either direction. Say so rather than inferring.

### What to do instead of assuming

Ask the device. These are read-only:

```
show system license
show system license usage
show services application-identification version
show security idp security-package-version
```

Then state what is **entitled**, what is **configured**, and what is **active**
as three separate facts. A licence that is installed but expired, or a signature
package that was never downloaded, both present as "configured but not working".

`srx-license-signature-maintenance` covers reading and maintaining these
entitlements and their offline signature content.

### Platform notes worth knowing

- **These services are not substitutes for one another, and Branch does not
  change which one you need.** Pick by the control required, then check
  entitlement:
  - **AppFW** enforces on the identified application —
    `match dynamic-application`. Nothing else in this list does that.
  - **NGWF and EWF** are URL/web filtering. Both are configured *under* UTM
    (`security utm feature-profile web-filtering ...`) and attached with
    `then permit application-services utm-policy`, so UTM is the container they
    live in rather than an alternative to them. See
    `references/web-filtering-ngwf-ewf-patterns.md`.
  - **SecIntel and ATP** act on threat intelligence and file/threat analysis,
    not on application identity or URL category.

  Juniper publishes "Understanding UTM for Branch SRX Series", and UTM is
  commonly deployed on Branch — but that is a statement about where UTM is
  popular, not a licence to answer an application-control requirement with URL
  filtering.
- Unified policies with `match dynamic-application` have been Branch-supported
  since Junos 18.2R1, well below this skill's 23.x floor.
- Performance headroom, not policy semantics, is the usual real Branch
  constraint: session capacity, throughput with services enabled, and logging
  rate. None of that changes how a policy is written, and none of it was
  measured here.
