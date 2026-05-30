# API plugins + auth (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on the four-file architecture + auth model (first-party). `[verify-at-build]` on the GCC-High support status + OpenAPI constraint specifics.
**Read when:** turning a REST API into a Copilot action, or wiring its auth.

---

## The four-file architecture

| File | Role |
|---|---|
| **App manifest** (Teams/M365 app manifest) | the package; references the plugin |
| **Plugin manifest** (`apiPlugin`) | declares functions → `runtimes` → `operationId`; descriptions; response semantics; auth reference |
| **OpenAPI spec** | the API surface; `operationId` per operation; Copilot-constrained subset |
| **Adaptive-card templates** | response rendering + citation |

Grounding: [API plugins](https://learn.microsoft.com/microsoft-365/copilot/extensibility/instructions-api-plugins).

## operationId mapping (the contract)

Each plugin-manifest function points at a concrete OpenAPI **`operationId`**. A mismatch means Copilot can't invoke the operation (or invokes the wrong one). **Verify the mapping both directions.** Every operation needs a clear, model-readable `description` — Copilot uses it to decide *whether* and *how* to call.

## OpenAPI-for-Copilot constraints

Copilot supports a **subset** of OpenAPI — design to the constraints, not full OpenAPI (supported verbs/parameters/response shapes; well-formed `operationId` + descriptions; bounded response payloads). Keep responses within the **25-item / ~4,096-token** plugin-response budget at **~66%**. See the [`api-plugin-openapi-hygiene`](../skills/api-plugin-openapi-hygiene/SKILL.md) skill + the [`api-plugin-pair`](../templates/api-plugin-pair.md) template.

## Auth

- **Microsoft Entra OAuth2** (incl. on-behalf-of) or **API-key** — declared in the plugin manifest, registered as a connection.
- The **Entra app registration + admin consent is `azure-cloud/entra-identity-engineer`'s**; the **security verdict is `ravenclaude-core/security-reviewer`'s** (mandatory). **No secrets in the plugin/manifest.**
- **GCC-High caveat: API-plugin auth is not supported in GCC-High** `[verify-at-build]` — surface this on any sovereign-cloud question. Grounding: [API-plugin auth](https://learn.microsoft.com/training/modules/copilot-declarative-agent-api-plugin-auth/).

## Licensing impact

API plugins run on Copilot seats; the downstream API may carry its own cost/quota. State both.

## Refresh triggers
- GCC-High / sovereign-cloud auth support changes.
- The OpenAPI-for-Copilot supported subset changes with a new manifest version.
