# Surface the client's own usage, not just business outcomes

**Status:** Pattern — strong default for a productized (Case C) engagement; optional for a
single-engagement client deliverable (Case B) where usage-based billing isn't in play.

**Domain:** Dashboard cost visibility / client-facing usage

**Applies to:** `data-platform`

---

## Why this exists

This plugin's cost knowledge is entirely **consultant-facing** — three Snowflake sizing/cost
files, a FinOps decision tree, a cost-blowout scenario (see
[`knowledge/dashboard-query-cost-instrumentation.md`](../knowledge/dashboard-query-cost-instrumentation.md)
for the attribution method this rule complements). None of it answers a different, equally real
question: **what does a viewer inside a plan-tier see about their own usage?** A productized
dashboard (Case C) with usage-based or plan-tiered pricing that never shows the viewer how close
they are to a limit creates two bad outcomes — the viewer is surprised by an overage bill with no
warning, or the viewer under-uses a plan tier they'd have happily upgraded had they known they
were close to a limit. Both are avoidable with one query-cost-cheap widget: a progress-bar KPI
joining the tenant's actual usage against their plan-tier limit.

## How to apply

- **Model a `usage` cube joined against a `plan_tier_limits` table**, not a hard-coded number.
  Plan-tier limits change (a client upgrades, a promo changes a default), so the limit itself must
  be a queryable value, not a constant baked into the dashboard.

  ```yaml
  # cube-schema-starter.yml pattern — a usage cube reading the SAME tenant-scoped
  # access_policy every other cube in this schema already carries (never a
  # separate, unscoped usage-reporting path).
  cubes:
    - name: usage
      sql_table: fct_api_calls # or whatever unit the plan tier actually meters
      access_policy:
        - role: viewer
          row_level:
            filters:
              - member: tenant_id
                operator: equals
                values: [SECURITY_CONTEXT.tenant_id]

      joins:
        - name: plan_tier_limits
          sql: "{CUBE}.tenant_id = {plan_tier_limits}.tenant_id"
          relationship: many_to_one

      measures:
        - name: calls_this_period
          sql: id
          type: count

  # A separate cube (or a dimension pulled from the join) exposes the
  # tenant's actual limit — NEVER a client-side constant. A limit rendered
  # from a hard-coded prop drifts the moment a plan changes underneath it.
  ```

- **Render the ratio, not just the raw count.** `usage / limit` as a progress bar communicates
  "how close am I" at a glance; a bare count ("1,847 API calls") makes the viewer do the division
  themselves against a limit they may not remember. This plugin's local Tremor-Raw `ui/` primitives
  (`templates/cube-*-dashboard-starter/{,src/}components/ui/`) don't yet ship a progress-bar
  component — build one the same way `BadgeDelta.tsx` was built (a small, local, accessible
  component, not a new dependency), following the same status-only-color + accessible-text pattern
  the accessibility floor requires:

  ```tsx
  // A minimal shape — not a shipped component in this phase (see this plugin's
  // CHANGELOG for P2-17's actual Files-touched scope); the pattern to follow
  // when an engagement needs it.
  function UsageProgressKpi({ used, limit, label }: { used: number; limit: number; label: string }) {
    const pct = Math.min(100, Math.round((used / limit) * 100));
    const nearLimit = pct >= 80; // status threshold, not a magic color
    return (
      <div role="status" aria-label={`${label}: ${used} of ${limit} used, ${pct}%`}>
        <Text>{label}</Text>
        <div className="h-2 rounded bg-tremor-background-subtle">
          <div
            className={nearLimit ? "h-2 rounded bg-rose-500" : "h-2 rounded bg-tremor-brand"}
            style={{ width: `${pct}%` }}
          />
        </div>
        {/* Icon + text, never color alone, per the accessibility floor's Use-of-Color criterion. */}
        {nearLimit && <Text color="rose"><span aria-hidden="true">⚠ </span>Approaching your plan limit</Text>}
      </div>
    );
  }
  ```

- **Tag this widget's query too** — `getCubeClient("usage-kpi.calls_this_period")`, per
  [`dashboard-query-cost-instrumentation.md`](../knowledge/dashboard-query-cost-instrumentation.md)'s
  tagging scheme. A usage widget is itself a query that costs something; the irony of an
  unattributed cost-visibility widget is worth avoiding.
- **This is a client-facing concern, distinct from the consultant-facing attribution method** in
  the sibling knowledge file — a viewer never needs to know Cube's internal cache-hit rate or a
  Snowflake credit-per-query figure; they need to know their own usage against their own limit.
  Don't conflate the two audiences in one widget.

## What "good" looks like

- The usage ratio is computed from a live `usage`/`plan_tier_limits` join, never a client-side
  constant.
- The widget renders an icon-and-text near-limit state, not color alone (WCAG 2.2 AA, per
  [`dashboard-meet-the-accessibility-floor.md`](./dashboard-meet-the-accessibility-floor.md)).
- The widget's own query carries a request tag, same as every other widget on the page.

## Related

- [`knowledge/dashboard-query-cost-instrumentation.md`](../knowledge/dashboard-query-cost-instrumentation.md) —
  the consultant-facing attribution method this rule's client-facing counterpart complements.
- [`dashboard-meet-the-accessibility-floor.md`](./dashboard-meet-the-accessibility-floor.md) —
  the status-only-color rule this widget's near-limit state must follow.
- [`dashboard-set-data-freshness-slas.md`](./dashboard-set-data-freshness-slas.md) — the sibling
  "show the viewer something true about the system, not just an outcome number" discipline.
