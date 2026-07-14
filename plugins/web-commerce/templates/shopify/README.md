# Shopify provider track

Shopify is **capability-inverted** relative to Stripe/Square: it owns both
the catalog and checkout, and checkout is **hosted-only** — there is no
server-side authorize/capture/refund step to expose, and no way to run your
own checkout on Shopify rails. See
[`../../knowledge/provider-tracks-2026.md`](../../knowledge/provider-tracks-2026.md) §1.

Pick **one** tier per site:

| Tier | When | Entry point |
|---|---|---|
| [`static/`](static/README.md) | A static site (no server framework) — still ships a thin serverless webhook receiver, since verifying a signature needs somewhere to run. | `static/cart.ts` + `static/webhook.ts` |
| [`framework/`](framework/README.md) | Next.js or Astro — server routes handle the cart + webhook natively. | `framework/cart.ts` + `framework/webhook.ts` |

Both tiers end at the same place: **`cart.checkoutUrl`**, Shopify's hosted
checkout page. Neither tier scaffolds the deprecated JS Buy SDK checkout flow
(hard cutover 2025-07-01) or the shut-down custom Checkout API (2025-04-01) —
see [`../../knowledge/deprecated-paths-do-not-scaffold.md`](../../knowledge/deprecated-paths-do-not-scaffold.md).

Both tiers implement the shared `PaymentProvider` contract
([`../shared/payment-provider.ts`](../shared/payment-provider.ts)) with:

```ts
capabilities = {
  checkout: "hosted",
  authorizeCapture: false,
  refunds: false,
  catalogSourceOfTruth: "provider",
  posReconciliation: false,
};
```

`authorize` / `capture` / `refund` / `cancel` are omitted (not stubbed) —
Shopify has no server-side equivalent to gate.
