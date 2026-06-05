# Use OIDC federation for CI/CD — no long-lived cloud credentials

**Status:** Absolute rule
**Domain:** IaC / CI/CD security
**Applies to:** `terraform-iac`

---

## Why this exists

A long-lived AWS access key, Azure service principal client secret, or GCP SA key stored in a CI/CD system is a credential that persists indefinitely. It can be leaked via logs, forked repos, stale secrets in closed PRs, or CI system breaches. OIDC (OpenID Connect) federation replaces static credentials with short-lived tokens: the CI system (GitHub Actions, GitLab, CircleCI) issues a signed JWT; the cloud provider exchanges it for a temporary session token that expires at the end of the pipeline run. Nothing persistent to leak. This is the IaC plugin's enforcement of the cloud plugins' credential hygiene rules applied to the pipeline runner.

## How to apply

**GitHub Actions + AWS (OIDC):**
```hcl
# Terraform — AWS OIDC provider + role for GitHub Actions
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_actions" {
  name = "github-actions-terraform-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:myorg/myrepo:ref:refs/heads/main"
        }
      }
    }]
  })
}
```

```yaml
# GitHub Actions workflow — no AWS credentials stored in secrets
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform-prod
    aws-region: us-east-1
    role-session-name: GitHubActions-${{ github.run_id }}
```

**GitHub Actions + Azure (WIF):**
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}        # not secret
    tenant-id: ${{ vars.AZURE_TENANT_ID }}        # not secret
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}  # not secret
    # No AZURE_CLIENT_SECRET needed
```

**GitHub Actions + GCP (WIF):**
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/github
    service_account: github-actions@my-project.iam.gserviceaccount.com
```

**Do:**
- Scope the OIDC trust to the specific branch/environment (`ref:refs/heads/main`, `environment:production`), not `repo:org/repo:*`.
- Grant the federated role/identity the minimum permissions for the pipeline job (plan = read; apply = write for specific resources).
- Store client IDs, tenant IDs, and subscription IDs as non-secret repo variables — they are not credentials.

**Don't:**
- Store `AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_SECRET`, or SA key JSON in CI secrets.
- Use a wildcard sub-claim (`repo:org/repo:*`) — scope to the specific branch or environment.
- Grant a federated identity broad admin permissions — scope to the resources the pipeline actually manages.

## Edge cases / when the rule does NOT apply

- **Self-hosted runners on on-premises infrastructure** without internet access to the cloud OIDC endpoint: workload identity from the host machine (EC2 instance profile, VM managed identity) is the preferred path; rotating credentials stored in a secrets manager (Vault, AWS Secrets Manager) is the fallback.

## See also

- [`../agents/iac-architect.md`](../agents/iac-architect.md) — owns CI/CD pipeline design for IaC.
- [`./least-privilege-for-the-runner.md`](./least-privilege-for-the-runner.md) — OIDC provides the identity; this rule covers the permissions the role should have.

## Provenance

Codifies the `iac-architect` seam from `CLAUDE.md` §3: "Running plan/apply in CI with a reviewed plan + OIDC → devops-cicd/pipeline-engineer." The OIDC pattern is the IaC plugin's complement to the credential hygiene rules in the cloud plugins (aws-cloud, azure-cloud, gcp-cloud). Standard CI/CD security practice.

---

_Last reviewed: 2026-06-05 by `claude`_
