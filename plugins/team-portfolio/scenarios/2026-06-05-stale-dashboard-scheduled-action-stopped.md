---
scenario_id: 2026-06-05-stale-dashboard-scheduled-action-stopped
contributed_at: 2026-06-05
plugin: team-portfolio
product: scheduled-action
product_version: "n/a"
scope: likely-general
tags: [scheduled-action, cron, stale-dashboard, default-branch, 60-day-disable]
confidence: medium
---

## Problem

A supervisor opened `portfolio.html` for the Monday review and the `generated_at` timestamp was **nine days old**. Every count was frozen at last week's numbers. Nothing in the dashboard said "stale" — it rendered cleanly with old data, which is the dangerous failure: a confidently-wrong-looking artifact. The collector and renderers were fine; the *trigger* had stopped firing.

## Context

- Hub repo on a **public** GitHub repo, scheduled refresh via the copy-in `portfolio-tracker.yml` Action (Mondays 13:00 UTC + nightly 06:00 UTC).
- A quiet stretch over a holiday: the team's tracked repos kept getting commits, but the *hub repo itself* (where the workflow lives) had no human commits for a while — its only writes were the Action's own `chore(portfolio): refresh` commits.
- The dashboard is regenerated only by the Action; nobody runs the renderers locally between meetings.

## Attempts

- Tried: checked the hub repo's **Actions tab** for the workflow's last successful run. Found the scheduled runs had stopped, with GitHub's banner: *"This scheduled workflow is disabled because there hasn't been activity in this repository for at least 60 days."* Outcome: root cause located — **GitHub auto-disables `schedule`-triggered workflows in a public repo after 60 days of no repository activity** [verified 2026-06-05 against GitHub Docs "Disabling and enabling a workflow"; behavior is volatile, [verify-at-use]].
- Tried: reasoned about *why* it tripped despite the Action committing nightly. The template commits **only when there's a diff** (`git diff --cached --quiet` → skip commit). Over the holiday the tracked-repo activity still changed, so most nights *did* commit — but the relevant subtlety is that GitHub's 60-day clock counts repository activity broadly, and a run of identical no-diff nights plus the `workflow_dispatch`/manual events not firing can let the window approach the threshold on a low-traffic hub. The honest read: the disable is a known GitHub behavior for low-activity public repos, and a portfolio hub whose only writer is a conditional bot commit is exactly the low-activity shape that hits it. [verify-at-use — confirm the exact activity definition in GitHub Docs at the time you act.]
- Tried (the fix): re-enabled the workflow from the Actions tab (one click) — also doable via the REST API `PUT /repos/{owner}/{repo}/actions/workflows/{id}/enable` [verify-at-use — endpoint per GitHub REST Actions docs]. Confirmed the next scheduled run produced a fresh `generated_at`.
- Tried (the guard, not just the fix): added the `workflow_dispatch` manual trigger awareness to the runbook so an operator can force a refresh on demand (the template already exposes it, and the `/portfolio-refresh` command is the on-demand path — CLAUDE.md §3), and noted that a private hub repo is **not** subject to the 60-day auto-disable, only public repos are [verify-at-use].

## Resolution

The data was never wrong — the **scheduled trigger had been auto-disabled** and the dashboard kept rendering the last-good artifact with no staleness signal. The fix was re-enabling the workflow; the lesson is detection.

**Action for the next operator:** when the dashboard looks frozen, **check `generated_at` against now FIRST, then the hub repo's Actions tab for a disabled/failed schedule** — don't re-debug the collector, which is downstream of a trigger that never fired. Two durable mitigations: (1) treat a `generated_at` older than the cron interval as a staleness alarm (a freshness check belongs in the operator's review ritual, and a future enhancement could bake a "stale if older than N hours" banner into the renderers — today it is operational, not coded); (2) know that **public repos auto-disable inactive scheduled workflows (~60 days)** [verify-at-use] while private repos do not — so a low-traffic public hub is the at-risk shape. Cadence alignment (cron timed before the standing meeting, `window_days` matching the interval) is covered by the "Cadence review" tree in [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md) and [`../best-practices/collection-window-must-match-cron-interval.md`](../best-practices/collection-window-must-match-cron-interval.md).
