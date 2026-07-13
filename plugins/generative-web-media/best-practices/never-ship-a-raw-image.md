# Never ship a raw image

**Status:** Absolute rule
**Domain:** Web integration
**Applies to:** `generative-web-media`

> Engineering rule. Web-platform mechanics are durable; the optimizer is gold WHEN it runs, partial on a no-node degrade.

---

## Why this exists

A generator emits a large PNG or JPEG — often thousands of pixels wide, uncompressed for the web. Dropped onto a page as-is it tanks LCP, ships bytes no visitor needs, and causes layout shift. The web needs next-gen formats, responsive widths, and reserved layout space. The raw file is an input to the pipeline, never the output that ships.

## How to apply

- Emit **AVIF primary → WebP fallback → JPEG/PNG safety net** via `<picture>`.
- Provide **3–5 responsive widths** (`srcset` + `sizes`).
- Set **explicit `width`/`height`** (or `aspect-ratio`) — this is the CLS fix.
- True vector (logo/icon) ships as **SVG**, not a raster pipeline.
- Run [`../scripts/web-optimize/optimize-image.mjs`](../scripts/web-optimize/optimize-image.mjs); if Node/Sharp is absent it LOUD-SKIPs and you hand-run the pipeline from [`../knowledge/web-media-pipeline.md`](../knowledge/web-media-pipeline.md).

**Do:** run the optimizer, emit responsive next-gen markup with explicit dims.
**Don't:** drop a raw PNG/JPEG into production or claim gold on a degraded (no-optimizer) host.

## Edge cases / when the rule does NOT apply

A true SVG (vector logo/icon) needs no raster pipeline — it ships as SVG directly. An email or a non-web deliverable has different format constraints.

## See also

- [`../skills/web-optimization-pipeline/SKILL.md`](../skills/web-optimization-pipeline/SKILL.md)
- [`../knowledge/web-media-pipeline.md`](../knowledge/web-media-pipeline.md)

## Provenance

Codifies `web-asset-pipeline-engineer` house opinion; grounded in web.dev/optimize-lcp + MDN (retrieved 2026-07-13).

---

_Last reviewed: 2026-07-13 by `claude`_
