---
name: api-plugin-openapi-hygiene
description: "Make a REST API safe and correct to expose as a Microsoft 365 Copilot API plugin — lay out the four files (app manifest + plugin manifest + OpenAPI + adaptive cards), verify the plugin-manifest↔OpenAPI `operationId` mapping both ways, respect the OpenAPI-for-Copilot subset, write model-readable operation descriptions, budget responses to ~66% of the 25-item/~4096-token wall, and wire Entra OAuth2/API-key auth (with the GCC-High caveat). Use when building or reviewing a Copilot API plugin."
---

# API-plugin OpenAPI hygiene

Playbook for `api-plugin-engineer`. Source of truth: [`../../knowledge/api-plugins-and-auth-2026.md`](../../knowledge/api-plugins-and-auth-2026.md). Template: [`../../templates/api-plugin-pair.md`](../../templates/api-plugin-pair.md).

## 1. The four files
App manifest + **plugin manifest** + **OpenAPI spec** + adaptive-card templates. Source-control all four.

## 2. operationId mapping (verify both ways)
Each plugin-manifest function/runtime → a concrete OpenAPI `operationId`. Check: every function maps to an existing `operationId`, and every exposed `operationId` is intentional. A mismatch = Copilot can't invoke (or invokes the wrong op).

## 3. Model-readable descriptions
Copilot decides *whether* and *how* to call from the operation `description` + parameter descriptions. Write them for the model, not for humans only. Vague descriptions = wrong/no invocation.

## 4. Respect the Copilot OpenAPI subset
Supported verbs/parameters/response shapes only `[verify-at-build]`. Bounded payloads.

## 5. Budget the response
Keep responses within **~66%** of the 25-item / ~4,096-token plugin-response budget. Trim fields; paginate; shape adaptive cards for citation.

## 6. Auth
Entra OAuth2 (incl. OBO) or API-key, declared as a connection. **No secrets in the files.** App registration → `azure-cloud/entra-identity-engineer`; the **verdict** → `ravenclaude-core/security-reviewer` (mandatory). Surface the **GCC-High not-supported caveat** `[verify-at-build]`.

## 7. Licensing impact
Copilot seats + any downstream API cost/quota.

## Anti-patterns
- operationId mismatch; full-OpenAPI features Copilot doesn't support; vague descriptions; unbounded responses; secrets in the manifest; ignoring the GCC-High caveat.
