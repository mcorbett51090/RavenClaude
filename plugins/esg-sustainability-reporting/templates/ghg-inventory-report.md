# GHG Inventory Report — Template

> Output of `ghg-accounting-analyst` / the `ghg-inventory` skill. A figure with no factor source/vintage,
> a single-method Scope 2 where both are required, or an undocumented base year is not assurance-ready.

## 1. Inventory boundary

- **Consolidation approach:** <equity share / financial control / operational control>
- **Matches the disclosure boundary?** <yes / delta named>
- **Reporting period:** <FY>

## 2. Scope 1

| Source | Activity data | Emission factor (source + vintage) | Method | tCO2e | Data-quality tier |
|---|---|---|---|---|---|
| <combustion/fleet/fugitive/process> | | | | | <primary / estimated> |

## 3. Scope 2 (dual reporting)

| Method | Basis | Emission factor (source + vintage) | tCO2e |
|---|---|---|---|
| Location-based | <grid-average factor> | | |
| Market-based | <RECs/GOs/PPAs/green tariff — instruments named + quality-screened> | | |

_Both required where instruments exist. Offsets are reported separately, never netted in._

## 4. Scope 3 — 15-category relevance screen

| # | Category | Relevant? | Included / excluded (rationale) | tCO2e | Data-quality tier |
|---|---|---|---|---|---|
| 1 | Purchased goods & services | | | | <spend-based = lower tier> |
| 2 | Capital goods | | | | |
| 3 | Fuel- & energy-related | | | | |
| 4 | Upstream transport & distribution | | | | |
| 5 | Waste generated in operations | | | | |
| 6 | Business travel | | | | |
| 7 | Employee commuting | | | | |
| 8 | Upstream leased assets | | | | |
| 9 | Downstream transport & distribution | | | | |
| 10 | Processing of sold products | | | | |
| 11 | Use of sold products | | | | |
| 12 | End-of-life of sold products | | | | |
| 13 | Downstream leased assets | | | | |
| 14 | Franchises | | | | |
| 15 | Investments (incl. financed emissions) | | | | |

## 5. Base year & recalculation

- **Base year:** <FY> · **Recalculation policy:** <documented> · **Significance threshold:** <%>
- **Restatement this cycle?** <yes (structural change) / no>

## 6. Totals & data quality

| Scope | tCO2e | % primary data | Weakest lines (flagged) |
|---|---|---|---|
| 1 | | | |
| 2 (location / market) | / | | |
| 3 | | | |

---

```
Status: ...
Files changed: ...
Framework & clause: ...
Assurance posture: ...
Handoff to source systems: ...
Open questions: ...
Grounding checks performed: ...
```
