---
name: schedule-crews-and-dispatch
description: "Turn a week of booked moves into a crew-and-truck schedule by sizing each crew to the shipment's cube and access, assigning trucks, routing local (hourly, multi-stop within a day) vs long-haul (weight-and-distance, multi-day, possible interline), holding a capacity/utilization target with buffer for overruns, and building the dispatch board so delivery windows hold. Reach for this when the user asks 'how do I schedule my crews and trucks next week?', 'how big a crew for this job?', 'how do I route local vs long-distance?', or 'my board keeps blowing up on overruns'. Used by `moving-operations-lead` (primary); consulted by `moving-compliance-and-claims-specialist` so an interstate job isn't dispatched before operating authority is confirmed."
---

# Skill: schedule-crews-and-dispatch

> **Invoked by:** `moving-operations-lead` (primary). Also consulted by `moving-compliance-and-claims-specialist` so an **interstate** job isn't dispatched before **operating authority** (USDOT/MC) is confirmed.
>
> **When to invoke:** "How do I schedule crews and trucks?"; "how big a crew for this move?"; "route local vs long-haul"; "my board overruns and misses delivery windows"; any move from booked jobs to a dispatch schedule.
>
> **Output:** the crew-and-truck schedule — crew sizing, truck assignment, local-vs-long-haul routing, a capacity/utilization target with overrun buffer, and the dispatch board.

## Procedure

1. **Name the branch and read the booked jobs.** Dispatch/capacity branch — traverse [`../../knowledge/moving-relocation-decision-tree.md`](../../knowledge/moving-relocation-decision-tree.md). Pull each booked job's cube, access (stairs/elevator/long carry/shuttle), and window.
2. **Size each crew to the cube and access.** Crew size scales with the shipment's cube and the access difficulty — a big house with stairs needs more movers than the raw cube suggests. Under-crewing blows the hourly estimate and the window; over-crewing burns margin.
3. **Assign trucks to jobs.** Match truck capacity to cube (don't send a 26-footer for a studio or a box truck for a 4-bedroom); account for trucks already committed to multi-day long-haul.
4. **Route local vs long-haul distinctly.** **Local** = hourly, often **multiple jobs per crew per day** with travel between — sequence to minimize deadhead. **Long-haul/interstate** = weight-and-distance, **multi-day**, a truck+crew committed out (or an **interline** hand-off) — it removes that truck/crew from the local board for the duration.
5. **Hold a utilization target with overrun buffer.** Utilization (billable crew-and-truck hours ÷ available) is the margin lever — an idle truck and crew is unrecoverable cost. But **buffer for overruns**: moves run long, and a board with zero slack cascades into missed windows. Target high utilization *with* slack, not 100% booked.
6. **Confirm authority before dispatching interstate (route to specialist).** An interstate household-goods job must have confirmed **USDOT/MC operating authority** before it goes on the board — route that check to the specialist.
7. **Publish the dispatch board and the flip conditions.** The board = job → crew → truck → window, with the utilization read and the 1-2 facts that would force a re-plan (a truck down, a crew short, a job running over).

## Worked example

> User: "Next week I have eight local jobs and one interstate move, three trucks, and my board keeps overrunning. How do I schedule it?"

- **Branch:** dispatch/capacity.
- **Interstate move:** confirm **USDOT/MC authority** with the specialist first — it commits one truck + crew multi-day (or interlines), so it comes off the local board for those days.
- **Local jobs:** size each crew to cube+access; sequence the eight across the remaining two trucks as **2-3 jobs/crew/day** with travel between, minimizing deadhead.
- **Utilization + buffer:** target ~80-85% utilization on the local trucks *with* a ~1-hour buffer per job — the overruns were from booking back-to-back with zero slack, so windows cascaded.
- **Board:** job → crew → truck → window published; the interstate truck flagged as committed out.
- **Flip conditions:** if a truck goes down or the interstate move slips, the two heaviest local jobs move to the next day rather than compressing the window.

## Guardrails

- **Size the crew to cube AND access** — raw cube under-counts a stairs/long-carry job; under-crewing blows the hourly estimate and the window.
- **Utilization is the margin — but never book to 100% with no buffer.** Overruns are the norm; a bufferless board cascades into missed delivery windows.
- **Local and long-haul are scheduled differently** — local is multi-job-per-day hourly; long-haul commits a truck+crew multi-day (or interlines). Don't schedule them the same way.
- **Never put an interstate job on the board before operating authority is confirmed** — route the authority check to the specialist first (regulated; not legal advice).
- Match **truck capacity to cube** — the wrong-size truck is either a second trip or wasted fuel/margin.
- Moving-software dispatch features (SmartMoving, MoveitPro, Elromco, Supermove) are volatile — carry a **retrieval date** and re-verify before relying on a specific capability.
