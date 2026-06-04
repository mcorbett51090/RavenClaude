---
description: "Add policy-as-code guardrails on the plan: reject public exposure, wildcard IAM, missing tags, unencrypted resources before apply."
argument-hint: "[compliance rules to enforce]"
---

You are running `/terraform-iac:add-policy-guardrails`. Use `iac-policy-and-state-engineer` + the `policy-as-code-iac` skill.

## Steps
1. Express each rule as OPA/Conftest (or Sentinel) on the plan JSON.
2. Wire the gate before apply (coordinate CI with devops-cicd).
3. Route the security verdict to security-engineering.
4. Emit the policies (pattern in `templates/plan-policy-gate.md`) + Structured Output block.
