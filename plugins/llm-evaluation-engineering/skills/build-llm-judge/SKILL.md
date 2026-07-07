---
name: build-llm-judge
description: "Design, calibrate, and bias-audit an LLM-as-judge so its scores track human judgment: named criteria with anchored levels (not 'rate 1-10'), a structured verdict + reason, a pinned judge model/version, a human-agreement calibration on a sample, and checks for position / verbosity / self-preference / leniency bias. Reach for it whenever a judge grades outputs. Used by `eval-harness-engineer` (primary)."
---

# Skill: build-llm-judge

> **Invoked by:** `eval-harness-engineer` (primary). Rubric criteria come from `eval-strategy-lead`'s metric.
>
> **When to invoke:** any time an LLM grades outputs (absolute score or pairwise), before trusting a single judged number.
>
> **Output:** a judge prompt + anchored rubric + structured-verdict schema + a calibration/bias-audit report.

## Procedure

1. **Write anchored criteria, not a vibe scale.** For each quality dimension, define what a pass looks like with a concrete anchor per level (e.g. "2 = cites a real source and answers the question; 1 = answers but no source; 0 = fabricates"). "Rate 1-10" produces noise.
2. **Force a structured verdict + reason.** The judge returns `{criterion: level, reason: "..."}` — the reason makes disagreements auditable and catches the judge bluffing.
3. **Prefer pairwise when absolute is noisy.** "Is A or B better?" is more stable than "score A 1-5". Randomize which side is A to defeat position bias.
4. **Pin the judge model + version + temperature.** Record them with every result; a judge that silently upgrades invalidates the baseline.
5. **Calibrate against humans on a sample.** Have humans label ~30-50 examples; measure judge-human agreement (e.g. Cohen's κ / raw agreement). If the judge doesn't agree with humans, fix the rubric before trusting the judge at scale.
6. **Audit for the known biases.** Position/order (swap A/B), verbosity/length (does longer win regardless?), self-preference (does the judge favor its own model family?), leniency drift (scores creeping up over runs). Document each check and its result.

## Worked example

> Judging two draft replies pairwise.

- Criteria → groundedness (anchored 0-2), helpfulness (0-2), policy-adherence (pass/fail hard gate).
- Pairwise + side-randomized; structured `{winner, per_criterion, reason}`.
- Calibration → 40 human-labeled pairs, raw agreement 88%; rubric tightened on "helpfulness" after 3 disagreements.
- Bias audit → position bias 3% after randomization (ok); verbosity: longer reply won 51% (no strong length bias); pinned `claude-sonnet-5` judge.

## Guardrails

- **A judge with no rubric and no human calibration is a random-number generator** — do not report its scores as fact.
- **Never let the judge model be the model under test** without a self-preference audit.
- **Re-calibrate when you change the judge model or the rubric** — the old baseline no longer applies.
