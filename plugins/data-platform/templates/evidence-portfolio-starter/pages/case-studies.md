# Case Studies — Detail

Every row shows the metric's value **before** and **after** the engagement, plus the computed
percent change — the comparison baseline `best-practices/dashboard-provenance-on-every-widget.md`
requires on every claim. Synthetic demo data, `sources/portfolio_demo/portfolio_demo.duckdb`.

```sql case_studies
select
  client_name,
  industry,
  metric_name,
  metric_before,
  metric_after,
  metric_unit,
  round(100.0 * (metric_after - metric_before) / metric_before, 1) as pct_change,
  completed_date
from portfolio_demo.case_studies
order by completed_date desc
```

{% table
    data="case_studies"
    title="All case studies"
%}
    {% column id="client_name" title="Client" /%}
    {% column id="industry" title="Industry" /%}
    {% column id="metric_name" title="Metric" /%}
    {% column id="metric_before" title="Before" fmt="num1" /%}
    {% column id="metric_after" title="After" fmt="num1" /%}
    {% column id="pct_change" title="% change" fmt="pct1" /%}
    {% column id="completed_date" title="Completed" /%}
{% /table %}

## By industry

```sql by_industry
select
  industry,
  count(*) as project_count,
  round(avg(100.0 * (metric_after - metric_before) / metric_before), 1) as avg_pct_change
from portfolio_demo.case_studies
group by all
order by avg_pct_change desc
```

{% bar_chart
    data="by_industry"
    x="industry"
    y="avg_pct_change"
    title="Average % improvement by industry"
/%}

*Source: `portfolio_demo.case_studies`. Every figure on this page is queried live from the
table above — no hand-copied numbers — so the SQL block itself is the provenance trail for
every claim on the page, per this skill's rubric on citing evidence per finding.*
