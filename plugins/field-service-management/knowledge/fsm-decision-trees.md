# Field-Service Management — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `field-service-management`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
> Volatile product/version facts in the capability map carry a retrieval date and a re-verify-at-use
> rider.

---

## Decision Tree: Schedule Priority (SLA tier → skill match → geo density)

```mermaid
flowchart TD
  A[New job arrives — what is the priority?] --> B{Is it an emergency / safety issue?}
  B -->|Yes| P0[P0: Override all current work<br/>Trigger escalation ladder immediately<br/>Skill match is a hard constraint — don't send unqualified tech]
  B -->|No| C{What SLA tier is the customer on?}
  C -->|Premium — 4h response| P1[P1: Assign within 30 min<br/>Skill match = hard constraint<br/>Nearest qualified tech wins]
  C -->|Standard — 8h response| D{Is a skill-matched tech available in territory?}
  C -->|Basic / best-effort| P3[P3: Schedule next-day<br/>Cluster with geo density<br/>Skill match required]
  C -->|Planned PM| P4[P4: Batch by geo density<br/>Pre-confirm 24h ahead<br/>Parts pre-staged]
  D -->|Yes| P2[P2: Assign within 2 hours<br/>Prefer highest geo density among qualified techs]
  D -->|No — skill gap| E{Is an adjacent-territory tech available?}
  E -->|Yes| P2adj[P2 adjacent: dispatch with OT authorization<br/>Flag skill-gap for coaching review]
  E -->|No| Esc[Escalate: approved subcontractor or SLA-miss notification<br/>Log skill coverage gap for workforce planning]
  P1 --> GEO[Break ties by geo density: assign tech whose next stop maximizes jobs per drive-hour]
  P2 --> GEO
```

**Leaf rule:** skill match is always a hard constraint — dispatching an unqualified technician
does not clear the SLA; it creates a callback and a customer-satisfaction miss. After skill match,
break ties with geographic density (jobs per drive-hour), not by who is "next in the queue."

---

## Decision Tree: Stock the Part or Not

```mermaid
flowchart TD
  A[Should this part be on every truck?] --> B{How often is this part used per tech per month?}
  B -->|≥ 1× per month| C{What is the first-time-fix cost if the part is missing?}
  B -->|< 1× per month| D{Is the part critical for a premium SLA job type?}
  C -->|High — SLA miss + return visit| UNIVERSAL[Universal carry<br/>Set min/max; reorder at 20% of max]
  C -->|Low — minor inconvenience or reschedulable| E{Is carrying cost < monthly miss cost?}
  E -->|Yes| UNIVERSAL
  E -->|No| SPECIALTY[Tech-specialty: carry on techs with that job type scheduled<br/>Pre-stage per job otherwise]
  D -->|Yes — e.g., premium contract, medical device| SPECIALTY
  D -->|No| F{Is the part low-frequency AND high-cost or bulky?}
  F -->|Yes| SPECIAL[Special-order: do not stock on truck<br/>Pull from depot or order per job<br/>Pre-dispatch confirmation required]
  F -->|No| E
```

**Leaf rule:** every truck-stock decision must state the service-level target it is designed to
meet. Removing a part from truck stock without modeling the first-time-fix fill-rate impact is not
a cost optimization — it's a blind tradeoff. Use `scripts/fsm_calc.py` `truck_stock_fill_rate()`
to quantify fill-rate changes before recommending add or remove.

---

## Decision Tree: PM vs. Reactive Dispatch

```mermaid
flowchart TD
  A[Should we invest in a preventive maintenance program for this equipment/customer?] --> B{What is the current reactive-call rate for this equipment type?}
  B -->|High — ≥ 2 reactive calls per unit per year| C{What is the cost per reactive call?}
  B -->|Low — < 1 reactive call per unit per year| D{Is the equipment critical — SLA penalty or safety risk on failure?}
  C -->|High — emergency dispatch + parts premium + OT| PM_YES[PM is likely ROI-positive<br/>Model: PM cost vs. reactive calls avoided<br/>Start with 2× per year and adjust]
  C -->|Low — non-critical, standard-hours call| E{Is the equipment under a service contract?}
  D -->|Yes — premium SLA, safety, medical device| PM_YES
  D -->|No — best-effort, low criticality| PM_OPTIONAL[PM optional<br/>Offer as upgrade; don't require it]
  E -->|Yes — PM already contractually included| PM_CONTRACT[Execute PM per contract schedule<br/>Track: reactive calls per unit before/after PM]
  E -->|No| F{Would a PM contract convert this customer to recurring revenue?}
  F -->|Yes — renewal likely, good account| PM_SELL[Propose PM contract to convert reactive to planned<br/>Use PM-vs-reactive cost model in pitch]
  F -->|No| REACTIVE_ONLY[Reactive-only is fine<br/>Monitor call frequency; revisit if it rises]
  PM_YES --> G[Set PM frequency: high-criticality = 4× year; standard = 2× year; low = 1× year<br/>Validate against contract; use templates/preventive-maintenance-schedule.md]
```

**Leaf rule:** before cutting PM visit frequency to reduce cost, model the reactive-call increase
that follows. PM converts reactive cost (emergency dispatch premium + parts premium + overtime
+ SLA penalty risk) into planned cost. The break-even is typically 1.5–2 avoided reactive calls
per PM cycle, depending on the equipment type.

---

## 2026 Capability Map — FSM Platform Landscape (dated, re-verify at use)

_Retrieved 2026-06-08. Product positioning and pricing are volatile — re-confirm at use; this is
orientation, not a procurement recommendation. [verify-at-use]_

| Category | Options (2026) | Notes |
|---|---|---|
| **SMB field-service platforms** | **ServiceTitan** — dominant in HVAC/plumbing/electrical SMB; strong dispatch board, mobile app, flat-rate pricing, financing integrations | High per-seat cost; best fit for businesses doing > $2M revenue with complex dispatch needs [verify-at-use] |
| **Mid-market / enterprise FSM** | **Salesforce Field Service** (formerly FieldService Lightning) — part of the Salesforce ecosystem; strong for enterprises already on Salesforce CRM | Deep CRM integration; higher implementation cost; best when service is part of a larger enterprise workflow [verify-at-use] |
| **Industrial / complex assets** | **IFS Field Service Management** — strong for asset-intensive industries (elevators, medical devices, utilities); handles complex service contracts, warranty, and depot repair | Best for OEM service orgs and complex multi-location asset portfolios [verify-at-use] |
| **Small / regional service** | **FieldEdge** — HVAC/plumbing/electrical focus; lower cost than ServiceTitan; strong flat-rate pricing and dispatch board for smaller fleets | Good fit for 2–15 technician operations; fewer advanced analytics than ServiceTitan [verify-at-use] |
| **Scheduling optimization** | **Skedulo**, **Jobber** (SMB), **ServiceMax** (Salesforce-native enterprise) — specialized scheduling and mobile-workforce tools | ServiceMax overlaps with IFS in industrial; Jobber is lightweight for sole-proprietor/small-team [verify-at-use] |
| **Route optimization** | **OptimoRoute**, **Route4Me**, **Onfleet** — pure route/territory optimization tools that integrate with FSM platforms | Used as add-ons when the core FSM's routing is insufficient for high-density fleets [verify-at-use] |

> Provenance: platform positioning based on industry analysis and vendor documentation available
> as of 2026-06-08; market shares and feature sets are volatile — re-verify at procurement.
> No invented products. [verify-at-use]

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution and seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the 6 named, citable rules.
- [`../scripts/fsm_calc.py`](../scripts/fsm_calc.py) — calculator for utilization, first-time-fix,
  MTTR, route density, SLA attainment, and truck-stock fill rate.

_Last reviewed: 2026-06-08 by `claude`._
