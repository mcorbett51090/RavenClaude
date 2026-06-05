# Bot and CI accounts need explicit config entries with role:bot

**Status:** Pattern
**Domain:** Team portfolio / configuration
**Applies to:** `team-portfolio`

---

## Why this exists

GitHub repos typically have activity from non-human actors: Dependabot, GitHub Actions bot, deploy bots, and automated release scripts. Without explicit configuration, this activity lands in `unmatched_activity` — making the unmatched count misleading and potentially triggering investigation into "unknown contributors." Marking bots explicitly with `role: bot` removes them from the unmatched bucket, keeps the human-only activity counts clean, and makes the team roster honest.

## How to apply

Add bot logins to the `team` array in `team-portfolio.json` with `role: bot`:

```json
{
  "team": [
    { "login": "alice", "name": "Alice Chen", "role": "engineer" },
    { "login": "bob", "name": "Bob Smith", "role": "engineer" },
    { "login": "dependabot[bot]", "name": "Dependabot", "role": "bot" },
    { "login": "github-actions[bot]", "name": "GitHub Actions", "role": "bot" },
    { "login": "release-bot", "name": "Release Bot", "role": "bot" }
  ]
}
```

The collection script separates `role: bot` entries from the human roster in the report output — bot activity is visible but separate, not folded into the team's per-person counts.

**Common bot logins to add:**
- `dependabot[bot]` — dependency update PRs
- `github-actions[bot]` — workflow-triggered commits and issues
- `renovate[bot]` — if Renovate is used for dependency management
- Custom deploy or release bots specific to the team's tooling

**Do:**
- Audit `unmatched_activity` in the first few runs to identify bot logins to add.
- Use the exact GitHub login string (check the commit author on a bot commit if unsure).

**Don't:**
- Exclude bot activity entirely — it provides useful context (e.g., a spike in Dependabot PRs signals a major dependency update wave).
- Include bot logins in the human contributor count in dashboard summaries.

## Edge cases / when the rule does NOT apply

- A purely public repo with no bots configured — there may be no bot activity to classify. The rule still applies if bots are added later; add them to the config when they first appear.

## See also

- [`../skills/cross-team-contributor-analysis/SKILL.md`](../skills/cross-team-contributor-analysis/SKILL.md) — Step 4 on resolving unmatched activity
- [`../CLAUDE.md`](../CLAUDE.md) — §5 anti-pattern: unmatched activity is signal, not an error

## Provenance

Derived from the `CLAUDE.md` §5 anti-pattern "treating unmatched activity as an error." Bot activity is expected and belongs in a separate, labeled bucket, not the unmatched bucket. Standard practice in any team-activity tracking system that reads GitHub events.

---

_Last reviewed: 2026-06-05 by `claude`_
