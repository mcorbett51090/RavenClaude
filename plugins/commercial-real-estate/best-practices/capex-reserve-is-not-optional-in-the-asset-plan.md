# CapEx Reserve Is Not Optional in the Asset Plan

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

An asset plan that projects NOI growth without an explicit capital expenditure reserve is a projection on borrowed time. Deferred capital — roof replacement, HVAC systems, elevator modernization, parking lot resurfacing, building envelope — does not disappear from the balance sheet when it is omitted from the model. It reappears as an emergency capital call, a tenant retention loss because the building is aging, or a buyer's price concession at exit. The CapEx reserve is not overhead; it is the cost of maintaining the income stream.

## How to apply

Include a CapEx reserve line in every asset plan, differentiated between recurring and discretionary capital:

```
CapEx Reserve Schedule — [Property Name]
──────────────────────────────────────────
Year  | Routine Maint | Capital Reserve | Value-Add CapEx | Total CapEx | NOI (pre-capex) | NOI (post-capex)
──────|---------------|-----------------|-----------------|-------------|-----------------|──────────────────
  1   | $             | $               | $               | $           | $               | $
  2   | $             | $               | $               | $           | $               | $
  ...

CapEx Categories:
  Routine maintenance:   Day-to-day upkeep (expensed, not capitalized) — in operating expenses.
  Capital reserve:       System replacements + building envelope — funded from reserve per PCA.
  Value-add CapEx:       Renovation / repositioning investment — funded from equity.

Capital reserve basis:
  Property Condition Assessment (PCA) deferred maintenance:  $______
  Immediate needs:  $______  (Year 1 obligation)
  10-year capital needs estimate:  $______
  Annual reserve recommended by PCA:  $___/sf  or  $___/yr
  Reserve in model:  $___/yr  (___% of PCA recommendation — document if below 100%)

Value-add CapEx:
  Investment:  $______  Timeline: ___  Expected NOI lift: $___/yr  Yield-on-cost: ___%
```

**Do:**
- Obtain a Property Condition Assessment (PCA) at acquisition and fund the reserve to the PCA's annual recommendation unless there is a documented reason to deviate.
- Show the CapEx reserve as a separate line from operating expenses — it is not an operating cost; it is a capital obligation that affects cash flow and return.
- Present yield-on-cost for any value-add CapEx: investment ÷ incremental NOI — this is the self-contained return test for discretionary capital.

**Don't:**
- Use a single round-number "reserves" assumption without a PCA basis — $0.25/sf per year is a placeholder, not an underwritten number.
- Net CapEx against NOI without disclosing it; the IC memo must show NOI both pre- and post-CapEx reserve.
- Fund value-add CapEx from the operating cash flow in the model without showing the equity contribution and timeline.

## Edge cases / when the rule does NOT apply

NNN leases where the tenant is fully responsible for capital improvements shift the CapEx obligation to the tenant; confirm the structural/roof responsibility in the lease abstract before setting the reserve to zero.

## See also

- [`../agents/asset-property-manager.md`](../agents/asset-property-manager.md) — owns the asset plan including the CapEx schedule.
- [`./operating-expenses-are-an-underwriting-input-not-a-plug.md`](./operating-expenses-are-an-underwriting-input-not-a-plug.md) — the companion rule on building opex bottom-up, which CapEx supplements.

## Provenance

Codifies CLAUDE.md §3 #7 (operating expenses are an underwriting input, not a plug) extended to capital expenditure. PCA-anchored CapEx reserves are standard practice in institutional-grade CRE underwriting and lender due diligence requirements [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
