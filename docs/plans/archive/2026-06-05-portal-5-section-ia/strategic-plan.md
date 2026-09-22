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

## Panel 1 gap-fill (architect · security · ops/gates · devil's-advocate)

The 5 sections (Home/Discover/Configure/Observe/Learn) are **fixed by the product owner**; the panel's job was to close gaps *within* that decision. Verdicts:

### Gaps found → resolutions adopted

- **G-A1 Phantom routes (architect, high).** `nidhoggr` and `sleipnir` are **not tabs** — `sleipnir` is the "stables" banner inside the **Run feed (`activity`)** tab; `nidhoggr` ("debt watch") is a card inside the **Heimdall** tab. Both are in `DASH_SECTIONS`, so `#/nidhoggr`/`#/sleipnir` currently `activate()`-fall-back to **overview** (silent). **Resolution:** alias `#/nidhoggr → heimdall`, `#/sleipnir → activity` in `DASH_TAB_ALIAS` (do **not** invent fake tabs); add a gate cross-checking that every non-aliased `DASH_SECTIONS` id is a real `validTabs` tab.
- **G-A2 Two-chromes is cheap, not Tier-2-risky (architect, decisive).** The dashboard CSS is already scoped under `#dash-root` and the **standalone** copy is *not* wrapped in `#dash-root`. So a single **shell-side** CSS rule `#dash-root .cat-bar, #dash-root .tab-bar { display:none }` hides the internal chrome in the **folded copy only** — **no `generate-dashboards.py` edit, no consumer-artifact risk.** This collapses the prior "Tier 2 = edit shipped generator" into a shell-only change. **Resolution:** adopt option (b) (scoped CSS hide) + drive tabs from a shell sub-nav calling `window.__dashApp.show()` (reuse the existing `navChildren()` accordion). Tier 2 effectively merges into Tier 1.
- **G-A3 a11y regression (architect, medium).** Hiding `.tab-bar` drops the dashboard's WAI-ARIA roving-tabindex keyboard nav. **Resolution:** the shell sub-nav must implement `role=tablist` + arrow-key roving so the folded view keeps keyboard parity; standalone keeps its own bar (scoped CSS guarantees it).
- **G-A4 Pipeline & Overview placement (architect, medium).** `pipeline` is one **interactive** tab (`syncPipelineTab()`), can't be split Configure/Learn. **Resolution:** keep `pipeline` as a single tab under **Learn**; Configure *links* to it (no copy). `overview` stays the dashboard landing + `DASH_TAB_ALIAS["dashboard"]="overview"` target; its content is **reachable** from Learn, not duplicated.
- **G-S1 Escape new Discover fields (security, the one real XSS vector).** Discover's richer per-plugin reference renders via shell `innerHTML`. **Resolution:** every newly-surfaced field (scenarios/quickstart/audience/works-with/skills/hooks/rules/templates/best-practices) MUST go through `esc()`. Build-plan acceptance criterion.
- **G-S2 Keep `__dashApp.show()` as the single drive seam (security + architect).** If the shell drives tabs by any other mechanism, the sub-app's per-card served-probe + empty-state loaders may not fire → hard error instead of graceful degradation on Pages. **Resolution:** `show()` stays the only entry.
- **G-D1 Static-vs-served audience (devil's-advocate, high).** Observe + live Configure tabs are empty on GitHub Pages (need local `/__*`). Giving them top billing on the consumer's static surface is poor IA. **Resolution (within 5 sections):** Observe + the live half of Configure render a single **"run the served dashboard to see live data"** banner at the section top on static hosts (the dashboard tabs already degrade per-card); on `127.0.0.1` the banner is silent. Detected via the existing served signal — **no new shell probe, no CORS** (security invariant).
- **G-D2 "I want to…" single component (devil's-advocate).** **Resolution:** the use-case table is rendered once in Discover; Home *links* to it (`#/discover`), never re-renders it.
- **G-D3 Discover overload (devil's-advocate + architect).** Marketplace + Team + 295-agent reference + ~1000-row table in one section. **Resolution:** Discover gets an internal sub-nav (**Plugins · Specialists · Use cases**); the rich per-plugin reference stays behind a plugin click (`__openPlugin`), the use-case table keeps its existing `.slice(0,400)` + scroll cap.
- **G-O1 Gate naming correction (ops).** The shell-router fixture is **Gate 51** in `audit-gates.sh` (`--check 70` / "Gate 70" is the unrelated Codex-trust-hooks gate). The build plan targets **Gate 51 / `check-shell-router.mjs`**.
- **G-O2 Gate 51 hard-codes the old 6 NAV ids + `resolveNavActive`→"dashboard"** → will fail on rename. **Resolution:** update to the 5 new ids; add a **NAV-rename must-fail** fixture (the DASH_SECTIONS must-fail half doesn't cover a dropped section).
- **G-O3 DASH_SECTIONS deep-link contract under-tested** (13 of 20 routes). **Resolution:** expand `expectedDashboardRoutes` to the full back-compat set + assert the new `DASH_TAB_ALIAS` entries — make the alias table the gated contract.
- **G-O4 `_strip_ts` git-date strip is markup-shape-coupled.** Discover reference rendering git dates in any new markup → Gate 97 false-fails on shallow-clone CI. **Resolution:** reuse the exact existing `Last updated</span> <code>…</code>` markup, or extend `_strip_ts`; audit any new aggregation for `set`/`dict`-without-sort (determinism).
- **G-O5 Render-gate `function activate(` sentinel + longest-script fallback** is a footgun if a future edit renames/moves `activate`. **Resolution:** keep `function activate(` as a stable anchor in the folded sub-app; the chrome-hide is CSS-only so it isn't threatened now.
- **G-O6 No page-weight gate** (index.html all-inlined, grows with 64 plugins). **Resolution:** add an optional byte-budget gate (bidirectional fixture) — flagged P1, not blocking.

### Dissent recorded (overridden by product-owner decision)
- Devil's-advocate argued for **keeping the old names** (Marketplace/Team) and an **audience-segmented 3–4 section** IA, and for **not** promoting empty-on-static Observe. The 5 named sections are fixed; we honor the *spirit* of the critique via G-D1 (served banner) and G-D3 (Discover sub-nav) rather than changing the section set.

**Net effect on phasing:** G-A2 collapses the feared "Tier 2 = edit the shipped generator" into a **shell-only CSS+sub-nav change**, so the whole reorg is now **one shell-layer effort** (no `generate-dashboards.py` edit, no consumer-artifact risk) — with the gate updates from G-O2/O3 and the escaping/served-banner closes. The tactical build plan ([`build-plan.md`](build-plan.md)) sequences it.

