# Dashboard removed routes (C5 ledger)

The dashboard IA re-cut (FORGE `dashboard-consumption`) collapsed the shell to four task
destinations — **Control · Activity · Guardrails · Catalog** — plus a **Help** drawer.
No bookmark rots silently: every retired route either redirects to a surviving
destination or is a named removal below. This table is rendered verbatim inside the
dashboard's **Help** drawer (`panel-help` → "Where things moved") so a user landing on an
old link can see where it went.

Both surfaces are generated (`scripts/generate-dashboards.py` +
`scripts/generate-index-dashboard.py`); routes resolve through `SECTION_ALIAS` /
`DASH_OWNER` / `DASH_TAB_ALIAS` and are enforced by Gate 51
(`scripts/check-committed-routes.mjs`, `scripts/check-shell-router.mjs`).

This is the same table (same rows, same order) rendered inside the Help drawer; it is
grouped by destination so the drawer stays net-DOM-negative, but every retired route is
named in the first cell with its disposition in the second.

| Old link(s) | Where it is now |
| --- | --- |
| `#/home` · `#/overview` · `#/configure` · `#/simulator` | **Control (Settings)** — the marketing home (`viewHome`: hero + CTA grid + onboarding checklist), the Overview tab (`panel-overview`), the non-writing posture editor (`viewConfiguration`, incl. its 167 always-`checked` "Plugin activation" toggles wired to nothing), and the "Preview a review" tab (`panel-simulator`) were removed. Settings is the one editor that saves; `/__classify` is kept for Gate 32 parity (now UI-orphaned). |
| `#/team` | **Catalog** — the specialist roster (`viewTeam`) now lives in the marketplace. |
| `#/about` · `#/bifrost` · `#/install` · `#/commands` | **Help** — folded into this drawer as the About, Claude Code (Bifröst), Copilot CLI, and Commands sections. |
| `#/concepts` | **Control** — a named removal. The Concepts route was aliased to the Learn *tab*, but P6 stripped the portal's `learn-payload`, so `loadLearn()` early-returned and `panel-learn` rendered a blank host. The concept explainers live on the standalone dashboard (`rc dashboard` → `/dashboard`). |
| `#/learn` | **Not removed — it renders `viewResources()` on the portal** (Templates, decision trees & knowledge). It is homed under **Catalog** via `SHELL_ROUTE_HOME`, matching the standalone's "Learn & Help" grouping. The 58 *concept* explainers are standalone-only; the route itself is live portal content, not a retired one. |
| `#/trees` | **Not removed — the portal ships the full 3.79 MB `trees-payload`** and `DASH_OWNER` homes it under Catalog. Byte-identical to the standalone. |

## Notes

- **No `required_routes` floor entry was retired** in this change: the floor (`#/settings`,
  `#/learn`, `#/plugin-vars` on the standalone; `#/settings`, `#/plugin-vars`, `#/control`,
  `#/activity`, `#/guardrails`, `#/catalog` on the portal) is intact. If a future phase
  retires a floor route, it must add a row here in the same commit (Gate 51 subset backstop).
- **Web access** keeps its honest empty/download state; `.ravenclaude/web-access.yaml` is
  **not** created (it remains the only authoring UI for a file the agent is forbidden to
  create).
- The blank-host safety net: the shared `activate()` fallback and `route()`'s default both
  land on **Control** (`panel-settings`), so a mistyped/unrecognized route renders the
  Control panel — never a blank host.
