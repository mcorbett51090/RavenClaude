---
name: portfolio-setup
description: "Stand up centralized multi-repo, multi-person activity tracking for a team. Use when a team works across several GitHub repos and needs one place to see who did what — and a supervisor needs a manage-the-team roll-up that a single-repo activity log can't provide. Walks choosing a hub repo, writing team-portfolio.json (repos + roster + cross-repo projects), wiring the scheduled GitHub Action and the on-demand command, picking a GitHub token, and optionally enabling a hand-maintained narrative layer."
---

# Skill: Portfolio setup

Goal: a working centralized tracker in well under an hour. The hard truth up front —
**a per-repo activity log can never see the repo next door.** GitHub already attributes
every commit, PR, and issue to a person across all repos; this plugin just reads it and
rolls it up. So the design is "one small hub that pulls from GitHub," not "a log inside
each repo."

## Step 0 — Decide where the hub lives

The hub is one repo that holds the config + the generated reports + the dashboard. It
does **not** need to be a repo anyone codes in. Options, smaller-blast-radius first:

- **A dedicated `team-portfolio` repo** (recommended) — clean, nothing else touches it,
  easy to give a supervisor read access without granting anything else.
- **An existing "home base" repo** the team already reads.

The repos being *tracked* need no changes at all — they're read through the API.

## Step 1 — Write the config

Copy [`templates/team-portfolio.json`](../../templates/team-portfolio.json) to the hub
repo root as `team-portfolio.json` and edit:

- `repos` — every `owner/name` to monitor (public or private).
- `team` — one entry per person: `login` (GitHub username), `name`, optional `role`.
- `supervisor` — optional; frames the roll-up as a manage-the-team view.
- `projects` — cross-repo projects (see the `cross-repo-project-tracking` skill).
- `window_days` — default lookback for the weekly tracker (7 is typical).

**Never put a token in this file.** It is read from the environment only.

## Step 2 — Pick a token

The collector reads `PORTFOLIO_TOKEN` → `GITHUB_TOKEN` → `GH_TOKEN`.

| Situation | Token |
| --- | --- |
| All tracked repos are public | the Action's built-in `GITHUB_TOKEN` is enough |
| Any private repo, or repos in another account/org | a **fine-grained PAT** with read on those repos, stored as the `PORTFOLIO_TOKEN` secret |

Least privilege: read-only, scoped to exactly the tracked repos.

## Step 3 — Automate it (scheduled + on-demand)

- **Scheduled:** copy [`templates/portfolio-tracker.yml`](../../templates/portfolio-tracker.yml)
  into the hub repo at `.github/workflows/portfolio-tracker.yml`. It refreshes weekly
  (Mondays) + nightly and commits the reports + dashboard back — the diff is the record.
- **On-demand:** run `/portfolio-refresh` (or the three scripts directly) anytime you want
  the current picture.

## Step 4 — Verify with the sample, then go live

Prove the renderers work before any token is involved, using the bundled fixture:

```shell
PLUGIN=~/RavenClaude/plugins/team-portfolio
python3 "$PLUGIN/scripts/portfolio-report.py"    --activity "$PLUGIN/templates/sample-activity.json" --out-dir /tmp/reports
python3 "$PLUGIN/scripts/portfolio-dashboard.py" --activity "$PLUGIN/templates/sample-activity.json" --out /tmp/portfolio.html
```

Then do a real collect against your config (Step 1) with a token in the environment.

## Step 5 — Optional narrative layer

If your manager wants context beyond the raw counts (decisions, blockers, "why"), set
`narrative.enabled: true` and drop one `*.md` per note into `narrative.dir` (template:
[`templates/activity-narrative.md`](../../templates/activity-narrative.md)). The report
generator folds them into the weekly tracker under a **Notes** heading. Leave it off to
stay purely GitHub-driven.

## What the supervisor reads

- `reports/weekly-tracker.md` — per-person, per-repo summary for the window.
- `reports/project-status.md` — cross-repo project roll-up.
- `portfolio.html` — interactive dashboard (open locally or publish to GitHub Pages).

## Anti-patterns

- Putting a token in `team-portfolio.json` (it goes in env/secrets — always).
- Adding a tracking log *inside each tracked repo* (the original problem — it can't see
  across repos; that's the whole reason for the hub).
- A PAT with org-admin scope when read-only on a handful of repos is all that's needed.
