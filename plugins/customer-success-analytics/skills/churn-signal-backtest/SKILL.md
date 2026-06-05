---
name: churn-signal-backtest
description: "Back-test a candidate churn signal or the full tier rule set against historical renewal outcomes to validate predictive strength before the signal enters the production health tier. Reach for this skill when a new signal is proposed, when the tier is misfiring, or after the first full renewal cycle to tune thresholds."
---

# Skill: Churn Signal Backtest

A signal that feels predictive is a hypothesis. A signal that has been back-tested against real renewal outcomes is evidence. This skill turns the hypothesis into a result the CS team can act on — or a documented reason not to use the signal.

## When to reach for this skill

- A new signal is proposed for inclusion in the health tier.
- The tier has misfired (accounts churned while Green, or the Red list is dominated by accounts that renewed).
- The first full renewal cycle has completed and the team has outcome data to validate against.
- A threshold change is proposed — validate before deploying to production.

## Step 1 — Assemble the outcome data set

The back-test requires a historical data set that pairs signal values at a fixed pre-renewal lookback (90 or 180 days before renewal) with the actual outcome (renewed / churned / expanded).

```sql
-- Outcome data structure (domain-neutral)
SELECT
    account_id,
    renewal_date,
    outcome,                  -- 'renewed' | 'churned' | 'expanded'
    signal_value_at_T_minus_90,
    signal_threshold_crossed  -- boolean: was the threshold crossed at T-90?
FROM [mart layer]
WHERE renewal_date BETWEEN [start] AND [end]
  AND outcome IS NOT NULL     -- exclude in-flight renewals
```

**Minimum sample:** back-tests below 30 completed renewals are directional only — label the result `provisional` and note the sample size in the tier rule.

## Step 2 — Compute precision and recall at the proposed threshold

For the signal at the proposed threshold value:

```
True Positive (TP)  = threshold crossed AND account churned
False Positive (FP) = threshold crossed AND account renewed
True Negative (TN)  = threshold not crossed AND account renewed
False Negative (FN) = threshold not crossed AND account churned

Precision = TP / (TP + FP)   — "when the signal fires, how often is it right?"
Recall    = TP / (TP + FN)   — "of all churns, how many did the signal catch?"
```

**Minimum bar for tier inclusion (per the churn-signal decision tree):** Precision > 40% AND Recall > 30%.

## Step 3 — Sweep thresholds to find the operating point

If the proposed threshold fails the bar, sweep a range of threshold values and plot Precision vs. Recall. Report:
- The threshold that maximizes Precision (minimizes false alarms)
- The threshold that maximizes Recall (minimizes missed churns)
- The balanced operating point (F1 maximum or the closest Precision/Recall trade that the CS team can act on)

Include the sweep table in the back-test report so the CS leader can see the trade-off and choose the operating point for their team's capacity.

## Step 4 — Test for segment confounding

A signal that predicts well overall may fail within a specific segment (SMB vs. enterprise, a specific vertical, or accounts with very short tenures). Break the back-test down by the top 2-3 segments:

```
Segment      | Precision | Recall | N (sample) | Note
-------------|-----------|--------|------------|-----
Enterprise   | 0.52      | 0.38   | 87         | Above bar
SMB          | 0.31      | 0.27   | 43         | Below bar — sub-indicator only for SMB
New accounts | 0.18      | 0.45   | 22         | Small sample — provisional
```

If precision/recall diverges significantly across segments, recommend a segment-specific threshold or sub-indicator treatment rather than a single universal rule.

## Step 5 — Produce the back-test report

```
Signal:            [signal name]
Threshold tested:  [value + window]
Data range:        [start] to [end]
N renewals:        [count]
Outcome split:     [churned: N | renewed: N | expanded: N]

At proposed threshold:
  Precision: [value]    bar: >40%   PASS/FAIL
  Recall:    [value]    bar: >30%   PASS/FAIL

Recommended action:
  INCLUDE IN TIER RULE    — thresholds tuned to [value] with [window]
  SUB-INDICATOR ONLY      — precision/recall below bar; show in explainability panel
  VALIDATE FIRST          — insufficient sample; mark provisional; re-test after [date]
  DO NOT INCLUDE          — lagging signal or no predictive value at any threshold

Segment notes: [any material divergence found in Step 4]
```

## Pitfalls

- Back-testing on in-flight renewals (outcome unknown) — always filter to completed outcomes only.
- Treating a back-test on fewer than 30 renewals as definitive — label it provisional.
- Selecting the threshold that maximizes Recall at the cost of 10% Precision — the CS team will stop trusting a Red list that is mostly wrong.
- Forgetting to re-run the back-test after a product change that shifts the baseline of a signal.

## See also

- [`../../knowledge/cs-health-metrics-and-churn-indicators.md`](../../knowledge/cs-health-metrics-and-churn-indicators.md) — leading vs. lagging signal classification
- [`../../knowledge/customer-success-decision-trees.md`](../../knowledge/customer-success-decision-trees.md) — churn signal selection decision tree
- [`../health-tier-design/SKILL.md`](../health-tier-design/SKILL.md) — the tier design skill that consumes this back-test result
