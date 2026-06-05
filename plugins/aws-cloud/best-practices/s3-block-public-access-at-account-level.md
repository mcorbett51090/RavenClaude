# Enable S3 Block Public Access at the account level

**Status:** Absolute rule
**Domain:** AWS storage / security
**Applies to:** `aws-cloud`

---

## Why this exists

S3 buckets default to private, but a single `PutBucketAcl` or `PutBucketPolicy` call can make them public — and that call can come from IaC, a CLI typo, or a compromised credential. Account-level S3 Block Public Access (BPA) is a preventive control that overrides any per-bucket or per-object ACL/policy that would otherwise grant public access. Without it, the estate relies entirely on bucket-level discipline to prevent a data-exposure incident. Enabling BPA at the account level costs nothing, has no operational overhead, and eliminates the class of "accidentally public S3" findings.

## How to apply

Enable all four BPA settings on the AWS account (not just the bucket). Do this in all accounts in the organization — add it to the account-vending baseline.

```bash
aws s3control put-public-access-block \
  --account-id <account-id> \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

As Terraform:
```hcl
resource "aws_s3_account_public_access_block" "this" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

Add an SCP to Organizations that denies `s3:PutAccountPublicAccessBlock` from being called with values that would weaken these settings.

**Do:**
- Enable all four settings at account creation time, before any bucket is created.
- Include this in your account vending module as a required resource.
- Apply at org level via SCP: deny weakening the account-level BPA.
- For the rare legitimate public bucket (e.g., a public static-site or public software distribution), override BPA at the individual bucket level with documented justification — the account setting remains protective for all other buckets.

**Don't:**
- Leave BPA at the default (unset) and rely on per-bucket ACLs.
- Disable account-level BPA globally just because one bucket needs to be public.
- Mix object ACLs with bucket policies — ACLs are a legacy mechanism; use bucket policies.

## Edge cases / when the rule does NOT apply

Legitimate public S3 use cases (public software releases, public static sites, public dataset hosting) can override BPA at the individual bucket level with a clear, auditable justification. Account-level BPA remains enabled; the exception is per-bucket, not per-account.

## See also

- [`../agents/aws-network-engineer.md`](../agents/aws-network-engineer.md) — owns VPC endpoints for S3 so private workloads never traverse the public internet
- [`./private-by-default.md`](./private-by-default.md) — the broader principle; account-level BPA is its S3-specific expression

## Provenance

Codifies CIS AWS Benchmark 2.1.x and AWS Foundational Security Best Practices control S3.1 (S3 Block Public Access enabled). Standard item in any AWS landing zone account-vending checklist.

---

_Last reviewed: 2026-06-05 by `claude`_
