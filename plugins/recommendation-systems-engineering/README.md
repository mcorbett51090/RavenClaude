# recommendation-systems-engineering

The **recsys layer** — turning interaction data into ranked recommendations through a candidate-generation → ranking → re-ranking pipeline, with honest offline **and** online evaluation. Distinct from generic MLOps (`ml-engineering`) and from query→document search (`search-relevance-engineering`): this plugin owns the user→item recommendation problem.

## What's inside

| Component | Items |
|---|---|
| Agents | 2 — `recsys-architect`, `recsys-implementation-engineer` |
| Skills | 3 — `choose-recsys-approach`, `evaluate-recommenders`, `handle-cold-start-and-serving` |
| Knowledge | 2 — approach decision tree, evaluation & serving |
| Templates | 2 — recsys design doc, eval report |

## When to use it

- **"Collaborative filtering, content-based, hybrid, or a two-tower model?"** → `recsys-architect`
- **"How should our candidate-gen → ranking → re-ranking pipeline be structured?"** → `recsys-architect`
- **"New users and new products recommend badly — cold-start plan?"** → `handle-cold-start-and-serving`
- **"Our model won offline but the A/B was flat — why?"** → `recsys-architect` (offline-vs-online gap diagnosis)
- **"Build the retrieval/ranking stage / set up offline eval / serve within a latency budget."** → `recsys-implementation-engineer`

## House line

**Ship a baseline before a neural net; offline wins must survive an online A/B.** Popularity is undefeated more often than anyone expects, temporal splits are the only valid ones, and train/serve parity is what separates a model that wins offline from one that wins in production.

## Seams (what this plugin does NOT own)

| Need | Route to |
|---|---|
| Training infra, feature store, model registry | `ml-engineering` |
| Keyword / semantic search (query→document) | `search-relevance-engineering` |
| A/B design, power/MDE, guardrail stats | `experimentation-growth-engineering` / `applied-statistics` |
| Interaction/feature schema + indexing | `database-engineering` |
| Serving service/queue/caching | `backend-engineering` |

## Requirements

Requires `ravenclaude-core@>=0.7.0` (inherits the Capability Grounding Protocol, Structured Output Protocol, and the domain-neutral team roster).

## Install

```
/plugin marketplace update ravenclaude
/plugin install recommendation-systems-engineering@ravenclaude
```

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (roster, routing, house opinions, output contract).
