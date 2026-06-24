# Document Model Spec — <document type>

> Output template for mapping shared state onto CRDT/OT primitives per field. One per collaborative document type. Convergence is free; this spec is where **intention preservation** is designed.

## Document
- **Type / what it represents:** _____
- **Merge model (from the architecture decision):** _CRDT / OT / hybrid_
- **Prepared:** 2026-__-__ · **By:** _<sync-engine-engineer>_

## Field-by-field mapping

| Field | Primitive | Merge behavior on concurrent edit | Why this type |
|---|---|---|---|
| _e.g. title_ | sequence/text | both refinements survive | prose, no LWW |
| _e.g. status_ | LWW-Register | last edit wins | one value should win |
| _e.g. tags_ | OR-Set | add/remove, re-add works | membership |
| _e.g. count_ | PN-Counter | sums concurrent increments | tally |
| … | … | … | … |

## Identity & positions
- **Operation identity scheme:** _(clientID, counter) / Lamport / vector clock_
- **Positions referenced by:** _element identity (NOT index)_

## Intention traps (name the desired outcome)
- **Concurrent insert + delete at the same spot:** _____
- **Concurrent format + edit of the same range:** _____
- **Move vs edit of the moved item:** _____

## Undo
- **Scope:** _per-user inverse ops (NOT global time-travel)_

## Growth bounding (if CRDT)
- **Tombstones from:** _deletes_ · **Snapshot cadence:** _____ · **GC safety condition:** _only history every active replica acknowledged_

---
_Plus the ravenclaude-core Structured Output block._
