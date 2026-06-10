# Changelog

All notable changes to the RavenClaude marketplace and its plugins. Format loosely follows [Keep a Changelog](https://keepachangelog.com/). The marketplace version (`metadata.version` in `.claude-plugin/marketplace.json`) bumps when the catalog shape or cross-plugin contracts change; individual plugins have their own semver tracked in their `plugin.json`.

## ravenclaude-core 0.149.0 — 2026-06-10 (repo-review autonomous fixes: guard hardening + portability + doc-count accuracy)

Three-panel repository review (expert fan-out → validation → tie-break) with autonomous fixes. Every objective gate was green going in; the panels surfaced correctness/hardening defects the gates can't see.

**Guard & hook hardening (consumer-visible):**

- `guard-destructive.sh` — `rm -rf ./` / `rm -fr ./` (trailing-slash current-dir delete) now blocked. The guard already blocked the bare `rm -rf .`; the trailing-slash idiom slipped past both target checks. `rm -rf ./tmp/build` and other relative subpaths stay allowed. New Gate 5 fixtures pin both directions.
- `enforce-layout.sh` — the in-project prefix test now requires the trailing `/` (`"$project_root"/*`), so a sibling directory sharing the project-root name as a prefix (e.g. `…/RavenClaude-backup`) is no longer misclassified as in-project (which had yielded an unstripped `rel_path` and a spurious deny).
- `copilot-hook-adapter.sh` — dropped the predictable `/tmp/rc-adapter-err.$$` fallback (a symlink-attack target on shared hosts) in favour of `/dev/null`, with the cleanup guarded so it never removes `/dev/null`.

**Portability & tooling:**

- `scripts/eval-adaptive-classifier.py` — `REPO_ROOT` now derives from `Path(__file__)` like every other script (was hardcoded to `/workspaces/RavenClaude`, so the eval harness failed on any other clone path, including CI).
- `scripts/archive-branch.sh` — the unmerged-SHA audit-log write is now array-quoted (no word-split/glob on the substitution).
- `scripts/check-frontmatter.py` — frontmatter extraction tolerates CRLF (`\r?\n`) so a Windows-authored file reports a real YAML error instead of a misleading "no frontmatter".

**Documentation accuracy:** corrected drifted hand-maintained counts across `README.md`, the core `CLAUDE.md`, `marketplace.json`, and several plugin READMEs (core 38→40 skills; power-platform 18/20→21; the `requires` line 22-of-23→98-of-99; the metadata 43→98 domain plugins; web-design/claude-app/azure/microsoft-fabric/finance knowledge-bank docs; regulatory-compliance 27→37 best-practice rules) and removed the stale "salesforce still planned" roadmap bullet (it ships). See `docs/repo-review-2026-06-10-decisions.md` for the recommendation to generate or gate these counts (the recurring drift class).

### Catch-up note — 0.104.0 through 0.148.0

These 45 intervening versions were not individually logged here. The authoritative version-by-version history is git (`git log`) plus the milestone narratives in [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md). The major arcs in that span: the Copilot-adapter diagnostic trilogy (0.110–0.113), the unified-portal / 5-section-IA build-out and the Norse observability tabs (Heimdall / Víðarr / Norns / Níðhöggr / Mímir / Bifröst / Sleipnir), the Learn-tab concept + stepper rollout, the FORGE external-contribution intake, the agent-dispatch-evaluator phases, the `rc-deep-research` rename + eval-harness wiring, `scout`, the visual-feedback-loop, and the reactive run-state monitor. Going forward this file's top entry tracks each bump per the AGENTS.md CHANGELOG convention.

## ravenclaude-core 0.103.0 — 2026-06-02 (Intercom polish: ⌘K palette + conversational posture editor + dark mode + onboarding)

Premium SaaS refinement of the landing dashboard (`index.html`) with five new visible surfaces. Plan v4 — refined through a 4-seat panel review (architect + code-reviewer + designer + project-manager) before exit. Built on the v0.102.0 design-system foundation.

**HIGH-severity loader fix (was silently dropping CSS):**

- `_load_shared_tokens_root()` in all three generators (`generate-index-dashboard.py`, `generate-repo-guide.py`, `generate-dashboards.py`) previously extracted only the first `:root { ... }` block from `shared-tokens.css`. The new `[data-theme="dark"]` siblings AND the existing `.rc-card`/`.rc-pill` component classes never reached any surface. Rewritten to inline the WHOLE file verbatim. **Consumer-visible effect**: dashboard.html and repo-guide.html now correctly receive the full design system (component classes + dark-mode CSS), inert until `data-theme="dark"` is set (toggle wired only on `index.html` this release).

**⌘K Command Palette (new):**

- Centered modal (560px, backdrop blur, slide-up entrance) triggered by `Cmd+K` / `Ctrl+K` (or `/` when not in an input).
- Categorized results: **Quick actions** (apply posture presets, copy install commands, toggle theme, show onboarding, open dashboard), **Plugins**, **Specialists**, **Skills**, **Hooks**. ~190 indexed items.
- Keyboard nav (↑/↓/Enter/Esc), mouse hover, focus restoration on close.
- Replaces the topbar search input with a `⌘K` opener button.

**Conversational Posture Editor (Configuration view):**

- New top-of-page **scenario picker** — 4 visual cards using `D.posture.presets[]`. Each card auto-generates a 3-line plain-English "what this means in practice" summary via sentence template — picks the 3 highest-stakes categories per preset (deny > ask > auto priority) and renders `"<category.title>: [always stops you / asks before acting / proceeds silently]"`.
- Color-coded safety profile per scenario: gold (strict), teal (recommended balanced), neutral (exploratory), **deep amber `#b5630a`** (max autonomy — designer-panel correction: warm-red read "destructive/error", wrong message for the user's chosen scenario).
- Click a scenario card → applies preset, updates segmented controls + YAML, toasts with a "Copy YAML" follow-up action.

**Dark mode (toggle wired on index.html):**

- Sun/moon button in topbar. Auto-detects `prefers-color-scheme: dark`; manual toggle persists to `localStorage.rc-theme` (`light` | `dark`).
- Warm near-black bg `#14110d`, lifted-chroma gold `#c9a84c` and teal `#3aa391` (designer-panel values — light-mode values read muddy on dark surfaces). WCAG AA: text on bg ≥ 7:1, accent on bg ≥ 4.5:1.
- CSS shipped to all three surfaces via the loader fix above, but `dashboard.html` and `repo-guide.html` keep their light aesthetic by never setting the `data-theme` attribute. Dashboard toggle wiring deferred to v0.104.0 after Norse-panel review.

**First-time Onboarding Checklist (Home view):**

- Dismissible card pinned above the hero. 5 steps: install ravenclaude-core, pick a scenario, read GETTING_STARTED.md, run first `/spawn-team`, open the deep dashboard. Each step has a tracked "Copy" / "Open" CTA; clicking marks the step done.
- State in localStorage (`rc-onboarding-progress` bit-flag, `rc-onboarding-dismissed`).
- Re-show via ⌘K → "Show onboarding checklist".
- Auto-hides on completion with a "nice work" toast.

**Generator data enhancements (`scripts/generate-index-dashboard.py`):**

- New `_scan_skills(plugin_dir)` — globs `plugins/*/skills/*/SKILL.md`, parses YAML frontmatter for `name` + `description`. Sorted iter, explicit utf-8.
- New `_scan_hooks(plugin_dir)` — reads `hooks/hooks.json`, indexes by `(event, name)`. Graceful fallback when missing.
- `D.plugins[].skills_index[]` + `D.plugins[].hooks_index[]` — feed the palette's Skills + Hooks categories.
- `D.posture.categories[]` extended passthrough — adds `controls`, `rec_individual`, `rec_team`, `examples` from `dashboard-schema.json` (was reading only `group`/`guidance`/`recommended`).

**Micro-interactions + design system extensions (`shared-tokens.css`):**

- 5-tier warm-tinted shadow scale (`--rc-shadow-xs` through `--rc-shadow-xl`) — proper Intercom-soft elevation on beige.
- Refined typography scale (8 size tokens + 4 line-heights + 4 tracking values).
- `.rc-shimmer` skeleton utility + `@keyframes rcShimmer` + `@keyframes rcShimmerOnce` + `@keyframes rcFadeUp`.
- Stagger on view enter: first 5 cards at 50ms each, uniform 250ms tail (avoids cliff at item 9).
- Hero `.accent` shines ONCE on first paint, not looping (designer-panel: looping signals "loading" anxiety).
- Card hover lift `translateY(-1px)` + warm shadow growth, button active `scale(0.98)`, sidebar active-rule animation.
- Toast: backward-compatible `(msgOrObj, action?)` overload. Existing string callers unchanged; new `{msg, action:{label,fn}}` shape gets a 5-second dismiss (WCAG 2.2.1 timing).

**Spawn-feedback widget (placeholder shape):**

- Home view renders a "Last team spawned" card if `localStorage.rc-spawn-log` exists `{playbook, agents[], ts}`. Inert by default — documents the shape for a future `/spawn-team` integration to write to.

**Deferred to v0.104.0 (explicit, panel-blessed):**

- Self-hosted Inter-subset.woff2 (designer-panel recommendation — couldn't fetch binary this session; system Inter fallback used).
- YAML diff pane (per-row drift dot ships now; full before-after pane needs design — what is "before"? Last-saved? Scenario baseline?).
- Dark mode toggle wiring on `dashboard.html` (CSS shipped; Norse-panel visual review needed before activation).
- `PLUGIN_COLORS` 17-plugin retune for beige base (still 5 explicit + 12 fall-through to `DEFAULT_COLOR`).
- Audience-chip + difficulty-chip + Mermaid theme hex retune in `generate-repo-guide.py`.
- `serve-dashboards.py` twin parity (pre-existing ~7KB drift surfaced by panel; not introduced by this PR).
- Meta-task template/skill (spec #5 second half).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. The dashboard.html receives the full design-system CSS (component classes + dark-mode pairs) but its visible behavior is unchanged in this release (light aesthetic, gold accent, Norse panels). The landing dashboard `index.html` is substantially refreshed — `⌘K` to try the new palette; Configuration view shows scenario cards; topbar sun/moon toggles light/dark.

## ravenclaude-core 0.102.0 — 2026-06-01 (UI design-system unification + doctor extensions + plugin-versioning surface)

A single bundled PR landing two distinct workstreams: a visual unification across all three web surfaces (Intercom-inspired light beige + dual gold/teal accents) and small extensions on doctor/versioning surfacing that round out v0.101.0's work.

**Design system (P0 — visual refresh, consumer-visible on next `/plugin marketplace update`):**

- New `plugins/ravenclaude-core/dashboard-assets/shared-tokens.css` — single source of truth for color, typography, spacing, radii, shadow tokens. Read at generate-time by all three generators (`generate-index-dashboard.py`, `generate-repo-guide.py`, `generate-dashboards.py`) and inlined into each surface's `<style>` block via a `/*__SHARED_TOKENS__*/` marker substitution. Surfaces stay self-contained — no runtime asset load.
- New `plugins/ravenclaude-core/dashboard-assets/README.md` — design-system docs: token reference, a11y discipline (gold is accent-only on light bg; teal passes AA-body), `.rc-*` class-naming rule, generator integration pattern.
- **Aesthetic flip — light beige base** (`#faf7f0`), warm near-black text (`#1a1614`), Intercom-soft shadows. **Two accents — by design**: gold (`#a8882e`) for the dashboard (preserves the Heimdall/Víðarr/Norns Norse identity — gold-on-beige reads as parchment-and-gilt); teal (`#1f7f78`) for index + repo-guide (consumer-facing surfaces).
- The dashboard's hard-coded pipeline-badge color literals (`#14532d`/`#bbf7d0`/`#4b1113`/`#fecaca`/`#3a3a42`/`#cbd5e1`) replaced with `var(--rc-{ok,danger,neutral}-{bg,fg})` tokens.
- `index.html` `<meta name="color-scheme">` flipped from `dark` to `light`; `theme-color` from `#0b1120` to `#faf7f0`.

**Doctor extensions (P1):**

- `ravenclaude doctor` adds two checks (now 7 total): **plugin version alignment** (reuses `scripts/check-marketplace-claims.py` as subprocess — single source of truth for drift checks) and **worktree + run-artifact hygiene** (worktrees >90 days → fail, >30 days → warn; run dirs >90 days → warn-only since artifacts may be partner-confidential).

**Plugin versioning surface (P1):**

- `scripts/generate-repo-guide.py` adds `_format_requires()` helper — every per-plugin card in `repo-guide.html` now renders `Requires` as `ravenclaude-core ≥ 0.X.Y` (clean readable line) instead of the prior raw `{'plugins': ['ravenclaude-core@>=0.X.Y']}` dict literal. 16/17 plugins already declare `requires.ravenclaude-core`; the surfacing was the missing piece.
- `README.md` — new **"Updating and version pinning"** section documenting the update flow, SHA-pinning recipe, compatibility via the repo-guide `Requires` row, the `shell_package_install: ask` migration prompt, and the non-removable security floor reference.

**Deferred to follow-up (explicit):**

- **`PLUGIN_COLORS` 17-plugin retune for the beige base** — the current 5 entries stay; the 12 fall-throughs keep `DEFAULT_COLOR`. Re-tuning all 17 to read against beige requires browser-tested WCAG checks; landing later as v0.103.0 prevents fragile hex-juggling in this PR.
- **Full audience-chip / difficulty-chip / Mermaid theme retune** in `generate-repo-guide.py` — the existing 31 hardcoded hexes remain alongside the shared tokens; a follow-up will migrate them to `var(--rc-*)` references and re-tune for the beige base.
- **`serve-dashboards.py` twin parity** — a pre-existing ~7 KB drift between the root and plugin copies (not caused by this PR) was surfaced by the panel; logged in `project_v0101_followups.md` for the next pass.
- **Meta-task template / skill** (spec item #5 second half) — owner: maintainer. Logged in `project_v0101_followups.md`.
- **STRATEGY.md content direction** (still open from PR #207).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. The dashboard's `/dashboard` page will look visually different on next launch (same controls + behavior — every Save & apply path, every Norse panel, every endpoint unchanged; only colors/typography/spacing refreshed). No new prompts beyond v0.101.0's `shell_package_install: ask`.

## ravenclaude-core 0.101.0 — 2026-06-01 (bundled P0–P2 gap closure: onboarding + evals + knowledge-health + security floor + doctor)

A single bundled gap-closure PR. New consumer-facing surfaces, one HIGH-severity security fix, one consumer-visible default change.

**New onboarding surface (P0):**

- `GETTING_STARTED.md` at repo root — 10-minute canonical end-to-end walkthrough with one new orienting Mermaid diagram and two worked examples (a domain-neutral docs dispatch, and a Power Platform posture configuration). Linked from `README.md` via a new "First Workflow in 10 Minutes" callout.
- `STRATEGY.md` stub — placeholder for public-core / private-extension direction; content pending Matt's direction.
- `docs/best-practices/diagrams-in-docs.md` — new "Root-doc summary diagram pattern" section codifying one orienting Mermaid in root docs + link out for depth.

**Evals harness (P1):**

- New `evals/` directory: `README.md`, `rubric.md`, `runner.py` (pure-stdlib scorer reading `.ravenclaude/runs/<id>/`), 5 case YAMLs (3 core + 2 power-platform), gitignored `results/`.
- `docs/evaluation.md` — long-form interpretation guide.

**Knowledge freshness (P1):**

- `plugins/ravenclaude-core/scripts/knowledge-health.py` + `skills/knowledge-health/SKILL.md` — sweeps every `plugins/*/knowledge/**.md`, groups by stale / due_soon / untracked / fresh.
- `checklists/release-checklist.md` — new Step 1.5 (run knowledge-health) and Step 1.6 (confirm the `security_deny` floor invariant via the new unit test).

**Security (P1) — one HIGH fix + one default flip + audit artifact:**

- **HIGH** — `plugins/ravenclaude-core/scripts/apply-comfort-posture.py`: `security_deny` now always unions `DEFAULT_SECURITY_DENY`, never replaces. A user saving `security_deny: []` from the dashboard cannot wipe the security floor. Regression test in `tests/fixtures/test_security_deny_floor.py` (6 cases, all pass).
- **CONSUMER-VISIBLE DEFAULT CHANGE** — `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` flips `shell_package_install` from `allow` to `ask` at the project layer. Supply-chain guard. Consumers on `/plugin marketplace update` will see one new prompt per `npm install` / `pip install`; opt back to `allow` from the dashboard if desired.
- `SECURITY.md` — new §"Defaults and floors" documenting the non-removable floor, Codespace port-visibility expectation, CSRF posture, and the `shell_package_install` change.
- `docs/security/2026-06-dashboard-and-posture-apply-review.md` — full 4-seat panel security review of the dashboard server + posture-apply pipeline; 6 findings (1 HIGH fixed, 1 MEDIUM as default change, 4 logged follow-ups).

**Doctor + worktree helpers + CI schemas (P2):**

- `scripts/ravenclaude doctor` — new subcommand. Checks `.repo-layout.json` parse, posture/settings presence, knowledge-health, layout-gate.
- `scripts/worktree-new.sh` + `scripts/worktree-clean.sh` — thin wrappers for sub-agent dispatch isolation.
- `schemas/plugin.schema.json` + `schemas/marketplace.schema.json` + `.github/workflows/validate-schemas.yml` — new lenient CI gate catching gross manifest defects (missing required fields, malformed semver).

**Self-referential workflow (P2):**

- `docs/best-practices/self-referential-improvement.md` — "Use RavenClaude to improve RavenClaude" pattern with one worked example.

**Manifest + layout:**

- `.repo-layout.json` — adds `GETTING_STARTED.md`, `STRATEGY.md`, `evals/**`, `schemas/**`, `tests/fixtures/**` to `allowed_globs`.
- `.github/workflows/validate-marketplace.yml` — `paths:` triggers extended to cover the new top-level files.
- `scripts/check-md-links.py` — extended root-files tuple to include `GETTING_STARTED.md` and `STRATEGY.md`.

**Deferred follow-ups (intentionally NOT in this PR — tracked):**

- CSRF token + Codespace port-visibility check + posture-file size cap in `serve-dashboards.py` — see `docs/security/2026-06-dashboard-and-posture-apply-review.md` findings #3–#6.
- `audit-gates.sh` fixtures for the new schema-validation gate (gate ships without the meta-test; will land in a follow-up).
- Knowledge-health dashboard card under the "Look back" tab — script is ready; UI integration deferred.
- `STRATEGY.md` content — Matt-preference call.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. One new prompt to expect: the first time the agent runs `npm install` / `pip install` you'll see an ask-prompt instead of silent execution. Approve or flip the category back to `allow` from `/dashboard`.

## ravenclaude-core 0.27.1 — 2026-05-26 (fix: `thing` skill load + frontmatter gate + dashboard docs)

Bug fix + hardening, prompted by a consumer install under GitHub Copilot.

- **Fix — `thing` skill failed to load in strict YAML hosts.** Its `description` frontmatter was an unquoted scalar containing an inline `: ` (`…explaining the tribunal: the PreToolUse…`), which is a YAML mapping indicator. Claude Code's lenient loader tolerated it, but strict parsers (e.g. Copilot) threw `mapping values are not allowed here` and dropped the skill. The description is now quoted. It was the only one of 22 skills affected.
- **New CI gate — skill/agent frontmatter strict-YAML validation.** `scripts/check-frontmatter.py` parses every `skills/*/SKILL.md` and `agents/*.md` frontmatter with a strict parser and requires a string `description`; wired into `validate-marketplace.yml` and covered bidirectionally by `audit-gates.sh` Gate 18. This is the gate that would have caught the bug — no malformed frontmatter can ship again.
- **Docs — how to open the comfort-posture dashboard.** The consumer `CLAUDE.md` template and the plugin README now explain where `dashboard.html` lives (the plugin cache), how to open it (static page, no server), the Copy→`comfort-posture.yaml`→`/set-posture` flow, and a **cross-tool note** that the dashboard / comfort-posture / tribunal are Claude-Code-specific (Copilot/Cursor/Codex don't execute them).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. The `thing` skill will then load in strict hosts. No behavior change for existing Claude Code installs beyond the skill now loading everywhere.

## ravenclaude-core 0.27.0 — 2026-05-26 (decision-review tribunal + posture re-apply on the web)

Extends the tribunal (the Thing) from command review to **decision review**: yes/no decisions can now be routed to a panel verdict instead of always interrupting the human. Also makes a dashboard-composed comfort posture take effect on Claude Code on the web automatically.

### ravenclaude-core 0.27.0

- **New `scripts/thing-decide.py`** — adjudicates a yes/no decision by convening the same role-shaped seats as command review (Forseti / Mímir / Heimdall, + Thor on a split) and returning `yes` / `no` / `defer`. **Self-contained:** it convenes its own seats and does NOT touch the live `PreToolUse(Bash)` path (`thing-seat.sh` / `thing-orchestrator.sh`), so command review is unchanged. Reuses `thing-decision.resolve_panel_config` so the two panels never drift.
- **New skill `skills/decision-review`** — the operating reference: before asking the human a yes/no question, route it through the tribunal; act on a binding `yes`/`no`, ask the human on `defer`. Also drives the post-PR retrospective.
- **Safety envelope (binding mode):** `decision_review: off | advisory | binding` in `.ravenclaude/comfort-posture.yaml`, **off by default**. High-blast / irreversible decisions never auto-resolve (always `defer`); abstention / low-confidence / split-to-defer / detected injection all fail safe to `defer`. Every routed decision is Sága-logged under `.ravenclaude/runs/thing/decisions/`.
- **New SessionStart hook `hooks/reapply-posture.sh`** — regenerates the project-layer permission rules from `.ravenclaude/comfort-posture.yaml` at session start (via `apply-comfort-posture.py --scope project`), so a dashboard-composed posture persists on Claude Code on the web (ephemeral container; only committed files survive). Silent no-op without a posture file; never blocks; idempotent. Registered in `hooks/hooks.json` + the dev-mirror; setup checklist in `docs/comfort-posture-web-setup.md`. _(Originally cut as 0.26.0 on this branch; rebased onto main's 0.26.0 = tribunal T4, so it ships in 0.27.0.)_
- **Docs** — `docs/post-pr-decision-review.md` updated to "shipped" with the classification rubric, seat-routing map, and the all-yes/no-questions scope; the standing trigger lives in the root `CLAUDE.md`.

**Verification caveat:** the seats call `claude -p`, which can't run in CI / some sandboxes. The engine is tested via the `THING_DECIDE_MOCK_VERDICT` hook (every tally + envelope path); true live behavior needs a real session with the CLI present.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — `decision_review` is off by default, so behavior is unchanged until opted in.

## ravenclaude-core 0.26.0 — 2026-05-26 (command-review tribunal T4 — injection & self-protection hardening) (#94)

Injection and self-protection hardening for the command-review tribunal (the Thing): the seats are hardened against prompt-injection carried in command context, and the panel resists attempts to disable its own review. Shipped via PR #94 (merged to `main`). See `docs/tribunal-review-feature-design.md` (§B.9) and the bidirectional fixtures in `scripts/audit-gates.sh` (Gates 15–16).

## marketplace 0.25.0 — 2026-05-22 (lesson capture: cross-platform-determinism)

Self-improvement loop in action. Two real bugs landed in `scripts/generate-repo-guide.py` on the same day — both stemmed from non-deterministic, OS-dependent output in a generated artifact that gets committed and diff-checked in CI. Captured as a new skill so the lesson applies to every future generator the team writes.

### ravenclaude-core 0.13.0

- **New skill `skills/cross-platform-determinism.md`** — when a script generates a file that is committed to the repo and/or diff-checked in CI, the output MUST be deterministic and OS-independent. The skill enumerates the six categories of nondeterminism (path separators, encoding, line endings, ordering, timestamps, locale) with concrete before/after Python snippets and a review checklist. Motivated by two real bugs in this repo's own `scripts/generate-repo-guide.py`:
  - **Path separators** — `str(path.relative_to(REPO_ROOT))` yields `plugins\foo\bar.md` on Windows but `plugins/foo/bar.md` on Linux. Any committed artifact regenerated on the opposite OS gets a giant unintended diff and the freshness gate fails forever. Fix: `path.relative_to(REPO_ROOT).as_posix()` everywhere a Path is serialized. The fix is also applied in this PR (9 sites).
  - **Encoding** — the script wrote UTF-8 to stdout in `--check` mode; Windows cp1252 default crashes on em-dashes, smart quotes, arrows. Fix: explicit `encoding="utf-8"` on every read/write, plus `PYTHONIOENCODING=utf-8` or `sys.stdout.reconfigure(encoding="utf-8")` for stdout paths.
- **`scripts/generate-repo-guide.py` fix** — applied the `.as_posix()` correction to all 9 `str(X.relative_to(REPO_ROOT))` sites. `repo-guide.html` regenerated with `PYTHONIOENCODING=utf-8`; zero backslash paths in the committed HTML.

### Marketplace meta

- `repo-guide.html` regenerated to pick up the new skill in the ravenclaude-core skills tab.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — no breaking changes. The new skill is invokable by any agent reviewing or writing a generator script.

## marketplace 0.11.0 — 2026-05-21 (new plugin: edtech-partner-success)

New domain plugin landing. Anchored on the Partner Success Manager (PSM) lane — vertical-explicit (we know it's education) but segment-agnostic (K-12 / higher-ed / corporate L&D). Built for an actual PSM running an actual book of EdTech partners, not for a generic customer-success tutorial.

### edtech-partner-success 0.1.0

- **6 specialist agents:**
  - `partner-success-manager` — EdTech-specialized PSM (extends the generic `ravenclaude-core/partner-success-manager`). Onboarding, adoption, ongoing pulse, day-to-day partner-facing work.
  - `success-playbook-designer` — the play library (renewal / expansion / recovery / advocacy plays); the PSM *executes* plays, this agent *designs* them.
  - `qbr-composer` — Quarterly Business Reviews end-to-end (data pull plan → narrative → deck → talk track → followup tracker).
  - `learning-analytics-analyst` — signal selection, health-score architecture, dashboard specs, rostering / SIS / LMS data-quality diagnostics.
  - `ferpa-comms-translator` — FERPA-aware (and segment-equivalent privacy-aware) multilingual / multi-audience partner & end-user comms.
  - `partner-profile-curator` — the durable partner record that outlives any one PSM seat; distinct from the touchpoint log.
- **4 skills:** `partner-health-scoring` (signal selection + weighting + decay + red-flag triggers + threshold-to-play mapping), `success-plan-authoring` (30/60/90 + quarterly), `qbr-composition` (the canonical QBR playbook with mock-rehearsal step), `rostering-data-quality` (Clever / ClassLink / OneRoster / SIS / LMS / HRIS diagnosis playbook).
- **8 templates:** success plan, partner profile, QBR deck outline, touchpoint log, escalation memo, health-score dashboard spec, onboarding checklist, annual partner review. Each tuned to capture the durable-vs-diary distinction.
- **1 advisory hook** (`flag-psm-anti-patterns.sh`) flagging the mechanically-detectable PSM anti-patterns: action items without dates, generic boilerplate ("we value your partnership", "just checking in", "circling back", "touching base"), unverified numeric claims, multi-partner names visible in `To:` lines, health-score red/yellow status without named signals. PostToolUse advisory by default; `EDTECH_PS_STRICT=1` makes it blocking. Verified bidirectional (fires on bad fixture, silent on clean).
- **CLAUDE.md follows the established 11-section pattern**: roster (§1) → routing rules (§2) → 13 house opinions (§3) → 12 anti-patterns (§4) → Grounding Protocol with the alternate-methods step (§5) → Output Contract with extended JSON schema including `next_actions[].owner+.date`, `signals_cited`, `partner_context` (§6) → automated checks (§7) → skills (§8) → knowledge bank pattern (§8a, empty at v0.1.0; will accumulate organically) → templates (§9) → escalation routes (§10) → references (§11).
- Requires `ravenclaude-core@>=0.7.0` (for the alternate-methods Capability Grounding Protocol that lands in agents' default behavior).

### Marketplace meta

- Catalog description updated. `docs/architecture.md` Status table gains the new row. EdTech is moved off the planned-plugins line (only Salesforce remains on the roadmap there).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/plugin install edtech-partner-success@ravenclaude` + `/reload-plugins`. New plugin only; no breaking changes to existing plugins.

## marketplace 0.10.0 — 2026-05-21 (alternate-methods enhancement to Capability Grounding Protocol)

Cross-plugin behavior change: agents now **proactively** enumerate alternative implementation paths and try them in order before declaring a task blocked. Motivated by the production incident captured in the 0.9.0 release (programmatic-flow-creation knowledge file) — the user had to prompt the agent to find the alternative Dataverse path. This release generalizes that lesson into a protocol rule that fires for every agent in every plugin.

### ravenclaude-core 0.7.0

- **Capability Grounding Protocol extended** in `CLAUDE.md`. New step 3 inserted: *"Enumerate alternative implementation paths from easiest to most difficult, and try them in that order before declaring the task blocked."* New sub-section "Try alternative paths before declaring blocked" spells out the rule (brainstorm 2–3 alternatives, rank by cost, try next-easiest, list what was tried), the mandatory phrasing template (`"After trying [A — outcome] and [B — outcome], I am blocked on …"`), the anti-patterns, and how the rule interacts with the Structured Output Protocol.

### power-platform 0.9.0

- §5 Capability Grounding Protocol gains the alternate-paths step + a Power-Platform-specific enumeration ladder (REST → SDK → CLI → portal-with-automation-around-it; PA Mgmt API → Dataverse Web API → Power Apps API → CDS plugin; per-user license → per-app → per-flow → pay-as-you-go). Cross-references `knowledge/programmatic-flow-creation.md` as the canonical case study. Grounding Protocol Checklist gains a new bullet: *"I enumerated at least 2–3 alternative implementation paths and tried the next-easiest one before declaring blocked."*

### web-design 0.3.0

- §5 gains the alternate-paths step + web-specific ladder (grid → flex → subgrid layout primitives; lighter library; build-time vs runtime split; static-first refactor; `<picture>`/`srcset` vs JS image-loading).

### finance 0.2.0

- §5 gains the alternate-paths step + finance-specific ladder (different revenue-recognition framing; peer-comp instead of DCF when forecast inputs are unstable; triangulation across three data sources; manual reconstruction with documented assumptions).

### regulatory-compliance 0.2.0

- §5 gains the alternate-paths step + compliance-specific ladder (alternative framework when one doesn't map; control narrative documenting the gap; triangulation across primary + secondary sources; directly-cited regulator guidance vs derivative summaries).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — existing agents stay backwards-compatible, just gain the new behavior. Mandatory phrasing template updated; downstream parsers reading blocked-status reports should accept the new shape (which includes "tried" enumeration).

## marketplace 0.9.0 — 2026-05-21 (power-platform production knowledge bank)

### power-platform 0.8.0

- **New knowledge bank** at `plugins/power-platform/knowledge/programmatic-flow-creation.md` — production lesson captured from creating ~136 cloud flows in a customer DEV environment via service principal in May 2026. Covers: why the Power Automate Management API is almost always blocked for SPNs (`roles: null` token; application permissions require Global Admin consent; delegated permissions don't work with `client_credentials`), the Dataverse Web API workaround (`workflow` entity, `category=5`, `type=1`, `primaryentity="none"`, `AddSolutionComponent` ComponentType=29), the `clientdata`-shape gotcha, the GUID-injection rule, and a production checklist.
- **`flow-engineer`, `solution-alm-engineer`, `power-platform-admin`** each gain inline priors tailored to their lane.
- **`CLAUDE.md` gains §8a (Knowledge bank)** documenting the pattern for future production-lesson entries.

### Marketplace meta

- Catalog descriptions for both `power-platform` and the marketplace mention the knowledge bank.

## marketplace 0.8.0 — 2026-05-21 (web-design pattern priors)

### web-design 0.2.0

- **New knowledge bank** at `plugins/web-design/knowledge/design-references.md` — a curated reference set of marketing / product sites praised in 2024–2026 design discourse as "cutting edge yet simple" (Linear, Vercel, Raycast, Resend, Cursor, v0, Tldraw, Cal.com). For each: why it's praised, two or three patterns worth borrowing, one thing NOT to borrow, source citations. Plus a synthesis section and an "avoid 2024 tropes" list (bento grids everywhere, glassmorphism beyond modals, AI-shimmer hero gradients, scroll-jacked horizontal panels). Reviewed-on date at the top; refresh roughly annually.
- **`visual-designer`, `ux-designer`, `frontend-implementer`, `web-architect`** each gain a compact **"Pattern library priors (2026)"** section tailored to their domain (aesthetic / interaction / implementation / stack respectively). The full brief lives in `knowledge/`; the inline priors make the opinions immediately active without bloating the prompt.
- `CLAUDE.md` gains a new §8a (Knowledge bank) pointing at `knowledge/design-references.md`.

### Marketplace meta

- Catalog description now mentions the curated reference set as part of the web-design plugin's value proposition.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. No breaking changes — additive content only. The four updated agents will now apply the priors automatically when invoked for marketing-site work; consumers who want to read the full brief can open `plugins/web-design/knowledge/design-references.md` in their cached plugin tree (or browse it via the [`repo-guide.html`](../repo-guide.html) at the repo root).

## marketplace 0.5.0 → 0.7.1 — 2026-05-21 (catch-up note)

Three new domain plugins and the interactive repo guide landed in rapid succession on the same day; their PR descriptions and merge commits are the authoritative changelog for each. Briefly:

- **0.5.0** — `finance` plugin v0.1.0 added (7 FP&A / controller / treasury / valuation / audit-prep / board-pack agents, 4 skills, 8 templates, advisory anti-pattern hook). Merge commit: `ddcd97e`.
- **0.6.0** — `regulatory-compliance` plugin v0.1.0 added (6 AML/KYC / regulatory-reporting / risk-and-controls / policy-writer / examination-prep / Bermuda-insurance agents, 4 skills, 8 templates, defensive PII-scrub hook). Merge commit: `83f2173`.
- **0.7.0** — `web-design` plugin v0.1.0 added (7 web specialists across IA / UX / visual / frontend / content / accessibility / performance, 4 skills, 8 templates, advisory web anti-pattern hook). Also: `repo-guide.html` generator + freshness CI step. Merge commits: `51386c6` and `8837615`.
- **0.7.1** — `repo-guide.html` moved from `docs/` to the repo root for top-level visibility; README opener refreshed to reflect the five-plugin state. Merge commit: `0bcdda2`.

## marketplace 0.4.0 — 2026-05-21 (overnight realignment)

Consolidates the salvageable content from overnight dispatcher PRs #8 / #9 / #10 onto the post-0.3.0 baseline. Stale version bumps (which would have rolled `ravenclaude-core` *back* to 0.3.0 and `power-platform` *back* to 0.6.0) were rejected; the additive content was preserved with version bumps recomputed forward.

### ravenclaude-core 0.6.0

- **New agent `agents/data-engineer.md`** — domain-neutral specialist for pipeline design, dimensional/lakehouse modeling, ELT/ETL, query performance, lineage, quality testing, ingestion patterns. Routes Power BI / DAX work to `power-platform/power-bi-engineer` and product-feature schema work to `architect`. Carries the Structured Output Protocol block.
- **New hook `hooks/guard-recursive-spawn.sh`** — PostToolUse advisory that warns when an edit to a plugin agent definition file looks like the agent is instructing itself to spawn another sub-agent (`Agent(`, `Task(`, `subagent_type:`, plain-English "spawn an agent" tokens). Conservative grep with false-positive guard on escalation-recommendation lines. Advisory by default; set `RC_GUARD_RECURSIVE_SPAWN_STRICT=1` to make it blocking. Registered as the 5th hook in `hooks/hooks.json`.
- **Skill update `skills/spawn-team.md`** — new **Cross-plugin dispatch** section after Step 8: domain-detection trigger table, domain-led playbooks for the seven most common Power Platform request shapes (including the new behavioral-test playbook for `power-platform-tester`), and a symmetric escalation table between `ravenclaude-core` and `power-platform`. Does not modify the Parallel Reviewer Fan-out, Artifact-Based Handoff, or Cited-Adjudicator escalation content from 0.5.0.
- CLAUDE.md narrative updated: 5 hooks, 14 specialist agents.

### power-platform 0.7.0

- **New agent `agents/power-platform-tester.md`** — Power Platform-specific tester. Spawns AFTER a specialist's change but BEFORE `solution-alm-engineer` packages a release. Covers Test Studio + Monitor (canvas), Manual Test + run-history assertions (flows), plug-in execution order + FLS/RLS + cascade (Dataverse), form / business-rule / command-bar (model-driven), DAX measure-tests + VertiPaq + DAX Studio server-timings (Power BI), `pac solution check` as a gate. Carries both the Markdown Output Contract (with mandatory `Licensing impact:` line) and the cross-plugin Structured Output Protocol JSON block.
- **House-opinions hook `hooks/check-house-opinions.sh`** gains three new mechanically-detectable checks (now 8 total):
  - `premium-connector-no-licensing-note` — flow JSON references a premium connector apiId without `_comments` / `// premium:` / `"premium": true` annotation (§3 #8).
  - `powerfx-var-prefix` / `powerfx-col-prefix` — `Set(name, ...)` and `(Clear)Collect(name, ...)` whose first argument doesn't follow the `var*` / `col*` convention (§3 #6). Skips Power Fx built-ins (`Self`, `Parent`, `ThisItem`, `ThisRecord`).
  - `secret-in-env-var` — environment-variable default that looks like a plaintext secret instead of `@Microsoft.KeyVault(...)` (§4 anti-pattern). Conservative — only fires on `password=`, `AccountKey=`, `api_key=`, `client_secret=`, `aws_secret_access_key`, or `Bearer <token>` patterns.
- CLAUDE.md narrative updated: 11 specialist agents, §7 hook table now lists 8 checks.

### Marketplace meta

- **Realignment of overnight dispatcher work**: PRs #11 (per-plugin changelogs, stale version refs) and #12 (CI quality gates that would have *replaced* the v0.5.0 behavioral guard-destructive tests) closed without merge. PRs #8 / #9 / #10 are superseded by this consolidation; closed after merge. PRs #14 / #15 / #16 (finance, regulatory-compliance, web-design plugins) remain queued for separate review.
- **README.md** opener rewritten to acknowledge both shipping plugins, the contribution-staging loop, and updated component counts (14 core agents / 11 PP agents / 5 core hooks / 8 PP checks).
- **`SECURITY.md`** added at repo root — disclosure policy for the private marketplace covering hooks, agent definitions, and bundled MCP server.
- **`.github/ISSUE_TEMPLATE/`** added (`bug_report.md`, `feature_request.md`, `proposed_lesson.md`, `config.yml`). `proposed_lesson.md` mirrors the contribution-staging flow.
- **`checklists/release-checklist.md`** + **`checklists/new-plugin-checklist.md`** added; `checklists/README.md` updated to point to both. Version examples in the release checklist use the post-realignment values (0.6.0 / 0.7.0 / 0.4.0) and acknowledge that `release.yml` workflow auto-publish is still a planned follow-up.
- `docs/architecture.md` Status table aligned to current versions (0.6.0 / 0.7.0); planned-plugins line points to the open PRs #14 / #15 / #16.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. No breaking changes — both plugins are minor bumps. The new `guard-recursive-spawn` hook is advisory by default; existing edits will not be blocked.

## marketplace 0.3.0 — 2026-05-21 (later same day)

### ravenclaude-core 0.5.0

Catch-up release that ports the marketplace's own self-review improvements into the plugin so consumer projects benefit:

- New skill `skills/audit-ci-gates.md` — guides any consuming agent that touches a CI workflow through the gate-audit-by-fixture pattern. Encodes the rule "for every CI step, prove it can fail on a known-bad input AND pass on a known-good input." References the canonical best-practice doc + the runnable scaffold below.
- New template `templates/agent-ready-repo/audit-gates.sh.template` — a runnable Bash scaffold the consumer's `/init-agent-ready` can drop into `scripts/audit-gates.sh`. Includes the gate-audit pattern (backup → mutate → assert → restore, with EXIT trap), idempotent fixture helpers, and a worked example block consumers replace with their own gates.
- New templates `templates/agent-ready-repo/.prettierrc.json.template` + `.prettierignore.template` — sensible prettier defaults (markdown line-wrap preserved; markdown excluded by default to avoid prose-reflow noise) that consumer projects can opt into via the updated `/init-agent-ready` command.
- `commands/init-agent-ready.md` — adds an optional Step 6 / new question 3: "should we add the CI-hygiene scaffold?" Three files written when accepted: `.prettierrc.json`, `.prettierignore`, `scripts/audit-gates.sh` (made executable).

Catch-up version-bump note: this release also captures content shipped in earlier marketplace commits that didn't bump retroactively — agent label drift cleanup (PR 4), constitution downgrade for run artifacts (PR 5), and the `to_specialist` / power-platform §6 SOP cross-link reconciliation (PR 7). Consumers who installed at 0.4.0 before those PRs will get all of that content along with the 0.5.0 additions above on next `/plugin marketplace update`.

### power-platform 0.6.1

- `CLAUDE.md` §6 now references the cross-plugin Structured Output Protocol JSON block that all 10 power-platform agents emit. Previously the section listed only the Markdown Output Contract; consumers reading §6 in isolation would have missed the JSON contract. (PR 7 in the marketplace; catch-up bump.)

### Marketplace meta

- `docs/architecture.md` Status table refreshed (was stale at ravenclaude-core 0.2.4 / power-platform 0.5.2).
- `docs/best-practices/ci-gate-audit.md` added (canonical Absolute Rule for CI gate hygiene).
- `scripts/audit-gates.sh` shipped at the marketplace level and wired into `validate-marketplace.yml` as a meta-test step. 10 gates × 2 fixtures = 21 assertions, all passing.
- `.prettierrc.json` + `.prettierignore` shipped at the marketplace level (the templates above mirror these).
- `.github/workflows/validate-marketplace.yml` gained behavioral hook tests, prettier check, actionlint check, email-leak guard, and the gate-audit meta-step.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up everything. Re-run `/init-agent-ready` in any project that wants the new optional CI-hygiene scaffold; existing files are not overwritten without explicit approval.

## marketplace 0.2.0 — 2026-05-21

### ravenclaude-core 0.4.0 (BREAKING)

- All 13 specialist agents now declare the **Structured Output Protocol** block in their Output Contract section. Agents emit a `---RESULT_START--- … ---RESULT_END---` JSON block inline after their Markdown report; the Team Lead parses it to drive routing.
- New **Cited-Adjudicator Escalation** pattern added to `rules/agent-collaboration.md` and the `spawn-team.md` Step 6 re-routing table. Trigger: when Agent A confidently asserts Agent B's prior artifact is wrong (confidence ≥ 0.7) in a correctness-critical domain, the Team Lead spawns `deep-researcher` in citation-only mode for adjudication.
- `/init-agent-ready` now copies the plugin constitution into the consumer repo as `docs/team-constitution.md` at init time, so the consumer-side Team Lead auto-loads the team roster on every session open. Portable across users — replaces an earlier (unshipped) design that imported from `~/.claude/plugins/cache/...`.
- README reconciliation: documented namespaced `subagent_type` form (`ravenclaude-core:architect`, `ravenclaude-core:code-reviewer`, etc.). Bare names remain reserved for built-in agents.
- Constitution language tightened: `.ravenclaude/runs/` artifact substrate is now **recommended for multi-step runs**, not required for every dispatch. Inline SOP JSON covers single-agent handoffs.
- `code-reviewer.md` and `security-reviewer.md` now include a one-line bridge clarifying that the JSON `status` field mirrors the Markdown Verdict.
- `deep-researcher.md` now distinguishes its per-claim Confidence tag (High/Medium/Low/Speculation) from the SOP run-level `confidence` float.
- Drift cleanup: removed legacy `.claude/rules/...`, `.claude/skills/...`, `.claude/agents/...` label references from agent files (10 files affected). Link targets unchanged; only displayed labels.
- Skill flattening: `skills/researcher/SKILL.md` → `skills/researcher.md` (no other files in the folder; flatten matches the other 10 skills).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up the new agent contracts automatically. If you have downstream parsers reading agent output as pure Markdown, accept or strip the trailing `---RESULT_START--- … ---RESULT_END---` JSON block. Re-run `/init-agent-ready` in any project that wants the new `docs/team-constitution.md` import.

### power-platform 0.6.0 (BREAKING)

- All 10 specialist agents now emit the same Structured Output Protocol JSON block as `ravenclaude-core`, extended with a `licensing_impact` field that mirrors the mandatory `Licensing impact:` line from the existing Power Platform output block.

**Migration for consumers:** same as `ravenclaude-core` — accept or strip the JSON block; existing Markdown output unchanged.

### Hygiene (both plugins + marketplace)

- Maintainer email scrubbed from `marketplace.json` and both `plugin.json` files (own house rule was being violated). New CI guard in `validate-marketplace.yml` fails on any future regression of `matt@ravenpower.net`.
- `guard-destructive.sh` `git reset --hard` regex tightened: previous anchored variants (`origin|HEAD~|@`) let `git reset --hard <branch>` and `git reset --hard <sha>` slip through. New pattern blocks all destinations; `--soft` and `--mixed` still pass.
- `enforce-layout.sh` adds defense-in-depth `..` path-traversal scrub before the allow-list check, with a header comment documenting bash `[[ == ]]` matching semantics so future refactorers don't break the matcher by porting to `find` / filename-expansion.
- Root `CLAUDE.md`: replaced hardcoded `/home/codespace/.claude/projects/...` memory path with portable `~/.claude/projects/<encoded-project-path>/` form. Marketplace-dev hooks section rewritten to accurately document the dual-registration design (in-repo `.claude/settings.json` + plugin's `hooks/hooks.json`) and the migration path.
- `docs/lab/gis-expert.md` now carries a clear STATUS banner identifying it as experimental and not loaded by any agent runtime.

## ravenclaude-core 0.3.0 — earlier in 2026-05

- Agent-readable repo pattern (AGENTS.md + CLAUDE.md + .repo-layout.json) shipped via `/init-agent-ready` slash command.
- Plugin-distributable hooks (`hooks/hooks.json`) added so consumer projects get the same enforcement as marketplace dev.
- 13 specialist agents finalized; spawn-team dispatch playbook stabilized.

## ravenclaude-core 0.1.0 → 0.2.x — early 2026-05

- Initial public release of the Team Lead + 13 specialists pattern.
