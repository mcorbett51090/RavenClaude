# Document Authentication Before Any Feature

**Status:** Absolute rule
**Domain:** Technical Writing — API / developer documentation
**Applies to:** `technical-writing-docs`

---

## Why this exists

A developer cannot use any API feature until authentication works. An API reference that leads with the widget endpoints and buries authentication in a subsection on page 4 forces every new reader to hunt for the prerequisite before they can run a single call. Authentication is a cross-cutting dependency of every feature in the API; it belongs at the top of the quickstart guide and in its own prominent section in the reference, with working, copy-paste-runnable examples before anything else.

## How to apply

**Recommended docs structure for APIs:**

```
1. Authentication (always first)
   - How to obtain credentials
   - How to authenticate a request (with a runnable example)
   - Token lifetime, refresh, and revocation
   - Error codes specific to auth (401, 403)

2. Quick Start (second — uses authentication from step 1)
   - Make your first authenticated call
   - A successful response you can see

3. [Feature endpoints, SDK methods, etc.]
```

**Authentication page minimum content:**

```markdown
## Authentication

All requests require a Bearer token in the `Authorization` header:

```http
GET /v1/widgets HTTP/1.1
Authorization: Bearer YOUR_API_KEY
```

**Getting your key:** Sign in at [dashboard.example.com/keys](https://dashboard.example.com/keys)
and generate a key under **Settings → API Keys**.

**Token lifetime:** Keys do not expire unless rotated manually. Rotate after any suspected
compromise.

**Auth errors:**
| Code | Meaning | Fix |
|------|---------|-----|
| 401 | Missing or invalid key | Check the header format and key value |
| 403 | Key lacks permission for this endpoint | Check the key's assigned scopes |
```

**Do:**
- Include a runnable `curl` or SDK example in the authentication section — "make one real authenticated request" is the first success.
- Link to the auth section from every feature page ("requires authentication — see [auth setup]").
- Document *both* the success path and the two most common failure modes (401 invalid key, 403 wrong scope).

**Don't:**
- Document authentication only in the quickstart and assume developers reading the reference remember it.
- Use placeholder values (`YOUR_API_KEY`) without also showing where to get a real key.
- Mix auth documentation with credential storage advice — auth describes the protocol; secret management (where to put the key) is a separate section.

## Edge cases / when the rule does NOT apply

- **Public/open APIs with no authentication**: the first section is the resource model, not auth. Still document any rate-limiting or IP restrictions that function as implicit access control.
- **Internal-only APIs consumed by a single trusted service**: "authentication" may be network-layer-only; document the network trust model instead.

## See also

- [`../agents/api-reference-writer.md`](../agents/api-reference-writer.md) — owns the authentication section of the reference
- [`./optimize-time-to-first-success.md`](./optimize-time-to-first-success.md) — authentication unblocked is the prerequisite to first-success

## Provenance

Codifies standard API documentation practice derived from high-quality API docs (Stripe, Twilio, GitHub REST API) and house opinion #6 ("Show the unhappy path — errors, edge cases, and limits") applied to auth. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
