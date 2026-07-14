# Stripe — framework tier (embedded Payment Element)

Embedded checkout for a Next.js or Astro site: the Payment Element renders
card fields inside Stripe's iframe on your page, while your server only ever
handles a `clientSecret` (not a card number) and the publishable key.

## Files

| File | Purpose |
|---|---|
| [`provider.ts`](provider.ts) | Implements the shared `PaymentProvider` contract — creates a PaymentIntent, plus `authorize`/`capture`/`refund`/`cancel`. |
| [`stripe-signature.ts`](stripe-signature.ts) | Hand-rolled `Stripe-Signature` verification — constant-time, verify-before-parse. |
| [`kv-idempotency-store.ts`](kv-idempotency-store.ts) | `IdempotencyStore` backed by an external KV (Upstash Redis or Vercel KV) reached over `fetch`. |
| [`checkout.ts`](checkout.ts) | Server route: creates the PaymentIntent, returns `{ clientSecret, publishableKey }`. |
| [`payment-element.tsx`](payment-element.tsx) | Client component: mounts the Payment Element and confirms payment. |
| [`webhook.ts`](webhook.ts) | Server route: verify → de-dupe → (your side effects) → 2xx. |
| [`.env.example`](.env.example) | Placeholder env vars — copy to `.env.local`/`.env`, fill with your own test-mode values. |
| [`tests/`](tests/) | Signature-tamper rejection, replay-is-a-no-op, and secret-hygiene checks. |

## Setup

1. `npm install stripe @stripe/stripe-js @stripe/react-stripe-js` in your site's repo.
2. Copy `.env.example` to `.env.local` (Next.js) or `.env` (Astro) and fill
   in your **test-mode** keys from <https://dashboard.stripe.com/test/apikeys>.
   Also add a client-bundle-visible copy of the publishable key (Next.js:
   `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`; Astro: `PUBLIC_STRIPE_PUBLISHABLE_KEY`)
   — see the comment in `.env.example`.
3. Drop `checkout.ts` at `app/api/checkout/route.ts` (Next.js App Router) or
   `src/pages/api/checkout.ts` (Astro).
4. Drop `webhook.ts` at `app/api/stripe/webhook/route.ts` (Next.js) or
   `src/pages/api/stripe/webhook.ts` (Astro), and point a Stripe webhook
   endpoint at its deployed URL (Dashboard → Developers → Webhooks, or
   `stripe listen` for local dev — see below).
5. Provision a KV store — either [Upstash Redis](https://upstash.com/docs/redis/features/restapi)
   or Vercel KV — and set its REST URL/token in `.env.local`/`.env`, UNLESS
   your deployment is a genuinely long-lived process (see the caveat in
   `kv-idempotency-store.ts`).
6. Render the checkout page: call `checkout.ts` from a Server Component /
   server-rendered page to get `{ clientSecret, publishableKey }`, then
   render `<StripeCheckoutForm clientSecret={...} publishableKey={...}
   returnUrl="https://yoursite.com/thank-you" />` from `payment-element.tsx`.
7. Wire your order-management side effects into the marked seam in `webhook.ts`.

## Test-mode workflow

- Use Stripe's [test cards](https://docs.stripe.com/testing) (e.g.
  `4242 4242 4242 4242` succeeds, `4000 0000 0000 0002` declines) against the
  Payment Element. A decline surfaces via `stripe.confirmPayment`'s returned
  `error.message`, rendered in `payment-element.tsx`'s `role="alert"` region —
  this is the user-facing declined-card path required by the plugin's rubric.
- Run `stripe listen --forward-to localhost:<port>/api/stripe/webhook`
  (Stripe CLI) to get a `whsec_...` you can put in `.env.local`/`.env` and
  exercise `webhook.ts` locally against real (test-mode) events, including
  replays via `stripe trigger`.

## What this tier does NOT do

- No card field bound to a merchant handler, ever — the Payment Element
  owns the card fields inside Stripe's iframe (PCI SAQ-A).
- No catalog/inventory system — line items are ad-hoc `Money` + name,
  summed into a single PaymentIntent amount at checkout time.
- No POS reconciliation (Stripe has no POS ledger — see `../../../CLAUDE.md` §2 #5,
  the Square track is the fit for POS-mirrored catalogs).
