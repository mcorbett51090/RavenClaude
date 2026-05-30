# Secrets live in Key Vault, referenced — never as plaintext env-var defaults

**Status:** Absolute rule — a secret typed into a solution component is committed to git, shipped in the managed `.zip`, and visible to anyone who can export the solution. That is credential disclosure, not configuration.

**Domain:** ALM / Security

**Applies to:** `power-platform`

---

## Why this exists

The unpacked solution tree is source-controlled and the managed `.zip` is shippable — both are designed to be read, diffed, and distributed. A secret placed in a `String` environment variable's default value, or pasted into a custom-connector definition, or hard-coded into a flow, rides along inside those artifacts. It lands in git history (where it survives even after you "delete" it), in every CI artifact, and in the export any maker with read access can pull. The platform's answer is the **`Secret`-typed environment variable**, whose value is not the secret itself but a *reference* to an Azure Key Vault secret. The solution carries the pointer; the secret stays in Key Vault, access-controlled and audited, and is resolved at runtime by the identity running the flow.

## How to apply

Use a `Secret` environment variable that points at a Key Vault secret. The solution ships the reference; Key Vault holds the value. Grant the environment's identity (or the running SPN) `get` on the secret.

```bash
# 1. Secret lives in Key Vault — never in the solution
az keyvault secret set --vault-name mc-prod-kv --name PartnerApiKey --value "<the-actual-secret>"

# 2. Grant the Power Platform environment's identity read access to that secret
#    (Key Vault access policy or RBAC 'Key Vault Secrets User' on the secret/vault)
```

In the solution, the `Secret` env var stores a Key Vault reference, not the value — the resolved shape looks like:

```
@Microsoft.KeyVault(SecretUri=https://mc-prod-kv.vault.azure.net/secrets/PartnerApiKey/)
```

Per environment, point the same env var at that environment's vault/secret via deployment settings — dev → `mc-dev-kv`, prod → `mc-prod-kv` — so no environment can read another's secret.

**Do:**
- Type the env var as `Secret` and store only the Key Vault reference; the actual secret never enters the solution.
- Use a separate vault (or separate secret) per environment so a dev compromise can't leak prod credentials.
- Confirm the running identity has `get` on the secret before declaring the deploy done — a missing access policy surfaces as a runtime failure, not an import failure.

**Don't:**
- Put a secret in a `String` env var default value — it's plaintext in the tree and the `.zip`.
- Paste an API key, client secret, or connection string into a flow action, custom-connector definition, or Power Fx formula.
- Reuse one vault secret across dev/test/prod — rotate-once-break-everywhere, and a lower-env breach reaches prod.

## Edge cases / when the rule does NOT apply

- **Connector credentials** (the SharePoint/SQL/Outlook account a flow runs as) are not env-var secrets — they live in **connections**, bound via connection references. Governed by [`./alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md).
- **Non-secret config** (URLs, IDs, flags) belongs in plain `String`/`JSON`/`Boolean` env vars — see [`./alm-environment-variables-not-hardcoded-config.md`](./alm-environment-variables-not-hardcoded-config.md). Don't reach for Key Vault for a public URL.
- **Tenants without Azure / Key Vault** still must not put secrets in plaintext env-var defaults; if there is genuinely no vault, the secret belongs in the connector's connection (credential held by the platform), not in solution data — escalate the architecture gap rather than working around it.

## See also

- [`./alm-environment-variables-not-hardcoded-config.md`](./alm-environment-variables-not-hardcoded-config.md) — non-secret per-env config
- [`./alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md) — credential bindings via connections
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns the env-var schema including `Secret` types
- [`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md) — how pipeline identities acquire credentials safely

## Provenance

Codifies house opinion §4 anti-pattern ("Storing secrets as plain string env vars instead of Key Vault references") and the `power-platform` hook check that flags plaintext secrets in environment-variable defaults (`check-house-opinions.sh`). The `@Microsoft.KeyVault(SecretUri=...)` reference shape and `Secret`-typed env-var mechanism verified against Microsoft Learn (environment-variables Key Vault secrets), retrieved 2026-05-30. Per-environment vault isolation is house security posture.

---

_Last reviewed: 2026-05-30 by `claude`_
