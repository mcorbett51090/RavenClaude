# Attach Cloud Armor to every public-facing Global HTTP(S) Load Balancer

**Status:** Pattern
**Domain:** GCP networking / security
**Applies to:** `gcp-cloud`

---

## Why this exists

A Global HTTP(S) Load Balancer without Cloud Armor has no automated layer-7 protection against OWASP Top 10 attacks, DDoS, or bot traffic. Cloud Armor provides WAF rules (OWASP CRS), adaptive protection (ML-based DDoS mitigation), and geo-based allow/deny at the Google edge — before traffic reaches the backend. Attaching a Cloud Armor security policy to the backend service takes one Terraform resource and significantly reduces the L7 attack surface at low incremental cost.

## How to apply

```hcl
# Terraform — Cloud Armor security policy with OWASP rules
resource "google_compute_security_policy" "this" {
  name = "waf-policy-${var.app_name}"

  # Default rule: allow
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config { src_ip_ranges = ["*"] }
    }
    description = "default allow"
  }

  # OWASP ModSecurity CRS (pre-configured ruleset)
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable = true
    }
  }

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-v33-stable')"
      }
    }
    description = "Block XSS"
  }

  rule {
    action   = "deny(403)"
    priority = "1001"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-v33-stable')"
      }
    }
    description = "Block SQLi"
  }
}

# Attach to backend service
resource "google_compute_backend_service" "this" {
  name          = "backend-${var.app_name}"
  # ... other config ...
  security_policy = google_compute_security_policy.this.id
}
```

**Do:**
- Start preconfigured WAF rules in `preview` mode before switching to `deny` — confirm legitimate traffic is not blocked.
- Enable Adaptive Protection (`layer_7_ddos_defense_config`) — it's ML-based and catches attack patterns the rule set doesn't explicitly cover.
- Use Cloud Armor for global LBs only; regional LBs have different support (Cloud Armor Standard + regional security policies).
- Log Cloud Armor actions to Cloud Logging for audit and forensics.

**Don't:**
- Attach Cloud Armor and immediately put all rules in `deny` mode without a preview period.
- Use Cloud Armor as the only network control — firewall rules and private backends still matter.
- Forget to attach the policy to every backend service behind the LB.

## Edge cases / when the rule does NOT apply

- **Internal-only HTTP(S) Load Balancers** not reachable from the public internet: Cloud Armor applies to global external LBs; internal LBs use different enforcement (firewall rules, VPC SC).
- **TCP/SSL Proxy Load Balancers** (non-HTTP): Cloud Armor is HTTP-layer only; use firewall rules for non-HTTP protection.

## See also

- [`../agents/gcp-network-engineer.md`](../agents/gcp-network-engineer.md) — owns load balancer and Cloud Armor configuration.
- [`./private-by-default-gcp.md`](./private-by-default-gcp.md) — Cloud Armor is the layer-7 protection for resources that must be public.

## Provenance

Derived from GCP Security Best Practices (Cloud Armor documentation) and the `gcp-network-engineer` remit in `CLAUDE.md` §1: "Cloud Load Balancing." Standard WAF pattern for GCP public-facing services.

---

_Last reviewed: 2026-06-05 by `claude`_
