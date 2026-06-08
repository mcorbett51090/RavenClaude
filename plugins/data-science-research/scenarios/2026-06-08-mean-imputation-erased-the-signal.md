---
scenario_id: 2026-06-08-mean-imputation-erased-the-signal
contributed_at: 2026-06-08
plugin: data-science-research
product: pandas
product_version: "unknown"
scope: likely-general
tags: [missingness, imputation, eda, feature-engineering, mnar]
confidence: high
reviewed: false
---

## Problem

A credit-risk model treated a 35%-missing `income_verified` field by filling the blanks with the column mean and moving on. The model underperformed and nobody could say why. The missingness was not random: income went unverified precisely for the highest-risk applicants (thin-file or self-employed), so "missing" itself carried the signal. Mean-imputing flattened that informative pattern into a single uninformative value and erased the strongest predictor in the data.

## Constraints context

- ~80k applications, several fields 20-40% missing, missingness concentrated in specific applicant segments.
- The team's default pipeline auto-imputed every numeric column with its mean before any analysis.
- No one had actually looked at *why* values were missing — the missingness mechanism was assumed MCAR without checking.

## Attempts

- Tried: dropping every row with any missing value. Failed — it discarded ~45% of the data and, worse, systematically removed the high-risk segment, biasing the model toward easy cases.
- Tried: median imputation instead of mean to be "more robust." Helped marginally against outliers but made the same fundamental error — it still erased the informative-missingness signal by treating a meaningful blank as noise.
- Tried: profiling the missingness mechanism first (correlating missingness with the target and other features), adding an explicit `income_verified_missing` indicator feature, and only then imputing the underlying value. This worked — the missingness-indicator became a top predictor.

## Resolution

The missingness indicator turned out to be one of the most predictive features in the model; once "this was missing" was encoded as its own signal rather than smoothed away, performance jumped and the model finally reflected the real risk structure. The fix was to ask *why* the value was missing before deciding how to fill it.

## Lesson

Understand missingness before imputing: missing-not-at-random data carries signal, and mean/median imputation erases it. Profile the mechanism first (is missingness correlated with the target?), add a missingness-indicator feature when the blank is informative, and treat imputation as a modeling decision — never a reflexive default.
