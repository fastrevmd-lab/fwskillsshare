# Inspired by: Large-scale Source NAT

Source: Maxim Tveritnev, Juniper Community discussion
URL: https://community.juniper.net/discussion/source-nat-part-3-large-scale-configuration-design-and-lab-demo-using-juniper-srx
Retrieved: 2026-05-15

This independently authored note captures scale questions raised by the lab. It
does not reproduce the original post.

## Design takeaways

- Large-scale NAT is a capacity system: public addresses, ports, sessions, logging
  throughput, timeout policy, and failure headroom must be modeled together.
- Port block allocation can reduce logging volume and make attribution easier,
  but block size and allocation behavior trade efficiency for predictability.
- Paired or persistent allocation can help applications that expect stable public
  identity while concentrating load on fewer pool addresses.
- Sharing public ranges among source, destination, and static NAT requires explicit
  non-overlap and routing design; do not assume the allocator prevents ambiguity.
- Feature limits and offload behavior vary by platform and Junos release.

## Verification implications

Track pool utilization, port-block consumption, allocation failures, session rate,
recycle time, and log loss. Exercise peak load and failover, then confirm that an
operator can map a translated tuple and timestamp back to the originating client.
