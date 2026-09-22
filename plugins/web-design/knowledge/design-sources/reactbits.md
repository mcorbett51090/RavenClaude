# ReactBits
URL: https://reactbits.dev
Retrieved: 2026-09-01
Type: Component gallery (live, frequently updated)

## What's valuable here
ReactBits (github.com/DavidHDev/react-bits, 46.6k stars, MIT + Commons Clause) is the largest
open-source library of copy-pasteable, animated React components — 165+ components spanning text
effects, backgrounds, and general UI motion. Its value to RavenClaude isn't the components
themselves (they're framework/animation-library-specific and will drift as the site updates) but
the **implementation conventions**: a disciplined 4-variant build matrix (JS/TS × CSS/Tailwind),
a zero-dependency-by-default posture with named libraries pulled in only per-component, and a
copy-in-not-install-a-package distribution model that keeps bundle weight owned by the consumer.
It's a strong "browse for inspiration + steal the technique" source for any brief that wants
memorable, motion-forward marketing-site moments — not a reference for building a full design
system or accessible baseline UI kit.

## Concrete extractable patterns/techniques
- **Category taxonomy worth mirroring in a components/motion knowledge doc:** Text Animations
  (SplitText, BlurText, GradientText, TypingEffect, WavyText, GlitchText, FlipText, ScrambleText —
  staggered/character-level entrance and ongoing typographic motion), Backgrounds (Aurora, Particles/
  ParticleBackground — flowing-gradient and physics/GPU-driven ambient backdrops), UI
  Components/Animations (hover/magnetic effects, animated borders, click sparks, pixel transitions,
  image trails, scroll-triggered reveal wrappers), and a newer "Creative Tools" set (Background
  Studio, Shape Magic, Texture Lab) for generating/tuning bespoke visual assets.
- **Per-component dependency minimalism, not a house animation stack.** Different components pull
  different engines as needed rather than one bundled runtime: CSS-only for simple gradient/blur
  effects (Aurora has zero deps), GSAP + ScrollTrigger for scroll-triggered/staggered sequences,
  OGL and three.js for WebGL-driven backgrounds, Matter.js as a peer dependency for physics-based
  particle fields. The lesson: pick the lightest engine that satisfies the specific effect rather
  than reaching for one animation library everywhere.
- **The 4-variant build matrix** (JS-CSS / JS-TW / TS-CSS / TS-TW) is a reusable pattern for any
  component-recipe knowledge doc that wants to serve both Tailwind and vanilla-CSS consumers, and
  both JS and TS codebases, without forking the underlying logic.
- **Copy-paste-first distribution via CLI, not an npm package install.** Components install through
  `shadcn` CLI (`npx shadcn@latest add @react-bits/<Component>-<lang>-<style>`) or the `jsrepo`
  registry, which drops source files directly into the consumer's project — no version-locked
  package dependency, full editability, tree-shakeable by construction. This is the same
  distribution philosophy shadcn/ui popularized and is worth naming explicitly as an alternative to
  npm-package component libraries when a brief wants full visual control plus easy customization.
- **Props-driven customization surface** (duration, direction, color, strength, etc.) on every
  component keeps the "steal the technique, restyle to brand" workflow fast — relevant to this
  marketplace's card-tile-ui skill's "gentle motion only" rule (§ rule 7) and to conversion-design
  work that wants a tasteful hero/CTA moment without hand-rolling GSAP timelines from scratch.
- **Companion tooling exists that turns the gallery into a queryable index**, e.g. community MCP
  servers (`ceorkm/reactbits-mcp-server`) and Claude-Code skill catalogs
  (`Philotheephilix/reactbits.dev-skill`, `unobtuse/reactbits-frontend-design-skill`) that mirror
  the component catalog as structured `references/catalog.md` data — a pattern worth revisiting if
  RavenClaude ever wants a locally-cached, greppable snapshot instead of a live browse.

## Where this should feed into RavenClaude
- Recommend adding to: `plugins/web-design/knowledge/design-references.md` — as a named entry in the
  curated reference set, alongside other pattern-donor sites, specifically flagged for
  motion/animation-forward marketing moments rather than layout/IA/brand craft.
- Recommend adding to: `plugins/web-design/skills/card-tile-ui/SKILL.md` "Gentle motion only" rule
  (rule 7) — as a citation for the props-driven, single-purpose-engine approach to hover/lift motion,
  contrasting ReactBits' heavier effects (particles, WebGL) with the card pattern's intentionally
  restrained motion budget.
- Recommend adding to: `plugins/web-design/knowledge/modern-web-stacks-2026.md` or a future
  animation-library decision tree — as a worked example of picking GSAP vs CSS vs OGL/three.js vs a
  physics engine per-effect rather than standardizing on one animation runtime site-wide.

## Refresh recipe
- Re-check: browse before any brief that calls for animated text, ambient/WebGL backgrounds, or
  scroll-triggered motion on a marketing site — not on a fixed calendar. This is a live, continuously
  updated gallery (component count has grown from ~110 to 165+ across different retrieval dates in
  2026), so treat any specific component list here as a snapshot, not a stable catalog.
- What to watch for: new categories beyond the current four (Text Animations, Backgrounds, UI
  Components/Animations, Creative Tools); changes to the install mechanism (shadcn CLI / jsrepo
  registry could shift); the paid Pro tier's scope creeping into what's free; and the GitHub repo
  (github.com/DavidHDev/react-bits) as the canonical source of truth if the live site's structure
  changes faster than this note can track.

## Verification note
Fetched via WebFetch: the reactbits.dev homepage itself returned only the page title (JS-rendered
SPA, no component content in the static HTML) — confirmed via WebFetch, not fabricated. The GitHub
repo README (github.com/DavidHDev/react-bits) fetched successfully and supplied the category count,
variant system, license, and star count directly. Specific animation-library-per-component details
(GSAP/OGL/three.js/Matter.js) and named components (SplitText, GradientText, Aurora, Particles, etc.)
come from WebSearch results citing third-party writeups and community catalogs, not a direct fetch of
the live component pages — treat individual component names as illustrative of the category, not a
verified-complete inventory.
