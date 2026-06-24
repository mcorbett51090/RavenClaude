---
description: "Map a collaborative document's fields onto CRDT/OT primitives so the merged result preserves intention — sequence for text, register for scalars, OR-Set for membership, counter for tallies — with identity-based positions and the intention traps named."
argument-hint: "[document type + its fields + chosen merge model]"
---

You are running `/realtime-collaboration-engineering:design-doc-model`. Use `sync-engine-engineer` + the `design-the-document-model` skill.

> Engineering craft, not product advice.

## Steps
1. Decompose the shared state into fields; for each, state what should happen on a concurrent edit.
2. Traverse the "which CRDT type per field" tree in `knowledge/crdt-vs-ot-decision-tree.md` and pick the primitive per field.
3. Define the operation-identity scheme `(clientID, counter)` and confirm positions are referenced by **element identity, not index**.
4. Name the intention traps (concurrent insert+delete, format+edit, move+edit) and the undo scope; if a CRDT, the growth-bounding plan.
5. Emit using `templates/document-model-spec.md` + the Structured Output block.
