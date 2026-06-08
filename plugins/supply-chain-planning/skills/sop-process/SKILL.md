---
description: "Design or facilitate the monthly S&OP/IBP cycle: run the five-step gate sequence (product review → demand review → supply review → pre-S&OP reconciliation → executive S&OP), produce the gap analysis, build scenarios, and close the cycle with a decision record."
---

# S&OP Process

**Purpose:** facilitate a disciplined, decision-producing monthly S&OP cycle that reconciles the
demand plan, supply plan, and inventory position into one approved operating plan.

---

## The five-step gate sequence

| Step | Owner | Input required | Output |
|---|---|---|---|
| **1. Product review** | Supply chain / product mgmt | Product lifecycle changes, new launches, EOL SKUs | Updated SKU list; NPI and discontinuation flags |
| **2. Demand review** | Demand planning | Statistical baseline, commercial overlays, MAPE/bias KPIs | Consensus demand plan (unconstrained) |
| **3. Supply review** | Supply / operations | Capacity plan, procurement lead times, supply constraints | Capacity-constrained supply plan; gap vs. demand plan |
| **4. Pre-S&OP (reconciliation)** | Supply chain / finance | Demand plan + supply plan + inventory position | Gap analysis, options, recommended scenario, financial view |
| **5. Executive S&OP** | ExecCo (COO/CEO) | Pre-S&OP pack (one page) + top-3 decisions | Approved scenario, decision record, triggers for next review |

---

## Steps

### 1. Set the calendar

- Fix the cycle start date (Day 1 = data cutoff) and each gate date.
- Typical monthly cadence: data cutoff D+0 → demand review D+3 → supply review D+7 → pre-S&OP
  D+10 → executive S&OP D+14.
- Publish the rolling 13-month forward calendar. The cycle does **not** move for busy months.

### 2. Run the product review (Day 1–2)

- Confirm which SKUs are active, NPI, end-of-life, or phasing.
- Flag any NPI without an analogue-based demand assumption — this becomes a risk item in the
  demand review.
- Output: a current SKU master with lifecycle status.

### 3. Run the demand review (Day 3–4)

- Present the statistical baseline with MAPE and bias from the last 3 months.
- Review commercial overrides: each override named, quantified, and rationale documented.
- Reach consensus on the demand plan — the single unconstrained number for the horizon.
- Flag high-uncertainty SKUs (high CV, new launches, discontinued) for scenario treatment.
- Output: the consensus demand plan with accuracy KPIs and override log.

### 4. Run the supply review (Day 5–8)

- Load the demand plan into MRP / capacity planning and run the supply plan.
- Identify capacity bottlenecks, supplier constraints, and lead-time gaps.
- Quantify: where demand exceeds supply (gap in units, by period); root cause; lead time to
  relieve; options (overtime, dual source, demand deferral).
- Output: the constrained supply plan + the gap list.

### 5. Pre-S&OP reconciliation (Day 9–11)

- Gap analysis: demand plan − supply plan = gap by period, by product family.
- Generate options for each gap:
  1. Supply acceleration (OT, expedite, dual source) — lead time + cost
  2. Demand prioritization (allocate to highest-margin or contractual accounts)
  3. Demand shaping (pricing, promotion, lead-time extension)
  4. Inventory buffer draw-down (if safety stock permits)
- Recommend a scenario with the financial impact (revenue, margin, working capital).
- Output: the pre-S&OP pack: one-page summary, gap table, options, recommended scenario, financial
  impact.

### 6. Executive S&OP (Day 12–14)

- Present: one-page performance summary (actuals vs. plan last month), top-3 supply-demand
  decisions, recommended scenario with alternatives.
- Keep the meeting ≤ 90 minutes. Operational detail belongs in pre-S&OP.
- Close with a decision record: the approved scenario, any conditions, the owner of each action,
  and the trigger that would require an out-of-cycle review.
- Output: signed decision record → distributed to all step owners within 24 hours.

### 7. Post-cycle: measure and improve

- Track S&OP KPIs: forecast accuracy (MAPE/bias), plan attainment (actual vs. approved plan),
  on-time meeting completion, override accuracy.
- Run a quarterly S&OP health check: are decisions being made? Is the cycle skipped? Is there
  one number?

## Anti-patterns

- An S&OP meeting with no pre-work (no demand plan, no supply plan, no gap list).
- Exec S&OP that spends time reviewing operational detail pre-S&OP should have resolved.
- No decision record — a meeting without a written, distributed decision is not an S&OP.
- Skipping the cycle in "busy months" — the value is highest under pressure.
- Multiple numbers in flight (demand, supply, and finance each running different forecasts).

## Output

An S&OP process design, a facilitated cycle, or a cycle health diagnosis. Use the templates:
[`../../templates/sop-deck.md`](../../templates/sop-deck.md) for the exec S&OP pack.
Use the `sop-process-lead` agent for the full guided workflow.
