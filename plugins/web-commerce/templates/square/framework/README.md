# Square -- framework tier (Web Payments SDK + POS reconciliation)

Scaffold this into a JS-framework site (Next.js / Astro / similar): the
buyer tokenizes their card client-side via Square's **Web Payments SDK**,
your server completes the charge with `CreatePayment`, and a long-lived
webhook route keeps a local inventory mirror converged with **Square's POS**
as the single source of truth.

## Files

| File | Purpose |
|---|---|
| `provider.ts` | Implements the shared `PaymentProvider` contract (`../../shared/payment-provider.ts`) for this tier. |
| `checkout.ts` | Server-side `CreatePayment` from the client's single-use card token. |
| `webhook.ts` | Verifies the Square HMAC-SHA256 signature (constant-time, before parsing), de-dupes by `event_id`, normalizes to `CommerceEvent`, and extracts inventory counts for reconciliation. |
| `pos-reconciliation.ts` | The POS-as-source-of-truth reconciliation loop -- see below. |
| `square-client.ts` | First-party `fetch` wrapper for the Square REST API (no vendored SDK). |
| `.env.example` | Placeholder env vars -- copy to `.env` and fill in with real sandbox/production values. |
| `tests/` | Signature-tamper, replay-dedup, POS double-decrement / out-of-order convergence, and secret-scan tests (`node --test`). |

## PCI: card data never touches this server

The **Web Payments SDK** runs entirely in the browser, in a Square-hosted
iframe. It hands your client code a **single-use token** (`sourceId`), never
the card number. Only that opaque token reaches `checkout.ts`'s
`createSquarePayment()` (rubric #1). A minimal client-side sketch (adapt the
DOM ids and error handling to your framework/UI):

```html
<form id="square-payment-form" aria-label="Payment details">
  <div id="card-container"></div>
  <button id="pay-button" type="submit">Pay</button>
  <div id="payment-status" role="status" aria-live="polite"></div>
</form>
<script src="https://sandbox.web.squarecdn.com/v1/square.js"></script>
```

```ts
// checkout.client.ts -- runs in the browser only
declare const Square: {
  payments(applicationId: string, locationId: string): Promise<{
    card(): Promise<{ attach(selector: string): Promise<void>; tokenize(): Promise<{ status: string; token?: string; errors?: unknown }> }>;
  }>;
};

async function initSquarePayment(applicationId: string, locationId: string, orderId: string) {
  const payments = await Square.payments(applicationId, locationId);
  const card = await payments.card();
  await card.attach("#card-container");

  document.getElementById("square-payment-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.getElementById("payment-status")!;
    const result = await card.tokenize();
    if (result.status !== "OK" || !result.token) {
      // User-facing decline/error message (rubric #5) -- never a raw stack trace.
      status.textContent = "We couldn't process that card. Please check the details and try again.";
      return;
    }

    const response = await fetch("/api/checkout/square", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ sourceId: result.token, orderId }),
    });

    status.textContent = response.ok
      ? "Payment received -- thank you!"
      : "We couldn't complete this payment. Please try again or use a different card.";
  });
}
```

Your server route (Next.js Route Handler / Astro API route / similar) reads
`{ sourceId, orderId }` from the request body, generates an idempotency key
per checkout attempt (e.g. a UUID stored against the cart/session, reused on
retry so a network blip can't double-charge), and calls
`createSquarePayment()` from `checkout.ts`.

## POS / inventory reconciliation

`pos-reconciliation.ts`'s `PosReconciler` keeps a **read-only local mirror**
of Square's inventory ledger -- your in-store POS stays the one and only
source of truth (`capabilities.catalogSourceOfTruth === 'provider'`). It:

- de-dupes every `catalog.version.updated` / `inventory.count.updated`
  webhook by `event_id` before applying anything (a replayed delivery is a
  no-op -- Square does not guarantee exactly-once delivery);
- ignores any inventory count whose `calculated_at` is OLDER than the
  last-applied one for that catalog object/location/state (Square also
  does not guarantee delivery order -- an out-of-order delivery must not
  regress the mirror);
- on `catalog.version.updated` (whose payload carries no object data), it
  PULLS just the changed catalog objects via Square's Catalog API
  (`SearchCatalogObjects` with a version cursor) rather than trying to
  infer them from the webhook body;
- **never writes back to Square.** Square's own docs warn that
  bidirectional sync between an external system and its catalog is risky
  (concurrency, merges, duplicates, deletes) -- see
  `knowledge/provider-tracks-2026.md` §4 in this plugin.

Wire your webhook route's inventory callback to `PosReconciler.
applyInventoryEvent()`, and your catalog-version callback to
`PosReconciler.applyCatalogVersionEvent()` (which takes your own
`fetchChangedObjects` Catalog API call as a parameter, keeping this module
free of a live network dependency and unit-testable).

## Setup

1. **Create a Square sandbox application.** Square Developer Dashboard →
   your app → **Sandbox** tab. Note the **Sandbox Access Token**,
   **Application ID**, and a **Sandbox Location ID** (Locations tab). Put
   them in `.env` (copied from `.env.example`); keep `SQUARE_ENVIRONMENT=sandbox`.
2. **Create a webhook subscription** (Developer Dashboard → your app →
   **Webhooks**). Point the notification URL at your deployed webhook
   route, subscribe to `payment.created`, `payment.updated`,
   `refund.updated`, `inventory.count.updated`, and `catalog.version.
   updated`, and copy the **Signature Key** into
   `SQUARE_WEBHOOK_SIGNATURE_KEY`. The registered notification URL must
   match `SQUARE_WEBHOOK_NOTIFICATION_URL` byte-for-byte -- it is part of
   the signed payload.
3. **Local webhook testing.** Square does not ship an equivalent of
   `stripe listen`; the supported local-testing path is: run your dev
   server, tunnel it with `ngrok http <port>`, temporarily point the
   webhook subscription's notification URL at the ngrok URL, and use the
   Developer Dashboard's **Webhooks → Subscription → Test** button to fire
   a sample event.
   `[unverified -- training knowledge; re-check
   developer.squareup.com/docs/webhooks/overview for any newer CLI tooling
   before relying on this as the only path.]`
4. **Sandbox test cards.** Use Square's published sandbox card numbers
   (Developer Dashboard → Sandbox → Test Values) with the Web Payments SDK
   to exercise the approved, declined, and CVV/AVS-failure paths.
5. **Run the tests:** `npm install && npm test` (see `package.json` in this
   directory).

## Decline path

A `card.tokenize()` failure or a `CreatePayment` decline both surface a
plain, user-facing message ("We couldn't process that card...") -- never a
raw Square error code or stack trace to the buyer (rubric #5). Log the
detailed error server-side only.
