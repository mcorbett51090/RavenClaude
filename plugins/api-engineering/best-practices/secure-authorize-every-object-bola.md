# Authorize every object on every request (BOLA / OWASP API1)

**Status:** Absolute rule — the #1 API breach; the verdict escalates to security-reviewer.

**Domain:** API security / authorization

**Applies to:** `api-engineering`

---

## Why this exists

**Broken Object Level Authorization** is the most common and most damaging API vulnerability (OWASP API1:2023). The pattern: an endpoint takes an object ID (`GET /accounts/{id}`), and the server returns the object *without checking that this caller is entitled to it*. An attacker increments or guesses the ID and reads every other tenant's data. The ID in the URL is **the attacker's input** — being authenticated is not being authorized for *this object*.

## How to apply

On every object access, verify ownership/tenancy server-side, derived from the authenticated principal — never from the request.

```
def get_account(account_id, principal):
    acct = repo.find(account_id)
    if acct is None or acct.tenant_id != principal.tenant_id:   # the check
        raise NotFound()        # 404 (or 403) — do not leak existence
    return acct
```

**Do:**
- Scope every query by the principal's tenant/owner (`WHERE id = ? AND tenant_id = ?`), not by the ID alone.
- Use unguessable IDs (UU/ULID) as defense-in-depth — but never *instead* of the check.
- Test the negative case explicitly: a different tenant's ID must `403`/`404`.

**Don't:**
- Trust a client-supplied ID, tenant, or `userId` in the body/query; authorize off the token's claims only.
- Rely on "the ID is random so they can't guess it" as the control.

## Edge cases / when the rule does NOT apply

Genuinely public resources (a public product catalog) need no per-object owner check — but confirm "public" is a decision, not an oversight. Admin/cross-tenant access is a *function-level* grant (BFLA) layered on top, not an exception to object checks.

## See also

- [`./secure-authorize-every-function-bfla.md`](./secure-authorize-every-function-bfla.md)
- [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md)
- [OWASP API1:2023 — Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) — authoritative

## Provenance

Codifies house opinion #7 (CLAUDE.md §3) and OWASP API1:2023 (BOLA, ~40% of API attacks). Web-verified 2026-06-04. **Verdict escalates to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_
