# Collection window days must exactly match the cron schedule interval

**Status:** Absolute rule
**Domain:** Team portfolio / scheduler configuration
**Applies to:** `team-portfolio`

---

## Why this exists

`collection_window_days` in `team-portfolio.json` and the cron schedule interval in the Action workflow are coupled: if they differ, every run either over-counts (window larger than interval — the same events appear in consecutive runs) or silently under-counts (window smaller than interval — some days are never collected). Neither problem produces an error message. The output simply looks wrong, and diagnosing why requires manual comparison of consecutive runs. Keeping the two values equal is the only way to guarantee a complete, non-overlapping activity record.

## How to apply

Whenever either `collection_window_days` or the cron expression is changed, update the other in the same commit:

```yaml
# .github/workflows/portfolio-tracker.yml
schedule:
  - cron: '0 6 * * 1'   # Weekly Monday → interval = 7 days

# team-portfolio.json
{
  "collection_window_days": 7   # Must equal the cron interval
}
```

Quick reference:

| Cron pattern | Interval | `collection_window_days` |
|---|---|---|
| `0 6 * * 1` (weekly) | 7 | 7 |
| `0 6 1,15 * *` (bi-weekly) | ~14 | 14 |
| `0 6 1 * *` (monthly) | ~30 | 30 |
| `0 6 * * *` (daily) | 1 | 1 |

**Do:**
- Update both files in the same commit and the same PR — one-value-only changes are a configuration debt item.
- Verify with a manual run after changing the cadence: check that `generated_at` aligns with the expected window.

**Don't:**
- Set `collection_window_days` to a round number that differs from the actual cron interval (e.g., 30 days for a weekly cron).
- Add an overlap "just in case" — overlapping produces inflated counts that mislead the supervisor.

## Edge cases / when the rule does NOT apply

- The secondary daily-summary cron (if one is added for a lightweight daily view) runs with its own `collection_window_days: 1` and outputs to a separate directory — it is a distinct configuration, not an override of the primary window.

## See also

- [`../skills/report-cadence-tuning/SKILL.md`](../skills/report-cadence-tuning/SKILL.md) — full cadence-change procedure
- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #6 (deterministic output) and §5 anti-pattern (window mismatch)

## Provenance

Codifies the collection-window mismatch root cause from the `team-portfolio-decision-trees.md` "Diagnose Why Counts Are Wrong" tree — the "Window mismatch" leaf is the silent problem that this rule prevents.

---

_Last reviewed: 2026-06-05 by `claude`_
