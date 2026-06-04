# Authorize every function (BFLA / OWASP API5)

**Status:** Absolute rule — hiding a button is not authorization; the verdict escalates to security-reviewer.

**Domain:** API security / authorization

**Applies to:** `api-engineering`

---

## Why this exists

**Broken Function Level Authorization** (OWASP API5:2023) is when a privileged function — an admin action, another role's operation — is reachable by any authenticated caller because the server never checks the caller's role/scope. The classic case: the admin UI hides the "delete user" button, but `DELETE /users/{id}` itself has no role gate, so any user who discovers the route can call it. BFLA is *function* access (a capability you shouldn't have); BOLA is *object* access (data you shouldn't see) — both must be enforced server-side.

## How to apply

Gate every privileged function by role/scope on the server, independent of the UI.

```
@require_scope("users:delete")          # enforced server-side, every call
def delete_user(target_id, principal):
    if not principal.has_role("admin"):
        raise Forbidden()               # 403 — function-level gate
    ...
```

**Do:**
- Default-deny: a new endpoint is unauthorized until a role/scope is explicitly granted.
- Map scope → operation in one place; enumerate admin/privileged endpoints and confirm each is gated.
- Test that a non-privileged token gets `403` on every privileged function.

**Don't:**
- Rely on the route being unlinked, the button being hidden, or the endpoint being "internal/undocumented."
- Gate by guessable conventions (`/admin/...` path) without an actual role check.

## Edge cases / when the rule does NOT apply

Functions intended for all authenticated users need only authentication, not a special role — but that's a decision to record. HTTP method matters: `GET /admin/users` and `DELETE /admin/users/{id}` may warrant different scopes; gate per operation, not per path.

## See also

- [`./secure-authorize-every-object-bola.md`](./secure-authorize-every-object-bola.md)
- [`./secure-validate-tokens-and-scopes-server-side.md`](./secure-validate-tokens-and-scopes-server-side.md)
- [OWASP API5:2023 — Broken Function Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/) — authoritative

## Provenance

Codifies house opinion #7 (CLAUDE.md §3) and OWASP API5:2023. Web-verified 2026-06-04. **Verdict escalates to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_
