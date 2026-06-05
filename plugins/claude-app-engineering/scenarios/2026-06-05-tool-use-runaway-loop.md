---
scenario_id: 2026-06-05-tool-use-runaway-loop
contributed_at: 2026-06-05
plugin: claude-app-engineering
product: tool-use
product_version: "unknown"
scope: likely-general
tags: [tool-use, agentic-loop, runaway, max-iterations, idempotency, stop-reason, pause-turn]
confidence: high
reviewed: false
---

## Problem

A manual agentic loop (Messages API, `while True:` calling tools and feeding results back) would occasionally never terminate on a small fraction of inputs — the same tool got called with the same arguments over and over, the token bill for that one request spiked into the dollars, and a side-effecting tool (`create_ticket`) fired several duplicate tickets before someone killed the process. It only showed up under production load because the triggering inputs were rare.

## Constraints context

- A hand-rolled loop, not the SDK tool runner: the team wanted human-in-the-loop approval on one tool, so they wrote the loop themselves and owned the termination logic.
- The loop's exit condition was `if response.stop_reason == "end_turn": break` — and **only** that. Anything else continued.
- One tool (`search_kb`) sometimes returned an empty/ambiguous result; the model would re-call it with a slightly reworded query, get the same empty result, and try again — a soft loop with no hard ceiling.
- `create_ticket` was not idempotent: each call created a new ticket, so a redundant tool call = a duplicate ticket, not a no-op.

## Attempts

- Tried: lowering `max_tokens` to "cut off" runaway requests. Wrong lever — it truncated *legitimate* long answers mid-output (a `max_tokens` stop) without stopping the *loop*, which is about iteration count, not per-response length.
- Tried: a system-prompt instruction ("do not call the same tool more than twice"). Helped some inputs, not reliably — a prompt is a nudge, not a guarantee; the rare looping inputs still slipped through.
- Tried (the moves that worked, together):
  1. A **hard iteration cap** in the loop (`for _ in range(MAX_STEPS)`) with an explicit "couldn't resolve in N steps" fallback — the deterministic backstop the prompt can't provide.
  2. **Handling every stop reason**, not just `end_turn` — in particular `pause_turn` (server-side tool loop hit its limit; re-send to resume, don't treat as done or as an error) and `max_tokens` (raise the cap or stream, don't loop).
  3. Making `create_ticket` **idempotent** on a client-supplied dedup key, so a redundant call is a safe no-op instead of a duplicate side effect.

## Resolution

**An agentic loop needs a deterministic ceiling and idempotent effects — the model's judgment is not the termination guarantee.** Three layers, none optional:

1. **Cap the iterations in code.** `for _ in range(MAX_STEPS)`, not `while True`. When the cap trips, return a graceful "unresolved" result, log it, and (if appropriate) escalate to a human — don't silently spin. This is the loop-guardrail discipline (house opinion: guardrail the loop).
2. **Branch on the real `stop_reason` set**, not just `end_turn`: `tool_use` (execute + continue), `pause_turn` (re-send to resume a server-side-tool loop — re-sending without an extra "continue" user message is the documented resume `[verify-at-use]`), `max_tokens` (raise/stream, don't loop), `refusal` (surface, don't retry the same prompt), `end_turn` (done).
3. **Make every side-effecting tool idempotent** on a stable key. Under any loop — agentic or retried — a tool *will* sometimes be called more than once; a non-idempotent effect turns a redundant call into a duplicate ticket/charge/email. Idempotency converts "ran twice" from a bug into a no-op.
4. **Prefer the SDK tool runner when you don't need custom loop control** — it owns the loop and termination for you; hand-roll only when you genuinely need approval gates or custom logging (which this team did, so the manual cap was theirs to add).

The trap is that the loop "works" on every input you tested, because the looping inputs are rare and only appear under real traffic. The ceiling has to be structural (a counter), not behavioral (a prompt), or the rare input eventually finds the gap.

**Action for the next engineer:** if a request's token bill spikes or a side effect fired N times, look for an unbounded `while`-loop with an `end_turn`-only exit and a non-idempotent tool. Add the iteration cap and the dedup key together — fixing one without the other just changes which symptom you see.

Cross-reference: complements the loop-guardrail and tool-idempotency best-practices ([`../best-practices/agent-guardrail-the-loop.md`](../best-practices/agent-guardrail-the-loop.md), [`../best-practices/tool-idempotency-for-effects.md`](../best-practices/tool-idempotency-for-effects.md)) and [`../knowledge/tool-use-and-structured-output.md`](../knowledge/tool-use-and-structured-output.md). The "agent vs workflow" framing (was a full agent even the right shape?) → [`../knowledge/agent-orchestration-patterns.md`](../knowledge/agent-orchestration-patterns.md) and the new agent-vs-workflow decision tree.
