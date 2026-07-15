# Inspired by: ATP Appliance and SRX Integration

Source: Juniper Networks, ATP Appliance documentation
URL: https://www.juniper.net/documentation/us/en/software/atp-appliance/atp-appliance-srx-integration/topics/concept/atp-appliance-srx-integration-overview.html
Retrieved: 2026-05-15

This independently authored integration note does not reproduce the source.

## Design takeaways

- Treat SRX enforcement, telemetry export, ATP analysis, and management connectivity
  as separate dependencies with separately testable failure modes.
- Confirm product generation, supported Junos release, licenses, certificates, time
  synchronization, routing, and policy attachment before designing enforcement.
- Define fail-open or fail-closed behavior and the operator response to unreachable,
  delayed, or inconclusive verdicts.

Verify device registration, healthy channels, sample event flow, enforcement-policy
hits, logs, and recovery after the analysis service is unavailable.
