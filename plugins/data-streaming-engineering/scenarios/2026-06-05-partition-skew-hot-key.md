---
scenario_id: 2026-06-05-partition-skew-hot-key
contributed_at: 2026-06-05
plugin: data-streaming-engineering
product: kafka
product_version: "3.6"
scope: likely-general
tags: [partition-skew, hot-key, keying, parallelism, ordering]
confidence: medium
reviewed: false
---

## Problem

A topic with 24 partitions and 12 consumers had one consumer pinned at 100% CPU with growing lag while the other 11 sat nearly idle. Aggregate throughput was a fraction of what the partition count should support. The topic was keyed by `tenant_id`, and one enterprise tenant produced ~60% of all traffic — every one of that tenant's events hashed to the same partition, so a single partition (and the single consumer that owned it) carried the majority of the load. Adding consumers did nothing: the hot partition can only be consumed by one consumer in the group.

## Constraints context

- Per-tenant ordering was a stated requirement ("events for a tenant must be processed in order"), which is why `tenant_id` was the partition key in the first place — a defensible original choice.
- Traffic was heavily skewed: a power-law tenant distribution where the top tenant dwarfed the rest (a classic hot key). The key choice was made when tenants were roughly equal-sized; the distribution drifted.
- Repartitioning a live topic is disruptive (changes key→partition mapping, breaks in-flight ordering), so the team was reluctant to just "add partitions."

## Attempts

- Tried: **adding consumers** (12 → 20). No effect — parallelism is capped at the partition count *and*, more bindingly, the hot partition is owned by exactly one consumer regardless of group size. The idle consumers couldn't take work off the hot one.
- Tried: **adding partitions** (24 → 48). Marginally helped the non-hot tenants but the hot tenant's events *still all hashed to one (new) partition* — same key, same hash, same single destination. More partitions doesn't split a single key; it only spreads *distinct* keys wider.
- Tried: **a composite key for the hot tenant** (`tenant_id` + a bounded sub-key) so its events spread across N partitions, while preserving the *required* ordering granularity. This is the resolution — the load spread and the real ordering requirement was re-examined and met at the right granularity.

## Resolution

**A hot key is a keying problem, not a scaling problem — order is per-partition, so a single key is a single partition is a single consumer, and no amount of partitions or consumers splits it.** Partitioning trades off ordering against parallelism, and a skewed key distribution collapses the parallelism for the hot key entirely.

1. **Diagnose skew before scaling.** Per-partition lag and per-partition byte/message rate (not just aggregate) reveal a hot partition immediately. "One consumer hot, rest idle, lag on one partition" is the signature. Scaling consumers/partitions is the wrong reflex — it can't move work off a single-key partition.
2. **Re-examine the *actual* ordering granularity required.** "Per-tenant order" was the stated need, but the real requirement was usually narrower — per *entity* within the tenant (per-account, per-session, per-order). If ordering is truly needed only per sub-entity, key by `tenant_id:entity_id`, which spreads a big tenant across many partitions while preserving the ordering that actually matters. Over-broad keys are the usual root cause.
3. **Salt the hot key when sub-key ordering genuinely isn't needed.** If the hot tenant truly has no finer ordering requirement, append a bounded salt (`tenant_id:{0..N}`) to spread its events across N partitions, and have the consumer side merge/aggregate accounting for the split. This explicitly *gives up* whole-tenant ordering for that tenant in exchange for parallelism — a deliberate trade, documented, not accidental.
4. **Size partitions for the *skewed* throughput, and pick the key for the ordering you actually need.** The partition key is hard to change later (it remaps everything and breaks in-flight order), so choose it for the genuine ordering granularity up front and size partition count for the busiest key's throughput, not the average.

The trap is reading a hot-partition problem as an under-provisioning problem. More consumers than the partition count is wasted; more partitions spreads *distinct* keys but never splits a *single* hot key. The lever is the key, chosen at the ordering granularity the business actually requires.

**Action for the next engineer:** if one consumer is hot while the rest idle, check *per-partition* lag/rate for a hot partition before touching consumer or partition count. Then ask what ordering is *truly* required — usually a finer granularity than the current key — and re-key to spread the hot key across partitions while preserving the real ordering need. Salt only when no sub-key ordering is needed, and document the ordering you traded away.

Cross-reference: complements [`../best-practices/partition-for-ordering-and-parallelism.md`](../best-practices/partition-for-ordering-and-parallelism.md), [`../best-practices/size-partitions-for-throughput-targets.md`](../best-practices/size-partitions-for-throughput-targets.md), the [`2026-06-05-consumer-lag-rebalance-storm.md`](2026-06-05-consumer-lag-rebalance-storm.md) scenario (the other "lag is climbing" pattern, with a different root cause), and the [`../knowledge/data-streaming-engineering-decision-trees.md`](../knowledge/data-streaming-engineering-decision-trees.md). The downstream merge/aggregation of a salted key → `stream-processing-engineer`.
