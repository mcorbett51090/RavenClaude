# Changelog — web-commerce

All notable changes to the `web-commerce` plugin. Versions follow semver; the plugin's `version` in `.claude-plugin/plugin.json` is the source of truth.

## 0.1.1 — 2026-07-14

Captured field learnings from using the plugin on a live engagement (scaffolded a Square store; designed shop packaging + product-on-site integration for a real site).

### Added

- **`knowledge/provider-tracks-2026.md`** — three net-new sections that answer the customer-facing questions the provider/tier selector doesn't: **§7 the reflect-on-site spectrum** (buy-button — edits sync but a new product needs a new embed; collection-embed/iframe — auto-appears to ~15–20; headless Storefront/Catalog API — full native catalog, premium); **§8 current 2026 fees + the pass-through principle** (card % settles against the merchant's own processor — the integrator never eats it) incl. the **Shopify non-Shopify-Payments ~2% surcharge trap**; **§9 the packaging heuristic** (shop as an add-on not bundled, platform-hosted so the merchant self-serves — because the real cost is build+ops+support, not the fee). All dated + sourced; complements `skills/provider-track-selection`.

## 0.1.0 — initial release (2026-07-13)

First release. The backend-integration lane that scaffolds a payment/commerce provider into a website; plugs into `web-design`'s build pipeline, routes every payment/PII security verdict to `ravenclaude-core/security-reviewer`.

**Architecture** (from a `/forge` deep plan grounded in a 10-exemplar research pass):

- **Three first-class provider tracks — Stripe, Square, Shopify — behind a thin shared payment-lifecycle contract**, not a unified adapter (the leaky-adapter trap Vercel abandoned ~145K LOC to escape).
- **Two tiers per provider**: static (hosted/redirect checkout + a thin serverless function + KV for webhooks/idempotency) and framework (embedded SDK).
- **Security invariants as generated-code invariants**: PCI card-isolation (SAQ-A), constant-time webhook verification before parse, idempotency + event-id de-duplication, env-only secrets (placeholders only in scaffolded `.env.example`).
- **Square POS reconciliation** — one-way, POS-as-source-of-truth inventory sync.
- **Deprecation guards** — never scaffolds Shopify's dead JS Buy SDK / Checkout API or the archived Commerce.js.

**Ships:** the shared TS contract (`templates/shared/`), all three provider tracks (`templates/{stripe,square,shopify}/{static,framework}/`), 5 skills, 4 agents, the `/scaffold-commerce` command, and the two knowledge references.

**Known limitation:** the gold-standard rubric's *live provider-sandbox* dimension (Stripe test-mode, Square sandbox, Shopify dev store — especially the decline/3DS path) must be run in the consumer's own provider account. The plugin ships the test harness and runs every *static* rubric check; it does not and cannot certify the live-sandbox dimension from the marketplace side.

**Security review:** a `ravenclaude-core/security-reviewer` adversarial pass confirmed all six generated-code security invariants hold (PCI card-isolation, constant-time verify-before-parse, idempotency + event-id dedup, secret hygiene, no injection/SSRF, safe error handling) — no blockers. Its cheap defense-in-depth suggestion was applied: Square REST path parameters are now `encodeURIComponent`-escaped.

**Known hardening (tracked for v0.1.1):** the KV `IdempotencyStore` exposes a separate `seen()` + `remember()` (not an atomic claim) and marks an event processed before the consumer's side-effect seam. Under concurrent same-event delivery this is a TOCTOU (mitigated in practice by provider-side dedup), and a throwing side effect can drop a retry. The correct fix — an atomic `claim()` (Redis `SET … NX`) that returns the dedup signal, plus mark-after-side-effects — is a cross-handler interface change deferred to v0.1.1 with its own review rather than rushed in pre-merge.
