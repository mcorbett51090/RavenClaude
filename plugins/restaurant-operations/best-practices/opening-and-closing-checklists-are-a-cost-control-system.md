# Opening and Closing Checklists Are a Cost Control System

**Status:** Pattern
**Domain:** FOH/BOH operations / cost control
**Applies to:** `restaurant-operations`

---

## Why this exists

Opening and closing checklists are perceived as operational hygiene — the kind of thing a good GM does but that doesn't move the P&L. They do move the P&L. A kitchen opening checklist that includes temperature logs, prep counts verified against par, and waste documentation catches over-prep (a food cost driver) before the shift starts. A closing checklist that requires manager sign-off on voids, comps, and waste pulls — plus a cash reconciliation — is a financial control, not just a cleanliness routine. Restaurants that run rigorous open/close checklist discipline consistently show lower food and beverage variance than those that treat the checklist as optional.

## How to apply

Audit the current checklists against a cost-control standard:

```
Opening checklist cost-control audit:
  BOH:
  [ ] Temperature logs (walk-in, prep units) documented before service
  [ ] Prep levels counted vs. par — overages flagged to manager
  [ ] Waste from previous close reconciled against closing waste pull
  [ ] Blind count on high-value items (steaks, seafood, alcohol) by manager

  FOH:
  [ ] Reservation sheet reviewed — staffing adjusted if needed
  [ ] Void and comp authorization limits confirmed with staff
  [ ] Cash drawer count confirmed vs. system opening balance

Closing checklist cost-control audit:
  BOH:
  [ ] Waste pull completed and logged (item, quantity, reason)
  [ ] Leftover prep counted and recorded for next-day opening count
  [ ] Cooling log signed for any items entering the walk-in

  FOH:
  [ ] Void report printed and reviewed by manager
  [ ] Comp report printed and reviewed with reason codes
  [ ] Cash count completed and variance documented (not just "over/short")
  [ ] Safe deposit confirmed vs. system Z-report
```

**Do:**
- Require manager signature on both the void/comp review and the waste pull — these are financial documents, not just operational logs.
- Track the completion rate of the checklist itself; a checklist that is signed but not completed is worse than no checklist (false signal).
- Add a "note for next shift" field — the checklist is also a shift-to-shift communication tool that prevents waste and rework.

**Don't:**
- Let the checklist become a paper formality — if it is not reviewed by the manager and acted on when exceptions appear, it has no cost-control value.
- Build a checklist so long that it takes 45 minutes to complete — a 12–15 item checklist that is always finished beats a 40-item checklist that is always skipped.

## Edge cases / when the rule does NOT apply

Fully automated ghost kitchens with camera-based inventory systems may replace manual counts with automated tracking; the underlying discipline (verify counts, document waste, review voids) still applies, but the checklist format shifts to exception dashboards rather than paper.

## See also

- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns the checklist design and enforcement cadence.
- [`../agents/menu-cost-engineer.md`](../agents/menu-cost-engineer.md) — uses waste-pull data from closing checklists to close the theoretical-vs-actual gap.
- [`./comps-voids-and-waste-are-a-control-system-not-noise.md`](./comps-voids-and-waste-are-a-control-system-not-noise.md) — the closing checklist is the operational capture point for the comps, voids, and waste data that rule requires.

## Provenance

Codifies standard restaurant operations discipline; checklist-as-financial-control is a core principle in restaurant audit and franchise operations manuals across QSR and full-service segments.

---

_Last reviewed: 2026-06-05 by `claude`_
