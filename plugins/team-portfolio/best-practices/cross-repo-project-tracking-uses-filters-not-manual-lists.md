# Define cross-repo projects with filters, not manually maintained contributor lists

**Status:** Absolute rule
**Domain:** Team portfolio / cross-repo tracking / configuration
**Applies to:** `team-portfolio`

---

## Why this exists

A "project" in the cross-repo tracking model is a set of GitHub events that belong together — commits, PRs, and issues that are part of the same effort, spread across multiple repos. There are two ways to define this set: (1) match events by filter (repo name, label, PR title prefix), or (2) maintain a manually curated list of specific commits or PRs per person. Option 2 is the wrong choice every time: it requires a human to update the list on every commit and PR, it drifts immediately when a developer changes their workflow, and it recreates the per-repo self-reporting burden this plugin exists to eliminate. Option 1 is the correct choice: define the filter once, and the collection engine continuously applies it to new activity automatically.

## How to apply

Define projects in `team-portfolio.json` using filter rules, not explicit item lists:

```json
{
  "projects": [
    {
      "name": "Website Redesign",
      "match": {
        "repos": ["frontend", "design-system"],
        "labels": ["website-redesign"],
        "title_prefix": ["[website]", "website:"]
      }
    },
    {
      "name": "API v2",
      "match": {
        "repos": ["api", "api-docs"],
        "labels": ["api-v2"],
        "title_prefix": ["[api-v2]"]
      }
    }
  ]
}
```

Filter evaluation order (OR within a project, AND is never required — any match counts):
1. Repo name is in `match.repos` — all events from those repos are attributed to the project.
2. Issue or PR label is in `match.labels`.
3. PR or issue title starts with one of `match.title_prefix`.

**Do:**
- Start with repo-level matching for large, dedicated efforts (one or more repos owned by the project).
- Use label or title-prefix matching for cross-cutting efforts that touch shared repos (e.g., a security hardening effort that touches the backend, frontend, and infra repos).
- Document the filter rationale in a comment in the config — "all activity in `frontend` + label `website-redesign` in `shared-components`."

**Don't:**
- Maintain a `"contributors": ["alice", "bob"]` list per project — contributors are inferred from the activity, not configured.
- Create a project filter so broad (e.g., matching all repos) that it classifies everything — that collapses the project/unmatched distinction.
- Update the filter retroactively to re-classify historical activity; filters apply from the date they are configured forward.

## Edge cases / when the rule does NOT apply

- A one-time retrospective query ("what happened in the week of an incident") may be satisfied by a temporary project filter with a date range, applied to a single offline run rather than the ongoing scheduled collection.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — §6 routing table for the cross-repo-project-tracking skill.
- [`../skills/cross-repo-project-tracking/SKILL.md`](../skills/cross-repo-project-tracking/SKILL.md) — the skill that sets up and validates project filters.
- [`./unmatched-activity-is-signal-not-an-error.md`](./unmatched-activity-is-signal-not-an-error.md) — activity that does not match any filter is unmatched, which is normal and expected.

## Provenance

Derived from `team-portfolio` plugin design principles and the `cross-repo-project-tracking` skill specification. The filter-not-list approach is the architectural decision that makes the tracking automatic and maintenance-free.

---

_Last reviewed: 2026-06-05 by `claude`_
