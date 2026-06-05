# Fix Activation Before Fixing Retention

**Status:** Primary diagnostic
**Domain:** Product metrics / growth
**Applies to:** `product-management`

---

## Why this exists

Retention analysis performed on a cohort with poor activation is measuring the wrong population. Users who never experienced the product's core value proposition don't retain — not because retention is broken, but because activation was never achieved. Investing in retention features, onboarding flows, and re-engagement campaigns before the activation moment is well-defined and accessible produces expensive work on a leaky funnel. The activation metric is the product's first proof that value has been delivered to a specific user; until it is healthy, the retention number is uninterpretable noise.

## How to apply

Diagnose the activation funnel before running retention analysis or prioritizing retention-improving features.

```
Activation Diagnostic — Before Retention Work
──────────────────────────────────────────────────────
Step 1 — DEFINE THE ACTIVATION MOMENT
  The activation moment is the first time a user completes the action that
  predicts long-term retention.
  Proxy if unknown: run a cohort correlation — which Day-1 or Week-1 action
  is most predictive of Day-30 retention? (regression or lift analysis)
  Examples: "User creates their first X", "User shares a result",
            "User connects their first integration"

Step 2 — MEASURE ACTIVATION RATE
  Activation rate = (Users who reached the activation moment) / (New signups)
  Measured on a cohort basis (same signup week / month)
  Segment by: source, device, onboarding path, plan tier

Step 3 — IDENTIFY THE ACTIVATION FUNNEL DROP-OFFS
  Map the steps from signup to activation moment.
  Find where the largest drop-off occurs (this is the fix, not the last step).

Step 4 — SET AN ACTIVATION TARGET
  Target activation rate: <X% by Y date>
  Gate: Do not run retention campaigns on cohorts with activation < Z%
        (Z% is the threshold below which retention work is premature)

Step 5 — VALIDATE THAT RETENTION CORRELATES WITH ACTIVATION
  After improving activation: does the cohort's Day-30 retention improve?
  If yes, activation was the root cause; continue.
  If no, the retention problem is post-activation; revisit the activation definition.
```

**Do:**
- Define the activation moment from data, not from intuition — the "aha moment" is an empirical claim that requires cohort analysis to validate.
- Run activation diagnostics at the segment level; mobile vs. web, self-serve vs. sales-assisted users often have entirely different activation funnels.
- Set a minimum activation rate threshold below which retention optimization is paused in favor of activation work.

**Don't:**
- Use "account created" or "email verified" as the activation moment — these measure intent, not value delivery.
- Run A/B tests on retention email copy while the activation funnel has a 40% drop-off in the first step; the funnel is the experiment that needs to run first.
- Conflate activation rate (percent of signups reaching the moment) with activated user behavior (what activated users do next).

## Edge cases / when the rule does NOT apply

- **Existing product with high activation (> 80%) and declining retention** — the problem is genuinely post-activation; skip directly to retention analysis.
- **B2B products with long sales cycles** — activation is partly a sales and onboarding process, not purely product-driven; the diagnostic still applies but the interventions span product and customer success.

## See also

- [`../agents/product-metrics-analyst.md`](../agents/product-metrics-analyst.md) — owns funnel analysis, cohort retention, and the activation moment definition.
- [`./north-star-with-input-metrics.md`](./north-star-with-input-metrics.md) — activation rate is typically an input metric in the North Star hierarchy; fixing it should move the North Star.

## Provenance

Codifies the product-metrics-analyst's activation-first diagnostic from the product-management plugin's CLAUDE.md §2 #4 (outcomes over outputs) and §2 #5 (North Star with input metrics). The activation-before-retention sequencing reflects standard growth product management practice (Sean Ellis, Reforge growth frameworks).

---

_Last reviewed: 2026-06-05 by `claude`_
