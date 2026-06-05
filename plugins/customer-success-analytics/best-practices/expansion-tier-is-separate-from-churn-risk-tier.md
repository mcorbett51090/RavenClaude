# Keep the expansion-readiness tier separate from the churn-risk tier

**Status:** Absolute rule
**Domain:** CS analytics — tier design
**Applies to:** `customer-success-analytics`

---

## Why this exists

Churn risk and expansion readiness are opposite risk questions. A single composite "health score" that blends both produces a tier that can't answer either question clearly: a high-usage account that is renewal-imminent and falling looks "neutral" because its expansion signals cancel out the risk signals. The CS rep needs to know which accounts to call to save and which accounts to call to grow — two separate lists, not one ambiguous composite.

## How to apply

Design the health mart with two independent tier columns:

- `risk_tier` — Red / Yellow / Green, driven by churn-leading signals (usage decline, low NPS, support escalation, renewal proximity × engagement drop)
- `expansion_tier` — Expansion Ready / Watch / Neutral, driven by expansion-leading signals (usage momentum, champion depth, positive NPS, renewal runway)

Both columns are in `fct_account_health_snapshot` (or a companion `fct_account_expansion_signal` table). Render them as two separate columns or two separate dashboard views — never combined into a single score.

**Do:**
- Accept that an account can simultaneously be Red (churn risk) and Expansion Watch (potential grow motion) — that is accurate and actionable, not contradictory.
- Build the CS surface to answer "who do I call to save?" and "who do I call to grow?" as two distinct queries.

**Don't:**
- Add expansion signals to the churn-risk tier rule to "balance" the tier.
- Build a composite score that averages risk and opportunity together — the resulting number has no interpretable meaning.
- Let an Expansion-Ready designation slow down a save-play on a Red account — the risk tier always takes priority in scheduling.

## Edge cases / when the rule does NOT apply

- Phase 0 / MVP — if the team has capacity to build only one tier view initially, build the churn-risk tier first (per the phasing rule). The expansion tier is the second milestone, not the first. But even in the MVP design, reserve the column namespace so the mart can accommodate both when the second tier is added.

## See also

- [`../skills/account-expansion-signal-design/SKILL.md`](../skills/account-expansion-signal-design/SKILL.md) — designing the expansion signal set
- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — designs the two-tier mart model

## Provenance

Derived from the `CLAUDE.md` §4 house opinion #1 (transparent rule-based tiering, every Red shows why) applied to the expansion case. A composite that conflates risk and opportunity is an opaque tier wearing a single number.

---

_Last reviewed: 2026-06-05 by `claude`_
