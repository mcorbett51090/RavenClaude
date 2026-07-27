---
name: design-token-architecture
description: "Structure design tokens across the primitive → semantic → component tiers, with theming/dark-mode and multi-brand solved as a semantic-tier value swap, then emit the platform outputs consumers use. Traverses the token branch of the design-systems decision tree: source of truth → tier structure → naming → theming → platform outputs. Reach for this when the user asks 'how should our tokens be structured?', 'set up design tokens', 'how do we do dark mode / multi-brand?', or 'primitive vs semantic tokens?'. Used by design-systems-architect (structure) and design-tokens-and-component-engineer (pipeline)."
---

# Skill: design-token-architecture

> **Invoked by:** `design-systems-architect` (the tier structure & naming decision) and
> `design-tokens-and-component-engineer` (the pipeline that realizes it).
>
> **When to invoke:** "how should our tokens be structured?"; "set up our design tokens"; "how do
> we do dark mode / multi-brand?"; "primitive vs semantic vs component tokens?"; any "what's the
> token model" question.
>
> **Output:** a token architecture — the tier structure (primitive → semantic → component), naming
> conventions, the theming/multi-brand strategy resolved at the semantic tier, and the platform
> outputs — plus the conditions that would restructure it.

## Procedure

1. **Establish the source of truth.** Decide where tokens *live* authoritatively — a
   framework-agnostic format (the W3C DTCG `$value`/`$type` JSON, or a Figma variables export) —
   not scattered in CSS. One source, transformed to every platform. Everything downstream derives
   from it.
2. **Define the primitive tier — raw, context-free values.** `color.blue.600`, `space.4`,
   `font.size.300`. These are the palette: no meaning, no intent, never consumed directly by a
   product. They exist so the semantic tier has something to point at.
3. **Define the semantic tier — intent, not appearance.** `color.bg.surface`, `color.text.default`,
   `color.border.focus`, `space.inset.md`. Each **references a primitive** and names a *role*.
   This is the tier products and components consume. The rename test: if renaming your company's
   brand color would force edits in product code, your semantic tier is missing or bypassed.
4. **Define the component tier where a component needs its own scoped tokens.** `button.bg.primary`
   → references `color.bg.brand`. Use it when a component's styling should be tunable independently
   of the global semantic value; skip it when the semantic token is enough (don't create ceremony).
5. **Solve theming at the semantic tier — a value swap, never a component fork.** A theme
   (light/dark, brand A/brand B) is a *set of semantic-token values*: `color.bg.surface` resolves
   to different primitives per theme, the component tree is identical. Wire it with CSS custom
   properties scoped by a `[data-theme]` (web) or a theme object (native). Dark mode is just
   another theme; multi-brand is just more themes.
6. **Emit the platform outputs consumers actually use.** Transform the source (e.g. Style
   Dictionary) to: CSS custom properties (+ a typed TS map) for web, and native formats if
   targeted. Types matter — a mistyped token name should fail at build, not render wrong.
7. **State the resize conditions** — the 1–2 facts that restructure the model (e.g. "if we add a
   third brand with a different type scale, the semantic tier needs a typography theme axis"; "if a
   product keeps reaching for primitives, the semantic tier has a gap — add the missing role rather
   than letting it bypass").

## Worked example

> User: "We have a web app and are about to launch a second brand. How should tokens be structured
> so dark mode and the second brand aren't a rewrite?"

- **Source:** author tokens in DTCG JSON, one repo, transformed via Style Dictionary
  *(retrieval-dated 2026-07; verify Style Dictionary config API at use)*.
- **Primitive:** `color.slate.{50..900}`, `color.brandA.{...}`, `color.brandB.{...}`, `space.*`.
- **Semantic:** `color.bg.surface`, `color.text.default`, `color.action.primary`, `space.inset.md`
  — components reference only these.
- **Component:** `button.bg.primary → color.action.primary` (kept because the button may want to
  diverge from the global action color later).
- **Theming:** four themes = {brandA, brandB} × {light, dark}; each is a semantic-value map. CSS
  vars under `[data-brand][data-theme]`. No component knows which brand/theme it's in.
- **Outputs:** CSS custom properties + a typed TS token map; `pnpm build:tokens` runs in CI so a
  bad token name fails the build.
- **Resize condition:** if brand B needs a different type scale, add a typography axis to the
  semantic tier rather than forking components.

## Guardrails

- **Products consume semantic/component tiers, never primitives** — a direct primitive reference is
  a leak that makes rebrands a refactor. Flag it.
- **Theming is a value swap at the semantic tier** — never fork or branch a component per brand/mode.
- **One source of truth, transformed** — tokens duplicated across CSS/JS/native drift; derive them.
- **Type the outputs** — an unknown token name should fail at build time.
- **Don't over-tier** — a component-tier token with no reason to diverge from its semantic parent is
  ceremony; add it only when the component genuinely needs an independent knob.
- **Retrieval-date volatile tooling** (Style Dictionary API, DTCG spec status); durable tiering
  principles don't need a date.
