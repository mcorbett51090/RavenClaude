# The turn is where NOI is won or lost

**Status:** Pattern
**Domain:** Operations / NOI performance
**Applies to:** `property-management-residential`

---

## Why this exists

Every day a unit sits vacant after a tenant moves out is lost rent — full stop. A 10-day turn on a
$1,800/month unit costs $600 in lost gross potential rent. A 20-day turn costs $1,200. Across a
100-unit portfolio, reducing average turn time from 20 days to 10 days recovers $60,000+ in
annualized revenue, depending on turnover rate — without changing asking rents, occupancy targets,
or operating expenses.

The turn is also the moment when deferred maintenance becomes visible and get-it-done pressure is
highest. A poorly scoped make-ready produces quality shortcuts that generate callbacks during the
next tenancy; a well-run turn produces a lease-ready unit that photographs well, leases faster, and
costs less to maintain for the next 12 months.

## How to apply

1. **Measure it.** Track days-to-ready as a KPI: key-surrender date to lease-ready date. Report it
   to the owner monthly. Anything over 10 days on a standard turn is worth investigating.
2. **Start the scope before move-out.** Walk the unit at the pre-move-out inspection (if allowed),
   or the day of key surrender. Delay in starting the scope = delay in the turn clock.
3. **Vendor scheduling is the critical path.** Paint, carpet, and cleaning can't all start at once.
   Know the sequencing and have vendors pre-booked for the likely scope.
4. **Use `templates/make-ready-turn-checklist.md`** for every turn. The checklist enforces scope
   completeness, tracks vendor completion, and produces a days-to-ready KPI automatically.
5. **Run the renew-vs-turn economics** before every renewal decision. Use `scripts/pm_calc.py`. The
   cost of a turn almost always favors retaining a good-standing tenant within a reasonable rent
   range.

**Do:**

- Set a days-to-ready target (7 days for standard turns; 14 days for heavy turns) and track every
  turn against it.
- Pre-book preferred vendors for paint, carpet, and cleaning so scheduling isn't the delay.
- Complete the move-out inspection on day 0 or day 1 — the scope can't start until inspection is
  done.
- Sign off on the scope before vendors begin — an undocumented scope has no cost control.

**Don't:**

- Start a turn without a completed move-out inspection — you'll miss damage claims and scope items.
- Let the turn clock start later than the day of key surrender.
- Accept a vendor's completion without a final walkthrough and photos.
- Skip the turn checklist because the unit "looks fine" — the checklist catches smoke detector
  battery dates, HVAC filter condition, and rekey status.

## Edge cases / when the rule does NOT apply

- **Planned capital improvements between tenancies:** if the owner is using the vacancy to make
  capital improvements (kitchen remodel, bathroom upgrade), days-to-ready extends deliberately and
  should be tracked separately from a standard turn. The owner is making a deliberate investment
  in future rent growth; the turn KPI applies to standard make-readies, not capex projects.

## See also

- [`./every-work-order-carries-an-sla.md`](./every-work-order-carries-an-sla.md)
- [`../templates/make-ready-turn-checklist.md`](../templates/make-ready-turn-checklist.md)
- [`../knowledge/pm-residential-decision-trees.md`](../knowledge/pm-residential-decision-trees.md) — renew-vs-turn decision tree, repair-vs-replace tree
- [`../scripts/pm_calc.py`](../scripts/pm_calc.py) — `turn_cost()` calculator

## Provenance

Grounded in residential property management operational benchmarks. Industry data consistently
shows that turn cost (vacancy loss + make-ready cost) is the largest controllable driver of NOI
variance for stabilized residential portfolios. Turn-time reduction is the highest-ROI operational
lever available to a PM with a stable occupancy rate.

---

_Last reviewed: 2026-06-08 by `claude`._
