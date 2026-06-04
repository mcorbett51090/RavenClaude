---
name: gcp-resource-hierarchy
description: "Design the GCP resource hierarchy: organization -> folders (env/dept) -> projects (app/workload), and set org-policy constraints (allowed regions, disable SA key creation, no external IP, OS Login) high in the tree for inheritance."
---

# GCP Resource Hierarchy

## Organization -> Folders -> Projects
Folders by env/department; **projects** by app/workload (the blast-radius + billing unit). IAM and org policy **inherit** down the tree.

## Org policy guardrails (set high)
- restrict allowed regions
- **disable service-account key creation**
- forbid external IPs
- require OS Login

Preventive, inherited safety beats per-project vigilance. Build with `terraform-iac`.
