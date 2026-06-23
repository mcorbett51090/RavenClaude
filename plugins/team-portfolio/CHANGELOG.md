# Changelog — team-portfolio

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.1] — 2026-06-22

Version bump previously unlogged here; the change that set `0.2.1`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.2.0] — 2026-06-05

Value-add build-out for the **tooling** tier of the menu. Because this plugin *is* deterministic scripts (a stdlib collector + markdown/HTML renderers + a scheduled Action), the runtime tier dispositions differently than for an advisory vertical: "add a runnable script" meant filling a real gap (config validation), not introducing the first script. Adds the scenarios bank, two new Mermaid decision trees, and an offline config linter; honestly dispositions bundled-MCP / monitors / LSP / themes as N-A with reasons (`CLAUDE.md` §10).

- **Scenarios bank** (`scenarios/`) — README index already present; added the **3** missing scenarios it referenced so the bank is now complete at **4**: collector rate-limit + token-scope (two distinct `403`s, two fixes), stale dashboard from a 60-day auto-disabled scheduled Action, and project status mis-attributed across repos (filter over/under-match). Schema mirrors the existing `repo-silently-dropped` scenario (`product_version: "n/a"`); each carries an "Action for the next operator" lesson. Surfaced only behind the unverified-scenario preamble (`ravenclaude-core/scenario-retrieval`).
- **2 new Mermaid decision trees** appended to `knowledge/team-portfolio-decision-trees.md` (the file already had 7):
  - **Auth scope at scale — fine-grained PAT vs GitHub App** — the fork *after* the existing built-in-token-vs-PAT tree: PAT (fixed rate limit, tied to a person, simplest) vs GitHub App installation (scales with org size, org-owned, survives departures) with an interim-PAT middle path. Volatile rate-limit numbers marked `[verify-at-use]`.
  - **What to track — per-repo vs per-project vs per-person rollup** — picks the primary rollup axis from the supervisor's actual question, mapping each to the report surface (`project-status.md` / `weekly-tracker.md` / `activity-rollup.md`) and the risk to manage (filter over-match; counts-≠-performance).
- **Runnable script** `scripts/portfolio-config-check.py` (stdlib only, ruff-clean) — an **offline** linter for `team-portfolio.json` that makes **no** network calls. Validates against the exact shape `portfolio-collect.py` reads and flags: a token committed into the config (security — §4 #2), duplicate/malformed `owner/name` repos, a project with no match rules (can never match), a `match.repos` entry absent from `repos[]` (dead rule), a team entry missing a `login`, and `narrative.enabled` without a `dir`. Exit `0`/`1`/`2`; `--strict` fails on warnings. Intended to run in the Action before collection to catch the config-drift classes 3 of the 4 scenarios end on.

### Honestly N-A / recommend-not-bundle (documented, not forced)
- **Bundled MCP server** — the official GitHub MCP is real but **per-tenant / authenticated**, so it is the "RECOMMEND, don't bundle" row of `docs/best-practices/bundled-mcp-servers.md`, never BUNDLE. It is also redundant here: routing collection through an MCP subprocess would defeat the plugin's deterministic, zero-dependency stdlib design (§4 #4, #6). No `mcpServers` entry added.
- **Monitors** — the scheduled GitHub Action already is the background job, and it is per-consumer (their hub repo / cron / token); a marketplace-shipped monitor can't be per-tenant. The stale-dashboard freshness concern is handled operationally and documented in the matching scenario.
- **LSP / `bin/` / output-styles / themes / `settings.json`** — N-A with one-line reasons in `CLAUDE.md` §10.

### Shared-file changes (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers every new path (`plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/CHANGELOG.md`, `plugins/*/knowledge/**`) — no edit needed.
- `.claude-plugin/marketplace.json` catalog `version` must be bumped `0.1.2` → `0.2.0` to match `.claude-plugin/plugin.json`.

## [0.1.2] — initial tooling plugin

Stdlib-only cross-repo activity collector (`portfolio-collect.py`) + markdown roll-up renderer (`portfolio-report.py`) + self-contained HTML dashboard (`portfolio-dashboard.py`), a copy-in scheduled GitHub Action template, an on-demand `/portfolio-refresh` command, an optional hand-maintained narrative layer, 5 skills (portfolio-setup, cross-repo-project-tracking, cross-team-contributor-analysis, portfolio-access-review, report-cadence-tuning), a knowledge bank (multi-repo tracking model + 7 decision trees), and a best-practices set. No agents — by design (core agents drive the tooling).
