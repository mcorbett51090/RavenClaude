# Design system — RavenClaude shared dashboard assets

This directory holds the visual design assets for the web surfaces RavenClaude ships. Surfaces #1 and #2 share [`shared-tokens.css`](shared-tokens.css) and are **one product** (decision [`docs/decisions/2026-11-12-one-product-portal-dashboard.md`](../../../docs/decisions/2026-11-12-one-product-portal-dashboard.md)); surface #3 (Spectate) is a deliberate exception with its own runtime stylesheet.

| # | Surface | Generator | Role in the one product |
|---|---|---|---|
| 1 | `index.html` (static / Pages hybrid) | `scripts/generate-index-dashboard.py` + `scripts/_index_dashboard_template.py` | Browse + Control shell (Catalog present); Save needs local serve |
| 2 | `plugins/ravenclaude-core/dashboard.html` (canonical local home) | `scripts/generate-dashboards.py` | `rc dashboard` / `/dashboard` — Control-first; Save & apply on loopback |
| 3 | `/spectate` — Harness Spectate livestream (`spectate/`), served by `serve-dashboards.py` | none — hand-authored static assets | teal focus / selection only (own token set) |

> The catalog surface `repo-guide.html` (and its `scripts/generate-repo-guide.py` generator) was folded into `index.html` and **removed in v0.124.0** — it is no longer a shipped surface.

Each generator reads [`shared-tokens.css`](shared-tokens.css) at generate-time and inlines the tokens into the surface's `<style>` block. **There is no runtime load** — every HTML artifact stays self-contained, consistent with the existing static-page discipline.

### Surface #3 — Spectate is the runtime-CSS exception

`spectate/` (`index.html`, `app.js`, `spectate.css`, `status-icons.svg`) is **not** generated and **does not** inline `--rc-*` tokens. Estate surfaces (#1, #2) inline `shared-tokens.css` at generate time; Spectate loads `/spectate/spectate.css` at runtime, with its own `--color-*` / `--status-*` token set (dark default + light mirror) from [`docs/plans/2026-10-09-harness-spectate/design-system-spec.md`](../../../docs/plans/2026-10-09-harness-spectate/design-system-spec.md). The CSP on the Spectate document forbids inline `<style>` / `<script>`, so runtime CSS is also the only shape that works.

It differs from the estate chrome on purpose: IBM Plex Sans + Mono instead of Space Grotesk + Inter, a single teal accent reserved for focus / selection / active edges (never success), and a hairline IDE layout (session rail, loop graph, inspector) instead of `.rc-card` tiles. Every status is colour + shape + exact label (11 statuses, including the `denied-harness` hexagon). Do not add `--rc-*` tokens or `.rc-*` classes to it, and do not import its tokens into the estate generators. `scripts/check-spectate-render.mjs` is its stub-DOM gate (`node scripts/check-spectate-render.mjs`).

## Aesthetic

Borrows the **RavenPower commerce site's visual language**: a cool near-black canvas (`--rc-bg #07080a`) with the commerce panel ladder (`#0c0e12` / `#10131a`) lifting on top, translucent-white hairlines (`rgba(255,255,255,0.07 / 0.14)`), cool near-white text (`#f5f7fa`), a **Space Grotesk** display face for headings + Inter for body, and generous whitespace. Depth is hairline-led: layered panels + a 1px hairline + a whisper shadow. DARK is the default; the light theme is retained as an opt-in `[data-theme="light"]`.

**Accent is minimal — a whisper, not a fill.** The **teal** product accent appears only as: a thin hairline rule (`.rc-rule`), a 3px card outline to flag a primary/active tile (`.rc-card--accent` / `--accent-gold`), the active nav-item tint, the eyebrow's glowing dot, the occasional link/heading, and a single primary CTA (`.rc-button--gold` — the teal pill with a ring+glow hover). Everything else is monochrome. The one memorable interactive beat is the CTA glow; restraint carries the rest. For the card/tile rationale + the dark-theme-residue audit, see the [`web-design/card-tile-ui`](../../web-design/skills/card-tile-ui/SKILL.md) skill and [`web-design/knowledge/card-tile-ui-pattern-2026.md`](../../web-design/knowledge/card-tile-ui-pattern-2026.md).

**One accent — by design (2026-11-12).** Estate surfaces share product **teal** (`--rc-accent #3aa391` dark / `#186e68` light). `--rc-gold` / `--rc-teal` are back-compat aliases of that teal. Historical commerce green is available as `--rc-commerce` for forks; it is not the product accent. IA destinations on both shells: **Control · Activity · Guardrails · Catalog**.

## Token reference

The complete token list is in [`shared-tokens.css`](shared-tokens.css). The categories:

| Category | Prefix | Purpose |
|---|---|---|
| Neutrals | `--rc-bg`, `--rc-surface`, `--rc-surface-2`, `--rc-border`, `--rc-border-strong` | Cool near-black base + the commerce panel ladder + translucent-white hairlines. |
| Text | `--rc-text`, `--rc-muted`, `--rc-faint` | Body, secondary, tertiary text (cool near-white). |
| Teal accent | `--rc-accent`, `--rc-accent-2`, `--rc-accent-soft`, `--rc-accent-glow` | Product accent. `--rc-gold` / `--rc-teal` alias it. AA on both themes. |
| Commerce green | `--rc-commerce`, `--rc-commerce-2` | Historical RavenPower site green — available, not the accent. |
| Status | `--rc-ok`, `--rc-warn`, `--rc-danger` | Solid status colors (kept separate from the brand accent). |
| Status-on-surface | `--rc-{ok,warn,danger,neutral}-{bg,fg}` | Badge backgrounds + foregrounds. |
| Typography | `--rc-font-display`, `--rc-font-sans`, `--rc-font-mono`, `--rc-tracking-*` | Space Grotesk (display) + Inter (body) + JetBrains Mono. Tight letter-spacing scale. |
| Spacing | `--rc-space-1` (4px) through `--rc-space-8` (64px) | 4px-base scale. |
| Radii | `--rc-radius-sm` (6px), `--rc-radius` (10px), `--rc-radius-lg` (16px), `--rc-radius-pill` (999px) | |
| Shadows | `--rc-shadow-sm`, `--rc-shadow`, `--rc-shadow-lg` | Black, low-opacity on the dark base; cool-tinted whisper under `[data-theme="light"]`. |
| Motion | `--rc-ease`, `--rc-ease-out` | The commerce easing curves (through-states / entrances). |
| Focus | `--rc-focus-ring`, `--rc-focus-ring-gold` | a11y outline rings, accent-tinted (the `-gold`-named ring is teal). |

## Accessibility (load-bearing — do not override without testing)

- **`--rc-accent` (teal `#3aa391`) is 6.51:1 on `--rc-bg` (`#07080a`)** → **AA**. Comfortably safe as body text; reserving it for accents is aesthetic restraint, not an a11y floor. Under `[data-theme="light"]` it darkens to `#186e68` = 5.60:1 (AA). `--rc-gold` / `--rc-teal` alias it, so the same ratios apply.
- **`--rc-warn` `#d4a017` is ~AA on `--rc-bg`** for badge labels at 12-13px; for badge chips prefer the `--rc-warn-bg` / `--rc-warn-fg` pair.
- The token file carries an inline `/* CONTRAST NOTE */` comment on each accent to reinforce these ratios for future contributors.

If you add a new token: verify it against `--rc-bg` and `--rc-surface-2` (the two background colors text might land on) using a contrast checker before committing.

## Class-naming discipline — the `.rc-*` prefix

Every shared component class is prefixed `.rc-*` (e.g. `.rc-card`, `.rc-pill`, `.rc-badge`, `.rc-tab`). **Per-surface classes keep their existing unprefixed names** — `dashboard.html` `.tab-btn` (Norse panel strip) keeps its unprefixed name; the former `repo-guide.html` `.tab-btn` (sticky header) defined the same class name with different geometry before that surface was removed in v0.124.0 — prefixing the SHARED classes prevents collision.

Do:
- Use `.rc-card`, `.rc-pill`, etc. for any pattern that should look identical across surfaces.
- Reach for the minimal-accent utilities — `.rc-card--accent` / `.rc-card--accent-gold` (a 3px accent edge to flag a primary/active tile) and `.rc-rule` / `.rc-rule--gold` (a faded-end hairline accent line) — instead of accent-tinting whole surfaces.
- Extend with surface-specific modifier classes when needed (e.g., `.rc-tab--gold` for the dashboard's gold variant).

Don't:
- Add unprefixed shared classes — they will collide.
- Inline hex colors in generators — use `var(--rc-*)` tokens. The verification suite enforces this (`grep -E '#[0-9a-fA-F]{6}'` on generator scripts).

**Host-scope chips:** Cards for skills / agents / commands carry an `.rc-badge--host-*` scope chip (All agents vs Claude Code / Cursor / Codex / Copilot / Grok reserved / Gemini / Multi) with a filter strip; see `host-scope-map.json` (inventory `platform_dependency` snapshot) and MH-18 in `scripts/generate-dashboards.py`.

## Generator integration pattern

All three generators converge on the same pattern:

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_TOKENS = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"
```

Read `SHARED_TOKENS` at generate time and inline into the surface `<style>` block. Do not runtime-link the CSS file.
