---
description: "Write least-privilege GCP IAM bindings (predefined/custom roles, federation not key files) at the correct hierarchy level."
argument-hint: "[principal + what it must do]"
---

You are running `/gcp-cloud:write-iam-binding`. Use `gcp-iam-engineer` + the `gcp-least-privilege-iam` skill.

## Steps
1. Choose the predefined/custom role matching the job (no primitive).
2. Bind at the right node; add IAM Conditions if needed.
3. Use WIF/Workload Identity, not key files.
4. Route sensitive grants to security-engineering.
5. Emit (from `templates/iam-binding.md`) + Structured Output block.
