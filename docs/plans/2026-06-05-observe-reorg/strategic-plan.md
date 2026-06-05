# Strategic plan — Observe category reorganization

**Date:** 2026-06-05 · **Status:** strategic (what/why) · **Route:** local (repo-internal, no web research) · **Follows:** the 5-section IA (Slices A+B, merged)

## Why

The **Observe** section (the dashboard's former "Look back" category, now a shell section with a sub-nav) is overloaded and conflates two different jobs:

1. **Heimdall ("Perimeter alerts") is doing two jobs.** Only its *alarm* card is perimeter security (recent hook denials/warnings, tiered). The other five cards are **marketplace/repo health**: version-drift (plugins behind required core), Níðhöggr debt-watch (stale plugins, ungated hooks, superseded decisions, TODO/FIXME), hook-coverage, CI, knowledge-health (`hm-drift-h`, `hm-debt-h`, `hm-hooks-h`, `hm-ci-h`, `hm-kh-h` in `generate-dashboards.py`).
2. **Víðarr ("Security log") overlaps Heimdall.** `_read_vidarr_events` reads `hook-events.jsonl` **deny-only** + `posture-events.jsonl`; Heimdall's `_read_hook_events` reads the same hook stream (all tiers). Víðarr's denies are a *subset* of Heimdall's; it uniquely adds posture-change history.
3. **Norns (lineage) and Níðhöggr (debt) are maintainer-facing** — git/marketplace-derived (`_read_norns`, `_read_nidhoggr` read git log + plugin.json + proposals), about the *plugins*, not the user's runs.

## Product-owner decisions (FIXED)

| Observe item | Decision |
|---|---|
| **Run feed** (activity + Sleipnir stables) | **Keep** as-is |
| **Perimeter alerts** (Heimdall *alarm*) + **Security log** (Víðarr) | **MERGE** → one **"Guardrails & security"** tab, with a view toggle: *live activity* (all tiers) ↔ *security audit* (deny-only + posture changes) |
| **Review log** (Sága — tribunal verdicts) | **MOVE** → **Configure**, rendered **below the command-review tribunal** settings |
| **Session state** (Mímir) | **Keep**, relabel **"Session"** |
| **Plugin lineage** (Norns) | **MOVE** → **Discover** (the per-plugin page) |
| **Marketplace-health cards** (version-drift, Níðhöggr debt, hook-coverage, CI, knowledge-health) | **SPLIT** out of Perimeter alerts |
| **Marketplace health** home | New **Observe sub-tab** |

### Resulting structure
- **Observe = 4 tabs:** Run feed · Guardrails & security · Session · **Marketplace health** (the split-out maintainer cards).
- **Relocations:** Review log (Sága) → Configure (below tribunal); Plugin lineage (Norns) → Discover (per-plugin).

## Hard constraints (build plan MUST respect)

- **This cuts into `scripts/generate-dashboards.py` — the SHIPPED plugin artifact** (`dashboard.html`), unlike Slices A/B (shell-only). The standalone consumer dashboard changes too → **version bump + migration note** required.
- **Render gates extract functions by text from `index.html`** (which inlines the dashboard JS verbatim): `check-heimdall-render.mjs`, `check-vidarr-render.mjs`, `check-nidhoggr-render.mjs`, `check-sleipnir-render.mjs`, `check-norns-render.mjs`, `check-mimir-render.mjs`, plus `check-dashboard-roundtrip.mjs` and Gate 51 (`check-shell-router.mjs`). Merging Heimdall+Víðarr / splitting Marketplace-health / moving Sága+Norns must keep these green — either the render functions survive (renamed/regrouped) or the gates move with them. The gates anchor on `function activate(` + per-tab render fn names.
- **Server `/__*` endpoints + the parity gate** (`check-dashboard-server-parity.py`): the data sources are unchanged (same readers `_read_hook_events`/`_read_vidarr_events`/`_read_nidhoggr`/`_read_norns`/`_read_mimir`/`_read_saga`/`_read_sleipnir`); this is a **UI regrouping**, so endpoints SHOULD stay byte-identical in both `serve-dashboards.py` copies. Confirm no endpoint rename is needed.
- **Deep-link back-compat:** `#/heimdall #/vidarr #/saga #/norns #/nidhoggr #/mimir #/activity #/sleipnir` must still resolve to *some* coherent destination (committed bookmarks, the in-fragment `gjallarhorn-link href="#/heimdall"`, SessionStart capability banner, docs `check-runtime-state.md`/`CLAUDE.md` pointers). After the merge/move, the route→(section, sub-tab) map changes: `vidarr`→Guardrails(audit view), `saga`→Configure, `norns`→Discover, `nidhoggr`→Marketplace-health, etc. Update `DASH_OWNER` + `SECTION_TABS` + Gate 51.
- **Served vs static:** the merged/moved live tabs still fetch `/__*`; preserve the per-card empty states + the Slice-B served banner. No new CORS/ACAO.
- **Freshness:** Gate 97 (`index.html`) + Gate 13 (`dashboard.html`) must stay deterministic; the git-derived readers stay server-side (never inlined) — do not regress that.

## Open questions (panel to gap-analyze + close)

1. **Heimdall+Víðarr merge mechanics.** Two render fns + two endpoints (`/__heimdall`, `/__vidarr`) → one tab with a toggle. Does the merged tab keep both render fns (so both render gates still extract them) under one panel with a view switch, or is one rewritten? What's the least-risk path that keeps `check-heimdall-render.mjs` + `check-vidarr-render.mjs` green?
2. **Marketplace-health split.** The 5 health cards live inside the Heimdall tab template/JS today. Extracting them into a new tab: new render fns? new `/__*`? (drift/debt/kh already have endpoints: `/__heimdall` versionDrift, `/__nidhoggr`, `/__knowledge-health`.) How do `check-nidhoggr-render.mjs` + the drift/kh assertions move?
3. **Sága → Configure.** Sága is a dashboard tab (`/__saga`). Configure is a shell section that shows the dashboard host for its dashboard tabs (settings/web-access/simulator) but a shell view (presets) for `#/configure`. "Below the tribunal" — the tribunal toggles live in the dashboard **Settings** tab (`command_review`). So does Sága render *inside* the Settings tab below the command-review block (same dashboard tab), or as its own Configure sub-tab adjacent to it? Which keeps `check-saga`/roundtrip simplest?
4. **Norns → Discover.** Norns reads `/__norns?plugin=<name>`. Discover's per-plugin view is the shell `__openPlugin` (static reference from JSON) — it has no served fetch today. Embedding lineage means either (a) the shell `__openPlugin` adds a `/__norns` fetch (new shell fetch — served-only, empty on static), or (b) Discover's per-plugin deep-links into the dashboard Norns tab. Which, and how does `check-norns-render.mjs` follow?
5. **Route/alias + Gate 51 update.** New `DASH_OWNER`/`SECTION_TABS`/`SECTION_ALIAS` for the merged + moved routes; the destination-asserting Gate 51 + must-fail.
6. **Phasing / slices.** Where's the cut line? (e.g. Slice 1 = Observe sub-nav relabel + Marketplace-health split [lower risk]; Slice 2 = Heimdall+Víðarr merge + Sága/Norns moves [higher risk, touches render gates]).
7. **Risks:** render-gate breakage, standalone-vs-folded drift, version-bump/migration, freshness determinism, no-browser visual-verification gap, and the consumer-relevance question (Marketplace-health/Norns are near-empty on a consumer's installed dashboard — is the served banner enough, or do they need their own "this is about the marketplace, not your project" empty state?).

---

## Panel 1 gap-fill
_(filled in Phase 2)_

## P0 / P1 recommendations (Panel 2 cold-review)
_(appended in Phase 5)_
