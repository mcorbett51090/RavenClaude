# Capture job data at the point of work

**Status:** Pattern
**Domain:** Field data quality and operational intelligence
**Applies to:** `field-service-management`

---

## Why this exists

Every downstream decision in field-service operations depends on job-completion data captured
in the field: scheduling optimization uses job-duration data; truck-stock reorder uses parts-
used data; first-time-fix root-cause analysis uses failure codes; billing uses time-on-site and
materials records; coaching uses technician-level performance history. A job with missing or
inaccurate data is a decision made blind — and the damage compounds, because missing data from
one job contaminates the aggregate metrics used to drive policy.

The most common failure mode is not malicious — it is structural: technicians complete jobs and
move on; data entry happens in bulk at the end of the day (or is done by the dispatcher from
memory); failure codes are left blank because the dropdown is inconvenient; parts are logged
inconsistently because the truck-stock system and the job management system are not integrated.
The fix is not "train harder" — it is to make data capture at the point of work the easiest path.

## How to apply

- **Design the mobile workflow so the minimum required data is captured before job close.**
  Every job-close action in the field must require: actual start time, actual end time, parts
  used (part number + quantity), failure code (from a pre-defined list), and a one-line
  technician note. If the mobile app does not enforce these fields, they will be skipped.
- **Validate data quality before using metrics for decisions.** Before drawing conclusions from
  utilization, first-time-fix, or MTTR data, check: what % of jobs in the analysis period have
  all five required fields populated? If it's below ~90%, the metrics are unreliable. Fix the
  data discipline before the metric.
- **Make the point of work the only place job data is entered.** Dispatcher bulk-close, end-of-
  day data entry by office staff, and retroactive edits contaminate the dataset. The system
  should log the actual job-close timestamp from the mobile app — not the time a dispatcher
  closes the ticket.

**Do:**

- Require all five minimum job-completion fields before the mobile app allows job close.
- Track data-completeness rate as a dispatch KPI (% of jobs with all required fields populated).
- Integrate truck-stock and job management systems so parts usage automatically decrements
  truck inventory.

**Don't:**

- Allow dispatcher bulk-close of jobs at end of day — it destroys time-accuracy in the dataset.
- Use metrics derived from a dataset with > 10% missing failure codes or parts data without
  noting the data-quality caveat.
- Build a coaching scorecard from data that hasn't been validated for completeness and accuracy.

## Edge cases / when the rule does NOT apply

For very simple, single-task jobs (e.g., filter replacement on a residential visit), a minimal
data capture (job-close time, parts used) may be sufficient if failure codes are not relevant.
The minimum standard is: parts used and actual time on site, always. Even the simplest job must
capture these two fields to feed the utilization waterfall and truck-stock reorder correctly.

## See also

- [`./first-time-fix-is-the-master-metric.md`](./first-time-fix-is-the-master-metric.md)
- [`./the-technician-is-the-brand-at-the-door.md`](./the-technician-is-the-brand-at-the-door.md)
- [`../skills/technician-productivity-and-first-time-fix/SKILL.md`](../skills/technician-productivity-and-first-time-fix/SKILL.md)

## Provenance

Reflects the field data quality discipline common to all FSM platforms: ServiceTitan, Salesforce
Field Service, and IFS all enforce minimum job-completion data at mobile close. The productivity-
analytics literature in field service consistently cites data-completeness as the primary
prerequisite for reliable utilization and first-time-fix measurement. `[verify-at-use]`

---

_Last reviewed: 2026-06-08 by `claude`._
