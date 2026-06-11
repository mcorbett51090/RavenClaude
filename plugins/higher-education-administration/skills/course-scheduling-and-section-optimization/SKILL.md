---
name: course-scheduling-and-section-optimization
description: "Optimize course scheduling and section offerings — match section capacity to demand, relieve gateway/bottleneck-course throttles on completion, cut empty-seat cost, and align faculty load to credit-hour production without harming time-to-degree."
---

# Course Scheduling & Section Optimization

**Purpose:** schedule sections so students can get the courses they need (protecting time-to-degree
and completion) while cutting the cost of empty seats — a capacity-vs-demand optimization.

---

## Steps

### 1. Map demand against capacity

For each course, compare seats offered to demand (registrations + unmet demand from waitlists and
degree-audit needs). Two failure modes show up:

| Failure | Symptom | Cost |
|---|---|---|
| Bottleneck | demand >> capacity on a gateway course | throttles completion, extends time-to-degree |
| Empty sections | capacity >> demand | wasted instructional cost |

### 2. Prioritize the gateway/bottleneck courses

A required gateway course that students can't get into delays the entire degree behind it — and is a
direct retention/completion risk, not just an inconvenience. Relieving bottleneck capacity is usually
the highest-leverage scheduling move.

### 3. Cut empty-seat cost without harming access

Consolidate chronically under-filled sections, but check that consolidation doesn't recreate a
bottleneck or push a required course to a time that blocks degree progress.

### 4. Align faculty load to credit-hour production

Connect section size and faculty load to credit-hour production and program contribution margin (the
program-viability skill consumes this). Fill rate is the link between scheduling and the budget.

### 5. Re-measure

Track section fill rate, unmet demand on gateway courses, and the effect on time-to-degree. Use
[`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py) for fill-rate/utilization math.

---

## Output

A scheduling analysis (bottleneck + empty-section findings), a re-allocation, and the time-to-degree
and cost effects. Frames into the program-viability and budget-model work.
