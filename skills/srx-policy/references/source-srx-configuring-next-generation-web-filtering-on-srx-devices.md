# Inspired by: Configuring Next-Generation Web Filtering on SRX

Source: Juniper Support, KB98153
URL: https://supportportal.juniper.net/s/article/SRX-Configuring-Next-Generation-Web-Filtering-on-SRX-Devices
Retrieved: 2026-05-15

This independently written note does not reproduce the support article.

## Design takeaways

- Evaluate NGWF (`ng-juniper`) first for supported Junos 23.4R1+ greenfield and
  modernization work; confirm exact platform, release, and subscription support.
- Category action, fallback, UTM attachment, cloud reachability, and logging form one
  operational control and should be reviewed together.
- EWF-to-NGWF category migration is a managed change. Preserve policy names when the
  documented workflow requires it and plan for asynchronous processing and downtime.

Verify migration status, representative categories, unknown and lookup-failure paths,
policy/UTM counters, logs, and rollback before removing the prior service.
