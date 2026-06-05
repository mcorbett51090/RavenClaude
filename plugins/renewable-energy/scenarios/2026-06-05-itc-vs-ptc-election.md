---
scenario_id: 2026-06-05-itc-vs-ptc-election
contributed_at: 2026-06-05
plugin: renewable-energy
product: finance
product_version: "n/a"
scope: likely-general
tags: [itc, ptc, tax-credit, capacity-factor, election]
confidence: medium
reviewed: false
---

## Problem

A developer defaulted to the **ITC** (a one-time investment credit, ~30% of eligible basis at full bonus) "because that's what everyone takes," without testing whether the **PTC** (a per-kWh production credit over the first 10 years) would deliver more lifetime value for a high-resource, low-CapEx project. The risk: leaving credit value on the table by treating the election as a habit rather than a per-project calculation driven by capacity factor and CapEx (CLAUDE.md §3 #8 — model the credit explicitly, dated).

## Context

- Segment: utility-scale solar in a high-irradiance region with competitive CapEx (the regime where the PTC tends to win).
- Constraint: the ITC-vs-PTC election is a **per-project, mutually-exclusive** call. The PTC's 10-year production stream out-values the one-time ITC when **capacity factor is high and CapEx is low** (more kWh per installed dollar to monetize); the ITC wins when CapEx is high or the resource is modest. Bonus adders (energy-community, domestic-content) and bonus depreciation interact with both and shift the crossover.
- The election is also **policy-window-sensitive**: post-OBBBA (2025), solar/wind ITC and PTC eligibility hinges on *begin-construction by July 4, 2026* OR *placed-in-service by Dec 31, 2027* [verify-at-use] — so the election can't be made in isolation from the project's milestone schedule.

## Attempts

- Tried: computed **both** credits on the project's real inputs — ITC = credit rate × eligible basis; PTC = per-kWh rate × P50 annual production × 10 years (degraded), each discounted to present value. Outcome: for this high-CF/low-CapEx project the PV of 10 years of PTC exceeded the one-time ITC.
- Tried: layered the **bonus adders** (energy-community, domestic-content) onto each side and re-checked the crossover, since an adder can swing a marginal call. Outcome: confirmed the PTC lead held after adders for this site; flagged that on a higher-CapEx sister project the ITC would win.
- Tried: confirmed the **policy-window eligibility** (begin-construction / placed-in-service dates) before relying on either credit, and routed the binding determination to tax counsel. Outcome: avoided modeling a credit the project's schedule couldn't actually capture.

## Resolution

The project **elected the PTC** because the explicit, discounted side-by-side — not habit — showed its 10-year production stream beat the one-time ITC for this high-capacity-factor, low-CapEx site, and the schedule cleared the post-OBBBA eligibility window. The output was a dated election memo showing both credits' PV, the adder layering, and an explicit "this is decision-support; the binding determination is tax counsel's" caveat (CLAUDE.md §2 — the team is not a tax advisor).

**Action for the next consultant hitting this pattern:** **compute both credits explicitly per project — high capacity factor + low CapEx favors the PTC; high CapEx or modest resource favors the ITC.** Layer the bonus adders before calling the crossover, and confirm the post-OBBBA begin-construction / placed-in-service window before trusting either — see [`../knowledge/renewables-itc-vs-ptc-decision-tree.md`](../knowledge/renewables-itc-vs-ptc-decision-tree.md). The election is decision-support; route the binding determination to tax counsel ([`energy-finance-analyst`](../agents/energy-finance-analyst.md) frames it, counsel rules on it).

**Sources (retrieved 2026-06-05):**
- ICF — *Solar Economics: The PTC vs. ITC Decision* (high capacity factor + low CapEx favors PTC): https://www.icf.com/insights/energy/solar-economics-ptc-vs-itc
- Crux — *ITC vs PTC Credits: What's the Difference?*: https://www.cruxclimate.com/insights/itc-vs-ptc
- IRS — *Notice 2025-42, §§45Y/48E Beginning of Construction* (post-OBBBA timing): https://www.irs.gov/pub/irs-drop/n-25-42.pdf

Credit rates, the capacity-factor/CapEx crossover, adder values, and the begin-construction / placed-in-service deadlines are year- and jurisdiction-specific and were materially reshaped by OBBBA (2025) — treat every figure as `[verify-at-use]` and confirm with current IRS guidance and tax counsel before any deliverable (§3 #3, #8).
