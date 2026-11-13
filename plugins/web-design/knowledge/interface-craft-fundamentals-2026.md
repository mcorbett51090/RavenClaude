# Interface craft fundamentals (2026): motion, colour, type, layout, states

> **Retrieved:** 2026-10-26. Every number below carries its source; anything without one is marked
> `[unverified]` and should not be quoted as a rule. Browser status is from the webstatus.dev / `web-features`
> Baseline data on that date.
>
> These are the rules underneath [`interface-craft-reference-brands-2026.md`](interface-craft-reference-brands-2026.md)
> (what Apple, Stripe, Cloudflare, Starlink and Tesla do) and
> [`game-ui-lessons-for-the-web-2026.md`](game-ui-lessons-for-the-web-2026.md) (what game menus do). The
> [`interface-craft`](../skills/interface-craft/SKILL.md) skill applies them. Where two respected sources
> disagree, both are shown and the house choice is stated — pick one per system and keep it.

## 1. Motion

| Rule | Detail | Source |
|---|---|---|
| **Keep UI motion short** | "UI animations should generally stay under 300ms." Stripe's 2017 rule: most animations under 500 ms. | [Emil Kowalski, 7 tips](https://emilkowal.ski/ui/7-practical-animation-tips); [Stripe 2017](https://stripe.com/blog/connect-front-end-experience) |
| **Animate rarely-used, high-meaning moments; never frequent or keyboard actions** | "Never animate keyboard-initiated actions"; command menus used hundreds of times a day lose their motion; macOS context menus appear without animation. Apple: "generally avoid adding motion to UI interactions that occur frequently". | [Emil, Good vs Great](https://emilkowal.ski/ui/great-animations); [Rauno Freiberg](https://rauno.me/craft/interaction-design); [HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion) |
| **Only cheap properties** | `transform` and `opacity`; never `transition: all`; prefer CSS → WAAPI → JS. | [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines); Stripe 2017 |
| **Ease-out for UI** | Built-in CSS curves are "usually not strong enough"; use a custom ease-out. `ease-in` feels slow. | Emil, 7 tips |
| **Exit vs enter** | Material 2: drawer opens 250 ms, closes 200 ms; card expands 300 ms, collapses 250 ms; exits use accelerate easing. Emil: ease-out for entering *or* leaving. **House choice:** exits ~20% shorter, ease-out both ways. | [Material 2 speed](https://m2.material.io/design/motion/speed.html) vs Emil |
| **Material 3 durations** | Short 50/100/150/200 ms · Medium 250–400 · Long 450–600 · ExtraLong 700–1000. Curves: emphasized `cubic-bezier(0.2,0,0,1)`, emphasized-decelerate `(0.05,0.7,0.1,1)`, emphasized-accelerate `(0.3,0,0.8,0.15)`. | androidx `MotionTokens.kt` (read 2026-10-26) |
| **Springs — Apple** | Duration + bounce. Bounce 0 is the versatile default; ~15% barely bouncy; 30% noticeable; "cautious about using values higher than around 0.4". Springs keep velocity when retargeted, so they are interruptible. Physics: mass 1, stiffness (2π/duration)², damping 1 − 4π·bounce/duration. | [WWDC23 Animate with springs](https://developer.apple.com/videos/play/wwdc2023/10158/) |
| **Springs — Material 3 Expressive** | Expressive scheme for "prominent UI elements and hero interactions"; Standard for "utilitarian UI elements and recurring interactions". Spatial springs (position/size) may overshoot; effects springs (colour/opacity) are critically damped. Expressive damping/stiffness: fast 0.6/800, default 0.8/380, slow 0.8/200; Standard: 0.9/1400, 0.9/700, 0.9/300. | androidx `ExpressiveMotionTokens.kt` / `StandardMotionTokens.kt` |
| **Springs in CSS** | `linear()` (Baseline widely available) with ~50 sample points makes a convincing spring; a CSS spring cannot be retargeted — on interruption it "turns around instantly". Keep custom curves to ~20% of animations; `@supports` fallback. | [Josh Comeau, linear()](https://www.joshwcomeau.com/animation/linear-timing-function/) |
| **Press feedback** | `scale(0.97)` on `:active`; never animate from `scale(0)` (start ≥ 0.9); scale popovers from their trigger (`transform-origin`). | Emil, 7 tips |
| **Tooltips** | Delay the first; peers that follow open instantly with no animation. | Emil; Vercel |
| **Interruptible** | Animations are cancelable by user input; destructive gestures commit only at gesture end. | Vercel; Rauno |
| **Reduced motion: start from none** | Write motion inside `@media (prefers-reduced-motion: no-preference)`; avoid the global `0.01ms !important` hack as the primary strategy; under reduce, swap movement for a fade. | [Josh Comeau, prefers-reduced-motion](https://www.joshwcomeau.com/react/prefers-reduced-motion/); HIG Accessibility |
| **Auto-moving content** | Muted, non-essential loops only; anything moving > 5 s needs pause/stop/hide (WCAG 2.2.2). Shimmer and skeletons count as motion (Cloudflare zeroes them under reduce). | [WCAG 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html); cloudflare.com CSS |
| **Hover colour changes are instant** | No colour transitions on hover in dense UI. | [Cloudflare Kumo skill](https://kumo-ui.com/skill) |
| **Stagger** | No sourced number found. | `[unverified]` — keep the whole sequence inside the duration budget |

```css
/* House motion tokens: no-motion-first, ease-out, short. */
:root { --ease-out: cubic-bezier(0.2, 0, 0, 1); --dur-1: 150ms; --dur-2: 250ms; --dur-3: 400ms; }
@media (prefers-reduced-motion: no-preference) {
  .btn { transition: transform var(--dur-1) var(--ease-out), box-shadow var(--dur-1) var(--ease-out); }
  .btn:active { transform: scale(0.97); }
  .reveal { animation: fade-up linear both; animation-range: entry 0% cover 30%; }
  @supports (animation-timeline: view()) { .reveal { animation-timeline: view(); } }
}
@keyframes fade-up { from { opacity: 0; transform: translateY(12px); } }
```

## 2. Colour

- **Build palettes in a perceptual space.** OKLCH's L is perceived lightness; HSL's is not
  ([Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)). Linear moved to LCH and
  cut each theme from **98 variables to 3 inputs (base, accent, contrast)**; the contrast input generates
  high-contrast themes ([Linear, 2024-03-28](https://linear.app/now/how-we-redesigned-the-linear-ui)).
- **Shared lightness ladder across hues** makes contrast a rule: Stripe's "at least five levels apart = small
  text passes; four = icons and large text" ([2019](https://stripe.com/blog/accessible-color-systems)).
- **Semantic step scales.** Geist: 10 steps per hue — 100–300 backgrounds (default/hover/active), 400–600
  borders, 700–800 high-contrast fills, 900–1000 text ([vercel.com/geist/colors](https://vercel.com/geist/colors)).
  Kumo names roles: canvas, base, elevated, recessed, line, subtle ([kumo-ui.com/colors](https://kumo-ui.com/colors)).
  Components consume roles, never palette steps — enforce it with a lint rule.
- **Contrast standard status (October 2026).** WCAG 2.2 is the referenceable standard and the legal floor. APCA
  was dropped from WCAG 3 drafts in July 2023; the April 2026 editor's draft says "The contrast algorithm used in
  WCAG 3 is yet to be determined" ([Roselli, 2026-04-10](https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html)).
  Vercel's guidelines prefer APCA. **House rule:** meet WCAG 2 AA; use APCA as an additional perceptual check,
  especially for thin type on dark grounds. Never claim APCA conformance.
- **Dark mode is not inverted light mode.** Reverse the lightness steps and keep hue (Cloudflare: naive inversion
  turned light blue into "dull dark orange"); a near-black ground (`#1D1D1D` Cloudflare, `#121212` Material) where
  elevation must show, with **higher surfaces lighter** rather than shadowed
  ([Cloudflare 2021](https://blog.cloudflare.com/dark-mode/); [Material dark theme](https://m2.material.io/design/color/dark-theme)).
  A drop shadow carries almost nothing on a dark ground — add a 1 px rim. An accent is a **pair**, re-tuned per
  mode (cloudflare.com: `#ff5010` light → `#ff7038` dark). Interactive states get *more* contrast than rest.
- **An accent used as a ground and as ink needs two tokens.** Its ratio to the ink on top of it does not depend on
  the page theme, so the ground value stays invariant while the ink value flips. Conflating them is the classic
  dark-mode button failure.
- **Set `color-scheme`** per theme and a `theme-color` meta; apply a stored theme in an inline `<head>` script
  **before paint** (cloudflare.com does).

## 3. Typography

- **Fluid type, zoom-safe.** Viewport-unit type can stop text reaching 200% under zoom (WCAG 1.4.4). Never set a
  `clamp()` maximum below twice the base; use `rem` in the preferred value; test at 200% zoom
  ([Roselli](https://adrianroselli.com/2019/12/responsive-type-and-zoom.html)). Stepped sizes per breakpoint
  (Apple 48/40/32 px; Starlink H1 64→36 px) are the safe alternative.
- **Line length** 50–75 characters, at most 80 ([Baymard](https://baymard.com/blog/line-length-readability)) —
  `max-width: 65ch` for prose.
- **`text-wrap: balance`** on headings (Baseline newly available); **`pretty`** on paragraphs only as
  enhancement (no Firefox).
- **Weights:** Regular to Semibold. "Avoid light font weights" (HIG); Kumo bans `font-bold` for headings in favour
  of semibold. Light display weights work only in faces drawn for them (Stripe's Söhne).
- **Numbers:** `font-variant-numeric: tabular-nums` on prices and comparisons; `&nbsp;` between a value and its
  unit (Vercel).
- **Optical sizes:** `font-optical-sizing` (widely available) with an `opsz` variable face, or switch display/text
  faces by size as apple.com does (display ≥19 px, text ≤17 px).
- **Body size:** 16–17 px for reading; inputs ≥ 16 px on mobile (iOS zooms smaller fields — Stripe). 14 px content
  text is a *dashboard* density rule (Kumo), not a marketing-page one.
- **Licensing:** SF Pro may not be used to display website content ([Apple fonts](https://developer.apple.com/fonts/)).
  Check every web font licence before shipping.

## 4. Layout, spacing, shape, density

- **Container queries** (size; widely available) — components respond to their slot, not the viewport. They need
  `container-type: inline-size` on an ancestor or they do nothing.
- **Spacing:** an 8 px base with a 4 px sub-grid (Stripe's `--hds-space-core-100: 8px` with 4/12/20 half-steps).
  The "4/8 pt grid" as an industry standard is `[unverified]` — cite a system, not a law.
- **Few breakpoints** (Apple 734/1068/1441; Stripe 640/940/1264); content adapts between them.
- **Concentric radii:** outer = inner + padding (Apple WWDC25 356; Kumo).
- **Elevation:** a ring *or* a border, not border + drop shadow (Kumo); at least two shadow layers — ambient and
  direct — when you do use shadows (Vercel).
- **Density:** keep information rich, let navigation recede — "Don't compete for attention you haven't earned";
  "Structure should be felt not seen" ([Linear, 2026-03-12](https://linear.app/now/behind-the-latest-design-refresh)).
- **Targets:** ≥ 24×24 CSS px (WCAG 2.5.8 AA); 44 px on touch (Apple HIG 44 pt; Vercel). Starlink's primary
  button is 56 px tall on mobile.

## 5. Interaction states and perceived performance

| Threshold / rule | Source |
|---|---|
| 0.1 s feels instant; 1 s keeps flow (show work is happening); 10 s keeps attention (percent done + cancel) | [NN/g response times](https://www.nngroup.com/articles/response-times-3-important-limits/) |
| Under 1 s no indicator; whole page → skeleton; single module → spinner; > 10 s → progress bar + estimate | [NN/g skeleton screens](https://www.nngroup.com/articles/skeleton-screens/) |
| Show a loading indicator after 150–300 ms, keep it ≥ 300–500 ms; POST/PATCH/DELETE under 500 ms | Vercel |
| Skeletons mirror the final layout exactly (no CLS); design empty, sparse, dense, error states | Vercel |
| Optimistic UI rolls back or offers Undo on failure | Vercel |
| Submit stays enabled until the request starts, then disables with a spinner and an idempotency key; errors beside their fields; focus the first error | Vercel; [Stripe checkout](https://stripe.com/resources/more/one-step-checkout) |
| "No data" is its own state, never folded into "error" (Starlink grey = no telemetry 7+ days) | [Starlink support](https://www.starlink.com/support/article/6aff51c6-254a-700e-c175-4c05a2b8c894) |
| Every metric shown to a customer carries "what this means for you" | Starlink support |
| A `<video>`'s LCP is the poster or first frame, whichever is earlier; good LCP ≤ 2.5 s at p75 | [web.dev LCP](https://web.dev/articles/lcp) |
| Doherty threshold — respond within 400 ms | [Laws of UX](https://lawsofux.com/doherty-threshold/) |

## 6. Design-engineering process

- **Tokens are a standard now:** the DTCG Format **2025.10** is the first stable version (2025-10-28), with OKLCH,
  Display P3, aliases and theming ([W3C DTCG](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/)).
  Emit DTCG JSON, generate CSS custom properties from it.
- **Layer the cascade like the system:** `@layer base, components` (starlink.com ships `@layer starlink-ui.base` →
  `.components`) — tokens → primitives → components, page CSS last.
- **Prototype in code, behind a flag.** Linear's 2024 redesign: ~6 weeks, daily designer–engineer pairing, a working
  version at the end of week 1, a feature flag and dev-toolbar toggle (Linear 2024-03-28). In 2026 a two-person team
  used coding agents to build a token colour tool and prototype competing directions (Linear 2026-03-12).
- **One brand slot, locked neutrals** for templated products (Stripe Apps limits custom styling "to ensure a high
  accessibility bar").
- **Judge the render, not the source.** Screenshots in both themes at 390 and 1440 px, measured contrast on
  composited pixels, focus walked by keyboard.

## 7. The taste checklist (each line sourced above)

1. One `<h1>`; one primary action per viewport.
2. The qualifying input (address/ZIP/date) above the fold when the business has one.
3. Motion under 300 ms; `transform`/`opacity` only; none on frequent actions; a reduced-motion path that starts from no motion.
4. WCAG 2 AA everywhere, plus a perceptual (APCA) sanity check on thin or dark text.
5. Translucent chrome only with an opaque fallback, α ≥ 0.6 under primary text, secondary text kept off glass.
6. Every state designed: loading (delayed), empty, sparse, dense, error, no-data.
7. Tabular numbers on prices; 65ch prose; 16 px+ inputs.
8. Targets ≥ 24 px (44 px on touch); concentric radii; ring *or* border, not both with a shadow.
9. Dark mode by reversed lightness, near-black ground, rim instead of shadow, the accent as a pair.
10. Test at 200% zoom and at 390 px wide, in both themes.

## Sources

Retrieved 2026-10-26: Emil Kowalski (7 Practical Animation Tips; Good vs Great Animations); Rauno Freiberg
(Invisible Details of Interaction Design, 2023); Vercel Web Interface Guidelines and Geist Colors; Linear (2024-03-28,
2026-03-12); Apple WWDC23 10158, WWDC25 356, HIG Motion / Accessibility; androidx Material 3 motion token sources;
Material 2 Motion Speed and Dark theme; Josh W. Comeau (linear(), prefers-reduced-motion); Evil Martians (OKLCH);
Adrian Roselli (WCAG3 contrast April 2026; responsive type and zoom); W3C WCAG 2.2 Understanding 2.2.2 / 2.5.8;
Baymard (line length); NN/g (response times; skeleton screens); Laws of UX; web.dev LCP; W3C DTCG 2025.10; Stripe blog
and checkout guidance; Cloudflare dark-mode blog and Kumo; Starlink support; webstatus.dev Baseline API.
