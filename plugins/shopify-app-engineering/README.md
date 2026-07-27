# shopify-app-engineering

> The **Shopify app & theme engineering layer** for Claude Code — the team that answers _"how do we build this on Shopify correctly, within the platform's rules, and so it survives review and scale — without building on a deprecated path?"_ Two agents: the **shopify-app-architect** (public vs custom app, embedded vs headless, Shopify Functions vs legacy customization, theme vs Storefront API, the metafields data model, and the billing/OAuth/rate-limit/App-Store-review envelope) and the **shopify-app-engineer** (Admin GraphQL API, OAuth/session-token auth, HMAC-verified webhooks incl. the mandatory GDPR ones, App Bridge/Polaris, Shopify Functions & checkout UI extensions, Liquid/OS 2.0 themes & metafields, Hydrogen/Storefront API, Billing API, and rate-limit-aware data operations).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Should this be a public app, a custom app, or a theme change?" | An app-type decision (custom for one merchant, public/App-Store for many, theme/extension when no backend is needed) with the review constraint named up front |
| "Embedded or headless?" | An App-Bridge/Polaris embedded vs Hydrogen/Storefront-API headless call on the flexibility/perf/maintenance trade-off — with the honest "a theme is enough" default when headless isn't earned |
| "How do we customize discounts / checkout?" | A Shopify Functions + checkout-UI-extension design, and the reason script tags / `checkout.liquid` are the wrong (deprecating) choice on modern plans |
| "Where do we store this custom product data?" | A typed metafields/metaobjects model with storefront exposure decided — not a shadow database |
| "How do we charge and stay inside Shopify's limits and review rules?" | A Billing-API plan, an OAuth + session-token auth design, a GraphQL cost-based rate-limit strategy (bulk operations for large reads), the mandatory GDPR/data webhooks, and the App-Store-review checklist |
| "Wire up app install and a webhook for new orders." | An OAuth + session-token flow and an HMAC-verified, idempotent, fast-200-async webhook handler — with the GDPR/data webhooks stubbed and the API version pinned |
| "We're getting throttled pulling all products." | The root cause (a hot pagination loop blowing the GraphQL cost budget) and the fix (bulk operations + cost-aware back-off) — not a guessed retry hack |

**Two rules it never breaks:** _build with the platform's grain_ (Functions over script tags, App Bridge over custom chrome, Billing API over off-platform — the bypass fails review and breaks on the next version), and _a theme is the default_ (headless Hydrogen is a real cost — earn it with a requirement).

## What's inside

- **2 agents** — `shopify-app-architect` (app type, integration surface, Functions/extensibility, data model, storefront, billing/review envelope) and `shopify-app-engineer` (GraphQL/webhooks/OAuth/App-Bridge/Functions/extensions/Liquid/Hydrogen/Billing, built the current-generation way, with auth verified and rate limits handled).
- **2 skills** — `design-shopify-build`, `ship-app-store-ready`.
- **2 knowledge files** — a Mermaid decision-tree bank (app type, customization surface, theme-vs-headless, data model, commercial/safety envelope) and a dated 2026 patterns reference (auth, webhook reliability/security, GraphQL rate limits & bulk ops, Functions & checkout extensibility, App Bridge/Polaris, OS 2.0, Hydrogen, Billing, review categories, tooling map).
- **1 template** — a Shopify build spec (audience/App-Store exposure → surface → customization path → data model → storefront → commercial/safety envelope → review checklist → seams).

## Where it sits among the commerce & frontend plugins

```
ecommerce-dtc               →  merchandising / retention / lifecycle OPERATIONS   (the strategy the app serves)
web-commerce                →  a generic, non-Shopify PAYMENT scaffold
fintech-payments-engineering →  off-Shopify PAYMENT RAILS / PSP work
frontend-engineering        →  generic React component / state craft
web-design                  →  visual / interaction / IA DESIGN
shopify-app-engineering (HERE) →  DESIGN & BUILD on the Shopify platform
                                  ("app type + GraphQL + Functions + themes + review-ready, with the platform's grain")
```

This plugin **builds on the Shopify platform** and **feeds** those teams rather than replacing them: it hands the merchandising strategy to `ecommerce-dtc`, the off-Shopify payment rails to `fintech-payments-engineering`, the generic React work to `frontend-engineering`, and the visual design to `web-design` — while owning the app-type decision, GraphQL/webhook/Functions craft, theme vs headless call, and App-Store-review discipline that make a Shopify build ship and survive.

## Domain stance

Platform-idiomatic and review-first: build with Shopify's grain (Functions and extensions over script tags, App Bridge over custom chrome, the Billing API over off-platform charging, the Admin GraphQL API over legacy REST), default to a theme over headless, verify every webhook (HMAC) and secure every embedded session (session tokens), treat the GraphQL cost model and the mandatory GDPR webhooks as design inputs, and pin the API version. Fluent across apps (OAuth, webhooks, App Bridge/Polaris, Functions, checkout extensibility, Billing), themes (Liquid, Online Store 2.0, metafields), and headless (Hydrogen, Storefront API). Shopify versions its API quarterly and revises review rules — every API field, rate-limit number, and review requirement carries a retrieval date and is re-verified before a commitment.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install shopify-app-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
