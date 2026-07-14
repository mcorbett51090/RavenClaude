# Deprecated Paths — DO NOT Scaffold

> The templates must **never** emit any path below. Each carries its cutover/shutdown date so a future maintainer can tell "still dead" from "revived." Sources retrieved **2026-07-13**. This file is the reference the (future) `commerce-template-maintainer` drift agent diffs provider changelogs against.

## Why this file exists

Provider APIs drift out from under templates — and it has already burned this ecosystem. Shopify shut down two payment paths in 2025; a project that scaffolded them would generate code that **cannot complete a purchase**. "Scaffold and forget" is not done; drift detection is part of the plugin (CLAUDE.md §6, v0.3.0).

## The dead paths

| Path | Status | Date | Scaffold instead | Source |
|---|---|---|---|---|
| **Shopify JS Buy SDK** (checkout flow) | Deprecated; hard cutover — after this date customers **cannot complete purchases** on it | **2025-07-01** | Storefront **Cart API** → `cart.checkoutUrl`, or the Buy Button channel embed | <https://shopify.dev/changelog/js-buy-sdk-deprecation-notice> |
| **Shopify custom Checkout API** (self-hosted checkout / Storefront `checkoutCreate`) | Shut down | **2025-04-01** | Hosted checkout only — Storefront Cart API returns `checkoutUrl`; the buyer completes on Shopify's page | <https://shopify.dev/docs/api/storefront/latest>, community: <https://community.shopify.com/t/storefront-api-checkout-payment-gateways/8809> |
| **Commerce.js / Chec** | Organization **archived** (dead — no maintenance) | **2024-10-09** | Do not use as an exemplar or a runtime dependency | <https://github.com/chec> |
| **`use-shopping-cart`** | Maintenance conflict — docs advertise React 19 support, but the repo's last release is **v2.4.2 (Feb 2021)** | (dormant since 2021) | Generate first-party Stripe cart code; do not add as a dependency | <https://github.com/dayhaysoos/use-shopping-cart> vs <https://useshoppingcart.com/> |

## Hard rules for template authors

1. **Shopify = hosted checkout, full stop.** Both the static and framework Shopify tiers end at `cart.checkoutUrl` → Shopify's hosted page. Do not generate a self-hosted checkout, a `checkoutCreate` call, or any JS Buy SDK checkout. The Shopify track's advertised capabilities must declare `checkout: 'hosted'` and `authorizeCapture: 'n/a'`.
2. **No dependency on an unmaintained cart/checkout library.** Generate first-party code the consumer owns (CLAUDE.md §2 #6). If a convenience lib is dormant (last release > ~18 months, or an archived org), it is out.
3. **Every deprecation claim in a generated comment or doc carries its date** (as above), so the freshness of the guidance is auditable.

## Freshness / re-verification

- Re-check each row against the provider's **changelog** (not blog/marketing) before a release. Shopify: <https://shopify.dev/changelog>. Stripe: <https://docs.stripe.com/changelog>. Square: <https://developer.squareup.com/changelog>.
- The `commerce-template-maintainer` agent (v0.3.0) automates this diff; until it ships, this is a manual pre-release step in the plugin's Definition of Done.
