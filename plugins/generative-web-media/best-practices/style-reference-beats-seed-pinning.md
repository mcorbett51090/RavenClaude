# Style-reference beats seed-pinning

**Status:** Pattern
**Domain:** Brand consistency
**Applies to:** `generative-web-media`

> Engineering pattern. Technique names are durable; per-provider style-input mechanics are `[verify-at-use]`.

---

## Why this exists

Teams reach for a pinned seed to make a brand look consistent. A seed does **not** transfer across models, prompts, or providers, and it doesn't encode a brand — it encodes one noise pattern. What actually carries a brand is a **style-reference** (an image set, a LoRA, or a Recraft brand-style upload of 3–10 images) plus a **post-overlay of the exact brand hex**, because model color memory is unreliable and a seed can't hit `#8B2635` on demand.

## How to apply

- Assemble **3–10 on-brand reference images** or a Recraft brand-style upload — this carries composition/palette-mood/texture.
- Condition generation on the style-reference (not a seed) plus a negative-prompt baseline.
- **Post-overlay the exact brand hex** in the web layer — don't trust the model to reproduce it.
- Consume brand tokens from whatever source is present (DTCG file or `brand-extraction`'s `brand.json`) — this plugin consumes, never produces, tokens.

**Do:** condition on a style-reference; overlay exact hex.
**Don't:** rely on a seed for brand consistency, or trust the model's color reproduction.

## Edge cases / when the rule does NOT apply

A single one-off exploratory image with no brand constraint doesn't need the style-reference apparatus. When a provider offers a true brand-lock feature, prefer it — still overlay the exact hex.

## See also

- [`../skills/brand-conditioned-generation/SKILL.md`](../skills/brand-conditioned-generation/SKILL.md)
- [`../knowledge/provider-model-matrix-2026.md`](../knowledge/provider-model-matrix-2026.md) (Recraft brand-style row)

## Provenance

Codifies the brand house opinion; grounded in getimg.ai brand-style + aimagicx style-guide (retrieved 2026-07-13; Medium confidence).

---

_Last reviewed: 2026-07-13 by `claude`_
