---
name: ship-app-store-ready
description: "Make a Shopify build correct, secure, and App-Store-review-ready: HMAC-verify every webhook + process idempotently + fast-200-async, implement the mandatory GDPR/data webhooks (customers/redact, shop/redact, customers/data_request), authenticate embedded requests with session tokens (not cookies) over OAuth, charge through the Billing API, handle GraphQL cost-based rate limits with back-off + bulk operations (never a hot pagination loop), pin the Admin API version, and build the current-generation way (Shopify Functions / checkout UI extensions / App Bridge+Polaris, never script tags or checkout.liquid). Reach for this when the ask is 'wire up OAuth + a webhook', 'why are we getting throttled?', 'is this ready for App Store review?', or 'build the Function/extension/embedded page'. Used by `shopify-app-engineer` (primary)."
---

# Skill: ship-app-store-ready

> **Invoked by:** `shopify-app-engineer` (primary). Consulted by `shopify-app-architect` to confirm the design will clear review before committing.
>
> **When to invoke:** "wire up OAuth + a webhook"; "build the Shopify Function / checkout extension / embedded Polaris page / theme section"; "why are we getting throttled?"; "is this ready for App Store review?"
>
> **Output:** review-passing, current-generation Shopify code with auth verified, rate limits handled, GDPR webhooks present, and API versions pinned — never a deprecated-path or unverified-payload build.

## Procedure

1. **Pin the API version and verify current field names/limits first.** Don't trust training-era API shape; confirm against current docs and pin the Admin API version in every call. Traverse [`../../knowledge/shopify-decision-tree.md`](../../knowledge/shopify-decision-tree.md).
2. **Secure auth.** OAuth for install; **session tokens** (App Bridge JWT) for embedded-app requests, not cookies. Request minimal scopes.
3. **Verify and harden every webhook.** **HMAC-validate** the payload before trusting it; process **idempotently** (dedupe on event/resource id); return a **fast 200** and do work async. Implement the **mandatory GDPR/data webhooks** and the `app/uninstalled` cleanup.
4. **Handle rate limits by design.** Budget GraphQL query cost, back off honoring the returned cost/available fields, and use **bulk operations** for large reads/writes — never a tight pagination loop (the classic self-throttle bug).
5. **Build the current-generation way.** Shopify **Functions** for discount/checkout/shipping/validation logic; **checkout UI extensions** for checkout UI; **App Bridge + Polaris** for embedded admin UI; **OS 2.0 sections/app blocks** for themes. No script tags, no `checkout.liquid`.
6. **Charge through the Billing API** — recurring/usage/one-time, on-platform, clearly disclosed.
7. **Walk the App Store review categories** (functionality/OAuth, GDPR webhooks, performance, security, billing, listing quality — exact items **verify-at-use**) and fix anything that would reject. Escalate the review-readiness **test pass** to `qa-test-automation` and deep OAuth/session hardening to `auth-identity`.

## Worked example

> User: "Our app keeps getting throttled when we sync all products, and Shopify flagged our webhooks in review."

- **Throttle root cause:** a tight pagination loop pulling every product page as fast as possible → blows the GraphQL cost budget. **Fix:** switch the large read to a **bulk operation** (async export), and for incremental calls budget cost + back off on the returned throttle fields. The throttle was predictable from the cost model.
- **Webhook flag:** review found handlers returning 200 slowly and no HMAC verification. **Fix:** HMAC-validate every payload, return 200 immediately and enqueue the work, dedupe on id for idempotency.
- **Review gap:** the mandatory **GDPR/data webhooks** (`customers/redact`, `shop/redact`, `customers/data_request`) were missing — implement them; a data-deletion request is a legal obligation.
- **Version:** pin the Admin API version so the sync doesn't silently break on the next quarterly rollover (verify current version at use).
- **Seam:** hand the full review-readiness regression pass to `qa-test-automation`.

## Guardrails

- **HMAC-verify every webhook** — an unverified payload is a forgery vector.
- **Fast 200, async work** — a slow handler times out, gets retried, and can be auto-disabled.
- **The GDPR/data webhooks and Billing API are mandatory for App Store apps** — ship them from day one.
- **Bulk operations, not a hot pagination loop** — the rate limit is a cost model; budget and back off.
- **Session tokens, not cookies, for embedded apps.**
- **No script tags or `checkout.liquid`** — build on Functions / extensions / App Bridge, the upgrade-safe path.
- **Pin the API version and verify current fields/limits before coding** — Shopify versions quarterly; every version-specific fact is verify-at-use + dated. See [`../../knowledge/shopify-patterns-2026.md`](../../knowledge/shopify-patterns-2026.md).
- **The review test pass and deep auth hardening leave this skill** — route to `qa-test-automation` / `auth-identity`.
