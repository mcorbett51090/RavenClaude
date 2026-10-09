# Design system spec — Harness Spectate v1.0

> Token + layout + status visual spec for a gold-standard coding-agent harness spectate surface.
> Familiar to Cursor / Claude Code / Codex users. Spec only — no implementation.
> Consumed by `frontend-implementer` / `ux-designer` for build.

**System:** Harness Spectate  
**Version:** v1.0  
**Last updated:** 2026-10-09  
**Owner:** visual-designer (web-design)  
**Token build:** manual CSS custom properties (Style Dictionary–ready naming)  
**Aesthetic prior:** dark-leaning IDE (Linear + Cursor + Claude Code terminal) — monochrome canvas, one teal accent, no purple glow / AI shimmer / glassmorphism

---

## 1. Design intent

| Principle | Application |
|---|---|
| One composition | First viewport = session rail + live loop graph + detail inspector. Not a card dashboard. |
| Familiar IDE | Hairline borders, dense mono labels, restrained chrome — reads as a tool, not a marketing site. |
| Status without emoji | Every node state is **color + shape + text label**. Shape alone must survive grayscale. |
| One accent | Teal (`--color-accent`) for selection / live focus only. Never overloaded as success. |
| Customizable | Theme tokens, density, panel ratios, agent-column visibility — all semantic, no hard-coded hex in components. |
| Restraint | No bento, no glow halos, no auto-playing 3D, no pill clusters in the hero chrome. |

**Accent locked first:** teal cyan-green `#2DD4BF` — terminal-adjacent, distinct from Cursor purple and Claude warm amber clichés, WCAG AA on canvas for UI (≥10:1).

---

## 2. Design token CSS variables

### 2.1 Primitive color ramps

```css
:root {
  /* Neutrals — cool graphite (GitHub Primer–adjacent, not pure black) */
  --color-neutral-950: #010409;
  --color-neutral-900: #0d1117;
  --color-neutral-850: #12151a;
  --color-neutral-800: #161b22;
  --color-neutral-750: #1c2128;
  --color-neutral-700: #21262d;
  --color-neutral-600: #30363d;
  --color-neutral-500: #484f58;
  --color-neutral-400: #6e7681;
  --color-neutral-300: #8b949e;
  --color-neutral-200: #b1bac4;
  --color-neutral-100: #c9d1d9;
  --color-neutral-50:  #e6edf3;
  --color-neutral-0:   #ffffff;

  /* Brand / accent — teal (single accent) */
  --color-teal-700: #0f766e;
  --color-teal-600: #14b8a6;
  --color-teal-500: #2dd4bf;
  --color-teal-400: #5eead4;
  --color-teal-300: #99f6e4;

  /* Functional */
  --color-green-600: #238636;
  --color-green-500: #3fb950;
  --color-green-400: #7ee787;
  --color-red-600:   #da3633;
  --color-red-500:   #f85149;
  --color-red-400:   #ff7b72;
  --color-amber-600: #9e6a03;
  --color-amber-500: #d29922;
  --color-amber-400: #e3b341;
  --color-orange-600:#db6d28;
  --color-orange-500:#f0883e;
  --color-orange-400:#ffa657;
  --color-blue-600:  #1f6feb;
  --color-blue-500:  #58a6ff;
  --color-blue-400:  #79c0ff;
  --color-blue-300:  #a5d6ff;
}
```

### 2.2 Semantic surfaces (dark default)

```css
:root,
[data-theme="dark"] {
  --color-surface-page:     var(--color-neutral-900);   /* #0D1117 canvas */
  --color-surface-panel:    var(--color-neutral-950);   /* #010409 rails */
  --color-surface-elevated: var(--color-neutral-800);   /* #161B22 nodes, popovers */
  --color-surface-sunken:   var(--color-neutral-850);   /* graph well */
  --color-surface-hover:    var(--color-neutral-750);
  --color-surface-selected: color-mix(in srgb, var(--color-teal-500) 12%, var(--color-neutral-800));
  --color-surface-overlay:  color-mix(in srgb, var(--color-neutral-950) 72%, transparent);

  --color-border-default:   var(--color-neutral-600);
  --color-border-subtle:    var(--color-neutral-700);
  --color-border-strong:    var(--color-neutral-500);
  --color-border-focus:     var(--color-teal-500);

  --color-text-primary:     var(--color-neutral-50);    /* 16.02:1 on page */
  --color-text-secondary:   var(--color-neutral-300);   /* 6.15:1 on page */
  --color-text-tertiary:    var(--color-neutral-200);   /* 9.63:1 — captions OK as body */
  --color-text-disabled:    var(--color-neutral-400);   /* UI/large only — 4.12:1 UI PASS; not body */
  --color-text-inverse:     var(--color-neutral-900);
  --color-text-link:        var(--color-blue-400);
  --color-text-on-accent:   var(--color-neutral-900);   /* 10.17:1 on teal-500 */

  --color-accent:           var(--color-teal-500);
  --color-accent-hover:     var(--color-teal-400);
  --color-accent-muted:     color-mix(in srgb, var(--color-teal-500) 22%, transparent);

  --color-success:          var(--color-green-500);
  --color-success-muted:    color-mix(in srgb, var(--color-green-500) 18%, transparent);
  --color-warning:          var(--color-amber-400);
  --color-warning-muted:    color-mix(in srgb, var(--color-amber-400) 18%, transparent);
  --color-danger:           var(--color-red-500);
  --color-danger-muted:     color-mix(in srgb, var(--color-red-500) 18%, transparent);
  --color-info:             var(--color-blue-400);
  --color-info-muted:       color-mix(in srgb, var(--color-blue-400) 18%, transparent);

  /* Graph chrome */
  --color-graph-edge:       var(--color-neutral-600);
  --color-graph-edge-active: var(--color-teal-500);
  --color-graph-grid:       color-mix(in srgb, var(--color-neutral-600) 35%, transparent);
}
```

### 2.3 Status semantic tokens (color + shape + label)

Components consume these — never raw primitives.

```css
:root {
  /* available — capability exposed, not yet in flight */
  --status-available-fg:          var(--color-teal-600);
  --status-available-bg:          transparent;
  --status-available-border:      var(--color-teal-600);
  --status-available-shape:       "circle-outline";
  --status-available-label:       "available";

  /* unavailable-harness — harness does not expose this step/tool */
  --status-unavailable-harness-fg:     var(--color-neutral-300);
  --status-unavailable-harness-bg:     transparent;
  --status-unavailable-harness-border: var(--color-neutral-300);
  --status-unavailable-harness-shape:  "circle-dashed";
  --status-unavailable-harness-label:  "unavailable-harness";

  /* denied-org — organization policy blocked */
  --status-denied-org-fg:         var(--color-orange-600);
  --status-denied-org-bg:         color-mix(in srgb, var(--color-orange-600) 14%, transparent);
  --status-denied-org-border:     var(--color-orange-600);
  --status-denied-org-shape:      "octagon";
  --status-denied-org-label:      "denied-org";

  /* denied-plugin — plugin / marketplace hook blocked */
  --status-denied-plugin-fg:      var(--color-orange-500);
  --status-denied-plugin-bg:      color-mix(in srgb, var(--color-orange-500) 14%, transparent);
  --status-denied-plugin-border:  var(--color-orange-500);
  --status-denied-plugin-shape:   "diamond";
  --status-denied-plugin-label:   "denied-plugin";

  /* denied-user — user / local permission denied */
  --status-denied-user-fg:        var(--color-red-400);
  --status-denied-user-bg:        color-mix(in srgb, var(--color-red-400) 14%, transparent);
  --status-denied-user-border:    var(--color-red-400);
  --status-denied-user-shape:     "square-x";
  --status-denied-user-label:     "denied-user";

  /* running */
  --status-running-fg:            var(--color-blue-400);
  --status-running-bg:            color-mix(in srgb, var(--color-blue-400) 16%, transparent);
  --status-running-border:        var(--color-blue-400);
  --status-running-shape:         "circle-filled-pulse";
  --status-running-label:         "running";

  /* succeeded (maps from colloquial "done") */
  --status-succeeded-fg:          var(--color-green-500);
  --status-succeeded-bg:          color-mix(in srgb, var(--color-green-500) 14%, transparent);
  --status-succeeded-border:      var(--color-green-500);
  --status-succeeded-shape:       "circle-check";
  --status-succeeded-label:       "succeeded";

  /* failed */
  --status-failed-fg:             var(--color-red-500);
  --status-failed-bg:             color-mix(in srgb, var(--color-red-500) 16%, transparent);
  --status-failed-border:         var(--color-red-500);
  --status-failed-shape:          "circle-cross";
  --status-failed-label:          "failed";

  /* waiting-approval */
  --status-waiting-approval-fg:     var(--color-orange-400);
  --status-waiting-approval-bg:     color-mix(in srgb, var(--color-orange-400) 16%, transparent);
  --status-waiting-approval-border: var(--color-orange-400);
  --status-waiting-approval-shape:  "rounded-square-pause";
  --status-waiting-approval-label:  "waiting-approval";

  /* idle — session/step not active (operational; companion to the nine named labels) */
  --status-idle-fg:               var(--color-neutral-400); /* UI ≥3:1 */
  --status-idle-bg:               transparent;
  --status-idle-border:           var(--color-neutral-400);
  --status-idle-shape:            "circle-outline-muted";
  --status-idle-label:            "idle";
}
```

**Fill text rule:** status chips that use a solid fill use `--color-text-on-accent` (`#0D1117`) on teal / green / amber / orange / blue fills. On red fills use `#0D1117` on `--color-red-400` (7.51:1) — never white on `#F85149` (fails AA for normal text).

### 2.4 Light theme mirror (optional toggle)

```css
[data-theme="light"] {
  --color-surface-page:     #f6f8fa;
  --color-surface-panel:    #ffffff;
  --color-surface-elevated: #ffffff;
  --color-surface-sunken:   #eaeef2;
  --color-surface-hover:    #f3f4f6;
  --color-surface-selected: color-mix(in srgb, #0d9488 10%, #ffffff);

  --color-border-default:   #d0d7de;
  --color-border-subtle:    #eaeef2;
  --color-border-strong:    #8b949e;
  --color-border-focus:     #0d9488;

  --color-text-primary:     #1f2328;
  --color-text-secondary:   #656d76;
  --color-text-tertiary:    #57606a;
  --color-text-disabled:    #8b949e;
  --color-text-inverse:     #ffffff;
  --color-text-link:        #0969da;
  --color-text-on-accent:   #0d1117;

  --color-accent:           #0d9488;
  --color-accent-hover:     #0f766e;
  --color-graph-edge:       #d0d7de;
  --color-graph-edge-active:#0d9488;
  --color-graph-grid:       color-mix(in srgb, #d0d7de 55%, transparent);

  /* Status hues shift one step darker for AA on light canvas — implementer re-verifies */
  --status-running-fg:            #0969da;
  --status-succeeded-fg:          #1a7f37;
  --status-failed-fg:             #cf222e;
  --status-waiting-approval-fg:   #bc4c00;
  --status-denied-org-fg:         #bc4c00;
  --status-denied-plugin-fg:      #bf8700;
  --status-denied-user-fg:        #cf222e;
  --status-available-fg:          #0d9488;
  --status-unavailable-harness-fg:#656d76;
  --status-idle-fg:               #8b949e;
}
```

### 2.5 Typography tokens

```css
:root {
  --font-sans: "IBM Plex Sans", "IBM Plex Sans Fallback", "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", "IBM Plex Mono Fallback", "Cascadia Code", "Consolas", monospace;

  /* Scale — 8 steps; IDE-dense, not marketing-display */
  --font-size-display: 1.75rem;   /* 28px — rare; session title only */
  --font-size-h1:      1.375rem;  /* 22px — panel titles */
  --font-size-h2:      1.125rem;  /* 18px — section heads in inspector */
  --font-size-h3:      1rem;      /* 16px — node group labels */
  --font-size-body-lg: 0.9375rem; /* 15px — inspector body */
  --font-size-body:    0.8125rem; /* 13px — default UI */
  --font-size-body-sm: 0.75rem;   /* 12px — secondary meta */
  --font-size-caption: 0.6875rem; /* 11px — status labels, timestamps */

  --line-height-tight:  1.25;
  --line-height-snug:   1.35;
  --line-height-normal: 1.5;

  --font-weight-regular: 400;
  --font-weight-medium:  500;
  --font-weight-semibold:600;

  --letter-spacing-label: 0.02em; /* uppercase status captions */
}
```

### 2.6 Spacing, density, radius, elevation

```css
:root {
  /* 4px base geometric scale */
  --space-0:  0;
  --space-1:  0.25rem;  /* 4 */
  --space-2:  0.5rem;   /* 8 */
  --space-3:  0.75rem;  /* 12 */
  --space-4:  1rem;     /* 16 */
  --space-5:  1.25rem;  /* 20 */
  --space-6:  1.5rem;   /* 24 */
  --space-8:  2rem;     /* 32 */
  --space-10: 2.5rem;   /* 40 */
  --space-12: 3rem;     /* 48 */
  --space-16: 4rem;     /* 64 */

  /* Density axis — toggled via data-density */
  --density-row-h:       2rem;     /* comfortable default */
  --density-node:        2.25rem;
  --density-panel-pad:   var(--space-3);
  --density-graph-gap:   var(--space-6);

  --radius-none: 0;
  --radius-sm:   2px;   /* IDE chrome */
  --radius-md:   4px;   /* nodes, inputs */
  --radius-lg:   6px;   /* panels — keep tight */
  --radius-full: 9999px; /* reserved; avoid for status (shape carries meaning) */

  --shadow-elev-1: 0 1px 0 color-mix(in srgb, #000 40%, transparent);
  --shadow-elev-2: 0 4px 16px color-mix(in srgb, #000 45%, transparent);
  --shadow-focus:  0 0 0 2px var(--color-surface-page), 0 0 0 4px var(--color-border-focus);

  --border-width-hairline: 1px;
  --border-width-strong:   2px;

  --z-panel:    10;
  --z-popover:  40;
  --z-modal:    50;
  --z-toast:    60;
}

[data-density="compact"] {
  --density-row-h:     1.625rem; /* 26px */
  --density-node:      1.75rem;
  --density-panel-pad: var(--space-2);
  --density-graph-gap: var(--space-4);
  --font-size-body:    0.75rem;
  --font-size-caption: 0.625rem;
}

[data-density="spacious"] {
  --density-row-h:     2.5rem;
  --density-node:      2.75rem;
  --density-panel-pad: var(--space-4);
  --density-graph-gap: var(--space-8);
  --font-size-body:    0.875rem;
}
```

### 2.7 Motion tokens

```css
:root {
  --ease-out:     cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in:      cubic-bezier(0.4, 0, 1, 1);
  --ease-in-out:  cubic-bezier(0.4, 0, 0.2, 1);

  --duration-1: 100ms;
  --duration-2: 200ms;
  --duration-3: 300ms;
  --duration-4: 500ms;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --duration-1: 0ms;
    --duration-2: 0ms;
    --duration-3: 0ms;
    --duration-4: 0ms;
  }
}
```

### 2.8 Layout / customization tokens

```css
:root {
  --layout-session-w:   240px;  /* left rail */
  --layout-inspector-w: 320px;  /* right rail */
  --layout-chrome-h:    40px;   /* top bar */
  --layout-min-graph-w: 360px;

  /* Agent columns — toggle visibility; width collapses to 0 when hidden */
  --col-claude-code: 1fr;
  --col-cursor:      1fr;
  --col-codex:       1fr;
  --col-copilot:     0fr; /* off by default example */
  --col-gemini:      0fr;
}

[data-layout="graph-focus"] {
  --layout-session-w:   56px;   /* icon-only */
  --layout-inspector-w: 280px;
}

[data-layout="inspector-focus"] {
  --layout-session-w:   200px;
  --layout-inspector-w: 420px;
}

[data-layout="sessions-focus"] {
  --layout-session-w:   320px;
  --layout-inspector-w: 280px;
}
```

---

## 3. Typography choices

| Role | Face | Why |
|---|---|---|
| UI / body | **IBM Plex Sans** (400 / 500 / 600) | Technical, IDE-adjacent, not Inter/Roboto/system. Clear at 12–13px. |
| Code / node IDs / tool names / timestamps | **IBM Plex Mono** (400 / 500) | Matches Plex Sans metrics; familiar to Claude Code / terminal users. |
| Display | Same Plex Sans at `--font-size-display` | No second display font — spectate is a tool, not a brand site. |

**Loading:** preload `IBMPlexSans-Regular`, `IBMPlexSans-Medium`, `IBMPlexMono-Regular`; `font-display: swap`; Latin subset. Fallback metrics via size-adjust for Segoe UI / Cascadia to limit CLS.

**Do not use:** Inter, Roboto, Arial, bare `system-ui` as the primary stack, Geist as a silent Inter substitute without an explicit product decision.

---

## 4. Layout wire description

### 4.1 First viewport — one composition

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [Harness Spectate]   session filter · density · columns · theme         │  ← chrome 40px
├────────────┬───────────────────────────────────────────┬─────────────────┤
│ SESSIONS   │  LIVE GRAPH                               │ INSPECTOR       │
│            │                                           │                 │
│ ● run-a    │   [assemble]──[model]──[classify]──┐      │  Node: Bash     │
│ ○ run-b    │                        │           │      │  status:running │
│ ○ run-c    │                   [tool:Bash]──[pkg]──…   │  ─────────────  │
│            │                   [tool:Read]  …          │  args / result  │
│            │                                           │  deny reason    │
│            │   · faint graph grid (not card chrome)    │  timing         │
│            │                                           │                 │
│ 240px      │   flex (min 360px)                        │  320px          │
└────────────┴───────────────────────────────────────────┴─────────────────┘
```

**Composition rules**

1. Three panes share one continuous canvas color family (panel vs page differ by one neutral step only).
2. Separators are **hairline** (`--border-width-hairline` + `--color-border-subtle`) — not card shadows.
3. Graph is a **node/timeline**, not tiles: loop steps as primary spine; tool calls as child nodes branching from step 4 (Execute tools).
4. No stats strip, no promo cards, no multi-widget dashboard in the first viewport.
5. Selected session + selected node are the only accent-tinted surfaces.

### 4.2 Panel roles

| Panel | Content | Customization |
|---|---|---|
| **Session list** | Chronological sessions; live dot; agent host badge (mono caption) | Width via `--layout-session-w`; collapse to icons |
| **Live graph** | Harness loop spine + tool-call nodes; multi-agent as parallel columns | `data-layout`; agent column fr tracks; density |
| **Detail inspector** | Selected node: status label, payload, permission/deny provenance, timing | Width via `--layout-inspector-w`; tabs: Overview / Payload / Policy |

### 4.3 Graph structure (domain)

Aligns to harness loop steps (assemble → model → classify → tools → package → context):

```
Assemble → Call model → Classify → Execute tools ─┬→ Tool node*
                                  └→ (no tools) → Done
Package results → Update context → (loop)
```

Tool nodes inherit status tokens. Parallel agents = additional columns sharing the same Y-time axis.

### 4.4 Breakpoints

| Token | Width | Behavior |
|---|---|---|
| `--bp-lg` | ≥1280px | Three panes default |
| `--bp-md` | 768–1279px | Session list collapses to icon rail (56px); inspector overlay drawer on node select |
| `--bp-sm` | <768px | Single pane stack: Sessions → Graph (full) → Inspector as bottom sheet |

At `--bp-md` and below, keep **one** primary surface visible at a time for the graph; do not shrink three panes into unreadable thirds.

### 4.5 Customization axes (product settings)

| Axis | Values | Token / attribute |
|---|---|---|
| Theme | `dark` (default), `light` | `data-theme` |
| Density | `compact`, `comfortable`, `spacious` | `data-density` |
| Panel layout | `default`, `graph-focus`, `inspector-focus`, `sessions-focus` | `data-layout` |
| Agent columns | per-host on/off | `--col-*` → `0fr` / `1fr` |
| Status legend | docked footer vs inspector tab | UI preference, not a color token |

---

## 5. Node status legend

Exact ship labels (string constants). Visual = **fill/stroke color + geometric shape + label text**. No emoji as the primary signifier.

| Token / label | Color (dark) | Shape | Meaning |
|---|---|---|---|
| `available` | Teal stroke `#14B8A6` | ○ hollow circle | Capability exposed; not started |
| `unavailable-harness` | Slate `#8B949E` | ◌ dashed hollow circle | Harness does not expose this step/tool |
| `denied-org` | Burnt orange `#DB6D28` | ⬡ octagon (stop) | Blocked by organization policy |
| `denied-plugin` | Amber-orange `#F0883E` | ◇ diamond | Blocked by plugin / marketplace / hook |
| `denied-user` | Coral `#FF7B72` | ▢ square + geometric X | Denied by user / local permission |
| `running` | Sky `#79C0FF` | ● filled circle + pulse ring | In flight |
| `succeeded` | Green `#3FB950` | ● filled circle + check notch | Completed successfully |
| `failed` | Red `#F85149` | ● filled circle + cross | Errored |
| `waiting-approval` | Amber `#FFA657` | ▣ rounded square + pause bars | Awaiting human / tribunal approval |
| `idle` | Muted `#6E7681` | ○ hollow muted circle | Not active in this session |

**Shape geometry (implementer reference)**

| Shape id | Construction |
|---|---|
| `circle-outline` | 20×20 viewBox; stroke 1.5; no fill |
| `circle-dashed` | same; `stroke-dasharray: 3 2` |
| `circle-outline-muted` | same as outline; lower contrast stroke |
| `circle-filled-pulse` | solid fill; outer ring opacity animates 0.35→0 |
| `circle-check` | solid fill; 2-stroke check in `--color-text-on-accent` |
| `circle-cross` | solid fill; 2-stroke X in `--color-text-on-accent` |
| `octagon` | regular octagon; stroke + light fill |
| `diamond` | rotated square 45°; stroke + light fill |
| `square-x` | axis-aligned square; X inset |
| `rounded-square-pause` | `rx=3`; two vertical pause bars |

**Label presentation:** monospace caption, `--letter-spacing-label`, lowercase exact token string as shown (e.g. `waiting-approval`, not “Waiting”). Tooltip may expand to sentence form (“Waiting for approval”).

**Contrast (dark canvas `#0D1117`, verified this session)**

| Pair | Ratio | Level |
|---|---|---|
| text-primary `#E6EDF3` | 16.02:1 | AA body |
| text-secondary `#8B949E` | 6.15:1 | AA body |
| accent / available UI `#2DD4BF` | 10.17:1 | AA UI |
| running `#79C0FF` | 9.73:1 | AA UI |
| succeeded `#3FB950` | 7.45:1 | AA UI |
| failed `#F85149` | 5.65:1 | AA UI |
| waiting `#FFA657` | 9.77:1 | AA UI |
| denied-org `#DB6D28` | 5.61:1 | AA UI |
| denied-plugin `#F0883E` | 7.48:1 | AA UI |
| denied-user `#FF7B72` | 7.51:1 | AA UI |
| unavailable / idle UI `#8B949E` / `#6E7681` | 6.15:1 / 4.12:1 | AA UI |

**Denied family differentiation:** three shapes (octagon / diamond / square-x) + three hues in the orange→coral band. Never rely on hue alone. Do **not** use purple for any deny state.

**Extension note:** if a future `denied-harness` (active harness deny, distinct from `unavailable-harness`) is needed, twin `denied-org` tokens with shape `hexagon` and label `denied-harness` — do not invent a purple lane.

---

## 6. Motion principles (3)

Only three easings site-wide: `--ease-out` (enter), `--ease-in` (exit), `--ease-in-out` (through). Honor `prefers-reduced-motion` (durations → 0; status communicated by static shape + label).

### M1 — Running pulse (presence)

- **What:** Outer ring on `running` nodes expands and fades (scale 1→1.35, opacity 0.45→0).
- **When:** While status === `running`.
- **Timing:** 1200ms loop, `--ease-out`, infinite.
- **Reduced:** Static filled circle; optional 1px accent underline on the label instead of motion.

### M2 — Edge draw / node enter (hierarchy)

- **What:** When a new loop step or tool node appears, the connecting edge strokes from parent→child (`stroke-dashoffset`), then the node fades/scales in (opacity 0→1, scale 0.96→1).
- **When:** Graph append during a live session.
- **Timing:** edge 300ms `--ease-out`; node 200ms `--ease-out`, staggered +40ms.
- **Reduced:** Instant appear; no dash animation.

### M3 — Inspector cross-fade (focus change)

- **What:** Selecting a different node cross-fades inspector body (opacity + 4px translateY).
- **When:** Selection change.
- **Timing:** 200ms `--ease-in-out`.
- **Reduced:** Instant swap; retain focus ring via `--shadow-focus`.

**Non-goals for motion:** scroll-jacking, parallax, shimmer gradients, celebration confetti on `succeeded`, bounce spring on deny.

---

## 7. Component visual notes (spec only)

### Session row

- Height `--density-row-h`; hairline bottom border.
- Live session: 6px `--status-running-fg` dot (not emoji).
- Selected: `--color-surface-selected` + 2px left accent bar.

### Graph node

- Min size `--density-node`; label below or inside for compact.
- Selected: `--shadow-focus` + accent border.
- Group header (loop step): `--font-size-h3`, secondary text.

### Inspector

- Section titles `--font-size-h2`; payload in mono block on `--color-surface-sunken`.
- Deny provenance shows exact status label chip + policy source string.

### Status chip

- Shape icon 12–14px + label caption; padding `--space-1` `--space-2`.
- Never color-only; icon + text required.

---

## 8. Anti-patterns (this product)

- Purple / violet accent, glow, or AI-halo gradients
- Emoji as status (✅ ❌ ⏳) in the graph or legend
- Card grids / bento in the first viewport
- Hard-coded hex in components (`color: #3fb950`)
- Status differentiated by color alone
- Using accent teal as success green
- White text on `#F85149` fills
- `#484F58` idle strokes (fails 3:1 UI on canvas — use `#6E7681`+)
- Inter / Roboto / system as primary UI font
- More than three easings

---

## 9. Handoff

| Next | Why |
|---|---|
| `ux-designer` | Interaction details: keyboard graph nav, column picker, approval actions in inspector |
| `frontend-implementer` | Wire tokens → CSS / theme provider; SVG status icon set; three-pane shell |
| `accessibility-auditor` | Full WCAG pass on light theme + focus order in graph |

**Out of scope here:** React/DOM code, API contracts, harness telemetry schema.

---

## Contrast audit method

```text
python3 plugins/web-design/scripts/contrast_ratio.py pair --fg <fg> --bg <bg> --size {normal|large|ui}
```

Dark page background measured as `#0D1117`; elevated as `#161B22`. Re-run after any token edit.
