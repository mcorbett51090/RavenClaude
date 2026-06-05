# Back-test every candidate signal against historical churn outcomes before adding it to the tier rule

**Status:** Absolute rule
**Domain:** CS analytics — signal validation
**Applies to:** `customer-success-analytics`

---

## Why this exists

A signal that seems predictive from intuition or anecdote may be lagging, confounded, or segment-specific. Adding an unvalidated signal to the production tier rule degrades the tier's precision — the CS team gets more false Reds, stops trusting the list, and stops acting on it. Once trust is lost, rebuilding it requires a full cycle of validated outcomes. The back-test is the evidence bar that signals must clear before they gate actions on real accounts.

## How to apply

Before adding any new signal to the tier rule:

```
1. Assemble the historical outcome data set (renewed / churned / expanded)
   — minimum 30 completed renewals for a non-provisional result

2. Compute precision and recall at the proposed threshold
   — Precision > 40%: when the signal fires, it's right more than 4 times in 10
   — Recall > 30%: the signal catches at least 3 in 10 actual churns

3. Sweep thresholds if the proposed value fails — find the operating point the CS team can act on

4. Test for segment confounding — a signal that predicts well overall may fail in SMB or a specific vertical

5. Document the result in a back-test report and update the signal's metadata in the knowledge bank
```

Use the `../skills/churn-signal-backtest/SKILL.md` playbook.

**Do:**
- Label back-tests on fewer than 30 renewals as `provisional` — the number is directional, not decisive.
- Sweep thresholds before declaring a signal unpredictive — the proposed threshold may be the problem, not the signal.
- Re-run the back-test after a product change that shifts the signal's baseline.

**Don't:**
- Add a signal marked `unvalidated-domain-default` to the tier rule because the team ran out of time — that is what the provisional label is for.
- Optimize for Recall alone at the cost of Precision: a Red list that is mostly wrong destroys CS team trust faster than a Red list that is incomplete.

## Edge cases / when the rule does NOT apply

- The churn-signal decision tree classifies the signal as a sub-indicator (show in explainability panel, not in the tier expression) — sub-indicators do not require a back-test pass before they appear in the explainability panel, only before they move into the tier rule itself.

## See also

- [`../skills/churn-signal-backtest/SKILL.md`](../skills/churn-signal-backtest/SKILL.md) — the step-by-step back-test playbook
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — the agent that runs and interprets back-tests
- [`../knowledge/customer-success-decision-trees.md`](../knowledge/customer-success-decision-trees.md) — churn signal selection tree

## Provenance

Codifies `CLAUDE.md` §4 house opinion #1 (transparent rule-based tiering) and the anti-pattern "a custom weighted composite shipped in phase 1 before the additive sub-signals have shown they diverge." A signal without a back-test is a hypothesis wearing a rule.

---

_Last reviewed: 2026-06-05 by `claude`_
