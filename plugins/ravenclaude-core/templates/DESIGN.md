---
version: alpha
name: RavenClaude House Style
description: >
  Default visual identity for ad-hoc HTML an agent generates to explain, diagnose, or report
  something to the user — NOT a client's own branded product or marketing site. If this repo has
  its own project-root DESIGN.md, that one wins for this repo; this file is the fallback house
  default. See plugins/ravenclaude-core/knowledge/design-md-resolution.md for the resolution rule
  and scope.
colors:
  background: "#07080a"
  surface: "#0c0e12"
  surface-2: "#10131a"
  border: "rgba(255,255,255,0.07)"
  border-strong: "rgba(255,255,255,0.14)"
  text: "#f5f7fa"
  text-muted: "#9aa3b2"
  ink: "#f0f2f5"
  ink-on-ink: "#07080a"
  primary: "#56d08a"
  primary-hover: "#6ee0a1"
  ok: "#4ade80"
  warn: "#d4a017"
  danger: "#f87171"
typography:
  display:
    fontFamily: "Space Grotesk"
    fontSize: 30px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  heading:
    fontFamily: "Space Grotesk"
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: -0.01em
  body:
    fontFamily: "Inter"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  caption:
    fontFamily: "Inter"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: -0.01em
  code:
    fontFamily: "JetBrains Mono"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
rounded:
  xs: 3px
  sm: 4px
  md: 6px
  lg: 10px
  pill: 999px
components:
  card:
    backgroundColor: surface
    textColor: text
    rounded: lg
    padding: lg
  button-primary:
    backgroundColor: primary
    textColor: ink-on-ink
    rounded: pill
    padding: sm
  badge:
    backgroundColor: surface-2
    textColor: text-muted
    rounded: xs
---

## Overview

Restrained and technical, not decorative. This is the default look for a page an agent generates
so a person can *see* something — a diagnostic report, an audit summary, a status dashboard, an
explainer of what changed and why. It borrows RavenPower's commerce visual language (a cool
near-black canvas with one signature accent color), the same aesthetic RavenClaude's own generated
dashboards (`index.html`, `dashboard.html`) already use via `dashboard-assets/shared-tokens.css` —
this file is that same set of decisions, expressed portably for any repo and any agent to read,
independent of RavenClaude's own Python generators.

## Colors

Dark canvas by default (`background` #07080a) with layered panels (`surface`, `surface-2`) lifting
off it via hairline borders, never heavy drop shadows. One accent — `primary`, a green (#56d08a) —
carries every call-to-action, active state, and focus ring. Do not introduce a second accent color;
one signature color per surface is the point. `ok`/`warn`/`danger` are reserved for status
badges and inline alerts only, never for primary UI.

## Typography

Two faces: `display`/`heading` in Space Grotesk (headlines, section titles, eyebrows — tight
tracking, high weight), `body`/`caption` in Inter (everything a person reads at length). `code` is
JetBrains Mono, used only for literal values (paths, commands, identifiers) — never for prose.

## Layout

Spacing is a geometric 4px-base scale (`xs` 4px → `3xl` 64px). Generous whitespace over dense
packing — this is a page meant to be read once and understood, not a working dashboard someone
lives in all day.

## Elevation & Depth

Depth comes from hairline borders and subtle background-lightness steps between `background` →
`surface` → `surface-2`, not from shadow stacking. A card lifts on hover with a 1-2px translate and
a barely-perceptible shadow increase — restraint is the point.

## Shapes

Sharper than soft-UI defaults: `sm` (4px) for inputs/buttons, `lg` (10px) for cards/panels, `pill`
for primary CTAs only. No `xl`/`2xl` radii — this is a technical surface, not a marketing page.

## Components

- **Card** — the primary content container: `surface` background, `lg` radius, `lg` padding,
  hairline border. Accent is applied only as a thin left-border rule on a highlighted card, never
  as a fill.
- **Primary button** — `primary` fill, `ink-on-ink` text, `pill` radius. Reserve for the single most
  important action on the page.
- **Badge** — `surface-2` background, `text-muted` foreground, `xs` radius, uppercase mono label for
  a status/category tag.

## Do's and Don'ts

- **Do** keep one accent color per page. **Don't** add a second "brand" color for variety.
- **Do** use Space Grotesk only for headings/short labels. **Don't** set body copy in it — it reads
  poorly at length.
- **Do** default to dark (`background` #07080a). A light variant is acceptable but is not this
  file's job to define — if a repo wants a light-first house style, override this file at the repo
  root rather than patching this default in place.
- **Don't** use this file for a client's own branded product or marketing site. That is
  `web-design`/`brand-identity-studio`'s job, always project-specific, with no house default — see
  `plugins/web-design/knowledge/design-md-token-interop.md`.
