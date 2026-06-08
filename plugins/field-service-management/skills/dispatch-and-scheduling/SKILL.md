---
name: dispatch-and-scheduling
description: "Design and optimize a field-service dispatch board — priority queue logic by SLA tier, skill-match routing, geographic density optimization, emergency vs. planned time-block allocation, and day-of-dispatch escalation protocols."
---

# Dispatch and Scheduling

**Purpose:** build a dispatch system that puts the right technician on the right job at the right
time — satisfying SLA commitments, skill requirements, and geographic efficiency simultaneously.

---

## Steps

### 1. Define the priority order

Map each SLA tier to a dispatch priority level before any scheduling work begins:

| Priority | Job type | Response window | Dispatch rule |
|---|---|---|---|
| P0 | Emergency / safety | ≤ 2 hours | Override all planned work; trigger escalation ladder immediately |
| P1 | Premium SLA | ≤ 4 hours | Assign within 30 min of call receipt; skill match is a hard constraint |
| P2 | Standard SLA | ≤ 8 hours | Assign within 2 hours; skill match required; geo-density preferred |
| P3 | Basic / best-effort | Next business day | Batch with geographic density; skill match required |
| P4 | Planned PM | Scheduled window | Route by density; batched and pre-confirmed |

P0 and P1 always pre-empt P4 and lower. If pre-emption affects a P4 commitment, notify the
customer immediately (see the escalation ladder in Step 4).

### 2. Apply skill-match as a hard constraint

For each job, define the minimum skill requirement (e.g., EPA 608 certification for refrigerant
work, OEM-certified for medical devices, licensed journeyman for plumbing). A technician who does
not meet the skill minimum for a job is not available for that job — the dispatch board must
enforce this as a filter, not an advisory.

Build and maintain a technician-skills matrix:

```
technician | cert_1 | cert_2 | equipment_types | tier_authorization
-----------+--------+--------+-----------------+-------------------
Tech A     | EPA608 | R-410A | HVAC-commercial | P0, P1, P2
Tech B     | NATE   |        | HVAC-residential| P2, P3, P4
```

### 3. Optimize for geographic density

After applying priority and skill filters, break ties by geographic density:

1. Calculate the jobs-per-zone for each technician's territory (use `route_density()` in
   `scripts/fsm_calc.py`).
2. Assign the job to the technician whose next stop produces the highest jobs-per-drive-hour
   ratio for the remainder of the day.
3. Cluster planned PM jobs by zip code or grid cell to minimize inter-job travel.
4. Review territory design quarterly: if any technician's average drive time per job exceeds
   30–35 min, rebalance territory boundaries.

### 4. Design the emergency escalation ladder

```
Step 1: Check in-territory qualified technicians — is one available within the SLA window?
   YES → dispatch immediately, confirm ETA with customer.
   NO  ↓
Step 2: Check adjacent-territory qualified technicians — can one reach within the window?
   YES → dispatch with overtime authorization if needed; notify customer of tech name + ETA.
   NO  ↓
Step 3: Check approved subcontractors — is there a pre-vetted sub within range and skill?
   YES → dispatch sub; confirm sub meets insurance + liability requirements.
   NO  ↓
Step 4: Notify customer of SLA miss; offer best available ETA; escalate to service manager.
        Document as an SLA miss event for the weekly review.
```

### 5. Set the daily time-block architecture

A field-service day needs explicit allocation across competing demands:

| Block | Time window | Allocation |
|---|---|---|
| Planned PM | Morning (06:00–10:00) | Batched by geo density; PM runs first before reactive demand builds |
| Reactive buffer | Rolling (10:00–15:00) | Unscheduled capacity for P2/P3 calls received same day |
| Emergency reserve | Always-on | 1 tech (or equivalent subcontractor capacity) held for P0/P1 |
| Admin/travel close | End-of-day (15:00–17:00) | Final job completions; mobile data entry; truck restock confirmation |

Adjust block sizes by the ratio of PM-to-reactive jobs in your business mix.

### 6. Validate with the pre-dispatch parts-readiness check

Before dispatching any job requiring non-stock (special-order) parts:

1. Confirm parts are on the tech's truck OR at the staging depot.
2. If parts are pending, do not dispatch until parts are confirmed in hand.
3. Log any job delayed by parts unavailability as a parts-delay event (feeds
   `parts-and-inventory-analyst` root-cause tracking).

---

## Anti-patterns

- Scheduling by order-received (FIFO) without SLA or skill weighting.
- Treating skill match as a preference rather than a hard filter.
- No emergency-reserve buffer — a fully-booked schedule cannot deliver on emergency SLAs.
- Territory design that ignores geographic density (jobs per drive-hour).
- Dispatching a job without a parts-readiness check for non-stock parts.

---

## Output

A dispatch board design document using `templates/dispatch-board.md`, with the priority-queue
rules, skill-match matrix, territory/density map, daily time-block allocation, and escalation
ladder documented. Include the key metrics to track: SLA attainment by tier, schedule-adherence
rate, and average jobs per drive-hour.
