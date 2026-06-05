# Scope the task before starting an agentic run

**Status:** Absolute rule
**Domain:** Autonomous agent usage
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

An autonomous coding agent run is not a chat turn. Once an agent starts modifying files, the cost of a wrong action compounds with every step — and a poorly scoped task on a frontier model is both expensive and hard to recover from. The primary cause of long-run failures is not model quality; it is an underspecified task boundary that lets the agent touch things it should not have touched. This rule forces the boundary to be defined before the billing clock and the blast radius both start.

## How to apply

Before recommending that a developer run any autonomous AI coding agent (Copilot coding agent, Codex autonomous mode, or a Grok API agent loop), confirm:

```
1. Start state defined?       → branch name, file state, test status
2. End state testable?        → a criterion that tells the agent when to stop
3. Scope envelope explicit?   → repos, files allowed, files NOT to touch
4. Blast radius classified?   → Low / Medium / High (see coding-agent-task-scoping skill)
5. Recovery plan documented?  → what happens if the agent hits an unexpected state?
```

Use the `../skills/coding-agent-task-scoping/SKILL.md` playbook and the `../templates/agentic-run-pre-flight.md` checklist.

**Do:**
- Treat an incomplete pre-flight as a reason to pause, not a reason to proceed and fix later.
- Classify High-blast tasks and require a human gate before and during execution.
- Define the success criterion in testable terms — "all tests pass and mypy exits 0" beats "looks right."

**Don't:**
- Allow "refactor everything" or "fix whatever you find" as a task boundary — these are not scopes.
- Skip the recovery plan for Medium-blast tasks because they "seem reversible."
- Recommend a frontier model to compensate for a poorly scoped task — a frontier model on an open-ended task is a more expensive version of the same problem.

## Edge cases / when the rule does NOT apply

- Short, clearly bounded single-file tasks (e.g., "add type annotations to this function") where the scope is self-evident — the pre-flight checklist can be mental, not written, but the blast-radius classification is still required.

## See also

- [`../skills/coding-agent-task-scoping/SKILL.md`](../skills/coding-agent-task-scoping/SKILL.md) — the step-by-step scoping playbook
- [`../templates/agentic-run-pre-flight.md`](../templates/agentic-run-pre-flight.md) — the pre-run checklist

## Provenance

Derived from `CLAUDE.md` §3 house opinion #2 (right-size, don't default to the top) and the anti-pattern "defaulting to the top frontier for everyday work" (§4). Scoping failures produce unnecessary frontier model charges — this rule prevents the confusion of "poor model choice" when the actual cause is "poor task definition."

---

_Last reviewed: 2026-06-05 by `claude`_
