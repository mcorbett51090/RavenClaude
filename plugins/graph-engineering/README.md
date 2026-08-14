# graph-engineering

> The **graph engineering** team for Claude Code — property graphs, knowledge graphs, traversal queries, and GraphRAG *construction*. Two specialists: one decides whether this is a graph and how to model it; the other writes bounded Cypher / ISO GQL / Gremlin / SPARQL. Answers the questions a generic database or RAG engineer cannot safely answer: **should this be a graph?**, **LPG or RDF?**, **why is this `*` path slow?**, **GraphRAG or stay with BM25?**

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

**Not GraphQL.** That is [`graphql-engineering`](../graphql-engineering/). **Not the Microsoft Graph API.** That is [`microsoft-graph`](../microsoft-graph/).

## What it does

| You ask | It returns |
|---|---|
| "Should this workload be a graph?" | A graph-vs-relational verdict, a neighbor hand-off if not, or an LPG vs RDF pick if yes |
| "Model this as a property graph" | Labels, typed directed relationships, identity keys, a supernode plan |
| "Write this Cypher / GQL" | A **bounded**, **typed** traversal the user runs, plus index advice |
| "Why is this `MATCH (a)-[*]->(b)` slow?" | Unbounded-path diagnosis + a rewritten pattern with an upper bound |
| "Stand up GraphRAG over this corpus" | Extract → index architecture **after** a BM25 / no-graph baseline lost; eval handed to `ai-rag-engineering` |

**Four rules it never breaks:** *type every relationship*, *bound every variable-length path*, *treat supernodes as a modeling problem*, and *do not pick GraphRAG until BM25 lost*.

## What's inside

- **2 agents** — `graph-data-modeler` (graph-vs-relational, LPG vs RDF, supernodes, GraphRAG construction) and `graph-query-engineer` (Cypher taught first, then ISO GQL, Gremlin, SPARQL; GraphRAG query patterns).
- **4 skills / 4 commands** — `choose-graph-or-not`, `model-property-graph`, `write-graph-query`, `construct-retrieval-graph`.
- **4 knowledge files** — graph-vs-relational decision tree, LPG modeling catalog, dated 2026 language/engine map, GraphRAG construction.
- **6 best-practice rules** — typed relationships, bounded paths, supernodes, GQL-as-standard, algorithms-as-library, GraphRAG humbling baseline.
- **3 templates** — graph data model, query-language decision, retrieval-graph design.
- **1 advisory hook** — `flag-graph-smells.sh` (unbounded `*`, untyped `-[]-`, anonymous `()-` expansion).
- **1 stdlib linter** — `scripts/lint_graph_shape.py` (shape checks, not a parser).

## How it seams with adjacent plugins

```
graph-engineering        →  property-graph / RDF craft, traversals, GraphRAG construction
database-engineering     →  when NOT a graph (OLTP, ad-hoc SQL, known-schema records)
ai-rag-engineering       →  vector / BM25+vector hybrid, chunking, recall@k
memory-engineering       →  whether a memory graph (paradigm III.a) beats BM25
graphql-engineering      →  GraphQL schema / resolvers — not a property graph
microsoft-graph          →  Microsoft Graph API / Entra / M365 — not an LPG
microsoft-fabric         →  Fabric Graph SKU / OneLake / CU billing
```

## Tooling stance

**Advisory only.** Agents emit Cypher / ISO GQL / openCypher / Gremlin / SPARQL snippets **you** run. This plugin does not connect to Neo4j, Fabric Graph, Spanner Graph, or Neptune.

ISO/IEC 39075:2024 **GQL** is the property-graph standard. **Cypher** is the lingua franca taught first. SPARQL is the RDF language. Gremlin is the TinkerPop language. Engine versions carry retrieval dates — re-verify before pinning in a client deliverable. See [`knowledge/graph-languages-and-engines-2026.md`](knowledge/graph-languages-and-engines-2026.md).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install graph-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
