# Set budget alerts on every GCP project from day one

**Status:** Pattern
**Domain:** GCP FinOps / cost
**Applies to:** `gcp-cloud`

---

## Why this exists

GCP resources can accumulate cost silently. Cloud Run instances scaling unexpectedly, BigQuery jobs scanning full tables, or a Cloud SQL instance left running after a project ends can all produce a surprising bill. Budget alerts are the minimum viable FinOps control: a billing alert fires before the bill arrives. Without them, the first signal of runaway spend is the monthly invoice or a billing-account suspension. The `label-everything-for-cost` rule provides attribution; budget alerts provide the alarm.

## How to apply

```hcl
# Terraform — budget alert per project
resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account_id
  display_name    = "budget-${var.project_id}"

  budget_filter {
    projects = ["projects/${var.project_number}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.monthly_budget_usd)
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }
  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "CURRENT_SPEND"
  }
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }
  threshold_rules {
    threshold_percent = 1.2
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    pubsub_topic = google_pubsub_topic.billing_alerts.id
  }
}

# Route alerts to Pub/Sub for programmatic action (or to email)
resource "google_pubsub_topic" "billing_alerts" {
  name    = "billing-alerts-${var.project_id}"
  project = var.billing_admin_project
}
```

**Do:**
- Set thresholds at 50%, 90%, 100% (actual spend) and 120% (forecasted) — the forecasted threshold catches runaway trends before the month ends.
- Route alerts to a Pub/Sub topic and trigger a Cloud Function that posts to Slack/PagerDuty, not just email.
- Include both development and production projects — dev environments are often the highest-waste category.
- Review budget amounts quarterly; a static budget becomes wrong as workloads scale.

**Don't:**
- Set a budget only at the billing-account level without per-project budgets — account-level alerts fire too late and don't point to the offender.
- Leave the `all_updates_rule` pointing to a team email that isn't monitored — budget alerts must reach someone who can act.
- Treat a 100% budget hit as an automatic spend cap — GCP budgets are advisory; they don't stop billing.

## Edge cases / when the rule does NOT apply

- **Projects with variable spend by design** (e.g., batch ML training that legitimately exceeds a monthly cap): set the threshold higher or use a forecasted-spend alert rather than a fixed cap.
- **Shared services projects with cross-project labels** for cost attribution: supplement with label-level budget filters to identify the contributing workload.

## See also

- [`../agents/gcp-architect.md`](../agents/gcp-architect.md) — owns org-level billing and project governance.
- [`./label-everything-for-cost.md`](./label-everything-for-cost.md) — labels enable per-workload cost attribution within a project.

## Provenance

Derived from GCP FinOps best practices (Cloud Billing budget alerts documentation) and the complementary `label-everything-for-cost` house rule in `CLAUDE.md` §2. Standard GCP cost governance pattern.

---

_Last reviewed: 2026-06-05 by `claude`_
