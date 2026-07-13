---
name: brand-conditioned-generation
description: "Condition generation on a brand: consume brand tokens from whatever source is present (a DTCG design-token file OR ravenclaude-core:brand-extraction's brand.json), assemble a 3-10 image style-reference / Recraft brand-style upload, then post-overlay the exact brand hex rather than trusting the model's color memory. Style-reference beats seed-pinning. This plugin CONSUMES tokens; it does not produce them."
---

# Brand-Conditioned Generation

Make generated assets look like the brand — via a style-reference plus an exact-hex overlay, not a lucky seed. This plugin **consumes** a brand-token contract; it never produces the token file (that's `web-design:design-tokens-scaffolding`).

> **Style-reference beats seed-pinning.** A pinned seed doesn't transfer across models or prompts; a style-reference (image set / brand-style upload) plus a post-overlay of the exact brand hex does. Model color memory is unreliable — overlay the real value.

## Workflow

1. **Get the brand tokens** — consume from *whatever source is present*: a DTCG design-token file (greenfield, produced by `web-design:design-tokens-scaffolding`) or [`ravenclaude-core:brand-extraction`](../../../ravenclaude-core/skills/brand-extraction/SKILL.md)'s `brand.json` (existing site). brand-extraction is one **adapter**, not a hard-wire.
2. **Assemble the style-reference half** (what brand-extraction lacks) — collect 3–10 on-brand reference images, or prepare a Recraft brand-style upload. This carries the *feel* (composition, palette mood, texture).
3. **Generate with the style-reference** — pass the references / brand-style, plus a negative-prompt baseline (no garbled text, no off-brand elements).
4. **Post-overlay the exact hex** — never trust the model to reproduce `#8B2635` precisely. Overlay real brand color (and real type — see overlay-text-dont-bake-it) in HTML/SVG on the web layer.
5. **Route to the brand review gate** — `curation-and-accessibility-gate` verifies hex/style conformance before ship.

## The brand-token contract (consumer side)

The brief arrives as the frozen schema in [`../../templates/asset-brief.md`](../../templates/asset-brief.md) (`contract_version: "1.0"`). This skill reads its `constraints`, `negative_constraints`, and `format_hints`, conditions generation on them, and returns `{asset_uri, provenance_record, provider, indemnity_status, license_class}`. The schema is **frozen** — a change is a coordinated cross-plugin decision (CLAUDE.md §6).

## Anti-patterns

- Trusting a seed for brand consistency (it doesn't transfer).
- Trusting the model to hit an exact brand hex (overlay it).
- Re-implementing the design-token producer here (we consume, not produce).
- Hard-wiring brand-extraction as the only source (it's one adapter).

## See also

- Best-practice: [`../../best-practices/style-reference-beats-seed-pinning.md`](../../best-practices/style-reference-beats-seed-pinning.md), [`../../best-practices/overlay-text-dont-bake-it.md`](../../best-practices/overlay-text-dont-bake-it.md)
- [`../../templates/asset-brief.md`](../../templates/asset-brief.md), [`../curation-and-accessibility-gate/SKILL.md`](../curation-and-accessibility-gate/SKILL.md)
