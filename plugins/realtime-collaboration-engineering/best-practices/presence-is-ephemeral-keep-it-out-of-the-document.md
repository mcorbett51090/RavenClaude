# Presence is ephemeral — keep it out of the document

**Status:** Absolute rule
**Domain:** Presence / awareness
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

Cursors, selections, user color, and "who's online" are **awareness state**: they have no history, they expire on disconnect, and they are last-write-wins per client. Writing them into the persisted CRDT/OT log **bloats history with data that should evaporate, corrupts undo, and entangles a durable lifecycle with a disposable one.** It is the single most common first-collaborative-build mistake.

## How to apply

- Carry presence on its **own channel**, separate from the document op stream.
- Last-write-wins per client; no merge, no history.
- Throttle/coalesce updates (cursors move constantly).
- Expire presence on the disconnect timeout — no ghost users.
- Map remote cursor positions through element identity, not raw indices.

**Do:** a separate, throttled, expiring awareness channel.
**Don't:** store cursors/selections in the shared document "because it's already synced."

## Edge cases / when the rule does NOT apply

A *persistent* annotation a user deliberately leaves (a comment anchored to a position) **is** document state and belongs in the document — that is content, not presence. The line is "does it survive the user leaving?"

## See also

- [`../skills/build-presence-and-awareness/SKILL.md`](../skills/build-presence-and-awareness/SKILL.md)
- [`../knowledge/consistency-and-merge-concepts.md`](../knowledge/consistency-and-merge-concepts.md)

## Provenance

Codifies `presence-and-transport-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
