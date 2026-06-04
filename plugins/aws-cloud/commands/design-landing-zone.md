---
description: "Design a multi-account AWS landing zone: account topology by blast radius, SCP guardrails, region/AZ + resilience."
argument-hint: "[org + workloads]"
---

You are running `/aws-cloud:design-landing-zone`. Use `aws-architect` + the `aws-account-strategy` skill.

## Steps
1. Traverse the account-strategy tree; lay out accounts by blast radius.
2. Define SCP guardrails; decide Control Tower or not.
3. Set region/AZ + RTO/RPO.
4. Hand build to terraform-iac.
5. Emit the plan (from `templates/landing-zone-plan.md`) + Structured Output block.
