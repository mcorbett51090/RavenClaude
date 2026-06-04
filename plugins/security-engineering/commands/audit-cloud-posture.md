---
description: "Audit a cloud account for misconfigurations (public exposure, IAM wildcards, missing encryption, open ports) and propose preventive guardrails."
argument-hint: "[cloud + scope]"
---

You are running `/security-engineering:audit-cloud-posture`. Use `cloud-security-engineer` + the `secrets-management` skill where relevant.

## Steps
1. Hunt misconfigurations (public storage, open admin ports, unencrypted, wildcard IAM).
2. Rank by blast radius; propose least-privilege + exposure closures.
3. Recommend preventive policy-as-code guardrails (wire via terraform-iac).
4. Route verdicts to security-reviewer.
5. Emit the audit (from `templates/cloud-posture-audit.md`) + Structured Output block.
