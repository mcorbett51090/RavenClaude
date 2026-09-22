# A dashboard inherits its host's color scheme — it doesn't impose its own

**Status:** Pattern — strong default for Case B (client deliverable, embedded) and Case C
(productized SaaS, often embedded); deviate only when the dashboard genuinely IS the whole
application and no host theme exists to inherit.

**Domain:** Dashboard theming / embed integration

**Applies to:** `data-platform`

---

## Why this exists

Confirmed directly against this plugin (FORGE dashboard-top1pct P2-18, 2026-09-03): a positive
control (`grep -ril "prefers-color-scheme|dark mode"` returning zero hits before this phase)
found both app starters shipped a single, hard-coded light theme — 16 literal hex values in each
`tailwind.config.ts`/`.mjs` and two more in each `RevenueChart.tsx`. `agents/dashboard-builder.md`
had already listed "Theme + branding" as a surface area with no artifact behind it. This matters
structurally, not cosmetically: **every embedded dashboard is mounted into a host page whose
theme it does not control.** A client's admin panel in dark mode, a marketing site that respects
`prefers-color-scheme`, a SaaS product with its own light/dark toggle — a dashboard that always
renders light-only either clashes visibly with its host or, worse, gets manually re-themed per
embed with a growing pile of one-off CSS overrides that drift from the starter's own source.

## How to apply

- **Model every color as a semantic CSS custom property, never a literal hex** in a component or
  a Tailwind config value — `--tremor-background-DEFAULT`, not `#ffffff` inline and not `#ffffff`
  baked into `tailwind.config.ts`. This is the enabling primitive: a variable can be overridden
  from outside the file that declares it; a literal cannot.
- **The starter's own `.dark` class toggle is the STANDALONE-app default, not the only
  mechanism.** A host embedding this dashboard (iframe, web component, or a server-rendered
  fragment mounted directly into the host's own DOM) has two paths, and should pick based on how
  it's actually embedding:
  - **Same-DOM embed** (a mounted component, not an iframe): the host can set the SAME
    `--tremor-*` variable names in the scope it mounts the dashboard into — no prop threading, no
    rebuild, no coordination with this starter's own toggle. The dashboard's CSS custom properties
    cascade from whatever ancestor scope defines them; a host that already manages its own
    dark/light state at the document root gets automatic inheritance for free.
  - **iframe embed**: CSS custom properties don't cross a frame boundary — the host instead needs
    to pass its current theme (e.g. via a `?theme=dark` query param or a `postMessage`, per
    `skills/embed-csp-and-iframe-sandboxing/SKILL.md`'s existing origin-check discipline) and the
    iframe's own page applies it by toggling its own `.dark` class, same as the standalone case.
- **System preference is the default, an explicit override wins over it** — per
  `web-design`'s `design-tokens-scaffolding` skill (§4, Light/dark mode): read
  `prefers-color-scheme` via `matchMedia`, but let an explicit user choice (persisted to
  `localStorage`) take precedence. Both starters implement this via a synchronous inline
  `<script>` in `<head>` that runs before first paint — a `useEffect`-driven toggle alone would
  cause a visible flash of the wrong theme, since it can only run after hydration.
- **Contrast must be independently verified in both modes**, not assumed to carry over from
  light mode — a color that passes AA on a white background can fail on a dark one and vice
  versa (see `dashboard-meet-the-accessibility-floor.md`). This plugin's own dark-mode work
  surfaced a genuine pre-existing light-mode failure (`content.subtle` at 2.54:1 against white,
  rendering real provenance-footer and status text) while re-deriving the palette — checking both
  modes together is what caught a bug neither mode's review alone had caught.
- **A brand color often needs a luminosity-boosted dark variant**, not the identical hex — a
  `#3b82f6` blue that reads clearly on white can look muddy or under-saturated on a near-black
  background; both starters' dark `brand.DEFAULT` is a lighter shade than the light-mode one for
  exactly this reason.

## What "good" looks like

- Zero literal 6-digit hex values inside a component or a Tailwind config's `colors` block —
  every color resolves through a `var(--tremor-*)` reference.
- A host embedding the dashboard same-DOM can re-theme it entirely by setting `--tremor-*`
  variables in its own mounting scope, with zero changes to the dashboard's own code.
- Contrast passes WCAG 2.2 AA in both modes for every text pairing actually rendered as text
  (not just the pairings that happened to be checked in light mode).
- The toggle is `role="switch"` + `aria-checked`, not a bare icon-swap button with no
  machine-readable state.

## Related

- [`dashboard-meet-the-accessibility-floor.md`](./dashboard-meet-the-accessibility-floor.md) —
  the WCAG 2.2 AA floor this rule's contrast requirement is a specific application of.
- [`../skills/embed-csp-and-iframe-sandboxing/SKILL.md`](../skills/embed-csp-and-iframe-sandboxing/SKILL.md) —
  the iframe-embed case's `postMessage` origin-check discipline, needed for the cross-frame theme
  hand-off this rule names but doesn't implement (out of this phase's scope — see the plugin
  CHANGELOG for P2-18's actual `Files touched`).
- [`../../web-design/skills/design-tokens-scaffolding/SKILL.md`](../../web-design/skills/design-tokens-scaffolding/SKILL.md) —
  the primitive/semantic token split and the "system preference + override" mechanics this rule
  is a data-platform-scoped application of, not a reinvention.
