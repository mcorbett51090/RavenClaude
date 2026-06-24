---
name: handle-offline-and-reconnection
description: "Design the offline-edit and reconnection path: buffer local ops with stable causal identity while disconnected, resume from the last acknowledged version on reconnect, and merge the delta — never replay offline edits as brand-new. The reconnect merge is where naive builds lose data."
---

# Handle Offline & Reconnection

The flaky network is the **common case**, not the edge case. The happy-path demo is not the system.

## The flow

1. **While disconnected:** apply edits locally and **buffer the ops with their stable causal ids** (`(clientID, counter)` / Lamport-stamped). The local replica is fully usable; the buffer is the to-be-synced delta.
2. **On reconnect:** exchange versions — the client tells the server its last acknowledged version, the server (or peer) sends what the client missed, and the client sends its buffered delta. **Merge by causal id**, deduplicating anything already applied.
3. **Never replay offline edits as new.** Re-sending the whole buffer as fresh ops duplicates or clobbers — the resume cursor (last acknowledged version) is what makes the exchange a delta, not a replay.
4. **Reconnect with jittered backoff**, and clear **stale presence** on the disconnect timeout (presence is ephemeral — see [`build-presence-and-awareness`](../build-presence-and-awareness/SKILL.md)).
5. **Decide the offline conflict UX:** because every op carries identity and the model converges, conflicting offline edits *merge* rather than prompt — but verify the merged result matches intention for your fields (see [`design-the-document-model`](../design-the-document-model/SKILL.md)).

## What makes it correct

- **Stable causal identity** on every op → safe dedupe and causal ordering regardless of arrival order.
- **Idempotent application** → re-delivery is harmless, so at-least-once delivery is enough.
- **A resume cursor** (last acknowledged version) → the post-reconnect exchange is a bounded delta.

## Anti-patterns

- Treating "I was offline" as "here are new edits" (data loss/duplication).
- No buffer cap / no compaction → a week offline produces an unbounded sync.
- Leaving a disconnected user's cursor "present" forever.

## See also

- Concepts: [`../../knowledge/consistency-and-merge-concepts.md`](../../knowledge/consistency-and-merge-concepts.md) (operation delivery semantics).
- Best practice: [`../../best-practices/design-for-offline-from-day-one.md`](../../best-practices/design-for-offline-from-day-one.md)
- Template: [`../../templates/offline-conflict-test-plan.md`](../../templates/offline-conflict-test-plan.md)
