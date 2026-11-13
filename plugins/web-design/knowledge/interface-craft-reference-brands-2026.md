# Interface craft from Apple, Stripe, Cloudflare, Starlink and Tesla (2026)

> **Retrieved:** 2026-10-26, from primary sources wherever they exist (HIG, WWDC transcripts, company engineering
> blogs, design-system docs) and from the **live production HTML/CSS/JS** of apple.com, stripe.com,
> cloudflare.com and starlink.com, read the same day. Re-verify before quoting a number in client work: these
> sites ship weekly.
>
> **Labels.** **OBS** = observed in a source or a production file on that date. **INF** = an inference from
> observations; it can be wrong while every observation holds. **COMPUTED** = a WCAG 2.x contrast ratio this
> research calculated (no source claims it). `[unverified]` = not confirmed this session — do not state it as
> fact.
>
> **What this file is for.** The owner of this marketplace named these brands as the bar. This is the
> transferable craft — each move, the principle it serves, how to build it on the web in 2026, and what *not*
> to copy. It complements [`design-references.md`](design-references.md) (dev-tool marketing donors) and
> [`gold-standard-website-references-2026.md`](gold-standard-website-references-2026.md) (whole-site
> exemplars). The general rules underneath every brand here are in
> [`interface-craft-fundamentals-2026.md`](interface-craft-fundamentals-2026.md); the procedure that applies
> them is the [`interface-craft`](../skills/interface-craft/SKILL.md) skill.

## The twelve rules that transfer

| # | Rule | Who does it | § |
|---|---|---|---|
| 1 | **Translucency belongs to a floating control layer, never to content** — and every glass surface has a designed opaque fallback that user preferences switch on. | Apple | 1 |
| 2 | **The hero is a static image first, enhanced second.** The LCP element is a preloaded `fetchpriority="high"` image; video or WebGL fades in only after its first frame, only on capable devices. | Stripe, Apple | 1, 2 |
| 3 | **Motion is opt-in:** written inside `prefers-reduced-motion: no-preference`, not removed afterwards. | Stripe (59 such blocks), WebKit | 2 |
| 4 | **Colours are semantic tokens chosen by role,** in a perceptual space (`oklch()`), resolved per mode with `light-dark()`; a lint rule bans raw palette colours in components. | Cloudflare Kumo | 3 |
| 5 | **Contrast is a rule of the palette, not a per-pair guess:** "any two colors at least five levels apart pass small text". | Stripe (2019) | 2 |
| 6 | **Concentric radii:** outer radius = inner radius + padding. | Apple, Kumo | 1, 3 |
| 7 | **Hierarchy from layout, grouping and weight — not decoration.** Semibold over bold, sentence case over caps. | Apple, Kumo | 1, 3 |
| 8 | **Forms ask only for what is needed,** validate inline next to the field in real time, keep what the user typed, and use ≥16 px input text on mobile. | Stripe | 2 |
| 9 | **Qualify in the hero.** The first screen answers "can I get it, and what does it cost?" with an input, a price anchor and one button. | Starlink | 4 |
| 10 | **One primary action at a time,** persisting as a compact bar after the hero scrolls away. | Starlink, Tesla | 4, 6 |
| 11 | **The browser presents; the server decides.** Prices, availability and bookings are validated server-side; critical actions have a second path. | SpaceX Dragon | 5 |
| 12 | **Dark mode is not inverted RGB.** Reverse the lightness steps only, keep hue, use a near-black (not #000) where UI depth must show. | Cloudflare, Material | 3 |

---

## 1. Apple

### 1.1 Liquid Glass, the criticism, and the correction

| Date | Event | Source |
|---|---|---|
| 2025-06-09 | Liquid Glass introduced at WWDC25; the HIG Materials page describes two material types: Liquid Glass and standard materials. | [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials) |
| 2025-10-10 | NN/g, *"Liquid Glass Is Cracked, and Usability Suffers in iOS 26"* — text over translucent controls loses contrast over busy content; shrunken targets; "Motion for motion's sake is not usability". | [nngroup.com](https://www.nngroup.com/articles/liquid-glass/) |
| iOS 26.1 | A **Clear / Tinted** setting; Tinted "reduces transparency a little… and increases contrast slightly". | [TidBITS 2025-10-21](https://tidbits.com/2025/10/21/ios-26-1-to-add-optional-opacity-to-liquid-glass/) |
| 2026-06-08 | WWDC26: "improvements to legibility, customizability, and consistency"; a transparency slider from ultra-clear to fully tinted (secondary coverage). | [Apple Newsroom](https://www.apple.com/newsroom/2026/06/apple-aids-app-development-with-new-intelligence-frameworks-and-advanced-tools/) |

**The lesson for agents (INF):** even Apple shipped glass people had to turn down. On the web, design the
**opaque state first** and treat translucency as the enhancement.

### 1.2 Signature moves

| Move | Principle | Source |
|---|---|---|
| Glass only on the **functional layer** (tab bars, toolbars, sidebars). "Don't use Liquid Glass in the content layer." | Separate controls from content | HIG Materials |
| **Regular** glass for anything with text; **Clear** only over rich media, with a **35% dark dimming layer** over bright content. | Legibility first | HIG Materials |
| **No glass on glass**; elements on top of glass use fills and vibrancy. | Avoid layered clutter | [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/) |
| Content **dissolves under floating bars** (a scroll-edge effect), dimming over dark content; one effect per view, "not decorative". | Preserve contrast where UI meets content | WWDC25 219, [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/) |
| **Tint sparingly** — "When every element is tinted, nothing stands out." Colour goes on the primary action's background, not its label. | Reserve emphasis | WWDC25 219, [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color) |
| **Concentric shapes** — child radius = parent radius − padding; capsules use radius = height / 2. | Continuity between nested containers | WWDC25 356 |
| "Hierarchy should be expressed through layout and grouping"; type "bolder and left-aligned". | Structure over ornament | WWDC25 356 |
| **Springs** set by perceived duration + bounce; default bounce 0; be "cautious about values higher than around 0.4"; springs stay continuous when interrupted. | Interruptible motion | [WWDC23 10158](https://developer.apple.com/videos/play/wwdc2023/10158/) |
| "Generally avoid adding motion to UI interactions that occur frequently"; let people cancel motion. Reduce Motion = fades instead of x/y/z movement, tighter springs, no animating into blurs. | Motion is optional and brief | [HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion), [HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) |
| Every custom colour has light, dark **and increased-contrast** variants — "even if your app ships in a single appearance mode". | Adaptivity is the default | HIG Color |

**Sourced numbers (HIG):** iOS body 17/22 pt, minimum 11 pt; "avoid light font weights"; contrast 4.5:1 at
≤17 pt, 3:1 at 18 pt or bold; hit targets 44×44 pt default, 28×28 pt minimum; text must enlarge to at least
200%. Spring physics: mass 1; stiffness = (2π ÷ duration)²; damping = 1 − 4π·bounce ÷ duration.

### 1.3 How apple.com is built (OBS in production files, 2026-10-26)

No first-party engineering write-up about apple.com's front end was found; these rows come from page source.

| Observation | What it teaches |
|---|---|
| Global nav: `backdrop-filter: saturate(180%) blur(20px)` over `rgba(250,250,252,.8)`; without `backdrop-filter` support the background is **`.92`** — nearly opaque. | The fallback is designed *more opaque*, not merely unblurred. |
| `@media (inverted-colors: inverted) or (prefers-contrast: more) or (prefers-reduced-transparency)` gives text over imagery a **solid backing**. | Three preferences OR'd together; text over photos gets a backing when asked. |
| Headline 48 / 40 / 32 px by breakpoint, weight 600, line-height ~1.08, slight negative tracking; body 17 px; display face ≥19 px, text face ≤17 px. | Optical sizes switched by hand; tracking tightens and leading drops as size grows. |
| Breakpoints `734`, `1068`, `1441` px. | Few breakpoints; content adapts between them. |
| Text `#1d1d1f` (not black), surface `#f5f5f7`, one blue for actions (`#0071e3`). | Near-black ink, a cool off-white, a single action colour. |
| Product pages: 13 `<video preload="none" muted playsinline>` with labelled play/pause buttons, 387 `<picture>`, 0 `<canvas>` in the HTML; scroll storytelling via `position: sticky` and their own JS (no `animation-timeline`). | INF: lazily attached video with a **user pause control** has replaced the 2014–2020 canvas image sequences (~55.8 MB measured for one full sequence by [CSS-Tricks, 2020](https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/)). |

### 1.4 Build it on the web

```css
/* Glass nav with honest fallbacks — values mirror apple.com; names are ours. */
.nav { background: oklch(98.6% 0.002 286 / .92); }              /* no-blur fallback: near-opaque */
@supports (backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px)) {
  .nav { background: oklch(98.6% 0.002 286 / .8);
         -webkit-backdrop-filter: saturate(180%) blur(20px); backdrop-filter: saturate(180%) blur(20px); }
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more), (inverted-colors: inverted) {
  .nav { background: var(--surface-solid); -webkit-backdrop-filter: none; backdrop-filter: none; }
}
```

- **Glass contrast floor (COMPUTED).** Composite the tint over pure black (light glass) or pure white (dark
  glass) — blur only averages the backdrop, so this is the worst case. `#1d1d1f` text on light glass at α .8
  over black = **10.1:1**; at α .6 = 5.7:1; at α .5 = **4.09:1, fails AA**. Secondary grey `#6e6e73` on α .8 glass
  over black = **3.03:1** — fails. **Rule: α ≥ 0.6 for primary text; keep secondary-grey text off glass.**
- **Safari does not implement `prefers-reduced-transparency`** (MDN BCD, 2026-10-26; Chrome 118+, Firefox
  behind a flag). On Apple devices `prefers-contrast: more` is the signal you can actually detect — always OR
  them, as apple.com does.
- **Scroll storytelling without a JS engine:** `position: sticky` media + `animation-timeline: view()` and
  `animation-range`, inside `@media (prefers-reduced-motion: no-preference)` and
  `@supports (animation-timeline: view())`. Declare `animation-timeline` *after* the `animation` shorthand
  ([WebKit guide](https://webkit.org/blog/17101/a-guide-to-scroll-driven-animations-with-just-css/)). Content
  must be complete without it — scroll-driven animations are not Baseline (no Firefox).
- **Springs in CSS:** `linear()` easing sampled from the duration/bounce formula above; bounce 0 for chrome,
  ≤ 0.3 for playful elements; a fade instead of movement under reduced motion.

### 1.5 Do not copy

- **Self-hosting SF Pro.** Apple's licence allows it only for mock-ups of Apple-platform UI and forbids using
  it to display website content ([developer.apple.com/fonts](https://developer.apple.com/fonts/)). Use a
  system stack or a licensed variable face with an optical-size axis.
- Glass under body text, inside cards, or on glass. Tinting every control. Light display weights (the HIG
  itself says avoid them).
- Autoplay video with no pause control; a full-resolution frame sequence on mobile.

---

## 2. Stripe

### 2.1 stripe.com (OBS in production files, 2026-10-26; Next.js SSR, `--hds-*` tokens)

| Move | Principle |
|---|---|
| **The hero "wave" is WebGL over a static LCP image.** `<link rel="preload" as="image" … fetchpriority="high">` for per-breakpoint WebPs; a `.single-wave__static` image sits under the canvas and fades out (`.25s`) only after the first frame draws. | The art is visible at first paint; motion is a bonus. |
| **Capability-gated renderer:** WebGL requested with `failIfMajorPerformanceCaveat: true`; on failure the static image simply stays. Device pixel ratio capped at 2; the dark wave is disabled on `(pointer: coarse)`. | Never punish a low-end device. |
| **Frame-rate governor:** the render loop suspends on `visibilitychange`, estimates refresh rate, and steps down a warning level when frames miss by >10%; IntersectionObserver gates rendering. | Spend GPU only when visible and affordable. |
| **Motion is opt-in in CSS:** 59 `prefers-reduced-motion: no-preference` blocks vs 15 `reduce`. Whether the wave itself checks reduced motion is `[unverified]`. | Progressive enhancement. |
| One variable family (Söhne, `font-weight: 1 1000`), mostly weight 300, slight negative tracking, `text-wrap: pretty` ×25 and `balance` ×6, a `.tabular-nums` utility. | One expressive family, carefully finished. |
| 8 px spacing base with 4 px half-steps; section gaps 56 → 96 px; buttons 44–48 px; small radii (2/4/6/16/32). | Precision and restraint. |
| Headings `#061b31` (deep navy, not black); cool blue-grey neutrals; brand `#533afd`. | Brand tone carried in the neutrals. |
| Easing `cubic-bezier(.25,1,.5,1)` (×44), durations mostly .3–.5 s. | Fast start, soft landing. |
| CSS scroll timelines replace JS listeners (a swipe-to-dismiss overlay; nav arrows that appear only when the nav overflows). | No scroll handlers. |

History (sourced): the 2017 diagonal stripes were a 10-column CSS grid skewed −12°; Stripe's own rules then
were *animate only `transform` and `opacity`, keep most animations under 500 ms, start from
IntersectionObserver, honour reduced motion, draw devices in CSS*
([Connect: behind the front-end experience, 2017-06-19](https://stripe.com/blog/connect-front-end-experience)).
No `skewY` remains in the 2026 CSS — INF: that signature has been retired. The 2020 "minigl" gradient is known
only from third-party reconstructions.

### 2.2 The colour system ([Designing accessible color systems, 2019-10-15](https://stripe.com/blog/accessible-color-systems))

Rebuilt in a perceptual space so every hue follows the same lightness curve per level, with an internal tool
giving real-time accessibility feedback. The guarantee: **"Any two colors are guaranteed to have sufficient
contrast for small text if they are at least five levels apart, and at least four levels apart for icons and
large text."** Web version: an `oklch()` scale per hue with **shared L values per step**, the "N steps apart"
rule written into the tokens, and a CI check. (COMPUTED from live tokens: `#64748d` on white 4.75:1 — passes
thinly; `#7d8ba4` 3.44:1 — large text only.)

### 2.3 Forms and checkout

- **Appearance API** — three tiers: theme (`stripe` / `night` / `flat`) → variables (`colorPrimary`,
  `fontSizeBase`, `spacingUnit`, `borderRadius`, `focusBoxShadow`, …) → rules on **public class names only** with
  an allow-list of states and properties. *Brand freedom inside guardrails that keep forms accessible*
  ([docs](https://docs.stripe.com/elements/appearance-api)). "Choose a font size of at least 16px for input fields
  on mobile."
- **Checkout guidance** ([one-step checkout, 2025-07-10](https://stripe.com/resources/more/one-step-checkout)):
  "Every form error should show up in real time, in or next to the field where the issue is"; "preserve the data
  the customer already entered"; "Use only the fields and information required".
- **Stripe Apps** limit custom styling "to ensure a high accessibility bar" — the only free brand colour is the
  app indicator ([design guide](https://docs.stripe.com/stripe-apps/design)). A model for a small-business
  template: **one brand slot, locked neutrals**.

### 2.4 Do not copy

- A WebGL hero without the static LCP image, capability check, DPR cap and visibility pause.
- Weight-300 body text in a face that is not built for it, or on tinted grounds.
- The diagonal-section look (Stripe has moved on). A hand-built payment form — use Elements themed through the
  Appearance API, which keeps PCI scope and accessibility with Stripe.

---

## 3. Cloudflare

### 3.1 Kumo, the product design system ([github.com/cloudflare/kumo](https://github.com/cloudflare/kumo), MIT, on Base UI)

| Token | Light | Dark |
|---|---|---|
| canvas | oklch(98.75% 0 0) | oklch(10% 0 0) |
| base | #fff | oklch(17% 0 0) |
| elevated | oklch(98% 0 0) | oklch(12% 0 0) |
| line | oklch(14.5% 0 0 / 0.1) | oklch(32% 0 0) |
| brand | oklch(0.5772 0.2324 260) | `color-mix(in oklch, <brand>, black 10%)` |
| text subtle | oklch(55.6% 0 0) | oklch(70.8% 0 0) |

Source: [kumo-ui.com/colors](https://kumo-ui.com/colors). Mode via `data-mode`, tokens resolved with
`light-dark()`, and "Always use semantic tokens instead of raw Tailwind colors" — enforced by a
`no-primitive-colors` lint rule. Surfaces layer canvas → base → elevated → recessed.

**Agent design rules** ([kumo-ui.com/skill](https://kumo-ui.com/skill)): content text 14 px (dashboard density;
16 px+ is for headings); never uppercase headings; `font-semibold` for headings, never `font-bold`; **"Never use
borders with drop shadows"** — use a ring; concentric radii; **"Color changes on hover must be immediate"**; never
conditionally render dialogs (use the `open` prop so exit animations run); a border separates sticky elements
from content.

### 3.2 cloudflare.com (OBS, 2026-10-26 — built with Astro)

| Observation | What it teaches |
|---|---|
| `generator: Astro v6.3.7`; Kumo tokens in the marketing CSS; `light-dark(` ×294, `oklch(` ×773, `color-mix(` ×2002, `@container` ×7. | Modern colour and container queries are production-safe at this scale. Marketing and product share one token system. |
| Brand orange **re-tuned per mode** (`#ff5010` light → `#ff7038` dark); warm neutrals to match. | An accent is not one hex; it is a pair. |
| **Overflow fade masks:** `@property` numbers animated by `animation-timeline: scroll(self x)` drive a `mask-image` gradient on `[data-overflowing]`, inside `@supports`. | Horizontal scrollers fade at the edge only when there is more — zero JS. |
| **View Transitions** morph a domain search field into its results (`view-transition-name`), zeroed under reduced motion. | Spatial continuity for one high-value flow. |
| 11 reduced-motion blocks, **including loading shimmer and skeletons**. | Shimmer is motion too. |
| An inline `<head>` script applies the stored theme or the system preference **before paint**, and follows system changes unless the user chose. | No flash of the wrong theme. |
| Hero credibility from concrete numbers ("330+ cities"). | Specific beats superlative. |

### 3.3 Dark mode and data density

- [Dark Mode for the Cloudflare Dashboard (2021-09-29)](https://blog.cloudflare.com/dark-mode/): 10 hues × 10
  lightness steps; dark mode prototyped by **reversing the lightness scale only** (naive RGB inversion turned light
  blue into "dull dark orange"); background **#1D1D1D**, pure black rejected as harsh; every button state checked
  for AA.
- [Radar redesign (2026-10-08)](https://blog.cloudflare.com/radar-redesign/): lead with the most timely, concrete
  data (outages); **the map is the navigation**; an equal-weight bento grid became **tabs with summary stats and a
  CTA** because it "keeps the page from feeling overwhelming".

### 3.4 Do not copy

- Brand orange `#f6821f` **as text on white: 2.58:1 (COMPUTED) — fails.** `#ff5e1f` with white text is 3.06:1
  (large text only); with `#171717` text 5.87:1. INF: small-business orange buttons usually need **dark labels**.
- 14 px body text on a consumer marketing page — Kumo's rule is for dashboards. Reading content stays 16–17 px.

---

## 4. Starlink (starlink.com, rendered and measured 2026-10-26)

| Element | Measured |
|---|---|
| Hero | H1 "Fast, affordable internet" (64 px desktop / 36 px mobile, `#fafafa` on `#000`) and a card with **"RESIDENTIAL STARTING AT $55/mo"**, a labelled **Address** field and one **Get Started** button (56 px tall; 286×56 on mobile). A second, collapsed card for the alternative path. |
| After the hero | The six-item nav collapses into a **floating bar with only the wordmark and Get Started**, animated with `transform`/`opacity` at 0.3 s. |
| Sections | Alternating full-bleed photo and copy, **each ending in one CTA**; a proof strip (✓ Plug & Play · ✓ Unlimited Data · ✓ 30-Day Trial); Good / Great / Best plan ladder. |
| Text hierarchy | Body `rgba(250,250,250,.7)` = **9.57:1** on black; disclaimers `.55` = **6.04:1** (COMPUTED) — quieter but still AA. |
| Media | 8 `<picture>` with art-directed `<source media>`; **no video**; one sticky media block exactly one viewport tall. |
| CSS | `@layer starlink-ui.base` → `.components`; tokens (`--color-bg`, `--spacing-md`); `color-mix(in oklab, …)`; 13 reduced-motion rules. |

**The app** ([support pages](https://www.starlink.com/support/article/6aff51c6-254a-700e-c175-4c05a2b8c894)):
a guided camera **obstruction check before you buy**; status colours where **grey = "no telemetry for 7+ days"** —
"no data" gets its own state, never folded into "error"; every metric carries a *what this means for you*
threshold (e.g. obstruction ">0.2%" hurts performance).

| Move | Principle | Web version |
|---|---|---|
| Address + price + one button in the hero | **Qualify first** | A real `<form>` posting a ZIP/service-area or "book a time" to a server function; visible `<label>`, `autocomplete`, 16 px input; works without JS. |
| Expanded primary card, collapsed alternative | **One decision per screen** | `grid-template-columns: 2fr 1fr`; the alternative visible but quiet. |
| CTA-only floating bar after the hero | **Persistent single action** | `position: sticky` + an IntersectionObserver class toggle animating `transform`/`opacity` only. |
| Pinned photo, scrolling copy | **Product as hero** | `position: sticky; height: 100svh` on the media column; scroll-driven opacity only as `@supports` enhancement. |

**Do not copy:** marketing content rendered only on the client (the server HTML body was empty; LCP was the H1
text at ~7 s in a sandboxed lab run — INF, lab not field data); **four `<h1>`s** with `<h4>`s beneath (heading
level chosen by size, not outline); translucent white buttons over photos (contrast depends on the photo); pure
`#000` where UI depth must show.

## 5. SpaceX Dragon: web tech in a cockpit

OBS ([InfoQ, 2020-06-30](https://www.infoq.com/news/2020/06/javascript-spacex-dragon/), quoting the SpaceX
software team's 2020 AMA): "Chromium in this context is used as a UI rendering engine only" — flight-software
interaction and fault tolerance live outside the displays; the UI uses web components and a custom reactive
framework; **"astronauts can still use hardware buttons to initiate critical actions."** The public docking
simulator's buttons measure 96×160 / 85×85 CSS px — 3.5–6.7× the WCAG 2.5.8 floor.

INF for a small-business site: the page presents, a server function decides (price, availability, booking);
**every critical action has a second path** (a phone link beside the booking form; a form that works without
JS); consequential actions get large targets and a confirm or undo. Treat the 2020 claim as evidence a
disciplined web stack *can* be reliable — not that web tech is reliable by default.

## 6. Tesla (secondary sources only — tesla.com returned 403 to automated fetches)

| Move | Status |
|---|---|
| Full-screen product hero, very few nav items, two CTAs (**Order Now** → configurator, plus a test-drive booking) | [The Driven, 2023](https://thedriven.io/2023/05/15/tesla-revamps-website-and-highlights-road-trips-to-help-model-3-buyers/) — regional and dated |
| Design Studio: one attribute group at a time (drivetrain → paint → wheels → interior → driver assist), immediate visual feedback, a running total | Order from a 2022-era guide (low quality); the live render + running total is `[unverified]` |
| v11 in-car UI (Dec 2021) moved frequent controls (wipers, seat heat, defrost) behind menus — criticised as "a glaring safety concern"; some controls restored in 2022 | [Not a Tesla App](https://www.notateslaapp.com/news/663/first-look-at-teslas-new-v11-ui), [The Drive](https://www.thedrive.com/tech/43710/teslas-v11-update-blasted-for-hiding-things-like-defroster-button-in-pointless-menus) |
| The app removed its charging section; charging details appear **only while plugged in** | [TechCrunch, 2021-08-26](https://techcrunch.com/2021/08/26/teslas-redesigned-iphone-app-features-two-new-home-screen-widgets) |
| The configurator's default headline price **nets out estimated "savings"** (Canada, Aug 2026: $34,390* vs $39,490) | [Drive Tesla Canada, 2026-08-11](https://driveteslacanada.ca/news/tesla-design-studio-canada-prices/) |

**Web version of the configurator principle:** a `<form>` of radio groups (`fieldset`/`legend`), the price summary
in an `aria-live="polite"` region, a ≤200 ms cross-fade or same-document View Transition on the preview.
**Context-sensitive UI:** show "Open now · closes 6 pm" only during open hours, computed at build/edge/client time,
never a hard-coded string. **Glanceability → the one-thumb visitor:** call, book or get directions in one tap from
any scroll position.

**Do not copy:** frequent controls behind menus; a headline price that subtracts speculative savings (show the
price paid first, savings second); autoplay hero video on mobile data; full-page scroll-jacking or mandatory
snap (`[unverified]` as a Tesla claim; NN/g found scrolljacking disoriented most participants).

---

## 7. Browser support for the techniques above (MDN BCD / webstatus.dev, 2026-10-26)

| Feature | Status | Use it as |
|---|---|---|
| `backdrop-filter` | Chrome 76, Firefox 103, Safari 18 (`-webkit-` before) | Enhancement behind `@supports`, opaque fallback first |
| `prefers-reduced-transparency` | Chrome 118; Firefox flag; **Safari no** | Always OR with `prefers-contrast: more` |
| `oklch()`, `color-mix()` | Widely available | Token authoring |
| `light-dark()` | Newly available | Mode-resolved tokens (with `color-scheme`) |
| Container queries (size) | Widely available | Every block/component |
| `linear()` easing | Widely available | CSS springs |
| `@starting-style` | Newly available | Dialog/popover enter animations without JS |
| Same-document View Transitions | Newly available (2025-10-14) | Configurator swaps, search → results |
| Cross-document View Transitions | **Not Baseline** (no Firefox) | Enhancement only |
| Scroll-driven animations | **Not Baseline** (no Firefox) | Enhancement only, inside `@supports`; content complete without |
| `text-wrap: balance` / `pretty` | balance newly available; pretty **not in Firefox** | Progressive enhancement |

## Sources

All retrieved 2026-10-26. Apple: HIG Materials / Typography / Motion / Color / Accessibility; WWDC25 219 and 356;
WWDC23 10158; developer.apple.com/fonts; Apple Newsroom (2025-06, 2026-06); apple.com production CSS/HTML
(`globalheader.css`, homepage `main.built.css`, iPhone product page). NN/g Liquid Glass (2025-10-10); TidBITS
(2025-10-21); CSS-Tricks (2020-05-22); WebKit scroll-driven guide (2025-06-20). Stripe: accessible-color-systems
(2019-10-15); connect-front-end-experience (2017-06-19); Appearance API docs; Stripe Apps design; one-step
checkout (2025-07-10); stripe.com production CSS/JS. Cloudflare: Kumo (GitHub, kumo-ui.com colors and skill);
dark-mode blog (2021-09-29); Radar redesign (2026-10-08); cloudflare.com production HTML/CSS. Starlink: starlink.com
rendered in headless Chromium (desktop 1440×900, mobile 390×844); support articles on obstructions and dashboard
statistics. SpaceX: InfoQ (2020-06-30); iss-sim.spacex.com rendered. Tesla: The Driven (2023-05-15); Not a Tesla
App (2021-12-22); The Drive (2022-01-04); TechCrunch (2021-08-26); Electrek (2019-06-03); Drive Tesla Canada
(2026-08-11). Platform: MDN BCD API; webstatus.dev API.
