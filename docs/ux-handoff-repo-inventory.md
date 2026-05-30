# RavenClaude — Repo Inventory for UX Handoff

A complete component inventory of the RavenClaude marketplace, written for a UX designer who has never seen this repo. The goal is to map the full surface — what it IS, what it contains, and every interactive/actionable element a dashboard could expose.

Everything below is grounded in the files cited. Anything not verifiable from the files is marked **[unverified]**. Marketplace version at time of writing: **0.32.0** (`/.claude-plugin/marketplace.json` → `metadata.version`).

---

## 1. What this repo is

RavenClaude is a **private Claude Code plugin marketplace**. The "product" of the repo is the contents of `plugins/` — the repo itself is never loaded into a consumer project; only individual plugins are installed via Claude Code's native `/plugin marketplace add` / `/plugin install <name>@ravenclaude` mechanism (one-way, read-only distribution). Each plugin bundles agents, skills, hooks, rules, knowledge, best-practices, and templates that travel with the user across projects. The same plugin content also runs under **GitHub Copilot CLI** via a live-from-disk bridge (`scripts/ravenclaude` materializes a Copilot package; nothing is cached — an update is just `git pull` + re-materialize). Sources: `README.md`, `docs/architecture.md`, `AGENTS.md`, `scripts/ravenclaude`.

---

## 2. The big systems

| System | What it is | Where it lives |
|---|---|---|
| **Command-review tribunal ("the Thing")** | Opt-in. A tiered panel of "seats" votes **allow / edit / deny** on a proposed command/tool call before it runs, with a human gate. Has a safety envelope (off→defer, high-blast→defer, abstain/split/injection→defer). Off by default. | `plugins/ravenclaude-core/scripts/thing-decide.py`, `thing-decision.py`, `thing-concerns.py`, `thing-seat.sh`; hook `hooks/thing-orchestrator.sh`; skill `skills/thing/` |
| **Decision review** | Routes yes/no decisions through the same tribunal seats and returns `yes` / `no` / `defer`. A `PreToolUse(AskUserQuestion)` hook intercepts binary yes/no questions so routing isn't dependent on the model remembering. Binding `yes`/`no` proceeds without paging the human; `defer` asks the human. | `skills/decision-review/`, `hooks/route-decision-review.sh`, `scripts/thing-decide.py`; docs `docs/post-pr-decision-review.md` |
| **Comfort-posture permission system** | Point-and-click permission model. A YAML (`.ravenclaude/comfort-posture.yaml`) sets per-category autonomy on a 3-level **deny → ask → allow** scale, per layer (**user / local / project**) and per individual permission. A translator emits narrow `permissions.{allow,ask,deny}` rules into `.claude/settings.json`. Schema v5 = per-layer. | `skills/set-posture/`, `commands/set-posture.md`, `scripts/apply-comfort-posture.py`, `.ravenclaude/comfort-posture.yaml` |
| **Guardrail pipeline (the hook lifecycle)** | A chain of hooks firing across the Claude Code event lifecycle: **SessionStart → PreToolUse → PostToolUse → Stop**. See the per-event table in §5 (Pipeline tab) and the hook list below. | `plugins/ravenclaude-core/hooks/hooks.json` |
| **Decision trees** | Canonical `## Decision Tree:` sections authored across plugins (many as Mermaid diagrams) — e.g. agent-routing, PCF React surface, governor limits, automation density. Surfaced marketplace-wide in the dashboard **Guidance** tab. | Each plugin's `knowledge/` + agent files; discovered by `scripts/generate-dashboards.py` |
| **Best practices** | Cross-domain rules with rationale + how-to-apply + provenance, one file per rule (root `docs/best-practices/`), plus per-plugin `best-practices/` dirs. | `docs/best-practices/`, `plugins/*/best-practices/` |
| **The Researcher** | A meta-skill for knowledge freshness: invoked when information feels uncertain/time-sensitive; returns findings in Structured Output Protocol format and applies the Capability Grounding Protocol to its own output. | `skills/researcher/` |
| **Structured Output Protocol** | Required for agent handoffs. Every specialist agent ends its report with a `---RESULT_START--- … ---RESULT_END---` delimited JSON block alongside human-readable Markdown; the Team Lead reads the JSON to drive routing. | `skills/structured-output/`, core `CLAUDE.md` |
| **Capability Grounding Protocol** | The "floor": an agent must not falsely claim it is blocked; it checks the environment + decision trees, enumerates alternate methods, and reports blockage honestly. | core `CLAUDE.md`; hook `hooks/capability-orientation.sh`; skill `skills/environment-discovery/` |
| **Claim Grounding & Source Honesty Protocol** | Consequential claims must cite a this-session check inline or be tagged `[unverified — training knowledge]`; never falsely concede on correction (verify first). Linted on write. | core `CLAUDE.md`; hook `hooks/claim-grounding-lint.sh` |
| **Last-Mile Completion Protocol** | The "ceiling": once an agent confirms it *can* act, it carries the work as far as its authority allows, leaving the human only the irreducibly-human residue (a confirm or a click). | core `CLAUDE.md` (added 2026-05-28) |

---

## 3. The 13 plugins

Counts: agents/templates/knowledge/best-practices = files in those dirs; skills = sub-directories under `skills/`; hooks = files in `hooks/` (includes `hooks.json` + the `copilot-hook-adapter.sh`, so the *behavioral* hook count is typically one or two fewer). Only `ravenclaude-core` ships `commands/` and `rules/`. Sources: directory counts + `.claude-plugin/marketplace.json` + `docs/architecture.md`.

| Plugin | Purpose (1 line) | Agents | Skills | Commands | Hooks | Knowledge | Best-prac | Templates |
|---|---|---|---|---|---|---|---|---|
| **ravenclaude-core** | Domain-neutral Team Lead + specialists; protocols, posture, tribunal, dashboard | 14 | 22 | 4 | 15 | 5 | 4 | 12 (+4 rules) |
| **power-platform** | Microsoft Power Platform specialist team (+ bundled pbix-mcp) | 11 | 18 | 0 | 3 | 7 | 4 | 1 |
| **finance** | Corporate finance & FP&A specialists | 7 | 9 | 0 | 2 | 1 | 4 | 8 |
| **regulatory-compliance** | Financial-regulatory & compliance specialists (PII-scrub hook) | 6 | 9 | 0 | 2 | 1 | 4 | 8 |
| **web-design** | Web design & build (WCAG / Core Web Vitals / SEO / Fluent) | 7 | 10 | 0 | 2 | 7 | 3 | 8 |
| **edtech-partner-success** | EdTech Partner Success Manager team | 6 | 12 | 0 | 2 | 16 | 3 | 15 |
| **data-platform** | Non-Microsoft / SMB embedded analytics | 4 | 11 | 0 | 2 | 13 | 3 | 11 |
| **applied-statistics** | "Is this difference/trend statistically REAL?" | 1 | 5 | 0 | 2 | 5 | 3 | 4 |
| **microsoft-fabric** | Microsoft Fabric (OneLake / Lakehouse / Direct Lake) | 7 | (see note) | 0 | 2 | 9 | 4 | 6 |
| **claude-app-engineering** | Building apps on Claude API + Agent SDK + MCP | 6 | (see note) | 0 | 2 | 13 | 4 | 6 |
| **azure-cloud** | Azure infrastructure & platform | 7 | (see note) | 0 | 2 | 10 | 4 | 6 |
| **salesforce** | Salesforce platform (Apex / Flow / Agentforce / sharing / 2GP) | 5 | 5 | 0 | 2 | 9 | 6 | 5 |
| **microsoft-365-copilot** | M365 Copilot extensibility & administration | 6 | 5 | 0 | 2 | 9 | 4 | 5 |

Note: `microsoft-fabric`, `claude-app-engineering`, and `azure-cloud` had **no `skills/` directory present** at inventory time (their capability is carried in `knowledge/` + agents). The marketplace descriptions reference skills for some; this is a knowledge-vs-skills packaging difference, not necessarily a defect — **[unverified whether intentional]**.

**ravenclaude-core's 14 agents:** architect, backend-coder, frontend-coder, fullstack-coder, code-reviewer, security-reviewer, tester-qa, data-engineer, project-manager, documentarian, designer, prompt-engineer, deep-researcher, partner-success-manager.

**ravenclaude-core's 22 skills:** agent-quality-rubric, audit-ci-gates, cleanup-worktrees, contribute-finding, create-pr, cross-platform-determinism, decision-review, draft-agent-brief, environment-discovery, knowledge-file-staleness-sweep, new-worktree, permission-hygiene, plugin-release-checklist, prompt-pattern-library, researcher, review-staged-contributions, run-full-test-suite, scenario-retrieval, set-posture, spawn-team, structured-output, thing.

**ravenclaude-core's 15 hook files:** capability-orientation, claim-grounding-lint, copilot-hook-adapter, dod-gate, enforce-layout, ensure-default-mode, format-on-write, guard-destructive, guard-recursive-spawn, reapply-posture, remind-tests, route-decision-review, runaway-brake, thing-orchestrator (+ `hooks.json`).

---

## 4. Slash commands

All four slash commands ship from `ravenclaude-core` (`plugins/ravenclaude-core/commands/*.md`). "Shell-executable" = backed by a runnable script/server the dashboard can invoke; "In-Claude" = a prompt-driven workflow Claude runs.

| Command | Plugin | What it does | Executable surface |
|---|---|---|---|
| `/dashboard` | ravenclaude-core | Launches the functional local comfort-posture dashboard in the browser (Save & apply writes config). Runs the bundled `serve-dashboards.py` on `127.0.0.1`. | **Shell-executable** (server + `scripts/open-dashboard.sh`, `rc dashboard`) |
| `/set-posture` | ravenclaude-core | Translates `.ravenclaude/comfort-posture.yaml` into `.claude/settings.json` allow/ask/deny rules (per-layer, schema v5). | **Shell-executable** (`scripts/apply-comfort-posture.py`) |
| `/init-agent-ready` | ravenclaude-core | Guided setup: writes `AGENTS.md`, `CLAUDE.md`, `docs/team-constitution.md`, `.repo-layout.json`, optional CI workflow + prettier/gate scaffold, tailored to repo type. | **In-Claude** (prompt-driven; writes files) |
| `/wrap` | ravenclaude-core | End-of-engagement capture: turns a lesson into a structured 9-field scenario YAML+markdown file under `plugins/<plugin>/scenarios/`. | **In-Claude** (prompt-driven) |

The `scripts/ravenclaude` CLI (the Copilot bridge / install path) additionally exposes shell verbs **`setup` / `install` / `update` / `status`** (and the `rc` launch alias). These are the actions the dashboard's `/__run` endpoint allow-lists (install / update / status). Source: `scripts/ravenclaude`, `commands/*.md`.

---

## 5. The dashboard today

The dashboard is a single generated `plugins/ravenclaude-core/dashboard.html` (built by `scripts/generate-dashboards.py`). Tab order and labels are canonical from the nav bar in that script. The published GitHub-Pages copy is **static** (read-only preview); the **functional** copy is served locally by `serve-dashboards.py` where Save/run endpoints work.

| Tab (in nav order) | data-tab | What it does |
|---|---|---|
| **Settings** | `settings` | Schema-driven form for the comfort-posture YAML — per-tool file/network/shell/package autonomy across deny→ask→allow, per layer (user/local/project), plus command-review (Thing) toggles. Save & apply writes the YAML and re-runs the translator. Hydrates from `/__read`; saves via `/__save`. |
| **Pipeline** | `pipeline` | Visualizes the all-events guardrail flow (SessionStart → PreToolUse → PostToolUse → Stop) with live per-hook state hydrated from config/run artifacts. |
| **Install & Update** | `install` | One-click buttons (Install / Update / Status) plus copy-to-clipboard command blocks for wiring the plugins. Buttons call `/__run`; disabled on a static host. |
| **Test a command** (Simulator) | `simulator` | Type a command and run it through the real Thing classifier to see the tribunal verdict (allow/edit/deny + reasoning). Calls `/__classify`; disabled on static host. |
| **Learn** | `learn` | Searchable concept registry (embedded at build time, fully offline) with concept chips/tooltips linking concepts. |
| **Review log** (Saga) | `saga` | Live, filterable table of the last N command-review (Thing) verdicts from `.ravenclaude/runs/thing/`. Reads `/__saga`. |
| **Commands** | `commands` | Card grid of every marketplace slash command. |
| **Guidance** | `trees` | Marketplace-wide: every plugin's `## Decision Tree:` sections + best practices, auto-discovered across plugins. |
| **Activity** | `activity` | Newest-first feed of multi-step runs from `.ravenclaude/runs/` (summary, structured-result status, event count). Reads `/__runs`. |

Source: `scripts/generate-dashboards.py` (nav bar + `_render_*_tab` functions).

---

## 6. Server endpoints

Served by `scripts/serve-dashboards.py`, bound to `127.0.0.1` (single-user/local; no auth, no multi-user). Each endpoint enforces an Origin/Host CSRF guard and an allow-list. **Served vs static distinction:** on the local served dashboard these endpoints exist and the action buttons are enabled (probed with `HEAD`); on a static host (e.g. GitHub Pages) the endpoints are absent and the corresponding buttons are disabled.

| Endpoint | Method | What it does | Allow-list / scope |
|---|---|---|---|
| `/__save` | POST | Writes an allow-listed config file (then re-runs the posture translator so `.claude/settings.json` updates immediately). | `ALLOWED_TARGETS`: `.ravenclaude/comfort-posture.yaml`, `.ravenclaude/environment-context.md`, + JSON-edit targets. JSON writes structurally pre-validated. |
| `/__read` | GET | Hydrates dashboard controls from the project's actual committed config on load (YAML returned server-side parsed). | `ALLOWED_READ` mirrors `ALLOWED_TARGETS`. |
| `/__run` | POST | Runs a FIXED, allow-listed `ravenclaude <action>` (no caller args, no shell) — powers Install & Update buttons. | `ALLOWED_ACTIONS`: `install`, `update`, `status`. |
| `/__classify` | POST | Runs the real Thing decision classifier on a submitted command — powers the "Test a command" simulator. Read-only. | Body: `{command}`; returns verdict JSON. |
| `/__saga` | GET | Returns the last N command-review verdicts from `.ravenclaude/runs/thing/` (enriched with base/final tier). Read-only. | `?limit=N`; CSRF-guarded. |
| `/__runs` | GET | Returns recent multi-step runs from `.ravenclaude/runs/` (thing/ verdict dir excluded — owned by `/__saga`). Read-only. | `?limit=N`; CSRF-guarded. |

Security posture (from the file + `commands/dashboard.md`): only fixed actions/paths are allowed, no arbitrary-command surface, binds localhost only. Note `commands/dashboard.md` describes a hardened launch variant with **no `/__run`** at all; the full server defines `/__run` for Codespace/local dev. **[unverified — which variant a given launch uses depends on how it's started.]**

---

## 7. Actionable surface for a dashboard

Everything a user might want to **DO** or **SEE**, grounded in the tabs/endpoints/commands above:

**Do (write / run):**
- Edit and **Save & apply** the comfort posture — per category, per level (deny/ask/allow), per layer (user/local/project) — writing YAML and translating to `.claude/settings.json` in one click (Settings → `/__save` + apply).
- **Toggle the command-review tribunal (the Thing)** on/off per category and tune its mode (Settings; `command_review` in the YAML).
- **Toggle / configure decision review** mode (`off | advisory | binding`) — the yes/no auto-routing knob.
- **Install / Update / Status** the plugin wiring with one click (Install & Update → `/__run`).
- **Test a command against the Thing** — type a command, see the live allow/edit/deny verdict + reasoning (Test a command → `/__classify`).
- Run the `/init-agent-ready`, `/wrap`, `/set-posture`, `/dashboard` slash commands (Commands tab as a launcher surface).

**See (read / browse):**
- The **guardrail pipeline** as a live flow across SessionStart → PreToolUse → PostToolUse → Stop, with per-hook state (Pipeline).
- The **Review log** of past tribunal verdicts, filterable, with tier enrichment (Review log → `/__saga`).
- The **Activity feed** of recent multi-step runs and their structured-result status (Activity → `/__runs`).
- **Decision trees + best practices** across every plugin, marketplace-wide (Guidance).
- **Concepts / Learn** — searchable embedded concept registry with tooltips (Learn).
- The **slash-command catalog** as cards (Commands).
- The **plugin / agent / skill / hook / template inventory** — currently surfaced in the separate generated `repo-guide.html` (by `scripts/generate-repo-guide.py`), an "I want to…" use-case lookup across all plugins; a candidate to fold into the dashboard. **[unverified whether intended for the dashboard]**

**Latent / not-yet-surfaced opportunities (grounded in repo contents, not yet a tab):**
- Browse the full **per-plugin agent cards + scenarios** (the repo-guide content) inside the dashboard.
- Surface **knowledge-file staleness** (there is a `knowledge-file-staleness-sweep` skill) as a freshness indicator.
- Expose **scenarios** captured via `/wrap` as a browsable lessons-learned feed.
