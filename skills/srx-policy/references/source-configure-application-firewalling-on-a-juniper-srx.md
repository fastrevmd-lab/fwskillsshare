# Inspired by: Configure Application Firewalling on SRX

Source: Redelijkheid technical blog
URL: https://www.redelijkheid.com/blog/2013/5/10/configure-application-firewalling-on-a-juniper-srx
Retrieved: 2026-05-15

This is an independently written historical-context note. The upstream article and
configuration are not bundled or relicensed.

## Design takeaways

- AppFW classifies applications after a session is admitted by a security policy;
  it does not replace zone, address, service, and default-deny design.
- Application signatures, packages, licenses, and platform support have changed
  since the lab was published. Current Juniper documentation is authoritative.
- Define a conservative action for unknown, unsupported, or unresolved traffic and
  log application decisions needed for operations.

Validate signature-package state, first-packet behavior, encrypted traffic limits,
fallback handling, AppFW counters, and the parent security-policy hit count.
