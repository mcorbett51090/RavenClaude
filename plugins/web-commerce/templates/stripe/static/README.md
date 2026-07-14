# Stripe — static tier (hosted Payment Links)

Hosted checkout for a literally-static site: no card field ever touches your
origin. This tier is a set of files you copy into your site's repo and wire
up to your own product config + hosting platform.

## The caveat you must not skip

**A static site still needs a thin serverless function.** There is nowhere
in the browser to verify a webhook signature or hold idempotency state —
"static" describes how the *frontend* renders, not "zero server-side
compute." [`webhook.ts`](webhook.ts) is that one piece of compute: a
Fetch-API-shaped `(request: Request) => Promise<Response>` handler that
drops onto a Vercel/Netlify/Cloudflare-Worker edge function unmodified.
Skipping it and "verifying" a webhook client-side is a security hole, not a
feature — see the plugin's [`CLAUDE.md`](../../../CLAUDE.md) §2 #3.

## Files

| File | Purpose |
|---|---|
| [`provider.ts`](provider.ts) | Implements the shared `PaymentProvider` contract — hosted checkout via Payment Links, plus `authorize`/`capture`/`refund`/`cancel`. |
| [`stripe-signature.ts`](stripe-signature.ts) | Hand-rolled `Stripe-Signature` verification — constant-time, verify-before-parse. |
| [`kv-idempotency-store.ts`](kv-idempotency-store.ts) | `IdempotencyStore` backed by an external KV (Upstash Redis or Vercel KV) reached over `fetch`. |
| [`webhook.ts`](webhook.ts) | The serverless function: verify → de-dupe → (your side effects) → 2xx. |
| [`checkout.ts`](checkout.ts) | Setup-time script: generates a Payment Link URL to embed as a static `<a href>`. |
| [`.env.example`](.env.example) | Placeholder env vars — copy to `.env`, fill with your own test-mode values. |
| [`tests/`](tests/) | Signature-tamper rejection, replay-is-a-no-op, and secret-hygiene checks. |

## Setup

1. `npm install stripe` in your site's repo (this template imports it; nothing else).
2. Copy `.env.example` to `.env` and fill in your **test-mode** keys from
   <https://dashboard.stripe.com/test/apikeys>.
3. Provision a KV store — either [Upstash Redis](https://upstash.com/docs/redis/features/restapi)
   (free tier is enough for idempotency keys) or Vercel KV — and set its
   REST URL/token in `.env`.
4. Edit the `EXAMPLE_LINE_ITEMS` in `checkout.ts` to your real product/price,
   then run:
   ```shell
   STRIPE_SECRET_KEY=sk_test_xxx npx tsx checkout.ts
   ```
   Paste the printed URL into your HTML as a plain, accessible link:
   ```html
   <a href="https://buy.stripe.com/xxxxx">Buy now — $48.00</a>
   ```
   Re-run whenever the price changes — Payment Links are immutable once created.
5. Deploy `webhook.ts` to your platform's edge/serverless function slot and
   point a Stripe webhook endpoint at its URL (Dashboard → Developers →
   Webhooks, or `stripe listen --forward-to <url>` for local dev — see below).
6. Wire your order-management side effects into the marked seam in `webhook.ts`.

## Test-mode workflow

- Use Stripe's [test cards](https://docs.stripe.com/testing) (e.g.
  `4242 4242 4242 4242` succeeds, `4000 0000 0000 0002` declines) against the
  Payment Link generated in step 4 — Stripe's own hosted page renders the
  decline as a user-facing error; no code on your side handles that path.
- Run `stripe listen --forward-to localhost:<port>/webhook` (Stripe CLI) to
  get a `whsec_...` you can put in `.env` and exercise `webhook.ts` locally
  against real (test-mode) events, including replays via `stripe trigger`.

## What this tier does NOT do

- No card field, ever, on your origin (PCI SAQ-A — Stripe's hosted page owns the PAN).
- No catalog/inventory system — line items are ad-hoc `Money` + name, turned
  into a Stripe Price at link-generation time.
- No POS reconciliation (Stripe has no POS ledger — see `../../../CLAUDE.md` §2 #5,
  the Square track is the fit for POS-mirrored catalogs).
