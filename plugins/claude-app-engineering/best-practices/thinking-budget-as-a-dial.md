# Treat thinking budget as a cost dial, not a boolean

**Status:** Pattern
**Domain:** Extended thinking / cost
**Applies to:** `claude-app-engineering`

---

## Why this exists

Extended / adaptive thinking is a real quality lever — but `budget_tokens` (or
the equivalent adaptive-thinking control `[verify-at-build]`) isn't a flag you
flip once. Teams that set a large fixed budget for every request over-spend on
easy tasks that don't need deep reasoning, and pay for thinking tokens that don't
improve the answer. The budget should track task difficulty, not be a deployment
constant.

## How to apply

Classify each request at the routing layer (cheap fast Haiku call or a heuristic)
and assign a thinking budget tier:

| Task tier | Observable signal | Budget guidance |
|---|---|---|
| Simple / extraction | Single-fact lookup, reformatting, classification | Off or minimum `[verify-at-build]` |
| Standard reasoning | Summarisation, multi-step tool use, moderate analysis | Low-mid budget |
| Hard reasoning tail | Multi-file code change, deep analysis, adversarial debate | High or max budget |

```python
def thinking_config(task_tier: str) -> dict:
    # Adjust budget thresholds to your workload — verify minimums at build
    tiers = {
        "simple":   {"type": "disabled"},
        "standard": {"type": "enabled", "budget_tokens": 4096},
        "hard":     {"type": "enabled", "budget_tokens": 16000},
    }
    return tiers[task_tier]

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking=thinking_config(classify_task(user_request)),
    messages=messages,
)
```

**Do:**
- Classify task difficulty at the routing layer before setting the budget.
- Keep the budget configuration in the dated capability map — thinking params
  change per model version.
- Track thinking-token spend separately in your cost dashboard
  (`usage.cache_creation_input_tokens` vs `thinking_tokens`).

**Don't:**
- Hard-code a large `budget_tokens` for all requests as a "quality default" —
  you're paying for thinking on every greeting and reformatting task.
- Conflate the thinking-budget dial with the model-tier dial: budget controls
  depth on the same model; model tier upgrades the ceiling.
- Mix `temperature` + thinking in the same request — the combination is not
  supported `[verify-at-build]`.

## Edge cases / when the rule does NOT apply

- Pure data transformation or extraction: thinking adds cost with no quality
  benefit; turn it off.
- Evals run via Batch API: thinking config should match the production tier for
  the task being evaluated — mismatched thinking makes the eval unrepresentative.

## See also

- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns thinking config design
- [`./context-keep-thinking-config-stable-and-dated.md`](./context-keep-thinking-config-stable-and-dated.md) — stability rule that this complements
- [`./right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) — model-tier decision is a separate, upstream dial

## Provenance

Codifies the thinking-cost discipline from
`knowledge/context-engineering-2026.md` (retrieved 2026-05-28) §"Thinking-block
cost". Budget-token minimums and model support are version-specific — always
re-verify against the dated capability map.

---

_Last reviewed: 2026-06-05 by `claude`_
