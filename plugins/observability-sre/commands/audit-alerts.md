---
description: "Audit alert rules for actionability and noise; replace cause-based alerts with symptom/burn-rate alerts."
argument-hint: "[current alerting description or rules]"
---

You are running `/observability-sre:audit-alerts`. Use `sre-reliability-engineer`.

## Steps
1. Classify each alert: actionable? symptom or cause? tied to an SLO? fired & acted on recently?
2. Delete the noise; convert salvageable cause-alerts to symptom/burn-rate.
3. Ensure each surviving alert links a runbook.
4. Emit the reviewed set (use `templates/alert-rule-review.md`) + Structured Output block.
