---
name: design-the-document-model
description: "Map the app's shared state onto CRDT/OT primitives per field — sequence for text/lists, map for records, register for scalars, counter for tallies, OR-Set for membership — so the merged result preserves intention, not just converges. Choose each field's type for the conflict you want."
---

# Design the Document Model

Convergence is free; **intention preservation** is what you design here. The merged result is only as good as the per-field type mapping.

## The method

1. **Decompose the shared state into fields**, and for each, ask "what should happen when two people change it at once?"
2. **Pick the primitive for that answer** (traverse [`../../knowledge/crdt-vs-ot-decision-tree.md`](../../knowledge/crdt-vs-ot-decision-tree.md) "which CRDT type per field"):
   - toggle / status / single value, last edit wins → **LWW-Register**,
   - a tally incremented from many clients → **counter (PN-Counter)**,
   - a set with add/remove where re-adding must work → **OR-Set**; grow-only → **G-Set**,
   - text or an ordered list → **sequence/text CRDT** (intention-preserving inserts via element identity, not indices),
   - a record of named fields → **map** of nested CRDT values,
   - a nested tree (rich-text, outline) → composed **map + sequence**.
3. **Use element identity, never indices, for positions.** An insert references "after element X", because indices shift under concurrent edits.
4. **Decide the intention traps explicitly:** concurrent insert + delete at the same spot, concurrent format + edit of the same range, a move vs an edit of the moved item. Name the desired outcome per case.

## Worked example — a task card

| Field | Type | Why |
|---|---|---|
| `title` | sequence/text | two people refining wording should both survive |
| `status` | LWW-Register | one value should win; last edit is fine |
| `assignees` | OR-Set | add/remove, re-add must work |
| `commentCount` | PN-Counter | increments from many clients |
| `description` | rich-text (map+sequence) | structured prose |

## Anti-patterns

- LWW on a paragraph (silent data loss) when a sequence type was needed.
- Index-based positions (concurrent edits land in the wrong place).
- A single "blob" field for everything, losing per-field merge control.

## See also

- [`../choose-crdt-or-ot/SKILL.md`](../choose-crdt-or-ot/SKILL.md), [`../handle-offline-and-reconnection/SKILL.md`](../handle-offline-and-reconnection/SKILL.md)
- Template: [`../../templates/document-model-spec.md`](../../templates/document-model-spec.md)
- Best practice: [`../../best-practices/every-edit-needs-a-stable-causal-identity.md`](../../best-practices/every-edit-needs-a-stable-causal-identity.md)
