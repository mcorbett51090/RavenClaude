# Pick the merge model by data shape, not hype

**Status:** Absolute rule
**Domain:** Architecture / merge model
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice. Library specifics are `[verify-at-use]`.

---

## Why this exists

The merge model — CRDT vs OT vs last-writer-wins — is a **one-way door**: migrating a shipped feature from one to another is a rewrite. The right choice is driven by **(1) whether the system must converge without a central order** (offline / local-first / P2P → CRDT) and **(2) the data shape per field**, not by which library is fashionable.

## How to apply

- Traverse [`../knowledge/crdt-vs-ot-decision-tree.md`](../knowledge/crdt-vs-ot-decision-tree.md) before choosing.
- Offline-first or P2P → CRDT (converges with no coordinator). Central server available → OT or server-authoritative CRDT both open.
- Match the field's type to the conflict you want: LWW-Register for a flag, sequence type for text, OR-Set for membership, counter for tallies.
- Name the consistency guarantee (server-authoritative vs strong eventual consistency) explicitly.
- If you choose a CRDT, commit to the growth-bounding plan **as part of the same decision**.

**Do:** decide on the tree; name the guarantee; accept the growth obligation.
**Don't:** pick a model by brand; use LWW on prose; default to a CRDT without a compaction plan.

## Edge cases / when the rule does NOT apply

A throwaway prototype that will never go offline and never scale can default to the simplest server-authoritative path — but say so as a decision, so the rewrite cost is visible if it ships.

## See also

- [`../skills/choose-crdt-or-ot/SKILL.md`](../skills/choose-crdt-or-ot/SKILL.md)
- [`../knowledge/consistency-and-merge-concepts.md`](../knowledge/consistency-and-merge-concepts.md)

## Provenance

Codifies `collab-architect` house opinion + the CRDT-vs-OT decision tree.

---

_Last reviewed: 2026-06-24 by `claude`_
