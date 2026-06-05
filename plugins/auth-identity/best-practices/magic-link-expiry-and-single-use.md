# Magic Links Must Expire Quickly and Be Single-Use

**Status:** Absolute rule
**Domain:** Auth & Identity — Passwordless / magic link
**Applies to:** `auth-identity`

---

## Why this exists

A magic link is a bearer token delivered over email. Email is not a secure channel — it may be forwarded, archived, accessed from a shared device, cached by a mail provider's indexer, or intercepted in transit. If the magic link does not expire and is not invalidated after first use, it is a reusable credential sitting in an email inbox indefinitely. An attacker with access to the email account (or even read access to archived email) can log in as the user at any future time. Both short expiry (preventing opportunistic use after the session ends) and single-use invalidation (preventing replay) are required.

## How to apply

**Magic link security requirements:**

| Property | Requirement | Rationale |
|---|---|---|
| Expiry | ≤ 15 minutes | Limits the window of a stolen link |
| Single-use | YES — invalidated on first click | Prevents replay attacks |
| Entropy | ≥ 128 bits (32 random bytes) | Makes brute-forcing infeasible |
| Delivery | Over HTTPS email link | Never send the token in plain text in the email body as a copyable string |

**Supabase magic link (implements all requirements automatically):**

```javascript
const { data, error } = await supabase.auth.signInWithOtp({
  email: 'user@example.com',
  options: {
    emailRedirectTo: 'https://app.example.com/auth/callback',
    // Supabase handles expiry (1 hour default, configurable) and single-use
  }
});
```

**Supabase configuration (project settings):**
- OTP expiry: set to 900 seconds (15 min) or the shortest value your UX supports.
- Supabase marks the OTP as used on first access — do not call the verify endpoint a second time.

**Do:**
- Set magic link expiry to 15 minutes or less.
- Show a user-friendly message when a link has expired: "This link has expired. [Request a new one]" — not a raw error.
- Log every magic link use (success and failure) for security audit: timestamp, user ID, IP.

**Don't:**
- Set magic link expiry to 24 hours or longer — that is a login credential with a multi-hour theft window.
- Reuse the same magic link token for a second sign-in after the first has completed.
- Include the raw token in the email's visible body as a copyable string — only as part of a URL the user clicks.

## Edge cases / when the rule does NOT apply

- **One-time verification codes (OTP by SMS or email, digit-based)**: these are a different variant of passwordless auth. Apply the same expiry and single-use rules, but the delivery format is a 6-digit code, not a link. SMS OTP carries additional SIM-swap risk; email OTP + magic link is preferred.
- **Password reset links**: the same expiry and single-use requirements apply. Password reset links are magic links with a different post-authentication action.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the magic link flow and expiry configuration
- [`./passkeys-need-a-fallback.md`](./passkeys-need-a-fallback.md) — magic link is the recommended fallback when passkeys are the primary method

## Provenance

Codifies security requirements for passwordless token delivery from `social-and-passwordless-providers-2026.md`. Magic link security recommendations from OWASP Authentication Cheat Sheet (verified 2026-06-05). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
