# Provider & Model Matrix — 2026

> **The single provider matrix for the marketplace.** This plugin owns it; `brand-identity-studio` and any other consumer **references** this file, never copies it (CLAUDE.md §0.2 — one home per layer). Agents READ the matrix and never hard-code a provider.
>
> **Every price below is `[unverified — confirm on provider pricing page]`.** Prices are aggregator-sourced and move monthly; they are decision-support ordering, not a quote. Model *capabilities/versions* are Medium–High confidence; **prices are the least reliable column** — confirm on the provider's own pricing page before any spend or client commitment. Model families change fast — `[verify-at-use]`.
>
> _Last reviewed: 2026-07-13 by `claude`. Sources cited inline; re-confirm before quoting._

---

## How to read this matrix

1. **License gate first** (the license-first tree). A model's aesthetics never override a license blocker.
2. **Grok-lean for images where competitive** — with the no-indemnity flag surfaced.
3. **Draft-vs-final tiering** — iterate on a cheap draft model, spend on one premium final.
4. Prices are `[unverified]`; use them only to *order* choices, never to quote a client.

---

## Image models (the v1-deep lane)

| Model / provider | Strength | Commercial license | Indemnity | Price (per image) `[unverified]` |
|---|---|---|---|---|
| **Grok / xAI image** | **Default where competitive** — fast, strong general photoreal | Commercial use per xAI terms `[verify-at-use]` | **NO IP indemnity** — flag for risk-averse client work | `[unverified — confirm on provider pricing page]` |
| **Recraft V3/V4** | **Native SVG/vector**, brand-style upload (3–10 refs), text handling | Commercial on paid plans `[verify-at-use]` | Provider terms — not a broad indemnity | ~$0.04 raster / ~$0.08 vector `[unverified]` |
| **Adobe Firefly** | **Lowest legal risk** — licensed/public-domain training data | Commercial on paid plans | **IP indemnification on paid plans** (the indemnified default when `indemnity_required`) | `[unverified — confirm on provider pricing page]` |
| **Ideogram 3.0** | **Best in-image text** (~90–95% legible) — but still overlay real type for the web | Commercial on paid plans `[verify-at-use]` | Provider terms | ~$0.03–0.09 `[unverified]` |
| **Imagen 4 (Google)** | Strong photoreal, prompt adherence | Commercial per Google terms `[verify-at-use]` | Provider terms | ~$0.02–0.06 `[unverified]` |
| **FLUX.2 [pro] (BFL API)** | High-fidelity photoreal via the paid API | Commercial via **BFL API / paid self-host license** | Provider terms | ~$0.055 `[unverified]` |
| **FLUX.2 [dev] (open weights)** | Strong — **but the open weights are NON-COMMERCIAL** | ❌ **NON-COMMERCIAL** — pulling from HF for a client site is a licensing trap (C8) | N/A | (self-host) — **do not use commercially without the BFL license** |
| **GPT Image (OpenAI)** | Instruction-following, editing | Commercial per OpenAI terms `[verify-at-use]` | Provider terms | ~$0.005–… `[unverified]` |
| **Nano Banana Pro** | Fast iteration / drafts | `[verify-at-use]` | Provider terms | `[unverified]` |

**FLUX-dev trap (the headline license risk).** FLUX.2 **[dev]** open weights are **non-commercial**; commercial use needs the **BFL API** or a paid self-host license (source: bfl.ai/licensing, bfl.ai/legal/self-hosted-commercial-license-terms). `/audit-asset-licenses` detects a FLUX-dev provenance record on a client project and flags it. **Never let a FLUX-dev asset reach a client site without an explicit override.**

**Editing round-trips (first-class, not an afterthought).** Inpaint, outpaint, background-removal, and upscale are available across several of the above (and dedicated tools). Prefer a round-trip on a brand-locked asset over a fresh generation. `[verify-at-use]` per provider.

---

## Video models (routed — real embed pipeline)

| Model / provider | Strength | Access | Price `[unverified]` |
|---|---|---|---|
| **Veo 3.1 (Google)** | 4K, native audio, strong coherence | API-real; commercial plan-dependent `[verify-at-use]` | ~$0.75/s `[unverified]` |
| **Kling 3.0** | Cost-effective motion | API-real | ~$0.10/s `[unverified]` |
| **Runway Gen-4.5** | Creative control, editing | API-real | `[unverified]` |
| **Sora 2 (OpenAI)** | Coherent longer clips | API/plan-dependent `[verify-at-use]` | `[unverified]` |

Commercial use is **plan-dependent** for every video model — confirm the plan tier before a client deliverable. The web embed (muted autoplay, `prefers-reduced-motion`, poster LCP, WebM/H.264 fallback) is owned by `web-asset-pipeline-engineer`.

---

## 3D models (routed — light)

| Model / provider | Output | Notes |
|---|---|---|
| **Meshy-6** | text/image → textured mesh (glTF/GLB) | API-real `[verify-at-use]` |
| **Rodin Gen-2 (Hyper3D)** | high-fidelity textured mesh | API-real `[verify-at-use]` |
| **Microsoft TRELLIS.2** | open, PBR materials | open weights — check the license before commercial use `[verify-at-use]` |

Web delivery = `<model-viewer>` glTF/GLB embed (lazy, poster, explicit dims). See [`web-media-pipeline.md`](web-media-pipeline.md).

---

## Audio (routed — lightest)

Ambient / SFX / voiceover route to a capable API (many are exposed through the fal substrate) `[verify-at-use]`. **Web-delivery rule: no autoplay audio** — attach to a video soundtrack (muted by default, user-unmuted) or an explicit play control. WCAG + user-hostility both forbid surprise audio.

---

## Substrate note

Most of the above are reachable through the **fal** hosted MCP (one endpoint, pay-per-run) declared in `plugin.json`. Grok/xAI also has a **direct** path (`api.x.ai/v1`) via `scripts/generate-via-provider.sh` so the preferred image provider isn't gated behind fal adoption. See CLAUDE.md §8 and `NOTICE.md`.

---

## Sources (retrieved 2026-07-13; prices `[unverified]`)

- Image landscape + prices: aggregator (atlascloud/buildmvpfast), ideogram.ai/features/api-pricing, recraft.ai/docs/api-reference/pricing — **prices Medium confidence, treat as unverified**.
- FLUX licensing: bfl.ai/licensing, bfl.ai/legal/self-hosted-commercial-license-terms (**High**).
- Firefly indemnity: tensoria.fr firefly (Med-High; **do not quote specific indemnity caps** — Low confidence).
- Video: buildmvpfast/api-costs/ai-video, modelslab (prices Medium).
- 3D: 3daistudio.com/state-of-ai-3d-generation-2026, trellis2.app.
- Grok multimedia coverage (images ✓; video/3D/audio partial) `[verify-at-use]`.
