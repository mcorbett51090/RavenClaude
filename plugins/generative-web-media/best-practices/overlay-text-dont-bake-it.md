# Overlay text, don't bake it

**Status:** Absolute rule
**Domain:** Anti-slop craft / accessibility
**Applies to:** `generative-web-media`

> Engineering rule. Durable craft principle; the model-legibility landscape shifts, but the overlay rule holds regardless.

---

## Why this exists

Garbled in-image text is the **single most common** generative failure. Even the best text models (Ideogram) are only ~90–95% legible — and *baked-in* text is un-editable, un-localizable, un-selectable, and inaccessible to a screen reader. Real HTML/SVG type layered over a text-free image is crisp, editable, translatable, selectable, and accessible. The image carries the picture; the DOM carries the words.

## How to apply

- Generate images **text-free**; add a negative-prompt baseline against text/watermarks/logos.
- Render the headline, wordmark, or caption as **real HTML/SVG type** over the image (also how you hit the exact brand hex).
- If a design truly needs text-in-image (rare), route to the best text model AND put the same text in the `alt`.
- The curation gate rejects baked-in text ([`../skills/curation-and-accessibility-gate/SKILL.md`](../skills/curation-and-accessibility-gate/SKILL.md)).

**Do:** keep generated images text-free; overlay real type.
**Don't:** trust a model to bake a brand name legibly into an image.

## Edge cases / when the rule does NOT apply

Abstract/decorative "texture" that merely *evokes* letterforms (not readable words) is fine. A one-off art piece where the garble is the point is out of scope for production web media.

## See also

- [`../skills/curation-and-accessibility-gate/SKILL.md`](../skills/curation-and-accessibility-gate/SKILL.md), [`../skills/brand-conditioned-generation/SKILL.md`](../skills/brand-conditioned-generation/SKILL.md)
- [`../knowledge/legal-and-provenance-2026.md`](../knowledge/legal-and-provenance-2026.md) §6 (failure taxonomy)

## Provenance

Codifies the anti-slop house opinion; grounded in the failure-mode sources (lifehackedai, p20v, zsky; retrieved 2026-07-13).

---

_Last reviewed: 2026-07-13 by `claude`_
