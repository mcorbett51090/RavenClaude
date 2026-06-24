# Realtime Collaboration — Consistency & Merge Concepts (durable)

> The durable mental model behind the team's decisions. These concepts are **stable** — they are properties of distributed systems, not of any one library — so unlike [`realtime-collab-tooling-2026.md`](realtime-collab-tooling-2026.md) they carry no expiry. Agents lean on this file when reasoning about *why* a merge model behaves as it does.
>
> _Last reviewed: 2026-06-24 by `claude`. Principles are durable; verify specific library guarantees at use._

---

## The two promises a collaborative system makes

1. **Convergence (Strong Eventual Consistency).** Any two replicas that have received the **same set of operations** reach the **same state**, regardless of the order or timing in which they received them, with no central coordinator required. This is what a CRDT guarantees by construction. Convergence alone does **not** mean the result is *good* — two replicas can agree on a mangled paragraph.
2. **Intention preservation.** The merged result reflects **what each user meant** by their edit (an insert lands where the user typed it relative to the text they saw; a concurrent format and a concurrent insert both survive). This is the hard part, and it is a property of how you **model the document**, not a free gift of the algorithm. OT was designed around intention preservation explicitly; CRDT sequence types achieve it through careful element identity.

A system can converge without preserving intention (LWW on prose), and a well-modeled one does both.

---

## Causal ordering and clocks

- **Causal order** is the "happened-before" relation: if operation B was created by a client that had already seen A, then every replica must apply A before B. Concurrent operations (neither saw the other) may be applied in any order — convergence must hold regardless.
- **Lamport timestamps** give a total order consistent with causality using a single counter per client (`max(seen) + 1`), with the `clientID` breaking ties. Cheap; enough to order operations deterministically.
- **Vector clocks** track a counter *per client*, so a replica can tell whether two operations are causally ordered or genuinely **concurrent** — information Lamport timestamps lose. Heavier (grows with client count) but precise.
- **Stable operation identity.** Every operation carries a `(clientID, counter)` (or equivalent) that is **globally unique and never reused**. This identity is what lets replicas **deduplicate** re-delivered ops, **order** them causally, and **reference** positions (an insert says "after element X", not "at index 5", because indices shift under concurrency).

---

## Why a CRDT grows — tombstones and history

- A **tombstone** is a marker left when an element is deleted, kept so that a concurrent operation referencing that element (an insert "after" it, a re-add) still has something to anchor to. Tombstones are why a CRDT document can keep growing even as visible content shrinks.
- **Operation history / oplog** also accumulates if you keep every op for late-joining or offline replicas to catch up.
- **Bounding growth** = **snapshots** (a compacted materialized state you can start a new replica from) + **compaction / tombstone garbage collection** (dropping history and tombstones that *every* replica has acknowledged). The safety condition is the catch: you can only collect what everyone has seen, so GC needs a notion of the minimum acknowledged version across active replicas.

---

## Presence is not the document

**Awareness / presence** state — cursor position, selection range, user name/color, "who's online" — is **ephemeral**: it has no history, it expires when the user disconnects, and it is **last-write-wins per client**. It must travel on a **separate channel** from the persisted operation log. Writing presence into the CRDT/OT document corrupts undo, bloats history with data that should have evaporated, and entangles two lifecycles that should be independent. This is the single most common architecture mistake in first collaborative builds.

---

## Operation delivery semantics

- The merge engine generally needs operations **at least once** and **idempotently applied** (stable ids make re-delivery safe) — exactly-once on the wire is unnecessary if application is idempotent.
- On **reconnect**, a client resumes from its **last acknowledged version** and exchanges the delta, rather than replaying its whole buffer as new edits. Conflating "I was offline and made these edits" with "here are brand-new edits" is how naive reconnect paths lose or duplicate data.

---

## See also

- [`crdt-vs-ot-decision-tree.md`](crdt-vs-ot-decision-tree.md), [`transport-and-topology-decision-tree.md`](transport-and-topology-decision-tree.md)
- Skills: [`../skills/handle-offline-and-reconnection/SKILL.md`](../skills/handle-offline-and-reconnection/SKILL.md), [`../skills/design-the-document-model/SKILL.md`](../skills/design-the-document-model/SKILL.md)
