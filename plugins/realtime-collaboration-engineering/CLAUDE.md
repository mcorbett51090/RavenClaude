# Realtime-Collaboration-Engineering Plugin — Team Constitution

> Team constitution for the `realtime-collaboration-engineering` Claude Code plugin. Three specialist agents — **collab-architect**, **sync-engine-engineer**, **presence-and-transport-engineer** — plus a decision-tree knowledge bank, skills, templates, best-practices, and an advisory hook, all aimed at building multiplayer / collaborative-editing systems (Figma / Notion / Google-Docs style): the **merge model**, the **shared-document model**, **offline & reconnection**, **presence & awareness**, and the **transport + sync-server scale**.
>
> Designed for the engineer or tech lead accountable for a collaborative feature that must stay correct under concurrent, offline, and out-of-order edits.
>
> **Orientation:** this file is **domain-specific** to realtime-collaboration engineering. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 0. Scope (read first)

This plugin ships **engineering craft — not legal, security, or product advice.** The agents:

- treat every **library, service, and protocol specific** as **volatile** — anything quoted from [`knowledge/realtime-collab-tooling-2026.md`](knowledge/realtime-collab-tooling-2026.md) carries a **retrieval date + `[verify-at-use]`** and must be confirmed against the current docs before it drives a dependency or a guarantee;
- keep the **durable distributed-systems reasoning** (consistency models, causal order, clocks, tombstones, intention preservation) in [`knowledge/consistency-and-merge-concepts.md`](knowledge/consistency-and-merge-concepts.md), which does **not** rot;
- defer the threat model to `security-engineering` and the binding capacity/latency numbers to `performance-engineering`.

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`collab-architect`](agents/collab-architect.md) | The merge model (CRDT vs OT vs LWW), the consistency guarantee, the topology, the offline posture | "should we use a CRDT or OT?"; "what happens when two people edit the same thing?"; "do we even need a server?" |
| [`sync-engine-engineer`](agents/sync-engine-engineer.md) | The document model on the chosen CRDT/OT, causal identity, offline/reconnect merge, tombstone/snapshot/compaction, collaborative undo | "how do I model our rich-text doc?"; "offline edits merge back how?"; "why does our CRDT keep growing?" |
| [`presence-and-transport-engineer`](agents/presence-and-transport-engineer.md) | Transport (WebSocket vs WebRTC), presence/awareness, connection lifecycle/reconnection, scaling the sync server, access control at the boundary | "WebSocket or WebRTC?"; "live cursors without polluting the doc?"; "50k rooms — how does one server not fall over?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead (`collab-architect`) delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles. Team growth ships as skills + knowledge + templates, not a fourth parallel agent.

---

## 2. Routing rules (Team Lead)

- **"Which merge model / consistency / topology / offline posture"** → `collab-architect`.
- **"The document model / how a field merges / offline reconciliation / tombstones-snapshots / undo"** → `sync-engine-engineer`.
- **"The transport / presence & cursors / reconnection / scaling the sync server / access control at the boundary"** → `presence-and-transport-engineer`.
- **UI rendering, editor binding (ProseMirror/CodeMirror/etc.)** → [`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md).
- **The sync *service* hosting, data store, identity/auth provider** → [`../backend-engineering/CLAUDE.md`](../backend-engineering/CLAUDE.md).
- **A durable op/event log fanned out beyond the live room (CDC, analytics)** → [`../data-streaming-engineering/CLAUDE.md`](../data-streaming-engineering/CLAUDE.md) (distinct from the per-document sync channel).
- **Latency budgets, load behavior under churn** → [`../performance-engineering/CLAUDE.md`](../performance-engineering/CLAUDE.md).
- **Threat model for the collaboration boundary** → [`../security-engineering/CLAUDE.md`](../security-engineering/CLAUDE.md).

---

## 3. The non-negotiables (cross-cutting house opinions)

1. **The merge model is a one-way door.** Decide CRDT vs OT vs LWW on the data shape + offline need, via the tree — migrating later is a rewrite. ([`best-practices/pick-the-merge-model-by-data-shape-not-hype.md`](best-practices/pick-the-merge-model-by-data-shape-not-hype.md))
2. **Convergence is table stakes; intention preservation is the craft.** Two replicas agreeing on garbage is still garbage — model the document so the merged result is what users meant.
3. **Presence is not the document.** Cursors/selections/who's-here are ephemeral, throttled, expiring, and on their own channel — never in the persisted log. ([`best-practices/presence-is-ephemeral-keep-it-out-of-the-document.md`](best-practices/presence-is-ephemeral-keep-it-out-of-the-document.md))
4. **Every edit needs a stable causal identity.** `(clientID, counter)` and identity-based positions are the foundation dedupe, ordering, and offline all stand on. ([`best-practices/every-edit-needs-a-stable-causal-identity.md`](best-practices/every-edit-needs-a-stable-causal-identity.md))
5. **A CRDT with no compaction story is a memory leak.** Plan snapshots + tombstone GC before launch. ([`best-practices/bound-document-growth-tombstones-and-snapshots.md`](best-practices/bound-document-growth-tombstones-and-snapshots.md))
6. **Test the partition, not the demo.** Concurrent conflicting edits + network split + reconnect is the test that matters. ([`best-practices/test-with-concurrent-conflicting-edits-and-partition.md`](best-practices/test-with-concurrent-conflicting-edits-and-partition.md))
7. **Authorize at the sync boundary.** The merge engine trusts what it receives. ([`best-practices/authority-and-access-control-live-at-the-sync-boundary.md`](best-practices/authority-and-access-control-live-at-the-sync-boundary.md))

---

## 4. Knowledge bank & decision trees

- [`knowledge/crdt-vs-ot-decision-tree.md`](knowledge/crdt-vs-ot-decision-tree.md) — CRDT vs OT vs LWW, and which CRDT type per field (two Mermaid trees).
- [`knowledge/transport-and-topology-decision-tree.md`](knowledge/transport-and-topology-decision-tree.md) — transport (WS vs WebRTC) and topology (client-server / SFU / mesh) (two Mermaid trees).
- [`knowledge/consistency-and-merge-concepts.md`](knowledge/consistency-and-merge-concepts.md) — **durable** concepts (strong eventual consistency, causal order, Lamport/vector clocks, tombstones, intention preservation, delivery semantics).
- [`knowledge/realtime-collab-tooling-2026.md`](knowledge/realtime-collab-tooling-2026.md) — **dated** library/service/protocol map (`[verify-at-use]`).

Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to core's Capability Grounding Protocol).

---

## 5. Seams (what this plugin does NOT own)

| Concern | Owner |
|---|---|
| Rendering shared state, editor bindings, local UI | `frontend-engineering` |
| Sync service hosting, data store, auth provider | `backend-engineering` |
| Durable op/event log for downstream consumers (CDC, analytics) | `data-streaming-engineering` |
| Latency budgets, load/capacity under churn | `performance-engineering` |
| Threat model for the collaboration boundary | `security-engineering` |
| Dependency intake / license of a chosen CRDT lib | `open-source-maintenance` |

This plugin owns the **collaboration-specific craft** — the merge model, the document model, offline/presence/transport, and sync-server scale — and hands every adjacent concern to its clean seam rather than duplicating it.

---

## 6. Milestones

- **0.1.0 (2026-06-24)** — Initial release. 3 agents, 5 skills, a 4-file knowledge bank (CRDT-vs-OT + transport/topology Mermaid trees, durable consistency concepts, dated 2026 tooling map), 8 best-practices, 4 templates, 3 commands, 1 advisory hook. Built as the top unbuilt row of the standing new-plugin roadmap (`docs/proposals/*-ten-new-plugin-candidates.md`).
