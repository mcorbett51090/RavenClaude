---
name: pt-clinic-pl-and-payer-mix
description: "Model the PT clinic P&L on reimbursed-visit economics — build the P&L on the real levers (reimbursed visits, units/visit, net collection/visit, cancellation rate, labor cost), analyze payer mix by net collection and administrative burden, and find where margin actually moves."
---

# PT Clinic P&L & Payer Mix

**Purpose:** model clinic profitability on reimbursed-visit economics — not booked visits or gross fee
schedule — and locate the levers that actually move margin.

---

## Steps

### 1. Build the P&L on the real levers

| Lever | Why it moves margin |
|---|---|
| Reimbursed visits | the unit of revenue (booked ≠ reimbursed) |
| Units per visit | within medically-necessary, documented bounds only |
| Net collection per visit | denials, coding accuracy, payer mix |
| Cancellation / no-show rate | recovered delivered visits |
| Labor cost / productivity | the largest cost line |

Use [`../../scripts/pt_calc.py`](../../scripts/pt_calc.py) `net_collection_per_visit`,
`units_per_visit`, `cancellation_rate`, and `clinic_contribution_margin`.

### 2. Count reimbursed visits, not booked visits

A schedule full of cancellations and denied claims is not a full schedule. Start the model from
delivered-and-reimbursed visits (see
[`count-reimbursed-visits-not-booked-visits`](../../best-practices/count-reimbursed-visits-not-booked-visits.md)).

### 3. Analyze payer mix by net collection AND admin burden

Rank payers by **net collection per visit** and the **administrative burden** each carries (auth
friction, denial rate, documentation demands). The highest gross fee schedule is not the best payer if
it denies a third of claims. A concentrated mix is also a risk.

### 4. Connect adherence to the economics

Plan-of-care adherence is the economic engine: a completed episode is the multi-visit revenue that
funds the clinic. The P&L assumptions about visits-per-episode rest on adherence — make them explicit.

### 5. Find the binding lever

Pull in order of leverage: adherence → cancellation rate → net collection per visit → units (within
bounds) → labor. Don't chase units past medical necessity; over-utilization is audit liability, not
margin.

---

## Output

A clinic P&L model on reimbursed-visit economics, a payer-mix analysis (net collection + admin
burden), and the binding margin lever. Frames into the practice-lead's operating model.
