# Graph-engineering Plugin — Team Constitution

> Team constitution for the `graph-engineering` Claude Code plugin. Two specialist agents — the **graph-data-modeler** and the **graph-query-engineer** — plus a knowledge bank, skills, templates, best-practice rules, an advisory hook, and a stdlib shape linter, all aimed at one thing: **the engineering of graph data** — deciding when a graph is the right store, modeling it so traversals stay cheap, and constructing a retrieval graph only after a non-graph baseline has lost.
>
> **Inherits `ravenclaude-core` protocols.** This file is **domain-specific** to property-graph / RDF / GraphRAG-construction work. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`graph-data-modeler`](agents/graph-data-modeler.md) | Graph-vs-relational; LPG vs RDF; labels / relationship types / identity / temporal edges / supernodes; **GraphRAG construction** (extract → index architecture). Traverses the decision tree first. | "should this be a graph?"; "LPG or RDF?"; "this celebrity node kills traversals"; "stand up GraphRAG over this corpus" |
| [`graph-query-engineer`](agents/graph-query-engineer.md) | Bounded traversals in **Cypher (taught first)**, ISO GQL, openCypher, Gremlin, SPARQL; path cost; algorithm-library vs traversal; **GraphRAG local/global/DRIFT query patterns**. Advisory snippets only. | "write this Cypher/GQL"; "why is this `*` path slow?"; "Gremlin vs SPARQL for this hop"; "local vs global GraphRAG search?" |

Two agents is one coherent team split along the natural seam: **should this be a graph and how is it shaped** vs **write the bounded traversal**. GraphRAG *construction* lives on the modeler; GraphRAG *query patterns* live on the query engineer. (Per the marketplace house rule, domain plugins may ship specialist *doing*-agents; they must not fork core's *review* roles.)

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Should this be a graph?" / "LPG or RDF?" / "this celebrity node"** → `graph-data-modeler` (drives `choose-graph-or-not` / `model-property-graph`).
- **"Stand up GraphRAG / multi-hop corpus synthesis / community summaries"** → `graph-data-modeler` first (*should we build a retrieval graph and how?* via `construct-retrieval-graph`); then `graph-query-engineer` for the traversal / DRIFT-local pattern.
- **"Write this Cypher / GQL / Gremlin / SPARQL" / "why is this `*` path slow?"** → `graph-query-engineer` (drives `write-graph-query`).
- **Multi-row transactions, ad-hoc SQL, known-schema records — when NOT a graph** → `database-engineering`.
- **Vector / BM25+vector hybrid, chunking, recall@k, token cost** → `ai-rag-engineering`.
- **"Should we pay for a memory graph / III.a vs BM25?"** → `memory-engineering` (`memory-architect-lead`). This plugin does **not** re-decide that paradigm.
- **GraphQL schema / resolvers / query-cost** → `graphql-engineering`.
- **Microsoft Graph API / Entra / M365** → `microsoft-graph`.
- **Fabric Graph SKU / OneLake / CU billing / Data Agent preview** → `microsoft-fabric`. This plugin teaches the LPG/GQL **craft** that SKU runs.

**The seams** (this plugin = the engineering of graph data):

| Adjacent concern | Owner |
|---|---|
| When NOT a graph (OLTP, ad-hoc SQL, known schema) | `database-engineering` |
| Vector / hybrid lexical RAG, chunking, recall@k | `ai-rag-engineering` |
| Whether a **memory** graph (paradigm III.a) beats BM25 | `memory-engineering` |
| GraphQL schema / resolvers | `graphql-engineering` |
| Microsoft Graph API / Entra / M365 | `microsoft-graph` |
| Fabric Graph SKU / ops / OneLake | `microsoft-fabric` |
| Warehouse / ELT of non-graph facts | `data-platform` (weak seam — mention only) |

**Do not** edit neighbor `CLAUDE.md` files from this plugin.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Decide graph-vs-relational before labels.** Traverse [`knowledge/graph-vs-relational-decision-tree.md`](knowledge/graph-vs-relational-decision-tree.md). Multi-row transactions + ad-hoc SQL + known schema → `database-engineering`.
2. **Type every relationship; give it a direction.** Untyped `()-[]-()` is a model bug. The hook and linter flag it.
3. **Bound every variable-length path.** Unbounded Cypher `-[*]->` / GQL `{1,}` without an upper bound is a latency bomb.
4. **Treat supernodes as modeling, not vendor trivia.** Type the edge; never expand `()-[]-()` from a celebrity node.
5. **GQL is the standard; Cypher is the lingua franca taught first; Gremlin and SPARQL stay in the field.** Do not name the slash command `/write-gql`.
6. **Algorithms live in libraries** (project a subgraph, then run). Pathfinding / centrality / community are not query-language trivia.
7. **GraphRAG constructs a retrieval graph; it does not pick a memory paradigm.** Needs a humbling non-graph baseline first. Hand III.a vs BM25 to `memory-engineering`; hand chunking / recall@k to `ai-rag-engineering`.
8. **Advisory snippets only.** No live store in this marketplace. No driver, no MCP graph server, no CI that requires Neo4j / Fabric / Spanner / Neptune.
9. **Date every engine / GA / version claim.** Fabric Graph GA stays `[verify-at-use]`.
10. **Do not teach archived Kuzu as the default embed** (repo archived 2025-10-10).

---

## 4. Anti-patterns the agents flag

- Untyped `()-[]-()` / `-[]->` / bare `--` (the hook and linter flag this).
- Unbounded variable-length `-[*]->`, `-[*..]->`, `-[*1..]->`, or GQL `{1,}` with no upper (the hook and linter flag this).
- Anonymous `MATCH ()-` expansion off a high-degree node (the linter flags this).
- Teaching Cypher `*` as if it were ISO GQL (linter WARNING).
- Picking GraphRAG before a BM25 / no-graph baseline has lost.
- Re-deciding memory paradigm III.a inside this plugin.
- Quoting a Fabric Graph / Neptune / Spanner version with **no retrieval date**.
- Teaching archived Kuzu as the current embedded default.
- Connecting to the consumer's graph database from this plugin.
- Treating GraphQL or the Microsoft Graph API as a property graph.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

- **Traverse the decision tree before choosing** ([`knowledge/graph-vs-relational-decision-tree.md`](knowledge/graph-vs-relational-decision-tree.md)).
- Dated engine / language / GA specifics live in [`knowledge/graph-languages-and-engines-2026.md`](knowledge/graph-languages-and-engines-2026.md) and carry `[verify-at-use]`. Re-verify against official docs before quoting or committing a version.
- GraphRAG family descriptions (Microsoft GraphRAG, HippoRAG, LightRAG) are **design-intent**, not bake-off winners. Author-reported metrics stay disclaimed.
- SPARQL is dated **1.1** only in this release. Do not invent SPARQL 1.2 / RDF 1.2 support.

---

## 6. Output contracts

| Agent | Returns |
|---|---|
| `graph-data-modeler` | store decision (graph vs not) / model (LPG\|RDF) / sketch / supernode plan / GraphRAG construct notes if any / neighbor hand-off / verdict |
| `graph-query-engineer` | language (Cypher\|GQL\|Gremlin\|SPARQL) / bounded pattern / index advice / algorithm-vs-traversal / lint result / GraphRAG query mode if any / verdict |

Both end with a one-line **verdict**. Both emit snippets the user runs — they never open a driver.

---

## 7. Skills

| Skill | Primary agent |
|---|---|
| [`choose-graph-or-not`](skills/choose-graph-or-not/SKILL.md) | `graph-data-modeler` |
| [`model-property-graph`](skills/model-property-graph/SKILL.md) | `graph-data-modeler` |
| [`write-graph-query`](skills/write-graph-query/SKILL.md) | `graph-query-engineer` |
| [`construct-retrieval-graph`](skills/construct-retrieval-graph/SKILL.md) | `graph-data-modeler` |

Matching slash commands live under [`commands/`](commands/).

---

## 8. Knowledge bank

| File | Use when |
|---|---|
| [`knowledge/graph-vs-relational-decision-tree.md`](knowledge/graph-vs-relational-decision-tree.md) | Choosing graph vs relational vs RDF vs retrieval-graph |
| [`knowledge/lpg-modeling-catalog.md`](knowledge/lpg-modeling-catalog.md) | Labels, typed directed rels, identity, temporal edges, supernodes |
| [`knowledge/graph-languages-and-engines-2026.md`](knowledge/graph-languages-and-engines-2026.md) | GQL vs Cypher vs Gremlin vs SPARQL; dated engine map |
| [`knowledge/graphrag-construction.md`](knowledge/graphrag-construction.md) | Extract → index → local/global search; cites memory III.a |
| [`knowledge/ravenclaude-internal-uses.md`](knowledge/ravenclaude-internal-uses.md) | Optional LPG sketches of RavenClaude internals — **examples, not a runtime**; not in the gated “4 knowledge” count |

---

## 9. Templates

| Template | Fill when |
|---|---|
| [`templates/graph-data-model.md`](templates/graph-data-model.md) | Before any `CREATE` / DDL |
| [`templates/query-language-decision.md`](templates/query-language-decision.md) | Picking Cypher vs GQL vs Gremlin vs SPARQL + engine |
| [`templates/retrieval-graph-design.md`](templates/retrieval-graph-design.md) | GraphRAG construction — extraction, index, search mode, baseline checkbox |

---

## 10. Best-practices

See [`best-practices/README.md`](best-practices/README.md). Absolute rules: type every relationship, bound variable-length paths, model for supernodes. Strong defaults: GQL-as-standard / Cypher-as-lingua-franca, algorithms-as-library, GraphRAG humbling baseline.

---

## 11. Hooks and linter

- **Hook:** [`hooks/flag-graph-smells.sh`](hooks/flag-graph-smells.sh) — PreToolUse `Edit\|Write\|MultiEdit`, grep-only POSIX ERE. Advisory default. `GRAPH_SMELLS_STRICT=1` → exit 2.
- **Linter:** [`scripts/lint_graph_shape.py`](scripts/lint_graph_shape.py) — stdlib shape checks. `--strict` fails on ERROR. `--self-test` is the CI canary. Not a parser. `.graphql` files are a no-op ("wrong plugin").

Intentional bad examples live **only** under [`scripts/fixtures/`](scripts/fixtures/).
