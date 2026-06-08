# Retail Store Operations — Decision Trees

_Decision trees + a dated metric/formula map. Formula rows are `[verify-at-build]` — re-check the definition (numerator, denominator, window) against the consumer's reporting before quoting. Last reviewed: 2026-06-08._

Traverse before marking down aged inventory, committing a buy against open-to-buy, diagnosing a shrink leak, re-shaping labor against a labor-% miss, or calling an inventory position "healthy".

## Decision Tree: Mark it down now, or hold?

Markdown clears trapped cash; holding bets on demand returning. The first markdown is usually the cheapest.

```mermaid
graph TD
  A[Aged / seasonal / slow SKU] --> B{Sell-through tracking to plan for this point in the life-cycle?}
  B -- Yes --> C[Hold - it is selling at plan; do not give away margin]
  B -- No --> D{Weeks-of-supply above the terminal threshold for the season left?}
  D -- No --> E[Hold but watch - re-check next cycle; set the trigger]
  D -- Yes --> F{Is the item seasonal / terminal with a hard end date?}
  F -- Yes --> G[Mark down now on a step-down cadence - first markdown shallow, escalate to terminal clearance]
  F -- No, replenishable --> H{Is the slow sell-through an assortment problem, not a price problem?}
  H -- Yes --> I[Route to merchandising-analyst - cut/relocate before discounting a structurally wrong SKU]
  H -- No --> J[Take the first markdown - depth compounds with time; a late markdown clears deeper and carries more weeks of cost]
```

_Trigger markdowns on sell-through + weeks-of-supply, not on the calendar alone. The first markdown is the cheapest; waiting trades a shallow cut now for a deep one later plus carrying cost._

## Decision Tree: Replenish the buy, or stop at the open-to-buy cap?

Open-to-buy is the budget; over-buying pre-commits the markdown.

```mermaid
graph TD
  A[Want to buy / reorder more] --> B{Computed OTB = planned sales - planned markdowns + target ending inventory - on-hand - on-order. Is OTB positive?}
  B -- No, OTB exhausted or negative --> C[Stop - you are over-bought; buying more pre-commits a markdown. Re-plan or clear first]
  B -- Yes --> D{Is current weeks-of-supply below target for this SKU/store?}
  D -- No --> E[Do not replenish this store - reallocate from an overstocked store instead; aggregate looks fine, the store-SKU does not]
  D -- Yes --> F{Is the reorder within the safety-stock + service-level model?}
  F -- No, ad-hoc --> G[Size it: reorder point + replenishment qty against a NAMED service level and lead-time variability]
  F -- Yes --> H{Vendor lead time / MOQ / terms known?}
  H -- No --> I[Route to procurement-sourcing for lead time + MOQ before committing the buy]
  H -- Yes --> J[Replenish to the reorder point within OTB - record the service level and the trapped-cash trade]
```

_OTB caps forward commitment; weeks-of-supply decides whether THIS store needs it; the service level sizes the buffer. Aggregate availability is a comforting lie during a stockout — always drill to store-SKU._

## Decision Tree: Where is the shrink leaking?

Shrink is a diagnosable leak, not a fixed cost. Split the gap before you spend the loss-prevention budget — most shrink is operational, and cameras are the wrong fix for a receiving error.

```mermaid
graph TD
  A[Shrink % above plan = book inventory - physical inventory, valued, over sales] --> B{Is the gap concentrated in specific SKUs/categories or spread evenly?}
  B -- Concentrated in high-value / easily-concealed items --> C{Pattern points to theft - internal or external?}
  C -- Internal: voids, refunds, employee-adjacent timing --> D[Loss-prevention + cash/refund SOP discipline - route employee surveillance / PII to security-reviewer]
  C -- External: open-floor high-theft SKUs --> E[Physical controls + LP coverage on the concentrated SKUs - cheapest control that fits the pattern]
  B -- Spread evenly across receiving / markdown / damage --> F{Do receiving counts, markdown execution, and damage logs reconcile?}
  F -- No, process gaps --> G[OPERATIONAL leak - fix receiving / markdown-execution / count SOPs FIRST; this is the cheapest and most common cause]
  F -- Yes, process clean --> H{Do vendor receipts match POs - short ships, price/scan error?}
  H -- No, vendor mismatch --> I[VENDOR/ADMIN leak - file a vendor claim; route cost/terms to procurement-sourcing]
  H -- Yes --> J[Re-audit the physical count itself before spending on any control - the gap may be a counting error]
```

_Quantify each bucket's share (operational vs. theft vs. vendor/admin) before prescribing a control. Treating all shrink as theft mis-spends the LP budget on the wrong leak; most shrink is operational._

## Decision Tree: Labor % over plan — re-shape or cut heads?

Labor follows traffic, not a flat grid. Labor % over plan is usually a scheduling-shape problem before it's a headcount problem.

```mermaid
graph TD
  A[Labor % over plan = store labor $ / store sales] --> B{Is sales tracking to plan, or is the denominator the problem?}
  B -- Sales below plan --> C[Labor % is a SALES miss wearing a labor costume - protect peak conversion before any labor cut; cutting peak labor to make the % craters sales further]
  B -- Sales at/above plan, labor $ over --> D{Is the schedule shaped to the conversion-weighted traffic curve?}
  D -- No, flat grid --> E[RE-SHAPE first: move hours OUT of dead hours INTO the peak; usually recovers labor % with no headcount cut and protects conversion]
  D -- Yes, already traffic-shaped --> F{Is the peak still under-staffed for conversion, or is total headcount genuinely above need?}
  F -- Peak under-staffed --> G[Do NOT cut - the lost conversion is invisible on the labor report but real on the sales line; add peak coverage]
  F -- Genuine over-headcount in all dayparts --> H[Now a headcount conversation - cut from the dead hours, never the peak; name the labor-% vs. conversion trade on the change]
```

_Over-staffing the dead hours wastes labor %; under-staffing the peak loses conversion — and conversion loss is invisible on the labor report. Name which one every schedule change trades on._

## Decision Tree: Reading the inventory vital signs

Judge inventory by sell-through %, weeks-of-supply, and GMROI — never raw on-hand units. The flow lens and the capital lens answer different questions; read both.

```mermaid
graph TD
  A[Is this inventory position healthy?] --> B{First normalize: what is weeks-of-supply = on-hand / avg weekly demand? State the window}
  B -- WOS far above target --> C{Is sell-through tracking to the life-cycle plan?}
  C -- No --> D[OVERSTOCKED + slow - markdown / reallocate by WOS; check assortment vs. price before discounting]
  C -- Yes --> D2[Healthy demand but heavy position - watch WOS; do not replenish until it draws down]
  B -- WOS far below target --> E[At stockout risk - replenish to a WOS target within OTB; size safety stock to a NAMED service level]
  B -- WOS in band --> F{Does GMROI clear the 1.0 capital floor?}
  F -- No, GMROI below 1.0 --> G[Turns fine but does NOT earn its carrying cost - trapped capital; re-mix / cut before buying deeper, even though flow looks OK]
  F -- Yes --> H[Healthy on BOTH lenses - right flow AND earns its capital; hold and re-check next cycle]
```

_WOS and sell-through answer "is the flow right?"; GMROI answers "is the capital earning?". A position can pass one and fail the other — fast-turning low-margin inventory can still flunk GMROI. Never declare inventory "fine" on raw on-hand units._

---

## Metric / formula map (2026, `[verify-at-build]`)

| Metric | Working definition | Notes |
|---|---|---|
| Sell-through % | units sold ÷ units received (over a window) × 100 | Always state the window; "sell-through" with no period is ambiguous `[verify-at-build]` |
| Weeks-of-supply (WOS) | on-hand units ÷ average weekly demand | The inventory truth-teller; normalizes on-hand to the demand rate `[verify-at-build]` |
| GMROI | gross margin $ ÷ average inventory cost | "Does this inventory earn its carrying cost?" — the capital-efficiency lens `[verify-at-build]` |
| Inventory turns | COGS ÷ average inventory (at cost) | Turns and WOS are reciprocals of the same flow `[verify-at-build]` |
| Open-to-buy (OTB) | planned sales − planned markdowns + planned ending inventory − (on-hand + on-order) | The forward-buy budget; usually in retail $ at a category/month level `[verify-at-build]` |
| Safety stock | f(demand variability, lead-time variability, target service level) | Sized to a NAMED service level; e.g. z·σ over lead time — state the z / service target `[verify-at-build]` |
| Comp / same-store sales | sales from stores open ≥ ~12 months, period vs. like period | Excludes new/closed stores; the organic-growth read `[verify-at-build]` |
| Labor % (of sales) | store labor $ ÷ store sales × 100 | The controllable lever scheduled against the traffic curve `[verify-at-build]` |
| Conversion | transactions ÷ traffic (door counter) | Sales = traffic × conversion × basket; protect at peak `[verify-at-build]` |
| Shrink % | (book inventory − physical inventory) value ÷ sales × 100 | Split operational vs. theft (internal/external) vs. vendor/admin `[verify-at-build]` |

_Reference: every metric is ambiguous until you state the numerator, denominator, and window. GMROI and turns answer "is this inventory earning?"; WOS and sell-through answer "is the flow right?"; OTB answers "can we buy more?". Re-verify any definition against the consumer's reporting system before defending a decision on it — definitions drift between retailers._
