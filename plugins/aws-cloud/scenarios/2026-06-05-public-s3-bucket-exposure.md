---
scenario_id: 2026-06-05-public-s3-bucket-exposure
contributed_at: 2026-06-05
plugin: aws-cloud
product: s3
product_version: "n/a"
scope: likely-general
tags: [s3, public-access, block-public-access, data-exposure, scp]
confidence: high
reviewed: false
---

## Problem

A routine review (and an external researcher's heads-up) found an S3 bucket holding application exports readable by anyone on the internet — a public bucket policy had been added "temporarily" to let a partner pull a file, and never removed. The immediate question was "how exposed are we, and how do we close it without breaking the partner integration that's now depending on the public path?" This is a data-exposure finding, so the **security verdict** routes to `ravenclaude-core/security-reviewer` (CLAUDE.md §3); the plugin produces the remediation and the durable fix.

## Context

- Estate: a few dozen buckets across two accounts, **S3 Block Public Access not enabled at the account level**, no SCP preventing public-bucket policies, no org-wide guardrail. The exposure was one `"Principal":"*"` bucket policy.
- Constraint: a partner workflow had quietly started reading from the public URL, so flipping Block Public Access blind would break that integration — the fix has to *both* close the exposure *and* give the partner a non-public path, or it'll be reverted under pressure (exactly how the policy got added in the first place).
- "Public" has several independent vectors (bucket policy, ACLs, Block Public Access settings, account-level vs bucket-level) — closing one without the others leaves a hole.

## Attempts

- Tried: just deleting the public bucket policy. Outcome: closed *this* exposure but left the account able to create the next one, and broke the partner read (which then created pressure to re-open it). A point fix without a guardrail or a replacement path.
- Tried (scoping the blast radius first): ran **IAM Access Analyzer for S3** to enumerate *every* bucket with public or cross-account access — not just the reported one — so the remediation covered the whole estate, not the single finding. Outcome: found one more bucket with an over-broad cross-account grant.
- Tried (the durable fix): (1) replaced the partner's public read with a **scoped, time-bound presigned URL** (or a cross-account bucket policy limited to the partner's principal) so the integration kept working off a non-public path; (2) removed the public policy and enabled **S3 Block Public Access at the bucket and then the account level**; (3) added an **SCP** at the OU denying `s3:PutBucketPolicy`/`s3:PutBucketAcl` that would make a bucket public, so the mistake can't recur org-wide; (4) confirmed **GuardDuty/Macie** coverage so a future exposure or sensitive-data finding alerts. Outcome: exposure closed, partner unbroken, recurrence blocked at the org ceiling.

## Resolution

The exposure was a leftover public bucket policy on an account with **Block Public Access disabled and no SCP ceiling**. The durable fix was: enumerate the whole estate with Access Analyzer for S3 (not just the reported bucket), give the partner a scoped presigned/cross-account path so the integration survives, remove the public policy, enable **Block Public Access at the account level**, and add an **SCP** denying public-making S3 actions so it can't recur. Public exposure is an explicit, reviewed exception — never a default (CLAUDE.md §2).

**Action for the next engineer hitting this pattern:** **scope before you fix** — run Access Analyzer for S3 to find *every* public/cross-account bucket, not just the reported one. Before closing a public path that something depends on, **provide the non-public replacement** (presigned URL or principal-scoped cross-account policy) so the fix isn't reverted under pressure. Enable **S3 Block Public Access at the account level** and add an **SCP** denying the public-making actions so the mistake is blocked org-wide, not just deleted once. Confirm GuardDuty/Macie alerting. Route the exposure verdict to `security-reviewer`. `[verify-at-use]` current Block Public Access setting names and Access Analyzer for S3 capabilities against AWS docs.

**Sources (retrieved 2026-06-05):**
- AWS — S3 Block Public Access: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- AWS — IAM Access Analyzer for S3: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html
- AWS — Service Control Policies (SCPs) in Organizations: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html

These are the canonical AWS references; setting names and feature coverage are continuously deployed — `[verify-at-use]` before relying on a specific control name or capability.
