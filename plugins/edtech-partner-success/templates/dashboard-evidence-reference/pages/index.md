# Evidence Home Dashboard — `pages/index.md`

> The 5-second-test page. PSM opens the console and must answer "what needs my attention right now?" in 5 s without scrolling, filtering, or hovering. UX research §3 / §11 principle 1.

## File: `pages/index.md`

````markdown
---
title: Partner Success — Command Center
sources:
  - portfolio_summary: ./sources/snowflake/portfolio_summary.sql
  - portfolio_health_snapshot: ./sources/snowflake/portfolio_health_snapshot.sql
  - daily_action_center: ./sources/snowflake/daily_action_center.sql
  - portfolio_trend: ./sources/snowflake/portfolio_trend.sql
---

<FreshnessChip
    last_updated_at={portfolio_summary[0].refreshed_at_utc}
    viewer_tz="America/Los_Angeles"
    refresh_url="/api/refresh"
/>

# Partner Success — Command Center

<Alert type="info" hidden={portfolio_summary[0].partners_needing_attention > 0}>
  All partners healthy as of {new Date(portfolio_summary[0].refreshed_at_utc).toLocaleString()} —
  last checked {portfolio_summary[0].minutes_since_refresh} minutes ago.
</Alert>

<!-- THE COMMAND LINE OF ATTENTION (resolves in 1-2 fixations, ~400-600ms) -->
<!-- UX research §3: the "what needs my attention?" answer is here. -->

<BigValue
    data={portfolio_summary}
    value=partners_needing_attention
    title="Partners needing attention today"
    fmt="num0"
    sparkline=portfolio_trend
    sparklineYAxis=true
    comparison=delta_vs_yesterday
    comparisonTitle="vs yesterday"
/>

## Portfolio Summary

<Grid cols=4>

<BigValue
    data={portfolio_summary} value=total_partners
    title="Total partners" fmt="num0"
/>

<BigValue
    data={portfolio_summary} value=active_partners
    title="Active partners" fmt="num0"
    comparison=active_pct comparisonFmt="pct1" comparisonTitle="of total"
/>

<BigValue
    data={portfolio_summary} value=renewal_window_count
    title="In renewal window (≤180d)" fmt="num0"
/>

<BigValue
    data={portfolio_summary} value=at_risk_count
    title="At risk (red)" fmt="num0"
/>

<BigValue
    data={portfolio_summary} value=open_escalations_count
    title="Open escalations" fmt="num0"
/>

<BigValue
    data={portfolio_summary} value=outreach_needed_count
    title="Need outreach this week" fmt="num0"
/>

<BigValue
    data={portfolio_summary} value=top15_count
    title="Top 15 partners" fmt="num0"
/>

</Grid>

## Portfolio Health Snapshot

<Grid cols=5>

<BigValue
    data={portfolio_health_snapshot} value=avg_health_score
    title="Avg health" fmt="num0"
    comparison=avg_health_delta_30d comparisonTitle="30d Δ"
/>

<BigValue
    data={portfolio_health_snapshot} value=avg_sentiment_score
    title="Avg sentiment" fmt="num0"
    comparison=avg_sentiment_delta_30d comparisonTitle="30d Δ"
/>

<BigValue
    data={portfolio_health_snapshot} value=avg_engagement_score
    title="Avg engagement" fmt="num0"
    comparison=avg_engagement_delta_30d comparisonTitle="30d Δ"
/>

<BigValue
    data={portfolio_health_snapshot} value=declining_usage_count
    title="Declining usage" fmt="num0"
/>

<BigValue
    data={portfolio_health_snapshot} value=no_touchpoint_90d_count
    title="No touch in 90+ days" fmt="num0"
/>

</Grid>

## Daily Action Center — top 10 today

<!-- Sorted server-side by priority_score DESC. -->
<!-- Click-row navigates to /partner/<id> — drill is route nav because Partner 360 is bookmarkable. -->
<!-- UX research §5: route navigation when URL matters; bookmarkable. -->

<DataTable
    data={daily_action_center}
    rows=10
    link=partner_url
    rowShading=true
>
    <Column id=partner_name title="Partner" />
    <Column id=priority_score title="Priority" align=right fmt="num0" />
    <Column id=reason title="Why" />
    <Column id=recommended_action title="Action" />
    <Column id=due_date title="Due" fmt="MMM D" />
    <Column id=status_badge title="" contentType=html />
</DataTable>

<EmptyState
    show={daily_action_center.length === 0}
    headline="Nothing needs your attention today."
    body="Last checked {portfolio_summary[0].minutes_since_refresh} minutes ago — refresh to re-evaluate."
    cta_label="Refresh now"
    cta_href="/?refresh=1"
/>

[See all {portfolio_summary[0].outreach_needed_count} actions →](/action-center)

## Portfolio score — last 12 weeks

<LineChart
    data={portfolio_trend}
    x=week_ending
    y=avg_health_score
    yAxisTitle="Avg health"
    yMin=0
    yMax=100
/>

````

## Source query: `sources/snowflake/portfolio_summary.sql`

```sql
-- Snowflake-flavored. Replace placeholder schema names before deploy.
-- Cite: spec § Home Dashboard / Portfolio Summary

WITH refreshed_at AS (
    SELECT CURRENT_TIMESTAMP() AS refreshed_at_utc
),
base AS (
    SELECT
        p.partner_id,
        p.partner_name,
        p.segment,
        p.psm_owner,
        p.is_top15,
        h.health_score,
        h.health_band,           -- 'green' | 'yellow' | 'red'
        c.renewal_date,
        e.open_escalations,
        DATEDIFF('day', t.last_touchpoint_at, CURRENT_DATE()) AS days_since_touch
    FROM core.partner            p
    LEFT JOIN core.partner_health h ON h.partner_id = p.partner_id
    LEFT JOIN core.contract       c ON c.partner_id = p.partner_id AND c.is_current
    LEFT JOIN core.escalation_agg e ON e.partner_id = p.partner_id
    LEFT JOIN core.touchpoint_agg t ON t.partner_id = p.partner_id
    WHERE p.is_active
)
SELECT
    (SELECT refreshed_at_utc FROM refreshed_at)                                AS refreshed_at_utc,
    DATEDIFF('minute',
             (SELECT refreshed_at_utc FROM refreshed_at),
             CURRENT_TIMESTAMP())                                              AS minutes_since_refresh,
    COUNT(*)                                                                   AS total_partners,
    COUNT_IF(health_score IS NOT NULL)                                         AS active_partners,
    COUNT_IF(health_score IS NOT NULL) / NULLIF(COUNT(*), 0)::FLOAT            AS active_pct,
    COUNT_IF(is_top15)                                                         AS top15_count,
    COUNT_IF(renewal_date <= DATEADD('day', 180, CURRENT_DATE()))              AS renewal_window_count,
    COUNT_IF(health_band = 'red')                                              AS at_risk_count,
    COUNT_IF(open_escalations > 0)                                             AS open_escalations_count,
    COUNT_IF(days_since_touch >= 7)                                            AS outreach_needed_count,
    COUNT_IF(health_band IN ('red', 'yellow') OR open_escalations > 0)         AS partners_needing_attention,
    -- delta vs yesterday's snapshot (assumes a daily_snapshot table)
    COUNT_IF(health_band IN ('red', 'yellow') OR open_escalations > 0)
        - COALESCE((
            SELECT partners_needing_attention
            FROM core.daily_portfolio_snapshot
            WHERE snapshot_date = DATEADD('day', -1, CURRENT_DATE())
        ), 0)                                                                  AS delta_vs_yesterday
FROM base;
```

## Source query: `sources/snowflake/daily_action_center.sql`

```sql
-- Snowflake-flavored. Implements the spec's "Dashboard Priority Ranking Logic" section.
-- Cite: spec § Daily Action Center + § Dashboard Priority Ranking Logic.
-- Sort: priority_score DESC, then renewal proximity, then health decline.

WITH reasons AS (
    SELECT
        p.partner_id,
        p.partner_name,
        p.segment,
        h.health_score,
        h.health_band,
        h.health_score - LAG(h.health_score, 7) OVER (
            PARTITION BY p.partner_id ORDER BY h.scored_on
        )                                                          AS health_delta_7d,
        s.sentiment_score,
        s.sentiment_band,
        s.sentiment_score - LAG(s.sentiment_score, 7) OVER (
            PARTITION BY p.partner_id ORDER BY s.scored_on
        )                                                          AS sentiment_delta_7d,
        DATEDIFF('day', t.last_touchpoint_at, CURRENT_DATE())      AS days_since_touch,
        DATEDIFF('day', CURRENT_DATE(), c.renewal_date)            AS days_to_renewal,
        e.open_escalations,
        u.usage_decline_7d_pct,
        sp.success_plan_overdue_count,
        c.arr,
        p.is_top15
    FROM core.partner                p
    LEFT JOIN core.partner_health    h  ON h.partner_id = p.partner_id AND h.is_current
    LEFT JOIN core.partner_sentiment s  ON s.partner_id = p.partner_id AND s.is_current
    LEFT JOIN core.touchpoint_agg    t  ON t.partner_id = p.partner_id
    LEFT JOIN core.contract          c  ON c.partner_id = p.partner_id AND c.is_current
    LEFT JOIN core.escalation_agg    e  ON e.partner_id = p.partner_id
    LEFT JOIN core.usage_agg         u  ON u.partner_id = p.partner_id
    LEFT JOIN core.success_plan_agg  sp ON sp.partner_id = p.partner_id
    WHERE p.is_active
    QUALIFY ROW_NUMBER() OVER (PARTITION BY p.partner_id ORDER BY h.scored_on DESC) = 1
),
scored AS (
    SELECT
        partner_id,
        partner_name,
        segment,
        health_score,
        health_band,
        -- Priority score: weighted blend per spec § Dashboard Priority Ranking Logic
        (
            IFF(days_to_renewal BETWEEN 0 AND 30,  40,
            IFF(days_to_renewal BETWEEN 31 AND 90, 25,
            IFF(days_to_renewal BETWEEN 91 AND 180,15, 0)))                +  -- renewal timing
            IFF(health_delta_7d <= -5,             20, 0)                  +  -- health decline
            IFF(sentiment_delta_7d <= -10,         15, 0)                  +  -- sentiment decline
            IFF(days_since_touch >= 14,            15, 0)                  +  -- no recent touchpoint
            IFF(open_escalations > 0,              20, 0)                  +  -- open escalations
            IFF(usage_decline_7d_pct >= 25,        15, 0)                  +  -- usage decline
            IFF(success_plan_overdue_count > 0,    10, 0)                  +  -- success plan overdue
            IFF(arr >= 100000,                     10, 0)                  +  -- ARR weighting
            IFF(is_top15,                          15, 0)                     -- Top 15
        )                                                                  AS priority_score,
        -- The one Reason string: pick the *highest-leverage* signal, not all of them.
        -- UX research §11 principle 4: cite the signal; don't dump everything.
        CASE
            WHEN open_escalations > 0           THEN 'Open escalation'
            WHEN days_to_renewal BETWEEN 0 AND 30 THEN 'Renewal in ' || days_to_renewal || 'd'
            WHEN health_delta_7d <= -5          THEN 'Health -' || ABS(health_delta_7d) || ' in 7d'
            WHEN usage_decline_7d_pct >= 25     THEN 'Usage down ' || usage_decline_7d_pct || '% wow'
            WHEN sentiment_delta_7d <= -10      THEN 'Sentiment dropped'
            WHEN days_since_touch >= 14         THEN 'No touch in ' || days_since_touch || 'd'
            WHEN success_plan_overdue_count > 0 THEN success_plan_overdue_count || ' success plan goals overdue'
            ELSE 'Routine check-in'
        END                                                                AS reason,
        -- Recommended action: maps reason → next-easiest motion. Source: spec § Daily Action Center.
        CASE
            WHEN open_escalations > 0           THEN 'Review escalation, confirm owner'
            WHEN days_to_renewal BETWEEN 0 AND 30 THEN 'Confirm decision-maker + send renewal pack'
            WHEN health_delta_7d <= -5          THEN 'Diagnostic call this week'
            WHEN usage_decline_7d_pct >= 25     THEN 'Pull rostering + login report'
            WHEN sentiment_delta_7d <= -10      THEN 'Sentiment check call'
            WHEN days_since_touch >= 14         THEN 'Send 15-min check-in invite'
            WHEN success_plan_overdue_count > 0 THEN 'Re-baseline success-plan dates'
            ELSE 'Standard pulse'
        END                                                                AS recommended_action,
        -- Due date: 2 business days for red signals, end-of-week for yellow.
        CASE
            WHEN open_escalations > 0
              OR days_to_renewal BETWEEN 0 AND 30
              OR health_delta_7d <= -10               THEN DATEADD('day', 2, CURRENT_DATE())
            ELSE                                          DATE_TRUNC('week', CURRENT_DATE()) + 4
        END                                                                AS due_date,
        -- Inline status badge HTML (Evidence renders contentType=html for the column)
        '<span class="status-badge status-' || health_band || '">' ||
            UPPER(health_band) || '</span>'                                AS status_badge,
        '/partner/' || partner_id                                          AS partner_url
    FROM reasons
)
SELECT *
FROM scored
WHERE priority_score > 0
ORDER BY priority_score DESC, due_date ASC
LIMIT 50;
```

## Source query: `sources/snowflake/portfolio_health_snapshot.sql`

```sql
-- Cite: spec § Home Dashboard / Portfolio Health Snapshot
SELECT
    AVG(h.health_score)::INTEGER                                AS avg_health_score,
    AVG(s.sentiment_score)::INTEGER                             AS avg_sentiment_score,
    AVG(e.engagement_score)::INTEGER                            AS avg_engagement_score,
    AVG(h.health_score)::INTEGER -
        COALESCE((
            SELECT AVG(health_score)::INTEGER
            FROM core.partner_health
            WHERE scored_on = DATEADD('day', -30, CURRENT_DATE())
        ), 0)                                                   AS avg_health_delta_30d,
    AVG(s.sentiment_score)::INTEGER -
        COALESCE((
            SELECT AVG(sentiment_score)::INTEGER
            FROM core.partner_sentiment
            WHERE scored_on = DATEADD('day', -30, CURRENT_DATE())
        ), 0)                                                   AS avg_sentiment_delta_30d,
    AVG(e.engagement_score)::INTEGER -
        COALESCE((
            SELECT AVG(engagement_score)::INTEGER
            FROM core.partner_engagement
            WHERE scored_on = DATEADD('day', -30, CURRENT_DATE())
        ), 0)                                                   AS avg_engagement_delta_30d,
    COUNT_IF(u.usage_trend_30d = 'declining')                   AS declining_usage_count,
    COUNT_IF(t.days_since_touch >= 90)                          AS no_touchpoint_90d_count
FROM core.partner                 p
LEFT JOIN core.partner_health     h ON h.partner_id = p.partner_id AND h.is_current
LEFT JOIN core.partner_sentiment  s ON s.partner_id = p.partner_id AND s.is_current
LEFT JOIN core.partner_engagement e ON e.partner_id = p.partner_id AND e.is_current
LEFT JOIN core.usage_agg          u ON u.partner_id = p.partner_id
LEFT JOIN core.touchpoint_agg     t ON t.partner_id = p.partner_id
WHERE p.is_active;
```

## Design choices + citations

| Decision | Source |
|---|---|
| `BigValue` for the "partners needing attention" command line at the very top | UX research §11 principle 1: 5-second rule. NN/g preattentive attributes — position + size carry the first signal. |
| One-sentence `reason` instead of dumping all signals | UX research §11 principle 4: cite the signal. EdTech plugin §3 #4: "Every status carries the 2-3 signals that drove it" — but the *table* shows one; the drill-down shows all. |
| `EmptyState` celebratory when nothing needs attention | UX research §6: "all-clear empty state is celebratory, not blank." |
| `DataTable link=partner_url` → route navigation to `/partner/<id>` | UX research §5: route nav when URL matters / bookmarkable. |
| `FreshnessChip` at the top of every page | UX research §11 principle 7: always show freshness; Live/Stale/Paused. |
| Snowflake `QUALIFY ROW_NUMBER()` to pick the most recent health row | Snowflake-native idiom; cleaner than self-join. |
| Priority weights match the spec's Ranking Logic section verbatim | Spec § Dashboard Priority Ranking Logic. |
