---
name: static-site-implementation
description: "Build a non-React static site: semantic HTML, token-driven CSS (custom properties, grid/flex, container queries, logical properties), and an SSG-first Astro/11ty/Hugo or plain HTML+CSS build with islands only where earned. Covers reflow to 320px, in-markup performance (AVIF/WebP srcset, lazy-load, font-display, critical CSS), and accessible markup. Used by frontend-implementer; dispatched by gold-standard-website-pipeline G5 for non-React static stacks."
---

# Skill: static-site-implementation

**Purpose.** Build a **non-React static site** end-to-end — semantic HTML + token-driven CSS + an SSG-first (or plain HTML/CSS) pipeline — to the same acceptance bar the rest of the plugin holds React builds to. This is the generic static-stack complement to [`fluent-react-implementation`](../../skills/fluent-react-implementation/SKILL.md): where that skill owns Fluent-UI-v9 + React, this one owns **Astro-static / 11ty / Hugo / plain semantic-HTML+CSS**, the stack the plugin's static-first house opinion (`web-design/CLAUDE.md` §3 #9) and [`gold-standard-website-pipeline`](../../skills/gold-standard-website-pipeline/SKILL.md) G1 recommend as the **marketing default**. Used by [`frontend-implementer`](../../agents/frontend-implementer.md) (primary) and **dispatched by G5 of the pipeline whenever the chosen stack is not React/Fluent** — on those stacks `fluent-react-implementation` is correctly `N/A`, and this skill is the direct build path, not a misroute.

Static-first is not a downgrade. On a content/marketing site, HTML that ships zero framework JS by default beats a hydrated SPA on every metric that gates a launch — LCP, INP, crawlability, resilience. The discipline is: **write the markup a screen reader and a crawler would want, style it entirely through tokens, pre-render everything you can, and hydrate only the islands that genuinely need it.**

## When to use

- Building a marketing site, landing page, docs site, blog, or brochure site on the static-first default stack (Astro-static / 11ty / Hugo / plain HTML+CSS).
- The G5 build gate of `gold-standard-website-pipeline` resolves to a **non-React static stack** — this is the skill G5 dispatches.
- Converting a wireframe + a completed token set into shippable static markup.
- The static shell of an **Astro + islands** build — author the semantic HTML/CSS here; the React island components route to `fluent-react-implementation`.
- Retrofitting an existing static site to hit the reflow / performance-in-markup / a11y bars below.

## When NOT to use

- **A Fluent UI v9 + React build** → [`fluent-react-implementation`](../../skills/fluent-react-implementation/SKILL.md). That skill owns FluentProvider, BrandVariants, Griffel, and the Next SSR boundary; this one does not.
- **An app-grade SPA / product app** — rendering strategy (SSR/RSC/CSR), component architecture, state/server-cache, in-code bundle budgets → `frontend-engineering` (the app-engineering plugin). This skill owns brand/marketing surfaces, not application internals.
- **Authoring the token system itself** (primitive → semantic layer, scale design, dark-mode semantics, the build pipeline) → [`design-tokens-scaffolding`](../../skills/design-tokens-scaffolding/SKILL.md). This skill **consumes** the tokens that skill produces; it never defines brand values.
- **Native mobile** → `mobile-engineering`. **Backend / SSR server logic** → `ravenclaude-core/backend-coder`. **Anything touching auth, sessions, user data, untrusted input, or payments** → mandatory `ravenclaude-core/security-reviewer`.

---

## 1. Semantic HTML first (the load-bearing layer)

Reach for the right element before ARIA (house opinion #5). Semantic markup is what makes the accessibility passes, the SEO heading checks, and the crawlable-without-JS bar all pass at once — one surface (#10).

- **Landmarks, once each.** Exactly one `<main>` per page; wrap the rest in `<header>` / `<nav>` / `<footer>` / `<aside>` / `<section>` with an accessible name (`aria-labelledby` a heading) where a page has multiple `<nav>`/`<section>` regions. No `<div id="main">` where `<main>` exists.
- **Heading nesting with no skips.** One unambiguous `<h1>` per page; ranks descend without gaps (`h2 → h4` is a fail). The heading outline is the document's table of contents for both AT and crawlers — build it before the visuals.
- **Labeled inputs, always.** Every `<input>`/`<select>`/`<textarea>` has an associated `<label for>` (or wraps in `<label>`); placeholder is never the label. Required fields marked with `required` (not colour alone); errors associated via `aria-describedby`.
- **Real elements for real semantics.** `<button>` for actions, `<a href>` for navigation, `<ul>/<ol>/<li>` for lists, `<table>` with `<th scope>` for tabular data, `<nav>` not `<div role="navigation">`. ARIA only fills a gap semantics cannot express — never to re-add what the element already provides.
- **`<html lang>` set**, skip-link as the first focusable element (visible on focus), and a page `<title>` + `<meta name="description">` on every indexable page.

## 2. Consume design tokens as CSS custom properties (never hardcode)

Tokens are the contract (house opinion #4, #12). This skill is strictly **token-consuming** — the primitive→semantic layer, scales, and dark-mode swaps are authored in [`design-tokens-scaffolding`](../../skills/design-tokens-scaffolding/SKILL.md); here you wire the generated CSS variables and stop.

- **Components reference semantic tokens only.** `color: var(--color-text-default)`, `background: var(--color-background-subtle)`, `gap: var(--space-4)`, `border-radius: var(--radius-md)`. Never a raw hex, never a primitive (`--gray-900`) in a component, never an off-scale one-off (`padding: 13px`).
- **Zero hardcoded brand values downstream.** No inline `style="color:#3b82f6"`, no Tailwind arbitrary `text-[#3b82f6]`, no literal hex in a stylesheet outside the generated token file. The plugin's anti-pattern hook (`check-web-anti-patterns.sh`) and a `grep` for hex literals outside `tokens/` catch these — run both before calling a build done.
- **Dark mode via `color-scheme` + re-pointed semantics**, declared on `:root` (`color-scheme: light dark`), honouring `prefers-color-scheme` with a persisted override. Audit for dark-theme residue — navy panels, near-black text, cool teal gradients surviving onto a light canvas is the classic card-surface failure (see [`card-tile-ui`](../../skills/card-tile-ui/SKILL.md)).
- **Motion tokens re-point under `prefers-reduced-motion: reduce`** — durations to `instant`, transforms to opacity-only fades (#13). Every transition has a no-motion fallback.

## 3. Modern CSS layout

Reach for the platform before a library. The safe-in-2026 surface and Baseline caveats live in [`modern-css-2026.md`](../../knowledge/modern-css-2026.md); check Baseline / caniuse for the target audience and provide `@supports` fallbacks for anything not yet universal.

- **Grid + flex for structure.** `grid-template-columns` with `minmax()` / `auto-fit` for card decks; flex for one-dimensional rows. **Subgrid** to align card headers/footers across a deck regardless of content length.
- **Container queries (`@container`)** for component-level responsiveness — a card responds to its *slot's* width, not the viewport. This is the modern replacement for viewport media queries inside reusable components.
- **Logical properties** (`margin-inline`, `padding-block`, `inset`) over physical `left/right/top/bottom` — RTL/i18n-safe by default.
- **`:has()`, `@layer`, native nesting** where they cut JS or specificity fights — `form:has(:invalid)` for state-driven styling with no JS; cascade layers to order app vs third-party CSS without `!important` wars.
- **`oklch()` for colour** (with an sRGB fallback for old targets) so token ramps stay perceptually uniform; `color-mix()` for programmatic tints.
- **View Transitions** (`@view-transition` for MPA, exposed by Astro) always gated behind `prefers-reduced-motion: reduce`.
- **Tailwind v4** (if used) maps tokens into the CSS-first `@theme` block so tokens remain the single source of truth — never ship Tailwind's default palette unchanged.

## 4. Static-stack build mechanics

Pick the stack against [`modern-web-stacks-2026.md`](../../knowledge/modern-web-stacks-2026.md); the static-first bias is **SSG > ISR > SSR > CSR** (#9), and CSR needs a written reason. G1 of the pipeline should already have chosen the stack with a rationale + ≥2 alternatives — honour that choice; this section is *how to build it well*, not *whether*.

- **Astro (static output)** — islands architecture, **zero JS by default**, Content Layer API for content sites, Server Islands to mix static + dynamic per-component. The performance default for content/marketing sites. Add `client:*` directives (`client:load` / `client:visible` / `client:idle`) **only** on components that genuinely need interactivity — partial hydration is the whole point; a page that hydrates everything has thrown away the win.
- **11ty (Eleventy)** — data-cascade + templating (Nunjucks/Liquid/etc.) for pure-static content sites with minimal build machinery; ship interactivity as small progressively-enhanced vanilla-JS/web-component sprinkles, not a framework runtime.
- **Hugo** — fastest builds for large content/docs sites; Go templates + partials. Same rule: interactivity is a deliberate, budgeted addition.
- **Plain semantic HTML + token-driven CSS** — for a handful of pages, no generator is the right generator. A build step for minification/Brotli + an image pipeline is still worth wiring.
- **Partial hydration / islands discipline** — default to no client JS; add an island only where a control cannot be expressed with HTML + CSS (`:has()`, `<details>`/`<dialog>`, the Popover API cover more than most reach for). Each island is a budgeted decision, not a default. When an island *is* React, hand that component to [`fluent-react-implementation`](../../skills/fluent-react-implementation/SKILL.md) and keep the shell here.
- **Build pipeline** — tree-shaking, minification, Brotli/gzip, an image pipeline that emits AVIF/WebP with fallbacks, a tested `404`, and HTTPS + HTTP/2/3 at the edge.

## 5. Responsive & reflow

Mobile-first — design the narrowest layout first and expand up with `min-width` (#3); `max-width`-cascade-down is not the default.

- **Reflow 320 → ≥1280 CSS px with no horizontal scroll and no loss of function** (WCAG 1.4.10). Verify the 320 px case explicitly — it is the one most builds skip.
- **Touch targets ≥ 24×24 px everywhere** (WCAG 2.5.8, AA); **primary controls at 44–48 px** (Apple HIG / Material, aligning with the AAA 2.5.5 stretch).
- **Fluid type and spacing** via `clamp()` on token scales rather than a stack of breakpoint overrides; container queries for component-internal reflow (§3).
- **Breakpoints in `em`, not `px`**, for typographic breakpoints so user zoom is respected.

## 6. Performance in the markup (feeds core-web-vitals-tuning)

Perf has a budget declared before the build (#2); this section is what you bake into the markup so [`core-web-vitals-tuning`](../../skills/core-web-vitals-tuning/SKILL.md) *verifies* rather than *rescues*. Diagnosis and the fix-by-symptom map live in that skill — don't duplicate them; do ship the defaults below.

- **Images.** AVIF/WebP with a fallback, responsive `srcset` + `sizes` (don't ship a 4000px file to a 400px slot), explicit `width`/`height` or `aspect-ratio` on every `<img>` to reserve space (CLS → 0). The LCP image gets `fetchpriority="high"` and **no** `loading="lazy"`; everything below the fold gets `loading="lazy"`.
- **Fonts.** Self-hosted + subset, `font-display: swap` (or `optional` when a swap-in would shift LCP text), preload the critical font, minimise weights. `size-adjust`/`ascent-override` to match fallback metrics where swap-in shifts layout.
- **CSS/JS delivery.** Critical (above-the-fold) CSS inlined; non-critical CSS deferred; **no render-blocking third-party above the fold**; defer/async every non-essential script; analytics/chat/A-B scripts load post-LCP. Third-party scripts are debt — catalogue and budget them (#11).
- **No layout shift after first paint** (#7) — reserve space for images, fonts, embeds, and cookie banners (banner as a fixed overlay, not a reflowing block).
- **Budgets belong in CI**, not eyeballs — see §7.

## 7. Accessibility in the markup (feeds accessibility-review)

Accessibility is a P1 design constraint, designed in from the wireframe, not a phase-2 audit (#1). The audited verdict is `accessibility-auditor`'s via [`accessibility-review`](../../skills/accessibility-review/SKILL.md) (the 5-pass ladder + WCAG 2.2 AA floor); your job is to hand that audit a build that already passes. Bake in:

- Correct `<html lang>`, one `<h1>`, non-skipping headings, landmark elements (§1).
- Every `<img>` has `alt` — descriptive for content images, `alt=""` for decorative (never omit the attribute).
- Visible focus (`:focus-visible` shaped to the tokens, never `outline:none` with no replacement); keyboard-operable everything; a skip-link visible on focus; focus returned to the opener when a `<dialog>` closes.
- No colour-only signifiers (error/success/status carry an icon/shape/text too); `prefers-reduced-motion` honoured on every animation; no autoplay media; nothing flashing > 3×/sec.
- Contrast pre-checked at build time against the *actual rendered* background (states/overlays flattened) with the plugin's [`../../scripts/contrast_ratio.py`](../../scripts/contrast_ratio.py): body ≥ 4.5:1, large text / UI ≥ 3:1 (WCAG 1.4.3).

## 8. Verify before "done" — see the render, wire the gate

- **See the rendered layout across form factors — not from CSS inspection.** Drive `chrome-devtools-mcp` (screenshot + console + Lighthouse) or a project-local Playwright/Puppeteer to dump the rendered box geometry at 320 px and assert no horizontal overflow, then run the referee in [`visual-feedback-loop`](../../../ravenclaude-core/skills/visual-feedback-loop/SKILL.md). If no rendering engine is reachable, a static proxy (grep the built CSS for fixed pixel widths > 320 px on non-`overflow-x:auto` containers) is the weak floor and the render check becomes a standing Conditional — never claim "responsive" from source alone.
- **Production build clean:** no console errors, lint/type-check pass, **no secrets in the client bundle** (grep the *built* output, not just source).
- **Wire CI:** Lighthouse-CI budget assertions + axe-core/pa11y lint. This is the line that turns every number above from a one-time manual check into an enforced gate — an unenforced build passes today and silently regresses tomorrow.

## 9. How this satisfies the pipeline's G5 acceptance criteria

When dispatched from [`gold-standard-website-pipeline`](../../skills/gold-standard-website-pipeline/SKILL.md) G5, this skill's sections map 1:1 to the gate's checkboxes:

| G5 criterion | Where satisfied |
|---|---|
| Semantic HTML first; one `<main>`; labels associated | §1 |
| Tokens consumed, not defined; zero hardcoded brand values | §2 |
| Reflow 320→≥1280, no h-scroll; targets ≥24px, primary 44–48px | §5 |
| Rendered-layout verification (tiered, never a silent wedge) | §8 |
| HTTPS/HTTP2-3, AVIF/WebP+srcset/sizes, lazy below fold, font-display, critical CSS, no render-blocking 3P, tree-shake/minify/Brotli, tested 404 | §4, §6 |
| Production build clean; no secrets in client bundle | §8 |
| CI wired: Lighthouse-CI budget + axe-core/pa11y | §8 |

Report against the plugin Output Contract (`web-design/CLAUDE.md` §6) with `Standards cited:` (WCAG 2.2 AA, CWV thresholds) and `Perf / a11y budget impact:` filled — plus the structured-output JSON block.

---

## Hygiene checklist

- [ ] Exactly one `<main>`; one `<h1>`; heading ranks nest with no skips
- [ ] All landmarks present; multiple `<nav>`/`<section>` regions named
- [ ] Every input has an associated `<label>`; no placeholder-as-label
- [ ] Every `<img>` has `alt` (descriptive or `alt=""`); explicit `width`/`height` or `aspect-ratio`
- [ ] Zero hardcoded hex / off-scale values outside the token file (hook + grep clean)
- [ ] Components reference **semantic** tokens only; dark mode via re-pointed semantics, no residue
- [ ] `prefers-reduced-motion` fallback on every animation/transition
- [ ] Reflow verified at 320 px — no horizontal scroll, no loss of function
- [ ] Touch targets ≥ 24×24 px; primary controls 44–48 px
- [ ] LCP image: `fetchpriority="high"`, no lazy; below-fold images `loading="lazy"`
- [ ] AVIF/WebP + `srcset`/`sizes`; fonts subset + self-hosted + `font-display`
- [ ] Critical CSS inlined; no render-blocking third-party above the fold
- [ ] SSG output; islands/hydration only where an HTML+CSS control cannot express it
- [ ] Contrast pre-checked against the real rendered background (`contrast_ratio.py`)
- [ ] Rendered layout seen across form factors (not inferred from CSS)
- [ ] No console errors; no secrets in the built bundle
- [ ] CI wired: Lighthouse-CI budget + axe-core/pa11y

## Anti-patterns

- **Framework runtime on a brochure site** — shipping React/Vue hydration for pages that are pure content. The static-first win is the default you just discarded.
- **Hydrating the whole page under "islands"** — `client:load` on every component. An island is a budgeted exception, not a default.
- **`<div onClick>` / `<div role="button">`** where `<button>` belongs; ARIA re-adding what the semantic element already provides.
- **Hardcoded hex / arbitrary Tailwind values** (`text-[#3b82f6]`) in components; primitives (`--gray-900`) used directly instead of semantics.
- **"Responsive" claimed from CSS inspection** with no rendered check at 320 px.
- **Lazy-loading the LCP image**, or omitting `width`/`height` and eating the CLS.
- **Render-blocking third-party in `<head>`** (analytics, fonts, chat) above the fold.
- **Placeholder-as-label**, `outline:none` with no focus replacement, colour as the only status signifier.
- **Lorem ipsum in a "final" mock** — realistic copy lengths expose the layout bugs lorem hides (#6).
- **A green one-off Lighthouse run with no CI budget** — unenforced perf regresses silently.
- **`px` typographic breakpoints** that ignore user zoom (use `em`).

## See also

- Skill: [`../../skills/design-tokens-scaffolding/SKILL.md`](../../skills/design-tokens-scaffolding/SKILL.md) — authors the tokens this skill consumes
- Skill: [`../../skills/core-web-vitals-tuning/SKILL.md`](../../skills/core-web-vitals-tuning/SKILL.md) — CWV diagnosis + fix-by-symptom (this skill ships the in-markup defaults)
- Skill: [`../../skills/accessibility-review/SKILL.md`](../../skills/accessibility-review/SKILL.md) — the audited WCAG 2.2 verdict
- Skill: [`../../skills/card-tile-ui/SKILL.md`](../../skills/card-tile-ui/SKILL.md) — card/tile surfaces + the dark-theme-residue audit
- Knowledge: [`../../knowledge/modern-css-2026.md`](../../knowledge/modern-css-2026.md) — the CSS surface + Baseline caveats
- Knowledge: [`../../knowledge/modern-web-stacks-2026.md`](../../knowledge/modern-web-stacks-2026.md) — rendering models + stack selection
- Agent: [`../../agents/frontend-implementer.md`](../../agents/frontend-implementer.md) — this skill's primary user
- Pipeline: [`../../skills/gold-standard-website-pipeline/SKILL.md`](../../skills/gold-standard-website-pipeline/SKILL.md) — G5 dispatches this skill for non-React static stacks
