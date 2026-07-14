# Provider Tracks 2026 — Stripe · Square · Shopify

> Frozen research reference. Sources retrieved **2026-07-13** (a `/forge` G1 pass, three research lanes). Every artifact in this plugin cites this file rather than restating it. Re-verify any capability against the linked primary docs before it becomes a durable code invariant; treat everything as "true as of 2026-07-13," not permanently.

## 0. The one architectural decision that shapes everything

**Three first-class provider tracks, unified only by a thin payment-lifecycle contract — NOT a single "commerce" adapter.**

The strongest evidence: Vercel's `@vercel/commerce` **v1** defined exactly such a unified provider interface (catalog + cart + customer + checkout + hooks), and **v2 deleted ~145K LOC to abandon it** in favor of one provider per repository ("swap the `lib/shopify` file"). Vercel now maintains only the Shopify version.
Source: <https://vercel.com/blog/introducing-next-js-commerce-2-0>, <https://github.com/vercel/commerce/blob/v1/packages/commerce/new-provider.md> (2026-07-13).

The abstractions that **survive** (Medusa `AbstractPaymentProvider`, Vendure `PaymentMethodHandler`, Saleor transaction webhooks) unify **only the payment lifecycle** (`initiate → authorize/capture → refund → cancel` + a webhook-normalization method), and keep catalog/checkout **out** of that interface.
Sources: <https://docs.medusajs.com/resources/references/payment/provider>, <https://docs.vendure.io/guides/core-concepts/payment/>, <https://docs.saleor.io/developer/payments/payment-apps> (2026-07-13).

**Design consequence:** a thin shared contract = payment-lifecycle interface + normalized webhook handler + **advertised capabilities** (Saleor `actions` style) so a provider can declare `checkout: 'hosted'` / `authorizeCapture: 'n/a'`. Catalog, cart, inventory, order = per-track code with shared *conventions*.

## 1. The three providers sit at different layers

| Concern | **Stripe** | **Square** | **Shopify** |
|---|---|---|---|
| Native scope | Payments; catalog is thin, feeds Checkout | Payments **+ POS**; one native catalog/inventory ledger | Owns **catalog + checkout** |
| Checkout ownership | You host (redirect) or embed (Element) | You host (redirect) or embed (Web Payments SDK) | **Shopify-hosted only** — you cannot run your own checkout on Shopify rails |
| Catalog source of truth | **Your app/DB** (Stripe has no real catalog) | **Square** (POS = truth) | **Shopify** |
| Card handling | Provider iframe/hosted → PCI SAQ-A | Client-side tokenization (SDK) or hosted | Provider-hosted checkout |
| POS unification | N/A | **Native, single ledger** (strongest) | Inverts — needs Shopify POS in-store, or a connector with an external master |

Sources: <https://docs.stripe.com/payments/checkout>, <https://developer.squareup.com/docs/web-payments/overview>, <https://developer.squareup.com/docs/checkout-api-overview>, <https://shopify.dev/docs/api/storefront/latest> (2026-07-13).

**Practical routing:** storefronts wanting online inventory to mirror an in-store POS → **Square** (default). Payments-first with an app-owned catalog → **Stripe**. Wanting a hosted store + checkout → **Shopify**.

## 2. Two tiers per provider

**Static tier → hosted / redirect checkout** (no card handling on the merchant origin):
- Stripe: Payment Links / Buy Button, or a Checkout Session in hosted mode. <https://docs.stripe.com/payment-links> (2026-07-13)
- Square: hosted Checkout API / Payment Links (`square.link/...`), no backend for the payment page. <https://developer.squareup.com/docs/checkout-api-overview> (2026-07-13)
- Shopify: Buy Button channel embed, or Storefront **Cart API** → `cart.checkoutUrl` redirect. <https://www.shopify.com/buy-button>, <https://shopify.dev/docs/api/storefront/latest> (2026-07-13)

**Framework tier → embedded SDK** (server routes + webhooks):
- Stripe: Payment Element + Payment Intents (publishable key client, secret key server; card data stays in the Stripe iframe). <https://docs.stripe.com/payments/payment-element> (2026-07-13)
- Square: Web Payments SDK → single-use token → server `CreatePayment`. <https://developer.squareup.com/docs/web-payments/overview> (2026-07-13)
- Shopify: Hydrogen / Storefront API (GraphQL); checkout still completes on Shopify's hosted page via `checkoutUrl`. <https://github.com/Shopify/hydrogen> (2026-07-13)

**The static-tier caveat (load-bearing):** a literally static site has nowhere to verify a webhook or store idempotency state. Every static tier therefore ships a **thin serverless function + external KV** for the webhook receiver and idempotency store. "Static" = the frontend rendering model, not "zero server-side compute." This is architectural reasoning atop the verified hosted-checkout facts — flagged as such.

## 3. Cross-cutting security invariants (make them generated-code invariants)

- **PCI SAQ-A:** card data is collected only in the provider's iframe/hosted page — never a card field on a merchant-origin handler. Store only card type / last4 / expiry. Sources: <https://stripe.com/guides/pci-compliance>, <https://docs.stripe.com/security/guide> (2026-07-13). *(Square's exact SAQ level is `[unverified — training knowledge]`; docs confirm client-side tokenization but the PCI-scope page wasn't opened this session.)*
- **Webhook verification:** verify the provider signature with the endpoint secret, **constant-time compare, before parsing** the body; don't mutate the raw body (invalidates the signature); return 2xx fast, process async; events are not order-guaranteed and are retried. Stripe: `Stripe-Signature` + `whsec_` (<https://docs.stripe.com/webhooks>). Square: HMAC-SHA-256 in `x-square-hmacsha256-signature` over signature-key + URL + raw body, constant-time compare (<https://developer.squareup.com/docs/webhooks/overview>). (2026-07-13)
- **Idempotency / exactly-once:** send an idempotency key on every mutating call (Stripe: `Idempotency-Key` header, ~24h replay window; Square: `idempotency_key` request field), **and** de-duplicate delivered events by provider event id (Stripe `event.id`, Square `event_id`). Sources: <https://docs.stripe.com/api/idempotent_requests>, Square webhooks doc (2026-07-13).
- **Secrets:** publishable key client-side only; secret + webhook-signing keys server-side, env-loaded, never in the bundle or git; TLS 1.2+. <https://docs.stripe.com/security/guide> (2026-07-13).

## 4. POS / online reconciliation (Square is cleanest)

Square exposes an explicit source-of-truth model: choose the master catalog, sync one way, pull only changed objects via `catalog.version.updated` webhooks (or `SearchCatalogObjects` with `begin_time`), store cross-reference IDs as custom attributes. Square **explicitly warns bidirectional sync is risky** (concurrency/merge/dup/delete) and out of scope.
Source: <https://developer.squareup.com/docs/catalog-api/sync-with-external-system> (2026-07-13).

Reference reconciliation loop for the Square track: `catalog.version.updated` + inventory webhook → constant-time HMAC verify → `event_id` idempotency → reconcile with **Square as source of truth**. Shopify inverts this (Shopify = truth); Stripe has no catalog to reconcile.

## 5. The 10 gold-standard exemplars this plugin replicates

1. **Stripe Payment Links / Buy Button** — no-code hosted checkout for static sites. <https://docs.stripe.com/payment-links>
2. **Stripe Checkout Sessions** — hosted or embedded prebuilt checkout. <https://docs.stripe.com/payments/checkout>
3. **Stripe Payment Element + Payment Intents** — full framework depth, card data isolated. <https://docs.stripe.com/payments/payment-element>
4. **Snipcart** — static-site full commerce via data attributes + one script + a gateway. <https://docs.snipcart.com/v3/>
5. **Square Web Payments SDK** — client tokenization → server charge. <https://developer.squareup.com/docs/web-payments/overview>
6. **Square hosted Checkout API** — no-backend hosted payment page + Orders. <https://developer.squareup.com/docs/checkout-api-overview>
7. **Shopify Buy Button + Storefront Cart** — static embed → hosted `checkoutUrl`. <https://www.shopify.com/buy-button>
8. **Shopify Hydrogen** — official React headless framework; hosted checkout via `checkoutUrl`. <https://github.com/Shopify/hydrogen>
9. **Medusa `AbstractPaymentProvider`** — the thin payment-lifecycle interface + `getWebhookActionAndData` normalization to model our shared contract on. <https://docs.medusajs.com/resources/references/payment/provider>
10. **Vercel Commerce provider-swap architecture** — the "one provider per track, thin seam" lesson (and the cautionary v1→v2 abandonment). <https://github.com/vercel/commerce>

(All retrieved 2026-07-13.)

## 6. Confidence flags carried forward

- Shopify **Buy Button still supported in 2026** rests on Shopify blog/help, not a changelog entry → **Medium**. The **JS Buy SDK deprecation** (distinct) is **High** (see the deprecations doc).
- Square's exact **PCI SAQ level** → `[unverified — training knowledge]`.
- Hydrogen's exact **React Router version** → **Low** (secondary sources); the core facts (Oxygen, GraphQL Storefront API, hosted checkout) are **High**.
- `use-shopping-cart` shows a **maintenance conflict** (docs claim React 19 support; repo's last release Feb 2021) → generate first-party code, do not depend. Verify the repo's default-branch commit date before any dependency decision.

---

> **The three sections below are net-new (added 2026-07-14) from using this plugin on a live engagement** (scaffolded a Square store; designed shop packaging + product-on-site integration for a real site). They answer the customer-facing questions the selector (§2, and [`../skills/provider-track-selection/SKILL.md`](../skills/provider-track-selection/SKILL.md)) doesn't: *"will my products show on my own site?"*, *"what does it cost?"*, and *"do I bundle a shop into the plan or sell it as an add-on?"* They **complement** the provider/tier picker — read that skill first for **which** provider+tier; read here for how the result reflects on the site, what it costs, and how to package it.

## 7. The reflect-on-site spectrum — "will my products show on my custom site?"

A real, recurring customer question, and a **second axis** on top of provider+tier: *how* the chosen store surfaces on the merchant's own custom-designed site. Three integration depths, cheapest→richest. The key differentiator is **what happens when the merchant adds a NEW product** (not just edits an existing one).

| Depth | What renders on the site | Edit existing product (price/stock/image) | **Add a NEW product** | Good up to | Best for |
|---|---|---|---|---|---|
| **Buy button / payment link** (light) | One embedded button/widget per product | **Syncs live** to the embedded button — no code change | **Requires embedding a new button** (a code/site edit each time) | A handful of hero products | A few fixed SKUs that rarely change |
| **Collection embed / iframe** (default full store) | A whole collection renders inline | Syncs live | **New products auto-appear** in the collection — no site edit | **~15–20 products**, no filtering/search | A small catalog the merchant self-manages |
| **Headless** — Shopify **Storefront API** / Square **Catalog API** (premium) | Full catalog rendered natively in the site's own design | Syncs live | Auto-appears, with search + filter, native styling | Large/filtered catalogs | A bespoke storefront experience — quote as a premium tier |

Sources: Shopify Buy Button product page + buy-button blog <https://www.shopify.com/buy-button>; Shopify **Collection** Buy Button (whole-collection embed, new products auto-appear) <https://help.shopify.com/en/manual/online-sales-channels/buy-button/create-buy-buttons#create-a-collection-buy-button>; Shopify headless / Storefront API <https://shopify.dev/docs/storefronts/headless>; Square Catalog / Online API <https://developer.squareup.com/docs/online-api> (all retrieved 2026-07-14). The "new product needs a new button vs. auto-appears" contrast is the load-bearing decision driver and is confirmed by the buy-button vs. collection-embed docs above.

**Routing:** map this to the tier from [`../skills/provider-track-selection/SKILL.md`](../skills/provider-track-selection/SKILL.md) — the **buy button / collection embed** depths are natural fits for the **static tier**; **headless** is a **framework-tier** build. Set the merchant's expectation on the "new product" behavior *before* scaffolding: a merchant who adds SKUs weekly should not be sold the buy-button depth (every new product is a site edit).

## 8. Current fees + the pass-through principle

**The pass-through principle (the doctrine that reframes packaging, §9):** card-processing fees settle against the **merchant's OWN processor account** — the integrator/agency **never eats the %**. The scaffolded code moves money into the merchant's Stripe/Square/Shopify account; the % is deducted there. So the fee table below is the *merchant's* cost of selling, **not** a cost line the agency carries or should mark up.

| Provider | Card fee | Monthly | Notes / the trap |
|---|---|---|---|
| **Stripe** | **2.9% + $0.30** online | **$0** (no monthly) | Cleanest pay-as-you-go; no platform fee. <https://stripe.com/pricing> |
| **Square** (in-person) | **2.6% + $0.15** | $0 | Square Online has a **free tier**. <https://squareup.com/us/en/pricing> |
| **Square Online** (Free plan) | **3.3% + $0.30** | $0 | The free-tier online rate |
| **Square Online** (Plus plan) | **2.9% + $0.30** | **$49/mo** | Plus buys the lower online rate + features |
| **Shopify** (Basic) | **2.9% + $0.30** online **with Shopify Payments** | **$39/mo** ($29/mo billed annually) | **The trap ↓** |

**The Shopify third-party-gateway surcharge trap:** on Shopify, using **any non-Shopify-Payments gateway** (e.g. routing to Stripe directly) adds a **~2% surcharge on top of the gateway's own card fee** — Shopify's platform toll for not using its rails. Default any Shopify build to **Shopify Payments** unless there's a hard reason not to, and flag the 2% explicitly if a merchant asks to bring their own gateway. Sources: Shopify pricing <https://www.shopify.com/pricing>; corroborated by demandsage Shopify-pricing-2026 and swipesum Square-fees-2026 (retrieved 2026-07-14). Exact plan prices drift — re-check the pricing pages before quoting a merchant; the **shapes** (Stripe no-monthly / Square free online tier / Shopify monthly + BYO-gateway surcharge) are the durable facts.

## 9. Packaging heuristic — add-on vs bundled, and self-service ops

Follows directly from the pass-through principle (§8): because the agency **doesn't** carry the card %, the real cost of "adding a shop" for the merchant is **build + ongoing ops + support** — not the transaction fee. That flips the packaging math.

| Heuristic | Do | Why |
|---|---|---|
| **Shop is an add-on, not bundled** into a flat site plan | Price the shop as a separate line item | Bundling raises the base price for the **non-sellers**, and exposes a flat plan to **unbounded store variance** (support load scales with catalog size, not with a fixed fee). The card % isn't yours to bundle anyway (§8). |
| **Build on Shopify / Square — not a bespoke store** | Stand the catalog up on the platform dashboard; the **merchant self-manages products** there | Ongoing ops for the agency drop to **≈ near-zero** — the merchant edits their own products/prices/stock in the platform UI; you're not the CMS for their inventory. |
| **Low-build "light payments" path = Square static tier** | Hosted Payment Links + a thin Worker webhook (the §2 static tier) | Lowest build + lowest ongoing burden for a merchant with a few SKUs who wants to take a card without a full store. |

**One-line rule of thumb:** *sell the shop as an add-on, host the catalog on the platform so the merchant self-serves, and reserve bespoke/headless (§7) for a premium quote.* This is a **packaging/labor-allocation** heuristic, not a pricing table — the specific dollar amounts are the agency's call; the **structure** (add-on, self-service, platform-hosted) is the reusable learning. `[unverified — training knowledge]` on any specific margin figure; the pass-through and self-service mechanics are grounded in §7–§8.
