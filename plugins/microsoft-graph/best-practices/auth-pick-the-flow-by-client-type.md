# Pick the OAuth2 flow by client type — not by habit

**Status:** Absolute rule — the client type dictates the flow; using the wrong one is a security or correctness defect (implicit and ROPC are off the menu).

**Domain:** Identity

**Applies to:** `microsoft-graph`

---

## Why this exists

The Microsoft identity platform exposes several OAuth 2.0 grants, and each maps to a specific client type and trust model. Use the wrong one and you either can't acquire a token at all (a daemon can't run an interactive auth-code flow) or you ship a security weakness (the implicit grant leaks tokens in the URL fragment; ROPC handles the user's password directly and defeats MFA/Conditional Access). The platform has retired implicit (use auth-code + PKCE) and explicitly recommends against ROPC. So the flow is not a preference — it's determined by: is there a user? is the client a confidential (can keep a secret) or public client? can it open a browser? Pick wrong and there's no amount of code that makes it correct.

## How to apply

Match the client to the flow. PKCE is mandatory for SPAs and the default for native/mobile.

| Client | Flow |
|---|---|
| Web app, signs in a user, has a backend (confidential) | **Authorization code** |
| SPA (browser, public client) | **Authorization code + PKCE** (never implicit) |
| Native / mobile / desktop app | **Authorization code + PKCE** (interactive) |
| Daemon / background service / connector — **no user** | **Client credentials** (`scope={resource}/.default`) |
| Web API that must call Graph **as the original user** | **On-behalf-of (OBO)** |
| Input-constrained device / browserless CLI | **Device code** |

```csharp
// Daemon — client credentials. App-only; uses the application token cache.
var app = ConfidentialClientApplicationBuilder.Create(clientId)
    .WithCertificate(cert)                 // not a secret — see certificates doc
    .WithAuthority($"https://login.microsoftonline.com/{tenantId}")
    .Build();
var result = await app.AcquireTokenForClient(
    new[] { "https://graph.microsoft.com/.default" }).ExecuteAsync();
```

```javascript
// SPA — authorization code + PKCE (MSAL.js handles PKCE for you)
await msalInstance.acquireTokenSilent({ scopes: ["User.Read"] })
  .catch(e => e instanceof InteractionRequiredAuthError
    ? msalInstance.acquireTokenRedirect({ scopes: ["User.Read"] })
    : Promise.reject(e));
```

**Do:**

- Default SPAs/native to auth-code **+ PKCE**; daemons to client-credentials with `.default`.
- Use OBO when an upstream API must propagate the *user's* identity + delegated permissions to a downstream call to Graph.
- Use device-code only for genuinely browserless/input-constrained clients (smart TVs, IoT, some CLIs).

**Don't:**

- Use the **implicit grant** — it's deprecated; auth-code + PKCE replaced it.
- Use **ROPC** (username/password) — it handles the password directly and breaks MFA/Conditional Access; Microsoft recommends against it.
- Try to acquire a daemon token with an interactive flow, or call a user flow where there's no user.

## Edge cases / when the rule does NOT apply

Integrated Windows Authentication (IWA) is a valid silent option for domain/Entra-joined desktop apps in workforce tenants `[verify-at-build]`. Client-credentials availability differs in external (CIAM) tenants — there it's limited to v2.0 applications `[verify-at-build]`. A confidential web app calling Graph for *itself* (not the user) uses client-credentials even though users sign in elsewhere in the app. The flow doesn't change the *credential* choice — see the certificates doc; client-credentials still needs a certificate/managed identity in production, not a secret.

## See also

- [`./auth-certificates-not-secrets-in-production.md`](./auth-certificates-not-secrets-in-production.md) — what confidential-client flows authenticate with
- [`./auth-cache-tokens-with-msal-dont-mint-per-call.md`](./auth-cache-tokens-with-msal-dont-mint-per-call.md) — acquiring/caching tokens once you've picked the flow
- [`./identity-delegated-vs-application-is-a-design-choice.md`](./identity-delegated-vs-application-is-a-design-choice.md) — delegated flows vs the app-only flow
- [`../knowledge/identity-auth-decision-trees.md`](../knowledge/identity-auth-decision-trees.md) — "Which auth flow by client type" tree
- [`../agents/graph-identity-engineer.md`](../agents/graph-identity-engineer.md) — owns the flow choice
- [Microsoft identity platform app types and authentication flows](https://learn.microsoft.com/entra/identity-platform/authentication-flows-app-scenarios) — authoritative scenario→flow table

## Provenance

From the Microsoft Learn "app types and authentication flows", "Authentication flow support in MSAL", and "Choose a Microsoft Graph authentication provider" pages (retrieved 2026-05-30 via Microsoft Learn MCP) — the scenario→flow mapping, the implicit-deprecated / ROPC-not-recommended guidance, and the mandatory-PKCE-for-SPA constraint are drawn directly from them. Codifies team house opinion (flow by client type). External-tenant and IWA specifics are volatile — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
