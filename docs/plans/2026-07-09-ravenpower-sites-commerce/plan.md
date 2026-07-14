# Plan — Raven Power website-services commerce site (`sites.ravenpower.net`)

**Slug:** raven-website-commerce · **FORGE depth:** deep · **Date:** 2026-07-09 · **Owner:** Matt Corbett
**Status:** validated (2 divergent panels → critic → tiebreaks → red-team) — awaiting build go-ahead.

> This plan builds a **new, separate** project (new repo `ravenpower-sites`). It does **not** modify the
> RavenClaude marketplace or the existing `ravenpower.net` consulting site.

---

## 1. What we're building (scoped intent)

A polished commerce site at **`sites.ravenpower.net`** that sells Raven Power's website services as a
**3-tier, $0-upfront monthly subscription** — **Starter $149 / Growth $299 / Premium $599**. Checkout is
**Stripe hosted Checkout** (`mode=subscription`, 14-day trial) with **Apple Pay** as a prominent wallet
alongside card / Google Pay / Link. The site is built to the **craft** of Raven Power's Astro winery
portfolio, in the **elevated dark/gold brand** (black + `#C9A249`, Space Grotesk/Inter, raven+lightning
logo). Branded **"Raven Power, powered by RavenClaude."**

### The business model (the decision that makes $0-upfront sound)
**Managed / hosted / no-handoff.** Each customer's site is built from Raven's templates + design tokens
and **lives on Raven's Cloudflare infrastructure**. The subscription keeps it live; **canceling takes the
site down (no code export)**. This is what closes the free-labor exploit a bespoke+trial model would open —
there is nothing to extract, and marginal labor per client is low and bounded.

### Locked decisions
| Decision | Choice |
|---|---|
| Payment stack | Stripe Billing, hosted Checkout, Apple Pay among all wallet methods |
| Host | New repo → Cloudflare Pages (SSR), subdomain `sites.ravenpower.net` |
| Pricing | $149 / $299 / $599 monthly, **$0 upfront** |
| Build model | Managed / hosted / **no-handoff** |
| First charge | 14-day trial, **auto-extended until the site is live** (delivery safety-valve) |
| Brand | "Raven Power, powered by RavenClaude"; dark/gold; raven+lightning logo |

### Out of scope (v1)
Full DesignFlow wizard app, blog/CMS, customer login/dashboard, Stripe Tax, annual billing, coupons,
multi-currency, testimonials engine, a `/work` gallery. (All deferred, tracked as v2.)

### Success signal
A visitor lands, picks a tier, completes a **$0-upfront Apple Pay checkout**, a `trialing` subscription is
created in Stripe, a D1 fulfillment record + founder alert fire, and the site is delivered before the
(auto-extended) trial ends and the first charge lands.

---

## 2. Payment & fulfillment architecture (verified against Stripe docs 2026-07-09)

- **$0 upfront:** `subscription_data.trial_period_days: 14`. $0 invoice today; Apple Pay mandate stays valid
  via Stripe's $0 SetupIntent validation; first real charge at trial end.
- **Apple Pay:** auto-enabled on hosted Checkout, **zero domain verification** (button on `checkout.stripe.com`).
  Prominent but **one method among card / Google Pay / Link** — so desktop/Android buyers aren't excluded.
- **Provisioning signal (critical — do NOT copy the one-time-payment tutorial):** fire build/provision **only**
  on `invoice.paid && amount_paid > 0` **OR** the `customer.subscription` status transition `trialing → active`.
  **Never** gate on `payment_status === 'paid'` (it is `no_payment_required` for $0 trials) or raw `invoice.paid`
  (a **$0 signup invoice** fires with `billing_reason: subscription_create`). Gate on `billing_reason` +
  current state.
- **Teardown signal (the other half of the lifecycle):** `customer.subscription.deleted` → status `canceled` →
  de-provision site + custom hostname. Also `charge.refunded` → teardown; `charge.dispute.created` → alert + pause.
- **Delivery safety-valve:** on `customer.subscription.trial_will_end` (~3 days out), if the customer's site is
  not yet `live`, **push `trial_end` forward** (`subscription.update`) so the first charge never lands on a blank
  site. Target stays 14 days.
- **Dunning:** `invoice.payment_failed` → `past_due`; keep the site **up** during the Smart-Retries grace window;
  transition to `paused` (a "billing issue" holding page, not teardown) only after N days. Set Stripe's
  failed-payment **terminal action = cancel** so `subscription.deleted` deterministically fires teardown.
- **Self-serve:** Stripe **Customer Portal** (cancel/upgrade/downgrade/card-update). Portal links minted via an
  **email magic-link keyed to the Stripe customer email** (proves ownership; also the auth for any ops mutation).
- **Tax:** Raven Power is **seller of record** and owes sales tax. Stripe Tax **OFF at launch**; **nexus monitored**
  in the decisions log; disclosure copy carries **"plus applicable tax"** now so enabling it later can't drift.

### Managed-hosting mechanics (each customer site)
- Customer sites are served from Raven's Cloudflare account: default `name.ravenpower.net` subdomains, or the
  customer's own domain via **CNAME-to-a-Raven-target only** (Cloudflare for SaaS custom hostnames).
  **Never full-zone nameserver delegation** — so a cancel can't brick the customer's MX/email.
- **Teardown** de-provisions the custom hostname and leaves a 30-day "re-point your DNS" holding page.
- **Nightly reconciliation** job diffs live Cloudflare hostnames against D1 `active`/`past_due` rows to catch
  any orphan (billed-but-dark or live-but-unbilled) from a missed webhook.

### Webhook correctness (Cloudflare Workers specifics)
- Read the **raw request stream FIRST**; **no middleware may touch the webhook body** (single-use stream).
- Verify with `stripe.webhooks.constructEventAsync` + `Stripe.createSubtleCryptoProvider()`
  (**sync `constructEvent` fails on Workers**) + `createFetchHttpClient()`.
- **Idempotency:** `INSERT ... ON CONFLICT(event_id) DO NOTHING` as the **first** statement; proceed only if it
  won the insert. Plus a **per-`(subscription_id, target_state)` state guard** (two distinct events can describe
  one transition). Out-of-order tolerant.
- **Never call the Stripe API synchronously** on the webhook path (cold-start + subrequest RTT blows the delivery
  budget → retries → duplicates). Process from the event payload; enqueue any enrichment.
- Assert `env.DB` and `env.STRIPE_WEBHOOK_SECRET` (with a **mode-match** check: test-secret ↔ test-key) at handler
  entry; on failure return non-2xx **and** fire a founder alert via Resend (a path that doesn't depend on D1).

---

## 3. Tiers (managed / no-handoff)

Recurring fee = ongoing hosting + monitoring + a bounded monthly change budget, **not** a disguised one-time build.

| | **Starter $149/mo** | **Growth $299/mo** | **Premium $599/mo** |
|---|---|---|---|
| Managed pages | up to 5 | up to 12 + blog section | unlimited (reasonable) |
| Hosting + SSL + custom domain (CNAME) | ✓ | ✓ | ✓ priority infra + staging |
| Uptime + security monitoring | ✓ | ✓ | ✓ priority |
| Monthly change budget | 30 min | 2 hrs | 5 hrs, 48-h turnaround |
| Content updates | 1 / mo | 4 / mo | rolling / priority |
| SEO | on-page + JSON-LD | monthly on-page tuning | advanced schema + quarterly plan |
| Analytics | quarterly snapshot | monthly report | monthly + conversion tracking |
| Lead capture | contact form | forms + routing | CRM-light + booking integration |
| Strategy | — | annual refresh | monthly strategy call + quarterly refresh |

$0 today → build + onboard during the (auto-extended-until-live) trial → first monthly charge when live →
cancel anytime in the portal (site goes dark, no handoff).

---

## 4. Phased build + gates (DAG)

```
P0 External gates (Matt) ─────────────┐         (Stripe live activation 1–3d = long pole)
P1 Scaffold ─▶ P2 Design system ─▶ P3 Content+legal pages ─┐
   └──────────────▶ P4 Stripe+fulfillment (test mode) ─────┤
                                                            ├─▶ P5 Deploy+domain ─▶ P6 Hardening ─▶ P7 Live launch
P4 ─▶ Pf Fulfillment/teardown+reconciliation ──────────────┘        (needs P0 live + legal)
```
Design track (P1→P2→P3) runs **fully parallel** to P0 (Stripe live activation + DNS). P4 can start after P1
using **test** prices. Critical path to a *paying* site: **P0-live → P5 → P7**.

- **P0 — External gates (Matt, non-code):** activate Stripe live mode (bank/business verify); create 3 recurring
  Products/Prices in test **and** live (`14900/29900/59900`); confirm `ravenpower.net` on a Cloudflare zone; create
  GitHub repo + Cloudflare Pages project; **Commerce Decisions Log** (refund policy, cancel-semantics, jurisdiction,
  tax posture, per-tier SLA). *Gate:* Stripe "Payments enabled"; price IDs recorded; DNS controllable.
- **P1 — Scaffold:** Astro ^5.6 (TS strict), `@astrojs/cloudflare` `output:'server'`, sharp, `@fontsource` fonts,
  port `tokens.css`/`global.css` (dark/gold, from `RavenPower-Website/site/styles.css` — WCAG-AA annotated),
  `config/site.ts` + `config/pricing.ts` (SSOT), `BaseLayout`, `wrangler.toml`, **CI: gitleaks + `astro check` + build**.
  *Accept:* build green on adapter; Lighthouse a11y ≥95 on blank layout; fonts self-hosted; no secrets committed.
- **P2 — Design system:** primitives `.split/.cards/.stats/.cta-band/.chapter/.band` **adapted for the already-dark
  base** (lifted panels `#0a0c10/#10131a` + gold-glow, not light→dark inversion); `Nav` (a11y drawer), `Footer`,
  `Photo`, `TierCard`, `Button`, `Logo` (from `/workspaces/RavenClaude/logo-export/`); `lib/schema.ts`
  (**Organization/Service** JSON-LD — no fake reviews), `lib/nav.ts`. *Accept:* keyboard/SR nav smoke; AA contrast;
  all images via `Photo`.
- **P3 — Content + legal pages (all `prerender`):** `/`, `/pricing`, `/success`, `/cancel`,
  `/legal/{terms,privacy,refund}`; **inline disclosure block** (trial length, post-trial price + "plus applicable
  tax", first-charge timing, cancel path ≤2 clicks) on pricing + at checkout; Corbett Claims case study; founder
  proof; voice = "regulator-grade rigor." Placeholders (address/LLC#) as `TODO(owner)` that **fail a pre-launch grep**.
  *Accept:* Lighthouse ≥95; valid JSON-LD; pricing numbers === `config/pricing.ts` (grep test); no orphan legal links.
- **P4 — Stripe integration (test mode):** `POST /api/create-checkout-session` (re-derive price ID **server-side**
  from tier slug; Turnstile + rate-limit), `POST /api/stripe-webhook` (raw-body, `constructEventAsync`, INSERT-first
  idempotency, state guard, payload-only), `POST /api/create-portal-session` (magic-link gated). *Accept (Stripe CLI):*
  trigger events → correct D1 state; **replay = no-op**; bad signature = 400; full test-card + Apple-Pay-simulator flow.
- **Pf — Fulfillment + teardown:** D1 schema (`webhook_events` PK ledger + `fulfillment` state machine
  `trialing→intake_pending→intake_complete→in_build→live→active→past_due→paused→canceled`); provisioning + **teardown**
  handlers; custom-hostname provision/de-provision; **nightly reconciliation** job; founder alerts (Resend); tiny
  `/admin` read view **behind Cloudflare Access**. *Accept:* simulated full lifecycle leaves a human-visible artifact
  at every transition; cancel → site down + hostname de-provisioned; orphan reconciliation flags a forced mismatch.
- **P5 — Deploy + domain:** connect repo → Cloudflare Pages; bind **D1 (Production!)** + env vars (live keys in
  Production, test in a stable Preview branch alias); register **live** webhook endpoint → capture live signing secret;
  `sites.ravenpower.net` CNAME + TLS. *Accept:* preview passes full test-mode E2E on a real URL; `curl -I` 200 + HSTS;
  webhook "enabled"; startup mode-match assertion passes.
- **P6 — Hardening:** Turnstile + edge + server rate-limit on `/api/*`; dunning timing rule; adversarial webhook
  re-test (replay / tampered / missing-sig / wrong-version); STRIDE-lite on the two endpoints; Stripe webhook-failure
  alerting on. *Accept:* forged webhook provably rejected + logged; past_due pause fires only after grace; rate-limit trips.
- **P7 — Live launch:** one **live-mode** end-to-end (Matt subscribes real card at $0, cancels → verify teardown +
  `subscription.deleted`); Apple Pay verified on real iOS Safari; legal pages linked; `robots.txt`/sitemap;
  monthly Stripe-vs-D1 reconciliation scheduled. *Accept:* full DoD (§6) passes once live before any real customer.

---

## 5. Repo file tree

```
ravenpower-sites/
├─ astro.config.mjs            # @astrojs/cloudflare, output:'server'
├─ wrangler.toml               # D1 binding, nodejs_compat
├─ .env.example                # names only, never values
├─ .gitignore                  # .dev.vars, .env*, dist, .wrangler
├─ src/
│  ├─ config/{site,pricing,legal}.ts        # typed SSOT
│  ├─ lib/{schema,nav,stripe,db}.ts
│  ├─ styles/{tokens,global}.css            # dark/gold, elevated-panel
│  ├─ layouts/BaseLayout.astro
│  ├─ components/{Nav,Footer,Logo,Photo,TierCard,Button,TrialDisclosure}.astro + primitives/
│  ├─ db/{schema.sql,migrations/}           # D1: webhook_events + fulfillment
│  ├─ pages/
│  │  ├─ index / pricing / success / cancel .astro
│  │  ├─ legal/{terms,privacy,refund}.astro
│  │  ├─ admin/index.astro                  # behind Cloudflare Access
│  │  └─ api/{create-checkout-session,stripe-webhook,create-portal-session,health}.ts
│  └─ assets/
├─ public/{robots.txt,favicon,og/}
└─ docs/{commerce-decisions-log,fulfillment-runbook}.md
```

---

## 6. Definition of Done (the money path, live)

1. Visitor `/` → `/pricing` → "Start — $0 today" → `POST /api/create-checkout-session` (server re-derives price) → redirect to `checkout.stripe.com`.
2. **Apple Pay renders** (real iOS Safari; card/Google Pay/Link for others); completes **$0 checkout** (trial; mandate captured).
3. Subscription created **`trialing`** → `/success` shows "$0 today, first bill when your site is live" + intake link + Manage-billing.
4. `checkout.session.completed` → raw-body verified → **INSERT-first idempotent** → D1 `intake_pending` → founder alert (never gated on `payment_status`).
5. Site built during (auto-extended-until-live) trial → state `live`; `trial_will_end` extends `trial_end` if not yet live.
6. First real charge (`invoice.paid && amount_paid>0` / `trialing→active`) → `active`. `payment_failed` → `past_due` (site up, grace) → `paused` after N days.
7. Cancel in portal → `subscription.deleted` → **teardown**: site down + hostname de-provisioned + 30-day DNS holding page. `refund`/`dispute` → teardown/pause.
8. Nightly reconciliation shows zero orphans. Secrets only in Cloudflare env; no address/LLC# hard-coded; disclosure matches the charge.

---

## 7. Risk register (critic + red-team, post-mitigation)

| Risk | P×I | Mitigation (in plan) |
|---|---|---|
| Free-labor extraction | was H/H | **Resolved** by managed/no-handoff |
| Bespoke mispriced as SaaS | was H/H | **Resolved** by templated low-marginal-labor |
| Teardown lifecycle missing | was Crit | Wired to `subscription.deleted`/`refund`/`dispute` + reconciliation |
| Charged for undelivered site | was Crit | Dynamic `trial_end` extend-until-live / waitlist |
| `payment_status`/`$0-invoice` mis-provision | H | Gate on `amount_paid>0`/`trialing→active` + `billing_reason` |
| Day-14 off-session decline | H | Dunning-from-day-one, grace, terminal-action=cancel |
| Webhook idempotency race | H | D1 INSERT-first + `(sub,state)` guard, payload-only |
| Preview/Prod secret + D1 misbind | H | Per-env binding, mode-match + `env.DB` assertions, canary |
| `/admin` PII exposure | H | Cloudflare Access |
| Seller-of-record tax nexus | M/H | Off at launch + nexus monitor + "plus tax" copy |
| DNS/email brick on cancel | H | CNAME-to-Raven only, never NS delegation |

**No residual unmitigated blocker** once these specs are built.

---

## 8. What only Matt can do (external gates)
1. **Stripe:** activate live mode (bank/business verify) + create the 3 Products/Prices; set failed-payment terminal action = cancel.
2. **DNS:** confirm `ravenpower.net` on Cloudflare; authorize the `sites.ravenpower.net` CNAME.
3. **GitHub:** create the `ravenpower-sites` repo (codespace token can't create repos — needs a PAT or manual create).
4. **Decisions log:** refund policy, cancel-semantics, jurisdiction, per-tier SLA, tax posture.
5. **Legal:** attorney review of ToS/Privacy/Refund before real customers (soft-launch with a documented "review-pending" banner acceptable; auto-renewal disclosure is non-negotiable).
