# The acceptance test is a sort, not a slide

**Status:** Absolute rule
**Domain:** CS health model design
**Applies to:** `customer-success-analytics`

---

## Why this exists

A health model ships to solve a specific operational problem: the CS leader needs to know, right now, which accounts deserve a call before the renewal window closes. The acceptance test for that model is not a presentation deck, a ROC curve, or a validation summary — it is a live sort. The CS leader opens the surface, sorts by `(tier = Red AND days_to_renewal < 90)`, and in under two minutes has an actionable call list of manageable length. If that sort returns the entire book, the thresholds are too permissive. If it returns zero accounts when there are known high-risk renewals, the signals are wrong. The sort is the test; everything else is supporting evidence.

## How to apply

Before declaring a health-model implementation done, run the acceptance test live: sort the production surface by the highest-risk filter and time how long it takes a CS leader to read and interpret the list.

```
Acceptance test protocol:

Sort query:
  SELECT account_name, composite_tier, days_to_renewal, tier_drivers
  FROM v_account_health_kpis
  WHERE composite_tier = 'RED' AND days_to_renewal < 90
  ORDER BY days_to_renewal ASC;

Acceptance criteria:
  1. Query runs in < 30 seconds (performance)
  2. Results are readable in < 2 minutes (actionability of list length)
  3. List length is < 20% of total book (signal specificity)
  4. Each row includes tier_drivers — the named signals that caused Red (explainability)
  5. CS leader can identify 1–2 accounts they already know as high-risk (face validity)

If criterion 3 fails: tighten the threshold or add AND conditions to the Red rule.
If criterion 5 fails: re-examine whether the signals are actually predictive of this team's churn pattern.
```

**Do:**
- Run the acceptance test with the actual CS leader, not just the analytics team.
- Treat a failed acceptance test as a signal-tuning or threshold problem, not a data-quality problem.
- Re-run the acceptance test quarterly after any tier rule changes.

**Don't:**
- Declare the model "done" based on back-test metrics alone without the live sort test.
- Use a slide or summary stat ("75% of churned accounts were Red before churn") as the sole acceptance criterion.
- Accept a model where the sort returns more than 20–25% of the book without a documented rationale.

## Edge cases / when the rule does NOT apply

Very small account books (fewer than 20 total accounts) may have a high proportion of genuinely high-risk accounts in any given quarter; the 20%-of-book threshold doesn't apply to micro-books. Enterprise-only CS motions with a small named account list may set the acceptance criterion at absolute count (e.g., "fewer than 5 Red accounts at any time unless there is an active crisis period") rather than a percentage.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the model and must run the acceptance test before signing off.
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — responsible for threshold tuning when the sort returns too many or too few accounts.

## Provenance

Codifies the plugin's §4 house opinion #9 ("The acceptance test is a sort, not a slide"). The over-reliance on back-test metrics as the only acceptance criterion is the most common sign-off error in CS health model deployments; the sort test is the operationally correct standard.

---

_Last reviewed: 2026-06-05 by `claude`_
