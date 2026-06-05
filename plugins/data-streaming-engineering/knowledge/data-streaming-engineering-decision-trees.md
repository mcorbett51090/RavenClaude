# Data Streaming — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before building a stream or choosing delivery semantics.

## Decision Tree: Streaming or batch?

Justify streaming with a real latency need; otherwise batch is simpler and cheaper.

```mermaid
graph TD
  A[A data need] --> B{Sub-minute reaction required?}
  B -- No, hourly/daily is fine --> C[Batch ELT -> data-platform]
  B -- Yes --> D{Continuous unbounded events?}
  D -- No, periodic snapshots --> C
  D -- Yes --> E[Streaming justified]
  E --> F{Source is a database?}
  F -- Yes --> G[CDC: Debezium + outbox - NOT dual-writes]
  F -- No, app/IoT events --> H[Produce to topics, keyed for ordering]
```

_Streaming is operationally heavy — don't pay for it without a latency need._

## Decision Tree: Delivery semantics

Pick the weakest semantic that meets the requirement; stronger costs throughput + complexity.

```mermaid
graph TD
  A[A pipeline hop] --> B{Can the consumer be made idempotent?}
  B -- Yes --> C[At-least-once + idempotent consumer - pragmatic default]
  B -- No --> D{Does the sink support transactions?}
  D -- Yes --> E[Exactly-once end-to-end - accept the throughput cost]
  D -- No --> F[At-least-once + dedup at the sink / accept duplicates]
  C --> G[Commit offsets AFTER processing]
  E --> G
```


## Decision Tree: Which window type?

The window type is the analytical question; pick it from the question, not by habit.

```mermaid
graph TD
  A[A windowed aggregation] --> B{Is the boundary driven by user activity gaps?}
  B -- Yes, sessionize by inactivity --> C[Session window: gap timeout closes it]
  B -- No --> D{Do consecutive results need to overlap / slide?}
  D -- Yes, rolling/moving metric --> E[Sliding window: size + slide interval]
  D -- No, fixed non-overlapping buckets --> F{Need a result per fixed period e.g. per minute?}
  F -- Yes --> G[Tumbling window: each event in exactly one window]
  F -- No, per-key count/volume threshold --> H[Count/global window with trigger]
  C --> I[All on event-time + watermark + a late-data policy]
  E --> I
  G --> I
```

_Sliding windows multiply state (each event in many windows) — bound it. Every window runs on event-time with a watermark and an explicit late-data policy._

## Decision Tree: Which schema-compatibility mode?

Compatibility mode is a contract about who can deploy first; choose by upgrade order.

```mermaid
graph TD
  A[Evolving an event schema] --> B{Who upgrades first?}
  B -- Consumers before producers --> C[BACKWARD: new schema reads old data - safe to add optional fields]
  B -- Producers before consumers --> D[FORWARD: old schema reads new data - safe to add then drop later]
  B -- Either order / mixed fleet --> E[FULL: both directions - most constrained, additive-only]
  A --> F{Breaking change unavoidable e.g. rename, type change?}
  F -- Yes --> G[New topic/version + dual-write window + migrate consumers, NOT in place]
  C --> H[Register + enforce in the registry; CI-check before deploy]
  D --> H
  E --> H
```

_An unversioned payload is a future cross-team outage. A genuinely breaking change is a new topic + migration, never a silent in-place edit._

## Decision Tree: How do I reprocess / recover?

Match the recovery mechanism to what you're fixing; idempotent consumers make all of these safe.

```mermaid
graph TD
  A[Need to reprocess data] --> B{Rebuilding current state e.g. a new cache/materialized view?}
  B -- Yes --> C{Source topic is log-compacted changelog?}
  C -- Yes --> D[Replay from compacted topic - latest value per key]
  C -- No --> E[Replay from earliest within retention OR rebuild from system of record]
  B -- No --> F{Fixing a processing bug retroactively?}
  F -- Yes --> G{History still within retention?}
  G -- Yes --> H[Reset offsets to the window, reprocess with idempotent consumer]
  G -- No --> I[Backfill from the source of record / warehouse]
  F -- No, onboarding a new consumer --> J[Read from earliest; ensure idempotent so it doesn't double-apply]
```

_Replay is a design constraint: it needs retention to cover the window, idempotent consumers, and an offset-reset plan that won't corrupt live state._

## Decision Tree: CDC connector failure — what broke and how to recover?

**When this applies:** a Debezium CDC connector fails, lags, or produces wrong/missing events. Observable inputs: the connector's status (RUNNING / PAUSED / FAILED), whether the WAL position is still available, and the type of failure (auth, schema change, WAL rotation).

**Last verified:** 2026-06-05 against Debezium 2.x documentation and Kafka Connect error handling docs.

```mermaid
flowchart TD
    START[CDC connector failed or lagging] --> Q1{Is the connector status FAILED?}
    Q1 -->|YES| Q2{What error class?}
    Q1 -->|NO - RUNNING but lagging| LAG[Consumer lag - check broker + network + Debezium throughput config]
    Q2 -->|Auth or permissions - cannot read WAL| AUTH[Fix DB permissions - grant replication role - restart connector]
    Q2 -->|Schema change - table added/dropped/altered| SCHEMA{Type of change?}
    SCHEMA -->|Column added - backward compatible| EVOLVE[Update schema registry - set BACKWARD mode - restart connector]
    SCHEMA -->|Column dropped or type changed - breaking| NEWSNAP[Re-snapshot the affected table - new topic version if breaking]
    Q2 -->|WAL position expired - slot advanced past retention| RESNAP[Full re-snapshot required - old WAL offset gone - no incremental recovery]
    Q2 -->|Connector config error| CONFIG[Fix the config - validate with connector API - restart]
    AUTH --> VERIFY[Verify events flowing on the target topic]
    EVOLVE --> VERIFY
    NEWSNAP --> VERIFY
    RESNAP --> VERIFY
    CONFIG --> VERIFY
    LAG --> TUNE[Tune max.batch.size + max.queue.size + poll.interval.ms]
```

**Rationale per leaf:**
- *AUTH* — the Debezium connector needs the `REPLICATION` privilege on Postgres; a permissions revocation (common after a DB rotation) is the most common auth failure.
- *EVOLVE* — an additive schema change is backward-compatible; update the registry and restart. Do not re-snapshot for an additive change.
- *NEWSNAP* — a breaking column change (type change, drop) requires a re-snapshot of the affected table; if the topic has existing consumers, this is the new-topic migration path.
- *RESNAP* — the WAL replication slot retains data only while it is consumed; if the connector was paused too long, the WAL offset has advanced past what the slot retained and a full re-snapshot is the only recovery. This is expensive — set `max.slot.wal.keep.size` to prevent silent slot growth.
- *LAG* — a RUNNING but lagging connector is usually a throughput tuning issue (batch size, polling interval, or broker I/O).

**Tradeoffs summary:**

| Failure class | Recovery | Data gap risk | Cost |
|---|---|---|---|
| Auth / permissions | Restart after fix | None if done promptly | Low |
| Additive schema change | Update registry + restart | None | Low |
| Breaking schema change | Re-snapshot | Window gap during snapshot | Medium |
| WAL slot expired | Full re-snapshot | Gap from last good event | High |
| Config error | Fix + restart | Minimal | Low |

---

## Decision Tree: Kafka platform — self-hosted vs managed?

**When this applies:** a new Kafka cluster is being provisioned, or an existing self-hosted cluster is being evaluated for migration to a managed service. Observable inputs: team ops capacity, cloud provider, required Kafka features, and engagement duration.

**Last verified:** 2026-06-05 against Confluent Cloud, MSK (Amazon), and Aiven documentation.

```mermaid
flowchart TD
    START[Kafka cluster needed] --> Q1{Is this a short engagement - under 6 months?}
    Q1 -->|YES| MANAGED[Managed service - Confluent Cloud or MSK or Aiven - no ops setup time]
    Q1 -->|NO long-running| Q2{Does the team have dedicated Kafka ops capacity?}
    Q2 -->|NO - small team| MANAGED
    Q2 -->|YES - ops engineer or SRE| Q3{Cloud-native Kafka features needed - Flink SQL/Tableflow/Connect?}
    Q3 -->|YES| CONFLUENT[Confluent Cloud - managed Kafka + Flink + Connect + Schema Registry]
    Q3 -->|NO - basic Kafka only| Q4{AWS-primary infrastructure?}
    Q4 -->|YES| MSK[Amazon MSK - managed Kafka - good VPC integration + IAM]
    Q4 -->|NO GCP/Azure/multi-cloud| Q5{Cost is primary constraint?}
    Q5 -->|YES open-source first| SELFHOST[Self-hosted Kafka on KRaft - no ZooKeeper - but size and patch burden]
    Q5 -->|NO vendor support matters| AIVEN[Aiven for Apache Kafka - multi-cloud managed - good for non-AWS]
```

**Rationale per leaf:**
- *MANAGED* — for short engagements or small teams, the ops burden of self-hosted Kafka (cluster sizing, ZooKeeper/KRaft, JVM tuning, broker patching) costs more time than the managed service costs money.
- *CONFLUENT* — when Flink SQL, managed connectors, and the full streaming platform are needed, Confluent Cloud is the only fully-integrated option.
- *MSK* — AWS-native integration (VPC, IAM, CloudWatch) makes MSK the lowest-friction managed Kafka on AWS; no Flink or Schema Registry included (add Confluent Schema Registry separately if needed).
- *SELFHOST* — a team with dedicated ops capacity and a long-running workload can run KRaft-mode Kafka without ZooKeeper; the cost savings are real but the ops burden (broker failures, rebalances, upgrades) is the team's responsibility.
- *AIVEN* — good multi-cloud managed option for non-AWS shops; includes Schema Registry.

**Tradeoffs summary:**

| Option | Monthly cost | Ops burden | Schema Registry | Flink / Connect | Use when |
|---|---|---|---|---|---|
| Confluent Cloud | Higher | None | Included | Managed | Full streaming platform + ops convenience |
| Amazon MSK | Medium | Low | Not included | Partial | AWS-native + cost-conscious |
| Aiven | Medium | None | Included | No | Multi-cloud managed |
| Self-hosted KRaft | Infra only | High | Deploy separately | Deploy separately | Long-running + ops capacity available |

---

## Decision Tree: Stream-stream join — can these two streams be joined?

**When this applies:** a stream processing pipeline needs to join two event streams (e.g., orders + payments, clicks + impressions) and you must choose whether a stream-stream join is feasible and what join window to use. Observable inputs: the expected time skew between correlated events on the two streams, the cardinality (how many events per join key), and whether late arrivals are common.

**Last verified:** 2026-06-05 against Apache Flink 1.19 and Kafka Streams 3.7 join documentation.

```mermaid
flowchart TD
    START[Join two event streams] --> Q1{Do correlated events arrive within a bounded time window?}
    Q1 -->|NO or unknown delay| ENRICH[Consider stream-table join instead - one side is a slowly-changing lookup]
    Q1 -->|YES bounded window| Q2{What is the expected max delay between correlated events?}
    Q2 -->|Seconds - same transaction| INTERVAL[Flink interval join - e.g. orders joins payments within -5s to +30s]
    Q2 -->|Minutes - async correlation| WINDOW[Flink window join - tumbling or sliding window covering the delay]
    Q2 -->|Hours or days - slow correlation| ENRICH
    INTERVAL --> Q3{Can late arrivals fall outside the join window?}
    Q3 -->|YES - late events common| SIDE[Add side output for unmatched events - audit late joins]
    Q3 -->|NO - window is generous enough| SHIP[Ship the join with the interval bounds]
    WINDOW --> STATE[Bound the window state with TTL - window size + buffer]
    ENRICH --> KTABLE[Stream-table join - one stream enriches with a KTable or broadcast state]
```

**Rationale per leaf:**
- *ENRICH* — when the two streams don't have a bounded time correlation, a stream-stream join is the wrong model; one side is likely a slowly-changing lookup (a customer dim, a product catalog) that should be a KTable or broadcast state.
- *INTERVAL* — Flink's interval join is the correct model when events correlate within a predictable time window (an order payment typically arrives within seconds to minutes of the order event).
- *WINDOW* — when the delay is known but wider (minutes), a windowed join covers the window; be careful about state size (every event is buffered for the full window duration per key).
- *SIDE* — unmatched events in a join window are a real-world occurrence (a payment for a cancelled order, a late-arriving click); route them to a side output for auditing rather than silently dropping them.
- *KTABLE* — for one-sided lookup enrichment (enrich an order event with the customer's tier), a stream-table join is cheaper and correct; the table side doesn't need a time window.
- *STATE* — window joins buffer both sides; bound the state with TTL equal to the join window plus a buffer, or the state grows unboundedly for high-cardinality keys.

**Tradeoffs summary:**

| Join type | State size | Late arrival handling | Use when |
|---|---|---|---|
| Interval join (Flink) | Bounded by interval | Side output for outliers | Correlated events within seconds-minutes |
| Window join (Flink) | Bounded by window | Events outside window dropped | Correlated events within minutes, fixed period |
| Stream-table join (KTable) | Table side only | Table is updated-in-place | One side is a slowly-changing lookup |
| Broadcast state join | Broadcast side only | n/a | Small lookup replicated to all partitions |

---

## Decision Tree: A processor is falling behind — backpressure vs. skew vs. under-provisioning?

**When this applies:** a stream processor's lag is growing (or its source is buffering), throughput is below target, and you must decide whether the fix is backpressure handling, re-keying, scaling, or bounding state. Observable inputs: whether lag is on *one* partition/task or *all*, whether an external sink/call is in the hot path, and whether state size is growing unbounded.

**Last verified:** 2026-06-05 against Apache Flink 1.19 (backpressure monitoring / network stack) and Kafka consumer-group documentation. Re-confirm tuning specifics at use.

```mermaid
flowchart TD
    START[Processor lag growing or source buffering] --> Q1{Is lag concentrated on ONE partition/task, rest idle?}
    Q1 -->|YES - one hot| SKEW[Hot key / partition skew - re-key at the real ordering granularity, do NOT add consumers - see partition-skew scenario]
    Q1 -->|NO - all tasks busy and behind| Q2{Is a slow external call or sink in the processing hot path?}
    Q2 -->|YES - sync DB/HTTP per record| OFFPATH[Get slow I/O off the critical path: batch, async, or a bounded worker pool - the call rate, not CPU, is the bottleneck]
    Q2 -->|NO - CPU/throughput bound| Q3{Is downstream the bottleneck - sink/next stage slower than source?}
    Q3 -->|YES - fast producer, slow consumer| BACKPRESSURE{Does the framework propagate backpressure end-to-end?}
    BACKPRESSURE -->|YES - Flink credit-based / reactive| ABSORB[Let backpressure throttle the source; bound buffers; alarm on sustained backpressure - it signals a real capacity gap]
    BACKPRESSURE -->|NO - manual pull loop / unbounded queue| BOUND[Bound the in-flight buffer + apply explicit backpressure: pause poll / block produce - never an unbounded queue - OOM risk]
    Q3 -->|NO - genuinely under-provisioned| Q4{At or below the partition/parallelism ceiling?}
    Q4 -->|Below ceiling| SCALE[Add parallelism up to the partition count - then add partitions if you need more, re-checking keying]
    Q4 -->|At ceiling already| REPARTITION[Add partitions AND raise parallelism together - re-verify the key isn't hot first]
    SKEW --> VERIFY[Re-measure per-partition lag after the change]
    OFFPATH --> VERIFY
    ABSORB --> VERIFY
    BOUND --> VERIFY
    SCALE --> VERIFY
    REPARTITION --> VERIFY
```

**Rationale per leaf:**
- *SKEW* — one hot task with the rest idle is a keying problem, not a capacity problem; scaling can't move work off a single-key partition (see the `partition-skew-hot-key` scenario).
- *OFFPATH* — a multi-second synchronous downstream call per record caps throughput at the call rate and (in a poll loop) trips `max.poll.interval.ms` rebalances; batch/async it or hand to a bounded worker pool.
- *ABSORB* — Flink's credit-based flow control propagates backpressure to the source automatically; sustained backpressure is a real signal to provision more, not something to hide. Alarm on it.
- *BOUND* — a hand-rolled consumer with an unbounded internal queue turns a producer surge into an OOM; bound the buffer and apply explicit backpressure (pause the poll / block the produce). Never let the queue grow without limit.
- *SCALE / REPARTITION* — only after ruling out skew and backpressure is the answer "more capacity," and parallelism is capped at the partition count, so the two move together.

**Tradeoffs summary:**

| Symptom | Root cause | Fix | What does NOT help |
|---|---|---|---|
| One task hot, rest idle | Hot key / skew | Re-key at real ordering granularity | Adding consumers/partitions |
| All tasks behind, slow per-record I/O | Sync call in hot path | Batch / async / worker pool | More CPU/tasks |
| Fast source, slow sink, buffers filling | Downstream bottleneck | Propagate/apply backpressure; bound buffers | Bigger unbounded queue |
| All tasks at ceiling, no skew | Under-provisioned | Add partitions + parallelism together | Re-keying |

---

## Decision Tree: Stateful recovery — how do I size and restore operator state?

**When this applies:** a stateful processor (windowed aggregation, join, dedup store) needs a recovery and state-sizing strategy — choosing checkpoint/state-store config, the state backend, and how state is restored after a crash or rescale. Observable inputs: state size relative to memory, whether keys live forever or expire, the tolerable recovery time, and whether you ever rescale parallelism.

**Last verified:** 2026-06-05 against Apache Flink 1.19 (checkpoints/savepoints, RocksDB state backend, state TTL) and Kafka Streams 3.7 (changelog topics, standby replicas). Re-confirm backend/TTL specifics at use.

```mermaid
flowchart TD
    START[Stateful operator needs a recovery plan] --> Q1{Does state grow without a natural bound - per-key, forever?}
    Q1 -->|YES - unbounded keyspace| TTL[Set state TTL / retention so dead keys expire - unbounded state is a future OOM, NOT a recovery problem to solve later]
    Q1 -->|NO - bounded or windowed| Q2{Does state fit comfortably in heap/memory?}
    TTL --> Q2
    Q2 -->|YES - small state| HEAP[In-memory / heap state backend - fast, simple; checkpoint to durable store]
    Q2 -->|NO - large state, GBs+| ROCKS[Disk-spilling backend - Flink RocksDB / Kafka Streams RocksDB - state exceeds memory, incremental checkpoints]
    HEAP --> Q3{What recovery-time objective?}
    ROCKS --> Q3
    Q3 -->|Fast failover needed| STANDBY[Standby replicas / local recovery - Flink local recovery, Kafka Streams num.standby.replicas - avoid full changelog replay]
    Q3 -->|Minutes acceptable| RESTORE[Restore from latest checkpoint / replay changelog topic - simpler, cheaper, slower]
    STANDBY --> Q4{Do you ever rescale parallelism?}
    RESTORE --> Q4
    Q4 -->|YES - change task/partition count| SAVEPOINT[Use savepoints + key-group/keyed state so state redistributes on rescale - a plain checkpoint may not rescale cleanly]
    Q4 -->|NO - fixed parallelism| CHECKPOINT[Periodic checkpoints sized so a checkpoint completes well within the interval - tune interval vs. recovery cost]
```

**Rationale per leaf:**
- *TTL* — the most common stateful-streaming outage is unbounded state (a dedup/aggregation keyed on an ever-growing keyspace) silently filling disk/heap. Set TTL/retention *first*; it's a sizing decision, not a recovery afterthought.
- *HEAP vs ROCKS* — small, bounded state runs fastest in memory; large state (GBs) needs a disk-spilling backend (RocksDB) with incremental checkpoints so a checkpoint doesn't snapshot the whole state every time.
- *STANDBY vs RESTORE* — standby replicas / local recovery cut failover from "replay the whole changelog" to "promote a warm copy," at the cost of extra resources; a generous RTO can just restore from the last checkpoint / replay the changelog.
- *SAVEPOINT vs CHECKPOINT* — if you ever change parallelism, you need savepoints + properly key-grouped state so state redistributes across the new task count; a checkpoint tuned only for crash recovery may not rescale cleanly.

**Tradeoffs summary:**

| Choice | When | Cost | Recovery profile |
|---|---|---|---|
| State TTL / retention | Always, if keyspace is unbounded | A correctness decision (when can a key be forgotten) | Prevents OOM; not a recovery feature per se |
| Heap state backend | Small bounded state | Limited by memory | Fast, full-snapshot checkpoints |
| RocksDB state backend | Large state (GBs+) | Disk I/O, tuning | Incremental checkpoints, slower per-key access |
| Standby replicas / local recovery | Tight RTO | Extra memory/disk for the replica | Fast failover, no full replay |
| Savepoints | You rescale or upgrade | Manual trigger, larger artifact | Portable, rescale-safe |

---

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Apache Kafka | GA, ecosystem default | KRaft (no ZooKeeper) standard |
| Schema Registry (Avro/Protobuf/JSON) | GA | Compatibility rules essential |
| Debezium CDC | GA | Log-based change capture |
| Apache Flink | GA | Event-time, watermarks, exactly-once |
| Kafka Streams | GA | JVM library; stateful processing |
| Kafka transactions / EOS | GA | Exactly-once within Kafka; sink matters |
| Pulsar / Kinesis | GA | Multi-tenant / AWS-managed alternatives |
