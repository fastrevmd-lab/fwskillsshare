# cSRX performance envelope

What "working" throughput looks like on a Proxmox/Docker cSRX stack, so a slow
number is not mistaken for a fault. Figures are from the reference build
(Proxmox VE 9.2.20, cSRX 26.2R1.7).

None of the gotchas in SKILL.md is "cSRX is slow" — deliberately.
Single-digit-Mbit/s TCP throughput on this stack is a **baseline, not a
fault**. A reader who measures a few Mbit/s and works through the gotchas
looking for a cause will most likely land on Gotcha 3 in SKILL.md
(`InCsumErrors`), find it already zero, and have nowhere left to go.

> **Sample size: one run per mode, on one build.** These figures come from a
> single `iperf3` run in each forwarding mode on a single cSRX release and host.
> Run-to-run variance was never measured, so treat them as an order-of-magnitude
> expectation — "single-digit Mbit/s, not Gbit/s" — rather than a number to
> compare against precisely. The *relative* finding (routing roughly 40x faster
> than secure-wire, with `CSRX_SIZE` and `CSRX_PACKET_DRIVER` held constant)
> is the durable part; the absolute figures are one data point each.
> `CSRX_PACKET_DRIVER=poll` and `dpdk` were never benchmarked, so the driver
> hypothesis for the residual gap remains untested.

**Observed** (`CSRX_SIZE=large`, `CSRX_PACKET_DRIVER=interrupt`, identical
across both runs):

| Forwarding mode | Sender bitrate | Retransmits | `InCsumErrors` |
|---|---|---|---|
| Secure-wire (L2 bump-in-the-wire) | 210 Kbit/s | 166 | 0 |
| Routing (L3, static routes) | 8.81 Mbit/s | 3192 | 0 |

Routing mode is roughly two orders of magnitude below line rate, and
secure-wire roughly four, on what is otherwise a local veth-chain path
with no physical link in it — and neither is a checksum-corruption symptom
(`InCsumErrors` is 0 in both).

**What the ~42x mode gap does and does not establish.** Holding `CSRX_SIZE`
and `CSRX_PACKET_DRIVER` constant isolates the forwarding path as the only
variable between the two runs: if sizing or the interrupt-mode packet driver
were the dominant bottleneck, both modes would be roughly equally slow, and
they are not — routing mode's flow-based L3 path (route lookup, TTL
decrement, a real policy/session lookup) outperforms secure-wire's raw
byte-splice forwarding by roughly 42x under otherwise identical settings.

**What is still unexplained — do not present this as solved.** Routing
mode's own 8.81 Mbit/s is itself far below what a local veth path should
sustain, with zero checksum errors and a congestion window pinned near its
floor for the full transfer. The leading hypothesis is
`CSRX_PACKET_DRIVER=interrupt` — a non-DPDK, userspace, per-packet driver
crossing several virtualization hops — but this is **partly explained, not
settled**: the packet driver was never varied against a DPDK/poll-mode
alternative here, so that theory was never isolated the way the mode
comparison was.

**Practical takeaway.** Single-digit Mbit/s in routing mode, or low hundreds
of Kbit/s in secure-wire, with `InCsumErrors` at 0, matches this baseline —
not a new bug. A number *below* this envelope, or a nonzero `InCsumErrors`,
is the actual signal worth investigating.
