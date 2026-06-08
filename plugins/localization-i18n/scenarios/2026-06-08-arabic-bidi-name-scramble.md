---
scenario_id: 2026-06-08-arabic-bidi-name-scramble
contributed_at: 2026-06-08
plugin: localization-i18n
product: formatjs
product_version: "unknown"
scope: likely-general
tags: [rtl, bidi, arabic, hebrew, isolation, interpolation, css-logical]
confidence: high
reviewed: false
---

## Problem

An app shipped Arabic and Hebrew, set `dir="rtl"` on the page, and considered RTL "done." Two
classes of bug came straight back from native reviewers. First, interpolated runtime values
scrambled sentences: an Arabic notification "تمت مشاركة الملف Q3-report.pdf معك" rendered with the
Latin filename and the trailing Arabic words flipped to the wrong side of the line, and phone
numbers and `@handles` jumped position mid-sentence. Second, the layout only half-mirrored — the
back-chevron still pointed left, progress bars filled left-to-right, but padding had flipped, so
controls overlapped. The team had treated RTL as one attribute instead of a discipline.

## Constraints context

- ~30 screens, CSS written years earlier with physical properties (`margin-left`, `padding-right`,
  `left:`), so nothing mirrored automatically.
- Messages built with `react-intl` but values dropped in raw, no bidi isolation anywhere.
- A mix of direction-sensitive chrome (chevrons, carousels, progress) and direction-neutral assets
  (the logo, product screenshots) that must NOT mirror.

## Attempts

- Tried: forcing `direction: rtl` harder and adding `text-align: right` overrides. Failed — it
  fixed paragraph direction but not the value-level scrambling, and the physical CSS still didn't
  mirror, so the overlaps stayed.
- Tried: reordering the interpolation in the Arabic translation by hand so the filename "looked
  right." Failed — it broke the moment a different-length value was substituted; the directionality
  is the value's, not the sentence's, so no static reordering holds.
- Tried: the three-part RTL discipline — (1) migrate physical CSS to logical properties
  (`margin-inline-start`, `padding-inline`, `inset-inline-start`) so layout mirrors automatically;
  (2) bidi-isolate every interpolated value with the Unicode FSI…PDI pair / `<bdi>` so a Latin
  filename or a number can't reorder the Arabic around it; (3) selectively mirror direction-sensitive
  chrome (chevrons, progress, carousels) while leaving the logo and photos unmirrored. This worked.

## Resolution

Logical CSS made the layout mirror with no per-screen overrides, bidi isolation stopped values from
scrambling sentences regardless of their content or length, and the selective-mirroring pass fixed
the chevrons and progress without flipping the logo. The visual-mirroring review (which elements
mirror, alignment, caret position) was handed to `web-design`; this work owned the contract — logical
properties, isolation, the mirror/don't-mirror list — and `localization-qa` verified it on the running
RTL build, which is its own discipline, not an extension of the LTR test pass.

## Lesson

RTL is logical CSS + bidi isolation + selective mirroring, designed in and QAed on the running build —
not a single `dir=rtl` attribute. Always wrap interpolated runtime values in FSI…PDI / `<bdi>` so an
untrusted value can't decide where the words around it land
(`bidi-isolate-interpolated-values`), and never mirror logos or photographic content.
