# Changelog — brand-identity-studio

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in
`.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-07-13

Initial release.

### Added

- **2 agents** — `brand-strategist` (discovery → positioning/value-prop/audience/archetype; voice platform —
  attributes, tone rules, do-say/don't-say, glossary; business/product naming + tagline as bulk-draft →
  human-curated shortlist; owns the strategy-before-visuals gate) and `identity-systems-designer` (visual
  identity direction — logo suite with lockups/clear-space/min-size/mono/B&W, color roles + WCAG-AA pairs,
  type + web-license class; authors the media generation brief; runs the human-curation + human-authorship
  gates; delegates tokens to web-design; assembles the brand book + collateral).
- **5 skills** — `brand-strategy-and-naming`, `brand-voice-and-messaging`, `logo-and-visual-system-direction`,
  `brand-legal-and-licensing`, `brand-book-assembly`.
- **Knowledge bank** — `brand-identity-anatomy-2026.md` (the 10-part deliverable anatomy + process + tiered
  packaging, prices `[unverified]`), `legal-and-licensing-2026.md` (copyright≠trademark, font web-license
  classes, provider indemnity — every row routes client-facing claims to `security-reviewer`/counsel;
  not legal advice), and `brand-decision-trees.md` (4 Mermaid trees: tier selection, agentic-vs-human-toolkit,
  font-web-license class, where-to-delegate).
- **5 best-practices** — strategy-before-visuals-or-it-reads-as-slop,
  ai-logo-copyright-is-not-trademark-document-human-authorship, font-web-license-is-not-desktop-license,
  color-systems-need-wcag-pairs-not-just-hex, curate-the-vector-dont-regenerate-it.
- **6 templates** — `brand-strategy-brief`, `creative-brief-for-generative-media` (the **frozen seam** —
  contract_version 1.0, consumed by `generative-web-media`), `curation-and-authorship-log`,
  `brand-book-outline`, `font-license-tracker`, `favicon-og-asset-manifest`.
- **4 commands** — `/start-brand-engagement`, `/generate-identity-concepts`, `/curate-concepts`,
  `/assemble-brand-book`.
- **1 script** — `check-brand-a11y.py` (stdlib WCAG contrast-pair checker; mirrors
  `web-design/scripts/contrast_ratio.py`).
- **1 advisory hook** — `flag-brand-antipatterns.sh` (PostToolUse; stderr, always exit 0; flags
  non-self-hostable fonts, un-curated concepts, Firefly logo-regen markers, and un-routed trademarkability
  claims).

### Architecture & honesty

- **Thin orchestration by design** — delegates design tokens to `web-design:design-tokens-scaffolding`, raw
  generation + license/indemnity to `generative-web-media`, and site application to
  `web-design:visual-designer`. Ships no token bridge and does not re-declare a Firefly default.
- **The deliverable is the curated vector** — logos/wordmarks are never regenerated in Firefly.
- **AI-drafts + mandatory human curation** — a documented-human-authorship gate keeps the resale deliverable
  copyright-ownable/assignable.
- **Not legal advice** — every client-facing IP/registrability/font-license claim routes to
  `ravenclaude-core:security-reviewer`. **Prices are `[unverified]`** (aggregator calibration, not quotes).
- **Soft composes** — `generative-web-media` (prompt-pack fallback if absent) and `web-design`; only
  `ravenclaude-core@>=0.7.0` is a hard requirement.
