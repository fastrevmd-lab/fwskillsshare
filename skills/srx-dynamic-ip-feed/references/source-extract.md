# Inspired by: SRX Dynamic IP Objects aka Feed-server

- **Author:** Karel Hendrych
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/karel-hendrych/2025/11/30/srx-dynamic-ip-objects-aka-feed-server
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the archive layout, HTTPS client options,
  dynamic-address mapping, update behavior, and troubleshooting workflow.

## Original summary

SRX dynamic IP objects separate stable policy logic from frequently changing
address data. A feed server publishes IPv4 or IPv6 addresses, prefixes, or
ranges. Junos maps files inside an archive to feed names, exposes those feed
names as dynamic address objects, and lets security policy match the objects as
source or destination criteria.

The TechPost demonstrates bundle-archive mode with a `.tgz` file served over
HTTPS. The configured `feed-name` path must match the path inside the archive.
When the archive changes, the SRX can refresh the object contents without a
configuration commit. The article observes HTTP `HEAD` checks followed by a
`GET` when content changes; the web service therefore needs to support both
methods.

The article separates a deliberately insecure lab path from production
patterns. A production feed should use a hostname that matches the server
certificate, a trusted CA through an SSL initiation profile, and certificate
attribute validation. Depending on Junos support and server policy, client
authentication can be anonymous, HTTP username/password, or mutual TLS. The
article associates simple HTTP password authentication with Junos 25.2R1, so
verify release support before using it.

Operational verification has three independent views:

- `show security dynamic-address summary` reports server/feed status, counts,
  update timing, and errors.
- `show security dynamic-address` confirms that expected entries are mapped to
  the intended object.
- `show log messages | match ipfd` and the HTTPS server access log show the
  fetch, certificate, authentication, and unchanged-file outcomes.

Use the separate `feed-update-test.md` to prove that rebuilding the archive
causes the new entries to appear without a commit. Validate the archive paths,
routing-instance reachability, DNS, CA chain, certificate name, authentication,
and policy reference before treating the feed as operational.

## Verification implications

- Confirm supported feed formats, scale, intervals, and authentication methods
  for the target platform and Junos release in current Juniper documentation.
- Treat the article's Debian/nginx and demonstration-PKI steps as inspiration,
  not a production hardening standard.
- Do not copy demonstration passwords, private keys, or disabled revocation
  settings into a deployment.
- Exercise failure cases for an unreachable server, invalid certificate chain,
  hostname mismatch, bad credentials, malformed archive, and stale feed.

This repository contains this independently written note and a source link, not
the TechPost text or its images.
