# Choose the API-plugin auth scheme deliberately, route the app registration + verdict out, and never embed a secret in the manifest

**Status:** Absolute rule — auth is the plugin's security boundary; the app registration is `azure-cloud`'s, the verdict is core's, and a secret in the manifest is a leak.

**Domain:** Grounding / API-plugin authentication

**Applies to:** `microsoft-365-copilot`

> **Security-sensitive.** The auth *design* lives here; the **app registration / admin consent** routes to `azure-cloud/entra-identity-engineer` and the **security verdict** (is this auth design sufficient, what's the injection / token-scope risk) routes to **`ravenclaude-core/security-reviewer`** — mandatory, not optional.

---

## Why this exists

An API plugin reaches a real backend, so the auth choice is the security decision, not a config detail. Copilot supports a spectrum — **None**, **API key**, **OAuth2** (authorization-code for user-delegated, client-credentials for server-to-server), and **Microsoft Entra ID** (app-only or delegated/on-behalf-of) — and they are not interchangeable: API-key is a shared secret unscoped to a user; OAuth2 auth-code and Entra-delegated carry the *user's* identity (so the backend can authorize per-user, which is what you usually want for line-of-business data); Entra app-only acts as the app regardless of user. Picking "None" or a static API key for data that should be user-scoped is an authorization hole. Two hard rules sit on top: the credential is declared as a **connection/registration reference**, never a literal secret in the plugin manifest (a secret in a manifest is a committed leak), and the **Entra app registration + admin consent** is `azure-cloud`'s to perform — this plugin names the requirement. And the **security verdict is core's**. This is house opinion #7's spirit (auth is a control) and the §10 mandatory security seam.

## How to apply

Match the scheme to the identity model the backend needs, declare it as a reference, and route the registration + verdict out. Surface the GCC-High caveat on sovereign-cloud questions.

```text
Scheme              Identity model                         Use when
──────────────────────────────────────────────────────────────────────────────────────
None                anonymous                              public, read-only, no user data
API key             shared secret (not user-scoped)        a service that authenticates by key
OAuth2 auth-code    the signed-in USER's delegated access  user-scoped LoB data (usual choice)
OAuth2 client-creds server-to-server, no user              app-level access to public/shared data
Entra ID (app-only) the APP's identity                     app acts as itself, not the user
Entra ID (delegated/OBO)  user + app                       call downstream APIs as the user
```

```jsonc
// plugin manifest — auth is a REFERENCE to a registered connection, NEVER a literal secret
{
  "schema_version": "v2.4",
  "runtimes": [
    {
      "type": "OpenApi",
      "auth": {
        "type": "OAuthPluginVault",        // reference to the registered OAuth2 connection
        "reference_id": "<connection-id-from-registration>"
      }
    }
  ]
}
// ❌ NEVER: "auth": { "type": "ApiKeyPluginVault", "api_key": "sk-live-abc123..." }
```

**Do:**
- Choose the scheme from the identity model — user-scoped data → OAuth2 auth-code / Entra delegated, not a static API key.
- Declare auth as a **connection/registration reference**; keep the secret in the registration, not the manifest.
- Route the **Entra app reg + admin consent** to `azure-cloud/entra-identity-engineer` and the **verdict** to `ravenclaude-core/security-reviewer` (mandatory).
- Surface the **GCC-High caveat: API-plugin auth is not supported there** (`[verify-at-build]`) on any sovereign-cloud question.
- State a `Licensing impact:` line — Copilot seats + any downstream API cost/quota.

**Don't:**
- Put a literal API key, client secret, or token in the plugin/app manifest — it's a committed leak.
- Use "None" or a shared API key for data that should be authorized per user.
- Treat the security verdict as this plugin's to give — it is `ravenclaude-core/security-reviewer`'s.

## Edge cases / when the rule does NOT apply

A genuinely public, read-only API (e.g. a weather or reference lookup with no user data) may legitimately use **None** — but that is a reviewed classification, confirmed with the security reviewer, not a default. **MCP-server** plugins (v2.4) authenticate at the MCP-connection level and the server requires separate admin/tenant Entra consent in the Agent Registry — the "route registration + consent out" rule still holds. GCC-High support and the exact supported scheme list are `[verify-at-build]`.

## See also

- [`./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md`](./apiplugin-pin-plugin-manifest-and-map-operationid-both-ways.md) — the manifest the auth is declared in
- [`./apiplugin-mark-consequential-actions-and-attest-security-info.md`](./apiplugin-mark-consequential-actions-and-attest-security-info.md) — gating the *write* actions auth unlocks
- [`../knowledge/api-plugins-and-auth-2026.md`](../knowledge/api-plugins-and-auth-2026.md) · [`../agents/api-plugin-engineer.md`](../agents/api-plugin-engineer.md)
- [API-plugin authentication training](https://learn.microsoft.com/training/modules/copilot-declarative-agent-api-plugin-auth/) · [Plugin manifest schema 2.4](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.4)

## Provenance

Codifies the API-plugin-auth security seam (§10, mandatory) from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn Copilot plugin-auth pages (the supported scheme table: None / Basic / ApiKey / ServiceHttp / OAuth auth-code / OAuth client-creds / Entra app-only / Entra delegated) and the plugin-manifest auth-reference model, retrieved 2026-05-30. GCC-High caveat is `[verify-at-build]`. The auth *verdict* escalates to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
