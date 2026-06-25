---
name: implement-structured-data
description: "Implement schema.org structured data for rich-result eligibility — pick a Google-supported type, write valid JSON-LD that matches the visible page, include the required (not just recommended) properties, and validate with the Rich Results Test / Schema validator. Reach for this when asked to add Product/Article/FAQ/Breadcrumb/Organization markup or to win a rich result. Used by `core-web-vitals-engineer` (primary)."
---

# Skill: implement-structured-data

> **Invoked by:** `core-web-vitals-engineer` (primary).
>
> **When to invoke:** "add structured data / schema markup"; "make us eligible for a rich result"; "fix our schema validation errors."
>
> **Output:** valid JSON-LD for a Google-supported rich-result type, matching the visible page, with required properties present and a validation step.

## Procedure

1. **Confirm a supported rich-result type exists** for the content (e.g. Product, Article, FAQ, Breadcrumb, Recipe, Organization, LocalBusiness). If Google doesn't support a rich result for it, generic schema.org is still valid but won't produce a SERP feature — set the expectation.
2. **Prefer JSON-LD** in a `<script type="application/ld+json">` — decoupled from the HTML, the format Google recommends. Avoid Microdata/RDFa for new work.
3. **Match the visible page.** Every value in the markup must correspond to content the user can see on that page. Marking up hidden or absent content is a structured-data guideline violation.
4. **Include the REQUIRED properties.** Each rich-result type has required vs recommended properties; missing a *required* one means no eligibility. Add recommended ones to strengthen it.
5. **Validate before shipping.** Run the Rich Results Test (eligibility) and the Schema Markup Validator (syntax). Fix errors; warnings are usually recommended-property gaps.
6. **Set the expectation:** valid markup makes you *eligible*; the engine decides whether to render the rich result.

## Worked example

> User: "Add Product structured data to our PDP."

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Trail Runner 2 Shoe",
  "image": "https://example.com/img/trail-runner-2.jpg",
  "description": "Lightweight trail running shoe.",
  "sku": "TR2-BLK-10",
  "brand": { "@type": "Brand", "name": "Example" },
  "offers": {
    "@type": "Offer",
    "price": "129.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/shoes/trail-runner-2"
  }
}
</script>
```

`offers`, `name`, and `image` are required for the Product rich result; `review`/`aggregateRating` are recommended. Validate, then confirm the price/availability shown match the visible page.

## Guardrails

- Never mark up content that isn't visible on the page, or rating/review data you don't genuinely have — it's a guideline violation and risks a manual action. (See [`../../best-practices/structured-data-matches-the-page.md`](../../best-practices/structured-data-matches-the-page.md).)
- Never promise a rich result — promise eligibility; the SERP feature is the engine's call.
- Re-verify the required-property list and supported types before quoting — Google's rich-result catalog changes (see [`../../knowledge/technical-seo-engineering-reference-2026.md`](../../knowledge/technical-seo-engineering-reference-2026.md)).
