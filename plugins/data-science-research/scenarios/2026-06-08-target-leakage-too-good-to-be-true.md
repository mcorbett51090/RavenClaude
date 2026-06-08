---
scenario_id: 2026-06-08-target-leakage-too-good-to-be-true
contributed_at: 2026-06-08
plugin: data-science-research
product: scikit-learn
product_version: "unknown"
scope: likely-general
tags: [leakage, cross-validation, evaluation, pipeline, churn]
confidence: high
reviewed: false
---

## Problem

A team built a customer-churn model that scored 0.97 ROC-AUC in offline evaluation and everyone was thrilled — until it predicted nothing useful in production. Two separate leaks were inflating the offline score: a `StandardScaler` and a `TargetEncoder` were fit on the *full* dataset before the train/test split (so the test set's statistics bled into training), and one feature — `days_since_last_login` — was computed using a snapshot taken *after* the churn label's observation window, so it encoded the answer.

## Constraints context

- ~120k customers, ~40 features, moderate class imbalance (~8% churn).
- Evaluation was a single 80/20 train/test split — one number, no error bar.
- The preprocessing lived in a few cells above the split, reused "for convenience" across experiments.

## Attempts

- Tried: adding more features and a fancier model (gradient boosting) to "make it robust." Failed — it raised the leaked score further, deepening the illusion. The problem was the evaluation, not the model.
- Tried: a single fixed test set held out earlier. Helped the pre-split-fit leak only partially, and it was still one split with no spread — and it didn't catch the post-window feature.
- Tried: moving every fit-based transform into a scikit-learn `Pipeline` so they fit *inside* each CV fold, switching to stratified k-fold (reporting the spread, not one number), and auditing each feature for whether it was available at the label's prediction time — which removed `days_since_last_login` as defined. This worked.

## Resolution

Inside-the-fold fitting plus the prediction-time-availability audit dropped the score to a believable ~0.78 ROC-AUC with a visible cross-fold spread — and *that* model held up in production because the offline number finally measured the real task. The honest score was lower but true; the 0.97 had been measuring leakage.

## Lesson

Leakage is the cardinal sin: fit every transform inside the CV fold, split before any fit, and audit every feature for whether it exists at prediction time. A single train/test split lies — cross-validate and report the spread. A suspiciously high score is a leakage alarm, not a win.
