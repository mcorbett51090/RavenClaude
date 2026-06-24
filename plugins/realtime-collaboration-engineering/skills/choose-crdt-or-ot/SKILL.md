---
name: choose-crdt-or-ot
description: "Choose the merge model for a collaborative feature: CRDT vs OT vs last-writer-wins, decided by whether the system must converge without a central order (offline/P2P) and by the data shape — not by hype. Name the consistency guarantee and the growth-bounding obligation that comes with the choice."
---

# Choose CRDT or OT

The merge model is a **one-way door**. Walk through it on purpose.

## The decision

1. **Does it need to converge without a central order?** Offline-first, local-first, or P2P → you need a **CRDT** (it converges with no coordinator). A central server can order all ops → OT or a server-authoritative CRDT are both open.
2. **What is the data shape?** Traverse the [`../../knowledge/crdt-vs-ot-decision-tree.md`](../../knowledge/crdt-vs-ot-decision-tree.md):
   - single scalar that should have one winner → **LWW-Register** (don't reach for a heavyweight model for a toggle),
   - text / ordered sequence with heavy concurrency → **OT** (if you have a correct, tested transform function + central server) or a **sequence CRDT** (off the shelf),
   - structured map/list/tree document → a **CRDT document** composing map + sequence + register types.
3. **Name the consistency guarantee.** Server-authoritative (server order wins) vs strong eventual consistency (every replica with the same ops converges). State it explicitly — it determines whether a client can act offline.
4. **Accept the growth obligation.** If you chose a CRDT, the snapshot + compaction + tombstone-GC plan is **part of this decision**, not a later chore (see [`scale-the-sync-server`](../scale-the-sync-server/SKILL.md)).

## Trade-off summary

| | CRDT | OT |
|---|---|---|
| Central server required | No | Yes |
| Offline / P2P | Natural | Hard |
| State size | Grows (tombstones/history) — must bound | Compact |
| Hard part | Bounding growth, per-field type choice | A correct transform function across all op pairs |

## Anti-patterns

- Picking a CRDT for the brand, then discovering you needed OT's compact server-authoritative model (or vice-versa) after launch.
- Last-writer-wins on prose (data loss); a heavyweight CRDT on a boolean (waste).
- Choosing a CRDT and not planning compaction — a memory leak with good PR.

## See also

- [`../design-the-document-model/SKILL.md`](../design-the-document-model/SKILL.md) — once the model is chosen, map the document onto it per field.
- Best practice: [`../../best-practices/pick-the-merge-model-by-data-shape-not-hype.md`](../../best-practices/pick-the-merge-model-by-data-shape-not-hype.md).
- Concepts: [`../../knowledge/consistency-and-merge-concepts.md`](../../knowledge/consistency-and-merge-concepts.md).
