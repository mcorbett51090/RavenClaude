# Control densification — when Tableau invents marks or hides gaps you didn't ask for

**Status:** Primary diagnostic — when a viz shows phantom rows, unexpected extra marks, or missing gaps in a sparse series (and the numbers look "off" but the grain looks right), suspect densification/domain-padding before re-checking the calc.

**Domain:** Viz / data modeling

**Applies to:** `tableau`

---

## Why this exists

Tableau silently **densifies** — it can add marks for domain members that don't exist in the data, or pad a date/bin axis to fill gaps — and a table calculation can *force* densification across the densified domain. The result is a viz that shows a running total continuing across months with no data, a "% of total" whose denominator includes invented rows, or a line that connects across gaps that should be breaks. This is a distinct failure class from a grain/LOD bug: the data and the level of detail are right, but Tableau is completing (or padding) the domain behind your back. The viz-engineer's "most wrong-number bugs are grain bugs" heuristic does **not** catch this one — densification produces wrong *marks*, not a wrong aggregation grain.

## How to apply

**Recognize the two mechanisms:**

- **Domain padding** — turning on *Show Empty Rows/Columns* (or a continuous date/bin axis) fills the domain with members that have no underlying rows. Useful for an intentional dense axis (every month on the X even when some are empty); harmful when it invents denominators.
- **Densification (data/table-calc)** — a table calculation computed *along* a dimension forces Tableau to materialize every domain member so the calc has something to compute on, even where no data exists.

**Control it deliberately:**

- Want gaps shown as gaps? Use a **discrete** date/dimension (gaps stay gaps) rather than a continuous axis that pads.
- Want a complete axis (every month) but correct denominators? Pad the axis but guard the calc — e.g. `IF ISNULL(SUM([Sales])) THEN NULL` so padded members don't enter a `% of total` / running total.
- Seeing phantom marks from a table calc? Check whether the calc is densifying — restrict its addressing/partitioning, or compute the value as an LOD expression (which doesn't densify) instead of a table calc.
- Lines connecting across real gaps? Set *Format → Special Values* / mark handling so nulls break the line rather than interpolate.

**Do:** decide consciously whether the domain should be complete (padded) or sparse (gaps shown); guard ratio/running calcs against padded nulls; prefer LOD over table calc when you don't want densification.

**Don't:** leave *Show Empty Rows/Columns* on by reflex and then compute ratios over the padded domain; assume a table calc only reads existing data; treat phantom marks as a grain bug.

## Edge cases / when the rule does NOT apply

Domain padding is the *right* choice when you genuinely want a continuous axis (a complete monthly timeline, a full histogram bin range) — the rule is to make it a conscious choice, not to always disable it. Some forecast/cluster features (Analytics pane) rely on a padded continuous axis — see the analytics-pane rule. Exact menu paths are version-sensitive — `[verify-at-build]`.

## See also

- [`./viz-analytics-pane-statistics-validity.md`](./viz-analytics-pane-statistics-validity.md) — forecasting/trend on a padded axis
- [`./viz-axis-and-dual-axis-integrity.md`](./viz-axis-and-dual-axis-integrity.md) — the sibling "don't let the chart mislead" rule
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — LOD vs table-calc (the densification-relevant fork)
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns viz correctness
- [Tableau — data densification](https://help.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields_densification.htm) — authoritative

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01, Panel 3 BUILD): the 14 existing tableau trees + 26 rules cover grain/LOD/connection-model thoroughly but had **zero** coverage of densification/domain-padding — a classic senior "extra/phantom marks" bug distinct from the grain bugs the calc tree addresses. Grounded in Tableau's data-densification documentation. Menu paths are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
