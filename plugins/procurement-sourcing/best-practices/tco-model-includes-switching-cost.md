# The TCO Model Must Include Switching Cost

**Status:** Absolute rule
**Domain:** Sourcing / TCO analysis
**Applies to:** `procurement-sourcing`

---

## Why this exists

Total cost of ownership models for supplier selection frequently omit the transition and switching cost of moving from one supplier to another. This makes the incumbent look more expensive than it is relative to a challenger on a steady-state basis, because the comparison does not include the one-time cost the buyer must incur to switch. A challenger's 8% lower unit price may be entirely offset by six months of qualification costs, tooling investment, onboarding overhead, and quality-risk during the ramp period. A TCO model that omits switching cost systematically over-values new entrants and creates pressure to switch suppliers on the basis of a misleading comparison.

## How to apply

Include a switching-cost component in every TCO model that compares an incumbent to a new supplier.

```
TCO Model — Switching Cost Component
──────────────────────────────────────────────────────
TCO components — incumbent (baseline)
  Unit price × volume
  + Freight / logistics
  + Incoming quality failure cost (defect rate × rework cost)
  + Inventory carry (safety stock days × unit value × cost of capital)
  + Supplier management overhead (FTE hours × loaded rate)
  = Incumbent TCO per period

TCO components — challenger (steady-state, after ramp)
  Same structure as above.

Switching cost (one-time, amortized over contract term)
  + Qualification / audit cost (travel, testing, certification)
  + Tooling / tooling transfer cost
  + Onboarding and training (internal FTE time)
  + Inventory build-up during transition (safety-stock increase × periods)
  + Quality risk / premium during ramp (expected elevated defect rate × cost)
  + System / EDI setup cost
  + Contract legal / admin cost
  ──────────────────────────────────────────────────────
  = Total switching cost

TCO comparison (per period, amortized):
  Incumbent TCO vs. [Challenger steady-state TCO + (Switching cost / contract term)]

Decision:
  Switch if: Challenger TCO (amortized) < Incumbent TCO by a defined threshold
             (e.g., ≥ 5% lower to absorb uncertainty in the switching-cost estimate)
```

**Do:**
- State all switching-cost assumptions explicitly and get stakeholder validation for the largest items (tooling, qualification).
- Apply a sensitivity analysis on switching cost ± 25% — switching-cost estimates are typically imprecise.
- For strategic categories, model the TCO over the full proposed contract term, not just Year 1.

**Don't:**
- Build a TCO model without a switching-cost component when comparing an incumbent to a challenger.
- Use switching cost as a reason never to switch; the point is to price it correctly, not to eliminate switching as an option.
- Treat qualitative risks (supply reliability during transition, relationship capital) as zero just because they are hard to quantify; add a risk-premium line with an explicit assumption.

## Edge cases / when the rule does NOT apply

- **New category with no incumbent** — no switching cost applies; the TCO model covers the build-out of the new supply relationship (qualification, setup) instead.
- **Contract expired and relationship already terminated** — switching to a new supplier has no incumbent to protect; model the setup cost of the new supplier directly.

## See also

- [`../agents/category-strategist.md`](../agents/category-strategist.md) — owns TCO modeling and the should-cost analysis.
- [`./source-on-total-cost-of-ownership-not-unit-price.md`](./source-on-total-cost-of-ownership-not-unit-price.md) — the upstream rule that mandates TCO over unit price; this doc operationalizes the switching-cost element of the TCO build.

## Provenance

Codifies the category-strategist's TCO discipline from the procurement-sourcing plugin's CLAUDE.md §3 #2 ("source on total cost of ownership, not unit price") and the `skills/source-on-tco/SKILL.md`. The switching-cost component structure is standard TCO methodology; validate cost inputs against engagement-specific data before use.

---

_Last reviewed: 2026-06-05 by `claude`_
