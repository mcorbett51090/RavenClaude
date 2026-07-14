# Square -- static tier (hosted Checkout / Payment Links)

Scaffold this into a static site: a hosted checkout redirect
(`square.link/...`) for the buyer-facing flow, plus a **thin serverless
function** for the webhook receiver. No card field, and no payment logic,
ever runs on the site's own origin.

> **Read this before you assume "static" means "no server."** A literally
> static site cannot verify a webhook signature or hold idempotency state --
> there is nowhere for that code to run. `webhook.ts` in this directory is
> meant to be deployed as a small **Cloudflare Worker / Vercel Function /
> Netlify Function**, backed by an **external KV** (`kv-idempotency-store.ts`
> wraps Upstash / Cloudflare KV / Vercel KV behind one small interface). If
> your deploy target truly has zero server-side compute available, this
> tier cannot be made secure -- move to the framework tier or add a
> minimal serverless platform.

## Files

| File | Purpose |
|---|---|
| `provider.ts` | Implements the shared `PaymentProvider` contract (`../../shared/payment-provider.ts`) for this tier. |
| `checkout.ts` | Calls Square's Payment Links API to build the `square.link/...` redirect URL. |
| `webhook.ts` | Verifies the Square HMAC-SHA256 signature (constant-time, before parsing), de-dupes by `event_id`, normalizes to `CommerceEvent`, and exposes a Fetch-API-compatible serverless entrypoint. |
| `kv-idempotency-store.ts` | KV-backed `IdempotencyStore` implementation -- bind your platform's KV client to the tiny `EdgeKv` interface. |
| `square-client.ts` | First-party `fetch` wrapper for the Square REST API (no vendored SDK). |
| `.env.example` | Placeholder env vars -- copy to `.env` and fill in with real sandbox/production values. |
| `tests/` | Signature-tamper, replay-dedup, and secret-scan tests (`node --test`). |

## Setup

1. **Create a Square sandbox application.** Square Developer Dashboard →
   your app → **Sandbox** tab. Note the **Sandbox Access Token**,
   **Application ID**, and a **Sandbox Location ID** (Locations tab). Put
   them in `.env` (copied from `.env.example`); keep `SQUARE_ENVIRONMENT=sandbox`.
2. **Create a webhook subscription** (Developer Dashboard → your app →
   **Webhooks**). Point the notification URL at your deployed serverless
   function (e.g. `https://<your-worker>.workers.dev/api/webhooks/square`),
   subscribe to `payment.created`, `payment.updated`, `refund.updated`, and
   copy the **Signature Key** into `SQUARE_WEBHOOK_SIGNATURE_KEY`. The
   notification URL you register must match `SQUARE_WEBHOOK_NOTIFICATION_URL`
   byte-for-byte -- it is part of the signed payload.
3. **Provision a KV store** for idempotency (Upstash Redis is the simplest
   cross-platform option: create a database, copy `KV_REST_API_URL` /
   `KV_REST_API_TOKEN`). Wire it to `EdgeKv` in `kv-idempotency-store.ts`
   with whichever REST/SDK client your platform provides.
4. **Local webhook testing.** Square does not ship an equivalent of
   `stripe listen`; the supported local-testing path is: run your serverless
   function locally (`wrangler dev`, `vercel dev`, or `netlify dev`), tunnel
   it with `ngrok http <port>`, temporarily point the webhook subscription's
   notification URL at the ngrok URL, and use the Developer Dashboard's
   **Webhooks → Subscription → Test** button to fire a sample event.
   `[unverified -- training knowledge; re-check developer.squareup.com/docs/webhooks/overview
   for any newer CLI tooling before relying on this as the only path.]`
5. **Sandbox test cards.** Use Square's published sandbox card numbers
   (Developer Dashboard → Sandbox → Test Values) to exercise the approved
   and declined paths on the hosted Payment Link page.
6. **Run the tests:** `npm install && npm test` (see `package.json` in this
   directory).

## Decline path

A declined sandbox card fails entirely on Square's hosted page -- the buyer
sees Square's own decline messaging and can retry, and your site never sees
raw card data or a stack trace either way (rubric #5).
