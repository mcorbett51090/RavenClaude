# Payment Terms Are a Working Capital Lever, Not Just a Contract Clause

**Status:** Pattern
**Domain:** Procurement & sourcing / contract management
**Applies to:** `procurement-sourcing`

---

## Why this exists

Payment terms are treated as boilerplate in most sourcing events — a checkbox negotiated last, after price and scope are locked. That is a mistake. For a company with $500M in addressable spend, moving average payment terms from Net 30 to Net 60 frees approximately $21M in working capital (at a 15% cost of capital, that is worth ~$3M/year in real cash). Conversely, a supplier who asks for early-pay and offers a 2/10 Net 30 discount is offering annualized financing at ~36%: either a highly profitable short-term investment for the buyer, or a signal of financial stress worth flagging to the risk team. Payment terms belong in the category strategy, not the legal redline pass.

## How to apply

Evaluate payment terms in three contexts: strategic negotiation, early-pay programs, and supplier risk signals.

**Working capital calculation:**

```
Working Capital Impact of Terms Extension
──────────────────────────────────────────
Annual spend in category:          $___
Current average payment terms:     ___ days
Target payment terms:              ___ days
Days improvement:                  ___ days

Working capital released:
  = Annual spend × (days improvement ÷ 365)
  = $___ × (___ ÷ 365)
  = $___

Annualized value (at company cost of capital ___% ):
  = Working capital released × cost of capital rate
  = $___
```

**Early-pay discount evaluation:**

```
2/10 Net 30 discount — annualized cost to supplier / return to buyer:
  Annualized rate = discount% ÷ (1 - discount%) × (365 ÷ (net days - discount days))
  Example: 2% ÷ 98% × (365 ÷ 20) = ~37.2% APR

  If company WACC < annualized rate → take the discount (profitable financing)
  If company WACC > annualized rate → decline (cheaper to borrow)
  If supplier routinely offers early-pay → flag for financial health check
```

**Do:**
- Include payment terms in the RFx scope and evaluate them as a scored element alongside price and TCO.
- Benchmark current terms against industry norms before the negotiation — Net 60–90 is standard in many manufacturing and services categories; accepting Net 30 when Net 60 is the norm is a silent working-capital cost.
- Use dynamic discounting or supply-chain finance programs to offer early payment to financially stressed but strategically important suppliers, rather than pushing aggressive terms that destabilize them.
- Coordinate with Treasury and AP before committing to terms — a negotiated Net 60 that AP processes at Net 30 is a paper win.

**Don't:**
- Accept supplier standard terms without a working-capital impact calculation — standard terms usually favor the supplier.
- Use aggressive payment-term extension as a substitute for supplier development when the supplier is a single-source strategic partner — straining their cash flow is straining your supply continuity.
- Annualize a 2/10 discount offer without checking whether the company has the liquidity to systematically capture it.

## Edge cases / when the rule does NOT apply

Small/minority-owned suppliers and those in regulated industries (government contracting, healthcare) may have mandatory or negotiated-in-law payment terms that override commercial flexibility. In those cases, document the constraint and route working-capital analysis to the addressable spend only.

## See also
- [`../agents/category-strategist.md`](../agents/category-strategist.md) — negotiates terms as part of the category sourcing play.
- [`../agents/supplier-risk-specialist.md`](../agents/supplier-risk-specialist.md) — interprets early-pay requests as potential financial-health signals.
- [`../knowledge/sourcing-economics.md`](../knowledge/sourcing-economics.md) — covers TCO framework and working-capital trade-offs.

## Provenance

Codifies standard corporate treasury and procurement practice; the annualized discount formula is the standard early-pay arithmetic used in APICS, ISM, and CIPS training materials [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
