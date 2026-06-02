# Card / tile UI pattern (Intercom-style) — 2026 reference

Backing knowledge for the [`card-tile-ui`](../skills/card-tile-ui/SKILL.md) skill. Read when designing or auditing a card-driven SaaS surface (dashboards, inboxes, admin consoles, settings, catalogs).

## Naming — say it accurately

There is **no public branded name** for Intercom's design system; Intercom's own engineering writing calls it "the full-stack design system." `[grounded: web search 2026 — getdesign.md/intercom, intercom.com/blog/the-full-stack-design-system; no proper noun surfaced]` So when a stakeholder says "make it look like Intercom," they mean the **visual pattern**, which has vendor-neutral names:

- **Card-based UI / card surfaces / tiles** — discrete, rounded, elevated content containers with soft shadows on a neutral canvas.
- **Soft UI** — the same, emphasizing low-contrast, gentle shadows (distinct from the 2020 "neumorphism" fad, which is double-shadow extruded-from-background and is **dated**; do not conflate them).
- **Multi-pane / list-detail layout** — persistent navigation rail (+ optional list column) + detail panel.
- **Monochromatic + single accent** — neutral surfaces, one restrained accent.

State it as "Intercom-style **card/tile UI**" and define it; don't invent a proper noun.

## Anatomy

```
┌──────────┬───────────────────────────────────────────────┐
│  nav     │  ┌─ card ─────────┐  ┌─ card ─────────┐        │  ← content area =
│  rail    │  │ white, hairline │  │                │        │    a grid/stack of
│ (icons + │  │ border, soft    │  │  multiple      │        │    discrete tiles
│  labels, │  │ shadow, radius  │  │  information   │        │
│  active  │  └─────────────────┘  │  cards         │        │
│  tinted) │  ┌─ card ─────────┐  └────────────────┘        │
│          │  │ accent hairline │                            │
│          │  │ left edge (flag)│                            │
└──────────┴───────────────────────────────────────────────┘
   canvas = one calm neutral; cards = lighter/white + elevation
```

Three forces make it read as "cards" and not "a flat sheet with lines":
1. **Figure/ground separation** — card surface is lighter than canvas, *and* casts a shadow.
2. **Containment** — hairline border + radius close each tile as an object.
3. **Rhythm** — equal gaps + internal padding so tiles are clearly peers.

Remove any one and it collapses to "flat monochromatic," which is the most common complaint about a card UI that "doesn't look like the reference."

## Donor study (what to borrow, 2026)

| Donor | Borrow | Don't borrow |
|---|---|---|
| **Intercom** | The inbox three-pane structure; calm card stacks; restrained accent; status pills | Their specific blue if you have your own brand |
| **Linear** | Monochrome canvas + faint grid; one accent; typography-led hierarchy; keyboard-first | Heavy command-palette dependency for a simple site |
| **Vercel / Geist** | Hairline borders; tight neutral scale; flat fills + minimal shadow | Pure-black canvas if your brand is warm |
| **Slack / Notion** | The persistent left navigation rail; subtle active-item tint | Sidebar density if your IA is shallow |

The recipe is **restraint + one or two memorable interactive beats** (a gentle hover lift, a single accent hairline). Aesthetics already dated as of 2026 and to avoid: bento grids on every section, glassmorphism beyond modals, AI-shimmer/silver-halo hero gradients, neumorphism, emoji-as-icon. (Cross-ref [`design-references.md`](design-references.md).)

## Color & elevation discipline

- **Canvas temperature is a brand choice.** Cool light grey (Intercom/Linear) reads "neutral tech"; warm beige reads "editorial/calm." Pick one and keep shadows the *same temperature* — a cool shadow on a warm canvas looks like dust; a warm shadow on a cool canvas looks muddy.
- **Shadow scale, not a shadow.** Define ~5 tiers (resting `sm` → hover `md` → overlay `lg`/`xl`), low opacity (≈0.04→0.14). Resting cards use the lightest; only elevate on interaction.
- **Accent ≤ ~5% of pixels.** Hairline rules, a 3px card outline to flag primary/active, the active nav tint, link/heading color, one filled CTA. That's the budget.
- **Two-accent systems** (e.g. this marketplace's teal + gold) work **only if each surface commits to one** of them; mixing both on one surface dilutes the signal and complicates contrast math.

## Accessibility gotchas specific to this pattern

- A warm/gold/amber accent usually passes only **AA-large** (~3:1) on a light canvas → borders/hairlines/icons/large-bold headings only; **never** body text or small labels. A teal/blue accent around 4.5:1 can carry body text. **Verify each accent against both the canvas and the inset surface** before shipping — luminance, not hue, drives the ratio, so re-check after any canvas tweak.
- Active nav / selected tile must not rely on color alone (add a 3px edge or weight).
- Every hover-lift / shimmer needs a `prefers-reduced-motion` fallback.
- Focus-visible ring on every interactive tile.

Run the formal pass via the [`accessibility-review`](../skills/accessibility-review/SKILL.md) skill.

## The dark-theme-residue trap (audit checklist)

A surface ported from a dark theme to light by remapping tokens almost always keeps **hardcoded literals** that bypassed the tokens, and those clash on the light canvas. Grep the *source*, not just the token file:

- Navy/black bars & code panels: `rgba(11,17,32,…)`, `#0b1120`, `#060c16`, `#07080a` → `var(--surface)` / translucent white / `--surface-2` for code.
- Near-black `color:` on saturated fills: `#04121a`, `#04201c`, `#04210f` → neutral text token, or `#fff` on the fill.
- Cool hero haze: `radial-gradient(... rgba(45,212,191,…) / rgba(56,189,248,…))` → remove; flat canvas + one accent whisper.
- Light accent text on white (`#5eead4`, `#93c5fd`, `#fbbf24`) → neutralize to muted+neutral-border, or a single AA-passing darker accent.
- Gradient card fills + glow shadows → flat `var(--surface)` fill + a real elevation shadow.

> **Worked example (this repo, 2026-06):** the three generated surfaces
> (`index.html`, `repo-guide.html`, `dashboard.html`) carried the *right*
> `--rc-*` tokens but rendered flat because of exactly this residue — a
> `rgba(11,17,32,0.82)` navy topbar, a `#060c16` code panel, `#04121a`
> selection text, cool cyan/blue hero gradients, and audience chips colored in
> light dark-theme hues that vanished on white. The fix was token-routing those
> literals + giving the content cards a real `box-shadow` + larger radius +
> hover lift — the tokens were already correct; the literals were the bug.

## Implementation note for this marketplace

Tokens + shared classes live in
[`ravenclaude-core/dashboard-assets/shared-tokens.css`](../../ravenclaude-core/dashboard-assets/shared-tokens.css)
(`--rc-*`, `.rc-card`, `.rc-card--accent`, `.rc-rule`). The three HTML surfaces
are **generated** (`scripts/generate-index-dashboard.py`,
`generate-repo-guide.py`, `generate-dashboards.py`) and **freshness-gated by
byte-exact match** — edit the token file + the generators, then **regenerate
and re-run `scripts/audit-gates.sh`**. Never hand-edit the committed HTML. Two
accents are kept by design: **teal** (index + catalog) and **gold**
(dashboard); each surface uses exactly one.
