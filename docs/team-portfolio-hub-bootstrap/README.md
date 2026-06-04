# team-portfolio

> **This README lives at the root of the NEW hub repo, not in this RavenClaude folder.** It's staged here as a copy-ready file — see [`BOOTSTRAP.md`](BOOTSTRAP.md) for the move-it-into-place steps.

Central activity & weekly tracking hub for the team. One place to see who did what across every repo the team works in, with a supervisor's manage-the-team roll-up that a single-repo activity log can't provide.

This repo holds three things — everything else is pulled from GitHub on a schedule:

- [`team-portfolio.json`](team-portfolio.json) — the config: which repos to watch, who's on the team, which cross-repo projects to roll up.
- [`reports/`](reports/) — markdown roll-ups regenerated weekly. `weekly-tracker.md` is what the supervisor reads.
- [`portfolio.html`](portfolio.html) — interactive dashboard, regenerated alongside the reports. Open it locally or publish via GitHub Pages.

## How it stays current

A scheduled GitHub Action ([`.github/workflows/portfolio-tracker.yml`](.github/workflows/portfolio-tracker.yml)) runs **Mondays 13:00 UTC** + **nightly 06:00 UTC**. Each run:

1. Checks out this repo + the `mcorbett51090/RavenClaude` marketplace at `main` (for the Python collector + renderer scripts — pure stdlib, no `pip install`).
2. Calls the GitHub REST API for commits, PRs, and issues across every configured repo within the lookback window.
3. Renders `reports/*.md` + `portfolio.html`.
4. Commits the refreshed files back. The diff is the week-over-week record.

You can also trigger it on-demand: Actions tab → "Team portfolio refresh" → Run workflow.

## Token

The Action reads a token from the environment in this order: `PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`.

- **All tracked repos public:** the built-in `GITHUB_TOKEN` is enough — no secret to add.
- **Any tracked repo private:** create a fine-grained PAT with **read-only** access to those repos, add it as the `PORTFOLIO_TOKEN` secret (Settings → Secrets and variables → Actions).

The token is never written to `team-portfolio.json` or any committed artifact.

## What a supervisor reads

| Surface | When |
| --- | --- |
| [`reports/weekly-tracker.md`](reports/weekly-tracker.md) | Once a week: per-person, per-repo summary for the window. |
| [`reports/project-status.md`](reports/project-status.md) | When a cross-repo project needs status. |
| [`portfolio.html`](portfolio.html) | Anytime: interactive view of everything. |

## Optional narrative layer

To add hand-written context (decisions, blockers, "why" the numbers don't show), set `narrative.enabled: true` in `team-portfolio.json` and drop one `*.md` per note into the configured `narrative.dir` (default `portfolio/narrative/`). The report generator folds every note into the weekly tracker under a **Notes** heading. Template: [`activity-narrative.md`](https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/team-portfolio/templates/activity-narrative.md).

## Add or remove repos / people

Edit `team-portfolio.json`, commit, push. The next scheduled run picks it up. There is no per-tracked-repo setup — those repos need no changes at all.

## Powered by

The [`team-portfolio` plugin](https://github.com/mcorbett51090/RavenClaude/tree/main/plugins/team-portfolio) in the RavenClaude marketplace. Full design + house rules: [`plugins/team-portfolio/CLAUDE.md`](https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/team-portfolio/CLAUDE.md). Schema for the config + activity model: [`plugins/team-portfolio/knowledge/multi-repo-tracking-model.md`](https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/team-portfolio/knowledge/multi-repo-tracking-model.md).
