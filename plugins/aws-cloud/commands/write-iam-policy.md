---
description: "Write a least-privilege IAM policy attached to a role, with a permission boundary; prefer federation over keys."
argument-hint: "[principal + exactly what it must do]"
---

You are running `/aws-cloud:write-iam-policy`. Use `aws-iam-identity-engineer` + the `aws-least-privilege-iam` skill.

## Steps
1. Scope actions + resource ARNs to the minimum.
2. Attach to a role (not a user/key); add a permission boundary.
3. Prefer IRSA/OIDC/SSO; route sensitive grants to security-engineering.
4. Emit the policy (from `templates/iam-least-privilege-policy.json`) + Structured Output block.
