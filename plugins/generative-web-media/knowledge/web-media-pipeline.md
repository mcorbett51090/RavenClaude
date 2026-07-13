# Web Media Pipeline — from raw asset to production markup

> How `web-asset-pipeline-engineer` turns a generated asset into a production web asset. The web integration is the differentiator: a generator emits a large raw file; the web needs responsive, next-gen-format, CLS/LCP-safe delivery. **Never ship a raw image.**
>
> _Last reviewed: 2026-07-13 by `claude`. Web-platform mechanics are durable; specific CDN feature/pricing details are `[verify-at-use]`. Sources cited inline._

---

## 1. The image contract (AVIF-first)

Every production image emits, via `<picture>`:

- **AVIF primary → WebP fallback → JPEG (or PNG for alpha) safety net.** Order matters: the browser picks the first supported `<source>`.
- **3–5 responsive widths** with a `srcset` + `sizes` so the browser downloads the right resolution.
- **Explicit `width` and `height`** (or an aspect-ratio box) on the `<img>` — this reserves layout space and prevents **Cumulative Layout Shift (CLS)**.
- True vector content (logo, icon, line art) ships as **SVG**, not a raster pipeline.

The runnable emitter is [`../scripts/web-optimize/optimize-image.mjs`](../scripts/web-optimize/optimize-image.mjs) (Node + Sharp via `npx`); the markup shape is [`../templates/picture-element-snippet.html`](../templates/picture-element-snippet.html).

> **LOUD-SKIP discipline.** If Node/Sharp is absent (offline / no-node host), the optimizer prints its prerequisite and exits **loudly** — "THIS IS NOT A PASS" — and the pipeline degrades to guidance-only. The web-ready output is **gold when the optimizer runs; partial on an offline/no-node degrade.** This is reported honestly, never rounded up.

---

## 2. Core Web Vitals

| Metric | Target | Levers |
|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s at the 75th percentile | Hero image `eager` + `fetchpriority="high"` (**cap 1–2 per page** — priority is zero-sum); preconnect to the image origin; right-size the LCP asset. |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Explicit `width`/`height` or `aspect-ratio` on every image, video, and embed. |
| **INP** (Interaction to Next Paint) | < 200ms | Keep heavy media off the main thread; lazy below-the-fold. |

**Rules:**
- The **LCP hero is eager**; give it `fetchpriority="high"` — but no more than 1–2 per page, or you starve the real hero (source: web.dev/articles/fetch-priority).
- **Everything below the fold is `loading="lazy"`** — do NOT lazy-load the LCP hero (a classic self-inflicted LCP regression; source: web.dev/articles/optimize-lcp, MDN fix-image-lcp).
- Explicit dimensions everywhere — CLS is almost always missing dimensions.

---

## 3. Delivery: build-time vs image CDN

| | Build-time (Sharp/Squoosh) | Image CDN (Cloudinary/imgix/Bunny) |
|---|---|---|
| Fits | **Repo-owned static sites** (winery/brand, Astro/Next static/HTML) — the consumer's default | CMS-driven, user uploads, dynamic transforms |
| How | `optimize-image.mjs` at build; committed derivatives | `format=auto`, width params on a transform URL |
| Cost shape | One-time build compute | Per-request / bandwidth `[verify-at-use]` |

**Default = build-time** (the consumer's sites lean static + repo-owned; source: imageguide.dev/guides/image-cdn-comparison). The CDN path is documented for CMS/upload sites, not the default.

---

## 4. Video embed (routed generation, REAL delivery)

Premium winery/brand sites often lead with a cinematic hero video. The embed is **not** a raw `<video src>`:

```html
<video
  autoplay muted loop playsinline
  poster="/media/hero-poster.avif"      <!-- poster is the LCP frame; eager -->
  width="1920" height="1080"            <!-- CLS-safe -->
  preload="metadata"
>
  <source src="/media/hero.webm" type="video/webm" />
  <source src="/media/hero.mp4"  type="video/mp4" />  <!-- H.264 fallback -->
</video>
```

- **Muted autoplay only** (browsers block unmuted autoplay; no surprise audio — accessibility + user respect).
- **`prefers-reduced-motion`**: gate autoplay behind the media query; show the poster still and a play control when reduced motion is requested.

```css
@media (prefers-reduced-motion: reduce) {
  video[autoplay] { /* pause / show poster; offer an explicit play control */ }
}
```

- **Poster frame is the LCP** — treat it like a hero image (eager, right-sized).
- **WebM (VP9/AV1) + H.264 MP4 fallback** for coverage.

---

## 5. 3D embed (`<model-viewer>`)

```html
<model-viewer
  src="/media/product.glb"
  poster="/media/product-poster.avif"
  loading="lazy" reveal="interaction"
  camera-controls disable-zoom
  style="width:100%;aspect-ratio:1/1"      <!-- CLS-safe -->
  alt="Interactive 3D model of the product"
></model-viewer>
```

Lazy by default, a poster still for the pre-interaction paint, explicit aspect-ratio for CLS, and a real `alt`. Template: [`../templates/model-viewer-3d-embed.html`](../templates/model-viewer-3d-embed.html). glTF/GLB is the web-native 3D format.

---

## 6. Audio (no autoplay)

No autoplay audio, ever. Attach ambient audio to a video soundtrack (muted-by-default, user-unmuted) or an explicit play control. Provide captions/transcript for spoken content (WCAG).

---

## Sources (retrieved 2026-07-13)

- LCP / fetchpriority / lazy: web.dev/articles/optimize-lcp, web.dev/articles/fetch-priority, MDN fix-image-lcp (**High**).
- AVIF/WebP `<picture>` best practice: web.dev, MDN (**High**).
- Build-time vs CDN: imageguide.dev/guides/image-cdn-comparison (Medium).
- `prefers-reduced-motion`: MDN (**High**). `<model-viewer>`: modelviewer.dev (**High**).
