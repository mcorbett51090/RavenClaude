---
name: cpm-scheduling
description: "Build and maintain a CPM schedule: activity list, durations, logic ties (FS/SS/FF), critical-path calculation, float analysis, baseline establishment, weekly updates, look-ahead schedules, delay analysis (as-planned vs. as-built, TIA), and recovery scheduling. Tool-agnostic; notes P6 and MS Project specifics."
---

# CPM Scheduling

**Purpose:** produce a CPM schedule that is the project's primary contract management tool —
not a Gantt chart decoration — and maintain it as a living document from baseline to closeout.

---

## Step 1 — Build the Work Breakdown Structure (WBS)

1. Organize by area (building/floor/zone) + phase (sitework, foundations, structure, enclosure,
   MEP rough-in, finishes, commissioning) OR by CSI division — whichever matches the contract
   milestones.
2. Keep activities at the right level: too coarse (one activity per trade) → can't manage it;
   too fine (every bolt torqued) → can't maintain it. Rule of thumb: activity duration 1–15
   working days.

## Step 2 — Activity list and durations

For each activity:
- **Description:** clear, starts with a verb (Install, Pour, Frame, Erect).
- **Duration:** computed from quantity ÷ productivity (e.g., 200 CY concrete ÷ 50 CY/crew-day
  = 4 days). Document the productivity assumption. Don't guess.
- **Calendar:** standard 5-day, 6-day, or project calendar with holidays and weather days.
- **Resources:** crew type and size (if resource-loading).

## Step 3 — Logic ties

**Every activity must have a predecessor AND a successor, except the project start and project
finish milestones.**

| Dependency type | When to use |
|---|---|
| Finish-to-Start (FS) | Default: B cannot start until A finishes |
| Start-to-Start (SS) with lag | B can start X days after A starts (concurrent work) |
| Finish-to-Finish (FF) with lag | B must finish within X days of A finishing |

- Document why each non-FS relationship exists.
- Use lags sparingly and only for real constraints (cure time, permit lead time). Hidden float
  disguised as a lag is a CPM anti-pattern.

## Step 4 — Critical-path calculation

The CPM algorithm (forward pass / backward pass):

- **Forward pass:** Early Start (ES) and Early Finish (EF) for each activity.
- **Backward pass:** Late Start (LS) and Late Finish (LF).
- **Total Float (TF)** = LS − ES = LF − EF. Activities with TF = 0 are on the critical path.
- **Free Float (FF)** = ES(successor) − EF(activity). Float that belongs to this activity.

Near-critical path: activities with TF ≤ 5 days. Flag these — they become critical with any
small disruption.

## Step 5 — Baseline establishment

1. Get the baseline approved (owner, GC PM, major subs) before work starts.
2. Save the baseline as a locked copy. Never overwrite the baseline.
3. Record the data date (status date) of the baseline.
4. Update against the baseline — the delta between baseline and current is the schedule variance.

## Step 6 — Weekly schedule updates

1. Enter actual start and finish dates for completed activities.
2. For in-progress activities: enter actual start + remaining duration (or % complete).
3. Revise logic ties only where field conditions have genuinely changed (document the reason).
4. Run the CPM recalculation. Identify the new critical path.
5. Report: SPI (Schedule Performance Index = earned value ÷ planned value if cost-loaded),
   critical-path change from last update, float trend.

## Step 7 — Look-ahead schedule

Extract from the CPM: all activities scheduled to start or continue in the next 3 (or 6) weeks.
Field format: date rows, trade columns, activity descriptions. Add:
- Predecessor completions required this week
- Material deliveries expected
- Submittals whose approval is needed before work starts
- Open RFIs blocking this scope

## Step 8 — Delay analysis

When a delay occurs, document it real-time (don't reconstruct later):

| Method | When to use |
|---|---|
| As-planned vs. as-built | Simple projects; compare baseline dates to actual dates by activity |
| Windows (contemporaneous path) | Complex projects; divide the project into analysis windows, analyze each window separately |
| Time Impact Analysis (TIA) | For prospective or concurrent delay; model the impacted baseline with a fragnet |

For each delay:
- **Excusable / non-compensable** — force majeure, owner-caused weather (owner grants time only)
- **Excusable / compensable** — owner-caused delay (owner grants time + costs)
- **Non-excusable** — contractor-caused (no time extension; may owe LDs)
- **Concurrent delay** — both parties contributed; entitlement is jurisdiction-specific

## Submittal integration in CPM

Add submittal lead times as a chain of activities:
`Sub prepares submittal → GC review → Transmit to A/E → A/E review (contract days) → Approval
→ Procurement → Fabrication → Delivery → Installation`

These chains often run 8–20 weeks for MEP equipment. If they're not in the schedule, you
won't see the procurement squeeze coming.

---

## Anti-patterns

- Activities with no predecessor or no successor (except start/finish).
- Float disguised as inflated durations or hidden lags.
- A "schedule update" that only extends the finish date without a recovery narrative.
- Delay analysis done from memory months after the fact — contemporaneous documentation is
  the only defensible record.

## Output

A CPM schedule in P6 (.xer) or MS Project (.mpp), plus a schedule narrative: critical path,
float summary, key milestones, top-3 schedule risks.
