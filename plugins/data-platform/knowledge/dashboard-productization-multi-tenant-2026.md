---
title: Productizing Internal Dashboards as Multi-Tenant — 2026 Field Guide
audience: data-platform-engineer, tech-lead, psm-tooling-lead
status: stable
last_reviewed: 2026-06-04
refresh_triggers:
  - "Snowflake pricing model change (Snowpipe, Adaptive Compute, Cortex)"
  - "DuckDB-WASM browser memory ceiling shifts"
  - "Embedded analytics vendor pricing change (Sigma / Looker / ThoughtSpot)"
  - "Cube or Lightdash dashboards-as-code surface change"
sources_verified_at: 2026-06-04
---

# Productizing Internal Dashboards as Multi-Tenant — 2026 Field Guide

> The "we have a great internal CS dashboard, let's ship it to customers" path. 2026 reality: the dominant pattern is **buy a flat-rate embedded analytics vendor + bring your own semantic layer**, not "build from scratch" or "expose the internal tool with a tenant filter." This file is the decision tree for the build-vs-buy + tenancy + cost-stacking calls.

---

## Why this file exists

Multiple PSM org write-ups in 2025-2026 describe the same trap: an internal Streamlit/Sigma/Looker dashboard works great for the CS team's 12 seats, gets opened up to 50 partner districts with "just add a tenant filter," and either (a) blows the FERPA isolation envelope because the filter sits in SQL the wrong place, or (b) blows the budget because the warehouse compute meter wasn't sized for partner-facing read volume. This file collects the supported 2026 patterns that avoid both.

The patterns below are **vendor-grounded** (cited inline) — not "the way it should work," but "what current docs + practitioner write-ups confirm works in 2026."

---

## Build vs buy — decision rule

| You should | When |
|---|---|
| **Build (headless Cube + React/Tremor + Snowflake)** | Semantic layer is durable IP. Brand control + UX is differentiating. Governance/regulatory is your team's domain expertise. You can sustain 2-3 FTEs on it long-term. |
| **Buy flat-rate embedded (Qrvey, Tinybird, Toucan)** | Predictable pricing matters more than full UX control. Multi-tenant + RLS is a checkbox, not a research project. Time-to-first-revenue < 6 months. Avg users-per-tenant > 10 (per-seat math kills you). |
| **Buy enterprise embed (ThoughtSpot Visual Embed, Looker, Sigma)** | Enterprise sales motion already exists. Customers expect a brand-name BI inside. Sales-cycle pricing is acceptable. Compute-cost stacking (license + warehouse) is budgeted explicitly. |
| **Don't productize at all — give them read-only SiS or a static Evidence site** | Audience is internal stakeholders + 3-5 named partner contacts. Per-partner customization isn't required. Snowflake-native auth is acceptable. |

**Common failure mode:** treating this as a binary build-or-buy. In 2026 the strong answer is usually "buy the embedding shell, build the semantic layer and the rendering specifics" — neither pure build nor pure buy.

---

## Tenancy patterns — cheapest → most isolated

| # | Pattern | Cost shape | Isolation | When |
|---|---|---|---|---|
| 1 | **Per-tenant Parquet + DuckDB-WASM** | One-time WASM bundle (~6MB cached). Object-store storage per tenant. Browser compute = free. | URL-signing layer enforces isolation. SQL never crosses tenant boundary. | Read-only. <10M rows/tenant. Acceptable for daily-refresh partner dashboards. |
| 2 | **Pooled DB + RLS on `CURRENT_USER`/JWT** | Lowest warehouse cost. Single set of objects. | RAP/RLS catches every query. Misconfigured RAP = silent leak (see §Owner's-rights trap). | Default for multi-tenant SaaS. <100 tenants. Warehouse compute caps via Cube pre-aggregations. |
| 3 | **Schema-per-tenant** | Per-tenant clustering keys. Larger metadata overhead. | Schema boundary + role grants. Easier to reason about than RLS. | Mid-market scale, 100-1000 tenants, compliance-flavored. |
| 4 | **DB-per-tenant** | 4-10× cost of pooled per-tenant baseline. | Hard isolation. Compliance-clean. | Enterprise-tier customers only. Sold as add-on, not default. |
| 5 | **Hypertenancy (MotherDuck Ducklings)** | $0.60/hr per Pulse instance. Scale-to-zero. | Per-user DuckDB compute. | Bursty per-user workloads. Newer pattern, watch maturity. |

One published 2026 case study (SaaS productivity, 10K small tenants): moving top-tier customers from pooled DB to schema-per-tenant produced **40% DB CPU reduction, 400ms→120ms API latency, 60% faster compliance reporting** — single source (UMA Tech), so treat as illustrative not consensus.

---

## Pricing model decision

| Model | Use when | Avoid when |
|---|---|---|
| **Flat per-tenant tier** ("$2K/mo Standard, $5K/mo Pro") | Avg users-per-tenant > 10. Scaling with tenant *value* not user count. SaaS norm in 2026. | Single-user-per-tenant prosumer. |
| **Per-seat** | Avg users-per-tenant < 5. Power-user-driven. | High-seat-count B2B — per-seat at $15/mo × 40 users = $600/tenant/mo before add-ons, kills expansion. |
| **Usage-based (queries/GB)** | Your own COGS is usage-linked (Snowflake pass-through). | Steady-state workloads — penalizes power users who provide your best testimonials. |

---

## Cost-stacking awareness (the meter you forgot)

Enterprise embedded analytics has **two compounding meters**:

1. **License meter** — Sigma per-viewer, Looker per-viewer ($400/yr documented), ThoughtSpot per-user ($25-$50/mo published, custom Enterprise).
2. **Warehouse compute meter** — Sigma/Looker queries hit Snowflake/BigQuery directly. Heavy analyst usage can push warehouse spend equal to or above the license meter (multiple 2026 practitioner write-ups confirm this — single citations not consensus).

**Levers:**
- **Cube pre-aggregations** — the canonical lever for capping warehouse compute on embedded analytics. Pre-compute the common slice; serve from cache.
- **Snowflake auto-suspend (60s)** — non-negotiable for partner-facing read load with idle gaps.
- **Snowpipe v2 flat pricing** (Dec 8 2025: 0.0037 credits/GB) — bake into the cost model, replaces per-core/per-file streaming cost.
- **Dynamic Tables `TARGET_LAG`** — each refresh is billable regardless of source change. Tight `TARGET_LAG` on slowly-changing data = silent burn.

[verify-at-use — 2026-06-04 — Snowpipe simplified pricing release notes; Looker viewer pricing third-party sourced]

---

## Owner's-rights trap (SiS-specific, partner-facing)

If using **Streamlit-in-Snowflake** for partner-facing multi-tenant, the default behavior is:

> "Streamlit in Snowflake apps run with owner's rights, so using CURRENT_ROLE … always returns the app owner role." [[Snowflake docs](https://docs.snowflake.com/en/developer-guide/streamlit/owners-rights)]

This means **row access policies keyed on `CURRENT_ROLE` silently return the owner's data, not the viewer's** — every viewer sees every tenant's rows. Classic FERPA-breach pattern.

**Two supported fixes:**
1. **RAP on `CURRENT_USER`** + grant the Streamlit app owner role the global `READ SESSION` privilege (ACCOUNTADMIN-only). The viewer's identity flows into the RAP.
2. **Container runtime + restricted caller's rights** (Preview as of mid-2026) — app runs with viewer privileges. RAP on `CURRENT_ROLE` then works.

**Don't ship partner-facing SiS without explicitly choosing one of these.** The dev-cluster default behavior is the unsafe path.

---

## Performance budgets (2026)

Vendor + practitioner consensus 2026 (cite [[InnoVision Core Web Vitals 2026]](https://innovisionbiz.com/core-web-vitals-guide/), [[Integrate.io real-time dashboard SLAs]](https://www.integrate.io/blog/build-slas-for-real-time-dashboards-with-ai-etl/)):

| Metric | Good | Alert at (80% threshold) |
|---|---|---|
| LCP (Largest Contentful Paint) | <2.5s | >2.0s |
| **INP (Interaction to Next Paint)** | <200ms | >160ms |
| CLS (Cumulative Layout Shift) | <0.1 | >0.08 |
| Dashboard query SLA | <5s end-to-end | 5s = abandonment trigger |
| Data freshness (real-time dash) | <60s | — |

**INP is the dominant 2026 failure mode in dense analytics UIs** — heavy SVG charts, large React trees, unmemoized formatters blow INP without affecting LCP. Budget INP per chart type; don't aggregate.

---

## Embedded-vendor flat-rate alternatives (2026)

When the cost-stacking math on Sigma/Looker/ThoughtSpot doesn't pencil:

| Vendor | Entry price | Surface | Multi-tenant story |
|---|---|---|---|
| **Qrvey** | Custom (flat-rate, not metered) | SDK + iframe, deploys into customer cloud | Multi-tenant-native, white-label |
| **Toucan** | €890/mo entry | White-label + API, embedded SDKs | RLS on JWT |
| **Tinybird** | $25/mo developer plan | ClickHouse-backed, real-time SDK | Per-workspace isolation |

[verify-at-use — 2026-06-04 — pricing pages, vendor-stated]

---

## What you almost certainly don't need

- **DB-per-tenant from day 1** — over-provisioning. Start pooled; promote to schema-per-tenant or DB-per-tenant when a specific enterprise customer needs it as a contractual carve-out.
- **Adaptive Compute Preview as your scaling answer** — vendor-claimed 1.6×-3.5× speedup, but Preview, Enterprise+ only, three regions. Seemore Data's caveat is sober: it changes the interface, not the engineering problem.
- **A custom RLS layer when Cube does it** — Cube's JWT security context is mature, well-trodden. Build it yourself only if Cube is rejected for other reasons.

---

## Sources to track (subscribe)

- **Qrvey, Toucan, Tinybird changelogs** — flat-rate embed shifts.
- **Cube blog** — semantic layer + agentic analytics (Cube D3, Analytics Chat API).
- **Snowflake release notes** — Snowpipe pricing, Adaptive Compute GA promotion, Cortex Analyst pricing.
- **MotherDuck docs** — Hypertenancy + DuckDB-WASM.
- **Tremor changelog** (Vercel-owned) — v4 stable signal.
- **Gartner Magic Quadrant Embedded Analytics** — annual refresh.

---

## See also

- [`snowflake-operational-dashboard-patterns.md`](./snowflake-operational-dashboard-patterns.md) — Snowflake-side mechanics + SiS owner's-rights detail.
- [`snowflake-psm-dashboard-cost-model.md`](./snowflake-psm-dashboard-cost-model.md) — explicit per-line cost calculation.
- [`charting-library-selection-2026.md`](./charting-library-selection-2026.md) — render-layer choice once tenancy + vendor are picked.
- [`multi-tenant-rls-patterns.md`](./multi-tenant-rls-patterns.md) — RLS specifics.
- [`embedded-analytics-landscape-2026.md`](./embedded-analytics-landscape-2026.md) — vendor-by-vendor depth.
