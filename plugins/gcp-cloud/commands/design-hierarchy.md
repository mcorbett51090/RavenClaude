---
description: "Design the GCP org/folder/project hierarchy and the org-policy guardrails to inherit."
argument-hint: "[org + workloads]"
---

You are running `/gcp-cloud:design-hierarchy`. Use `gcp-architect` + the `gcp-resource-hierarchy` skill.

## Steps
1. Traverse the hierarchy tree; lay out org->folders->projects by blast radius.
2. Choose org-policy constraints and place them for inheritance.
3. Set region/zone + RTO/RPO.
4. Hand build to terraform-iac.
5. Emit (from `templates/project-hierarchy.md`) + Structured Output block.
