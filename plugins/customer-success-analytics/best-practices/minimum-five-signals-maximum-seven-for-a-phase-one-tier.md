# Use 5-7 signals in a phase-one tier — more is noise, fewer is fragile

**Status:** Pattern
**Domain:** CS analytics — tier design
**Applies to:** `customer-success-analytics`

---

## Why this exists

A tier rule with 2-3 signals is fragile: one missing data source breaks the whole tier. A tier rule with 10+ signals is uninterpretable: the CS rep can't explain to the account what drove the Red classification, and the analyst can't tell which signal is actually doing the work. The 5-7 range is the empirically-validated sweet spot for B2B CS health tiers — enough redundancy to tolerate a missing source, few enough to explain to a non-technical CS leader in a 10-minute walkthrough.

## How to apply

When designing a phase-one tier, apply the signal-count discipline during Step 2 of the health-tier-design skill:

```
Signal selection budget for phase one: 5-7 signals

One signal per category (max):
  - Usage trend (mandatory) — 1 signal
  - Health-score trend (if CSP native score available) — 1 signal
  - Renewal proximity × engagement gate (mandatory) — 1 signal
  - Support load (P1/P2 rate, not raw volume) — 1 signal
  - Sentiment (NPS or CSAT, most recent in window) — 1 signal
  - Champion presence / depth — 1 signal
  - Collaboration / escalation keyword density (optional if source available) — 1 signal
```

If 7 signals are still insufficient because a stakeholder insists on adding more:
1. Require a back-test result showing the additional signal adds predictive power the current set lacks.
2. Replace, don't add — if a new signal is better than an existing one, swap it; don't grow the rule.

**Do:**
- Document the signal count and the category rationale in the tier-design record.
- Add a "signal candidates not included and why" section — it shows the decision was deliberate, not accidental.

**Don't:**
- Add signals because a department lobbied for their metric to be represented — "stakeholder visibility" is not a predictive criterion.
- Treat a 5-7 signal limit as a reason to skip validation — count and quality are both required.

## Edge cases / when the rule does NOT apply

- A validated phase-2 or phase-3 tier where back-tests have consistently shown that additional signals add measurable precision — document the back-test evidence for each signal beyond 7.

## See also

- [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md) — Step 2 covers signal selection with the "5-7 max; more is noise" guidance
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — validates whether a proposed additional signal adds predictive value

## Provenance

Derived from standard CS analytics practice and the `health-tier-design` skill §2: "Pick the signals that *predict the outcome*, not signals the dashboard happens to have. 5-7 max; more is noise." The upper bound keeps the tier explainable; the lower bound keeps it robust.

---

_Last reviewed: 2026-06-05 by `claude`_
