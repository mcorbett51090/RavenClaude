# ai-rag-engineering

A **AI / RAG Engineering specialist team** for a RAG architect, ML engineer, or AI product lead accountable for answer quality, retrieval, and serving cost. It fixes retrieval before generation, treats chunking as a retrieval decision, evals before it ships, and reads context-window and token economics rather than assuming more context is better.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Stack-flexible, corpus-explicit (greenfield RAG | hybrid-search upgrade | eval-before-ship | cost-reduction).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `rag-architect-lead`, `retrieval-eval-analyst`, `ingestion-chunking-specialist`, `llm-serving-cost-specialist` |
| **5 skills / commands** | `build-rag-eval` · `diagnose-retrieval` · `tune-chunking` · `budget-tokens` · `ground-and-guardrail` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · rag-eval-sheet.md · serving-cost-sheet.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, user data / prompt PII) in generated deliverables |
| **`scripts/ai_rag_engineering_calc.py`** | stdlib calculator — `retrieval-eval` · `token-cost` · `chunk-budget` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ai-rag-engineering@ravenclaude
```

## Quickstart

> "Our RAG gives wrong answers — is it the model or the retrieval?"

The `rag-architect-lead` scopes the problem, routes to `retrieval-eval-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a model-training/fine-tuning lab, an MLOps platform team, or a data-governance/privacy authority. It does not train base models, run cluster ops, or make data-privacy/compliance determinations — those route to the qualified authority.
