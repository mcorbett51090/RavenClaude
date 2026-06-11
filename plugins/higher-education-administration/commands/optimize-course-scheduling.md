---
description: "Optimize course scheduling — match section capacity to demand, relieve gateway/bottleneck-course throttles on completion, cut empty-seat cost, and align faculty load to credit-hour production without harming time-to-degree."
---

# /optimize-course-scheduling

Spawn `academic-operations-and-compliance-coordinator` (with the program-portfolio strategist for the
credit-hour economics) to optimize the schedule.

## What it does

1. Maps section capacity vs. demand (registrations + unmet/waitlist).
2. Identifies bottleneck gateway courses (a completion/retention risk) and empty sections (wasted cost).
3. Re-allocates capacity without harming access or time-to-degree.
4. Links section size and faculty load to credit-hour production and program margin.

## Usage

```
/optimize-course-scheduling
```

Then share section fill rates and any gateway-course waitlist/unmet demand. The agent applies
[`course-scheduling-and-section-optimization`](../skills/course-scheduling-and-section-optimization/SKILL.md).

## Good inputs

- Section capacities and enrollments; gateway-course waitlists.
- Faculty load constraints.
