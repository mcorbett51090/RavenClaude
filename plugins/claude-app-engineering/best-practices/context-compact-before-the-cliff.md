# Compact context before the window cliff, not after

**Status:** Pattern
**Domain:** Context engineering / cost
**Applies to:** `claude-app-engineering`

---

## Why this exists

A Claude session that grows turn-by-turn toward the context limit hits a hard
wall: the model either returns a truncation error, starts hallucinating over a
degraded context, or forces an expensive refill. Teams that react to the cliff
rather than engineer around it pay for it in reliability and latency. Proactive
compaction (summarise + prune + handoff) keeps cost linear and the context
signal-dense rather than history-dense.

## How to apply

Track the rolling `input_tokens` count from the API response's `usage` block.
When it crosses ~70–75% of the model's context limit, trigger a compaction step
before the next user turn.

```python
COMPACT_THRESHOLD = 0.72  # 72% of the model's context limit

def needs_compaction(usage, model_limit):
    return usage.input_tokens / model_limit > COMPACT_THRESHOLD

# Compaction step:
summary = client.messages.create(
    model="claude-haiku-4-5",   # cheap + fast; summary not a reasoning task
    max_tokens=1024,
    messages=session.messages,
    system="Summarise this conversation in < 800 tokens preserving all open "
           "tool calls, stated goals, and constraints. Omit pleasantries.",
)
session.messages = [
    {"role": "user", "content": summary.content[0].text},
]
```

Alternatively use the Claude Agent SDK's built-in context compaction if you are
running an Agent SDK session — it automates this step.

**Do:**
- Compact on a token-count threshold, not a turn-count heuristic.
- Preserve all open goals, constraints, and pending tool state in the summary.
- Use a cheap, fast model (Haiku) for the summarisation; it is not a hard task.
- Log compaction events and their before/after token counts for cost audit.

**Don't:**
- Wait for a `context_length_exceeded` error to trigger compaction.
- Discard the raw message history without archiving it (you may need it for evals
  or debugging).
- Let the compaction summary itself grow unbounded across many compaction cycles.

## Edge cases / when the rule does NOT apply

- Batch API jobs with a hard input size: pre-trim to fit rather than compact
  mid-job.
- Single-shot tasks (no session): no rolling context, so no compaction needed.
- When the task genuinely requires the full history (forensic audit, code review
  of an entire session): budget the larger model, don't compact.

## See also

- [`../agents/claude-app-ops-engineer.md`](../agents/claude-app-ops-engineer.md) — monitors token usage and cost
- [`./context-budget-the-1m-window.md`](./context-budget-the-1m-window.md) — budgeting context holistically
- [`./cost-and-secrets-observability.md`](./cost-and-secrets-observability.md) — tracking `input_tokens` in telemetry

## Provenance

Codifies the context-engineering guidance in
`knowledge/context-engineering-2026.md` (retrieved 2026-05-28) §"Context
compaction". The 70–75% threshold is a practical operating margin; adjust for
your model's actual limit from the dated capability map.

---

_Last reviewed: 2026-06-05 by `claude`_
