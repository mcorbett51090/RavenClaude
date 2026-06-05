# Add new repos to team-portfolio.json before expecting them in reports

**Status:** Absolute rule
**Domain:** Team portfolio / configuration
**Applies to:** `team-portfolio`

---

## Why this exists

A repo that is not listed in `team-portfolio.json` is invisible to the portfolio collector. When a new repo is created, activity in that repo does not appear in the tracker until the repo is added to the config. The failure is silent: the weekly tracker simply shows the team doing less work than they are, with no warning that a repo is missing. The supervisor may interpret the lower counts as reduced activity rather than a configuration gap — especially if the new repo is where an entire sprint's work is happening.

## How to apply

Whenever a new repo is created or a contractor's/contributor's repo is added to the tracked team:

1. Add the `owner/name` entry to the `repos` array in `team-portfolio.json`.
2. If the repo is private or in another account, verify the `PORTFOLIO_TOKEN` has read access to the new repo before the next scheduled run.
3. Commit the config update and trigger a manual collection run to verify the new repo's events appear in `portfolio-activity.json`.

```json
{
  "repos": [
    "myorg/api",
    "myorg/web",
    "myorg/new-service"   // ← added; verify token access before next scheduled run
  ]
}
```

**Pre-run checklist for a new private repo:**
- [ ] `owner/name` added to `repos` in `team-portfolio.json`
- [ ] Fine-grained PAT updated to include the new repo's read permission
- [ ] Manual test run confirms the new repo's activity appears in the output

**Do:**
- Treat a new-repo creation as a portfolio-config update trigger — it belongs in the same sprint or PR as the repo setup.
- Check the collection log after the next scheduled run to confirm no 403 or 404 appears for the new repo.

**Don't:**
- Assume a repo is being tracked because it is in the same org — the config is explicit, not auto-discovered.
- Wait until the weekly report looks wrong to add the missing repo — by then, multiple weeks of activity are not recoverable.

## Edge cases / when the rule does NOT apply

- Temporary repos (spike/throw-away repos with a planned lifetime under one sprint) — the overhead of adding and removing them may exceed the value of tracking; document the decision.

## See also

- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — initial repo list configuration
- [`../knowledge/team-portfolio-decision-trees.md`](../knowledge/team-portfolio-decision-trees.md) — the "Config gap" leaf in the collection-problem diagnostic tree

## Provenance

Codifies the "Config gap" root cause from the team-portfolio collection-problem decision tree. This is the most common cause of missing-repo activity, and it is preventable with a proactive config-update discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
