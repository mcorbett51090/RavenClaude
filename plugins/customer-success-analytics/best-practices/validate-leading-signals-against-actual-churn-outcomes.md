# Validate leading signals against actual churn outcomes

**Status:** Primary diagnostic
**Domain:** CS churn signal validation
**Applies to:** `customer-success-analytics`

---

## Why this exists

Calling a signal "churn-leading" without back-testing it against actual churn events is hypothesis, not evidence. Many signals that intuitively feel predictive — login count, email opens, CSP sentiment flags — describe account engagement but do not measurably correlate with subsequent churn. A health model built on unvalidated signals generates false Reds (wasting CS time on accounts that renew fine) and false Greens (missing accounts that churn despite appearing healthy). Back-testing against a holdout of past churned accounts is the only way to know which signals actually lead churn, with what lead time, and at what threshold.

## How to apply

Before finalizing any signal as a tier input, run a back-test: for accounts that churned in the past 12 months, examine whether the candidate signal was below its threshold N days before the churn event. Calculate precision (Red accounts that actually churned) and recall (churned accounts that were Red before churning) for each candidate signal.

```
Signal validation back-test protocol:

1. Pull churned accounts from the past 12 months.
2. For each churned account, pull the candidate signal value at T-30, T-60, T-90 before churn.
3. Compute:
   - lead_time: how many days before churn the signal crossed the threshold
   - precision: churned / (churned + not-churned) among all accounts where signal was below threshold
   - recall: accounts where signal was below threshold before churn / total churned accounts
4. Baseline: compare to a naive model (e.g., "flag all accounts in bottom 20% of usage")

Minimum evidence bar to include signal in tier:
   precision > 40% AND recall > 30% at a lead time of >= 30 days [ESTIMATE — calibrate to your book]

Signals that fail both bars: remove from tier; keep in sub-indicator display for observational value.
```

**Do:**
- Back-test every candidate signal before including it in the tier rule expression.
- Include a "signal validation date" in the mart metadata so the team knows when each signal was last verified.
- Re-validate signals annually or after a major product change that could alter baseline usage patterns.

**Don't:**
- Assume a signal is leading because it is correlated with low health scores — a lagging signal is highly correlated with churn but fires too late to act.
- Include a signal in the tier rule that has never been back-tested, even if it seems intuitively predictive.
- Use the full dataset as both the training and validation set — use a holdout period.

## Edge cases / when the rule does NOT apply

For new products or early-stage implementations with fewer than 50 historical churn events, back-testing lacks statistical power. In this case, use documented domain-standard signals (usage decline, support spike, NPS drop — see the plugin's knowledge bank) as placeholders and commit to back-testing after 12 months of operation. The placeholders are labeled "unvalidated — domain default" until the back-test runs.

## See also

- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — owns signal selection, validation, and threshold tuning.
- [`./transparent-rule-based-tiering-before-ml-in-phase-one.md`](./transparent-rule-based-tiering-before-ml-in-phase-one.md) — the companion rule on keeping the tier structure understandable during validation.

## Provenance

Codifies the signal-validation discipline that the `churn-signal-analyst` agent is built around. The unvalidated-signal error is the most common root cause of "the score stopped predicting" complaints after a health tier ships; this rule documents the prevention.

---

_Last reviewed: 2026-06-05 by `claude`_
