# ui-ux-pro-max-skill
URL: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
Retrieved: 2026-09-01
Type: GitHub repo (Claude Code skill, UI/UX quality)

## What's valuable here
It is a **generation/retrieval tool**, not an audit pipeline like RavenClaude's: a searchable knowledge
base (79 named UI aesthetic styles, 192 industry-specific color palettes + reasoning rules, 74 font
pairings, 105 icons, 25 chart types, 22 tech stacks) that a BM25-style search engine matches against a
project's product category to *generate* a tailored design system, then checks the output against a
10-category priority-ranked rule table and a mobile-native pre-delivery checklist. Its distinctive value
is the **named-style + per-industry-anti-pattern taxonomy** ("avoid AI purple/pink gradients for
banking") — a vocabulary RavenClaude's own audit skills don't carry — plus tight native-mobile
interaction-timing numbers RavenClaude doesn't state.

## Concrete extractable patterns/techniques
- **10-category priority-ranked rule table** (Accessibility CRITICAL → Charts/Data LOW) pairing each
  category with its checks *and* its anti-patterns in one row — a compact severity+check+anti-pattern
  format RavenClaude's audits state as prose/tables but not as one unified ranked list.
- **Tap-feedback latency: 80–150ms** for tactile/visual response to a touch — a specific number not
  present anywhere in `gold-standard-website-pipeline` or `design-system-audit` (which has a duration
  *scale* of 100/200/300/500ms for transitions but no tap-acknowledgment-latency bound).
- **Icon-specific rules**: unified icon family + sizing tokens (`icon-sm`/`icon-md`) + consistent stroke
  width; **emoji-as-structural-icon named as an explicit anti-pattern**; icons carry their own **3:1
  contrast minimum** for meaningful (non-decorative) icons, called out separately from body-text
  contrast.
- **Named UI style taxonomy** (Glassmorphism, Claymorphism, Minimalism, etc. — 79 total, 50 active) with
  per-product-category matching and a "mixing flat & skeuomorphic randomly" anti-pattern — a vocabulary
  layer RavenClaude's `design-system-audit` doesn't have (it audits token/scale *consistency*, not
  aesthetic-style *selection* against a named catalog).
- **Bottom-navigation item cap: ≤5** — a specific mobile nav heuristic not present in RavenClaude's
  `information-architecture` skill.
- **Native-mobile safe-area + platform-touch-target split**: 44pt (iOS) vs 48dp (Android) stated
  separately (RavenClaude states a single "44–48 px, Apple HIG/Material" range without the platform
  split), plus explicit gesture-zone/notch safe-area and 4/8dp spacing-rhythm discipline for native apps.
- **Design "dials"** — `--variance`, `--motion`, `--density` on a 1–10 scale mapping to concrete spacing
  ranges (8–32px dense → 24–96px spacious) — a generation-time tuning knob RavenClaude's token-scaffolding
  skill doesn't expose as a named, numbered control.
- **Chart/dashboard-specific guidance** (25 chart types; legends, tooltips, accessible-without-color-alone)
  — RavenClaude's `web-design` plugin has no chart/dataviz-specific skill of its own (the marketplace's
  `dataviz` capability lives outside this plugin).

## Gap analysis vs RavenClaude's existing skills
- **RavenClaude is already more thorough on standards provenance.** Every RavenClaude number traces to a
  cited WCAG success criterion (e.g., 1.4.3, 1.4.10, 2.5.8) or a CWV metric with a field-vs-lab split;
  ui-ux-pro-max states numbers ("4.5:1", "44×44px") without SC citations, and has no lab/field distinction
  for its performance claim (just "CLS < 0.1").
- **RavenClaude is already more rigorous on process.** The gate ladder (fail-closed / Conditional / waiver
  with owner+date), the dependency DAG, and the tiered evidence ladders (Tier 1 MCP browser → Tier 2
  headless-browser dep → Tier 3 static proxy + Conditional) have no analogue in ui-ux-pro-max, which is a
  single-pass checklist with no gating mechanics or fallback tiers.
- **RavenClaude's `design-system-audit` already covers token/scale consistency at least as deeply**
  (10 dimensions incl. tokens layer, dark-mode residue, documentation) — ui-ux-pro-max's rule table is
  shallower here (one "Typography & Color" row).
- **Genuinely missing/weaker in RavenClaude:** (1) no named aesthetic-style taxonomy for *selecting* a
  look per product category — RavenClaude's `design-references.md` curates exemplar sites, not a
  named-style-with-anti-patterns catalog; (2) no tap-feedback-latency number; (3) no platform-split
  (iOS/Android) touch-target statement, only a merged 44–48px range; (4) no emoji-as-icon anti-pattern
  called out explicitly; (5) no chart/dataviz-specific skill inside `web-design`; (6) no per-industry
  design anti-pattern list (e.g., banking-vs-gradient).

## Where this should feed into RavenClaude
- Recommend adding to: `plugins/web-design/skills/design-system-audit/SKILL.md` §7 (Iconography) —
  add the emoji-as-icon anti-pattern and the icon-specific 3:1 non-text contrast check as an explicit
  sub-bullet, since the skill already audits icon sizing/color but not this failure mode.
- Recommend adding to: `plugins/web-design/skills/design-system-audit/SKILL.md` §6 (Motion) — add an
  80–150ms tap-acknowledgment-latency bound alongside the existing duration scale.
- Recommend adding to: `plugins/web-design/skills/information-architecture/SKILL.md` — add the
  ≤5-items bottom-navigation heuristic to whatever nav-pattern guidance it carries for mobile/app IA.
- Recommend adding to: `plugins/web-design/knowledge/design-references.md` — consider whether a
  compact named-aesthetic-style vocabulary (glassmorphism/claymorphism/etc.) with 1-line
  when-to-use/avoid notes belongs there, since RavenClaude currently curates *sites*, not *styles*.
- Not recommended for adoption: the design "dials" (variance/motion/density 1–10) and the BM25 search
  mechanics are generation-tool UX, not audit criteria — no clean seam into a gate-based pipeline.

## Refresh recipe
- Re-check: every 6–12 months, or whenever RavenClaude's `gold-standard-website-references-2026.md` gets
  its annual refresh (natural bundling point).
- What to watch for: version bumps to the style/palette/font counts (v2.0's "Design System Generator" is
  new; watch for a v3 with different reasoning-engine claims), new named UI styles entering the 50-active
  set, and whether the Premium-tier features (brand identity, logo, enterprise tokens) move any rubric
  content out of the open-source tier this file was retrieved from.
