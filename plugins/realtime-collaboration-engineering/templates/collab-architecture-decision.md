# Collaboration Architecture Decision — <feature>

> Output template for the merge-model + topology decision. One per collaborative feature. **Engineering craft, not product advice.** Library specifics are `[verify-at-use]`. Decide before sync code is written — these are one-way doors.

## Feature
- **What is collaboratively edited:** _____
- **Prepared:** 2026-__-__ · **Decided by:** _<collab-architect>_

## Merge model
- **Decision:** ☐ CRDT  ☐ OT  ☐ Last-writer-wins (per field, list below)
- **Must converge without a central order (offline / local-first / P2P)?** ☐ yes → CRDT  ☐ no
- **Data shape:** _text / list / map / rich-text / JSON tree_
- **Tree node landed on:** _<crdt-vs-ot-decision-tree node>_
- **Library (if any):** _____ — retrieved 2026-__-__ `[verify-at-use]`

## Consistency guarantee
- **Model:** ☐ Server-authoritative  ☐ Strong eventual consistency
- **What "merged" means for the user on conflict:** _____
- **Intention-preservation expectations:** _____

## Topology
- **Decision:** ☐ Client-server  ☐ SFU/relay  ☐ P2P mesh
- **Source of truth lives:** _____
- **Persistence:** _op log / snapshots / both_
- **Access control enforced at:** _the sync boundary_

## Offline posture
- **Offline editing:** ☐ full  ☐ read-only  ☐ none — _and why_

## Seams handed off
- **Document model + merge engine →** `sync-engine-engineer`
- **Transport + presence + scaling →** `presence-and-transport-engineer`
- **UI/editor binding →** frontend-engineering · **Sync service/store →** backend-engineering

## Verify-at-use flags
- _List every library/protocol/version relied on; each re-confirmed against current docs before adoption._

---
_Plus the ravenclaude-core Structured Output block._
