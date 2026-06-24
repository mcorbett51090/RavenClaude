---
description: "Decide the merge model for a collaborative feature — CRDT vs OT vs last-writer-wins — on the data shape and offline need, naming the consistency guarantee and the growth obligation (verify-at-use on any library)."
argument-hint: "[what's collaboratively edited + offline need + data shape]"
---

You are running `/realtime-collaboration-engineering:choose-merge-model`. Use `collab-architect` + the `choose-crdt-or-ot` skill.

> Engineering craft, not product advice. Every library/protocol specific is `[verify-at-use]`.

## Steps
1. Capture what is collaboratively edited, whether it must work offline/P2P, and the data shape (text / list / map / rich-text / JSON tree).
2. Traverse the **CRDT-vs-OT** tree in `knowledge/crdt-vs-ot-decision-tree.md`.
3. Decide the model and name: the consistency guarantee (server-authoritative vs strong eventual consistency), the per-field type implications, and — if a CRDT — the growth-bounding obligation.
4. Emit using `templates/collab-architecture-decision.md` + the Structured Output block. Hand the document model to `sync-engine-engineer` and the wire to `presence-and-transport-engineer`.
