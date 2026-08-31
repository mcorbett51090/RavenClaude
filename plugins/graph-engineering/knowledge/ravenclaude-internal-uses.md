# RavenClaude internal uses (examples only)

**Last reviewed:** 2026-08-14

[unverified — premise not disconfirmed: documenting internals (36) and dual-write-as-defect (35) are design inferences; phases stay one reversible file each and may be skipped]

Three **labeled-property-graph sketches**. Paste them into *your* playground if you want. They are not a marketplace service. **Wiring these to a required graph server is out of scope; no hook or CI depends on this file.**

## 1. Plugin enablement topology

```cypher
MERGE (m:Marketplace {name: 'ravenclaude'})
MERGE (p:Plugin {name: 'graph-engineering'})
MERGE (c:Plugin {name: 'ravenclaude-core'})
MERGE (p)-[:REQUIRES {floor: '0.7.0'}]->(c)
MERGE (m)-[:LISTS]->(p)
```

A plugin **depends on** core; the marketplace **lists** plugins. Useful for “what breaks if I disable X?” — as a drawing, not as a live store.

## 2. Memory / knowledge graph (already owned as a paradigm)

`memory-engineering` already classifies GraphRAG / Zep / Graphiti as stores with a bill. Sketch only:

```cypher
MERGE (e:Entity {key: $stable_key})
MERGE (f:Fact {id: $fact_id})
MERGE (e)-[:ASSERTED {as_of: $day}]->(f)
```

Do **not** stand this up inside RavenClaude from this plugin. Paradigm choice stays with `memory-architect-lead`.

## 3. FORGE claim / decision graph

```cypher
MERGE (c:Claim {id: '36'})
MERGE (ph:Phase {id: '8'})
MERGE (ph)-[:DEPENDS_ON {kind: 'inference'}]->(c)
```

This is the G3b edge made visible. The run dir (`.ravenclaude/runs/forge/<slug>/`) remains the source of truth — files, not a graph database.

## Closing

These sketches teach LPG shape on *this* repo's nouns. They are not a reason to add Neo4j, FalkorDB, or Spanner to marketplace CI.
