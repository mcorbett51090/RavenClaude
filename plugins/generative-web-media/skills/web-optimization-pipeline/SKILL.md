---
name: web-optimization-pipeline
description: "Turn a raw generated asset into a production web asset: AVIF/WebP/fallback responsive <picture> at 3-5 widths with explicit dims (CLS-safe), LCP hero eager + fetchpriority=high (cap 1-2), lazy below-fold, accessible muted-autoplay prefers-reduced-motion video embeds with a poster-LCP frame + WebM/H.264 fallback, and <model-viewer> glTF. Build-time (Sharp) default; CDN documented. Optimizer LOUD-SKIPs if Node/Sharp absent."
---

# Web-Optimization Pipeline

Never ship a raw image. A generator emits a large PNG/JPEG; production needs next-gen formats, responsive widths, and CLS/LCP-safe markup. This is the differentiator.

> **The web-ready output is gold WHEN the optimizer runs (Node/Sharp present); partial on an offline/no-node degrade.** Reported honestly, never rounded up.

## Workflow

1. **Run the optimizer** — [`../../scripts/web-optimize/optimize-image.mjs`](../../scripts/web-optimize/optimize-image.mjs) via `npx --yes --package=sharp@0.33.5 node optimize-image.mjs --in … --outdir … --name …`. It emits AVIF+WebP+fallback at responsive widths, reports intrinsic dims, and prints a `<picture>`.
2. **If Node/Sharp is absent** the optimizer **LOUD-SKIPs** ("THIS IS NOT A PASS") and you degrade to guidance-only: hand-run the same steps from [`../../knowledge/web-media-pipeline.md`](../../knowledge/web-media-pipeline.md). Do not claim gold on a degraded host.
3. **Place the markup** — LCP hero eager + `fetchpriority="high"` (cap 1–2/page); everything else `loading="lazy"`; explicit `width`/`height` everywhere (CLS).
4. **Video / 3D** — use the real embed patterns (below), not a raw `<video src>` / raw model file.
5. **Choose delivery** — build-time (Sharp) for repo-owned static sites (the default); image CDN for CMS/uploads.

## The image contract

- AVIF primary → WebP fallback → JPEG (or PNG for alpha) safety net, via `<picture>`.
- 3–5 responsive widths (`srcset` + `sizes`).
- Explicit `width`/`height` or `aspect-ratio` (CLS).
- True vector (logo/icon) → **SVG**, not a raster pipeline.

Template: [`../../templates/picture-element-snippet.html`](../../templates/picture-element-snippet.html).

## Core Web Vitals

- **LCP ≤ 2.5s (p75):** hero eager, `fetchpriority="high"` (cap 1–2), preconnect the image origin, don't lazy-load the hero.
- **CLS < 0.1:** explicit dimensions on every image/video/embed.
- **INP < 200ms:** heavy media off the main thread, lazy below the fold.

## Video embed (real, not a pointer)

Muted autoplay + `playsinline` + `loop`, a poster frame (the LCP), explicit dims (CLS), WebM + H.264 MP4 fallback, and a `prefers-reduced-motion` guard that shows the poster + a play control. Full pattern in [`../../knowledge/web-media-pipeline.md`](../../knowledge/web-media-pipeline.md) §4.

## 3D embed

`<model-viewer>` with glTF/GLB, `loading="lazy"`, a poster, explicit `aspect-ratio` (CLS), and a real `alt`. Template: [`../../templates/model-viewer-3d-embed.html`](../../templates/model-viewer-3d-embed.html).

## Anti-patterns

- Shipping a raw PNG/JPEG.
- Lazy-loading the LCP hero (self-inflicted LCP regression).
- `fetchpriority="high"` on many images (priority is zero-sum).
- Missing `width`/`height` (the usual CLS cause).
- Autoplay audio; unmuted video autoplay (browsers block it anyway).

## See also

- [`../../knowledge/web-media-pipeline.md`](../../knowledge/web-media-pipeline.md), [`../../knowledge/generation-decision-trees.md`](../../knowledge/generation-decision-trees.md)
- Best-practice: [`../../best-practices/never-ship-a-raw-image.md`](../../best-practices/never-ship-a-raw-image.md)
