# field-service-management

The **dispatch-to-cash operating engine** for field-service businesses — HVAC, plumbing, elevator,
and medical-device service. This plugin's team designs SLA tiers and service contracts, optimizes
dispatch boards and scheduling, improves technician utilization and first-time-fix rates, and
calibrates truck-stock to service-level targets.

> **The one-line philosophy:** first-time-fix is the master metric — every scheduling, inventory,
> and coaching decision is justified by how much it moves that number.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our SLA tiers / service contract structure" | **field-service-management** (`fsm-ops-lead`) |
| "Optimize our dispatch board / scheduling by skill and SLA" | **field-service-management** (`dispatch-and-scheduling-engineer`) |
| "Why is our first-time-fix rate low? Analyze technician utilization" | **field-service-management** (`technician-productivity-analyst`) |
| "Optimize truck stock / which parts should every tech carry?" | **field-service-management** (`parts-and-inventory-analyst`) |
| "Price a new service contract / write an SOW" | `skilled-trades-contracting` |
| "Manage the vehicle fleet (GPS, vehicle PM, fuel)" | `fleet-logistics` |
| "Handle customer complaints / NPS / CX escalations" | `customer-support-cx-operations` |

---

## What's inside

- **4 agents** — `fsm-ops-lead`, `dispatch-and-scheduling-engineer`, `technician-productivity-analyst`,
  `parts-and-inventory-analyst`.
- **3 skills** — `dispatch-and-scheduling`, `technician-productivity-and-first-time-fix`,
  `truck-stock-and-parts`.
- **3 commands** — `/field-service-management:design-dispatch-board`,
  `:improve-first-time-fix`, `:optimize-truck-stock`.
- **2 templates** — `dispatch-board.md`, `preventive-maintenance-schedule.md`.
- **Knowledge bank** — `knowledge/fsm-decision-trees.md`: Mermaid trees for schedule priority
  (SLA/skill/geo), stock-the-part-or-not, PM-vs-reactive; plus a dated 2026 capability map
  (ServiceTitan, Salesforce Field Service, IFS, FieldEdge).
- **6 best-practices** and **1 advisory hook** (flags SLA/skill/geo gaps, hard-coded rates).
- **Calculator** — `scripts/fsm_calc.py`: technician utilization, first-time-fix rate, MTTR, route
  density, SLA attainment, truck-stock fill rate.

---

## House opinions (the short list)

1. First-time-fix is the master metric — every other decision serves it.
2. Schedule by skill and SLA, never by FIFO.
3. Truck stock is inventory with a service level — optimize for first-time-fix, not lowest parts spend.
4. Preventive maintenance beats emergency dispatch — model the tradeoff explicitly.
5. The technician is the brand at the door — coaching and professionalism are customer-relationship investments.
6. Capture job data at the point of work — a job with missing field notes is a decision made blind.

---

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
