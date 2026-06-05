# Document every model assumption with a source and a review date

**Status:** Absolute rule
**Domain:** Financial modeling
**Applies to:** `finance`

---

## Why this exists

An undocumented assumption is one that cannot be challenged, updated, or defended six months later when the model is reused. Assumptions go stale the moment they are made: growth rates shift, tax laws change, market comps reprice. A model that carries assumptions without sources and dates appears authoritative while silently becoming wrong. When a board, lender, or acquirer asks "where did 8% WACC come from?", "we used it last time" is not an answer. The documentation tab is the chain of custody for every input that drives the output.

## How to apply

Every model's Assumptions tab (or equivalent Documentation sheet) must carry, for each material assumption:

| Assumption | Value | Source | Source Date | Owner | Review Due |
|---|---|---|---|---|---|
| Revenue growth — Year 1 | 22% | Management plan + FP&A driver build | 2026-01-15 | FP&A Lead | 2026-07-01 |
| Terminal growth rate | 2.5% | Long-run nominal GDP + company-specific discount | 2026-03-01 | Valuation Analyst | 2026-09-01 |
| Risk-free rate | 4.3% | 10-yr UST yield, Bloomberg, 2026-03-15 | 2026-03-15 | Valuation Analyst | Next DCF build |
| Tax rate — effective | 21% | Prior 3-year average ETR; confirm with tax counsel | 2025-12-31 | Controller | Annually |

**Materiality threshold for assumption documentation:** any input whose ±10% change moves the model's primary output metric by more than 2% should be documented with a source. Below-threshold inputs may use a grouped note ("standard market-rate assumptions").

**Do:**
- Link or cite the primary source (Bloomberg date, management memo, audited filing) — not "common sense" or "industry standard."
- Set a review-due date for volatile inputs (rate assumptions, commodity prices, headcount costs) — not just a version date.
- Include a `Changed from prior version` row for any assumption that was updated, showing the old value, new value, and reason.

**Don't:**
- Write "assumed" or "per team discussion" as a source — name the document and the date.
- Leave market-rate assumptions undated; a WACC pulled from a source six months old may be materially wrong.
- Treat the documentation tab as an afterthought to be filled in before the deliverable ships — build it as you go.

## Edge cases / when the rule does NOT apply

Quick sensitivity analysis ("what if growth is 5% instead of 10%?") in a working session does not require formal documentation. But if the sensitivity output is sent to a stakeholder, a cover note stating "inputs are working assumptions, not audited" is required, and any assumption that feeds a board-pack or lender deliverable must be documented before it ships.

## See also

- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — owns the model-documentation standard and the seven-pass review.
- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — WACC and terminal-value assumptions are especially sensitive to staleness.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — the rule that forces all inputs into one sheet where this documentation lives.

## Provenance

Codifies house opinion #11 ("models age — every model carries a model-documentation.md with version, assumptions, last refresh date, and an owner") and the `model-review` skill's 7-pass review requirement for an Assumptions pass. Documentation-tab discipline is a standard Big-4 financial-modeler requirement and an M&A due-diligence prerequisite.

---

_Last reviewed: 2026-06-05 by `claude`_
