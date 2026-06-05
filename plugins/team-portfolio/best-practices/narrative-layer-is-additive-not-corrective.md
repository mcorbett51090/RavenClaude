# The narrative layer is additive context, not a correction to the GitHub-derived counts

**Status:** Absolute rule
**Domain:** Team portfolio / report design
**Applies to:** `team-portfolio`

---

## Why this exists

The optional `activity-narrative.md` narrative layer is designed to add human context — blockers, design decisions, team events — that GitHub activity counts can't capture. It is tempting to use the narrative layer to explain away lower-than-expected counts: "the numbers look low because we were doing design work." That use is legitimate, but the narrative layer must never be used to substitute for or contradict the GitHub-derived counts. If the counts are wrong because the config is misconfigured or the pipeline failed, the fix is the config or the pipeline — not a narrative note that says "ignore the numbers."

## How to apply

**Correct uses of the narrative layer:**

```
Week of 2026-06-02: Sprint planning and architecture design
The team spent most of the week in design sessions for the v3 API architecture.
Observable commit/PR counts will be lower than usual while design documents are finalized.
Expected production pace resumes [date].
```

**Incorrect uses of the narrative layer:**

```
Week of 2026-06-02: Counts appear low
We think some PRs may not have been captured this week. Please add 15-20 to the totals.
```

The second example is a data-quality correction that belongs in a config fix or a pipeline re-run — not a note asking the reader to adjust numbers manually.

The narrative note is stored in the hub repo (not in tracked repos — see the github-is-the-source-of-truth rule), clearly separated from the GitHub-derived counts section of the report.

**Do:**
- Use the narrative for context the data can't carry: planned quiet periods, design sprints, team events, blockers.
- Keep narrative notes brief (2-4 sentences) and time-scoped.

**Don't:**
- Use the narrative to correct count errors — fix the underlying config or pipeline instead.
- Add a narrative note to every report by default — it should appear only when there is genuine context to add.
- Store narrative notes in the tracked repos themselves (that re-introduces the per-repo log problem).

## Edge cases / when the rule does NOT apply

- There are no legitimate exceptions. The narrative adds context; the counts are authoritative. If the counts are wrong, the fix is technical.

## See also

- [`../skills/portfolio-setup/SKILL.md`](../skills/portfolio-setup/SKILL.md) — Step 5 on the optional narrative layer
- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #1 (GitHub is the source of truth; logs are the optional narrative layer)

## Provenance

Codifies the phrase "GitHub is the source of truth; logs are the optional narrative layer" from `CLAUDE.md` §4 house opinion #1. The boundary between authoritative data and human context is architectural, not stylistic.

---

_Last reviewed: 2026-06-05 by `claude`_
