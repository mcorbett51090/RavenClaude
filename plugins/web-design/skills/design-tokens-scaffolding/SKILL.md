---
name: design-tokens-scaffolding
description: Scaffold a token system from brand spec to token JSON to CSS variables to framework theme (Tailwind / Shadcn / CSS-in-JS / Theme UI). Includes naming convention, scale design (color / spacing / typography / radius / shadow / motion), light/dark mode, semantic vs primitive tokens, and the dual-mode build pipeline. Reach for this skill when launching a new design system or when an existing system has "design drift" between Figma and code. Used by `visual-designer` (primary) + `frontend-implementer`.
---

# Skill: design-tokens-scaffolding

**Purpose:** Scaffold a design token system end-to-end: brand spec → token JSON → CSS variables → framework theme. Used by `visual-designer` (primary) and `frontend-implementer` (token-to-code wiring).

Tokens are the contract between design and engineering. Without them, the design system is a screenshot library and code accumulates hardcoded hex values. With them, a color update propagates everywhere in one PR. The discipline is to model **decisions** (primitives) separately from **uses** (semantics), and to make the pipeline one-way: design tool → JSON → code.

## When to use

- Launching a new design system from scratch
- Existing system has visible drift between Figma and code (different blues, different spacing)
- Dark-mode rollout (semantic tokens are how this becomes tractable)
- Tailwind / Shadcn migration where the team wants brand-specific theming
- Component-library refactor — pre-work before the components themselves change

## 1. Primitive vs semantic tokens (the non-negotiable distinction)

This is the single highest-leverage idea in a token system. Two layers:

**Primitives** — raw values, named by what they are:

```json
{
  "color": {
    "gray": {
      "50":  "#fafafa",
      "100": "#f4f4f5",
      "500": "#71717a",
      "900": "#18181b"
    },
    "brand": {
      "500": "#3b82f6"
    }
  }
}
```

**Semantics** — use-cases that consume primitives, named by what they do:

```json
{
  "color": {
    "background": {
      "default": "{color.gray.50}",
      "subtle":  "{color.gray.100}",
      "inverse": "{color.gray.900}"
    },
    "text": {
      "default": "{color.gray.900}",
      "muted":   "{color.gray.500}",
      "inverse": "{color.gray.50}"
    },
    "accent": {
      "default": "{color.brand.500}"
    }
  }
}
```

**Components consume semantic tokens only.** Never `bg-gray-50` in a component; always `bg-background-default`. The button doesn't know what color it is — it knows it's a button.

This is the discipline that makes dark mode tractable, makes brand refreshes a one-PR change, and prevents drift.

## 2. Naming conventions

- **Avoid Tailwind-like appearance names in semantics** — `blue-500` is fine as a primitive; in components, use `primary` or `accent`, not `blue`. When the brand color stops being blue in v2, you don't want to rename `bg-blue-500` everywhere.
- **Role-based, not appearance-based** — `danger` not `red`, `success` not `green`, `muted` not `gray`
- **Hierarchical dots** — `color.text.default`, `color.text.muted`, `color.text.inverse`. Maps cleanly to JSON, CSS custom properties, and Tailwind config.
- **Surface terms consistent** — `background` / `foreground` / `border` / `text` / `accent`. Match Radix / Shadcn's vocabulary; the team already knows it.
- **State suffixes** — `-hover`, `-active`, `-disabled`, `-focus` as a suffix on the role (`accent-hover`, not `hover-accent`)

## 3. Scale design

Every visual property needs a scale. Scales constrain choice, which is what makes the system feel coherent.

### Color ramps

- **9-step or 11-step** per color family (50–900 or 50–950). Tailwind's pattern works because each step has computed contrast meaning: `500` is the typical mid-tone, `700–900` for text on light backgrounds, `50–200` for backgrounds behind dark text.
- **Computed contrast** — for each step, document the WCAG contrast it provides against `gray.50` and `gray.900`. Surface the failing pairs.
- **Brand + neutral + 3–4 functional** (success / warning / danger / info). No more. A 9th accent color is a design smell.

### Spacing

- **Geometric (`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96`)** — the 8pt system with `4` for fine adjustments. Modern reference.
- **No off-scale values in production** — if a component needs `13px`, the scale is wrong or the component is wrong.

### Typography

- **Modular type scale** — base × ratio. Common: base 16, ratio 1.25 (major third) for marketing, 1.2 (minor third) for dense UI.
- **8–10 named steps** — `display-xl`, `display-lg`, `h1`, `h2`, `h3`, `h4`, `body-lg`, `body`, `body-sm`, `caption`. Don't ship 20 steps.
- **Line-height paired with size** — heading line-heights tight (1.1–1.2), body line-heights comfortable (1.5–1.6). Encode as the token, not as a separate decision per component.
- **Font-weight palette** — 400 / 600 / 700 typical; never load every weight. Variable fonts let you express weight as a number without N font files.

### Radius

- `none` / `sm` (4px) / `md` (8px) / `lg` (12px) / `xl` (16px) / `full`. Stops there.

### Shadow / elevation

- `0` / `1` (1px subtle) / `2` (card) / `3` (popover) / `4` (modal). Each step is a pre-composed `box-shadow` value; no per-component custom shadows.

### Motion

- **Duration scale** — `instant` (0ms — important for reduced-motion), `fast` (100ms), `default` (200ms), `slow` (300ms), `slower` (500ms)
- **Easing scale** — `ease-out` (entries), `ease-in` (exits), `ease-in-out` (through-states), `spring` (Framer / Motion). Never linear except for indeterminate loading.
- **`prefers-reduced-motion: reduce` is a semantic-token re-pointing exercise** — all durations point to `instant`, all transforms point to opacity-only fades.

## 4. Light / dark mode

Dark mode works if and only if the system is semantic. Mechanics:

- **Primitives don't change** — `gray.50` is still `#fafafa` in dark mode. Primitives are facts.
- **Semantics swap** — `color.background.default` points to `gray.50` in light, `gray.900` in dark. `color.text.default` flips. `color.accent` may stay the same or get a brighter variant.
- **`color-scheme: light dark` declared** on `:root` so native UI (scrollbars, form controls) respect the mode
- **System preference + override** — respect `prefers-color-scheme` by default; let the user override (toggle, persisted in localStorage)
- **Test every component in both modes** — Storybook should have a mode toggle on every story
- **Brand colors don't always survive dark mode** — a vivid brand color on a dark background often needs a luminosity-boosted variant. Document this as a primitive (`brand.500-dark`) and re-point the semantic.

## 5. Token JSON format

Two emerging standards in 2026:

- **Style Dictionary** — Amazon's tool, JSON format, very mature
- **W3C Design Tokens Community Group draft format** — converging standard, supported by Figma Tokens / Tokens Studio, Specify, Knapsack, Supernova

Pick W3C-aligned format for forward compatibility:

```json
{
  "color": {
    "background": {
      "default": {
        "$value": "{color.gray.50}",
        "$type": "color",
        "$description": "Page-level background, light mode"
      }
    }
  }
}
```

The `$value`, `$type`, `$description` triple is the W3C convention. References use `{path.to.token}` syntax.

## 6. Build pipeline

The pipeline is the contract:

```
Figma (Tokens Studio plugin)
   ↓ publishes
tokens/tokens.json  ← source of truth, in the repo
   ↓ Style Dictionary build
build/css/tokens.css          (CSS custom properties)
build/tailwind/tokens.cjs     (Tailwind theme config)
build/ts/tokens.ts            (TypeScript typed export — for CSS-in-JS / inline)
   ↓ consumed by
components/*  ← only via semantic CSS variables or Tailwind classes
```

Concrete steps:

1. **Designers edit in Figma**, publish via Tokens Studio plugin to a JSON file
2. **CI checks the JSON** — schema valid, no orphan references, no naming-convention violations
3. **Style Dictionary builds the platform outputs** — CSS variables, Tailwind config, TS types, iOS / Android if applicable
4. **The framework theme consumes the built outputs** — `tailwind.config.cjs` imports the generated config, CSS-in-JS theme provider reads the TS export
5. **No hand-edits in `build/`** — generated artifact, gitignored or generated on `pnpm build`

### Tailwind specifically

```js
// tailwind.config.cjs
const tokens = require('./build/tailwind/tokens.cjs');
module.exports = {
  theme: {
    colors: tokens.color,           // semantic names — accent, background, text
    spacing: tokens.spacing,
    fontSize: tokens.fontSize,
    borderRadius: tokens.radius,
    boxShadow: tokens.shadow,
    extend: {}
  }
};
```

The team uses `bg-accent` not `bg-blue-500`. The Tailwind class set **becomes** the semantic vocabulary.

### Shadcn / Radix specifically

Shadcn ships with semantic CSS custom properties (`--background`, `--foreground`, `--primary`, etc.) that already match the discipline. The job is to re-point these to your generated tokens, not to invent a parallel system.

## 7. Audit for drift

Once the system ships, drift is the failure mode:

- **Figma-published tokens vs code tokens** — quarterly diff. CI step: parse the Figma export, parse the built CSS, fail on any drift.
- **Hardcoded values in code** — grep for hex literals outside the `tokens/` directory and the generated `build/` outputs. Plugin's anti-pattern hook catches some of this.
- **Off-scale spacing** — grep for `padding: 13px` etc. Lint rule that allows only token values.
- **Component-level color overrides** — `style={{ color: '#ff0000' }}` in JSX. Same lint.
- **Designer's "exception" colors** — every additional brand color or one-off shade is debt. Audit and consolidate.

## Hygiene checklist

- [ ] Primitive layer defined separately from semantic layer
- [ ] Components only reference semantic tokens
- [ ] Naming uses roles, not appearances (`accent` not `blue`)
- [ ] All scales geometric (no off-scale spacing, no random font sizes)
- [ ] Color ramps document computed WCAG contrast pairs
- [ ] Dark-mode semantics defined; primitives unchanged
- [ ] `prefers-reduced-motion` re-points motion semantics to `instant`
- [ ] Token JSON in W3C-draft format (or Style Dictionary)
- [ ] Build pipeline one-way (Figma → JSON → platform outputs); no hand-edited build artifacts
- [ ] Storybook (or equivalent) renders every component in both modes
- [ ] Drift audit scheduled (Figma vs code, quarterly)
- [ ] Lint rule for hardcoded hex / off-scale values in components

## Anti-patterns

- **Cosmetics in shared tokens** — `color.button-hover-pink-special` is a one-component override masquerading as a token. Tokens are decisions used in ≥ 2 places.
- **Hex sprinkled in components** — `style={{ color: '#3b82f6' }}` or `className="text-[#3b82f6]"` (Tailwind arbitrary value). Both are anti-patterns.
- **Appearance-based naming in semantics** — `text-blue-500` in a component. Rename to `text-accent` immediately.
- **Component-level dark-mode overrides** — `dark:bg-gray-900` everywhere. Means the semantic layer is missing.
- **Filter-based dark mode** — `filter: invert(1) hue-rotate(180deg)`. Visually catastrophic on images and brand colors; immediate red flag.
- **Tailwind defaults shipped unchanged** — `text-blue-500` from Tailwind's default palette. Either replace the theme, or accept that the team has no brand.
- **20-step type scale** — designers indulging. Consolidate.
- **Tokens defined in code, mirrored in Figma manually** — drift is guaranteed. Pipeline must be one-way.
- **No motion tokens** — every animation invents its own duration / easing. Inconsistency at the smallest scale.
- **Token file with no `$description` fields** — six months later, no one remembers what `color.surface.subtle-inverse-2` is for.

## See also

- Skill: [`../design-system-audit/SKILL.md`](../design-system-audit/SKILL.md)
- Skill: [`../accessibility-review/SKILL.md`](../accessibility-review/SKILL.md) — color contrast checks live here
- Template: [`../../templates/design-system-spec.md`](../../templates/design-system-spec.md)
- Knowledge: [`../../knowledge/design-references.md`](../../knowledge/design-references.md)
- Agent: [`../../agents/visual-designer.md`](../../agents/visual-designer.md)
- Agent: [`../../agents/frontend-implementer.md`](../../agents/frontend-implementer.md)
