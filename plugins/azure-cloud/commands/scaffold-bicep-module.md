---
description: Scaffold an Azure Bicep (or Terraform) module that composes from a pinned Azure Verified Module, keeps the WAF secure defaults, wires diagnostics + managed identity, and gates the deploy on a what-if preview.
argument-hint: "[the resource/stack, e.g. 'a private Key Vault + Storage account']"
---

# Scaffold a Bicep module (AVM-composed)

You are running `/azure-cloud:scaffold-bicep-module`. Author production-grade IaC for what the user described (`$ARGUMENTS`) following this plugin's `bicep-iac-engineer` discipline — a thin layer of intent over a vetted, versioned building block, never a hand-rolled resource.

## When to use this

A new Azure resource or small stack needs IaC. If the ask is "which topology / which service?" rather than "write the code", stop and route to `azure-architect` first — this command assumes the design is settled. If the estate is multi/hybrid-cloud or there's existing Terraform, write the Terraform variant (the AVM rule applies either way).

## Steps

1. **Check the AVM registry before hand-authoring** (`iac-compose-from-azure-verified-modules`): default to the published Azure Verified Module for the resource (`br/public:avm/res/...`); only hand-author when no AVM exists, and then follow the AVM interface conventions so it's swappable later.
2. **Pin an exact module version** (`iac-compose-from-azure-verified-modules`) — `:0.x.y`, never a `~>`/`latest` float — so a module bump is a reviewed PR, and keep the module's secure defaults (private endpoints, diagnostics, RBAC) unless overriding for a documented reason.
3. **Private-by-default data plane** (`private-by-default-paas-data-planes`): `publicNetworkAccess: 'Disabled'`, `networkAcls.defaultAction: 'Deny'`, no `allowBlobPublicAccess`/`allowSharedKeyAccess`; reach it via Private Endpoint + Private DNS. Public exposure is an explicit, reviewed exception.
4. **Passwordless + no secret literals** (`passwordless-by-default`): system/user-assigned managed identity, Key Vault references (`@Microsoft.KeyVault(...)`) for the unavoidable secrets — never a `client_secret`/`connectionString`/`accountKey` in the file (the anti-pattern hook flags it). Parameterize subscription/tenant GUIDs.
5. **Diagnostics from day one** (`ops-diagnostic-settings-to-log-analytics-from-day-one`): attach a diagnostic setting (`allLogs` + `AllMetrics`) to a workspace-based Log Analytics workspace at provisioning time, not after the first incident.
6. **Gate the deploy on a preview** (`iac-what-if-before-every-deploy`): emit the `az deployment ... what-if` (or `terraform plan -out`) the engineer runs as a required, human-read PR check before apply — and tee up a Deployment Stack (`denySettings`) / locked remote state for lifecycle protection.

## Guardrails

- Never inline a secret, account key, SAS, or connection string — Key Vault reference or managed identity only.
- Never ship a public PaaS data plane or a single-zone prod SKU without a written, reviewed reason.
- The IaC is advisory: emit the runnable Bicep/Terraform + `az`/`terraform` commands; the engineer deploys with their own credentials (or workload identity federation in CI) — you don't deploy against their subscription.
- Route the identity/secret/network-security design (which identity, which scope, which Private Endpoint posture) to `ravenclaude-core/security-reviewer` — this plugin supplies the craft, core owns the verdict.
