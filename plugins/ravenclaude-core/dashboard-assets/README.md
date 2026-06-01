# Design system — RavenClaude shared dashboard assets

This directory holds the single source of truth for the visual design of the three web surfaces RavenClaude ships:

| Surface | Generator | Accent |
|---|---|---|
| `index.html` (landing) | `scripts/generate-index-dashboard.py` + `scripts/_index_dashboard_template.py` | teal |
| `repo-guide.html` (catalog) | `scripts/generate-repo-guide.py` | teal |
| `plugins/ravenclaude-core/dashboard.html` (posture editor + Norse panels) | `scripts/generate-dashboards.py` | gold |

Each generator reads [`shared-tokens.css`](shared-tokens.css) at generate-time and inlines the tokens into the surface's `<style>` block. **There is no runtime load** — every HTML artifact stays self-contained, consistent with the existing static-page discipline.

## Aesthetic

Intercom-inspired. Light beige monochromatic base (`#faf7f0`), warm near-black text (`#1a1614`), generous whitespace (16-24-32 padding rhythm), Inter typography with tight letter-spacing, very soft shadows.

**Two accents — by design.** Gold (`#a8882e`) is the dashboard's accent and preserves its Norse identity (Heimdall, Víðarr, Norns, Bifröst, Sleipnir, Níðhöggr — gold on light beige reads as parchment-and-gilt, Lindisfarne-Gospels-thematic). Teal (`#1f7f78`) is the consumer-facing accent for landing + catalog. A consumer who lands on `index.html` and clicks into the dashboard will see the accent shift; the shift is intentional and consistent — every surface has ONE accent, what it is differs by surface.

## Token reference

The complete token list is in [`shared-tokens.css`](shared-tokens.css). The categories:

| Category | Prefix | Purpose |
|---|---|---|
| Neutrals | `--rc-bg`, `--rc-surface`, `--rc-surface-2`, `--rc-border`, `--rc-border-strong` | The beige base + page surfaces. |
| Text | `--rc-text`, `--rc-muted`, `--rc-faint` | Body, secondary, tertiary text. |
| Gold accent | `--rc-gold`, `--rc-gold-soft` | Dashboard's accent. Borders / headings / icons / accent rules ONLY. |
| Teal accent | `--rc-teal`, `--rc-teal-soft` | Index + repo-guide accent. Safe for body text + inline links. |
| Status | `--rc-ok`, `--rc-warn`, `--rc-danger` | Solid status colors. |
| Status-on-surface | `--rc-{ok,warn,danger,neutral}-{bg,fg}` | Badge backgrounds + foregrounds. |
| Typography | `--rc-font-sans`, `--rc-font-mono`, `--rc-tracking-*` | Inter + JetBrains Mono. Tight letter-spacing scale. |
| Spacing | `--rc-space-1` (4px) through `--rc-space-8` (64px) | 4px-base scale. |
| Radii | `--rc-radius-sm` (6px), `--rc-radius` (10px), `--rc-radius-lg` (16px), `--rc-radius-pill` (999px) | |
| Shadows | `--rc-shadow-sm`, `--rc-shadow`, `--rc-shadow-lg` | Warm-tinted, low-opacity. |
| Focus | `--rc-focus-ring`, `--rc-focus-ring-gold` | a11y outline rings, accent-tinted. |

## Accessibility (load-bearing — do not override without testing)

- **`--rc-gold` is ~3.6:1 on `--rc-bg`** → passes WCAG AA for **large text only** (and UI components per WCAG 1.4.11). **Never use `--rc-gold` as body text.** Use for borders, headings ≥18pt or 14pt-bold, icons, accent rules. The token file carries an inline `/* CONTRAST NOTE */` comment to reinforce this for future contributors.
- **`--rc-teal` is ~4.5:1 on `--rc-bg`** → passes AA for body text and inline links.
- **`--rc-warn` is ~4.6:1 on `--rc-bg`** → passes AA for badge labels at 12-13px (the dashboard's Norse pipeline badge size).

If you add a new token: verify it against `--rc-bg` and `--rc-surface-2` (the two background colors text might land on) using a contrast checker before committing.

## Class-naming discipline — the `.rc-*` prefix

Every shared component class is prefixed `.rc-*` (e.g. `.rc-card`, `.rc-pill`, `.rc-badge`, `.rc-tab`). **Per-surface classes keep their existing unprefixed names** — `repo-guide.html` `.tab-btn` (sticky header) and `dashboard.html` `.tab-btn` (Norse panel strip) currently define the same class name with different geometry; prefixing the SHARED classes prevents collision with either.

Do:
- Use `.rc-card`, `.rc-pill`, etc. for any pattern that should look identical across surfaces.
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

- **Accent nudge** (taste, not contrast): edit `--rc-gold`, `--rc-teal`, or their `-soft` variants, regenerate all three surfaces, visual smoke. Single-token edits are low-risk.
- **Status contrast adjustment**: re-verify against `--rc-bg` using a contrast checker, update both the value and the inline `CONTRAST NOTE` comment.
- **Adding a new shared component class**: add to `shared-tokens.css` with the `.rc-*` prefix, document in the table above, add a usage example to the surface(s) that will consume it.
- **Adding a new surface**: read the shared tokens via the generator pattern above. Do not duplicate the token block.
