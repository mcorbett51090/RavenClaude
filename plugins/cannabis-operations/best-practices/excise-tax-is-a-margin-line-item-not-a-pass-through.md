# Treat excise tax as a margin line item, not a pass-through

**Status:** Absolute rule
**Domain:** Cannabis operations / tax / dispensary retail
**Applies to:** `cannabis-operations`

---

## Why this exists

Cannabis excise taxes (state cultivation tax, excise tax at retail, ad valorem on wholesale, or combined) are levied at rates and bases that vary dramatically by state — from California's 15% retail excise to Illinois's 10–25% tiered structure — and in most states the operator is the taxpayer, not the consumer. An operator who mentally books excise as "just passed through to the customer" is systematically understating the effective cost of goods sold and overstating store margin. When excise is baked into retail price without being modeled as a cost, discount decisions that "look fine on margin" are actually eroding the after-tax position. Under 280E, excise tax on cultivation is a COGS-eligible cost; retail excise is not — the accounting treatment differs and matters.

## How to apply

Build excise tax into the margin model explicitly:

```
Retail price:           $XX.XX
Less: retail excise tax: ($X.XX)   [state rate × retail price, or flat per unit]
Net revenue to ops:      $XX.XX

Cost of goods sold:      ($X.XX)   [incl. cultivation excise if applicable]
Gross margin on net rev: XX%
```

Track actual excise liability separately from sales revenue in the chart of accounts. Reconcile to the state return quarterly.

**Do:**
- Map your state's excise structure (cultivation tax vs. retail excise vs. wholesale ad valorem) at setup — they are assessed at different points in the supply chain.
- Include cultivation excise in your 280E COGS calculation; retail excise is not COGS.
- Model the impact of excise on net margin before approving volume discounts or loyalty programs.
- Cite the state and effective date on any excise figure used in a deliverable (§3 #3 and §3 #8).

**Don't:**
- Net excise against sales revenue and present a "clean" revenue line to ownership — it obscures real margin.
- Assume excise rates are stable; states have revised rates, added tiers, and suspended them with little notice.
- Confuse the excise tax the operator remits with sales tax the customer pays — both may appear on a receipt, they flow differently in the books.

## Edge cases / when the rule does NOT apply

- Jurisdictions with no state excise tax (rare; some medical-only markets) have no excise line to model, but the same discipline applies if local municipal taxes exist.
- Delivery/markup platforms that collect and remit excise on behalf of the dispensary still require the operator to verify the remittance and reconcile it — the obligation doesn't transfer just because a third party files.

## See also

- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — builds the scorecard that embeds excise correctly.
- [`./280e-makes-cogs-allocation-existential-not-academic.md`](./280e-makes-cogs-allocation-existential-not-academic.md) — cultivation excise intersects with COGS allocation.
- [`./the-rules-change-at-the-state-line-never-generalize-a-state.md`](./the-rules-change-at-the-state-line-never-generalize-a-state.md) — excise structures differ by state; never import another state's rate.

## Provenance

Standard cannabis operations and tax practice for regulated dispensary/cultivation economics. Marked `[unverified — training knowledge]`; validate rates and treatment with a licensed cannabis CPA for the specific state.

---

_Last reviewed: 2026-06-05 by `claude`_
