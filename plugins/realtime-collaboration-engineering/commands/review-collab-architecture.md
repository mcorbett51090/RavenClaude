---
description: "Review a realtime/collaborative design for the recurring failure modes: unnamed merge model/consistency, presence stored in the document, no offline/reconnect path, missing causal identity, unbounded CRDT growth, and authorization in the wrong layer."
argument-hint: "[design doc / system description to review]"
---

You are running `/realtime-collaboration-engineering:review-collab-architecture`. Use `collab-architect` to coordinate; pull in `sync-engine-engineer` and `presence-and-transport-engineer` for their lanes.

> Engineering craft, not product advice. Library specifics are `[verify-at-use]`.

## Review checklist
1. **Merge model + consistency named?** CRDT/OT/LWW chosen on data shape + offline need; guarantee stated. (`pick-the-merge-model-by-data-shape-not-hype`)
2. **Causal identity?** Every op has a stable `(clientID, counter)`; positions by element identity, not index. (`every-edit-needs-a-stable-causal-identity`)
3. **Presence separated?** Cursors/selections on their own ephemeral, throttled, expiring channel — not in the document. (`presence-is-ephemeral-keep-it-out-of-the-document`)
4. **Offline/reconnect path?** Buffer + resume-from-version + delta merge, no replay-as-new. (`design-for-offline-from-day-one`)
5. **Growth bounded?** Snapshots + compaction + tombstone GC with the safety condition. (`bound-document-growth-tombstones-and-snapshots`)
6. **Topology + truth named, access control at the boundary?** (`the-server-is-a-relay-and-source-of-truth-decide-which`, `authority-and-access-control-live-at-the-sync-boundary`)
7. **Tested for concurrency/partition/reconnect**, not just a demo? (`test-with-concurrent-conflicting-edits-and-partition`)

Emit findings (P0/P1) + the Structured Output block. Each library/protocol claim flagged `[verify-at-use]`.
