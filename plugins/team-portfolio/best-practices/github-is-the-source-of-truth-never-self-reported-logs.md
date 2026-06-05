# GitHub is the source of truth — never ask repos to self-report activity

**Status:** Absolute rule
**Domain:** Team portfolio / data sourcing
**Applies to:** `team-portfolio`

---

## Why this exists

The fundamental problem this plugin exists to solve is the **blind spot created by per-repo activity logs**: each tracked repo self-reports only what it knows, and a supervisor watching ten repos must visit ten places to get a view of their team. A plugin that solves this by asking each repo to maintain a status file has reproduced the original problem at one remove — it added a maintenance burden without removing the fragmentation. The only source of activity data that is structurally honest, requires no per-repo maintenance, and covers all repos uniformly is the GitHub API. Any design that supplements or replaces GitHub API data with per-repo markdown logs re-introduces the blind spot.

## How to apply

When designing or extending portfolio tracking:

1. Treat every observable GitHub event (commits, pull requests, issues, reviews, releases) as the raw activity record.
2. Read it via the GitHub REST API from the hub repo — the hub reads all tracked repos; it does not ask tracked repos to write to anything.
3. If a piece of information is not available from the GitHub API (e.g., time spent, blocked status, individual developer commentary), classify it as a **narrative layer** that the team maintains voluntarily in `templates/activity-narrative.md` — clearly separated from the authoritative GitHub-derived counts.

**Do:**
- Read commit, PR, issue, and review event counts from the GitHub API as the authoritative activity record.
- Surface "unmatched" activity (events with no project tag) as normal — it is signal, not an error.
- Treat a `403` or `404` on a repo as a skip-with-error, not a failure of the whole run.

**Don't:**
- Add a `portfolio-status.md` or similar file inside each tracked repo — that re-introduces the per-repo log this plugin replaces.
- Ask developers to update a status file as part of a PR checklist in the tracked repos.
- Treat GitHub event counts as a performance evaluation metric; they are an activity signal, not a productivity judgment.

## Edge cases / when the rule does NOT apply

- The `templates/activity-narrative.md` is an intentional exception: it is a human-written note file in the hub repo (not in tracked repos), explicitly separated from the GitHub-derived counts, and optional.
- GitLab, Bitbucket, or other hosting platforms would require a different API adapter; the principle (source from the platform, not from self-reports) still applies.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — house opinion §4 #1 states this rule as a plugin-level constitution.
- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — the setup skill that implements this rule in the hub configuration.

## Provenance

Derived from `team-portfolio` plugin CLAUDE.md §4 house opinion #1 ("GitHub is the source of truth; logs are the optional narrative layer"). This rule is architectural, not behavioral.

---

_Last reviewed: 2026-06-05 by `claude`_
