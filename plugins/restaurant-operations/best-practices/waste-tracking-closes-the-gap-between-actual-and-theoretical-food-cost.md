# Waste Tracking Closes the Gap Between Actual and Theoretical Food Cost

**Status:** Absolute rule
**Domain:** Restaurant operations / food cost control
**Applies to:** `restaurant-operations`

---

## Why this exists

The gap between theoretical food cost (what the food should cost if every recipe were made perfectly) and actual food cost (what the food actually cost per the P&L) is where margin disappears. Industry average actual food cost runs roughly 32–35% of revenue; when theoretical is built correctly, the gap to actual is typically 2–6 percentage points. Every point of gap on $1M in sales is $10,000 in missing margin. Without a structured waste log, the gap is an unexplained number — the operator knows food cost is too high but cannot locate the cause. Waste tracking turns the gap from a financial mystery into a locatable, fixable operational problem.

## How to apply

Run a waste log and reconcile it against the theoretical-to-actual gap on a weekly cycle:

```
Waste Log — [Location] Week of [YYYY-MM-DD]
───────────────────────────────────────────
Category           │ Item           │ Qty  │ Unit cost │ Total $ │ Root cause code
───────────────────┼────────────────┼──────┼───────────┼─────────┼────────────────
Prep / trim        │                │      │           │         │ P
Over-production    │                │      │           │         │ O
Spoilage           │                │      │           │         │ S
Breakage / spill   │                │      │           │         │ B
Void / re-fire     │                │      │           │         │ V
Employee meal      │                │      │           │         │ E
                   │                │      │           │         │
───────────────────┼────────────────┼──────┼───────────┼─────────┼────────────────
Week total         │                │      │           │ $___    │

Root cause codes:
  P = Prep / trim (portion or trim inconsistency)
  O = Over-production (forecast error — made more than sold)
  S = Spoilage (ordering or shelf-life management failure)
  B = Breakage / spill (accident)
  V = Void / re-fire (quality failure — guest rejection)
  E = Employee meal (should be accounted, not untracked waste)
```

**Weekly reconciliation:**

```
Theoretical vs. Actual Reconciliation — Week of [date]
──────────────────────────────────────────────────────
Net sales:                    $___
Theoretical food cost $:      $___ (___ %)
Actual food cost $:           $___ (___ %)
  Gap ($):                    $___  (___ % of sales)

Waste log total:              $___
Unexplained gap (residual):   $___ (= actual − theoretical − tracked waste)

If unexplained gap > $200/week or > 0.5% of sales → investigate:
  [ ] Portion audit (weigh 5 items against recipe card)
  [ ] Void / comp report audit (POS)
  [ ] Receiving audit (delivered vs. invoiced weight)
  [ ] Cash vs. food cost cross-check (high food cost + low cash variance = portioning)
```

**Do:**
- Log waste at the point of discard, not at end of shift — aggregated memory logs are inaccurate.
- Separate controllable waste (over-production, spoilage) from uncontrollable (trim, breakage) in reporting — only controllable waste has a corrective action.
- Use the waste log to drive the production sheet (how much to prep each day), not the other way around.
- Share the reconciliation with the kitchen manager weekly — a manager who sees the waste-cost number owns it; one who doesn't, doesn't.

**Don't:**
- Treat the gap as normal variance without investigating it — a persistent 3-point gap on $50K/week in sales is $1,500/week that has a cause.
- Use the waste log as a disciplinary tool before it is used as a diagnostic tool — the first question is what caused the waste, not who.
- Skip the reconciliation in high-volume weeks — those are the weeks where portion drift and over-production are most costly.

## Edge cases / when the rule does NOT apply

Ghost kitchens with no in-person dining and highly standardized production (e.g., meal-kit assembly) may have theoretical food costs that are inherently accurate; a formal waste log may be replaced by batch reconciliation. High-end prix-fixe operations with very low covers and highly variable tasting menus may find that daily waste tracking is cost-ineffective relative to its value — but the theoretical-to-actual reconciliation still applies, even if waste is tracked by production batch rather than item.

## See also
- [`../agents/menu-cost-engineer.md`](../agents/menu-cost-engineer.md) — owns recipe costing and the theoretical food-cost model.
- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns production sheets, void controls, and BOH procedures.
- [`../knowledge/restaurant-unit-economics.md`](../knowledge/restaurant-unit-economics.md) — covers theoretical vs. actual food cost framework.

## Provenance

Standard restaurant operations discipline; the theoretical-vs-actual reconciliation is the core of the National Restaurant Association's food cost control curriculum and the Restaurant365/Toast best-practice documentation [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
