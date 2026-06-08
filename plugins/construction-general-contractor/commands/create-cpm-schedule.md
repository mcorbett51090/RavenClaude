---
description: "Build a CPM schedule for a construction project: define the WBS, create the activity list with durations, establish logic ties (FS/SS/FF), identify the critical path and float, integrate submittal lead times, and produce a schedule narrative."
argument-hint: "[project type and contract milestones, e.g. '18-month school addition, NTP June 1, substantial completion Nov 30 following year, P6 required']"
---

You are running `/construction-general-contractor:create-cpm-schedule`. Use the
`scheduling-engineer` discipline and the `cpm-scheduling` skill.

## Steps

1. **Define the WBS.** Organize by area/phase or CSI division per the contract structure.
   Match WBS levels to the owner's reporting requirements.

2. **Build the activity list.** For each work item: description (verb + noun), duration
   computed from quantity ÷ productivity (document the assumption), calendar (5-day, 6-day,
   or project-specific), resource loading if required.

3. **Establish logic ties.** Default to Finish-to-Start. Use Start-to-Start or Finish-to-Finish
   with documented lags only when real field constraints require them. Verify: every activity
   (except project start/finish) has both a predecessor and a successor.

4. **Calculate the critical path.** Run the forward pass (ES/EF) and backward pass (LS/LF).
   Identify activities with Total Float = 0 (critical) and ≤ 5 days (near-critical). List the
   top-3 critical-path drivers.

5. **Integrate submittal lead times.** Add submittal chains for long-lead items:
   `sub prepares → GC review → transmit → A/E review (contract period) → approval →
   procurement → fabrication → delivery → install`. If any chain is on the critical path,
   flag it immediately to the submittal-rfi-coordinator.

6. **Establish the baseline.** Lock the approved baseline (data date, project finish date,
   float summary). It is never overwritten.

7. **Produce the schedule narrative.** Identify the critical path, near-critical path, float
   by major work area, key milestones, and top-3 schedule risks.

8. **Emit the Structured Output block** with: project finish date vs. contract requirement,
   critical-path summary, float summary, top schedule risks, and handoffs
   (submittal-rfi-coordinator for submittal chain integration; gc-project-lead for milestone
   contractual implications; estimating-and-takeoff-analyst if acceleration costing is needed).
