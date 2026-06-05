# Attach WAF to every public ALB and CloudFront distribution

**Status:** Pattern
**Domain:** AWS networking / security
**Applies to:** `aws-cloud`

---

## Why this exists

A public ALB or CloudFront distribution without AWS WAF is a layer-7 target with no automated protection against OWASP Top 10 attacks, bot traffic, or account-takeover attempts. AWS WAF with the AWS Managed Rules (AWSManagedRulesCommonRuleSet + AWSManagedRulesKnownBadInputsRuleSet) provides a baseline layer-7 defense with near-zero operational overhead. The incremental cost (per request + WebACL fee) is small relative to the incident cost of an undefended endpoint.

## How to apply

```hcl
# Terraform — WAF WebACL with AWS Managed Rules attached to an ALB
resource "aws_wafv2_web_acl" "this" {
  name  = "${var.app_name}-${var.env}-waf"
  scope = "REGIONAL"   # use "CLOUDFRONT" + provider alias us-east-1 for CloudFront

  default_action { allow {} }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "common-rules"
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "bad-inputs"
    }
  }

  visibility_config {
    sampled_requests_enabled   = true
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-waf"
  }
}

resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.this.arn
  web_acl_arn  = aws_wafv2_web_acl.this.arn
}
```

**Do:**
- Start rules in `COUNT` mode; confirm expected traffic is clean before switching to `BLOCK`.
- Enable WAF logging to S3 or CloudWatch Logs for forensics.
- Add rate-based rules for login/API endpoints to prevent brute-force.
- Use `AWSManagedRulesAmazonIpReputationList` for additional bot/scraper signal.

**Don't:**
- Attach WAF only to CloudFront and leave a direct-routable ALB unprotected.
- Skip WAF logging — you lose forensic visibility.
- Accept managed rule false-positive blocks without triaging; start in COUNT mode.
- Use WAF as the only layer-3/4 defense — security groups still control which ports are open.

## Edge cases / when the rule does NOT apply

- **Internal-only ALBs** (not reachable from the public internet): WAF adds overhead without layer-7 threat exposure. Add it if the ALB receives untrusted internal traffic (e.g., multi-tenant SaaS).
- **Very low-traffic dev/sandbox environments**: the per-WebACL + per-request fee may not be worth it; evaluate.

## See also

- [`../agents/aws-network-engineer.md`](../agents/aws-network-engineer.md) — owns VPC and public exposure design.
- [`./private-by-default.md`](./private-by-default.md) — WAF is the defensive layer when a resource must be public.

## Provenance

Codifies the `aws-network-engineer` house opinion (#4 "Private by default; public exposure by explicit exception") and the AWS WAF best practices guide. AWS WAF Managed Rules are the standard baseline layer-7 defense recommended in the Well-Architected Security pillar.

---

_Last reviewed: 2026-06-05 by `claude`_
