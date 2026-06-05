# team-portfolio — plugin constitution

Centralized, multi-repo, multi-person activity & project tracking for a team. This file
governs how the Team Lead and agents behave when a request touches cross-repo activity
tracking, weekly/status roll-ups, or a supervisor's manage-the-team view. It **extends**
`ravenclaude-core` — it inherits the Capability Grounding, Structured Output, Last-Mile
Completion, and Claim-Grounding protocols and does not restate them.

## 1. What this plugin is (and is not)

- **Is:** a thin hub that reads the GitHub API across many repos and rolls activity up by
  person, repo, and cross-repo project — plus the markdown reports, HTML dashboard,
  scheduled Action, and on-demand command around it.
- **Is not:** a replacement for `ravenclaude-core/project-manager` (RAID/status hygiene) or
  the `project-management` plugin (delivery craft). Those run *a* project; this **observes
  activity across all of them**. A request to facilitate a sprint or score a risk register
  routes there; a request to "see who did what across my repos" routes here.

## 2. No agents — by design

This plugin ships **no agents**. Per the marketplace house rule (domain plugins extend core
via skills + knowledge, not parallel agents), the work here is deterministic tooling +
playbooks: the core `project-manager` / `documentarian` agents drive it via the skills and
scripts below. There is no review or architecture judgment that a core agent handed these
skills couldn't produce.

## 3. Routing rules (Team Lead)

| Request signal | Route to |
| --- | --- |
| "track activity across my repos", "who did what", "weekly tracker across repos" | `portfolio-setup` skill → the scripts |
| "track a project that spans repos", "roll up the website work" | `cross-repo-project-tracking` skill |
| "refresh the portfolio / show the latest" | `/portfolio-refresh` command |
| run/own a single project, sprint facilitation, scored risk register | `project-management` plugin (not here) |
| RAID/status hygiene on one effort | `ravenclaude-core/project-manager` (not here) |

## 4. House opinions (every invocation enforces)

1. **GitHub is the source of truth; logs are the optional narrative layer.** Never propose a
   tracking doc *inside each tracked repo* — that is the exact failure this plugin exists to
   fix. The hub reads GitHub; it does not ask repos to self-report.
2. **Secrets live in env/secrets, never in `team-portfolio.json`.** The token is read from
   `PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`. If you ever find a token in the config,
   flag it as a security issue.
3. **Least privilege.** A read-only token scoped to the tracked repos — never org-admin,
   never write — is the recommendation. Don't suggest a broader scope than the task needs.
4. **Zero runtime dependencies.** The scripts are pure standard library so they run in a bare
   GitHub Action and a plain `python3` session unchanged. Don't add `requests` / PyYAML /
   anything that needs `pip install`; if a feature seems to need one, reach for the stdlib
   equivalent or reconsider.
5. **Fail soft per repo.** One unreadable repo (private, 404'd, renamed) records an error and
   is skipped — it never sinks the whole run. Preserve that property in any change.
6. **Deterministic output.** Same input → same `portfolio-activity.json`, same reports, same
   HTML. Don't introduce nondeterminism (unsorted dict iteration, timestamps in rendered
   bodies beyond the declared `generated_at`).

## 5. Anti-patterns to flag

- A token committed to the config or printed into an artifact / log.
- Re-introducing a per-repo activity log "as well" — it re-creates the blind spot.
- Claiming counts are complete when the run was unauthenticated or skipped repos (the
  reports/dashboard surface both states with a banner — keep it honest).
- Treating "unmatched" activity (no project) as an error — it's normal.

## 6. Skills in this plugin

| Skill | Use for |
| --- | --- |
| [`portfolio-setup`](skills/portfolio-setup/SKILL.md) | Stand up the hub: config, token, Action, command, optional narrative. |
| [`cross-repo-project-tracking`](skills/cross-repo-project-tracking/SKILL.md) | Define + track a project spanning multiple repos (repo / label / title-prefix match). |

## 7. Scripts, templates & knowledge

- `scripts/portfolio-collect.py` — GitHub REST API → `portfolio-activity.json` (stdlib only).
- `scripts/portfolio-report.py` — activity JSON → `weekly-tracker.md` + `activity-rollup.md` +
  `project-status.md`.
- `scripts/portfolio-dashboard.py` — activity JSON → self-contained `portfolio.html`.
- `scripts/portfolio-config-check.py` — **offline** linter for `team-portfolio.json` (no network):
  flags a token committed into the config, duplicate/malformed `owner/name` repos, a project with
  no match rules (can never match), a `match.repos` entry not in `repos[]` (dead rule), a team entry
  missing a `login`, and `narrative.enabled` without a `dir`. Exit `0`/`1`/`2`; `--strict` fails on
  warnings. Run it in the Action before `portfolio-collect.py` to catch config drift before a run.
- `templates/team-portfolio.json` — the config schema (copy to the hub repo).
- `templates/portfolio-tracker.yml` — the scheduled GitHub Action (copy to the hub repo).
- `templates/activity-narrative.md` — optional hand-maintained note template.
- `templates/sample-activity.json` — fixture for an offline demo of the renderers.
- [`knowledge/multi-repo-tracking-model.md`](knowledge/multi-repo-tracking-model.md) — the
  event data model, gathering boundaries, the where-should-tracking-live decision tree, and
  the privacy posture.

## 8. Seams to neighbouring plugins

- **`project-management`** — owns running a project (schedule, EVM, sprints, risk registers).
  This plugin feeds it observed cross-repo activity; it does not duplicate delivery craft.
- **`ravenclaude-core/project-manager`** — lightweight RAID/status hygiene on a single effort.
- **`ravenclaude-core/documentarian`** — prose polish on the narrative layer.
- **`ravenclaude-core/security-reviewer`** — any token-handling / scope question escalates here.

## 9. Requires

`ravenclaude-core@>=0.7.0`.

## 10. Value-add completeness (build-out 2026-06-05)

This is a **tooling** plugin — the deliverable is deterministic scripts (collector + renderers + a
scheduled Action), not advisory agents. Several runtime-tier menu items therefore disposition
differently than they would for a content/advisory vertical: the plugin *already is* the code tier,
so "add a runnable script" means "fill a genuine gap," not "introduce the first one." Every item is
dispositioned honestly below.

| Item | Disposition | Note |
|---|---|---|
| scenarios/ bank | **BUILT** | README index + 4 dated, scope-tagged scenarios (repo silently dropped / collector rate-limit + token-scope `403`s / stale dashboard from an auto-disabled scheduled Action / project status mis-attributed across repos). Schema mirrors the existing scenario; surfaced only behind the unverified-scenario preamble (`scenario-retrieval`). |
| Decision-tree (Mermaid) knowledge | **BUILT (extended existing)** | Added 2 new trees to `knowledge/team-portfolio-decision-trees.md` (already had 7): **auth scope at scale — fine-grained PAT vs GitHub App** (the fork *after* the existing built-in-token-vs-PAT tree), and **what to track — per-repo vs per-project vs per-person rollup axis**. Volatile rate-limit numbers marked `[verify-at-use]`. |
| Runnable script (`scripts/`) | **BUILT** | `scripts/portfolio-config-check.py` — the one real runtime gap. Collect/report/dashboard existed; nothing validated the config first. Offline, stdlib-only, ruff-clean; catches the exact drift classes 3 of the 4 scenarios end on (drifted/duplicate repo, token-in-config, dead project rule). |
| Bundled MCP server | **N-A (recommend-not-bundle)** | The official GitHub MCP server is real, but it is **per-tenant / authenticated** (PAT or OAuth) — the "RECOMMEND, don't bundle" row of [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), never BUNDLE (can't hardcode a consumer's credential). And it is **redundant here**: this plugin's whole point is a *deterministic, diffable, zero-dependency* stdlib collector reading the REST API directly (CLAUDE.md §4 #4) — routing collection through an MCP subprocess would defeat determinism and portability. No MCP entry added. |
| LSP integration | **N-A** | LSP is a code-editing protocol for a source language; the scripts are the operated artifact, not edited via LSP in this plugin's flow. |
| `bin/` executables | **N-A** | The `scripts/*.py` are the executables (stdlib, `python3 script.py`); no compiled/installed binary warranted. |
| Monitors / background jobs | **N-A (by design)** | The scheduled GitHub Action **is** the background job, and it is per-consumer (their hub repo, their cron, their token) — a marketplace-shipped monitor can't be per-tenant. The freshness concern (a stale dashboard from a stopped Action) is handled operationally + documented in the stale-dashboard scenario, not as a bundled monitor. |
| output-styles / themes | **N-A** | Output is governed by the deterministic renderers (markdown + a self-contained HTML dashboard); §4 #6 determinism is the contract, not a swappable style. |
| `settings.json` / permissions tuning | **N-A** | No tool-permission surface specific to this plugin beyond `ravenclaude-core`. |
| skills / hooks / commands / templates | **SUFFICIENT** | 5 skills, `/portfolio-refresh` command, 4 templates already cover the surface. The new config-check script + 2 decision trees extend reach without a new skill or hook; no high-value gap this round (and **no agents — by design**, §2). |
| CHANGELOG.md | **BUILT** | Added with a top `0.2.0` entry. |
| NOTICE.md | **N-A** | No third-party content bundled — the scripts are original and stdlib-only; no vendored source, no bundled MCP. |

## 11. Milestones

- **v0.1.x** — initial tooling plugin: stdlib collector + markdown/HTML renderers + scheduled Action
  template + `/portfolio-refresh`, 5 skills, knowledge bank (tracking model + 7 decision trees),
  best-practice rules. No agents by design (§2).
- **v0.2.0** — value-add build-out: scenarios bank (4 scenarios + README index), 2 new Mermaid
  decision trees (PAT-vs-App auth scope; rollup-axis selection), `scripts/portfolio-config-check.py`
  (offline config linter), CHANGELOG. Runtime-tier items (bundled MCP, monitors, LSP, themes)
  dispositioned N-A with reasons (§10).
