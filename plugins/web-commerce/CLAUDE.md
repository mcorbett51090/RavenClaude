# Web Commerce Plugin — Team Constitution

> Team constitution for the `web-commerce` Claude Code plugin. It scaffolds a **production-ready payment/commerce backend** — Stripe, Square, or Shopify (one per site) — into a static or JS-framework website, at full commerce depth (catalog, cart, checkout, webhooks, idempotency, POS/inventory reconciliation, order handling).
>
> **Orientation:** this file is **domain-specific** to web commerce integration. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).
>
> **Provenance:** the architecture below is the output of a `/forge` deep-depth plan (2026-07-13) grounded in a 10-exemplar research pass. The load-bearing findings live in [`knowledge/provider-tracks-2026.md`](knowledge/provider-tracks-2026.md) and [`knowledge/deprecated-paths-do-not-scaffold.md`](knowledge/deprecated-paths-do-not-scaffold.md) — read them before scaffolding anything.

---

## 1. What this team is and is not

**Is:** the **backend-integration lane** for commerce. It wires a chosen payment provider into a site — provider SDK, hosted-checkout handoff, verified webhooks, idempotency, POS/inventory sync, and the order model — and generates first-party code the consumer owns.

**Is not:** a site builder, a checkout-*UX* designer, a storefront theme, a unit-economics advisor, or a tax authority. It stores no card data and no PII.

### The seams (who owns what next door)

| Adjacent plugin | Owns | This plugin's boundary |
|---|---|---|
| [`web-design`](../web-design/CLAUDE.md) | The site + **checkout UX** — PDP/cart/checkout layout, conversion design, a11y/perf/SEO, static-site & framework implementation, the `gold-standard-website-pipeline`. | `web-commerce` provides the **payment/commerce backend** the UX calls. It plugs into `web-design`'s pipeline as the **commerce/payments sub-step** (defer-to-specialist with a non-specialist stand-in re-run once installed — the same pattern that pipeline uses to defer platform-vs-headless to `ecommerce-dtc`). |
| [`ecommerce-dtc`](../ecommerce-dtc/CLAUDE.md) | The **whether/what of commerce** — assortment, pricing, LTV:CAC, channel spend, platform-vs-headless payback. | `web-commerce` is downstream: it implements the integration once the business decision is made. |
| `ravenclaude-core/security-reviewer` | The **security verdict**. | **Mandatory, non-optional:** every diff touching payments, webhooks, secrets, or PII is reviewed by `security-reviewer` before it is called done. This team proposes controls; it does not self-certify them. |

---

## 2. House doctrine (the team's standing biases)

1. **Three first-class provider tracks — never a unified adapter.** Stripe, Square, and Shopify sit at different layers of the stack; forcing them behind one "commerce" interface is a proven anti-pattern (Vercel `@vercel/commerce` v1 tried it and deleted ~145K LOC in v2). The **only** shared abstraction is a thin **payment-lifecycle contract** (`initiate → authorize/capture → refund → cancel`) + a **normalized webhook handler**, with **advertised capabilities** so a provider can honestly declare `checkout: 'hosted'` / `authorizeCapture: 'n/a'`. Everything else — catalog, cart, inventory, order — is track-specific with shared *conventions*, not shared *code*.

2. **Two tiers per provider, chosen by the site's runtime.** Static site → **hosted/redirect checkout** (no card handling on the merchant origin). Framework site → **embedded SDK** checkout. The tier is a first-class decision the selector records, not an afterthought.

3. **"Static" describes the frontend, not the absence of a server.** A literally-static site cannot verify a webhook or hold idempotency state — there is nowhere for that code to run. So **every static tier ships a thin serverless function** (Cloudflare Worker / Vercel/Netlify Function) **+ external KV** (Upstash / Vercel KV) for the webhook receiver and idempotency store. **Say this out loud** in every static-tier README. A coder who "verifies webhooks client-side" has shipped a security hole, not a feature.

4. **Security invariants are GENERATED-CODE invariants, not documentation.** Every scaffolded integration must, by construction:
   - keep **raw card data off the merchant server** — it is collected only in the provider's iframe/hosted page (PCI SAQ-A). Never a card field bound to a merchant-origin handler.
   - **verify every webhook signature** with a constant-time compare **before** parsing the body.
   - carry an **idempotency key** on every mutating call **and** de-duplicate delivered events by provider event id.
   - read secrets from **env only** — publishable key client-side, secret key server-side, nothing in the bundle or in git. The scaffolder writes `.env.example` placeholders and env references, **never a live key**, and every generated repo gets a `.gitignore` + secret-scan guard.

5. **Square is the default for POS-as-source-of-truth storefronts.** Square's single native catalog/inventory ledger makes online↔in-store reconciliation clean (`catalog.version.updated` + inventory webhook + constant-time HMAC + event-id idempotency). Shopify **inverts** the model (Shopify is the source of truth); Stripe has no real catalog. Match the site's provider to how the merchant's truth already lives.

6. **Generate first-party code — never depend on a dormant or deprecated library.** No JS Buy SDK, no custom Shopify Checkout API, no Commerce.js/Chec, no unmaintained cart lib. If a provider deprecates a path, the templates must not scaffold it — see [`knowledge/deprecated-paths-do-not-scaffold.md`](knowledge/deprecated-paths-do-not-scaffold.md).

7. **"Gold standard" means it passed an executable rubric, not that someone eyeballed it.** See §4. A track is not done until it passes all seven dimensions **including a live provider-sandbox integration test**.

8. **One provider per site, decided once, recorded durably.** The choice + tier + POS need is written to a `commerce.manifest.json` in the target repo so a later invocation reads it instead of re-interviewing and drifting.

---

## 3. Anti-patterns the team flags

- A single unified `CommerceProvider` interface spanning catalog + checkout + payments across all three providers (violates §2 #1 — the leaky-adapter trap).
- Any card input field bound to a merchant-origin request handler (violates §2 #4 — breaks PCI SAQ-A).
- Webhook handling with no signature verification, or verification with a non-constant-time compare (violates §2 #4).
- A mutating API call with no idempotency key, or a webhook handler with no event-id de-duplication (violates §2 #4).
- A secret key written into a template, a client bundle, or the git tree (violates §2 #4).
- A "static site" integration that verifies webhooks or stores idempotency state in the browser (violates §2 #3 — impossible + insecure).
- Scaffolding a deprecated provider path (Shopify JS Buy SDK / custom Checkout API, Commerce.js) (violates §2 #6).
- Declaring a track "gold standard" from a manual read with no executable rubric run + sandbox test (violates §2 #7).
- Re-designing site/checkout UX that `web-design` owns (violates §1 — lane overlap).
- Calling a payment change done without a `security-reviewer` verdict (violates §1 — mandatory review).

---

## 4. The gold-standard rubric (executable, per track)

Every provider×tier template is scored on seven dimensions, each a concrete, falsifiable test — not a checklist item:

| # | Dimension | How it's proven |
|---|---|---|
| 1 | **PCI card-isolation** | static analysis: no card field reaches a merchant-origin handler; only the provider iframe/hosted page collects the PAN |
| 2 | **Webhook signature verification** | a tampered-payload fixture must be rejected; constant-time compare asserted |
| 3 | **Idempotency / exactly-once** | a replayed event id is a no-op; every mutating call carries an idempotency key |
| 4 | **Secret / env hygiene** | bundle + `git grep` for secret-shaped strings returns nothing outside `.env.example` |
| 5 | **Decline / test-mode UX** | a declined-test-card fixture renders a user-facing error, not a stack trace; the provider's test mode + local listener are wired |
| 6 | **DX / setup-time + abstraction** | the track imports the shared contract and declares capabilities; scaffold-to-green time is recorded |
| 7 | **Checkout a11y / i18n** | axe on the checkout surface = 0 critical; user-facing strings externalized |

**Plus (§2 #7):** a **live provider-sandbox integration test** — Stripe test mode + `stripe listen`, Square sandbox, Shopify dev store — covering the happy path **and the decline/3DS path** (where a careless redirect can leak card data into a server log). Static checks alone cannot prove PCI/decline behavior.

**The iteration loop** (this is what "loop and iterate until gold standard" means here): `BUILD → score all 7 + sandbox test → for each failing dim, emit a fix spec → apply → re-score → repeat until 7/7 → freeze the track`. Bounded at 3 cycles per track; a dim still red after 3 cycles escalates to the Team Lead as a design question (contract insufficient vs. genuine provider limitation).

---

## 5. Knowledge bank

| File | Covers |
|---|---|
| [`knowledge/provider-tracks-2026.md`](knowledge/provider-tracks-2026.md) | Stripe/Square/Shopify capability matrix, static-vs-framework tiers, the 10 gold-standard exemplars, POS reconciliation, sources + dates |
| [`knowledge/deprecated-paths-do-not-scaffold.md`](knowledge/deprecated-paths-do-not-scaffold.md) | Dated deprecations/shutdowns the templates must never emit (Shopify JS Buy SDK, Shopify Checkout API, Commerce.js, use-shopping-cart) |

---

## 6. Roadmap (incremental — do NOT gate v1 on all six template sets)

Ship provider-by-provider, each passing the full rubric before the next:

- **v0.1.0** — shared contract + **Stripe** (both tiers, the cheap contract-ratifier) + **Square** (both tiers + POS reconciliation loop, the storefront customer's best fit).
- **v0.2.0** — **Shopify** (both tiers, hosted-checkout only).
- **v0.3.0** — `/scaffold-commerce` selector + `commerce.manifest.json`, the `commerce-template-maintainer` drift agent, and a consolidated a11y/i18n pass.

Agents (`commerce-provider-selector`, `pos-reconciliation-engineer`, `commerce-webhook-security-reviewer`, `commerce-template-maintainer`) arrive with v0.3.0 and MUST ship with ≤300-char descriptions + the scenario-authoring frontmatter schema, or `check-frontmatter.py` fails the build.
