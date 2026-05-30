# Read secrets via Key Vault references, not literal app settings — managed identity does the auth

**Status:** Absolute rule — a secret value pasted into an app setting / pipeline variable is a leak that every contributor can read.

**Domain:** Identity / Secrets

**Applies to:** `azure-cloud`

---

## Why this exists

`passwordless-by-default` says "no secret literals in code or IaC." This rule covers the unavoidable secret that *does* have to live somewhere — a third-party API key, a legacy connection string — and where it goes: **Azure Key Vault, referenced from the app**, never pasted as a plaintext app-setting or pipeline variable. The gap people miss is that an app setting like `API_KEY=<the-actual-key>` is readable by **anyone with Contributor on the app**, even if they have no Key Vault access at all — so the secret leaks through the *app's* RBAC surface. App Service / Functions / Logic Apps (Standard) support **Key Vault references**: the setting value is `@Microsoft.KeyVault(SecretUri=...)`, the platform resolves it at runtime using the app's **managed identity** (granted `Key Vault Secrets User`), and app contributors see only the reference string — never the secret. Rotate the secret in the vault and the app picks it up with no redeploy.

## How to apply

Store the secret in a Key Vault, grant the app's managed identity `Key Vault Secrets User`, and set the app setting to a Key Vault reference — not the value.

```bash
# 1. App gets a managed identity + the read-only secrets role on the vault
az webapp identity assign -g $rg -n $app --scope $kvId --role "Key Vault Secrets User"

# 2. The secret lives in the vault
secretUri=$(az keyvault secret set --vault-name $vault --name partner-api-key --value "$KEY" --query id -o tsv)

# 3. The app setting is a REFERENCE, not the value — platform resolves it at runtime
az webapp config appsettings set -g $rg -n $app \
  --settings PARTNER_API_KEY="@Microsoft.KeyVault(SecretUri=$secretUri)"
```

```bicep
// User-assigned identity for Key Vault references (resolves even at create time)
properties: {
  keyVaultReferenceIdentity: uamiResourceId
  siteConfig: { appSettings: [
    { name: 'PARTNER_API_KEY', value: '@Microsoft.KeyVault(SecretUri=${secretUri})' }
  ] }
}
```

**Do:**
- Use `@Microsoft.KeyVault(SecretUri=...)` references for App Service / Functions / Logic Apps (Standard) secrets; grant the MI **`Key Vault Secrets User`** (RBAC vault) or `Get` (access-policy vault).
- Prefer a **user-assigned identity** (`keyVaultReferenceIdentity`) when the app must resolve references at **creation** time (before a system-assigned identity exists).
- Keep the vault **private** (`publicNetworkAccess: 'Disabled'`) and ensure the app has VNet egress to reach it.
- Let **rotation** happen in the vault — no app redeploy needed.

**Don't:**
- Paste a secret value into an app setting or pipeline variable — app Contributors can read it without any Key Vault permission.
- Grant the app a broad role like `Key Vault Administrator` when `Key Vault Secrets User` (read-only) is all it needs.
- Forget VNet routing on a network-restricted vault — the reference fails to resolve and the raw `@Microsoft.KeyVault(...)` string leaks into the app's config.

## Edge cases / when the rule does NOT apply

- **Services that support managed identity natively** (Azure SQL, Storage, Service Bus) need **no secret at all** — use the MI directly; Key Vault references are for the secrets you can't eliminate.
- **Compute without Key Vault-reference support** (some container scenarios) reads from the vault via the SDK + `DefaultAzureCredential` instead — same vault, same MI, different mechanism.
- **A network-restricted vault** requires the app's subnet on the vault's allow-list; expect a benign `403` from the app's public IP followed by a success from its private IP in the audit log (by design).

## See also

- [`./passwordless-by-default.md`](./passwordless-by-default.md) — the broader rule (no secret literals; MI/WIF for auth)
- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) — keeping the vault's data plane private
- [`../knowledge/entra-identity-and-access.md`](../knowledge/entra-identity-and-access.md) — managed identity, RBAC roles
- [`../agents/entra-identity-engineer.md`](../agents/entra-identity-engineer.md) · [`../agents/app-platform-engineer.md`](../agents/app-platform-engineer.md)

## Provenance

Codifies house opinion #4 from [`../CLAUDE.md`](../CLAUDE.md) §3 (Key Vault references for unavoidable secrets). Grounded in Microsoft Learn [Use Key Vault references as app settings](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references) — `@Microsoft.KeyVault(SecretUri=...)`, `Key Vault Secrets User` role, `keyVaultReferenceIdentity` for user-assigned, the network-restricted-vault `403`-then-success behavior (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
