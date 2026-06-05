# Use transparent rule-based tiering before ML in phase one

**Status:** Absolute rule
**Domain:** CS health scoring
**Applies to:** `customer-success-analytics`

---

## Why this exists

A CS leader cannot act on a health score they cannot explain. When a black-box or ML-derived score flips an account to Red, the first question is "why?" — and if the answer is "the model weighed 47 features," the leader has no confidence in the call and no story for the account conversation. A rule-based tier (e.g., "Red because usage trended down 30% over 60 days AND support tickets tripled") is immediately actionable and defensible. ML is a later-phase option once the rule tier has been tuned against a real renewal cycle and the team understands which signals the rules miss.

## How to apply

Design the phase-one tier as an explicit rule expression with named signals, thresholds, and direction. Every account that is Red names the 2–3 signals that put it there, each with its value, threshold, and observation window.

```
Phase-one tier rule template:

GREEN: (usage_trend_30d >= -10%) AND (support_ticket_count_30d <= 2) AND (nps_score >= 7 OR nps_score IS NULL)
YELLOW: (usage_trend_30d between -30% and -10%) OR (support_ticket_count_30d between 3 and 6)
RED: (usage_trend_30d < -30%) OR (support_ticket_count_30d > 6) OR (nps_score < 5)

Per-Red explainability output:
  Account: Acme Corp
  Tier: RED
  Drivers:
    — usage_trend_30d: -42% (threshold: -30%)
    — support_ticket_count_30d: 8 (threshold: 6)
```

**Do:**
- Name every signal in the tier expression with its threshold and direction.
- Show the driving signals for every Red and Yellow account — never just the tier label.
- Document the rule expression in version control so changes are auditable.

**Don't:**
- Ship a composite weighted score as the phase-one tier without a per-signal explainability layer.
- Use ML scores as tier inputs before the transparent tier has been tuned against one renewal cycle.
- Allow a tier to produce a "Red" without a named driver that a CS leader can use in a partner conversation.

## Edge cases / when the rule does NOT apply

In phase 2 or beyond, once the rule tier has a track record and the team has identified signals the rules miss, a weighted composite or ML layer is appropriate — additive to the rule tier's explainability, not replacing it. For very large account books where manual threshold tuning is impractical, a statistically-fitted threshold (e.g., logistic regression coefficient) is acceptable as long as the rule expression itself remains human-readable.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the health tier and the mart that powers it.
- [`./anchor-on-the-csp-native-score-then-add-signals-additively.md`](./anchor-on-the-csp-native-score-then-add-signals-additively.md) — the companion rule on layering signals without replacing the CSP's native score.

## Provenance

Codifies the plugin's §4 house opinion #1 ("transparent rule-based tiering over black-box / ML in phase 1"). The ML-first error is the most common over-engineering pattern observed in CS health-score implementations; the rule is the corrective.

---

_Last reviewed: 2026-06-05 by `claude`_
