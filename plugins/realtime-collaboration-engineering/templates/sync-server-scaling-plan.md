# Sync Server Scaling Plan — <system>

> Output template for scaling a realtime sync server. The room is the shard; horizontal scale is more rooms, not a bigger node.

## System
- **Sync model:** _server-authoritative / relay+CRDT_ · **Transport:** _WebSocket / WebRTC_
- **Prepared:** 2026-__-__ · **By:** _<presence-and-transport-engineer>_

## Sharding
- **Shard unit:** _document / room_
- **Routing / affinity:** _how a room's clients land on one node (gateway / consistent hash / per-room object)_
- **Fan-out within a room:** _apply once, broadcast to members_

## Persistence & snapshots
- **Durable store:** _____ · **Snapshot cadence:** _____
- **Cold start / failover:** _rehydrate from snapshot + tail of op log (NOT full replay)_

## Growth bounding
- **Compaction + tombstone GC cadence:** _____
- **Safety condition tracked:** _min acknowledged version across active replicas_

## Connection lifecycle
- **Reconnect:** _jittered backoff_ · **Resume:** _from last acknowledged version_
- **Presence expiry:** _on disconnect timeout_

## Access control
- **Enforced at:** _the sync boundary (connection edge)_ · **Edit vs view:** _____

## Capacity signals & thresholds

| Signal | Threshold | Action |
|---|---|---|
| Connections / node | _____ | re-shard rooms |
| Op broadcast latency | _____ | coalesce / add node |
| Document size growth | _____ | compaction / GC |

## Seam
- **Latency budgets + load testing under churn →** performance-engineering

---
_Plus the ravenclaude-core Structured Output block._
