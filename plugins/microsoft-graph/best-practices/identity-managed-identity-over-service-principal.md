# Prefer managed identity over service principal with client secret for Azure-hosted workloads

**Status:** Pattern
**Domain:** Microsoft Graph / identity
**Applies to:** `microsoft-graph`

---

## Why this exists

A service principal with a client secret requires the secret to be stored somewhere — an environment variable, a Key Vault reference, a CI/CD secret, a config file. Every storage location is a potential leak, and secrets expire and require rotation. A managed identity (system-assigned or user-assigned) removes credentials from the equation entirely: the Azure runtime issues a short-lived token internally; the application never sees the credential, it can never be stolen, and it never expires in the traditional sense. For any Azure-hosted workload (App Service, Functions, Container Apps, AKS, Logic Apps) that calls Microsoft Graph, managed identity is the lower-blast-radius default.

## How to apply

Enable managed identity on the Azure resource:

```bash
# System-assigned managed identity on an Azure Function
az functionapp identity assign --name my-func --resource-group my-rg

# Get the principal ID to assign Graph app roles to
az functionapp identity show --name my-func --resource-group my-rg --query principalId -o tsv
```

Assign the required Graph app role to the managed identity:

```bash
# Assign Mail.Read application permission to the managed identity
GRAPH_APP_ID="00000003-0000-0000-c000-000000000000"
ROLE_ID="570282fd-fa5c-430d-a7fd-fc8dc98a9dca"  # Mail.Read app role
PRINCIPAL_ID="<managed-identity-object-id>"
TENANT_ID="<your-tenant-id>"

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/${PRINCIPAL_ID}/appRoleAssignments" \
  --body "{\"principalId\":\"${PRINCIPAL_ID}\",\"resourceId\":\"<graph-sp-object-id>\",\"appRoleId\":\"${ROLE_ID}\"}"
```

In code (Python MSAL / Azure SDK):
```python
from azure.identity import ManagedIdentityCredential
from msgraph import GraphServiceClient

credential = ManagedIdentityCredential()
client = GraphServiceClient(credential, ["https://graph.microsoft.com/.default"])
```

**Do:**
- Use a **user-assigned** managed identity when the same identity must be shared across multiple Azure resources (avoids recreating app-role assignments when the resource is redeployed).
- Verify the app-role assignment is on the **Graph service principal** in the tenant, not on the target resource itself.
- Escalate the app-role assignment step to `ravenclaude-core/security-reviewer` — managed identity + broad Graph app roles is still a security decision.

**Don't:**
- Use managed identity for workloads not hosted in Azure — managed identity is Azure-native; for non-Azure hosts, use a service principal with certificate credentials.
- Skip the app-role assignment step and assume managed identity inherits permission from the developer's delegated access — managed identity uses application permissions, not delegated.

## Edge cases / when the rule does NOT apply

A developer workstation or CI/CD pipeline (GitHub Actions, ADO pipelines) cannot use managed identity directly. Use environment-specific service-principal credentials with certificate authentication, stored in the CI/CD secret manager.

## See also

- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns auth-flow selection and managed identity design
- [`./auth-certificates-not-secrets-in-production.md`](./auth-certificates-not-secrets-in-production.md) — the fallback for non-Azure environments where managed identity is unavailable

## Provenance

Codifies CLAUDE.md §3 #8 ("secrets are certificates, not strings, in production") applied to Azure-hosted workloads where managed identity removes credentials entirely; Microsoft Graph managed identity documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
