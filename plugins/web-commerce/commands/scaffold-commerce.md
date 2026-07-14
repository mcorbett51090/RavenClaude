---
name: scaffold-commerce
description: "Guided commerce integration: pick a provider (Stripe/Square/Shopify) and tier (static/framework), scaffold the templates into the site, wire webhooks + idempotency + env, then run the gold-standard rubric checks. The one-command entry point for adding payments to a site."
---

# /scaffold-commerce

Add a payment/commerce backend to the current site, end to end.

## What it does

1. **Select** — runs [`commerce-provider-selector`](../agents/commerce-provider-selector.md): picks the provider by where inventory truth lives and the tier by the site's runtime, and writes `commerce.manifest.json`. If a manifest already exists, it reads it instead of re-asking.
2. **Scaffold** — runs [`commerce-integration-engineer`](../agents/commerce-integration-engineer.md): copies `templates/shared/` + `templates/<provider>/<tier>/` into the site, wires checkout + webhooks + idempotency, and writes `.env.example` placeholders (never a live key).
3. **Reconcile (Square only)** — if the manifest sets `posReconciliation`, runs [`pos-reconciliation-engineer`](../agents/pos-reconciliation-engineer.md) to build the inventory loop.
4. **Verify** — runs the [`commerce-gold-standard-rubric`](../skills/commerce-gold-standard-rubric/SKILL.md) static checks, then [`commerce-webhook-security-reviewer`](../agents/commerce-webhook-security-reviewer.md) audits the result. The residual security verdict routes to `ravenclaude-core/security-reviewer`.

## What it does NOT do

- Build or restyle the site / checkout UX — that is `web-design`'s `gold-standard-website-pipeline`.
- Run the live provider-sandbox test — that needs your Stripe/Square/Shopify account; the command wires the test harness and tells you how to run it.

## Usage

```
/scaffold-commerce
```

Follow the prompts (or let it read an existing `commerce.manifest.json`). Fill the real keys into `.env` (never commit them) after scaffolding.
