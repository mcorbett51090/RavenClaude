# Honor reduced-motion, forced-colors, and reduced-data preferences

**Status:** Absolute rule — every animation has a no-motion fallback, and the UI survives forced-colors mode. Motion without a `prefers-reduced-motion` fallback is an anti-pattern (house opinion #13).

**Domain:** Accessibility / Preferences

**Applies to:** `web-design`

---

## Why this exists

Animation can trigger vestibular disorders — nausea, dizziness, migraine — for real users, which is why `prefers-reduced-motion` exists and why "print and reduced-motion are not afterthoughts" is a house opinion (#13). Honoring it is cheap (a media query) and the failure is invisible to anyone not affected, so it gets skipped. The adjacent preference, `forced-colors` (Windows High Contrast), overrides the page's colors with a user-chosen palette; UIs that paint backgrounds/borders with `background-image` or rely on color-only cues break in it. These are user *preferences* the platform exposes — respecting them is the same discipline as honoring dark mode, not a special-case bolt-on.

## How to apply

Gate non-essential motion behind `prefers-reduced-motion`, and verify the UI in `forced-colors` mode (use system color keywords / `forced-color-adjust` where needed).

```css
/* Default: a subtle, purposeful transition */
.card { transition: transform 200ms ease-out; }
.card:hover { transform: translateY(-4px); }

/* Reduced motion: remove movement; keep the affordance via a non-motion cue */
@media (prefers-reduced-motion: reduce) {
  .card { transition: none; }
  .card:hover { transform: none; outline: 2px solid var(--color-focus-ring); }
  *,
  *::before,
  *::after { animation-duration: 0.001ms !important; scroll-behavior: auto !important; }
}

/* Forced colors: don't fight the user's palette; ensure borders survive */
@media (forced-colors: active) {
  .btn { border: 1px solid ButtonText; }   /* system color keyword, not a token hex */
}
```

```js
// Gate scripted / View Transitions motion too
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!reduce && document.startViewTransition) document.startViewTransition(update);
else update();
```

**Do:**
- Provide a no-motion fallback for every animation, transition, parallax, and autoplay; gate the View Transitions API on the preference.
- Verify the UI in forced-colors mode; rely on system color keywords and don't convey meaning by color alone.
- Honor `prefers-reduced-data` where relevant (skip heavy autoplay video / decorative downloads).

**Don't:**
- Autoplay video/audio or loop hero animations with no reduced-motion escape (`accessibility-auditor` anti-pattern).
- Paint essential boundaries/icons with `background-image` that vanishes under forced-colors.
- Treat reduced-motion as "turn off all animation everywhere" — essential motion (a loading indicator) can remain, just minimized.

## Edge cases / when the rule does NOT apply

- **Motion that conveys essential meaning** (a progress indicator, a state transition the user needs) can persist in reduced form — the rule is "no *gratuitous* motion," not "frozen UI."
- **Brand hero animation** the client insists on still needs the fallback; animate once on scroll-into-view rather than looping, and respect the preference.
- **forced-colors `none`** is appropriate only for genuinely meaningful color (a syntax-highlighted code block) via `forced-color-adjust` — use sparingly and deliberately.

## See also

- [`./a11y-visible-focus-and-target-size.md`](./a11y-visible-focus-and-target-size.md) — focus must stay visible in forced-colors too
- [`./visual-color-contrast-is-a-constraint.md`](./visual-color-contrast-is-a-constraint.md) — color is never the only signifier
- [`../knowledge/modern-css-2026.md`](../knowledge/modern-css-2026.md) — View Transitions API gated on `prefers-reduced-motion`
- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) (motion/forced-colors), [`../agents/visual-designer.md`](../agents/visual-designer.md) (motion design + reduced-motion fallback)

## Provenance

Distilled from house opinion #13 (reduced-motion not an afterthought), the `accessibility-auditor` motion section + anti-patterns (animations without `prefers-reduced-motion`; autoplay), the `visual-designer` "`prefers-reduced-motion` honored; any motion has a no-motion fallback" opinion, and the View Transitions / `forced-colors` notes in `modern-css-2026.md` + `web-platform-capabilities-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
