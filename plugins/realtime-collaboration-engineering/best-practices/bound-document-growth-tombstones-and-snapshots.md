# Bound document growth — tombstones and snapshots

**Status:** Absolute rule (for CRDT systems)
**Domain:** Merge engine / scaling
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

In a CRDT, deletes usually become **tombstones** (kept so concurrent ops referencing the deleted element still anchor), and op history accumulates for late-joining/offline replicas. Left unplanned, a long-lived document keeps growing even as visible content shrinks — **a memory leak with good PR.** The fix is snapshots + compaction + tombstone garbage collection, planned before launch.

## How to apply

- Take periodic **snapshots** (a compacted materialized state new replicas start from).
- **Compact** op history and **GC tombstones** — but only history that **every active replica has acknowledged** (the safety condition; collecting too eagerly breaks a lagging replica's merge).
- Track the minimum acknowledged version across active replicas to know what is safe to collect.
- Offload snapshots to durable storage so cold start / failover doesn't replay the full log.

**Do:** plan compaction at design time; respect the "everyone has seen it" safety condition.
**Don't:** ship a CRDT with no growth story; GC history a slow/offline replica still needs.

## Edge cases / when the rule does NOT apply

A short-lived, ephemeral document (a transient session that is discarded) may not need compaction — but say so; "short-lived" has a way of becoming "open for a year."

## See also

- [`../skills/scale-the-sync-server/SKILL.md`](../skills/scale-the-sync-server/SKILL.md)
- [`../knowledge/consistency-and-merge-concepts.md`](../knowledge/consistency-and-merge-concepts.md) ("Why a CRDT grows")

## Provenance

Codifies `sync-engine-engineer` + `presence-and-transport-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
