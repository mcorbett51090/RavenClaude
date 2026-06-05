# Label Every Unit and Currency on Every Input and Output

**Status:** Absolute rule
**Domain:** Financial modeling / model integrity
**Applies to:** `finance`

---

## Why this exists

The most avoidable modeling errors are unit mismatches: a revenue figure in millions fed into a formula expecting thousands, a EUR-denominated cost added to a USD revenue line with no FX conversion, a per-unit cost multiplied by a headcount instead of a volume figure. These errors are invisible in the formula bar and they produce plausible-looking outputs that are wrong by orders of magnitude. The fix is trivial — a label — and failing to apply it is a choice to accept silent error risk. The discipline matters most during handoffs, model merges, and when a new analyst extends a model someone else built.

## How to apply

Apply explicit unit and currency labels at three locations in every model:

```
Location 1 — Inputs tab / Assumptions sheet
  Every input row carries a "Units" column:
  e.g., "Revenue per unit | $USD | per unit (not per thousand)"
  e.g., "Headcount | # FTE | period-end"
  e.g., "Revenue growth rate | % | decimal (0.15 = 15%)"

Location 2 — Column and row headers in calculations
  Every output column header states the unit:
  e.g., "Revenue ($M)" not "Revenue"
  e.g., "Employees (FTE, period-end)" not "Headcount"

Location 3 — Cross-currency cells
  Every cell that converts or combines currencies shows:
  e.g., "EUR revenue (€) × FX rate ($/€) = USD equivalent ($)"
  The FX rate row carries its own "Units: $/€" label and a source + date.
```

**Do:**
- Add a legend or "model conventions" section to the Documentation tab: "All dollar figures are in USD thousands unless labeled otherwise."
- Use consistent scale across the model (don't mix $M and $K in the same sheet without an explicit bridging step).
- Flag any cell that combines figures of different units with a cell comment or a color-coded convention.
- For multi-currency models, designate one "functional currency" for all model mechanics and convert everything else to it before computing.

**Don't:**
- Rely on column-header labels alone for currency — if the inputs are in a different scale or currency than the mechanics, the header label doesn't catch it.
- Use format codes (e.g., `#,##0.0`) as the only unit signal — formats show scale, not currency or measurement unit.
- Allow "M" to mean both million and thousand in the same model (a common inherited-model trap).

## Edge cases / when the rule does NOT apply

- **Single-currency, single-scale models** where the convention is documented once and consistently applied — a detailed label on every row adds noise rather than clarity; a single model-level convention statement suffices. The absolute rule is that the convention must be documented somewhere; the per-row label is the default implementation.

## See also

- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — owns model integrity and the unit-labeling discipline.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — the inputs tab is where unit labels live alongside the assumption value.

## Provenance

Codifies the financial-modeler's model-integrity discipline from the finance plugin's CLAUDE.md §3 #2 (no hardcoded numbers in model mechanics — units are a form of documentation). The currency-mixing anti-pattern ("currency mixing without explicit FX rate disclosure") is explicitly called out in CLAUDE.md §4. The three-location label discipline reflects standard model-governance practice from professional financial-modeling courses and Big Four audit-support conventions.

---

_Last reviewed: 2026-06-05 by `claude`_
