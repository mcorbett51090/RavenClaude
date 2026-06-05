---
scenario_id: 2026-06-05-280e-cogs-allocation-gap
contributed_at: 2026-06-05
plugin: cannabis-operations
product: finance
product_version: "n/a"
scope: likely-general
tags: [280e, cogs, 471, effective-tax-rate, cpa, rescheduling]
confidence: medium
reviewed: false
---

## Problem

A single-store adult-use dispensary was profitable on the P&L but bled cash every tax season, and the owner couldn't see why. The cause: under IRC **Section 280E**, an operator "trafficking" a Schedule I/II controlled substance may not deduct ordinary business expenses (budtender wages, store rent, marketing, most overhead) — only **cost of goods sold (COGS)** reduces taxable income. The dispensary was classifying only a thin slice of its costs as COGS, so it was paying federal tax on essentially its entire gross margin plus all operating expenses. **cannabis-finance-analyst** must frame any fix as decision-support for the operator's CPA, never as tax advice (CLAUDE.md §2).

## Context

- Segment: dispensary (resale, not cultivation/manufacturing), adult-use, single state.
- Constraint: a dispensary's deductible COGS is structurally narrow — it is primarily the **wholesale cost of product plus freight-in and direct receiving costs**; most of what feels like "cost of running the store" is a non-deductible selling expense under 280E. Reported industry framing: dispensaries typically classify only ~35–50% of total expenses as COGS, which is why they carry the **highest** effective rates — routinely **>70%** federal effective on the modeled fact pattern [verify-at-use].
- The **rescheduling caveat (critical, volatile):** in April 2026 the DOJ/DEA moved **FDA-approved** marijuana products and **state-licensed *medical*** marijuana to Schedule III; **recreational/adult-use, unlicensed activity, and synthetic THC remained Schedule I** (a broader hearing was set for June 29, 2026). So for *this* adult-use store, 280E **still applied** at the time of the engagement — do not assume rescheduling removed the burden for adult-use operators (CLAUDE.md §2; §3 #3, #8). `[verify-at-use]` against the operator's segment, state license type, and the current federal posture.

## Attempts

- Tried: "just deduct more as COGS." Outcome: rejected — aggressive *misclassification* (pulling clearly-selling expenses into COGS) is exactly what an IRS exam disallows; the goal is **aggressive-but-defensible**, not aggressive-and-indefensible.
- Tried: confirmed the load-bearing facts against authoritative sources rather than memory — (a) 280E disallows ordinary deductions for Schedule I/II "trafficking," leaving COGS as the only shelter; (b) **Section 471** governs what may be capitalized into inventory/COGS, and a documented 471 cost study can materially widen allowable COGS **for the inventory-producing side** (cultivation/manufacturing — facility rent, utilities, depreciation tied to production); a pure resale dispensary has much less to pull in; (c) **Section 471(c)** offers a small-business inventory method for operators under the gross-receipts threshold (~$32M average over the prior three years) [verify-at-use — threshold is inflation-indexed]. Outcome: separated the *dispensary* lever (limited) from the *production* lever (larger).
- Tried (the move that worked): commissioned a **471 cost study with the operator's cannabis CPA**, correctly capitalizing freight-in and direct inventory-handling costs the store had been expensing, and — because this client also had a small in-house pre-roll production line — capitalized the production-attributable indirect costs into that product's COGS. Outcome: a defensible, documented COGS increase that lowered the effective rate, with the CPA as the signing authority.

## Resolution

The gap was **structure and documentation**, not a magic deduction — 280E is survived by maximizing *defensible* COGS under Section 471, with the largest lever on the production side and a much narrower one for pure resale. A CPA-led 471 cost study converted expensed inventory-handling and production-attributable costs into capitalized COGS, and the engagement explicitly did **not** assume the 2026 partial rescheduling helped an adult-use operator.

**Action for the next consultant hitting this pattern:** establish the operator's **segment and license type first** — a cultivator/manufacturer has a far larger 471 lever than a resale-only dispensary. Confirm the **current** rescheduling posture for the operator's exact segment (the April 2026 order was *narrow* — medical/FDA-approved only; adult-use stayed Schedule I and under 280E) before claiming any relief. Route every position through the operator's **cannabis CPA** — this plugin is not a tax authority and gives no tax advice (CLAUDE.md §2). Document everything: an undocumented COGS reclassification is a disallowed one.

**Sources (retrieved 2026-06-05):**
- Northstar Financial Advisory — Complete 280E Tax Guide (effective-rate framing, COGS share): https://nstarfinance.com/resources/280e-tax-guide-cannabis-businesses
- LegalClarity — Cannabis Tax Law: 280E, COGS, Section 471: https://legalclarity.org/understanding-cannabis-tax-law-from-280e-to-cogs/
- Congress.gov CRS — IRC §280E applied to marijuana businesses (R46709): https://www.congress.gov/crs-product/R46709
- DOJ — rescheduling of FDA-approved + state-licensed *medical* marijuana to Schedule III (April 2026): https://www.justice.gov/opa/pr/justice-department-places-fda-approved-marijuana-products-and-products-containing-marijuana
- Federal Register — Schedules of Controlled Substances: Rescheduling of Marijuana (2026-04-28): https://www.federalregister.gov/documents/2026/04/28/2026-08177/schedules-of-controlled-substances-rescheduling-of-marijuana

280E mechanics, the 471(c) threshold, and especially the **rescheduling posture** are volatile and segment-dependent — `[verify-at-use]` with the operator's CPA and the current federal rule before any deliverable (CLAUDE.md §2, §3 #8).
