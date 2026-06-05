# Curtailment Risk Belongs in the Base Case, Not the Downside Scenario

**Status:** Pattern
**Domain:** Energy yield / project economics
**Applies to:** `renewable-energy`

---

## Why this exists

Grid curtailment — the forced reduction of solar output due to transmission congestion, negative prices, or system operator instructions — is increasingly common in high-penetration renewable markets (ERCOT, CAISO, MISO South, SPP). A project modeled without curtailment in the base case is overstating energy production in markets where curtailment events are observable and growing. Pro-formas that relegate curtailment to a downside scenario miss the fact that it is a recurring, modeled cost in high-penetration markets — lenders and buyers already price it in; a developer who doesn't is selling an optimistic number. Curtailment above 3–5% of annual production in a constrained market is not a downside — it is the base case.

## How to apply

Build curtailment into the base-case energy model for any project in a congested or high-penetration market:

```
Curtailment assessment (pre-pro-forma):
  Step 1 — Market screen:
    Is the project in ERCOT, CAISO, MISO South, or a known constrained ISO zone?
    What is the local renewable penetration % on the same node or zone? [unverified, use ISO data]

  Step 2 — Curtailment estimate source (use best available):
    ISO/RTO historical nodal curtailment data (ERCOT OASIS, CAISO OASIS): ______% prior year
    Comparable projects in the same node (if available): ______%
    Third-party curtailment study (if procured for project): ______%

  Step 3 — Base-case haircut:
    Apply the estimated curtailment % to the P50 energy yield:
    Adjusted P50 = P50 gross × (1 − curtailment %) = ______ MWh

  Step 4 — Curtailment sensitivity:
    Low curtailment (2%):     ______ MWh — IRR: ______%
    Base curtailment (6%):    ______ MWh — IRR: ______%
    High curtailment (12%):   ______ MWh — IRR: ______%

  IRR hurdle test: if the base-case curtailment scenario fails the IRR hurdle, the project is curtailment-fragile.
```

**Do:**
- Use actual ISO historical curtailment data for the node or zone when available — it is public and is better than a generic assumption.
- Model curtailment as a separate line-item haircut to the gross energy yield, not as a reduction in system production — the distinction matters for performance ratio analysis.
- Include a PPA curtailment provision in the offtake contract review — some PPAs allow the buyer to curtail without price reduction; others count curtailment hours against the buyer's minimum take obligation.

**Don't:**
- Present a base case energy yield without curtailment in a high-penetration market — the lender's independent engineer will apply it anyway.
- Treat curtailment as a one-time event; in constrained markets it grows over time as more renewable capacity is added to the same zone.

## Edge cases / when the rule does NOT apply

Behind-the-meter projects with 100% self-consumption have no grid curtailment exposure — the "curtailment" equivalent is the host load dropping below system output, which is modeled as a load-matching study. Projects with merchant offtake and the ability to dispatch (storage-solar hybrid) can partially mitigate curtailment by shifting generation to lower-curtailment hours; model the dispatch value separately.

## See also

- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the curtailment adjustment in the energy model and pro-forma.
- [`../agents/grid-interconnection-specialist.md`](../agents/grid-interconnection-specialist.md) — owns the nodal congestion and curtailment risk assessment.
- [`./production-estimates-are-p50-p90-not-a-single-number.md`](./production-estimates-are-p50-p90-not-a-single-number.md) — curtailment must be applied to both P50 and P90 estimates before presenting the range.

## Provenance

Curtailment risk modeling is documented in NREL curtailment studies, ISO/RTO annual reports, and is a standard lender requirement in project finance due diligence for utility-scale solar in congested markets.

---

_Last reviewed: 2026-06-05 by `claude`_
