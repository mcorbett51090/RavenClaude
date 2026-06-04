# team-portfolio hub — bootstrap kit

Copy-ready scaffolding for a new dedicated hub repo that runs the [`team-portfolio` plugin](../../plugins/team-portfolio/) — centralized cross-repo, per-person activity tracking with weekly markdown reports + an HTML dashboard.

These files are **artifacts to copy out**, not active config for this RavenClaude marketplace. Nothing in this folder fires on its own.

## Why this folder exists

A fresh GitHub session can't create the new repo from inside this Codespace (the MCP integration's token returns `403 Resource not accessible by integration` on `POST /user/repos`, and the documented fallbacks — `gh` CLI, direct API curl — are cut off in the web/remote environment). So instead of half-creating the hub from a session that can't finish the job, the four files needed to stand it up are staged here for you to copy across once the new repo exists.

## What's here

| File in this folder | Goes where in the new hub repo | Purpose |
| --- | --- | --- |
| `team-portfolio.json` | repo root | The hub config. Placeholders for `repos`, `team`, `projects` — fill in once. Secrets never live here. |
| `portfolio-tracker.yml` | `.github/workflows/portfolio-tracker.yml` | Scheduled Action: weekly + nightly collect → render → commit-back. Verbatim copy of `plugins/team-portfolio/templates/portfolio-tracker.yml`. |
| `README.md` | repo root (overwrite the auto-init one) | One-screen orientation for anyone who lands in the hub: what it is, where the reports are, how to trigger a refresh. |
| `.gitignore` | repo root | Ignores `_ravenclaude/` (the Action's workspace clone of the marketplace). |

## Setup — 6 steps

1. **Create the empty hub repo.** GitHub UI → New repository → name `team-portfolio` (or any name you like) → Private → "Add a README" → Create. ~30 seconds.

2. **Copy these four files in.** Either clone the new repo locally and drop them in, or use the GitHub UI's "Add file → Upload files". Overwrite the auto-init `README.md`. The workflow file goes at `.github/workflows/portfolio-tracker.yml`.

3. **Fill in `team-portfolio.json`.** Replace the empty `repos: []` and `team: []` arrays with your real values. Set `supervisor` if you want the manage-the-team framing. Add `projects[]` entries for any cross-repo project worth a roll-up. The schema is documented in `plugins/team-portfolio/knowledge/multi-repo-tracking-model.md` of this marketplace. Delete the `_TODO` keys once you've filled them in (the collector ignores them, but they're noise).

4. **Decide the token.**

   | Situation | Token |
   | --- | --- |
   | All tracked repos public, hub repo in the same account as RavenClaude | Built-in `GITHUB_TOKEN` is enough. No secret to add. |
   | Any tracked repo is private | Create a fine-grained PAT with **read-only** access to those repos, add as `PORTFOLIO_TOKEN` secret on the hub repo (Settings → Secrets and variables → Actions). |
   | **Hub repo is in a different account than `mcorbett51090/RavenClaude`** | The `PORTFOLIO_TOKEN` PAT also needs read access to `mcorbett51090/RavenClaude` (the workflow checks it out at line 38–43 for the Python scripts), **and** you must add `token: ${{ secrets.PORTFOLIO_TOKEN }}` to that second checkout step in `.github/workflows/portfolio-tracker.yml` — the default `GITHUB_TOKEN` from a workflow in account B cannot read a private repo in account A. |

5. **First run.** Hub repo → Actions tab → "Team portfolio refresh" → Run workflow. With an empty config that completes in ~10 seconds and commits empty `reports/` + `portfolio.html` back — proving the pipeline works. With a populated config it commits the real roll-up.

6. **(Optional) Publish the dashboard.** Hub repo → Settings → Pages → Source = `main` branch root → Save. The committed `portfolio.html` becomes a URL the supervisor can bookmark.

## Verify the renderers without any of the above

Before creating any repo, prove the scripts run on your box against the bundled sample fixture:

```shell
PLUGIN=/home/user/RavenClaude/plugins/team-portfolio
mkdir -p /tmp/portfolio-verify/reports
python3 "$PLUGIN/scripts/portfolio-report.py"    --activity "$PLUGIN/templates/sample-activity.json" --out-dir /tmp/portfolio-verify/reports
python3 "$PLUGIN/scripts/portfolio-dashboard.py" --activity "$PLUGIN/templates/sample-activity.json" --out  /tmp/portfolio-verify/portfolio.html
```

Pass criterion: all four output files exist (`weekly-tracker.md`, `activity-rollup.md`, `project-status.md`, `portfolio.html`) and the HTML opens with real content.

## Full walkthrough

The plugin's own setup skill has the long version with all the trade-offs: [`plugins/team-portfolio/skills/portfolio-setup/SKILL.md`](../../plugins/team-portfolio/skills/portfolio-setup/SKILL.md). The cross-repo project model: [`plugins/team-portfolio/knowledge/multi-repo-tracking-model.md`](../../plugins/team-portfolio/knowledge/multi-repo-tracking-model.md). The on-demand command: [`plugins/team-portfolio/commands/portfolio-refresh.md`](../../plugins/team-portfolio/commands/portfolio-refresh.md).

## House rules carried over from the plugin

- **Never** put a token in `team-portfolio.json`. Env/secrets only (`PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`).
- **Never** add a per-repo activity log to the tracked repos as well — it re-creates the blind spot this hub exists to fix.
- Least privilege: a read-only PAT scoped to exactly the tracked repos. Not org-admin, not write.
