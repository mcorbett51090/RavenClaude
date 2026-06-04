---
description: "Drive a live incident or write its postmortem: severity, roles, comms cadence, mitigate-first, then a blameless postmortem."
argument-hint: "[incident symptom + impact, or 'postmortem for <incident>']"
---

You are running `/observability-sre:run-incident`. Use `incident-commander` + the `incident-response` skill.

## Steps (live)
1. Classify severity (use `templates/incident-severity-matrix.md`); assign IC/ops/comms.
2. Set a comms cadence; mitigate before root-causing (route rollback to devops-cicd).
3. Keep a running timeline.
## Steps (after)
4. Write the blameless postmortem (from `templates/postmortem.md`) with owned, dated action items.
5. Emit + Structured Output block.
