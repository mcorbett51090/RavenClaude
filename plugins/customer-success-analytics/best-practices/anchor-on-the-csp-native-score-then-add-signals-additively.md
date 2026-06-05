# Anchor on the CSP native score, then add signals additively

**Status:** Absolute rule
**Domain:** CS health scoring
**Applies to:** `customer-success-analytics`

---

## Why this exists

If the team trusts its customer-success platform's (Planhat's, Gainsight's, or any CSP's) health score, replacing it silently with a custom composite invites the deadliest of arguments: "why doesn't your dashboard match what I see in the CSP?" The conflict between two scoring systems destroys CS-leader confidence in both. The correct phase-one posture is to pull the CSP's native score as-is and display custom signals alongside it as visible sub-indicators — additive, not substitutive. The custom composite only becomes the primary signal in a later phase after the sub-signals have demonstrably diverged from the CSP score in predicting actual churn.

## How to apply

Design the health mart with a dedicated `csp_health_score` column sourced directly from the CSP API or export. Additional signals (usage trend, support load, engagement) surface in separate columns and sub-indicator tiles — never silently folded into a re-computed aggregate.

```sql
-- Phase-one health snapshot schema pattern:
fct_account_health_snapshot (
  account_key         INT,
  snapshot_date       DATE,
  csp_health_score    FLOAT,         -- pulled as-is from CSP; the anchor
  csp_tier            VARCHAR(10),   -- CSP's own Red/Yellow/Green label
  usage_trend_30d     FLOAT,         -- custom sub-indicator #1
  support_spike_flag  BOOLEAN,       -- custom sub-indicator #2
  nps_score           INT,           -- custom sub-indicator #3 (NULL if not collected)
  composite_tier      VARCHAR(10),   -- custom tier (phase 2+); NULL in phase 1
  tier_drivers        JSON           -- named signals for each non-Green account
)

-- Sub-indicator display rule:
-- If csp_tier != custom_tier (when custom_tier is populated), surface a visible
-- divergence flag — do not silently override the CSP score.
```

**Do:**
- Always show the CSP's native score and tier alongside any custom signals.
- Surface a divergence flag when custom sub-indicators disagree with the CSP tier.
- Let the CS team observe signal divergence over at least one renewal cycle before promoting a custom composite.

**Don't:**
- Silently recompute the health score in the BI tool using raw source signals, bypassing the CSP score.
- Name the custom composite the same as the CSP score label.
- Replace the CSP score in phase 1 even if the team believes custom signals are more predictive.

## Edge cases / when the rule does NOT apply

If the CSP does not provide a health score (some platforms don't), or the team explicitly does not trust it, this rule does not apply — design the custom rule tier from scratch. If the CSP's score has a documented, known bias (e.g., over-weighting logins and ignoring support signals), that is evidence for phase-2 divergence work, not a license to replace it in phase 1.

## See also

- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the data model with the CSP-anchor column.
- [`./transparent-rule-based-tiering-before-ml-in-phase-one.md`](./transparent-rule-based-tiering-before-ml-in-phase-one.md) — the companion rule on keeping the tier expression readable.

## Provenance

Codifies the plugin's §4 house opinion #2 ("Anchor on the CSP's native score; add signals additively, don't silently recompute"). The silent-recompute anti-pattern is the most common first-build error; the CSP-anchor discipline prevents the two-score conflict that destroys leader trust.

---

_Last reviewed: 2026-06-05 by `claude`_
