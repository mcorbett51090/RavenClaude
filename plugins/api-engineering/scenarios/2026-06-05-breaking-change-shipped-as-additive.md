---
scenario_id: 2026-06-05-breaking-change-shipped-as-additive
contributed_at: 2026-06-05
plugin: api-engineering
product: rest-openapi
product_version: "unknown"
scope: likely-general
tags: [versioning, breaking-change, tolerant-reader, enum, contract-drift, openapi]
confidence: high
reviewed: false
---

## Problem

A team shipped what they believed was an "additive, non-breaking" change to a public REST API: they added a new value (`partially_refunded`) to the `status` enum on the `Order` resource, and a new `refund_breakdown` object alongside the existing `refund_total`. Within hours, three partner integrations broke in production. Two of them threw deserialization errors the moment an order came back with the new status; one silently dropped every order whose status it didn't recognize, so a partner's reconciliation job under-counted refunds for a full day before anyone noticed.

## Constraints context

- A public, partner-consumed REST API with an OpenAPI 3.0 contract and **no version bump policy** — the team's working rule was "additive = safe = no version change."
- Partners were on a mix of generated SDKs (strict, code-genned from the spec → a new enum value is an unknown variant → throws) and hand-rolled clients (a `switch` on `status` with no `default` branch → silent drop).
- The change had passed the team's own contract tests because those tests only asserted the *old* enum values still worked — they never modeled a consumer receiving a *new* one.

## Attempts

- Tried: rolling the enum value back and re-shipping it "more carefully." Failed as a strategy — the underlying question ("is adding an enum value breaking?") was unresolved, so the next additive enum value would break the same partners again.
- Tried: declaring it the partners' fault for not writing tolerant clients. True in principle (a strict reader on a *response* enum is fragile), but unactionable — you don't control the consumer's deserializer, and "be more tolerant" is not a release-safe change-management policy on the producer side.
- Tried (the resolution): classifying the change correctly with the producer/consumer asymmetry, then shipping the genuinely-safe subset and gating the rest.

## Resolution

**"Additive on the wire" is not the same as "non-breaking for the consumer" — the test is whether an existing client can break, and for a closed enum on a response, adding a value can.** The correct classification and fix:

1. **Adding a field to a response is safe** (a tolerant reader ignores unknown fields) — `refund_breakdown` could ship as-is. Adding a value to a **response enum** is **breaking for any strict/closed-enum reader** — it must be treated as a breaking change, not an additive one.
2. **The fix on the producer side:** either (a) bump the major version and offer the new enum value only on the new version, or (b) document the enum as **open/extensible** from day one (`x-extensible-enum` convention) so SDK generators emit an "unknown" fallback variant instead of a closed set, and publish that as the contract *before* the first new value lands.
3. **Add a "new enum value" contract test on the producer side** — assert a consumer that receives an *unmodeled* status degrades gracefully (the test models the consumer, not just the server). This is the test that was missing.
4. **Announce the change on a clock.** Even the safe field addition went out with a changelog entry and a dated note; the enum change went out behind a `Deprecation`/`Sunset`-style migration window on the old major version.

The mental model: a producer's "additive" classification must be made from the **strictest plausible consumer's** point of view, not the wire format's. A closed enum is a contract that says "these are all the values"; widening it silently breaks anyone who believed you.

**Action for the next engineer:** before calling any change "additive, no version bump," ask "could a *strict* generated client break on this?" Adding a required request field, narrowing a type, removing/renaming anything, and **adding a value to a closed response enum** are all breaking — version them. Adding an optional response field is the genuinely-safe additive case. Mark response enums extensible *before* you need to extend them.

Cross-reference: complements [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md) (the versioning tree) and [`../knowledge/api-versioning-and-evolution-decision-trees.md`](../knowledge/api-versioning-and-evolution-decision-trees.md) (the change-classification tree added with this bank), plus [`../best-practices/design-version-only-for-breaking-changes.md`](../best-practices/design-version-only-for-breaking-changes.md) and [`../best-practices/design-use-tolerant-reader-on-additive-changes.md`](../best-practices/design-use-tolerant-reader-on-additive-changes.md).
