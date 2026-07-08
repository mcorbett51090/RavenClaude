---
name: design-eval-suite
description: "Turn a fuzzy 'is the AI good enough?' into a concrete measurement plan: task spec, the eval method from the decision tree (exact / rule-based / model-graded / human), the metric + what it misses, the offline-vs-online split, a power-adequate sample size, and a numeric ship-gate decided before the run. Reach for it at the START of any LLM-feature eval. Used by `eval-strategy-lead` (primary)."
---

# Skill: design-eval-suite

> **Invoked by:** `eval-strategy-lead` (primary). Hands off to `eval-harness-engineer` to build.
>
> **When to invoke:** "how do I evaluate this?"; before writing any harness code; whenever an LLM feature has no measurement plan.
>
> **Output:** a task spec + eval method + metric(s) + offline/online split + sample size + a numeric ship-gate.

## Procedure

1. **Write the task spec.** Name the inputs, the desired output, and what "good" means *to the user* — not to a benchmark. If you can't state the failure a user would notice, you can't measure it.
2. **Pick the method from the decision tree.** Traverse [`../../knowledge/eval-method-decision-tree.md`](../../knowledge/eval-method-decision-tree.md): checkable answer → exact/programmatic; constrained format → rule-based (regex/schema/unit test); subjective quality → model-graded or human. Prefer the cheapest reliable method.
3. **Choose the metric and name what it misses.** Accuracy, F1, pass-rate, win-rate, groundedness — pick the one that tracks user value, then write one sentence on what it drops (so nobody Goodharts the proxy).
4. **Split offline from online.** Decide what the frozen golden set gates (ship/no-ship) and what only production can tell you (thumbs, escalation rate, downstream conversion). You need both.
5. **Size the set.** Enough examples that a real regression clears the noise — start ~100 real examples for a ship decision, more where the effect is small or the bar is high. Stratify across the input segments that matter.
6. **Set the ship-gate as a number, before the run.** "metric ≥ X on N examples, zero guardrail regressions." Decide X before seeing the score so it can't be rationalized after.

## Worked example

> Support-reply drafting feature.

- Task spec → input: ticket + KB; output: a draft reply; good = accurate, on-policy, no fabricated facts.
- Method → groundedness is subjective → **model-graded judge**; "did it cite a real KB article?" → **rule-based** check alongside.
- Metric → judge win-rate vs the current prompt + a hard groundedness pass-rate. Misses: tone nuance → sample to human monthly.
- Offline gate → judge win-rate ≥ 55% AND groundedness = 100% on 120 frozen tickets. Online → thumbs-down rate + agent-edit distance.

## Guardrails

- **Never gate on a leaderboard/benchmark score** — it doesn't measure your task.
- **Decide the threshold before the run** — a bar set after seeing the number is not a gate.
- **A vibe check is a hypothesis** — fine to start, never to decide.
