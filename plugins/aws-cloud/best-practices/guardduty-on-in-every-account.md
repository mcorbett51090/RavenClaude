# Enable GuardDuty in every account, delegated to a security account

**Status:** Absolute rule
**Domain:** AWS security / threat detection
**Applies to:** `aws-cloud`

---

## Why this exists

GuardDuty continuously analyzes CloudTrail management events, VPC flow logs, and DNS query logs for threat signals (credential compromise, crypto-mining, exfiltration) without any agent to install. It is the lowest-friction, highest-signal threat detection control on AWS. Its absence means the first indicator of a compromise is often a support case, a customer complaint, or a surprising bill — not an internal alert. For multi-account estates, delegating GuardDuty to a Security account gives a single pane of glass across all member accounts.

## How to apply

```hcl
# Terraform — Enable GuardDuty in a member account (repeat per region)
resource "aws_guardduty_detector" "this" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }
}

# In the management account — delegate administration to the security account
resource "aws_guardduty_organization_admin_account" "security" {
  admin_account_id = var.security_account_id
}

# In the security account — auto-enroll new member accounts
resource "aws_guardduty_organization_configuration" "this" {
  auto_enable_organization_members = "ALL"
  detector_id                      = aws_guardduty_detector.this.id

  datasources {
    s3_logs { auto_enable = true }
    kubernetes { audit_logs { enable = true } }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes { auto_enable = true }
      }
    }
  }
}
```

Wire GuardDuty findings to an SNS topic and your on-call tool via EventBridge:
```hcl
resource "aws_cloudwatch_event_rule" "guardduty_high" {
  name        = "guardduty-high-severity"
  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail      = { severity = [{ numeric = [">=", 7] }] }
  })
}
```

**Do:**
- Enable all data sources (S3 protection, EKS audit logs, Malware Protection).
- Delegate to the Security/Audit account so findings aggregate centrally.
- Set `auto_enable_organization_members = "ALL"` so new accounts enroll automatically.
- Route high-severity (≥7) findings to on-call immediately; low-severity to a daily digest.

**Don't:**
- Leave GuardDuty at the management account — delegation to Security account is required.
- Disable GuardDuty to "save cost" — the per-event cost is minimal; the risk is not.
- Ignore findings — high-severity GuardDuty findings (credential exfiltration, crypto-mining) require immediate investigation.
- Run GuardDuty only in us-east-1 — enable in every region where you operate.

## Edge cases / when the rule does NOT apply

- **Regions with no active workloads**: GuardDuty still costs a small amount even with no data; you may disable it in truly unused regions and regions you are actively blocking via SCP. Document this decision.

## See also

- [`../agents/aws-architect.md`](../agents/aws-architect.md) — owns multi-account security tooling design.
- [`./cloudtrail-on-in-every-account.md`](./cloudtrail-on-in-every-account.md) — CloudTrail is a data source for GuardDuty and must be enabled first.
- [`./multi-account-by-blast-radius.md`](./multi-account-by-blast-radius.md) — the multi-account context that makes delegated GuardDuty necessary.

## Provenance

Codifies an implicit gap in the `aws-cloud` house opinions: security posture requires automated threat detection, not just preventive controls. GuardDuty is the standard AWS threat-detection baseline from the AWS Security Best Practices whitepaper and the Well-Architected Security pillar.

---

_Last reviewed: 2026-06-05 by `claude`_
