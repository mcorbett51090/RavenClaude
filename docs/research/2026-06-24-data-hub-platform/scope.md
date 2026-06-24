# G0 — Scope: Unified Data Hub Platform (slug: data-hub-platform)

**Date:** 2026-06-24 · **Owner:** Matt · **Depth:** standard · **Models:** A=opus, B=sonnet

## Scoped intent (one paragraph)
A web-based application a **non-technical user ("layman")** uses to add app registrations / OAuth
credentials and connect their SaaS data sources (QuickBooks, Stripe, Salesforce, HubSpot, Google
Calendar, Slack, Granola, Planhat, …) into one place. The app **primarily pulls data IN** to build
reporting/dashboards and **secondarily pushes data OUT** to other systems (reverse-ETL). Connectors
are **built from scratch** and the **core connections live in the application itself**. The app has
**secure credential storage built in**. A **"vibecoder" + Claude build the dashboards** per customer.

## Pinned decisions (from G0 clarify)
1. **Delivery model = per-customer consulting deploy** — one isolated single-tenant instance per
   engagement. Defers multi-tenant RLS / JWT-embed complexity.
2. **Connectors = build from scratch** — Matt has done this before (Planhat, Salesforce, Google
   Calendar, Slack, Granola). NOT Airbyte/Merge/Nango as a runtime dependency. (The connector-SDK
   *pattern* from those tools is still borrowable — see G1.)
3. **This run produces = full platform architecture** — to hand to Ultraplan as a large cloud build.

## Success signal (one line)
A layman connects ≥2 real sources via guided OAuth, data lands in secure per-customer storage, and
Claude builds a working dashboard on top — end to end, with no hand-edited secrets and no per-customer
hand-coded SQL sprawl.

## Explicitly OUT of scope
- Multi-tenant SaaS / shared-tenant RLS (Phase-2 "if proven" only).
- A 700-connector catalog. Each instance carries a **small curated source set** for that customer.
- Selling this as a self-serve product. It is consulting-delivered.

## Key tension to resolve in the panels
"Build from scratch" is pinned by Matt — but G1 (claim B.4) flags connector **maintenance** as the
dominant lifetime cost and the red-team's primary attack. The panels must make from-scratch
**sustainable** (declarative connector SDK + versioned registry + semantic layer), not relitigate the
decision.
