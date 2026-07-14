# web-commerce

**Scaffold a production-ready payment/commerce backend — Stripe, Square, or Shopify — into any website.**

`web-commerce` is a RavenClaude marketplace plugin that wires a chosen payment provider into a static or JS-framework site at full commerce depth: catalog, cart, checkout, verified webhooks, idempotency, POS/inventory reconciliation, and order handling. It **generates first-party code you own** — no dormant or deprecated dependencies — with PCI card-isolation, webhook signature verification, idempotency, and env-only secrets built in by construction.

It is the **backend-integration lane**. Your site and its checkout UX are [`web-design`](../web-design)'s job; the business decision of what/whether to sell is [`ecommerce-dtc`](../ecommerce-dtc)'s. `web-commerce` implements the payment plumbing that connects them, and routes every payment/PII security verdict to `ravenclaude-core/security-reviewer`.

## Why three tracks, not one adapter

Stripe, Square, and Shopify sit at different layers — Stripe is payments-only, Square couples payments to a POS, and Shopify owns both catalog and checkout (hosted-only). A single "commerce" interface over all three leaks badly (Vercel learned this the expensive way — its unified `@vercel/commerce` adapter was deleted in v2). So `web-commerce` gives each provider a **first-class track**, unified only by a *thin* shared payment-lifecycle contract + a normalized webhook handler with advertised capabilities.

## Provider fit — quick guide

| Your situation | Recommended provider |
|---|---|
| Storefront with an **in-store POS** you want online inventory to mirror | **Square** (native single ledger — POS stays the source of truth) |
| **Payments-first**, you own the catalog in your own site/DB | **Stripe** |
| You want a **hosted store + checkout** and are fine with Shopify owning it | **Shopify** |

## Two tiers per provider

- **Static site** → hosted/redirect checkout (no card handling on your origin). Note: a "static" site still gets a **thin serverless function + KV** for the webhook receiver and idempotency — a truly server-less site cannot verify webhooks safely.
- **Framework site** (Next.js / Astro) → embedded SDK checkout.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude   # or a local path
/plugin install web-commerce@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Status

Early — see [`CLAUDE.md`](CLAUDE.md) §6 for the roadmap. v0.1.0 targets the shared contract + Stripe + Square tracks; Shopify and the `/scaffold-commerce` selector follow. Each provider track ships only after it passes the executable seven-dimension gold-standard rubric (including a live provider-sandbox test).

## What's inside

Read these before relying on the plugin:

- [`CLAUDE.md`](CLAUDE.md) — the team doctrine, the seams, and the gold-standard rubric.
- [`knowledge/provider-tracks-2026.md`](knowledge/provider-tracks-2026.md) — the provider capability matrix and the 10 exemplars this replicates.
- [`knowledge/deprecated-paths-do-not-scaffold.md`](knowledge/deprecated-paths-do-not-scaffold.md) — the dead paths the templates will never emit.
