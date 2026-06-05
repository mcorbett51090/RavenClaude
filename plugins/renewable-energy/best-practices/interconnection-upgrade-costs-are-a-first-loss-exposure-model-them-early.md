# Interconnection Upgrade Costs Are a First-Loss Exposure — Model Them Early

**Status:** Primary diagnostic
**Domain:** Grid interconnection / project economics
**Applies to:** `renewable-energy`

---

## Why this exists

Interconnection upgrade costs — the network upgrades the generator must pay to connect to the grid — are the most common cause of project abandonment in utility-scale and large C&I solar. A project with a $1.5M/MW upgrade cost allocation on a $1.2M/MW all-in project cost is economically dead on arrival, but developers frequently don't discover this until the detailed interconnection study results arrive — after 18–36 months of development cost. Early-stage modeling of upgrade exposure using pre-application screening, queue transparency tools (MISO, PJM, CAISO public data), and comparable project results gives a rough estimate that gates the development decision long before the study is completed.

## How to apply

Build the upgrade cost exposure model in Phase 1 development:

```
Early-stage upgrade cost screen (before Phase 1 study):
  Substation target:              ______
  Existing queue at substation (MW): ______ (from ISO queue transparency data)
  Project size (MW-AC):           ______

  Heuristic upgrade cost ranges [unverified — highly variable by ISO and substation]:
    Radial distribution (sub 5 MW):    $0–$200/kW typical
    Transmission (utility-scale):      $50–$500/kW typical; outliers to $1,500/kW
    HVDC or major substation work:     $500–$2,000+/kW in constrained networks

  Upgrade cost sensitivity in pro-forma:
    Base case (no upgrade):           IRR = ______%
    Moderate upgrade ($150/kW):       IRR = ______%
    High upgrade ($400/kW):           IRR = ______%
    Fatal threshold (upgrade kills IRR below hurdle): $______/kW

  If base-case IRR only survives the "no upgrade" scenario → the project's economics are upgrade-fragile.
  Flag this explicitly before proceeding to site control or interconnection application filing.
```

Decision rule: if the project's IRR drops below the equity hurdle at a moderate upgrade scenario ($150–$200/kW), the project cannot absorb the development risk of the study process. Either (a) find a lower-cost interconnection point, (b) resize the project, or (c) structure a contingency exit before the upgrade cost is known.

**Do:**
- Use ISO public queue data (MISO Generator Interconnection Queue, PJM Queue, CAISO Interconnection Queue) to screen substation load and existing queue position before filing.
- Model the upgrade cost sensitivity in the pro-forma at three levels (none, moderate, severe) before committing to full development cost.
- Include a study cost budget line in the development budget; Phase 1 and Phase 2 interconnection studies cost $50,000–$500,000+ depending on the ISO and project scale [unverified — training knowledge].

**Don't:**
- Assume that a low-queue substation means low upgrade costs — queue size is one factor; substation capacity, transformer loading, and transmission constraints are equally important.
- Proceed to full interconnection application without a contingency plan if the Phase 1 study reveals upgrade costs that break the pro-forma.

## Edge cases / when the rule does NOT apply

Behind-the-meter projects that do not interconnect to the utility grid have no interconnection upgrade exposure; the relevant cost is the equipment permit and utility approval for the interconnection switch. Distribution-level projects (< 5 MW) in many ISOs have simplified interconnection processes with lower study costs and often lower upgrade exposure.

## See also

- [`../agents/grid-interconnection-specialist.md`](../agents/grid-interconnection-specialist.md) — owns the interconnection queue analysis and study-cost modeling.
- [`../agents/energy-finance-analyst.md`](../agents/energy-finance-analyst.md) — owns the upgrade cost sensitivity in the pro-forma.
- [`./interconnection-is-the-schedule-and-the-schedule-is-the-risk.md`](./interconnection-is-the-schedule-and-the-schedule-is-the-risk.md) — upgrade cost and schedule risk are the two interconnection variables; this rule addresses cost, that rule addresses schedule.

## Provenance

Interconnection upgrade cost modeling is standard in utility-scale solar development; queue data sources are public (MISO, PJM, CAISO) and are used by developers and lenders in early-stage feasibility screens. Cost ranges marked `[unverified — training knowledge]` and vary significantly by location and year.

---

_Last reviewed: 2026-06-05 by `claude`_
