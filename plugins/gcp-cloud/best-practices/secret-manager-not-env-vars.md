# Store secrets in Secret Manager — not environment variables or metadata

**Status:** Absolute rule
**Domain:** GCP security / secrets
**Applies to:** `gcp-cloud`

---

## Why this exists

Environment variables in Cloud Run services, GKE pods, and Cloud Functions are visible to anyone with sufficient IAM access to describe the service or pod spec. They appear in the Cloud Console UI, in Terraform state, and in any CI artifact that captures the deployment manifest. Secret Manager stores secrets encrypted at rest, versioned, auditable, and accessible only via IAM-controlled API calls. A Cloud Run service referencing a Secret Manager secret by name exposes the value only at runtime to the service account — not in any deployment artifact.

## How to apply

```bash
# Create a secret
gcloud secrets create db-password --replication-policy="automatic"
echo -n "s3cr3t!" | gcloud secrets versions add db-password --data-file=-

# Grant Cloud Run service account access to the secret
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:sa-my-service@my-project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Reference the secret in Cloud Run (not as an environment variable literal):
```hcl
# Terraform — Cloud Run with Secret Manager mount
resource "google_cloud_run_v2_service" "this" {
  name     = "my-service"
  location = var.region

  template {
    service_account = google_service_account.this.email

    containers {
      image = var.image

      # Mount as env var from Secret Manager — value never in the spec
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }
    }
  }
}
```

For GKE pods, use the Secrets Store CSI Driver to mount secrets as files:
```yaml
# GKE pod — mount Secret Manager secret as a file via CSI driver
volumes:
  - name: secrets-store
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "my-app-secrets"
```

**Do:**
- Pin secret versions in prod (`version = "3"`) rather than `"latest"` — prevents surprise rotation surprises.
- Use `"latest"` only in dev/non-prod with an explicit rotation cadence.
- Grant only `roles/secretmanager.secretAccessor` to workloads — not `roles/secretmanager.admin`.
- Enable Secret Manager audit logs (Data Access: DATA_READ) to track every secret access.

**Don't:**
- Pass secret values in `--set-env-vars` or via Terraform `environment { name = "X" value = "literal" }`.
- Store secrets in GCS bucket files — no audit trail per access and no versioning with automatic expiry.
- Grant service accounts access to all secrets in a project (`--resource="projects/*"`) — scope to the specific secret.

## Edge cases / when the rule does NOT apply

- **Non-sensitive configuration** (log levels, feature flags, region names): plain environment variables are fine.
- **Bootstrapping Secret Manager access** — the initial service account key that authenticates the app to Secret Manager must itself be handled carefully (Workload Identity eliminates this entirely for GCP-hosted workloads).

## See also

- [`../agents/gcp-iam-engineer.md`](../agents/gcp-iam-engineer.md) — owns the service account bindings to Secret Manager.
- [`./no-service-account-key-files.md`](./no-service-account-key-files.md) — key files are a class of secret; Secret Manager is the right store even if WIF can't replace them entirely.

## Provenance

Derives from GCP security best practices (Secret Manager documentation) and the `gcp-cloud` house opinion on private-by-default and no-key-files in `CLAUDE.md` §2. Standard GCP secret management pattern.

---

_Last reviewed: 2026-06-05 by `claude`_
