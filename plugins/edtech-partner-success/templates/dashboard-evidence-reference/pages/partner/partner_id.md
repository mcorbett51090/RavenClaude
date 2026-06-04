# Evidence Partner 360 — `pages/partner/[partner_id].md`

> Drill-down page from the Home Dashboard or Daily Action Center. URL is bookmarkable / shareable in Slack. UX research §5 (route navigation pattern) + §8 (URL state).

## File: `pages/partner/[partner_id].md`

````markdown
---
title: "Partner 360 — {params.partner_id}"
sources:
  - partner_360: ./sources/snowflake/partner_360.sql
  - account_timeline: ./sources/snowflake/account_timeline.sql
  - contacts: ./sources/snowflake/partner_contacts.sql
  - lifecycle: ./sources/snowflake/lifecycle_stages.sql
  - usage: ./sources/snowflake/usage_adoption.sql
  - success_plan: ./sources/snowflake/success_plan_status.sql
  - contract: ./sources/snowflake/contract_detail.sql
  - score_components: ./sources/snowflake/health_score_components.sql
queries:
  - partner_id: ${params.partner_id}
---

<!-- Breadcrumbs first — UX research §5: every drill level needs back nav. -->
[← Command Center](/) · [Action Center](/action-center) · **{partner_360[0].partner_name}**

<FreshnessChip
    last_updated_at={partner_360[0].refreshed_at_utc}
    viewer_tz="America/Los_Angeles"
/>

# {partner_360[0].partner_name}

<Grid cols=4>
  <BigValue data={partner_360} value=health_score
            title="Health" fmt="num0"
            comparison=health_delta_30d comparisonTitle="30d Δ" />
  <BigValue data={partner_360} value=sentiment_score
            title="Sentiment" fmt="num0" />
  <BigValue data={partner_360} value=arr
            title="ARR" fmt="usd0" />
  <BigValue data={partner_360} value=days_to_renewal
            title="Days to renewal" fmt="num0" />
</Grid>

<!-- Open flags: render only when present (UX §6 empty-state discipline). -->
{#if partner_360[0].flags_json && JSON.parse(partner_360[0].flags_json).length > 0}
## Open flags

<DataTable data={JSON.parse(partner_360[0].flags_json)} rows=all>
    <Column id=flag title="Flag" />
    <Column id=raised_at title="Since" fmt="MMM D" />
    <Column id=severity title="" contentType=html />
</DataTable>
{/if}

## Account information

<DataTable data={partner_360} rows=1 hideColumns="partner_id,refreshed_at_utc,flags_json">
    <Column id=district_name      title="District" />
    <Column id=segment            title="Segment" />
    <Column id=state              title="State" />
    <Column id=psm_owner          title="PSM" />
    <Column id=sf_account_owner   title="SF Owner" />
    <Column id=contract_start     title="Contract start" fmt="MMM D, YYYY" />
    <Column id=contract_end       title="Contract end" fmt="MMM D, YYYY" />
    <Column id=renewal_date       title="Renewal" fmt="MMM D, YYYY" />
    <Column id=funding_source     title="Funding" />
</DataTable>

## Contacts

<DataTable data={contacts} rows=all sort="influence_level desc">
    <Column id=name              title="Name" />
    <Column id=role              title="Role" />
    <Column id=title             title="Title" />
    <Column id=influence_level   title="Influence" align=right />
    <Column id=sentiment_band    title="Sentiment" contentType=html />
    <Column id=last_interaction  title="Last interaction" fmt="MMM D" />
</DataTable>

<EmptyState
    show={contacts.length === 0}
    headline="No contacts linked to this partner yet."
    body="Add stakeholders to start tracking influence and sentiment."
    cta_label="Open in Salesforce"
    cta_href={partner_360[0].sf_url}
/>

## Lifecycle

<!-- Spec § Lifecycle Tracking: Deployment → BOI → MOI → Renewal -->
<BigValue
    data={lifecycle} value=current_stage title="Current stage"
/>
<BigValue
    data={lifecycle} value=days_in_stage title="Days in stage" fmt="num0"
/>
<BigValue
    data={lifecycle} value=next_milestone title="Next milestone"
/>

## Health score — components

<!-- Spec § Health Dashboard + spec § Daily Action Center "cite the signals". -->
<!-- UX research §11 principle 4: status carries the 2-3 signals that drove it. -->

<BarChart
    data={score_components}
    x=component
    y=score
    yMin=0
    yMax=100
    sort=weight
/>

<DataTable data={score_components} rows=all>
    <Column id=component        title="Signal" />
    <Column id=score            title="Score" align=right fmt="num0" />
    <Column id=weight           title="Weight" align=right fmt="pct0" />
    <Column id=delta_30d        title="30d Δ" align=right fmt="num0" />
    <Column id=half_life_days   title="Half-life (d)" align=right />
    <Column id=plain_english    title="What it means" />
</DataTable>

## Usage & adoption — last 90 days

<LineChart
    data={usage}
    x=measurement_date
    y={['active_users', 'active_teachers']}
    yAxisTitle="Active count"
/>

<BarChart
    data={usage}
    x=measurement_date
    y=messages_sent
    yAxisTitle="Messages sent"
/>

## Success plan

<DataTable data={success_plan} rows=all>
    <Column id=goal         title="Goal" />
    <Column id=owner        title="Owner" />
    <Column id=due_date     title="Due" fmt="MMM D" />
    <Column id=progress_pct title="Progress" align=right fmt="pct0" />
    <Column id=status_badge title="" contentType=html />
</DataTable>

<EmptyState
    show={success_plan.length === 0}
    headline="No success plan on file."
    body="Draft a 30/60/90 plan to start tracking measurable goals."
    cta_label="Create success plan"
    cta_href={"/success-plan/new?partner_id=" + params.partner_id}
/>

## Account timeline — last 180 days

<!-- Spec § Account Timeline: merged event stream across SF + Planhat + Support + Snowflake + Success Plans + Meetings. -->

<DataTable data={account_timeline} rows=25>
    <Column id=event_date    title="When" fmt="MMM D" />
    <Column id=source_system title="Source" />
    <Column id=event_type    title="Type" />
    <Column id=summary       title="Summary" />
</DataTable>

[Open full timeline →](/partner/{params.partner_id}/timeline)

## Contract

<DataTable data={contract} rows=1>
    <Column id=current_arr           title="ARR" fmt="usd0" />
    <Column id=multi_year            title="Multi-year" />
    <Column id=licensed_users        title="Licensed users" align=right fmt="num0" />
    <Column id=products_purchased    title="Products" />
    <Column id=pd_purchased_hours    title="PD purchased (hrs)" align=right />
    <Column id=pd_remaining_hours    title="PD remaining (hrs)" align=right />
</DataTable>

[Open contract documents →](/contracts?partner_id={params.partner_id})
````

## Source query: `sources/snowflake/partner_360.sql`

```sql
-- Snowflake-flavored. Bound parameter: ${partner_id}
-- Cite: spec § Partner 360 / Account Information
WITH refreshed AS (SELECT CURRENT_TIMESTAMP() AS refreshed_at_utc)
SELECT
    p.partner_id,
    p.partner_name,
    p.district_name,
    p.segment,
    p.state,
    p.psm_owner,
    p.sf_account_owner,
    p.sf_url,
    h.health_score,
    h.health_band,
    h.health_score - COALESCE((
        SELECT health_score FROM core.partner_health h2
        WHERE h2.partner_id = p.partner_id
          AND h2.scored_on = DATEADD('day', -30, CURRENT_DATE())
    ), h.health_score)                                                 AS health_delta_30d,
    s.sentiment_score,
    s.sentiment_band,
    c.arr,
    c.contract_start,
    c.contract_end,
    c.renewal_date,
    c.funding_source,
    DATEDIFF('day', CURRENT_DATE(), c.renewal_date)                    AS days_to_renewal,
    f.flags_json,
    (SELECT refreshed_at_utc FROM refreshed)                           AS refreshed_at_utc
FROM core.partner            p
LEFT JOIN core.partner_health h ON h.partner_id = p.partner_id AND h.is_current
LEFT JOIN core.partner_sentiment s ON s.partner_id = p.partner_id AND s.is_current
LEFT JOIN core.contract       c ON c.partner_id = p.partner_id AND c.is_current
LEFT JOIN core.partner_flags  f ON f.partner_id = p.partner_id
WHERE p.partner_id = ${partner_id};
```

## Source query: `sources/snowflake/health_score_components.sql`

```sql
-- Cite: spec § Health Dashboard; EdTech plugin §3 #4 "cite the signal";
--       data.json `components[]` (weight + half_life_days)

SELECT
    component_key                                                       AS component,
    score,
    weight_pct                                                          AS weight,
    score - COALESCE((
        SELECT score FROM core.health_score_components sc2
        WHERE sc2.partner_id = ${partner_id}
          AND sc2.component_key = sc.component_key
          AND sc2.scored_on = DATEADD('day', -30, CURRENT_DATE())
    ), score)                                                           AS delta_30d,
    half_life_days,
    plain_english
FROM core.health_score_components sc
WHERE sc.partner_id = ${partner_id}
  AND sc.is_current
ORDER BY weight_pct DESC;
```

## Source query: `sources/snowflake/account_timeline.sql`

```sql
-- Cite: spec § Account Timeline — merged event stream from 6 source systems.
-- Snowflake UNION ALL across canonicalized event views.

SELECT event_date, source_system, event_type, summary
FROM (
    SELECT event_date, 'salesforce'     AS source_system, event_type, summary
    FROM   stg.salesforce_events     WHERE partner_id = ${partner_id}
    UNION ALL
    SELECT event_date, 'planhat'        AS source_system, event_type, summary
    FROM   stg.planhat_events        WHERE partner_id = ${partner_id}
    UNION ALL
    SELECT event_date, 'support'        AS source_system, event_type, summary
    FROM   stg.support_events        WHERE partner_id = ${partner_id}
    UNION ALL
    SELECT event_date, 'snowflake_usage' AS source_system, event_type, summary
    FROM   stg.usage_events          WHERE partner_id = ${partner_id}
    UNION ALL
    SELECT event_date, 'success_plan'   AS source_system, event_type, summary
    FROM   stg.success_plan_events   WHERE partner_id = ${partner_id}
    UNION ALL
    SELECT event_date, 'calendar'       AS source_system, event_type, summary
    FROM   stg.calendar_events       WHERE partner_id = ${partner_id}
)
WHERE event_date >= DATEADD('day', -180, CURRENT_DATE())
ORDER BY event_date DESC;
```

## Design choices + citations

| Decision | Source |
|---|---|
| Route navigation (not modal / drawer) for Partner 360 | UX research §5: route nav when URL matters / bookmarkable / shareable. Spec implies Partner 360 is a "page" the PSM lives in. |
| Breadcrumbs at top + every empty state has a CTA | UX research §5: "drilling without a way back is a usability bug" + §6: diagnostic + CTA. |
| Health score components rendered as a `BarChart` + table | UX research §11 principle 4: every status carries 2-3 signals; EdTech plugin §3 #4. data.json `components[]` provides weight + half_life_days. |
| Sparkline-equivalent: line chart for usage trends, anchored on current value | UX research §10: Tufte sparkline rules — anchor with the current value as labeled endpoint. |
| Open flags rendered only when present (no "No flags" placeholder) | UX research §6: distinguish healthy-empty (don't show "No data") from filter-empty. |
| Account timeline UNION ALL across 6 staging views | Spec § Account Timeline lists 6 source systems verbatim. |
| `${partner_id}` parameter binding | Evidence's parameterized-pages mechanism (research §1.1). |
