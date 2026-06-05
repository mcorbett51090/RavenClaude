# Implement Dark Mode via prefers-color-scheme, Not a Toggle-Only Class

**Status:** Pattern
**Domain:** Web Design — Theming / accessibility
**Applies to:** `web-design`

---

## Why this exists

A user who has set their operating system to dark mode has done so because they prefer it — for eye strain, migraine sensitivity, battery conservation, or readability. A site that ignores `prefers-color-scheme: dark` and forces them into a light interface is overriding an explicit system preference. The `prefers-reduced-motion` and `forced-colors` rules in this plugin extend to the color-scheme preference: the design must respond to the media query, not only to a user-toggled JS class. Relying solely on a toggle class (`.dark { … }`) means users who haven't explicitly found and toggled the switch are served the wrong mode; relying solely on the media query means users who want to override their system preference cannot. The correct design does both.

## How to apply

**Two-layer approach:**

**Layer 1 — Media query (system preference, no JS required):**

```css
:root {
  --bg: #ffffff;
  --text: #111827;
  --surface: #f9fafb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111827;
    --text: #f9fafb;
    --surface: #1f2937;
  }
}
```

**Layer 2 — Class override (user toggle stored in localStorage):**

```css
/* Override the media query when the user explicitly toggles */
:root[data-theme="light"] {
  --bg: #ffffff;
  --text: #111827;
  --surface: #f9fafb;
}

:root[data-theme="dark"] {
  --bg: #111827;
  --text: #f9fafb;
  --surface: #1f2937;
}
```

```javascript
// On load: restore stored preference before first paint
const stored = localStorage.getItem('theme');
if (stored) document.documentElement.setAttribute('data-theme', stored);
```

**Checklist:**
- [ ] `prefers-color-scheme: dark` redefines all semantic color tokens.
- [ ] All images and icons that are legible on white are checked for legibility on dark backgrounds (SVGs using `currentColor` adapt automatically; JPEGs/PNGs may need a dark-mode variant or a light overlay).
- [ ] The `<meta name="color-scheme" content="light dark">` meta tag signals to the browser's default UI (scrollbars, form controls) that both modes are supported.
- [ ] A user-controlled toggle stores the choice in `localStorage` and applies the `data-theme` attribute before first paint to prevent a flash of the wrong theme.

**Do:**
- Include `<meta name="color-scheme" content="light dark">` in the `<head>` so native browser chrome also adapts.
- Test both modes in DevTools (Rendering panel → Emulate CSS media feature: prefers-color-scheme).
- Verify contrast ratios in dark mode — light-mode token values may not meet WCAG AA at dark-mode backgrounds.

**Don't:**
- Implement dark mode only via a JS-toggled class without a media query fallback — users with JS disabled or with slow JS load will see the wrong mode.
- Invert colors with `filter: invert(1)` as a dark mode shortcut — this inverts images, video, and icons incorrectly.
- Use `!important` inside the dark mode override layer — it creates a specificity debt that is painful to unwind.

## Edge cases / when the rule does NOT apply

- **Design systems where `prefers-color-scheme` is handled by the component library** (e.g. Fluent v9's `webDarkTheme`): the media query is surfaced through the library's theme mechanism; implement through `createDarkTheme` and the FluentProvider, not through raw CSS media queries.
- **Pages that are intentionally always dark** (a video player UI, a cinema ticketing site): declare `<meta name="color-scheme" content="dark">` only and skip the media query — but document the design decision.

## See also

- [`../agents/visual-designer.md`](../agents/visual-designer.md) — defines the dark-mode token overrides
- [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) — implements the media query and toggle
- [`./css-custom-properties-bridge-tokens-to-components.md`](./css-custom-properties-bridge-tokens-to-components.md) — the custom-property layer that makes dark-mode token overrides possible without touching component CSS

## Provenance

Codifies house opinion #4 ("Design tokens, not hardcoded values") and the forced-colors/reduced-motion house opinion (#13) applied to color-scheme preference. CSS `prefers-color-scheme` media feature: W3C CSS Media Queries Level 5; MDN Web Docs. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
