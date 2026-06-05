# Attach source provenance to every dashboard widget that makes a claim

**Status:** Absolute rule
**Domain:** Dashboard / trust / data quality
**Applies to:** `data-platform`

---

## Why this exists

A widget that says "Revenue is up 18%" without a source query, date range, and comparison baseline is making an unfalsifiable claim. Stakeholders who cannot verify a number stop trusting all the numbers. Consultants who cannot reproduce a widget's value cannot defend an engagement audit. Provenance — where the number came from, over what period, compared to what — is the minimum contract a dashboard owes its reader. Omitting it is the same as presenting a financial statement without a footnote.

## How to apply

Every dashboard widget that expresses a comparison, trend, or KPI should expose provenance at three levels:

| Level | Minimum | Recommended |
|---|---|---|
| Visual | Subtitle or tooltip with date range | "Revenue MTD vs prior MTD — source: Stripe charges" |
| Interactive | Click/hover reveals source query and parameters | Cube Dev Tools URL or "View source" link |
| Documentation | `stack-decision-record.md` cross-reference to the mart + Cube measure that feeds this widget | `fct_payments.recognized_revenue` via `orders.total_revenue` measure |

```markdown
<!-- Evidence.dev widget example -->
<BigValue
  value={total_revenue}
  title="Revenue (MTD)"
  subtitle="Source: Stripe charges → fct_payments, orders.total_revenue measure. Range: {date_range}. Compared to: prior calendar month."
/>
```

**Do:**
- Embed date range and comparison baseline in every KPI subtitle or tooltip.
- Link each widget back to the named Cube measure or dbt mart model in the codebase.
- Update provenance when the underlying mart or measure is renamed/refactored.

**Don't:**
- Ship "Revenue: $1.2M" with no period, no source, and no comparison anchor.
- Use display-layer filters to silently narrow a date range without surfacing it in the subtitle.
- Let a widget's source drift from its documented provenance through mart refactors.

## Edge cases / when the rule does NOT apply

- Internal development dashboards used only during an engagement build (not delivered to a client) may omit the full provenance UI while queries are still being validated. Provenance must be added before the dashboard is presented or delivered.

## See also

- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — generates widget components and should embed provenance at generation time
- [`./dashboard-set-data-freshness-slas.md`](./dashboard-set-data-freshness-slas.md) — freshness SLA is a key provenance dimension

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #7: "Provenance on every claim. A dashboard widget that says 'Revenue is up 18%' needs the source query, date range, and comparison baseline accessible from the widget."

---

_Last reviewed: 2026-06-05 by `claude`_
