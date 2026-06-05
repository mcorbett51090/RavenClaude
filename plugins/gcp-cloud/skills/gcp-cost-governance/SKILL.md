---
name: gcp-cost-governance
description: "Playbook for setting up GCP billing visibility and cost controls — billing export to BigQuery, budget alerts, label-based attribution, committed-use discounts, and the common cost leaks to eliminate first."
---

# GCP Cost Governance

## When to invoke

Use when standing up cost visibility for a new GCP project or organization, investigating a billing surprise, or building the FinOps foundation before spend scales. Pairs with `gcp-resource-hierarchy` (folder/project structure is the prerequisite for meaningful attribution).

## Step 1 — Billing export to BigQuery (non-negotiable first step)

Enable detailed billing export — this is the raw material for every cost analysis:

```hcl
resource "google_billing_account_iam_member" "bq_export" {
  billing_account_id = var.billing_account_id
  role               = "roles/billing.admin"
  member             = "serviceAccount:${google_service_account.billing_export.email}"
}
```

In the GCP console: **Billing → Billing export → BigQuery export → Edit settings**:
- Enable **Standard usage cost** export (required).
- Enable **Detailed usage cost** export (adds resource-level granularity; recommended).
- Enable **Pricing** export (needed for unit economics).

Dataset location should match your primary region. Export begins from the date it is enabled — there is no backfill.

## Step 2 — Label strategy

Labels are the attribution axis. Enforce them via org policy:

```hcl
resource "google_org_policy_policy" "require_labels" {
  name   = "organizations/${var.org_id}/policies/gcp.resourceLocations"
  parent = "organizations/${var.org_id}"
  # Use Terraform google_project module with mandatory label defaults
}
```

Minimum mandatory labels on all resources:

| Label key | Example values | Purpose |
|---|---|---|
| `env` | `prod`, `staging`, `dev` | Environment split |
| `team` | `platform`, `data`, `commerce` | Team attribution |
| `service` | `api-gateway`, `ml-training` | Service-level cost |
| `cost-center` | `eng-123` | Finance allocation |

**Verify label coverage:**
```sql
-- BigQuery billing export
SELECT service.description, labels, sum(cost) AS total
FROM `billing_dataset.gcp_billing_export_*`
WHERE DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND (labels IS NULL OR array_length(labels) = 0)
GROUP BY 1, 2
ORDER BY 3 DESC
LIMIT 20;
```

Any row with null/empty labels is unattributed spend.

## Step 3 — Budget alerts

Create budgets at the project level (and optionally at the folder level):

```hcl
resource "google_billing_budget" "per_project" {
  billing_account = var.billing_account_id
  display_name    = "${var.project_id}-monthly-budget"

  budget_filter {
    projects = ["projects/${var.project_number}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "500"
    }
  }

  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.9 }
  threshold_rules { threshold_percent = 1.0 }
  threshold_rules { threshold_percent = 1.25 }  # overage alert

  all_updates_rule {
    pubsub_topic = google_pubsub_topic.billing_alerts.id
  }
}
```

Route the Pub/Sub topic to Slack/PagerDuty via a Cloud Function or Eventarc.

## Step 4 — Committed-use discounts (CUDs)

| Workload | CUD type | Savings |
|---|---|---|
| Steady-state GCE VMs | Resource-based CUD (1 or 3 year) | Up to 57% |
| Cloud Run / GKE Autopilot | Spend-based CUD | Up to 17% |
| BigQuery (on-demand → slots) | BigQuery editions + reservations | Up to 40% for predictable query load |

Baseline before committing: run `Recommender` (GCP console → Committed Use Discounts) for a 30-day usage analysis recommendation.

**Do not commit before you have 30+ days of stable usage** — a CUD on a workload you are about to resize is waste.

## Step 5 — Top cost leaks to check first

Run this BigQuery query weekly:

```sql
SELECT
  service.description AS service,
  sku.description AS sku,
  SUM(cost) AS cost_usd,
  SUM(usage.amount) AS usage_amount,
  usage.unit
FROM `billing_dataset.gcp_billing_export_resource_*`
WHERE DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1, 2, 5
ORDER BY 3 DESC
LIMIT 50;
```

| Common culprit | Diagnostic | Fix |
|---|---|---|
| Idle GCE VMs | `status = RUNNING`, low CPU | Stop or delete; use preemptible/spot for batch |
| Oversized Cloud SQL | `database_id`, high memory cost | Downsize tier; use read replicas only where needed |
| Egress to internet | Networking → external egress SKUs | Use Private Google Access; keep traffic in-region |
| Unused persistent disks | Disk SKU with no attached VM | Delete orphaned disks |
| BigQuery on-demand scans | High `Bytes processed` per query | Partition + cluster tables; use query cost estimator |
| Artifact Registry storage | Old image layers accumulating | Add lifecycle policy to delete untagged images |

## Step 6 — Cost anomaly detection

Enable **GCP Recommender / Cost Insights** and the **Billing anomaly detection** feature (under Billing → Cost Management). It sends alerts when spend increases >10% week-over-week on a service.

Supplement with a BigQuery scheduled query that fires when a service's 7-day spend exceeds 2× its 30-day average:

```sql
-- anomaly_detect.sql (run daily via scheduled query)
WITH baseline AS (
  SELECT service.description, AVG(daily_cost) AS avg_cost
  FROM (
    SELECT DATE(usage_start_time) AS d, service.description, SUM(cost) AS daily_cost
    FROM `billing_dataset.gcp_billing_export_*`
    WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY 1, 2
  )
  GROUP BY 1
),
recent AS (
  SELECT service.description, SUM(cost) AS week_cost
  FROM `billing_dataset.gcp_billing_export_*`
  WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  GROUP BY 1
)
SELECT r.description, r.week_cost, b.avg_cost * 7 AS expected_7d_cost
FROM recent r JOIN baseline b USING (description)
WHERE r.week_cost > b.avg_cost * 7 * 2
ORDER BY r.week_cost DESC;
```

## Pitfalls

- **Not enabling billing export on day one** — there is no backfill; you lose the historical baseline needed for anomaly detection and CUD decisions.
- **Sharing a billing account across unrelated orgs or customers** — attribution becomes impossible without a separate billing account per top-level org.
- **Setting a budget alert at 100% only** — by the time it fires, the month's budget is gone. Add 50% and 90% thresholds.
- **Buying CUDs for dev/test workloads** — committed use discounts apply across the org, but committing against unpredictable workloads is waste; measure first.
