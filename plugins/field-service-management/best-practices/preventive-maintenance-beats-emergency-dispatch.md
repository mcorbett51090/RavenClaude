# Preventive maintenance beats emergency dispatch

**Status:** Pattern
**Domain:** Service operations strategy
**Applies to:** `field-service-management`

---

## Why this exists

Emergency dispatch is the most expensive way to deliver a service. It carries: an emergency
response premium (labor overtime, parts-premium from emergency supplier), SLA penalty risk,
disruption to planned schedules (a P0 that arrives mid-day displaces 2–3 planned jobs), and
elevated customer stress. Preventive maintenance converts this reactive cost into planned cost:
a PM visit costs more per labor-hour than a routine reactive call but far less than an emergency
dispatch that includes overtime, parts premium, and a disrupted schedule.

The tradeoff is quantifiable. A business that cuts PM visit frequency to save cost will typically
see reactive call rates increase within 1–2 equipment cycles. The typical break-even is 1.5–2
avoided reactive calls per PM cycle — a threshold most commercial HVAC/elevator/medical-device
equipment crosses without difficulty.

## How to apply

- **Model the PM-vs-reactive tradeoff explicitly before cutting PM frequency.** The PM-vs-reactive
  tree in `knowledge/fsm-decision-trees.md` structures the decision. If reactive call rates are
  above 2 per unit per year for the equipment type, PM is almost certainly ROI-positive.
- **Sell PM contracts to convert reactive-only customers.** A PM contract gives the service
  business predictable, recurring revenue; gives the customer lower emergency risk. Use the
  cost-avoidance model in the sales pitch: "our PM program reduces your emergency call frequency
  by X% based on fleet history — here is what that saves you in downtime and repair cost."
- **Set PM frequency by criticality.** High-criticality equipment (medical devices, elevators,
  data-center HVAC) warrants 4× per year; standard commercial equipment typically 2×; low-
  criticality residential equipment typically 1×. Validate the frequency against the failure-
  rate history for the equipment type.

**Do:**

- Track reactive calls per unit per year by equipment type. Use this as the input to PM ROI models.
- Set PM frequency based on equipment criticality and failure rate, not on what is cheapest.
- Review PM-to-reactive call conversion rates quarterly to validate PM frequency decisions.

**Don't:**

- Cut PM visit frequency without modeling the reactive-call increase that follows.
- Sell a PM program without knowing the cost to deliver (labor + parts + travel per PM visit).
- Treat PM as purely a cost item — it is a reactive-cost-avoidance investment with a measurable
  return.

## Edge cases / when the rule does NOT apply

For low-criticality, best-effort equipment with very low failure rates and cheap reactive fixes,
reactive-only may genuinely be the right model. The decision should be explicit: model the
reactive call frequency and cost, compare to the PM investment, and choose deliberately — not
by default or budget pressure.

## See also

- [`./first-time-fix-is-the-master-metric.md`](./first-time-fix-is-the-master-metric.md)
- [`../knowledge/fsm-decision-trees.md`](../knowledge/fsm-decision-trees.md) (PM-vs-reactive tree)
- [`../templates/preventive-maintenance-schedule.md`](../templates/preventive-maintenance-schedule.md)

## Provenance

Reflects standard field-service management economics: PM cost-avoidance modeling is a staple of
service contract pricing in HVAC, elevator, and medical-device service industries. The break-even
framework (avoided reactive calls × cost per reactive call > PM program cost) is widely used in
service-contract ROI analysis. `[verify-at-use]`

---

_Last reviewed: 2026-06-08 by `claude`._
