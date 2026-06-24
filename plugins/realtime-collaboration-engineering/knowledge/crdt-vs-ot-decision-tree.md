# Realtime Collaboration — CRDT vs OT Decision Tree

> Reference decision tree for the `realtime-collaboration-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering craft, not legal or product advice.** Anything naming a specific library, version, or guarantee is `[verify-at-use]` — confirm against the current library docs before it drives a dependency. Durable concepts live in [`consistency-and-merge-concepts.md`](consistency-and-merge-concepts.md); the dated library map in [`realtime-collab-tooling-2026.md`](realtime-collab-tooling-2026.md).
>
> _Last reviewed: 2026-06-24 by `claude`. The principles are durable; the named libraries are dated._

---

## Decision Tree: CRDT vs OT vs last-writer-wins?

```mermaid
flowchart TD
    A[Concurrent edits to shared state] --> B{Does it need to work
    OFFLINE / peer-to-peer
    with no central order?}
    B -- "yes — offline-first,
    local-first, or P2P" --> C[CRDT
    converges with no central server]
    B -- "no — a central server
    can order all ops" --> D{What is the data shape?}
    D -- "a single scalar / flag
    where one value should win" --> E[Last-writer-wins register
    simplest correct merge]
    D -- "text or an ordered sequence
    with heavy concurrent edits" --> F{Team has a correct,
    tested transform function
    + central server?}
    F -- yes --> G[OT
    compact state, server-authoritative]
    F -- "no / want it off the shelf" --> H[Sequence CRDT
    e.g. RGA/Fugue-style]
    D -- "structured doc:
    maps, lists, nested trees" --> I[CRDT document
    map + sequence + register types]
    C --> J{Growth acceptable?}
    I --> J
    J -- "must bound size" --> K[Plan snapshots + compaction
    + tombstone GC from day one]
    J -- ok --> L[Ship; revisit at scale]
```

**Rule:** the choice is driven by **(1) whether the system must converge without a central order** (offline / local-first / P2P → CRDT) and **(2) the data shape**. A CRDT buys decentralization and offline-first at the cost of metadata growth (tombstones, op history) you must plan to bound. OT buys compact state and fine-grained server control at the cost of a **central server** and a **correct transform function** that is notoriously hard to get right across operation pairs. Last-writer-wins is a real, correct merge for a scalar that should have one winner — use it deliberately, never on prose. Whenever a CRDT is chosen, the snapshot/compaction/tombstone-GC plan is part of the decision, not a later chore.

---

## Decision Tree: which CRDT type per field?

```mermaid
flowchart TD
    A[A field in the shared document] --> B{What is it?}
    B -- "a toggle / status / single value
    last edit should win" --> C[LWW-Register]
    B -- "a counter
    increments from many clients" --> D[PN-Counter]
    B -- "a set of items,
    add/remove" --> E{Re-add after remove
    must work?}
    E -- yes --> F[Observed-Remove Set OR-Set]
    E -- "no, grow-only" --> G[G-Set]
    B -- "text or an ordered list" --> H[Sequence CRDT
    list/text type]
    B -- "a record of named fields" --> I[Map CRDT
    keys -> nested CRDT values]
    B -- "a nested tree
    (rich-text, outline)" --> J[Nested document
    map + sequence composed]
```

**Rule:** merge behavior is a **property of the type you pick per field**, not of the library as a whole. Choose the type for the conflict you want: LWW-Register for a flag, a counter type for tallies, an OR-Set when re-adding a removed item must work, a sequence type for text/lists, and a map of nested CRDTs for records. Getting this mapping right is what makes the merged result match user intention rather than merely converge. The field-level reasoning lives in the `design-the-document-model` skill.

---

## See also

- [`transport-and-topology-decision-tree.md`](transport-and-topology-decision-tree.md) — the wire and topology decision.
- [`consistency-and-merge-concepts.md`](consistency-and-merge-concepts.md) — causal order, clocks, tombstones, strong eventual consistency, intention preservation.
- Skill: [`../skills/choose-crdt-or-ot/SKILL.md`](../skills/choose-crdt-or-ot/SKILL.md), [`../skills/design-the-document-model/SKILL.md`](../skills/design-the-document-model/SKILL.md).
