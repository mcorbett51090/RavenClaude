---
scenario_id: 2026-06-05-bola-idor-on-nested-resource
contributed_at: 2026-06-05
plugin: api-engineering
product: rest-openapi
product_version: "unknown"
scope: likely-general
tags: [bola, idor, owasp-api1, authorization, jwt, scope, multi-tenant]
confidence: high
reviewed: false
---

## Problem

A multi-tenant SaaS exposed `GET /invoices/{invoiceId}` and `GET /accounts/{accountId}/invoices`. Authentication was solid — every request carried a validated JWT with the caller's `account_id` claim, and the endpoints checked that the token was present, well-formed, and unexpired. But a customer's security researcher found that **any authenticated user could read any other tenant's invoice** by guessing or enumerating `invoiceId` (sequential integers). The token was valid; the object it pointed at belonged to someone else. This is OWASP **API1:2023 Broken Object Level Authorization (BOLA / IDOR)** — the single most common and most damaging API vulnerability.

## Constraints context

- The mental model in the code was "authenticated ⇒ authorized" — the team conflated *who you are* (authentication, which they did well) with *what you may touch* (object-level authorization, which they skipped).
- The collection route `/accounts/{accountId}/invoices` *looked* scoped, but the handler trusted the `accountId` in the **path** rather than the `account_id` in the **token** — so a caller could pass someone else's `accountId` in the URL.
- IDs were sequential integers, which made enumeration trivial; but the team's first instinct ("switch to UUIDs") treats the symptom, not the cause.
- Per the constitution, any authorization/exposure **verdict** is not this team's to make alone — the control is designed here and the verdict escalates to `ravenclaude-core/security-reviewer`.

## Attempts

- Tried: switching sequential integer IDs to UUIDs. Reduced *enumerability* but is **not** a fix — a leaked, logged, or shared UUID is still readable by anyone, because there's still no ownership check. Security-by-obscurity, not authorization.
- Tried: a global API gateway rule "require a valid token." Already in place; it's the authentication layer, and BOLA lives *below* it — the gateway can't know whether *this* token may read *this* object.
- Tried (the resolution): an explicit, server-side, per-request ownership check on every object access, derived from the token — never from the client-supplied ID.

## Resolution

**Authorize the object, server-side, on every request, from the identity in the token — never trust an ID from the client.** The fix:

1. **Every object fetch carries an ownership predicate.** `GET /invoices/{invoiceId}` becomes `SELECT ... WHERE id = :invoiceId AND account_id = :token_account_id`. If the row isn't owned by the caller's tenant, return **404** (not 403 — a 403 confirms the object exists, which is itself an enumeration oracle).
2. **Derive the tenant from the token, not the path.** For `/accounts/{accountId}/invoices`, assert `path.accountId == token.account_id` (or that the token grants access to that account) *before* the query — a mismatch is 404. The URL is caller-supplied input; the token is the trust anchor.
3. **Centralize the check so it can't be forgotten.** A per-resource authorization helper (or policy middleware) that every handler must call, plus a test that a cross-tenant fetch returns 404 for *every* object-bearing route. The vulnerability recurs because the check is per-handler and easy to omit — make omitting it the thing that fails the build.
4. **Scopes are necessary but not sufficient.** A `read:invoices` scope says the *client* may read invoices in general (function-level, API5/BFLA); it does **not** say this caller may read *this* invoice (object-level, API1/BOLA). You need both: scope check (may you call this operation?) **and** object check (may you touch this instance?).
5. **UUIDs are defense-in-depth, not the fix.** Adopt them to reduce the enumeration blast radius, but only *after* the ownership check is in place — never instead of it.

The mental model: authentication answers "who are you?", function-level authz answers "may you call this kind of operation?", and object-level authz answers "may you touch *this specific* thing?" BOLA is forgetting the third question. Every endpoint that takes a resource ID must answer it.

**Action for the next engineer:** for every route that accepts an object ID (path, query, or body), write down "who owns this object, and where does that ownership check happen?" If the answer is "we check the token is valid" — that's authentication, not authorization, and you have a BOLA. Return 404 on ownership failure, derive the tenant from the token, and add a cross-tenant-access test per object route. **Escalate the exposure verdict to `ravenclaude-core/security-reviewer`** — this team designs the control; the security reviewer signs off on whether the surface is acceptable.

Cross-reference: complements [`../knowledge/api-security-decision-trees.md`](../knowledge/api-security-decision-trees.md) (the OWASP control map + object-vs-function authZ tree), [`../best-practices/secure-authorize-every-object-bola.md`](../best-practices/secure-authorize-every-object-bola.md), and [`../best-practices/secure-validate-tokens-and-scopes-server-side.md`](../best-practices/secure-validate-tokens-and-scopes-server-side.md). OWASP API Security Top 10 (2023), API1 — https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/ (retrieved 2026-06-05).
