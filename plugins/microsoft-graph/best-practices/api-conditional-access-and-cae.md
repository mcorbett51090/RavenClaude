# Handle Continuous Access Evaluation 401 challenges — do not treat all 401s as re-authentication

**Status:** Primary diagnostic
**Domain:** Microsoft Graph / auth / resilience
**Applies to:** `microsoft-graph`

---

## Why this exists

Microsoft Graph tenants with Continuous Access Evaluation (CAE) enabled can revoke a token mid-lifetime — if the user is disabled, their location changes to a blocked IP, or an admin revokes all sessions. When this happens, Graph returns a `401 Unauthorized` with a `WWW-Authenticate` header that includes `claims="<base64-challenge>"`. An application that catches all `401` responses and silently calls `acquireToken()` with no claims challenge will get a new token from MSAL's cache (which is still valid from MSAL's perspective) and retry — and receive another `401` in an infinite loop. CAE-aware handling requires passing the claims challenge back to the token-acquisition call so Entra can issue a fresh, condition-passing token.

## How to apply

```python
import base64, json
from msal import PublicClientApplication

def handle_cae_challenge(response):
    """Extract CAE claims challenge from a 401 WWW-Authenticate header."""
    www_auth = response.headers.get("WWW-Authenticate", "")
    if "claims=" not in www_auth:
        return None
    # Extract the base64-encoded claims value
    for part in www_auth.split(","):
        if "claims=" in part:
            b64_claims = part.strip().split("claims=")[1].strip('"')
            return base64.urlsafe_b64decode(b64_claims + "==").decode()
    return None

# In your request loop:
result = graph_call()
if result.status_code == 401:
    claims = handle_cae_challenge(result)
    if claims:
        # Pass the claims challenge to MSAL — this forces a fresh token
        new_token = app.acquire_token_silent(scopes, account, claims_challenge=claims)
        # Retry the Graph call with the new token
```

The Graph SDK's built-in `ContinuousAccessEvaluationMiddleware` (available in the .NET and JavaScript SDKs) handles this automatically — use the SDK.

**Do:**
- Opt in to CAE by sending `cp1` in the client capabilities header at token acquisition: `{"xms_cc": {"values": ["cp1"]}}` in MSAL.
- Use the Graph SDK — it handles CAE challenges transparently in supported SDK versions.
- Log the CAE challenge event with its claims value so the security team can review forced re-authentication patterns.

**Don't:**
- Suppress all `401` responses with a generic re-authenticate-and-retry without checking for the claims challenge first.
- Treat a CAE `401` as a credential error — it is a policy enforcement event, not a bad secret or expired token.
- Disable CAE handling as a "simplification" — tenants with Conditional Access policies require CAE-aware clients for correct behavior.

## Edge cases / when the rule does NOT apply

For daemon/service-to-service flows (application permissions, no user context), CAE events are less common but can still occur for IP-location policies applied to service principals. The same claims-challenge handling applies.

## See also

- [`../agents/graph-api-engineer.md`](../agents/graph-api-engineer.md) — owns SDK selection and resiliency patterns
- [`./auth-cache-tokens-with-msal-dont-mint-per-call.md`](./auth-cache-tokens-with-msal-dont-mint-per-call.md) — the token-caching rule that interacts with CAE handling

## Provenance

Codifies CLAUDE.md §3 #5 (resilience — 429/Retry-After) extended to the `401`/CAE challenge surface; Microsoft Graph CAE documentation and MSAL claims-challenge API reference.

---

_Last reviewed: 2026-06-05 by `claude`_
