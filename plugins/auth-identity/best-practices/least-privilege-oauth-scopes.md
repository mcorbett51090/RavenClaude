# Request the Minimum OAuth Scopes the Feature Needs

**Status:** Absolute rule
**Domain:** Auth & Identity — OAuth scope hygiene
**Applies to:** `auth-identity`

---

## Why this exists

Over-broad OAuth scopes are the most common preventable consent-screen friction and the most preventable blast-radius problem in auth. Requesting `https://mail.google.com/` ("read all your email") when the feature only needs `openid email profile` triggers Google's OAuth verification process, shows a "sensitive scope" warning on the consent screen, and causes 30–50% of users to abandon the flow (verified 2026-06-03 — Google OAuth sensitivity thresholds; see `oauth-oidc-and-google-sso.md`). If the token is later stolen or leaked, overly broad scopes give the attacker capabilities far beyond the original feature. House opinion #6 states this: "Least-privilege scopes — request only what the feature needs."

## How to apply

**Google scope tiers and when to use them:**

| Scope | What it grants | Use when |
|---|---|---|
| `openid` | ID token (authentication only) | Always include for OIDC |
| `email` | User's email address | Need to identify the user by email |
| `profile` | Name, profile photo, locale | Need display name or avatar |
| `https://www.googleapis.com/auth/calendar.readonly` | Read-only calendar access | Only read calendar events |
| `https://www.googleapis.com/auth/gmail.modify` | Full Gmail read/write | Requires Google verification; use only if the core product feature is email |

**General principles:**

- **`openid email profile` is the correct scope for plain Google SSO** — it gives you the ID token, verifiable email, and display name. Nothing more is needed for authentication.
- **Separate features = separate authorization steps**: don't bundle all possible future scopes into the initial login. Use incremental authorization (add scopes when the feature needs them, not upfront).
- **Sensitive scopes trigger Google verification**: any scope beyond the basic profile tier triggers a Google OAuth verification review. Scope your initial integration to the non-sensitive tier; add sensitive scopes only when the feature ships and only in a separate authorization request.

**Incremental authorization pattern (Google / Supabase):**

```javascript
// Step 1: Login — basic scopes only
supabase.auth.signInWithOAuth({ provider: 'google',
  options: { scopes: 'openid email profile' } });

// Step 2: User clicks "Connect Google Calendar" — request just the new scope
supabase.auth.signInWithOAuth({ provider: 'google',
  options: {
    scopes: 'https://www.googleapis.com/auth/calendar.readonly',
    queryParams: { access_type: 'offline', include_granted_scopes: 'true' }
  }
});
```

**Do:**
- Audit scopes at code review time: any scope beyond `openid email profile` requires a written justification in the PR.
- Remove scopes that are no longer used when a feature is removed.
- Test the consent screen before launch to verify which scopes appear and whether a "sensitive scope" warning is shown.

**Don't:**
- Request Gmail/Drive/Calendar/Contacts scopes in the initial login flow "just in case we need them later."
- Treat the scope request as a one-time setup — scope requirements change as features are added and removed.
- Bundle multiple unrelated feature scopes into a single authorization request.

## Edge cases / when the rule does NOT apply

- **Service accounts (machine-to-machine)**: OAuth scopes for service accounts are fixed to the service role at provisioning time, not requested interactively. Apply the least-privilege principle at the service-account permission level, not the OAuth scope level.

## See also

- [`../agents/auth-architect.md`](../agents/auth-architect.md) — makes the scope decision during the auth design
- [`./use-authorization-code-pkce-never-implicit.md`](./use-authorization-code-pkce-never-implicit.md) — the companion rule on OAuth flow selection

## Provenance

Codifies house opinion #6 ("Least-privilege scopes") from `CLAUDE.md` §3. Google OAuth scope sensitivity thresholds: developers.google.com/identity/protocols/oauth2/scopes (verified 2026-06-03). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
