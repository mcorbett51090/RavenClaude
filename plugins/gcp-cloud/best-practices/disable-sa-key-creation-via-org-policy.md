# Disable service account key creation via Org Policy

**Status:** Absolute rule
**Domain:** GCP IAM / org policy
**Applies to:** `gcp-cloud`

---

## Why this exists

The `no-service-account-key-files` rule says don't download key files. This rule enforces that preventively via Org Policy so it is not merely advisory. `constraints/iam.disableServiceAccountKeyCreation` blocks API calls that generate SA key files for any project under the org/folder. Without this constraint, any developer with `iam.serviceAccountKeys.create` permission can silently generate a long-lived key — an action that may not be noticed until a key leaks. A preventive guardrail catches the action before the key exists; a detective audit log catches it after.

## How to apply

```hcl
# Terraform — org policy to disable SA key creation at org level
resource "google_org_policy_policy" "disable_sa_key_creation" {
  name   = "organizations/${var.org_id}/policies/iam.disableServiceAccountKeyCreation"
  parent = "organizations/${var.org_id}"

  spec {
    rules {
      enforce = true
    }
  }
}
```

To allow an exception for a specific project (e.g., a legacy on-prem integration that genuinely cannot use WIF):
```hcl
resource "google_org_policy_policy" "allow_sa_keys_legacy" {
  name   = "projects/${var.legacy_project_id}/policies/iam.disableServiceAccountKeyCreation"
  parent = "projects/${var.legacy_project_id}"

  spec {
    rules {
      enforce = false    # override — must be documented and reviewed quarterly
    }
  }
}
```

**Do:**
- Set the constraint at **organization** level — don't rely on per-project enforcement.
- Document every exception project with a comment in IaC explaining why key creation is allowed and set a review date.
- Pair this constraint with `constraints/iam.disableServiceAccountKeyUpload` to prevent re-uploading an externally generated key.
- Review exception projects quarterly; eliminate them as WIF coverage expands.

**Don't:**
- Enable the constraint without first inventorying existing keys — block creation, then rotate out existing keys in a separate step.
- Apply a blanket exception at a folder level — exception scope should be as narrow as a single project.
- Treat this constraint as a substitute for `no-service-account-key-files` training — it is the enforcement mechanism, not the reason.

## Edge cases / when the rule does NOT apply

- **Projects running legacy on-prem workloads** that cannot use WIF: narrow exception at the project level, documented, with a migration plan.
- **Security tooling projects** that manage keys as part of rotation automation: assess whether the tooling can be moved to WIF before creating an exception.

## See also

- [`../agents/gcp-iam-engineer.md`](../agents/gcp-iam-engineer.md) — owns org policy and IAM guardrails.
- [`./no-service-account-key-files.md`](./no-service-account-key-files.md) — the behavioral rule; this doc is the preventive enforcement.
- [`./org-policy-guardrails.md`](./org-policy-guardrails.md) — the broader set of org policy constraints.

## Provenance

Codifies the `gcp-cloud` house opinion #3 ("No service-account key files") in `CLAUDE.md` §2 as a preventive Org Policy constraint. Standard GCP security hardening from the Google CIS Benchmark for GCP and the GCP Security Foundations Blueprint.

---

_Last reviewed: 2026-06-05 by `claude`_
