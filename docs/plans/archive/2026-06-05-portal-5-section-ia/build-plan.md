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

## P0 / P1 recommendations (Panel 2 cold-review — tester-QA · PM · deep-researcher · UX)

Panel 2 verified the plan's 7 load-bearing claims **all TRUE** (chrome-hide is folded-only and safe; render gates are CSS-engine-free so `display:none` can't break them; `__dashApp.show()`/`activate()` fallback, the phantom routes, the Gate-51 hardcoded ids, and `_strip_ts`'s 4 surfaces all confirmed at the cited lines). The gaps are in **completeness of the route contract, the served signal, and testability of the deferred-to-eyeball UI**. Consolidated, deduped:

### P0 — must resolve before/within build

- **P0-1 Alias the legacy *shell* top-level routes too, and repoint internal links.** The plan only aliased the *dashboard* sub-routes. But `#/marketplace #/configuration #/team #/resources` are emitted by **~15 in-shell `href=` call sites** (`_index_dashboard_template.py:606,607,789,862,879-881,1026,1090,1304-1312…`) **and** by `quick_actions[].route` in **`generate-index-dashboard.py:633,636`** (`#/configuration`, `#/marketplace`). Add aliases `marketplace→discover`, `configuration→configure`, `team→discover/specialists`, `resources→learn`, **and** repoint the call sites + quick-actions to the canonical new routes. (deep-researcher P0-1/P0-2)
- **P0-2 Define the served-mode signal precisely — there is no shared one.** Served detection today is **three independent per-card HEAD probes inside the folded sub-app** (`generate-dashboards.py:7278/7725/7887`), none exposed on `window.__dashApp`; `location.hostname==="127.0.0.1"` *disagrees* with them (LAN IP served, or `python -m http.server` on localhost = static). Decision: **expose one served flag on `window.__dashApp`** (set from the sub-app's existing probe result) and have the shell banner read it — **no new shell probe, no CORS** (preserves the security invariant). (tester-QA P0-3, PM P0)
- **P0-3 Specify the `resolveNavActive` return contract.** It must map a folded route → its owning **section id** (`heimdall→observe`), not the literal `"dashboard"` the rename deletes. Update Gate 51 `:139` accordingly. (tester-QA P0-1)
- **P0-4 Decide `plugin-*` routing.** Today `payloadKind→"dashboard"→viewDashboard→hydratePluginPage` (`generate-dashboards.py:8106`); the plan moves plugin reference into the **shell** Discover (`__openPlugin`). Pick one and update `route()`: recommend **`#/plugin-<name>` becomes a shell route** → `__openPlugin` (rich reference), with "Configure variables →" still deep-linking to the dashboard editor. (tester-QA P0-2)
- **P0-5 Gate the destination, not mere presence.** Gate 51's route check only asserts a route *string exists* in `DASH_SECTIONS_TEXT` (`check-shell-router.mjs:108`) — a route can be present yet resolve to the wrong section/sub-tab and stay green. Add a per-route **(section, sub-tab)** expectation table as the gated contract. (tester-QA P0-6)
- **P0-6 Add structural coverage for the sub-nav + chrome-hide** (the parts deferred to "eyeball"). New `check-shell-subnav-render.mjs` (DOM-stub, house style, no new dep — mirrors the render gates) OR assertions in `check-shell-router.mjs`: assert a `role="tablist"` shell sub-nav with roving `tabindex` exists, and that `#dash-root .cat-bar, #dash-root .tab-bar { display:none }` is present. Without this, a keyboard-dead nav or a dropped chrome-hide ships green. (tester-QA P0-4)
- **P0-7 Specify the must-fail mutations exactly.** NAV-rename must-fail must rename one of the **5 asserted** ids (a non-asserted-field mutation false-greens the meta-test). Phantom-route cross-check must regex-extract `data-tab="…"` from the `#dash-root` body and assert `DASH_SECTIONS − keys(DASH_TAB_ALIAS) ⊆ tabSet`. (tester-QA P0-5/A-G1)
- **P0-8 `esc()` on every new Discover field** — `__openPlugin` already escapes (`_index_dashboard_template.py:1076-1110`); hold the line on any newly-surfaced field. Add a grep/regex check. (security G-S1, tester-QA P0-7)
- **P0-9 Split into two PRs.** **Slice A** = NAV rename + full route-alias table (incl. P0-1) + Gate 51 update + must-fail — low-risk, reversible, gate-covered, *chromes stay visible*. **Slice B** = chrome-hide CSS + shell sub-nav + a11y roving + served banner + Discover merge. Clean revert boundary; A can land alone. (PM P0)
- **P0-10 Deep-link active-state must be visible + asserted.** A legacy `#/heimdall` landing in Observe→Perimeter alerts must show the sub-nav item `aria-selected` + a `Observe › Perimeter alerts` breadcrumb; extend Gate/verification to assert the active-state, not just that content loads. (UX P0-3)
- **P0-11 Banner command string + two labels.** Banner uses **`rc dashboard`** (fallback `python3 scripts/serve-dashboards.py`) — matches every existing empty-state; drop the plan's `bash scripts/open-dashboard.sh`. Sub-nav: **"Perimeter alerts"** (not "Perimeter"); **never ship bare "Posture"** (use tooltip or "Posture (autonomy)"). (UX P0-1/P0-2/P0-4)
- **P0-12 DoD asserts ALL legacy routes round-trip** (the full `DASH_SECTIONS` set + shell aliases, not a sample of 8) and **update human-readable old-name references** (docs / SessionStart capability banner prose) in the same change — aliases fix URLs, not prose pointers. (PM P0)

### P1 — should-fix

- **Adopt the UX label/tooltip set** (UX): Discover=Plugins/Specialists/Use cases; Configure=Posture (autonomy)/Web access/**Review simulator**/Plugin variables; Observe=Run feed/**Perimeter alerts**/Security log/**Plugin lineage**/**Session state**/Review log; Learn=Concepts/Commands/**Decision trees**/Pipeline/Architecture/Install/About. Keep **no Norse name as a label** (parenthetical flavor only) — the plan's single biggest legibility win.
- **Discover↔Learn rule** (UX): *Discover = "what can I get & which do I pick" (catalog/roster/per-agent reference you act on); Learn = "how it works & how to use it" (concepts/playbooks/install/architecture you read).* Per-plugin best-practices → Discover (attached to a plugin).
- **Configure↔Observe rule** (UX): *Configure = change/try before it's real (write/simulate); Observe = read-only record of what happened.* Mirror the "Preview a review" / "Review log" tooltips ("now / dry-run / nothing saved" vs "saved / real / already happened").
- **Distinguish two Observe empty-states** (UX): "needs served dashboard" (banner) vs "served but no data yet" (quiet) — the second must not read as broken.
- Re-label chrome-hide+sub-nav+a11y as the **real bulk-of-work** (~1.5–2.5d, the no-browser-risk core), not a scaffold sub-bullet; add explicit **a11y acceptance criteria** (Tab-into-tablist-once, arrow roving, `aria-selected` tracks). (PM)
- Resolve sub-tab **active-state** for `nidhoggr`/`sleipnir`/`settings`/`install`/`overview` (each legacy route needs one defined (section, sub-tab)); enumerate the exact `expectedDashboardRoutes`. (tester-QA, deep-researcher)
- Discover git-dates must reuse the **identical** `Last updated</span> <code>…</code>` markup so `_strip_ts` (`generate-index-dashboard.py:763`) determinism holds; no `set`/`dict`-without-sort in new aggregations. (ops G-O4, tester-QA)
- Fix the **stale "Gate 70" comment** inside `check-shell-router.mjs:17,21` during the Phase-2 edit. (deep-researcher P1-1)
- Add **gjallarhorn-link** (`generate-dashboards.py:5987`, `href="#/heimdall"`) to the deep-link verification list. (deep-researcher P1-2)
- Keep the **phantom-route cross-check mandatory** (not deprioritized next to the optional byte-budget gate). (deep-researcher P1-3)
- Note that doc route-pointers (`check-runtime-state.md:23-25`, `CLAUDE.md:454`) are **preserved by the alias table** — no edit, don't flag as breaks. (deep-researcher P1-4)
- Add to Verification: ⌘K/quick-actions/featured-combos route canonically; single-source "I want to…" table (rendered once, Home links); served-banner negative case (silent on localhost AND absent on Home/Discover/Learn); "regenerate index.html before running Gate 51 locally". (PM, tester-QA)
- Confirm the **byte-budget gate (G-O6) is out of scope** here; disambiguate **which CLAUDE.md** (plugin) gets the milestone; confirm `.repo-layout.json` allows `index.html`. (PM, ops)

### Net changes to the build plan (post-review)
1. The route-alias table now covers **both** dashboard sub-routes **and** the 4 legacy shell top-level routes + the ~15 internal `href` sites + `quick_actions` (P0-1) — this was the plan's biggest blind spot.
2. The served banner reads a **new `window.__dashApp` served flag** (P0-2), not `hostname` and not a new probe.
3. `plugin-*` becomes a **shell** route → `__openPlugin` (P0-4).
4. Gate work expands: destination-asserting route table, exact must-fail mutations, a sub-nav/chrome-hide structural gate, esc() check (P0-5/6/7/8).
5. Ship as **two PRs** (rename+aliases, then chrome-collapse+sub-nav) (P0-9).
6. Adopt the UX labels/tooltips/rules + `rc dashboard` banner copy (P0-11, P1s).

