# Model Tenant Improvements and Leasing Commissions Bottom-Up

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

TI and leasing commissions are the most commonly underestimated line items in a CRE acquisition model. A deal that uses blended "TI per sf" and "LC as % of rent" assumptions without tying them to the specific lease-expiration schedule and market conditions is plugging in numbers, not underwriting. In a high-rollover asset or a market where TI allowances have risen with escalating construction costs, the gap between the model and reality on re-leasing costs is the difference between a 12% IRR and a 6% one.

## How to apply

Build TI and LC assumptions tenant-by-tenant and expiration-by-expiration, not as blended portfolio averages:

```
TI / LC Schedule — [Property Name]
────────────────────────────────────
Tenant | SF | Expiry | New/Renewal? | TI ($/sf) | Source | LC (% of rent) | Source | Total TI+LC
───────|----|--------|--------------|-----------|--------|----------------|--------|─────────────
       |    |        |              |           |        |                |        |
...

TI/LC Basis:
  New lease TI ($/sf):     $___  [source — market comp / broker quote / prior-deal actual]
  Renewal TI ($/sf):       $___  (typically 25–50% of new lease TI; confirm by market)
  LC — new lease (%):      ___%  of total rent value [market basis]
  LC — renewal (%):        ___%  (typically 50% of new; confirm)

Re-leasing cost summary:
  Total TI in hold period:   $______
  Total LC in hold period:   $______
  Combined re-leasing cost:  $______  (___% of acquisition price)

Free-rent assumption:
  New lease free rent:  ___ months  (deducted from NER)
  Renewal free rent:    ___ months
```

**Do:**
- Separate new-lease TI from renewal TI — renewal TI is materially lower in most markets; blending them overstates the holdover cost for an asset with high renewal probability.
- Source TI and LC figures from market comps with a date — construction costs and leasing commissions move with market conditions; a 2021 TI comp is not 2025 market.
- Show TI and LC as a cash-flow line item in the hold-period model, timed to the lease expiration year — they are a capital event, not an operating expense.

**Don't:**
- Use a single blended TI/sf assumption for all lease expirations without considering whether the space is raw shell, second-generation, or a renewal of an existing fit-out.
- Omit free rent from the NER calculation on new leases — free rent is one of the three components that converts face rent to NER.
- Treat LC as a single-line percentage; break out landlord's and tenant's broker commissions if the market convention splits them.

## Edge cases / when the rule does NOT apply

NNN single-tenant net leases often have no TI obligation on the landlord (tenant improvements are tenant-funded); the TI line is zero or limited to a specific allowance under the lease. Confirm in the lease abstract.

## See also

- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — builds the TI/LC schedule as part of the hold-period cost model.
- [`./net-effective-rent-is-the-real-number-not-face-rent.md`](./net-effective-rent-is-the-real-number-not-face-rent.md) — TI and free rent are two of the three NER deductions.

## Provenance

Codifies CLAUDE.md §3 #7 (operating expenses are an underwriting input, not a plug) extended to re-leasing capital. Bottom-up TI/LC modeling is standard practice in institutional-grade CRE underwriting [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
