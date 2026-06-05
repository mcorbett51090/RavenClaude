# Rate-limit Auth Endpoints at the Application Layer

**Status:** Absolute rule
**Domain:** Auth & Identity — Brute-force protection
**Applies to:** `auth-identity`

---

## Why this exists

Login, password-reset, magic-link, and OTP endpoints are the natural target for brute-force and credential-stuffing attacks. A managed provider (Supabase Auth, Clerk, Auth0) applies its own rate limits internally, but those limits only protect the provider's API — not your own API endpoints that verify sessions, issue tokens, or accept OTP codes. An unrated `/api/verify-otp` or `/api/reset-password` endpoint can be exhausted in seconds. The attack surface is especially acute for OTP endpoints: a 6-digit code has only 1,000,000 combinations, and an unrated endpoint is a brute-force invitation.

## How to apply

**Managed provider path (Supabase Auth / Clerk / Auth0):**

For login and sign-up routed entirely through the provider SDK, the provider's built-in rate limits apply. Verify and document those limits in the ADR; do not assume they are sufficient for your threat model without checking.

**Your own auth-adjacent API endpoints:**

```typescript
// Next.js middleware example using upstash/ratelimit
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "1 m"), // 10 attempts per minute per IP
  analytics: true,
});

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for") ?? "unknown";
  const { success, reset } = await ratelimit.limit(`auth:${ip}`);

  if (!success) {
    return Response.json(
      { error: "Too many requests" },
      {
        status: 429,
        headers: { "Retry-After": String(Math.ceil((reset - Date.now()) / 1000)) },
      },
    );
  }
  // ... rest of handler
}
```

**Tier the limits by endpoint sensitivity:**

| Endpoint | Recommended limit | Key |
|---|---|---|
| Login / sign-in | 5 per minute per IP | IP + email |
| Password reset request | 3 per hour per IP | IP + email |
| OTP / magic-link verify | 10 per 15 minutes per IP | IP + session |
| Token refresh | 30 per minute per IP | IP |
| OAuth callback | 20 per minute per IP | IP |

**Do:**
- Apply limits by IP **and** by user identifier (email/user ID) when known — IP-only limits are bypassable from distributed botnets.
- Return `429 Too Many Requests` with a `Retry-After` header — do not return `401` or `403`, which can leak information.
- Lock out the account or require CAPTCHA after N consecutive failures, not just per-IP limiting.
- Log and alert on high-failure-rate patterns — they are credential-stuffing signals.

**Don't:**
- Apply the same loose rate limit across all auth endpoints uniformly — OTP and password-reset endpoints need tighter limits than token-refresh.
- Rate-limit only at the CDN layer and assume that is sufficient — CDN rules can be misconfigured or bypassed.
- Silently drop requests — always return 429 so legitimate retry logic can back off correctly.

## Edge cases / when the rule does NOT apply

- **Internal service-to-service endpoints** using mTLS or signed JWTs with no user-facing brute-force surface: IP-based rate limiting adds little value and may interfere with legitimate high-frequency internal callers. Apply limits by service identity instead.
- **Development / test environments** behind a private network: rate limiting can be relaxed for development velocity, but must be re-enabled before production deploy.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the rate-limit middleware
- [`../agents/auth-architect.md`](../agents/auth-architect.md) — sets the threat model that determines limit tiers

## Provenance

Codifies standard brute-force protection guidance from OWASP Authentication Cheat Sheet and OWASP Credential Stuffing Prevention Cheat Sheet. Necessary supplement to managed-provider protections, which cover the provider's endpoints but not any custom auth-adjacent API routes.

---

_Last reviewed: 2026-06-05 by `claude`_
