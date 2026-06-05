---
scenario_id: 2026-06-05-semantic-layer-metric-drift
contributed_at: 2026-06-05
plugin: analytics-engineering
product: dbt-cloud
product_version: "MetricFlow / dbt Semantic Layer"
scope: likely-general
tags: [semantic-layer, metric-drift, revenue, single-definition, governance]
confidence: high
reviewed: false
---

## Problem

Three teams reported three different "active users" numbers for the same month — the exec dashboard said ~1.42M, the growth team's Looker explore said ~1.51M, and the finance reconciliation said ~1.38M. Each was internally defensible: the exec dashboard counted users with ≥1 session, growth counted users with ≥1 *qualifying* event (excluding bots and internal traffic), and finance counted users who were *billable* that month. Nobody was wrong; there were simply three definitions of "active user" wearing one name, computed in three places (a BI calculation, a hand-rolled mart column, and a finance spreadsheet). The CFO stopped trusting all three.

## Constraints context

- A dbt Semantic Layer / MetricFlow setup existed but was *half-adopted*: revenue was defined as a metric, "active user" was not — so the most politically-charged metric was the one still being re-derived per consumer.
- Each team's definition encoded a real business rule (bot exclusion, billable filter) that the others didn't know about — so "just pick one" would silently break a downstream report that depended on the excluded rule.
- The marts were correct at their grain; the drift was entirely in the *aggregation/filter layer*, which lived in three different tools.
- Changing the definition was a governance question (who owns "active user"?), not just a SQL question — the technical fix was the easy half.

## Attempts

- Tried: picking the exec dashboard's number as canonical and pointing everyone at it. It immediately broke finance's reconciliation (it included non-billable users) and growth's bot-exclusion, so two teams re-built their own version again within a week. A single definition imposed without absorbing the others' rules just restarts the drift.
- Tried: cataloguing the three definitions side by side and surfacing that they answered three *different questions* — "logged-in", "engaged", "billable". The disagreement was a naming collision, not a calculation bug. This reframing unblocked the governance call.
- Tried: defining **three explicitly-named metrics** in the semantic layer — `active_users_logged_in`, `active_users_engaged` (with the bot/internal filter as a metric-level filter), and `billable_users` (with the billing filter) — each with one owner, one definition, grain stated. Every BI tool now queries the metric by name; none re-derive it.
- Tried (enforcement): adding a check that flagged net-new aggregate columns named `*active_user*` or `*revenue*` in marts/BI as candidates that belong in the semantic layer, so a fourth hand-rolled definition can't quietly appear.

## Resolution

**One definition per metric — but first make sure you actually have one metric.** The sequence that held:

1. **Distinguish "drift" from "different questions."** Three numbers can all be right if they answer different questions. Catalogue the definitions before declaring a winner; the fix for genuinely-different questions is *more named metrics*, not one forced metric.
2. **Define each as metrics-as-code in the semantic layer** (MetricFlow `metrics:`), with the business rule encoded as a metric-level filter, an explicit grain, and a single named owner. The name *is* the contract.
3. **Forbid re-derivation downstream** — BI tools and marts reference the governed metric by name; a metric is never recomputed in a dashboard calc or a mart column. The moment two places compute the "same" metric, trust in both is gone.
4. **Gate against new shadow definitions** — flag net-new aggregate columns that look like a KPI so a fourth definition can't reappear outside the layer.

The trap is treating metric disagreement as a *bug to debug* when it's often a *governance gap to name*: the numbers differ because the definitions differ, and the cure is explicit, owned, named definitions — not a single number declared by whoever shouts loudest.

**Action for the next engineer:** when two dashboards disagree on a headline metric, don't diff the SQL first — diff the *definitions* (what's included, excluded, the grain, the filter). If they answer different questions, ship two named metrics; if they answer the same question, consolidate to one governed definition and delete the re-derivations.

Cross-reference: the field-note complement to [`../best-practices/one-definition-per-metric.md`](../best-practices/one-definition-per-metric.md) and [`../best-practices/metrics-as-code-not-as-dashboard-sql.md`](../best-practices/metrics-as-code-not-as-dashboard-sql.md). For where a metric belongs, see the "Where should this metric be defined?" tree in [`../knowledge/analytics-engineering-decision-trees.md`](../knowledge/analytics-engineering-decision-trees.md).
