# Shopify App & Theme Engineering — Patterns & Practices (2026)

> Last reviewed: 2026-07-20. Confidence: **HIGH** for durable platform practice; **VERIFY-AT-USE** for every version/field/limit/review-rule specific. This file is inline priors; the decision trees in [`shopify-decision-tree.md`](shopify-decision-tree.md) are the callable source of truth. Shopify versions its Admin API quarterly and revises review rules — re-verify volatile facts against current Shopify.dev docs before a stakeholder commitment.

## Apps — auth & install

- **OAuth** for install; **session tokens** (JWT from App Bridge) for authenticating embedded-app requests — not cookies (embedded iframes and third-party-cookie restrictions make cookies unreliable).
- **Pin the Admin API version** in every call and track the deprecation window. An unpinned request silently shifts behavior on quarterly rollover.
- **Scopes: request the minimum.** Over-broad access scopes are a review flag and a merchant-trust cost.

## Webhooks — the reliability + security discipline

- **HMAC-verify every webhook.** An unverified payload is a forgery vector; validate the signature before trusting a byte.
- **Idempotent processing.** Shopify delivers at-least-once; the same event can arrive twice — dedupe on the event/resource id.
- **Fast 200, async work.** Return success immediately and do the real processing off the request path. A slow handler times out, gets retried, and can be auto-disabled.
- **Mandatory GDPR/data webhooks** — `customers/data_request`, `customers/redact`, `shop/redact`. Required for App Store apps; a data-deletion request is a legal obligation, not a feature.
- **Re-register on reinstall** and handle the `app/uninstalled` cleanup.

## Admin GraphQL API — rate limits & bulk

- **Cost-based throttling.** Each query has a calculated cost; the response carries the current cost/available/restore-rate. Budget queries and **back off honoring those fields** — the throttle is predictable, not random.
- **Bulk operations** for large reads/writes (export/import scale) instead of a tight pagination loop that hammers the API and throttles you. This is the single most common self-inflicted rate-limit bug.
- **GraphQL over REST** for new work — REST is legacy/deprecating (verify timeline at use). Query only the fields you need.

## Shopify Functions & checkout extensibility

- **Functions** (Wasm-compiled logic) own discount, shipping, payment-method, and cart/checkout **validation** logic — replacing the old script-tag/Scripts approach. They read config from metafields; respect the input-query and output-schema contract and the runtime limits.
- **Checkout UI extensions** own checkout **UI** changes — `checkout.liquid` is restricted on modern plans (verify-at-use). Extensions are the supported, upgrade-safe path.
- **Admin/theme app extensions** inject UI into admin pages and OS 2.0 themes (app blocks) without owning the whole surface.

## Embedded admin UI — App Bridge + Polaris

- **App Bridge** for the embedded frame (navigation, session tokens, resource pickers, toasts).
- **Polaris** for components so the app looks native inside admin — a strong signal for review and merchant trust.
- Keep the UI responsive and accessible; a janky embedded page is a review and adoption risk.

## Themes — Online Store 2.0

- **JSON templates + sections + blocks + app blocks** — merchant-editable in the theme editor; keep settings schemas clean so merchants stay in control.
- **Liquid** for server-rendered storefront logic; **metafields/metaobjects** for custom data bound into sections.
- Prefer sections/blocks over hard-coded templates so merchants can rearrange without a developer.

## Headless — Hydrogen + Storefront API

- **Hydrogen** (React framework) on **Oxygen** hosting, consuming the **Storefront API** (and Customer Account API). Earn it with a real requirement (custom framework, perf budget, omnichannel) — it costs build + hosting + maintenance and gives up the theme editor.
- Cache aggressively; the Storefront API has its own limits.

## Billing

- **Billing API** — recurring, usage-based, or one-time charges, all on-platform. App Store apps **must** charge through it; off-platform billing is a review rejection.

## App Store review — the categories (verify exact items at use)

1. **Functionality & OAuth** — installs cleanly, requests minimal scopes, no broken flows.
2. **Mandatory GDPR/data webhooks** present and working.
3. **Performance** — embedded UI loads fast; no admin slowdown; theme apps don't tank Lighthouse.
4. **Security** — HMAC-verified webhooks, session-token auth, no secrets leaked.
5. **Billing** — through the Billing API, clearly disclosed.
6. **Listing quality** — accurate description, screenshots, support contact.

Exact checklist items change — **verify-at-use** against the current App Store requirements.

## Tooling map (2026 — verify-at-use)

- **Shopify CLI** — scaffolds apps/extensions/themes, dev tunneling, deploy.
- **Remix** — the common app framework in Shopify's template (verify current default).
- **`@shopify/shopify-api` / App Bridge / Polaris / Hydrogen** libraries.
- **GraphiQL app / Admin API explorer** — for query cost + field verification.
- **Dev/preview stores** — test installs and review flows before listing.

Every version/field/limit/review-rule claim above carries an implicit `[verify-at-use, retrieved 2026-07-20]` — re-check current Shopify.dev docs.
