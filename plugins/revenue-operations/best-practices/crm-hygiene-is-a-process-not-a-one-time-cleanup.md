# CRM hygiene is a process, not a one-time cleanup

**Status:** Pattern
**Domain:** CRM operations
**Applies to:** `revenue-operations`

---

## Why this exists

A CRM cleaned once and left unguarded will return to its baseline entropy within two quarters.
Entropy is not a function of rep malice; it is a function of the absence of structure. Without
required fields, validation rules, and a recurring audit loop, the CRM accumulates stale deals,
blank required fields, misadvanced stages, and duplicate records as a natural consequence of
sales activity — not as an exception to it.

"CRM hygiene project" is an oxymoron. A project has a start date, an end date, and a done state.
CRM hygiene has no done state; it has a current state and a maintenance process. The only durable
form of CRM hygiene is: automation that prevents dirty data from entering (validation rules,
required fields), automation that flags entropy as it accumulates (stale-deal aging alerts, field-
completeness dashboards), and a recurring human review cadence that addresses exceptions the
automation cannot.

## How to apply

Design a CRM hygiene program that has three components, all active at the same time:

1. **Prevention (automation):**
   - Required fields at key stage transitions (Amount required before Stage 3; Next Step required
     before Proposal; Close Date must be in the future for open deals).
   - Validation rules that enforce stage-exit criteria mechanically.
   - Duplicate-prevention rules that block record creation when a match is found above a threshold.
   - Workflow triggers that flag a deal when no activity has been logged in > N days.

2. **Detection (monitoring):**
   - A weekly hygiene dashboard: stale deals (no activity > 30/60/90 days), missing required
     fields by rep, stage-age outliers, Commit deals with no recent activity.
   - A monthly duplicate-rate report (leads and contacts).
   - A quarterly field-completeness audit: what percentage of opportunities have all required
     fields populated at each stage?

3. **Response (human cadence):**
   - Weekly: manager reviews flagged deals in the hygiene dashboard; reps address Red items before
     the next pipeline review.
   - Monthly: RevOps reviews field-completeness and duplicate reports; exceptions are escalated.
   - Quarterly: a formal hygiene review; stale deals are closed or archived; duplicates are merged;
     validation rules are reviewed for gaps.

**Do:**

- Build prevention before running the first cleanup sprint — otherwise you clean and immediately
  re-dirty the data.
- Tie the hygiene cadence to the pipeline review cadence — a rep should never attend a pipeline
  review with Red hygiene items outstanding.
- Publish the hygiene scores by rep and by segment — transparency drives behavior without requiring
  mandates.
- Treat a hygiene-automation gap (a recurring problem that is not caught by a validation rule) as
  a rule-design failure, not a rep failure.

**Don't:**

- Declare a hygiene sprint "done" and remove the monitoring.
- Build validation rules without change-management communication — reps blocked by a rule they
  don't understand will find workarounds.
- Run a deduplicate project without building duplicate-prevention rules afterward — you will need
  to run the project again in six months.
- Accept "we'll clean it after the quarter" as a hygiene posture — stale data at the end of a
  quarter is when the forecast is most critical.

## Edge cases / when the rule does NOT apply

Immediately after a CRM migration or a major data import, a one-time cleanup sprint is appropriate
and necessary — but it is the starting state for the process, not a substitute for it. The sprint
removes the historical debt; the process prevents future accumulation. Without the process that
follows, the sprint's value depreciates within two quarters.

## See also

- [`./stages-are-exit-criteria-not-vibes.md`](./stages-are-exit-criteria-not-vibes.md)
- [`./one-definition-of-pipeline.md`](./one-definition-of-pipeline.md)
- [`../skills/pipeline-hygiene-and-stage-definitions/SKILL.md`](../skills/pipeline-hygiene-and-stage-definitions/SKILL.md)
- [`../agents/crm-operations-architect.md`](../agents/crm-operations-architect.md)
- [`../commands/audit-crm-hygiene.md`](../commands/audit-crm-hygiene.md)

## Provenance

Codifies the RevOps community consensus on CRM hygiene as a continuous process rather than a
project, consistent with the Salesforce Trailhead CRM hygiene guidance and the RevOps Alliance
data-quality playbook.

---

_Last reviewed: 2026-06-08 by `claude`._
