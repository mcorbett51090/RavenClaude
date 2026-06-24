---
name: build-presence-and-awareness
description: "Build live cursors, selections, and who's-here as an EPHEMERAL channel separate from the persisted document: last-write-wins per client, throttled, expiring on disconnect. Never write presence into the CRDT/OT log — it corrupts undo and bloats history."
---

# Build Presence & Awareness

Presence is **not the document**. It is ephemeral, it expires, and it rides its own channel.

## The rules

1. **Separate channel, always.** Awareness state (cursor position, selection range, user name/color, "who's online") never enters the persisted op log. It is its own message stream alongside the document sync.
2. **Last-write-wins per client.** Each client publishes its current awareness; there is no merge and no history — the latest wins and the old is discarded.
3. **Throttle it.** Cursor movement fires constantly; rate-limit/coalesce updates (e.g. on an animation frame) so presence doesn't drown the op channel.
4. **Expire on disconnect.** A presence entry has a timeout; when a client disconnects or goes silent, its cursor and "here" state clear. A cursor that outlives its user is a haunting.
5. **Map positions through the document's identity, not raw indices.** A remote cursor "after element X" stays correct as the text changes under it — the same element-identity discipline as the document model.

## Why this boundary matters

Writing presence into the CRDT/OT document:

- bloats history with data that should have evaporated,
- corrupts undo (undoing "moved my cursor" is meaningless),
- entangles two lifecycles — the document is durable, presence is disposable.

This is the single most common first-collaborative-build mistake.

## Anti-patterns

- Storing cursors/selections in the shared doc "because it's already synced."
- Un-throttled cursor broadcast saturating the channel.
- No expiry → ghost users linger after they leave.

## See also

- [`../scale-the-sync-server/SKILL.md`](../scale-the-sync-server/SKILL.md) (the awareness channel scales with the room).
- Best practice: [`../../best-practices/presence-is-ephemeral-keep-it-out-of-the-document.md`](../../best-practices/presence-is-ephemeral-keep-it-out-of-the-document.md)
- Concepts: [`../../knowledge/consistency-and-merge-concepts.md`](../../knowledge/consistency-and-merge-concepts.md) ("Presence is not the document").
