# Estimate context demand before every long or multi-file run

**Status:** Primary diagnostic
**Domain:** Context window management
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

Context window overflow is one of the most silent failure modes in AI coding tools: the model receives a truncated input, produces a confident but incorrect output, and neither the developer nor the agent surface an error. The failure is invisible until the output is wrong. This best practice makes context demand estimation a mandatory pre-step for any task classified as High or Very High demand — long autonomous runs, full-repo scans, long multi-file diffs, and extended multi-turn conversations with large file pastes.

## How to apply

Before running or recommending a High-demand task:

```
Step 1: Classify demand tier
  Low    → single file or function; short conversation
  Medium → 2-5 files; a focused PR diff
  High   → entire module; cross-file refactor with dependencies
  Very High → full repo scan; long autonomous run; many-turn history with large pastes

Step 2: For High or Very High demand
  → Check whether the task can be chunked into Medium-demand sub-tasks
  → If chunking is feasible: chunking is cheaper and produces more debuggable results
  → If chunking is not feasible: escalate to frontier tier and verify window [verify-at-use]

Step 3: For Very High demand
  → Chunking is required regardless of model tier
  → No current model covers a full production codebase in a single call
  → Document the chunking plan before the run starts
```

**Do:**
- Classify demand tier as part of the pre-run checklist or the model recommendation.
- Prefer a well-scoped chunked run over a single frontier-model call for large tasks.
- Quote window sizes as `[verify-at-use — YYYY-MM]` — limits change with model updates.

**Don't:**
- Assume the largest available model avoids overflow — all models have limits.
- Treat output tokens as free — a task that generates large files consumes output space that reduces the effective input window.
- Recommend a frontier model solely to increase context capacity when chunking would serve the same task more cheaply.

## Edge cases / when the rule does NOT apply

- Single-file or short chat turns (Low demand) — no estimation step needed; proceed with balanced default tier.

## See also

- [`../skills/context-window-planning/SKILL.md`](../skills/context-window-planning/SKILL.md) — the step-by-step estimation playbook
- [`../skills/coding-agent-task-scoping/SKILL.md`](../skills/coding-agent-task-scoping/SKILL.md) — chunking strategy as part of task scoping

## Provenance

Derived from a gap in the existing rules: the plugin covers model selection and retirement but not context demand. Context overflow is among the most common causes of silent long-run failures in the three covered ecosystems.

---

_Last reviewed: 2026-06-05 by `claude`_
