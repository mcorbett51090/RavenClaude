---
name: design-shopify-build
description: "Design a Shopify build from who-uses-it and does-it-ship-to-the-App-Store backward: the app type (custom vs public vs theme/extension), the integration surface (Admin GraphQL API, webhooks, App Bridge/Polaris embedded UI, extensions), the current-generation customization path (Shopify Functions + checkout UI extensions, never script tags / checkout.liquid), the metafields/metaobjects data model, the storefront choice (Online Store 2.0 theme — the default — vs Hydrogen/Storefront API headless), and the commercial/safety envelope (Billing API, OAuth + session tokens, GraphQL cost-based rate limits + bulk operations, mandatory GDPR/data webhooks, App Store review). Reach for this when the ask is 'how should we build this on Shopify?', 'public app or theme?', 'embedded or headless?', or 'Functions or script tags?'. Used by `shopify-app-architect` (primary)."
---

# Skill: design-shopify-build

> **Invoked by:** `shopify-app-architect` (primary). Consulted by `shopify-app-engineer` for the design contract the code must honor.
>
> **When to invoke:** "how should we build this on Shopify?"; "public app, custom app, or theme?"; "embedded or headless?"; "Functions or script tags?"; "where do we store this custom data?"; "how do we charge and stay inside the limits?"
>
> **Output:** an app-type + integration-surface decision + Functions/extensibility call + metafields data model + storefront (theme vs Hydrogen) choice + billing/OAuth/rate-limit/review envelope, captured in the app spec template.

## Procedure

1. **Start from who uses it and App Store exposure.** One merchant/internal → custom app; many/listed → public app (review applies); no backend → theme change or extension. Traverse [`../../knowledge/shopify-decision-tree.md`](../../knowledge/shopify-decision-tree.md) Tree 1.
2. **Choose the integration surface (Tree 2).** Admin **GraphQL API** (not legacy REST), **webhooks** for events, **App Bridge + Polaris** for embedded admin UI, **extensions** for injected UI. Name embedded-vs-headless where it applies.
3. **Pick the current-generation customization path.** Discount/checkout/shipping/validation → **Shopify Functions**; checkout UI → **checkout UI extensions**. Never design against script tags or `checkout.liquid` (restricted/deprecating — verify-at-use); it's rework you're choosing.
4. **Model custom data with metafields/metaobjects (Tree 4)**, typed and namespaced, with storefront exposure decided. Don't invent a shadow datastore for what metafields hold.
5. **Choose the storefront on the trade-off (Tree 3) — a theme is the default.** OS 2.0 (Liquid, sections, app blocks, merchant-editable) unless a real framework/perf/omnichannel need earns **Hydrogen + Storefront API** (which costs build + hosting + maintenance + the theme editor). Say when the theme wins.
6. **Design the commercial + safety envelope (Tree 5).** **Billing API** (never off-platform), **OAuth + session tokens**, **GraphQL cost-based rate-limit** strategy (budget + back-off + **bulk operations** for large ops), **mandatory GDPR/data webhooks**, and the **App Store review** requirements. Mark every rule/limit/version **verify-at-use + dated**.
7. **State the seams and flip conditions.** Merchandising/retention strategy → `ecommerce-dtc`; off-Shopify payment rails → `fintech-payments-engineering`; generic React inside Hydrogen → `frontend-engineering`; visual/IA → `web-design`. Name the 1-2 facts that would flip the design.

## Worked example

> User: "We want to sell a volume-discount + custom-checkout-note app to lots of merchants on the App Store."

- **App type (Tree 1):** many merchants, listed → **public app**, App Store review is a hard design constraint.
- **Surface (Tree 2):** Admin GraphQL API for setup, an embedded **App Bridge + Polaris** settings page, and webhooks for lifecycle.
- **Customization path:** the volume discount → a **Shopify Function** (reads its threshold config from a metafield); the checkout note field → a **checkout UI extension**. **Not** script tags, **not** `checkout.liquid`.
- **Data model (Tree 4):** discount tiers stored as a **metafield** on the shop/product; no shadow DB needed for that.
- **Storefront (Tree 3):** none needed — this is admin + checkout, no headless. A theme isn't even in scope.
- **Envelope (Tree 5):** charge via the **Billing API** (recurring); OAuth + session tokens; budget GraphQL cost and back off; implement the **GDPR/data webhooks** from day one; walk the App Store review categories. All rule/limit specifics verify-at-use.
- **Seam:** the merchant's discount _strategy_ (what tiers convert) is `ecommerce-dtc`; we build the mechanism.

## Guardrails

- **Build with the platform's grain** — Functions over script tags, App Bridge over custom chrome, Billing API over off-platform; the bypass fails review and breaks on the next version.
- **A theme is the default** — headless Hydrogen is a real cost; earn it with a requirement.
- **REST is legacy** — design new work on the Admin GraphQL API (verify deprecation timeline at use).
- **Rate limits are a design input** — GraphQL cost model + bulk operations belong in the design, not bolted on after the first throttle.
- **The GDPR/data webhooks and Billing API are mandatory for App Store apps** — not optional.
- **Every version/limit/review-rule fact carries a retrieval date + verify-at-use** — Shopify versions quarterly. See [`../../knowledge/shopify-patterns-2026.md`](../../knowledge/shopify-patterns-2026.md).
- **The design is the architect's; the code, merchandising strategy, and payment rails leave this skill** — route to `shopify-app-engineer` / `ecommerce-dtc` / `fintech-payments-engineering`.
