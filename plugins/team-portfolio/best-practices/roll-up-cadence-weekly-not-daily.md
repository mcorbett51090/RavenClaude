# Default the roll-up cadence to weekly — daily runs are noise for portfolio altitude

**Status:** Pattern
**Domain:** Team portfolio / roll-up cadence / configuration
**Applies to:** `team-portfolio`

---

## Why this exists

A portfolio roll-up answers the question "what has the team been working on?" at the supervisor altitude — not the developer altitude. At developer altitude, a commit is meaningful. At supervisor altitude, a single commit is background noise; the signal is the trend across the week: which projects are moving, which contributors are active, and whether the cross-repo work distribution looks healthy. Daily roll-ups at supervisor altitude produce reports where most rows say "2 commits" and the supervisor has no comparative context to assess them against. Weekly roll-ups produce counts that are large enough to be meaningful, comparable week-over-week, and worth a 5-minute review.

## How to apply

Default the GitHub Action to a weekly schedule:

```yaml
# templates/portfolio-tracker.yml
on:
  schedule:
    - cron: "0 8 * * 1"   # Monday 08:00 UTC — start-of-week review
  workflow_dispatch:        # Manual trigger for on-demand runs
```

Configure the collection window in `team-portfolio.json`:

```json
{
  "collection_window_days": 7,
  "cadence": "weekly"
}
```

When a consumer needs a different cadence:
- **Bi-weekly sprint review:** change cron to `"0 8 * * 1/2"` and `collection_window_days` to 14.
- **On-demand only:** remove the schedule trigger and use `workflow_dispatch` exclusively.
- **Daily (not recommended):** use only if the team's work cycle is genuinely daily (e.g., a daily standup where cross-repo activity is reviewed). Pair with a `collection_window_days: 1` to avoid overlapping windows.

**Do:**
- Document the chosen cadence and the collection window in the hub repo's README so the team knows what the numbers represent.
- Align the roll-up to the team's review cadence (sprint review, weekly standup) rather than a purely technical interval.
- Use manual (`workflow_dispatch`) triggers for ad-hoc "what happened during the incident" runs without changing the scheduled cadence.

**Don't:**
- Default to daily because it seems "more real-time" — more frequent runs at portfolio altitude produce more data, not more insight.
- Use a `collection_window_days` value shorter than the cron interval — gaps between the collection window and the trigger interval produce invisible dead zones in the timeline.
- Use a `collection_window_days` value longer than the cron interval — overlapping windows produce double-counted events.

## Edge cases / when the rule does NOT apply

- A team running a daily operations review (e.g., a DevOps team managing live deployments) where cross-repo commit and PR activity is part of the daily operational picture may benefit from a daily cadence. Confirm the cadence with the team before setting it.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — §7 describes the scheduled Action template.
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup skill configures the cadence as part of hub initialization.

## Provenance

Derived from portfolio management practice and team observability principles. The weekly default reflects the standard management-review cycle at team/portfolio altitude.

---

_Last reviewed: 2026-06-05 by `claude`_
