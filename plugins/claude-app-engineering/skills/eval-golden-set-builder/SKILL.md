---
name: eval-golden-set-builder
description: "Playbook for constructing a high-signal golden evaluation set: sampling strategy, input diversity, reference-answer authoring, grader pairing, and the minimum-viable size thresholds that make a delta meaningful. Owned by eval-engineer."
---

# Eval Golden Set Builder

## When to invoke

- Starting evals from scratch on a new prompt or agent.
- An existing golden set is producing noisy deltas (every change looks "better").
- A product change (new tool, new model, new system prompt) needs a before/after regression check.
- LLM-judge results are inconsistent across runs.

## Step 1 — Define what you are measuring

Before collecting examples, answer these:

| Question | Why it matters |
|---|---|
| What is the unit of success? | A correct final answer? A correctly-chosen tool? A well-structured JSON output? |
| Who is the judge? (human / programmatic / LLM) | Determines reference-answer format |
| What is the blast radius of a regression? | Determines minimum set size and grader strictness |

One eval, one signal. Do not try to evaluate "everything" in one set. Separate factual accuracy from tone from tool-call correctness — they need different graders.

## Step 2 — Sampling strategy

| Stratum | Target fraction | What goes here |
|---|---|---|
| Happy path | 40 % | Canonical inputs the system handles today |
| Edge / boundary | 30 % | Near-miss inputs, ambiguous phrasing, missing fields |
| Adversarial | 20 % | Injection probes, jailbreak-adjacent inputs, known failure modes |
| Regression seeds | 10 % | Any input that caused a past production bug |

Minimum viable set: **50 examples** for a binary pass/fail grader; **100+** for a scored (0–5) rubric or LLM judge (smaller sets produce deltas too noisy to trust).

## Step 3 — Authoring reference answers

1. **Human-authored ground truth first.** Write the ideal answer before you see what the model produces — post-hoc rationalization corrupts the set.
2. **For tool-call evals:** record the expected `tool_use` block — `name` + exact `input` keys. Use `"contains"` matching (not string equality) for free-text arguments.
3. **For structured-output evals:** store the expected JSON; use JSON Schema validation as the grader, not string diff.
4. **For open-ended answers:** write a rubric (3–5 criteria, each scored 1–3) that a judge (human or LLM) can apply without seeing the question first. Store it alongside the example.

```jsonl
{"id": "q_001", "input": {"messages": [...]}, "expected": {"tool": "search_docs", "query_contains": "refund policy"}, "grader": "tool_call_match"}
{"id": "q_002", "input": {"messages": [...]}, "expected": {"rubric": "criteria_accuracy_helpfulness"}, "grader": "llm_rubric"}
```

## Step 4 — Grader pairing

| Output type | Grader | Notes |
|---|---|---|
| Exact JSON / schema | JSON Schema validator | Fast, deterministic, free |
| Tool call correctness | Name + key-subset match | Allow partial `input` matches |
| Binary pass/fail factual | String `in` / regex | Hand-write assertions |
| Scored rubric / tone / style | LLM-as-judge (Haiku via Batch) | Run via Anthropic Batch at 50 % cost; randomize answer order per call to reduce position bias |

**LLM-judge discipline:** present judge with rubric + response only (not the question) to prevent question-loading bias. Run 3× and take majority vote on borderline cases.

## Step 5 — Baseline and delta protocol

```python
# Run on every prompt/model/tool change
baseline = run_eval(golden_set, old_config)
candidate = run_eval(golden_set, new_config)
delta = candidate.mean_score - baseline.mean_score
p_value = ttest(candidate.scores, baseline.scores).pvalue
print(f"delta={delta:+.3f}  p={p_value:.3f}  n={len(golden_set)}")
# Merge only if delta >= +0.02 and p < 0.05
```

Treat a delta < 0.02 on a 0–1 scale as noise, not improvement. Track per-stratum scores — an adversarial regression hidden by a happy-path improvement is still a regression.

## Pitfalls

- Seeding the golden set from model output ("label what the model said as correct") — creates a circular reference that only confirms the current model's biases.
- A set with 90 % happy-path inputs — edge and adversarial cases are where regressions actually hide.
- Comparing runs on different dates without pinning the model version and temperature (`temperature: 0` for evals).
- Re-running a failing test until it passes and calling that "fixed" — add the fixed case as a regression seed; don't delete the test.
