# Require Step-Up Authentication for Sensitive Actions

**Status:** Pattern
**Domain:** Auth & Identity — Session security
**Applies to:** `auth-identity`

---

## Why this exists

A session established hours ago is not the same security guarantee as a session established 30 seconds ago. An attacker who hijacks or borrows a long-running session — from an unattended workstation, a session-cookie theft, or a XSS — inherits whatever the session allows. For most page views and reads, this is an acceptable risk. For sensitive operations — changing the account email, resetting the password, adding a new payment method, approving a large transaction, accessing admin controls — it is not. Step-up authentication re-verifies the user's identity at the point of the sensitive action, narrowing the attack window to the authentication moment rather than the full session lifetime. This is distinct from MFA at login: step-up is a targeted re-challenge issued only for high-value operations.

## How to apply

**Identify the sensitive-action list for your application:**

| Action type | Step-up required? |
|---|---|
| View profile / dashboard | No |
| Change email or password | Yes |
| Add or remove MFA device | Yes |
| Add payment method | Yes |
| Approve transaction above threshold | Yes |
| Access admin / super-user controls | Yes |
| Export or bulk-download data | Consider by size/sensitivity |
| Read-only data access | No |

**Implementation pattern — `authenticated_at` claim check:**

```typescript
// Middleware: check that the session was authenticated within a recency window
async function requireRecentAuth(
  req: Request,
  maxAgeSeconds = 300, // 5 minutes for sensitive actions
): Promise<Response | null> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return Response.redirect("/login");

  const authenticatedAt = user.confirmed_at
    ? new Date(user.confirmed_at).getTime()
    : 0;
  const ageSeconds = (Date.now() - authenticatedAt) / 1000;

  if (ageSeconds > maxAgeSeconds) {
    // session is too old for this action — redirect to step-up challenge
    return Response.redirect(
      `/auth/step-up?next=${encodeURIComponent(req.url)}&reason=sensitive_action`,
    );
  }
  return null; // continue
}

// Protect a sensitive route
export async function POST(req: Request) {
  const stepUpRequired = await requireRecentAuth(req, 300);
  if (stepUpRequired) return stepUpRequired;
  // ... perform the sensitive action
}
```

**Step-up challenge options (simplest first):**

1. **Password re-entry** — prompt the user to re-enter their password; validate with the auth provider. Supabase: `supabase.auth.reauthenticate()` (email/phone re-auth). [verify current API in Supabase docs]
2. **TOTP / HOTP code** — if the user has MFA enrolled, require a TOTP code regardless of whether the session MFA was already satisfied.
3. **Push notification or hardware key** — for highest-sensitivity actions (admin ops, large transactions).

**Do:**
- Scope the recency window to the action's risk: payment add → 5 min, email change → 15 min, view dashboard → no step-up.
- After a successful step-up, record `step_up_at` in the session and use it (not `authenticated_at`) for that action's recency check.
- Show the user a clear explanation of why they are being re-challenged ("To change your email, please confirm your password").
- Route step-up implementation through `ravenclaude-core/security-reviewer` — it touches session state.

**Don't:**
- Apply step-up to low-sensitivity reads — it degrades UX without a security benefit.
- Treat step-up as a substitute for short session lifetimes; both layers serve different threats.
- Trust a client-provided "last authenticated at" timestamp — derive it from the server-side session record or provider claims.

## Edge cases / when the rule does NOT apply

- **CLI / service-to-service auth:** session recency is not the right model; use short-lived access tokens issued per-request.
- **Applications with no sensitive write operations** (read-only public tools): step-up adds friction without benefit.
- **Highly regulated environments where every action requires MFA:** if MFA is required at login for all sessions, step-up is part of the baseline, not an escalation. Verify that the baseline MFA is actually enforced before skipping step-up design.

## See also

- [`../agents/auth-architect.md`](../agents/auth-architect.md) — identifies the sensitive-action list and designs the step-up challenge
- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements `requireRecentAuth` middleware and the step-up challenge flow
- [`./rotate-refresh-tokens-on-use.md`](./rotate-refresh-tokens-on-use.md) — refresh rotation is the companion control that limits the blast radius of an old session

## Provenance

Codifies the NIST SP 800-63B concept of step-up authentication for sensitive operations. Aligns with OAuth 2.0 Step Up Authentication Challenge Protocol (RFC 9470). Standard practice in financial applications, identity-provider consoles, and admin panels where session recency is a first-class security control.

---

_Last reviewed: 2026-06-05 by `claude`_
