---
description: "Stand up major-incident command — roles, severity, status cadence, and a timeline — driving to service restoration. Reach for this when a critical service is down broadly."
argument-hint: "[the outage]"
---

# Run major incident

You are running `/itsm-service-management:run-major-incident` for `$ARGUMENTS`. Run it the way the `incident-and-problem-manager` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Declare — confirm major-incident criteria; declare and set severity.
2. Assign roles — an incident commander + a comms lead, distinct from the technical responders.
3. Set the status cadence — regular stakeholder updates, even with 'nothing new'.
4. Keep the timeline — record events as they happen, for the review.
5. Restore, then convert — restore service; open a problem for the cause; schedule the blameless review.

## Output
A major-incident structure + timeline in the [`../templates/major-incident-runbook.md`](../templates/major-incident-runbook.md) shape. See [`../skills/triage-incident-vs-problem/SKILL.md`](../skills/triage-incident-vs-problem/SKILL.md).

## Guardrails
- A major incident needs a commander and comms, not just engineers (§2 #5) — silence is its own incident.
- Engineering reliability practice (SLOs, eng postmortem, chaos) → coordinate with `observability-sre`.
- End with next actions: owner + date.
