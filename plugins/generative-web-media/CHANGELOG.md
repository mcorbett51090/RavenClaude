# Changelog — generative-web-media

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-13

Initial release.

### Added

- **4 agents** — `generation-strategist` (brief → provider/model routing across images/video/3D/audio, draft-vs-final cost tiering, brand-style-reference conditioning, editing round-trips), `web-asset-pipeline-engineer` (raw asset → AVIF/WebP responsive `<picture>` with explicit dims, LCP/CLS-safe markup, accessible muted-autoplay video embeds, `<model-viewer>` glTF, framework fit), `asset-provenance-guardian` (commercial-use license pinning + the FLUX-dev non-commercial trap, provenance ledger, per-project generation budgets, EU AI Act Art.50 disclosure), `brand-and-accessibility-reviewer` (brand-hex/style conformance, anti-slop QA, AI-drafted + human-reviewed WCAG alt text, mandatory human curation sign-off).
- **6 skills** — `prompt-to-asset-routing`, `web-optimization-pipeline`, `license-and-provenance-ledger`, `brand-conditioned-generation`, `curation-and-accessibility-gate`, `generation-budget-guard`.
- **Knowledge bank (4 docs)** — `provider-model-matrix-2026.md` (the single provider matrix; Grok-lean image row; FLUX-dev non-commercial flag; Firefly-indemnified default; Grok-no-indemnity note — all prices `[unverified — confirm on provider pricing page]`), `web-media-pipeline.md` (AVIF/WebP/fallback, responsive widths, CLS/LCP, build-time-vs-CDN, real video/3D embeds), `legal-and-provenance-2026.md` (Thaler no-copyright-in-pure-AI, license≠ownership, C2PA fragility, EU AI Act Art.50 enforceable 2 Aug 2026), `generation-decision-trees.md` (4 Mermaid trees: modality-depth, license-first→Grok-lean→fallback, build-time-vs-CDN, format-choice).
- **6 best-practices** — never-ship-a-raw-image, pin-the-license-before-the-prompt, overlay-text-dont-bake-it, style-reference-beats-seed-pinning, human-curation-is-not-optional, route-cheap-draft-before-premium-final.
- **5 templates** — asset-brief (the frozen brand-token contract), generation-defaults.yaml, asset-provenance-ledger-entry.json, picture-element-snippet.html, model-viewer-3d-embed.html.
- **4 commands** — `/generate-web-asset` (end-to-end + hard curation gate), `/audit-asset-licenses` (executable detector), `/wire-media-substrate` (fallback), `/check-generation-budget`.
- **4 scripts** — `web-optimize/optimize-image.mjs` (+`package.json`, Node/Sharp via `npx`, LOUD-SKIP if absent), `provenance.py` (stdlib), `gen-budget.py` (stdlib), `generate-via-provider.sh` (curl + env key, direct-provider fallback). All probe-and-degrade — never a silent pass.
- **Declarative fal MCP binding** in `plugin.json` (`https://mcp.fal.ai/mcp`) so the substrate auto-wires on install; `FAL_KEY` is the only manual input; `/wire-media-substrate` is the documented fallback. `NOTICE.md` for third-party MCP attribution.

### Scope & verify-at-use

- **Foundation for `brand-identity-studio`** — owns the single provider matrix, license/indemnity/provenance layer, cost ledger, raw generation, and web-optimization; the brand plugin consumes assets, it does not re-implement these layers (CLAUDE.md §0.2). The DTCG token producer is `web-design:design-tokens-scaffolding`; this plugin only consumes tokens.
- **Depth ordering** — images v1-deep (photoreal/vector/text-in-image + inpaint/outpaint/bg-removal/upscale round-trips); video routed with a real embed pipeline; 3D/audio routed light. Not shallow-everywhere.
- **Generative-media engineering judgment, not legal advice.** Every provider price is `[unverified — confirm on provider pricing page]`; the web-ready output is gold *when the Sharp optimizer runs* and partial on an offline/no-node degrade (stated conditionally, not rounded up). No client secrets stored — keys are referenced by env-var name.
