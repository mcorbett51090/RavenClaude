---
scenario_id: 2026-06-05-repo-silently-dropped-from-tracking
contributed_at: 2026-06-05
plugin: team-portfolio
product: config
product_version: "n/a"
scope: likely-general
tags: [config-drift, missing-repo, fail-soft, 404, onboarding]
confidence: medium
---

## Problem

A supervisor's weekly tracker showed a repo's activity "going to zero" for three weeks running, even though the team was visibly shipping to it. Nobody had touched the schedule. The repo had simply stopped appearing in `weekly-tracker.md` and `project-status.md` — but no banner, no error, no obvious cause. The supervisor's first instinct was "is the team not working in there anymore?" — exactly the wrong question, and the kind the plugin exists to *prevent* by reading GitHub directly (CLAUDE.md §1).

## Context

- ~6 repos tracked, mix of public + private, collection run nightly from a GitHub Action.
- The "missing" repo had been **renamed** on GitHub (`org/api` → `org/api-gateway`) during a reorg. `team-portfolio.json` still listed the old path.
- The collector is **fail-soft per repo** (CLAUDE.md §5): a 404 on one repo records an error and is skipped — the run did not crash, which is exactly why the drop was silent in the weekly view.

## Attempts

- Tried: re-ran the collector locally and **read `portfolio-activity.json` `errors[]`** instead of only the rendered reports. Found `org/api: HTTP 404 (Not Found)`. Outcome: root cause located — this is the single most useful diagnostic step, and the reports under-surface it (the error lives in the JSON, not the weekly tracker's body).
- Tried: confirmed GitHub *does* redirect API calls for renamed repos in many cases, but **the config path is the source of truth for clarity** and a redirect is not guaranteed for every endpoint/permission combination — so relying on the redirect is fragile. Outcome: decided to fix the config rather than lean on the redirect.
- Tried (the fix): updated `team-portfolio.json` `repos[]` to the new `org/api-gateway` path, re-ran, confirmed the repo reappeared with the right counts, and added it to the project's `match.repos` so historical project attribution stayed intact.

## Resolution

The activity wasn't gone — the **config had drifted** from GitHub's reality after a rename, and fail-soft skipping made the drop quiet. The fix was a one-line config edit plus a re-run.

**Action for the next operator hitting this pattern:** when a repo "goes to zero," **read `portfolio-activity.json` `errors[]` before drawing any human conclusion** — a 404 means renamed/moved (fix the config path), a 403 means token scope (see the rate-limit/token-scope scenario), and only a clean run with genuinely zero events is a real signal. Traverse [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md) "Collection Problem — Diagnose Why Counts Are Wrong" top-to-bottom; it routes 404 → "repo moved or renamed." Onboarding a repo is the mirror image: add it to `repos[]` (and `team[]` for new people, and any `project.match`) **before** expecting it in reports — see [`../best-practices/add-repos-to-config-before-expecting-them-in-reports.md`](../best-practices/add-repos-to-config-before-expecting-them-in-reports.md). Consider running [`../scripts/portfolio-config-check.py`](../scripts/portfolio-config-check.py) in the Action to catch a drifted/duplicate repo entry before the next run.
