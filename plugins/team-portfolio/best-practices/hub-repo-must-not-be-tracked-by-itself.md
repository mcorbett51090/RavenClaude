# The hub repo must not track itself as a collected repo

**Status:** Absolute rule
**Domain:** Team portfolio / configuration
**Applies to:** `team-portfolio`

---

## Why this exists

The hub repo contains the portfolio reports and the portfolio dashboard as committed files. If the hub is also listed as a tracked repo in `team-portfolio.json`, the portfolio-tracker workflow commits reports to the hub, which are then counted as activity in the next run, which produces another report commit, which is counted again. The result is a self-referential loop that inflates commit counts on every run and makes the weekly tracker useless as an activity signal for the team.

## How to apply

After choosing a hub repo (Step 0 of the portfolio-setup skill), verify that the hub repo's `owner/name` path is **not** in the `repos` array in `team-portfolio.json`:

```json
// WRONG — hub repo is tracking itself
{
  "repos": ["myorg/team-portfolio", "myorg/api", "myorg/web"]
}

// CORRECT — hub repo excluded from tracking
{
  "repos": ["myorg/api", "myorg/web"]
}
```

If the team does meaningful product work in the hub repo (unusual but possible), those commits will be missed from the tracker — acknowledge this as an accepted limitation and note it in the hub's README.

**Do:**
- Verify the hub exclusion in the initial setup and again after any `team-portfolio.json` restructuring.
- Add a comment in `team-portfolio.json` documenting the hub repo exclusion: `// hub repo excluded — portfolio-tracker commits would self-reference`.

**Don't:**
- Add the hub repo "so we can see bot activity" — bot/workflow commits should be excluded from human-activity tracking, not added.
- Accidentally re-add the hub repo when adding new tracked repos in a bulk edit.

## Edge cases / when the rule does NOT apply

- The team uses the hub repo for genuine development work (e.g., the portfolio dashboard is a product the team is building) — the hub must still be excluded from tracking to avoid the self-reference loop; document the missed hub-repo activity as an explicit gap.

## See also

- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — Step 0 covers hub repo selection and the exclusion decision
- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #6 (deterministic output — self-reference violates determinism)

## Provenance

Derived from the deterministic-output principle (`CLAUDE.md` §4 #6) applied to a specific configuration trap: a hub repo that tracks itself produces a report that changes on every run due to its own commits, making the diff meaningless as an activity signal.

---

_Last reviewed: 2026-06-05 by `claude`_
