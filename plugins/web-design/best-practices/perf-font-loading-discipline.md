# Load web fonts with discipline — subset, preload critical, control the swap

**Status:** Pattern — strong default. Web fonts are the #1 perf killer; treat every font as a budgeted asset with a deliberate loading strategy.

**Domain:** Performance / Fonts

**Applies to:** `web-design`

---

## Why this exists

Web fonts block text rendering and shift layout when they swap in, hitting both LCP (text painted late) and CLS (reflow when the metrics change). The `web-architect` and `performance-engineer` both flag fonts as the top performance risk, and the team default is **one root font stack + two display fonts max** (3+ web fonts loaded is an anti-pattern). The two failure modes are loading too many faces and loading them without controlling the swap — a flash of invisible text (FOIT) on a critical font, or a layout-shifting flash of unstyled text (FOUT) on a display font.

## How to apply

Self-host and `preload` the critical text font, subset to the characters actually used, and pick `font-display` by the font's role. Match fallback metrics so the swap doesn't reflow.

```html
<!-- Critical body font: preload so text paints early; swap to avoid invisible text -->
<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin />
```

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-var.woff2") format("woff2-variations");
  font-weight: 100 900;            /* one variable font covers the weight palette */
  font-display: swap;              /* body text: show fallback, swap when ready */
}
@font-face {
  font-family: "Display";
  src: url("/fonts/display.woff2") format("woff2");
  font-display: optional;          /* non-critical heading font: no swap, no CLS */
  size-adjust: 100%;               /* tune so the fallback matches the web-font box */
}
:root { --font-body: "Inter", system-ui, sans-serif; }
```

**Do:**
- `preload` only the critical (above-the-fold text) font; subset it to the glyphs you ship.
- Prefer one **variable** font over many static weight files; serve `woff2`.
- Use `font-display: swap` for critical text and `optional` for decorative display faces; tune `size-adjust`/`ascent-override` so the fallback matches.

**Don't:**
- Load 3+ web fonts, or a display font for one heading nobody reads (`visual-designer` flags this).
- Pull fonts from a third-party origin in the render path without `preconnect` — that's an extra blocking round-trip and a privacy cost.
- Leave `font-display` unset (the default is FOIT-prone `block` behavior).

## Edge cases / when the rule does NOT apply

- **System font stack** (`system-ui, sans-serif`) needs none of this — zero bytes, zero swap. Reach for it when the brand allows.
- **Icon fonts** are largely obsolete — prefer inline SVG (better a11y, themeable, no FOIT). If a legacy icon font remains, subset it hard.
- **Brand-critical headline font** that must be exact may justify `swap` over `optional` despite a small CLS risk — reserve space with `size-adjust` and note the trade-off.

## See also

- [`./perf-reserve-space-to-prevent-cls.md`](./perf-reserve-space-to-prevent-cls.md) — font swap is a top CLS source
- [`./perf-protect-lcp-with-preload-and-priority.md`](./perf-protect-lcp-with-preload-and-priority.md) — when the LCP is text, the font is on the critical path
- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — self-host / preload / `font-display` / subset
- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) (font optimization), [`../agents/web-architect.md`](../agents/web-architect.md) (one stack, two display fonts)

## Provenance

Distilled from the `performance-engineer` font-optimization surface (subset, preload, `font-display: swap`/`optional`, variable fonts, system fallback), the `web-architect`/`visual-designer` "two display fonts max" opinion, and the fonts section of `web-platform-capabilities-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
