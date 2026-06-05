---
scenario_id: 2026-06-05-subagent-tried-to-spawn-subagents
contributed_at: 2026-06-05
plugin: ravenclaude-core
product: orchestration
product_version: "n/a"
scope: likely-general
tags: [recursion-guard, orchestrator-worker, hierarchical-dispatch, escalation, handoff, guard-recursive-spawn]
confidence: medium
reviewed: false
---

## Problem

A dispatched `architect` specialist, mid-task, decided the design needed a security review and a data-engineering slice — so it tried to **spawn `security-reviewer` and `data-engineer` itself**, directly, from inside its own focused task. This is the recursion failure the orchestrator-worker pattern exists to prevent: sub-agents freely spawning other sub-agents collapses the observability and loop-safety the hierarchy buys. The `guard-recursive-spawn.sh` hook fired a **warn** verdict (it emits to the event substrate, it does not hard-block), but the deeper fix was behavioral — the specialist should have **escalated a structured handoff to the Team Lead**, not reached for the dispatch tool.

## Context

- Surface: domain-neutral, `ravenclaude-core`. The marketplace follows the **orchestrator-worker / hierarchical** pattern: *only the Team Lead performs dispatching and orchestration* (CLAUDE.md §"Multi-Agent Coordination & Dispatch Rules").
- The core rule the specialist violated: "Sub-agents should not freely spawn or directly invoke other sub-agents." When work has relevance to another specialist, the agent completes its slice and includes a **recommended handoff** note naming the suggested specialist + context — the Team Lead decides whether and how to involve them.
- Two enforcement layers exist and compose: (1) the behavioral rule in the constitution, and (2) `guard-recursive-spawn.sh` (a `warn`-emitting hook wired into the hook-event substrate — see CLAUDE.md §"Structured event substrate"). The hook is a salience signal, not the boundary; the boundary is the dispatch rule itself.
- Why it matters: better observability, easier debugging, reduced risk of loops — exactly the properties that erode when a worker can fan out workers of its own.

## Attempts

- Tried: `architect` directly invokes `security-reviewer` + `data-engineer` from inside its task. Outcome: recursion-guard `warn` event emitted; the spawn pattern is the anti-pattern the hierarchy forbids — no single owner of context, no loop budget, no clean audit trail.
- Tried: have `architect` complete only its own slice (the design) and **stop**, then emit the cross-boundary work as recommendations rather than acting on them. Outcome: the focused task stays focused; the worker doesn't grow a sub-team.
- Tried (the move that worked): `architect` ends its report with a **Structured Output Protocol handoff block** — `handoff_recommendation` naming `security-reviewer` (auth surface in the design) and a second recommendation for `data-engineer` (the warehouse slice), each with context and a confidence float — and returns to the Team Lead. The **Team Lead** then dispatches those two, in parallel or sequence, and synthesizes. Outcome: same downstream work gets done, but through the one orchestrator that owns dispatch, context, and loop-safety.

## Resolution

The defect was a **worker acting as an orchestrator** — spawning peers instead of escalating a recommended handoff. The hierarchy is load-bearing: only the Team Lead dispatches; specialists deliver a slice and hand back structured recommendations. The recursion-guard hook's `warn` is the smoke alarm; the rule it points at is the actual fire boundary.

**Action for the next specialist that finds cross-boundary work:** do **not** spawn the other specialist. Finish your own slice, then end your report with a Structured Output Protocol `handoff_recommendation` block naming the suggested specialist, the context they need, and your confidence — and return to the Team Lead. Limited *structured handoff* is sanctioned; actual *dispatch* is the Team Lead's alone. If you see a `guard-recursive-spawn` warn in the event log, read it as a flag that a worker tried to orchestrate. `[verify-at-use]` whether the recursion guard is wired in the active install (it ships in `ravenclaude-core/hooks/hooks.json`, but a consumer's posture can vary).
