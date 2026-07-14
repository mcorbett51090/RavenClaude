---
name: provider-track-selection
description: "Choose the commerce provider (Stripe / Square / Shopify) and the tier (static hosted-checkout vs framework embedded-SDK) for a site, then point at the right template set. Use at the START of any commerce integration, before scaffolding. Routes on how the merchant's inventory truth already lives and the site's runtime."
---

# Provider & Tier Selection

The first decision in any `web-commerce` integration. Pick **one** provider per site and **one** tier, record the choice, then scaffold. Read [`../../knowledge/provider-tracks-2026.md`](../../knowledge/provider-tracks-2026.md) for the full capability matrix.

## Step 1 — pick the provider (by where inventory truth lives)

| The merchant's situation | Provider | Why |
|---|---|---|
| Storefront with an **in-store POS**; online inventory must mirror it | **Square** | Native single catalog/inventory ledger — POS stays the source of truth; clean reconciliation |
| **Payments-first**; catalog owned in the site/DB; no POS | **Stripe** | Payments-only, app owns the catalog — least assumption |
| Wants a **hosted store + checkout** and is fine with Shopify owning it | **Shopify** | Owns catalog + checkout; you integrate, you don't rebuild |

Tie-breakers: an existing in-store POS almost always decides it (match the POS ecosystem so in-store and online unify). If the merchant already runs Square in-store → Square. Already on Shopify → Shopify.

## Step 2 — pick the tier (by the site's runtime)

| Site runtime | Tier | What gets scaffolded |
|---|---|---|
| Static HTML (no SSR/framework) | **static** | Hosted/redirect checkout + **a thin serverless function** (Cloudflare Worker / Vercel/Netlify Function) + KV for the webhook receiver and idempotency store |
| Next.js / Astro / a JS framework | **framework** | Embedded SDK checkout + server routes + webhooks |

> A "static" site still needs the serverless function — a browser cannot verify a webhook or hold idempotency state safely. Never fake webhook verification client-side (see [`webhook-hardening`](../webhook-hardening/SKILL.md)).

## Step 3 — record the choice

Write a `commerce.manifest.json` into the target repo: `{ provider, tier, posReconciliation, generatedAt, templateVersion }`. A later invocation reads it instead of re-interviewing.

## Step 4 — scaffold

Copy `templates/shared/` + `templates/<provider>/<tier>/` into the site, then run the [`commerce-gold-standard-rubric`](../commerce-gold-standard-rubric/SKILL.md) checks. Every payment/PII diff is then reviewed by `ravenclaude-core/security-reviewer` (mandatory).

## Do NOT

- Try to make one site support all three providers behind a unified adapter (the leaky-adapter trap — see the CLAUDE.md doctrine).
- Scaffold a Shopify self-hosted checkout or JS Buy SDK path — Shopify is hosted-only (see [`../../knowledge/deprecated-paths-do-not-scaffold.md`](../../knowledge/deprecated-paths-do-not-scaffold.md)).
