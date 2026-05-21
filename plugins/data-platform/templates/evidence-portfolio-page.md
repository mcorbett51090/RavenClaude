---
title: {{Case Study Title}}
description: {{One-sentence summary of the engagement and outcome}}
---

# {{Case Study Title}}

> Evidence.dev portfolio page template for `ravenpower.net` marketing-site case studies.
> Build-as-code (Markdown + SQL fenced blocks), static-deployable to Vercel/Netlify.
>
> **Last reviewed:** 2026-05-21
> **Engagement type:** {{Case B per-client deliverable / Case C productized SaaS}}
> **Industry:** {{EdTech / Finance / Regulatory / Manufacturing / etc.}}
> **Engagement length:** {{X weeks}}

---

## Problem

{{2-3 sentences. The partner's stated problem in their own words. Quote them verbatim if you can.}}

> "{{Direct quote from the partner / champion, attributed and dated.}}"
> — {{Name}}, {{Role}}, {{Client Org}}

## What we built

{{2-3 sentences. The deliverable in plain language. No vendor jargon unless the partner uses it.}}

- **Data layer:** {{Database choice + ELT tool + key sources}}
- **Modeling layer:** {{dbt project + key marts}}
- **Dashboard layer:** {{Framework + key views the partner uses weekly}}
- **Embed pattern:** {{How it's surfaced to the partner's end users}}

## The data flow

```sql
-- Example: top-line revenue trend over the engagement period
-- This SQL is executed at build time by Evidence
WITH monthly_revenue AS (
  SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount) AS revenue
  FROM fact_orders
  GROUP BY 1
)
SELECT * FROM monthly_revenue ORDER BY month
```

<LineChart
  data={monthly_revenue}
  x=month
  y=revenue
  yAxisTitle="Revenue ($)"
  xAxisTitle="Month"
/>

## Outcome metrics

{{What changed. Be specific. Numbers with comparison baselines.}}

- {{Metric 1: Before X → After Y over Z timeframe}}
- {{Metric 2: ...}}
- {{Metric 3: ...}}

```sql
-- Outcome metric — adoption depth before and after
SELECT
  CASE WHEN order_date < '{{engagement_start_date}}' THEN 'Before' ELSE 'After' END AS period,
  COUNT(DISTINCT customer_id) AS active_customers,
  SUM(amount) AS total_revenue
FROM fact_orders
GROUP BY 1
```

<BarChart
  data={adoption_comparison}
  x=period
  y=active_customers
  title="Active customers — before vs after the engagement"
/>

## What the partner said

> "{{Second direct quote — what changed for them, in their words.}}"
> — {{Name}}, {{Role}}, {{Client Org}}

## What was tricky (the honest section)

{{1-2 sentences. The non-obvious challenge. Pricing surprise, rate-limit gotcha, schema mismatch, integration gap. Demonstrates craft. Not a sales pitch.}}

## Tools

| Layer | Tool |
|---|---|
| Database | {{Supabase Pro / Neon Scale / Fabric F2}} |
| ELT | {{Airbyte Cloud Standard / Fivetran free / custom Airbyte}} |
| Modeling | dbt Core |
| Dashboard | {{Evidence / Superset / Metabase / Cube + React / Power BI Embedded}} |
| Embed | {{JWT + iframe / web component / SDK}} |
| Multi-tenancy | {{Postgres RLS / Cube securityContext / DAX role / single-tenant}} |

## Engagement timeline

- **Week 1:** Discovery — stack-decision-record signed off
- **Week 2:** Infrastructure — DB + ELT live, dbt project initialized
- **Weeks 3-5:** Dashboard build
- **Week 6:** Validation + UAT
- **Week 7:** Handoff

## What's next

{{1 sentence. Either "ongoing engagement" or "client now self-services" or "expansion under discussion."}}

---

## Notes on this template

- **Evidence's native format is markdown-with-SQL** — the SQL fenced blocks run at build time against the configured data source. See [evidence.dev/docs](https://evidence.dev/docs/) for chart components.
- **Refresh cadence:** monthly build (data) + quarterly content refresh
- **Hosting:** Vercel or Netlify static deploy; $0 hosting cost
- **Privacy:** if the case study quotes the partner or names them, get sign-off in writing before publishing. Use generic terms ("a $50M-revenue EdTech vendor", "a 12-state K-12 SaaS company") when the partner prefers anonymity.

## Acceptance criteria for publishing

- [ ] Two direct quotes from the partner, attributed and dated, sign-off in writing
- [ ] Outcome metrics with comparison baselines and date ranges
- [ ] No pricing claims for tools used (links to vendor pages instead — pricing ages)
- [ ] No claim about competitor tools (focus on what worked, not what didn't)
- [ ] Tools table accurate and current
- [ ] At least one "what was tricky" honesty paragraph
- [ ] No client PII visible (anonymize where required)

---

*Refresh triggers for this template:* Evidence ships a new chart component worth using; the case-study format itself improves based on what readers respond to; the partner asks for a change to their quote.
