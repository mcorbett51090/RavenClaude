# Treat color contrast as a constraint, not a preference

**Status:** Absolute rule — contrast ratios are checked at design time against the actual displayed background. A token that fails contrast is a bug, not a taste call.

**Domain:** Accessibility / Color

**Applies to:** `web-design`

---

## Why this exists

Low contrast is the single most common automated-detectable WCAG failure, and it is decided at design time, not in review. WCAG 2.2 SC 1.4.3 (Contrast Minimum, AA) requires **4.5:1 for normal text** and **3:1 for large text (≥ 24px, or ≥ 18.66px bold)**; SC 1.4.11 (Non-text Contrast) requires **3:1 for UI component boundaries, focus rings, and meaningful graphics** [verify-at-build — WCAG ratios]. The trap is measuring against the design-tool canvas instead of the _real_ background: a button label fails over a gradient, a hover state, or an image overlay even when it passed over flat white. Building the palette in `oklch()` makes this tractable — equal lightness looks equally bright across hues, so a contrast-safe ramp is a lightness ramp.

## How to apply

Bake the ratio check into the token scale. Verify every text/background _pair_ that actually co-occurs, including hover/active states and overlays.

```css
@theme {
  /* oklch lightness ramp → predictable, verifiable contrast steps */
  --color-text: oklch(0.22 0.02 250); /* ~13:1 on the surface below — passes AA + AAA */
  --color-text-muted: oklch(0.5 0.02 250); /* verify ≥ 4.5:1 before shipping as body */
  --color-surface: oklch(0.99 0 0);
  --color-link: oklch(0.55 0.18 250); /* check 4.5:1 vs surface AND vs hover bg */
}
```

```html
<!-- Text over imagery: add a scrim so contrast holds over any photo -->
<div class="hero" style="background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url(hero.avif)">
  <h1 style="color: oklch(0.99 0 0)">Readable over any photo</h1>
</div>
```

**Do:**

- Check the ratio against the _displayed_ background — gradients, hover/active states, image overlays included.
- Build color scales in `oklch()` so lightness maps to perceived brightness and contrast steps are predictable.
- Add a scrim/overlay when placing text over photography; never hope the image is dark enough.

**Don't:**

- Treat decorative or "secondary" text as exempt — muted grey body copy is the classic 3.9:1 fail.
- Use color as the _only_ signifier (see SC 1.4.1) — pair every status color with an icon + text.
- Defer contrast to a11y review; by then the palette is locked and the fix is expensive.

## Edge cases / when the rule does NOT apply

- **Disabled controls** and **pure decoration** (a logotype, incidental graphics) are exempt from SC 1.4.3 — but a disabled state still needs to read as disabled.
- **Logotypes** carry a contrast exception, though legibility is still a brand decision.
- **AAA (SC 1.4.6, 7:1)** is a target for body-heavy reading experiences, not a universal floor — AA is the team default; state when you're holding to AAA.

## See also

- [`./visual-design-tokens-not-hardcoded-values.md`](./visual-design-tokens-not-hardcoded-values.md) — contrast lives in the token layer, verified once
- [`./a11y-visible-focus-and-target-size.md`](./a11y-visible-focus-and-target-size.md) — the focus ring needs 3:1 non-text contrast
- [`../knowledge/modern-css-2026.md`](../knowledge/modern-css-2026.md) — `oklch()` for perceptually-uniform, contrast-friendly scales
- [`../agents/visual-designer.md`](../agents/visual-designer.md) (contrast as a constraint), [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md)

## Provenance

From the `visual-designer` opinions ("contrast as a constraint, not a polish item"; "contrast measured against the actual displayed background, including hover/active, gradients, overlays"), the `accessibility-auditor` color section (4.5:1 body / 3:1 large + UI), and the `oklch()` guidance in `modern-css-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
