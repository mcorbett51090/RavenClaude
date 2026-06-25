# Structured-data spec — <page type / template>

> One spec per page template (PDP, article, FAQ, category…). Markup must match the
> visible page and use a Google-supported type. Validity = eligibility, not a guaranteed
> rich result. Validate before shipping.

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Applies to template:** <e.g. product detail page>

## 1. Target
- **schema.org type:** <Product / Article / FAQPage / BreadcrumbList / Organization / LocalBusiness / …>
- **Rich-result goal:** <which SERP feature — and confirm it's a Google-supported type>
- **Format:** JSON-LD (recommended)

## 2. Property mapping (every value maps to VISIBLE page content)

| Property | Required? | Page source (visible element) | Example value |
|---|---|---|---|
| <name> | required | <h1> | "Trail Runner 2 Shoe" |
| <offers.price> | required | price block | "129.00" |
| <offers.availability> | required | stock badge | schema.org/InStock |
| <aggregateRating> | recommended | reviews widget | <only if genuinely shown> |

- **All required properties present?** <yes/no>
- **Any value not visible on the page?** <none — confirmed (else it's a guideline violation)>

## 3. Markup
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "<Type>"
  // ... required + recommended properties from §2
}
</script>
```

## 4. Validation
- [ ] Rich Results Test — eligible, no errors
- [ ] Schema Markup Validator — syntax clean
- **Expectation set:** eligibility only; the engine decides whether to render the rich result.

## 5. Re-verify
- Supported-type catalog + required-property list confirmed against Google's docs on <date> — `[unverified — catalog changes]` until confirmed.

## 6. Seams
- **Page-rendering implementation** → `frontend-engineering` · **CWV impact of the markup** → `core-web-vitals-engineer`.

---
_Plus the ravenclaude-core Structured Output block._
