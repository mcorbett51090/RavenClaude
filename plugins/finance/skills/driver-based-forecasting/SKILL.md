---
name: driver-based-forecasting
description: Build and refresh a driver-based rolling forecast that survives FP&A review — driver tree from revenue volume × price, opex by category-driver, working-capital roll, capex schedule, scenario layer. Reach for this skill when standing up a new forecast model, refreshing the annual plan, or when an executive asks "what would it take to hit X?" Used by `fpa-analyst` (primary), `financial-modeler`, and `board-pack-composer` for the forecast slides.
---

# Skill: driver-based-forecasting

**Purpose:** Build forecasts the user can defend in a board room — every line traces back to a driver, every driver to an assumption, every assumption to a source. Spreadsheet-style "grow at 5%" forecasts fail this test. Used by `fpa-analyst` (primary).

## When to use

- Standing up a new forecast model (greenfield or replacing a spreadsheet)
- Annual planning / budget season
- Rolling-forecast refresh (monthly or quarterly cadence)
- Scenario-modeling requests ("what if churn doubles?", "what does it take to hit $50M ARR?")
- Pre-fundraise model build for investor / lender review
- Re-baselining after a material event (acquisition, divestiture, restructuring)

## The discipline: drivers, not growth rates

A driver-based forecast separates three layers:

1. **Inputs / drivers** — the small set of things the business actually moves (sales-reps hired, conversion rate, ASP, churn, headcount, comp-per-head, marketing spend)
2. **Mechanics** — formulas that turn drivers into financial line items (revenue = reps × productivity × ramp; opex = headcount × loaded-cost + non-comp)
3. **Outputs** — P&L, BS, CF, KPIs

Each layer lives in its own tab / section. A reviewer should be able to change exactly one driver and see every downstream number recalculate without touching formulas.

**Smell test:** if changing the revenue assumption requires editing more than one cell, the model is broken.

## Revenue: the driver tree

Pick the right tree for the business model.

### SaaS / subscription

```
ARR = Beginning ARR
    + New ARR (= leads × MQL→Opp × Win-rate × ACV)
    - Churned ARR (= Beginning ARR × Gross logo churn × ACV-weighted churn factor)
    + Expansion ARR (= Beginning ARR × NRR uplift)
```

Subdivide by segment (SMB / MM / Ent) and / or product if mix shifts materially.

Recognized revenue ≠ ARR. Bridge them:

```
GAAP Rev (period) = (Beginning ARR × period fraction) + Σ(New ARR contracts × pro-rata recognition)
```

### Usage-based / consumption

```
Revenue = Customers × Usage-per-customer × Price-per-unit
```

Three independent drivers, three independent assumptions, three independent sensitivities.

### Marketplace / transaction

```
GMV = Buyers × Transactions-per-buyer × AOV
Revenue = GMV × Take-rate
```

### Services / project

```
Revenue = Heads × Utilization × Bill-rate × Realization × Hours-available
```

### Retail / multi-location

```
Revenue = Stores × Same-store-sales × Mix-effect
        + New-store revenue (cohort-based — Year 1, 2, 3+ stores ramp differently)
```

If the business has more than one engine (e.g., SaaS + services), forecast each separately and roll up. Don't blend.

## Opex: category-driver pairing

For each opex line, name the driver that should move it. If the driver doesn't change, the line shouldn't either.

| Opex category | Natural driver |
|---|---|
| Sales comp | Heads × OTE × attainment |
| Sales non-comp (T&E, tooling) | Heads × $/head |
| Marketing programs | Programs budgeted (or % of New ARR target) |
| R&D comp | Heads × loaded cost |
| Hosting / infra | Active customers (or GB-hr, or transactions) — usage-paced |
| G&A comp | Heads × loaded cost |
| Rent | Locations × $/sqft × sqft |
| Professional services | Project-driven; flat or named-engagement |
| Insurance / D&O | Revenue × rate (insurers price on rev) OR flat |

**Anti-pattern:** "Other G&A grows 8%." That's not a driver, that's a confession.

## Working capital roll

Three lines do most of the work:

```
Accounts receivable = Revenue × DSO / 365
Inventory = COGS × DIO / 365
Accounts payable = COGS × DPO / 365
```

The forecasted change in NWC flows to cash. If DSO is rising (collections slipping), the cash story is worse than the P&L. Always.

Subscription / prepaid businesses also model **deferred revenue**:

```
Deferred revenue (BS) = Sum of unrecognized billings
Change in deferred revenue = Billings - Recognized revenue
```

Cash from operations gets a boost when deferred revenue grows (cash before recognition) and a drag when it shrinks.

## Capex + depreciation

Capex schedule by category:

| Category | Useful life | Drives |
|---|---|---|
| Computer equipment | 3 yr | Headcount × $/head |
| Office furniture / FF&E | 5 yr | Locations × $/sqft × sqft |
| Leasehold improvements | Lease term | New locations |
| Capitalized software (internal-use) | 3-5 yr | R&D headcount × % capitalizable |
| Capitalized R&D (where allowed) | 3-7 yr | R&D opex × cap rate |

Depreciation flows from a roll-forward of gross PP&E by category, not from a single number.

## The 3-statement integration check

A forecast is not a forecast until the three statements tie:

1. **Income statement** → Net income flows to retained earnings
2. **Balance sheet** → Assets = Liabilities + Equity in every forecast period
3. **Cash flow** → Beginning cash + CFO + CFI + CFF = Ending cash (matches BS)

If BS doesn't balance in any forecast period, the model is broken. Add an explicit **BS_check** row (=Assets − Liabilities − Equity) that should always read 0 or near-zero (rounding only). When it breaks, the most common causes:

1. A revenue driver flows to P&L but not to AR
2. Capex flows to PP&E but depreciation doesn't flow back to accumulated depreciation
3. Stock-based comp flows to P&L but not to APIC
4. FX translation differences not booked to OCI / CTA

## Scenarios

Three scenarios, always: **Base**, **Upside**, **Downside**. Sometimes a **Stress** for lender / covenant work.

Build scenarios as **driver overrides**, not as separate models. A `Scenario` switch in the inputs tab toggles between driver-value columns. Reviewers compare scenarios side-by-side without re-running anything.

What makes scenarios honest:

- Each scenario names which **2-3 drivers** moved and how
- Each scenario has a **probability weighting** (e.g., 60 / 25 / 15) — even rough probabilities discipline the exercise
- The **delta to base case** is shown in $ and % for every key KPI

**Anti-pattern:** "Downside = base × 0.7." That's not a scenario, it's a discount. Name the drivers.

## Sensitivity tables

Two-variable sensitivities on the highest-stakes outputs:

- ARR end of year vs. (rep hiring, productivity)
- EBITDA margin vs. (revenue growth, marketing spend as % rev)
- Cash runway vs. (revenue growth, opex growth)
- Free cash flow vs. (NWC days, capex intensity)

Spreadsheet data-table feature handles these natively. Keep them on a dedicated tab.

## The variance loop

Every forecast feeds the variance commentary downstream. Build with that in mind:

- Tag every driver with a category that maps to variance-commentary buckets (Revenue → Volume / Price / Mix; Opex → Comp / T&E / Programs / Other)
- Lock the prior-period forecast as a frozen baseline; do not overwrite when refreshing
- Each refresh produces three columns: Actuals, Latest forecast, Prior forecast — variance commentary explains both Actual vs. Forecast AND Latest vs. Prior

See [`../variance-commentary/SKILL.md`](../variance-commentary/SKILL.md) for the downstream commentary discipline.

## Forecast hygiene checklist

Before declaring a forecast refresh done:

- [ ] Every driver has a documented assumption with a source and a date
- [ ] Revenue rolls up to total (segment / product check)
- [ ] BS balances in every forecast period (BS_check row)
- [ ] CF ties to BS cash change (CF_check row)
- [ ] Scenario switch produces different outputs without formula changes
- [ ] Sensitivity tables refresh cleanly
- [ ] No hardcoded numbers buried in formulas (search for `*0.21`, `*1.05` etc.)
- [ ] Documentation tab updated with refresh date, owner, what changed since last version
- [ ] Variance commentary against prior forecast drafted for material changes
- [ ] Reviewer signed off (a forecast without a reviewer is informal)

## Common failure modes

- **Top-down growth rates with no driver decomposition** — "Revenue grows 25%" tells the reader nothing. Decompose it.
- **Hiring plan disconnected from revenue model** — sales-rep hiring should drive New ARR; non-quota hiring should drive opex. If they live on different tabs and don't talk, the model is two models.
- **Working-capital ignored** — many SMB models forecast P&L only and assume cash follows. It doesn't, especially in growing or cyclical businesses.
- **Optimistic ramp assumptions** — "New reps are productive in month 3" is the most consistently-wrong assumption in SaaS forecasts. Benchmark against actuals; usually 6-9 months full ramp.
- **Plug** — when BS doesn't balance and a "plug" line is inserted to make it tie. Never. Find the missing flow.
- **One-scenario model** — without alternates, the model is a wish.
- **No probability weighting on scenarios** — without a P-weight, the user defaults to Base, which is almost always the optimistic case in disguise.

## See also

- Skill: [`../model-review/SKILL.md`](../model-review/SKILL.md) — 7-pass review every model goes through before ship
- Skill: [`../variance-commentary/SKILL.md`](../variance-commentary/SKILL.md) — the downstream commentary discipline
- Skill: [`../thirteen-week-cash-forecast/SKILL.md`](../thirteen-week-cash-forecast/SKILL.md) — direct cash forecast (different mechanic)
- Template: [`../../templates/cash-flow-forecast.md`](../../templates/cash-flow-forecast.md)
- Template: [`../../templates/model-documentation.md`](../../templates/model-documentation.md)
- Agent: [`../../agents/fpa-analyst.md`](../../agents/fpa-analyst.md)
- Agent: [`../../agents/financial-modeler.md`](../../agents/financial-modeler.md)
