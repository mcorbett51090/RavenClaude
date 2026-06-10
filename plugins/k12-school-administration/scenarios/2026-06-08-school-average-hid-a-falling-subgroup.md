---
scenario_id: 2026-06-08-school-average-hid-a-falling-subgroup
contributed_at: 2026-06-08
plugin: k12-school-administration
product: outcomes
product_version: "n/a"
scope: likely-general
tags: [outcomes, segmentation, equity, attendance]
confidence: medium
reviewed: false
---

## Problem

A leadership team saw flat school-average proficiency and concluded 'no change, hold course.' The risk: a school average blends subgroups, so it can stay flat while a specific subgroup falls — and the equity and intervention decision requires the disaggregated view, not the average (§3 #6).

## Context

- Organization: charter K-8 with multiple subgroups.
- Constraint: outcomes must be read segmented; an average can hide a falling group (§3 #6).
- The team reasoned from the single average.

## Attempts

- Tried: **disaggregated proficiency and growth by subgroup** before trusting the average. Outcome: the flat average masked one subgroup falling while another rose (§3 #6).
- Tried: **linked the falling subgroup to attendance.** Outcome: chronic absenteeism was concentrated in the falling subgroup — a leading signal (§3 #2 #5).
- Tried: **framed any special-ed cases for counsel** rather than deciding them on the team (§2).

## Resolution

The fix was a **targeted intervention and attendance-recovery push for the falling subgroup**, resourced by re-allocating per-pupil dollars — not 'hold course' on the average. The output was the segmented outcome read, the attendance link, and the targeted plan.

**Action for the next consultant hitting this pattern:** **read outcomes segmented before acting on a school average.** A flat average can hide a falling subgroup; disaggregate, link to attendance, and target intervention — routing special-ed to counsel. See Tree 3 and the `k12_school_administration_calc.py` `absenteeism` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
