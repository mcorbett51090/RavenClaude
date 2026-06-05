# Build plan — portal 5-section IA (Home/Discover/Configure/Observe/Learn)

**Date:** 2026-06-05 · Tactical ("how"). Strategic/why + Panel-1 gap-fill: [`strategic-plan.md`](strategic-plan.md).

**Headline (from Panel 1, G-A2):** the feared "Tier 2 = edit the shipped `generate-dashboards.py`" is **avoidable**. The dashboard CSS is already scoped under `#dash-root` and the standalone copy is *not* wrapped, so hiding the dashboard's internal chrome in the folded view is a **one-line shell-side CSS rule** + a shell sub-nav. The entire reorg is therefore a **shell-layer change** (`scripts/_index_dashboard_template.py` + `scripts/generate-index-dashboard.py`) plus gate updates — **no `generate-dashboards.py` edit, no consumer `dashboard.html` change, no drift risk.**

## Target IA + mapping (nothing orphaned)

```
Sidebar            Section content (shell)                         Drives (folded #dash-root tab via __dashApp.show)
─────────────────────────────────────────────────────────────────────────────────────────────────
Home               hero · onboarding · "I want to…" LINK → Discover · featured combos     —
Discover  ┐ sub-nav: Plugins · Specialists · Use cases
          │  Plugins      catalog cards + categories (viewMarketplace)                     —
          │  Specialists  295-agent roster + skills/hooks library (viewTeam)               —
          │  Use cases    the "I want to…" table (single source; Home links here)          —
          └  (plugin click → __openPlugin rich reference; "Configure variables →" → plugin-<name>)
Configure ┐ sub-nav: Posture · Web access · Preview a review · Plugin variables
          │  Posture        → settings        Web access → web-access
          │  Preview review → simulator       Plugin variables → plugin-<name>
          └  (served-only banner on static)
Observe   ┐ sub-nav: Run feed · Perimeter · Security log · Lineage · Session · Review log
          │  → activity · heimdall · vidarr · norns · mimir · saga   (nidhoggr→heimdall, sleipnir→activity)
          └  (served-only banner on static)
Learn     ┐ sub-nav: Concepts · Commands · Guidance · Pipeline · Architecture · Install · About
          │  → learn · commands · trees · pipeline · (shell prose) · bifrost+install · about
          └  Resources prose (templates/knowledge/architecture/export) rendered shell-native
```

Every one of the 17 dashboard tabs + 6 old shell views has exactly one home (architect's table, strategic-plan §"G-A4 / Mapping").

## Phase 1 — Shell IA scaffold (the only phase that ships behavior)

Edit **`scripts/_index_dashboard_template.py`**:

1. **NAV → 5 ids:** `home, discover, configure, observe, learn` (icons: home, market, sliders, eye/activity, book). Remove team/marketplace/dashboard/configuration/resources as top-level ids.
2. **Sub-nav per section** — extend the existing `navChildren(id)` accordion (already used for Marketplace categories) to emit each section's sub-items as `role=tablist` with arrow-key roving (G-A3 a11y). Sub-items either render a shell view (Discover/Learn-prose) or call `viewDashboard(section, subtab)`.
3. **Router (`route()` / `resolveNavActive()` / `payloadKind()`):**
   - Add `SECTION_DEFAULT = { discover:"plugins", configure:"settings", observe:"activity", learn:"learn" }` (shell sub-tab landing).
   - Add legacy-route **alias table** → `{section, subtab}` covering every committed `#/…` (architect's routing table): `heimdall/vidarr/norns/mimir/saga/activity→observe`; `nidhoggr→observe/heimdall`, `sleipnir→observe/activity`; `settings/comfort-posture→configure/settings`, `web-access→configure/web-access`, `simulator→configure/simulator`; `pipeline→learn/pipeline`, `learn/commands/trees/bifrost/install/about→learn/<id>`, `dashboard→learn/overview`; `plugin-*→discover` (then `__openPlugin`).
   - `route()` stays the **sole** `hashchange` owner (fragment already strips the dashboard's listener). Single-router invariant preserved.
4. **Hide the folded dashboard's chrome (G-A2):** add to the shell `<style>` — `#dash-root .cat-bar, #dash-root .tab-bar { display:none !important; }`. Standalone `dashboard.html` is unaffected (not under `#dash-root`).
5. **Served-mode banner (G-D1):** Observe + the live Configure sub-tabs render a top banner `"Live data needs the served dashboard — run \`bash scripts/open-dashboard.sh\`"` when not on `127.0.0.1`. Reuse the dashboard's existing served signal; **no new shell `/__*` probe, no CORS** (security invariant). Silent on localhost.
6. **Discover** (`viewMarketplace`+`viewTeam` merged under one section with sub-nav): Plugins=existing catalog; Specialists=existing roster; Use cases=existing UC table (keep `.slice(0,400)` + scroll cap). `__openPlugin` unchanged (rich reference + "Configure variables →" deep-link).
7. **Home:** drop any inline use-case re-render; the "I want to…" CTA links to `#/discover` (G-D2). Keep hero/onboarding/featured; **remove "Recent activity"** (moves to Observe).
8. **Learn:** fold shell `viewResources` prose (templates/knowledge/architecture/export) as a sub-tab; other sub-tabs drive `learn/commands/trees/pipeline/bifrost/install/about`.
9. **Escaping (G-S1):** every newly-surfaced field in Discover goes through `esc()`.
10. **⌘K palette + quick-actions + featured-combos:** repoint routes to the new sections (`#/discover`, `#/configure`, `#/observe`, `#/learn`).

Edit **`scripts/generate-index-dashboard.py`** only if data shape needs it (determinism per G-O4: reuse exact `Last updated</span> <code>…</code>` markup; no `set`/`dict`-without-sort in any new aggregation). No `generate-dashboards.py` change.

## Phase 2 — Gates (atomic with Phase 1)

Edit **`scripts/check-shell-router.mjs`** (the **Gate 51** fixture — not Gate 70; G-O1):
- NAV id list → `home, discover, configure, observe, learn` (G-O2).
- `resolveNavActive` returnable ids → surviving set (drop `"dashboard"`).
- Expand `expectedDashboardRoutes` to the **full** back-compat set (all 13+ legacy `#/…`) and assert the new `DASH_TAB_ALIAS`/alias-table entries resolve (G-O3).
- Keep mount-host (`#dash-root`), `window.__dashApp`, no-iframe assertions.
- **Add a NAV-rename must-fail half** + a matching fixture in `audit-gates.sh` (today only DASH_SECTIONS is mutated) — teeth for "a section silently dropped."
- **Add a phantom-route cross-check** (G-A1): assert every non-aliased `DASH_SECTIONS` id maps to a real tab or an explicit alias (so shell/DOM tab sets can't drift).

Render gates / Gate 13 / Gate 97: **unchanged** — Phase 1 doesn't touch the folded sub-app's JS, so `function activate(` (G-O5) and per-tab function extraction still resolve; `dashboard.html` standalone is byte-identical (no generator edit).

## Phase 3 — Ship
- Version bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` minor + `marketplace.json` lockstep.
- CLAUDE.md milestone (the IA reorg + the "two-chromes via scoped CSS" insight).
- Regenerate `index.html`; run full `audit-gates.sh` + ruff + prettier + layout; PR.

## Verification
1. `python3 scripts/generate-index-dashboard.py && python3 scripts/generate-index-dashboard.py --check` (Gate 97).
2. Deep-links resolve: `#/heimdall #/nidhoggr #/sleipnir #/comfort-posture #/web-access #/pipeline #/plugin-finance #/dashboard` → correct section + sub-tab (no silent overview fallback).
3. `node scripts/check-shell-router.mjs index.html` (Gate 51) incl. both must-fail halves.
4. Served: `bash scripts/open-dashboard.sh` → Observe/Configure live; Static (plain server): served banner + per-card empty states; no `<iframe>`; one chrome (no dashboard cat-bar visible).
5. Full `audit-gates.sh` green; render gates unchanged; standalone `dashboard.html` still has its own nav.
6. **No-browser caveat:** sub-nav rendering + the chrome-hide + a11y roving need a local eyeball.

## Risk register
| # | Risk | Mitigation |
|---|---|---|
| R1 | Gate 51 fails on NAV rename | Phase 2 atomic with Phase 1; update ids + must-fail |
| R2 | Deep-link silent fallback (nidhoggr/sleipnir) | alias table + phantom-route cross-check gate (G-A1) |
| R3 | XSS via new Discover innerHTML field | `esc()` everywhere (G-S1) + security glance |
| R4 | Gate 97 false-fail on shallow CI (git-date markup) | reuse exact markup / extend `_strip_ts` (G-O4) |
| R5 | a11y regression from hidden tab-bar | shell sub-nav roving-tabindex (G-A3) |
| R6 | Empty Observe/Configure on static look broken | served banner (G-D1) |
| R7 | page weight grows | optional byte-budget gate (G-O6, P1) |
| R8 | no-browser visual gap | local eyeball before merge; gates cover logic |

## P0 / P1 recommendations (Panel 2 cold-review)

_(to be appended in Phase 5)_
