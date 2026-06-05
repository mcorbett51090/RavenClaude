---
scenario_id: 2026-06-05-underpowered-no-significant-difference
contributed_at: 2026-06-05
plugin: applied-statistics
product: experiment-design
product_version: "n/a"
scope: likely-general
tags: [underpowered, null-result, power, mde, equivalence]
confidence: medium
reviewed: false
---

## Problem

A product manager reported that a redesigned onboarding flow "made no difference" — the A/B test came back p = 0.31, not significant — and wanted to roll it back and stop investing in onboarding. The redesign had cost the team a quarter. The consultant was asked whether "no significant difference" really meant "no effect," before the rollback.

## Context

- Design: two-arm A/B test, conversion-rate primary, baseline ≈ 8%, **n ≈ 1,200 per arm** (the test ran only one week before the PM pulled the result).
- The observed lift was +0.9 percentage points (8.0% → 8.9%), p = 0.31, 95% CI on the absolute difference roughly **[−0.8, +2.6] points**.
- No power analysis had been run before launch; the sample size was "however many we got in a week."

## Attempts

- Tried: computed the test's **achieved power / MDE** post-hoc — not to "prove" an effect, but to characterize what the study *could* have detected (pitfall #6; [`../best-practices/interpret-null-with-power-and-mde.md`](../best-practices/interpret-null-with-power-and-mde.md)). With n ≈ 1,200/arm at baseline 8%, α = 0.05, power 0.80, the **MDE was ≈ +2.0–2.2 percentage points** — i.e., the test was only powered to detect a *huge* (~25% relative) lift. A realistic +1-point lift was well inside the noise. Outcome: "not significant" here means "underpowered," not "no effect."
- Tried: read the **confidence interval** as the deliverable, not the p-value (house opinion #2). The CI `[−0.8, +2.6]` includes both a meaningful positive lift and a small negative — it is *consistent with* a worthwhile improvement. A null result whose CI still spans the decision-relevant effect is **inconclusive**, not negative.
- Tried (the move that worked): reframed the decision. The honest options were (a) **extend the test** to the sample size needed to detect the smallest lift worth shipping (computed with `scripts/stat_calc.py samplesize --baseline 0.08 --mde 0.01` → a far larger n), or (b) if onboarding wasn't worth that runway, **decide on cost/benefit grounds, not on a misread null.** A genuine "no effect" claim would require an **equivalence/non-inferiority** framing (TOST) with a pre-set margin — which this test was nowhere near powered for.

## Resolution

"No significant difference" was an **underpowered null**, not evidence of no effect — the classic absence-of-evidence-vs-evidence-of-absence error. The CI was wide and straddled a shippable lift. The defensible read: the test couldn't answer the question at the sample size collected; either extend it to a pre-computed n or make the call on other grounds — but do **not** record "onboarding doesn't matter" as a finding.

**Action for the next consultant hitting this pattern:** never accept "p > 0.05, so no effect." Report the **CI and the MDE the study could detect**; if the CI still contains the smallest effect worth acting on, the result is *inconclusive*. A true "no effect" claim needs an equivalence test (TOST) against a pre-specified margin, not a non-significant superiority test. Size the would-be extension with the `power-and-sample-size` skill / `scripts/stat_calc.py samplesize` before quoting a runway.

**Sources for the methods cited:** the absence-of-evidence principle — Altman & Bland (1995), "Statistics notes: Absence of evidence is not evidence of absence," *BMJ* 311:485; equivalence/TOST — Lakens (2017), "Equivalence Tests," *Social Psychological and Personality Science* 8(4):355-362. Two-proportion power/MDE per the [`../skills/power-and-sample-size/SKILL.md`](../skills/power-and-sample-size/SKILL.md) workhorse. Figures are illustrative; validate against the engagement's actual data before a deliverable.
