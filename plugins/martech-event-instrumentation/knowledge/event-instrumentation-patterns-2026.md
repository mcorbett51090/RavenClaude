# Knowledge — Event-instrumentation patterns (2026)

> **Last reviewed:** 2026-07-08 · **Confidence:** High on the concepts (object-action naming, event-vs-property modeling, identity stitching, client-vs-server trade-offs, schema-first tracking, consent-by-design are stable fundamentals); **Medium on tool-specific specifics — re-verify against the installed SDK/version and the current Consent Mode / TCF / GPC specs.**
> The patterns the `instrumentation-engineer` applies when building instrumentation, and the `event-taxonomy-architect` designs against. Concepts are engine-agnostic; the per-tool mappings and the tooling map are a 2026-07 snapshot.

---

## 1. Object-action naming + a controlled vocabulary

Name events `Object Action` — `Order Completed`, `Product Viewed`, `Signup Started` — with **one consistent case** and a **fixed verb set**. This is the single highest-leverage convention: taxonomy sprawl (`Signup Completed` vs `signup_complete` vs `user-signed-up` for one concept) is the #1 killer of analytics trust because every downstream dashboard silently forks. Write the convention down; enforce it before the first Track call; keep a controlled vocabulary of objects and verbs.

## 2. Event-vs-property — model the object, don't explode the events

Fewer, well-propertied events beat an explosion of bespoke ones. Model the **object** once and pass variation in **properties**:

- Good: `Product Viewed {category, price, source}` — one event, filterable.
- Anti-pattern: `product_viewed_from_search`, `product_viewed_from_home`, `product_viewed_blue` — event explosion, un-analyzable.
- Type every property (string / number / bool / enum), mark required vs optional, and keep property names as consistent as event names.

## 3. Identity & stitching — the hardest part, designed first

The `anonymousId` → `userId` model is a **design decision made before the first Track call**, never retrofitted:

- **`anonymousId`** — assigned on first touch (cookie / device), stable across the anonymous session.
- **`Identify(userId, traits)`** — called when the user becomes known; traits (email, plan) live here, behind a consent category — **not** in event properties.
- **`alias` / merge** — the anonymous→known transition links pre-signup activity to the account; get this rule right or pre-signup events are orphaned forever.
- **Where the identity graph lives** — CDP-native vs resolved in the warehouse. Deterministic (login) beats probabilistic; decide the rule explicitly.

Retrofitting identity onto already-collected anonymous data is the classic un-fixable mess — this is why identity leads the plan.

## 4. Client-side vs server-side — accuracy vs richness

| Mode | Strength | Weakness |
|---|---|---|
| **Client-side** | Rich UI/session context (page, referrer, DOM state); easy to add | ITP (Safari), Firefox ETP, and ad-blockers silently **drop** events → undercount, worst on revenue |
| **Server-side** | Accurate, ITP/ad-blocker-**resilient**, PII stays server-side | Less UI context; more engineering to instrument backends |
| **Hybrid (the norm)** | UI events client-side, revenue/conversion server-side | Two code paths — keep `anonymousId`/identity + a dedup key consistent so one action isn't double-counted |

**Rule of thumb:** revenue and conversion events go server-side (they can't be ad-blocked and survive ITP cookie caps); behavioral/UI events go client-side; most teams run hybrid.

## 5. Schema-first / typed tracking + CI validation

The plan and the code must not drift. **Codegen a typed tracking library** from the tracking plan (Avo, Segment **Typewriter/Protocols**, or a JSON-Schema-driven wrapper) so a typo can't ship a broken event:

- Generate types + call wrappers from the plan → `Analytics.orderCompleted({orderId, revenue})`, never `track('order done', {...})`.
- **Validate schema in CI** — a check (JSON Schema / the generated types / Segment Protocols) fails the PR on an off-plan or mis-typed event.
- Catch the bad event at the PR, not in a downstream dbt test three days later — by then it has already polluted the warehouse and every dashboard on it.

## 6. Consent & privacy-by-design in the collection layer

Consent is **designed into collection, not bolted onto destinations**:

- **Google Consent Mode v2** — gate `analytics_storage` / `ad_storage` (and the ad-user-data / ad-personalization signals) at the source; the tags respect the signal before firing. *(v2 specifics are volatile — verify current signal set; retrieved 2026-07-08.)*
- **IAB TCF** — where a CMP + TCF string applies (esp. EU ad use cases), honor the consent string per purpose.
- **GPC (Global Privacy Control)** — respect the browser signal as an opt-out where law treats it as one.
- **PII minimization** — no raw email/name/phone in event **properties**; keep PII in `Identify` traits behind a consent category, with a lawful basis. Assign every event a **consent category** at design time.

This is the *collection-layer* consent seam — org-wide policy, DSAR fulfillment, and PII governance are `data-governance-privacy`.

## 7. Destinations & reverse ETL

- **Destinations (fan-out)** — from the CDP to warehouses, ad platforms, and tools; prefer **server-side / cloud-mode** delivery for revenue and ad-conversion destinations (accuracy, ITP resilience).
- **Reverse ETL (Hightouch / Census)** — the warehouse-first activation path: model an audience/trait in the warehouse (dbt) and sync it *out* to the tools. Use it when the warehouse is the source of truth; it complements (or, for activation, can replace) a packaged CDP's audience store.
- Keep a **dedup / idempotency key** on events so a retried delivery doesn't double-count.

## 8. Stream QA — trust what lands, not the code

Instrumentation isn't done when the code compiles — it's done when the **live stream matches the plan**:

- The CDP **debugger / live view** shows the event actually arriving with the right shape.
- A **schema diff** vs the tracking plan catches missing/extra/mistyped properties.
- A **dedup + identity check** confirms one action isn't double-counted and anonymous→known stitched correctly.

---

## 2026 tooling map (snapshot — re-verify before quoting)

| Category | Tools (2026-07) | Note |
|---|---|---|
| **Packaged CDP** | Segment, RudderStack, mParticle | RudderStack warehouse-native/OSS-core; mParticle mobile+identity |
| **Self-hosted / schema-first** | Snowplow (BDP) | You own collector→enrich→loader; richest schema control |
| **Warehouse-first / reverse ETL** | Hightouch, Census | Activation from the warehouse; pair with a collector for capture |
| **Typed tracking / codegen** | Avo, Segment Typewriter/Protocols | Plan↔code drift prevention |
| **Consent / CMP** | Google Consent Mode v2, IAB TCF (OneTrust, Cookiebot, Osano CMPs), GPC | Gate at the source |
| **Schema registry** | Snowplow Iglu, Segment Protocols, JSON Schema in CI | The CI validation surface |

> **Volatile:** vendor feature sets, pricing, mobile SDK behavior, and Consent Mode / TCF / GPC spec details change frequently — treat this table as 2026-07 and re-verify with `ravenclaude-core/deep-researcher` before a client commitment.

---

## Anti-patterns the agents flag

- Ad-hoc `track()` calls for events not in the plan (taxonomy sprawl).
- Inconsistent naming/case for one concept; free-text verbs instead of a controlled vocabulary.
- Event explosion — a bespoke event per variant instead of one event + a property.
- Track calls added before the identity model exists → un-stitchable anonymous data.
- Client-only collection for revenue/conversion events that ITP/ad-blockers drop.
- Raw PII in event properties with no lawful basis / consent category.
- Consent bolted on at the destination instead of gated at the source.
- Relying on a downstream dbt test to catch a malformed event instead of validating schema in CI.
- Hand-written stringly-typed `track('...')` calls with no typed layer → plan/code drift.
- Quoting a CDP feature / Consent Mode version / price with no retrieval date.

---

## Provenance

- Engine-agnostic fundamentals (object-action naming, event-vs-property modeling, anonymous→known stitching, client-vs-server accuracy trade-off, schema-first/typed tracking, consent-by-design, reverse ETL) are stable across the martech/analytics-engineering literature, reviewed 2026-07-08.
- Tool-specific specifics (Segment Protocols/Typewriter, RudderStack, mParticle, Snowplow Iglu, Hightouch/Census, Avo; Google Consent Mode v2, IAB TCF, GPC) reflect 2026-07 docs — **re-verify against the installed SDK/version and current consent specs** before shipping, per the accuracy discipline.
