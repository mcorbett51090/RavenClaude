# Measuring text over photographs (2026)

> **Dated 2026-10-27.** The method below was built, run and broken on purpose in the owner's site factory
> (`RavenPower-website-factory` PR #131, `scripts/test/device-matrix.mjs`, the `photo-contrast` probe). Every number
> marked **[observed]** was measured there on real builds. WCAG facts were re-read on 2026-10-27 from the W3C's
> *Understanding SC 1.4.3: Contrast (Minimum)* for WCAG 2.2.
>
> Labels: **[doc]** a W3C page states it · **[observed]** measured in the factory · **[inferred]** a conclusion drawn
> from those · **[unverified]** not confirmed. Backs the [`adaptive-layout`](../skills/adaptive-layout/SKILL.md)
> device matrix, [`accessibility-review`](../skills/accessibility-review/SKILL.md) Pass 5 and the
> [`block-composed-site`](../skills/block-composed-site/SKILL.md) visual pass.

---

## 0. The short version

1. **Text over a photo is a 1.4.3 surface, and nothing that reads hexes can score it.** Contrast is measured "with
   respect to the specified background over which the text is rendered in normal usage", and the W3C lists
   "background images that do not provide sufficient contrast with foreground text" as failure F83 **[doc]**. A
   token checker sees the text colour against the section's `background-color`, which the photo covers. Axe-style
   tools report it as needing review rather than as a pass or a failure **[unverified — training knowledge]**. The
   factory's own render audit reports it as unscorable **[observed]**. Either way, nobody has measured it.
2. **It is where real builds fail.** **[observed]**
   - Two independent agent builds of the same site shipped a 12px eyebrow over a bright hero at 1.8–1.9:1. Each found
     it only by writing its own pixel script.
   - The probe below then found the kit's own CI example at 1.25:1 (eyebrow), 2.54:1 (title) and 2.95:1 (lede) at
     320px.
   - It found a hand-built reference template at 1.24–3.27:1 on its hero, masthead and chapter bands, and a winery
     tile label at 4.37:1.
   - Every one of these sites passed its token-pair contrast check.
3. **Measure composited pixels in a browser, at the 5th-percentile pixel behind each line.** The procedure is §1.
4. **Fix it by anchoring the scrim to the copy, not the photo.** See §2.

## 1. The method: each step and the failure it prevents

| Step | How | Without it |
|---|---|---|
| **Find the lines** | Walk text nodes. Take each line's boxes from `Range.getClientRects()`, so a two-line heading is two boxes, not one rectangle full of gaps. Keep the boxes that overlap an `img`, `video`, `canvas` or `background-image` at least 48px on a side. The element must not contain that media. Skip `svg`, which is icons and marks here. | Scoring a heading's bounding box scores the gaps between lines and the empty end of a short last line |
| **Clip each box** | Intersect it with every ancestor whose `overflow` or `clip`/`clip-path` would cut it | A `.visually-hidden` label's text runs past its 1px box, so you score text nobody can see |
| **Skip what is not painted text** | `aria-hidden`, `hidden` and `inert` subtrees, `visibility: hidden`, and `background-clip: text` (its colour is a background, not a colour) | Findings on things no one reads |
| **Resolve the colour as it paints** | Paint `color` (or `-webkit-text-fill-color`) into a 1×1 canvas and read the 8-bit sRGB back. That handles `oklch()`, `color-mix()` and `color()` alike. Multiply its alpha by every ancestor's `opacity`. | A parser for one colour syntax, wrong on the rest. Text at 60% opacity scored as solid |
| **Hide the glyphs, keep their background** | `:root *, :root *::before, :root *::after { -webkit-text-fill-color: transparent !important; text-decoration-color: transparent !important; caret-color: transparent !important }`. Leave `text-shadow` and the element's own background alone: they sit behind the glyphs and are part of what the text is read against. Then **assert the hide landed** on every candidate. | Glyphs scored against themselves, which reads as high contrast. `:root *` outranks a page's own `* { … !important }` |
| **Capture the viewport, never the document** | `Page.captureScreenshot` without `captureBeyondViewport`. Scroll so the first unscored line sits a quarter of the way down, and score every line fully in the frame. | `captureBeyondViewport` resizes the viewport to the document, so every `svh`-tall hero grows, and the photo crop you are testing is not the one a phone shows **[observed]** |
| **Respect fixed chrome** | If `elementFromPoint` at the line's centre lands in a `fixed`/`sticky` ancestor that is not the line's own, defer the line to another scroll position | Scoring a heading against the sticky header that covers it |
| **Assert the geometry** | Decode the PNG in the page and require capture pixels = viewport × DPR on both axes, or throw | Every sample lands somewhere else, and the readings are still plausible numbers |
| **Score every pixel of every line box** | Composite the text colour at its alpha over each pixel. Linearise with a 256-entry lookup (WCAG's sRGB curve, threshold **0.04045** **[doc]**). Take the WCAG ratio for each pixel. The reading is the **5th-percentile** pixel; report the median beside it. | Mean or median passes a line whose first word sits on a white highlight |
| **Apply the right bar** | 4.5:1, or 3:1 for text at least 24px, or at least 18.66px and bold (18pt and 14pt bold at 1pt = 1.333px; the Understanding doc rounds the bold figure to "approximately 18.5px") **[doc]** | Large display type failed at the body-text bar, or small text passed at the large one |
| **Keep analytics quiet** | `Network.setBlockedURLs` for the tag and beacon hosts during the run | A device matrix sends hundreds of fake pageviews into the owner's analytics |
| **Choose where it runs** | One viewport per device class: the crop changes with the aspect ratio, so 320, a phone in portrait, a phone in landscape, a tablet and a desktop each see a different photo. The light theme only. | Either a 40-row matrix that takes an hour, or one width that misses the crop where it fails |
| **Prove it can fail** | A mutation that sets every text colour to white at 15% opacity, with the run required to report `photo-contrast`. A plain mid-grey is the wrong mutation, because a grey can pass over some photos. | A probe that has never been red, and so proves nothing |

**Cost [observed]:** about a minute for an 8-page site at six viewports, because each line needs its own scroll
position and capture. That is why the factory caps it at 12 captures a page and runs it only in the control and its own
mutation.

**Why the 5th percentile [inferred]:** it fails a line when a bright patch sits behind a fifth of it, and it lets one
specular highlight through. WCAG names no sampling rule for a photograph, so treat the percentile as a heuristic that
the factory's control and mutation hold in place, not as a conformance rule.

## 2. The fix: a scrim anchored to the copy

The failures in §0 had one cause. Each scrim was a gradient sized in percent of the hero. On a phone the copy stands
taller relative to the hero, so the gradient's dark end stopped below the eyebrow **[observed]**. Darkening the whole
photo costs the image without fixing the line that fails. The fix is to make the scrim belong to the text block:

```css
.hero__inner { position: relative; padding-block: var(--space-3xl) var(--space-2xl); }
.hero__inner::before {
  content: ''; position: absolute; z-index: -1;   /* inside the hero's isolated stacking context */
  inset-block: 0; inset-inline: -50vw;           /* full-bleed band behind the copy, wherever it wraps */
  background: linear-gradient(to top,
    color-mix(in srgb, var(--night-deep) 86%, transparent),
    color-mix(in srgb, var(--night-deep) 74%, transparent) calc(100% - var(--space-3xl)),
    transparent);
}
```

- The band starts its fade inside the block's own top padding and is **at least 74% under every line**. That held the
  kit's light inks at AA even over a white pixel **[observed]**. Derive the opacity for your own inks: solve for the
  scrim alpha that keeps the lightest ink at the bar over `#fff`.
- The hero needs `isolation: isolate` and `overflow: hidden`, so that `z-index: -1` stays above the photo and the
  `-50vw` overhang is clipped.
- The same band fixed a masthead and a chapter band. A small caption on a photo tile gets a floor under the caption
  instead of a band.
- A photo can be any photo, because the owner changes it later. The band makes the contrast independent of what the
  photo happens to be, and the probe confirms it on the photo that ships.

## 3. What this does not cover

- **The dark theme.** The factory's probe runs in light only. This plugin's port (`scripts/device_matrix.mjs`) runs it
  in light, dark and both more-contrast themes **[observed, 2026-10-27]**.
- **Forced colours.** The browser paints glyphs in the forced colour whatever `-webkit-text-fill-color` says, so the
  hide cannot land, and its computed-style check still passes **[observed in Chromium, 2026-10-27]**. The method does
  not apply there. Give the copy an opaque `Canvas` backplate in `@media (forced-colors: active)` instead, and check
  that the backplate is there.
- **Reduced motion.** A `0.01ms` transition on every property (a common reduced-motion reset) means the hide has not
  landed in the same tick it was added. Wait two frames before asserting it **[observed]**.
- **Video and motion.** A poster or first frame is what gets scored. A bright later frame is not measured.
- **Text inside the image.** Raster text has no text node, so the probe cannot find it.
- **WebKit.** The probe runs in Chromium. Rendering differences in Safari are not measured **[inferred, not
  measured]**.
- **Conformance.** A green run means "every scored line met its bar at the 5th-percentile pixel in this browser". It is
  not a WCAG conformance statement.

## Sources

- W3C, *Understanding SC 1.4.3: Contrast (Minimum)*, WCAG 2.2, retrieved 2026-10-27. Covers the background "over which
  the text is rendered in normal usage", failure F83 (background images), the 0.04045 threshold (0.03928 before
  May 2021), and the large-text pt and px equivalents.
- `RavenPower-website-factory` PR #131 (merged 2026-10-26): `scripts/test/device-matrix.mjs` (`PHOTO_FIND`,
  `PHOTO_HIDE`, `PHOTO_SAMPLE`, `M-photo-contrast`); `blocks/catalog/hero-full/HeroFull.astro` (the anchored band); and
  `docs/plans/2026-10-26-block-route-gap-analysis.md` §2–§3 (the failures it found and the two builds that hit it
  first).
