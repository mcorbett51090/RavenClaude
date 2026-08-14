# Model for supernodes

**Status:** Absolute rule
**Domain:** Property-graph modeling
**Applies to:** `graph-engineering`

---

## Why this exists

A celebrity node (global tag, admin user, tenant root) has a degree that makes anonymous `MATCH ()-` a sequential scan of a huge adjacency list. This is a **modeling** problem. Vendor indexes do not make `()-[]-()` from a celebrity cheap.

## How to apply

- Type the edge so queries can start from the *other* side.
- Partition the celebrity (`HashtagDay`, `UserMonth`) if degree *is* the product.
- Never `MATCH ()-[:TAGGED]->(h:Hashtag {name:'#ai'})` and then walk unbounded.

## Edge cases / when the rule does NOT apply

- A node that is celebrity-in-theory but has tens of edges in *this* dataset is not a supernode yet. Measure degree; do not cargo-cult partitions.

## See also

- [`../knowledge/lpg-modeling-catalog.md`](../knowledge/lpg-modeling-catalog.md)

## Provenance

Codifies house opinion #4 in [`../CLAUDE.md`](../CLAUDE.md) (C29).

---

_Last reviewed: 2026-08-14_
