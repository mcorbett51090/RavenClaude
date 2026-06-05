# Set lifecycle prevent_destroy on stateful resources

**Status:** Pattern
**Domain:** IaC / state safety
**Applies to:** `terraform-iac`

---

## Why this exists

A typo in a resource name, a refactored module, or a careless `terraform destroy` can delete a production database or S3 bucket before anyone realizes the plan was doing more than expected. `lifecycle { prevent_destroy = true }` makes Terraform error at plan time if a configuration change would destroy the resource — the apply is blocked until the flag is explicitly removed. This is not a substitute for reviewed plans or backup, but it is an in-IaC guard rail that catches accidental destroys before they happen.

## How to apply

```hcl
# Add to stateful resources in production
resource "aws_db_instance" "postgres" {
  identifier     = "app-db-prod"
  engine         = "postgres"
  instance_class = "db.t3.medium"
  # ...

  lifecycle {
    prevent_destroy = true
    # Also: ignore_changes for fields that are managed outside Terraform
    ignore_changes = [password]   # if password is rotated externally
  }
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "myapp-data-lake-prod"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_sql_database_instance" "postgres" {
  name   = "app-db-prod"
  region = "us-central1"

  lifecycle {
    prevent_destroy = true
  }
}
```

When a legitimate destroy is needed:
```hcl
# To destroy: temporarily remove the lifecycle block, review the plan, then apply
# NEVER remove it without a reviewed plan showing only the intended resource is destroyed
lifecycle {
  # prevent_destroy = true  # temporarily commented for EOL decommission — see ticket INFRA-123
}
```

**Resources that warrant `prevent_destroy = true`:**
- Production databases (RDS, Cloud SQL, Azure SQL, Cosmos)
- Object storage buckets with live data
- KMS keys
- VPC / VNet and core network resources
- Log archive and security audit destinations

**Do:**
- Pair `prevent_destroy` with deletion protection at the cloud resource level (e.g., RDS `deletion_protection = true`, GCS bucket retention lock) — defense in depth.
- Document in a comment when `prevent_destroy` is temporarily removed and link to the ticket.
- Review plans in CI: a plan showing a destroy on a stateful resource should fail the pipeline even if `prevent_destroy` was temporarily disabled.

**Don't:**
- Set `prevent_destroy = true` on ephemeral resources (Lambda functions, stateless EC2 instances, Container instances) — it prevents useful changes.
- Remove `prevent_destroy` without a written reason and a reviewed plan.
- Treat `prevent_destroy` as a complete backup strategy — it is a plan-time guard, not a restore capability.

## Edge cases / when the rule does NOT apply

- **Dev/test environments**: `prevent_destroy = false` (the default) is correct — dev DBs are meant to be torn down.
- **Blue/green deployments where the old resource is legitimately destroyed**: use a flag variable to control the lifecycle block by environment.

## See also

- [`../agents/iac-policy-and-state-engineer.md`](../agents/iac-policy-and-state-engineer.md) — owns state safety and destructive operation guardrails.
- [`./plan-is-the-review-artifact.md`](./plan-is-the-review-artifact.md) — the plan should still be reviewed even when prevent_destroy is set.

## Provenance

Codifies the `iac-policy-and-state-engineer` remit from `CLAUDE.md` §1: "State is precious and dangerous." `lifecycle { prevent_destroy }` is documented in the Terraform language reference as the in-IaC protection mechanism for this concern.

---

_Last reviewed: 2026-06-05 by `claude`_
