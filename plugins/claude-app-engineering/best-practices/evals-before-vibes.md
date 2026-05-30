# Evals before vibes — no prompt or model change ships without a delta on a golden set

**Status:** Absolute rule — "it looks better" is not a result.

**Domain:** Evals / quality

**Applies to:** `claude-app-engineering`

---

## Why this exists

Prompt, model, and tool-definition changes are invisible until they regress in production: a reworded system prompt that helps one case quietly breaks five, a model swap that's better on the happy path and worse on the edges, a tool-description tweak that shifts call accuracy. Shipping on "looks better" means the regression surfaces as a user complaint, not a build failure. House opinion #4 makes the discipline binary: **no prompt/model/tool change ships without an eval delta on a golden set**, and the eval is built *before* the change so the before/after is measurable. The golden set + graders + a reported delta-vs-prior turn quality from a vibe into a number you can gate CI on.

## How to apply

Curate a small golden set, grade cheapest-reliable-first, and report a delta against the pinned prior baseline — failing cases enumerated. Pin the eval model, judge model, and judge prompt so a baseline shift is intentional.

```python
# Graders, cheapest-reliable-first:
#   1. programmatic  — exact match / regex / JSON-schema validity / numeric tolerance (free, deterministic)
#   2. LLM-as-judge  — open-ended quality only; default the judge to Haiku, run via Batch (50% off)
#   3. human         — calibration spot-check; sample, don't grade everything
def grade(case, output):
    if case.kind == "checkable":
        return programmatic(case.expected, output)        # prefer this whenever possible
    # judge: pairwise + RANDOMIZED order to defeat position/verbosity bias
    return judge_pairwise(case, output, judge_model="claude-haiku-4-5")

# CI gate: fail the build on a regression beyond threshold; enumerate the failing cases.
delta = run_golden_set(version="candidate") - baseline   # baseline is PINNED
assert delta >= -REGRESSION_THRESHOLD, failing_cases(delta)
```

**Do:**
- Build the golden set **before** the change (20-50 representative cases incl. hard/edge/adversarial; grow it from production failures).
- Use **programmatic** graders wherever the answer is checkable in code — free and deterministic — and reserve the LLM judge for open-ended quality.
- Defeat judge **position/verbosity bias**: pairwise comparison with randomized order (run A-vs-B and B-vs-A, average), score on a version-controlled rubric.
- **Pin** the eval model, judge model, and judge prompt; run the eval in CI on every prompt/model/tool change and report the delta with failing cases.
- Re-baseline **deliberately** when the platform ships a new model — a baseline shift should be intentional, not silent.

**Don't:**
- Ship a prompt/model change because the output "looks better" — that's the named anti-pattern.
- Let the judge prompt drift uncontrolled — it silently moves your baseline.
- Grade everything with the LLM judge when a programmatic check would do — it's slower, costlier, and less reliable.

## Edge cases / when the rule does NOT apply

- **Pure refactors with no behavior change** (renaming a variable, reformatting code that doesn't touch the prompt/model/tools) don't need an eval delta — the rule gates *behavioral* changes.
- **Brand-new features with no prior baseline** establish the *first* baseline rather than measuring a delta — but they still ship with a golden set, not on vibes.
- **Evaluating a RavenClaude agent-file's prompt quality** (an artifact) is `ravenclaude-core/prompt-engineer` via the `agent-quality-rubric` skill — this rule governs an *application's* prompt/model change (the seam, [`../CLAUDE.md`](../CLAUDE.md) §10).
- Judge bias mitigations are floors, not ceilings — a high-stakes eval still needs a human calibration sample.

## See also

- [`../knowledge/evals-and-quality.md`](../knowledge/evals-and-quality.md) — the golden set, graders, LLM-judge bias/cost mitigations, regression discipline
- [`./right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) — the re-baseline event when a model changes
- [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the dated lineup; new models trigger a deliberate re-baseline
- [`../agents/eval-engineer.md`](../agents/eval-engineer.md) — owns evals, graders, and the regression gate

## Provenance

Codifies house opinion #4 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("evals before vibes") and the §4 anti-pattern ("shipping a prompt/model change on 'looks better' with no eval delta"). Grounded in the evals-and-quality knowledge file (established LLM-eval practice + Anthropic guidance, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
