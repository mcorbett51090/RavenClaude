---
name: aws-least-privilege-iam
description: "Write least-privilege AWS IAM: scope actions and resource ARNs to exactly what's needed, attach to roles (not users/keys), prefer federation (IRSA/OIDC) and Identity Center, and cap with permission boundaries + SCPs."
---

# AWS Least-Privilege IAM

## Roles + federation, not keys
Instance/task roles, **IRSA** (EKS), **OIDC** (CI). Humans -> **Identity Center (SSO)**. A long-lived access key is the top breach vector.

## Minimum, then prove it
Scope `Action` + `Resource` ARNs tightly. Use Access Analyzer + last-used to remove unused grants. `*`/`*` is a finding.

## Ceilings
**Permission boundaries** (per-role cap) + **SCPs** (org cap) = defense in depth.

## Route the verdict
Produce the policy + residual risk; `security-engineering`/`security-reviewer` clears sensitive grants.
