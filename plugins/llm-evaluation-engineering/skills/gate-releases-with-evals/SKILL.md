---
name: gate-releases-with-evals
description: "Wire an offline eval suite into a CI ship-gate so a prompt/model change is scored against a frozen baseline and blocked on a regression past a preset threshold, with guardrail/red-team checks as a zero-tolerance blocker and cost/latency tracked alongside quality. Reach for it to make evals a merge gate instead of a report. Used by both agents."
---

# Skill: gate-releases-with-evals

> **Invoked by:** `eval-harness-engineer` (build) + `eval-strategy-lead` (threshold).
>
> **When to invoke:** once a golden set + judge exist and you want a change scored before it merges/ships.
>
> **Output:** a CI gate spec — baseline, threshold, what blocks, and the guardrail + cost/latency reporting.

## Procedure

1. **Establish the frozen baseline.** Score the current production prompt/model on the golden set; record it (with the pinned models/versions) as the number every change is compared to.
2. **Define the block condition from the strategy lead's gate.** e.g. "block if judge win-rate < baseline − margin on N examples" AND "block on ANY guardrail regression". Absolute-quality gates and no-regression gates are both valid — pick per task.
3. **Run on the PR.** The suite executes on the change, produces the score delta vs baseline, and posts it to the PR. Determinism: pin temperature/model/prompt; seed anything stochastic; record them with the result.
4. **Make it a gate, not a decoration.** A regression past the threshold fails the check and blocks the merge — a number nobody blocks on gets ignored.
5. **Report cost + latency alongside quality.** Tokens and p50/p95 latency per example, so a quality win that triples cost is a visible tradeoff, not a surprise bill.
6. **Feed production surprises back in.** When something slips past offline into production, add the failing case to the golden set (or red-team set) so the gate catches it next time.

## Worked example

> Prompt change to the support-reply feature.

- Baseline → judge win-rate 52%, groundedness 100%, $0.004/reply, p95 1.9s on 120 frozen tickets.
- Gate → block if win-rate < 50% OR groundedness < 100% OR any injection/PII red-team failure.
- PR run → win-rate 58% (+6), groundedness 100%, $0.005/reply (+25% cost flagged), 0 red-team failures → **passes, cost tradeoff surfaced for sign-off**.

## Guardrails

- **Never move the baseline silently** to make a regression pass — the baseline changes only on a deliberate, recorded promotion.
- **Guardrail failures are zero-tolerance** — they block regardless of the quality delta.
- **A flaky gate is worse than none** — pin determinism or the team learns to ignore red.
