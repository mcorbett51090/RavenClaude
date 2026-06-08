---
description: "Map the hotel guest journey, diagnose reputation-score drivers, design a review-response and service-recovery strategy, and quantify the ADR headroom and repeat-revenue value of a targeted reputation improvement."
argument-hint: "[current reputation scores and context, e.g. 'TripAdvisor 3.9/5, Booking.com 8.1/10, top complaints: cleanliness and slow check-in, 180-room full-service hotel']"
---

You are running `/hospitality-hotels:plan-guest-experience`. Use the `guest-experience-lead`
discipline and the `guest-experience-and-reputation` skill.

## Steps

1. Establish the reputation baseline: collect current overall scores (TripAdvisor, Booking.com,
   Google, Expedia), 90-day trend, category breakdown (cleanliness, service, value, F&B,
   location), and comp-set comparison if available.

2. Identify the top 3 negative review themes from recent guest feedback (or infer from the
   category scores). Map each theme to an operational owner:
   - Cleanliness → `rooms-and-housekeeping-analyst`
   - Service speed / warmth → front office / department SOPs
   - F&B quality → `restaurant-operations` seam
   - Value perception → `revenue-manager` / `reservations-and-channel-analyst`

3. Map the guest journey across the 5 stages (pre-arrival, arrival, in-stay, departure,
   post-stay). For each stage, note the highest-friction touchpoint identified in step 2
   and the specific action to address it.

4. Design the review-response playbook:
   - Response timing target (within 48 hours for negative)
   - Tone guidelines (acknowledge specific complaint, state correction, invite back)
   - Escalation path for safety, billing, or brand-standards complaints

5. Design the service-recovery empowerment matrix:
   - Front-desk agent authority level (room move, amenity, F&B credit up to $X without manager)
   - Supervisor authority level (rate adjustment, comp night offer)
   - MOD / GM authority level (legal, safety, significant loyalty impact)

6. Quantify the ADR headroom: apply the ~1.4–2.7% ADR premium per 1-point score improvement
   [verify-at-use] to the current ADR and the target score gap vs. comp-set. Show the math.
   Calculate repeat-revenue uplift at the target repeat-guest rate.

7. Emit the Structured Output block with handoffs to `rooms-and-housekeeping-analyst`
   (cleanliness operational actions), `revenue-manager` (ADR headroom context), and
   `restaurant-operations` (if F&B is a top driver).
