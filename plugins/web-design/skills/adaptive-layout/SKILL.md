---
name: adaptive-layout
description: Make a website adapt correctly to desktop, laptop, phone (portrait and landscape), tablet, iPad windows and foldables like iPhone Duo, the way Apple prescribes — one document, content-driven breakpoints, dynamic viewport units, safe areas, touch and input rules — and prove it on a device matrix. Used by frontend-implementer, visual-designer and accessibility-auditor.
---

# Skill: adaptive-layout

**Purpose:** one site that is right on every screen it will meet — a 2560px desktop, a short 1280×720 laptop, an
iPad in a resizable window, a landscape iPhone 368px tall, and an iPhone Duo unfolded to a near-square 669px —
built the way Apple and WebKit prescribe and **verified on a device matrix**, not on two screenshots.
Primary agents: `frontend-implementer` (head, CSS, images), `visual-designer` (tiers, type steps, hero heights),
`accessibility-auditor` (reflow, zoom, target size, input zoom).

**Knowledge it applies:** [`../../knowledge/apple-adaptive-web-2026.md`](../../knowledge/apple-adaptive-web-2026.md)
— Apple/WebKit guidance with sources, apple.com measured at 35 viewports, the iPhone Duo viewport table, the
Viewport Segments and Device Posture support matrix, multitasking widths and the test matrix. Read its §0 and §11
before anything else; the numbered rules there are what this skill enforces.

## When to use

- Building or reviewing any page that must work on phones, tablets and desktops (that is: every page).
- A brief says "make it work on iPad", "landscape is broken", "it zooms when I tap the form", "the hero is cut off
  on iPhone", "support foldables / iPhone Duo / split screen", or "make it adapt like apple.com".
- Before a launch gate: the device matrix in step 7 is the evidence a reviewer should ask for.

Not for: native iOS/iPadOS layout (size classes in UIKit/SwiftUI), a full site pipeline
(`gold-standard-website-pipeline` runs this inside its build and QA gates), or visual craft on one surface
(`interface-craft` — that skill decides how it looks; this one decides that it still works at 382px and 951px).

## The prescription in one line

WebKit, shipping the foldable iPhone Duo (2026-10-23): *"lean into the wisdom of Responsive Web Design … layouts
… that simply work on every sized screen … Avoid UA sniffing to detect devices, and use feature detection
instead."* Everything below is that sentence made specific.

## Procedure

### 1. The head — exactly this, nothing clever

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

- Never `user-scalable=no` and never `maximum-scale` below 2 (WCAG 1.4.4). iOS ignores the lock; Android obeys it.
- **Do not add `viewport-fit=cover` by default.** Without it Safari fills the notch, Dynamic Island and iPhone Duo
  control areas with the page background — right for most sites. WebKit (2026-10-23): *"we see a lot of projects
  that fail to inset all four edges correctly"*. Opt in only for genuine edge-to-edge paint, and then pad every
  fixed bar and gutter with `max(<gutter>, env(safe-area-inset-<edge>))` on **all four** edges (apple.com's
  pattern, measured).
- One HTML document for every device. No `m.` site, no UA branching, no server-side device detection — iPad
  Safari sends a **Mac** user agent, so a UA test is wrong on the most common tablet.
- Icons: an SVG `rel=icon` (Safari 26 uses SVG icons everywhere) plus a 180×180 `apple-touch-icon.png`. In iOS 26
  **every site added to the Home Screen opens as a web app** with no manifest required — the icon is what the customer
  sees. Ship a manifest with `"display": "standalone"` only if you style for `display-mode: standalone`.
- **Toolbar tint (Safari 26+):** Safari extends a solid colour into the browser bars from the page background and from
  fixed or sticky elements at the edges. Set an opaque `html`/`body` background and give edge-fixed bars an opaque
  background, or check a translucent glass bar on a device. Keep `theme-color` with `media` light/dark variants: it costs
  nothing and other browsers use it, but whether Safari 26/27 still reads it is unverified (knowledge file §2).

### 2. Width — content-driven tiers, few of them

- Start fluid: `minmax(0, 1fr)` tracks (a bare `1fr` will not shrink below its content), `max-width: 100%` media,
  `overflow-wrap: anywhere` on columns that hold names, emails and addresses.
- Page-level tiers: **two or three**, placed where the content breaks, written in `em` so user zoom moves them
  (this plugin's house rule; 734px = 45.875em). apple.com uses 734/1068 for layout and type,
  a separate **833/834** for its nav, and nothing visible changes above 1069. Measure your own nav: collapse it at
  the width its links stop fitting, not at a device width.
- **Components use container queries**, not viewport media queries: the same card sits in a 382px phone, a 385px
  iPhone Duo split window and a 600px sidebar.
- Expect continuous widths. iPadOS 26 windows resize freely; Android split screen has no fixed ratios; an
  unfolded iPhone Duo is 669px — a 768px `md` breakpoint gives it the phone layout. Zero horizontal scroll at
  **320px** is the floor (WCAG 1.4.10); nothing should break at 280.
- Body text at least 16px everywhere (apple.com uses 17px on every device and never changes it in a media query);
  type steps per tier rather than `vw`-driven fluid type if the brand wants Apple's restraint — `clamp()` is fine
  for spacing.

### 3. Height — dynamic viewport units, in the right order

```css
.hero { min-height: 92vh; min-height: 92svh; }        /* vh = fallback, svh = fits with the toolbar showing */
.cover-video { min-height: 100vh; min-height: 100lvh; } /* a COVER fills the largest viewport */
.overlay { height: 100vh; height: 100dvh; }            /* full-screen menus track the toolbar */
```

- **`vh` first, dynamic unit second, always.** The last height a browser understands is the one it uses, and the
  build's CSS minifier deletes the earlier duplicate: Lightning CSS turns `min-height:92svh;min-height:92vh` into
  `min-height:92vh` (measured 2026-10-26). A site that wrote the pair backwards ships plain `vh` to everyone.
- Plain `vh` is the **large** viewport on mobile Safari, so a `100vh` section runs under the toolbar.
- Landscape phones are **368–440px tall**. Give the hero a short form (apple.com: 692px at ≥776px of height, 580px
  below) and keep fixed or sticky chrome well under a third of the height.

### 4. Input — touch, hover, keyboard, pencil

- Every control at least **24×24 CSS px**, or clear of its neighbours by WCAG 2.5.8's spacing rule (a 24px circle
  centred on it touches no other target). Inline links in running text are exempt.
- Form text at least **16px** — `input, select, textarea { font-size: max(16px, 1rem); }`. WebKit's source zooms a
  focused control by `16 / fontSize`, so anything smaller zooms the page on focus. Never "fix" it with `maximum-scale`.
- `hover` and `pointer` media features may **add** (reveal gallery arrows, a hover lift); content and navigation
  must work with `hover: none`. An iPad with a trackpad reports hover; the same iPad without one does not.
- Keyboard and focus are unchanged by device: visible focus, logical order, nothing reachable only by hover.

### 5. User settings — respect them, don't guess them

`prefers-reduced-motion`, `prefers-contrast: more`, `prefers-color-scheme` (with `color-scheme: light dark` declared —
Safari never auto-darkens). Give every animation a reduced-motion override. Size type in `rem`/`em` so browser text
zoom and Page Zoom apply — but know that **`rem` does not follow iOS Dynamic Type in Safari** (WebKit bug 260880, open
since 2023); the system-font keywords (`font: -apple-system-body`) do, and are an iOS-only, device-tested enhancement.
Safari has **no `prefers-reduced-transparency`**, so translucent glass needs its own contrast floor. Details: knowledge
file §6.

### 6. Images — art direction by tier, density capped

- `<picture>` with a `<source media>` per tier where the crop must change; `srcset` with `w` descriptors and an
  honest `sizes` where it does not. apple.com caps at **2x** even on 3x phones; so can you.
- AVIF first, then a JPEG/WebP fallback; explicit `width`/`height`; `fetchpriority="high"` on the hero only;
  `loading="lazy"` below the fold.
- Keep the subject in a centred safe zone so tier crops and `object-fit: cover` never cut it.

### 7. Verify on the device matrix — the step that makes the rest true

Render every page at each row below and assert, from the **live layout** (never from source): no element painted
past the viewport edge and no mobile zoom-out (`innerWidth > clientWidth`), every touch target passes 2.5.8, every
text input ≥16px, landscape chrome ≤30% of the height. Then add **±1px around every breakpoint the site's own CSS
declares** — read from the built CSS, which a minifier may have rewritten to range syntax (`(width<=860px)`).

| Class | CSS px (W×H) |
|---|---|
| Reflow floor | 320×568 |
| iPhone portrait | 375×667, 390×844, 402×874, 420×912, 440×956 |
| iPhone landscape | 667×375, 874×402, 956×440 |
| iPhone Duo (WebKit's table, SVH heights) | 382×580 outer, 594×368 outer landscape, 669×867 inner, 951×585 inner landscape, 385×571 split window |
| Android foldable (presets disagree — shapes, not specs) | 344×882 cover, 836×842 open |
| iPad | 756×1158 (mini), 820×1180, 834×1210, 1032×1376, 1376×1032, split 688×1032 and 375×1032 |
| Laptop / desktop | 1280×720 (short), 1280×800, 1470×956, 1920×1080, 2560×1440 |

- **This plugin ships the harness:** [`scripts/device_matrix.mjs`](../../scripts/device_matrix.mjs) runs
  [`scripts/layout-probe.js`](../../scripts/layout-probe.js) over exactly this table, plus ±1px around every
  `@media` width in your CSS and an optional sweep (`--sweep 320:1600:8`). The one-per-class rows also run in dark,
  forced colours and more contrast (light and dark). Desktop rows draw real scrollbars.
  `node scripts/device_matrix.mjs --dir dist --pages /,/menu/ --full` (or `--manifest site.manifest.json`).
  - Its `--self-test` plants every defect the probe knows and requires each one to be reported, and checks
    look-alikes that must not be. Run it once per machine.
  - Use it rather than writing a probe that has never been shown to fail.
- **Text over a photo needs its own probe**, and the harness runs it (`photo-contrast`) at one viewport per class,
  because the photo crop changes with the aspect ratio. It hides the glyphs, captures the viewport (never the full
  document, which grows every `svh` hero), and scores each line at its 5th-percentile composited pixel. The method and
  its pitfalls are in [`text-over-photo-contrast-2026.md`](../../knowledge/text-over-photo-contrast-2026.md); it was
  built in the owner's site factory and ported here, with the factory's mutation that must fire. It cannot run in
  forced colours, where glyphs paint in the forced colour and cannot be hidden: there the copy needs an opaque
  `Canvas` backplate.
- **Chromium is not WebKit.** Emulation sets width, DPR, touch and the viewport tag, but has no Safari toolbar,
  no safe areas and no dynamic viewport. Finish on a real iPhone and iPad, or in the Xcode Device Hub simulator
  (Xcode 27.1+ includes iPhone Duo).

### 8. Foldable enhancement — optional, never a dependency

Plain responsive layout is enough for a marketing site; WebKit says so. Add segment-aware CSS only for content that
is naturally two-pane (gallery and details, menu and dish, map and address):

```css
@media (horizontal-viewport-segments: 2) {
  .duo {
    grid-template-columns: env(viewport-segment-width 0 0, 1fr) env(viewport-segment-width 1 0, 1fr);
    column-gap: calc(env(viewport-segment-left 1 0, 0px) - env(viewport-segment-right 0 0, 0px));
  }
  .duo > * { padding-inline: 1rem; } /* keep text off the crease */
}
```

It is live in Chromium browsers (Chrome/Edge 138+, Samsung Internet) only while a foldable is partly folded, and
**behind a feature flag** in Safari 27.1 on iPhone Duo. `.duo` must start at x=0 for the columns to meet the fold.

## Verification table

| Claim | How to prove it | Pass bar |
|---|---|---|
| Reflows on every device | device matrix, all rows + breakpoint boundaries | 0 overflow findings, no zoom-out |
| Hero fits with the toolbar showing | built CSS: last height declaration per selector | no plain-`vh` height last in its cascade slot |
| Not zoom-locked | built HTML viewport tag | `width=device-width, initial-scale=1`, no lock |
| Safe areas handled (only if `viewport-fit=cover`) | built CSS | `env(safe-area-inset-*)` on all four edges |
| Touch-ready | device matrix target and input checks | 2.5.8 incl. spacing exception; inputs ≥16px |
| Works without hover | matrix rows run with `hover: none, pointer: coarse` | nothing hidden behind hover |
| Real Safari | iPhone/iPad or Device Hub simulator, portrait + landscape + Duo | eyes on it; note what was checked |

## Anti-patterns

- Device detection by user agent, or a separate mobile site.
- `100vh` heroes, and `svh` written **before** `vh` (the minifier then ships only the `vh`).
- `viewport-fit=cover` without all four insets; `user-scalable=no`; `maximum-scale=1`.
- Breakpoints copied from a device list (768/1024) instead of where the content breaks.
- `body { overflow-x: hidden }` as the fix for overflow: it hides the clipped content instead of fitting it, and
  makes a `scrollWidth` check blind. Find the element that overflows.
- 14px form fields; hover-only menus; tap targets packed tighter than 24px.
- Calling a layout verified from two screenshots at 390 and 1440.
