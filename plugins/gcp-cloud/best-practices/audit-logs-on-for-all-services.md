# Enable Cloud Audit Logs for all services in every project

**Status:** Absolute rule
**Domain:** GCP governance / security
**Applies to:** `gcp-cloud`

---

## Why this exists

GCP Cloud Audit Logs record who did what, when, and where across every API call. Admin Activity logs are always on and free; Data Access logs are disabled by default and carry a cost — but without them you cannot answer "who read this secret?" or "who queried that BigQuery table?" after an incident. For security-relevant services (Secret Manager, KMS, BigQuery, Cloud Storage, IAM), not enabling Data Access logs means your audit trail has a deliberate gap. Org Policy `constraints/gcp.restrictCmekCryptoKeyProjects` and VPC Service Controls are only meaningful when the audit trail is intact.

## How to apply

Enable Data Access audit logs for security-relevant services via the org-level audit config in Terraform:

```hcl
# Terraform — org-level audit config
resource "google_organization_iam_audit_config" "all_services" {
  org_id  = var.org_id
  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# Sink to a dedicated log-archive project (long-term storage)
resource "google_logging_organization_sink" "audit_sink" {
  name             = "org-audit-sink"
  org_id           = var.org_id
  destination      = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"
  include_children = true

  filter = "logName:\"cloudaudit.googleapis.com\""
}
```

**Do:**
- Set the audit config at the **organization** level with `include_children = true` so new projects inherit it automatically.
- Sink audit logs to a dedicated log-archive project with a separate billing account and restricted IAM — the team that generates the logs should not control the sink.
- Set a retention policy on the archive bucket (e.g., 1 year) with a retention lock for compliance.
- Enable `DATA_READ` for Secret Manager, KMS, and Cloud Storage — these are the high-value access events.

**Don't:**
- Rely on only Admin Activity logs — they miss data-plane read access to secrets and storage.
- Route audit logs to the same project that runs the workload — a compromised project owner can delete the logs.
- Leave BigQuery Data Access logs disabled if BigQuery holds sensitive data.

## Edge cases / when the rule does NOT apply

- **Dev/sandbox projects with no sensitive data**: Data Access logs generate cost; you may apply a more targeted log type filter (Admin Activity only) for cost control.
- **Projects where per-service log volume is extremely high** (e.g., BigQuery in a high-query analytics tier): evaluate the cost/benefit of DATA_READ vs a query audit sampling approach.

## See also

- [`../agents/gcp-architect.md`](../agents/gcp-architect.md) — owns org-level policy and governance posture.
- [`./use-the-resource-hierarchy.md`](./use-the-resource-hierarchy.md) — org-level audit config propagates through the hierarchy; hierarchy must be clean first.

## Provenance

Derived from GCP Security Best Practices (Cloud Audit Logs documentation) and the GCP CISO Blueprint. Standard GCP governance pattern: enable audit logs at the org level with a sink to a protected archive project.

---

_Last reviewed: 2026-06-05 by `claude`_
