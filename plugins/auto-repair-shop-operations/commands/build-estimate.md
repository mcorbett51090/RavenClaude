---
description: "Turn a write-up and a digital vehicle inspection into a defensible, DVI-backed repair estimate priced from the labor guide and the parts matrix, triaged sell-now vs sell-later, with declined work logged for follow-up (labor times/rates verify-at-use)."
argument-hint: "[vehicle + concern + inspection findings]"
---

You are running `/auto-repair-shop-operations:build-estimate`. Use `service-advisor-estimator` + the `estimate-and-dvi-workflow` skill.

> Operations decision-support, not legal/consumer-protection advice. Every labor time, rate, and part price is `[verify-at-use]`; state authorization/disclosure rules are `[verify-at-use]`. No customer PII — work in job types, never a customer record.

## Steps
1. Capture the verified complaint (customer's words + conditions) and confirm the diagnostic is authorized before pricing.
2. Traverse the **price a job (labor + parts matrix)** tree in `knowledge/auto-repair-shop-decision-trees.md`.
3. Attach DVI evidence to each recommended line; price labor = labor-guide hours × the shop rate and parts = cost × the matrix tier — each figure flagged `[verify-at-use]`.
4. Triage the lines **sell-now vs sell-later** (safety/failure now; wear items as dated deferred service) and note the authorization step.
5. Log any declined lines with urgency and part life for follow-up.
6. Emit using `templates/repair-order-workflow.md` + the Structured Output block. Hand rate/matrix questions to `auto-repair-shop-lead` and dispatch to `technician-workflow-manager`.
