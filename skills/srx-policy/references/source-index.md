# SRX Policy Source Index

This index records the source articles used to synthesize `srx-policy`. HTTP/extraction status is preserved so future agents know which sources were fully available and which were only partially accessible during creation.

## Primary reading-list sources

- [Add a Web Filtering Profile | J-Web for SRX Series 23.2](https://www.juniper.net/documentation/us/en/software/jweb-srx23.2/jweb-srx/topics/task/j-web-security-content-security-web-filtering-profile-add.html) -> `source-add-a-web-filtering-profile-j-web-for-srx-series-23-2.md`; HTTP 404; chars 13989 (limited extraction; do not rely on details not corroborated elsewhere)
- [Configure Application Firewalling On A Juniper SRX](https://www.redelijkheid.com/blog/2013/5/10/configure-application-firewalling-on-a-juniper-srx) -> `source-configure-application-firewalling-on-a-juniper-srx.md`; HTTP 200; chars 14418
- [Configuring Security Policies | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-policy-configuration.html) -> `source-configuring-security-policies-junos-os.md`; HTTP 200; chars 68192
- [Getting Started with ATP Appliance and the SRX Series](https://www.juniper.net/documentation/us/en/software/atp-appliance/atp-appliance-srx-integration/topics/concept/atp-appliance-srx-integration-overview.html) -> `source-getting-started-with-atp-appliance-and-the-srx-series.md`; HTTP 200; chars 1702
- [How to use SecIntel?](https://www.reddit.com/r/Juniper/comments/1hpjo6a/how_to_use_secintel/) -> `source-how-to-use-secintel.md`; HTTP 200; chars 37 (limited extraction; do not rely on details not corroborated elsewhere)
- [JNCIP-SEC – Configuring Juniper Enhanced Web Filtering](https://blog.netpro.be/jncip-sec-configuring-juniper-enhanced-web-filtering/) -> `source-jncip-sec-configuring-juniper-enhanced-web-filtering.md`; HTTP 200; chars 12011
- [Juniper Advanced Threat Prevention datasheet](https://www.networkscreen.com.au/datasheets/ds-advanced-threat-prevention.pdf) -> `source-juniper-advanced-threat-prevention-datasheet.md`; HTTP 200; chars 14261
- [Juniper SecIntel Datasheet](https://www.juniper.net/us/en/products/security/secintel-datasheet.html) -> `source-juniper-secintel-datasheet.md`; HTTP 200; chars 23684
- [Juniper SRX Enhanced Web Filtering Configuration](https://rayka-co.com/lesson/juniper-srx-enhanced-web-filtering-configuration/) -> `source-juniper-srx-enhanced-web-filtering-configuration.md`; HTTP 200; chars 16707
- [Juniper SRX Policy Configuration](https://rayka-co.com/lesson/juniper-srx-policy-configuration/) -> `source-juniper-srx-policy-configuration.md`; HTTP 200; chars 13193
- [SecIntel Feeds Overview and Benefits](https://www.juniper.net/documentation/us/en/software/atp-cloud/atp-cloud-user-guide/topics/concept/secintel-feeds-overview-and-benefits.html) -> `source-secintel-feeds-overview-and-benefits.md`; HTTP 200; chars 13713
- [Global Policy Overview | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/security-global-policies.html) -> `source-security-global-policies.md`; HTTP 200; chars 14657
- [Security Policy Applications and Application Sets | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/security-policies/topics/topic-map/policy-application-sets-configuration.html) -> `source-security-policy-applications-and-application-sets-junos-os.md`; HTTP 200; chars 9518
- [[SRX] Configuring Next-Generation Web Filtering on SRX Devices](https://supportportal.juniper.net/s/article/SRX-Configuring-Next-Generation-Web-Filtering-on-SRX-Devices) -> `source-srx-configuring-next-generation-web-filtering-on-srx-devices.md`; HTTP 200; chars 75 (limited extraction; do not rely on details not corroborated elsewhere)
- [Understanding Application Firewall Policies](https://www.juniper.net/documentation/us/en/software/nm-apps24.1/junos-space-security-director/topics/concept/junos-space-application-firewall-policies-overview.html) -> `source-understanding-application-firewall-policies.md`; HTTP 404; chars 13989 (limited extraction; do not rely on details not corroborated elsewhere)

## Later NGWF/EWF correction sources

- [Juniper NextGen Web Filtering Overview | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/utm/topics/concept/next-gen-juniper-url-filtering-overview.html) -> summarized in `ngwf-vs-ewf-research.md`; browser-rendered extraction; observed page date 03-Feb-26
- [request security utm web-filtering category migrate-to-ng-juniper | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/request-security-utm-web-filtering-category-migrate-to-ng-juniper.html) -> summarized in `ngwf-vs-ewf-research.md`; browser-rendered extraction; observed page date 11-Aug-25
- [Web Filtering Overview | Junos OS](https://www.juniper.net/documentation/us/en/software/junos/utm/topics/concept/utm-web-filtering-overview.html) -> summarized in `ngwf-vs-ewf-research.md`; browser-rendered extraction; observed page date 09-Nov-25
- [Juniper Support Portal KB98153: [SRX] Configuring Next-Generation Web Filtering on SRX Devices](https://supportportal.juniper.net/s/article/SRX-Configuring-Next-Generation-Web-Filtering-on-SRX-Devices) -> summarized in `ngwf-vs-ewf-research.md`; browser-rendered extraction; created / last updated 2025-05-01

## Extraction limitations

- The Security Director application-firewall overview URL and J-Web 23.2 web-filtering URL returned Juniper 404 pages during extraction; their article titles from the user-supplied reading list were preserved, but operational guidance was corroborated from other accessible Juniper/Junos and lab sources.
- The initial non-rendered extraction of the Juniper Support Portal next-generation web-filtering article returned a JavaScript shell with minimal text. Later browser-rendered extraction exposed the KB98153 article body; NGWF/EWF conclusions are captured in `ngwf-vs-ewf-research.md` and corroborated with official Juniper Junos documentation.
- The Reddit SecIntel thread was blocked by a JavaScript challenge; it was not used as authoritative guidance.
- `source-security-global-policies.md` was fetched as an additional official Juniper source because the user explicitly requested strong preference for `security policies global` in greenfield and vendor-migration work, and Juniper's main policy page links Global Policy Overview as related policy material.
