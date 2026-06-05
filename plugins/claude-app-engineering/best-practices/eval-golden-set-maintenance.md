# Maintain the golden set: add regressions, prune irrelevant cases

**Status:** Pattern
**Domain:** Evals / quality
**Applies to:** `claude-app-engineering`

---

## Why this exists

A golden eval set that never grows is a leaking test suite: over time it covers
the features from three releases ago and misses the failure modes the current
system actually encounters. Conversely, a set that only grows accumulates
contradictory, redundant, and obsolete cases that slow the eval run and bury the
signal. The discipline is a living set: add cases from production regressions,
prune cases that no longer reflect the system's actual inputs, and keep it
sized to what the CI budget can run in a useful time.

## How to apply

Maintenance triggers:

| Event | Action |
|---|---|
| Production regression (user-reported) | Root-cause, add the failing input as a new golden case; add the expected output |
| Prompt / model change | Audit the full set for obsolete expected outputs; update or delete stale cases |
| New feature / capability | Add at least 3–5 cases covering the new behaviour before shipping |
| Set grows past your CI time budget | Prune: remove duplicates, merge near-identical cases, delete cases for removed features |

```python
# structure: {id, input, expected_output, tags, added_date, reason}
golden_set = load_golden_set("evals/golden.jsonl")

# After a regression:
golden_set.append({
    "id": "reg-2026-06-05-001",
    "input": failing_input,
    "expected_output": correct_output,
    "tags": ["regression", "feature-X"],
    "added_date": "2026-06-05",
    "reason": "User ticket #4421 — model was returning ...",
})
save_golden_set("evals/golden.jsonl", golden_set)
```

Track set composition metrics: total cases, cases per tag, case age distribution.
A set where >50% of cases are over 6 months old and tagged for a deprecated
feature is a maintenance signal.

**Do:**
- Add a new golden case for every production regression as the last step of the
  incident response.
- Tag cases by feature and prompt version so stale cases are identifiable.
- Time-box the CI eval run and prune to fit; 200–500 high-quality cases beats
  2 000 stale ones.

**Don't:**
- Add cases without an `expected_output` — an untestable case is noise.
- Grow the set at a rate the CI budget can't sustain (eval on a cheap model via
  Batch if cost is the binding constraint).
- Skip the prune pass when the system prompt or model changes significantly.

## Edge cases / when the rule does NOT apply

- Brand-new projects (< 1 month): add aggressively, don't prune yet.
- Compliance / safety evals: never prune safety-critical cases regardless of age.

## See also

- [`../agents/eval-engineer.md`](../agents/eval-engineer.md) — owns eval design and golden set management
- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the upstream rule that makes the golden set load-bearing
- [`./eval-judge-bias-controls.md`](./eval-judge-bias-controls.md) — judge configuration for the eval run

## Provenance

Codifies the golden-set maintenance discipline from
`knowledge/evals-and-quality.md` (retrieved 2026-05-28) §"Eval maintenance".
Standard practice in ML engineering adapted for LLM evals.

---

_Last reviewed: 2026-06-05 by `claude`_
