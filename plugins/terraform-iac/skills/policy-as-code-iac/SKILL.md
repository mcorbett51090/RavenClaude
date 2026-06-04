---
name: policy-as-code-iac
description: "Gate infrastructure with policy-as-code: evaluate the Terraform plan JSON with OPA/Conftest (or Sentinel) to reject misconfigurations — public exposure, wildcard IAM, missing tags, unencrypted resources — before apply, preventively."
---

# Policy-as-Code for IaC

## Evaluate the plan
Run `terraform plan -out` -> `terraform show -json` -> evaluate with **OPA/Conftest** (or Sentinel). Fail the pipeline on violations **before apply**.

## Common guardrails
- No public storage / `0.0.0.0/0` to admin ports
- No wildcard IAM (`*` action/resource)
- Required tags present
- Encryption at rest enabled

## Preventive > detective
Blocking the misconfigured plan beats auditing the breached resource later. Route the security **verdict** to `security-engineering`; the gate just enforces the rule.
