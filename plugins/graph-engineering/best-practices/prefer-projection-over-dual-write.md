# Prefer a projection over a dual-write

**Status:** Pattern (owner-gated)
**Domain:** Graph + relational coexistence
**Applies to:** `graph-engineering`

[unverified — premise not disconfirmed: documenting internals (36) and dual-write-as-defect (35) are design inferences; phases stay one reversible file each and may be skipped]

---

## Why this exists

[unverified — training knowledge] Dual-writing the same facts to a relational system of record **and** a separately writable graph, with no named owner for each write, is how the two copies drift. The *allowed* 2026 pattern in this marketplace is a **graph projection over tables** (Fabric Graph over OneLake, Spanner Graph over Spanner), not an ETL that owns a second write path.

## How to apply

- Keep OLTP writes in the relational system of record (`database-engineering`).
- If you need traversals, prefer an engine that **reads the same tables** as a graph (C25 Fabric Graph, C26 Spanner Graph) `[verify-at-use]`.
- If you must materialize a graph copy, name **one owner** for the write, an idempotent key, and a lag SLO. That is an integration, not this plugin's default.

## Edge cases / when the rule does NOT apply

- A graph that is the *only* store (no relational SoR) is not a dual-write.
- Read replicas / warehouse copies with a named pipeline owner are projections, not silent dual-writes.

## See also

- [`../knowledge/graph-languages-and-engines-2026.md`](../knowledge/graph-languages-and-engines-2026.md)
- `plugins/microsoft-fabric/knowledge/fabric-2026-capability-map.md`

## Provenance

G3b owner-gated C35. Allowed pattern grounded in C25/C26. General consistency claim remains `[unverified — training knowledge]`.

---

_Last reviewed: 2026-08-14_
