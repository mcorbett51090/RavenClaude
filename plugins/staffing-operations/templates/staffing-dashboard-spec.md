# Staffing Dashboard Spec — `<audience: VP Ops / MD / desk lead>`

**Decision this dashboard serves:** `<the one question — e.g., "are we filling fast enough to win placements?">`
**Segment selector:** `<healthcare-travel | locum | allied | per-diem | education-school-based>` (never a cross-segment blend as headline)
**Refresh cadence:** `<daily / weekly>` · **Data source:** `<ATS / VMS export>`

## Layout (information hierarchy)

1. **Top-left (decision metric):** `<fill rate | margin | FTE on assignment>` — value + delta + baseline + 12-period sparkline.
2. **Paired tiles (adjacency enforces §3 #2–#4):**
   - Fill rate ▸ Time-to-fill (to start)
   - Gross margin ▸ Bill / Pay / Burden breakdown
   - Revenue per recruiter ▸ Reqs per recruiter
3. **Quality strip:** redeployment, fall-off, extension, NPS.
4. **Aging panel:** requisition-aging distribution (nominal vs. workable).

## Per-tile contract
- Value, delta vs. baseline, and the baseline named (prior / SLA / target).
- Sparkline for seasonality context.
- On red: surface top 1–2 drivers (from the scorecard drill-down).
- Triggered action shown in plain language beside the tile.

## Benchmarks
- Client baseline = solid reference line. External benchmark = dashed line, labeled `[ESTIMATE]` if advisory-sourced.

## Demo data
See [`../bi-report/data.json`](../bi-report/data.json) for the shape (de-identified, no PII).

## Build / instrumentation
Route the actual build to `ravenclaude-core/data-engineer`. This spec defines layout + semantics only.
