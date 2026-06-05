# Unmatched activity is signal, not an error — surface it, do not suppress it

**Status:** Pattern
**Domain:** Team portfolio / reporting / data quality
**Applies to:** `team-portfolio`

---

## Why this exists

The `cross-repo-project-tracking` skill matches GitHub events to named projects via repo, label, or title-prefix filters. Any event that does not match a project is "unmatched." A naive implementation either suppresses unmatched events (producing a report that looks clean but misses real work) or flags them as errors (producing noise for a normal operating condition). In practice, a healthy team does a mix of project work and maintenance, exploration, and cross-cutting fixes that are not tagged to any named project — this is expected, not a bug. Suppressing it hides the maintenance and exploration load from the supervisor; flagging it as an error trains the team to ignore the warnings.

## How to apply

Include unmatched activity as a named category in every output artifact:

```json
{
  "projects": [
    {"name": "Website Redesign", "commits": 12, "prs_merged": 3},
    {"name": "API v2", "commits": 8, "prs_merged": 1}
  ],
  "unmatched": {
    "commits": 5,
    "prs_merged": 2,
    "repos": ["ops-scripts", "infra"],
    "note": "Activity not matched to a tracked project — normal operating condition"
  }
}
```

In `weekly-tracker.md`, add an "Unmatched activity" section after the project-level sections:

```markdown
## Unmatched activity (5 commits, 2 PRs)
Activity in `ops-scripts` and `infra` not matched to a tracked project.
This is normal — consider adding a project filter if this work should be tracked.
```

**Do:**
- Display unmatched event counts in both the JSON output and every rendered artifact.
- Include the repo names where unmatched activity occurred, so the supervisor can decide whether to add a project filter.
- Note that unmatched activity is a "normal operating condition" in the output — this prevents confusion.

**Don't:**
- Suppress unmatched events from the output; the supervisor cannot see the full team load without them.
- Treat a high unmatched count as a data quality error; it is information about the ratio of project work to maintenance/exploration.
- Automatically create a new project entry for unmatched repos; only the supervisor should decide what constitutes a tracked project.

## Edge cases / when the rule does NOT apply

- An authenticated run against a repo where the token has no read access produces a skip (not unmatched) — the distinction matters and both should be surfaced.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — anti-pattern §5 explicitly states "Treating 'unmatched' activity (no project) as an error — it's normal."
- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the skill that defines and applies project matching filters.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §5 anti-patterns. The principle reflects standard observability practice: emit what you see, including gaps, rather than filtering to only what you expected.

---

_Last reviewed: 2026-06-05 by `claude`_
