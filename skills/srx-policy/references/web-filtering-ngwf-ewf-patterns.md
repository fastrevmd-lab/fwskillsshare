# NGWF and EWF Configuration Patterns (srx-policy reference)

Moved out of SKILL.md for token-efficient progressive disclosure; content unchanged and previously reviewed.

NGWF facts to remember from Juniper docs:

- NGWF starts in Junos OS 23.4R1.
- NGWF uses Juniper NGWF cloud for URL category and reputation; the device caches results for faster later lookups.
- NGWF provides better URL traffic visibility than EWF, more regional language support, and direct URL categorization / re-categorization workflows.
- EWF and NGWF are separate license models, but Juniper documents migration from EWF to NGWF and notes category download / installation behavior with `wf_key_websense_ewf` or `wf_key_ng_juniper`.
- EWF sends requests directly from the device to the vendor cloud; NGWF uses Juniper URL filtering as the gateway to Juniper NGWF cloud.

Typical NGWF implementation flow:

1. Verify Junos release, platform support, license, DNS, routing, Internet reachability, and cloud egress policy.
2. Configure the SSL initiation profile required for NGWF cloud HTTPS communication.
3. Set the web-filtering type to `ng-juniper`.
4. Build an NGWF profile under `security utm feature-profile web-filtering ng-juniper profile`.
5. Create a UTM policy referencing that profile.
6. Attach the UTM policy to the intended global security policy under `then permit application-services utm-policy`.
7. Verify status, statistics, URL-block logs, policy hit counts, and user experience.

Example NGWF pattern for a global policy:

```junos
set security utm default-configuration web-filtering type ng-juniper
set security utm default-configuration web-filtering ng-juniper server tls-profile SSL-INIT-NGWF
set security utm default-configuration web-filtering ng-juniper default log-and-permit
set services ssl initiation profile SSL-INIT-NGWF client-certificate UTM-CERT
set services ssl initiation profile SSL-INIT-NGWF actions ignore-server-auth-failure
set services ssl initiation profile SSL-INIT-NGWF trusted-ca all

set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE category NG_Gambling_in_general action block
set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE default log-and-permit
set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE fallback-settings default permit
set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE fallback-settings server-connectivity log-and-permit
set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE fallback-settings timeout log-and-permit
set security utm feature-profile web-filtering ng-juniper profile WF-NG-BASE fallback-settings too-many-requests log-and-permit
set security utm utm-policy UTM-NG-WEB web-filtering http-profile WF-NG-BASE

set security policies global policy 200-USERS-WEB then permit application-services utm-policy UTM-NG-WEB
```

EWF compatibility pattern:

```junos
set security utm default-configuration web-filtering type juniper-enhanced
set security utm feature-profile web-filtering juniper-enhanced profile WF-EWF-BASE category Enhanced_Games action block
set security utm feature-profile web-filtering juniper-enhanced profile WF-EWF-BASE category Enhanced_Peer_to_Peer_File_Sharing action block
set security utm feature-profile web-filtering juniper-enhanced profile WF-EWF-BASE site-reputation-action harmful block
set security utm feature-profile web-filtering juniper-enhanced profile WF-EWF-BASE site-reputation-action suspicious quarantine
set security utm feature-profile web-filtering juniper-enhanced profile WF-EWF-BASE default log-and-permit
set security utm utm-policy UTM-EWF-WEB web-filtering http-profile WF-EWF-BASE

set security policies global policy 200-USERS-WEB then permit application-services utm-policy UTM-EWF-WEB
```

NGWF / EWF verification:

```text
show system license
show security utm web-filtering status
show security utm web-filtering statistics
show security policies hit-count global
show log messages | match "webfilter|web-filter|RT_UTM|URL_BLOCKED"
```

Useful NGWF categorization and migration commands:

```text
request security utm web-filtering categorize
request security utm web-filtering recategorize
request security utm web-filtering recategorize url <url> status
request security utm web-filtering category migrate-to-ng-juniper
show security utm web-filtering category migrate-to-ng-juniper status
```

EWF-to-NGWF migration pitfall: Juniper documents the migration as asynchronous and recommends doing it during downtime. Do not rename policy names during migration; Juniper notes configuration commit can fail if policy names are changed during migration.
