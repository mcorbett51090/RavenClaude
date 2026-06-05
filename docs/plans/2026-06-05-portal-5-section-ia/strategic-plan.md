# Strategic plan — RavenClaude portal (index.html) → 5-section task-based IA

**Date:** 2026-06-05 · **Status:** strategic (what/why) · **Route:** local (medium scope, repo-internal, no web research)

## Why

`index.html` stacks **two navigation systems for one product**: a shell sidebar (Home, Team, Marketplace, Dashboard, Configuration, Resources) **plus** a nested "Dashboard" sub-app with its own 2-tier nav (5 categories × 17 tabs). The same job lives in both layers:

- **Posture** in both shell `Configuration` AND `Dashboard→Set up→Settings`.
- **Activity** in both `Home→Recent activity` AND `Dashboard→Look back→Run feed`.
- **Learn/reference** split across shell `Resources` AND `Dashboard→Learn`.
- **Specialists** in `Team` + Marketplace detail + ⌘K.

Reaching "what tripped a guardrail" = sidebar→Dashboard→Look back→Perimeter alerts (3 clicks + an app-switch).

## Target IA (product-owner decision — fixed)

Sidebar = exactly **five** sections, each owning one job:

1. **Home** — hero + onboarding checklist + "I want to…" entry + featured combos. (No longer hosts recent activity.)
2. **Discover** — 64-plugin catalog + "I want to…" use-case table + rich per-plugin REFERENCE (agents w/ scenarios/quickstart/audience/works-with, skills, hooks, rules, templates, best-practices) + cross-plugin specialist roster. (= Marketplace + Team + reference half of Dashboard→Plugins.)
3. **Configure** — live comfort-posture editor (per-layer, presets as entry) + web-access + per-plugin variables (→`/__save`) + command-review tribunal + "preview a review" (simulator). (= shell Configuration + Dashboard→Set up minus Overview/Pipeline.)
4. **Observe** — run feed, perimeter alerts (Heimdall), security log (Víðarr), lineage (Norns), session (Mímir), review log (Sága), debt watch (Níðhöggr). (= Dashboard→Look back, promoted.)
5. **Learn** — concepts, command playbooks, guidance/decision-trees (SVG), pipeline explainer, architecture prose, install wizards (Bifröst, Copilot), README/changelog. (= shell Resources + Dashboard→Learn + Install&help + Overview/Pipeline.)

## Hard constraints (build plan MUST respect)

- **`plugins/ravenclaude-core/dashboard.html` is a SHIPPED plugin artifact** (`scripts/generate-dashboards.py`), served standalone to CONSUMERS by the bundled `serve-dashboards.py` (`/dashboard`). It has its own cat-bar/tab-bar. `index.html` folds the SAME content via `render_fragment()` (scoped `#dash-root`, IIFE, `window.__dashApp.show(tab)`). Reorg must keep the standalone consumer dashboard working AND avoid drift (single generator source).
- **Deep-link back-compat:** `#/heimdall #/vidarr #/norns #/nidhoggr #/bifrost #/mimir #/sleipnir #/saga #/activity #/learn #/pipeline #/comfort-posture #/dashboard #/plugin-<name>` must still resolve (committed bookmarks, SessionStart capability banners, gjallarhorn-link).
- **Served vs static:** live `/__*` tabs degrade to empty states on GitHub Pages; no new CORS/ACAO (DNS-rebinding defense).
- **Gates:** Gate 70 (`check-shell-router.mjs`), render gates (extract fns from index.html), Gate 97 freshness, full `audit-gates.sh` (415+), ruff + prettier + layout — all stay green.
- **Two chromes:** folded dashboard shows BOTH shell sidebar AND dashboard cat-bar/tab-bar. Collapsing to one chrome edits the shipped generator + render gates (higher risk) → phasing matters.

## Open questions (panel to gap-analyze + close)

1. Exact mapping of all 17 dashboard tabs + 6 shell views → 5 sections, nothing orphaned.
2. Drive dashboard internal tabs from new shell sections without two navs, while keeping STANDALONE consumer nav intact.
3. Where Dashboard→Overview and Dashboard→Pipeline land.
4. Deep-link/route-alias table: every legacy `#/...` → new section + sub-tab.
5. ⌘K palette + quick-actions + featured-combos route updates.
6. Phasing: Tier 1 (shell-only IA, low risk) vs Tier 2 (collapse dashboard chrome, touches generator). Cut line + gate updates per tier.
7. Risks: page weight, freshness determinism, standalone-vs-folded drift, no-browser visual-verification gap.

---

## Panel 1 gap-fill (filled after review)

_(to be completed in Phase 2)_
