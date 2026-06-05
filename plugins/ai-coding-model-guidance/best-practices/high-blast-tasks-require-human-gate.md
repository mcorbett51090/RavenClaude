# High-blast agentic tasks require a human gate before and during execution

**Status:** Absolute rule
**Domain:** Autonomous agent safety
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

High-blast tasks — those involving database writes, deploy triggers, secret rotation, force-pushes, or any irreversible production action — are specifically excluded from the plugin's autonomous decision flow and always escalate to a human gate (`CLAUDE.md` §3, cross-cutting opinion on high-blast decisions). When an AI coding agent proposes or begins a high-blast operation, the cost of a wrong action is not limited to a model charge; it is a production incident, a data loss event, or a security exposure. No model tier eliminates this risk. The human gate is the only reliable backstop.

## How to apply

Before an agent run or a model recommendation involving high-blast operations:

```
Gate 1 — Pre-run (always required):
  → Classify the task: does it touch DB writes / deploys / secret rotation / force-push?
  → If yes: document the blast classification and obtain human approval before the run starts
  → Document the gate holder's name and approval timestamp

Gate 2 — During run (required for multi-step high-blast):
  → Define explicit checkpoints where the agent pauses and reports state before proceeding
  → Each irreversible action is a checkpoint — not just the final step

Gate 3 — Post-run (required):
  → Human reviews the output before any automated follow-on action runs
  → Rollback procedure documented and tested before the run, not after
```

**Do:**
- Classify blast radius in the pre-flight checklist for every agentic run.
- Require a named human gate holder — not "a reviewer" but a specific person.
- Treat a failed high-blast run as an incident, not a retry — diagnose the root cause before re-running.

**Don't:**
- Allow "the model is very capable" as a reason to skip the human gate on a high-blast task.
- Treat Medium-blast tasks as High-blast-free — a PR that triggers a CI/CD deploy is medium-to-high.
- Allow the gate to be synchronous-optional (i.e., proceed unless objection is raised within N minutes) — explicit approval is the standard.

## Edge cases / when the rule does NOT apply

- The "high-blast" action is purely local (e.g., a large local file deletion in a sandbox environment with no production connection) — the gate is still recommended but not mandatory. Document the sandbox status explicitly.

## See also

- [`../skills/coding-agent-task-scoping/SKILL.md`](../skills/coding-agent-task-scoping/SKILL.md) — blast-radius classification in the scoping skill
- [`../templates/agentic-run-pre-flight.md`](../templates/agentic-run-pre-flight.md) — the pre-run checklist that enforces Gate 1

## Provenance

Codifies the `ravenclaude-core` high-blast / irreversible-decision rule in the specific context of AI coding agent runs. The three ecosystems covered (Copilot, Codex, Grok) all expose agentic execution surfaces; this rule applies uniformly across all three.

---

_Last reviewed: 2026-06-05 by `claude`_
