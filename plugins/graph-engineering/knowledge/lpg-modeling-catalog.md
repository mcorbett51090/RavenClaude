# LPG modeling catalog

**Last reviewed:** 2026-08-14

A labeled property graph stores **nodes** (labels + key-value properties) and **directed, typed, property-bearing relationships**. A relationship always has a start node, an end node, and exactly one type. An untyped empty-bracket hop is a model bug, not a shortcut.

## Nodes

- Give every node **at least one label** that is a type (`Person`, `Order`, `Plugin`), not a state (`Active`).
- Put state on **properties** (`status: 'active'`) or on a **dated relationship**.
- Identity is a **stable business key** (`sku`, `plugin_name`, `email_id`) plus a store-generated id. Do not use a display name as the join key.

## Relationships

- **Type every relationship.** `[:KNOWS]`, `[:DEPENDS_ON]`, `[:MENTIONS]`.
- **Give it a direction** that matches the verb. `(:Order)-[:PLACED_BY]->(:Customer)` is a different sentence from the reverse.
- Put edge payload on the **relationship** when it belongs to the *link* (since, weight, role), not on either node.
- Do not invent a pair of inverse types (`KNOWS` / `KNOWN_BY`) unless both directions carry different properties. Traverse against the stored direction or use an explicit undirected read.

## Temporal edges

Two honest patterns:

1. **Relationship properties** — `[:EMPLOYED_AT {from: date, to: date}]`. Simple; poor at “who was employed on date D” without a filter.
2. **First-class time nodes or bi-temporal properties** — use when history is the product (the Zep / Graphiti *intent*, not their SKU). This plugin does not stand up that store.

## Supernodes / dense nodes

A celebrity node (`(:Hashtag {name:'#ai'})`, `(:User {id:'admin'})`, a global `(:Tenant)`) has a degree that makes an untyped empty-bracket hop a full scan.

**Do:**

- Type the edge so a local index can start from the *other* side (`(:Post)-[:TAGGED]->(:Hashtag)` and query from `Post` when possible).
- Partition the celebrity (`(:HashtagDay {name, day})`) if the degree is the product.
- Bound the hop: `[:TAGGED*1..1]` is a join; an unbounded star from a celebrity is an outage.

**Don't:**

- Start from an anonymous empty node and walk every inbound edge of a celebrity Hashtag, then continue unbounded.
- “We’ll add a vendor index later” as a substitute for typing the edge.

## Identity and idempotent loads

Loads must be **merge-on-business-key**. `CREATE` on every ingest duplicates the graph. Prefer `MERGE (p:Person {email: $email})` (or the engine’s equivalent) and set mutable properties after.

## Good snippet (lint-clean)

```cypher
MERGE (a:Person {email: $from_email})
MERGE (b:Person {email: $to_email})
MERGE (a)-[r:EMAILED {on: $day}]->(b)
SET r.subject = $subject
```

## See also

- [`graph-vs-relational-decision-tree.md`](graph-vs-relational-decision-tree.md)
- [`../best-practices/type-every-relationship.md`](../best-practices/type-every-relationship.md)
- [`../best-practices/model-for-supernodes.md`](../best-practices/model-for-supernodes.md)

## Sources

- Neo4j getting-started property-graph model (C17, C29) — https://neo4j.com/docs/getting-started/graph-database/ (retrieved 2026-08-14).
