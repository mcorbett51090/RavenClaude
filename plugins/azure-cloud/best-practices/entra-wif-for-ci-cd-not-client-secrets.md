# Use Entra Workload Identity Federation for CI/CD — no client secrets

**Status:** Absolute rule
**Domain:** Azure identity / CI/CD
**Applies to:** `azure-cloud`

---

## Why this exists

A client secret stored in a pipeline variable can be read by anyone with repo access, is often committed by accident, and must be manually rotated before expiry or it becomes a stale credential that nobody watches. Workload Identity Federation (WIF) replaces the client secret with a federated trust relationship: the CI provider (GitHub Actions, Azure DevOps) issues a short-lived OIDC token; Azure Entra exchanges it for a short-lived access token with no persistent secret anywhere. The client secret surface is zero. The `check-azure-anti-patterns.sh` hook flags `client_secret` literals in IaC for exactly this reason.

## How to apply

```bash
# 1. Create an app registration (or use managed identity) + federated credential
az ad app create --display-name "myapp-cicd"
APP_ID=$(az ad app list --display-name "myapp-cicd" --query "[0].appId" -o tsv)

az ad app federated-credential create --id $APP_ID --parameters '{
  "name": "github-actions-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:myorg/myrepo:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# 2. Assign the app the minimum RBAC role for its job
az role assignment create \
  --assignee $APP_ID \
  --role "Contributor" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg>"

# 3. In GitHub Actions — no secrets needed
- uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

The GitHub Actions OIDC token is exchanged automatically — no `AZURE_CLIENT_SECRET` variable needed.

**Do:**
- Use `vars` (non-secret) for client ID, tenant ID, and subscription ID — these are not secret.
- Scope the federated credential `subject` to the specific branch/environment (`ref:refs/heads/main`, `environment:production`) for a tighter trust.
- Prefer managed identities over app registrations for workloads running on Azure compute (VMs, Container Apps, Functions).
- Rotate nothing — there is no credential to rotate.

**Don't:**
- Store `AZURE_CLIENT_SECRET` as a pipeline secret; if it's there, replace it with WIF.
- Use a broad `subject` like `repo:myorg/myrepo:*` — scope to the branch/environment.
- Assign `Owner` or `Contributor` at subscription scope; scope to the resource group the pipeline actually deploys to.

## Edge cases / when the rule does NOT apply

- **On-premises CI runners** that cannot reach Entra to exchange the OIDC token: a managed identity on the runner VM is the preferred path; a rotating client secret (with a clear rotation runbook) is the fallback — never a static key.
- **Legacy CI systems without OIDC support**: evaluate upgrade paths; a short-lived client secret with a 90-day rotation is the minimum if WIF is truly unavailable.

## See also

- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) — owns WIF configuration and federated identity design.
- [`./passwordless-by-default.md`](./passwordless-by-default.md) — the parent rule; WIF is the CI/CD implementation of passwordless.

## Provenance

Codifies house opinion #4 ("Passwordless by default — WIF for CI/CD") from `CLAUDE.md` §3 and the WIF capability in `knowledge/azure-deployment-cicd.md`. Standard Azure/GitHub Actions best practice since WIF GA (2022).

---

_Last reviewed: 2026-06-05 by `claude`_
