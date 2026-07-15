# Inspired by: DHCP on MNHA: Back to Basics

- **Author:** James Rathbun
- **Publisher:** Juniper Community TechPost
- **Source:** https://community.juniper.net/blogs/james-rathbun/2026/04/22/dhcp-on-mnha-back-to-basics
- **Retrieved:** 2026-05-14
- **Use in this skill:** Informs the DHCP relay preference and the safeguards
  for node-local DHCP in default-gateway or hybrid MNHA designs.

## Original summary

MNHA nodes keep independent control planes and configurations. The article
reports that, on the tested Junos 25.4R1 design, each node also maintains an
independent DHCP process and lease database. It does not assume that DHCP lease
state is synchronized through MNHA runtime-object synchronization.

The conservative design is to relay client requests through the MNHA gateway to
an external redundant DHCP service. That keeps lease ownership outside the SRX
pair while MNHA protects the client gateway path.

If the SRX nodes must serve addresses locally, avoid overlapping allocation
ranges. Give each node a distinct pool and node-local server identifier so both
nodes cannot offer the same address. Keep common subnet options aligned, then
test renew, rebind, node failure, and failback behavior. This sacrifices one
shared lease database in favor of deterministic ownership.

## Verification implications

- Treat non-synchronized lease behavior as a release-specific field
  observation until it is confirmed for the target Junos image.
- Verify whether both nodes receive broadcasts and can answer while their
  relevant SRG is active or backup.
- Capture the DHCP exchange during steady state, node failure, and recovery.
- Confirm that relay next hops and return routes remain reachable through the
  surviving node.
- Do not use overlapping local pools unless current Juniper documentation
  explicitly describes safe synchronization behavior for the target release.

This repository contains this independently written note and a source link, not
the TechPost text or its diagrams/configuration transcript.
