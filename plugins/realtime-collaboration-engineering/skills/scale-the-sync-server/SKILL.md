---
name: scale-the-sync-server
description: "Scale a realtime sync server: shard by document/room with connection affinity, fan-out ops within a room, offload snapshots to durable storage, bound document growth (tombstone GC + compaction), and enforce access control at the sync boundary. Horizontal scale is more rooms, not a bigger single node."
---

# Scale the Sync Server

The **room is the shard**. Scale by adding rooms across nodes, not by making one node hold every room.

## The plan

1. **Shard by document/room.** A room (one collaborative document and its participants) is the natural unit of state and concurrency. Route all of a room's clients to the **same node** (connection affinity / consistent routing) so the live state has a single home.
2. **Fan-out within a room.** An incoming op is applied once and broadcast to the room's other members. Presence rides the same room scope on its separate channel.
3. **Add nodes by sharding rooms**, with a routing/affinity layer (a gateway, consistent hashing, or a per-room stateful object). One node owns a slice of the rooms; you scale out by moving rooms, not by replicating one giant room everywhere.
4. **Offload persistence and snapshots to durable storage.** The live node holds the hot state; the op log and periodic snapshots go to a store so a room can be rehydrated, a late joiner can catch up, and a node can fail over.
5. **Bound document growth.** Schedule **snapshots + compaction + tombstone garbage collection**, collecting only history that **every active replica has acknowledged** (the safety condition). Unbounded tombstones are how a long-lived document eventually falls over.
6. **Enforce access control at the boundary.** Who may join a room, edit vs view, and per-op authorization live at the **server edge** where connections terminate — the merge engine trusts that the ops it receives are already authorized.

## Capacity signals to watch

| Signal | Reads | Action |
|---|---|---|
| Connections per node | Fan-out load | Re-shard rooms across nodes |
| Op broadcast latency | In-room responsiveness | Coalesce/throttle; check node saturation |
| Document size over time | Tombstone/history growth | Compaction + GC cadence |
| Reconnect storm behavior | Resilience | Jittered backoff + resume-from-version |

## Anti-patterns

- One node holding every room (no shard key) — a single point of saturation.
- No snapshot offload → cold start and failover replay the full op log.
- Authorizing inside the merge engine instead of at the connection edge.

## See also

- [`../../knowledge/transport-and-topology-decision-tree.md`](../../knowledge/transport-and-topology-decision-tree.md) (topology that this scales).
- Template: [`../../templates/sync-server-scaling-plan.md`](../../templates/sync-server-scaling-plan.md)
- Best practices: [`../../best-practices/bound-document-growth-tombstones-and-snapshots.md`](../../best-practices/bound-document-growth-tombstones-and-snapshots.md), [`../../best-practices/authority-and-access-control-live-at-the-sync-boundary.md`](../../best-practices/authority-and-access-control-live-at-the-sync-boundary.md)
- Seam: latency budgets + load testing → [`../../../performance-engineering/CLAUDE.md`](../../../performance-engineering/CLAUDE.md)
