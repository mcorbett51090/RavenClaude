# Hospitality — Hotel Operations

The **hospitality-hotel-operations** plugin — the lodging / rooms craft: running a hotel property as a business across operations, revenue, and reputation. It runs the front office and housekeeping, builds and prices the rate strategy that drives RevPAR, and closes the guest-experience and loyalty loop — distinct from the restaurant and food-and-beverage operation (`restaurant-operations`).

## Agents

- **`hotel-operations-lead`** — Property operations: front desk / PMS workflows, housekeeping productivity and room-status flow, the end-to-end guest journey, SOP authoring, labor scheduling to the occupancy forecast, and maintenance/engineering coordination. Runs the property as one system, not a set of siloed departments.
- **`revenue-manager`** — Rooms revenue: RevPAR / ADR / occupancy / GOPPAR, pricing and rate strategy (the BAR/rate ladder), channel and OTA mix and cost, demand forecasting, and overbooking / yield. Optimizes RevPAR on **net** ADR after distribution cost, never occupancy or headline rate in isolation.
- **`guest-experience-analyst`** — Reputation and loyalty: reviews and online-reputation management, guest-satisfaction measurement (NPS / GSS / verbatims), the comment-to-action loop, service-recovery playbooks, and loyalty / repeat economics. Treats the review as a defect report and closes the loop to an operational fix.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install hospitality-hotel-operations@ravenclaude
```

## Seams

- **The restaurant, bar, banquet, kitchen, menu, covers** → `restaurant-operations`; this plugin runs the rooms, that one runs the F&B outlet.
- **The statistical model behind the demand forecast (seasonality, method choice, confidence intervals)** → `applied-statistics`; we frame and consume the forecast, they own the method.
- **The reporting warehouse, BI pipeline, and dashboards for the KPIs** → `data-platform`; we define the KPI set and metric definitions, they build the pipeline.
- **Guest PII, payment data, loyalty-account data, and consent** → `ravenclaude-core/security-reviewer` + `data-governance-privacy`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `restaurant-operations`, `applied-statistics`, and `data-platform`.
