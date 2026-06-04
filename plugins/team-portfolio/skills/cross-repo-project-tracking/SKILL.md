---
name: cross-repo-project-tracking
description: "Define and track a project that spans multiple GitHub repos. Use when a piece of work (a launch, a client, a feature) lives across several repositories and you want its status rolled up in one place instead of checked repo-by-repo. Covers the three match rules (repo / label / title-prefix), how an event is attributed to a project, choosing a convention that scales, and reading the per-project status the report and dashboard produce."
---

# Skill: Cross-repo project tracking

A "project" here is a named slice of work that doesn't respect repo boundaries — a
website launch touching a design repo and a content repo, a client engagement touching
three repos, a feature split across frontend and backend. The plugin maps each activity
event (commit / PR / issue) to at most one project, then rolls up status per project
across every repo.

## How matching works

In `team-portfolio.json`, each project carries a `match` object. An event is attributed
to the **first** project whose `match` covers it, by ANY of these rules:

| Rule | Matches when | Best for |
| --- | --- | --- |
| `repos` | the event's repo is in the list | a project that owns whole repos |
| `labels` | any event label is in the list (case-insensitive) | work tagged with a shared label across repos |
| `title_prefixes` | the PR/issue title starts with a listed prefix | a lightweight `[tag]` convention in titles |

```json
{
  "name": "Raven Power Website",
  "match": {
    "repos": ["mcorbett51090/RavenPower-Website", "mcorbett51090/RavenPowerWebsite"],
    "labels": ["website"],
    "title_prefixes": ["[web]"]
  }
}
```

Order matters: projects are evaluated top-to-bottom, first match wins. Put the most
specific project first if an event could plausibly match two.

## Choosing a convention that scales

- **Repo-owned projects** (a repo belongs to exactly one project): use `repos` only —
  zero per-issue effort, nothing for contributors to remember.
- **Cross-cutting work inside shared repos**: use a **shared label** applied in each repo
  (e.g. `website`, `client-acme`). Labels travel with the issue/PR and need no title
  discipline.
- **Quick-and-dirty**: a `[tag]` title prefix. Cheapest to start, easiest to forget —
  prefer labels once the project is real.

## Reading the roll-up

Both outputs surface per-project status:

- `reports/project-status.md` — per project: which repos saw activity, open PRs, merged
  PRs, open issues, and total events in the window.
- `portfolio.html` → **Projects (cross-repo)** table — the same, interactive.

Events that match no project are still counted in the per-person and per-repo views; they
just don't appear under a project. That's expected — not all work belongs to a tracked
project.

## Anti-patterns

- Overlapping `match` rules across projects with no clear priority — the first-match-wins
  ordering becomes the silent tiebreaker. Order deliberately.
- A label convention nobody applies — if contributors won't label, use `repos` instead and
  don't pretend the label view is complete.
- Treating "unmatched" as an error. Unmatched activity is normal; only define projects for
  work you actually want a cross-repo status on.
