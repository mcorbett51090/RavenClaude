# Automotive Dealership Operations KPI Glossary

> The team's canonical metric definitions. Every metric carries a **definition**, a **window**, and a **baseline** before it ships (CLAUDE.md §3 #1). Benchmark ranges are `[unverified — training knowledge]` unless a dated source is attached — confirm against a current source before using in a deliverable (§3 #8).

## Variable ops — sales & gross

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Front gross** | Vehicle gross (sale − cost − pack) | Per unit | Half the picture; read with the back (§3 #3). |
| **Back gross (PVR)** | F&I back-end gross ÷ units retailed | Per unit | High-margin; inside compliance (§3 #4). |
| **Total gross/unit** | (front + back) ÷ units | Per unit | The real deal-profitability number (§3 #3). |
| **F&I penetration** | Product sales ÷ units retailed | Period | The back-end lever (§3 #4). |

## Inventory & floorplan

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Days-supply** | Units in stock ÷ daily sales rate | Point-in-time | Read vs target; aged units burn cash (§3 #2). |
| **Floorplan cost** | Units × per-unit daily carry | Period | Interest + holdback + depreciation drag (§3 #2). |
| **Aged inventory** | Units past the target days-supply | Point-in-time | Price-to-turn rather than hold (§3 #2). |

## Fixed ops & survival

| Metric | Definition | Window | Note |
|---|---|---|---|
| **Fixed-ops gross** | Service + parts gross profit | Period | The durable profit engine (§3 #1). |
| **Absorption rate** | Fixed-ops gross ÷ total fixed overhead | Period | The survival metric; ≥100% self-covers (§3 #5). |
| **Service retention** | Customers returning for service | Rolling | Feeds the annuity and repeat sales (§3 #7). |
| **CSI** | Customer satisfaction index | Rolling | A leading indicator, not a number to game (§3 #7). |

## The rule

A metric without a **window** and a **baseline** is not a finding — it's a number (§3 #1). A benchmark without a **source URL + retrieval date** is `[unverified — training knowledge]` (§3 #8).
