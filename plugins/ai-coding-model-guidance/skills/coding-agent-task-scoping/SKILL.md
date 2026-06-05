---
name: coding-agent-task-scoping
description: "Scope an autonomous AI coding agent task so it is well-bounded, recoverable, and matched to the right model tier before it runs. Reach for this skill before any long, unsupervised, or multi-step agentic run — a poorly scoped task on a frontier model is both expensive and hard to debug."
---

# Skill: Coding Agent Task Scoping

An autonomous coding agent run is not a chat turn. The task description, model tier, and recovery plan must be decided before the run starts — not after it has touched 40 files. This skill structures that pre-run decision.

## Step 0 — Is this task actually agent-appropriate?

Not every "I want to automate this" request benefits from an autonomous run. Run this quick check:

| Question | If YES | If NO |
|---|---|---|
| Can the task be done interactively in one supervised chat turn? | → Supervised chat, not an agent run | Continue |
| Does the task require reading many files the developer can't enumerate? | → Agent run appropriate | Supervised chat |
| Does the task require irreversible production actions (deploys, deletions, DB writes)? | → Mandatory human gate; see high-blast rule | Continue with caution |
| Can the task be decomposed into ≤ 5 well-defined sub-steps? | → Prefer sequential supervised turns | Agent run if steps are still complex |

## Step 1 — Define the task boundary

A well-scoped agent task has a clear **start state**, **end state**, and **scope envelope**:

```
Start state:  [what exists before the run: branch, file list, test state]
End state:    [what "done" looks like: tests pass, file changed, PR opened]
Scope envelope:
  - Repos in scope: [explicit list]
  - Files allowed to modify: [pattern or list]
  - Files NOT to touch: [explicit exclusions — migrations, infra, secrets]
  - External calls allowed: [none | read-only | specific APIs]
```

**Never leave the scope envelope open-ended.** "Refactor the whole codebase" is not a task boundary; "refactor the authentication module in `src/auth/` so all functions have type annotations, passing the existing test suite" is.

## Step 2 — Classify the blast radius

| Blast class | Definition | Model tier implication |
|---|---|---|
| Low blast | Reversible; touches only local files; no external state | Balanced default tier |
| Medium blast | PR opened or test suite modified; reversible via PR close | Balanced or frontier; reasoning level up |
| High blast | Database writes, deploy triggers, secret rotation, force-push | Frontier tier mandatory; human gate before execution |

High-blast tasks must have a **checkpoint plan**: what does the agent do if it encounters an unexpected state mid-run? Define the recovery path before starting.

## Step 3 — Select the model tier for the run

Apply the vendor-neutral tier logic:

1. **Low-blast, bounded task** — balanced default tier with reasoning level raised if needed (Codex).
2. **Medium-blast or multi-file refactor** — start at balanced default; upgrade to frontier only after a failed run at medium reasoning.
3. **High-blast or very long autonomous run** — frontier tier; human approval gate at the start and at each irreversible step.
4. **Long run that spans many files** — check context demand against `../context-window-planning/SKILL.md` first; chunking may be cheaper than a frontier model.

## Step 4 — Define the success criterion before running

The agent must be able to tell the developer when it is done. A testable criterion:

- **Code change:** "all tests in `src/auth/tests/` pass and `mypy src/auth/` exits 0"
- **PR creation:** "a PR is open against `main` with a description matching the task scope"
- **Analysis:** "a report file at `docs/audit.md` covers all files matching `src/**/*.py`"

Without a testable criterion, the agent will either run forever or produce an incomplete artifact with no way to know it is incomplete.

## Pitfalls

- Starting a high-blast run at the balanced tier because "it will probably be fine" — the cost of a wrong action on 40 files exceeds any model-cost savings.
- Leaving the scope envelope open ("just fix whatever you find") — the agent will touch files the developer didn't intend.
- Skipping the checkpoint plan on a high-blast task — mid-run failures are harder to recover from than pre-run planning is expensive.
- Treating a long run failure as a model-quality problem before checking task scope — most long-run failures are scope problems, not model problems.

## See also

- [`../../agents/codex-model-strategist.md`](../../agents/codex-model-strategist.md) — reasoning-level calibration for Codex agent runs
- [`../../agents/copilot-model-strategist.md`](../../agents/copilot-model-strategist.md) — Copilot coding-agent surface and plan gates
- [`../context-window-planning/SKILL.md`](../context-window-planning/SKILL.md) — context demand estimation for long runs
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — vendor-neutral tier selection
