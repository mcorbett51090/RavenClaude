---
scenario_id: 2026-06-05-exactly-once-redesign
contributed_at: 2026-06-05
plugin: data-streaming-engineering
product: kafka
product_version: "3.6"
scope: likely-general
tags: [exactly-once, at-least-once, idempotent-consumer, transactions, end-to-end]
confidence: high
reviewed: false
---

## Problem

A team had configured Kafka's exactly-once semantics (EOS) — `processing.guarantee=exactly_once_v2` on a Kafka Streams app, transactional producer, `isolation.level=read_committed` on consumers — and still saw duplicate rows in their downstream Postgres analytics table after a broker failover. The owner's mental model was "we turned on exactly-once, so duplicates are impossible." Throughput had also dropped ~25% versus the prior at-least-once setup, and a stakeholder was asking whether the EOS complexity was paying for itself.

## Constraints context

- The pipeline was: source topic → Kafka Streams aggregation (EOS) → sink topic → a **custom consumer that did a plain `INSERT` into Postgres** and then committed offsets.
- The Postgres sink was **not** part of any Kafka transaction — it was a separate consumer outside the Streams EOS boundary.
- The business requirement was "no double-counting in the analytics table," interpreted as "we need exactly-once everywhere."

## Attempts

- Tried: **double-checking the EOS config** (idempotent producer `enable.idempotence=true`, `transactional.id` set, `read_committed`). All correct — and EOS *was* holding inside Kafka. The duplicates were not coming from the Kafka hops.
- Tried: **raising the transaction timeout / tuning the transactional coordinator**, on the theory that the failover left a hanging transaction. Didn't change the duplicate count — because the duplicates were created *after* the data left Kafka's transactional boundary, in the plain-`INSERT` sink.
- Tried: **making the Postgres sink idempotent with an upsert keyed on the event id** (`INSERT ... ON CONFLICT (event_id) DO NOTHING`) and committing the Kafka offset only after the upsert succeeded. This is the resolution — duplicates stopped, and the team could *downgrade* the over-applied EOS where it wasn't buying anything.

## Resolution

**Exactly-once is end-to-end or it's nothing — Kafka's EOS only covers Kafka-to-Kafka hops; the moment data crosses into a non-transactional sink, you re-enter at-least-once and need an idempotent write there.** "We turned on exactly_once_v2" guarantees no duplicates *within the Streams topology and its Kafka output*, not in a Postgres table written by a separate consumer.

1. **Trace the guarantee hop by hop, name where it actually holds.** EOS held source→Streams→sink-topic. The sink-topic→Postgres hop was a separate consumer doing a non-transactional `INSERT` — that hop was at-least-once, and a redelivery after a failover (offset committed but insert replayed, or insert done but offset not yet committed) produced the duplicate. The guarantee is only as strong as its weakest hop.
2. **Make the boundary-crossing write idempotent instead of chasing transactional purity.** A unique constraint on the event id + an upsert (`ON CONFLICT DO NOTHING`) makes a redelivered message a safe no-op. This is cheaper and more robust than trying to enrol Postgres in a Kafka transaction (which Kafka can't do natively — only a Kafka-Connect sink with its own delivery contract, or a two-phase pattern, gets you transactional sink writes).
3. **Right-size EOS to where it earns its 25% throughput cost.** EOS adds transaction-coordinator round-trips and read-committed buffering. Where the downstream is *already* idempotent (the upsert), at-least-once + idempotent consumer gives the same correctness for more throughput. The team kept EOS on the aggregation hop (where a duplicate would corrupt a running sum) and relied on the idempotent sink for the database hop.
4. **Pick the weakest semantic that meets the requirement per hop, not one global setting.** The requirement was "no double-counting in the analytics table" — satisfiable with an idempotent sink — not "exactly-once on every wire." Conflating the two bought complexity and a throughput tax for a guarantee that still leaked at the un-transactional boundary.

The trap is treating exactly-once as a switch you flip globally rather than a property you have to establish at every hop. A transactional Kafka core with a naive sink is at-least-once end-to-end — the duplicate just moves to the last mile.

**Action for the next engineer:** when someone reports duplicates "even though exactly-once is on," draw the pipeline and find the first hop that leaves Kafka's transactional boundary — that's where the duplicate is born. Fix it with an idempotent (keyed-upsert) write at that boundary, and only pay for EOS on the hops where a duplicate genuinely corrupts state. Don't assume `exactly_once_v2` covers a sink it has no transactional reach into.

Cross-reference: complements [`../best-practices/exactly-once-is-end-to-end-or-nothing.md`](../best-practices/exactly-once-is-end-to-end-or-nothing.md), [`../best-practices/choose-delivery-semantics-deliberately.md`](../best-practices/choose-delivery-semantics-deliberately.md), [`../best-practices/idempotent-consumers-and-a-dlq.md`](../best-practices/idempotent-consumers-and-a-dlq.md), and the [`../knowledge/data-streaming-engineering-decision-trees.md`](../knowledge/data-streaming-engineering-decision-trees.md) `## Decision Tree: Delivery semantics`. The downstream DB schema/constraint → `database-engineering`; the SLOs → `observability-sre`.
