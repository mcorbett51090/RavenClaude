---
description: "Run a full inventory and desking analysis: days-supply by segment with floor-plan cost, hold-vs-wholesale evaluation on a specific unit, recon time and cost SLA assessment, sourcing gap analysis, and deal desking (trade spread, front-end gross, payment sensitivity, pencil progression). Uses the hold-vs-wholesale decision tree and desking worksheet template."
---

# Inventory and Desking

**Purpose:** systematically manage vehicle inventory (days-supply, floor-plan cost, recon,
sourcing) and desk individual deals (trade spread, front-end gross, F&I flag) through a
structured process that always returns a dollar-grounded recommendation.

## Entry point

Use this skill when the question is: "What is our days-supply by segment?", "Should I hold
or wholesale this unit?", "How do I reduce recon time and cost?", "Desk this deal to gross."

Primary agent: `inventory-and-desking-analyst`. Supporting agents: `dealership-ops-lead`
(whole-store context), `fixed-ops-analyst` (internal RO recon pricing), `fni-advisor`
(F&I opportunity on the deal).

## Steps

### 1. Inventory health baseline

Collect for each segment (new: by model, used: by segment — compact, midsize, SUV, truck, etc.):
- Units on hand (lot + in-transit + recon-in-process)
- Prior 30-day retail sales rate (or 60-day average for lower-volume stores)
- Floor-plan balance and applicable interest rate

Calculate:
```
Days-supply = Units on hand ÷ (Average monthly retail rate ÷ 30)
Daily floor-plan cost per unit = (Floor-plan balance × annual rate) ÷ 365
```

Flag segments outside target range. General used-car target: 45 days [verify-at-use].
New-vehicle target: OEM-specified by model, typically 30–60 days [verify-at-use].

### 2. Aging analysis

Bucket units into age tiers: 0–30 days, 31–60 days, 61–90 days, 91+ days.
For each over-60-day unit: calculate cumulative floor-plan cost to date + projected
additional cost if held to 90 days. Flag units where cumulative holding cost exceeds 25%
of estimated front-end gross opportunity.

### 3. Hold-vs-wholesale evaluation (per unit)

Traverse the **Hold-vs-wholesale** decision tree in
[`../../knowledge/automotive-dealership-decision-trees.md`](../../knowledge/automotive-dealership-decision-trees.md).

Key inputs:
- ACV (actual cash value — market wholesale, not book value)
- Recon estimate (itemized if possible)
- Estimated retail price after recon (based on comparable retail comps)
- Estimated front-end gross = retail price − total investment (ACV + recon + holding cost to sale)
- Days to retail from today (estimate)
- Additional holding cost for those days

```
Hold if: expected net retail gross > immediate wholesale net recovery
Wholesale if: recon cost + remaining holding cost > expected gross improvement over wholesale
```

Break-even recon threshold: `(Estimated retail − ACV) − expected remaining holding cost`.
If recon quote > break-even, wholesale.

### 4. Recon time and cost SLA assessment

For the recon pipeline:
- Average days from acquisition to retail-ready (target: ≤5 business days [verify-at-use])
- Average recon cost per unit vs budget
- Recon-in-process count and average age
- Reason codes for recon delays (parts, scheduling, authorization)

Flag: any unit >7 business days in recon as an escalation. Identify whether delay is
a fixed-ops scheduling issue (route to `fixed-ops-analyst`) or a parts availability issue.

### 5. Sourcing gap analysis

Compare days-supply by segment to target:
- **Over-supplied segments:** develop liquidation plan (pricing reduction schedule, wholesale
  channel, in-store trade-in incentive to shift customer interest).
- **Under-supplied segments:** develop sourcing plan (auction (Manheim/ADESA/OVE), dealer-to-dealer
  trade, off-lease return, direct-from-customer conquest buy).

Quantify missed retail gross on under-supplied segments: `(Target days-supply − actual days-supply)
× estimated daily retail gross opportunity`.

### 6. Deal desking

Collect:
- OTD (out-the-door) target price or monthly payment asked by customer
- Trade-in allowance asked by customer vs ACV (your appraisal)
- Vehicle cost (invoice + pack for new; total investment for used)
- Target front-end gross
- Finance rate/term options available

Structure the desk:
```
Trade spread = Customer's asked allowance − ACV (your cost)
Front-end gross = Selling price − Vehicle cost
Total variable gross = Front-end gross − Trade spread
```

Build a payment sensitivity matrix at 2–3 rate/term combinations.
Design the pencil progression: first pencil (near ask, near gross target) → counter
(split-the-difference structure) → close (minimum acceptable structure). Flag F&I
opportunity for each deal structure.

Use [`../../templates/desking-worksheet.md`](../../templates/desking-worksheet.md)
for the deal output artifact.

## Anti-patterns

- Using KBB retail (book value) instead of ACV (market wholesale/trade-in cash) to evaluate
  trades — always use a market source (Manheim MMR, vAuto/dealer tool, auction history).
- Recon with no cost cap or time SLA — open-ended recon destroys used-car gross.
- Desking purely to a payment without tracking front-end gross and trade spread.
- Holding every unit regardless of age — the decision must be data-driven, not habitual.
- Days-supply analysis on total inventory only, masking segment-level imbalances.

## Output

A segment-by-segment days-supply table with floor-plan cost, an aging report with 60-day
action list, hold-vs-wholesale recommendation (with decision tree leaf cited), recon SLA
status, sourcing gap summary, and (if desking) a complete deal structure with payment
sensitivity matrix and pencil progression.
