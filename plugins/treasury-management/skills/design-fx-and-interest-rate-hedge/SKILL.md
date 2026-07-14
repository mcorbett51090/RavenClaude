---
name: design-fx-and-interest-rate-hedge
description: "Design an FX or interest-rate hedge by traversing the treasury decision tree (scope the exposure: transaction vs translation vs economic → decide hedge-vs-accept → set hedge ratio & horizon → choose the instrument: forward/swap/option/collar → set the hedge-accounting stance: ASC 815 / IFRS 9, cash-flow vs fair-value), then return whether to hedge, how much and how long, the instrument, the accounting designation with documentation/effectiveness, and the conditions that flip it. Reach for this when the user asks 'should we hedge this FX/rate exposure?', 'forward or option or collar?', 'what hedge ratio?', 'cash-flow or fair-value hedge?', or 'do we need hedge accounting?'. 'Do nothing' is a valid output. Used by treasury-strategy-lead (policy) and cash-and-risk-operations-specialist (execution)."
---

# Skill: design-fx-and-interest-rate-hedge

> **Invoked by:** `treasury-strategy-lead` (the hedge-policy / risk-management-policy design) and `cash-and-risk-operations-specialist` (the execution + hedge-accounting setup against a designated exposure).
>
> **When to invoke:** "should we hedge this FX / interest-rate exposure?"; "forward, swap, option, or collar?"; "what hedge ratio and horizon?"; "cash-flow or fair-value hedge?"; "do we need hedge accounting (ASC 815 / IFRS 9)?"; any "how do we protect against this rate/currency move?" question.
>
> **Output:** the hedge-vs-accept decision + hedge ratio & horizon + the instrument + the hedge-accounting designation (cash-flow vs fair-value, with documentation & effectiveness) or a governed *accept* + the 1-2 flip conditions. **"Do nothing" is a legitimate result.**

## Procedure

1. **Scope the exposure precisely — you can't hedge what you can't measure.** Classify it: **transaction** (a contracted cash flow in a foreign currency, or a floating-rate coupon — a real, datable cash exposure), **translation** (the reporting-currency value of a foreign subsidiary's net assets on consolidation — an equity/OCI, non-cash exposure), or **economic / operating** (competitive exposure to rates/FX that isn't a single contracted flow). The class drives everything downstream.
2. **Decide hedge-vs-accept — "do nothing" is on the menu.** Traverse the hedge branch in [`../../knowledge/treasury-management-decision-tree.md`](../../knowledge/treasury-management-decision-tree.md): hedge when the exposure is **material, measurable, and adverse-volatility matters** to covenants/earnings/cash. **Accept (do nothing)** when it's immaterial, naturally offset (a matching opposite exposure), un-hedgeable at reasonable cost, or where the hedge cost exceeds the risk reduced. Translation exposure especially is often a governed *accept* — hedging equity translation burns cash to smooth a non-cash line.
3. **Set the hedge ratio and horizon.** Rarely 100% and rarely a single date — hedge a **percentage** of the exposure (often layered/laddered: more of the near, less of the far) over a **horizon** matched to the exposure's certainty (highly-probable forecast flows can be hedged further out; speculative ones cannot). The ratio and horizon are the policy's core dials.
4. **Choose the instrument for the payoff you want.**
   - **Forward** — locks a rate for a known FX flow; zero upfront cost, but gives up favorable moves (an obligation). The default for a certain transaction exposure.
   - **Swap** — exchanges one rate/currency stream for another; the workhorse for **interest-rate** exposure (fixed↔floating) and cross-currency funding.
   - **Option** — buys protection while keeping the upside; costs a premium. For uncertain flows or when the upside has real value.
   - **Collar** — buy a protective option, sell one to fund it; caps cost by giving up part of the upside. A common premium-reduced middle ground.
5. **Set the hedge-accounting stance deliberately — it's a cost, not a default.** Decide whether to seek **hedge accounting** under **ASC 815 (US GAAP)** / **IFRS 9**:
   - **Cash-flow hedge** — for a variable/forecast exposure (a future FX flow, a floating-rate coupon); the effective gain/loss parks in **OCI** and releases to P&L when the hedged item hits earnings. Smooths P&L volatility.
   - **Fair-value hedge** — for a fixed exposure whose fair value moves (fixed-rate debt vs rates); both the hedge and the hedged item are marked through **P&L**.
   - Either requires **contemporaneous documentation** at inception (the exposure, the instrument, the risk, the effectiveness method) and ongoing **effectiveness** assessment. If that cost isn't worth the P&L smoothing, book it as an **economic hedge through P&L** — a valid choice, just disclose the earnings volatility.
6. **State the flip conditions** — the 1-2 facts that change the design (e.g., "if the forecast flow drops below 'highly probable', cash-flow-hedge designation is lost and it goes through P&L"; "if rates are expected to fall, a collar/option beats a locked forward"; "if the exposure becomes immaterial, the answer flips to accept").

## Worked example

> User: "We're a USD-functional company with €10M of highly-probable EUR revenue over the next 12 months. Hedge it? How?"

- **Exposure:** **transaction** (a datable, highly-probable foreign-currency cash inflow) — material and measurable.
- **Hedge-vs-accept:** the EUR/USD move directly hits USD revenue and it's forecastable → **hedge**, but not 100% (it's a forecast, not contracted).
- **Ratio & horizon:** **layer** it — e.g. 75% of the near two quarters, 50% of quarters 3-4, declining as certainty falls; horizon 12 months.
- **Instrument:** **forward** for the certain near layers (zero premium, locks the rate); consider a **collar** on the further, less-certain layers to keep some upside if EUR strengthens.
- **Hedge accounting:** designate as a **cash-flow hedge** (ASC 815 / IFRS 9) so the effective portion sits in **OCI** until the revenue is recognized — worth the documentation/effectiveness cost because it smooths reported revenue. Document at inception.
- **Flip condition:** if the revenue forecast slips below "highly probable," cash-flow-hedge designation is lost and the mark goes through P&L — re-assess the layer.

## Guardrails

- **Scope the exposure (transaction / translation / economic) before choosing anything** — the class drives the whole design.
- **"Do nothing" is a valid, governed decision** — don't reflex to hedging; an immaterial, naturally-offset, or un-economically-hedgeable exposure is an *accept*.
- **Translation ≠ transaction** — hedging equity translation spends cash to smooth a non-cash consolidation line; treat it as usually-accept unless there's a specific covenant/rating reason.
- Rarely hedge 100% or a single date — **layer/ladder** the ratio and match the horizon to the exposure's certainty.
- **Hedge accounting is a cost** (contemporaneous documentation + effectiveness testing) bought for P&L smoothing — choose cash-flow vs fair-value deliberately, or book through P&L.
- This is **not** accounting, tax, or legal advice, and hedge-accounting mechanics (ASC 815 / IFRS 9) are volatile — carry a **retrieval date** and confirm the current treatment with a qualified accountant before booking. See [`../../knowledge/treasury-management-patterns-2026.md`](../../knowledge/treasury-management-patterns-2026.md).
- Deep sanctions/counterparty-screening on the hedge counterparty is a `regulatory-compliance` seam; building the trade/confirmation systems is `fintech-payments-engineering`.
