# Game menu & HUD UX (2018–2026): what the best recent games do, and the numbers to build to

> **Retrieved:** 2026-10-26. **OBS** = a source says it; **INF** = a design recommendation drawn from the
> observations; `[unverified]` = not confirmed this session. The GDC Vault was down for maintenance and
> gameuidatabase.com returned 403 to the fetcher, so Vault-only talks are cited through credible secondary
> write-ups and marked that way. Short quotes are verbatim from the cited page.
>
> This is the **game-side** reference: menu architecture, HUD decisions and accessibility for a game you ship. The
> web-design plugin carries the translation for websites (`web-design/knowledge/game-ui-lessons-for-the-web-2026.md`).

## 1. Decide what each piece of UI *is* — the diegesis grid

| | In the fiction | Not in the fiction |
|---|---|---|
| **In 3D space** | **Diegetic** — characters can see and hear it (*Dead Space*'s spine health bar) | **Spatial** — placed in the world, not part of it (outlines, ground locators) |
| **Not in 3D space** | **Meta** — fiction-adjacent effects (blood on the lens, screen-edge damage) | **Non-diegetic** — the classic HUD |

From Fagerholt & Lorentzon, *Beyond the HUD* (Chalmers / EA DICE, 2009), popularised by
[Marcus Andrews, Game Developer, 2010](https://www.gamedeveloper.com/design/game-ui-discoveries-what-players-want).
Andrews: *Dead Space*'s diegetic holographic map did not help navigation, so the team added a projected ground locator;
WoW players tolerated dense, customisable HUDs when they helped performance. **Functionality first, whatever the
style.** Dead Space's lead UI designer Dino Ignacio framed the diegetic goal as to "remove a wall of safety between the
player and the game" (GDC 2013, via [Game Developer](https://gamedeveloper.com/design/video-designing-i-dead-space-i-s-immersive-user-interface)).

## 2. HUD: every element earns its place

- *Ghost of Tsushima* (OBS): "All HUD serves a purpose… if you remove that HUD… suddenly the design problem is harder…
  'no compass, no mini map,' well, then we have to solve that with an alternative and our answer to that was the wind"
  — Jason Connell ([TechRadar 2020-05-27](https://www.techradar.com/news/ghost-of-tsushima-interview-nature-sprawls-in-ps4s-epic-samurai-swan-song)).
  Birds and foxes lead to points of interest; a GDC 2021 talk covered the wind tech.
- *Destiny 2* (OBS): tough enemies' health bars split into thirds; enemy level removed so the bar answers one question,
  "Am I strong enough to attack this enemy?" ([Kulik, Game Developer 2017](https://www.gamedeveloper.com/design/ux-enhancements-from-destiny-1-to-destiny-2)).
- *Elden Ring* (OBS): the minimal HUD split developers; critics found its icons unreadable without opening descriptions
  ([Kotaku 2022-03-10](https://kotaku.com/elden-ring-ui-ux-user-experience-interface-fromsoftware-1848637410)).
- *Apex Legends* (OBS): the contextual ping produces a typed, spoken message without voice chat; Respawn "playtested for a
  month with voice comms off and fake names". EA reportedly framed it as an accessibility feature — that page now 404s
  (`[verified only via search index]`).

**INF:** remove HUD only where the world can carry the signal; a symbol that has to be looked up is a discoverability tax.
One context-sensitive action that produces a rich, typed message beats a menu of message types.

## 3. Menus: architecture that holds up

| Pattern | Evidence (OBS) | Build it |
|---|---|---|
| **Focus is the cursor** | Microsoft's 10-foot guidance: "assume that the user is not paying full attention to the entire TV screen"; initial focus top-left; never a popup with no focusable element; a "smoke" overlay dims everything outside a popup. XAG 113: combine outline, fill and weight; focus never moves to an off-screen or invisible element. | Redundant focus cues; a deliberate initial focus per screen; dim + trap behind modals |
| **Universal Back + focus restoration** | Unreal **CommonUI**: activatable widgets cache a restoration target when `bAutoRestoreFocus` is on; `GetDesiredFocusTarget` returns the widget to focus on activation; `RequestRefreshFocus` exists for buttons that "animate in from off-screen"; "the designated Back button is universally used for navigating backward". | One Back semantic across every layer; returning to a list lands on the last item visited |
| **Digital-only navigation** | XAG 112: navigation must work with digital input alone; focus order follows the visual layout (*Forza Horizon 4*); **wrap linear menus, not 2-D grids**; more than one way to find content (Minecraft's search tab); a text list alternative to a zoomable map (*Halo Infinite*); prompts in the same place on every screen (*Sea of Thieves*). | Spatial navigation tables; no wrap in grids; list views for maps |
| **Input-prompt switching** | CommonUI Controller Data maps actions to glyphs "based on the current platform and input type" and swaps them at runtime; XAG 101: glyph interiors meet minimum text size and scale with text to 200%. | Glyphs follow the last device used |
| **One-hop travel** | *Destiny 2*'s Director travels anywhere in one step where Destiny 1 routed through orbit. | Collapse multi-hop navigation for frequent destinations |
| **Controller-first rebuilds** | *Baldur's Gate 3* console rebuilt the PC UI as radial menus; **adaptive triggers — a light pull peeks, a hard press past resistance commits**; cursor mode as an option. Sara Hirst (Larian): "You have 12 buttons to work with. Good luck." ([PlayStation Blog 2023-09-05](https://blog.playstation.com/2023/09/05/how-baldurs-gate-3-adapts-its-expansive-rpg-gameplay-for-your-dualsense-controller/)) | Peek vs commit as two pressures, not two buttons |
| **Context on demand** | *Final Fantasy XVI* Active Time Lore — hold the touchpad (even in a paused cutscene) for entries on the characters, places and terms in the current scene; ignorable. | Recallable lore/help keyed to what is on screen |
| **Comparison deltas** | *Diablo IV* Advanced Tooltip Compare (every stat vs the equipped item) — **off by default**, called the game's "best hidden setting" ([Den of Geek 2023-06-06](https://www.denofgeek.com/games/diablo-4-best-hidden-setting-compare-gear)). | Ship the delta on by default |
| **Destructive actions** | *Spider-Man 2*'s fast-travel hold is "a hold-to-confirm prompt, not hiding a load" (mp1st 2023-10-17); XAG 115: "Don't require button holds for confirmation of destructive actions"; review/confirm/undo for purchases, sales and overwrites. | Confirm or undo with a press path; holds optional |
| **Settings with live preview** | *AC Valhalla* before/after camera images; *Halo Infinite* 0–100% sliders for blur, shake, full-screen effects; *Grounded* warns about "Unapplied Changes" and offers Factory Default; *Cyberpunk 2077* warns before leaving character creation with unspent points (XAG 115/117). | Preview inline, apply with undo, per-section reset, warn on unsaved |

## 4. Brand-as-UI: worth it on a few screens, expensive on all

*Persona 5* and *Metaphor: ReFantazio* (OBS): red/black/white with no gradients; ransom-note typography; Katsura Hashino:
"we have unique designs that we make for each and every menu… This is actually really annoying to do", each with "a whole
separate program running", "It takes a lot of time"; Kotaku relays that P5's angular text boxes were "really hard to read"
until "a lot of iteration and refinement"
([Kotaku 2024-10-07](https://kotaku.com/-metaphor-refantazio-persona-5-menu-ui-hashino-1851667088)). Lead UI designer Koji Ise
designed with Leonardo da Vinci in mind and colleagues stop him when he goes "a bit too far"
([NYT via DT Next 2024-10-18](https://www.dtnext.in/amp/story/edit/exuberant-video-game-menus-designed-with-da-vinci-in-mind-807823)).
Sakurai called P5's GUI one that takes "an active role in the game's presentation" but also "unconventionally cluttered",
and noted English localisation had to fit longer text into the same space.

**INF:** budget bespoke menu programs like content — a cost per screen — and spend them on the screens players see most
or remember (title, pause, results); keep the long tail on a shared system. Plan localisation length (+30–40% for some
languages is a common rule of thumb `[unverified]`) before committing to fixed-shape text boxes.

## 5. Juice and sound — feedback in proportion to the action

- "Maximum output for minimum input" — Martin Jonasson, *Juice It or Lose It* with Petri Purho (GDC Europe 2012), which
  made a Breakout clone juicy live ([Game Developer](https://www.gamedeveloper.com/design/video-is-your-game-juicy-enough-)).
  Jan Willem Nijman's *The Art of Screenshake* (~40 min; venue reported as INDIGO 2013 `[unverified]` — watch it before
  quoting its technique list). A 2014 counter-talk argued juice can cost immersion (search snippet only).
- **UI sound (WinUI `ElementSoundPlayer`):** the Focus sound "does not play on PointerEntered or mouse hover events"; it
  cycles through four variants so it never sounds monotonous; focus sounds "will be played most often and therefore should
  be the most subtle"; separate Invoke, Show/Hide, MoveNext/MovePrevious and GoBack sounds.

**INF:** one sound per semantic event, the most frequent one the quietest and varied; never on hover; every shake, flash
and blur behind an intensity setting (see §6).

## 6. Accessibility numbers to build to (OBS, Microsoft Learn and the Game Accessibility Guidelines)

| Area | Requirement |
|---|---|
| **Text (XAG 101)** | Console ≥ **26 px at 1080p** (52 at 4K); PC/VR ≥ **18 px at 1080p** (36 at 4K); scale to **200%** without loss of content and without two-direction scrolling; at least one sans-serif option; icon/glyph interiors meet the same minimums |
| **Accessible Games Initiative tags v2.0.1** | Default text height 26 px at 1080p; text contrast **4.5:1 against all backgrounds** or an opaque backing that achieves it; "Large Text" tag needs **38 px at 1080p** |
| **Subtitles (XAG 104)** | On and configurable **before** any intro cinematic; speaker identified and never by colour alone; at most **two lines** (three in exceptional cases) |
| **Motion (XAG 117)** | Moving, blinking and auto-updating UI can be paused, hidden or disabled; shake, bob and blur avoidable or switchable (Halo Infinite 0–100% sliders; Cyberpunk "additive camera motions") |
| **Destructive actions (XAG 115)** | Review/confirm/undo; no hold-only confirmation |
| **Game Accessibility Guidelines** | No essential information by fixed colour alone; settings saved and remembered (and to profiles); start without navigating multiple menu levels; an option to turn off background movement; interactive tutorials; no essential instructions by text alone; controls recallable during play |

**Reference implementations:**
- *The Last of Us Part II*: 60+ settings; Vision / Hearing / Motor **presets that stay adjustable**; high-contrast mode;
  HUD scale; screen magnifier; traversal and combat audio cues with a glossary; skip-puzzle option; camera shake as a
  **1–10 slider**; subtitle size, background, speaker names and an off-screen speaker-direction arrow
  ([PlayStation Blog 2020-06-09](https://blog.playstation.com/2020/06/09/the-last-of-us-part-ii-accessibility-features-detailed)).
- *Forza Horizon 5*: picture-in-picture **ASL/BSL interpreters** for 150 cinematics (2022-03-01), player-chosen position and
  background colour.
- *Marvel's Spider-Man 2*: game speed 70/50/30%; challenge modifiers; high/low/notch audio filters; motion blur, grain,
  chromatic aberration and depth of field each switchable.
- *Hades*: God Mode — 20% damage resistance, +2% per death, capped at 80%; Greg Kasavin: "take the sting of failure and
  reduce that as much as possible" ([Inverse 2021-08-11](https://www.inverse.com/gaming/hades-god-mode-interview)).
- Minecraft Dungeons opens on accessibility settings — **settings before spectacle**.

## 7. Loading

The Namco loading-minigame patent (US 5,718,632) expired 2015-11-27. *Spider-Man 2*'s fast travel reportedly lands in
~1.3 s and its hold is a confirm, not a mask. **INF:** fix load time before decorating it; a fake wait used as cover is a
defect.

## 8. Engine notes

- **Unreal CommonUI** — activatable widget stacks, input-routing, Back handling, focus restoration and platform glyphs are
  built in; prefer it to hand-rolled UMG focus code for controller-first games
  ([overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/common-ui-plugin-for-advanced-user-interfaces-in-unreal-engine),
  [`UCommonActivatableWidget`](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/CommonUI/UCommonActivatableWidget)).
- **Unity UI Toolkit** — navigation events (`NavigationMoveEvent`, `NavigationSubmitEvent`, `NavigationCancelEvent`)
  route gamepad/keyboard navigation through the visual tree ([docs](https://docs.unity3d.com/Manual/UIE-Navigation-Events.html)).
- **Visual precedent:** Game UI Database 2.0 (Edd Coates, Aug 2024) — 55,000+ screenshots and 1,700 videos from 1,341
  games, filterable by screen type, controls, HUD element and colour
  ([Creative Bloq](https://www.creativebloq.com/3d/video-game-design/game-ui-database-20-is-the-ultimate-free-reference-tool-for-game-designers)).

## 9. Not covered

*Astro Bot*, *Balatro*, *Zelda: Tears of the Kingdom*, *FF VII Rebirth* and *Hades II* — no developer-sourced UI material
found this session; anything written about their menus would be `[unverified]` observation. The 2023 *Dead Space* remake's
UI changes and *Cyberpunk 2077* 2.0's (secondary press only) were not researched in depth.

## Sources

Retrieved 2026-10-26: Fagerholt & Lorentzon (Chalmers 2009); Andrews (Game Developer 2010); Game Developer on Dead Space
(2013); TechRadar (2020); GDC news (Ghost of Tsushima wind, 2021); Kulik (Game Developer 2017); Kotaku (2016, 2022, 2024);
NYT via DT Next (2024); Gameranx/Eurogamer (2025); SEGAbits/Famitsu (2016); Source Gaming (Sakurai, 2016); PlayStation Blog
(TLOU2 2020; BG3 2023); FRVR (Hirst, 2025); Can I Play That (FH5 2021; Spider-Man 2 2023); GameSpot / Windows Central (FH5);
Gematsu (2023); mp1st (2023); Prima Games and TrueTrophies (FFXVI); Inverse (Hades 2021); wnhub (Apex 2019); Den of Geek
(2023); Siliconera (Cyberpunk 2.0); Techdirt and Google Patents (US5718632A); Game Developer (Juice It or Lose It
2012/2013); Kenney's talk list; Creative Bloq (2024); Microsoft Learn — XAG 101/104/112/113/115/117, accessibility metadata,
Accessibility Feature Tags v2.0.1, gamepad and remote interactions, Reveal Focus, WinUI Sound; Game Accessibility
Guidelines; Unreal CommonUI overview, quickstart and API; Unity UI Toolkit navigation events.
