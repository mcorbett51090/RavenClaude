# Segment ABC/XYZ before you set inventory policy

**Status:** Pattern
**Domain:** Inventory policy
**Applies to:** `supply-chain-planning`

---

## Why this exists

A single inventory policy for all SKUs destroys value at both ends of the portfolio:

- **Over-serving slow, erratic movers (C/Z):** high safety stock on items with low demand and
  high variability ties up capital in items that may obsolesce before they sell. A C/Z SKU often
  belongs in make-to-order, not with a standing safety-stock buffer.
- **Under-serving fast, high-value movers (A/X):** without a segmented policy, A/X SKUs compete
  for the same generic "30 days of safety stock" as C/Z SKUs — and often lose out to policy
  averages that are too low for the service level the customer expects.

The two-axis segmentation separates the problem:
- **ABC** (Pareto by revenue or volume): identifies where inventory dollars have the most impact.
- **XYZ** (coefficient of variation CV = σ/μ): identifies which SKUs can be forecast reliably
  and which are driven by erratic demand that a statistical model cannot capture.

The nine-cell matrix then routes each cell to the appropriate replenishment mechanism and
safety-stock philosophy.

## How to apply

1. Calculate ABC: sort SKUs by annual revenue (or volume) descending. Cumulative top ~70% = A,
   next ~20% = B, bottom ~10% = C. Adjust thresholds to the business.
2. Calculate XYZ: compute CV = σ/μ for each SKU's demand history. CV ≤ 0.5 = X; 0.5–1.0 = Y;
   > 1.0 = Z.
3. Traverse `## Decision Tree: Inventory-policy selection` in the knowledge bank to assign the
   policy per cell.
4. Review the matrix at least annually — SKUs migrate between cells as demand patterns change.

**Do:**

- Segment before any safety-stock or service-level calculation.
- Use CV to detect intermittent demand early — Z-class SKUs often belong in Croston-method
  forecasting and MTO or minimal-stock policies.
- Set differentiated service-level targets per cell (A/X high CSL; C/Z low or MTO).
- Review the segmentation annually or when the product portfolio changes materially.

**Don't:**

- Apply a uniform days-of-supply target across all 10,000 SKUs.
- Skip segmentation because the portfolio is "too large" — the calculation is straightforward
  in a spreadsheet or any planning tool.
- Treat the ABC/XYZ matrix as permanent — demand patterns drift and so do the cells.

## Edge cases / when the rule does NOT apply

If the portfolio is fewer than ~50 SKUs with similar demand character and similar costs, the
segmentation gain is minimal. Set a uniform policy, review it quarterly, and revisit segmentation
when the portfolio grows. The principle (not all SKUs are the same) still applies even informally.

## See also

- [`./safety-stock-covers-variability-not-the-average.md`](./safety-stock-covers-variability-not-the-average.md) — sizing safety stock per segment.
- [`./service-level-is-a-deliberate-choice-with-a-cost.md`](./service-level-is-a-deliberate-choice-with-a-cost.md) — setting targets per segment.
- [`../skills/inventory-policy-and-safety-stock/SKILL.md`](../skills/inventory-policy-and-safety-stock/SKILL.md) — full workflow.

## Provenance

APICS/ASCM CPIM body of knowledge; Flores & Whybark (1986) ABC/XYZ classification; Syntetos,
Boylan & Croston (2005) on intermittent demand classification. Standard practitioner technique in
every major APS platform.

---

_Last reviewed: 2026-06-08 by `claude`._
