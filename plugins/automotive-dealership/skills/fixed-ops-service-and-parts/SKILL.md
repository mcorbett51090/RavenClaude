---
description: "Run a full fixed-ops diagnosis: absorption rate gap analysis by lever (RO count, ELR, CP retention, parts gross), ELR waterfall (posted to actual), technician productivity (flag rate, efficiency, utilization), RO mix optimization (CP/warranty/internal), and parts-to-service ratio. Returns a dollar-denominated improvement plan with time horizons."
---

# Fixed-Ops Service and Parts

**Purpose:** systematically diagnose and improve dealership service and parts performance —
absorption rate, ELR, tech productivity, RO mix, parts gross, and CSI — through a
structured set of steps that always returns dollar-denominated findings.

## Entry point

Use this skill when the question is: "Why is absorption low?", "What is causing ELR
dilution?", "How do I improve technician productivity?", or "What is wrong with parts gross?"

Primary agent: `fixed-ops-analyst`. Supporting agents: `dealership-ops-lead` (whole-store
context), `inventory-and-desking-analyst` (internal RO pricing for recon).

## Steps

### 1. Gather baseline inputs

Collect the following (request from user or read from available context):
- Total RO count (CP / warranty / internal split) for the period
- Total labor sales by pay type
- Total hours sold and hours available (tech headcount × scheduled hours)
- Posted labor rate and effective rate by pay type
- Parts sales (wholesale / internal / retail / wholesale gross)
- Total dealership overhead (fixed + variable) for absorption denominator
- CSI score and trend (optional, needed for retention analysis)

### 2. Calculate absorption rate

```
Fixed gross = service labor gross + service parts gross + body shop gross (if applicable)
Absorption rate = Fixed gross ÷ Total dealership overhead
```

Compare against benchmarks: <70% (critical), 70–85% (below average), 85–100% (average–good),
>100% (excellent — overhead fully covered by fixed ops) [verify-at-use against current
20-group data]. Flag the dollar gap: `(target % − actual %) × total overhead`.

### 3. Build the ELR waterfall

```
ELR = Total labor sales ÷ Total hours sold
```

Waterfall layers:
1. **Posted rate** — the rate on the rate card
2. **Warranty dilution** — warranty caps below posted rate (OEM-set, cannot change)
3. **Internal dilution** — internal RO rate vs posted rate; identify gap
4. **Advisor discounting** — authorized discounts vs unauthorized; audit auth levels
5. **Come-back credits** — come-backs reduce billed hours; track separately
6. **Miscellaneous adjustments** — free LOF with purchase, goodwill, etc.

Identify the largest dilution layer; quantify in $/month.

### 4. Diagnose technician productivity

Three metrics, each with its own lever:

| Metric | Formula | Target (general) |
|---|---|---|
| Flag rate | Hours flagged ÷ hours available | 85–100%+ [verify-at-use] |
| Efficiency | Hours sold ÷ hours flagged | 100%+ on CP [verify-at-use] |
| Utilization | Hours flagged ÷ hours scheduled | >90% [verify-at-use] |

Low flag rate → scheduling, come-backs, parts availability, shop capacity.
Low efficiency → tech skill, repair order accuracy, parts delays.
Low utilization → scheduling gaps, call-outs, shop loading.

### 5. Analyze RO mix

Calculate CP%, warranty%, internal% of total RO count and labor gross.
- Internal ROs are the controllable variable: are they priced at full retail, discounted,
  or at cost? Identify subsidy dollars flowing from service to variable.
- Warranty mix is OEM-determined; focus on warranty ELR vs labor-time guide accuracy.
- High internal % with below-market pricing is a silent transfer to variable ops.

### 6. Assess parts performance

```
Parts-to-service ratio = Parts gross ÷ Service labor gross
```

General benchmark: 45–55% [verify-at-use]. Below this suggests missed part attachment,
wholesale pricing issues, or obsolescence dragging GP%.

Check:
- Parts obsolescence (non-moving stock >12 months as % of total inventory)
- Wholesale gross vs retail gross vs internal
- ELR-equivalent for parts (parts GP% × effective labor rate attachment)

### 7. Output the improvement plan

Rank findings by dollar impact. For each:
- **Finding** (e.g., "Advisor discounting costs $8,400/month")
- **Dollar impact** (monthly and annualized)
- **Fix** (specific, with owner and deadline)
- **Time horizon** (quick-win ≤30 days vs structural ≥90 days)

Use [`../../templates/fixed-ops-kpi-dashboard.md`](../../templates/fixed-ops-kpi-dashboard.md)
for the output artifact.

## Anti-patterns

- Confusing posted rate with ELR — they are always different numbers.
- Diagnosing "low tech productivity" without separating flag rate, efficiency, and utilization
  (different problems, different fixes).
- Reporting absorption improvement without identifying which lever is moving.
- Recommending advisor compensation changes without a parallel ELR analysis.

## Output

A dollar-denominated fixed-ops diagnosis: absorption rate with gap, ELR waterfall with
largest dilution layer identified, tech productivity by metric, RO mix subsidy quantified,
parts performance summary, and ranked action plan with time horizons.
