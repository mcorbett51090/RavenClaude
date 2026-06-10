# K-12 School Administration Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/k12_school_administration_calc.py`](../scripts/k12_school_administration_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Enrollment and ADA are dollars (§3 #1 #2)

```
funding = enrollment * per_pupil_rate * ada_rate
per_attendance_point = enrollment * per_pupil_rate * 0.01   # value of 1 ADA point
```

Per-pupil funding makes enrollment the revenue base and every attendance point real money; ADA is the rare lever that moves both the budget and the outcome.

## 2. Staffing fits the budget envelope (§3 #3)

```
teachers_needed = enrollment / target_ratio
salary_cost     = teachers_needed * avg_teacher_cost
variance        = salary_cost - current_salary_budget
```

A target ratio is an expense commitment; model the FTE and dollar variance against the funded envelope before committing — staffing is the largest controllable line.

## 3. Chronic absenteeism is an early signal (§3 #5)

```
chronic_rate = students_at_or_over_threshold / enrolled
recovery_upside = recoverable_attendance_points * per_attendance_point
```

Chronic absenteeism predicts disengagement and dropout long before grades show it; the year-end count is a post-mortem, so flag and intervene early.

## 4. Allocate per-pupil to need, not history (§3 #4)

```
allocation = per_pupil_envelope directed to highest-need subgroups/intervention
```

Rolling last year's distribution forward freezes resources against last year's problem; allocate to where need and impact are highest.
