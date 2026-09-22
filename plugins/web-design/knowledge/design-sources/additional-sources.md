# Additional design sources (broad sweep)
Retrieved: 2026-09-01

> Scope note: this sweep deliberately excludes 5 sources another agent researched in parallel —
> github.com/danium/astro-frontend-developer-skill, the Vercel `design.md` blog post,
> reactbits.dev, collectui.com, and github.com/nextlevelbuilder/ui-ux-pro-max-skill.
> Every entry below was independently verified via WebSearch/WebFetch this session — none
> are guessed URLs. Curated down from ~24 candidates found across 6 categories to the 12 with
> the strongest, most specific value and confirmed 2025-2026 activity.

## Astro official Showcase
URL: https://astro.build/showcase/
Type: gallery
Value: Curated real production sites built with Astro (The Guardian, Google Firebase, Trivago, Evil Martians, Microsoft properties) — the reference for what Astro looks like at enterprise scale, distinct from marketing-site aesthetic donors.
Recommend adding to: plugins/web-design/knowledge/design-references.md — as an Astro-specific companion pointer alongside the existing eight donor sites, or a new "Astro exemplars" subsection.
Refresh cadence: annually (community-submitted, evolves gradually).

## Astro official Themes catalog
URL: https://astro.build/themes/
Type: gallery/marketplace
Value: Official catalog that auto-updates daily from the Astro Developer Portal, spanning portfolio/blog/docs/business themes with a submission + sponsorship track — a live curation mechanism, not a stale directory.
Recommend adding to: plugins/web-design/skills/static-site-implementation/SKILL.md — as a starting-point reference when scaffolding a new Astro site.
Refresh cadence: check the catalog mechanism every 6-12 months; content itself churns daily.

## incluud/astro-agent-skills
URL: https://github.com/incluud/astro-agent-skills
Type: repo (Claude Code/Cursor/Codex skill pack)
Value: The only currently-real entrant for "Astro-focused AI-coding-agent skill repo" — 6 skills (create-component, content-collection, add-integration, docs-lookup, migrate, astro-best-practices) targeting TypeScript, accessibility, and shipping less JS. Caveat: thin (9 stars, 2 commits, no visible sustained-activity signal) — cite as a real but unproven/early-stage source, not an authority.
Recommend adding to: plugins/web-design/skills/static-site-implementation/SKILL.md — as a "watch this repo" note, not a load-bearing citation, given its youth.
Refresh cadence: re-check activity in 3 months; drop if it goes dormant.

## one-aalam/awesome-astro
URL: https://github.com/one-aalam/awesome-astro
Type: curated list
Value: Actively maintained awesome-list (PR activity through mid-2026) covering Astro integrations, templates, and showcased projects — the standard ecosystem entry point when a specific Astro tool/integration is needed.
Recommend adding to: plugins/web-design/skills/static-site-implementation/SKILL.md — as the go-to index for Astro integrations/templates.
Refresh cadence: annually.

## Base UI (MUI)
URL: https://base-ui.com/
Type: library
Value: MUI's headless-primitive library, hit stable v1.0 in December 2025 and staffed by several engineers who originally built Radix — now the more actively-maintained headless-primitive option since Radix's 2026 acquisition by WorkOS slowed that project's release cadence (notably on complex components like Combobox/multi-select). shadcn/ui defaults new projects to Base UI as of July 2026.
Recommend adding to: plugins/web-design/knowledge/design-systems-and-component-architecture-2026.md — update/supplement any existing Radix-primitives guidance with this landscape shift.
Refresh cadence: check every 6 months — this is a fast-moving ecosystem realignment.

## shadcn/ui
URL: https://ui.shadcn.com/
Type: library
Value: Still the dominant "copy-owned-code, not a dependency" component approach in 2026, with releases roughly every 1-2 weeks (React Aria integration, `@shadcn/helpers`, `shadcn/typeset`, chat-interface components shipped through mid-2026) and now pluggable onto either Radix or Base UI primitives.
Recommend adding to: plugins/web-design/knowledge/design-systems-and-component-architecture-2026.md — confirm/refresh existing shadcn guidance against the 2026 Base UI default-primitive change.
Refresh cadence: every 6 months given the release pace.

## Emil Kowalski — emilkowal.ski + emilkowalski/skills
URL: https://emilkowal.ski/ , https://github.com/emilkowalski/skills
Type: blog + packaged Claude Code/Codex skill
Value: Design engineer at Linear (ex-Vercel), author of Sonner and Vaul; in 2026 he converted his own animation/component-design writing into a packaged agentic skill with 100k+ installs — structurally the closest direct comparable to what RavenClaude ships, and worth studying for both content (motion/interaction craft) and packaging approach.
Recommend adding to: plugins/web-design/knowledge/fluent-react-for-web-2026.md — as a motion/interaction-craft source; also worth a skim by whoever maintains RavenClaude's own skill-authoring conventions, as a competitive/comparable reference.
Refresh cadence: monthly — it's a fast-moving skill repo, not a static blog.

## Shopify Polaris — design tokens
URL: https://github.com/Shopify/polaris-tokens (package: `@shopify/polaris-tokens`), docs at https://polaris.shopify.com/
Type: methodology (open-sourced token system from a real company)
Value: Ships tokens as their own versioned package (npm + Ruby gem) consumed independently of the component library, with a documented monorepo split between `polaris-tokens`, `polaris-react`, and the docs site — a concrete "tokens as infrastructure, not a byproduct of components" case study.
Recommend adding to: plugins/web-design/skills/design-tokens-scaffolding/SKILL.md — as a real-world worked example of token-package separation.
Refresh cadence: annually.

## Motion (motion.dev) + Motion Examples
URL: https://motion.dev/ , https://examples.motion.dev/
Type: library + pattern gallery
Value: The renamed, actively-developed successor to Framer Motion (v12 in 2026) — the dominant React/JS animation library, paired with 430+ copy-paste examples (scroll effects, gestures, layout transitions) that are directly usable in Astro islands or React components, not just static inspiration.
Recommend adding to: plugins/web-design/knowledge/fluent-react-for-web-2026.md — as the primary motion-implementation library reference.
Refresh cadence: check on major version bumps (roughly every 6-12 months).

## WAI-ARIA Authoring Practices Guide (APG)
URL: https://www.w3.org/WAI/ARIA/apg/
Type: methodology/standard (W3C)
Value: Still the canonical reference for accessible widget patterns — roles, states, and keyboard-interaction models per component type — actively maintained (task-force page and GitHub repo both show 2026 activity). This is the standard to cite against, not a supplementary nice-to-have.
Recommend adding to: plugins/web-design/skills/accessibility-review/SKILL.md — as the primary normative reference for widget-pattern correctness, if not already cited.
Refresh cadence: check yearly; ARIA 1.3 is still a Working Draft, worth tracking for changes.

## GOV.UK Design System — accessibility patterns
URL: https://design-system.service.gov.uk/
Type: production design system (patterns + components)
Value: Components are tested against real assistive technology for WCAG 2.2 AA compliance, not merely documented as compliant — e.g. its error-summary pattern is a widely-cited, battle-tested reference for accessible form errors with real focus management. The underlying frontend package is actively versioned (v6.1.0, March 2026).
Recommend adding to: plugins/web-design/skills/accessibility-review/SKILL.md — as a concrete pattern reference for form/error-state accessibility.
Refresh cadence: check on major GOV.UK Frontend version bumps.

## bergside/awesome-design-skills
URL: https://github.com/bergside/awesome-design-skills
Type: curated list / skill registry
Value: 2.6k stars, active (open PRs/issues in 2026), packaging 67 aesthetic `SKILL.md`+`DESIGN.md` pairs (glassmorphism, brutalism, neumorphism, retro, etc.) for the exact same agentic-skill pattern RavenClaude uses — high value as both a content source for specific aesthetic treatments and a structural/competitive comparison point for RavenClaude's own web-design skill authoring.
Recommend adding to: new skill/knowledge doc, or plugins/web-design/knowledge/design-references.md as a "see also: comparable community skill registries" pointer — worth a maintainer skim for packaging-format ideas even where the aesthetic content itself isn't a fit.
Refresh cadence: quarterly, given active PR/issue churn.

---

## Notes on sources investigated and deliberately excluded

- **Aceternity UI, Magic UI, Origin UI** — all confirmed still active in 2026 (Magic UI growing fastest), but declined as separate entries to avoid diluting the curated list; Base UI and shadcn/ui cover the load-bearing "component library with taste" ground more durably.
- **Astro Components Kit (astrocomponents.dev) / WebcoreUI** — real, active, well-documented, but both lean into glassmorphism/neumorphism/cyberpunk aesthetics that directly contradict this marketplace's existing anti-pattern guidance in `design-references.md`. Declined as taste donors.
- **Sara Soueidan's blog** — highly respected but low 2026 post cadence (mostly paid workshops now); Adrian Roselli and GOV.UK cover current ground more actively.
- **Inclusive Components (Heydon Pickering)** — the author himself has called it dated; APG + GOV.UK now supersede it.
- **Adobe Spectrum, GitHub Primer** — both real, active, tokens-first design systems, verified but held back from the final 12 for curation tightness; worth a follow-up look if design-tokens-scaffolding wants a second worked example beyond Polaris.
- **buildui.com** — real, well-regarded, but primarily a paid video-course product; weaker fit as a free "pull from" source.
- **Godly.website, Land-book, CSS-Tricks, Smashing Magazine, web.dev/Chrome for Developers blog** — all verified active and solid, held back from the final 12 for curation tightness rather than any quality concern; Godly in particular is worth a second look given its taste alignment with the existing Linear/Vercel/Raycast restraint aesthetic.
