# Design references — "cutting edge yet simple" (2026)

> **Last reviewed:** 2026-09-01 (Catalogs section added; the eight donors below untouched, still dated 2026-05-21). Refresh when (a) a new "Linear-style refresh" moment lands for a flagship dev tool, (b) Awwwards / Site of the Year shifts the consensus, or (c) at least 12 months pass — the design discourse cycles roughly annually.

A curated, opinionated reference set for any web-design work that wants to feel **modern, restrained, and developer-credible** without chasing trends that age in six months. Use this as the visual + interaction north star for marketing sites, product pages, design-system rebuilds, and dashboards intended for technical buyers.

**For a dashboard specifically** (as opposed to a marketing/product surface), the restraint principle
below is generalized into dashboard-specific craft — information hierarchy, KPI/whitespace/color
discipline, and chart-type selection — in `data-platform`'s
[`knowledge/dashboard-visual-craft-2026.md`](../../data-platform/knowledge/dashboard-visual-craft-2026.md),
cross-linked from that plugin's `dashboard-builder` agent. Same pattern as `design-clone`'s
cross-link into this plugin: the craft canon lives with its primary consumer, referenced from here.

The whole frame is **restraint plus one or two memorable interactive beats**. Most of the work is the restraint. The "wow" beats are surgical and earn their motion budget.

---

## Catalogs (breadth, when the 8 donors don't fit)

The eight donors below are hand-curated — a small, deep set with explicit borrow/don't-borrow judgments
for each. Sometimes the job needs **breadth** instead: a direction the eight donors don't cover, or a
starting point when the brief itself is vague ("make it look premium" with no reference point at all).

**[Refero Styles](https://styles.refero.design/)** — a searchable catalog of **2,000+ AI-readable
design systems** extracted from real product websites, each exposing colour palette, typography,
spacing, components, and a `DESIGN.md` export in the same format this repo's own
[`templates/DESIGN.md`](../../ravenclaude-core/templates/DESIGN.md) house default uses (see
[`knowledge/design-md-token-interop.md`](design-md-token-interop.md)). Sortable by Trending / Popular /
Newest, with a search box; a directional-category browse (minimal, brutalist, monochrome, etc.) is
described in third-party coverage of the tool but was not independently re-confirmed against the live
page this session — verify the exact filter set at use.
`[docs-verified — fetched and confirmed 2,000+ figure + per-entry contents this session, 2026-09-01]`

**Use it to extract a visual language, not to clone a product.** Ask for the parts that matter — type
scale, spacing rhythm, colour role, hierarchy — and build an *original* interface from them, exactly
the discipline the eight donors below already apply per-entry. This repo's own
[`design-clone`](../../ravenclaude-core/skills/design-clone/SKILL.md) skill states the same boundary at
length for a single reference site: cloning functional *craft* (spacing, grid, elevation, component
recipes) is the lower-risk path; faithfully reproducing a distinctive *whole composition* is not, and
neither that skill nor this catalog note clears trade-dress risk — a Refero entry read as "the parts to
borrow," never as "the site to copy."

---

## The eight donors

### 1. Linear — <https://linear.app>

- **Why praised** — The 2024 refresh and the 2025 monochrome reduction are routinely cited as the benchmark for SaaS restraint. "Linear design" is a named trend now ([LogRocket](https://blog.logrocket.com/ux-design/linear-design/), [Linear changelog 2024-03-20](https://linear.app/changelog/2024-03-20-new-linear-ui)).
- **Borrow** — Static product-UI hero (no video, no 3D). Sequential, scan-friendly section rhythm. Muted palette with one accent color used sparingly.
- **Don't borrow** — The heavy gradient washes from the 2024 era; Linear itself dialed them back in 2025.

### 2. Vercel — <https://vercel.com>

- **Why praised** — The Geist grid background became so widely copied it earned the nickname "the Vercel aesthetic" ([Setproduct](https://www.setproduct.com/blog/complete-guide-to-blueprint-grid-design), [Vercel Geist Grid](https://vercel.com/geist/grid)).
- **Borrow** — Faint underlying grid as a calm background system. Systematic spacing tokens. Subtle functional micro-animations on CTAs and cards.
- **Don't borrow** — Stacking decorative gradients on top of the grid; per the same source, that "defeats the purpose."

### 3. Raycast — <https://raycast.com>

- **Why praised** — Treats the marketing site as an extended product screenshot; command-palette mockups as the hero are widely studied ([Lapa Ninja](https://www.lapa.ninja/post/raycast-4/), [VoltAgent teardown](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/raycast/DESIGN.md)).
- **Borrow** — Cmd-K command palette as primary nav. Hairline 1px borders with 6–10px card radii. Saturated accents reserved only for category illustrations.
- **Don't borrow** — The diagonal red wordmark stripes — distinctive to Raycast's brand; would feel borrowed elsewhere.

### 4. Resend — <https://resend.com>

- **Why praised** — Frequently cited alongside Linear and Stripe as making "craftsmanship a first principle" in the Evil Martians [100 devtool landing pages](https://evilmartians.com/chronicles/we-studied-100-devtool-landing-pages-here-is-what-actually-works-in-2025) study.
- **Borrow** — Code-snippet hero. Tightly typed two-column "feature + example" rows. Restrained motion only on hover.
- **Don't borrow** — Email-specific iconography; not transferable.

### 5. Cursor — <https://cursor.com>

- **Why praised** — Black canvas, oversized headline, single demo video; one of the cleanest AI-dev-tool sites of 2025.
- **Borrow** — One giant in-context demo as the only hero asset. Dark-by-default with a clean light toggle. Ruthless feature-count discipline (under 6 sections).
- **Don't borrow** — The silver "halo" gradient hero — already a 2025 AI-tool cliché.

### 6. v0.dev — <https://v0.app>

- **Why praised** — The chat-input hero doubles as the product; "try it in the hero" is the cleanest possible demo.
- **Borrow** — Functional input-in-hero (the searchbox can be the hero itself). Generated-result preview cards below. Tabbed code/preview switcher.
- **Don't borrow** — The AI-shimmer animation; will date fast.

### 7. Tldraw — <https://tldraw.dev>

- **Why praised** — Interactive canvas embedded directly in the marketing site lets visitors *use* the product before signing up.
- **Borrow** — An interactive embed as the "memorable moment" (e.g., a simulated walkthrough). Playful but restrained micro-copy. Inline iframe demos beside feature copy.
- **Don't borrow** — The hand-drawn aesthetic — wrong tone for an infra / agent / data product.

### 8. Cal.com — <https://cal.com>

- **Why praised** — Open-source-flavored monochrome with embeddable demos; cited in pattern libraries like [siiimple](https://siiimple.com/cal-com/) and [getdesign.md](https://getdesign.md/cal/design-md).
- **Borrow** — Live-embed demo block. Developer-credible neutral palette. "Open source" badge treatment near the hero.
- **Don't borrow** — The dense pricing tier comparison — too enterprise for a small product or personal project.

---

## A ninth category — component/motion donors (not whole-site)

The eight donors above are whole-site aesthetic exemplars — canvas, hierarchy, section rhythm. A
different, narrower kind of donor is worth naming separately: sites/libraries you raid for **one
technique**, not an overall direction.

- **ReactBits — <https://reactbits.dev>** (165+ animated React components, 46.6k★, MIT+Commons
  Clause). Not a fit for "what should this site feel like overall" — it's a fit for "I need one
  memorable motion moment" (animated text, ambient/WebGL backgrounds, scroll-triggered reveals). The
  transferable lesson isn't the components themselves (they'll drift as the site updates) but the
  **per-component dependency-minimalism**: pick the lightest animation engine per effect (CSS-only,
  GSAP, OGL/three.js, Matter.js) rather than one house animation runtime for everything. Full note +
  refresh guidance: [`design-sources/reactbits.md`](design-sources/reactbits.md).
- **Astro official Showcase — <https://astro.build/showcase/>** — the reference for what Astro looks
  like at *enterprise* production scale (The Guardian, Google Firebase, Trivago, Microsoft
  properties), distinct from this file's marketing-site aesthetic donors. Use when the brief is
  specifically an Astro build and needs a same-stack precedent, not just an aesthetic one. See
  [`design-sources/additional-sources.md`](design-sources/additional-sources.md).

## Synthesis — what these sites have in common

1. **Monochrome canvas with one accent color**, used sparingly on CTAs and category markers. Never two accents.
2. **Typography-led hierarchy** — large headlines (48–96px), generous line-height, system stack or one well-licensed display font (Inter, Geist, IBM Plex). No more than two type sizes per section.

### Live tension — Inter as a display face (unresolved)

Item 2 above recommends Inter as one of three acceptable display faces for the general case this
file catalogs. [`brand-guidance-authoring`](../skills/brand-guidance-authoring/reference/anti-pattern-catalogue.md)'s
`AP-01` bans a generic-sans face — Inter included — as a project's brand-voice/display face by
default, for a narrower reason: it is the fastest visual tell of an unstyled, agent-default build.
Both are correct in their own scope. This file's recommendation above is **not rewritten** to match
the catalogue's default — doing so would itself be a unilateral resolution, made in the file holding
the opposing position. The genuinely contested case (a project whose brand voice *is* Inter) is
exactly what `AP-01`'s `override` block, with a required one-line rationale, exists to resolve
per-project — see the [`gold-standard-website-pipeline`](../skills/gold-standard-website-pipeline/SKILL.md)
G3 criterion this catalogue is wired into. This tension is deliberately left unresolved here.
3. **Real product UI as the hero**, not stock illustrations or 3D renders. Static screenshot beats animated render. If you must move, move once.
4. **Sequential section rhythm** — every section is the same shape (~1 column on mobile, 2 columns desktop), generous vertical spacing (~96–160px between sections). Predictable cadence is calming.
5. **One or two interactive beats** that earn their place: command palette, in-hero demo, hover-to-reveal cards. Everything else stays still.

## Avoid — 2024 tropes that already look dated

Four of these are the prose form of catalogue rows `AP-07`–`AP-10` in
[`brand-guidance-authoring`](../skills/brand-guidance-authoring/reference/anti-pattern-catalogue.md)'s
anti-pattern catalogue; the catalogue is the canonical, per-project-overridable version — edit it
there, not here.

- **Bento grids on every section** ("Japanese lunch box" fatigue, per [studiomeyer 2026 reality check](https://studiomeyer.io/en/blog/webdesign-trends-2026-reality-check)).
- **Glassmorphism beyond modals/nav** — accessibility regressions plus aesthetic cliché.
- **AI-shimmer / silver-halo hero gradients** — peaked in 2025; signals "AI tool launched in 2024–25" the way Material Design signaled "Android app launched in 2016".
- **Scroll-jacked horizontal panels** — disorienting; breaks browser back/forward; the discourse has turned hostile to them.
- **Emoji-as-icon in feature blocks** — reads as a low-effort placeholder once it's a default.
- **Auto-playing 3D hero scenes** — burn the motion budget on the *one* memorable beat, not on the hero.

---

## How to apply this

When picking the aesthetic for a new site:

- **Anchor on Linear + Vercel** for the overall canvas (monochrome, faint grid, typography discipline).
- **Pick ONE of {command-palette nav, in-hero functional demo, interactive embed below the fold}** as the memorable beat. Two max. Adding a third dilutes the others.
- **Decide on the one accent color first**, before anything else — it constrains every later decision. Default: cool teal (`#14b8a6`-ish) or electric violet (`#8b5cf6`) for technical/agent products; warm coral or amber for finance/regulatory; classic blue for general SaaS.
- **Write the headline before you draw the hero.** If the headline needs the visual to make sense, rewrite the headline.

When reviewing an existing site against this reference:

- Count the accent colors. >1 is a smell.
- Count the interactive beats. >2 is a smell.
- Count the sections on the home page. >6 is a smell.
- Look for any of the "avoid" tropes and flag them.

---

## Confidence notes

- **High confidence** on Linear, Vercel, Raycast as donors — these are repeatedly cited in 2024–2026 design discourse and have stable design teams behind them.
- **Medium confidence** on Resend, Cursor, v0, Tldraw, Cal.com — strong recent reputation, less longitudinal evidence. Re-check at the next refresh.
- **Open question** flagged by the original research: hero choice (input-driven vs. canvas-driven) depends on whether the site's primary job is *catalog browsing* or *walkthrough demonstration*. Decide upfront.

## Related — the raw source layer

[`design-sources/`](design-sources/) holds the broader, less-curated research this file and
`gold-standard-website-references-2026.md` draw from — dated, sourced notes on specific external
repos/sites (including CollectUI's pattern-category taxonomy and a 12-source broad sweep across
Astro, component libraries, and accessibility pattern references). Check there before re-researching
a source from scratch.

## Sources

- [Evil Martians — 100 devtool landing pages](https://evilmartians.com/chronicles/we-studied-100-devtool-landing-pages-here-is-what-actually-works-in-2025) — primary multi-site survey
- [LogRocket — Linear design as a trend](https://blog.logrocket.com/ux-design/linear-design/)
- [Linear changelog 2024-03-20](https://linear.app/changelog/2024-03-20-new-linear-ui)
- [Setproduct — Blueprint Grid guide](https://www.setproduct.com/blog/complete-guide-to-blueprint-grid-design)
- [Vercel Geist Grid](https://vercel.com/geist/grid)
- [Lapa Ninja — Raycast](https://www.lapa.ninja/post/raycast-4/), [VoltAgent design teardown](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/raycast/DESIGN.md)
- [siiimple — Cal.com](https://siiimple.com/cal-com/), [getdesign.md — Cal](https://getdesign.md/cal/design-md)
- [studiomeyer — 2026 webdesign reality check](https://studiomeyer.io/en/blog/webdesign-trends-2026-reality-check)
