---
scenario_id: 2026-06-05-replication-lag-stale-reads-after-failover
contributed_at: 2026-06-05
plugin: database-engineering
product: postgres
product_version: "15"
scope: likely-general
tags: [replication-lag, read-replica, failover, consistency, read-your-writes]
confidence: medium
reviewed: false
---

## Problem

After routing read traffic to a read replica to offload the primary, users started reporting "I saved it but it's gone" — a profile edit would succeed, then the very next page load showed the *old* value. Worse, during an unplanned failover (the primary died and a replica was promoted), a few seconds of recently-committed transactions appeared to vanish. Two faces of one root cause: reads served from a replica that is **seconds behind** the primary, and a failover that promoted a replica which hadn't yet received the most recent writes.

## Constraints context

- One primary, two async streaming replicas; reads load-balanced across replicas to cut primary CPU.
- Async replication (the default) — the primary does **not** wait for replicas to confirm before committing, so the replica is always some lag behind.
- The app did "write to primary, then immediately read" in the same user flow (the classic read-your-writes pattern), and the read landed on a lagging replica.
- Failover was automated (a managed-DB HA setup) and promoted whichever replica was healthy, not necessarily the most caught-up one.

## Attempts

- Tried: routing *all* reads back to the primary. Fixed the staleness instantly — and re-created the CPU saturation that motivated replicas in the first place. Correct but throws away the benefit; not the answer.
- Tried: lowering the app's replica-lag tolerance by polling `pg_stat_replication` lag and only using replicas under N ms. Helped for steady state but didn't solve read-your-writes (even 50 ms of lag loses a just-committed write) and didn't help the failover data-loss case at all.
- Tried (the working split): **route by freshness requirement, not by reflex.** Reads that must reflect the user's own just-made write → primary (or pinned to the replica's LSN). Reads that tolerate seconds of staleness (lists, dashboards, search) → replicas. And separately, **change the failover durability posture** so a promotion can't silently lose committed writes.

## Resolution

**Replication lag is a consistency property you must route around, not a bug to eliminate.** Two distinct fixes for the two distinct symptoms:

1. **Stale reads (steady state) → route by freshness need.**
   - **Read-your-writes** flows (the user just wrote and immediately reads it back) go to the **primary**, or use LSN-pinning: capture the write's LSN and have the replica read wait until it has replayed past that LSN before serving.
   - **Lag-tolerant** reads (analytics, lists, search, anything where "a few seconds old" is fine) go to **replicas**. This is where the offload value actually lives.
   - Monitor lag (`pg_stat_replication` / `pg_last_wal_replay_lsn`) and **eject a replica from the read pool when its lag exceeds the tolerance** so a far-behind replica never serves user reads.

2. **Failover data loss → raise durability deliberately.** Async replication trades durability for primary latency: a promotion can lose the writes the old primary committed but hadn't yet shipped. If losing committed writes is unacceptable, move the critical path to **synchronous replication** (`synchronous_commit = on` with a `synchronous_standby_names` quorum) — the primary waits for a standby to confirm before acking the commit, so a promoted standby has the write. Name the cost: synchronous commit adds latency to every write and can stall if no standby is available. `[verify-at-use]` — the exact `synchronous_commit` levels and quorum syntax are version- and topology-specific; confirm against the target engine + managed-DB provider.

The trap is treating "add a read replica" as free horizontal read scaling. It is — *for reads that tolerate lag*. The moment a read must reflect a write that just happened, a lagging replica will lie, and the moment a failover happens, async replication can drop the tail of committed writes. Both are properties of the topology you chose, surfaced under load.

**Action for the next engineer:** classify every read as "must be current" vs "lag-tolerant" before routing it to a replica, and decide the failover durability posture (async vs sync, and which replica gets promoted) *before* the outage, not during it.

Cross-reference: canonical rule [`../best-practices/replication-lag-is-a-consistency-risk.md`](../best-practices/replication-lag-is-a-consistency-risk.md); the "Scaling reads — replica, cache, or partition?" and "Read routing across replicas — where does this read go?" trees in [`../knowledge/database-engineering-decision-trees.md`](../knowledge/database-engineering-decision-trees.md). Application-side read/write splitting in the data-access layer is `backend-engineering`'s lane; this team owns the topology and the routing rule.
