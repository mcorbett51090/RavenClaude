# llm-evaluation-engineering

**LLM-evaluation engineering team** for the question every team shipping an AI feature has to answer:
**is it getting better or worse?** Two agents cover the two halves of that job — deciding *what to
measure*, and *building the machinery* that proves it.

> Engineering decision-support, **not** a safety certification. Model, judge, and tooling specifics are
> volatile — every one carries a retrieval date + `[verify-at-use]`. No eval-data PII. Inherits the
> `ravenclaude-core` constitution.

## Agents

| Agent | Owns | Spawn when |
|---|---|---|
| [`eval-strategy-lead`](agents/eval-strategy-lead.md) | What to measure — task spec, eval-method choice, metric + what it misses, offline/online split, sample size, the numeric ship-gate | "How do I even evaluate this?"; "LLM judge or something simpler?"; "what score should gate the release?" |
| [`eval-harness-engineer`](agents/eval-harness-engineer.md) | How to measure — frozen golden sets with provenance, LLM-as-judge rubric + calibration + bias audit, CI regression gates, guardrail/red-team suites | "Set up an LLM to grade outputs"; "build the eval dataset"; "run evals on every PR"; "test for jailbreaks/PII" |

## Skills

- [`design-eval-suite`](skills/design-eval-suite/SKILL.md) — task → measurement plan → numeric ship-gate.
- [`build-llm-judge`](skills/build-llm-judge/SKILL.md) — design + calibrate + bias-audit an LLM-as-judge.
- [`gate-releases-with-evals`](skills/gate-releases-with-evals/SKILL.md) — wire the offline suite into a CI ship-gate.

## Knowledge bank

- [`knowledge/eval-method-decision-tree.md`](knowledge/eval-method-decision-tree.md) — exact / rule-based / model-graded / human, and the offline/online split.
- [`knowledge/llm-eval-tooling-2026.md`](knowledge/llm-eval-tooling-2026.md) — dated tooling map + the LLM-judge bias list.

## Boundaries (what routes elsewhere)

- **Retrieval quality (recall@k, groundedness of retrieval)** → `ai-rag-engineering`.
- **Which model to pick / model capability guidance** → `ai-coding-model-guidance`.
- **Classical-ML training + metrics (AUC, calibration)** → `ml-engineering`.
- **Product A/B experiments** → `experimentation-growth-engineering`.

## Install

```
/plugin marketplace add ./           # from a separate Claude Code project
/plugin install llm-evaluation-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
