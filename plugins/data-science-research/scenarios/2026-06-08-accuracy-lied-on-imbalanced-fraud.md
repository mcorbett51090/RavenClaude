---
scenario_id: 2026-06-08-accuracy-lied-on-imbalanced-fraud
contributed_at: 2026-06-08
plugin: data-science-research
product: scikit-learn
product_version: "unknown"
scope: likely-general
tags: [metric-choice, imbalance, evaluation, precision-recall, fraud]
confidence: high
reviewed: false
---

## Problem

A fraud-detection model was reported as "99.3% accurate" and signed off on that number. In production it caught almost no fraud. The base rate of fraud was ~0.7%, so a model that predicted "never fraud" for every transaction scored 99.3% accuracy by doing nothing useful. Accuracy was the wrong metric for a rare-positive decision with a wildly asymmetric cost (a missed fraud costs real money; a false alarm costs a review).

## Constraints context

- ~2M transactions, ~0.7% positive class — severe imbalance.
- The business cost was asymmetric: a false negative (missed fraud) was ~30x more expensive than a false positive (a flagged-for-review legit transaction).
- Stakeholders had anchored on "accuracy" because it was the one number everyone understood.

## Attempts

- Tried: rebalancing with naive random oversampling of the minority class, then re-reporting accuracy. Failed — accuracy stayed high and meaningless, and the oversampling done *before* the split leaked duplicated minority rows across train/test, inflating the score further.
- Tried: switching to ROC-AUC alone. Helped frame ranking quality but hid the operating-point problem — at the threshold the business would actually use, recall on fraud was poor and AUC didn't show it.
- Tried: choosing the metric from the decision — precision/recall at the deployment threshold, the precision-recall curve (not ROC, which flatters on imbalance), and a cost-weighted score reflecting the 30:1 asymmetry; plus moving the resampling inside the CV fold. This worked: the team optimized recall at a precision floor the review team could staff.

## Resolution

Re-scored against recall-at-a-precision-floor and a cost-weighted metric, the "99.3% accurate" model was exposed as catching ~6% of fraud at the chosen threshold. A simpler model tuned to the real metric caught ~60% of fraud at a precision the review team could handle. The headline accuracy had been measuring the base rate, not the model.

## Lesson

The metric must match the decision: accuracy on a 0.7%-positive problem measures the base rate, not skill. For rare positives use the precision-recall curve and report precision/recall at the deployment threshold; when costs are asymmetric, weight the metric by the real cost ratio. And resample inside the fold — never before the split.
