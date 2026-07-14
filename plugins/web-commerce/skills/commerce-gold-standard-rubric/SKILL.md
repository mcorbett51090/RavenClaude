---
name: commerce-gold-standard-rubric
description: "Score a scaffolded commerce integration against the seven-dimension gold-standard rubric and run the BUILD-measure-fix iteration loop until it passes. Use after scaffolding a provider track, before calling it done. Each dimension is a falsifiable test; a live provider-sandbox test is required beyond the static checks."
---

# Commerce Gold-Standard Rubric

"Gold standard" here means **passed an executable rubric**, not "someone eyeballed it." Run this after scaffolding a provider track and before shipping it. Do not gate a whole release on all tracks at once — score and ship provider by provider (CLAUDE.md §6).

## The seven dimensions (each a falsifiable test)

| # | Dimension | Passing test |
|---|---|---|
| 1 | **PCI card-isolation** | No card field reaches a merchant-origin handler; only the provider iframe/hosted page collects the PAN. (`git grep` for card-field bindings to app routes = none.) |
| 2 | **Webhook signature verification** | A tampered-payload fixture is rejected; the compare is constant-time (`safeSignatureEqual`). |
| 3 | **Idempotency / exactly-once** | A replayed event id is a no-op; every mutating call carries an idempotency key. |
| 4 | **Secret / env hygiene** | `git grep` for secret-shaped strings returns nothing outside `.env.example`; publishable vs secret split correct. |
| 5 | **Decline / test-mode UX** | A declined-test-card fixture renders a user-facing error, not a stack trace; test mode + a local listener are wired. |
| 6 | **DX / abstraction** | The track imports `templates/shared/*` and declares `capabilities`; scaffold-to-green time recorded. |
| 7 | **Checkout a11y / i18n** | axe on the checkout surface = 0 critical; user-facing strings externalized. |

## Beyond static checks — the live-sandbox requirement

Dimensions 1, 2, 3, and 5 cannot be **fully** proven by static analysis. Each track ALSO requires a **live provider-sandbox integration test** covering the happy path **and the decline / 3DS path** (where a careless redirect can leak card data into a server log):

- **Stripe** — test mode + `stripe listen` / `stripe trigger`.
- **Square** — sandbox environment.
- **Shopify** — a development store.

The scaffolded consumer repo ships `scripts/verify-template.sh` so these checks are CI-runnable in the consumer's account, not eyeballed once.

## The iteration loop (what "loop until gold standard" means)

```
BUILD → MEASURE (score all 7 + run the sandbox test)
      → for each FAILING dimension, emit a concrete fix spec
      → APPLY the fix → re-MEASURE
      → repeat until 7/7 → freeze the track
```

Bound each track at **3 cycles**. A dimension still failing after 3 cycles escalates to the Team Lead as a design question: is the shared contract insufficient, or is this a genuine provider limitation to record as an accepted `N/A` (e.g. Shopify has no server-side authorize/capture)?
