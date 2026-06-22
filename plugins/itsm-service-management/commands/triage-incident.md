---
description: "Classify an issue as incident, problem, or major incident and route it. Reach for this when something is broken or keeps breaking."
argument-hint: "[the issue / symptom]"
---

# Triage incident

You are running `/itsm-service-management:triage-incident` for `$ARGUMENTS`. Run it the way the `incident-and-problem-manager` would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §2.

## Steps (traverse top-to-bottom; do not skip)
1. Major incident? — check criteria (broad impact / critical service / high urgency); if yes, declare command.
2. Incident or problem? — restore-now = incident; remove-cause = problem; recurring = both.
3. Prioritize the incident — impact × urgency; restore with the fastest safe path (workaround counts).
4. Drive the problem to RCA — open a problem record + known error for the cause.
5. Feed the fix forward — a permanent fix usually needs a change.

## Output
A classification and the right record(s) opened. See [`../skills/triage-incident-vs-problem/SKILL.md`](../skills/triage-incident-vs-problem/SKILL.md) and the routing tree in [`../knowledge/itsm-decision-trees.md`](../knowledge/itsm-decision-trees.md).

## Guardrails
- An incident restores service; a problem removes the cause (§2 #1) — never one number for both.
- Engineering SRE/on-call/SLOs → `observability-sre`; a security incident → `cybersecurity-grc`.
- End with next actions: owner + date.
