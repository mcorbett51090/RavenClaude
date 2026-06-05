---
name: llm-routing-ladder
description: "Playbook for designing a cost-optimised model routing ladder: classifying request complexity, wiring the triage→escalate flow, measuring cost-per-resolved-task, and avoiding the common over-provisioning traps. Owned by claude-app-ops-engineer and claude-solution-architect."
---

# LLM Routing Ladder

## When to invoke

- Designing the model-selection strategy for a new Claude app.
- Monthly cost is higher than expected and "use Opus for everything" is the de-facto policy.
- Latency requirements vary across request types and a single model isn't the right answer.
- Evaluating whether a task-routing layer is worth the added complexity.

## The core concept

A routing ladder directs each request to the cheapest model that resolves it correctly. The metric is **cost-per-resolved-task**, not tokens or per-call cost.

```
Incoming request
    │
    ▼
[Triage classifier — Haiku]  ←─ cheap, fast, binary classification
    │
    ├─ Simple  ──────────────► [Haiku handler]  → resolved? → done
    │
    ├─ Medium  ──────────────► [Sonnet handler] → resolved? → done
    │                                                    │ no
    └─ Complex ──────────────► [Opus handler]   ◄────────┘
```

## Step 1 — Define complexity tiers

| Tier | Characteristics | Default model |
|---|---|---|
| Simple | Single-turn, factual lookup, <500 token output, no tool use | Haiku |
| Medium | Multi-step, moderate reasoning, tool use with ≤3 calls | Sonnet |
| Complex | Long chain-of-thought, multi-tool orchestration, high-stakes output | Opus |

Write explicit definitions for your domain — "simple" for a customer support bot differs from "simple" for a code review agent.

## Step 2 — Triage classifier design

The triage step is itself a Haiku call (or a heuristic) that returns a tier label:

```python
TRIAGE_PROMPT = """Classify the following user request into one of three tiers:
- simple: factual lookup, one-step task, no reasoning chain needed
- medium: multi-step, moderate reasoning or tool use
- complex: requires deep reasoning, long output, or high-stakes judgment

Return ONLY the tier label. Request: {request}"""

def classify(request: str) -> str:
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": TRIAGE_PROMPT.format(request=request)}]
    )
    return resp.content[0].text.strip().lower()
```

Cache the triage result for identical requests (same hash) to avoid paying the classifier cost twice.

## Step 3 — Escalation on uncertainty

Simple and medium handlers should detect uncertainty and escalate:

```python
UNCERTAINTY_SIGNALS = [
    "I'm not sure", "I cannot determine", "this requires",
    "outside my knowledge", "I would need more"
]

def should_escalate(response_text: str) -> bool:
    return any(s in response_text for s in UNCERTAINTY_SIGNALS)
```

Escalation is one tier at a time — Haiku → Sonnet → Opus. Never skip tiers unless the triage classified complex from the start.

## Step 4 — Measure cost-per-resolved-task

```python
# Track per request:
# - model used
# - input_tokens, output_tokens, cache_read_input_tokens
# - resolved: bool (from your eval / user feedback)
# Then compute:
cost_per_resolved = total_cost / resolved_count
# Compare across ladder configs; the goal is lower cost_per_resolved, not lower per-call cost
```

A ladder that escalates 40 % of calls to Opus may be more expensive than running Sonnet everywhere if Haiku's resolution rate is low. Measure before assuming the ladder helps.

## Step 5 — Routing ladder + Batch API

For async / offline workloads (nightly reports, bulk classification, eval runs):

- Run the **full batch** at Haiku first (50 % discount via Batch API).
- Flag low-confidence responses for a second Sonnet pass.
- Only Opus-escalate the residual requiring expert reasoning.
- Batch mode adds ~15 min latency; never use for interactive user requests.

## Cost model table (reference — verify current pricing)

| Model | Input cost | Cache-read cost | Batch discount |
|---|---|---|---|
| Haiku | low | 10 % of input | 50 % |
| Sonnet | medium | 10 % of input | 50 % |
| Opus | high | 10 % of input | 50 % |

`[verify-at-build]` — pricing changes; retrieve from `knowledge/model-selection-and-2026-capability-map.md` before quoting.

## Pitfalls

- Using the routing ladder as an excuse to avoid prompt optimisation — a well-engineered Sonnet prompt often beats a poorly-engineered Opus call at 1/5 the cost.
- Not pinning the triage classifier's model — a Sonnet triage that costs as much as a Haiku resolution defeats the purpose.
- Treating the ladder as set-and-forget — measure resolution rate per tier monthly; model capability changes can shift which tier owns which request type.
- Adding a ladder to a low-volume app (< 1 000 req/day) — the engineering cost rarely pays back below that volume.
