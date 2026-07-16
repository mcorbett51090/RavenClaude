# Agent Eval Plan — <agent name>

> Fill this out with the `agent-implementation-engineer`. The rule: **offline against fixtures first**, score three dimensions, and report cost/latency next to quality. A demo is not an eval.

## 1. Task set (the frozen regression harness)

| # | Task input | Known-good outcome | Category (happy / edge / tail) |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |

- **Source of tasks:** (real logs / synthetic / hand-authored)
- **Frozen?** yes/no — grow only by *adding* production failures, never by editing away failures.

## 2. Scorers

| Dimension | How scored | Threshold to ship |
|---|---|---|
| **Task-completion** (goal achieved?) | exact-match / rubric / LLM-judge |  |
| **Trajectory** (sane path?) | step count, redundant/looping calls, plan coherence |  |
| **Tool-use** (right tool + args, recovered from errors?) | wrong-tool rate, bad-arg rate, error-recovery rate |  |

## 3. Offline harness

- **Tools mocked?** yes/no — (deterministic, free, fast; catch regressions before live spend)
- **Fixtures location:**
- **How run:** (command / CI hook)

## 4. Cost & latency

| Metric | Mean | p95 | Ceiling to ship |
|---|---|---|---|
| Token cost / run |  |  |  |
| Wall-clock / run |  |  |  |

## 5. Hardening checklist

- [ ] Hard step / tool-call cap
- [ ] Per-tool timeout + bounded retry
- [ ] Explicit stop conditions (goal / no-progress / cap-hit)
- [ ] Human-in-the-loop gate on every irreversible action
- [ ] Tracing: step, tool call, args, result, token cost — all recorded & replayable
- [ ] Tool allowlist + input/output validation
- [ ] Untrusted-content handling (prompt-injection): tool/retrieved content treated as data, high-blast tools gated

## 6. Production feedback loop

- **How new failure modes become fixtures:**
- **Review cadence for the task set:**

> Volatile facts (model IDs, pricing, framework tracing APIs): date each + `[verify-at-use]`.
