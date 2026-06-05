---
name: context-budget-planner
description: "Playbook for allocating a Claude context window across system prompt, retrieved documents, conversation history, and tool results — with token-budget formulas, the retrieve-vs-hold decision, and the compaction triggers that prevent context overflow. Owned by prompt-and-context-engineer."
---

# Context Budget Planner

## When to invoke

- Designing a new Claude app's context layout from scratch.
- Getting `context_length_exceeded` errors in production.
- Context costs are high and it's unclear which section is eating the budget.
- Adding retrieval (RAG) or a memory tool to an existing app.

## The five zones

Every Claude request has five token zones. Plan all five before writing a line of code.

| Zone | Typical allocation | Notes |
|---|---|---|
| System prompt + tools | 2 000–8 000 | Stable; cache this block. Place `cache_control` at the end of this zone. |
| Retrieved documents | 20 000–200 000 | Variable; retrieved per-request. Order: most relevant first. |
| Conversation history | 4 000–40 000 | Grows unboundedly; requires compaction. |
| Current user turn | 200–2 000 | The actual request. |
| Thinking budget (if enabled) | 1 000–32 000 | Extended thinking tokens; allocated separately via `budget_tokens`. |

**Rule:** retrieved documents + history + thinking budget must not exceed 80 % of the model's context limit. Reserve 20 % for the output (`max_tokens`).

## Step 1 — Measure your zones

```python
# Count tokens in each zone before building the full request
import anthropic
client = anthropic.Anthropic()

def count_zone_tokens(content: str | list) -> int:
    """Use the token-counting endpoint; don't estimate."""
    resp = client.messages.count_tokens(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": content}]
    )
    return resp.input_tokens
```

Measure once per zone type under real load, not on toy examples. The system prompt rarely stays at its authored size once few-shot examples and XML context sections are added.

## Step 2 — Retrieve vs hold decision

| Condition | Decision |
|---|---|
| Corpus ≤ ~150 K tokens and is stable across requests | Hold in context (one cache-read hit) |
| Corpus > 150 K tokens or frequently changes | Retrieve (RAG, semantic search, Files API) |
| Document is needed on almost every call | Cache with `cache_control`; hold |
| Document is needed < 30 % of calls | Retrieve on demand |

The 150 K threshold is approximate — model a few scenarios using the cost formula in `knowledge/context-engineering-2026.md` before committing.

## Step 3 — History compaction triggers

| Trigger | Action |
|---|---|
| History > 50 % of the zone 3 budget | Summarise oldest turns into a "memory block" and drop them |
| Total context > 70 % of the model's limit | Emergency compaction: summarise + truncate |
| User explicitly requests "start fresh" | Clear history; preserve the system prompt and retrieved context |

Compaction prompt pattern:

```
You are summarising a conversation for a context window.
Summarise the key decisions, facts agreed on, and open questions from the following turns.
Be concise. Output a bullet list. Do NOT include pleasantries or meta-commentary.
```

Store summaries in a session-level `memory` block placed after the system prompt and before new retrieved documents.

## Step 4 — Budget formula

```
safe_context = model_context_limit × 0.80
available_for_dynamic = safe_context - system_tokens - tools_tokens
max_retrieved = available_for_dynamic × 0.70   # leave 30% for history + output
max_history   = available_for_dynamic × 0.25
max_output    = model_context_limit × 0.20      # set as max_tokens

# Example for 200K model:
# safe = 160 000
# system+tools = 6 000 → available = 154 000
# max_retrieved = 107 800 | max_history = 38 500 | max_tokens = 40 000
```

## Step 5 — Thinking budget sizing

Extended thinking `budget_tokens` counts against the context window, not separately. Size it by task:

| Task type | Suggested budget_tokens |
|---|---|
| Analytical / multi-step reasoning | 8 000–16 000 |
| Code generation with correctness checks | 4 000–8 000 |
| Simple Q&A (thinking probably not needed) | 0 (disable thinking) |

Do not set thinking on every call — it adds cost and latency. Enable it on the tasks where the quality delta justifies it (verify with evals).

## Pitfalls

- Estimating tokens from word count (1 word ≈ 1.3 tokens on average, but code and JSON can be 2–3× denser).
- Placing retrieved documents before the system prompt — they break the cache breakpoint and inflate the stable-prefix cost.
- Letting conversation history grow without compaction — context overflow errors in long sessions are nearly always a history management failure.
- Allocating a 32 K thinking budget on every Haiku call — Haiku's thinking support and optimal budget differ from Sonnet; verify in the capability map.
