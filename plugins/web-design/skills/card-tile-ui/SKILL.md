---
name: card-tile-ui
description: Design and implement an Intercom-style card / "tile" UI — discrete soft-shadowed rounded surfaces on a calm monochromatic canvas, in a multi-pane (navigation-rail + content) layout, with a single restrained accent used only as hairlines, outlines, and occasional text. Used by `visual-designer` (primary) and `frontend-implementer` (token-to-code wiring). Invoke when a brief asks for a "card", "tile", "panel", "Intercom-style", "dashboard-like", or "clean SaaS" surface, or when restyling an existing flat/monochromatic page toward elevated content tiles.
---

# Skill: card-tile-ui

**Purpose:** produce the **Intercom-style card / tile UI** — the calm, card-driven SaaS aesthetic seen in Intercom's Inbox: a fixed **navigation rail**, a content area composed of **multiple discrete information cards** (white tiles, hairline border, very soft warm shadow, generous radius), all floating on a monochromatic canvas, with one accent color used **minimally** (hairline rules, card outlines, the occasional link/heading, a single primary CTA). Used by `visual-designer` (primary) and `frontend-implementer` (token → code).

## What this pattern is actually called

There is **no public proper-noun name** for Intercom's design system (their engineering blog calls it "the full-stack design system"). The reusable, vendor-neutral name for the *visual* pattern is:

- **Card-based UI** (a.k.a. **card surfaces** / **tiles**) — content grouped into discrete, rounded, **elevated** containers with **soft, low-contrast shadows**, separated by whitespace on a neutral canvas. When the shadows are subtle and warm it's often called **"soft UI."**
- **Multi-pane / list-detail layout** — a persistent navigation rail + (optionally) a list column + a detail panel.
- **Monochromatic base + single accent** — neutral surfaces everywhere; one restrained accent carries interactive meaning.

So the one-liner: *Intercom-style **card/tile UI** — soft-shadowed elevated rounded surfaces on a monochromatic canvas, in a multi-pane layout, with a single restrained accent.*

## When to use

- A brief says "card", "tile", "panel", "Intercom-style", "dashboard", "inbox-style", or "clean / calm SaaS".
- Restyling a **flat, monochromatic** page that has no visual hierarchy of surfaces (the page reads as one undifferentiated sheet) toward **distinct content tiles**.
- Auditing a surface that *claims* a card aesthetic but renders flat — usually because shadows/radius/borders weren't applied, or because **dark-theme color residue** (navy bars, dark code blocks, near-black button text, cool gradients) was mapped onto a light palette.

## The eight rules of a credible card/tile surface

1. **One canvas, white tiles.** The page background is a single calm neutral (cool light grey, or a warm beige). Cards are a *lighter/whiter* surface so they read as lifted. Never gradient-fill a card — a flat fill + shadow is what reads as "tile."
2. **Hairline border + soft shadow, together.** 1px border in a neutral that's *slightly* darker than the card, plus a low-opacity, slightly-warm (or slightly-cool, matching the canvas temperature) shadow. Shadow alone = floating blob; border alone = flat box; both = tile.
3. **Generous radius.** 12–16px on cards (smaller — 6–8px — on inner controls). Consistent radius is most of the "polish."
4. **Whitespace is structural.** 16/24/32 padding rhythm inside and between cards. Crowded cards stop reading as discrete objects.
5. **Accent is a whisper.** The accent appears as: a hairline rule (a faded-end gradient line topping a hero or dividing a section), a 3px left/top **card outline** to flag a primary/active tile, the occasional link or heading color, the active nav-item tint, and **one** filled primary CTA. Everything else is monochrome. If accent is on more than ~5% of the pixels, dial it back.
6. **Navigation rail, not a top nav.** A persistent left rail with icon+label items; the active item gets a subtle accent tint + a 3px accent edge. This is the "navigation pane" users recognize from Intercom/Linear/Slack.
7. **Gentle motion only.** Cards lift `translateY(-2px)` + deepen one shadow step on hover, ~0.18s ease. No scale, no glow pulses. Honor `prefers-reduced-motion`.
8. **Hover/elevation encode interactivity, not decoration.** Static info cards may stay flat-resting; clickable cards lift on hover. Don't animate non-interactive tiles.

## Dark-theme-residue audit (the #1 reason a "card" page renders flat/ugly)

When a surface was ported from a dark theme to a light palette by remapping tokens, **literal colors that bypassed the tokens** survive and clash. Grep for and fix:

| Residue | Symptom | Fix |
|---|---|---|
| `rgba(11,17,32,…)`, `#0b1120`, `#060c16`, `#07080a` | Navy/black top bars, sticky headers, code panels on a light page | Route to `var(--surface)` / translucent white; light code panel uses `--surface-2` |
| `#04121a`, `#04201c`, `#04210f` as `color:` | Near-black button/selection text meant for a bright fill | Route to the neutral text token, or `#fff` on a saturated fill |
| `radial-gradient(... rgba(45,212,191,…))`, `rgba(56,189,248,…)` | Cool cyan/blue "hero glow" haze | Remove; flat canvas, or a single faint accent whisper |
| Light accent text (`#5eead4`, `#93c5fd`, `#fbbf24`) on white | Audience/status chips nearly invisible | Neutralize to muted text + neutral border, or a single darker accent that passes AA |
| Heavy `linear-gradient` card fills + `box-shadow … glow` | Cards look like buttons, not tiles | Flat `var(--surface)` fill + a real elevation shadow |

A page can carry the *right tokens* and still render wrong because these literals never read them. Always grep the actual source for hex/`rgba` literals, not just the token file.

## Token shape (vendor-neutral)

```css
:root {
  --canvas:    /* one calm neutral — cool grey or warm beige */;
  --surface:   #ffffff;            /* the tile */
  --surface-2: /* slightly tinted — code blocks, insets */;
  --border:    /* hairline, ~1 step darker than surface */;
  --border-strong: /* hover border */;
  --text: …; --muted: …; --faint: …;
  --accent: /* ONE accent — verify AA on --canvas if it ever carries text */;
  /* 5-tier soft shadow scale, opacity 0.04 → 0.14, tinted to match canvas temp */
  --shadow-sm: …; --shadow-md: …;
  --radius: 10px; --radius-lg: 16px;
}
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); box-shadow: var(--shadow-sm);
  padding: 24px;
  transition: box-shadow .18s ease, border-color .18s ease, transform .18s ease;
}
.card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.card--accent { border-left: 3px solid var(--accent); }  /* minimal-accent flag */
```

> In **this marketplace**, those tokens already exist as `--rc-*` in
> [`plugins/ravenclaude-core/dashboard-assets/shared-tokens.css`](../../../ravenclaude-core/dashboard-assets/shared-tokens.css)
> with the shared `.rc-card`, `.rc-card--accent`, and `.rc-rule` classes. Two
> accents are kept by design: **teal** on the consumer surfaces (index +
> repo-guide) and **gold** on the dashboard. Each surface uses **one** accent;
> the split is intentional. Edit the token file + each surface's generator,
> then **regenerate** (`scripts/generate-*.py`) — the HTML is generated and
> freshness-gated, never hand-edited.

## Accessibility (load-bearing)

- The accent, **if it ever carries text**, must pass WCAG AA (≥4.5:1) on the canvas. A gold/amber accent typically only passes AA-*large* (~3:1) → restrict it to borders, hairlines, icons, and ≥18px/14px-bold headings; never body text or small labels. Verify with a contrast checker against **both** the canvas and the inset surface.
- Hover-lift and shimmer must collapse under `prefers-reduced-motion`.
- Active nav state needs more than the accent tint — also a 3px edge or weight change (don't rely on color alone).
- Focus-visible rings on every interactive tile/control.

Defer the full WCAG pass to the [`accessibility-review`](../accessibility-review/SKILL.md) skill; defer broad token-system work to [`design-system-audit`](../design-system-audit/SKILL.md) and [`design-tokens-scaffolding`](../design-tokens-scaffolding/SKILL.md).

## Hand-off

- **Visual decisions** (canvas temperature, accent choice, radius/shadow scale) → `visual-designer`.
- **Token → component implementation** (the `.card` class, the nav rail, regenerating generated HTML) → `frontend-implementer`.
- **Contrast / keyboard / motion sign-off** → `accessibility-auditor` via `accessibility-review`.

## References

- Knowledge: [`knowledge/card-tile-ui-pattern-2026.md`](../../knowledge/card-tile-ui-pattern-2026.md)
- Anchor donors + what to borrow: [`knowledge/design-references.md`](../../knowledge/design-references.md)
- This marketplace's living implementation: [`ravenclaude-core/dashboard-assets/README.md`](../../../ravenclaude-core/dashboard-assets/README.md)
