---
name: workload-identity-federation
description: "Playbook for configuring passwordless CI/CD using Workload Identity Federation — covers app registration, federated credential setup for GitHub Actions and Azure DevOps, RBAC assignment, and the OIDC token exchange flow."
---

# Workload Identity Federation (WIF)

## When to Use This Skill

Any CI/CD pipeline (GitHub Actions, Azure DevOps, other OIDC-capable systems) that needs to deploy to Azure. Replaces client secrets and long-lived service principal passwords with short-lived OIDC tokens — zero stored credentials.

## 1. How It Works

```
GitHub Actions runner
  │  requests OIDC token from GitHub (sub: repo:org/repo:ref:refs/heads/main)
  ▼
Azure AD token exchange endpoint
  │  validates token against registered federated credential
  ▼
Azure AD issues a scoped access token
  │
  ▼
az deployment group create  (uses the access token — no secret ever stored)
```

## 2. Setup Steps

### Step 1 — Create the App Registration (or use Managed Identity for self-hosted runners)

```bash
az ad app create --display-name "myapp-cicd-prod"
# Note: appId and objectId from output
APP_ID=$(az ad app show --id myapp-cicd-prod --query appId -o tsv)
az ad sp create --id $APP_ID
SP_OBJECT_ID=$(az ad sp show --id $APP_ID --query id -o tsv)
```

### Step 2 — Add a Federated Credential (GitHub Actions example)

```bash
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**Subject claim patterns:**

| Trigger | Subject claim |
|---|---|
| Branch `main` | `repo:org/repo:ref:refs/heads/main` |
| Any PR | `repo:org/repo:pull_request` |
| Environment `production` | `repo:org/repo:environment:production` |
| Tag push | `repo:org/repo:ref:refs/tags/v*` |

Prefer **environment** subjects for production deployments — they enforce environment protection rules.

### Step 3 — Assign RBAC (least privilege, scoped to resource group)

```bash
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Contributor" \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-myapp-prod-eastus
```

Prefer purpose-built roles (`Website Contributor`, `Storage Blob Data Contributor`) over broad `Contributor` where the service supports them.

## 3. GitHub Actions Workflow Integration

```yaml
permissions:
  id-token: write      # required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production    # enforces protection rules; matches subject claim
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy Bicep
        run: |
          az deployment group create \
            --resource-group rg-myapp-prod-eastus \
            --template-file main.bicep \
            --parameters @params.prod.json
```

Store `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` as GitHub Actions **variables** (not secrets) — they are not sensitive.

## 4. Azure DevOps Integration

1. Create a **Service Connection** of type "Azure Resource Manager" → choose "Workload Identity federation (automatic)" — the portal creates the app registration and federated credential automatically.
2. Reference the service connection in the pipeline: `azureSubscription: 'myapp-prod-wif'`

For manual setup (cross-tenant, or when automatic is restricted), follow the same Step 1-3 pattern above and supply the `clientId` to the service connection manually.

## 5. Bicep Module for the App Registration + Federated Credential

```bicep
// Note: App registrations live in Entra (Microsoft Graph), not ARM.
// Provision via az CLI in a bootstrap script, or use the AVM identity module [verify-at-build].
// Store outputs (clientId, tenantId) in Key Vault or pipeline variables.
```

## 6. Verification Checklist

- [ ] No client secrets exist on the app registration (Entra Portal → App → Certificates & Secrets)
- [ ] Federated credential `subject` matches the exact pipeline context (branch/environment/PR)
- [ ] RBAC is scoped to resource-group or resource — not subscription
- [ ] `permissions: id-token: write` is set in the GitHub Actions job
- [ ] Pipeline runs successfully with OIDC login before removing any legacy secret

## Pitfalls

- Using `ref:refs/heads/*` (wildcard branch) as the subject for production — any branch can then trigger prod deploys; use a named branch or environment
- Forgetting `id-token: write` permission on the job — OIDC token request silently fails
- Assigning `Owner` at subscription scope — use the minimum role at resource-group scope
- Mixing WIF with a stored client secret on the same app registration — defeats the purpose; delete all secrets after WIF is confirmed working

## See Also

- [`../../agents/entra-identity-engineer.md`](../../agents/entra-identity-engineer.md) — Managed Identity, app registrations, and RBAC design
- [`../../agents/bicep-iac-engineer.md`](../../agents/bicep-iac-engineer.md) — CI/CD pipeline setup and Deployment Stacks
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: passwordless by default, secrets in Key Vault
