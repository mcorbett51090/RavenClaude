# Write to a scannable hierarchy at a held reading level

**Status:** Pattern — content leads with the answer, structures for scanning (headline → subhead → body → CTA), and holds one reading-level target per audience.

**Domain:** Content / Readability

**Applies to:** `web-design`

---

## Why this exists

People scan before they read (F-pattern), and AI answer engines extract from structure, so content that buries its point in a long undifferentiated paragraph loses both. The `content-strategist`'s standing positions — headlines say one thing, sentence case for body, scannable structure over walls of text, one reading-level target per audience (a consumer site at 7th–8th grade, a developer doc at 11th–12th) — are readability as a constraint, not a style flourish. The structure also serves SEO/AEO (house opinion #10: SEO + a11y converge): clear H2/H3 questions and short declarative paragraphs are what crawlers and LLMs lift. "Real copy in mocks" (house opinion #6) is the upstream rule — lorem ipsum hides the layout problems that realistic text lengths cause.

## How to apply

Lead each section with a direct, self-contained answer; use a true heading hierarchy (no level skips); keep paragraphs short and the measure readable; hold one reading level.

```html
<article>
  <h1>How fast does the site need to be?</h1>
  <!-- Lead with the answer, in one scannable sentence (inverted pyramid) -->
  <p>Aim for LCP under 2.5 seconds on a mid-range phone over 4G. Here is why and how.</p>

  <h2>Why 2.5 seconds</h2>           <!-- real heading hierarchy: h1 → h2 → h3, no skips -->
  <p>Short, declarative paragraphs. One idea each. Cap the measure with <code>max-inline-size: 65ch</code> for comfortable line length.</p>

  <h3>What to measure</h3>
  <ul><li>Field data at p75…</li></ul>   <!-- lists + tables for scannable comparisons -->
</article>
```

**Do:**
- Lead with the answer; structure headline → subhead → body → CTA; use lists/tables for comparisons.
- Keep a true heading hierarchy (h1 → h2 → h3, no level skips — also an a11y requirement).
- Pick a reading level for the audience and hold it; cap line length around 60–75ch for body text.

**Don't:**
- Use lorem ipsum in mocks (house opinion #6) — realistic copy lengths expose layout problems.
- Skip heading levels (h1 → h3) to get a font size — that's a styling job for tokens, not a semantics hack.
- Ship long paragraphs with no scannable structure, or mix sentence case and Title Case across one surface.

## Edge cases / when the rule does NOT apply

- **Long-form editorial / narrative** has a different rhythm than marketing copy — but it still leads sections with their point and holds a reading level.
- **Legal / regulatory disclosure** copy may be constrained in wording and reading level by counsel — route that through `regulatory-compliance`; don't "simplify" mandated language.
- **Headline craft** can carry personality, but never at the cost of hiding the actual proposition (the clever-headline anti-pattern).

## See also

- [`./content-microcopy-cta-and-errors.md`](./content-microcopy-cta-and-errors.md) — the smallest copy units (CTAs, errors, empty states)
- [`./seo-semantic-structure-and-metadata.md`](./seo-semantic-structure-and-metadata.md) — headings serve SEO/AEO too
- [`./frontend-fluid-type-and-space.md`](./frontend-fluid-type-and-space.md) — measure + type scale make the hierarchy legible
- [`../agents/content-strategist.md`](../agents/content-strategist.md) (reading level, scannability, headline discipline)
- [`../knowledge/answer-engine-optimization-2026.md`](../knowledge/answer-engine-optimization-2026.md) — answer-ready structure for AI extraction

## Provenance

Distilled from the `content-strategist` opinions/anti-patterns (headlines say one thing; sentence case for body; one reading-level target per audience; scannable structure; no clever-headline-hiding-the-proposition), house opinions #6 (real copy in mocks) and #10 (SEO + a11y converge), and the answer-ready-structure tactics in `answer-engine-optimization-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
