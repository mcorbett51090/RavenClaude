# Never Hard-Code Client Secrets, Service Keys, or Signing Keys in Source

**Status:** Absolute rule
**Domain:** Auth & Identity — Secrets management
**Applies to:** `auth-identity`

---

## Why this exists

A client secret, service role key, or JWT signing key committed to source control is a public credential the moment the repository is ever pushed to a shared host — including a "private" GitHub repo that could be made public, leaked, or whose access is later expanded. The anti-pattern is in `CLAUDE.md` §4: "Hard-coding a client secret / signing key / service key in source (must live in env / a secret store; the service key never reaches the browser)." Unlike a rotated password, a leaked signing key may have signed tokens that are still valid; recovering from it requires key rotation AND invalidating all previously-issued tokens.

## How to apply

**Secret classification and allowed location:**

| Secret type | Development | CI/CD | Production |
|---|---|---|---|
| OAuth client secret (Google, Apple, GitHub) | `.env.local` (gitignored) | CI secret (GitHub Actions `secrets.*`) | Secret manager or provider env var |
| Supabase service role key | `.env.local` | CI secret | Platform env var (Vercel, Fly, etc.) |
| JWT signing key / HMAC secret | `.env.local` | CI secret | Secret manager |
| Supabase anon key | Env var (public) | Public | Public (this is safe to expose — it has no server-side privileges) |

**Project `.gitignore` (required):**

```gitignore
.env
.env.local
.env.*.local
*.pem
*.p8         # Apple private key
secrets/
```

**Pre-commit protection (recommended):**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

**Loading secrets at runtime:**

```javascript
// Correct — loaded from environment, never from source
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!supabaseServiceKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY is not set');

// Never
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';  // WRONG
```

**Do:**
- Run `git secret scan` or gitleaks on every PR in CI.
- Rotate any secret that was ever committed to source, even for a single commit — assume it is compromised.
- Use separate secrets for development and production environments.

**Don't:**
- Store secrets in `appsettings.json`, `config.yaml`, or any file that is checked in.
- Use the Supabase service role key client-side — it bypasses Row Level Security and must only be used in trusted server contexts.
- Accept "it's a private repo" as a justification for leaving a secret in source.

## Edge cases / when the rule does NOT apply

- **Public/anon keys** (Supabase anon key, public OAuth client ID): these are intentionally public and safe to include in client-side code. The distinction is: if the key has server-side privileges or can authenticate as a service, it is a secret; if it only identifies the application to the provider (and the provider enforces its own access controls), it is public.

## See also

- [`../agents/auth-implementation-engineer.md`](../agents/auth-implementation-engineer.md) — implements the secret-loading pattern in application code

## Provenance

Codifies the anti-pattern "Hard-coding a client secret / signing key / service key in source" from `CLAUDE.md` §4. OWASP Secrets Management Cheat Sheet (verified 2026-06-05). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
