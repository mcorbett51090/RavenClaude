# Dashboard Design Spec — <dashboard name>

> Fill-in spec for designing a Tableau dashboard so the deliverable is **the question answered**,
> not the dashboard. Owned by `tableau-viz-engineer`. Chart type follows the question; performance
> is designed in, not tuned later. Date: <YYYY-MM-DD> · Author: <name>

## 1. The question(s)

| # | Business question (observable terms) | Question class | Audience |
|---|---|---|---|
| 1 | | comparison / trend / distribution / correlation / part-to-whole / geographic | |

> If you can't state the question, you can't pick the chart. Fill this first.

## 2. Grain & model

| Field | Value |
|---|---|
| Tables + grain | <each table's grain> |
| Connection method | relationship (default) / join / blend — + why |
| Connection mode | extract (default) / live — + freshness reason |

## 3. Sheets (chart type follows the question)

| Sheet | Answers Q# | Chart type | Why this type (not aesthetics) | Key calcs / LODs |
|---|---|---|---|---|
| | | | | |

## 4. Layout & interactivity

| Field | Value |
|---|---|
| Layout | <tiled / containers; sizing — fixed vs range> |
| Interactions | filter action / highlight action / parameter / set action — matched to user intent |
| Filters | <which, what layer; relevant-values for high-cardinality> |

## 5. Performance by design (not later)

- [ ] Filters at the lowest layer
- [ ] Mark count bounded
- [ ] No high-cardinality "all values" quick filters
- [ ] LOD / table-calc addressing explicit
- [ ] Sheets share source/grain (query fusion)

## 6. Integrity & accessibility

- [ ] Axes not truncated; dual axes synchronized; no two-point "trend"
- [ ] Meaning not encoded by color alone (color-vision-deficiency safe)
- [ ] Labels, contrast, tooltips legible

## 7. Governance notes

- **Permissions / RLS / embedding:** <if any → tableau-admin; security verdict → security-reviewer>
- **Volatile claims `[verify-at-build]`:** <feature availability, version limits>
