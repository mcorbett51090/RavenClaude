# memory-engineering

A **memory-engineering specialist team** for the engineer who has to design, cost, secure and retire an agent's durable memory store. It answers six questions in order — what earns a write, which paradigm, which surface holds the bytes, what makes it forget, what a delete leaves behind, and what it costs per correct answer — and it makes you prove the no-memory baseline loses before you build anything.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, capability-grounding, structured output) and the always-on **Memory Engineering Protocol** in the core constitution. **Requires `ravenclaude-core@>=0.238.0`** — the release that adds that protocol.

> **Advisory only.** Nothing in this plugin reads or mutates a real memory store. The calculator is decision-support you feed with your own numbers; it ships zero vendor constants.

## What you get

| Surface | Contents |
|---|---|
| **3 agents** | [`memory-architect-lead`](agents/memory-architect-lead.md), [`memory-retention-and-erasure-engineer`](agents/memory-retention-and-erasure-engineer.md), [`memory-eval-cost-analyst`](agents/memory-eval-cost-analyst.md) |
| **6 skills / 6 commands** | `choose-memory-paradigm` · `map-memory-surface` · `design-forgetting-policy` · `budget-memory-costs` · `memory-poisoning-review` · `build-memory-eval` |
| **5-file knowledge bank** | paradigms + corrections · the shipped memory surfaces, dated · unit economics · security & privacy (OWASP ASI06) · Mermaid decision trees |
| **8 best-practice rules** | one per house opinion — [`best-practices/`](best-practices/README.md) |
| **4 templates** | design record · eval sheet · cost sheet · threat model |
| **3 scenarios** | dated, unverified engagement narratives — [`scenarios/`](scenarios/README.md) |
| **1 advisory hook** | flags an unsourced benchmark number and a metric cited with no baseline in generated deliverables |
| **`scripts/memory_engineering_calc.py`** | stdlib calculator — `cost-per-correct` (the spine) · `amortize` · `store-growth` · `cache-economics` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install memory-engineering@ravenclaude
```

## Quickstart

> "We're about to give our agent long-term memory. Should we, and what will it cost us?"

[`memory-architect-lead`](agents/memory-architect-lead.md) makes the no-memory and lexical-retrieval baselines compete first, then picks the paradigm and the surface, names who holds the bytes and who executes the write, and routes: retention and erasure to [`memory-retention-and-erasure-engineer`](agents/memory-retention-and-erasure-engineer.md), break-even and cost per correct answer to [`memory-eval-cost-analyst`](agents/memory-eval-cost-analyst.md), and the write-path poisoning audit to the [`memory-poisoning-review`](skills/memory-poisoning-review/SKILL.md) skill that core's `security-reviewer` invokes.

## Where it stops

- **Whether to build an agent at all, and where state sits in its topology** → [`ai-agent-engineering`](../ai-agent-engineering/). That plugin decides whether an agent should remember; this one engineers the memory system itself.
- **Offensive testing** → [`ai-red-teaming`](../ai-red-teaming/). That plugin owns the ASI06 attack taxonomy and runs the attack; this one owns the defensive design half and cites their taxonomy rather than restating it.
- **DSAR process, legal basis, records-retention policy** → [`data-governance-privacy`](../data-governance-privacy/). This team names the engineering residue a delete leaves behind — embeddings, derived indexes, version history — it does not make the legal call.
- **Corpus retrieval and chunking** → [`ai-rag-engineering`](../ai-rag-engineering/). **Generic eval harnesses and ship-gates** → [`llm-evaluation-engineering`](../llm-evaluation-engineering/). **The Claude app itself** → [`claude-app-engineering`](../claude-app-engineering/).

## What it is not

Not an agent-topology practice, a retrieval team, an eval vendor, a red-team, or a privacy authority. It certifies nothing and makes no legal determination. Vendor surface details move fast — every dated fact in [`knowledge/`](knowledge/memory-surfaces-2026.md) carries a `**Last verified:**` line, and the freshness sweep reports **age, never correctness**. Re-verify before quoting.
