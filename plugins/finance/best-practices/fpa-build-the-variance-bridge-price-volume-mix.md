# Decompose a revenue or cost variance into price, volume, and mix before naming a cause

**Status:** Primary diagnostic
**Domain:** FP&A / variance analysis
**Applies to:** `finance`

---

## Why this exists

`reconcile-before-you-narrate.md` gates *when* commentary may be written; this doc governs *how* a revenue or unit-driven-cost variance gets decomposed once the account is reconciled. A single P&L line — "revenue $1.2M below plan" — almost always hides three drivers (price, volume, mix) moving simultaneously, sometimes in opposite directions. Naming "sales missed" without the split routes remediation at the wrong lever: you chase volume when the problem was a discount (price), or you blame pricing when the customer base shifted toward a lower-priced tier (mix). The PVM bridge is the standard decomposition; it is the PVM leaf of [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md), made into a constructive how-to.

## How to apply

Compute the three effects in this order, holding the other two constant for each, so the three sum exactly to the total variance:

```
Total variance = Actual − Budget   (revenue or unit-driven cost)

Volume effect = (Actual qty − Budget qty) × Budget price       # qty changed, price held at budget
Price effect  = (Actual price − Budget price) × Actual qty      # price changed, qty held at actual
Mix effect    = Σ over products [ (Actual mix% − Budget mix%) × (product price − avg budget price) × total qty ]

Check:  Volume effect + Price effect + Mix effect = Total variance   (must tie exactly)
```

Where the data won't support a clean three-way split, a **two-way rate × volume** bridge (the agent's `rate × volume / mix / FX` decomposition) is the honest fallback — state that mix is folded into rate.

**Do:**
- Make the three effects **sum to the total** and show the reconciliation row — an un-tying bridge is a broken bridge.
- Hand each slice to its owner: price → pricing/sales, volume → demand/sales, mix → product/segment.
- Net any FX effect out *first* (constant-currency) before PVM, per the FX leaf — FX is translation, not operating performance.

**Don't:**
- Write "revenue missed by $X" with no PVM split when the line is revenue or a unit-driven cost.
- Pick one effect and discard the others; if two drivers both moved, name both (the triage tree's "bridges are additive" rule).
- Confuse a mix shift with a volume miss — a customer-base tier shift is mix, not lost units.

## Edge cases / when the rule does NOT apply

- **Non-unit-driven lines** (fixed opex, rent, a one-time legal accrual) have no price/volume/mix structure — traverse to the ONE-TIME or DECISION leaf instead.
- **Single-product, single-price lines** collapse mix to zero; a rate × volume two-way bridge is sufficient and honest.
- **Below-threshold variances** owe no commentary at all, so no bridge is required (house opinion #5: materiality is a design constraint).

## See also

- [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) — the PVM leaf this operationalizes; the full leaf order.
- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the gate that must clear before this bridge is built.
- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — "names the driver, not the variance"; the `rate × volume / mix / FX` decomposition surface area.
- [`../skills/variance-commentary/SKILL.md`](../skills/variance-commentary/SKILL.md) — templates for revenue/GM/opex/EBITDA walks.

## Provenance

Codifies the PVM leaf of [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) (sourced there from CFI, CFO Secrets' bridge methodology, Phoenix Strategy Group), the `fpa-analyst` decomposition surface area, and house opinion #7 (numbers don't ship without commentary). Adjacent to the existing reconcile-first rule.

---

_Last reviewed: 2026-05-30 by `claude`_
