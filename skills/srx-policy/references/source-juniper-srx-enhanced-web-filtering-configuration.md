# Inspired by: SRX Enhanced Web Filtering Configuration

Source: Rayka technical training page
URL: https://rayka-co.com/lesson/juniper-srx-enhanced-web-filtering-configuration/
Retrieved: 2026-05-15

This is an original operational checklist inspired by the lab. No upstream prose or
configuration is included.

## Design takeaways

- Web-filtering behavior spans the category profile, UTM policy, security-policy
  attachment, license, cloud lookup path, and logging destination.
- A permissive default category can silently defeat narrow block entries; document
  the intended action for each fallback state.
- Legacy examples may use EWF syntax. Evaluate NGWF for supported modern platforms
  and preserve EWF only where compatibility or estate constraints justify it.

Test known allow/block categories, uncategorized sites, cloud failure, HTTPS limits,
and log visibility. Inspect the committed hierarchy and live counters.
