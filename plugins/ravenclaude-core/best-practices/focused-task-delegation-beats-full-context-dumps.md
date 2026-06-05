# Give specialists a focused task, not the full conversation history

**Status:** Pattern
**Domain:** Agent design / Multi-agent / Context management
**Applies to:** `ravenclaude-core`

---

## Why this exists

When the Team Lead delegates to a specialist, the natural impulse is to forward the entire conversation history so the specialist "has all the context." That impulse produces worse output. A specialist handed 40 messages of back-and-forth between the user and the Team Lead must first process everything that is irrelevant to its narrow task — the design discussion the architect had, the earlier failed attempts, the tangents — before it reaches the 3 pieces of context it actually needs. Context overload degrades focus, increases token cost, and produces output that hedges against the full history rather than addressing the task. A focused task brief — narrow scope, explicit success criteria, the relevant subset of context, and the required output format — consistently outperforms a full-context handoff.

## How to apply

When drafting a sub-agent task brief:

```
Task: [one-sentence, unambiguous objective — what to produce]

Context (only what is load-bearing for this task):
- [file:path that contains the relevant code]
- [the decision already made that constrains the approach: X was chosen, not Y]
- [the interface this task must produce to — the contract]

Success criteria:
- [specific, verifiable outcome 1]
- [specific, verifiable outcome 2]

Constraints:
- Do not modify [file/module/interface X]
- Output must be compatible with [runtime/framework/schema Y]

Output format:
[Use Structured Output Protocol: ---RESULT_START--- ... ---RESULT_END---]
```

**Do:**
- Scope the task to the smallest deliverable that lets the next task begin — tasks that are too large produce partial completion and ambiguous success.
- Include only the file paths and context that are genuinely necessary; "read the full codebase first" is not a valid instruction for a focused task.
- Specify the output format explicitly — the Structured Output Protocol block ensures the Team Lead can parse the result programmatically, not just read it.

**Don't:**
- Forward the entire conversation history as "context" — extract and include only what the specialist needs.
- Assign two tasks to the same task brief (e.g., "implement X and also review Y") — each task gets its own brief with its own success criteria.
- Give a specialist permission to spawn further sub-agents without an explicit instruction to do so — sub-agent spawning is the Team Lead's job.

## Edge cases / when the rule does NOT apply

- When the specialist needs genuinely multi-step context that cannot be compressed (e.g., a code reviewer who must understand the architectural history to evaluate a diff), give them a curated summary, not raw history — the principle still applies.
- The deep-researcher agent has a legitimate need for broader context when conducting open-ended research; even then, give it a research brief with a specific question and an expected output format rather than an open-ended history dump.

## See also

- [`./route-before-spawning.md`](./route-before-spawning.md) — routing selects the specialist; this rule governs what you give them.
- [`../CLAUDE.md`](../CLAUDE.md) — "Focused Task Execution (New — Task Decomposition)" section.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Focused Task Execution" and the Structured Output Protocol §"Example Prompt Pattern". Ground truth: context-overload failures are the most-reported quality issue in long multi-agent sessions.

---

_Last reviewed: 2026-06-05 by `claude`_
