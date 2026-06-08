---
description: "Run a merchandising and assortment analysis: evaluate category health via GMROI, design or audit a planogram for space-to-sales alignment, build a sell-through-triggered markdown ladder, or define an assortment architecture (depth vs. breadth, role by SKU, private label vs. national brand)."
---

# Merchandising and Assortment

**Purpose:** produce a data-grounded assortment or planogram recommendation — one where every
shelf-foot and every SKU is justified by GMROI, sell-through, and space-productivity math.

---

## Entry-point playbook

### Step 1 — Establish the baseline

Before recommending any change, gather:

| Input | Why it matters |
|---|---|
| Current sell-through rate (units sold ÷ units received) | Tells you if the inventory is moving |
| Weeks-of-supply (on-hand units ÷ avg weekly sales) | Tells you how long the inventory lasts |
| Gross margin % by SKU / category | Input to GMROI |
| Average inventory at cost | The denominator of GMROI |
| Sales/linear-foot or sales/sqft by SKU / section | Space-productivity signal |
| Planogram compliance % (if an audit is in scope) | Revenue proxy |

If any input is missing, flag it explicitly — a recommendation without a sell-through rate is an
opinion.

### Step 2 — Calculate GMROI

```
GMROI = (Gross Margin $) ÷ (Average Inventory at Cost)
```

- **GMROI < 1.0:** the category is destroying capital (returns less in margin than the cost of
  the inventory tied up).
- **GMROI 1.0–2.0:** marginal. Consider space reallocation unless strategic (traffic driver).
- **GMROI > 2.0:** healthy. Protect and potentially expand.
- **GMROI > 3.5:** star category. Prioritize assortment depth, planogram position, and in-stock.

Use [`../../scripts/retail_calc.py`](../../scripts/retail_calc.py) `gmroi` mode to confirm arithmetic.

### Step 3 — Space-to-sales alignment

Rank SKUs by sales/linear-foot. Compare actual shelf allocation to rank.

- Over-spaced slow movers: reduce space allocation; reallocate to high-velocity SKUs.
- Under-spaced fast movers: expand space; flag replenishment frequency impact.
- Dead-space holders (< 0.5× category average): candidates for exit or substitution.

### Step 4 — Markdown-or-hold decision

Traverse the markdown-or-hold tree in
[`../../knowledge/retail-store-operations-decision-trees.md`](../../knowledge/retail-store-operations-decision-trees.md):

1. What is the current sell-through rate vs. the season target at this point in the season?
2. How many weeks remain in the selling season?
3. What is the weeks-of-supply on hand?
4. Is the item seasonal/perishable (hard deadline) or evergreen (no hard deadline)?

Output: reorder / hold / mark-down now / accelerate markdown / liquidate.

### Step 5 — Planogram compliance audit (if in scope)

1. Photograph or survey the fixture vs. the planogram PDF.
2. Score compliance by: correct SKU in correct slot, correct facing count, correct height/depth,
   correct adjacency, correct signage.
3. Rank stores or sections by compliance score.
4. Root-cause low compliance: reset not completed, facing count wrong, SKU substitution, fixture
   incompatibility.

### Step 6 — Output artifact

Use [`../../templates/planogram-brief.md`](../../templates/planogram-brief.md) to structure the
deliverable. Include: GMROI by category, sell-through and WOS inputs, space-to-sales
alignment table, planogram compliance score (if audited), and the explicit decision (reorder /
hold / mark down / exit) with rationale.

---

## Anti-patterns

- A markdown decision with no sell-through rate or weeks-of-supply input.
- GMROI calculated without average inventory at cost (using retail value overstates the return).
- Space allocated by buyer preference or vendor negotiation without a sales/linear-foot check.
- A planogram compliance score without a root-cause breakdown.
- Category expansion recommended based on gross margin % alone.

---

## Output

A merchandising deliverable from this skill always contains:

1. **GMROI table** (or explicit flag that inputs are missing).
2. **Sell-through and WOS** at the time of the recommendation.
3. **Space-to-sales alignment** (or planogram compliance score).
4. **Decision:** reorder / hold / mark down / exit — with the markdown ladder if applicable.
5. **Handoff flags:** inventory-and-replenishment-analyst if a replenishment change is needed;
   store-ops-lead if the category change has a material four-wall impact.
