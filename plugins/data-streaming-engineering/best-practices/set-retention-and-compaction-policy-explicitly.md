# Set retention and compaction policy explicitly on every topic

**Status:** Absolute rule
**Domain:** Kafka / topic lifecycle
**Applies to:** `data-streaming-engineering`

---

## Why this exists

Kafka's default retention is 7 days of log retention by time. A topic that silently exceeds this window without warning loses data that downstream consumers might need for replay or recovery. More critically, a topic used as a changelog (KTable state, CDC replay base) that is misconfigured as time-based retention will delete the history needed to rebuild consumer state. Conversely, a topic left with infinite retention (`-1`) grows unbounded and fills broker disk. Setting retention and compaction policy explicitly at topic creation — and documenting it in the runbook — is the only way to know what guarantee the topic makes.

## How to apply

**At topic creation time:**

```bash
# Time-series event log: 7-day retention, delete old segments
kafka-topics.sh --create --topic commerce.prod.order.placed \
  --config retention.ms=604800000 \           # 7 days
  --config cleanup.policy=delete

# Changelog / KTable base: compaction (keep latest value per key)
kafka-topics.sh --create --topic commerce.prod.order.state \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.1 \
  --config segment.ms=3600000                 # compact at least hourly

# Long-lived audit / replay buffer: 90-day retention
kafka-topics.sh --create --topic iam.prod.account.created \
  --config retention.ms=7776000000            # 90 days
```

**Document in the topic runbook:**
```markdown
## Topic: commerce.prod.order.placed
- Retention policy: 7 days (delete)
- Replay window: up to 7 days from last publish
- Recovery: within 7 days, reset consumer offsets; beyond 7 days, backfill from warehouse
```

**Do:**
- Set `retention.ms` (or `retention.bytes`) explicitly on every topic at creation.
- Use `compact` for topics that serve as the authoritative current-state source (KTable, CDC snapshot).
- Document the retention policy in the runbook so the team knows the recovery window.

**Don't:**
- Rely on Kafka's default retention without documenting it as an intentional choice.
- Use `retention.ms=-1` (infinite) on high-volume event topics — it fills broker disk silently.
- Mix `compact` and `delete` without understanding that `compact,delete` compacts first then deletes old compacted segments.

## Edge cases / when the rule does NOT apply

- Exactly-once transactional topics internal to Kafka (`__transaction_state`) follow platform defaults and are not managed by the application team.
- Short-lived ephemeral topics (used for a single pipeline test run) may use defaults, but must be explicitly cleaned up after the run.

## See also

- [`../agents/kafka-pipeline-engineer.md`](../agents/kafka-pipeline-engineer.md) — configures topic lifecycle at creation
- [`./design-a-replay-strategy.md`](./design-a-replay-strategy.md) — the replay rule that retention policy bounds

## Provenance

Apache Kafka documentation on log retention and compaction. Retention misconfiguration is one of the most common silent operational failures in production Kafka clusters. Codifies data-streaming-engineering CLAUDE.md §2 house opinion #5 ("Schemas evolve; govern them") as applied to the topic lifecycle dimension.

---

_Last reviewed: 2026-06-05 by `claude`_
