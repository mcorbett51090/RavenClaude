# RPO and RTO drive the topology — not the other way around

Reliability architecture starts from two numbers: how much data can you lose (RPO)
and how long can you be down (RTO). Everything downstream — sync vs async
replication, single-AZ vs multi-AZ vs multi-region, automatic vs manual failover,
backup cadence, warm-standby vs restore-from-storage — is *derived* from those
targets. An architecture chosen before the targets are stated is a guess dressed up
as a design.

**Do:** get an explicit RPO and RTO from the business first; then trace the topology
and backup trees from them; and name the cost of each guarantee (sync replication
buys RPO with write latency; multi-region buys region-survival with cost and
complexity).

**Don't:** copy a topology from another system, or over-engineer to zero-RPO/zero-RTO
everywhere. Five-nines for a system that can tolerate an hour of downtime is wasted
money and complexity that itself reduces reliability.

**Flag:** any HA or backup design presented without a stated RPO and RTO, or a
guarantee (sync, multi-region, automatic failover) whose cost hasn't been named
against the target that justifies it.
