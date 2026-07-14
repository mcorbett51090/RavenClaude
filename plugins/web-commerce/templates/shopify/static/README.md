# Shopify — static tier

Storefront **Cart API** (GraphQL) → `cart.checkoutUrl` redirect. No card field
ever touches your origin; **checkout is entirely Shopify-hosted, and we
deliberately do not self-host it** — see the "why" below.

## Why hosted-only, and why not the JS Buy SDK

Shopify shut down two self-hosted paths:

- The **JS Buy SDK checkout flow** — hard cutover **2025-07-01**; after that
  date it cannot complete a purchase.
- The custom **Checkout API** (self-hosted checkout / `checkoutCreate`) —
  **shut down 2025-04-01**.

The only path that still works, and the only one these templates emit, is:
**Storefront Cart API → read `cart.checkoutUrl` → redirect the buyer there.**
Full detail: [`../../../knowledge/deprecated-paths-do-not-scaffold.md`](../../../knowledge/deprecated-paths-do-not-scaffold.md).

## Files

| File | Purpose |
|---|---|
| `cart.ts` | Storefront Cart GraphQL client — `createCart` / `cartLinesAdd` / `getCart` / `redirectToCheckout`. Runs in the browser. |
| `webhook.ts` | Thin serverless webhook receiver — verifies `X-Shopify-Hmac-Sha256`, de-dupes by `X-Shopify-Webhook-Id`, normalizes to the shared `CommerceEvent` shape. |
| `provider.ts` | `ShopifyProvider`, implementing the shared `PaymentProvider` contract. |
| `.env.example` | Placeholders for the three env vars below — copy to `.env` and fill in real values, never commit the filled-in file. |
| `tests/` | Tampered-signature rejection, replay no-op, secret-hygiene scan, and a deprecation guard. |

## The static-tier caveat (read this)

A literally static site has nowhere to verify a webhook signature or hold
idempotency state — there is no server. So even the "static" tier ships a
**thin serverless function** (`webhook.ts`, exported as a standard
`(request: Request) => Promise<Response>`) that you deploy to a Cloudflare
Worker / Vercel Edge Function / Netlify Edge Function, **backed by an
external KV** (Upstash / Vercel KV) implementing
[`../../shared/idempotency-store.ts`](../../shared/idempotency-store.ts)'s
`IdempotencyStore` interface. Do NOT verify webhooks or store idempotency
state in the browser — a client can't hold a secret and can't be trusted to
report "I already ran this side effect."

Adapter one-liners:

```ts
// Cloudflare Worker
export default { fetch: createShopifyWebhookHandler({ verifier, store }) };

// Vercel Edge Function / Next.js Route Handler
export const POST = createShopifyWebhookHandler({ verifier, store });

// Netlify Edge Function
export default createShopifyWebhookHandler({ verifier, store });
```

## Setup

1. **Create a Shopify dev/partner store** (Shopify Partners → Stores → Development store) — free, isolated from any real store, safe for testing checkout end-to-end.
2. **Storefront API access token**: Shopify admin → Settings → Apps and sales channels → Develop apps → create an app → enable Storefront API → install → copy the public Storefront access token into `SHOPIFY_STOREFRONT_TOKEN`.
3. **Webhook signing secret**: same admin app, or Settings → Notifications → Webhooks → create a webhook subscription pointed at your deployed `webhook.ts` endpoint → copy the signing secret into `SHOPIFY_WEBHOOK_SECRET`.
4. Copy `.env.example` to `.env`, fill in `SHOPIFY_STORE_DOMAIN` / `SHOPIFY_STOREFRONT_TOKEN` / `SHOPIFY_WEBHOOK_SECRET`.
5. Wire `cart.ts` to your PDP's "Buy" button:
   ```ts
   const cart = await createCart(config, [{ merchandiseId: variantGid, quantity: 1 }]);
   redirectToCheckout(cart);
   ```
6. Deploy `webhook.ts` (via one of the adapters above) and subscribe to the topics you need (`orders/paid`, `orders/create`, `refunds/create`, …) via the Shopify admin or `shopify app webhook trigger` for local testing.

## TypeScript with "no build step"

This file ships as TypeScript per the plugin's convention (typed, testable).
If your site truly has no bundler, transpile once — this is not a framework
or a dev server, just a single-file compile:

```shell
npx esbuild cart.ts --bundle --format=esm --outfile=cart.js
```

Ship the resulting `cart.js` as a plain `<script type="module" src="cart.js">`.

## Buy Button alternative

If you'd rather not write any cart code at all, Shopify's **Buy Button
channel embed** (Sales channels → Buy Button, in the Shopify admin) generates
a drop-in `<script>` snippet that also ends at Shopify's hosted checkout —
appropriate when you don't need custom cart UI.
