---
name: report-cadence-tuning
description: "Tune the portfolio-tracker scheduled Action cadence, collection-window-days, and report output settings to match the team's actual review rhythm. Reach for this skill when the weekly tracker is generating too much noise, when the window produces gaps or double-counts, or when the supervisor wants a different report frequency."
---

# Skill: Report Cadence Tuning

The default portfolio-tracker cadence (weekly refresh on Mondays, 7-day collection window) is the right starting point but not always the right steady state. A team that ships daily and reviews metrics monthly needs a different configuration than a consulting team that does weekly stand-ups. This skill aligns the scheduler and the collection window so the output is neither stale nor overwhelming.

## The core invariant: collection window must match the cron interval

The `collection_window_days` in `team-portfolio.json` must equal the cron schedule interval. If they diverge:

| Mismatch | Effect |
|---|---|
| `collection_window_days` < cron interval | Activity in the gap is permanently uncounted — not recoverable |
| `collection_window_days` > cron interval | Double-counting: events near the boundary appear in two consecutive runs |

Neither gap nor double-count is detectable without comparing runs manually. The invariant is enforced by keeping both values in sync whenever either changes.

## Step 1 — Identify the supervisor's review rhythm

Ask or infer from the team's working style:
- How often does the supervisor look at the portfolio reports? (daily / weekly / bi-weekly / monthly)
- Is the goal a diff-per-run (see what changed since last run) or a cumulative window (see the last N days regardless of run)?
- Is there a fixed meeting cadence the report should feed? (Monday stand-up / weekly all-hands / monthly review)

## Step 2 — Select the cron interval

| Review rhythm | Recommended cron | `collection_window_days` |
|---|---|---|
| Weekly stand-up | `0 6 * * 1` (Monday 06:00 UTC) | 7 |
| Bi-weekly sprint review | `0 6 1,15 * *` (1st and 15th of month) | 14 |
| Monthly review | `0 6 1 * *` (1st of month) | 30 |
| Daily (high-velocity team) | `0 6 * * *` (daily at 06:00 UTC) | 1 |

**Anti-pattern:** daily cron with a 7-day window produces 7x over-counting and a dashboard that changes every day by 1/7 of the total — it looks active but is not meaningful.

## Step 3 — Update both the workflow and the config in the same commit

```yaml
# .github/workflows/portfolio-tracker.yml
on:
  schedule:
    - cron: '0 6 * * 1'   # Update this

# team-portfolio.json
{
  "collection_window_days": 7   # Update this to match
}
```

Both files must be updated atomically — a mismatched commit creates a gap or double-count for exactly one run.

## Step 4 — Optionally add a nightly summary vs. a weekly full report split

For teams that want both a quick daily activity check and a full weekly narrative:
- Keep the primary weekly cron for the full `weekly-tracker.md` + `portfolio.html` output.
- Add a secondary daily cron that runs `portfolio-collect.py` + `portfolio-report.py --mode=daily` with `collection_window_days: 1` for a lightweight daily summary.
- Store the daily outputs in a `reports/daily/` subdirectory to keep the weekly reports uncluttered.

## Step 5 — Verify the new cadence with one manual run

Before relying on the updated schedule, run the collection and renderers manually with the new window to verify:
1. Activity counts look reasonable for the window size.
2. No gaps appear in the date range (a gap means the previous cron collected an overlapping window that is now not covered).
3. The `generated_at` timestamp in `portfolio-activity.json` updates correctly.

## Pitfalls

- Changing `collection_window_days` without updating the cron interval (or vice versa) — the gap or double-count is silent.
- Setting a very short window (1-3 days) for a monthly review cadence — most of the period goes uncounted.
- Forgetting to commit the cron change to the workflow file — the Action keeps running on the old schedule after the config is updated.
- Adding a nightly cron without a separate `collection_window_days` setting — it overwrites the same `portfolio-activity.json` the weekly run uses.

## See also

- [`../../CLAUDE.md`](../../CLAUDE.md) — §4 house opinion #6 (deterministic output) and §5 anti-pattern (collection window mismatch)
- [`../../skills/portfolio-setup/SKILL.md`](../../skills/portfolio-setup/SKILL.md) — Step 3 for the initial cron setup
