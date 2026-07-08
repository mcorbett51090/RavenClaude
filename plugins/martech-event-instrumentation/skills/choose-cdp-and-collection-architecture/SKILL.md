---
name: choose-cdp-and-collection-architecture
description: Pick the right CDP and event-collection architecture for a described workload by traversing the CDP/collection decision tree (source of truth & activation → packaged CDP vs warehouse-first/reverse-ETL vs Snowplow self-hosted; accuracy vs UI-richness → client-side vs server-side vs hybrid), then return the recommendation, the trade-offs, and the conditions that would flip it. Reach for this when the user asks "Segment vs RudderStack vs Snowplow?", "packaged CDP or warehouse-first?", or "client, server, or hybrid?". Used by `event-taxonomy-architect` (primary).
---

# Skill: choose-cdp-and-collection-architecture

> **Invoked by:** `event-taxonomy-architect` (primary). Also consulted by `instrumentation-engineer` when a build reveals the chosen CDP can't express a required pattern.
>
> **When to invoke:** "Segment vs RudderStack vs mParticle vs Snowplow?"; "packaged CDP or warehouse-first / reverse ETL?"; "client-side, server-side, or hybrid collection?"; any "what should collect and route our events?" question.
>
> **Output:** the recommended CDP + collection mode + the trade-offs + the 1-2 flip conditions that would change the answer.

## Procedure

1. **Restate the workload in the tree's terms.** Capture: where the **source of truth & activation** live (warehouse-first vs a packaged CDP's own store), **event volume & cost sensitivity**, **accuracy requirement** (revenue/conversion events vs UI telemetry), **ITP / ad-blocker exposure**, **engineering capacity** (can you operate Snowplow?), **existing stack / lock-in tolerance**, and **privacy posture** (data residency, PII control).
2. **Gate the "warehouse-first vs packaged" fork first.** If the warehouse is already the source of truth and the activation need is "sync warehouse audiences to tools", **warehouse-first / reverse ETL** (Hightouch / Census) may beat a packaged CDP — don't default to packaged by reflex.
3. **Traverse the decision tree** in [`../../knowledge/cdp-collection-decision-tree.md`](../../knowledge/cdp-collection-decision-tree.md) against those inputs:
   - want a managed router + a broad destination catalog, fast → **Segment** (or **RudderStack** for a warehouse-first, cost/control-leaning, OSS-core alternative),
   - mobile-heavy, cross-device identity + audience tooling as a first-class need → **mParticle**,
   - want to own the pipeline, rich behavioral schema, data-residency/control, engineering capacity to operate it → **Snowplow** (self-hosted / BDP),
   - warehouse is the source of truth, activation = "sync to tools" → **warehouse-first / reverse ETL (Hightouch / Census)**, often *alongside* a lightweight collector.
4. **Choose the collection mode**, and usually per-event: **client-side** (rich UI context, but ITP/ad-blockers drop some) / **server-side** (accurate, resilient, less UI context) / **hybrid** (client for UI events, server for revenue/conversion). Most teams need hybrid — say which events go where.
5. **Place the identity + consent seam.** Confirm the chosen architecture can express the plan's identity model (stitching) and gate consent at the source (Consent Mode / TCF / GPC). If it can't, that's a flip condition.
6. **Decide packaged vs self-hosted vs warehouse-first out loud:** packaged buys speed + a destination catalog and adds per-event cost + some lock-in; self-hosted (Snowplow) buys control + schema richness + residency and costs ops; warehouse-first buys "one source of truth" and leans on the warehouse.
7. **State the flip conditions** — the 1-2 facts that, if different, change the answer (e.g., "if event volume 10×'s, the packaged CDP's per-event pricing flips this to warehouse-first / RudderStack").

## Worked example

> User: "Series-B B2B SaaS, ~5M events/month, warehouse (Snowflake) is already our source of truth, small data team, we mainly need to sync product-usage audiences to HubSpot and ad platforms. Segment?"

- **Warehouse-first fork:** source of truth + activation both live in Snowflake → lead with **reverse ETL (Hightouch / Census)** for activation, plus a lightweight collector for capture (RudderStack or Segment) — a full packaged CDP's audience store is redundant here.
- **Collection mode:** revenue/qualification events **server-side** (accuracy, ITP-resilient); in-app UI events **client-side** → **hybrid**.
- **Identity/consent:** stitching modeled in the warehouse; consent gated client-side via Consent Mode.
- **Flip condition:** if the team lacked warehouse/dbt capacity, a packaged CDP's turnkey audiences would win despite the per-event cost; if volume dropped and speed-to-value dominated, Segment alone.

## Guardrails

- Never name a CDP before traversing the tree — workload before brand.
- Don't default to a packaged CDP when the warehouse is already the source of truth — evaluate warehouse-first / reverse ETL explicitly.
- Client-only collection for revenue/conversion events is a trap (ITP/ad-blockers silently drop them) — route those server-side.
- Confirm the architecture can express the plan's **identity model** and **consent gating** before committing; if not, it's a flip condition.
- Volatile claims (CDP feature parity, pricing, Consent Mode versions) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/event-instrumentation-patterns-2026.md`](../../knowledge/event-instrumentation-patterns-2026.md).
