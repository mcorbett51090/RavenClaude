# G0 — Scope

**Slug:** `graph-engineering`
**Depth:** `quick` (FORGE default; research itself is wide-then-deep)
**Date:** 2026-08-14
**Owner:** Matt (marketplace maintainer) via this FORGE run

## Clarification answers

| Question | Answer |
|---|---|
| What “graph engineering” means | **P1 candidate plus RavenClaude internals.** Property graphs, knowledge graphs, Cypher/Gremlin/SPARQL, graph algorithms, GraphRAG. Not GraphQL. Not computational/ML graphs. Also: using graphs *inside* RavenClaude (plugin dependency graphs, memory/knowledge graphs, decision/claim graphs). |
| What this run ships if useful | **Full candidate plugin.** 2–3 agents including GraphRAG, knowledge, skills, commands, and a Cypher/graph-shape linter. |
| Primary user | **Both — client first.** Client/consulting craft ships so any consumer repo can use it; internal RavenClaude uses consume it later. |

## Scoped intent

Research graph engineering (property-graph and RDF/knowledge-graph data modeling, traversal query languages, graph algorithms, and GraphRAG) wide then deep; decide whether RavenClaude should ship a dedicated plugin for that craft; if yes, produce a phased plan and then build a full `graph-engineering` plugin. The plugin sits in the gap already named in `docs/plugin-candidates-2026-06-13.md` §4 (`graph-knowledge-engineering`, P1): `database-engineering` owns relational OLTP; `ai-rag-engineering` owns vector RAG; neither owns graph modeling or graph-augmented retrieval. First consumers are client engagements (“should this be a graph?”, “write this Cypher”, “GraphRAG vs vector”). Second consumers are RavenClaude internals (marketplace/plugin topology, memory/knowledge graphs already gestured at in `memory-engineering`, decision/claim graphs). GraphQL (`graphql-engineering`) and Microsoft Graph API (`microsoft-graph`) stay out.

## Out of scope

- GraphQL schema/server/federation craft (`graphql-engineering` already owns it)
- Microsoft Graph / Entra / M365 API (`microsoft-graph` already owns it)
- Computational / autodiff / ML graphs
- Replacing or absorbing `database-engineering`, `ai-rag-engineering`, or `memory-engineering`
- Standing up a production graph database as a hosted service
- Rewriting RavenClaude’s memory or FORGE claim graph as a required runtime in this run (document the seam; do not make the plugin depend on a live graph store)
- A second plugin. Internals are *uses of* this plugin, not a sibling plugin

## Ultraplan triage

**Stay local.** The idea is large (new plugin, multi-file) but not cloud-suited: it needs this marketplace’s plugin conventions, existing seams, and layout/frontmatter gates. Privacy is clean (no customer data). Do not hand to Ultraplan.

## Success signal

A usefulness verdict grounded in a sourced claims table. If useful: a `/plugin install`-able `graph-engineering` plugin whose agents route “graph vs relational”, “property vs RDF”, “GraphRAG vs vector RAG”, and “write/lint this traversal query”, plus a written internal-use seam (what RavenClaude may consume later without this run wiring a live graph).

## Named owner

Matt. Implementation lands on `forge/graph-engineering` in the provisioned worktree.
