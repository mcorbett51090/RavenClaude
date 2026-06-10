# First-time-fix is the master metric

**Status:** Absolute rule
**Domain:** Field-service operations
**Applies to:** `field-service-management`

---

## Why this exists

First-time-fix rate — the percentage of jobs resolved on the first visit without a return trip —
is the single metric that best predicts field-service business health. A failed first visit has a
compounding cost: the direct cost of a return trip (labor, drive time, parts re-staging), the
SLA penalty if the response window is missed on the callback, the customer satisfaction damage,
and the contract renewal risk. Every other operational lever — scheduling discipline, truck-stock
design, technician training, data capture — is best evaluated by how much it moves first-time-fix.

Without first-time-fix as the anchor, teams optimize for the wrong things: lowest parts cost
(drives stockout failures), highest utilization (drives dispatch of unqualified technicians),
fastest response (drives arrival without the right part or skill). All of these locally-optimal
behaviors reduce first-time-fix and increase total cost.

## How to apply

- **Set the first-time-fix rate target explicitly** before any operational redesign (dispatch,
  truck stock, training). The target must be agreed across service management, dispatch, and
  parts — it cannot be optimized by one function alone.
- **Segment every improvement initiative by its first-time-fix impact.** A truck-stock reduction
  that saves $X in carrying cost but decreases first-time-fix by Y% is only a good decision if
  Y% × cost-per-miss < $X.
- **Use first-time-fix as the root-cause diagnostic entry point.** When performance is off, start
  with the first-time-fix segment breakdown (parts / skill / diagnosis / information) before
  deciding where to invest.

**Do:**

- Track first-time-fix by technician, job type, equipment type, and root-cause category.
- Evaluate every dispatch, parts, and training decision by its first-time-fix implication.
- Set a first-time-fix target at each SLA tier level (premium contracts may require higher targets).

**Don't:**

- Optimize utilization, parts cost, or response speed independently without modeling the
  first-time-fix tradeoff.
- Accept a first-time-fix improvement without asking "which root cause did we actually fix?"
- Report first-time-fix as a fleet-wide average without segmentation — the average hides which
  job types, technicians, or territories are dragging the number.

## Edge cases / when the rule does NOT apply

For some very-low-criticality, best-effort service categories (e.g., cosmetic fixture replacement,
non-urgent appliance service), a two-visit model may be deliberately acceptable for cost reasons.
This must be an explicit design decision, not a default — and the customer must accept the model
at booking.

## See also

- [`./schedule-by-skill-and-sla-not-fifo.md`](./schedule-by-skill-and-sla-not-fifo.md)
- [`./truck-stock-is-inventory-with-a-service-level.md`](./truck-stock-is-inventory-with-a-service-level.md)
- [`../knowledge/fsm-decision-trees.md`](../knowledge/fsm-decision-trees.md)
- [`../skills/technician-productivity-and-first-time-fix/SKILL.md`](../skills/technician-productivity-and-first-time-fix/SKILL.md)

## Provenance

Codifies the field-service management industry consensus: first-time-fix is the primary KPI
(Aberdeen Group field-service research, ServiceTitan benchmarking data, IFS field-service
industry reports — all converge on first-time-fix as the master indicator of operational health
and customer retention). `[verify-at-use]`

---

_Last reviewed: 2026-06-08 by `claude`._
