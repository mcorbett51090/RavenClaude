# Shopify — framework tier (Next.js / Astro)

Storefront **Cart API** (GraphQL) → `cart.checkoutUrl` redirect, called from
a server route/component so `SHOPIFY_STOREFRONT_TOKEN` and
`SHOPIFY_WEBHOOK_SECRET` stay out of the client bundle. Checkout completion
happens entirely on Shopify's hosted page — **we deliberately do not
self-host checkout**; see the "why" below.

## Why hosted-only, and why not the JS Buy SDK / Hydrogen's old checkout

Shopify shut down two self-hosted paths:

- The **JS Buy SDK checkout flow** — hard cutover **2025-07-01**.
- The custom **Checkout API** (self-hosted checkout / `checkoutCreate`) —
  **shut down 2025-04-01**.

The only path that still works, and the only one these templates emit, is:
**Storefront Cart API → read `cart.checkoutUrl` → redirect the buyer there.**
Hydrogen (Shopify's official React framework) uses the identical pattern
under the hood. Full detail:
[`../../../knowledge/deprecated-paths-do-not-scaffold.md`](../../../knowledge/deprecated-paths-do-not-scaffold.md).

## Files

| File | Purpose |
|---|---|
| `cart.ts` | Storefront Cart GraphQL client — `createCart` / `cartLinesAdd` / `getCart` / `getOrCreateCart`. Framework-agnostic; no `next/headers` or Astro-specific import. |
| `webhook.ts` | Webhook handler factory — verifies `X-Shopify-Hmac-Sha256`, de-dupes by `X-Shopify-Webhook-Id`, normalizes to the shared `CommerceEvent` shape. Returns a standard `Response`. |
| `provider.ts` | `ShopifyProvider`, implementing the shared `PaymentProvider` contract. |
| `.env.example` | Placeholders for the three env vars below. |
| `tests/` | Tampered-signature rejection, replay no-op, cart-client contract tests, secret-hygiene scan, deprecation guard. |

## Setup

1. **Create a Shopify dev/partner store** (Shopify Partners → Stores → Development store) — free, safe for end-to-end checkout testing.
2. **Storefront API token**: Shopify admin → Settings → Apps and sales channels → Develop apps → create an app → enable Storefront API → install → copy the token into `SHOPIFY_STOREFRONT_TOKEN`.
3. **Webhook signing secret**: same admin app, or Settings → Notifications → Webhooks → create a subscription pointed at your deployed webhook route → copy the secret into `SHOPIFY_WEBHOOK_SECRET`.
4. Copy `.env.example` to `.env.local` (Next.js) or `.env` (Astro).

### Next.js (App Router)

```ts
// app/api/webhooks/shopify/route.ts
import { createShopifyWebhookHandler, ShopifyWebhookVerifier } from "@/shopify/webhook";
import { myKvIdempotencyStore } from "@/lib/kv"; // implements IdempotencyStore

export const POST = createShopifyWebhookHandler({
  verifier: new ShopifyWebhookVerifier(process.env.SHOPIFY_WEBHOOK_SECRET!),
  store: myKvIdempotencyStore,
});
```

```ts
// app/cart/checkout/route.ts — server-side cart-id persistence via an
// httpOnly cookie, so the cart survives across requests without exposing
// the cart id to client-side scripts.
import { cookies } from "next/headers";
import { getOrCreateCart, cartLinesAdd } from "@/shopify/cart";

export async function POST(request: Request) {
  const { merchandiseId, quantity } = await request.json();
  const cookieStore = await cookies();
  const cart = await getOrCreateCart(config, cookieStore.get("shopify_cart_id")?.value);
  const updated = await cartLinesAdd(config, cart.id, [{ merchandiseId, quantity }]);
  cookieStore.set("shopify_cart_id", updated.id, { httpOnly: true, secure: true, sameSite: "lax" });
  return Response.json({ checkoutUrl: updated.checkoutUrl });
}
```

### Astro

```ts
// src/pages/api/webhooks/shopify.ts
import type { APIRoute } from "astro";
import { createShopifyWebhookHandler, ShopifyWebhookVerifier } from "../../../shopify/webhook";
import { myKvIdempotencyStore } from "../../../lib/kv";

const handler = createShopifyWebhookHandler({
  verifier: new ShopifyWebhookVerifier(import.meta.env.SHOPIFY_WEBHOOK_SECRET),
  store: myKvIdempotencyStore,
});

export const POST: APIRoute = ({ request }) => handler(request);
```

```ts
// src/pages/api/cart/checkout.ts — persist the cart id via an httpOnly cookie
import type { APIRoute } from "astro";
import { getOrCreateCart, cartLinesAdd } from "../../../shopify/cart";

export const POST: APIRoute = async ({ request, cookies }) => {
  const { merchandiseId, quantity } = await request.json();
  const cart = await getOrCreateCart(config, cookies.get("shopify_cart_id")?.value);
  const updated = await cartLinesAdd(config, cart.id, [{ merchandiseId, quantity }]);
  cookies.set("shopify_cart_id", updated.id, { httpOnly: true, secure: true, sameSite: "lax" });
  return new Response(JSON.stringify({ checkoutUrl: updated.checkoutUrl }), { status: 200 });
};
```

## Hydrogen note (optional)

If you're building on **Hydrogen** (Shopify's official React framework,
built on Remix/Oxygen), it ships its own Storefront API client and cart
hooks that follow this same hosted-checkout pattern — you likely don't need
this template at all; use Hydrogen's built-in `<CartForm>` /
`storefront.query` instead and skip straight to wiring `webhook.ts`'s
verify-and-normalize logic into an Oxygen route. This template targets
teams on a plain Next.js/Astro stack who want a first-party client without
adopting the full Hydrogen framework.

## KV-backed IdempotencyStore

`webhook.ts`'s handler needs a real `IdempotencyStore` implementation in
production (the in-memory reference in
[`../../shared/idempotency-store.ts`](../../shared/idempotency-store.ts) is
for tests only — see that file's doc comment). A minimal Vercel KV-backed
example:

```ts
import { kv } from "@vercel/kv";
import type { IdempotencyStore } from "@/shopify/../shared/idempotency-store";

export const myKvIdempotencyStore: IdempotencyStore = {
  async seen(eventId) {
    return (await kv.get(`shopify:event:${eventId}`)) !== null;
  },
  async remember(eventId, ttlSeconds = 60 * 60 * 24 * 7) {
    await kv.set(`shopify:event:${eventId}`, 1, { ex: ttlSeconds });
  },
};
```
