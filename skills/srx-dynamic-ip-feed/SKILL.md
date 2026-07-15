---
name: srx-dynamic-ip-feed
description: Configure, audit, and troubleshoot Juniper SRX dynamic IP objects from HTTPS feeds. Use when handling feed archives, dynamic-address mapping, certificate validation, basic auth, mTLS, session scanning, routing-instance reachability, show security dynamic-address, ipfd logs, or feed and TLS failures. Use srx-policy for SecIntel feeds.
version: 1.0.2
author:
  - fastrevmd-lab
  - Claude
  - GPT
license: MIT
metadata:
  hermes:
    tags: [srx, junos, dynamic-address, feed-server, ipfd, feed-name, session-scan, mutual-tls, basic-auth, firewall, security-policy, pki, tls, nginx]
    related_skills: [parsing-srx-configs, srx-policy]
  sources:
    - title: SRX Dynamic IP Objects aka Feed-server
      author: Karel Hendrych
      url: https://community.juniper.net/blogs/karel-hendrych/2025/11/30/srx-dynamic-ip-objects-aka-feed-server
      retrieved: "2026-05-14"
      inspired_note: references/source-extract.md
---

# SRX Dynamic IP Feed Servers

## Overview

SRX dynamic IP objects let Junos periodically download IPv4/IPv6 entries from an HTTPS feed server and expose those entries as address objects usable in security policies. This is useful when rule structure is stable but source or destination addresses change frequently through automation, threat intelligence, cloud inventory, orchestration systems, or allow/block lists.

The key SRX idea is:

1. The web server hosts a bundle archive, typically `.tgz`.
2. Inside the archive are feed files, each containing IPs/prefixes/ranges.
3. `security dynamic-address feed-server <server>` points to the archive URL.
4. `feed-name <name> path <path-inside-archive>` maps a feed to a file in the archive.
5. `security dynamic-address address-name <object> profile feed-name <feed>` exposes the feed as a policy address object.
6. Policies reference the dynamic address name as source or destination address.

SRX checks feed freshness with HTTP `HEAD`, downloads changed archives with `GET`, and updates dynamic objects without a commit. The default update interval is 5 minutes; the minimum is 30 seconds. Use production TLS validation and authentication whenever possible.

## Scope and routing

Use this skill for self-hosted dynamic-address feeds. Use `srx-policy` for Juniper SecIntel or ATP feeds and `parsing-srx-configs` for full-config extraction.

## Prerequisites and Version Notes

- SRX/vSRX running Junos with `security dynamic-address` feed support.
- A reachable HTTPS server that supports `HEAD` and `GET` against the feed archive URL.
- Feed archive in a format supported by Junos. This skill focuses on bundle archive `.tgz` mode.
- Feed file contents can include:
  - single IPs: `192.0.2.1`, `2001:db8::1`
  - prefixes: `192.0.2.32/28`, `2001:db8:1::/64`
  - ranges: `192.0.2.5-192.0.2.20`, `2001:db8::5-2001:db8::20`
- Junos 25.2 or later is required for the simple SRX username/password authentication feature described here.
- For production, prefer DNS/hostname feed URLs with certificate validation. If using static host mapping, ensure the hostname in the URL matches the certificate CN or SAN when certificate attribute validation is enabled.

## Feed Archive Layout

Use one directory per archive and one file per feed. Example:

```bash
cd /var/www/html
mkdir feed-1
printf '1.1.1.1\n' > feed-1/whitelist-1
printf '2.2.2.2\n' > feed-1/blacklist-1
tar czf feed-1.tgz feed-1/
```

The SRX maps the archive contents by path:

```text
feed-1.tgz
└── feed-1/
    ├── whitelist-1
    └── blacklist-1
```

SRX feed-name mapping:

```junos
set security dynamic-address feed-server debian-1 feed-name whitelist-1 path feed-1/whitelist-1
set security dynamic-address feed-server debian-1 feed-name blacklist-1 path feed-1/blacklist-1
```

Then expose each feed as a dynamic policy object:

```junos
set security dynamic-address address-name whitelist-1 profile feed-name whitelist-1
set security dynamic-address address-name blacklist-1 profile feed-name blacklist-1
```

## Lab-Grade HTTPS Feed Server

Use this only for labs because it does not validate the server certificate on SRX.

On Debian with nginx:

```bash
apt install nginx-light ssl-cert
make-ssl-cert generate-default-snakeoil
```

Enable the SSL listener in `/etc/nginx/sites-enabled/default`:

```nginx
listen 443 ssl default_server;
listen [::]:443 ssl default_server;
include snippets/snakeoil.conf;
```

Restart and test:

```bash
systemctl restart nginx
openssl s_client -connect localhost:443
```

Create a feed archive:

```bash
cd /var/www/html
mkdir feed-1
printf '1.1.1.1\n' > feed-1/whitelist-1
printf '2.2.2.2\n' > feed-1/blacklist-1
tar czf feed-1.tgz feed-1/
tail -f -n0 /var/log/nginx/access.log
```

SRX lab configuration:

```junos
set security dynamic-address feed-server debian-1 url https://10.0.0.10/feed-1.tgz
set security dynamic-address feed-server debian-1 update-interval 60
set security dynamic-address feed-server debian-1 hold-interval 604800
set security dynamic-address feed-server debian-1 feed-name whitelist-1 path feed-1/whitelist-1
set security dynamic-address feed-server debian-1 feed-name blacklist-1 path feed-1/blacklist-1
set security dynamic-address address-name whitelist-1 profile feed-name whitelist-1
set security dynamic-address address-name blacklist-1 profile feed-name blacklist-1
```

Commit and verify. The nginx access log should show an initial `GET`, then periodic `HEAD` probes. When the archive changes, SRX should perform another `GET`.

## Production Pattern: Validate the Feed Server Certificate

Production feed servers should use a certificate issued by a CA trusted by the SRX, and the SRX should validate that the certificate identity matches the URL hostname.

### Server Side

Generate or obtain:

- CA certificate, e.g. `IPFD_CA`
- server certificate/key for the feed server hostname, e.g. `debian-2`

Install the server cert/key and CA certificate for nginx:

```bash
cp CA/cacert.pem /etc/ssl/certs/IPFD_CA.pem
cp CA/debian-2-cert.pem /etc/ssl/certs/
cp CA/debian-2-key.pem /etc/ssl/private/
chmod 600 /etc/ssl/private/debian-2-key.pem
```

Configure nginx SSL snippet, e.g. `/etc/nginx/snippets/IPFD.conf`:

```nginx
ssl_certificate /etc/ssl/certs/debian-2-cert.pem;
ssl_certificate_key /etc/ssl/private/debian-2-key.pem;
```

Enable it in the site:

```nginx
listen 443 ssl default_server;
listen [::]:443 ssl default_server;
include snippets/IPFD.conf;
```

Restart:

```bash
systemctl restart nginx
openssl s_client -connect localhost:443
```

Create the production archive:

```bash
cd /var/www/html
mkdir feed-2
printf '10.1.1.1\n' > feed-2/whitelist-2
printf '10.2.2.2\n' > feed-2/blacklist-2
tar czf feed-2.tgz feed-2/
tail -f -n0 /var/log/nginx/access.log
```

### SRX Side

Configure and load the CA profile:

```junos
set security pki ca-profile IPFD_CA ca-identity IPFD_CA revocation-check disable
```

Then load the CA certificate after uploading it to the SRX:

```text
request security pki ca-certificate load ca-profile IPFD_CA filename cacert.pem
request security pki ca-certificate verify ca-profile IPFD_CA
```

Configure hostname resolution if DNS is not available:

```junos
set system static-host-mapping debian-2 inet 10.0.1.10
```

Configure the SSL initiation profile and feed server:

```junos
set services ssl initiation profile srx-1_IPFD_CA trusted-ca IPFD_CA
set security dynamic-address feed-server debian-2 url https://debian-2/feed-2.tgz
set security dynamic-address feed-server debian-2 update-interval 60
set security dynamic-address feed-server debian-2 hold-interval 86400
set security dynamic-address feed-server debian-2 tls-profile srx-1_IPFD_CA
set security dynamic-address feed-server debian-2 validate-certificate-attributes subject-or-subject-alternative-names
set security dynamic-address feed-server debian-2 feed-name whitelist-2 path feed-2/whitelist-2
set security dynamic-address feed-server debian-2 feed-name blacklist-2 path feed-2/blacklist-2
set security dynamic-address address-name whitelist-2 profile feed-name whitelist-2
set security dynamic-address address-name blacklist-2 profile feed-name blacklist-2
```

Important: with `validate-certificate-attributes subject-or-subject-alternative-names`, the hostname in the URL must match the server certificate CN or SAN. A URL like `https://debian-3/feed-2.tgz` against a certificate for `debian-2` should fail.

## Optional: HTTP Basic Authentication

Requires Junos 25.2R1 or later for SRX client username/password feed authentication.

On nginx, enable basic auth for the relevant location:

```nginx
location / {
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/htpasswd;
    # existing content serving configuration
}
```

Create credentials:

```bash
apt install apache2-utils
htpasswd -c -b /etc/nginx/htpasswd srx <feed-basic-auth-password>
systemctl restart nginx
```

Before SRX credentials are configured, expect HTTP 401 errors in `ipfd` logs:

```text
failed<http return error code 401>
```

Add credentials to the SRX feed server:

```junos
set security dynamic-address feed-server debian-2 user-name srx
set security dynamic-address feed-server debian-2 password <feed-basic-auth-password>
```

Use a secure password management workflow for production. Avoid leaving cleartext credentials in tickets, chat, or documentation.

## Optional: Mutual TLS Client Certificate Authentication

Use mutual TLS when the feed server should only serve feed archives to authenticated SRX clients.

On nginx, configure a trusted client CA and enforce client certificate success inside a location:

```nginx
ssl_client_certificate /etc/ssl/certs/IPFD_CA.pem;
ssl_verify_client optional;

location / {
    if ($ssl_client_verify != SUCCESS) {
        return 403;
    }
    # existing content serving configuration
}
```

Without the SRX client cert, expect HTTP 403 errors in `ipfd` logs:

```text
failed<http return error code 403>
```

Upload the SRX client certificate and key to SRX, then load and verify:

```text
request security pki local-certificate load certificate-id srx-1_IPFD_CA filename srx-1-cert.pem key srx-1-key.pem
request security pki local-certificate verify certificate-id srx-1_IPFD_CA
```

Reference the client certificate from the SSL initiation profile:

```junos
set services ssl initiation profile srx-1_IPFD_CA client-certificate srx-1_IPFD_CA
```

After commit, successful downloads should resume.

## Applying Dynamic Objects in Security Policies

Dynamic address names become policy address objects and can be used as source or destination criteria.

Example blocklist policy:

```junos
set security policies from-zone trust to-zone untrust policy block-dynamic-bad-dst match source-address any
set security policies from-zone trust to-zone untrust policy block-dynamic-bad-dst match destination-address blacklist-1
set security policies from-zone trust to-zone untrust policy block-dynamic-bad-dst match application any
set security policies from-zone trust to-zone untrust policy block-dynamic-bad-dst then deny
set security policies from-zone trust to-zone untrust policy block-dynamic-bad-dst then log session-init
```

Example allowlist policy:

```junos
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst match source-address any
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst match destination-address whitelist-1
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst match application junos-http
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst then permit
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst then log session-init
set security policies from-zone trust to-zone untrust policy permit-dynamic-good-dst then log session-close
```

Policy ordering still matters. Put deny/reject blocklist policies above broader permit policies when the blocklist must take precedence.

## Session Scan Tunable

SRX can reconcile existing sessions when addresses are added to dynamic feeds. Enable:

```junos
set security dynamic-address session-scan
```

Important behavior:

- Session scan works for policies with `deny` or `reject` action.
- It is useful when a newly added blacklist address should affect existing sessions.
- Removing an address from an allowlist does not automatically kill existing sessions by itself. If immediate teardown behavior is needed, add the address to a deny/reject feed at least temporarily so a deny/reject policy can match.

A common structure is:

1. `reject-http` or `deny-bad` policy matching `blacklist-1`
2. permit policy matching `whitelist-1`
3. final deny policy for everything else

## Routing Instance Reachability

If the feed server is reachable only through a non-default routing instance, configure the feed-server routing table. The hidden stanza uses `table.inet` format without the normal trailing `.0`:

```junos
set routing-instances vr-1 instance-type virtual-router
set security dynamic-address feed-server debian-1 routing-table vr-1.inet
```

Live-verified on vSRX 24.4R1: the table name takes NO trailing `.0` — `routing-table vr-1.inet.0` and even `inet.0` are rejected with `routing table ... cannot find`, while the bare form `inet` (default instance) and `<instance>.inet` are accepted. The referenced instance's table must already exist on the device when the commit is validated: defining the routing instance in the same candidate still fails commit check with "cannot find" — commit the instance first.

Verify routing and source reachability from the relevant routing instance before troubleshooting TLS or feed syntax.

## Verification Commands

After commit, check feed-server and feed status:

```text
show security dynamic-address summary
```

Look for:

- server name and URL
- update interval and hold interval
- TLS profile and user name fields
- feed names mapped to dynamic address names
- total IPv4/IPv6 entries
- download/db/other error counters
- next update and expiration times
- last update status

List loaded dynamic address records:

```text
show security dynamic-address
```

Check feed downloader logs:

```text
show log messages | match ipfd
```

Expected successful log patterns include:

```text
IPFD_DA_FEED_HTTPS_STATUS: Feed(<feed>) download data(<url>) status (succeeded)
IPFD_DA_FEED_HTTPS_STATUS: Feed(<feed>) download data(<url>) status (succeeded<file not changed>)
```

On the web server, tail access logs:

```bash
tail -f -n0 /var/log/nginx/access.log
```

Expected web access pattern:

```text
GET /feed-1.tgz HTTP/1.1 200
HEAD /feed-1.tgz HTTP/1.1 200
HEAD /feed-1.tgz HTTP/1.1 200
```

When the archive changes, expect a `HEAD` followed by a `GET`.

## Update Test Procedure

Read `references/feed-update-test.md` when validating that feed changes propagate without a configuration commit.

## Troubleshooting Matrix

| Symptom | Likely Cause | What to Check |
|---|---|---|
| No entries in `show security dynamic-address` | Feed file empty, path mismatch, archive mismatch, download failure | `show security dynamic-address summary`, `show log messages \| match ipfd`, archive paths with `tar tzf` |
| HTTP 401 in ipfd logs | Basic auth enabled on server but SRX has no/wrong credentials | `user-name`, `password`, nginx htpasswd file |
| HTTP 403 in ipfd logs | mTLS enforced but SRX has no/invalid client certificate | local certificate load/verify, SSL initiation profile `client-certificate`, nginx client CA |
| SSL peer certificate error | Missing/untrusted CA or server cert validation failure | CA profile, loaded CA cert, SSL initiation profile trusted CA |
| `IPFD_DA_FEED_CERT_SUBJ_CHECK_FAIL` | URL hostname does not match server cert CN/SAN | Use correct DNS/static-host-mapping and URL hostname, regenerate cert if needed |
| Initial GET works but updates do not | Archive not recreated, mtime/headers not changing, HEAD handling issue | Recreate `.tgz`, nginx logs, check HEAD 200 responses |
| Feed unreachable only from SRX | Routing or source path issue | static route/default route, routing-instance `routing-table`, DNS/static-host-mapping |
| Old sessions still pass after feed change | Existing sessions not being reconciled | Consider `set security dynamic-address session-scan`; use deny/reject policies for blacklist entries |
| Scale concerns | Platform limits or PFE update time | `/var/log/ipfd`, platform capacity, staged performance testing |

## Common Pitfalls

1. **Using IP URLs in production with certificate validation.** Certificate identity validation needs a hostname that matches the certificate CN/SAN. Use DNS or `system static-host-mapping` and put the hostname in the feed URL.

2. **Forgetting that `feed-name path` is the path inside the archive.** If the archive contains `feed-1/blacklist-1`, configure that full path, not only `blacklist-1`.

3. **Updating feed files but not recreating the `.tgz`.** SRX downloads the archive URL, not the loose files. Re-run `tar czf feed-X.tgz feed-X/` after changing contents.

4. **Assuming removal from an allowlist kills sessions.** Dynamic address updates affect policy matching, but existing sessions may persist. Use session scan plus deny/reject feed design where immediate teardown is required.

5. **Setting too aggressive update intervals without considering server and fleet load.** The minimum can be 30 seconds, but many SRXs polling many feeds can create avoidable server load.

6. **Treating lab TLS as production TLS.** A self-signed server without SRX validation is useful for proving feature behavior, not for production security.

7. **Using revocation-check disable without understanding risk.** The demo disables revocation checking for simplicity. Production PKI should explicitly decide CRL/OCSP behavior.

8. **Leaking feed-server credentials.** SRX basic auth passwords and private keys should not be pasted into chat/logs/tickets. Use redaction and credential-handling practices.

## Verification Checklist

- [ ] Feed archive URL is reachable from the SRX routing context.
- [ ] Web server returns HTTP 200 for `GET` and `HEAD` against the archive URL.
- [ ] Archive contains expected paths: `tar tzf feed-X.tgz`.
- [ ] `feed-name <name> path <archive/path>` matches archive contents exactly.
- [ ] `address-name <object> profile feed-name <feed>` exists for every policy object.
- [ ] TLS CA profile is loaded and verified when certificate validation is used.
- [ ] URL hostname matches server certificate CN/SAN when certificate attribute validation is enabled.
- [ ] Basic auth credentials or client certificate are configured if the server requires them.
- [ ] `show security dynamic-address summary` shows zero download errors and expected entry counts.
- [ ] `show security dynamic-address` shows expected IPs/prefixes/ranges.
- [ ] Policies reference dynamic address names in correct source/destination fields and correct order.
- [ ] `show log messages | match ipfd` shows succeeded or succeeded<file not changed>.
- [ ] Server logs show expected GET/HEAD behavior.
- [ ] Update test confirms changed archive contents appear without commit.

## Source

This skill is a condensed, operationalized SRX playbook based on Karel Hendrych's Juniper Community TechPost, “SRX Dynamic IP Objects aka Feed-server,” published 2025-11-30:

https://community.juniper.net/blogs/karel-hendrych/2025/11/30/srx-dynamic-ip-objects-aka-feed-server

An independently written `Inspired by` note is stored at
`references/source-extract.md`; it preserves attribution and verification
implications without reproducing the TechPost.
