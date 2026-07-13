# Brand Identity Anatomy & Engagement Reference — 2026

> Reference for the `brand-identity-studio` team: what a professional brand deliverable contains, the process
> that produces it, and the tiered packaging. **Prices are `[unverified]` aggregator calibrations, not quotes**
> — confirm on the vendor/market pricing page. Tool/provider capability facts carry `[verify-at-use]`.
>
> _Last reviewed: 2026-07-13 by `claude`. Retrieval date 2026-07-13. Principles are durable; prices + tool
> specifics are volatile._

---

## 1. The 10-part anatomy of a pro brand deliverable

Sourced from brand-identity practice (bcobranding.com brand_book_anatomy; digitalsilk.com; identitymakers.co;
Wheeler, *Designing Brand Identity*). Retrieval 2026-07-13, **High** confidence on the anatomy.

| # | Part | What it contains | v1 depth (this plugin) |
|---|---|---|---|
| 1 | **Strategy / positioning** | Positioning statement, value prop, audience, archetype, brand voice | deep |
| 2 | **Logo suite** | Primary/secondary/mark/wordmark, lockups, clear-space, min-size, mono, reversed/B&W, do/don't | deep |
| 3 | **Color system** | Roles (primary/secondary/accent/neutrals), HEX/RGB/CMYK/OKLCH, **WCAG contrast pairs** | deep |
| 4 | **Type system** | Families, modular scale, pairing rules, **web-license class per family** | deep |
| 5 | **Grid / spacing** | Layout grid, spacing scale | direction |
| 6 | **Iconography** | Icon style, grid, stroke | direction (not full production) |
| 7 | **Imagery direction** | Photography/illustration style, art direction (indemnity via media) | direction |
| 8 | **Voice & messaging** | Tagline, tone rules, do-say/don't-say, glossary | deep |
| 9 | **Usage do/don'ts** | The specific misuse gallery | deep |
| 10 | **The brand book** | 30–80pp historically; **2025+ adds AI-content rules + accessibility + governance**; a **dynamic hub beats a static PDF** | deep |

**The 2025/2026 shift:** brand books are living hubs (the color tokens shown ARE the tokens; logo files are
downloadable) with explicit **AI-content usage rules**, an **accessibility** section (validated contrast +
reduced-motion), and **governance** (who can change what). A PDF rots; the hub re-reads the token source.

## 2. The engagement process

`discovery → strategy → moodboard → identity concepts → refinement → guidelines → asset handoff`

- Human timeline is ~**6–12 weeks** (digitalsilk.com; clay.global; cultmethod.com; retrieval 2026-07-13,
  **High** on the shape). An agent pipeline compresses and productizes it — but does **not** remove the human
  curation + strategy steps (those are where distinctiveness and legal defensibility come from).
- **AI-in-the-loop is exploration-only + human-curated.** "AI is great at exploration, terrible at refinement"
  and defaults to a "legible middle" that reads as slop (humanagency.com; superside.com; typeface.ai).
  Distinctiveness = human strategy + ruthless curation + **specific** constraints ("like Stripe but warmer,
  avoid blue" not "modern"). Strategy/positioning stays human.

## 3. Tiered packaging (sellable service offerings)

**Prices are `[unverified]` — US self-reported aggregator ranges (8gnc.io; cultmethod.com; sproutbox.co),
calibration NOT quotes. Confirm on the vendor/market pricing page before quoting a client.** Retrieval
2026-07-13, **Medium** confidence (aggregator).

| Tier | Deliverables | Timeline `[unverified]` | Price `[unverified]` |
|---|---|---|---|
| **Starter** | Logo + basic palette + type + mini guide | ~2–4 wks | ~$2–7K |
| **Mid** | Full identity WITH strategy + voice + brand book | ~4–8 wks | ~$7–25K |
| **Comprehensive** | Mid + messaging + web token handoff + collateral | ~8–12 wks | ~$25–100K+ |

**The natural studio bundle:** mid/comprehensive, where the brand system IS the source of the site's design
tokens — the differentiator is that the brand survives the website (tokens delegated to
`web-design:design-tokens-scaffolding`, no hand-copy into CSS).

## 4. The agent-callable generation landscape (for the brief — decision is media's)

**This plugin does NOT call these directly** — it sets `indemnity_required` in the brief and
`generative-web-media` chooses. Facts carry `[verify-at-use]`; prices `[unverified]`. Retrieval 2026-07-13.

- **Consumer logo tools (Looka, Brandmark, Tailor Brands) have NO public generative API** — UI-only; an agent
  cannot orchestrate them (looka.com; logoai.com/logo-api; toolsforhumans.ai). This is why the agentic path is
  Claude-orchestrator-over-Recraft/Ideogram/Firefly, not a Looka resale.
- **Agent-callable core:** Recraft (true SVG/vector), Ideogram (typography/wordmarks), **Adobe Firefly
  Services** (the IP-indemnified option — imagery only), Gamma Generate (auto guideline docs; GA Jan 2026
  `[verify-at-use]`), Canva Connect (Enterprise-gated). For current per-image prices (all `[unverified]`) see
  `generative-web-media`'s `knowledge/provider-model-matrix-2026.md` — that is the single home for the provider
  price/license matrix; this plugin does not restate them. Sources: developer.adobe.com/firefly-services;
  recraft.ai; docs.ideogram.ai; developers.gamma.app; canva.dev.
- **Claude Design + MCP** (launched ~Apr 17 2026 `[verify-at-use]`) generates design SYSTEMS/UI tokens and
  inherits org brand colors/fonts (support.claude.com/articles/14604416) — a compose point at the token layer,
  not a brand-identity creator.
- **The gap = the opportunity:** no first-party or notable community plugin does end-to-end BRAND IDENTITY
  creation (logo suite → palette → type → voice → brand book). The ecosystem is mature for UI design-systems,
  not brand identity (github.com/rohitg00/awesome-claude-design). Retrieval 2026-07-13, **High**.

## 5. Favicon / OG asset set (2026 minimum)

`favicon.svg` (dark-mode via media query), `favicon.ico` (16/32/48), `apple-touch-icon` 180×180, PWA 192/512,
OG image 1200×630, Twitter/X card 1200×675 (favicon.io/tutorials/favicon-sizes; evilmartians.com; retrieval
2026-07-13, **High**). Specced in the favicon-og-asset-manifest template; generated via `generative-web-media`.

---

## Verification debts

- **Prices (§3, §4):** aggregator → `[unverified — confirm on vendor/market pricing page]`; never quote as fact.
- **Provider/API capabilities (§4):** `[verify-at-use]` — re-confirm against the vendor before relying on them.
- **Trademark clearance workflow (USPTO TESS):** not deep-dived — required before promising trademarkability;
  route to `security-reviewer`/counsel. See [`legal-and-licensing-2026.md`](legal-and-licensing-2026.md).
