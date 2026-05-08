# Rule: Security (long form)

Expands on §6 of CLAUDE.md.

## Secrets
- **Never commit:** `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `id_rsa`, `credentials*`, `secrets*`, `service-account*.json`, anything matching `[A-Za-z0-9]{40,}` that looks like a token.
- The repo's `.gitignore` blocks the obvious patterns. The `Read` permission deny-list (in `settings.json`) blocks Claude from reading them.
- If a secret reaches the working tree by mistake: **abort the commit, rotate the key, then clean the tree**. Do not push and "rotate later."

## Untrusted input
The boundary is where input enters your trust domain (HTTP body, query, header, file upload, queue message, env var on first read, third-party API response).

At the boundary:
1. **Parse, don't validate-then-parse.** Use a schema (zod, pydantic, etc.) that returns a typed object on success and rejects everything else.
2. **Reject unknown fields** unless the schema is explicitly tolerant.
3. **Constrain shape:** length, type, range, format. Default to the strictest constraint that lets real users through.
4. **Decode once, in one place.** Don't `JSON.parse` the same blob twice on a request path.

Inside the trust domain, callers can be trusted — don't re-validate everywhere; you'll teach the team that validation is decorative.

## Authentication & sessions
- Passwords: never log them, never include them in error messages, never store them reversibly. Use the language's recommended password hashing (argon2id, bcrypt, scrypt).
- Tokens: cryptographic RNG only. Short-lived access tokens, longer-lived refresh tokens with rotation on use.
- Cookies for browser sessions: `HttpOnly`, `Secure`, `SameSite=Lax` (or `Strict` for sensitive flows). Token-in-localStorage is a smell on session-bearing tokens.
- Logout invalidates server-side state, not just the client cookie.

## Authorization
- Check at the resource, not the route. A user with a valid session is not the same as a user authorized for *this* row.
- Multi-tenant: scope every query by tenant ID at the SQL/query layer. Don't filter in app code after fetching.
- Admin routes: the role check is on the server. Don't rely on the UI hiding the button.

## Crypto
- Use the project's vetted crypto library and a standard, recent mode (e.g. AES-GCM, not ECB; ed25519 for signatures; HKDF for key derivation).
- No DIY crypto. No "I'll just XOR with a key." No re-implementing JWT verification.
- Constant-time comparison for secret equality (`timingSafeEqual` and friends), never `==`.

## SQL & database
- Parameterized queries everywhere. Never string-concatenate user input into SQL.
- Migrations: review for data exposure (new columns visible to which roles?) and for non-zero-downtime patterns (NOT NULL on a populated table without a default + backfill).
- Connection pools have an upper bound; assume yours can be exhausted under load.

## File handling
- Filenames from users: never trust them. Generate your own; record the original name as data, not as a path component.
- Path traversal: resolve to absolute, then assert the result is inside the allowed root.
- Uploads: validate type by content (magic bytes), not extension. Cap size at the boundary.

## Third-party HTTP
- Set timeouts on every outbound call. Default to 5–10 seconds; never unlimited.
- Retries: bounded, with backoff. No "while True, retry."
- Don't follow redirects to arbitrary hosts when the call carries credentials.

## Logging
- Log structurally (key/value), not as freeform strings — easier to redact, easier to query.
- Block-list secrets at the logger, not at every call site. If you ever find yourself sanitizing in a `console.log`, fix the logger instead.
- Never log: passwords, tokens, full credit cards, full SSNs, raw request bodies on error paths.

## Dependency hygiene
- Pin versions. Commit the lockfile.
- New dependency review: who maintains it, when was it last published, what does it pull in, what's its license? If you can't answer all four in 60 seconds, it's not ready to add.
- Audit on add: `npm audit`, `pip-audit`, `cargo audit`, `govulncheck` — run once and look at output.
