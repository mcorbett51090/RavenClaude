# Design for RTL and 30 % text expansion

**Status:** Pattern
**Domain:** Internationalization (i18n) — UI design and layout
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

Two structural layout properties of internationalized UIs are consistently under-designed for and
discovered late (at translation time, or in production for a new locale):

1. **Text expansion.** German runs approximately 30 % longer than English on average; Finnish and
   other Uralic/agglutinative languages can run 40–60 % longer; Hindi, Thai, and Southeast Asian
   scripts may render larger due to font metrics. A UI designed to exactly fit English text will
   overflow, truncate, or break layout in German and Finnish. Late-discovered overflow is expensive:
   it requires UI redesign, CSS changes, and regression testing across all affected components.

2. **RTL/bidi layout.** Arabic (ar-*), Hebrew (he-IL), Persian/Farsi (fa-IR), and Urdu (ur-*)
   read right-to-left. A UI that uses physical CSS properties (`margin-left`, `padding-right`,
   `left: 0`, `float: left`) instead of logical properties (`margin-inline-start`, `padding-inline-end`,
   `inset-inline-start`) will require a full CSS rewrite to support RTL. Physical properties
   cannot be automatically mirrored; logical properties are mirrored by the browser when
   `dir="rtl"` is applied.

Both are retrofit problems: fixing them after the UI is built is expensive and risky. Designing
for them from the start costs almost nothing extra.

## How to apply

### Text expansion

**Do:**

- Design UI containers to accommodate text up to **150 % of English source length** without
  truncation or overflow. For tight-space components (mobile button labels, table cells), allow
  wrapping to a second line.
- Use `min-width` (not `max-width`) for components that must accommodate longer text. Prefer
  `overflow: visible` or `word-break: break-word` over hard truncation with ellipsis unless
  truncation is the deliberate UX.
- Run the expansion pseudo-locale (`i18n-foundations-and-icu` Step 7) to verify that no component
  clips at the pseudo length. Do this before translation, not after.
- For navigation labels and buttons: test with the longest German equivalent of the English label.
  Example: "Settings" → "Einstellungen" (13 chars vs. 8).

**Don't:**

- Hard-code a fixed `width` or `max-width` on a text container that will hold translated text
  without validating expansion.
- Use `white-space: nowrap` on UI copy without a hard expansion budget for that component.
- Assume English-length text and add a `text-overflow: ellipsis` without testing in German/Finnish.

### RTL/bidi

**Do:**

- Use **CSS logical properties** for all layout-critical properties:

  | Physical (avoid) | Logical (use) |
  |---|---|
  | `margin-left` | `margin-inline-start` |
  | `margin-right` | `margin-inline-end` |
  | `padding-left` | `padding-inline-start` |
  | `padding-right` | `padding-inline-end` |
  | `left: X` | `inset-inline-start: X` |
  | `right: X` | `inset-inline-end: X` |
  | `float: left` | (avoid float; use flex/grid with `start`/`end`) |
  | `text-align: left` | `text-align: start` |
  | `text-align: right` | `text-align: end` |
  | `border-left` | `border-inline-start` |

- Set `dir` dynamically on the root element:
  ```js
  const rtlLocales = ["ar", "he", "fa", "ur"];
  document.documentElement.dir = rtlLocales.includes(locale.split("-")[0]) ? "rtl" : "ltr";
  ```
- Mirror directional icons (back/forward arrows, progress bars, bullet points) for RTL.
- Run the bidi pseudo-locale variant in CI to surface layout failures before any RTL translation
  is done.

**Don't:**

- Treat RTL as a CSS `transform: scaleX(-1)` on the whole page — this mirrors images and icons
  that should not be mirrored (logos, non-directional icons).
- Manage RTL with a separate RTL stylesheet that overrides all physical properties — this doubles
  the CSS surface and drifts over time.
- Use `direction: rtl` only on specific elements without setting `dir` on the root — the Unicode
  Bidirectional Algorithm needs the page-level direction to be set correctly.

## Edge cases / when the rule does NOT apply

- **Internal/developer tools** with no RTL locale requirement: logical properties are still
  recommended as a habit, but the RTL layout investment is not justified if no RTL locale is in
  scope. Expansion planning still applies if any non-English locale is targeted.
- **Fixed-dimension data visualizations** (charts, graphs): these often require bespoke mirroring
  logic beyond CSS. Flag them for visual QA when RTL locales are added.
- **Logos and brand assets:** do not mirror logos or brand marks for RTL — only directional UI
  chrome icons (arrows, chevrons, list bullets, progress bars).

## See also

- [`./pseudo-localize-in-ci-to-catch-i18n-bugs-early.md`](./pseudo-localize-in-ci-to-catch-i18n-bugs-early.md)
- [`../skills/i18n-foundations-and-icu/SKILL.md`](../skills/i18n-foundations-and-icu/SKILL.md)
  (Steps 5, 7)
- W3C Internationalization: https://www.w3.org/International/
- CSS Logical Properties: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values
- Unicode Bidirectional Algorithm: https://unicode.org/reports/tr9/

## Provenance

Expansion percentages from the IBM Globalization Design Guide (30–50 % for Germanic languages)
and the Apple HIG l10n guidance. CSS logical properties recommendation from W3C CSS Working
Group and the Mozilla MDN l10n guide. RTL design patterns from the Material Design RTL guide and
the Apple Arabic/Hebrew HIG.

---

_Last reviewed: 2026-06-08 by `claude`._
