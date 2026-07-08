# Web Design Plugin — Team Constitution

> Team constitution for the `web-design` Claude Code plugin. Bundles **7** specialist agents covering web design and build: site architecture and IA, UX, visual design and design systems, frontend implementation, content strategy, accessibility, performance, and technical SEO. (Visual / content / SEO is split across complementary specialists; the team is 7 named agents.)
>
> Designed for full web engagements — from greenfield discovery through launch and ongoing optimization. Assumes the user has a real site to ship, not a coding tutorial.
>
> **Orientation:** this file is **domain-specific** to web design. For the domain-neutral team constitution inherited by every plugin (architect, generic frontend-coder, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`web-architect`](agents/web-architect.md) | Site architecture, information architecture, tech-stack selection, hosting, CDN, build pipeline, repo structure | Greenfield architecture, re-platform decisions, stack trade-offs, build / hosting topology |
| [`ux-designer`](agents/ux-designer.md) | Wireframes, user flows, screen layouts, conversion design, interaction design, usability heuristics | Pre-build UX, screen flows, conversion-focused redesigns, usability reviews |
| [`visual-designer`](agents/visual-designer.md) | Brand systems, typography, color, layout grid, design tokens, component visual style | Brand-from-scratch, design-system spec, visual review, theming |
| [`frontend-implementer`](agents/frontend-implementer.md) | Modern web frontend (HTML/CSS, vanilla JS, React, Astro, Next), component libraries, responsive patterns, build integration | UI build / refactor, design → code, component-library work |
| [`content-strategist`](agents/content-strategist.md) | Site copy, content hierarchy, microcopy, SEO content, content style guide, content audit | Content audit, copy authoring, voice-and-tone design, content-modeling for CMS |
| [`accessibility-auditor`](agents/accessibility-auditor.md) | WCAG 2.2 AA/AAA, ARIA, keyboard navigation, screen-reader behavior, color contrast, reduced-motion preferences | Pre-launch a11y audit, remediation prioritization, ongoing review |
| [`performance-engineer`](agents/performance-engineer.md) | Core Web Vitals (LCP / CLS / INP), image / font optimization, CDN strategy, caching, JS budget, third-party hygiene | Performance review, slow-page diagnosis, pre-launch budget enforcement |

(The roster covers the 8 disciplines in the [`docs/plugin-roadmap-analysis.md`](../../docs/plugin-roadmap-analysis.md) scope; technical SEO is owned by the `web-architect` for indexability and meta concerns, and by `content-strategist` for content-SEO, with `accessibility-auditor` weighing in on the headings/structure side. If technical SEO grows past these handoffs, split it out into a dedicated specialist in a future version.)

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns their slice and the Team Lead re-dispatches.

---

## 2. Routing rules (Team Lead)

- **"Build a new marketing site"** → `web-architect` (stack + hosting + IA) → `ux-designer` (wireframes + flows) → `visual-designer` (brand + tokens) → `content-strategist` (copy) → `frontend-implementer` (build) → `accessibility-auditor` + `performance-engineer` (pre-launch gates).
- **"Audit this existing site"** → run in parallel: `accessibility-auditor` (a11y), `performance-engineer` (CWV), `content-strategist` (content quality + SEO content), `web-architect` (technical SEO + IA). Team Lead synthesizes.
- **"This page is slow"** → `performance-engineer` (root-cause CWV); pull in `frontend-implementer` for code changes, `visual-designer` for asset compression decisions.
- **"Our brand needs a refresh"** → `visual-designer` (brand system); pull in `content-strategist` for voice-tone alignment.
- **"This form has poor conversion"** → `ux-designer` (flow + interaction); pull in `content-strategist` for microcopy.
- **"Set up the design system"** → `visual-designer` (token spec + components) → `frontend-implementer` (token-to-code wiring + Storybook).
- **"Our site fails WCAG 2.2 AA"** → `accessibility-auditor` (audit + prioritized remediation) → `frontend-implementer` (code changes).
- **"Search ranking dropped"** → `web-architect` (technical SEO sweep) + `content-strategist` (content audit) in parallel.
- **Anything touching auth, secrets, untrusted input handling, or user data** → mandatory `ravenclaude-core` `security-reviewer`.

---

## 3. Cross-cutting house opinions (every agent enforces)

Domain-specific opinions live in each agent's own file. These plugin-wide opinions are inherited by all **7**.

1. **Accessibility is a P1 design constraint.** Not a polish item, not "phase 2." Designed in from wireframe stage. WCAG 2.2 AA is the floor.
2. **Performance has a budget.** Every page declares its weight + LCP / CLS / INP targets before development starts. Budgets are enforced in CI where possible.
3. **Mobile-first or it's not done.** Design narrowest first, expand up. Desktop is a layout target, not the starting point.
4. **Design tokens, not hardcoded values.** Color, typography, spacing, radius, shadow, motion all flow through tokens. Hardcoded `#3b82f6` in a component is a smell.
5. **Semantic HTML before ARIA.** Reach for the right element. Only use ARIA when no semantic element fits, and never to *add* what semantics provides for free.
6. **Content informs design.** Real copy in mocks. Lorem ipsum is a smell that hides layout problems caused by realistic text lengths.
7. **No layout shift after first paint.** Reserve space for images, fonts, ads, embeds. CLS > 0.1 ships only with a written justification.
8. **One CTA per screen, at most two.** Conversion design is choosing what to remove, not what to add.
9. **Static-first.** Pre-render where possible; client-side rendering needs a reason. SSG > SSR > CSR (in that order of preference).
10. **SEO + a11y converge.** Headings, alt text, semantic structure, link text serve both. Treat them as one surface.
11. **Third-party scripts are debt.** Every third-party script (analytics, chat, A/B, fonts) costs perf + privacy + reliability. Catalogue them, audit them.
12. **One source of truth per design decision.** Token defined in one place; documented in one place; consumed everywhere. Drift = bug.
13. **Print and reduced-motion are not afterthoughts.** Print stylesheets for content sites; `prefers-reduced-motion` honored on every animation.

---

## 4. Anti-patterns every agent flags

- WCAG 2.2 AA failures that have been "open" for > 30 days without remediation
- Image > 500 KB on a page that loads above the fold (a JPEG over a clean PNG, an unoptimized hero image)
- Inline `style="color: #3b82f6"` or class names that hardcode color hex values
- `<img>` without `alt` (even decorative images need `alt=""`)
- Layout shift after first paint that's not from intentional user interaction
- More than 2 CTAs per screen
- Page weight > 1.5 MB total transfer for a marketing site
- LCP > 2.5s, CLS > 0.1, INP > 200ms on the production page in the field (CrUX or RUM data)
- Heading-level skips (h1 → h3 with no h2)
- Link text that says "click here" or "read more" with no destination context
- Forms without labels (placeholder-as-label is broken for a11y)
- Color used as the *only* signifier (error states, status indicators)
- Third-party scripts in `<head>` that block render
- Hardcoded font sizes / line-heights / spacing that should be tokens
- Marketing-site pages with no `<title>` or `<meta description>`
- Pages with `<meta name="robots" content="noindex">` accidentally shipping to production
- Pages with broken or missing OG / Twitter Card metadata for a sharable site
- A11y-focused only on visible UI, ignoring the keyboard / screen-reader experience entirely
- Animation with no `prefers-reduced-motion: reduce` fallback
- Print stylesheet absent on a content-heavy site

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

This plugin inherits the Capability Grounding Protocol from `ravenclaude-core`. Before any web-design agent says "I can't do X" or "this isn't possible", it must:

1. **Check available skills first** — `design-system-audit`, `card-tile-ui`, `accessibility-review`, `core-web-vitals-tuning`, `seo-technical-audit`, `information-architecture`, `conversion-design`, `content-audit`, `design-tokens-scaffolding`, `third-party-script-hygiene`, `fluent-react-implementation`, `static-site-implementation`, and the `gold-standard-website-pipeline` orchestration pipeline (for a whole new-website build), plus the core `frontend-coder` capabilities.
2. **Check for partial capability** — can part of the task be done in this tool while the rest is a hand-off?
3. **Try alternative implementation paths from easiest to most difficult before declaring blocked.** When one approach fails — a CSS feature isn't supported in the target browser, a CMS API doesn't expose what's needed, a library is overweight for the budget — enumerate at least 2–3 alternative approaches, rank them by cost, and try the next-easiest one before reporting blocked. Web-design alternatives often include: a different layout primitive (grid vs flex vs subgrid), a lighter library, a build-time vs runtime split, a static-first refactor, a `<picture>`/`srcset` instead of JS image-loading. See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md) for the full rule.
4. **Consider team composition** — is there a generic agent in `ravenclaude-core` (architect, frontend-coder, designer) that can complete the work?
5. **Escalate uncertainty** — route back to the Team Lead with a clear explanation of what was checked AND what was attempted.

**Mandatory phrasing when uncertain:**
> "After trying [Approach A — outcome] and [Approach B — outcome], I cannot fully complete this because [specific reason]. The remaining options I considered but did not attempt are [X (ruled out because Y)]. I can help with [partial scope]. I recommend [escalation / next-best path]."

The architectural definition of the Grounding Protocol lives in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md) (`Capability Grounding Protocol` section). The reference implementation skill is [`../power-platform/skills/grounding-protocol/SKILL.md`](../power-platform/skills/grounding-protocol/SKILL.md) (consumers who install `power-platform` get the skill file directly; otherwise the inline §5 above is authoritative for this plugin).

---

## 6. Output Contract (every web-design agent)

Every report from every web-design agent **must** include the following block at the end of its human-readable Markdown report:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Standards cited: <WCAG version + level, CWV thresholds, Schema.org types, etc.>
Browsers / devices tested: <if applicable — "n/a" otherwise>
Perf / a11y budget impact: <budget delta if known, or "n/a">
Open questions: <anything the Team Lead needs to decide before this can ship>
Grounding checks performed: <brief note on skills/rules reviewed before any limitation was stated>
```

**Mandatory lines:**
- `Standards cited:` — WCAG version (2.2 AA is the default floor), CWV thresholds, Schema.org types, OG / Twitter Card spec versions, etc.
- `Perf / a11y budget impact:` — for any change that could affect performance or accessibility, the impact relative to the project's documented budget.
- `Grounding checks performed:` — required when any limitation is stated.

After the Markdown report, **emit the cross-plugin Structured Output Protocol JSON block**:

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<role or null>", "reason": "..."},
  "confidence": 0.0,
  "risks_or_open_questions": ["..."],
  "next_actions": ["..."],
  "standards_cited": ["..."],
  "budget_impact": {"perf": "<string or null>", "a11y": "<string or null>"},
  "tested_on": ["..."]
}
---RESULT_END---
```

The JSON `standards_cited`, `budget_impact`, and `tested_on` fields mirror the mandatory Markdown lines. Both surfaces must be consistent. `confidence` ≥ 0.7 triggers Cited-Adjudicator Escalation per [`../ravenclaude-core/rules/agent-collaboration.md`](../ravenclaude-core/rules/agent-collaboration.md).

See [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md).

---

## 7. Automated anti-pattern checks (hooks)

The `hooks/` directory ships [`check-web-anti-patterns.sh`](hooks/check-web-anti-patterns.sh) — a PostToolUse Edit/Write/MultiEdit hook that flags the most common mechanically-detectable violations on real edits:

| Check | Triggers on | Rule (§3 / §4) |
|---|---|---|
| Oversized raster image committed (> 500 KB jpg / png / webp) | Image files in `src/`, `public/`, `assets/`, `static/` | §4 — image > 500 KB above-the-fold |
| `<img>` tag missing `alt` attribute | `*.html`, `*.jsx`, `*.tsx`, `*.astro`, `*.vue`, `*.svelte`, `*.md` (some markdown HTML) | §3 #5, §4 — semantic HTML, `<img>` missing `alt` |
| Hardcoded hex color in JSX / TSX / CSS (outside `tokens.*`) | `*.css`, `*.scss`, `*.jsx`, `*.tsx`, `*.vue`, `*.svelte` | §3 #4 — design tokens, not hardcoded values |
| HTML page missing `<title>` or `<meta name="description">` | `*.html` (excluding fragment / partial files) | §4 — marketing-site page with no title / description |
| `<meta name="robots" content="noindex">` in shipped page | `*.html` | §4 — noindex accidentally in production |

The hook is **advisory by default** (prints to stderr, doesn't block). To enforce in CI, flip the final `exit 0` to `exit 1`. The plugin's [`hooks/hooks.json`](hooks/hooks.json) wires it into PostToolUse.

The hook is conservative — it only fires on conventional web file extensions / locations, so unrelated edits aren't flagged.

---

## 8. Skills in this plugin

| Skill | Primary agent | What's inside |
|---|---|---|
| [`skills/design-system-audit/SKILL.md`](skills/design-system-audit/SKILL.md) | `visual-designer`, `frontend-implementer` | Auditing a brand / design system for consistency, completeness, token coverage, dark-mode readiness |
| [`skills/card-tile-ui/SKILL.md`](skills/card-tile-ui/SKILL.md) | `visual-designer`, `frontend-implementer` | Designing/implementing an Intercom-style **card / tile UI** — soft-shadowed rounded white tiles on a monochromatic canvas, multi-pane navigation-rail layout, one restrained accent (hairlines / outlines / single CTA), plus the dark-theme-residue audit that fixes a "card" page rendering flat |
| [`skills/accessibility-review/SKILL.md`](skills/accessibility-review/SKILL.md) | `accessibility-auditor` | WCAG 2.2-aligned audit checklist (semantics, ARIA, keyboard, contrast, focus, motion); severity guide; tooling notes |
| [`skills/core-web-vitals-tuning/SKILL.md`](skills/core-web-vitals-tuning/SKILL.md) | `performance-engineer` | Diagnosing and improving LCP / CLS / INP with the canonical fix-by-symptom map |
| [`skills/seo-technical-audit/SKILL.md`](skills/seo-technical-audit/SKILL.md) | `web-architect`, `content-strategist` | Technical SEO sweep (crawlability, schema, sitemaps, OG / Twitter cards, hreflang, structured data) |
| [`skills/information-architecture/SKILL.md`](skills/information-architecture/SKILL.md) | `web-architect`, `ux-designer` | Sitemap shapes, URL taxonomy, navigation patterns, card-sort discipline, content model + CMS implications, redirect plan for re-architecture |
| [`skills/conversion-design/SKILL.md`](skills/conversion-design/SKILL.md) | `ux-designer`, `content-strategist` | Funnel definition, one-CTA discipline, form-field reduction, trust-signal placement, CTA microcopy, pricing-page patterns, measurement plan |
| [`skills/content-audit/SKILL.md`](skills/content-audit/SKILL.md) | `content-strategist`, `web-architect` | Full content inventory, scoring across 5 dimensions, KKCR matrix (Keep / Consolidate / Kill / Rewrite), redirect plan, governance cadence |
| [`skills/design-tokens-scaffolding/SKILL.md`](skills/design-tokens-scaffolding/SKILL.md) | `visual-designer`, `frontend-implementer` | Primitive vs semantic tokens, scale design, light/dark mode, W3C token JSON + Style Dictionary pipeline, Tailwind / Shadcn integration, drift audit |
| [`skills/third-party-script-hygiene/SKILL.md`](skills/third-party-script-hygiene/SKILL.md) | `performance-engineer`, `web-architect` | Third-party inventory, category budgets, loading patterns, consent-mode v2 gating, CSP integration, CWV impact measurement, retirement criteria |
| [`skills/fluent-react-implementation/SKILL.md`](skills/fluent-react-implementation/SKILL.md) | `frontend-implementer`, `visual-designer` | The 7-step playbook for building a **Fluent UI v9 + React** site + implementing a brand as a Fluent design language — FluentProvider, BrandVariants → `createLightTheme`/`createDarkTheme`, Griffel `makeStyles` + tokens, dark/high-contrast, Next App Router SSR (the `use client` + `renderToStyleElements` boundary) / Astro islands, custom components on Fluent primitives, themed Storybook, the when-not-to-use-Fluent guard |
| [`skills/static-site-implementation/SKILL.md`](skills/static-site-implementation/SKILL.md) | `frontend-implementer` | The **generic non-React static build** — semantic HTML + token-driven CSS (custom properties, grid/flex, container queries, logical properties), SSG-first Astro/11ty/Hugo or plain HTML+CSS with islands only where earned; reflow-to-320px, in-markup performance (AVIF/WebP srcset, lazy-load, font-display, critical CSS), accessible markup. The static-stack complement to `fluent-react-implementation`; dispatched by `gold-standard-website-pipeline` G5 for non-React stacks |
| [`skills/gold-standard-website-pipeline/SKILL.md`](skills/gold-standard-website-pipeline/SKILL.md) | Team Lead (orchestrates all 7 agents) | The **orchestration pipeline over all the skills above** — nine fail-closed gates (discovery → IA → tokens → content → build → a11y → perf → SEO/AEO → pre-launch sign-off) for any new marketing / web-app / ecommerce build, each with checkable WCAG 2.2 / CWV / SEO acceptance bars + the owning agent→skill dispatch + a lab-vs-field CWV split, ending in one Go / Conditional / No-go. Driven by `/web-design:new-website` |

---

## 8a. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/design-references.md`](knowledge/design-references.md) | Scoping a new site, pitching a new aesthetic direction, or evaluating an existing site against the field. Curated reference set of marketing / product sites praised in 2024–2026 design discourse as "cutting edge yet simple" — pattern donors, what to borrow, what to avoid. Refreshed roughly annually. |
| [`knowledge/gold-standard-website-references-2026.md`](knowledge/gold-standard-website-references-2026.md) | The exemplar set behind the `gold-standard-website-pipeline` — **10 gold-standard websites** (marketing / web-app / ecommerce) each mapped to the pipeline gate its lesson informs, plus **10 gold-standard agentic website-building tools/plugins** each mapped to the pipeline-craft idiom it teaches. Distilled from this session's research dossiers; unverifiable claims flagged. Owned by all 7 agents via the pipeline. Dated 2026-07-06. |
| [`knowledge/card-tile-ui-pattern-2026.md`](knowledge/card-tile-ui-pattern-2026.md) | Designing or auditing a card-driven SaaS surface (dashboard, inbox, admin console, catalog) in the **Intercom-style card / tile** pattern. Anatomy, donor study, color/elevation discipline, a11y gotchas, the dark-theme-residue audit checklist, and the worked example of fixing this marketplace's own three generated surfaces. Backs the `card-tile-ui` skill. Owned by `visual-designer` + `frontend-implementer`. Dated 2026-06-02. |
| [`knowledge/modern-web-stacks-2026.md`](knowledge/modern-web-stacks-2026.md) | Choosing a stack / rendering model — the rendering-model table (SSG/ISR/SSR/RSC/CSR/islands) + framework decision tree (Astro / Next.js 16 RSC / React Router / SvelteKit / Eleventy / Hugo). Owned by `web-architect` + `frontend-implementer`. Dated 2026-05-28. |
| [`knowledge/modern-css-2026.md`](knowledge/modern-css-2026.md) | Building UI with current CSS — container queries, `:has()`, cascade layers, subgrid, `oklch()` color, View Transitions, Tailwind v4 (Oxide / CSS-first `@theme`), logical properties, native nesting. Owned by `visual-designer` + `frontend-implementer`. Dated 2026-05-28. |
| [`knowledge/web-platform-capabilities-2026.md`](knowledge/web-platform-capabilities-2026.md) | Performance + platform — 2026 Core Web Vitals thresholds (LCP/INP/CLS; INP is the most-failed), Speculation Rules API, bfcache, `fetchpriority`, native `<dialog>`/Popover, WCAG 2.2 + the EU Accessibility Act. The dated freshness anchor. Owned by `performance-engineer` + `web-architect`. Dated 2026-05-28. |
| [`knowledge/answer-engine-optimization-2026.md`](knowledge/answer-engine-optimization-2026.md) | Discoverability in the AI-search era — AEO/GEO: earning **citations** in AI Overviews / ChatGPT / Perplexity / Gemini / Claude (vs classic SERP rank). Answer-ready structure, FAQ/entity schema + knowledge-graph, E-E-A-T, the `llms.txt` debate (hedged), AI crawler access, and **AI Share of Voice** measurement. Complements the `seo-technical-audit` skill (classic technical SEO). Owned by `content-strategist` + `web-architect`. Dated 2026-05-28. |
| [`knowledge/design-systems-and-component-architecture-2026.md`](knowledge/design-systems-and-component-architecture-2026.md) | Designing/implementing a design system — the 3 layers (tokens → components → patterns), DTCG tokens + Style Dictionary, component-API discipline (composition, controlled/uncontrolled, polymorphism, a11y-built-in), **headless vs styled**, Storybook + monorepo/versioning, and a "which component foundation?" decision tree. The foundation under the Fluent-UI-v9-for-web work. Complements `design-tokens-scaffolding` + `design-system-audit`. Owned by `visual-designer` + `frontend-implementer`. Dated 2026-05-28. |
| [`knowledge/web-design-decision-trees.md`](knowledge/web-design-decision-trees.md) | Facing a recurring branching decision — the **primary tree file** (13 Mermaid trees): a11y native-vs-ARIA, CWV-by-symptom, rendering strategy, image format, design-system foundation, IA, conversion, responsive, CMS, motion, dark mode, form labels, content SEO. Traverse top-to-bottom before choosing. Added PR #315. |
| [`knowledge/css-architecture-and-a11y-remediation-decision-trees.md`](knowledge/css-architecture-and-a11y-remediation-decision-trees.md) | Two **complementary** Mermaid trees to the primary file: **CSS architecture / styling-approach selection** (RSC-aware, zero-runtime-default: Tailwind v4 `@theme` vs CSS Modules / modern CSS vs zero-runtime vs runtime CSS-in-JS) and **accessibility-remediation prioritization** (P0 launch-blocker → P1 fast-follow → P2 dated-backlog → P3 enhancement, by user impact not tool count). Owned by `visual-designer` + `frontend-implementer` (CSS) and `accessibility-auditor` (remediation). Added 2026-06-05. |
| [`knowledge/fluent-react-for-web-2026.md`](knowledge/fluent-react-for-web-2026.md) | Building **Fluent UI v9 + React** websites — `@fluentui/react-components`, FluentProvider, design tokens, **BrandVariants → `createLightTheme`/`createDarkTheme`** (the design-language core), Griffel styling, dark/high-contrast (+ the body-bg gotcha), Next.js App Router **SSR** (`use client` + `renderToStyleElements`; React 19/Next 15 friction), implementing a design language in Fluent, and when NOT to use Fluent. Shares the Fluent-v9 version source with `power-platform`'s PCF doc. Owned by `frontend-implementer` + `visual-designer`. Dated 2026-05-28. |
| [`../ravenclaude-core/knowledge/visual-feedback-loop.md`](../ravenclaude-core/knowledge/visual-feedback-loop.md) | Building/refining any visual surface and you want to *see it before calling it done* — the render→see→critique→iterate loop, the two ways to "see" (screenshot via `chrome-devtools-mcp` / structural coordinate read), the objective stopping signals (Lighthouse a11y/perf, zero console errors), and the render-loop security rules (no-echo of untrusted page output, synthetic data for untrusted pages). The cross-plugin canon behind each agent's **Visual feedback loop** section. Owned by core; consumed here by `frontend-implementer` + `visual-designer` + `accessibility-auditor` + `performance-engineer`. Dated 2026-06-09. |

The `visual-designer`, `ux-designer`, `frontend-implementer`, and `web-architect` agents all carry a compact "Pattern library priors" section that summarizes this knowledge inline; the full briefs in `knowledge/` are the source of truth and get re-read on demand. The three `*-2026.md` docs are dated freshness anchors — the Researcher staleness sweep re-dates them (the web platform ships continuously).

---

## 8b. Scenarios bank & runnable tooling (enabled 2026-06-05)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md) and the bank's own [`scenarios/README.md`](scenarios/README.md)). The first four field notes: WCAG contrast + focus-order audit, LCP perf-budget hero-image, design-token drift / hardcoded hex, and CLS layout-shift + SEO-meta regression. Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, and **never let a scenario override the cited WCAG / CWV standard or a verified browser-support fact** — those are the canonical bank's lane. Scenarios carry no client-identifying info or real site names. The most-likely-to-benefit specialists — `accessibility-auditor`, `performance-engineer`, `visual-designer`, `content-strategist` — should check the bank when a situation matches.
- **Runnable checker** — [`scripts/contrast_ratio.py`](scripts/contrast_ratio.py) (stdlib only, Python 3.8+) makes the WCAG contrast-ratio arithmetic mechanical and CI-gateable: `pair` (one foreground/background, with normal-text / large-text / UI-component thresholds for SC 1.4.3 + SC 1.4.11) and `check` (batch-assert a set of token/usage pairings stays in contrast — the token-drift guard). It is a **checker, not a renderer** — you supply the *actual displayed* colors (measure against the real background a surface renders on, gradients/overlays flattened, every interactive state); a nominal pass against the wrong background is not a pass. Owned primarily by `accessibility-auditor` + `visual-designer`. The contrast math is verified against W3C WCAG techniques (see §13).

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/design-brief.md`](templates/design-brief.md) | Project kickoff / discovery deliverable |
| [`templates/site-architecture.md`](templates/site-architecture.md) | IA + page-type taxonomy + navigation spec |
| [`templates/accessibility-audit-report.md`](templates/accessibility-audit-report.md) | WCAG audit output format |
| [`templates/design-system-spec.md`](templates/design-system-spec.md) | Token + component visual spec |
| [`templates/launch-checklist.md`](templates/launch-checklist.md) | Pre-launch verification across all disciplines |
| [`templates/content-style-guide.md`](templates/content-style-guide.md) | Voice, tone, terminology, microcopy patterns |
| [`templates/seo-audit-report.md`](templates/seo-audit-report.md) | Technical + content SEO findings |
| [`templates/performance-budget.md`](templates/performance-budget.md) | Per-page performance budget |

---

## 10. Escalating out of the web-design team

Web-design agents stay within web design. When a question crosses out, escalate via the Team Lead to:

- **`ravenclaude-core` `architect`** — when the question crosses into broader systems architecture (backend, API design, data modeling beyond what the frontend consumes).
- **`ravenclaude-core` `backend-coder`** — when server-side code is needed (API endpoint, SSR / RSC server logic, background jobs).
- **`ravenclaude-core` `security-reviewer`** — mandatory for any change touching auth, sessions, user-data handling, untrusted input, file upload, third-party integration.
- **`ravenclaude-core` `deep-researcher`** — when an answer requires verifying current browser-support data, current WCAG / spec status, or competing approach analysis.
- **`ravenclaude-core` `documentarian`** — when the output is stakeholder prose (proposal, design rationale memo, post-launch report).
- **`ravenclaude-core` `designer`** — the cross-domain designer agent overlaps with this plugin's `ux-designer` / `visual-designer` on generic visual artifacts (slide decks, infographics). Route to the core `designer` for non-web visual work.
- **`ravenclaude-core` `project-manager`** — multi-month engagements with RAID / status / stakeholder needs.
- **`ravenclaude-core` `tester-qa`** — test plan design beyond visual / a11y / perf (functional, integration, regression).
- **`finance` / `regulatory-compliance` plugin agents** (when those plugins are installed in the same consumer project) — when the site has finance / regulatory content (disclosures, cookie consent, regulator-facing claims). If neither plugin is installed, escalate through `ravenclaude-core/architect` for routing.

When in doubt, the web-design team **declines and asks the Team Lead** rather than guessing outside their lane.

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Capability Grounding Protocol (upstream): [`../power-platform/skills/grounding-protocol/SKILL.md`](../power-platform/skills/grounding-protocol/SKILL.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Cited-Adjudicator Escalation: [`../ravenclaude-core/rules/agent-collaboration.md`](../ravenclaude-core/rules/agent-collaboration.md)
- Sister plugins (when installed alongside): `finance` and `regulatory-compliance` — web content that surfaces finance or regulatory disclosures routes through their teams. See [`../../docs/plugin-roadmap-analysis.md`](../../docs/plugin-roadmap-analysis.md) for the marketplace plan.
- Marketplace-wide developer guide: [`../../CLAUDE.md`](../../CLAUDE.md)

---

## 12. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

Web design ships and edits real HTML/CSS/JS, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — diagnostics, completion, go-to-definition — on the markup/style/script files they touch, instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures three language servers covering this plugin's surface (CSS/SCSS/LESS, HTML, and ESLint for JS/TS) — deliberately **markup/style-centric**, not the app-grade TypeScript posture `frontend-engineering` carries:

| Surface | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| CSS / SCSS / LESS | vscode-css-language-server | `vscode-css-language-server --stdio` | `npm install -g vscode-langservers-extracted` |
| HTML | vscode-html-language-server | `vscode-html-language-server --stdio` | `npm install -g vscode-langservers-extracted` |
| ESLint (JS/TS) | vscode-eslint-language-server | `vscode-eslint-language-server --stdio` | `npm install -g vscode-langservers-extracted` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one surface degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session.

> All three servers (`vscode-css-language-server`, `vscode-html-language-server`, `vscode-eslint-language-server`) ship in the single **`vscode-langservers-extracted`** npm package (the HTML/CSS/JSON/ESLint servers extracted from VS Code) — so a consumer installs one package for all three. Verified 2026-06-05 against its [npm listing](https://www.npmjs.com/package/vscode-langservers-extracted) and [repo](https://github.com/hrsh7th/vscode-langservers-extracted). Package name + the 2.0.74 LSP-support version are version-volatile — re-confirm at use. (The package is community-maintained with active forks; vet maintenance status at adoption.)

---

## 13. Recommended (not bundled) MCP servers — design-tool & browser context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a server that is first-party-from-the-vendor, authenticated/per-account, metered, or drives a live browser is **recommend-not-bundle**. Every genuinely-useful web-design server below trips at least one of those — documented as recommend-not-bundle with the exact `claude mcp add …` path.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Figma Dev Mode MCP server** (Figma, official — [blog](https://www.figma.com/blog/introducing-figma-mcp-server/) / [docs](https://developers.figma.com/docs/figma-mcp-server/)) | The most-useful design-tool server here, but it is **first-party from the vendor** *and* **authenticated/per-account** (a Figma account + Dev/Full seat), and **metered** — free during beta, "eventually a usage-based paid feature." It is also **write-capable** (agents can write components/variables/auto-layout back to the canvas). Any one of those routes it to recommend-not-bundle. | Desktop variant: enable the MCP server in the Figma desktop app's preferences, then point the client at the local server. Remote (browser) variant: `claude mcp add --transport http figma <hosted-server-url>` and authenticate. Review the toolset (it can **write to the canvas**); gate write-capable use through `ravenclaude-core/security-reviewer`, and note the billing/usage callout. |
| **Chrome DevTools MCP** ([`chrome-devtools-mcp`](https://www.npmjs.com/package/chrome-devtools-mcp), Google / ChromeDevTools, Apache-2.0) | First-party from the vendor; **controls a live Chrome** (record CWV/perf traces, inspect network/console, automate actions) — stateful + side-effecting, not zero-config-read-only. Ships **usage telemetry on by default** (opt out with `--no-usage-statistics`). Strong for in-the-loop CWV / perf-trace work (the `performance-engineer`'s lane). | `claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --no-usage-statistics` — `security-reviewer` gate before adoption. |
| **Playwright MCP** ([`@playwright/mcp`](https://www.npmjs.com/package/@playwright/mcp), Microsoft, Apache-2.0) | First-party from the vendor **and** it **launches/drives a browser** (navigate, click, type, run page scripts) — write-capable/side-effecting, not zero-config-read-only. Useful for a11y-tree snapshots + cross-viewport checks. | `claude mcp add playwright -- npx -y @playwright/mcp@latest` — the `browser_run_code_unsafe`-class tools execute arbitrary page scripts, so gate adoption through `ravenclaude-core/security-reviewer`. |

**Why none are bundled (the load-bearing reasoning):** the Figma Dev Mode server is real and first-party, but it is per-account-authenticated, metered, and write-capable — three independent disqualifiers from the rule's decision table, which sends "per-consumer config / authenticated / billed OR first-party-from-vendor OR write-capable" to **recommend, don't bundle**. The two browser servers are first-party-from-vendor *and* drive a live browser (side-effecting). No invented servers. If a genuinely zero-config, read-only, broadly-useful design/web server appears, revisit with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05: the **Figma Dev Mode MCP server** is Figma's official MCP server with desktop + remote (hosted) variants, in beta and slated to become a **usage-based paid feature**, and it can write components/variables/auto-layout back to the canvas ([figma.com/blog](https://www.figma.com/blog/introducing-figma-mcp-server/), [developers.figma.com](https://developers.figma.com/docs/figma-mcp-server/)). `chrome-devtools-mcp` is Google's official Chrome DevTools MCP (telemetry-on-by-default); `@playwright/mcp` is Microsoft's official Playwright MCP. Versions, tool surfaces, pricing status, and telemetry defaults are volatile — re-confirm at use. The community `GLips/Figma-Context-MCP` exists as a third-party alternative but is not first-party and is not recommended here over Figma's own server.

---

## 14. Value-add completeness (build-out 2026-06-05)

PR #315 already added the consolidated `knowledge/web-design-decision-trees.md` (13 trees), `best-practices/` (30 rules), and `templates/` (8). This build-out adds the net-new gap (scenarios bank + the runtime tier + two complementary trees) and dispositions every value-add menu item below (built or recorded N-A with reason):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (WCAG contrast + focus-order audit, LCP perf-budget hero-image, design-token drift / hardcoded-hex, CLS layout-shift + SEO-meta regression) matching the existing `scenarios/README.md` index + 9-field schema. The contrast scenario was the pre-existing stray partial — kept and reconciled; the other three were added to complete the index. |
| 2 | **Decision-tree knowledge (NEW, complementary)** | **BUILT** — `knowledge/css-architecture-and-a11y-remediation-decision-trees.md`: a **CSS architecture / styling-approach** tree (RSC-aware, zero-runtime-default) + an **accessibility-remediation priority** tree (P0→P3 by user impact). Chosen to **complement** #315's 13-tree file, not duplicate it — styling-approach and a11y-finding-triage were the gaps (design-system *adopt-vs-build* is already covered by the existing "reach for a token system / component foundation" tree). |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §13. The most-useful design server (Figma Dev Mode MCP) is first-party + per-account-authenticated + metered + write-capable; the two browser servers (Chrome DevTools MCP, Playwright MCP) are first-party + browser-driving. All three route to recommend-not-bundle with a `security-reviewer` gate. Documented the `claude mcp add` paths instead. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (vscode-css / vscode-html / vscode-eslint language servers), wired via `plugin.json` `lspServers`. Genuinely useful for a domain that ships real HTML/CSS/JS; markup/style-centric (distinct from `frontend-engineering`'s TS-centric set); binaries install separately via the single `vscode-langservers-extracted` package (§12). |
| 5 | **Runnable script** | **BUILT** — `scripts/contrast_ratio.py` (`pair` + `check` modes), stdlib-only, ruff-clean. Real value: turns the WCAG contrast arithmetic into a CI-gateable check and closes the dangling reference the contrast scenario already pointed at. The complementary perf/CWV checker lives in `frontend-engineering/scripts/perf_budget.py` (the CWV scenarios cross-reference it) — no need to duplicate it here. |
| 6 | **bin/ / monitors / settings / themes / output-styles** | **N-A** — no `rc-*` binary clears the "namespace + prefer Bash-tool skills" bar better than the advisory hook + the new `scripts/` checker; nothing long-running to monitor; no plugin-specific permission surface beyond `ravenclaude-core`. An **output-style** for a design-review format was considered and declined: the §6 Output Contract + the `accessibility-audit-report` / `seo-audit-report` templates already fix the deliverable shape, so an output-style would duplicate them. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 11 skills, 5 commands, 8 templates, 1 advisory hook already cover IA, conversion, design systems/tokens, a11y, CWV, SEO, content, third-party hygiene, and Fluent-React. The new scenarios + 2 trees + contrast checker extend reach without a new agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled; the script is original stdlib-only; MCP/LSP packages are referenced + attributed inline, not vendored). |

---

## 15. Milestones

- **v0.11.2 (and earlier)** — 7-agent web-design team; 11 skills, 5 commands, 8 templates, 1 advisory hook, 30 best-practices. PR #315 added the consolidated `web-design-decision-trees.md` (13 Mermaid trees), the best-practices bank, and the templates.
- **this build-out (2026-06-05)** — value-add completeness: scenarios bank (4 field notes + README index), a complementary `css-architecture-and-a11y-remediation-decision-trees.md` (2 Mermaid trees), `scripts/contrast_ratio.py` (pair + check WCAG contrast checks), `.lsp.json` (CSS/HTML/ESLint) wired via `plugin.json`, and CLAUDE.md §8b/§12–§15 (scenarios + tooling, LSP tier, recommended-not-bundle MCP incl. Figma Dev Mode MCP, value-add disposition, milestones). Bundled-MCP tier dispositioned recommend-not-bundle with reasons (§13).


## Adjacent plugins (added 2026-06-04)

Reciprocal seam to the adjacent-plugins build-out:

- App-grade frontend engineering (React/Next, TypeScript, rendering strategy, state/server-cache, bundle/CWV) → `frontend-engineering`; native iOS/Android & React-Native/Flutter → `mobile-engineering`. This plugin owns brand/UX/marketing-site + the WCAG audit; they engineer the app.
- Ecommerce growth & unit-economics (assortment, pricing, LTV:CAC, AOV, channel spend, the themed-platform-vs-headless payback decision) → `ecommerce-dtc`. This plugin owns the storefront **build** — PDP/cart/checkout UX, conversion-design, product-page a11y/perf/SEO; `ecommerce-dtc` owns the **whether/what** of commerce, upstream of any build. The `gold-standard-website-pipeline` makes the platform-vs-headless decision an explicit **G1 sub-step** that defers to `ecommerce-dtc` when installed (and takes a documented non-specialist stand-in, re-run-once-installed, when it is not). _Cross-ref added 2026-07-06 to close the previously-unclosed seam the pipeline surfaced._
- Security review of any auth / sessions / payments / PII / untrusted-input / file-upload surface → `ravenclaude-core` `security-reviewer` (**mandatory, zero exceptions**). Named in all 7 agents' `## Escalation routes` and enforced pipeline-side at the `gold-standard-website-pipeline` G9 gate, which never waives.
