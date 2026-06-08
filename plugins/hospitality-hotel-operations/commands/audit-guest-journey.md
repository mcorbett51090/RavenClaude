---
description: "Map the end-to-end guest journey, surface the operational defects and bottlenecks, and produce the SOP / labor / maintenance fixes that close them."
argument-hint: "[property + the symptom (slow check-in, rooms not ready, recurring complaint) + current staffing/PMS context]"
---

You are running `/hospitality-hotel-operations:audit-guest-journey`. Use `hotel-operations-lead` + the `front-office-and-housekeeping-ops` skill.

## Steps
1. Map the guest journey as one system: booking → arrival → stay → departure → post-stay. Mark the stage(s) where the symptom surfaces.
2. Trace the defect/bottleneck to its operational root cause (room-status handoff, the maintenance-ticket loop, the arrival-peak staffing, a PMS workflow run off a side spreadsheet).
3. Write the SOP fix — the repeatable procedure that removes the per-incident judgment call (and the walk-protocol if overbooking is in play).
4. Map labor to the occupancy forecast: coverage at the arrival peak and the room-turn load, never below the service floor (route the forecast to `revenue-manager`).
5. Close the maintenance loop: report → triage → fix → return-to-sellable for any out-of-order inventory.
6. Route handoffs: pricing/forecast → revenue-manager, the review/loyalty loop → guest-experience-analyst, F&B → restaurant-operations.
7. Emit the guest-journey map + fixes + the Structured Output block (with `KPI impact:` and `Handoff to neighbours:`).
