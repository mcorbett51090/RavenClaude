---
name: interface-craft
description: Raise a page or app surface to the craft bar of Apple, Stripe, Cloudflare, Starlink, Tesla and recent game menus. Pick a craft register per surface, apply its sourced moves (glass with opaque fallbacks, static-first heroes, qualify-first CTAs, opt-in motion, two-tone focus, OKLCH roles) and verify on the rendered page in both themes. Used by visual-designer, ux-designer and frontend-implementer.
---

# Skill: interface-craft

**Purpose:** take a surface from "correct" to "crafted" the way the brands the owner admires do it — and prove it
on the rendered page, not in the source. Primary agents: `visual-designer` (registers, tokens, motion), `ux-designer`
(qualify-first flows, one action per screen, states), `frontend-implementer` (the CSS/JS recipes and guardrails).

**Knowledge it applies (read the one your register needs):**
- [`../../knowledge/interface-craft-reference-brands-2026.md`](../../knowledge/interface-craft-reference-brands-2026.md) — Apple, Stripe, Cloudflare, Starlink, SpaceX, Tesla: move → principle → web build → what not to copy.
- [`../../knowledge/interface-craft-fundamentals-2026.md`](../../knowledge/interface-craft-fundamentals-2026.md) — the sourced numbers: motion durations and springs, colour, type, layout, states.
- [`../../knowledge/game-ui-lessons-for-the-web-2026.md`](../../knowledge/game-ui-lessons-for-the-web-2026.md) — focus, back stack, presets, juice, and the game patterns that must not reach the web.

## When to use

- A brief says "make it feel like Apple / Stripe / Tesla / Starlink / Cloudflare", "premium", "cinematic", "like a
  game menu", or "it looks generic".
- A page works but reads flat: no hierarchy of surfaces, motion everywhere or nowhere, a weak first screen.
- Reviewing glass/translucency, a hero video or WebGL, a configurator, a settings panel, or keyboard/gamepad focus.

Not for: brand strategy or naming (`brand-identity-studio`), a full new-site pipeline (`gold-standard-website-pipeline`
— this skill runs inside its G3/G5), or cloning one specific site's look (`ravenclaude-core` `design-clone`).

## Step 1 — Choose a register per surface (not per site)

| Register | Donors | Use for | Signature moves |
|---|---|---|---|
| **Cinematic product** | Apple, Tesla, Starlink | A business whose place or product photographs well; home heroes; one-product pages | Full-bleed art-directed image as the LCP; one short claim; sticky media with scrolling copy; one action; a chapter band between sections |
| **Qualify-first conversion** | Starlink, Tesla Design Studio | Service-area businesses, bookings, quotes, configurators | The qualifying input (ZIP, date, address) and a price anchor *in the hero*; one primary card, a quiet alternative; a CTA-only bar after the hero; running total in `aria-live` |
| **Precise system** | Stripe, Cloudflare Kumo | Pricing, docs, dashboards, forms, data-dense pages | Semantic OKLCH roles; a shared lightness ladder; ring *or* border; instant hover colour; tabular numbers; inline real-time validation |
| **Kinetic brand moment** | Persona/Metaphor menus, Stripe's wave | One to three hero surfaces at most | Bespoke motion as enhancement over a static first frame; capability-gated; paused off-screen; off under reduced motion |
| **Ten-foot focus** | Xbox / CommonUI / Forza | Kiosks, TV, keyboard-heavy apps, any grid of choices | Two-tone focus, roving tabindex, one Back semantic, focus restoration, input-glyph switching |

Most pages mix two: a cinematic or qualify-first hero over precise-system content. Write the chosen registers into the
design brief so the next agent does not re-decide.

## Step 2 — Apply the moves, each with its guardrail

Work through the list for the registers you chose. Every row is sourced in the knowledge files above.

1. **Hero = static first.** A preloaded `fetchpriority="high"` `<picture>` (AVIF/WebP) is the LCP. Video or WebGL
   enhances only when `prefers-reduced-motion: no-preference`, the tab is visible, the element is on screen, and (for
   WebGL) the context was created without a major performance caveat; cap DPR at 2; fade the still only after the first
   frame; **a visible pause control** for anything moving > 5 s.
2. **Glass only on floating chrome** (sticky nav, toolbar), never under body text, never glass on glass. Opaque
   fallback first (`.92` when `backdrop-filter` is unsupported); solid under
   `(prefers-reduced-transparency: reduce), (prefers-contrast: more)` — Safari only exposes the second. Keep α ≥ 0.6
   under primary text and **secondary-grey text off glass** (it measured ~3:1).
3. **One primary action per viewport.** Colour on the action's *background*, not its label; the action persists in a
   compact bar after the hero scrolls away; a second path for anything critical (phone beside the booking form; the form
   works without JS).
4. **Colour by role,** in `oklch()`: canvas / surface / band / ink / ink-soft / accent / on-accent / focus, each with a
   dark value. Components never use a raw hex. The accent is a **pair** (re-tuned per mode), and an accent used as a
   button ground is a separate invariant token from the accent used as ink.
5. **Motion opt-in.** Write motion inside `@media (prefers-reduced-motion: no-preference)`; ease-out; under 300 ms;
   `transform`/`opacity` only; **no motion on frequent or keyboard-initiated actions**; press feedback `scale(0.97)`;
   reveal-on-scroll only behind `@supports (animation-timeline: view())` with content complete without it; shimmer
   and skeletons count as motion.
6. **Type.** One family, Regular–Semibold; `text-wrap: balance` on headings; 65ch prose; 16 px+ inputs; tabular numbers on
   prices; a `clamp()` whose maximum is at least twice the base, tested at 200% zoom. Never self-host SF Pro.
7. **Shape.** Concentric radii (outer = inner + padding); ring *or* border, not border + shadow; every shadow ends in a
   1 px rim so it survives dark mode; targets ≥ 24 px (44 px on touch).
8. **Focus like a game menu.** Two-tone `:focus-visible` (outline + contrasting halo) at ≥ 3:1 on every background;
   sticky chrome never covers it (`scroll-padding-top`); closing any layer returns focus to its invoker; Esc/Back pops
   one layer.
9. **States.** Delay loading indicators 150–300 ms and hold them ≥ 300 ms; skeletons for pages, spinners for modules;
   empty, sparse, dense, error and **no-data** designed separately; deltas ("old → new") at decision points.
10. **Context-sensitive truth.** "Open now" is computed, never a hard-coded string; prices shown are the price paid
    (never net of speculative savings).

## Step 3 — Verify on the rendered page (the only verdict that counts)

Run the [`visual-feedback-loop`](../../../ravenclaude-core/skills/visual-feedback-loop/SKILL.md) and, with a headless
browser, measure:

| Check | Pass |
|---|---|
| Screenshots at 390 and 1440 px, light **and** dark | No band vanishes into the page in dark mode; nothing reads as one muddy band |
| Horizontal overflow at 320 px | `scrollWidth − innerWidth` = 0 on every page |
| Heading outline | exactly one `<h1>`; no level skips |
| Targets | every visible interactive element ≥ 24×24 px |
| Composited contrast | text over photos, scrims and glass measured on rendered pixels, both themes |
| Reduced motion forced on | nothing moves; no content hidden behind an animation |
| Keyboard walk | focus always visible, never obscured, restored after every dialog/drawer |
| Images | each alt describes what is **actually in the frame** — look at the image |
| LCP element | the still image or the H1 text, present in server HTML (never JS-rendered copy) |

A source-level pass is not a pass. Record what you measured and what you could not.

## Step 4 — Report

List the registers chosen, the moves applied, every guardrail measured with its number, and every move deliberately
**not** taken with the reason (budget, legibility, maintenance — e.g. "no WebGL hero: the static image already meets the
brief and the device mix is mostly phones").

## Anti-patterns this skill exists to stop

- Glass under paragraphs; tinting every control; light display weights in a face not drawn for them.
- A WebGL or video hero with no static LCP, no capability gate, no pause control.
- Motion on every hover and keypress; scroll-jacking; mandatory full-page snap; unskippable intros.
- Multiple `<h1>`s chosen by font size; marketing copy rendered only by client JS.
- Brand orange (or any light accent) as small text on white without measuring it.
- Hover-only reveals; hold-only destructive confirmation; text inside images.
- A bespoke animated treatment on every screen instead of one to three hero moments.
