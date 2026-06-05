---
scenario_id: 2026-06-05-eval-regression-shipped-silently
contributed_at: 2026-06-05
plugin: claude-app-engineering
product: evals
product_version: "unknown"
scope: likely-general
tags: [evals, regression, golden-set, llm-judge, model-migration, ci-gate, position-bias]
confidence: medium
reviewed: false
---

## Problem

A team "improved" a classification prompt (a tweak that read better and demoed well) and shipped it. Days later, support tickets showed a category of inputs the app now mislabeled — the prompt change had *regressed* a slice while improving the slice the author eyeballed. Separately, a model migration (bumping the pinned model id to a newer version) had shipped the same week with no eval run, so when quality shifted nobody could attribute it: was it the prompt, the model, or noise?

## Constraints context

- No golden set and no CI eval gate: prompt/model changes shipped on "looks better in the playground" (the vibes anti-pattern).
- When they *did* build a quick LLM-as-judge to check, the first cut was unreliable — it scored the option presented first higher (position bias), and ran the judge on the same expensive model as production (slow + costly), so they almost abandoned it.
- The model migration and the prompt change landed in the same deploy, so even with a later eval the two effects were entangled.

## Attempts

- Tried: manual spot-checking a handful of inputs before shipping. That's exactly how the regression slipped — the author checked the slice they were optimizing and never saw the slice they broke. Spot-checks confirm the happy path; they don't catch regressions.
- Tried: an LLM judge that scored A-vs-B by reading both in a fixed order. It was biased toward the first option and the team distrusted it. Fix: **randomize option order** per comparison (and/or average both orderings) to control position bias, which made the judge's verdicts stable enough to trust.
- Tried (the moves that worked):
  1. Built a **golden set** (representative inputs incl. the previously-broken slice + expected labels), and made any prompt/model/tool-def change **run it in CI and fail on a regression beyond a threshold**, with failing cases enumerated.
  2. **Pinned the judge model + judge prompt** and ran the judge on a **cheap model via Batch** (50% off, latency-tolerant for an offline gate) — making it affordable to run on every change.
  3. **Separated the two changes:** treat a model migration as its own deliberate eval event, run independently of a prompt change, so a quality shift is attributable.

## Resolution

**No prompt/model/tool-def change ships without an eval delta on a golden set — and the judge has to be made trustworthy and cheap or it won't get run.** The discipline:

1. **Evals before vibes.** A behavioral change (prompt, model, tool definitions) runs the golden set in CI and gates on the delta; a brand-new feature ships *with* a golden set to establish the first baseline (not a delta). A pure refactor needs no gate. (See the eval-gate decision tree in [`../knowledge/claude-app-decision-trees.md`](../knowledge/claude-app-decision-trees.md).)
2. **Make the judge believable.** Randomize option order against position bias; pin the judge model + judge prompt so a baseline shift is intentional, not drift; prefer a programmatic grader where the output is checkable (exact match / schema-valid) and reserve the LLM judge for genuinely subjective quality.
3. **Make the judge cheap.** Default the judge to a small/fast model and run eval batches through the Batch API — a gate that's expensive or slow gets skipped under deadline pressure, and a skipped gate is no gate.
4. **One variable at a time.** A model migration is its own eval event — don't entangle it with a prompt change in the same deploy, or you can't attribute the result. Re-baseline deliberately when the platform ships a new model (it ships monthly); a default model swap is an eval event, not a silent bump.

The trap is that "looks better" is real signal for the slice you looked at and zero signal for the slice you didn't — and an LLM judge built carelessly (position-biased, expensive) gets distrusted and abandoned, leaving you back on vibes.

**Action for the next engineer:** if a quality regression shipped, check whether a golden set + CI gate existed (usually not) and whether a prompt and a model change rode the same deploy (usually yes). Add the golden set with the broken slice included, gate CI on it, and split model migrations into their own eval runs.

Cross-reference: operationalizes [`../best-practices/evals-before-vibes.md`](../best-practices/evals-before-vibes.md), [`../best-practices/eval-judge-bias-controls.md`](../best-practices/eval-judge-bias-controls.md), [`../best-practices/eval-golden-set-maintenance.md`](../best-practices/eval-golden-set-maintenance.md), and [`../best-practices/model-migrate-behind-an-eval-gate.md`](../best-practices/model-migrate-behind-an-eval-gate.md); full reference in [`../knowledge/evals-and-quality.md`](../knowledge/evals-and-quality.md). The Batch discount + model lineup are dated — `[verify-at-use]`.
