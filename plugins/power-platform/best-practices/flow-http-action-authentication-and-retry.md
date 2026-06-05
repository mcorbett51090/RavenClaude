# Use the HTTP action's built-in auth and retry — do not hand-roll bearer tokens or catch-and-retry manually

**Status:** Pattern
**Domain:** Power Automate cloud flows
**Applies to:** `power-platform`

---

## Why this exists

The Power Automate HTTP action has a built-in authentication picker (Managed Identity, Active Directory OAuth, Basic, API Key, Client Certificate) and a native retry policy. Engineers who hand-roll `Authorization: Bearer ...` with a preceding `Get secret from Key Vault` action create a three-action sequence that: re-acquires a token on every run (instead of caching), embeds the secret value in the run history (visible in the Portal), and requires manual retry logic in a `Scope`-based catch block. The built-in auth never surfaces the credential value in run history and handles token refresh automatically.

## How to apply

In the HTTP action → Authentication:

| Backend type | Correct auth choice |
|---|---|
| Entra-protected API (same tenant) | **Active Directory OAuth** (or Managed Identity if the flow runs on a gateway) |
| Third-party API key | **API key** (header or query param) stored as an env var secret reference |
| mTLS / certificate | **Client Certificate** (upload the PFX inline — store the PFX base64 in Key Vault, read at build time) |
| Basic | **Basic** — but flag for upgrade to OAuth2 |

Retry policy (set on the action's `settings` panel):
```json
{
  "retryPolicy": {
    "type": "exponential",
    "count": 4,
    "interval": "PT7S",
    "minimumInterval": "PT5S",
    "maximumInterval": "PT1H"
  }
}
```

**Do:**
- Use Managed Identity for HTTP calls to Azure services when the flow's environment has a managed identity configured — zero credentials to manage.
- Store OAuth2 client secrets as Key Vault references in environment variables, not as plaintext env var defaults.
- Confirm the retry policy `count` and `interval` are appropriate for the backend's throttling envelope — a third-party API with a 60-second rate window needs a 60-second minimum retry interval.

**Don't:**
- Compose the `Authorization` header manually from a secret — the value appears in run inputs in the monitoring portal even if the connector is "secure inputs."
- Set `type: "none"` on a retry policy and implement your own `Do until / Status code = 200` loop — the native retry is simpler and honored by the flow engine's run-history recording.
- Use the HTTP Webhook action for a polling-based API — HTTP Webhook is for callback registration, not polling; use HTTP + retry.

## Edge cases / when the rule does NOT apply

When calling an on-premises system via the on-premises data gateway, Managed Identity is not available. Use the `Active Directory OAuth` type with a service-principal credential stored in Key Vault.

## See also

- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — owns HTTP action design
- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — the broader try/catch/retry pattern this rule plugs into

## Provenance

Codifies `flow-engineer`'s opinion from CLAUDE.md §3 #8 and #10 applied to the HTTP action specifically; aligned with `connector-custom-connector-auth-and-policy` pattern; standard domain practice confirmed in Power Automate HTTP action documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
