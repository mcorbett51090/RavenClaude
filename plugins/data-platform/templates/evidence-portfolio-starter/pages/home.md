# Case Studies Portfolio

A demo/synthetic data-platform Case A (portfolio) starter — every number on this page comes
from the committed `sources/portfolio_demo/portfolio_demo.duckdb` fixture, never a live
client's data. Swap the fixture for a real engagement's data before publishing.

**As of:** this page's data is generated once, at fixture-build time (2026-09-03) — this
starter has no live-refreshing source, so "as of" here names the fixture's own build date, not
today's date. A real engagement replacing this with a live warehouse connection should surface
a genuine query-time "as of" per data-platform CLAUDE.md §3 #7 (provenance on every claim).

```sql summary
select
  count(*) as project_count,
  avg((metric_before - metric_after) / metric_before) as avg_pct_change
from portfolio_demo.case_studies
```

<div class="grid grid-cols-2 gap-4">

{% big_value
    data="summary"
    value="project_count"
    title="Case studies"
/%}

{% big_value
    data="summary"
    value="avg_pct_change"
    title="Avg. improvement"
    fmt="pct1"
/%}

</div>

## Traffic trend

```sql pageviews
select month, pageviews
from portfolio_demo.monthly_pageviews
order by month
```

{% line_chart
    data="pageviews"
    x="month"
    y="pageviews"
    title="Monthly pageviews"
/%}

*Source: `portfolio_demo.monthly_pageviews` — synthetic demo traffic, 2026-01 through
2026-08. Comparison baseline: this is the full series shown, not a period-over-period delta —
see the case-studies page for the before/after comparison pattern this rule expects on a
per-metric claim.*

See [Case Studies](./case-studies.md) for the full before/after detail per project.
