# Apple-grade adaptive web: desktop, phone, tablet and foldable (2026)

> **Retrieved 2026-10-26.** Three research passes: Apple and WebKit primary sources (HIG, WebKit blog, Safari release notes,
> WWDC transcripts, WebKit source on `main`, WebKit Bugzilla); apple.com measured in Chromium 153 at 35 viewports × 3 pages
> (105 runs); and dual-screen/foldable specs and support data. The two load-bearing Apple sources for foldables were re-fetched
> and read in full by the author: the Apple Newsroom release *Apple unveils iPhone Duo* (2026-09-09) and WebKit's
> *WebKit Features for Safari 27.1* (Jen Simmons, 2026-10-23).
>
> Labels: **[doc]** an Apple/WebKit/standards page states it · **[observed]** measured or read in source this session ·
> **[inferred]** a conclusion drawn from those · **[unverified]** could not be confirmed. Backs the
> [`adaptive-layout`](../skills/adaptive-layout/SKILL.md) skill. Re-verify anything version-shaped before relying on it.

---

## 0. Apple's prescription, in its own words

Apple does not publish a "web breakpoints" standard. What it publishes is a principle, restated every time a new screen shape
ships:

- **HIG Layout:** *"Determine layout based on size classes, not device type or orientation… a device's orientation and type…
  aren't useful for making layout decisions because they don't provide your app with information about how much space is
  available."* [doc — developer.apple.com/design/human-interface-guidelines/layout, change log 2026-09-09]
- **WebKit, shipping iPhone Duo:** *"you don't need to worry about all these numbers. Instead, lean into the wisdom of
  Responsive Web Design techniques. Create layouts … that simply work on every sized screen from the extremely large to the
  very tiny… Avoid UA sniffing to detect devices, and use feature detection instead."* [doc — webkit.org/blog/18486]
- **HIG, Designing for iPhone Duo:** *"Build your app to resize… Avoid fixed widths and display-specific dependencies."*
  *"Avoid extreme layout changes as people fold the device."* *"In a grid-style layout, prefer an even number of columns."*
  [doc — HIG page added 2026-09-09]

Translation for the web [inferred]: size classes → content-driven breakpoints plus container queries; safe areas →
`env(safe-area-inset-*)`; readable width → `max-inline-size` around 60–75ch; device sizes → **test points, never
breakpoints**.

## 1. The screens a site meets (CSS px)

The HIG's device-specifications table is **gone**: its change log still mentions "Added specifications for iPhone 17…" (2025)
but the page body fetched 2026-10-26 has no specifications section, and points to Apple Design Resources and Xcode's Device
Hub instead [observed]. Sizes below are from Apple spec pages (pixels [doc]) divided by the HIG scale factors (points
[inferred]).

| Device | CSS px, portrait | Notes |
|---|---|---|
| iPhone 17e | 390×844 | @3x |
| iPhone 17 / 18 Pro | 402×874 | @3x |
| iPhone Air | 420×912 | @3x |
| iPhone 18 Pro Max | 440×956 | @3x |
| **iPhone Duo** outer / inner | 382×580 / 669×867 (svh) | WebKit's own table, §8 |
| iPad (A16) / iPad Air 11" | 820×1180 | @2x |
| iPad Pro 11" (M5) | 834×1210 | @2x |
| iPad Air 13" | 1024×1366 | @2x |
| iPad Pro 13" (M5) | 1032×1376 | @2x |
| iPad mini (A20 Pro) | 756×1158 | @2x; older mini 744×1133 |
| Mac | depends on the scaled-resolution setting | [unverified]; apple.com was measured at 1280–2560 |

**Widths are continuous now.** iPadOS 26 windows resize freely from any corner and Apple publishes **no minimum Safari window
width** [doc: HIG Windows; Apple Support "Multitask on iPad" 2026-09-14; observed: none found]; iPadOS 26.2+ adds a Slide Over
window [doc]; Android split screen has no fixed ratios [doc]; Windows Snap apps should support ≤500, preferably ≤330 effective
px [doc]. Assume any width from about 320 up [inferred], with **320 as the hard floor** (WCAG 2.2 SC 1.4.10) and 280 as a
stress test [inferred].

**Heights are short more often than designers think:** landscape iPhones are 368–440px tall, iPhone Duo outer landscape is
368 (svh) [doc], Galaxy Flip landscape about 308 [doc — Playwright descriptor].

## 2. The head

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">   <!-- 180×180 PNG -->
<meta name="theme-color" content="#f6f1e7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#211d18" media="(prefers-color-scheme: dark)">
```

- **Viewport tag.** WebKit parses `width`, `height`, `initial-scale`, `minimum-scale`, `maximum-scale`, `user-scalable`,
  `shrink-to-fit`, `viewport-fit` and `interactive-widget`; `minimal-ui` is ignored [observed: WebKit
  `ViewportArguments.cpp`]. apple.com ships `width=device-width, initial-scale=1, viewport-fit=cover` on all three pages
  measured [observed].
- **Zoom.** iOS has ignored `user-scalable`, `minimum-scale` and `maximum-scale` for pinch since iOS 10 [doc:
  webkit.org/blog/7367] — but `maximum-scale=1` still suppresses the focus zoom and other browsers may honour the lock
  [observed in source; non-Apple behaviour unverified]. Never ship a zoom lock (WCAG 1.4.4).
- **`viewport-fit=cover` — default OFF for a small-business site.** `auto` insets the page; `cover` lays it out under the
  notch and Dynamic Island and requires `env(safe-area-inset-*)` padding [doc: webkit.org/blog/7929]. WebKit, 2026-10-23:
  *"we see a lot of projects that fail to inset all four edges correctly"* [doc]. On iPhone Duo's outer display Safari does
  not draw content behind the side controls; it *"extends its background color to fill the space"* [doc]. If you opt in, use
  `max(<gutter>, env(safe-area-inset-<edge>))` on every edge — apple.com pads nav and footer sides with
  `max(22px, env(safe-area-inset-left))` and the footer bottom with `max(11px, env(safe-area-inset-bottom))` [observed].
- **Toolbar tint (Safari 26+).** No release note documents it, but an Apple WebKit engineer explains on Bugzilla 301756
  (2025-11-07) that Safari extends a solid colour into the bar area when a **fixed or sticky element sits at an edge** next to
  the browser chrome, to avoid a gap [doc]; the 27.1 post confirms Safari extends the page background [doc]. So: set an
  opaque `background-color` on `html`/`body`; give edge-fixed headers and footers an opaque background you are happy to see
  extended; test translucent `backdrop-filter` bars at the edges on a device [inferred]. Keep `theme-color` with `media`
  variants — it is never formally deprecated, Safari 15–18 and other browsers use it, and it costs nothing; whether it still
  does anything in Safari 26/27 is **unverified** (WWDC21 told sites to use it; developer reports say it has no effect).
- **Home Screen (iOS/iPadOS 26).** *"By default, every website added to the Home Screen opens as a web app"*; *"zero
  requirements for 'installability'"*; manifest icons are used if defined; SVG icons are supported *"everyplace there are
  icons"* [doc: webkit.org/blog/17333]. Without a manifest, `display-mode` reports `browser` [observed in WebKit source], so
  `@media (display-mode: standalone)` may not match in such a web app — ship a manifest with `"display": "standalone"` if you
  style for it [inferred].
- **apple.com itself** ships no `theme-color`, no manifest and no icon `<link>` tags; it relies on `/favicon.ico` and a
  152×152 `/apple-touch-icon.png` at the root, and has no dark mode [observed]. Do not copy the missing dark mode.
- **One document, no sniffing.** apple.com serves byte-identical HTML to Mac and iPhone user agents, with `Vary:
  Accept-Encoding` only [observed]. iPad Safari presents itself as a Mac (*"iPad will now present itself to websites as a
  Mac"*, WWDC19) [doc], iOS/iPadOS 26 report a **frozen OS version** in the UA [doc: Safari 26 release notes], and WebKit can
  report a desktop pointing device and `maxTouchPoints` 0 in desktop mode [observed in source]. No user-agent, touch-point or
  pointer test identifies an iPad.

## 3. Width: tiers, nav threshold, containers

**apple.com, measured** [observed, Chromium 153, 2026-10-26]:

| Tier | Width | Page h1 / tile headline | Content column |
|---|---|---|---|
| Phone | ≤734 | 48 / 32 px | 87.5% (20–27px gutters), **capped at 420px** from 481–734 |
| Tablet | 735–1068 | 64 / 48 px | 87.5% |
| Desktop | ≥1069 | 80 / 56 px | 87.5%, max 1260px |

- **Nothing visible changes above 1069**: 1440 and 1441 rendered identically; the CSS's `min-width:1441px` only drives a grid
  utility tier [observed].
- **The nav has its own threshold:** menu button at ≤833, 14 links at ≥834, so landscape phones at 852 and 956 get the full
  desktop nav, and iPad mini/Air portrait get the menu [observed].
- **Type steps per tier; body text never changes:** 17px / 25px line-height on every device, no `vw` font sizes, `clamp()`
  only on padding; display line-height = font-size + 4px [observed]. Card captions drop to 14px on phones — keep running text
  at **16px or more** on a small-business site anyway (house rule).
- Imagery is full-bleed with a 12px gutter grid (one column ≤734, two at ≥735, no max-width); text inside tiles obeys the
  column cap [observed].

**Rules** [inferred]: two or three tiers placed where the content breaks, in `em` (user zoom moves them); a nav threshold
measured from your own links; container queries for components (Safari since 16.0 [doc]); `minmax(0, 1fr)` grid tracks — a
bare `1fr` is `minmax(auto, 1fr)` and will not shrink below its content (it overflowed a real footer on an 874px landscape
iPhone, measured in the owner's factory 2026-10-26). An unfolded phone (669–954px, near-square) lands in the "tablet" band,
so a 768px `md` breakpoint hands an iPhone Duo's 669px inner screen the phone layout.

## 4. Height: dynamic viewport units, and the minifier trap

- `svh` = smallest viewport (toolbars showing), `lvh` = largest (toolbars retracted), `dvh` = tracks the toolbar as it moves;
  shipped in Safari 15.4 (2022) [doc: webkit.org/blog/12445]. **Plain `vh` is the large viewport** on mobile Safari, so a
  `100vh` section runs under the toolbar that is showing. The gap on iPhone Duo is 36–38px (580 svh vs 618 lvh) [doc].
- Write the **`vh` fallback first, the dynamic unit second**: `min-height: 92vh; min-height: 92svh;`. The last declaration
  the browser understands wins — and the build's CSS minifier keeps only the last one: Lightning CSS turns
  `.hero{min-height:92svh;min-height:92vh}` into `.hero{min-height:92vh}` [observed 2026-10-26]. The owner's two reference
  templates shipped exactly that on every hero and masthead; a source grep for `svh` found it "present".
- `lvh` for a cover background or video (it must fill the largest viewport); `dvh` for full-screen overlays only, with a `vh`
  fallback — that is apple.com's sole use (its nav flyout, `@supports (height:100dvh)`) [observed].
- **Height is a layout input too.** apple.com's homepage hero is 692px tall only when the viewport is ≥776px tall, 580px
  below, with a different image crop [observed]. Design a short hero form; keep fixed or sticky chrome well under a third of
  a 368–440px landscape height.
- Keyboard: by default the iOS keyboard overlays the page and shrinks only the visual viewport; use
  `visualViewport.height` and its `resize` event for UI that must stay above it [inferred from Safari 13 notes + source].
  Whether `dvh` reacts to the keyboard is **unverified**.

## 5. Input: touch, hover, pencil, gaze

- **Form text ≥16px.** No Apple document states it, but WebKit source does: `_zoomToFocusRect` computes
  `scale = 16 / fontSize`, so a control whose used font size is ≥16px is not zoomed on focus [observed:
  `WKWebViewIOS.mm`]. Use `font-size: max(16px, 1rem)` on `input, select, textarea` — never `maximum-scale` [inferred].
- **Targets ≥24×24 CSS px** or clear of neighbours by WCAG 2.5.8's spacing exception.
- **Hover is an enhancement.** WebKit (Safari 16.1, Pencil hover): *"structuring code using feature detection, instead of
  device or UA detection, helps future-proof websites"* [doc]. `hover`/`pointer` read the primary device; `any-hover`/
  `any-pointer` read all of them, so an iPad with a trackpad matches `(any-pointer: fine)` while its primary pointer is coarse
  [observed in source + inferred]. HIG Apple Pencil: *"Avoid using hover to initiate an action."* [doc]
- **visionOS Safari:** *"The pointer is coarse and doesn't support hovering"*; looking at an element does not trigger
  `:hover`; the system highlights links, buttons, form controls and anything with `cursor: pointer`, following
  `border-radius` [doc: WWDC23 "Meet Safari for spatial computing"]. Give clickable non-buttons `cursor: pointer`.

## 6. User settings

- **Dynamic Type does not reach `rem` in Safari.** WebKit bug 260880 ("WebKit does not respect system font size for rem
  units") has been open since 2023-08-29 [observed]; WebKit has no position on `env(preferred-text-scale)` or a `text-scale`
  meta [observed]. The iOS opt-in is the system font keywords: `font: -apple-system-body` (plus `-headline`, `-caption1`…),
  which follow Dynamic Type [doc: webkit.org/blog/3709]. A root-level opt-in (`html { font: -apple-system-body }` inside
  `@supports`) changes the font family too and resolves differently on macOS, which has no Dynamic Type [doc: HIG
  Typography] — treat it as an iOS-only, device-tested enhancement, not a default [inferred]. Everyone else gets Page Zoom
  and text zoom; size in `rem`/`em` so those work.
- HIG Typography: iOS default body text **17pt**, minimum 11pt; Dynamic Type Large (default) 17 → AX5 53 [doc].
- Supported in WebKit: `prefers-color-scheme`, `prefers-contrast` (use `more`), `prefers-reduced-motion` (reflects iOS
  Reduce Motion), `inverted-colors`, `forced-colors`, `dynamic-range`, `color-gamut` [observed in source].
- **Not supported:** `prefers-reduced-transparency` and `prefers-reduced-data` [observed] — so Liquid-Glass-style
  translucency needs its own contrast floor, not a media query. Unprefixed `text-size-adjust` is not a WebKit property; only
  `-webkit-text-size-adjust` (apple.com sets it to 100%) [observed].
- Safari does not auto-darken: opt in with `color-scheme: light dark` or `<meta name="color-scheme">` [doc:
  webkit.org/blog/8840]. Safari 27.0 added `light-dark()` with `<image>` values [doc].
- HDR images and `dynamic-range-limit` arrived in Safari 26.0; *"the browser will simply map the HDR contents to the SDR
  range, so no fallbacks are needed"* [doc: WWDC25].

## 7. Images

- **apple.com** [observed]: `<picture>` with `<source media>` per tier and **`x` descriptors only** (no `sizes`, no `w`);
  three crops (small/medium/large) at 1x and 2x, **never 3x** — DPR-3 phones get `_2x`; JPEG/PNG only with no format
  negotiation; `width`/`height` on `<source>` on the newest page; one `fetchpriority="high"` hero; JS lazy-loading. Its
  desktop hero canvas is 3008 CSS px wide, so at 1280px 57% of a 403 KB image is off-screen.
- **Use instead** [inferred from the above + doc]: `<picture>` art direction only where the crop changes, otherwise `srcset`
  with `w` descriptors and an honest `sizes` (Safari 26.4 accepts `min()`/`max()`/`clamp()` in `sizes` [doc]; Safari 27.0
  adds `sizes="auto"` with `loading="lazy"` [doc]); AVIF → WebP → JPEG (AVIF since Safari 16, JPEG XL and HEIC since 17
  [doc]); cap density at 2x; explicit `width`/`height`; native `loading="lazy"` below the fold; subject in a centred safe
  zone so tier crops and `object-fit: cover` never cut it.

## 8. Foldables: iPhone Duo and the rest

**iPhone Duo** — announced 2026-09-09, on sale 2026-10-23, book-style fold, outer 5.4" and inner 7.6" with the same aspect
ratio, from $1,999 [doc: Apple Newsroom]. Safari 27.1 *"with the same WebKit engine and the same web technologies as every
other iPhone"* [doc]. Viewports, from WebKit's post [doc]:

| Configuration | Width | svh | lvh |
|---|---|---|---|
| Outer, portrait | 382 | 580 | 618 |
| Outer, landscape | 594 | 368 | 406 |
| Inner, portrait (one tab) | 669 | 867 | 902 |
| Inner, landscape (one tab) | 951 | 585 | 620 |
| Inner, two windows side by side (each) | 385 | 571 | 609 |

The outer display's controls move to the side and Safari fills that strip with the page background [doc]. Partly folded like
a book, Safari shows PDFs as two pages [doc]. Test in the **Xcode 27.1 Device Hub** simulator [doc].

**Segment and posture APIs** [doc unless marked]:

| API | Chromium | Safari | Firefox |
|---|---|---|---|
| Viewport Segments (`horizontal-/vertical-viewport-segments`, `env(viewport-segment-*)`, `window.viewport.segments`) | Chrome/Edge 138, Samsung Internet 30, Opera 122 | **27.1 on iPhone Duo, behind a feature flag** | none; no Mozilla position |
| Device Posture (`device-posture: folded \| continuous`, `navigator.devicePosture`) | Chrome/Edge 132, Samsung Internet | **27.1 on iPhone Duo, behind a feature flag** | none |

Modern foldables are one continuous screen: the segment media features are true **only while partly folded** (flat open
reports one segment) [doc]. Surface Duo is end of life (last update 2024-10-08) [doc]. Android foldable CSS sizes disagree
between tools — DevTools gives Galaxy Z Fold 6 744×860 unfolded, Playwright 928×1004 — so measure on a device before trusting
a number [observed].

**Progressive enhancement, only for naturally two-pane content** (gallery and details, menu and dish, map and address)
[observed: verified in headless Chromium with emulated folds]:

```css
.duo { display: grid; gap: 1.5rem; grid-template-columns: 1fr; }
@media (min-width: 40rem) { .duo { grid-template-columns: 1fr 1fr; } }
@media (horizontal-viewport-segments: 2) {   /* book posture; false everywhere else */
  .duo {
    grid-template-columns: env(viewport-segment-width 0 0, 1fr) env(viewport-segment-width 1 0, 1fr);
    column-gap: calc(env(viewport-segment-left 1 0, 0px) - env(viewport-segment-right 0 0, 0px)); /* hinge, 0 on one screen */
  }
  .duo > * { padding-inline: 1rem; }        /* keep text off the crease */
}
```

`.duo` must start at x=0 with no outer padding for the columns to meet the fold. Stacked (laptop-posture) segments do not stay
aligned on a scrolling page, because `env()` values are viewport coordinates [inferred]. Re-read segments on resize and on
posture change; never read the width once in JS — folding resizes the page live.

## 9. Testing

| Purpose | CSS px (W×H) |
|---|---|
| Reflow floor / stress | 320×568 / 280×653 |
| iPhone portrait | 375×667, 390×844, 402×874, 420×912, 440×956 |
| iPhone landscape | 667×375, 874×402, 956×440 |
| iPhone Duo (svh heights) | 382×580, 594×368, 669×867, 951×585, 385×571 |
| Android foldable | 344×882 (Fold 5 cover), 836×842 (Pixel Fold open) |
| iPad | 756×1158, 820×1180, 834×1210, 1032×1376, 1376×1032; split ≈688 and ≈375 wide |
| Laptop / desktop | 1280×720, 1280×800, 1470×956, 1920×1080, 2560×1440 |
| Boundaries | ±1px around every breakpoint in the site's **built** CSS |

- **Read breakpoints from the built CSS, in both syntaxes.** Lightning CSS rewrites `(max-width: 860px)` to range syntax
  `(width<=860px)`; a boundary parser that knew only the old form read zero breakpoints from two real sites [observed].
- **Assert from the live layout:** no element painted past the viewport edge (and no mobile zoom-out:
  `innerWidth > documentElement.clientWidth` means the browser shrank the page to fit overflowing content — 909px of content
  on an 874px screen, measured); targets by WCAG 2.5.8 including its spacing exception; text inputs ≥16px; landscape chrome
  share. `body { overflow-x: hidden }` hides overflow from a `scrollWidth` check, so look for painted elements, not scroll
  width.
- **Prove the harness can fail:** a control run must be clean, then each planted defect (a 2000px block, squeezed nav links,
  14px inputs, a 60vh fixed header) must be reported. The owner's factory ships this as `scripts/test/device-matrix.mjs`.
- **Chromium is not WebKit.** Emulation sets width, DPR, touch, `hover`/`pointer` and honours the viewport tag (`mobile:
  true`), but `env(safe-area-inset-*)` reads 0, `100vh == 100dvh`, and there is no collapsing toolbar [observed]. Playwright
  WebKit was not installed in this environment [observed]. Finish on a real iPhone/iPad or the Device Hub simulator.
- Fold emulation: Chrome DevTools has a posture and dual-screen toggle; with Playwright, the CDP fold override only works with
  `viewport: null` (or `Emulation.setDeviceMetricsOverride` with `displayFeature`) and is lost on reload [observed].

## 10. WebKit feature status for adaptive layout

| Feature | Safari | Source |
|---|---|---|
| Container queries | 16.0 | [doc] webkit.org/blog/13152 |
| `:has()` | 15.4 | [doc] /12445 |
| `dvh`/`svh`/`lvh` | 15.4 | [doc] /12445 |
| Subgrid | 16.0 | [doc] /13152 |
| `@scope` | 17.4 | [doc] /15063 |
| View transitions | same-document 18.0, cross-document 18.2 | [doc] |
| Anchor positioning | 26.0 | [doc] /17333 |
| Grid Lanes (masonry) | 26.4 | [doc] /17862 |
| `sizes` with `min()`/`max()`/`clamp()` | 26.4 | [doc] |
| `sizes="auto"` | 27.0 | [doc] /18325 |
| Viewport Segments / Device Posture | 27.1, iPhone Duo, behind flags | [doc] /18486 |
| `prefers-reduced-transparency`, unprefixed `text-size-adjust` | not implemented | [observed] WebKit source |

## 11. Rules

1. One HTML document for every device; feature detection, never UA, touch-point or pointer sniffing. (§0, §2)
2. `<meta name="viewport" content="width=device-width, initial-scale=1">`; no zoom lock. (§2)
3. `viewport-fit=cover` only for real edge-to-edge paint, and then safe-area insets on all four edges. (§2)
4. Opaque `html`/`body` background; opaque or device-tested edge-fixed bars; keep `theme-color` with `media`. (§2)
5. Two or three content-driven tiers in `em`; a separately measured nav threshold; container queries for components;
   `minmax(0, 1fr)` tracks. (§3)
6. Body text constant at 16–17px; type steps per tier. (§3)
7. Heights: `vh` first, then `svh` / `lvh` (cover) / `dvh` (overlay). Check the **built** CSS. (§4)
8. A short hero form and modest fixed chrome for 368–440px landscape heights. (§4)
9. Form text ≥16px (`max(16px, 1rem)`); targets ≥24px or spaced per 2.5.8; hover only adds. (§5)
10. Respect reduced motion, contrast and colour scheme; do not rely on `prefers-reduced-transparency` in Safari; know that
    `rem` ignores iOS Dynamic Type. (§6)
11. `<picture>`/`srcset`, AVIF → WebP → JPEG, density ≤2x, explicit dimensions, one high-priority hero. (§7)
12. Foldables get plain responsive layout; segment-aware CSS only as progressive enhancement for two-pane content. (§8)
13. Verify on the device matrix with breakpoint boundaries and a harness proven to fail; finish on real Safari. (§9)

## 12. Conflicts and unknowns

- **`theme-color`:** WWDC21 recommends it; Safari 26's tint is described by an Apple engineer as a background extension
  driven by edge-fixed elements, without mentioning it; developer reports say it has no effect; no Apple document deprecates
  it. Superseded in practice, never withdrawn.
- **iPhone Duo controls:** HIG says the system puts toolbars and tab bars on the side of the outer display; WebKit says
  Safari's tab bar is at the bottom by default and *"iOS moves controls to the side"*. Possibly both (system controls aside,
  Safari's bar at the bottom) [inferred].
- **HIG device table:** the change log records adding iPhone 17 specifications in 2025; the page has none today.
- **Android fold sizes:** DevTools and Playwright presets disagree; Playwright's "Galaxy Z Fold 7 Cover" equals its Flip 7
  main screen (probably a data error) [inferred].
- **Unknown:** minimum Safari window width on iPadOS 26 and macOS; iPhone Duo inner `devicePixelRatio` (pixel ratio ≈2.81,
  unpublished); first Safari release with `interactive-widget`; whether `dvh` reacts to the keyboard; whether
  `apple-mobile-web-app-status-bar-style` still applies in iOS 26; `display-mode` in a manifest-less iOS 26 web app; how
  web-app icons render in tinted or clear Home Screen appearances.

## Sources (retrieved 2026-10-26)

- Apple: HIG Layout, Windows, Multitasking, Typography, Images, Designing for iPhone Duo (developer.apple.com/design/human-interface-guidelines/…);
  Apple Newsroom *Apple unveils iPhone Duo* (apple.com/newsroom/2026/09/apple-unveils-iphone-duo/); apple.com spec pages;
  Apple Support "Multitask on iPad" (support.apple.com/en-us/125309); Safari release notes 13–27.x; WWDC19 203, WWDC21 10029,
  WWDC23 10122 and 10279, WWDC25 233 and 282, WWDC26 204.
- WebKit: blog posts 3709, 7367, 7929, 8840, 12445, 13152, 13399, 14445, 15063, 16929, 17333, 17862, 18325, 18486, 18515;
  Bugzilla 260880, 300965, 301756, 305546; source on `main` (`ViewportArguments.cpp`, `WKWebViewIOS.mm`,
  `MediaQueryFeatures.cpp`, `CSSProperties.json`, `UnifiedWebPreferences.yaml`); standards-positions summary.
- Standards and others: W3C WCAG 2.2 Understanding 1.4.10 and 2.5.8; CSS Viewport / Media Queries 5 / css-env drafts;
  Chrome and Edge platform status for Viewport Segments and Device Posture; MDN BCD; Microsoft dual-screen guidance; Android
  window size classes and multi-window docs; Chrome DevTools `EmulatedDevices.ts`; Playwright device descriptors.
- Measured: apple.com `/`, `/iphone/`, `/ipad/` (HTML, CSS, 105 Chromium renders); the owner's factory templates and block
  sites (built CSS, Lightning CSS behaviour, a device-matrix run of 440+ page×viewport states per pair of sites).
