---
name: prompt-to-asset-routing
description: "Route a creative brief to the right AI generator across images (photoreal, illustration, vector/SVG, text-in-image), video, 3D, and audio — plus the editing round-trips (inpaint, outpaint, background-removal, upscale) that beat a fresh generation. License-first, Grok-lean for images where competitive, draft-vs-final cost tiering. Provider/price specifics [verify-at-use]; every price [unverified]."
---

# Prompt-to-Asset Routing

The first decision: given a brief, which generator, which model, and text-to-image vs an editing round-trip. Images are the v1-deep lane; video/3D/audio are routed. **License gate first, then aesthetics.**

> **Generative-media judgment, landscape is volatile.** Every provider/model/price is `[verify-at-use]`; **every price is `[unverified — confirm on provider pricing page]`.** Read the matrix, never hard-code a provider.

## Workflow

1. **Traverse the modality-depth tree** ([`../../knowledge/generation-decision-trees.md`](../../knowledge/generation-decision-trees.md)). What *is* the asset — still image, hero/ambient video, 3D object, audio? Then pick depth.
2. **License-first routing** (the license-first→Grok-lean→fallback tree). Is this a client site? Is `indemnity_required` set? A FLUX-dev asset is worthless on a client site (non-commercial). Route to a Firefly-class indemnified provider when indemnity is required; Grok/xAI where competitive (flag: no IP indemnity); fallback chain otherwise.
3. **Draft-vs-final tiering.** Iterate on a cheap draft model to lock composition + brand, then spend on **one** premium final render. Log spend with `gen-budget.py`.
4. **Prefer an editing round-trip over a regeneration** when a brand-locked asset exists.
5. **Hand off.** Web-optimization → `web-optimization-pipeline`; license/provenance → `license-and-provenance-ledger`; brand-style setup → `brand-conditioned-generation`; the ship gate → `curation-and-accessibility-gate`.

## Images — the five capabilities (v1-deep)

| Capability | Route to (matrix) | Note |
|---|---|---|
| **Photoreal** | Grok (default where competitive) / Imagen 4 / FLUX.2 [pro] via BFL API | Never FLUX-dev on a client site |
| **Illustration** | Recraft / Firefly / Ideogram | Style-reference for brand consistency |
| **Vector / SVG** | **Recraft V3/V4 (native SVG)** | True vector for logo/icon — infinite scale, tiny, crisp |
| **Text-in-image** | Ideogram 3.0 (best legibility) — **but still overlay real type** | Models garble text; overlay HTML/SVG for the web |
| **Brand-styled** | Recraft brand-style upload (3–10 refs) + post-overlay exact hex | See `brand-conditioned-generation` |

## Images — the four editing round-trips (first-class)

| Round-trip | When | Why it beats a fresh generation |
|---|---|---|
| **Inpaint** | Fix/replace a region (remove an artifact, swap an element) | Keeps the rest of the brand-locked composition intact |
| **Outpaint** | Extend the canvas (wider hero, new aspect ratio) | Reuse an approved image instead of re-rolling |
| **Background-removal** | Product cut-outs, transparent overlays | Deterministic, cheap, no re-generation |
| **Upscale** | Ship a small draft at hero resolution | Draft cheap, upscale the chosen one |

**Rule:** if a brand-locked asset already exists, reach for a round-trip before spending on a new generation.

## Video / 3D / audio (routed)

- **Video** → Veo/Kling/Runway/Sora class (commercial use plan-dependent `[verify-at-use]`); the real embed pipeline is `web-optimization-pipeline`.
- **3D** → Meshy/Rodin/TRELLIS → glTF/GLB; `<model-viewer>` embed.
- **Audio** → capable API via fal; **no autoplay audio** on the web.

## Anti-patterns

- Routing on aesthetics before the license (the FLUX-dev trap).
- A fresh generation when an inpaint/outpaint/upscale round-trip would do.
- Baking text into an image instead of overlaying real type.
- Hard-coding a provider instead of reading the matrix.

## See also

- [`../../knowledge/provider-model-matrix-2026.md`](../../knowledge/provider-model-matrix-2026.md), [`../../knowledge/generation-decision-trees.md`](../../knowledge/generation-decision-trees.md)
- Best-practices: [`../../best-practices/pin-the-license-before-the-prompt.md`](../../best-practices/pin-the-license-before-the-prompt.md), [`../../best-practices/route-cheap-draft-before-premium-final.md`](../../best-practices/route-cheap-draft-before-premium-final.md)
- Sibling skills: [`../brand-conditioned-generation/SKILL.md`](../brand-conditioned-generation/SKILL.md), [`../web-optimization-pipeline/SKILL.md`](../web-optimization-pipeline/SKILL.md)
