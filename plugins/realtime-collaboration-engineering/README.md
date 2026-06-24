# realtime-collaboration-engineering

A RavenClaude plugin: a **realtime / multiplayer collaboration engineering** specialist team for building collaborative-editing systems (Figma / Notion / Google-Docs style) that stay correct under concurrent, offline, and out-of-order edits.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Engineering craft — not legal, security, or product advice.** Library, service, and protocol specifics are volatile: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a dependency or a guarantee. The durable distributed-systems reasoning is kept separate (it doesn't rot).

## What it's for

Getting the two irreversible decisions right — **how concurrent edits merge** and **the topology they flow through** — then building the document model, the offline/reconnect path, presence, transport, and a sync server that scales to many rooms. The hard part of collaboration is never the demo; it's the user who edited on a plane, the field two people changed at once, and the document that's been open for a year.

## Agents

| Agent | Use for |
|---|---|
| **collab-architect** | The merge model (CRDT vs OT vs LWW), the consistency guarantee, the topology, the offline posture |
| **sync-engine-engineer** | The document model on the chosen CRDT/OT, causal identity, offline/reconnect merge, tombstone/snapshot/compaction, collaborative undo |
| **presence-and-transport-engineer** | Transport (WebSocket vs WebRTC), presence/awareness, connection lifecycle/reconnection, scaling the sync server, access control at the boundary |

## What's inside

- **5 skills** — choose-crdt-or-ot, design-the-document-model, handle-offline-and-reconnection, build-presence-and-awareness, scale-the-sync-server.
- **Knowledge bank** — [`crdt-vs-ot-decision-tree.md`](knowledge/crdt-vs-ot-decision-tree.md) and [`transport-and-topology-decision-tree.md`](knowledge/transport-and-topology-decision-tree.md) (four Mermaid decision trees), [`consistency-and-merge-concepts.md`](knowledge/consistency-and-merge-concepts.md) (durable concepts), [`realtime-collab-tooling-2026.md`](knowledge/realtime-collab-tooling-2026.md) (dated tooling map, verify-at-use).
- **8 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **4 templates** — collaboration-architecture decision, document-model spec, sync-server scaling plan, offline/conflict test plan.
- **3 commands** — `/choose-merge-model`, `/design-doc-model`, `/review-collab-architecture`.
- **1 advisory hook** — `flag-realtime-collab-smells.sh` (CRDT/OT design with no consistency guarantee, presence stored in the document, library reference with no date/verify-at-use). `RTC_STRICT=1` to block.

## Seams

UI/editor binding → `frontend-engineering` · sync service & store → `backend-engineering` · op/event log fan-out (CDC/analytics) → `data-streaming-engineering` · latency/load → `performance-engineering` · threat model → `security-engineering` · CRDT-library dependency intake → `open-source-maintenance`.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project (local dev)
/plugin install realtime-collaboration-engineering@ravenclaude
```
