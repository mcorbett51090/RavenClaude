# Payroll Tax and Fringe Are a Budget Line, Not a Rounding Error

**Status:** Absolute rule
**Domain:** Film & video production — budgeting
**Applies to:** `film-video-production`

---

## Why this exists

Payroll tax and fringe benefits are not a footnote — on a union production they typically add 25–35% on top of direct labor cost, and on a non-union production still add 15–20% in employer taxes alone. [unverified — training knowledge] A budget that states crew and cast day rates without building in payroll tax and fringe understates below-the-line labor cost by 20–35%, which is the single most common source of first-week budget shock on productions new to the line-item build approach. Fringe on a $200k below-the-line labor spend is $40–70k — not a rounding error, a major budget category.

## How to apply

**Components to budget explicitly:**

| Component | Typical Rate (US, non-union) | Typical Rate (US, union — IATSE/SAG) | Notes |
|---|---|---|---|
| Federal FICA (OASDI + Medicare) | 7.65% of wages | 7.65% | Hard floor — applies to all W-2 crew |
| Federal FUTA | 0.6% of first $7k/employee | 0.6% | Often small; model it |
| State unemployment (SUI) | 2–5% (varies by state) | 2–5% | Check the shoot state, not the production's home state |
| Workers' comp | 3–8% (varies by class) | Varies | Camera/grip class codes differ from office/PA |
| Union H&W (Health & Welfare) | — | $6–$9/hr (IATSE — verify current) | Check current IATSE BPA; rates change each agreement |
| Union pension | — | 7.5–8.5% of scale (IATSE) | Check current BPA |
| Payroll company fee | 1–2% of gross | 1–2% of gross | If using a third-party payroll company (Entertainment Partners, Media Services, etc.) |

**How to model in the budget:**

```
Below-the-Line labor (direct):         $180,000
Payroll tax & fringe rate applied:         +28%    ← build this as a percentage line
Payroll tax & fringe cost:              $50,400
Total BTL labor (gross):               $230,400
```

Use a separate fringe account number (e.g., Acct 3300 in a standard production budget) so the rate is visible and auditable.

**Do:**
- Set the fringe rate before the first budget draft, not as a final-line adjustment.
- Confirm the applicable rate with your payroll company — IATSE rates, SAG residual schedules, and state SUI rates all move.
- Differentiate the rate for union vs. non-union crew in the same budget (e.g., union camera, non-union PA).

**Don't:**
- Use a blended fringe rate for both union and non-union crew — the difference is 10+ points.
- Apply the fringe rate to per diems and box rentals — fringe applies to wages, not allowances.
- Omit the payroll company fee — on a $500k budget it's $5–10k that won't appear anywhere else.

## Edge cases / when the rule does NOT apply

Loan-out companies (cast and above-the-line talent who bill through their own loan-out corporations) do not carry the same FICA/FUTA/SUI burden on the production — the loan-out's employer of record handles it. Confirm with your payroll company which W-2 vs. loan-out agreements apply for each hire before setting the fringe rate.

## See also
- [`../agents/line-producer.md`](../agents/line-producer.md) — owns the below-the-line build including the fringe model.
- [`../agents/production-finance-analyst.md`](../agents/production-finance-analyst.md) — tracks payroll actuals against the fringe budget in the weekly cost report.

## Provenance

Codifies standard US production budgeting practice; specific rates are [unverified — training knowledge] and must be verified against current IATSE BPAs, SAG agreements, state SUI schedules, and the production's payroll company.

---

_Last reviewed: 2026-06-05 by `claude`_
