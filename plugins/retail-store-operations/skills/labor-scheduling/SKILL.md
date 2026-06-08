---
description: "Build or diagnose a store labor model: translate hourly traffic data into a coverage-ratio schedule, decompose a labor % of sales variance into rate vs. hours vs. demand, size a flex/part-time headcount for a seasonal period, and flag predictive-scheduling compliance exposure."
---

# Labor Scheduling

**Purpose:** produce a schedule grounded in traffic data — one where labor is deployed when
customers are present and conversion opportunity is highest, and where labor % of sales is an
output of the model, not a blunt cut.

---

## Entry-point playbook

### Step 1 — Collect the traffic basis

| Input | Why it matters |
|---|---|
| Hourly transaction count or traffic counter data | The foundation — no schedule without it |
| Average conversion rate by hour block | Converts traffic to revenue opportunity |
| Historical sales by day-of-week and hour | Demand shape for staffing |
| Current scheduled hours vs. actual hours | Adherence baseline |
| Current labor % of sales | Financial target benchmark |
| Target labor % of sales | The financial constraint |

**If hourly traffic data is unavailable:** state this explicitly and use hourly transaction count
as a proxy. A schedule built with no traffic basis must be flagged as estimated.

### Step 2 — Build the traffic curve

1. Aggregate hourly traffic (or transaction count) by day-of-week for at least 4 weeks.
2. Compute the average and peak traffic index by hour block (index = hour traffic ÷ daily average).
3. Identify the peak block(s) — typically Saturday 11 am–2 pm, weekday lunch windows, and
   evening-before-close for many formats. These vary by store type — flag when assumptions are used.
4. Identify the valley blocks — opening, mid-morning weekdays, late Sunday.

### Step 3 — Apply coverage ratios

| Coverage ratio | Meaning |
|---|---|
| 1 associate per N customers per hour | Rule of thumb varies by format: specialty apparel ~1:8–12, home goods ~1:15–20, grocery front-end is transaction-rate-driven [verify-at-use] |
| Manager on duty | At least 1 salaried/key-holder at all times; 2 during peak and high-shrink windows |
| Task-based floor time | Stocking, receiving, and non-selling tasks must be scheduled in valley blocks, not peak |

**Coverage ratios must be calibrated to the store's actual conversion data** — these are starting
points, not universal constants.

### Step 4 — Design the shift shapes

Map coverage requirements back to schedulable shifts:

1. Identify the minimum coverage floor (opening through close with no gaps).
2. Layer in peak coverage using opening-to-peak and peak-to-close shifts.
3. Add flex (short, 4–5 hour) shifts on the highest-traffic blocks.
4. Assign task-heavy shifts (receiving, stocking) to valley windows.
5. Cross-check total hours against the labor-budget target.

Calculate: scheduled hours × average wage rate = labor cost. Labor cost ÷ projected sales = labor %.

Use [`../../scripts/retail_calc.py`](../../scripts/retail_calc.py) to verify sales-per-labor-hour.

### Step 5 — Decompose labor % of sales variance

When labor % is out of target, separate:

| Driver | Diagnosis |
|---|---|
| **Rate variance** | Actual wage rate vs. plan (overtime, higher-seniority staff, role mix) |
| **Hours variance** | Scheduled hours vs. actuals (callouts, early-outs, manager discretion) |
| **Demand variance** | Sales came in lower than forecast (traffic miss, conversion miss) |

Cutting hours to fix a demand-side miss destroys conversion. The fix for a rate variance is
scheduling, not headcount. Separate before prescribing.

### Step 6 — Compliance flags

Flag (do not interpret legally) the following ordinance types if in scope:

- **Advance notice:** predictive scheduling laws typically require 1–2 weeks' advance posting.
- **On-call restrictions:** many ordinances prohibit "report-in" or "on-call" shifts without
  minimum guaranteed pay.
- **Right-to-rest:** minimum hours between shifts (typically 8–12 hours) — flag short turnarounds.
- **Minor work restrictions:** hour limits for employees under 18.

**Always state:** legal interpretation requires counsel. This skill flags exposure; it does not
provide a compliance opinion.

### Step 7 — Output artifact

Use [`../../templates/store-labor-model.md`](../../templates/store-labor-model.md) to structure the
deliverable. Include: traffic basis used, coverage ratios, draft schedule by day/block, total
scheduled hours, projected labor %, SPLH, variance decomposition (if analyzing an existing
schedule), and compliance flags.

---

## Anti-patterns

- A schedule built on clock-based shifts without reference to traffic data or transaction counts.
- Labor % cut by reducing hours uniformly across all blocks.
- A holiday labor plan that doesn't account for the traffic surge on peak days.
- Coverage ratios presented as universal constants without a store-type and format note.
- A compliance statement with no citation of which ordinances were reviewed.

---

## Output

A labor scheduling deliverable from this skill always contains:

1. **Traffic basis** (traffic counter / transaction count / assumed — explicitly stated).
2. **Coverage ratios** by hour block and format type.
3. **Draft schedule** with shift shapes, total hours, and labor % projection.
4. **Sales per labor hour** (calculated or targeted).
5. **Variance decomposition** (if diagnosing an existing schedule): rate / hours / demand.
6. **Compliance flags** (advance notice, on-call, right-to-rest) with a counsel-required note.
7. **Handoff flag:** store-ops-lead for labor % impact on four-wall contribution.
