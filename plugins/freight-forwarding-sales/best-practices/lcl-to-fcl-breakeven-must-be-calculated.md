# Calculate the LCL-to-FCL break-even before recommending a mode

**Status:** Absolute rule
**Domain:** Mode selection / quoting
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

Defaulting to LCL for a 12 CBM shipment without running the FCL comparison can cost the customer 20–40% more than a 20' FCL on the same lane — and it costs the forwarder a mode upsell, a stronger margin product, and a faster, lower-risk shipment. Conversely, recommending FCL for a 4 CBM shipment wastes the customer's money on empty container space. The LCL-to-FCL break-even is a simple, fast calculation that should be automatic before any mode recommendation is committed to in writing.

## How to apply

**The break-even formula:**

The LCL-to-FCL break-even point is where:

```
FCL all-in sell price = LCL all-in sell price per W/M × break-even CBM
```

Rearranged:

```
Break-even CBM = FCL all-in sell price ÷ LCL all-in sell price per W/M
```

**Example (worked):**

| Item | Value |
|---|---|
| FCL 20' all-in sell (ocean + THC both ends + BAF + documentation) | USD 2,400 |
| LCL all-in sell rate per W/M | USD 55/W-M |
| Break-even = 2,400 ÷ 55 | **43.6 W/M ≈ 43.6 CBM** |

At 43.6 CBM, cost is equal. Below that, LCL is cheaper per unit. Above that, FCL is cheaper. For this lane, a 45 CBM shipment should move as FCL.

**The industry-wide heuristic** is approximately 13–15 CBM (roughly half a 20') as the LCL/FCL break-even — but **calibrate to your actual lane rates**. On high-rate lanes (e.g. transpacific during a GRI) the break-even shifts significantly lower; on short-sea low-rate lanes it may shift higher.

**Also consider (not just cost):**
- **Transit time**: FCL is typically 1–4 days faster on most lanes (no CFS consolidation/deconsolidation dwell).
- **Risk**: LCL co-loads with other cargo — contamination, damage, and customs-hold risk affects the whole consolidation.
- **Visibility**: FCL is easier to track box-to-box; LCL visibility gaps at the CFS are common.
- **Cargo type**: high-value, hazmat, temperature-sensitive, or oversized cargo should generally avoid LCL even below the cost break-even.

**Do:**
- Run the break-even calculation before recommending LCL for any shipment above 8 CBM.
- Show the customer the comparison — a seller who runs the math earns trust.
- Use `scripts/freight_calc.py ocean` to confirm the CBM and W/M basis; then compare against the FCL quote from `scripts/freight_calc.py quote`.

**Don't:**
- Use "approximately 14 CBM" as a universal rule without checking the actual lane rates — the heuristic is a starting point, not the answer.
- Recommend FCL to upsell margin without confirming the customer actually benefits (the all-in must be cheaper or the service advantage must be clear).
- Skip the risk/transit comparison — a cost-equal scenario may still favour FCL if cargo type or transit urgency applies.

## Edge cases / when the rule does NOT apply

For dedicated project cargo, hazmat, or temperature-controlled shipments, the mode choice is determined by cargo requirements before cost — the break-even is still computed but may be overridden. For express/integrator courier (small parcels), the LCL/FCL comparison does not apply.

## See also
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — all-in quote builder
- [`../agents/trade-lane-compliance-advisor.md`](../agents/trade-lane-compliance-advisor.md) — mode selection logic
- [`../knowledge/freight-sales-decision-trees.md`](../knowledge/freight-sales-decision-trees.md) — mode selection decision tree

## Provenance

Codifies `freight-rate-quoter`'s and `trade-lane-compliance-advisor`'s mode selection discipline. The W/M comparison is the standard LCL billing basis. Break-even methodology is standard freight-forwarding commercial practice.

---

_Last reviewed: 2026-06-05 by `claude`_
