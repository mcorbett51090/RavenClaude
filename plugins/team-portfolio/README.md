# team-portfolio

**Centralized, multi-repo, multi-person activity & project tracking** — one place to see who
did what across all your repositories, and a manage-the-team view for a supervisor.

If you're running an activity log / weekly tracker / status doc inside one repo and it can't
see what's happening in your other repos, this is the fix. A per-repo log can't see the repo
next door. GitHub already attributes every commit, PR, and issue to a person across all your
repos — this plugin reads it and rolls it up into reports and a dashboard.

## What you get

| Piece | What it does |
| --- | --- |
| **Collector** (`scripts/portfolio-collect.py`) | Pulls commits, PRs, and issues across every configured repo from the GitHub API → one normalized `portfolio-activity.json`. Pure stdlib, no `pip install`. |
| **Reports** (`scripts/portfolio-report.py`) | `weekly-tracker.md` (per-person, per-repo), `activity-rollup.md` (chronological feed), `project-status.md` (cross-repo projects). Committed + diffable. |
| **Dashboard** (`scripts/portfolio-dashboard.py`) | A self-contained `portfolio.html` — no CDN, no server; open it or publish to Pages. |
| **Scheduled refresh** (`templates/portfolio-tracker.yml`) | A GitHub Action you drop into the hub repo: weekly + nightly, commits the roll-up back. |
| **On-demand** (`/portfolio-refresh`) | Refresh the whole picture anytime from your Claude Code session. |
| **Narrative layer** (optional) | Hand-maintained `*.md` notes folded into the weekly tracker for the "why" the counts miss. |

## How it works

```
   tracked repos (read via GitHub API)
   └──► portfolio-collect.py ──► portfolio-activity.json
                                   ├──► portfolio-report.py    ──► reports/*.md   (supervisor reads)
                                   └──► portfolio-dashboard.py ──► portfolio.html (interactive)
```

You designate one **hub repo** to hold the config + reports + dashboard. The repos being
*tracked* need no changes at all.

## Quickstart

1. Pick a hub repo (a dedicated `team-portfolio` repo is cleanest).
2. Copy [`templates/team-portfolio.json`](templates/team-portfolio.json) to its root and edit
   `repos`, `team`, and `projects`.
3. Prove the renderers work with the bundled fixture (no token needed):
   ```shell
   PLUGIN=~/RavenClaude/plugins/team-portfolio
   python3 "$PLUGIN/scripts/portfolio-dashboard.py" --activity "$PLUGIN/templates/sample-activity.json" --out /tmp/portfolio.html
   ```
4. Copy [`templates/portfolio-tracker.yml`](templates/portfolio-tracker.yml) to the hub repo's
   `.github/workflows/`, add a `PORTFOLIO_TOKEN` secret if any repo is private, and let it run —
   or run `/portfolio-refresh` on demand.

Full walkthrough: the **`portfolio-setup`** skill.

## When to use / not use

**Use it** when work spans 2+ repos, you need per-person attribution, or a supervisor needs a
cross-repo roll-up. **Skip it** for a single repo — GitHub's per-repo Insights are enough.

## Security

The GitHub token is read from the environment (`PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`)
and **never** stored in the config or the artifacts. Scope it read-only to exactly the tracked
repos.

## Requires

`ravenclaude-core@>=0.7.0` (inherits the Capability Grounding, Structured Output, and
Last-Mile protocols). See [`CLAUDE.md`](CLAUDE.md) for the team constitution and
[`knowledge/multi-repo-tracking-model.md`](knowledge/multi-repo-tracking-model.md) for the
data model.
