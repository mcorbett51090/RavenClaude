---
name: technician-productivity-and-first-time-fix
description: "Diagnose and improve technician utilization, first-time-fix rate, MTTR, and callback rate — including root-cause segmentation by parts/skill/information/diagnosis, the utilization waterfall, and the coaching framework to address each failure category."
---

# Technician Productivity and First-Time-Fix

**Purpose:** identify what is actually reducing first-time-fix rate and technician utilization,
segment root causes by category, and route each category to the right fix — training, parts,
scheduling, or data quality.

---

## Steps

### 1. Establish the metric baseline

Before diagnosing, measure and validate the four core metrics using `scripts/fsm_calc.py`:

| Metric | Formula | Healthy range (context-dependent) |
|---|---|---|
| Technician utilization | `billable_hours / available_hours` | 70–80% (field service typical) |
| First-time-fix rate | `jobs_resolved_first_visit / total_jobs` | ≥ 75–85% (varies by equipment type) |
| MTTR | `sum(resolution_times) / count(jobs)` | Benchmark by equipment type |
| Callback rate | `callbacks_within_30_days / jobs_completed` | < 5% target; > 10% is a flag |

**Data-quality check first:** before drawing conclusions, verify that technicians are logging
actual start/end times (not dispatcher bulk-close), parts used, and failure codes on every job.
Unreliable data produces misleading metrics — fix the data before the metric.

### 2. Build the utilization waterfall

Decompose available hours into categories:

```
Available hours (paid hours on clock)
  └─ Scheduled hours (assigned to jobs)
       └─ Travel time (drive to/between jobs)
       └─ Admin time (job notes, parts ordering, team meetings)
       └─ Wait time (waiting for access, parts, customer)
       └─ Billable hours (productive on-site work)
  └─ Unscheduled time (no job assigned — scheduling gap or downtime)
```

Each drag category has a different owner and fix:

| Drag | Fix owner |
|---|---|
| Excessive travel | `dispatch-and-scheduling-engineer` (territory redesign) |
| Admin time > 15% | Workflow/mobile-app improvement; job-note templates |
| Wait-for-parts | `parts-and-inventory-analyst` (truck-stock or pre-pull) |
| Scheduling gaps | `dispatch-and-scheduling-engineer` (fill-rate / buffer optimization) |
| Data-entry errors | Dispatcher audit; mobile app field validation |

### 3. Segment first-time-fix failures by root cause

For each first-time-fix miss, classify the failure:

| Root cause | Diagnostic question | Fix |
|---|---|---|
| Parts unavailable | Was the part not on the truck and not pre-pulled? | `parts-and-inventory-analyst` |
| Skill/cert mismatch | Was the technician dispatched outside their skill authorization? | `dispatch-and-scheduling-engineer` + training |
| Misdiagnosis | Did the technician assess wrong and fix the wrong component? | Training; diagnostic checklist |
| Incomplete job information | Was the symptom description or equipment history missing at dispatch? | Mobile data capture; job-intake triage |
| Customer expectation | Did the customer define the job differently than the technician completed it? | Job-scope confirmation at booking |

Calculate the % of first-time-fix misses in each category. The category with the highest share
gets the first improvement action.

### 4. Analyze callback rate by segment

A callback is a job where the customer called back within 30 days for the same or related issue.

Segment callbacks by:
- **Technician:** is one tech generating a disproportionate share of callbacks? → coaching.
- **Job type / equipment model:** is a specific job type generating callbacks? → training, parts,
  or diagnostic-procedure issue.
- **Failure mode:** is the repeat failure the same component? → parts quality or repair method.
- **Time-to-callback:** callbacks within 7 days often indicate an incomplete fix; callbacks
  in 15–30 days may indicate parts failure or an unrelated second failure.

### 5. Design the coaching framework

For technicians with below-threshold performance on first-time-fix or callbacks:

1. **Diagnose first.** Is the root cause parts (not their fault), scheduling (dispatched out of
   skill), or genuine skill/judgment gaps?
2. **Only coach what the technician controls.** Don't hold a technician accountable for parts-
   delay failures or skill-mismatch dispatches.
3. **Structured 1:1:** review the technician's last 30 days of metrics — utilization, first-time-
   fix rate, MTTR, callbacks. Walk through the specific miss events together.
4. **Training-to-gap mapping:** identify the 1–2 highest-impact skill gaps from the first-time-fix
   segment analysis. Design targeted training, not a generic refresher.
5. **30-day improvement check:** set a specific, measurable target for the gap (e.g., "first-time-
   fix on refrigerant jobs from 55% to 75% in 30 days") and check progress at the next 1:1.

---

## Anti-patterns

- Drawing conclusions from unvalidated job-completion data (bulk dispatcher close, missing
  failure codes).
- A coaching program that doesn't distinguish parts/scheduling failures from skill failures.
- Treating a systemic failure (all technicians miss on one job type) as individual underperformance.
- Utilization targets that ignore travel-time geography.
- Callback programs that don't segment by technician, job type, and failure mode.

---

## Output

A productivity diagnostic report with: the metric baseline (utilization waterfall, first-time-fix
segment breakdown, MTTR and callback analysis), the root-cause categories ranked by impact, the
routing of each non-skill root cause to the right specialist, and the coaching plan for the
skill-gap portion. Cite the job-count basis for each calculation.
