# Fixed-Ops KPI Dashboard

> Monthly/weekly scorecard for the service and parts department.
> Reference skill: `skills/fixed-ops-service-and-parts/SKILL.md`.
> Calculator: `scripts/dealer_calc.py` modes `absorption`, `elr`.

---

## Report Header

| Field | Value |
|---|---|
| Store name | |
| Reporting period | |
| Prepared by | |
| Date prepared | |

---

## 1. Absorption Rate

| Input | Value |
|---|---|
| Service labor gross ($) | |
| Service parts gross ($) | |
| Body shop gross ($, if applicable) | |
| **Total fixed gross ($)** | |
| **Total dealership overhead ($)** | |
| **Absorption rate (%)** | = Fixed gross ÷ Overhead |

| Status | Threshold |
|---|---|
| Critical | < 70% |
| Below average | 70–84% |
| Average | 85–95% |
| Good | 96–100% |
| Excellent | > 100% |

> Benchmark source: [verify-at-use against current 20-group data].
> Dollar gap to target: `(Target % − Actual %) × Total overhead = $___`

---

## 2. Effective Labor Rate (ELR)

| Input | Value |
|---|---|
| Total labor sales ($) | |
| Total hours sold | |
| **ELR ($ / hour)** | = Labor sales ÷ Hours sold |
| Posted labor rate ($) | |
| **ELR gap from posted ($)** | = Posted − ELR |

### ELR Waterfall

| Layer | $/hour | Comment |
|---|---|---|
| Posted rate | | Rate card |
| Warranty dilution | | OEM caps below posted |
| Internal dilution | | Internal RO rate vs posted |
| Advisor discounting | | Authorized + unauthorized |
| Come-back credits | | Come-back RO credits |
| Other adjustments | | |
| **Actual ELR** | | |

---

## 3. Technician Productivity

| Tech (name or ID) | Hours Avail. | Hours Flagged | Hours Sold | Flag Rate (%) | Efficiency (%) | Utilization (%) |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |
| **Total / Average** | | | | | | |

| Metric | Formula | Target [verify-at-use] |
|---|---|---|
| Flag rate | Hours flagged ÷ hours available | ≥ 85% |
| Efficiency | Hours sold ÷ hours flagged | ≥ 100% (CP) |
| Utilization | Hours flagged ÷ hours scheduled | ≥ 90% |

---

## 4. RO Count and Mix

| Pay Type | RO Count | % of Total | Labor Gross ($) | % of Labor Gross |
|---|---|---|---|---|
| Customer pay (CP) | | | | |
| Warranty | | | | |
| Internal | | | | |
| **Total** | | | | |

> Internal pricing check: are internal ROs priced at full posted rate?
> If no, internal subsidy = `(Posted rate − internal rate) × internal hours sold = $___`

---

## 5. Service RO Metrics

| Metric | Value | Target [verify-at-use] |
|---|---|---|
| Total RO count | | |
| CP RO count | | |
| Hours per RO (CP) | | ≥ 2.0 hrs |
| Come-back rate (%) | | < 3% |
| CSI score | | Per OEM standard |
| First-visit fix rate (%) | | ≥ 90% |

---

## 6. Parts Performance

| Metric | Value | Notes |
|---|---|---|
| Total parts gross ($) | | |
| Parts-to-service ratio (%) | = Parts gross ÷ Labor gross | Target: 45–55% [verify-at-use] |
| Parts GP% | | |
| Wholesale parts gross ($) | | |
| Non-moving stock (>12 mo) % | | Obsolescence indicator |

---

## 7. Ranked Action Items

| # | Finding | Dollar Impact ($/mo) | Action | Owner | Deadline | Time Horizon |
|---|---|---|---|---|---|---|
| 1 | | | | | | Quick / Structural |
| 2 | | | | | | Quick / Structural |
| 3 | | | | | | Quick / Structural |

---

## 8. Month-Over-Month Trend

| Metric | Prior Month | This Month | Change | Trend |
|---|---|---|---|---|
| Absorption % | | | | ↑ / ↓ / → |
| ELR ($) | | | | ↑ / ↓ / → |
| Total RO count | | | | ↑ / ↓ / → |
| Hours per RO | | | | ↑ / ↓ / → |
| CSI score | | | | ↑ / ↓ / → |

---

_Template version: 0.1.0. Last reviewed: 2026-06-08._
