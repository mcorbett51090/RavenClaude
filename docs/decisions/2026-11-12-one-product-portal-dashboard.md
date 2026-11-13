# Decision: RavenClaude portal + dashboard are one product

**Date:** 2026-11-12 (America/New_York)  
**Status:** accepted  
**Surfaces:** `index.html`, `plugins/ravenclaude-core/dashboard.html`, generators, entry commands

## Context

The marketplace already folds the comfort-posture fragment into `index.html` ("One portal", v0.123.0), but ships a dual-product feel: a public **portal** (teal-then-green catalog shell on GitHub Pages) and a consumer **dashboard** (green Save surface via `rc dashboard` / `/dashboard`). Route ownership and chrome labels still diverge (Catalog vs Learn & Help; product tags; accent story).

Owner direction (2026-11-12): collapse to **one product**, local dashboard as home with hybrid Catalog+Control when possible, Control-first, teal accent, generators in scope.

## Locked decisions

| # | Decision | Notes |
|---|---|---|
| 1 | **Single product / single entry story (shape B)** | Kill the dual-product feel. Artifact collapse is phased (see below); product identity is one name now. |
| 2 | **Local dashboard is home; hybrid preferred** | `rc dashboard` / `/dashboard` is the canonical entry. Marketplace hybrid = same product with Catalog when the catalog payload is present (Pages/static or marketplace serve). |
| 3 | **Entry recommendation (owner: decide & go)** | Keep `/dashboard` + `rc dashboard` as the verb. Do not invent a second launcher. Marketplace maintainers keep `scripts/open-dashboard.sh` / root `serve-dashboards.py` as the same product in hybrid/static mode — not a second brand. |
| 4 | **Control-first** | Empty/unknown hash → Control (`#/settings` / The Thing). Already true on both shells; keep it. |
| 5 | **Parity recommendation (owner: decide & go)** | Same four destinations everywhere: **Control · Activity · Guardrails · Catalog**. Permanent content splits are debt. Payload diet is **mode-based** (static vs served; marketplace vs consumer install), not a forever portal-only / standalone-only split. Phase 1 renames standalone "Learn & Help" → **Catalog** for IA parity without baking the full marketplace inventory into every consumer install yet. |
| 6 | **Teal product accent** | Reopen the 2026-07-28 green-unification: `--rc-accent` is **teal** on every estate surface. One accent, one product. |
| 7 | **Generators / CI in scope** | Phase 1 unifies chrome + tokens + parity maps. Later phases collapse generators/artifacts (Gate 97/51 retarget) once Catalog mode exists on the shipped artifact. |
| 8 | **Save stays local-only (owner: decide & go)** | Sacred. `POST /__save` only on loopback `serve-dashboards.py`. GitHub Pages / static never writes posture. Hybrid = same UI; capability gated by server presence (Download fallback on static). Gate 27 marketplace refuse stays. |

## Phasing

### Phase 1 (this change) — one product *feel*

- Teal `--rc-accent` estate-wide; docs/README/tokens comments match.
- Standalone chrome: tag + **Catalog** group label aligned with the shell destinations.
- Gate 200 / Gate 144 destination maps accept `catalog` as the fourth group label.
- Decision + entry-command copy: one product, local home, Save local-only.
- Regenerate `dashboard.html` + `index.html`.

### Phase 2 — hybrid Catalog on the shipped artifact

- Mode flag / payload diet: include marketplace Catalog when building the marketplace hybrid; omit or lazy-load for lean consumer installs.
- Gate 132 budget raise only with an owned reason when Catalog shell DOM lands on standalone.
- **Phase 2 landed (implementation):** shipped `dashboard.html` stays `include_catalog=False` (Gate 132 Δ0). Runtime hybrid enables Browse via `catalog-data.json` / `__RC_DATA__`. CLI `--include-catalog` embeds lean payload for explicit hybrid builds only. Plan: `docs/plans/2026-11-12-phase2-catalog-hybrid.md`.

### Phase 3 — single artifact

- One generator pipeline; retire or redirect the non-canonical HTML; retarget Gates 97/51/132 to one surface; root `dash_path` + Pages host follow.
- **Phase 3a (entry unification):** root `serve-dashboards.py` / `open-dashboard.sh` land on `/plugins/ravenclaude-core/dashboard.html` (Catalog via `catalog-data.json`). Fat `index.html` kept for Pages + Gates 97/51 until 3b. Plan: `docs/plans/2026-11-12-phase3-single-artifact.md`.

## Non-goals (this decision)

- Killing `index.html` in the Phase 1 PR (Gate 51/97 blast radius).
- Making Save work on GitHub Pages.
- Shipping the full marketplace Catalog payload inside every consumer `dashboard.html` before mode diet exists.

## Consequences

- Brand story reverses the 2026-07-28 "commerce green everywhere" note — green remains available as status/`--rc-ok` and historical commerce reference, not the product accent.
- Prior "One portal" milestone remains historically true (fold mechanics); the **product home** is now the local dashboard entry, with the Pages shell as the static hybrid of the same product.
