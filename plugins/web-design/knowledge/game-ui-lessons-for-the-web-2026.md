# Game menu & HUD craft, translated for the web (2026)

> **Retrieved:** 2026-10-26. **OBS** = a source says it (or a tool returned it this session); **INF** = a design
> recommendation drawn from those observations; `[unverified]` = not confirmed this session. Short quotes are
> verbatim from the cited page. The GDC Vault was down for maintenance and gameuidatabase.com returned 403 to the
> fetcher, so Vault-only talks are cited through credible secondary write-ups.
>
> The game-side version of this material (CommonUI/UI Toolkit patterns, XAG numbers, menu architecture for a
> shipped game) lives in the `game-development` plugin's `knowledge/game-menu-and-hud-ux-2026.md`. This file is
> the **web translation**: what a website or web app should take from recent game menus, how to build it with
> 2026 platform features, and what must not be copied.

## The ten findings that transfer

1. **Focus is the cursor.** At ten feet, "assume that the user is not paying full attention to the entire TV
   screen" (Microsoft). XAG 113 asks for several cues at once — outline, fill and weight. → A **two-tone
   `:focus-visible` ring** plus a fill/weight change, visible on every background it can sit over.
2. **Every HUD element earns its place.** "All HUD serves a purpose… if you remove that HUD… then we have to solve
   that with an alternative and our answer to that was the wind" (Jason Connell, *Ghost of Tsushima*). → Removing
   chrome means owing the user an **in-context signal**.
3. **Back always works, and focus is remembered** (Unreal CommonUI activatable widgets; XAG 112). → Closing a layer
   returns focus to what opened it; Esc / browser Back pops exactly one layer.
4. **Presets on top, granular sliders underneath.** *The Last of Us Part II* ships 60+ settings, three presets, and
   camera shake as a **1–10 slider**. → `prefers-reduced-motion` *plus* an in-app intensity setting.
5. **Settings before spectacle.** XAG 104 puts subtitles before any cinematic. → No auto-playing hero motion until
   preferences are resolved.
6. **Juice is "maximum output for minimum input"** (Martin Jonasson). On the web it is opt-in, capped and never on
   reading surfaces. UI sound follows WinUI's rules: subtle, varied, never on hover.
7. **Brand-as-UI is expensive.** Atlus builds "a whole separate program running" per menu ("It takes a lot of
   time"), and Kotaku reports *Persona 5*'s menus were "really hard to read" until heavily reworked. → Spend bespoke
   motion on **one to three hero surfaces**, not every screen.
8. **Destructive actions need friction with a click path.** *Spider-Man 2*'s hold is "a hold-to-confirm prompt, not
   hiding a load", but XAG 115 says "Don't require button holds for confirmation of destructive actions." → Confirm
   or undo, never hold-only.
9. **Context on demand.** *Final Fantasy XVI*'s Active Time Lore (hold to see who/what is on screen, ignorable);
   *Diablo IV*'s gain/loss compare against the equipped item. → Inline "what's this?" panels and **before → after
   deltas at the decision point** — on by default (Diablo shipped it off, which was the mistake).
10. **The 2026 platform does most of this natively** — same-document View Transitions (Baseline 2025-10-14),
    `@starting-style` (2024), `<dialog>` + `inert`, Gamepad, Web Audio, `:focus-visible`. Cross-document view
    transitions and scroll-driven animations are **not** Baseline (no Firefox) — enhancement only.

## 1. Theory: the diegesis grid (Fagerholt & Lorentzon, 2009)

| | In the game's fiction | Not in the fiction |
|---|---|---|
| **In 3D space** | **Diegetic** — seen and heard by the characters (*Dead Space*'s spine health bar) | **Spatial** — placed in the world but not part of it (outlines, ground markers) |
| **Not in 3D space** | **Meta** — fiction-adjacent effects (blood on the lens) | **Non-diegetic** — the classic HUD |

Source: Chalmers master's thesis with EA DICE (2009), popularised by
[Marcus Andrews, Game Developer, 2010](https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want).
Andrews's own caveat: even *Dead Space*'s diegetic map needed a projected locator — **functionality first, whatever
the style.**

**Web mapping (INF):** diegetic = in-content status (inline validation, progress on the invoking button);
non-diegetic = app chrome; spatial = anchored popovers and tooltips; meta = ambient feedback (toasts, edge glows).
Choose by how fast the user can read it, not by immersion.

## 2. What the exemplars actually do

| Game | Technique | Source |
|---|---|---|
| *Persona 5* / *Metaphor: ReFantazio* | A red/black/white palette with no gradients; ransom-note typography; a bespoke program per menu; the UI as "an inherent part of the story". Legibility needed "a lot of iteration and refinement". | [Kotaku 2024-10-07](https://kotaku.com/-metaphor-refantazio-persona-5-menu-ui-hashino-1851667088); [NYT via DT Next 2024-10-18](https://www.dtnext.in/amp/story/edit/exuberant-video-game-menus-designed-with-da-vinci-in-mind-807823) |
| *Destiny 2* | The Director travels anywhere in one step (Destiny 1 routed through orbit); tough enemies' health bars split into thirds so one glance answers "am I strong enough?" | [Kulik, Game Developer 2017](https://www.gamedeveloper.com/design/ux-enhancements-from-destiny-1-to-destiny-2) |
| *Baldur's Gate 3* (console) | PC UI rebuilt as radial menus; **adaptive triggers — a light pull peeks, a hard press past resistance commits**; an optional cursor mode. "You have 12 buttons to work with. Good luck." | [PlayStation Blog 2023-09-05](https://blog.playstation.com/2023/09/05/how-baldurs-gate-3-adapts-its-expansive-rpg-gameplay-for-your-dualsense-controller/) |
| *The Last of Us Part II* | 60+ settings; Vision/Hearing/Motor presets that stay adjustable; high-contrast mode; screen magnifier; traversal audio cues with a glossary; shake 1–10; subtitle size, background, speaker names and direction. | [PlayStation Blog 2020-06-09](https://blog.playstation.com/2020/06/09/the-last-of-us-part-ii-accessibility-features-detailed) |
| *Forza Horizon 4/5* | Warning dialogs blur the background, move and trap focus; focus order follows the visual tile layout; sign-language interpreters picture-in-picture for 150 cinematics. | XAG 112/113/115; GameSpot 2022 |
| *Ghost of Tsushima* | No compass, no minimap — the wind, birds and foxes guide. | [TechRadar 2020-05-27](https://www.techradar.com/news/ghost-of-tsushima-interview-nature-sprawls-in-ps4s-epic-samurai-swan-song) |
| *Apex Legends* | One contextual ping produces a typed, spoken message; playtested a month with voice chat off. | @PlayApex 2019-02-06 (via wnhub) |
| *Hades* | God Mode: 20% damage resistance, +2% per death, capped at 80% — "take the sting of failure and reduce that as much as possible". | [Inverse 2021-08-11](https://www.inverse.com/gaming/hades-god-mode-interview) |
| *Diablo IV* | Advanced Tooltip Compare (every stat vs the equipped item) — off by default, called the game's "best hidden setting". | [Den of Geek 2023-06-06](https://www.denofgeek.com/games/diablo-4-best-hidden-setting-compare-gear) |
| *Elden Ring* | Minimal HUD; icons criticised as unreadable without opening descriptions. | [Kotaku 2022-03-10](https://kotaku.com/elden-ring-ui-ux-user-experience-interface-fromsoftware-1848637410) |

Not covered: *Astro Bot*, *Balatro*, *Tears of the Kingdom*, *FF VII Rebirth*, *Hades II* — no developer-sourced UI
material found this session. For visual precedent, the **Game UI Database 2.0** (Edd Coates, Aug 2024) has 55,000+
screenshots from 1,341 games, filterable by screen type, controls and HUD element
([Creative Bloq](https://www.creativebloq.com/3d/video-game-design/game-ui-database-20-is-the-ultimate-free-reference-tool-for-game-designers)).

## 3. Craft techniques → web implementation

| Technique (game evidence) | Web implementation | Status |
|---|---|---|
| **Unmistakable focus** — Microsoft's 10-foot guidance; XAG 113 redundant cues; focus never moves to an off-screen element | `:focus-visible` two-tone ring (outline + contrasting halo) and a fill/weight change; meet WCAG 2.4.7, 2.4.11 *Focus Not Obscured* (AA), aim for 2.4.13 *Focus Appearance* (AAA). Sticky headers must not cover the focused element (`scroll-padding-top`). | `:focus-visible` widely available |
| **D-pad grids** — XAG 112: digital input alone suffices; focus order follows visual flow; **wrap linear menus, not 2-D grids** | Roving tabindex (APG): one `tabindex="0"` per composite, arrows inside, Tab between. `focusgroup` has no shipping support — use JS. | APG pattern |
| **Back stack + focus restoration** — CommonUI caches a restoration target; universal Back | `<dialog>.showModal()` + `inert` on the rest; return focus to the invoker (otherwise browsers move it to `<body>`); store the last-focused id per route in `history.state`; one Back semantic (Esc, browser Back, pad B); breadcrumbs beyond depth 2. | `<dialog>`, `inert` widely available |
| **Spatial continuity** — authored menu transitions; Destiny's one-hop Director | `document.startViewTransition()` with `view-transition-name` from the clicked card to the detail hero; skip under reduced motion; never block input on it. | Same-document newly available; cross-document not Baseline |
| **Enter/exit for popovers and dialogs** | `@starting-style` + `transition-behavior: allow-discrete` on `display`/`overlay`. | Newly available |
| **Input-prompt switching** — CommonUI swaps glyphs by last input; XAG 101 glyphs scale with text | Track the last modality (`keydown` → keyboard; `pointerdown.pointerType`; gamepad poll) into `<html data-input>`; CSS shows the matching hints; hide `Esc`/`Enter` hints for touch. | Composition of Baseline APIs |
| **Navigation sound** — WinUI: no focus sound on hover, four rotating variants, focus the most subtle | Web Audio, short pre-decoded buffers, `AudioContext` created/resumed inside the opt-in click (it starts suspended until a gesture); **muted by default**; one sound per semantic event; never on hover. | Web Audio widely available |
| **Settings with live preview** — AC Valhalla before/after images; Halo Infinite 0–100% sliders; Grounded's "Unapplied Changes" warning and factory reset | Apply on `input`, preview inline, offer per-section reset, warn on leaving unsaved changes — or have no unapplied state at all. Persist to the account, not only `localStorage`. | — |
| **Comparison deltas** — Diablo IV compare; Destiny's one-question health bar | `<output>` / `aria-live="polite"` showing "old → new (± x)" next to the control; on by default. | — |
| **Onboarding without text walls** — Game Accessibility Guidelines: interactive tutorials; "no essential information… conveyed by text alone"; recallable controls | Just-in-time hints a "?" can recall, not a modal tour. | — |
| **Gamepad** for kiosks, TV and in-store screens | Gamepad API in a `requestAnimationFrame` loop, `"standard"` mapping; D-pad and A/B call the **same** roving-focus and Back handlers as the keyboard. | Widely available |
| **Loading** — the loading-minigame patent expired 2015; *Spider-Man 2*'s ~1.3 s fast travel needs no mask | Skeletons and optimistic UI; never a fake wait as cover. | — |

```css
:root { --focus: #ffd400; --focus-halo: #000; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; box-shadow: 0 0 0 6px var(--focus-halo); }
.tile:focus-visible { background: color-mix(in oklab, var(--focus) 18%, transparent); font-weight: 700; }
dialog { opacity: 0; translate: 0 8px;
  transition: opacity .2s, translate .2s, display .2s allow-discrete, overlay .2s allow-discrete; }
dialog[open] { opacity: 1; translate: 0 0; }
@starting-style { dialog[open] { opacity: 0; translate: 0 8px; } }
@media (prefers-reduced-motion: reduce) { dialog { transition: opacity .15s, display .15s allow-discrete, overlay .15s allow-discrete; translate: none; } }
```

```js
// View transition as enhancement; never blocks input.
function go(update) {
  if (!document.startViewTransition || matchMedia('(prefers-reduced-motion: reduce)').matches) return update();
  document.startViewTransition(update);
}
```

## 4. Accessibility numbers worth borrowing (OBS, Microsoft Learn)

- **XAG 101 text:** console ≥ 26 px at 1080p; PC ≥ 18 px at 1080p; scale to **200% without loss of content** and
  without two-direction scrolling; at least one sans-serif option; glyph interiors meet text minimums.
- **Accessible Games Initiative tags v2.0.1:** text contrast **4.5:1 against all backgrounds**, or an opaque backing
  that achieves it.
- **XAG 104 subtitles:** on and configurable *before* any intro cinematic; speaker identified, never by colour alone;
  at most two lines.
- **XAG 117:** moving, blinking and auto-updating content can be paused, hidden or disabled; shake/bob/blur avoidable
  or switchable.
- **XAG 115:** review/confirm/undo for purchases, sales and overwrites; no hold-only confirmation.
- **Game Accessibility Guidelines:** no essential information by colour alone; settings saved and remembered (and to
  profiles); start without navigating multiple menu levels; an option to turn off background movement.

**For websites (INF):** one "Reduce motion / High contrast / Larger text" preset that seeds individual settings;
intensity rather than on/off (0 none, 1 subtle, 2 full); read `prefers-reduced-motion`, `prefers-contrast` and
`forced-colors` first; captions and a sign-language layout option for video; settings saved to the account.

## 5. Do not copy on the web

| Game pattern | Why it hurts on the web | Rule / source |
|---|---|---|
| Unskippable logos and intros | Users arrive with a task; motion before preferences harms vestibular users | WCAG 2.2.2 (A) |
| Type as illustration (rotated, ransom-note text) | Images of text can't be translated, zoomed, reflowed or read aloud; even Atlus fought legibility | WCAG 1.4.5 — keep it to decorative display text |
| Hover-only reveals | Touch has no hover; keyboard users are trapped | WCAG 1.4.13 (AA) |
| Stylised low-contrast type over moving art | Fails over video and gradients | AGI 4.5:1 against all backgrounds or an opaque backing |
| Motion that blocks input | Every interaction pays the wait; fast users mis-click | Transitions must be interruptible |
| Scroll-jacking / cinematic scroll | "The majority of our study participants were at least mildly disoriented" | [NN/g Scrolljacking 101](https://www.nngroup.com/articles/scrolljacking-101/) |
| Diegetic-only status | Invisible to assistive tech and to anyone who doesn't know the convention | Expose state in text/ARIA too |
| Strict HUD-less minimalism | Discoverability beats immersion when the user has a task | Elden Ring icon critique |
| Hold-to-confirm as the only path | Excludes motor-impaired users | XAG 115 |
| A bespoke program per screen | Maintenance and consistency cost grows with every screen | Hashino: "It takes a lot of time." |
| Juice everywhere | Noise on reading surfaces; a vestibular trigger | WCAG 2.3.3 — opt-in or capped |

## 6. Checklist

- [ ] Two-tone `:focus-visible` at ≥ 3:1 on every background it can sit over; never hidden under sticky chrome.
- [ ] A deliberate initial focus per view; closing a layer restores focus to its invoker; Back restores the last item.
- [ ] Roving tabindex in grids; wrap only 1-D lists; a list alternative for every map or canvas.
- [ ] One Back semantic; breadcrumbs when the stack is deeper than two.
- [ ] Hint glyphs follow the last input modality.
- [ ] Motion honours the OS setting *and* an in-app setting, never blocks input, is enhancement only.
- [ ] Sound off by default, started by an opt-in gesture, one sound per event, never on hover.
- [ ] Live-preview settings with undo and per-section reset, saved to the account; accessibility presets first.
- [ ] Deltas at decision points; destructive actions confirm or undo with a click path.
- [ ] No text-in-images, hover-only content, scroll-jacking or unskippable intros.

## Sources

Retrieved 2026-10-26: Fagerholt & Lorentzon (Chalmers, 2009); Andrews (Game Developer, 2010); TechRadar (2020);
Kotaku (2016, 2022, 2024); NYT via DT Next (2024); Kulik (Game Developer, 2017); PlayStation Blog (2020, 2023);
GameSpot / Windows Central (FH5, 2022); Inverse (2021); Den of Geek (2023); wnhub (Apex, 2019); Creative Bloq (2024);
Game Developer (Juice It or Lose It, 2012/2013); Microsoft Learn — XAG 101, 104, 112, 113, 115, 117, Accessibility
Feature Tags v2.0.1, 10-foot gamepad guidance, Reveal Focus, WinUI Sound; Game Accessibility Guidelines; Unreal CommonUI
docs and `UCommonActivatableWidget` API; W3C APG keyboard interface; WCAG 2.2 Understanding 1.4.13, 2.2.2, 2.3.3,
2.4.11, 2.4.13; MDN View Transitions, `@starting-style`, Gamepad API; Chrome autoplay policy; NN/g Scrolljacking 101
(2023); `web-features` v3.44.0 Baseline data.
