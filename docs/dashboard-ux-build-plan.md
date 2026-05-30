# Dashboard UX — tactical build plan (v2, 2026-05-30)

> **v2** folds in [`dashboard-ux-gap-analysis.md`](./dashboard-ux-gap-analysis.md) (cold-review verdict: *sound-with-fixes*). The v1 premises that were **factually wrong** are corrected here and called out inline as **[gap-fix]**.
> **Inputs:** [`ux-handoff-repo-inventory.md`](./ux-handoff-repo-inventory.md) + [`ux-dashboard-analysis.md`](./ux-dashboard-analysis.md). This doc is the **how**; the UX audit is the **what/why**; the gap analysis is the **adversarial check**.
> **Goal:** make the dashboard a complete, interactive, marketplace-wide control surface that (a) communicates the repo's purpose + contents, (b) makes commands clickable + executing with tooltips showing exactly what runs, (c) upgrades static guidance to interactive — **consolidating and adding content, removing none**, **preserving the security envelope**, and **degrading gracefully on every host**.

## Load-bearing facts (verified against code this session — cite file:line)

- `/__run` executes only `ALLOWED_ACTIONS = {"install","update","status"}` — fixed argv, no shell, CSRF-guarded, `127.0.0.1`-bound, served-only (`scripts/serve-dashboards.py:83`, `_handle_run :612`).
- **Exact argv (an implementer must match this for the "what this runs" line):** `argv = ["bash", RAVENCLAUDE_SCRIPT, action]`, and `--project <root>` is appended for **`install`/`status` only — NOT `update`** (`scripts/serve-dashboards.py:635-637`). So the literal-argv line differs per action; do not copy the install pattern onto `update`.
- **[gap-fix] `/__run` is INTENTIONALLY EXCLUDED from the two-server parity contract** (`scripts/check-dashboard-server-parity.py` `INTENTIONALLY_EXCLUDED = {"/__run"}`). The **bundled/consumer** server (`plugins/ravenclaude-core/scripts/serve-dashboards.py`) has **no `/__run`, no `ALLOWED_ACTIONS`, and does not answer `HEAD /__run`**. Consequence: **Class-A "Run" buttons only work when the page is served by the ROOT dev server**; under a consumer's `rc dashboard` (bundled server) or any static host, the `HEAD /__run` probe fails and the button **disables with help text** — exactly like the existing Install-tab buttons already do. This must be stated, not hidden.
- A browser **cannot** launch a Claude Code slash command (no IPC). The 4 shipped commands are in-Claude prompts → Class B (Copy + "runs inside Claude Code").
- **[gap-fix] Inline Mermaid is NOT a `render-concepts.py` reuse.** `render-concepts.py` iterates `concepts.load_concepts()` against a strict concept schema only; it has **no arbitrary-Mermaid path**, and `_decision_trees_inventory()` does **not** extract the mermaid block. Real scale is **~75 mermaid fences across 38+ tree sections** (now larger after the PP/SF build-out). Inline-SVG pre-render is **net-new infra** (own inventory + manifest + `--check` gate + mermaid-cli in CI) → **out of PR-1**.
- The committed `dashboard.html` is freshness-gated (`generate-dashboards.py --check`, Gate 13) and round-trip-gated (Gate 35, `check-dashboard-roundtrip.mjs` extracts `emitYaml`/`applyGuardrailConfig` by string-matching — brittle to edits near those functions). Parity is Gate 32.

## Phasing — three PRs, security delta front-loaded to zero **[gap-fix]**

### PR-1 (this plan) — zero security delta, no new infra
1. **Overview tab (default).** New `_render_overview_tab()`, registered first; move `active` off Settings. **[gap-fix] The default-tab move couples TWO sites** — the tab-bar `<button>` (`aria-selected`) **and** the `<section class="tab-panel">` (`active`). Move both together or the active tab and the rendered panel disagree (Gate 13 freshness will flag it only as a generic diff, not the real cause). Build-time, generator-discovered (House Rule 1): "what this is" (dashboard vs repo-guide), inventory (`PLUGINS_DIR` glob counts), 4 big-system deep-link cards, 3-step "start here", and the served/static banner (reuse `HEAD /__save` probe). Static-safe.
2. **Commands → clickable buttons + mandatory tooltips, over the EXISTING 3 actions only.** Rewrite `_render_command_card()`:
   - **Class A** (a command whose effect maps to an *existing* `install`/`update`/`status` action): **▶ Run** reusing the Install-tab `data-run-action` mechanic + `HEAD /__run` probe + `run-result` panel. **[gap-fix] No new `ALLOWED_ACTIONS`** — security delta = 0.
   - **Class B** (slash commands — all 4 shipped): **Copy** (primary) + a "Runs inside Claude Code" pill. **No fake execution.**
   - **Every card**: an always-visible "what this runs" line (literal argv for A, literal `/name` for B) **plus** a `title=`/`aria-describedby` tooltip — **not hover-only** (touch + a11y). Copy never removed.
   - **[gap-fix] Honesty line + literal disabled copy**: Run buttons execute only when served by the **root dev server**. The disabled-state help text must read **"Run is available only when served by the root dev server"** — **NOT** "run `serve-dashboards.py`": a consumer running `rc dashboard` *is* already running `serve-dashboards.py` (the bundled, no-`/__run` copy), so the Install-tab's existing string is actively misleading in this context and must not be reused verbatim.
3. **Guidance — best-practice text preview-on-click** (first heading + first paragraph / Status+rationale). **[gap-fix] This is net-new parse code, NOT free reuse:** `_best_practices_inventory()` (`generate-dashboards.py:791-818`) returns only `{owner, title, status, path}` — it does **not** extract any body text. PR-1 must **extend** it with a new `preview` field capturing the first non-heading paragraph, then embed that at build time. (Same "is this actually reuse or net-new?" rigor the v2 fix applied to render-concepts.) **Decision-tree Mermaid inline-render stays deferred to PR-3** (infra). Keep the "open source file" links.
4. **P1 consolidation** (additive): one-line "what this tab does" headers (Settings/Review-log/Activity); relabel "Test a command" → "Preview a command's review"; cross-link Settings↔Pipeline, Review-log↔Activity, Learn↔Guidance; shared served/static banner.

### PR-2 (separate, security-reviewed) — `/__run` allow-list widening
- Only if a genuinely-safe, fixed-argv, **non-destructive** action is justified. **[gap-fix] `open-dashboard` is rejected** — `scripts/open-dashboard.sh` `pkill -f "serve-dashboards.py"` (`:25`) then `nohup … & disown` (`:29-30`): it kills the serving process and detaches a new one (process-spawning, worse than read-only `status`). `set-posture`-apply already rides `/__save`'s auto-apply, so a button adds an entry point, not capability — candidate, but reviewed in isolation.
- Ship the **argv-integrity audit-gate** in the SAME PR: assert every `ALLOWED_ACTIONS` entry maps to a fixed argv with no interpolation/shell. Lands in BOTH server copies only if `/__run` is ever added to the bundled server (today it isn't — document why).

### PR-3 (separate, infra) — inline decision-tree SVGs in Guidance
- New tree-Mermaid inventory + themed-SVG pre-render (generalize `render-concepts.py`'s normalize step or a sibling) + a source-hash manifest + `--check` gate, mermaid-cli in CI. Sized on its own.

## Gate impact (per PR-1 change)
- Overview/Commands/Guidance/P1 → regenerate `dashboard.html`; `node --check` the embedded JS; **freshness** (Gate 13), **parity** (Gate 32 — no server change in PR-1, so unaffected), prettier, full `audit-gates.sh` before ready.
- **[gap-fix] Gate 35 (round-trip) — the largest-`<script>` hazard.** `check-dashboard-roundtrip.mjs:21` extracts `app = the single LONGEST <script>` block, then string-matches `emitYaml`/`applyGuardrailConfig` inside it. Two ways PR-1 breaks it: (a) inlining Overview/Commands JS as a **new top-level `<script>`** that becomes larger than the posture app → `extract()` reads the wrong block → every assertion throws; (b) editing **adjacent** to those two functions and disturbing the string extraction. **Mitigation: put ALL new tab JS INSIDE the existing app `<script>`** (so it stays largest by construction) and don't touch the `emitYaml`/`applyGuardrailConfig` regions. PR-1 adds no posture keys, so the round-trip assertions themselves are unchanged.
- **[gap-fix] Versioning: one minor `ravenclaude-core` bump PER PR (three total across PR-1/2/3)**, per AGENTS.md "bump on every user-visible change" — not one bump for the whole effort.

## Sequencing & PR
- Branch `feat/dashboard-ux`; PR-1 only. Draft early, drive CI green, merge-when-green.

## Open questions — RESOLVED by the gap analysis
1. **Mermaid pre-render?** → **Deferred to PR-3** (net-new infra; not a render-concepts reuse). PR-1 ships best-practice text-preview only.
2. **`/__run` widening surface?** → **Zero in PR-1** (security delta 0). `open-dashboard` rejected (process-spawning); `set-posture`-apply considered for PR-2 under security review.
3. **Overview-as-default?** → Yes; low risk, high first-run value; last-tab restore (localStorage) still honored where present [verify runtime behavior].
4. **`/__run` allow-list integrity gate?** → Yes, but in **PR-2** alongside any widening.
5. **Anything missed?** → The consumer-server-has-no-`/__run` reality (Class-A buttons dead for consumers — disable+help) and Gate-35 string-extraction brittleness — both now captured above.

## Acceptance criteria (PR-1 "done")
- Overview tab default, generator-discovered, static-safe, served/static banner correct on both hosts.
- Every command card is a button with an always-visible "what it runs" + non-hover tooltip; Class-A runs via existing `/__run` when served (disable+help otherwise); Class-B copies + honest in-Claude pill; Copy preserved everywhere.
- Guidance best-practice preview-on-click works static + served; tree source links intact.
- P1 headers/relabel/cross-links present; nothing removed.
- 304+/all gates green; freshness + parity + round-trip pass; `node --check` clean.
