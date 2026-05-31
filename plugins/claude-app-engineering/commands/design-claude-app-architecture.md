---
description: "Choose the build surface and architecture for a Claude-backed feature — traverse the decision tree (Workbench/Messages/Agent SDK/Managed Agents), right-size the model with a routing ladder, and decide RAG vs long-context, measuring cost-per-resolved-task."
argument-hint: "[the feature, e.g. 'a support-ticket triage and drafting assistant']"
---

# Design a Claude app architecture

You are running `/claude-app-engineering:design-claude-app-architecture`. Turn the user's feature (`$ARGUMENTS`) into an architecture decision — the right build surface, the right model tier, and the right context strategy — the work the `claude-solution-architect` agent owns. A classification call isn't an agent; don't give it an agent loop.

## When to use this

You are starting a new Claude-backed feature (or re-evaluating one) and need the surface/model/context shape settled before implementation. NOT for tuning an existing prompt (that is `/claude-app-engineering:engineer-prompt-and-context`).

## Steps

1. **Pick the build surface by traversing the decision tree on observable inputs** (`agent-pick-the-build-surface.md`): are you still prototyping a prompt (Workbench); a single-shot call (Messages API / Client SDK); does Claude need to autonomously read/run/edit + use tools *in a loop* (Agent SDK); and should that loop run in your process or be Anthropic-hosted (Managed Agents). Reaching for the Agent SDK "because we're building an agent" when a Messages call suffices is the named anti-pattern.
2. **Right-size the model with a routing ladder** (`right-size-with-a-routing-ladder.md`): a cheap model (Haiku) triages/classifies, escalate-on-uncertainty to the balanced default (Sonnet), reserve the flagship (Opus) for the hard reasoning tail — and measure **cost-per-resolved-task**, not raw token count, because a failed-and-rerouted cheap call costs more than starting on Sonnet.
3. **Decide RAG vs long-context by corpus size** (`rag-skip-it-under-200k.md`): under ~200K tokens, prefer putting the corpus in-context over a retrieval pipeline you have to build and maintain; reach for RAG when the corpus genuinely outgrows the window.
4. **Budget the context window deliberately** (`context-budget-the-1m-window.md`): plan what the *right set* of tokens is at each step and how stale history gets compacted — a 1M window is not a license to dump the whole corpus "just in case" (context rot degrades quality and costs money).
5. **Plan the reliability and cost posture up front** (`reliability-stream-and-back-off.md`, `cost-and-secrets-observability.md`): streaming for interactive latency, exponential backoff + jitter on 429, and observability on cost/secrets from day one.
6. Hand the downstream pieces to the right command: caching to `/claude-app-engineering:add-prompt-caching`, evals to `/claude-app-engineering:build-eval-harness`, MCP/tools to `/claude-app-engineering:wire-mcp-server-or-tool`, prompt/context to `/claude-app-engineering:engineer-prompt-and-context`.

## Guardrails

- Don't default to the Agent SDK for a single-shot call, or to Managed Agents when you already operate the infra they'd duplicate.
- Defaulting every request to Opus is the most common way an app overspends without buying quality — ladder it and measure resolution.
- "Retrieve everything just in case" tanks quality and cost — under 200K, long-context usually beats a RAG pipeline.
