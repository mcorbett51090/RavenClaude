---
scenario_id: 2026-06-05-over-permissioned-role-wildcard
contributed_at: 2026-06-05
plugin: aws-cloud
product: iam
product_version: "n/a"
scope: likely-general
tags: [iam, least-privilege, wildcard, access-analyzer, permission-boundary]
confidence: high
reviewed: false
---

## Problem

A microservice's task role carried an inline policy of `{"Effect":"Allow","Action":"*","Resource":"*"}` — full administrator — because "we kept hitting AccessDenied during the build and someone widened it to ship." A security review flagged it as the single largest finding in the account: a compromise of one task would be a compromise of the whole account. The owner's worry was the inverse: tightening it would break the service in a way nobody could predict, because nobody knew what the service actually used.

## Context

- Estate: a handful of ECS-on-Fargate services in one prod account, no permission boundaries, no SCP ceiling. The wildcard role was assumable by the task and (worse) had no `aws:SourceArn`/confused-deputy condition.
- Constraint: the team had no inventory of the API calls the service makes — the wildcard had been masking every missing grant for months, so a hand-written least-privilege policy would be guesswork and would regress in production.
- This is a posture finding, so the **security verdict** routes to `ravenclaude-core/security-reviewer` (CLAUDE.md §3); the IAM specialist produces the remediation, not the sign-off.

## Attempts

- Tried: hand-writing a "minimal" policy from the team's memory of what the service does. Outcome: rejected — it was still a guess, and a guessed deny in prod is an outage. Memory is not an access inventory.
- Tried (the move that worked): used the **observed-access** path instead of guessing. Enabled CloudTrail data/management events for the account (already on per the house rule), then generated a policy from the role's *actual* recent activity — IAM Access Analyzer can generate a least-privilege policy from CloudTrail history for a role. Reviewed the generated policy, scoped `Resource` ARNs to the specific tables/buckets/queues the service touched, and added the missing confused-deputy `aws:SourceArn` condition. Outcome: a grounded candidate policy backed by real usage, not memory.
- Tried (the containment that made it safe): attached a **permission boundary** to the role capping it at the service's domain (its own DynamoDB tables + its SQS queue + its KMS key) *before* swapping the wildcard, and added an **SCP** at the OU denying the account from ever creating a `*:*` policy again. Outcome: even a future widening can't exceed the boundary, and the wildcard mistake can't recur at the org level.

## Resolution

The fix was **observed-access generation + a boundary ceiling**, not a hand-edited policy. Access Analyzer's policy-from-CloudTrail gave a candidate grounded in real calls; scoping the resource ARNs and adding the confused-deputy condition tightened it; the permission boundary and the SCP made the least-privilege state *durable* (a later "just widen it to ship" can't exceed the boundary, and `*:*` is denied org-wide). The wildcard was replaced during a low-traffic window with CloudWatch on the role's `AccessDenied` count so any missed grant surfaced as an alarm, not an incident.

**Action for the next engineer hitting this pattern:** don't hand-author a least-privilege replacement from memory — **generate it from observed access** (Access Analyzer over CloudTrail) so the policy reflects what the workload actually calls, then scope the `Resource` ARNs and add the confused-deputy condition. Wrap it in a **permission boundary** + an **SCP** so the tightened state survives the next deadline. Watch the role's `AccessDenied` metric after the swap. A `*` action or `*` resource is always a finding (CLAUDE.md §2). `[verify-at-use]` Access Analyzer's policy-generation feature set and CloudTrail lookback window against current AWS IAM docs before relying on the generated policy.

**Sources (retrieved 2026-06-05):**
- AWS IAM Access Analyzer — policy generation from CloudTrail and least-privilege guidance: https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-policy-generation.html
- AWS IAM best practices (least privilege, permission boundaries): https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

These are the canonical AWS IAM references; feature details are continuously deployed — `[verify-at-use]` before quoting a specific capability or limit.
