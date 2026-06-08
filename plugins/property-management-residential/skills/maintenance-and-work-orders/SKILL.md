---
description: "Operate the full maintenance and work-order lifecycle: intake triage to priority tier, SLA assignment and tracking, vendor dispatch, make-ready and turn management, preventive maintenance scheduling, and work-order analytics. Covers habitability-first triage, turn-time reduction, and vendor performance management."
---

# Maintenance and Work Orders

**Purpose:** run a maintenance operation where every work order has a priority tier, every tier
has an SLA, habitability items are never deprioritized, and turns complete in minimum days so
vacant units produce rent instead of cost.

---

## The operating loop

### Step 1 — Intake and triage

Every incoming maintenance request — via PM software portal, phone, email — is triaged within 1
business hour and assigned a priority tier before anything else happens.

**Tier definitions:**

| Tier | Definition | Response SLA | Resolution SLA |
| --- | --- | --- | --- |
| **Emergency** | Habitability, health, or safety: no heat (winter), no AC (summer, where legally required), sewage backup, active water leak, gas smell, fire-related damage, no hot water, structural hazard, pest infestation with habitability implication | ≤1 hour acknowledgment | ≤24 hours or fastest available |
| **Urgent** | Significant impact on resident comfort or property: appliance failure (refrigerator, stove), HVAC not optimal (but not habitability-level), broken locks or windows, water leak (contained), electrical issue (non-emergency) | ≤4 hours | ≤72 hours |
| **Routine** | Non-urgent repairs: cosmetic damage, minor appliance issue (dishwasher, disposal), painting, carpet cleaning, general maintenance | ≤24 hours | ≤7 calendar days |

**Rule:** when in doubt, assign the higher tier. A routine-triaged habitability item creates legal
and reputational exposure. Err toward emergency/urgent.

### Step 2 — Vendor dispatch

1. **Preferred vendor list** — by trade (HVAC, plumbing, electrical, appliance, general
   maintenance). COI, license, and W-9 on file. Pricing schedule (flat-rate preferred for
   standard items; T&M with a cap for complex work).
2. **Dispatch sequence** — PM software auto-dispatch or manual assignment. Vendor notified with
   work order details, access instructions, and SLA deadline.
3. **Vendor confirmation** — vendor acknowledges the work order and confirms ETA within 1 hour of
   dispatch (for emergency/urgent). No confirmation → escalate to backup vendor.
4. **Access coordination** — notify the resident of the scheduled access window (24-hour notice
   required by most jurisdictions for non-emergency access). Emergency access: notify simultaneously
   with entry.

### Step 3 — Work completion and close

1. **Completion confirmation** — vendor marks the work order complete in the PM software, uploads
   photos of the completed work and the signed invoice.
2. **Resident confirmation** — for routine and urgent work, PM follows up with the resident within
   24 hours of completion to confirm satisfaction. Document the response.
3. **Work order close** — mark closed in the PM software. Attach all documentation (invoice,
   photos, resident confirmation).
4. **Callback tracking** — flag any re-open within 30 days as a callback. Track by vendor and by
   trade. A callback rate > 10% triggers a vendor performance review.

### Step 4 — Make-ready / turn process

1. **Move-out inspection** — scheduled the day of or day after move-out. Document all conditions
   vs. move-in inspection form.
2. **Scope sign-off** — PM reviews move-out inspection, produces make-ready scope: paint, carpet,
   appliances, cleaning, repairs. Cost estimate against the `templates/make-ready-turn-checklist.md`.
3. **Vendor scheduling** — schedule all trades in sequence (repairs → paint → clean → carpet if
   needed). Target: key-to-ready in ≤7 days for standard turns; ≤14 days for heavy turns.
4. **Final walkthrough** — PM walks the completed turn before the unit is listed. Verify against
   the make-ready scope. Punch list anything not done.
5. **Days-to-ready KPI** — track from move-out key surrender to lease-ready status. Report to
   `pm-ops-lead` as part of NOI KPI pack.

### Step 5 — Preventive maintenance

Run a seasonal PM schedule to catch failures before they become emergency calls:

| Frequency | Items |
| --- | --- |
| Monthly | HVAC filter replacement (common areas, any units with PM responsibility) |
| Quarterly | Smoke and CO detector test; fire extinguisher check |
| Semi-annual | HVAC system inspection and tune (spring AC, fall heat); gutter cleaning; pest inspection |
| Annual | Roof inspection; water heater inspection and flush; common-area lighting check; fire safety system inspection |

Document each PM task in the work-order system with a "preventive maintenance" type tag. This
creates the maintenance history needed for capital planning and owner reporting.

### Step 6 — Work order analytics

Pull monthly from the PM software:

- **SLA compliance rate** by tier: % of work orders closed within SLA
- **Days-to-close average** by tier
- **Callback rate** by vendor and by trade
- **Cost per unit** by category (HVAC, plumbing, electrical, appliance, general)
- **Turn cost per unit** and **days-to-ready average**
- **Emergency vs routine split** (a high emergency ratio signals deferred PM)

---

## Anti-patterns

- Habitability work orders (heat, AC, sewage, active leak, pest, mold) in the routine queue.
- A turn started without a completed move-out inspection and signed scope.
- Vendor invoices approved without attached photos or a signed work order.
- No preventive maintenance program — all maintenance is reactive.
- Callback rates not tracked — quality data exists but no one reads it.

---

## Output

A SLA matrix, a make-ready scope, a turn process design, a preventive maintenance calendar, or a
vendor performance report. Reference `templates/work-order-sla-matrix.md` and
`templates/make-ready-turn-checklist.md`. Structured Output Protocol block per `ravenclaude-core`.
