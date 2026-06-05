# Revisit prompt scope before upgrading the model tier

**Status:** Pattern
**Domain:** Model selection methodology
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

When an AI coding tool produces a poor result, the instinct is to upgrade to a larger model. In practice, a significant fraction of poor results are caused by underspecified prompts or tasks that are too large for the model to resolve coherently — not by model-tier limitations. Upgrading the model tier on an underspecified task produces a more expensive version of the same poor result. This rule enforces a prompt-and-scope check before recommending a model upgrade.

## How to apply

When a developer reports that model output is insufficient:

```
Step 1: Is the task description precise?
  → Does it name the specific file(s) to change?
  → Does it state the expected output format?
  → Is the scope bounded (not "fix all issues")?
  → If no: clarify the prompt first; retry on the same model tier

Step 2: Is the task too large for the model to resolve as a single call?
  → If yes: chunk it; retry sub-tasks on the same tier
  → If no: proceed to step 3

Step 3: Is the reasoning lever available (Codex)?
  → If yes: raise the reasoning level on the same model; retry
  → If no: proceed to step 4

Step 4: Has the task demonstrably failed at the maximum reasoning level on the balanced tier?
  → If yes: recommend a tier upgrade
  → If no: document which of steps 1-3 was tried and what the result was
```

**Do:**
- Document the steps tried before recommending an upgrade — "tried steps 1-3; quality gap remains" is a defensible recommendation.
- Treat prompt clarity as part of the model-selection recommendation, not a separate concern.

**Don't:**
- Skip steps 1-3 because "the developer already tried" — confirm which specific steps were tried.
- Recommend a frontier model as the first response to any quality complaint.

## Edge cases / when the rule does NOT apply

- The task is demonstrably in the hard tail (e.g., complex reasoning across a large codebase that a balanced model has failed on at max reasoning after proper scoping) — tier upgrade is appropriate; document the evidence.

## See also

- [`../best-practices/reasoning-level-before-model-upgrade.md`](./reasoning-level-before-model-upgrade.md) — the Codex-specific reasoning-level rule this one generalizes
- [`../skills/coding-agent-task-scoping/SKILL.md`](../skills/coding-agent-task-scoping/SKILL.md) — scoping as the first fix

## Provenance

Generalizes house opinion #6 ("reasoning level is a dial") to cover all three ecosystems and adds the prompt-clarity step that sits upstream of the reasoning dial. The Codex reasoning-level rule handles the Codex-specific case; this rule handles the upstream diagnostic.

---

_Last reviewed: 2026-06-05 by `claude`_
