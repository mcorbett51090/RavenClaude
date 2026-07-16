# Design system — RavenClaude shared dashboard assets

This directory holds the single source of truth for the visual design of the three web surfaces RavenClaude ships:

| Surface | Generator | Accent |
|---|---|---|
| `index.html` (landing) | `scripts/generate-index-dashboard.py` + `scripts/_index_dashboard_template.py` | teal |
| `repo-guide.html` (catalog) | `scripts/generate-repo-guide.py` | teal |
| `plugins/ravenclaude-core/dashboard.html` (posture editor + Norse panels) | `scripts/generate-dashboards.py` | green |

Each generator reads [`shared-tokens.css`](shared-tokens.css) at generate-time and inlines the tokens into the surface's `<style>` block. **There is no runtime load** — every HTML artifact stays self-contained, consistent with the existing static-page discipline.

## Aesthetic

Borrows the **RavenPower commerce site's visual language**: a cool near-black canvas (`--rc-bg #07080a`) with the commerce panel ladder (`#0c0e12` / `#10131a`) lifting on top, translucent-white hairlines (`rgba(255,255,255,0.07 / 0.14)`), cool near-white text (`#f5f7fa`), a **Space Grotesk** display face for headings + Inter for body, and generous whitespace. Depth is hairline-led: layered panels + a 1px hairline + a whisper shadow. DARK is the default; the light theme is retained as an opt-in `[data-theme="light"]`.

**Accent is minimal — a whisper, not a fill.** The green accent appears only as: a thin hairline rule (`.rc-rule`), a 3px card outline to flag a primary/active tile (`.rc-card--accent` / `--accent-gold`), the active nav-item tint, the eyebrow's glowing dot, the occasional link/heading, and a single primary CTA (`.rc-button--gold` — the green pill with a ring+glow hover). Everything else is monochrome. The one memorable interactive beat is the CTA glow; restraint carries the rest. For the card/tile rationale + the dark-theme-residue audit, see the [`web-design/card-tile-ui`](../../web-design/skills/card-tile-ui/SKILL.md) skill and [`web-design/knowledge/card-tile-ui-pattern-2026.md`](../../web-design/knowledge/card-tile-ui-pattern-2026.md).

**Two accents — by design.** The commerce signature **green** (`--rc-accent #56D08A`) is the dashboard's primary accent (10.29:1 on the base — AAA). **Teal** (`--rc-teal #3aa391`) is the secondary accent for landing + catalog. `--rc-gold` / `--rc-gold-soft` are kept as **back-compat aliases** of the green so historical references resolve unchanged. A consumer who lands on `index.html` and clicks into the dashboard sees the accent shift green↔teal; the shift is intentional and consistent — every surface has ONE accent, what it is differs by surface.

## Token reference

The complete token list is in [`shared-tokens.css`](shared-tokens.css). The categories:

| Category | Prefix | Purpose |
|---|---|---|
| Neutrals | `--rc-bg`, `--rc-surface`, `--rc-surface-2`, `--rc-border`, `--rc-border-strong` | Cool near-black base + the commerce panel ladder + translucent-white hairlines. |
| Text | `--rc-text`, `--rc-muted`, `--rc-faint` | Body, secondary, tertiary text (cool near-white). |
| Green accent | `--rc-accent`, `--rc-accent-2`, `--rc-accent-soft`, `--rc-accent-glow` | Dashboard's primary accent (commerce green). `--rc-gold` / `--rc-gold-soft` alias it. AAA on the dark base. |
| Teal accent | `--rc-teal`, `--rc-teal-soft` | Index + repo-guide secondary accent. Safe for body text + inline links. |
| Status | `--rc-ok`, `--rc-warn`, `--rc-danger` | Solid status colors (kept separate from the green brand accent). |
| Status-on-surface | `--rc-{ok,warn,danger,neutral}-{bg,fg}` | Badge backgrounds + foregrounds. |
| Typography | `--rc-font-display`, `--rc-font-sans`, `--rc-font-mono`, `--rc-tracking-*` | Space Grotesk (display) + Inter (body) + JetBrains Mono. Tight letter-spacing scale. |
| Spacing | `--rc-space-1` (4px) through `--rc-space-8` (64px) | 4px-base scale. |
| Radii | `--rc-radius-sm` (6px), `--rc-radius` (10px), `--rc-radius-lg` (16px), `--rc-radius-pill` (999px) | |
| Shadows | `--rc-shadow-sm`, `--rc-shadow`, `--rc-shadow-lg` | Black, low-opacity on the dark base; cool-tinted whisper under `[data-theme="light"]`. |
| Motion | `--rc-ease`, `--rc-ease-out` | The commerce easing curves (through-states / entrances). |
| Focus | `--rc-focus-ring`, `--rc-focus-ring-gold` | a11y outline rings, accent-tinted (the `-gold`-named ring is green). |

## Accessibility (load-bearing — do not override without testing)

- **`--rc-accent` (green `#56D08A`) is 10.29:1 on `--rc-bg` (`#07080a`)** → **AAA** (10.79:1 on pure `#000`). Comfortably safe as body text; reserving it for accents is aesthetic restraint, not an a11y floor. Under `[data-theme="light"]` it darkens to `#157a45` = 4.98:1 (AA — clears the body floor). `--rc-gold` aliases it, so the same ratios apply.
- **`--rc-teal` is 6.51:1 on `--rc-bg`** (dark) / 4.45:1 on the light canvas → passes AA for body text and inline links.
- **`--rc-warn` `#d4a017` is ~AA on `--rc-bg`** for badge labels at 12-13px; for badge chips prefer the `--rc-warn-bg` / `--rc-warn-fg` pair.
- The token file carries an inline `/* CONTRAST NOTE */` comment on each accent to reinforce these ratios for future contributors.

If you add a new token: verify it against `--rc-bg` and `--rc-surface-2` (the two background colors text might land on) using a contrast checker before committing.

## Class-naming discipline — the `.rc-*` prefix

Every shared component class is prefixed `.rc-*` (e.g. `.rc-card`, `.rc-pill`, `.rc-badge`, `.rc-tab`). **Per-surface classes keep their existing unprefixed names** — `repo-guide.html` `.tab-btn` (sticky header) and `dashboard.html` `.tab-btn` (Norse panel strip) currently define the same class name with different geometry; prefixing the SHARED classes prevents collision with either.

Do:
- Use `.rc-card`, `.rc-pill`, etc. for any pattern that should look identical across surfaces.
- Reach for the minimal-accent utilities — `.rc-card--accent` / `.rc-card--accent-gold` (a 3px accent edge to flag a primary/active tile) and `.rc-rule` / `.rc-rule--gold` (a faded-end hairline accent line) — instead of accent-tinting whole surfaces.
- Extend with surface-specific modifier classes when needed (e.g., `.rc-tab--gold` for the dashboard's gold variant).

Don't:
- Add unprefixed shared classes — they will collide.
- Inline hex colors in generators — use `var(--rc-*)` tokens. The verification suite enforces this (`grep -E '#[0-9a-fA-F]{6}'` on generator scripts).

## Generator integration pattern

All three generators converge on the same pattern:

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_TOKENS = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"

def _load_shared_tokens() -> str:
    return SHARED_TOKENS.read_text(encoding="utf-8")
```

The loaded string is embedded into the surface's `<style>` block at generate-time. F-string injection is safe — Python f-string substitution does not re-evaluate substituted content, so CSS braces inside `shared_tokens` are inserted as plain text.

Per-surface CSS (the structural layout, the surface-specific accent override) comes AFTER the shared tokens block in the `<style>` element. Cascade order: shared tokens → surface tokens → component classes → surface-specific overrides.

## When to update tokens

- **Accent nudge** (taste, not contrast): edit `--rc-accent` (green) / `--rc-teal` or their `-2`/`-soft` variants, regenerate all surfaces, visual smoke. Single-token edits are low-risk (the `--rc-gold` alias follows `--rc-accent` automatically).
- **Status contrast adjustment**: re-verify against `--rc-bg` using a contrast checker, update both the value and the inline `CONTRAST NOTE` comment.
- **Adding a new shared component class**: add to `shared-tokens.css` with the `.rc-*` prefix, document in the table above, add a usage example to the surface(s) that will consume it.
- **Adding a new surface**: read the shared tokens via the generator pattern above. Do not duplicate the token block.
