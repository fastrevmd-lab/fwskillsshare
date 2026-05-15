# NGWF vs EWF research notes

Session-derived research for `srx-policy` web-filtering guidance. Use this as provenance and do not mirror it verbatim in user output.

## Sources checked

- Juniper NextGen Web Filtering Overview | Junos OS
  - URL: https://www.juniper.net/documentation/us/en/software/junos/utm/topics/concept/next-gen-juniper-url-filtering-overview.html
  - Observed date on page: 03-Feb-26
- request security utm web-filtering category migrate-to-ng-juniper | Junos OS
  - URL: https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/request-security-utm-web-filtering-category-migrate-to-ng-juniper.html
  - Observed date on page: 11-Aug-25
- Web Filtering Overview | Junos OS
  - URL: https://www.juniper.net/documentation/us/en/software/junos/utm/topics/concept/utm-web-filtering-overview.html
  - Observed date on page: 09-Nov-25
- Juniper Support Portal KB98153: [SRX] Configuring Next-Generation Web Filtering on SRX Devices
  - URL: https://supportportal.juniper.net/s/article/SRX-Configuring-Next-Generation-Web-Filtering-on-SRX-Devices
  - Created / Last Updated: 2025-05-01

## Durable conclusions

- NGWF is the newer preferred path for supported Junos 23.4R1+ SRX/cSRX deployments.
- Do not state that EWF is formally deprecated unless a current Juniper deprecation notice is found. Safer wording: EWF is an existing-estate / compatibility path, while NGWF is the preferred path for new supported designs.
- NGWF uses Juniper NGWF cloud for URL category/reputation; EWF sends requests directly from the device to the vendor cloud / Websense ThreatSeeker Cloud.
- NGWF provides customer-facing categorization / re-categorization workflows, status visibility, better URL traffic visibility, and broader regional language support than EWF according to Juniper's comparison table.
- EWF and NGWF have separate license models. Juniper documents migration from EWF to NGWF and notes NGWF/category download behavior when `wf_key_websense_ewf` or `wf_key_ng_juniper` is present.
- Starting Junos 23.4R1, Juniper documents NGWF availability and `wf_key_ng_juniper` behavior for new installs/upgrades.

## Useful commands and syntax

NGWF type/profile pattern:

```junos
set security utm default-configuration web-filtering type ng-juniper
set security utm default-configuration web-filtering ng-juniper server tls-profile <ssl-init-profile>
set security utm feature-profile web-filtering ng-juniper profile <profile> category <category> action <action>
set security utm utm-policy <utm-policy> web-filtering http-profile <profile>
set security policies global policy <policy> then permit application-services utm-policy <utm-policy>
```

Verification:

```text
show system license
show security utm web-filtering status
show security utm web-filtering statistics
show log messages | match -i "webfilter|web-filter|RT_UTM|URL_BLOCKED"
```

Categorization / re-categorization:

```text
request security utm web-filtering categorize
request security utm web-filtering recategorize
request security utm web-filtering recategorize url <url> status
```

EWF to NGWF migration:

```text
request security utm web-filtering category migrate-to-ng-juniper
show security utm web-filtering category migrate-to-ng-juniper status
```

Migration caution from Juniper docs:

- The migration command is asynchronous.
- Migration duration depends on platform and configured policies.
- Juniper recommends doing migration during downtime.
- If policy names are changed during migration, configuration commit can fail.
