# Risk = renewal proximity × engagement, not proximity alone

**Status:** Absolute rule
**Domain:** CS renewal-risk design
**Applies to:** `customer-success-analytics`

---

## Why this exists

Every account eventually hits 90 days to renewal — that is a calendar fact, not a risk signal. If renewal proximity alone flags an account Red, the CS leader gets a list of every account in the next quarter: useless as a prioritization tool. The risk signal that actually predicts whether an account churns is proximity combined with a down-trend, a support spike, or champion / sponsor silence. An account at 60 days to renewal with strong usage and a recent NPS of 9 is not at risk; an account at 180 days to renewal with a 40% usage drop and three escalated support tickets needs attention now. The combination is the signal; either input alone is noise.

## How to apply

Design the renewal-risk model as an explicit product of two inputs: days to renewal (proximity) and current engagement state. Both must be unfavorable to classify as renewal-risk Red.

```sql
-- Renewal-risk classification:
renewal_risk_tier =
  CASE
    WHEN days_to_renewal <= 90 AND health_tier = 'RED'    THEN 'HIGH'
    WHEN days_to_renewal <= 90 AND health_tier = 'YELLOW' THEN 'MEDIUM'
    WHEN days_to_renewal <= 180 AND health_tier = 'RED'   THEN 'MEDIUM'
    WHEN days_to_renewal <= 90 AND health_tier = 'GREEN'  THEN 'LOW'
    ELSE 'MONITOR'
  END

-- Counterexample (do NOT do this):
renewal_risk_tier =
  CASE WHEN days_to_renewal <= 90 THEN 'HIGH' ELSE 'LOW' END
  -- ^ flags every account in Q this quarter as HIGH — meaningless

-- Actionability test: can CS leader sort by
-- (renewal_risk_tier = HIGH) and get < 20% of the book?
-- If not, the proximity threshold is too wide.
```

**Do:**
- Require both a proximity threshold AND a sub-Green health tier for a HIGH renewal-risk classification.
- Validate the model against the actionability bar: a sort on HIGH risk should return a manageable call list, not the whole book.
- Include trend direction in the health input — a declining Yellow is higher risk than a stable Yellow.

**Don't:**
- Flag all accounts within 90 days of renewal as high-risk.
- Design renewal-risk columns without an engagement/health input.
- Use proximity alone to trigger outreach sequences — this trains CS leaders to ignore the alerts.

## Edge cases / when the rule does NOT apply

Accounts on their first renewal with no historical engagement baseline have unknown risk; treat them as MEDIUM regardless of proximity and health until a trend exists. Very high-ACV accounts (enterprise) may warrant a risk-based review even when health is Green and proximity is 180 days, given the asymmetric blast radius.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the renewal-risk mart model.
- [`./direction-beats-absolute-level-model-trend-columns-explicitly.md`](./direction-beats-absolute-level-model-trend-columns-explicitly.md) — the companion rule on using trend direction as the engagement input.

## Provenance

Codifies the plugin's §4 house opinion #4 ("Renewal proximity × engagement, never proximity alone"). The proximity-only model is the most common renewal-risk anti-pattern; it floods the CS call list and trains the team to treat the alert as noise.

---

_Last reviewed: 2026-06-05 by `claude`_
