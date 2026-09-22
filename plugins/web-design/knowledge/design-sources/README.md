# External design sources — raw research layer

Read when deciding whether to pull a new pattern/technique from outside RavenClaude, or when
refreshing what's already been pulled. This directory is the **raw-source** layer: one dated,
sourced note per external repo/site/post, each ending in a refresh recipe (what to re-check and
when). It sits **upstream** of the plugin's curated knowledge:

- [`../design-references.md`](../design-references.md) — curated **whole-site aesthetic exemplars**
  (Linear, Vercel, Raycast, …) for visual/interaction direction.
- [`../gold-standard-website-references-2026.md`](../gold-standard-website-references-2026.md) —
  curated **agentic website-building tools/plugins**, mapped to pipeline-craft idioms.
- **This directory** — the broader, less-curated raw material: specific techniques, taxonomies, and
  candidate sources, each flagged with exactly where it should (or shouldn't) feed into the plugin's
  skills/knowledge, and how confident the extraction is.

Nothing in this directory is itself load-bearing on a gate — it's the evidence trail for the specific
additions made to `skills/*/SKILL.md` and `knowledge/*.md` elsewhere in this plugin (and, for a couple
of entries, in `ravenclaude-core` and `brand-identity-studio`). If a citation in another file looks
stale or wrong, this is where to find what it was based on and when.

## The sources

| Source | Type | What it's for | Refresh cadence |
|---|---|---|---|
| [`astro-frontend-developer-skill.md`](astro-frontend-developer-skill.md) | GitHub repo (Claude Code skill) | Astro 7+ rendering hierarchy, `client:*` directive discipline, Content Layer API rules, claim discipline for SEO/AEO | Semi-annual (repo is new, created 2026-08-31 — watch for early churn) |
| [`vercel-design-md.md`](vercel-design-md.md) | Blog post (engineering pattern) | The `design.md` agent-facing brand-guidance-file pattern (observable rules + named anti-patterns + post-gen validation) | ~6 months, or when reworking `gold-standard-website-pipeline` G3 / `brand-book-assembly` |
| [`reactbits.md`](reactbits.md) | Component gallery (live) | Animated React component taxonomy + per-component dependency-minimalism + copy-paste distribution model | Browse before any motion-forward brief, not on a calendar |
| [`collectui.md`](collectui.md) | UI inspiration gallery (live) | The ~100-item Daily UI pattern-category taxonomy, grouped by page-type work | Consult per-screen-type, not on a calendar |
| [`ui-ux-pro-max-skill.md`](ui-ux-pro-max-skill.md) | GitHub repo (Claude Code skill) | Named aesthetic-style taxonomy, tap-latency/touch-target numbers, icon anti-patterns, gap analysis vs this plugin's own audit skills | 6–12 months, bundled with `gold-standard-website-references-2026.md`'s annual refresh |
| [`additional-sources.md`](additional-sources.md) | 12-source broad sweep | Astro ecosystem (Showcase, Themes, awesome-astro, incluud/astro-agent-skills), component libraries (Base UI, shadcn/ui), Shopify Polaris tokens, Motion (motion.dev), WAI-ARIA APG, GOV.UK Design System, Emil Kowalski, bergside/awesome-design-skills — plus a "declined" list so future sweeps don't re-research the same ground | Per-entry cadence stated inline (ranges 3 months to annually) |

## How this got here

Commissioned 2026-09-01: analyze `danium/astro-frontend-developer-skill`, Vercel's `design.md` blog
post, reactbits.dev, collectui.com, and `nextlevelbuilder/ui-ux-pro-max-skill`, extract what's
concretely useful, and broad-sweep for other strong sources (Astro-weighted, not Astro-exclusive).
Six research passes ran in parallel, each independently verified (WebFetch/`curl`/WebSearch, not
inferred) and dated. Findings were then folded into the specific skills/knowledge files named in each
note's "Where this should feed into RavenClaude" section — see those files' own citations for exactly
what changed and why.

## Refreshing this directory

Each note's own "Refresh recipe" section is authoritative for that source. As a directory-level
habit: re-run this same broad-sweep pattern (5 named sources + N broad-sweep candidates, each
independently verified) roughly annually, or whenever `gold-standard-website-references-2026.md` gets
its own annual refresh — bundling the two keeps the plugin's whole external-reference layer on one
freshness cycle instead of drifting independently. Drop a source's note (or mark it superseded) rather
than silently leaving a dead citation elsewhere in the plugin.
