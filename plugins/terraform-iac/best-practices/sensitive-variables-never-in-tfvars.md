# Never put sensitive values in tfvars files — use environment variables or a secret manager

**Status:** Absolute rule
**Domain:** IaC / secrets management
**Applies to:** `terraform-iac`

---

## Why this exists

`*.tfvars` files are routinely committed to version control. A password, database URL with credentials, or API key in a `terraform.tfvars` is a committed secret — visible to everyone with repo access, present in git history forever, and stored in Terraform state (which is also sensitive). The house opinion #1 is explicit: state stores secrets in plaintext. The corollary is: don't put secrets into Terraform at all if you can avoid it; if you must, pass them as `TF_VAR_` environment variables from a CI secret store, not as committed file values.

## How to apply

**Approach 1 (preferred): don't pass secrets to Terraform at all**

Use data sources to read from a secret manager at plan time:
```hcl
# Read from AWS Secrets Manager — the password never appears in tfvars or state
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "app/${var.env}/db-password"
}

resource "aws_db_instance" "this" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
  # Note: even this writes the value to state — use manage_master_user_password instead
}

# Even better for RDS — let AWS manage the password entirely
resource "aws_db_instance" "this" {
  manage_master_user_password = true   # password never in state
}
```

**Approach 2: TF_VAR_ environment variables from CI secrets**

```bash
# In CI (GitHub Actions example):
# Store DB_PASSWORD in GitHub Actions encrypted secret, inject at runtime
export TF_VAR_db_password="${{ secrets.DB_PASSWORD }}"
terraform apply
```

```hcl
# Declare the variable as sensitive
variable "db_password" {
  type      = string
  sensitive = true   # value is redacted in plan output
}
```

**Do:**
- Mark all secret variables with `sensitive = true` to redact them from plan/apply output.
- Use cloud-native managed credentials (RDS `manage_master_user_password`, Azure SQL Entra auth) to keep secrets out of state entirely.
- Inject sensitive values via `TF_VAR_` env vars sourced from a CI-native secret store.
- `.gitignore` any `*.tfvars` files that might contain local test values as a safety net.

**Don't:**
- Commit `terraform.tfvars` or `*.auto.tfvars` files containing secret values.
- Check `TF_VAR_*` exports into shell scripts that are committed.
- Assume `sensitive = true` keeps the value out of state — it only redacts plan output; state still holds the value.

## Edge cases / when the rule does NOT apply

- **Non-sensitive variables** (region, instance size, tag values): plain `tfvars` files committed to the repo are fine and desirable for audit trail.
- **`terraform.tfvars` for local development only**: acceptable if `.gitignore`d; add a pre-commit hook to block accidental commits.

## See also

- [`../agents/iac-policy-and-state-engineer.md`](../agents/iac-policy-and-state-engineer.md) — owns state safety and secrets-in-state prevention.
- [`./no-secrets-in-state.md`](./no-secrets-in-state.md) — the complementary rule: even when secrets are injected correctly, audit whether they end up in state.

## Provenance

Codifies the `terraform-iac` house opinion #1 in `CLAUDE.md` §2: "State is precious and dangerous — never with secrets in it (state stores them in plaintext)." Applied to the input path (tfvars). Standard Terraform secrets management guidance from HashiCorp's security documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
