# Every edit needs a stable causal identity

**Status:** Absolute rule
**Domain:** Document model / merge engine
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

Without a globally-unique, never-reused identity per operation — a `(clientID, counter)` or Lamport-stamped id — "merge" is guesswork. Stable identity is what lets replicas **deduplicate** re-delivered ops, **order** them causally, and **reference positions** safely ("after element X", not "at index 5", because indices shift under concurrency). It is the foundation the offline path, idempotent delivery, and convergence all stand on.

## How to apply

- Stamp every operation with a unique `(clientID, counter)` (or vector/Lamport-clock equivalent) at creation.
- Reference document positions by element identity, never by mutable index.
- Make application idempotent so at-least-once delivery (and reconnect re-delivery) is safe.
- Use vector clocks where you must distinguish concurrent from causally-ordered ops; Lamport timestamps where a cheap total order suffices.

**Do:** unique, stable ids; identity-based positions; idempotent apply.
**Don't:** index-based positions; reusing counters; relying on arrival order for correctness.

## Edge cases / when the rule does NOT apply

A purely server-authoritative log where the server assigns the single canonical sequence can lean on that sequence as the identity — but each op still needs an id the client can use to dedupe its own re-sends.

## See also

- [`../skills/design-the-document-model/SKILL.md`](../skills/design-the-document-model/SKILL.md)
- [`../knowledge/consistency-and-merge-concepts.md`](../knowledge/consistency-and-merge-concepts.md)

## Provenance

Codifies `sync-engine-engineer` house opinion + the consistency concepts file.

---

_Last reviewed: 2026-06-24 by `claude`_
