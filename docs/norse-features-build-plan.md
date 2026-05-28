# Norse-themed features — execution-ready build plan

**Date:** 2026-05-23
**Author:** Build-plan synthesis (autonomous, Claude Opus 4.7)
**Status:** EXECUTION-**SEQUENCED** (revised 2026-05-23 review — see the delivery-realism note in §4). Twelve features, sequenced into phases with hard prerequisites, expert-panel caveats baked in as ship gates, dependencies resolved, open questions enumerated. **Effort figures are focused developer-hours and will expand under integration friction on the monolithic `dashboard.html`; two substrate assumptions (`$CLAUDE_INVOCATION_SOURCE` and the memory-hook input mechanism) are UNVERIFIED and gate the phases that depend on them.** Intended to be executed by Matt in a clean Linux Codespace.

> **Relationship to other docs.** This plan operationalizes the recommendations from the expert review in [`docs/norse-mythology-feature-map.md` §8](norse-mythology-feature-map.md) (PR #72), and slots into the surfaces designed in [`docs/dashboard-buildout-plan.md`](dashboard-buildout-plan.md) (PR #69), [`docs/tribunal-review-feature-design.md`](tribunal-review-feature-design.md) (PR #70), and [`docs/huginn-muninn-recon-design.md`](huginn-muninn-recon-design.md) (PR #71). When those docs and this plan disagree, **the design docs win for mechanics**; this plan wins for sequencing, scope-per-phase, and acceptance criteria.

---

## Table of contents

0. [What this plan is — and what it isn't](#0-what-this-plan-is)
1. [The 12 features at a glance](#1-the-12-features-at-a-glance)
2. [Prerequisite work (Phase 0)](#2-prerequisite-work-phase-0)
3. [Per-feature execution specs](#3-per-feature-execution-specs)
   - [3.1 Heimdall — unified perimeter-alarm surface](#31-heimdall)
   - [3.2 Mjölnir — release-readiness reporter](#32-mjolnir)
   - [3.3 Gleipnir — posture-as-binding (docs rename)](#33-gleipnir)
   - [3.4 Fenrir — bound-danger lane in posture](#34-fenrir)
   - [3.5 Norns — Urðr / Verðandi / Skuld lineage view](#35-norns)
   - [3.6 Bifröst — install-bridge wizard](#36-bifrost)
   - [3.7 Sleipnir — worktree-traversal labels](#37-sleipnir)
   - [3.8 Mímir — narrative renames + guard rails](#38-mimir)
   - [3.9 Yggdrasil — static then interactive marketplace tree](#39-yggdrasil)
   - [3.10 Ragnarök — `/reset-plugin-cache` with full DR gates](#310-ragnarok)
   - [3.11 Víðarr — posture/security event log panel](#311-vidarr)
   - [3.12 Níðhöggr — minimal-scope debt-watch panel](#312-nidhoggr)
4. [Master sequence — phased roadmap](#4-master-sequence)
5. [Cross-feature dependency graph](#5-cross-feature-dependency-graph)
5a. [Top risks](#5a-risks)
6. [Consolidated open questions](#6-consolidated-open-questions)
7. [How to execute this in a Codespace](#7-how-to-execute-in-a-codespace)
8. [Effort summary](#8-effort-summary)

---

<a id="0-what-this-plan-is"></a>

## 0. What this plan is — and what it isn't

**Is.** A 12-feature execution-ready spec sheet. Each feature has a scoped definition with every expert "Approve-with-changes" gate hard-coded as a ship requirement, a concrete file list, an ordered implementation checklist, acceptance criteria, dependencies, and an effort estimate. A phased master sequence groups the work so each phase is independently shippable with clear entry/exit criteria.

**Is not.** A design exploration. The design space was closed in the four prior docs; this plan does not re-litigate it. Where the expert panel deferred a sub-feature (Yggdrasil's interactive view, Níðhöggr's panel), the user has explicitly overridden the deferral and asked them included — they sit later in the sequence with the panel's caveats applied as scope limits, recorded inline.

**Scope.** All 12 features in ravenclaude-core. None of the per-domain plugins (power-platform, finance, regulatory-compliance, etc.) get changes from this plan. The plan ships **`ravenclaude-core 0.18.0` through `ravenclaude-core 0.28.0`** across 10 sequential phases, with the conditional Gleipnir viz adding `0.19.1` if the P0.5 mapping holds.

**Honesty pre-commitments.**

- Effort estimates are best-effort hours of focused work; they expand under integration friction.
- "Acceptance criteria" are observable conditions a CI gate or a manual checklist verifies — not aspirational goals.
- The plan assumes Phase A of the dashboard buildout (multi-layer comfort-posture: user / project / local) has shipped or is shipping in parallel; several features (Fenrir, Mímir's head, Víðarr) lean on the `network_read` and `security_deny` categories landing as documented in [`docs/dashboard-buildout-plan.md`](dashboard-buildout-plan.md) §2.
- The plan assumes the Huginn/Muninn Phase 0 prerequisites (the `events.jsonl` emission added to `scenario-retrieval`, the `.repo-layout.json` allow-list entries for `.ravenclaude/runs/dawn/**`) have shipped. The Norns and Víðarr features here piggyback on that substrate.

---

<a id="1-the-12-features-at-a-glance"></a>

## 1. The 12 features at a glance

| # | Feature | Verdict source | Phase | Approx effort | Key gate baked in |
|---|---|---|---|---|---|
| 1 | **Heimdall** — perimeter-alarm surface | §8.1, build-first | Phase 1 | 18–24 h | Tiered banner; read-only mirror; hooks emit machine-readable logs first |
| 2 | **Mjölnir** — release-readiness reporter | §8.1 Approve-with-changes | Phase 1 | 10–14 h | Reporter-first; no "consecrated" label until invalidation defined; no auto-commit/push |
| 3 | **Gleipnir** — posture-as-binding docs rename | §8.1 Approve-with-changes | Phase 1 (parallel) | 4–6 h | Docs-only first; decay viz only after six-axis confirmed; decay view operator-only |
| 4 | **Fenrir** — bound-danger lane in posture | §8.1 Approve | Phase 2 | 8–12 h | After Gleipnir docs; security_deny-cannot-be-locally-overridden invariant; annotation cites the literal hook/CI gate |
| 5 | **Norns** — Urðr / Verðandi / Skuld lineage view | §8.1 Approve-with-changes | Phase 3 | 12–16 h | Collapsible section inside existing Settings tab; Urðr + Verðandi only until `next_version` manifest field exists; plain-language sub-labels |
| 6 | **Bifröst** — install-bridge wizard | §8.1 Approve-with-changes | Phase 4 | 10–14 h | Copy-paste wizard with status verification, **not** orchestrator; ASCII `bifrost` in CLI; "bridge is down" troubleshooting copy |
| 7 | **Sleipnir** — worktree label convention | §8.1 Approve-with-changes (copy-only) | Phase 5 (parallel) | 3–5 h | Copy/label only; no new component / agent / slash-command |
| 8 | **Mímir** — narrative renames + guard rails | §8.1 Approve-with-changes | Phase 5 (parallel) | 8–12 h | Narrative renames only in docs/UI; do NOT rename `knowledge/` or `MEMORY.md`; ASCII `mimir` in CLI; first-write disclosure + secret-redaction guard |
| 9 | **Yggdrasil** (static then interactive) | §8.1 Deny → user override | Phase 6 (static), Phase 10 (interactive) | 4–6 h (static), 16–20 h (interactive) | Static SVG/ASCII diagram first; interactive view scoped sensibly per designer's caveat; deferral caveat recorded |
| 10 | **Ragnarök** — `/reset-plugin-cache` | §8.1 Approve-with-changes | Phase 7 | 18–24 h | Primary command `/reset-plugin-cache`; `/ragnarok` is alias; atomic-swap; dry-run; user-only invocation; pinned-SHA reinstall; `MEMORY.md` survives |
| 11 | **Víðarr** — posture/security event-log panel | §8.2 soft rescue | Phase 8 | 10–14 h | Surfaces the `security_deny`/per-pattern-override event log as a named UI panel; read-only mirror |
| 12 | **Níðhöggr** — minimal debt-watch panel | §8.1 Deny → user override | Phase 11 | 8–12 h | Minimal scope; subtitle "Debt watch" alongside Norse name; deferral caveat recorded |

**Headline effort: 129–179 hours.** Distributed across roughly 11 minor releases (`ravenclaude-core 0.18.0` through `0.29.0+`).

The **per-feature execution specs** in [§3](#3-per-feature-execution-specs) make this table concrete. The **master sequence** in [§4](#4-master-sequence) groups them into shippable phases with entry/exit criteria.

---

<a id="2-prerequisite-work-phase-0"></a>

## 2. Prerequisite work (Phase 0)

Six pieces of foundational work must land **before** the headline features in any meaningful form. Each is small (1–6 hours) but blocks one or more downstream features.

### 2.1 P0.1 — Manifest `next_version` / `roadmap` field

**What.** Extend `plugins/<plugin>/.claude-plugin/plugin.json`'s schema to allow an optional `next_version` field (semver string, target version) and an optional `roadmap[]` field (ordered list of `{version, summary}` entries). Update the marketplace.json validator (in `.github/workflows/validate-marketplace.yml`) to permit-and-validate these fields.

**Why.** The Norns panel's Skuld (future) column is empty without it — PM expert flagged this as a hard gate ("Skuld will be permanently empty or fabricated"). Mjölnir's reporter can also cross-check `next_version` against the actual `version` to catch drift.

**Files.**
- `.claude-plugin/marketplace.json` schema doc (inline comment).
- `.github/workflows/validate-marketplace.yml` — allow new fields without failure.
- `scripts/generate-dashboards.py` — surface the field into the per-plugin Settings tab data (read-only).
- `plugins/ravenclaude-core/.claude-plugin/plugin.json` — add the field as a worked example.

**Steps.**
1. Add `next_version` and `roadmap` to the example schema docstring in `plugins/ravenclaude-core/.claude-plugin/plugin.json` (committed alongside the validator change).
2. Update validator: read both fields, type-check, allow them to be absent.
3. Update `generate-dashboards.py` to read both fields and expose to dashboard JS as `window.__pluginNext` / `window.__pluginRoadmap`.
4. Document in `AGENTS.md` under "Adding a new plugin" — bumping `next_version` is optional; roadmap is optional but useful.

**Acceptance.** A new plugin.json with `next_version: "0.18.0"` and a `roadmap[]` of length 2 passes `python3 -m json.tool` and the validate-marketplace CI job; the field appears in the dashboard's Settings tab data.

**Effort.** 2–3 hours.

**Unblocks.** Norns Skuld column (3.5), Mjölnir's drift check (3.2).

### 2.2 P0.2 — Hooks emit machine-readable deny logs

**What.** All four PreToolUse / PostToolUse hooks in `plugins/ravenclaude-core/hooks/` write a structured JSON line to `.ravenclaude/runs/<session-id>/hook-events.jsonl` whenever they fire a deny verdict, in addition to their existing stderr/banner output. Schema:

```json
{
  "schema_version": 1,
  "ts": "2026-05-23T10:14:22Z",
  "hook": "enforce-layout.sh",
  "verdict": "deny | warn | allow",
  "tool": "Edit",
  "path": "plugins/foo/bar.md",
  "rule": "off-allow-list",
  "session_id": "...",
  "exit_code": 2
}
```

**Why.** Heimdall surfaces hook deny verdicts (§8.1 architect's gate: "consolidates four scattered signals into one operator view"). Today they go to stderr only; the dashboard cannot read them after the fact. Without machine-readable logs Heimdall can only show "something fired"; with them it can show "what fired, when, why, on what."

**Files.**
- `plugins/ravenclaude-core/hooks/enforce-layout.sh` — append jsonl write.
- `plugins/ravenclaude-core/hooks/guard-destructive.sh` — same.
- `plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh` — same.
- `plugins/ravenclaude-core/hooks/format-on-write.sh` — same (warn-only, but useful for telemetry).
- New helper: `plugins/ravenclaude-core/hooks/_emit-event.sh` (shared shell function — `source` from each hook).
- `.repo-layout.json` — confirm `.ravenclaude/**` is allow-listed for write (it is).
- `.gitignore` — ensure `.ravenclaude/runs/` is ignored (already is, per existing standard).

**Steps.**
1. Write `_emit-event.sh` — POSIX shell function `_emit_hook_event` taking `(hook, verdict, tool, path, rule, exit_code)` and appending JSON to `${CLAUDE_PROJECT_DIR}/.ravenclaude/runs/${CLAUDE_SESSION_ID:-unknown}/hook-events.jsonl`. Atomic-append-safe (use `>>` plus newline; one write per call).
2. `chmod +x` and add to allow-list; verify no executability gates (`find plugins/*/hooks -name '*.sh' -exec test -x {} \;` from AGENTS.md still passes).
3. In each of the four hooks, source the helper and call it on the deny path (and on the warn path for format-on-write and guard-recursive-spawn). Existing stderr/banner output is unchanged.
4. Add a fixture-based test under `plugins/ravenclaude-core/hooks/tests/` (new directory; allow-list it in `.repo-layout.json`) that:
   - Sets `CLAUDE_PROJECT_DIR` and `CLAUDE_SESSION_ID` to a tmp path.
   - Invokes the hook on a known-bad input.
   - Asserts that exactly one valid JSON line appears in the expected file.
5. Document the format in `plugins/ravenclaude-core/CLAUDE.md` under a new "Hook event log" subsection.

**Acceptance.** Each of the four hooks emits exactly one valid jsonl event per deny/warn; the gate-audit meta-test (`scripts/audit-gates.sh`) verifies one good fixture and one bad fixture per hook produce the expected event.

**Effort.** 3–4 hours.

**Unblocks.** Heimdall (3.1), Víðarr's posture/security event log (3.11 partly — Víðarr also reads `apply-comfort-posture.py` audit events).

### 2.3 P0.3 — ASCII-form discipline rule in AGENTS.md

**What.** Add a short house-rule subsection to `AGENTS.md` codifying that **any name with a diacritic gets a defined ASCII form** for CLI surfaces (`mimir`, `bifrost`, `mjolnir`, `ragnarok`, `nidhoggr`, `vidarr`, `urd`, `verdandi`, `skuld`, `yggdrasil`). Diacritic forms remain in prose, docs headers, and UI display labels.

**Why.** Documentarian explicitly flagged this as a cross-cutting concern across Mímir, Bifröst, Mjölnir, Ragnarök, Níðhöggr, Víðarr, and the Norns sub-labels (§8.3). Codifying once prevents per-feature litigation.

**Files.**
- `AGENTS.md` — add a "Themed-name discipline" subsection under "Code style" or "House rules."

**Steps.**
1. Author the subsection. Three paragraphs max: (a) the rule, (b) the ASCII form list, (c) where each form applies (CLI / file names / IDs use ASCII; prose / UI labels / docs may use diacritics).
2. Cross-reference from `plugins/ravenclaude-core/CLAUDE.md` so plugin-side rules stay aligned.

**Acceptance.** The rule exists in `AGENTS.md`; subsequent features cite it as the authority for their CLI naming.

**Effort.** 1 hour.

**Unblocks.** Mímir (3.8), Bifröst (3.6), Mjölnir (3.2), Ragnarök (3.10), Víðarr (3.11), Níðhöggr (3.12), Yggdrasil (3.9).

### 2.4 P0.4 — Posture-script audit-event emission

**What.** `plugins/ravenclaude-core/scripts/apply-comfort-posture.py` writes one structured event per posture change to `.ravenclaude/posture-events.jsonl` (per project), with fields `{ts, scope, category, level_from, level_to, security_deny_diff, override_diff, source}`. This file is append-only.

**Why.** Víðarr's panel needs an actual event substrate to surface (§8.2 soft rescue is contingent on "that log being surfaced as a named UI panel rather than a buried file"). Today posture changes happen in-place with no event trail.

**Files.**
- `plugins/ravenclaude-core/scripts/apply-comfort-posture.py` — add `_emit_posture_event()` and call it on every translation pass.
- `.gitignore` — ensure `.ravenclaude/posture-events.jsonl` is ignored.
- `plugins/ravenclaude-core/CLAUDE.md` — document the format.

**Steps.**
1. Add `_emit_posture_event(...)` that opens `${PROJECT_DIR}/.ravenclaude/posture-events.jsonl` in append mode (atomic line write) and writes one JSON object.
2. Diff old vs new `.claude/settings.json` to compute `level_from / level_to / security_deny_diff / override_diff` per category.
3. `source` is one of: `dashboard-save`, `slash-command`, `cli-direct`, `migration`, `unknown` — detected from the script's invocation context.
4. Unit-test with two before/after fixtures.

**Acceptance.** Running `/set-posture` with a change writes one new JSONL line containing all expected fields; the file remains valid JSONL after N invocations.

**Effort.** 3–4 hours.

**Unblocks.** Víðarr (3.11).

### 2.5 P0.5 — Confirm Gleipnir six-axis decomposition

**What.** A short audit document at `docs/posture-six-axis-decomposition.md` enumerating which dashboard-schema category, security_deny entry, and per-pattern override contributes to each of the six "Gleipnir ingredients." If the actual posture YAML doesn't cleanly decompose into six axes, this step writes a memo to that effect and **the Gleipnir decay viz is descoped to a stretch goal**; the docs-only rename still ships.

**Why.** Architect's gate on Gleipnir (§8.1): "only worth it if exactly six axes actually map." Doing the audit once, up-front, avoids building viz infrastructure that can't be populated.

**Steps.**
1. Read `plugins/ravenclaude-core/dashboard-schema.json`'s 12-category list.
2. Read `plugins/ravenclaude-core/scripts/apply-comfort-posture.py`'s `security_deny` baseline and per-pattern override mechanism.
3. Author a 200-word audit answering: "If we map posture rules onto Gleipnir's six paradoxical ingredients (cat's footfall / woman's beard / mountain roots / bear sinews / fish breath / bird spittle), what's the cleanest assignment? Does each of the 12 categories collapse into one of the six? If not, where's the friction?"
4. Decide: (a) it maps — proceed to Gleipnir Phase 1 with viz; (b) it doesn't map — descope viz, keep docs rename.

**Acceptance.** The memo exists at `docs/posture-six-axis-decomposition.md`; either Gleipnir 3.3's viz survives or is explicitly descoped with a one-line note.

**Effort.** 2–3 hours.

**Unblocks.** Gleipnir viz portion of 3.3 (if mapping holds).

### 2.6 P0.6 — `events.jsonl` emission in `scenario-retrieval`

**What.** Confirm or land the Huginn-doc Phase 0 prerequisite: `plugins/ravenclaude-core/skills/scenario-retrieval.md` instructs the dispatched agent to emit an event line per surfaced scenario into the current run's `events.jsonl`. If already shipped (via PR #71's Phase 0 work), this step is a no-op verification. If not, ship it here.

**Why.** Norns Urðr column reads "last-surfaced" data from these events. Without them Urðr is partial.

**Files.**
- `plugins/ravenclaude-core/skills/scenario-retrieval.md` — add an emission instruction with a sample line.

**Steps.**
1. Check current `scenario-retrieval.md` for an `events.jsonl` emission clause.
2. If absent, add: "After surfacing a scenario, append a line to `.ravenclaude/runs/<run-id>/events.jsonl` of shape `{type: 'scenario_surfaced', scenario_path, ts, surfaced_to: <agent>}`."
3. Cross-link from the new Norns spec.

**Acceptance.** `scenario-retrieval.md` contains the emission clause; a manual fixture invocation produces the expected event.

**Effort.** 1–2 hours.

**Unblocks.** Norns Urðr column (3.5).

### Phase 0 entry / exit

**Entry.** Main is green; ravenclaude-core is at v0.17.0 or later; Phase A of the dashboard buildout (multi-layer comfort posture) has at least started.

**Exit.**
- All six prerequisite tasks (P0.1–P0.6) are merged to main.
- The gate-audit meta-test (`scripts/audit-gates.sh`) passes against the updated hooks and validator.
- A single combined release `ravenclaude-core 0.18.0-prereqs` (or sequenced micro-bumps) records the prerequisite work.
- This plan's open-questions list ([§6](#6-consolidated-open-questions)) has been re-read after Phase 0 and any newly-surfaced questions are added.

**Phase 0 effort.** 12–17 hours total.

---

<a id="3-per-feature-execution-specs"></a>

## 3. Per-feature execution specs

Each feature spec below has the same structure: **scope (with caveats baked in)**, **files touched**, **steps**, **acceptance criteria**, **dependencies**, **effort**.

<a id="31-heimdall"></a>

### 3.1 Heimdall — unified perimeter-alarm surface

> Build first. Most-approved candidate of the 11 (§8.1 Heimdall: no expert disagreement).

#### Scope (with caveats baked in)

A new dashboard tab labeled **"Heimdall"** (subtitle "Perimeter alerts") at `#/heimdall` in `plugins/ravenclaude-core/dashboard.html`. The tab is a **read-only mirror** (security's gate, §8.1) of four signal sources.

> **Serving-mode note.** The per-plugin dashboard has two viewing modes: (a) **GitHub Pages** (read-only, marketplace-state baked-in at last generator run; can't read the visitor's local files), and (b) **`scripts/serve-dashboards.py`** (locally-served at `http://localhost:8000/...`, reads the consumer's local `.ravenclaude/runs/` directory). Heimdall's hook-event card is **fully populated only in the locally-served mode**. In the Pages mode, the card shows a one-line empty state: "Run `scripts/serve-dashboards.py` locally to see your hook-event history — this surface needs file-system access GitHub Pages can't provide." The other three cards (CI status, version drift, Gjallarhorn from marketplace-state) work in both modes.

The four signal sources:

1. Most-recent hook deny/warn verdicts (read from `hook-events.jsonl` — see P0.2). *Local-served only.*
2. CI gate status — dashboard JS fetches `https://api.github.com/repos/<owner>/<repo>/actions/runs?per_page=5` directly at panel-load time (no auth needed for public repos; rate-limited at 60 req/hr per IP, which is more than enough for a panel that loads once per session). Falls back to a "rate-limited or offline" empty state.
3. Plugin-version drift (compute `marketplace.json` plugin versions vs each `plugins/*/.claude-plugin/plugin.json` `version` field; surface drift as a finding). *Works in both modes — data is committed to the repo.*
4. **Gjallarhorn banner** — a tiered, fixed-position banner that triggers when something irrecoverable is about to happen (push-to-main attempt, force-push attempt, plugin uninstall on a project with state). Tiers (security's gate):
   - **Red** — irrecoverable action in flight (force-push, `rm -rf` outside trash, `git reset --hard` with uncommitted work, `npm publish`).
   - **Amber** — deny verdict just fired (layout violation, destructive-guard hit).
   - **Grey** — advisory (format-on-write modified a file, recursive-spawn warning).

The banner reads upstream-event data only. It does NOT accept an "acknowledge and proceed" interaction for red-tier events without a second confirmation channel (security's gate). For red-tier, the banner offers a "view event detail" affordance and a deep-link to the relevant slash command (e.g., `/permission-hygiene` for a deny verdict) — execution happens in the user's Claude Code session, not the dashboard.

Plain-language subtitle on every tab card so non-mythology readers grok it (designer's gate).

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — new tab + `#/heimdall` route + JS rendering + `fetchCiStatus()` helper.
- `plugins/ravenclaude-core/dashboard-schema.json` — no change (tab IDs aren't in the schema; routes are in `dashboard.html`).
- `plugins/ravenclaude-core/dashboard-assets/heimdall.css` (new) — styles for the banner tiers + card grid.
- `scripts/generate-dashboards.py` — read `hook-events.jsonl` (last 30 days, per-project) and compute version-drift, inline into `window.__heimdall = {...}` at generator time. CI status is fetched client-side.
- `scripts/serve-dashboards.py` — confirm it sets a CORS-friendly response for the GitHub API fetch (no change expected; documenting the dependency).
- `plugins/ravenclaude-core/CLAUDE.md` — document Heimdall tab and its read-only-mirror property AND the serving-mode distinction.
- `.repo-layout.json` — allow `plugins/*/dashboard-assets/**` (already allowed).

#### Steps

1. **Verify P0.2 is shipped.** `hook-events.jsonl` files exist after a session that triggered a hook. If not, complete P0.2 first.
2. **Author `heimdall.css`.** Three tier classes (`.gjallarhorn--red`, `.gjallarhorn--amber`, `.gjallarhorn--grey`). Banner is `position: fixed; top: 0; left: 0; right: 0; z-index: 200`. Card grid for the four signal sources uses the existing dashboard card grid pattern.
3. **Add Heimdall tab to `dashboard.html`'s tab inventory.** Tab button: label "Heimdall", subtitle "Perimeter alerts", icon (one small monochrome shield glyph). Tab content is a deferred-render section that activates on `#/heimdall`.
4. **Implement the four card readers in JS.**
   - `renderHookEvents(window.__heimdall.hookEvents)` — group by hook, show last 10 per hook, severity-color rows.
   - `renderCiStatus(window.__heimdall.ciStatus)` — last 5 CI runs, green/red dot, link to GH Actions.
   - `renderVersionDrift(window.__heimdall.versionDrift)` — table: plugin name, marketplace.json version, plugin.json version, drift status.
   - `renderGjallarhorn(window.__heimdall.gjallarhornState)` — render banner if any state is non-empty; else hide.
5. **Wire the CI-status fetch.** Implement a JS function `fetchCiStatus(owner, repo)` that issues a single `fetch('https://api.github.com/repos/<owner>/<repo>/actions/runs?per_page=5')` at panel-load time. Cache the response in `sessionStorage` for 5 minutes (60 req/hr limit is generous; this caching is defensive). Owner and repo come from a constant at the top of `dashboard.html` (`const REPO_OWNER = "mcorbett51090"; const REPO_NAME = "RavenClaude";`). **Private-repo branch (2026-05-23 review — this marketplace is private by default):** the unauthenticated GitHub API returns 403/404 for a private repo, so render **three** distinct states, not two — (a) public → CI cards; (b) rate-limited → "try again shortly"; (c) 403/404 → "This marketplace is private; the CI card needs a GitHub token — run `scripts/serve-dashboards.py` with `gh auth` to populate it." Decide explicitly whether private-repo CI status is in scope for v1 or deferred; do NOT let the empty state silently masquerade as "CI green/offline."

6. **Extend `generate-dashboards.py`** to read `hook-events.jsonl` (last 30 days from the consumer's `.ravenclaude/runs/*/` folders) and the version-drift computation, and inline both into `window.__heimdall`.
7. **Add empty states.** Each card surfaces an explicit "No recent events — your perimeter has been quiet" message if its data source is empty. The banner is hidden when all four sources are clean.
8. **Add Gjallarhorn tiering tests.**
   - Fixture A: an `hook-events.jsonl` with one red event → banner shows red.
   - Fixture B: only an amber event → banner shows amber.
   - Fixture C: only grey → banner shows grey.
   - Fixture D: empty → banner hidden.
9. **Document the read-only-mirror property** in `plugins/ravenclaude-core/CLAUDE.md`: "Heimdall does not write to `hook-events.jsonl`, `ci-status.json`, or any deny-source. It surfaces what those upstream sources already emitted."
10. **Plain-language subtitles.** Tab subtitle: "Perimeter alerts." Card titles: "Recent hook denials," "Recent CI runs," "Plugin version drift," "Active alarms (Gjallarhorn)."

#### Acceptance

- The Heimdall tab renders at `#/heimdall` with all four cards present.
- A controlled fixture (one deny event in `hook-events.jsonl`) produces a visible amber banner and an entry in the "Recent hook denials" card.
- The banner is hidden when all data sources are empty.
- A11y: the banner is keyboard-focusable; the red tier carries an `aria-live="assertive"` attribute; amber and grey use `aria-live="polite"`.
- The CI gate (`scripts/audit-gates.sh`) includes one known-bad and one known-good fixture for the Heimdall renderer.
- A maintainer reviewing the tab can answer "what's the most recent layout violation, CI run, and version drift on this marketplace?" in one glance.

#### Dependencies

- **P0.2** (hooks emit machine-readable logs) — hard.
- **P0.3** (ASCII discipline) — soft (Heimdall has no diacritics, but the subtitle convention propagates from here).
- Dashboard buildout Phase A (Settings tab persistence triple) — soft, only for "Configure Heimdall" affordances which are out of scope for v1.

#### Effort

18–24 hours.

---

<a id="32-mjolnir"></a>

### 3.2 Mjölnir — release-readiness reporter

> Reporter-first (QA's gate). No auto-commit / auto-push (architect's gate). No "consecrated" label until invalidation semantics are defined (QA + documentarian gate).

#### Scope

A new slash command `/mjolnir` (ASCII; CLI form is `mjolnir`, prose form is "Mjölnir") that composes existing tools to produce a single, named, color-coded **release-readiness report** for a plugin. **Reporter-only in v1**: the command does not commit, push, tag, or write to `marketplace.json`. It reads, checks, and reports.

Checks performed (in order; each emits a named error on failure):

1. **Version sync** — `plugins/<plugin>/.claude-plugin/plugin.json` `version` matches `.claude-plugin/marketplace.json`'s entry for that plugin. (Existing CI gate `validate-marketplace.yml`; Mjölnir surfaces the result.)
2. **All CI gates green** — call `scripts/audit-gates.sh` and check exit code 0.
3. **Prettier clean on whole tree** — `npx prettier --check . --log-level warn` exits 0.
4. **Layout clean** — every staged file matches an allowed glob (re-uses the snippet in `AGENTS.md`'s "Layout-allow-list discipline").
5. **Hooks executable** — `find plugins/*/hooks -name '*.sh' -exec test -x {} \;` succeeds.
6. **Manifest validity** — every `plugins/*/.claude-plugin/plugin.json` parses with `python3 -m json.tool`.
7. **README + CLAUDE.md present** — for the plugin being released.
8. **`next_version` parity (when present)** — if `plugin.json` declares `next_version`, the staged change either bumps `version` to that or doesn't touch `next_version` (cross-check uses P0.1).
9. **Hooks emit events** — for any hook that fired this session, `hook-events.jsonl` contains at least one entry (lazy smoke test of P0.2).

On all green, emit a single line: `Mjölnir — release-ready for <plugin>@<version>. The hammer rings true.` (Themed copy is configurable to plain per the `huginn_muninn.theme` toggle from the dashboard.) On any red, emit a numbered list of failures with the named error per check.

**No "consecrated" semantics in v1.** Mjölnir does not write a "consecrated" marker; does not gate merges; does not block pushes. A second pass (Phase 10+) introduces the consecrated label *after* invalidation semantics are defined (i.e., what un-consecrates a plugin after a post-bless edit).

#### Files touched

- `plugins/ravenclaude-core/commands/mjolnir.md` (new) — slash command definition. Frontmatter declares `audience`, `works_with`, `scenarios`, `quickstart` per `docs/best-practices/agent-scenario-authoring.md`.
- `plugins/ravenclaude-core/scripts/check-release-readiness.sh` (new) — the actual checker; the command dispatches the deep-researcher or scripts the bash directly.
- `plugins/ravenclaude-core/scripts/_pattern-named-errors.json` (new) — the named-error catalog for the report.
- `plugins/ravenclaude-core/CLAUDE.md` — document the command and the reporter-only scope.
- `AGENTS.md` — add `/mjolnir` to the "Slash commands shipped by the plugin" section.

#### Steps

1. Author `check-release-readiness.sh` as a self-contained POSIX shell script. Each check function emits `[OK]` or `[FAIL: <named-error>]` per line. Final exit code: 0 on all green; 1 on any fail.
2. Author `_pattern-named-errors.json` — the catalog of error names + one-line descriptions + suggested fixes.
3. Author `mjolnir.md` slash command. Body:
   - Brief description of the command's scope ("checks release-readiness; does NOT commit, push, or write").
   - Frontmatter scenario fields per the authoring schema.
   - The single-line success / failure-list output format.
   - Cross-link to `scripts/check-release-readiness.sh` and the named-error catalog.
4. **Test against the current `ravenclaude-core@0.17.0` state.** Expect mostly green; fix any surprises before shipping. Document the expected baseline output in the command's docstring.
5. Add to `dashboard.html` Commands tab (per buildout B.2) — Mjölnir card with hover-tooltip showing `/mjolnir <plugin>` syntax.
6. **No auto-commit / no auto-push.** Verify by code-review that the script never invokes `git commit`, `git push`, `git tag`, `gh ...` (read-only `gh api` for PR check status is permitted; mutating gh calls are not).
7. Add a fixture-based test in `plugins/ravenclaude-core/scripts/tests/` (if absent, create it and allow-list under `.repo-layout.json`) — one known-green plugin and one known-red fixture per check.

#### Acceptance

- Running `/mjolnir ravenclaude-core` on a green tree emits the single-line success message.
- Running `/mjolnir ravenclaude-core` on a tree with one intentional violation (e.g., a manifest with a parse error) emits the expected named error.
- The script exits 0 on all green; 1 on any fail.
- No git, gh, npm-publish, or marketplace-write call appears in the script's source.
- The command is listed in `AGENTS.md` under the slash-command section.

#### Dependencies

- **P0.1** (manifest `next_version` field) — soft; one check is a no-op if absent.
- **P0.2** (hook events) — soft; check 9 is a no-op if absent.
- **P0.3** (ASCII discipline) — hard for the CLI form.

#### Effort

10–14 hours.

---

<a id="33-gleipnir"></a>

### 3.3 Gleipnir — posture-as-binding (docs rename)

> Docs-only first (architect's gate). Decay viz only after six-axis confirmed (P0.5). Decay view operator-only (security's gate).

#### Scope

A documentation rename + framing pass that reframes the comfort-posture system as **Gleipnir, a binding composed of six paradoxical ingredients**. **Pure docs change in Phase 1.** No schema keys renamed; no YAML structure altered.

Files altered:
- `plugins/ravenclaude-core/skills/set-posture.md` — opening paragraph adds the Gleipnir framing with one explicit myth-cite ("Gleipnir was forged from six things that do not exist — your posture binding is the same idea: the strength comes from the composition of light, paradoxical, individually-soft constraints").
- `plugins/ravenclaude-core/CLAUDE.md` — comfort-posture subsection adds a "Why this works (the Gleipnir read)" callout box.
- `AGENTS.md` — a one-sentence reference under house rules.
- `README.md` (optional) — one paragraph on the metaphor.

**Decay viz (deferred).** If P0.5's six-axis audit confirms a clean six-way mapping, a follow-on phase ships a small "binding health" bar in the Settings tab showing six segments (one per ingredient), dimming a segment when a rule contributing to that ingredient is removed. **Operator-only** — the bar appears on the dashboard but NOT on any agent-visible surface (no stdout, no slash-command output, no SOP block).

If P0.5 finds the mapping doesn't cleanly hold, the decay viz is descoped to a stretch goal and the docs rename ships standalone.

#### Files touched

- `plugins/ravenclaude-core/skills/set-posture.md`.
- `plugins/ravenclaude-core/CLAUDE.md`.
- `AGENTS.md`.
- `README.md` (optional, one paragraph).
- (Conditional, if P0.5 mapping holds) `plugins/ravenclaude-core/dashboard.html` — Settings tab adds the six-segment binding-health bar.
- (Conditional) `plugins/ravenclaude-core/dashboard-assets/gleipnir.css` (new).

#### Steps

1. **Phase 1 (docs-only):**
   - Add the myth-cite to `set-posture.md` (opening paragraph).
   - Add the "Why this works (the Gleipnir read)" callout to `plugins/ravenclaude-core/CLAUDE.md` (under the comfort-posture subsection).
   - Add the one-sentence reference to `AGENTS.md` house rules.
   - Optionally, the README paragraph.
2. **Conditional Phase (deferred until P0.5 + Phase 1 confidence):**
   - Author `gleipnir.css`.
   - Add the six-segment binding-health bar to the Settings tab. Each segment carries a tooltip naming its ingredient ("cat's footfall — the deny baselines"; "woman's beard — the per-pattern overrides"; etc., per the P0.5 memo's assignment).
   - When a rule contributing to a segment is removed from the posture YAML, the segment dims.
   - Wire it to the dashboard's existing live-edit posture flow.
   - **Operator-only enforcement:** the bar lives in the dashboard's Settings tab; no JS or agent surface emits the segment data into stdout, the SOP block, or any other channel an agent reads.

#### Acceptance

**Phase 1:**
- The myth-cite appears verbatim in `set-posture.md`.
- The "Why this works" callout appears in `plugins/ravenclaude-core/CLAUDE.md`.
- No schema keys, YAML fields, or settings.json keys were renamed.
- No agent definitions or skills changed.

**Conditional Phase (if shipped):**
- The six-segment bar renders in the Settings tab.
- Removing a rule from posture YAML causes the affected segment to dim within one dashboard refresh.
- No segment data appears in any agent-readable channel (verify by grepping `dashboard.html`'s JS — no segment data leaks to global `window` keys an agent would read; the data is scoped to the renderer).

#### Dependencies

- **P0.5** (six-axis audit) — hard for the viz portion; soft for the docs.
- **P0.3** (ASCII discipline) — soft; `gleipnir` has no diacritics.

#### Effort

4–6 hours (docs Phase 1). Add 8–12 hours if the viz Phase ships.

---

<a id="34-fenrir"></a>

### 3.4 Fenrir — bound-danger lane in posture

> Lands after Gleipnir docs (documentarian's gate). `security_deny`-cannot-be-locally-overridden invariant (architect's gate). Annotation cites the literal hook/CI gate (security's gate).

#### Scope

A new section in the posture YAML schema and the Settings-tab UI: **"Fenrir-bound capabilities"** — a named lane that lists each known-dangerous capability the system is **deliberately** holding back, distinct from the general deny list.

Concretely:

- The Fenrir lane is rendered as a collapsible list in the Settings tab, with one row per Fenrir-marked rule.
- Each row shows: **the capability** (e.g., "force-push to main"), **why it's dangerous** (one-sentence rationale), **what binds it** (the literal hook/CI gate, e.g., `security_deny baseline + guard-destructive.sh`), and **what would happen if it broke free** (the Ragnarök linkage, e.g., "history rewrite is recoverable only via reflog + force-push to recover").
- A **hard invariant** in `apply-comfort-posture.py`: a Fenrir-marked rule that lives in `security_deny` **cannot be locally overridden** by a per-pattern override at any scope (user / project / local). The translator rejects local overrides that would relax a Fenrir-marked `security_deny` entry. Other deny-list entries are still locally overridable; only Fenrir-marked ones are absolute.
- Each Fenrir-marked rule carries one myth-cite reference in the docs (documentarian's gate).

#### Files touched

- `plugins/ravenclaude-core/dashboard-schema.json` — add a top-level `fenrir_bound[]` array of `{capability, why, bound_by, breakout_consequence}` entries.
- `plugins/ravenclaude-core/scripts/apply-comfort-posture.py` — extend the translator to read the Fenrir list and enforce the invariant.
- `plugins/ravenclaude-core/dashboard.html` — Settings tab adds the collapsible Fenrir lane.
- `plugins/ravenclaude-core/skills/set-posture.md` — document the lane and the invariant.
- `plugins/ravenclaude-core/CLAUDE.md` — myth-cite in the comfort-posture section.
- New: `plugins/ravenclaude-core/dashboard-assets/fenrir.css`.

#### Steps

1. Author the initial Fenrir list. Seed: `force-push-to-main`, `git-reset-hard-with-uncommitted-work`, `npm-publish-without-tag`, `curl-pipe-shell`, `chmod-777-broad`, `recursive-agent-spawn`. (Sourced from the existing `security_deny` baseline.) Each entry gets a one-sentence `why`, a literal `bound_by` reference, and a one-sentence `breakout_consequence`.
2. Add `fenrir_bound[]` to `dashboard-schema.json`.
3. Extend `apply-comfort-posture.py`:
   - Read the Fenrir list from the schema.
   - On translation, before writing the merged settings.json, verify that no local-scope override removes or relaxes any Fenrir-marked entry from `security_deny`. If one does, abort with a named error: `FENRIR_LOCAL_OVERRIDE_REJECTED: <capability>`.
   - Emit a posture event (P0.4) on Fenrir invariant violations.
4. Author `fenrir.css` and render the collapsible lane in the Settings tab. Each row: capability label, "why" rationale (italic), bound-by reference (monospace, click-to-expand for the literal hook source), breakout-consequence (warning color).
5. Add the myth-cite to `set-posture.md`: "Fenrir was bound by Gleipnir — a constraint composed of impossibilities. Each capability below is held in place by a specific binding; when the binding is removed, the wolf walks."
6. **Test the invariant.** Fixture: a `comfort-posture.yaml` at project-scope that includes a per-pattern override removing `force-push-to-main` from `security_deny`. Expected: `apply-comfort-posture.py --scope local` rejects it with `FENRIR_LOCAL_OVERRIDE_REJECTED`.
7. **Test the inverse.** Fixture: a per-pattern override removing a non-Fenrir-marked deny entry. Expected: succeeds.

#### Acceptance

- `dashboard-schema.json` includes a `fenrir_bound[]` array with ≥6 seed entries.
- The Settings-tab Fenrir lane renders with all entries; each row shows capability + why + bound-by + breakout.
- The translator rejects a local-scope override that would relax a Fenrir-marked rule, with the named error.
- The translator accepts a local-scope override that relaxes a non-Fenrir rule.
- The myth-cite appears in `set-posture.md`.
- One posture event (P0.4) is emitted on a rejected override.

#### Dependencies

- **3.3 Gleipnir (docs)** — hard. Documentarian's gate: Fenrir's myth-cite assumes Gleipnir framing is in place.
- **P0.3** (ASCII discipline) — soft; `fenrir` has no diacritics.
- **P0.4** (posture-event emission) — soft; the rejection emits a posture event but the feature works without it.

#### Effort

8–12 hours.

---

<a id="35-norns"></a>

### 3.5 Norns — Urðr / Verðandi / Skuld lineage view

> Collapsible section inside the existing Settings tab, NOT a new tab (designer's gate). Urðr + Verðandi columns only; Skuld held until P0.1 (`next_version`) lands (PM's gate). Plain-language sub-labels at all times (architect + designer gate).

#### Scope

A new **collapsible section** within each plugin's existing **Settings tab** (`plugins/<plugin>/dashboard.html`), labeled **"Plugin lineage"** with the Norse sub-name **"The Norns"** in parentheses. Three columns:

| Column | Norse label | Plain-language sub-label | Content |
|---|---|---|---|
| Past | Urðr | "Lessons & history" | Last 5 scenario surfaces (from `events.jsonl`), last 5 decision-log entries (from `docs/decisions/` if present), last 10 commits (from `git log --oneline -10` against `plugins/<plugin>/`) |
| Present | Verðandi | "Current" | Current `version`, active hook count, active rule count, last release date |
| Future | Skuld | "Proposed" | `next_version` value (if set per P0.1), `roadmap[]` entries (if set), open proposals in `docs/proposals/` referencing this plugin |

**v1 ships Urðr + Verðandi only.** Skuld is gated on P0.1 having shipped *and* at least one plugin having declared `next_version`. If neither is true, the Skuld column is hidden with a one-line empty state: "No proposed version. Add a `next_version` field to this plugin's `plugin.json` to populate Skuld."

ASCII forms in CLI: `urd`, `verdandi`, `skuld` (no diacritics). Display labels in UI: Urðr, Verðandi, Skuld.

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — Settings tab gains a collapsible "Plugin lineage" section.
- `plugins/ravenclaude-core/dashboard-assets/norns.css` (new) — three-column layout.
- `scripts/generate-dashboards.py` — read git log, scenarios `events.jsonl`, `docs/decisions/`, `docs/proposals/`, and inline into `window.__norns` per-plugin.
- `plugins/ravenclaude-core/CLAUDE.md` — document the section.
- `plugins/<each plugin>/.claude-plugin/plugin.json` — optionally add `next_version` (no hard requirement at v1; Skuld is empty when absent).

#### Steps

1. Wire the data sources in `generate-dashboards.py`:
   - **Urðr.** For each plugin: read `events.jsonl` files under `.ravenclaude/runs/*/`, filter for `type: 'scenario_surfaced'` where `scenario_path` is under `plugins/<plugin>/scenarios/`, take last 5. Read `docs/decisions/<plugin>-*.md` if present (sorted by mtime, last 5). Read `git log --oneline -10 -- plugins/<plugin>/`.
   - **Verðandi.** Read the plugin's `plugin.json` for `version`. Count hooks in `plugins/<plugin>/hooks/`. Count rules in `plugins/<plugin>/rules/`. Read last release date from `git log` of `plugin.json`.
   - **Skuld.** If P0.1 has shipped: read `next_version` and `roadmap[]` from `plugin.json`. Read `docs/proposals/*.md` and filter by name match.
2. Author `norns.css`. Three columns side-by-side at wide viewport; stacked at narrow. Each column has a Norse label header + plain-language sub-label + scrollable list.
3. Add the collapsible section to the Settings tab in `dashboard.html`. The section header is `▶ Plugin lineage (The Norns)`. Click toggles `aria-expanded`. Default collapsed.
4. Add a one-line legend below the section header: "Urðr (Lessons & history) · Verðandi (Current) · Skuld (Proposed)." Always shown; not stylistic.
5. **Empty states.** Each column gets a meaningful empty state. Urðr: "No history yet — this plugin has no surfaced scenarios, decisions, or commits in scope." Verðandi: "—" for missing release date. Skuld: see scope above.
6. Document in `plugins/ravenclaude-core/CLAUDE.md` under a new "Norns section" subsection.

#### Acceptance

- The Settings tab includes a "Plugin lineage (The Norns)" collapsible section.
- Urðr column renders with at least one of: surfaced scenarios, decisions, commits.
- Verðandi column renders the current version + active hook/rule counts.
- Skuld column either shows `next_version` + roadmap + proposals, OR shows the gated empty state if no plugin has declared `next_version`.
- Plain-language sub-labels are always visible.
- Norse names render with correct diacritics (Urðr / Verðandi); ASCII forms used in any CLI surface (none in v1).
- A11y: collapsible has `aria-expanded`; columns are reachable via keyboard tab order.

#### Dependencies

- **P0.1** (manifest `next_version`) — hard for Skuld; soft for the rest.
- **P0.6** (`events.jsonl` emission in scenario-retrieval) — hard for Urðr.
- **P0.3** (ASCII discipline) — soft.

#### Effort

12–16 hours.

---

<a id="36-bifrost"></a>

### 3.6 Bifröst — install-bridge wizard

> Copy-paste wizard with status verification, **not** orchestrator (architect's gate). ASCII `bifrost` in CLI (documentarian's gate). "Bridge is down" troubleshooting copy is load-bearing (designer's gate).

#### Scope

A new dashboard tab labeled **"Install"** (subtitle "Bifröst") at `#/install` (alias `#/bifrost`) in `plugins/ravenclaude-core/dashboard.html`. The tab is a **guided 4-step copy-paste wizard** for installing a plugin from the marketplace:

| Step | Action | Status check |
|---|---|---|
| 1. Add marketplace | `/plugin marketplace add <url-or-path>` (copy-button) | Polls `marketplace.json` presence in `~/.claude/plugins/cache/...` (no JS-level mutation; user re-checks via "Verify" button) |
| 2. Install plugin | `/plugin install <plugin-name>@<marketplace-name>` (copy-button) | Polls plugin presence in the install cache |
| 3. Reload plugins | `/reload-plugins` (copy-button) | Manual confirmation: "I see the plugin in my `/plugin` menu" |
| 4. Verify | `/init-agent-ready --check` (copy-button) | Reads return value; surfaces green / red |

Between each step, a **status verification region** with a "Verify" button + "What I see now" text area where the user pastes the slash-command's output. The wizard's JS does **not** execute commands; the user runs each command in their Claude Code session, the wizard surfaces the next step on confirmation.

**Failure-mode accordion** ("If the bridge is down…"):
- "Marketplace add failed — check the URL or path; common causes: typo, missing `.claude-plugin/marketplace.json`, missing read permission."
- "Plugin install failed — check that the plugin name matches an entry in marketplace.json's `plugins[]`."
- "Reload failed — try restarting Claude Code; the cache may be stale."
- "Verify failed — see `plugins/<plugin>/CLAUDE.md` for the plugin's required environment."

Each failure-mode row is a click-to-expand accordion with a 2-3 sentence diagnosis + suggested next step.

ASCII form `bifrost` in any CLI surface (e.g., command alias `/bifrost-install` if ever added; v1 ships no slash command). The tab title uses Bifröst with the diacritic; the URL alias is `bifrost`.

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — new Install tab + wizard JS.
- `plugins/ravenclaude-core/dashboard-assets/bifrost.css` (new) — 4-step layout + accordion.
- `plugins/ravenclaude-core/CLAUDE.md` — document the wizard.
- `AGENTS.md` — update Setup commands section to reference the wizard.

#### Steps

1. Author `bifrost.css` — 4-step linear layout, status badges (green / amber / red / grey), copy-button styles, accordion styles.
2. Add the Install tab to `dashboard.html`'s tab inventory. Tab title: "Install (Bifröst)". Subtitle: "Bridge a plugin into your project."
3. Implement the 4-step wizard:
   - Each step has: heading, one-paragraph explanation, code-snippet (with copy-button), "Verify" button + paste-output region, status badge.
   - The "Verify" button parses the pasted output with a regex against a known success/failure pattern per step (e.g., step 1 success: "marketplace added"; step 1 failure: "failed to add").
   - On verify-success, the next step's heading turns from grey to bright; on verify-failure, the failure-mode accordion's relevant row auto-expands.
4. Author the failure-mode accordion content (4 rows minimum, one per step's most-likely failure).
5. Add a one-paragraph intro at the top: "Bifröst is the rainbow bridge between the marketplace and your project. Follow these four steps to install a plugin. Each step is copy-paste only — Bifröst guides you, but you cross the bridge yourself."
6. Implement keyboard navigation: tab through copy-buttons, accordion-rows, verify-buttons in linear order.
7. Document the wizard in `plugins/ravenclaude-core/CLAUDE.md` under "Bifröst install wizard" subsection.

#### Acceptance

- The Install tab renders at `#/install` (and `#/bifrost` alias).
- Each of the 4 steps shows a copy-button + verify-button + paste region + status badge.
- Pasting a known-success output into step 1's verify region transitions step 1 to green and unlocks step 2.
- Pasting a known-failure output auto-expands the matching failure-mode accordion row.
- The wizard's JS does NOT invoke slash commands programmatically (verify by code review).
- ASCII alias `#/bifrost` resolves to the same view.
- All four failure-mode accordion rows render with diagnosis + suggested next step.
- A11y: each accordion has `aria-expanded`; copy-buttons have `aria-label`; status badges have visible-text labels in addition to color.

#### Dependencies

- **P0.3** (ASCII discipline) — hard.
- Dashboard buildout B.3 (Install/Setup tab in the buildout plan) — bidirectional: this *is* the Install tab; the buildout's B.3 scope folds into Bifröst.

#### Effort

10–14 hours.

---

<a id="37-sleipnir"></a>

### 3.7 Sleipnir — worktree-traversal labels

> Copy / labeling convention only (architect's veto: no new component, agent, slash-command).

#### Scope

A **copy and labeling change** across the dashboard and select agent dispatch documentation that renames the worktree-traversal capability to **Sleipnir** in user-facing prose. No new code, no new component, no new slash command, no new agent.

Specific changes:

- The dashboard's Activity tab (per buildout B.1) adds a one-row status widget labeled **"Sleipnir's stables"** showing the current worktree list (read from `.claude/worktrees/`).
- Worktree-creation prose in agent docs (`plugins/ravenclaude-core/agents/*.md` where worktrees are mentioned) gets one inline label change: "I'll spawn an EnterWorktree call" → "I'll send Sleipnir to that branch." This is a docs/example change only; the underlying tool call is unchanged.
- A one-paragraph "Sleipnir" subsection in `plugins/ravenclaude-core/CLAUDE.md` under the worktree section.

ASCII form `sleipnir` in CLI (no diacritics; CLI form is identical to display form).

**Explicitly not in scope:**
- No `/sleipnir` slash command.
- No `Sleipnir` agent.
- No new dashboard tab; Sleipnir lives as a widget inside the existing Activity tab.

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — Activity tab adds the "Sleipnir's stables" row widget.
- `plugins/ravenclaude-core/CLAUDE.md` — one-paragraph subsection.
- `plugins/ravenclaude-core/agents/*.md` — update example dispatch prose in 3–5 agents (whichever currently mention worktrees explicitly).
- `plugins/ravenclaude-core/skills/new-worktree.md` — update opening prose, not the mechanics.

#### Steps

1. Grep `plugins/ravenclaude-core/agents/*.md` for "worktree" / "EnterWorktree" — identify the 3–5 places that explicitly mention worktrees in dispatch prose. Update inline prose only.
2. Update `skills/new-worktree.md`'s opening paragraph to mention Sleipnir as the labeling convention; do not change the skill's mechanics.
3. In `dashboard.html`, add the "Sleipnir's stables" row widget to the Activity tab (read `.claude/worktrees/` directory; show current worktree count + a link to the worktree-list view).
4. Document the convention in `plugins/ravenclaude-core/CLAUDE.md`: "Worktree traversal is named Sleipnir — Odin's eight-legged horse, capable of crossing realm boundaries safely. Use this label in dispatch prose to anchor the user's intuition; the underlying mechanism is `git worktree`."

#### Acceptance

- "Sleipnir's stables" row appears in the Activity tab.
- 3–5 agent docs have updated dispatch prose.
- No new slash commands, agents, or components were added (verify by code review).
- The convention is documented in CLAUDE.md.

#### Dependencies

- **Dashboard buildout B.1** (Activity tab) — hard.
- **P0.3** (ASCII discipline) — soft.

#### Effort

3–5 hours.

---

<a id="38-mimir"></a>

### 3.8 Mímir — narrative renames + guard rails

> Narrative-only renames in docs + dashboard labels (architect's gate). DO NOT rename `knowledge/` directories or `MEMORY.md` files (architect's gate). ASCII `mimir` in CLI (documentarian's gate). First-write disclosure + secret-redaction guard (security's gate).

#### Scope

A **prose / label rename** for two existing surfaces:

1. **Mímir's well** = the knowledge bank. The phrase "knowledge bank" / "knowledge files" is supplemented (not replaced) by "Mímir's well" in user-facing prose and dashboard labels. The directory `plugins/*/knowledge/` is **NOT** renamed.
2. **Mímir's head** = the memory subsystem. The phrase "memory" / "MEMORY.md" is supplemented by "Mímir's head" in user-facing prose. The file `MEMORY.md` is **NOT** renamed.

Plus two security guard rails on the memory subsystem (security's gate):

3. **First-write disclosure.** When a memory file is created for the first time (the agent writes to `MEMORY.md` or any `memory/*.md` file in an empty memory directory), prepend a one-paragraph disclosure: "**What does and does not belong in Mímir's head.** This file is conversational, persistent context — preferences, role, feedback. It is NOT for: secrets, credentials, API keys, JWTs, session tokens, or private data. Treat it as something a future Claude session will read."
4. **Secret-redaction pass on memory writes.** A pre-write check (in the Write/Edit tool path for memory files) scans new content for credential-shaped strings (AWS access key, OpenAI/Anthropic API key prefix, GitHub PAT prefix, SSH private-key fragment, JWT-shaped token, password-flag pattern) and refuses the write with a named error. Implementation: a new hook `plugins/ravenclaude-core/hooks/guard-memory-write.sh` that fires PreToolUse on Write/Edit when the target path matches `**/memory/*.md` or `MEMORY.md`.

ASCII forms in CLI: `mimir`, `mimir-well`, `mimir-head` (no diacritics).

**Explicitly not in scope:**
- No filesystem renames.
- No new slash command (`/mimir` is reserved as a future affordance, not built here).
- No new dashboard tab; Mímir labels live as captions on the existing Scenarios tab (buildout B.4.3) and the existing memory-bank UI.

#### Files touched

- `plugins/ravenclaude-core/CLAUDE.md` — narrative rename pass + "Mímir" subsection.
- `plugins/ravenclaude-core/skills/scenario-retrieval.md` — opening prose mentions Mímir's well.
- `AGENTS.md` — auto memory section adds one paragraph naming the convention.
- `plugins/ravenclaude-core/dashboard.html` — Scenarios tab label adds "(Mímir's well)" subtitle.
- `plugins/ravenclaude-core/hooks/guard-memory-write.sh` (new) — the secret-redaction pre-write guard.
- `plugins/ravenclaude-core/hooks/hooks.json` — register the new hook.
- `.claude/settings.json` — mirror the new hook in the dev-mirror block.
- New helper: `plugins/ravenclaude-core/hooks/tests/guard-memory-write/` — fixture tests.

#### Steps

1. **Narrative rename:**
   - In `plugins/ravenclaude-core/CLAUDE.md`, add a "Mímir — narrative naming" subsection. Two paragraphs: well = knowledge bank, head = memory subsystem.
   - In `AGENTS.md`, add one sentence under the auto-memory section.
   - In `skills/scenario-retrieval.md`, opening paragraph mentions: "The scenario bank is part of Mímir's well — deep, sometimes costly to consult, but the wisdom of past sessions."
   - In `dashboard.html`, Scenarios tab title becomes "Scenarios (Mímir's well)."
2. **First-write disclosure:**
   - The disclosure paragraph is appended to the **system-level memory writer prompt** (in the agent meta-skill that owns memory writes). Find: the auto-memory section in `AGENTS.md` or `plugins/ravenclaude-core/CLAUDE.md`. Add an instruction: "When creating `MEMORY.md` or any memory file for the first time, prepend the canonical disclosure paragraph."
   - Author the canonical disclosure paragraph in a new file `plugins/ravenclaude-core/templates/memory-disclosure.md` (allow-listed under `templates/**`).
3. **Secret-redaction guard:**
   - Author `guard-memory-write.sh` — bash script, fires PreToolUse on Write/Edit when `$CLAUDE_TOOL_FILE_PATH` matches `**/memory/*.md` or `MEMORY.md`. The script reads `$CLAUDE_TOOL_INPUT` (the proposed content), runs a regex sweep over known credential shapes, and exits non-zero with a named error if a match is found. Patterns sourced from `xc.secret-in-command` in `docs/tribunal-review-feature-design.md` §A.2. **⚠ VERIFY FIRST (2026-05-23 review): the hook input mechanism is unconfirmed.** Existing hooks (`enforce-layout.sh`, `guard-destructive.sh`) read tool input via a positional arg / stdin JSON — not necessarily via `$CLAUDE_TOOL_INPUT`/`$CLAUDE_TOOL_FILE_PATH` env vars. Instrument an existing PreToolUse hook with a known Write event and confirm exactly how proposed content is exposed before authoring this guard; if those env vars are empty, the redaction silently no-ops (reads empty → always passes). Use the confirmed mechanism in the acceptance criterion.
   - Register in `hooks/hooks.json` under `PreToolUse` with matcher `Write|Edit|MultiEdit`.
   - Mirror in `.claude/settings.json` per marketplace-dev convention.
4. Add fixture tests under `plugins/ravenclaude-core/hooks/tests/guard-memory-write/`:
   - One known-safe content fixture (no secrets) — expect exit 0.
   - One credential-shaped content fixture (e.g., `sk-ant-api03-...` pattern) — expect non-zero exit + named error.
5. Document the guard in `plugins/ravenclaude-core/CLAUDE.md`.

#### Acceptance

- The narrative renames appear in CLAUDE.md, AGENTS.md, scenario-retrieval.md, and dashboard.html.
- No directory rename occurred (verify: `plugins/*/knowledge/` and `MEMORY.md` paths are unchanged in the diff).
- The disclosure paragraph exists as a canonical template at `plugins/ravenclaude-core/templates/memory-disclosure.md`.
- `guard-memory-write.sh` exists, is executable, and is registered in both `hooks/hooks.json` and `.claude/settings.json`.
- The fixture tests pass: safe content allows the write; credential-shaped content rejects with a named error.
- The dashboard's Scenarios tab title includes "(Mímir's well)."

#### Dependencies

- **P0.3** (ASCII discipline) — hard.

#### Effort

8–12 hours.

---

<a id="39-yggdrasil"></a>

### 3.9 Yggdrasil — static then interactive marketplace tree

> Static diagram first (designer's gate — "ship a static structural diagram now"). Interactive view scoped sensibly per the override (architect's deferral caveat: "premature at 2 plugins"). Deferral caveat recorded in the spec.

> **User override.** The expert panel recommended deferring the interactive view to 5+ plugins (§8.1 Yggdrasil: architect's "Deny"). The user has overridden and asked it included. This spec honors the override by scoping the interactive view to **a minimum-viable visualization** that doesn't require maintenance at scale — it reads structure from the existing manifest data, no separate state, no hand-curated metadata. The architect's deferral concern (maintenance burden at low plugin count) is **recorded but not blocking**.

#### Scope

**Phase A (ships first, in Phase 6 of the master sequence):** A static structural diagram of the marketplace — a single SVG (preferred) or ASCII tree (fallback) showing:
- Root: `marketplace.json` (the trunk).
- Major branches: each `plugins/<plugin>/`.
- Twig nodes: each plugin's `agents/`, `skills/`, `hooks/`, `rules/`, `templates/`, `commands/`, `knowledge/` subdirectory (presence only; no counts).
- Three roots at the base, labeled: "Urðr (lessons)" → `plugins/*/scenarios/`, "Mímir (knowledge)" → `plugins/*/knowledge/`, "Hvergelmir (proposals)" → `docs/proposals/`. (The three Yggdrasil roots maps cleanly to the temporal triad — past, depth, future.)

The diagram is generated by `scripts/generate-yggdrasil-diagram.py` (new), checked into the repo as `docs/yggdrasil.svg`, and referenced from the README and the dashboard's Overview tab. Regeneration runs in CI on push to main; the committed file in main is the source of truth (deterministic generation per the [`cross-platform-determinism`](../plugins/ravenclaude-core/skills/cross-platform-determinism/SKILL.md) skill).

**Phase B (ships later, in Phase 10):** An **interactive** version of the same diagram in a new dashboard tab `#/yggdrasil`. Scoped sensibly:
- Reads the same data sources as the static diagram (no separate state).
- Click a plugin node → expand to show that plugin's agents/skills/hooks/rules counts.
- Hover the three root labels → show a count of items (e.g., "Urðr root: 23 scenarios across 6 plugins").
- **No editing.** Read-only view.
- **No animation, no auto-layout that re-flows.** Layout is deterministic; the same data produces the same layout every time.

ASCII form `yggdrasil` in CLI (no diacritics).

#### Files touched

**Phase A:**
- `scripts/generate-yggdrasil-diagram.py` (new) — SVG generator.
- `docs/yggdrasil.svg` (generated, committed).
- `README.md` — embed the SVG.
- `plugins/ravenclaude-core/dashboard.html` — Overview tab embeds the SVG.
- `.github/workflows/validate-layout.yml` — add a step to regenerate and diff `yggdrasil.svg` (fail if drift).

**Phase B:**
- `plugins/ravenclaude-core/dashboard.html` — new Yggdrasil tab + interactive renderer.
- `plugins/ravenclaude-core/dashboard-assets/yggdrasil.css` (new).
- `plugins/ravenclaude-core/dashboard-assets/yggdrasil-render.js` (new) — D3 or hand-rolled SVG renderer.

#### Steps

**Phase A:**
1. Author `generate-yggdrasil-diagram.py`. Read `marketplace.json` for the plugin list; for each plugin, list subdirectory presence under `plugins/<plugin>/`. Read `plugins/*/scenarios/` count, `plugins/*/knowledge/` count, `docs/proposals/` count.
2. Render as an SVG: trunk vertical line, branches off to each plugin, twigs off each branch for subdirectories, three roots at the bottom labeled with counts.
3. Determinism rules: sort plugins alphabetically; sort subdirectories in fixed order; use POSIX line endings; UTF-8 encoding; no embedded timestamps.
4. Commit `docs/yggdrasil.svg`. Add a CI gate: regenerate on push to main; if the regenerated file differs from the committed one, fail.
5. Embed in README.md (one section, one image, one paragraph caption).
6. Embed in the dashboard's Overview tab (the existing top-level dashboard view).

**Phase B:**
1. Port the SVG generator into a JS renderer (`yggdrasil-render.js`) that produces the same SVG client-side from the same data structure (the generator script and the JS renderer share a `tree_data.json` artifact, generated by the script and inlined by `generate-dashboards.py`).
2. Add the Yggdrasil tab to `dashboard.html`'s tab inventory. Tab title: "Yggdrasil." Subtitle: "Marketplace tree."
3. Add click-to-expand on plugin nodes (no fancy animation; expand-collapse is instant).
4. Add hover-to-show on root labels (a small tooltip with counts).
5. Verify deterministic layout: the same data produces the same node positions every render.

#### Acceptance

**Phase A:**
- `docs/yggdrasil.svg` exists, committed, valid SVG, viewable in a browser.
- README displays the diagram.
- Dashboard Overview tab displays the diagram.
- CI fails if `yggdrasil.svg` drifts from the regenerated version.

**Phase B:**
- The Yggdrasil tab renders the interactive diagram at `#/yggdrasil`.
- Clicking a plugin node expands to show subdirectory counts.
- Hovering a root label shows item counts.
- Layout is deterministic across renders (same data → same SVG output).
- No edit affordances exist.

#### Dependencies

- **P0.3** (ASCII discipline) — soft.
- **Cross-platform-determinism skill** (already exists) — hard for the SVG generator.

#### Effort

4–6 hours (Phase A). 16–20 hours (Phase B).

---

<a id="310-ragnarok"></a>

### 3.10 Ragnarök — `/reset-plugin-cache` with full DR gates

> Primary command `/reset-plugin-cache` (architect's gate — instrumental name, won't be misread as a stunt). `/ragnarok` is alias (documentarian's compromise). Atomic-swap mandatory (QA gate). Dry-run flag mandatory (QA + architect gate). User-only invocation (security gate). Pinned-SHA reinstall (security gate). `MEMORY.md` survives (security gate).

#### Scope

A new slash command `/reset-plugin-cache` (primary, ASCII) with alias `/ragnarok` (themed) that performs a disaster-recovery reset of a plugin's cache:

1. **Dry-run mode** (default): enumerate what would be touched. Print the inventory; do nothing.
2. **Execute mode** (with `--execute` flag and explicit confirmation): perform the reset.

Execute mode steps (in order, with atomic-swap semantics):
1. **Snapshot.** Read the current plugin cache location (e.g., `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`) into a temp directory `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>-snapshot-<timestamp>/`.
2. **Fetch fresh.** Pull the marketplace at a **user-named commit SHA** (security gate — no floating `head`) into a sibling temp directory. The SHA is a required argument: `/reset-plugin-cache <plugin> --execute --pin <sha>`.
3. **Verify fresh.** Run `audit-gates.sh` against the fresh tree. If any fail, abort; the original cache is untouched.
4. **Atomic swap.** Rename the existing cache to `<version>-pre-ragnarok-<timestamp>`, rename the fresh tree to the canonical location. (Two renames are the closest portable POSIX has to atomic; on Windows the second rename may fail if any process has a file handle open — abort and roll back the first rename.)
5. **Verify swap.** Confirm the new cache loads (`/reload-plugins` smoke test; user is asked to confirm in their session).
6. **Preserve `MEMORY.md`.** The command never touches `~/.claude/projects/<encoded-project-path>/memory/` — the memory directory lives outside the plugin cache and is explicitly excluded from the reset.
7. **Audit snapshot.** Write a JSON record at `.ravenclaude/runs/<session-id>/ragnarok-<timestamp>.json` documenting: what plugin, what SHA, what version, what was preserved, where the pre-reset snapshot lives. **Never exfiltrated** — stays in the user's project.

**Security invariants (hard ship gates):**

- **⚠ VERIFY BEFORE BUILDING (2026-05-23 review): `$CLAUDE_INVOCATION_SOURCE` is an unverified env var** — it appears nowhere in the current codebase or the hooks schema, yet Ragnarök's _entire_ user-only security gate rests on it. If it is absent/empty at runtime, `"" != "user"` is TRUE and the command refuses **every** invocation (including the user's own); if it's simply unset for agents too, the gate is a silent no-op. Confirm the variable exists and carries the expected values (echo it from a trivial slash command) BEFORE spending Phase-7 hours; if it does not exist, document an alternative mechanism (a sentinel file written by the slash-command dispatcher, or a required interactive `yes` reply) and update these acceptance criteria accordingly.
- The command **rejects non-interactive invocation.** If `$CLAUDE_INVOCATION_SOURCE != "user"` (i.e., the command was called by an agent, not the user typing it), the command exits with a named error `RAGNAROK_NOT_USER_INVOKED`. **Register `non-interactive-ragnarok-invocation` as a Fenrir-bound entry in `dashboard-schema.json` *as part of this phase* (Phase 7)** — the entry isn't added retroactively in Phase 2 because the command doesn't exist yet then. The Fenrir invariant from Phase 2 (security_deny-cannot-be-locally-overridden) immediately applies to the newly-registered entry on landing.
- Reinstall pins to a user-named SHA. No `marketplace HEAD` fallback.
- `MEMORY.md` and `~/.claude/projects/.../memory/` are excluded from the reset.
- Dry-run is the default; execute requires explicit `--execute` flag.
- The pre-reset snapshot is preserved for 30 days (Ragnarök's "world reborn from what was preserved" — Líf and Lífþrasir slept through the fire and walked out into the green world).

ASCII forms in CLI: primary `reset-plugin-cache`, alias `ragnarok`. The themed copy is one-line — a kenning in the help text, not a label in error messages.

#### Files touched

- `plugins/ravenclaude-core/commands/reset-plugin-cache.md` (new) — primary command.
- `plugins/ravenclaude-core/commands/ragnarok.md` (new) — thin alias that documents the primary.
- `plugins/ravenclaude-core/scripts/reset-plugin-cache.py` (new) — the actual reset logic.
- `plugins/ravenclaude-core/scripts/_ragnarok-named-errors.json` (new).
- `plugins/ravenclaude-core/dashboard-schema.json` — add `non-interactive-ragnarok-invocation` to `fenrir_bound[]` and to `security_deny`.
- `plugins/ravenclaude-core/CLAUDE.md` — document the command with explicit "high blast radius" callout.
- `AGENTS.md` — add to slash-command list.
- `plugins/ravenclaude-core/scripts/tests/reset-plugin-cache/` — fixture tests for dry-run, atomic-swap, abort-on-fresh-failure, user-invocation rejection.

#### Steps

1. Author `reset-plugin-cache.py`:
   - Argument parsing: `<plugin>` (required), `--execute` (flag, default false), `--pin <sha>` (required when --execute), `--ttl-days <int>` (default 30, for snapshot retention).
   - Detect `$CLAUDE_INVOCATION_SOURCE`. Refuse if not `user`.
   - Implement the 7-step execute flow above with atomic-swap.
   - On any abort, restore from snapshot (renames in reverse).
   - Emit the audit JSON record.
   - Print a clear summary on success / failure.
2. Author `_ragnarok-named-errors.json` — at minimum: `RAGNAROK_NOT_USER_INVOKED`, `RAGNAROK_FRESH_TREE_GATES_FAILED`, `RAGNAROK_ATOMIC_SWAP_PARTIAL`, `RAGNAROK_SHA_NOT_FOUND`, `RAGNAROK_PLUGIN_NOT_INSTALLED`.
3. Author `reset-plugin-cache.md` slash command. Body:
   - One-paragraph explanation with the kenning ("In Ragnarök the old world burned; what survived rebuilt better. This command performs an analogous reset of a plugin's cache. Use only when the cache is genuinely broken — verify dry-run output before executing.").
   - Required-confirmation flow: the command always prints the dry-run output first; the user must re-invoke with `--execute --pin <sha>` to actually run.
   - Security invariants listed inline.
4. Author `ragnarok.md` — a one-paragraph alias pointing to the primary, with the themed name as the heading.
5. Add the Fenrir entry (per 3.4) marking non-interactive Ragnarök invocation as Fenrir-bound.
6. Add fixture tests:
   - Dry-run on a non-existent plugin → returns NOT_INSTALLED error.
   - Dry-run on a real plugin → enumerates what would be touched; doesn't move files.
   - Execute on a real plugin with a valid SHA → performs the swap; original cache moves to snapshot path.
   - Execute when the fresh tree's gates fail → aborts; original cache untouched.
   - Invocation when `$CLAUDE_INVOCATION_SOURCE = agent` → refuses.
   - `MEMORY.md` survival test: confirm the memory directory is untouched after a real swap.
7. Document the command's blast radius in CLAUDE.md under a "High-blast-radius commands" callout.

#### Acceptance

- `/reset-plugin-cache <plugin>` without `--execute` prints a dry-run inventory.
- `/reset-plugin-cache <plugin> --execute --pin <sha>` performs the atomic swap.
- A failed fresh-tree audit aborts the swap; original cache is untouched.
- A non-user invocation refuses with `RAGNAROK_NOT_USER_INVOKED`.
- `MEMORY.md` is preserved across a real run.
- The audit JSON record exists in `.ravenclaude/runs/<session-id>/`.
- The pre-reset snapshot exists at the expected timestamped path for the TTL.
- All 6 fixture tests pass.

#### Dependencies

- **3.4 Fenrir** — hard. The `non-interactive-ragnarok-invocation` Fenrir entry is the enforcement mechanism for the user-only invariant.
- **P0.3** (ASCII discipline) — hard.

#### Effort

18–24 hours.

---

<a id="311-vidarr"></a>

### 3.11 Víðarr — posture/security event-log panel

> Soft rescue from the skip list, contingent on the posture/security event log surfacing as a named UI panel (§8.2).

#### Scope

A new collapsible section in the dashboard's Settings tab (or, if it grows past ~50 events, its own subtab under Settings) labeled **"Posture & security event log"** with the Norse sub-name **"Víðarr's shoe"** in parentheses. The panel:

- Reads `.ravenclaude/posture-events.jsonl` (per P0.4) and `hook-events.jsonl` (per P0.2) filtered for `security_deny`-related and Fenrir-related events.
- Renders events as a chronological table: timestamp, event type, category, summary, source.
- Provides filters: time range (last 24h / 7d / 30d / all), event type (posture change / security_deny match / Fenrir override rejection / hook deny).
- Read-only mirror — the panel surfaces what existed; no editing or dismissing.
- One myth-cite in the section's intro: "Víðarr's shoe was assembled from leather scraps across all of time. This log is the same — small events accumulating against the day someone needs to know exactly what happened."

ASCII form `vidarr` in CLI (no diacritics; no CLI command in v1).

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — Settings tab adds the "Posture & security event log (Víðarr's shoe)" collapsible section.
- `plugins/ravenclaude-core/dashboard-assets/vidarr.css` (new).
- `scripts/generate-dashboards.py` — read both jsonl sources, inline into `window.__vidarr`.
- `plugins/ravenclaude-core/CLAUDE.md` — document the panel.

#### Steps

1. Verify P0.2 and P0.4 are shipped (the two event-log substrates).
2. Author `vidarr.css` — chronological-table layout, filter chips, plain-language column headers.
3. Add the collapsible section to the Settings tab. Default collapsed.
4. Implement the data reader in `generate-dashboards.py`: read last 30 days of `posture-events.jsonl` + `hook-events.jsonl` filtered for security-relevant events (Fenrir rejections, `security_deny` matches, layout violations). Inline into `window.__vidarr`.
5. Implement filter UI: time range select, event-type chips.
6. Add the myth-cite to the section intro.
7. Empty state: "No security events. Your perimeter has been quiet."

#### Acceptance

- The panel renders in the Settings tab with the chronological event table.
- Filters work (time range + event type).
- The panel is read-only (no edit/dismiss affordances).
- A controlled fixture (one `security_deny` event in `posture-events.jsonl`) appears in the panel.
- The empty state renders when both jsonl files are empty for the selected range.
- The myth-cite appears in the section intro.

#### Dependencies

- **P0.2** (hook events) — hard.
- **P0.4** (posture-event emission) — hard.
- **P0.3** (ASCII discipline) — soft.

#### Effort

10–14 hours.

---

<a id="312-nidhoggr"></a>

### 3.12 Níðhöggr — minimal-scope debt-watch panel

> User-overridden; expert verdict was "deny" (architect: premature at 2 plugins; documentarian: net-negative name). User has overridden and asked it included. Scoped minimally per the panel guidance ("when the panel lands, prefer a plain name 'debt watch' OR fold into Skuld in the Norns panel"). This spec ships **a minimal debt-watch panel with both labels visible** — "Debt watch" as the primary plain-language label and "Níðhöggr" as the parenthetical Norse name — and folds *some* content into Norns' Skuld column.

#### Scope

A small, low-maintenance debt-watch surface composed of two parts:

1. **A "Debt watch" card** inside Heimdall's tab (3.1) — surfaces a handful of marketplace-wide debt signals, each easy to compute:
   - Plugins not bumped in ≥120 days (read from `git log -1 -- plugins/<plugin>/.claude-plugin/plugin.json`).
   - Hook scripts without a corresponding CI gate (cross-check `plugins/*/hooks/*.sh` against `.github/workflows/*.yml` references).
   - Superseded decision-log entries (entries in `docs/decisions/` whose successor exists — detected via a `supersedes:` frontmatter field, if present; else absent).
   - Open TODOs in commit messages (`git log --all --format="%H %s" | grep -i todo`).
2. **A subtitle on the card**: "Debt watch (Níðhöggr)" — the plain name is primary; the themed name is parenthetical.

ASCII form `nidhoggr` in CLI (no diacritics; no CLI command in v1).

**Minimal scope.** No new dashboard tab. No standalone Níðhöggr surface. No backlog management. The card surfaces signals; remediation happens through normal PR flow.

The deferral caveat is recorded: "Reconsider at 5+ plugins. Today this is a low-noise watch card; if the marketplace grows past ~5 plugins or debt signals exceed ~20 entries, promote to a dedicated tab and revisit the name."

#### Files touched

- `plugins/ravenclaude-core/dashboard.html` — Heimdall tab gains a "Debt watch (Níðhöggr)" card.
- `plugins/ravenclaude-core/dashboard-assets/nidhoggr.css` (new) — small additions, shared with Heimdall.
- `scripts/generate-dashboards.py` — read the four signals, inline into `window.__nidhoggr`.
- `plugins/ravenclaude-core/CLAUDE.md` — document the panel + the deferral caveat.

#### Steps

1. Wire the four signal readers in `generate-dashboards.py`:
   - `git log -1 --format=%cI -- plugins/<plugin>/.claude-plugin/plugin.json` per plugin → compare to 120 days ago.
   - For each `plugins/*/hooks/*.sh`, grep all `.github/workflows/*.yml` for the hook's filename — flag if no reference.
   - Scan `docs/decisions/*.md` frontmatter for `supersedes:` references; flag the superseded entry.
   - `git log --all --format="%H %s" | grep -i -E "(TODO|FIXME)" | head -10`.
2. Add the card to the Heimdall tab. Title: "Debt watch (Níðhöggr)." Subtitle: "Slow-rotting bits at the foundations."
3. Render each signal as a small section within the card, with counts + click-to-expand list.
4. Document the deferral caveat in `plugins/ravenclaude-core/CLAUDE.md`: "Níðhöggr is currently a small card inside Heimdall. If marketplace plugin count grows past ~5 or debt signals exceed ~20 entries, promote to a dedicated tab."

#### Acceptance

- The card renders in the Heimdall tab.
- All four signal readers populate with current data (or render empty-state per signal).
- The "Debt watch" primary label is visible; "Níðhöggr" appears as the parenthetical.
- The deferral caveat is documented.

#### Dependencies

- **3.1 Heimdall** — hard. The card lives inside the Heimdall tab.
- **P0.3** (ASCII discipline) — soft.

#### Effort

8–12 hours.

---

<a id="4-master-sequence"></a>

## 4. Master sequence — phased roadmap

Phases group the 12 features by sequential dependency. Each phase has an entry condition (what must be true to start) and an exit condition (what must be true to ship). Phases ship as one or more minor releases of `ravenclaude-core`.

### Phase 0 — Prerequisites (12–17 h)

**Entry.** Main green; ravenclaude-core ≥ 0.17.0; dashboard buildout Phase A in flight.

**Contents.**
- P0.1 — manifest `next_version` / `roadmap` field.
- P0.2 — hooks emit machine-readable deny logs.
- P0.3 — ASCII-form discipline rule in AGENTS.md.
- P0.4 — posture-script audit-event emission.
- P0.5 — confirm Gleipnir six-axis decomposition (memo).
- P0.6 — `events.jsonl` emission in scenario-retrieval (verify or land).

**Exit.** All 6 tasks merged; gate-audit passes; one combined release `ravenclaude-core 0.18.0` records the prerequisite work.

### Phase 1 — Perimeter watch + release reporter + posture framing (22–34 h)

**Entry.** Phase 0 exit met.

**Contents.**
- **3.1 Heimdall** — perimeter-alarm surface.
- **3.2 Mjölnir** — release-readiness reporter.
- **3.3 Gleipnir (docs portion only)** — posture-as-binding docs rename.

**Rationale.** Heimdall is the architect's "build first" pick (most-approved, most consensus). Mjölnir is the next-cheapest direct-value win (reduces real maintainer toil). Gleipnir docs work is cheap (4–6 h) and unblocks Fenrir in Phase 2.

**Gleipnir viz portion (conditional, optional micro-phase between Phase 1 and Phase 2).** If P0.5's six-axis memo confirms a clean mapping, the binding-health bar (3.3 Phase B) ships as an 8–12 hour addition. If the memo finds the mapping doesn't hold, the viz is descoped and Phase 1 exits with docs-only. Either outcome unblocks Fenrir; the viz is decoration, not a Fenrir prerequisite.

**Exit.** Heimdall tab live with all four cards + Gjallarhorn tiered banner. `/mjolnir` reports release-readiness without committing/pushing. Gleipnir framing exists in `set-posture.md` and CLAUDE.md. Ships as `ravenclaude-core 0.19.0` (docs-only path) or `ravenclaude-core 0.19.0` + `0.19.1` (with viz).

### Phase 2 — Posture invariants (8–12 h)

**Entry.** Phase 1 exit met; Gleipnir docs are in place; Fenrir's myth-cite reads as anchored, not arbitrary.

**Contents.**
- **3.4 Fenrir** — bound-danger lane with security_deny-cannot-be-locally-overridden invariant.

**Exit.** `dashboard-schema.json` has `fenrir_bound[]`; the translator enforces the invariant; the Settings-tab Fenrir lane renders. Ships as `ravenclaude-core 0.20.0`.

### Phase 3 — Temporal lineage (12–16 h)

**Entry.** Phase 0 P0.1 + P0.6 shipped; Phase 2 exit met (not strictly necessary, but reduces dashboard-edit conflicts).

**Contents.**
- **3.5 Norns** — Urðr / Verðandi / Skuld lineage section.

**Exit.** "Plugin lineage (The Norns)" collapsible section renders in the Settings tab with Urðr + Verðandi populated; Skuld populated where `next_version` is declared, gated empty state elsewhere. Ships as `ravenclaude-core 0.21.0`.

### Phase 4 — Install bridge (10–14 h)

**Entry.** Phase 3 exit met; dashboard buildout B.3 either deferred (B.3 folds into Bifröst here) or coordinated with this phase.

**Contents.**
- **3.6 Bifröst** — install-bridge 4-step wizard.

**Exit.** Install tab at `#/install` (alias `#/bifrost`) renders the 4-step wizard with copy-buttons + verification + failure-mode accordion. Ships as `ravenclaude-core 0.22.0`.

### Phase 5 — Cheap copy + narrative renames (11–17 h)

**Entry.** Phase 4 exit met. (These features touch agent prose and dashboard labels; doing them after the main tabs land minimizes label churn.)

**Contents.** (Run in parallel — no internal dependencies.)
- **3.7 Sleipnir** — worktree label convention (3–5 h).
- **3.8 Mímir** — narrative renames + guard rails (8–12 h).

**Exit.** "Sleipnir's stables" row exists in Activity tab; agent prose updated. Mímir's well / Mímir's head naming exists in CLAUDE.md, AGENTS.md, scenarios skill, and dashboard label. `guard-memory-write.sh` is registered and tested. Ships as `ravenclaude-core 0.23.0`.

### Phase 6 — Static marketplace tree (4–6 h)

**Entry.** Phase 5 exit met.

**Contents.**
- **3.9 Yggdrasil Phase A** — static SVG/ASCII tree diagram.

**Exit.** `docs/yggdrasil.svg` committed and rendering in README + dashboard Overview; CI regeneration gate active. Ships as `ravenclaude-core 0.24.0`.

### Phase 7 — Disaster recovery (18–24 h)

**Entry.** Phase 2 exit met (Fenrir's `security_deny`-cannot-be-locally-overridden invariant is what enforces user-only Ragnarök invocation). Phase 5 exit recommended (Mímir narrative is in place so the "MEMORY.md survives" gate maps to a named concept).

**Contents.**
- **3.10 Ragnarök** — `/reset-plugin-cache` with full DR gates.

**Exit.** `/reset-plugin-cache` (primary) + `/ragnarok` (alias) ship with: dry-run default, atomic-swap, user-only invocation, pinned-SHA reinstall, `MEMORY.md` survival, audit JSON record, fixture tests. Ships as `ravenclaude-core 0.25.0`.

### Phase 8 — Rescued surface (10–14 h)

**Entry.** Phase 2 exit met (Fenrir emits posture events that Víðarr surfaces). Phase 7 exit recommended but not blocking (Ragnarök contributes events to the same log, which makes Víðarr's panel more populated and more useful, but the panel renders meaningfully on Fenrir's events alone).

**Contents.**
- **3.11 Víðarr** — posture/security event-log panel.

**Exit.** "Posture & security event log (Víðarr's shoe)" panel renders in Settings tab with chronological table + filters + myth-cite. Ships as `ravenclaude-core 0.26.0`.

### Phase 9 — User-overridden additions (24–32 h)

**Entry.** Phase 8 exit met. (Defer overridden features until everything the expert panel approved-with-changes has shipped; that way the override stack is single-feature scope rather than cascading scope.)

**Contents.** (Parallel — independent. Yggdrasil-B needs Yggdrasil-A from Phase 6 but not Níðhöggr; Níðhöggr needs Heimdall from Phase 1 but not Yggdrasil-B.)
- **3.9 Yggdrasil Phase B** — interactive marketplace tree (16–20 h).
- **3.12 Níðhöggr** — minimal-scope debt-watch panel (8–12 h).

**Exit.** Yggdrasil tab renders the interactive tree (read-only; deterministic layout). Heimdall tab gains a "Debt watch (Níðhöggr)" card with four signal readers. Ships as `ravenclaude-core 0.27.0` (interactive Yggdrasil) and `ravenclaude-core 0.28.0` (Níðhöggr card). Both could ship in a single 0.27.0 if appetite allows.

### Total: 11 phases (Phase 0 + 1–9; Phase 1.5 conditional), 131–186 hours

The full sequence ships across roughly 10–11 minor `ravenclaude-core` releases. At a steady single-maintainer pace of 8–10 hours/week of focused build time, that's ~16–24 weeks (4–6 months). Faster on focused sprints.

> **Delivery realism (2026-05-23 PM review).** The 8–10 h/week figure is optimistic: Matt is a solo, non-developer owner whose paid consulting + the marketing-website build compete for the same hours. At a realistic 2–4 h/week with consulting active, the full plan is **8–18 months**, not 4–6. Treat this as a backlog with a hard off-ramp, not a commitment:
>
> | Stop after | What's live | What's parked |
> |---|---|---|
> | **Phase 1** (Heimdall + Mjölnir + Gleipnir docs) | The single highest-value operator surface | Everything Phase 2+; the plugin is fully usable as-is |
> | **Phase 3** (+ Fenrir, Norns) | Posture safety invariant + past/present panel | Bifröst, Sleipnir, Ragnarök, Yggdrasil, Níðhöggr |
> | **Phase 7** (+ Bifröst, Mímir, Ragnarök) | The DR/reset workflow + knowledge naming | Yggdrasil-interactive + Níðhöggr (the two user-override features) |
>
> **Capacity check (fill in before starting):** realistic weekly hours = ____; Phase 0+1 done by ____; full plan by ____. **Retrospective checkpoints:** after Phase 3 and after Phase 6, compare hours-spent vs estimated and decide continue / descope Phase 9 / pause. **Schedule risks (belong in §5a):** R-sched-1 — consulting pipeline absorbs hours (likelihood H, impact H); R-sched-2 — PR #69 dashboard-buildout scope expands and absorbs Phase 1–5 budget (M/M). **Sequencing warning:** the two user-override features (Yggdrasil-interactive, Níðhöggr) sit last and may never ship under this order — if they matter, re-prioritize them earlier or accept they're the first to be cut.

---

<a id="5-cross-feature-dependency-graph"></a>

## 5. Cross-feature dependency graph

> **External dependency (2026-05-23 review): PR #69 (dashboard build-out, `dashboard-buildout-plan.md` Phase A) is a prerequisite node, not just prose.** Fenrir (3.4) and Víðarr (3.11) lean on the `network_read` + `security_deny` categories and the dashboard surfaces that #69 Phase A lands. **Phase 2 and Phase 8 entry condition:** #69 Phase A is merged to main AND its category names (`network_read`, `security_deny`) are verified against this plan's references — if #69 renamed them, update the Fenrir/Víðarr specs first.

```
                                  ┌──────────────────────────────────────────┐
                                  │              Phase 0 — Prereqs            │
                                  │                                          │
                                  │  P0.1 manifest next_version              │
                                  │  P0.2 hook machine-readable logs         │
                                  │  P0.3 ASCII discipline (AGENTS.md)       │
                                  │  P0.4 posture-event jsonl                │
                                  │  P0.5 Gleipnir six-axis memo             │
                                  │  P0.6 scenario-retrieval events emit     │
                                  └─────────┬────────────────────────────────┘
                                            │
                                            │
              ┌─────────────────────────────┼─────────────────────────────────┐
              │                             │                                 │
              ▼                             ▼                                 ▼
       ┌──────────────┐             ┌──────────────┐                 ┌──────────────┐
       │ 3.1 HEIMDALL │             │ 3.2 MJÖLNIR  │                 │ 3.3 GLEIPNIR │
       │  needs: P0.2 │             │  needs: P0.3 │                 │  needs: P0.5 │
       └──────┬───────┘             └──────────────┘                 └──────┬───────┘
              │                                                              │
              │                                                              │
              ▼                                                              ▼
   ┌──────────────────┐                                              ┌──────────────┐
   │ 3.12 NÍÐHÖGGR    │                                              │ 3.4 FENRIR   │
   │  card in Heimdall│                                              │  needs: 3.3  │
   │  needs: 3.1      │                                              └──────┬───────┘
   └──────────────────┘                                                     │
                                                                            │
                                                                            ▼
                                                                  ┌──────────────────┐
                                                                  │  3.10 RAGNARÖK   │
                                                                  │  needs: 3.4      │
                                                                  └──────────────────┘
              ┌──────────────┐             ┌──────────────┐
              │  3.5 NORNS   │             │ 3.6 BIFRÖST  │
              │ needs P0.1+6 │             │   needs P0.3 │
              └──────────────┘             └──────────────┘

              ┌──────────────┐             ┌──────────────┐
              │ 3.7 SLEIPNIR │             │  3.8 MÍMIR   │
              │   needs B.1  │             │   needs P0.3 │
              └──────────────┘             └──────────────┘

              ┌──────────────┐             ┌──────────────┐
              │ 3.9 YGGDRASIL│             │ 3.11 VÍÐARR  │
              │   Phase A    │             │ needs P0.2+4 │
              │   (static)   │             └──────────────┘
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ 3.9 YGGDRASIL│
              │   Phase B    │
              │ (interactive)│
              └──────────────┘
```

**Critical path** (longest dependency chain to a shippable end state):

`P0.3 → 3.3 Gleipnir docs → 3.4 Fenrir → 3.10 Ragnarök` (≥ 32–46 hours).

Heimdall + Mjölnir + Norns + Bifröst + Mímir + Sleipnir + Yggdrasil-static + Víðarr can all proceed off the critical path. The plan groups them into Phases 1, 3, 4, 5, 6, 8 to flatten the actual delivery schedule below the critical path's length.

---

<a id="5a-risks"></a>

## 5a. Top risks (and their mitigations)

The 12 features compose into a larger system; the risks below are the ones that span phases and could derail the sequence. Per-feature risks are recorded inline in §3.

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Dashboard.html merge conflicts** between this plan and the parallel dashboard-buildout PR (#69). | H | M | Coordinate via a documented merge order (buildout PR first, then norse-feature PR) and rebase weekly. Phases 1–6 of this plan touch the same regions of `dashboard.html` as buildout Phase B; if buildout B sequencing slips, this plan's Phase 5 onward (when it touches Settings tab) must accept a 1–2 week pause. |
| R2 | **P0.5's six-axis memo finds the mapping doesn't hold** — Gleipnir viz is descoped but the architect's "only worth it if six axes map" gate also bears on the docs portion. | M | M | The docs portion still ships if the mapping is partial (the metaphor is a useful frame even with rough edges). Only if the memo finds the mapping is *materially misleading* should the docs portion descope too. Author the memo cautiously: "good enough" mapping is sufficient for docs; only the viz needs clean six-axis decomposition. |
| R3 | **Heimdall's hook-event card appears empty** on a freshly-installed dashboard (no sessions have fired yet → no `hook-events.jsonl` files). User assumes the feature is broken. | M | M | Ship a clear empty state with copy: "No hook events yet. The first session that triggers a hook (e.g., a layout violation) will populate this view." Plus a "Generate a test event" affordance in dev-only mode that fires a known-safe deny for demonstration. |
| R4 | **Ragnarök's atomic-swap fails partially on Windows** (file handle held by Claude Code or the dashboard) — first rename succeeds, second fails, cache is in an inconsistent state. | M | H | The script detects partial-swap and rolls back the first rename. A safety net: before any rename, verify no process holds a handle to the cache files (best-effort; on Windows use `handle.exe` if available, else accept a small risk window). The 30-day snapshot retention is the ultimate recovery substrate. |
| R5 | **The themed copy reads as cringe** to certain users / teams who would rather see plain labels. | M | L | Every themed surface honors the dashboard's `huginn_muninn.theme` setting (per the buildout B.3.1.3). When set to `plain`, all 12 features' themed labels swap to plain alternatives. Set up the `STRINGS_NORSE` / `STRINGS_PLAIN` table in dashboard.html at the same time as Phase 1 ships. |
| R6 | **`scenario-retrieval` events emission (P0.6) lands later than expected**, blocking Norns Urðr column. | M | M | P0.6 is included as a verify-or-land step; if PR #71's Phase 0 work shipped, P0.6 is a no-op. If not, this plan ships it. Both paths converge on the same emission contract. |
| R7 | **The user override on Yggdrasil interactive (3.9 Phase B) ages poorly** — the architect's concern about premature complexity at 2 plugins is real if the marketplace stays at 2 plugins through Phase 9. | M | L | The interactive tab uses the same data source as the static SVG, so the maintenance cost is bounded. Worst case: it's a polished tab that's underwhelming until plugin count grows. Acceptable trade. |
| R8 | **Memory write guard (`guard-memory-write.sh`) has false positives** — blocks legitimate writes that incidentally contain credential-shaped substrings. | M | M | Patterns are conservative (look for known prefixes like `sk-ant-`, `ghp_`, `AKIA`, JWT 3-segment with `eyJ` prefix). The regex file is version-controlled and editable (Q9). On a false positive, the user can move the offending text out of the memory file (a feature, not a bug). |
| R9 | **Heimdall + Víðarr surface overlapping data** — both show hook events from `hook-events.jsonl`. The user can't tell which is canonical. | L | L | Heimdall surfaces *all* hook events as recency/severity-sorted operational signal; Víðarr surfaces *only security-relevant* events in chronological audit-trail form. The framing is different — operations vs forensics. Document the distinction in both feature's intro paragraphs. |
| R10 | **`/mjolnir` reports false-greens** because one of its checks misses a real issue (e.g., the layout check doesn't catch a path that passes the glob but is misplaced). | L | M | Per-check fixture tests (one known-good, one known-bad) catch this at CI time. Add a quarterly review: are there release-readiness signals not yet in Mjölnir? If yes, add them. |
| R11 | **Phase 0 sprawls** — the six prerequisites each look small but interact with multiple consumers (CI, scripts, hooks, manifest validator), and shipping them takes much longer than 12–17 hours. | M | M | Ship Phase 0 as 2–3 small PRs rather than one combined PR. Each PR is independently reviewable. If a prereq hits unexpected complexity, the others still ship. The plan's Phase 1 entry condition is satisfied incrementally. |
| R12 | **GitHub Pages caching delays** mean a refreshed dashboard with new Heimdall content isn't visible for up to 10 minutes after main is updated. | L | L | Accept the latency. Document in CLAUDE.md: "GitHub Pages takes up to 10 minutes to reflect main; for immediate verification use `scripts/serve-dashboards.py`." |

---

<a id="6-consolidated-open-questions"></a>

## 6. Consolidated open questions

These need resolution before or during execution. Marked **B** = block phase entry, **W** = should answer during the relevant phase but not blocking entry.

| # | Question | Phase | Block? | Provisional answer |
|---|---|---|---|---|
| Q1 | Does the posture YAML decompose into exactly six axes (Gleipnir ingredients)? | Phase 0 (P0.5) | **B** for Gleipnir viz; **W** for docs | Author the P0.5 memo first; descope viz if mapping fails. |
| Q2 | How does the dashboard read `ci-status.json` if the dashboard is served from GitHub Pages and CI writes to a branch? | Phase 1 | **B** | Resolve as: dashboard JS fetches `https://api.github.com/repos/.../actions/runs` directly at panel load. Avoids bot-commit complexity. |
| Q3 | Where does Mímir's first-write disclosure get appended? At the system-level memory writer, or per-write inside the file? | Phase 5 | **B** | At the system-level memory writer prompt instruction in `AGENTS.md` / `CLAUDE.md` auto-memory section. Concretely: edit the existing "How to save memories" subsection in `CLAUDE.md` to instruct, "If `MEMORY.md` does not yet exist, the first write prepends the contents of `plugins/ravenclaude-core/templates/memory-disclosure.md`." The agent reads the template at write-time and includes it verbatim. Subsequent writes append below the disclosure without modifying it. |
| Q4 | Should Ragnarök's snapshot retention (30 days) be configurable? | Phase 7 | **W** | Yes, via `--ttl-days <int>` flag. Default 30. |
| Q5 | Does the Norns Skuld column read `docs/proposals/` directly or via a generated index? | Phase 3 | **W** | Direct grep of `docs/proposals/*.md` filenames matching the plugin name. Cheap enough; no index needed at current scale. |
| Q6 | Should the Gjallarhorn red-tier banner block dashboard interaction, or just be visually loud? | Phase 1 | **B** _(re-triaged 2026-05-23: affects Phase-1 acceptance; resolve at phase entry, not mid-build)_ | Visually loud + `aria-live="assertive"`; does NOT block interaction. The user may need to navigate to see what fired. |
| Q7 | Does Heimdall's version-drift check live in `generate-dashboards.py` or in a separate `check-version-drift.py` script? | Phase 1 | **W** | Inside `generate-dashboards.py` for v1 (no separate script needed). If multiple features need it later, extract. |
| Q8 | Should Yggdrasil Phase B (interactive) use D3 or a hand-rolled SVG renderer? | Phase 9 | **W** | Hand-rolled. Adding a D3 dependency for one tab is overkill; the data shape is small (<100 nodes) and the layout is deterministic. |
| Q9 | Is the secret-redaction pattern set in `guard-memory-write.sh` versioned/extensible? | Phase 5 | **B** _(re-triaged 2026-05-23: affects Phase-5 acceptance + the hook's file layout; resolve at phase entry)_ | Yes — patterns live in `plugins/ravenclaude-core/hooks/_secret-patterns.regex` (allow-listed under `hooks/**`), one regex per line. Hook reads the file. Add a regex-DoS (catastrophic-backtracking) time-bound test on a large synthetic input. |
| Q10 | What happens to the dashboard if a consumer is on an older `ravenclaude-core` and the marketplace updates with a new tab? | Cross-cutting | **W** | The dashboard is rendered per-plugin-version; older versions show older tab sets. No back-compat concern. Document in CLAUDE.md release-notes section. |
| Q11 | Does Mjölnir's reporter need a flag to suppress themed copy and emit plain text only? | Phase 1 | **B** _(re-triaged 2026-05-23: affects Phase-1 acceptance)_ | Yes — `/release-check <plugin> --plain` (alias `/mjolnir`) emits plain text. Default is themed unless `huginn_muninn.theme: plain` is set in the dashboard. |
| Q12 | Does the Fenrir lane in the Settings tab include a "request unbinding" affordance? | Phase 2 | **W** | No. The whole point is that Fenrir-marked rules CANNOT be locally overridden. Adding a request-affordance would dilute the invariant. Future work could add a user-scope-only override prompt; out of v1. |

---

<a id="7-how-to-execute-in-a-codespace"></a>

## 7. How to execute this in a Codespace

The plan was authored on Windows but executes cleanly on a Linux GitHub Codespace. Reasons to prefer Codespace execution:

- **No Windows path issues.** The existing devcontainer / Codespace setup has POSIX paths throughout; the Windows path-encoding bug class (cp1252, backslashes in generated artifacts) does not apply.
- **No git-push hang.** The Codespace has gh credentials pre-provisioned; `git push` runs to completion without an interactive credential prompt.
- **Pre-installed tooling.** `python3`, `jq`, `gh`, `prettier`, `npx` are all on the path. `bash -n`, `find -exec`, `python3 -m json.tool` work without quoting workarounds.

### Bootstrap in a fresh Codespace

```shell
# 1. Open the Codespace (devcontainer auto-builds).
# 2. Verify environment:
python3 --version    # expect 3.12+
jq --version         # expect 1.6+
gh --version         # expect 2.x
prettier --version   # expect 3.x

# 3. Verify gates pass on main:
scripts/audit-gates.sh

# 4. Pull this branch:
git fetch origin plan/norse-features-build
git checkout plan/norse-features-build
```

### Per-phase execution loop

For each phase in [§4](#4-master-sequence):

1. **Create a feature branch off main** (`feat/<feature-slug>`). Phases ship one or more features; each feature gets its own branch.
2. **Read the per-feature spec** in [§3](#3-per-feature-execution-specs). Implementation order is the numbered Steps list.
3. **Spawn a focused-task agent per feature** if multiple features fit a phase (e.g., Sleipnir + Mímir in Phase 5). The Team Lead dispatches; each sub-agent completes one feature's checklist.
4. **Run the pre-PR gate suite** before pushing:
   ```shell
   # JSON validity
   python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
   for m in plugins/*/.claude-plugin/plugin.json; do python3 -m json.tool "$m" > /dev/null; done
   python3 -m json.tool .repo-layout.json > /dev/null

   # Shell syntax + exec
   bash -n plugins/*/hooks/*.sh
   find plugins/*/hooks -name '*.sh' -exec test -x {} \;

   # Prettier (whole tree, per AGENTS.md discipline)
   npx --yes prettier --write . --log-level warn
   npx --yes prettier --check . --log-level warn

   # Layout allow-list check
   python3 - <<'PY'
   import fnmatch, json, subprocess
   allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
   new = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "main"],
                        capture_output=True, text=True).stdout.splitlines()
   violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
   if violations:
       print("LAYOUT VIOLATIONS:")
       for v in violations: print(f"  - {v}")
   else:
       print("Layout OK.")
   PY

   # Gate audit meta-test
   scripts/audit-gates.sh
   ```
5. **Push and open PR**:
   ```shell
   git push -u origin feat/<feature-slug>
   gh pr create --base main \
                --title "feat(ravenclaude-core): <feature> v0.XX.0" \
                --body "..."
   ```
6. **Run `/mjolnir ravenclaude-core`** (after Phase 1 ships) before requesting merge; verify all green.
7. **Bump versions** in both `plugins/ravenclaude-core/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` in the same commit.

### Codespace-specific notes

- The dashboard is served via GitHub Pages from main (per [PR #59](https://github.com/mcorbett51090/RavenClaude/pull/59)). Local-dev preview uses `scripts/serve-dashboards.py`.
- Headless Chrome is installed (per [PR #62](https://github.com/mcorbett51090/RavenClaude/pull/62)) for mermaid-cli / SVG generation tasks (relevant for 3.9 Yggdrasil).
- The Codespace has no Windows-specific encoding env vars to worry about; `PYTHONIOENCODING=utf-8` is the default.

### Coordination with the parallel dashboard buildout

The dashboard buildout plan (PR #69) covers Phase A (multi-layer comfort posture) and Phase B (new dashboard tabs). This plan **assumes Phase A is in flight or shipped** and **augments Phase B** (Settings tab gets the Fenrir lane, the Norns section, the Víðarr panel; new tabs Heimdall and Bifröst and Yggdrasil are added).

If both plans are executing in parallel, coordinate via:
- Phase 0 of this plan ships independently (no buildout dependencies).
- Phases 1–9 of this plan should land **after** the relevant buildout phase to avoid merge conflicts in `dashboard.html`.
- A single weekly rebase against main + an agreed merge order (buildout-PR first, then norse-feature-PR) keeps both branches healthy.

---

<a id="8-effort-summary"></a>

## 8. Effort summary

| Phase | Contents | Hours |
|---|---|---|
| 0 | P0.1 – P0.6 prerequisites | 12–17 |
| 1 | Heimdall + Mjölnir + Gleipnir docs | 22–34 (+ 8–12 if Gleipnir viz ships) |
| 2 | Fenrir | 8–12 |
| 3 | Norns | 12–16 |
| 4 | Bifröst | 10–14 |
| 5 | Sleipnir + Mímir | 11–17 |
| 6 | Yggdrasil static | 4–6 |
| 7 | Ragnarök | 18–24 |
| 8 | Víðarr | 10–14 |
| 9 | Yggdrasil interactive + Níðhöggr | 24–32 |

**Total: 131–186 hours**, or roughly **4–6 months** at 8–10 focused hours/week.

The smallest meaningful first slice is **Phase 0 + Phase 1**, ~34–51 hours, which ships:
- Working prerequisites (`next_version`, hook events, ASCII discipline, posture events, six-axis memo, scenario events).
- Heimdall tab (the most-approved expert candidate).
- `/mjolnir` reporter.
- Gleipnir framing in posture docs.

That four-week sprint alone delivers the highest-leverage piece of the Norse theming and lays the substrate for everything after.

---

_End of plan._
