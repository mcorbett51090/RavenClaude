# Brand assets — drop the raven logo here

**Drop your raven logo file in this folder**, named exactly one of:

| Preferred | Filename | Spec |
|---|---|---|
| ⭐ 1st choice | `raven-logo.svg` | Vector. Any size. **Solid black raven on a transparent background.** |
| 2nd choice | `raven-logo.png` | **≥ 256 × 256 px**, black raven on a **transparent** background (PNG-24 with alpha). |

That's all you need to do. Once the file is here, I'll wire it in.

## Why these specs

- **Black-on-transparent** is the source of truth. The pages tint it per theme with
  CSS (`filter: brightness(0)` → black on the light theme; left as-is / lightened on
  dark mode), the same trick that fixed the white-raven brand mark. A pre-colored
  (white or teal) logo fights that, so ship it **black**.
- **Vector (SVG) is best** because the logo is used at very different sizes — a 28 px
  brand mark **and** the large (~150 px) onboarding graphic that replaces the rocket.
  A small raster pixelates when scaled up; an SVG (or a ≥256 px PNG) stays crisp.
- **Transparent background** so it sits cleanly on the cards/canvas at any size.

## What I'll do once it's here

1. Inline it (SVG inlined directly, or a PNG as a base64 data-URI) so the pages stay
   self-contained / offline-safe — no external asset load, consistent with the rest
   of the marketplace.
2. Replace the **onboarding rocket** on `index.html` with the raven logo.
3. Swap the **house brand-mark** on `index.html` for the raven (so the wordmark
   actually shows a raven), and point the dashboard's brand mark at this same file.
4. Keep the light/dark color handling (black on light, light on dark) and verify the
   freshness + render gates stay green.

## Notes

- This folder lives in the shared design-system assets dir
  (`plugins/ravenclaude-core/dashboard-assets/`) so every surface can reference one
  canonical logo. It's `.prettierignore`d so an exported SVG isn't reformatted.
- If you only have the small 28 px PNG, say so and I'll use it with the brightness
  fix (accepting some softness at the large onboarding size).
