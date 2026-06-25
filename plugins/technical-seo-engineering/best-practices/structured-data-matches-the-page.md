# Structured data must match the visible page — eligibility, not a guarantee

**Status:** Absolute rule
**Domain:** Structured data / rich results
**Applies to:** `technical-seo-engineering`

---

## Why this exists

Structured data (schema.org markup) makes a page **eligible** for a rich result — it does not earn one. Two failure modes follow from forgetting that:

1. **Markup that doesn't match the visible page** — marking up a rating you don't have, a price the user can't see, FAQ content that isn't on the page — is a **structured-data guidelines violation** and can trigger a manual action, costing you all rich-result eligibility. The markup must describe content the user can actually see on that page.
2. **Treating validity as a promise.** Even perfect, validated markup only makes you eligible; the engine decides whether to render the rich result, and may stop showing it at any time. Promising a client "this will get you stars in the SERP" is a promise you can't keep.

## How to apply

**Do:**
- Mark up only content that is **visible on the page**.
- Use **JSON-LD** (Google's recommended format) and a **Google-supported** rich-result type.
- Include the type's **required** properties (no eligibility without them); add recommended ones to strengthen.
- **Validate** with the Rich Results Test (eligibility) and the Schema Markup Validator (syntax) before shipping.
- Frame the outcome as **eligibility**, not a guaranteed SERP feature.

**Don't:**
- Mark up hidden, absent, or invented content (ratings, prices, reviews).
- Promise a rich result.
- Ship without validating, or quote a required-property list from memory (the catalog changes).

## Edge cases / when the rule does NOT apply

- **Generic schema.org with no Google rich result** (e.g. some `WebPage`/`Organization` properties) is still valid and useful for entity understanding — it just won't produce a SERP feature; set that expectation.

## See also

- [`../skills/implement-structured-data/SKILL.md`](../skills/implement-structured-data/SKILL.md).
- [`../knowledge/technical-seo-engineering-reference-2026.md`](../knowledge/technical-seo-engineering-reference-2026.md) — supported types + required properties (re-verify).

## Provenance

Codifies the `core-web-vitals-engineer` house opinion "schema is for eligibility, not decoration." Grounded in Google's structured-data documentation and the schema.org vocabulary, retrieved 2026-06-25 — re-verify the supported-type catalog before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
