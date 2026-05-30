# Dashboard UX — tactical build plan (2026-05-30)

> **Inputs:** [`ux-handoff-repo-inventory.md`](./ux-handoff-repo-inventory.md) (component inventory) + [`ux-dashboard-analysis.md`](./ux-dashboard-analysis.md) (UX audit + P0/P1/P2). This doc is the **how** (file-level changes, gate impact, sequencing). The UX audit is the **what/why**.
> **Goal:** make the dashboard a complete, interactive, marketplace-wide control surface that (a) communicates the repo's purpose + contents, (b) makes commands clickable + executing with tooltips showing exactly what runs, (c) upgrades static guidance to interactive — **consolidating and adding content, removing none**, and **preserving the security envelope** (allow-list-only `/__run`, fixed argv, no shell, CSRF, 127.0.0.1, static-host parity).

## Load-bearing facts (verified this session)

- `/__run` executes only `ALLOWED_ACTIONS = {"install","update","status"}` — fixed argv, no shell, CSRF-guarded, 127.0.0.1-bound, served-only (`serve-dashboards.py:83, _handle_run :612`).
- A browser **cannot** launch a Claude Code slash command (no IPC) — the 4 shipped commands are in-Claude prompts. "Execute on click" is real only for shell-shaped actions.
- The dashboard renders diagrams as **build-time pre-rendered themed SVGs** (`render-concepts.py` via mermaid-cli), **NOT** client-side Mermaid. **Correction to the UX audit §3:** inline decision-tree diagrams in Guidance must be **pre-rendered to SVG at build time**, the same mechanism as Learn concepts — not a client-side renderer (the dashboard ships no CDN/JS-mermaid dependency, and that constraint must hold).
- Two server copies exist (root `scripts/serve-dashboards.py` + bundled `plugins/ravenclaude-core/scripts/serve-dashboards.py`) and must stay endpoint-parity-clean (Gate 32). Any `/__run` change lands in BOTH.

## Phases

### Phase 1 — Overview tab (P0-3)
- New `_render_overview_tab()` in `generate-dashboards.py`; register **first** in the tab bar; move `active` off Settings onto Overview; add `overview_html=` to `render_dashboard()` + the `_PAGE_TEMPLATE` slot + a `<section data-tab="overview">` panel.
- Content (all **build-time, generator-discovered** — House Rule 1): "What this is" paragraph (distinguish dashboard vs repo-guide); generator-discovered inventory (N plugins via `PLUGINS_DIR`, active-plugin agent/skill/hook/command counts); 4 "big system" deep-link cards (posture→Settings, pipeline→Pipeline, tribunal→Review log, bridge→Install); a 3-step "start here" checklist; a served/static banner reusing the `HEAD /__save` probe + `live` badge idiom.
- **Gate impact:** freshness (regenerate dashboard.html), round-trip (Gate 35 — Overview adds no posture keys, unaffected), parity (no server change).

### Phase 2 — Commands clickable + execute + tooltips (P0-1) + `/__run` widening (P0-2)
- **Server (both copies):** add audited fixed-argv actions to `ALLOWED_ACTIONS`: `open-dashboard` → `bash scripts/open-dashboard.sh`; `set-posture` → the posture-apply already invoked by `/__save`. Each: closed-set name validation, no caller args, no shell, CSRF + bind unchanged, high-blast excluded. Document each with a one-line justification beside `ALLOWED_ACTIONS`.
- **Generator:** rewrite `_render_command_card()` to classify each discovered command into Class A (shell-executable → ▶ Run via `/__run`, reuse Install-tab `data-run-action` mechanic + `HEAD /__run` probe + `run-result` panel), Class B (slash-only → Copy + "Runs inside Claude Code" pill), Class C (both). **Every card shows the exact thing it runs** (literal argv for A/C, literal `/name` for B) as an always-visible "what this runs" line **plus** a `title=`/`aria-describedby` tooltip (not hover-only — touch/a11y). Copy never removed.
- **Gate impact:** parity (Gate 32 — both server copies get the actions), freshness, audit-gates (the parity + round-trip fixtures). **New gate consideration:** a small assertion that every `ALLOWED_ACTIONS` entry maps to a fixed argv (no interpolation) — add to `audit-gates.sh` if feasible.

### Phase 3 — Interactive Guidance (P0-4)
- Pre-render each discovered decision tree's `mermaid` block to a themed static SVG at build time (extend/`reuse render-concepts.py`'s normalize pipeline; mermaid-cli is already a build dep). Embed the SVG in a collapsed `<details>` under each Guidance tree item; keep the "open source file" link as secondary.
- Best-practice items: build-time **preview-on-click** disclosure (first heading + first paragraph / Status+rationale), reusing `_best_practices_inventory()`'s parse. Full doc one click away.
- Static-safe (build-time embed) — works on GitHub Pages.
- **Gate impact:** freshness; if a new SVG-manifest/`--check` is added (like concepts), wire it into audit-gates; prettier on any new JSON.

### Phase 4 — P1 consolidation (cross-linking, never removing)
- One-line "what this tab does" headers (Settings, Review log, Activity); relabel "Test a command" → "Preview a command's review"; cross-link Settings↔Pipeline, Review-log↔Activity, Learn↔Guidance with division-of-labor text; shared served/static banner component.
- **Gate impact:** freshness only.

## Sequencing & PR
- One feature branch `feat/dashboard-ux`, phases committed in order, draft PR early, drive CI green.
- Per phase: regenerate dashboard.html, `node --check` the embedded JS, run Gate 32 (parity) + Gate 35 (round-trip) + freshness + prettier; full `audit-gates.sh` before marking ready.
- ravenclaude-core version: one minor bump for the whole effort (already-unreleased bumps compound within a PR).

## Open questions for the expert review
1. **Mermaid pre-render scale:** ~32 decision trees across 13 plugins (more after the in-flight power-platform/salesforce build-out) → 32+ SVGs to pre-render + commit. Is build-time SVG pre-render the right call, or embed raw Mermaid + a one-time bundled offline renderer? (Plan assumes pre-render for dependency/CDN-free consistency.)
2. **`/__run` widening surface:** are `open-dashboard` + `set-posture` the right two, or should the first cut ship Commands-as-buttons with ONLY the existing 3 actions (install/update/status) wired and slash-commands as Class B — deferring new actions to a second PR to keep the security review tight?
3. **Overview-as-default:** does changing the default tab risk muscle-memory disruption for existing users who expect Settings first? (Plan says yes-change; low risk, high first-run value.)
4. **Gate for `/__run` allow-list integrity:** worth a dedicated audit-gate asserting no action maps to interpolated/shell argv?
5. Anything the plan missed at the implementation level (parity drift, freshness, a11y of tooltips, static-host degradation of the new Run buttons).
