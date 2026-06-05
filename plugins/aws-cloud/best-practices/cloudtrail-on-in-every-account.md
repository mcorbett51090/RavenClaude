# Enable CloudTrail in every account from day one

**Status:** Absolute rule
**Domain:** AWS security / compliance
**Applies to:** `aws-cloud`

---

## Why this exists

CloudTrail records every API call made to your AWS account — who called what service, from where, when. Without it you have no audit trail, no forensics capability, and no way to reconstruct a breach or an accidental deletion. You cannot retroactively enable CloudTrail and recover the past; every hour without it is a gap in your audit log that regulators and your incident-response process will notice. Disabling or restricting CloudTrail is itself one of the first actions an attacker takes after gaining access, so centralized, immutable storage is essential.

## How to apply

Create an organization-level **management trail** that covers all regions and all accounts in your Organizations hierarchy. Store logs in a dedicated S3 bucket in your log-archive account (private, bucket policy denies CloudTrail from being disabled, no public access, MFA-delete enabled, lifecycle to Glacier after 90 days). Enable **log file validation** to detect tampering.

```json
{
  "IsMultiRegionTrail": true,
  "IncludeGlobalServiceEvents": true,
  "EnableLogFileValidation": true,
  "S3BucketName": "org-cloudtrail-logs-<log-archive-account-id>",
  "CloudWatchLogsLogGroupArn": "arn:aws:logs:us-east-1:<account>:log-group:cloudtrail"
}
```

**Do:**
- Create one org-level trail in the management account that covers every member account.
- Store in a dedicated S3 bucket in your log-archive account with bucket policy that denies `DeleteTrail` and `StopLogging` from member accounts.
- Enable log file validation (`--enable-log-file-validation`).
- Send logs to CloudWatch Logs for near-real-time alerting on sensitive API calls (e.g., `DeleteBucket`, `PutBucketAcl`, root login).
- Archive to S3 Glacier/IA after 90 days; retain for 1–7 years per compliance requirements.

**Don't:**
- Let member accounts create separate trails that can be deleted by their own admins.
- Store trail logs in the same account whose activity they record (conflict of interest if that account is compromised).
- Leave S3 bucket open to public or allow `s3:DeleteObject` without MFA delete.
- Skip `IncludeGlobalServiceEvents` — IAM and STS calls are global and are the most important to capture.

## Edge cases / when the rule does NOT apply

There are no exceptions to the enablement requirement. Log volume cost can be reduced by routing to S3 Infrequent Access storage class and not duplicating trails, but the trail itself must exist in every account from the moment it is created.

## See also

- [`../agents/aws-iam-identity-engineer.md`](../agents/aws-iam-identity-engineer.md) — owns the bucket policy and SCP guardrail that prevents CloudTrail from being disabled
- [`../agents/aws-ops-finops-engineer.md`](../agents/aws-ops-finops-engineer.md) — owns the CloudWatch metric filters and alarms over trail events
- [`./scp-guardrails-set-the-ceiling.md`](./scp-guardrails-set-the-ceiling.md) — the SCP that prevents member accounts from disabling the trail

## Provenance

Codifies AWS Security Pillar SEC01-BP01 (account-level logging) and CIS AWS Benchmark control 3.x (CloudTrail enabled in all regions). Standard multi-account landing zone practice.

---

_Last reviewed: 2026-06-05 by `claude`_
