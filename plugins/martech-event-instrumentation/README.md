# martech-event-instrumentation

> The **event-collection layer** for Claude Code — the team that decides *what user/product events you capture, with what schema and identity, and where you route them*, and then *instruments them correctly*. Two agents: the **event-taxonomy-architect** (designs the tracking plan + identity model + picks the CDP/collection architecture) and the **instrumentation-engineer** (implements the tracking, consent, validation, and destinations).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "What events should we track for this product, and how should we name them?" | A tracking plan: the event taxonomy (object-action naming), the properties, the spec table, and the identity model — the contract you instrument to |
| "Segment vs RudderStack vs Snowplow — or a warehouse-first CDP?" | A decision-tree-driven CDP + collection-architecture choice (packaged vs warehouse-first/reverse-ETL vs self-hosted; client vs server vs hybrid) + the conditions that would flip it |
| "How do we stitch anonymous visitors to known users?" | An identity model: `anonymousId` → `userId` stitching, alias/merge rules, and where the identity graph lives — designed *before* the first Track call |
| "Implement these events in our app + server." | Typed tracking calls (SDK / server-side), a codegen'd tracking library, schema validation in CI, and QA of the live stream |
| "Wire up consent so we don't collect without a lawful basis." | Consent gating in the collection layer (Google Consent Mode v2 / IAB TCF / GPC), PII minimization, and per-event consent categories |
| "Route these events to our warehouse, ad platforms, and tools." | Destination + reverse-ETL wiring (Hightouch / Census), with server-side delivery where accuracy/ITP resilience matters |

**Two rules it never breaks:** *the tracking plan is the contract* (instrument to the plan, never ad-hoc), and *no identity model → no Track call* (design anonymous→known stitching first).

## What's inside

- **2 agents** — `event-taxonomy-architect` (tracking plan, event taxonomy, identity model, CDP/collection-architecture choice) and `instrumentation-engineer` (SDK/server-side calls, typed tracking library, schema validation in CI, consent wiring, destinations + reverse ETL, stream QA).
- **3 skills** — `design-a-tracking-plan`, `choose-cdp-and-collection-architecture`, `implement-event-instrumentation-and-consent`.
- **2 knowledge files** — a Mermaid CDP/collection decision tree (+ trade-off table) and a 2026 event-instrumentation-patterns reference (naming, identity/stitching, client-vs-server, schema-first/typed tracking, consent & privacy-by-design, destinations/reverse ETL, a dated tooling map).
- **2 templates** — a canonical tracking-plan and a single-event schema spec.

## Where it sits in the stack

```
martech-event-instrumentation (HERE) →  DEFINE & CAPTURE the events         ("what we track, with what schema/identity, routed where")
analytics-engineering                →  dbt models the events downstream    ("model the captured events")
experimentation-growth-engineering   →  runs A/B tests on the events        ("use the events to decide")
marketing-operations                 →  campaign strategy / activation      ("what the business does with them")
data-platform                        →  warehouse the events land in        ("store & serve")
```

This plugin is the **event-collection layer** the others sit on top of. It owns the tracking plan, the schema, and the identity/consent model; the analytics, experimentation, and marketing teams all consume the events it captures. It is **engineering/instrumentation**, deliberately distinct from `marketing-operations` (business campaign strategy), `data-governance-privacy` (org-wide policy / DSAR / PII governance), and `analytics-engineering` (dbt transforms).

## Collection stance

Engine-agnostic on concepts (object-action taxonomy, event-vs-property modeling, anonymous→known identity stitching, client-vs-server-vs-hybrid collection, schema-first/typed tracking with CI validation, consent-by-design, destinations & reverse ETL), fluent across **Segment, RudderStack, Snowplow, and mParticle**, with **warehouse-first / reverse-ETL** (Hightouch, Census) as a first-class alternative to a packaged CDP, and typed-tracking codegen (Avo / Typewriter-style) as the default. CDP feature sets, Consent Mode versions, and pricing carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install martech-event-instrumentation@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
