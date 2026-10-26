---
name: design-game-menus
description: "Design a game's menus and HUD so they read at a glance, navigate with a controller alone, and ship accessible. Decide what each HUD element is and whether it earns its place, build a universal Back with focus restoration, set accessibility presets over granular settings, and spend bespoke menu motion on a few screens. Reach for this before menu or HUD work starts."
---

# Skill: Design the menus and HUD

Menus are the part of a game every player touches, and the part most often built last. Decide their architecture
early — retrofitting focus, Back and accessibility into finished screens is where the cost hides.

Backing knowledge: [`../../knowledge/game-menu-and-hud-ux-2026.md`](../../knowledge/game-menu-and-hud-ux-2026.md).

## Step 1 — Inventory and classify every HUD element

For each element, name its type (diegetic, spatial, meta, non-diegetic) and the **one question it answers** (Destiny 2's
segmented bar answers "am I strong enough?"). An element that answers no question goes. An element you remove must be
replaced by a signal the world carries (Ghost of Tsushima's wind) — removing chrome creates a design obligation.
Symbols that have to be looked up (Elden Ring's icons) count as a discoverability cost.

## Step 2 — Build the menu architecture before any screen

1. **Universal Back** — one input pops exactly one layer, everywhere (CommonUI's designated Back).
2. **Focus restoration** — returning to a screen lands on the item the player last used; closing a layer returns focus to
   whatever opened it.
3. **A deliberate initial focus** on every screen; never a popup with no focusable element; dim and trap behind modals.
4. **Digital-only navigation** works everywhere; focus order follows the visual layout; wrap linear menus, never 2-D grids;
   a list alternative for every map.
5. **Prompts** in the same place on every screen, with glyphs that follow the last input device and scale with text.
6. **Frequent destinations in one hop** (Destiny 2's Director).

In Unreal, use CommonUI's activatable widget stack rather than hand-rolled focus code; in Unity, route navigation through
UI Toolkit's navigation events.

## Step 3 — Settings and accessibility, first-class

- **Presets on top, granular controls underneath** (TLOU2's Vision / Hearing / Motor presets stay adjustable).
- **Intensity, not just on/off** — camera shake 1–10, 0–100% sliders for blur, flash and speed lines.
- **Settings before spectacle** — subtitles and accessibility reachable before any intro cinematic.
- **Live preview, apply with undo, per-section reset, warn on unsaved changes**; save settings and allow profiles.
- **Text:** ≥ 26 px at 1080p on console, ≥ 18 px on PC; scales to 200%; 4.5:1 against all backgrounds or an opaque
  backing; at most two subtitle lines with the speaker named (never by colour alone).
- **Destructive actions** confirm or undo with a press path — never hold-only (XAG 115).
- **Deltas at decision points**, on by default (Diablo IV shipped its compare off and players had to discover it).

## Step 4 — Budget the brand moments

Bespoke animated menus (Persona/Metaphor) cost "a whole separate program" per screen. List the screens players see most or
remember (title, pause, results, the main hub) and spend bespoke motion there; keep the long tail on the shared system.
Plan for localisation length before committing to fixed-shape text boxes — Atlus fought legibility for years.

## Step 5 — Feedback and sound

Feedback in proportion to the action ("maximum output for minimum input"), every shake and flash behind the Step 3
intensity setting. UI sound: one sound per semantic event (focus, invoke, show/hide, back), the most frequent the quietest
and varied across a few takes, never on hover.

## Step 6 — Verify with players, not screenshots

Playtest the menus controller-only and with each accessibility preset; time the top three tasks (start a match, change a
setting, equip an item); check every screen at 200% text scale; confirm focus never lands off-screen. Treat a fake loading
delay used as cover as a defect to fix, not a screen to decorate.

## Output

A menu architecture note (Back, focus, initial focus per screen, navigation tables), the HUD inventory with each element's
question, the settings/preset matrix with defaults, the list of bespoke "brand moment" screens with their cost, and the
verification results.
