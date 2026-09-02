# Vercel design.md pattern
URL: https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md
Retrieved: 2026-09-01
Type: Blog post (engineering pattern)

## What's valuable here
Vercel's internal AI agents write on-brand marketing pages by reading `design.md` — a single
guidance file loaded into the model's context before generation — plus a companion public
stylesheet (`vercel-brand.css`) that supplies bounded CSS classes for headers, tables, stat
strips, and chart styles. The core insight: prose brand guidelines ("keep the layout clean")
are read differently by every model, so Vercel rewrote them as **observable, falsifiable rules**
("let evidence tables use the full available width") and named the recurring bad patterns
explicitly so agents can recognize and avoid them. Measured effect: pages generated **without**
`design.md` showed 91 mechanical failures vs. 39 **with** it — a 57% reduction.

## Concrete extractable patterns/techniques
- Split the deliverable in two: a **guidance file** (voice, hierarchy, typography/color
  composition rules, publishing/asset rules) loaded into context at generation time, and a
  **separate stylesheet** consumed post-render in the browser — keeps token budget for prose
  guidance instead of spending it on CSS the agent doesn't need to reason about.
- Rewrite every subjective brand rule as an **observable, checkable statement** — replace
  adjectival language ("feels cramped," "keep it clean") with a directive an agent (or a linter)
  can act on unambiguously ("let evidence tables use the full available width").
- **Name anti-patterns explicitly.** Cataloguing recurring generated-design failure modes by
  name gives the model something to pattern-match against and avoid, rather than relying on it
  to infer "don't do that" from silence.
- Point external tools at **one canonical public URL** for the guidance file regardless of
  environment (dev/staging/prod) — a single source of truth an agent always resolves the same way.
- Pair the context-time guidance with a **post-generation deterministic validation layer** that
  catches mechanical failures (the thing that produced the 91→39 count) — validation isn't
  optional once you have a checkable rule set, it's the second half of the pattern.
- Treat the guidance file as a **living artifact tuned against measured agent output**, not a
  one-time brand-guidelines PDF translated to Markdown — the anti-pattern catalogue and the
  91→39 number both imply iterative refinement driven by observed failures.

## Where this should feed into RavenClaude
- Recommend adding to: `plugins/web-design/skills/gold-standard-website-pipeline/SKILL.md` (G3
  Design/Tokens gate) — the pipeline already emits `design-tokens.json` + a design-system-audit
  report at G3; extending G3's artifact set with a generation-time brand-guidance file (voice,
  layout, do/don't, named anti-patterns) closes the gap between "tokens exist" and "an agent
  reliably produces on-brand pages," which is exactly the problem this post solves.
- Recommend adding to: `plugins/brand-identity-studio/skills/brand-book-assembly/` (or wherever
  `assemble-brand-book` lives) — the brand book is this plugin's terminal artifact; a
  machine-readable companion (observable rules + named anti-patterns, not just prose) is a
  natural adjunct output at the same handoff point where `design-md-token-interop.md`'s
  `DESIGN.md` token export already lives, so precedent for an agent-facing markdown artifact at
  this seam already exists.
- Recommend adding to: `plugins/web-design/knowledge/design-md-token-interop.md` — that file
  already documents an *unrelated* `DESIGN.md` convention (Google Labs' W3C-token export format).
  Cross-link rather than merge: the Google `DESIGN.md` is a **token-export** spec; the Vercel
  `design.md` is a **generation-time brand-guidance** spec. Same filename, different job — the
  cross-link should say so explicitly to prevent confusion at the point a reader finds one and
  assumes it's the other.
- Owning skill for establishing the convention: `design-tokens-scaffolding` is the natural owner
  of the *token* half (already true via the Google DESIGN.md cross-ref); the *voice/layout/
  anti-pattern* half is closer to `brand-identity-studio`'s `brand-voice-and-messaging` +
  `logo-and-visual-system-direction` skills, escalated to `web-design`'s `visual-designer` for
  the code-facing observable-rule translation. **Closed:** [`brand-guidance-authoring`](../../skills/brand-guidance-authoring/SKILL.md)
  now owns "write the agent-facing on-brand generation contract," wired as a `gold-standard-website-pipeline`
  G3 criterion — the gap this source named.

## Refresh recipe
- Re-check: every ~6 months, or opportunistically when reworking `gold-standard-website-pipeline`
  G3 or `brand-book-assembly`.
- What to watch for: Vercel publishing a follow-up post, open-sourcing `vercel-brand.css` or a
  `design.md` template/schema, other vendors (Google, Figma, Anthropic) publishing a competing
  or converging spec for agent-facing brand-guidance files, and any tooling that auto-validates
  a `design.md` against rendered output (the "91→39 failures" measurement implies Vercel has
  such a validator internally — a public release of it would be directly adoptable).
