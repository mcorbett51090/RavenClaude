# Hospitality / Hotel Operations scenarios bank

> Unverified, dated, scope-tagged narratives from real hotel-operations engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real lodging-operations work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: hospitality-hotel-operations
product: <opera | mews | cloudbeds | ideas | duetto | siteminder | revinate | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-occupancy-win-revpar-loss.md`](2026-06-08-occupancy-win-revpar-loss.md) | revpar, adr, occupancy, channel-mix, net-adr | `revpar-is-the-north-star`, `price-on-net-adr-after-distribution` |
| [`2026-06-08-reviews-archived-not-actioned.md`](2026-06-08-reviews-archived-not-actioned.md) | reviews, comment-to-action, service-recovery, loyalty | `the-review-is-a-defect-report`, `service-recovery-is-a-designed-process` |
| [`2026-06-08-overbook-walk-with-no-protocol.md`](2026-06-08-overbook-walk-with-no-protocol.md) | overbooking, walk-protocol, yield, no-show | `overbook-only-to-a-forecasted-no-show-rate` |
| [`2026-06-08-pms-side-spreadsheet-drift.md`](2026-06-08-pms-side-spreadsheet-drift.md) | pms, room-status, housekeeping, double-sold | `the-pms-is-the-system-of-record` |
| [`2026-06-08-labor-cut-below-service-floor.md`](2026-06-08-labor-cut-below-service-floor.md) | labor, staffing, service-floor, review-score | `staff-to-the-curve-protect-the-service-floor` |
