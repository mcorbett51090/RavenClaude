---
description: Refresh the team portfolio on demand — collect cross-repo GitHub activity, then regenerate the markdown reports and the HTML dashboard.
allowed-tools: Bash, Read
---

# /portfolio-refresh

On-demand counterpart to the scheduled GitHub Action. Pulls the current cross-repo,
multi-person activity and rebuilds the reports + dashboard so you can see the latest
picture without waiting for the next scheduled run.

## What this does

1. Locate `team-portfolio.json` (the config) at the hub-repo root. If it's missing,
   point the user at `templates/team-portfolio.json` and the `portfolio-setup` skill.
2. Run the collector to pull commits, PRs, and issues across every configured repo:
   ```shell
   python3 <plugin>/scripts/portfolio-collect.py --config team-portfolio.json --out portfolio-activity.json
   ```
3. Render the markdown roll-ups and the HTML dashboard:
   ```shell
   python3 <plugin>/scripts/portfolio-report.py    --activity portfolio-activity.json --out-dir reports --config team-portfolio.json
   python3 <plugin>/scripts/portfolio-dashboard.py --activity portfolio-activity.json --out portfolio.html
   ```
4. Summarize what changed (per-person and per-project deltas) and surface the two
   files the supervisor reads: `reports/weekly-tracker.md` and `portfolio.html`.

`<plugin>` is this plugin's directory inside the RavenClaude clone (e.g.
`~/RavenClaude/plugins/team-portfolio`).

## Token

The collector reads a GitHub token from the environment in this order:
`PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`. For public repos any token works;
for private/other-account repos use a fine-grained PAT with read access. The token is
never written to the config or the artifacts.

## Last-mile

After refreshing, do everything automatable: run all three scripts, stage the updated
`reports/` + `portfolio.html`, and (if the user is on the hub repo and asked) open a PR
or commit. Hand back only the irreducible human step (e.g. "review the weekly tracker").
Deep-link to the rendered `portfolio.html` and the committed `reports/weekly-tracker.md`.
