---
name: secrets-rotation-and-management
description: "Playbook for managing secrets across the CI/CD pipeline — vaulting, injection at runtime, automated rotation, and the emergency response procedure when a secret is compromised — so long-lived credentials never live in pipeline definitions, env files, or Git."
---

# Secrets Rotation and Management

## When to invoke

Use when setting up secrets management for a new service, auditing an existing pipeline for hardcoded/long-lived credentials, or responding to a leaked secret incident.

## Step 1 — Credential classification

Before choosing a storage mechanism, classify each secret:

| Class | Examples | Target storage |
|---|---|---|
| Short-lived federated | AWS OIDC tokens, GCP Workload Identity | No storage — generate at runtime |
| Long-lived service credentials | Database passwords, API keys | Secrets manager (AWS SM / GCP SM / Vault) |
| CI-only variables | NPM publish tokens, Docker Hub PAT | CI platform secrets store (GitHub Actions Secrets) |
| Signing keys | Container signing, artifact signatures | Hardware-backed (AWS KMS / GCP KMS) |

**Rule:** never store short-lived federated credentials — configure the OIDC trust and let the provider issue them.

## Step 2 — OIDC federation for CI (preferred)

Replace long-lived cloud credentials in CI with federated tokens:

**GitHub Actions → AWS:**
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
      aws-region: us-east-1
```

**GitHub Actions → GCP:**
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER
    service_account: deploy@my-project.iam.gserviceaccount.com
```

No secrets stored anywhere — the token is issued for the specific workflow run and expires in minutes.

## Step 3 — Runtime injection (not build-time baking)

Secrets must be injected at **runtime**, not baked into images or build artifacts:

| Anti-pattern | Correct pattern |
|---|---|
| `ENV DB_PASSWORD=...` in Dockerfile | Fetch from secrets manager in entrypoint or app startup |
| Secret in Helm values.yaml | ExternalSecrets Operator or sealed-secrets |
| `echo $SECRET > config.json` in CI | Mount as a volume from a CSI secrets store |

**Kubernetes:** Use the [External Secrets Operator](https://external-secrets.io) to sync from AWS Secrets Manager / GCP Secret Manager into Kubernetes Secrets — the manifest stores only the secret reference, not the value.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: prod/myapp/db
        property: password
```

## Step 4 — Rotation schedule

| Secret type | Rotation cadence | Automation |
|---|---|---|
| Database passwords | 90 days | AWS SM rotation Lambda / Vault database engine |
| API keys (3rd-party) | On-demand + 180 days | Manual or provider webhook |
| TLS certificates | Before expiry (cert-manager automates) | cert-manager / ACM auto-renew |
| Signing keys (KMS) | Annual key rotation, not re-keying | KMS automatic rotation |

Enable **AWS Secrets Manager automatic rotation** for RDS:
```hcl
resource "aws_secretsmanager_secret_rotation" "db" {
  secret_id           = aws_secretsmanager_secret.db.id
  rotation_lambda_arn = aws_lambda_function.rotate_db.arn
  rotation_rules {
    automatically_after_days = 90
  }
}
```

## Step 5 — Compromise response

When a secret is suspected compromised:

1. **Rotate immediately** — don't wait for root cause. Rotation is the first action.
2. **Revoke the old credential** — most providers allow a grace period where both old and new credentials are valid; shorten it to minutes, not hours.
3. **Audit access logs** — AWS CloudTrail / GCP Audit Logs / GitHub audit log for usage of the compromised credential.
4. **Scan Git history** for any other locations the secret may have been committed:
   ```bash
   git log --all --full-history -- '*.env' | head
   trufflehog git file://. --only-verified
   ```
5. **Remove from Git history** using `git filter-repo` (not `filter-branch`); force-push only after all team members have been notified.
6. **Write a post-incident note** capturing what was exposed, for how long, and the remediation taken.

## Step 6 — Detection gate in CI

Add a pre-commit and CI scan to catch secrets before they land in the repo:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

```yaml
# GitHub Actions step
- name: Secret scanning
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Pitfalls

- **Hardcoding secrets in environment variable names in CI config** — `env: DB_PASSWORD: ${{ secrets.DB_PASSWORD }}` is fine; `env: DB_PASSWORD: "p@ssw0rd"` is a committed secret.
- **Long rotation grace periods** — a 7-day overlap between old and new credentials means the old credential is live for a week post-compromise.
- **Secrets in container image layers** — a secret passed as a `--build-arg` ends up in the image layer history even if the `RUN` step deletes the file.
- **No expiry alerting** — API keys and TLS certificates expire silently; add reminder alarms 30/7 days before expiry.
