# brand-identity-studio

A **thin orchestration** Claude Code plugin that runs a standalone **brand-CREATION engagement** for a web
studio's commission customers: discovery → strategy/positioning/archetype → naming & tagline → curated logo
suite → color/type systems (WCAG-paired) → brand book → legal/IP posture → collateral → sellable tiers.

AI drafts in bulk; **a human curates**. The plugin composes with siblings instead of re-implementing them.

## The 3-way boundary (why this plugin is thin)

> This plugin owns the standalone brand-CREATION engagement (strategy → positioning/archetype → naming → logo
> suite → brand book → legal/IP → collateral → sellable tiers). It does **not** re-implement design tokens
> (delegates to **`web-design:design-tokens-scaffolding`**), raw asset generation or license/indemnity
> (delegates to **`generative-web-media`**), or site application (hands the finished brand system to
> **`web-design:visual-designer`**). web-design's visual-designer/content-strategist stay site-scoped.

- **Design tokens** → `web-design:design-tokens-scaffolding` (DTCG → Style Dictionary → CSS vars / Tailwind).
  This plugin ships **no** token bridge.
- **Raw generation + the license/indemnity decision** → `generative-web-media`. This plugin only sets
  `indemnity_required` in the generation brief; the provider is chosen per-asset by media's license gate.
- **Site application** → `web-design:visual-designer`.
- **The logo/wordmark deliverable IS the curated Recraft/Ideogram-class vector** — never regenerated in
  Firefly (regeneration voids the human curation the value promise rests on).

## What's inside

| Surface | Count | What |
|---|---|---|
| Agents | 2 | `brand-strategist` (strategy + verbal identity), `identity-systems-designer` (visual system direction + orchestration + brand book) |
| Skills | 5 | brand-strategy-and-naming, brand-voice-and-messaging, logo-and-visual-system-direction, brand-legal-and-licensing, brand-book-assembly |
| Commands | 4 | `/start-brand-engagement`, `/generate-identity-concepts`, `/curate-concepts`, `/assemble-brand-book` |
| Knowledge | 3 | brand-identity-anatomy-2026, legal-and-licensing-2026, brand-decision-trees (Mermaid) |
| Best-practices | 5 | strategy-before-visuals, ai-logo-copyright≠trademark, font-web-license≠desktop, color-needs-WCAG-pairs, curate-the-vector |
| Templates | 6 | brand-strategy-brief, **creative-brief-for-generative-media** (the frozen seam), curation-and-authorship-log, brand-book-outline, font-license-tracker, favicon-og-asset-manifest |
| Scripts | 1 | `check-brand-a11y.py` — stdlib WCAG contrast-pair checker (mirrors web-design's `contrast_ratio.py`) |
| Hooks | 1 | `flag-brand-antipatterns.sh` — **advisory** (stderr, exit 0), never blocks |

## The gated pipeline

1. **strategy-before-visuals** — concept generation refuses without a strategy brief.
2. **human-curation** — a person selects from the bulk-generated concepts (`/curate-concepts`).
3. **documented-human-authorship** — the curation logs a substantial human modification so the resale
   deliverable is copyright-ownable/assignable.
4. **font-license-class** — a non-self-hostable font (Adobe/Monotype) is blocked from the token export.
5. **WCAG-pair validation** — every text/background pair validated to AA before the palette ships.
6. **legal-sign-off** — the brand book can't be marked client-ready until curation + authorship exist and
   every IP/registrability/font claim has been routed to `security-reviewer`.

## Honesty

- **Not legal advice.** Facts are stated; conclusions are not. Every client-facing IP / trademark /
  registrability / font-license claim routes to `ravenclaude-core:security-reviewer` (and counsel).
- **Prices are `[unverified]`.** Tier calibrations are aggregator ranges, never quotes.
- **Tool landscape is volatile.** Provider/API facts carry `[verify-at-use]`; the indemnity decision is
  `generative-web-media`'s.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install brand-identity-studio@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`. `generative-web-media` and `web-design` are **soft** composes — if
absent, the plugin degrades gracefully (a copy-paste prompt-pack replaces the media handoff; the brand book
ships with a "needs web-design for the token build + site application" note).

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and [`CHANGELOG.md`](CHANGELOG.md) for version
history.
