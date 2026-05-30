# Passwordless by default — managed identity and federated credentials, never literals

**Status:** Absolute rule — a client secret or connection string in code or IaC is a leak, not a config choice.

**Domain:** Identity / IaC

**Applies to:** `azure-cloud`

---

## Why this exists

Every secret literal you commit is a credential that must be rotated, scanned for, and eventually leaks. Azure removed the need for most of them: workloads authenticate with **managed identity**, and CI/CD pipelines authenticate with **workload identity federation** (an OIDC trust between the pipeline's identity provider and an Entra app/UAMI) — no stored secret on either side. The discipline is "passwordless by default" (house opinion #4): managed identity / WIF for runtime and pipeline auth, Key Vault references for the unavoidable secrets, and **never** a client secret, connection string, account key, SAS token, or primary key in source. The anti-pattern hook flags `password=`, `accountKey=`, `client_secret`, `connectionString`, `primaryKey`, and SAS literals on `.bicep`/`.tf`/config writes.

## How to apply

Give the workload a managed identity and grant it scoped RBAC; have the app read secrets from Key Vault by reference, not from a baked-in string. For CI/CD, federate the pipeline identity instead of storing a secret.

```bicep
resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  identity: { type: 'SystemAssigned' }       // managed identity, not a secret
  properties: { httpsOnly: true, siteConfig: { minTlsVersion: '1.2' } }
}

// App reads the DB password via a Key Vault reference — no literal in IaC:
//   value: '@Microsoft.KeyVault(SecretUri=https://<vault>.vault.azure.net/secrets/db-pw/)'
```

```yaml
# GitHub Actions deploy step — federated, no AZURE_CREDENTIALS secret:
permissions: { id-token: write, contents: read }
steps:
  - uses: azure/login@v2
    with:
      client-id: ${{ vars.AZURE_CLIENT_ID }}
      tenant-id: ${{ vars.AZURE_TENANT_ID }}
      subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      # no client-secret — OIDC federated credential handles trust
```

**Do:**
- Use system- or user-assigned managed identity for app-to-Azure-service auth; scope its RBAC to the resource/RG (house opinion #5), not the subscription.
- Configure a **federated credential** on the Entra app/UAMI for each pipeline (GitHub OIDC, Azure DevOps WIF) and pass only the public client/tenant/subscription IDs.
- Put unavoidable secrets in Key Vault and reference them; rotate on any exposure.

**Don't:**
- Store an `AZURE_CREDENTIALS` JSON secret or a service-principal client secret for CI/CD when federation is available.
- Commit a connection string / account key / SAS — even "temporarily." The hook flags it; CI will too.

## Edge cases / when the rule does NOT apply

- **Third-party systems with no managed-identity support** may force a secret — store it in Key Vault, reference it, set a rotation policy; never inline it.
- **Local developer loops** may use `az login` / `DefaultAzureCredential` interactive auth — that's a developer credential, not a committed secret, and is fine.
- **Legacy estates mid-migration** may still hold app registrations with secrets; the rule is the target state, and each remaining secret is a tracked migration item.
- The federated-credential / managed-identity **design** (which identity, which scope, which subject claim) is a security decision and routes to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/entra-identity-and-access.md`](../knowledge/entra-identity-and-access.md) — managed identity / WIF / RBAC / PIM / External ID
- [`../knowledge/azure-iac-decision-and-bicep.md`](../knowledge/azure-iac-decision-and-bicep.md) — "Secrets never in IaC — Key Vault references / managed identity, never literals"
- [`../knowledge/azure-deployment-cicd.md`](../knowledge/azure-deployment-cicd.md) — passwordless CI/CD with workload identity federation
- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) · [`../agents/bicep-iac-engineer.md`](../agents/bicep-iac-engineer.md)

## Provenance

Codifies house opinions #4 and #5 from [`../CLAUDE.md`](../CLAUDE.md) §3, the matching anti-patterns (§4), and the secret-literal grep checks in `check-azure-anti-patterns.sh` (§7). Grounded in the IaC + CI/CD knowledge files (Microsoft Learn, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
