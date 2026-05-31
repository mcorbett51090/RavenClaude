---
description: Scaffold a Microsoft 365 Copilot API plugin from an OpenAPI spec — choose the auth scheme from the identity model (never embed a secret), map operationId both ways, and mark every state-changing action consequential with security_info attestation.
argument-hint: "[the API, e.g. 'a ticketing API with read + delete operations']"
---

# Scaffold an API plugin

You are running `/microsoft-365-copilot:scaffold-api-plugin`. Turn the API the user described (`$ARGUMENTS`) into a Copilot API plugin, following this plugin's `api-plugin-engineer` discipline — the auth choice is the security decision, and a write action that fires unconfirmed is a real backend mutation.

## When to use this

Copilot needs to take a transactional action against a real backend (not just read/rank a store — that's a connector). If the data only needs to be grounded and cited, use `/microsoft-365-copilot:build-graph-connector` instead.

## Steps

1. **Choose the auth scheme from the identity model** — user-scoped LoB data → OAuth2 auth-code / Entra delegated, not a static API key; "None" only for genuinely public read-only APIs (`apiplugin-choose-and-route-auth-never-embed-secrets.md`).
2. **Declare auth as a connection/registration reference, never a literal secret** in the manifest — a secret in a manifest is a committed leak (same file). Route the Entra app reg + admin consent to `azure-cloud/entra-identity-engineer`.
3. **Map `operationId` both ways** — every OpenAPI operation the plugin exposes maps to a plugin-manifest function and back; pin the manifest schema (`apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`).
4. **Mark every state-changing action consequential** (confirmation required) — leave `isNonConsequential: true` only for genuinely side-effect-free GETs, re-checked under v2.4's refined GET behavior (`apiplugin-mark-consequential-actions-and-attest-security-info.md`).
5. **Populate `security_info`** to attest what each function does/touches (v2.2+) so the orchestrator and reviewer can assess call risk (same file).
6. **Surface the GCC-High caveat** (API-plugin auth is not supported there, `[verify-at-build]`) on any sovereign-cloud question, and source-control the four-file project (`apiplugin-choose-and-route-auth-never-embed-secrets.md`). Use the `templates/api-plugin-pair.md` shape.

## Guardrails

- Never put a literal API key, client secret, or token in the plugin/app manifest; never use "None"/a shared key for data that should be user-scoped.
- Never flag a state-changing operation as non-consequential to skip the confirmation prompt; a GET with side effects is still consequential.
- The auth design *verdict* (is this sufficient, what's the token-scope/injection risk) and the consequence-framing sufficiency route to `ravenclaude-core/security-reviewer` — mandatory. State a `Licensing impact:` line (Copilot seats + downstream API cost).
