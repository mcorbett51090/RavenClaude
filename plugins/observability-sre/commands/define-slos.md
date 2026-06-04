---
description: "Define user-centric SLIs/SLOs and an error-budget policy for a service, with multi-window burn-rate alerts."
argument-hint: "[service + user expectations]"
---

You are running `/observability-sre:define-slos`. Use `sre-reliability-engineer` + the `slo-and-error-budgets` skill.

## Steps
1. Pick SLIs measured at the user boundary (availability, latency, correctness).
2. Traverse the SLO-target tree; set targets and derive budgets.
3. Write the ship-vs-freeze error-budget policy.
4. Define multi-window burn-rate alerts tied to runbooks.
5. Emit the SLO definition (from `templates/slo-definition.md`) + Structured Output block.
