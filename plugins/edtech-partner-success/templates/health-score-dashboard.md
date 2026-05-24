# Health-Score Dashboard — Spec

**Owner:** `<analytics-analyst + PSM team>`
**Refresh cadence:** `<daily / hourly>`
**Last refresh:** `<auto-stamp>`

---

## Composite score

For each partner:

- **Score** (0–100)
- **Color band:** Green (70–100) / Yellow (50–69) / Red (<50). _(Thresholds adjustable; document any change here.)_
- **Week-over-week delta:** ±N points
- **12-week sparkline** for trajectory context

---

## Component drill-down (click composite → see this)

| Component | Current | Weight | Half-life | Driver of last move |
|---|---|---|---|---|
| Adoption depth | `<value>` | `25%` | `90 days` | `<which signal moved>` |
| Touchpoint recency | `<value>` | `20%` | `14 days` | `<>` |
| Business outcome | `<value>` | `20%` | `90 days` | `<>` |
| Sentiment | `<value>` | `15%` | `60 days` | `<>` |
| Champion strength | `<value>` | `10%` | `60 days` | `<>` |
| Usage breadth | `<value>` | `10%` | `30 days` | `<>` |

> Weights are starting defaults; adjust per [`../skills/partner-health-scoring/SKILL.md`](../skills/partner-health-scoring/SKILL.md) Step 3.

---

## Red-flag triggers (independent of composite score)

These fire a recovery play immediately regardless of color band:

- [ ] Active-user count drop >30% week-over-week
- [ ] Champion departure (named champion no longer in role)
- [ ] 21+ days of zero meaningful touchpoints during active season
- [ ] Renewal date within 90 days AND decision-maker not yet confirmed alive in role
- [ ] 2+ consecutive support escalations to leadership tier
- [ ] Partner explicitly states "we're evaluating alternatives"

Each trigger displays in plain language with a date/recommendation.

---

## Per-partner row layout

```
| Partner Name | Score | Δ | Color | Triggers active | Recommended play | Last touchpoint | Next QBR | PSM |
|---|---|---|---|---|---|---|---|---|
```

Row click → drill into component-level + 12-week history + recommended play details.

---

## Cohort comparison (when cohort size ≥10)

For each partner, show:
- The partner's score
- The cohort median
- The cohort 25th–75th percentile band
- Visual indicator: where this partner sits relative to peers

Cohorts: segment × tier × time-since-onboarding bucket.

---

## Outages / data-quality flags

Surfaced at the top of the dashboard:

- Any sync that hasn't run successfully in 48+ hours
- Any vendor status-page incident for connected systems
- Any composite-score recompute that fell back to stale data

A partner showing "red" while their rostering data is stale is **not** a red partner; it's a data-quality flag. The dashboard must surface this rather than letting the PSM misread it.

---

## Refresh / governance

- Score components reviewed quarterly per [`../skills/partner-health-scoring/SKILL.md`](../skills/partner-health-scoring/SKILL.md) Step 8.
- For each renewed partner: did the score correctly predict the renewal?
- For each churned partner: did the score show red in time?
- Any signals that correlate but don't predict → dropped.
- Any new patterns → new signals proposed; weights reviewed.
